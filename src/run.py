"""Dây chuyền 1 truyện theo lô, giữ nhất quán bằng sổ tay truyện. Thiết kế: docs/plans/story-bible.md

python -m src.run <slug> --chapters 1-10 [--workers 3] [--render] [--title "..."] [--force STEP]

Mỗi lô (batch_size chương, mặc định 5), lô sau chờ sổ tay của lô trước:
  A. rã chương (song song)          → outline/chapter_cards/NNN.md
  B. nhóm trưởng lập/cập nhật sổ tay + đề cương lô → bible/*.md, bible/arcs/KK.md, rename_map.json
     (sổ tay v1: DỪNG chờ Người sáng lập duyệt, rồi đặt `bible_approved: true` trong story.yaml)
  D. viết (theo sổ tay) → soát + kiểm máy → duyệt từng chương (song song) → script/NNN.txt + NNN.proposals.md
  E. nhóm trưởng kiểm mạch cả lô; chương lệch viết lại kèm ghi chú (tối đa continuity_rounds vòng)
  F. nhóm trưởng gộp đề xuất vào sổ tay → phiên bản mới + bible/CHANGELOG.md
  G. giọng VieNeu từng chương (tuần tự). --render: ghép cả dải chương thành 1 video + mốc chương.

- Mức viết lại theo story.yaml `rewrite`: light (đọc chương gốc, giữ bối cảnh + tên Hán Việt), deep, hoặc none (kịch bản
  nhập sẵn bằng `python -m src.drama import`: bỏ viết/duyệt, đi thẳng sang giọng đọc).
- Bước nào đã có file đầu ra thì bỏ qua. --force <bước> làm lại bước đó và mọi bước sau.
- LLM chạy trên agy (gói Gemini Pro cá nhân), model theo config.yaml `agents:`. Log: stories/<slug>/render/pipeline.jsonl
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import yaml

from src.common import agy, render, tts

ROOT = pathlib.Path(__file__).resolve().parents[1]
ROLES = ROOT / "prompts/roles"
STEPS = ["card", "plan", "write", "edit", "review", "continuity", "update", "voice"]
BIBLE = ["bible.md", "characters.md", "ledger.md"]
CJK = re.compile(r"[\u3400-\u9fff\uf900-\ufaff]")
MARKDOWN = re.compile(r"^\s*(#|[-*•]\s|\d+\.\s|>)|\*\*|__|```", re.M)
VERDICT = re.compile(r"Kết luận\W*(CHƯA ĐẠT|KHÔNG ĐẠT|ĐẠT)\b", re.I)
FILE_MARK = re.compile(r"^=== FILE: (\S+) ===\s*$", re.M)
PROPOSAL_MARK = "=== ĐỀ XUẤT SỔ TAY ==="
NO_SOURCE = "KHÔNG ĐỌC ĐƯỢC NGUỒN"


class Stop(Exception):
    """Dừng dây chuyền, cần người xem (quota, hết thang model, duyệt CHƯA ĐẠT, chờ duyệt sổ tay)."""


class Story:
    def __init__(self, slug: str):
        self.dir = ROOT / "stories" / slug
        self.meta = yaml.safe_load((self.dir / "story.yaml").read_text(encoding="utf-8"))
        ch = ROOT / "channels" / self.meta["channel"]
        self.channel = yaml.safe_load((ch / "channel.yaml").read_text(encoding="utf-8"))
        self.channel_dir = ch
        self.cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
        self.cfg["pipeline"].update(self.meta.get("pipeline") or {})   # story.yaml được ghi đè pipeline (vd. fast)
        self.mode = self.meta.get("rewrite", "deep")
        self.log_path = self.dir / "render" / "pipeline.jsonl"
        self.bible = self.dir / "bible"
        self._lock = threading.Lock()

    def p(self, kind: str, n: int) -> pathlib.Path:
        return {
            "card": self.dir / "outline/chapter_cards" / f"{n:03d}.md",
            "draft": self.dir / "script" / f"{n:03d}.draft.txt",
            "edit": self.dir / "script" / f"{n:03d}.txt",
            "review": self.dir / "script" / f"{n:03d}.review.md",
            "proposal": self.dir / "script" / f"{n:03d}.proposals.md",
            "mp3": self.dir / "audio" / f"{n:03d}.mp3",
            "srt": self.dir / "audio" / f"{n:03d}.srt",
            "arc": self.bible / "arcs" / f"{n:02d}.md",          # n = số lô
            "check": self.bible / "checks" / f"{n:02d}.md",      # n = số lô
        }[kind]

    @property
    def names(self) -> pathlib.Path:
        return self.dir / "rename_map.json"

    @property
    def words(self) -> list[int]:
        return self.cfg["pipeline"]["script_words"][self.mode]

    def batch_of(self, n: int) -> int:
        return (n - 1) // self.cfg["pipeline"]["batch_size"] + 1

    def version(self) -> int:
        log = self.bible / "CHANGELOG.md"
        return len(re.findall(r"^## v\d+", log.read_text(encoding="utf-8"), re.M)) if log.exists() else 0

    def log(self, **kw) -> None:
        kw = {"time": dt.datetime.now().isoformat(timespec="seconds"), **kw}
        with self._lock:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(kw, ensure_ascii=False) + "\n")
            print(" ".join(f"{k}={v}" for k, v in kw.items() if k in ("chapter", "step", "model", "result", "note")),
                  flush=True)


def ask(story: Story, role: str, brief: str, n: int, step: str, level: int = 0, check=None,
        avoid: str = "", ladder_key: str = "") -> tuple[str, int, str]:
    """Gọi agy theo thang model (config `agents[ladder_key or role]`), từ bậc `level`; leo thang khi rỗng hoặc
    trượt `check`. `avoid`: model không được dùng (người duyệt khác người viết). Trả về (text, bậc, model)."""
    ladder = story.cfg["agents"][ladder_key or role]
    head = (ROLES / f"{role}.md").read_text(encoding="utf-8")
    for lv in range(level, len(ladder)):
        if ladder[lv] == avoid:
            continue
        guard_quota(story, n, ladder[lv])
        r = agy.run(head + "\n\n## Nhiệm vụ lần này\n" + brief, ladder[lv])
        problem = "rỗng" if not r["text"] else (check(r["text"]) if check else None)
        story.log(chapter=n, step=step, model=ladder[lv], result="ok" if not problem else "lỗi", note=problem or "",
                  seconds=r["seconds"], usage=r["usage"], notices=r["notices"])
        if not problem:
            return r["text"], lv, ladder[lv]
    raise Stop(f"Chương/lô {n}, bước {step}: hết thang model {ladder}")


_QUOTA = {"at": 0.0, "left": {}}


def guard_quota(story: Story, n: int = 0, model: str = "gemini") -> None:
    import time
    with story._lock:  # nhớ kết quả 2 phút: mỗi lần hỏi /usage tốn thêm một lần gọi agy
        if time.time() - _QUOTA["at"] > 120:
            _QUOTA.update(at=time.time(), left=agy.usage())
        left = _QUOTA["left"]
    if not left:
        story.log(chapter=n, step="quota", result="cảnh báo", note="không đọc được quota agy, chạy tiếp")
    floor = story.cfg["pipeline"]["quota_floor"]
    pool = "Gemini" if model.startswith("gemini") else "Claude"  # agy có 2 kho: Gemini, và Claude/GPT
    low = {k: v for k, v in left.items() if k.startswith(pool) and v < floor}
    if low:
        raise Stop(f"Quota kho {pool} thấp {low}; chạy lại sau giờ làm mới hoặc đổi model trong config.yaml")


# ── Kiểm tra bằng máy ──────────────────────────────────────────────────────────────────────────────
def script_problems(text: str, story: Story) -> str | None:
    lo, hi = story.words
    words = len(text.split())
    issues = []
    if CJK.search(text):
        issues.append(f"còn chữ Hán: {''.join(sorted(set(CJK.findall(text))))[:20]}")
    if MARKDOWN.search(text):
        issues.append("có markdown/gạch đầu dòng")
    if not lo <= words <= hi:
        issues.append(f"độ dài {words} từ ngoài khoảng {lo}-{hi}")
    banned = [f"'{w}' → '{r}'" for w, r in load_names(story).get("banned", {}).items()
              if re.search(rf"(?<!\w){re.escape(w)}(?!\w)", text)]
    if banned:
        issues.append("còn từ cấm theo sổ tay (phải thay): " + ", ".join(banned))
    return "; ".join(issues) or None


def verdict(review: str) -> bool | None:
    """True/False theo dòng 'Kết luận: ...' đầu tiên; None nếu không có dòng kết luận."""
    m = VERDICT.search(review)
    return None if not m else m.group(1).upper() == "ĐẠT"


def split_files(text: str) -> dict[str, str]:
    parts = FILE_MARK.split(text)
    return {parts[i].strip(): parts[i + 1].strip() + "\n" for i in range(1, len(parts) - 1, 2)}


def parse_json(text: str) -> dict:
    m = re.search(r"\{.*\}", text, re.S)
    return json.loads(m.group(0)) if m else {}


def names_problem(old: dict, text: str) -> str | None:
    try:
        new = parse_json(text)
    except json.JSONDecodeError:
        return "rename_map.json hỏng"
    if not all(isinstance(new.get(sec), dict) for sec in ("characters", "places", "terms")):
        return "rename_map thiếu characters/places/terms"
    bad = [k for sec in ("characters", "places", "terms") for k, v in old.get(sec, {}).items() if new[sec].get(k) != v]
    return f"rename_map làm mất hoặc đổi tên cũ: {bad[:5]}" if bad else None


def ledger_rows(md: str) -> int:
    return len(re.findall(r"^\|\s*\d+\s*\|", md, re.M))


def bible_problems(story: Story, text: str, need: list[str]) -> str | None:
    files = split_files(text)
    missing = [f for f in need if f not in files]
    if missing:
        return f"thiếu file: {missing}"
    old_ledger = story.bible / "ledger.md"
    if "ledger.md" in files and old_ledger.exists() and \
            ledger_rows(files["ledger.md"]) < ledger_rows(old_ledger.read_text(encoding="utf-8")):
        return "ledger.md bị mất dòng dữ kiện cũ"
    if "rename_map.json" in files:
        return names_problem(load_names(story), files["rename_map.json"])
    return None


# ── Ngữ cảnh gửi cho agent ─────────────────────────────────────────────────────────────────────────
def load_names(story: Story) -> dict:
    return json.loads(story.names.read_text(encoding="utf-8")) if story.names.exists() else \
        {"_note": "Giữ bối cảnh Trung Quốc, tên riêng dùng âm Hán Việt" if story.mode == "light"
         else "Việt hoá theo quyết định của truyện", "characters": {}, "places": {}, "terms": {}}


def bible_pack(story: Story, batch: int | None = None) -> str:
    """Sổ tay hiện hành (+ đề cương lô) để gửi kèm brief."""
    parts = [f"# SỔ TAY TRUYỆN v{story.version()}"]
    for f in BIBLE:
        path = story.bible / f
        parts.append(f"## {f}\n" + (path.read_text(encoding="utf-8") if path.exists() else "(chưa có)"))
    parts.append("## rename_map.json\n" + json.dumps(load_names(story), ensure_ascii=False, indent=2))
    if batch and story.p("arc", batch).exists():
        parts.append(f"## Đề cương lô {batch}\n" + story.p("arc", batch).read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def card_url(story: Story, n: int) -> str:
    card = story.p("card", n)
    m = re.search(r"Nguồn:\s*(\S+)", card.read_text(encoding="utf-8")) if card.exists() else None
    return m.group(1) if m else ""


def source_hint(story: Story, n: int) -> str:
    m = story.meta
    hint = (f"Đọc CHƯƠNG {n} của truyện 《{m['title_zh']}》 (tác giả {m.get('author', '?')}). "
            f"Trang truyện: {m.get('source_mobile') or m['source_url']} (bản điện thoại thường đọc được, bản máy tính "
            "hay bị chặn bot). Nếu cần, mở mục lục (目录) để tìm đúng chương.")
    if url := card_url(story, n - 1):
        hint += f" Chương {n - 1} ở {url}; chương {n} là chương kế tiếp."
    return hint + f" Lập thẻ chương số {n} theo đúng khung; dòng đầu phải là '# Thẻ chương {n}:'."


def write_brief(story: Story, n: int, feedback: str = "") -> str:
    lo, hi = story.words
    if story.mode == "light":
        head = (f"Viết bản kể CHƯƠNG {n} của truyện '{story.meta['title_vi']}' ({story.meta['title_zh']}). "
                f"Chương gốc: {card_url(story, n)} — hãy đọc chương này. Độ dài {lo}–{hi} từ.")
    else:
        head = (f"Viết kịch bản kể CHƯƠNG {n} của truyện '{story.meta['title_vi']}'. Độ dài {lo}–{hi} từ, "
                "khoảng 60–80% chương gốc.")
    parts = [head]
    if story.meta.get("source") == "original" and n == 1:      # truyện tự viết: 30 giây đầu quyết định người xem ở lại
        parts.append("MỞ ĐẦU GIỮ CHÂN (bắt buộc): 2–3 câu đầu là cảnh đắt nhất hoặc câu sốc của truyện (có thể kể vượt thời "
                     "gian lên trước rồi quay lại), hoặc một câu hỏi khiến người nghe phải nghe tiếp; KHÔNG chào kênh, không "
                     "giới thiệu dài. Lời chào kênh ngắn (1 câu) đặt sau đoạn mở đầu này.")
    if n > 1:
        parts.append("Đây là chương nối tiếp: KHÔNG chào hỏi hay giới thiệu kênh lại; mở bằng 1 câu nối mạch rồi vào "
                     "truyện. Kết chương vẫn có móc câu.")
    parts += [bible_pack(story, story.batch_of(n)), "## Thẻ chương này\n" + story.p("card", n).read_text(encoding="utf-8")]
    if feedback:
        parts.append("## Góp ý ở lần trước (phải sửa hết)\n" + feedback)
    if story.cfg["pipeline"].get("fast"):            # chế độ nhanh: không có vòng soát riêng nên tự kiểm trước khi nộp
        banned = load_names(story).get("banned", {})
        parts.append("## TỰ KIỂM trước khi trả lời (không có người soát riêng)\n"
                     f"- Độ dài {lo}–{hi} từ; không còn chữ Hán; không markdown, không gạch đầu dòng, không tiêu đề.\n"
                     "- Tên riêng đúng bảng tên Hán Việt trong sổ tay; xưng hô nhất quán với sổ tay.\n"
                     "- Thoại trong ngoặc kép, mỗi lượt thoại rõ ai nói; lời bình người kể khoảng 5%, không lan man.\n"
                     + (f"- Tuyệt đối không dùng: {', '.join(banned)}.\n" if banned else ""))
    return "\n\n".join(parts)


def review_brief(story: Story, n: int) -> str:
    lo, hi = story.words
    if story.mode == "light":
        crit = ("(1) sát mạch chương gốc và thẻ chương, không thêm hay bỏ tình tiết chính; (2) là bản viết lại nhẹ, tự "
                "nhiên với người Việt, không dịch word-by-word; (3) GIỮ bối cảnh Trung Quốc và tên Hán Việt theo bảng "
                "tên, không Việt hoá địa danh; (4) lời bình người kể khoảng 5% (mở, cao trào, kết), không chen giữa thoại")
    else:
        crit = ("(1) đúng mạch thẻ chương, không bịa tình tiết đổi cốt truyện; (2) là bản viết lại, không dịch từng câu; "
                "(3) dùng đúng bảng đổi tên, không sót tên Trung; (4) có lời bình người kể ~10–15%, có móc câu đầu/cuối")
    return "\n\n".join([
        f"Duyệt KỊCH BẢN KỂ CHUYỆN chương {n} (không phải báo cáo nghiên cứu: không cần kiểm link). Tiêu chí: {crit}; "
        f"(5) câu ngắn, không markdown/emoji, đọc TTS tự nhiên; (6) độ dài {lo}–{hi} từ; (7) ĐÚNG SỔ TAY: quy ước kể và "
        "xưng hô, trạng thái nhân vật, dữ kiện đã xác lập, không tiết lộ điều đề cương lô cấm. Dòng đầu phải là "
        "'Kết luận: ĐẠT' hoặc 'Kết luận: CHƯA ĐẠT'. Bảng kiểm tra mỗi dòng 1 tiêu chí kèm trích dẫn; thêm 'Câu cần "
        "sửa' (trích + đề xuất).",
        bible_pack(story, story.batch_of(n)),
        "## Thẻ chương\n" + story.p("card", n).read_text(encoding="utf-8"),
        "## Kịch bản cần duyệt\n" + story.p("edit", n).read_text(encoding="utf-8")])


def expand(force: set[str]) -> set[str]:
    """Làm lại 1 bước thì mọi bước sau nó cũng phải làm lại."""
    return set(STEPS[min(STEPS.index(f) for f in force):]) if force else set()


def need(force: set[str], step: str, *paths: pathlib.Path) -> bool:
    return step in force or not all(p.exists() for p in paths)


def write_bible_files(story: Story, files: dict[str, str], batch: int, what: str) -> int:
    story.bible.mkdir(parents=True, exist_ok=True)
    for f in BIBLE:
        if f in files:
            (story.bible / f).write_text(files[f], encoding="utf-8")
    if "arc.md" in files:
        story.p("arc", batch).parent.mkdir(parents=True, exist_ok=True)
        story.p("arc", batch).write_text(files["arc.md"], encoding="utf-8")
    if "rename_map.json" in files:  # giữ các khoá quy ước (address, banned…) nếu nhóm trưởng quên trả lại
        new = {**{k: v for k, v in load_names(story).items() if k not in ("characters", "places", "terms")},
               **parse_json(files["rename_map.json"])}
        story.names.write_text(json.dumps(new, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    v = story.version() + 1
    with open(story.bible / "CHANGELOG.md", "a", encoding="utf-8") as fh:
        fh.write(f"## v{v} — lô {batch}: {what} ({dt.date.today().isoformat()})\n"
                 f"{files.get('changes.md', '- (không ghi thay đổi)').strip()}\n\n")
    return v


# ── A. Rã chương ─────────────────────────────────────────────────────────────────────────────────────
def card_step(story: Story, n: int, force: set[str]) -> None:
    if not need(force, "card", story.p("card", n)):
        return
    ok = re.compile(rf"#\s*Thẻ chương\s*{n}\b")
    text, *_ = ask(story, "story-analyst", source_hint(story, n), n, "card",
                   check=lambda t: None if "## Diễn biến" in t and len(t) > 1500 and ok.search(t)
                   else "thẻ chương sai số chương hoặc thiếu Diễn biến")
    story.p("card", n).parent.mkdir(parents=True, exist_ok=True)
    story.p("card", n).write_text(text + "\n", encoding="utf-8")


# ── B. Nhóm trưởng lập/cập nhật sổ tay + đề cương lô ──────────────────────────────────────────────────
def plan_step(story: Story, batch: int, chapters: list[int], force: set[str]) -> None:
    if need(force, "plan", story.p("arc", batch)):
        first = story.version() == 0
        task = (f"Nhiệm vụ: {'LẬP sổ tay v1' if first else 'CẬP NHẬT sổ tay'} và LẬP ĐỀ CƯƠNG LÔ {batch} "
                f"(chương {chapters[0]}–{chapters[-1]}) từ các thẻ chương dưới đây. Trả về các file: bible.md, "
                "characters.md, ledger.md, arc.md, rename_map.json (JSON cùng cấu trúc bảng tên hiện tại, thêm tên mới, "
                "giữ nguyên tên cũ; có thể thêm khoá `address` cho quy ước xưng hô), changes.md (gạch đầu dòng: thêm/sửa "
                "gì trong sổ tay, lý do, chương nguồn).")
        cards = "\n\n".join(story.p("card", n).read_text(encoding="utf-8") for n in chapters)
        need_files = ["bible.md", "characters.md", "ledger.md", "arc.md", "rename_map.json"]
        text, *_ = ask(story, "story-lead", "\n\n".join([task, bible_pack(story), "## Thẻ chương của lô\n" + cards]),
                       batch, "plan", check=lambda t: bible_problems(story, t, need_files))
        v = write_bible_files(story, split_files(text), batch, f"lập đề cương ch.{chapters[0]}–{chapters[-1]}")
        story.log(chapter=batch, step="plan", result="ok", note=f"sổ tay v{v}")
    if story.version() >= 1 and not story.meta.get("bible_approved"):
        raise Stop(f"Sổ tay v{story.version()} đã lập ở {story.bible.relative_to(ROOT)}/. Người sáng lập đọc và duyệt, "
                   "rồi thêm `bible_approved: true` vào story.yaml và chạy lại lệnh.")


# ── D. Viết → soát → duyệt từng chương ────────────────────────────────────────────────────────────────
def text_step(story: Story, n: int, force: set[str], feedback: str = "") -> None:
    writer_role = "scriptwriter-light" if story.mode == "light" else "scriptwriter"
    level, writer = 0, ""
    for attempt in range(story.cfg["pipeline"]["rewrite_attempts"] + 1):
        redo = bool(attempt or feedback)
        if redo or need(force, "write", story.p("draft", n)):
            text, level, writer = ask(story, writer_role, write_brief(story, n, feedback), n, "write", level,
                                      check=lambda t: "không đọc được chương gốc" if NO_SOURCE in t[:200] else None)
            script, _, proposal = text.partition(PROPOSAL_MARK)
            story.p("draft", n).parent.mkdir(parents=True, exist_ok=True)
            story.p("draft", n).write_text(script.strip() + "\n", encoding="utf-8")
            story.p("proposal", n).write_text(f"# Đề xuất sổ tay từ chương {n} (viết theo sổ tay v{story.version()})\n"
                                              + (proposal.strip() or "(không)") + "\n", encoding="utf-8")
        fast = bool(story.cfg["pipeline"].get("fast"))
        ai_edit = False
        if fast and (redo or need(force, "edit", story.p("edit", n))):
            # chế độ nhanh: soát bằng code (thay từ cấm, bỏ markdown); chỉ gọi người soát AI khi máy vẫn thấy lỗi
            text = story.p("draft", n).read_text(encoding="utf-8")
            for w, r in load_names(story).get("banned", {}).items():
                text = re.sub(rf"(?<!\w){re.escape(w)}(?!\w)", r, text)
            text = re.sub(r"^\s*(#+|[-*•]|\d+\.)\s+", "", text, flags=re.M).replace("**", "").replace("__", "")
            if script_problems(text, story) is None:
                story.p("edit", n).write_text(text.strip() + "\n", encoding="utf-8")
                story.log(chapter=n, step="edit", model="code", result="ok", note="chế độ nhanh: máy soát")
            else:
                ai_edit = True
        if (not fast or ai_edit) and (redo or ai_edit or need(force, "edit", story.p("edit", n))):
            banned = load_names(story).get("banned", {})
            brief = "Soát kịch bản dưới đây. Bảng tên:\n" + json.dumps(load_names(story), ensure_ascii=False) + \
                ("\n\n## Từ cấm (BẮT BUỘC thay ở mọi chỗ, kể cả trong thoại)\n" +
                 "\n".join(f"- {w} → {r}" for w, r in banned.items()) if banned else "") + \
                "\n\n## Kịch bản\n" + story.p("draft", n).read_text(encoding="utf-8")
            text, *_ = ask(story, "editor", brief, n, "edit", check=lambda t: script_problems(t, story))
            story.p("edit", n).write_text(text.partition(PROPOSAL_MARK)[0].strip() + "\n", encoding="utf-8")
        every = int(story.cfg["pipeline"].get("fast_review_every", 5))
        if fast and not redo and not ai_edit and n % every and need(force, "review", story.p("review", n)):
            story.p("review", n).write_text("Kết luận: ĐẠT (chế độ nhanh: máy kiểm đạt, không gọi duyệt; duyệt mẫu mỗi "
                                            f"{every} chương)\n", encoding="utf-8")
            story.log(chapter=n, step="review", model="code", result="ĐẠT", note="chế độ nhanh: bỏ qua duyệt AI")
        elif redo or ai_edit or need(force, "review", story.p("review", n)):
            text, *_ = ask(story, "content-reviewer", review_brief(story, n), n, "review", avoid=writer,
                           check=lambda t: None if verdict(t) is not None else "thiếu dòng 'Kết luận:'")
            story.p("review", n).write_text(text + "\n", encoding="utf-8")
        if verdict(story.p("review", n).read_text(encoding="utf-8")) is True:
            return
        if story.cfg["pipeline"].get("patch", True) and patch_step(story, n, writer):
            return                                   # sửa khoanh vùng đúng các câu bị chỉ ra, duyệt lại đã ĐẠT
        feedback, level = story.p("review", n).read_text(encoding="utf-8"), level + 1
        story.log(chapter=n, step="review", result="CHƯA ĐẠT", note=f"viết lại lần {attempt + 1}")
    if story.cfg["pipeline"].get("fast"):     # chế độ nhanh (Người sáng lập 28/9/2026: chạy hết quy trình, không dừng sửa)
        story.log(chapter=n, step="review", result="CHẤP NHẬN",
                  note=f"chế độ nhanh: hết lần viết lại, giữ bản cuối; lỗi còn lại xem {story.p('review', n).name}")
        return
    raise Stop(f"Chương {n}: duyệt CHƯA ĐẠT sau {story.cfg['pipeline']['rewrite_attempts']} lần viết lại, "
               f"xem {story.p('review', n).relative_to(ROOT)}")


def patch_apply(story: Story, n: int, review: str) -> bool:
    """SỬA KHOANH VÙNG: người soát trả JSON {"fixes": [{"old", "new"}]} chỉ cho các câu bị nhận xét chỉ ra; máy thay đúng
    chỗ (câu cũ phải có nguyên văn trong kịch bản) và kiểm máy. Không được thì False (để viết lại cả chương)."""
    script = story.p("edit", n).read_text(encoding="utf-8")
    brief = ("Người duyệt chấm CHƯA ĐẠT kịch bản dưới đây. Chỉ SỬA ĐÚNG các câu bị chỉ ra (giữ nguyên mọi câu khác, giữ "
             "giọng văn). Trả về DUY NHẤT JSON: {\"fixes\": [{\"old\": \"câu cũ chép NGUYÊN VĂN từ kịch bản\", \"new\": "
             "\"câu thay thế\"}]}. Nếu lỗi không sửa được bằng vài câu (sai cả mạch, thiếu cả đoạn) thì trả {\"fixes\": []}."
             "\n\n## Nhận xét của người duyệt\n" + review + "\n\n## Kịch bản\n" + script)
    try:
        text, *_ = ask(story, "editor", brief, n, "patch")
        data = parse_json(text)
        fixes = data.get("fixes") if isinstance(data, dict) else None
    except Exception:  # noqa: BLE001  không đọc được thì viết lại cả chương
        return False
    if not isinstance(fixes, list) or not fixes:
        return False
    new = script
    for f in fixes:
        old, rep_ = (f.get("old"), f.get("new")) if isinstance(f, dict) else (None, None)
        if not isinstance(old, str) or not isinstance(rep_, str) or not old.strip() or old not in new:
            return False                                 # câu cũ không có nguyên văn → không đoán, viết lại cả chương
        new = new.replace(old, rep_, 1)
    if script_problems(new, story):
        return False
    story.p("edit", n).write_text(new, encoding="utf-8")
    story.log(chapter=n, step="patch", model="editor", result="ok", note=f"sửa khoanh vùng {len(fixes)} câu")
    return True


def patch_step(story: Story, n: int, writer: str) -> bool:
    """Duyệt CHƯA ĐẠT → sửa khoanh vùng theo nhận xét rồi duyệt lại. Rẻ hơn nhiều so với viết lại + soát + duyệt."""
    if not patch_apply(story, n, story.p("review", n).read_text(encoding="utf-8")):
        return False
    text, *_ = ask(story, "content-reviewer", review_brief(story, n), n, "review", avoid=writer,
                   check=lambda t: None if verdict(t) is not None else "thiếu dòng 'Kết luận:'")
    story.p("review", n).write_text(text + "\n", encoding="utf-8")
    ok = verdict(text) is True
    story.log(chapter=n, step="review", result="ĐẠT" if ok else "CHƯA ĐẠT", note="sau sửa khoanh vùng")
    return ok


# ── E. Nhóm trưởng kiểm mạch cả lô ──────────────────────────────────────────────────────────────────
LINE = re.compile(r"^\W*Chương\s*(\d+)\W+(KHỚP|LỆCH)\b(.*)$", re.M | re.I)


def continuity_step(story: Story, batch: int, chapters: list[int], force: set[str], parallel) -> None:
    if not need(force, "continuity", story.p("check", batch)) and \
            verdict(story.p("check", batch).read_text(encoding="utf-8")) is True:
        return
    old = story.p("check", batch)
    if "continuity" not in force and old.exists():  # lần trước đã chỉ ra chương lệch: sửa luôn, khỏi kiểm lại từ đầu
        off = {int(n): (tag + rest).strip() for n, tag, rest in LINE.findall(old.read_text(encoding="utf-8"))
               if tag.upper() == "LỆCH" and int(n) in chapters}
        if off:
            story.log(chapter=batch, step="continuity", result="LỆCH", note=f"dùng kết quả cũ: chương {sorted(off)}")
            parallel(lambda s, n, f: fix_off(s, n, f, off[n]), sorted(off))
    for rnd in range(story.cfg["pipeline"]["continuity_rounds"] + 1):
        scripts = "\n\n".join(f"### Kịch bản chương {n}\n" + story.p("edit", n).read_text(encoding="utf-8")
                              for n in chapters)
        task = (f"Nhiệm vụ: KIỂM MẠCH lô {batch} (chương {chapters[0]}–{chapters[-1]}). Đối chiếu từng kịch bản với sổ tay "
                "và đề cương, và chéo giữa các chương: xưng hô, tên, trạng thái nhân vật (tiền, tuổi, năng lực, ai biết "
                "gì), dữ kiện, thời gian, cài cắm, điều bị tiết lộ trước. Chỉ báo LỆCH khi có mâu thuẫn cụ thể (trích "
                "câu). Dòng đầu 'Kết luận: ĐẠT' hoặc 'Kết luận: CHƯA ĐẠT'; sau đó MỖI chương một dòng: "
                "'Chương N: KHỚP' hoặc 'Chương N: LỆCH — <trích câu> → <phải sửa thế nào>'.")
        text, *_ = ask(story, "story-lead", "\n\n".join([task, bible_pack(story, batch), scripts]), batch, "continuity",
                       ladder_key="continuity",
                       check=lambda t: None if verdict(t) is not None and len(LINE.findall(t)) >= len(chapters)
                       else "thiếu kết luận hoặc thiếu dòng từng chương")
        story.p("check", batch).parent.mkdir(parents=True, exist_ok=True)
        story.p("check", batch).write_text(text + "\n", encoding="utf-8")
        off = {int(n): (tag + rest).strip() for n, tag, rest in LINE.findall(text)
               if tag.upper() == "LỆCH" and int(n) in chapters}
        if verdict(text) is True and not off:
            story.log(chapter=batch, step="continuity", result="ĐẠT", note=f"vòng {rnd}")
            return
        if rnd == story.cfg["pipeline"]["continuity_rounds"]:
            if story.cfg["pipeline"].get("fast"):     # chế độ nhanh: lỗi vặt cuối cùng sửa khoanh vùng rồi đi tiếp
                parallel(lambda s, n, f: fix_off(s, n, f, off[n]), sorted(off))
                story.log(chapter=batch, step="continuity", result="CHẤP NHẬN",
                          note=f"chế độ nhanh: hết {rnd + 1} vòng, đã sửa khoanh vùng chương {sorted(off)}, không kiểm lại")
                return
            break
        story.log(chapter=batch, step="continuity", result="LỆCH", note=f"vòng {rnd}: chương {sorted(off)}")
        parallel(lambda s, n, f: fix_off(s, n, f, off[n]), sorted(off))
    raise Stop(f"Lô {batch}: kiểm mạch vẫn lệch sau {story.cfg['pipeline']['continuity_rounds']} vòng, "
               f"xem {story.p('check', batch).relative_to(ROOT)}")


def fix_off(story: Story, n: int, force: set[str], note: str) -> None:
    """Chương lệch mạch: thử sửa khoanh vùng đúng câu nhóm trưởng chỉ ra; không được mới viết lại cả chương."""
    if story.cfg["pipeline"].get("patch", True) and patch_apply(story, n, "Nhóm trưởng kiểm mạch báo lệch:\n" + note):
        return
    text_step(story, n, force, "Nhóm trưởng kiểm mạch báo lệch:\n" + note)


# ── F. Nhóm trưởng cập nhật sổ tay ────────────────────────────────────────────────────────────────────
def update_step(story: Story, batch: int, chapters: list[int], force: set[str]) -> None:
    log = story.bible / "CHANGELOG.md"
    done = log.exists() and re.search(rf"^## v\d+ — lô {batch}: cập nhật", log.read_text(encoding="utf-8"), re.M)
    if done and "update" not in force:
        return
    proposals = "\n\n".join(story.p("proposal", n).read_text(encoding="utf-8") for n in chapters
                            if story.p("proposal", n).exists())
    task = (f"Nhiệm vụ: CẬP NHẬT SỔ TAY sau lô {batch} (chương {chapters[0]}–{chapters[-1]}) đã duyệt. Gộp các đề xuất "
            "dưới đây (đối chiếu thẻ chương, bỏ đề xuất không có căn cứ), cập nhật trạng thái nhân vật về cuối lô, thêm "
            "dữ kiện và cài cắm mới, đóng cài cắm đã trả. Trả về: bible.md, characters.md, ledger.md, rename_map.json "
            "(nếu có tên mới), changes.md.")
    cards = "\n\n".join(story.p("card", n).read_text(encoding="utf-8") for n in chapters)
    text, *_ = ask(story, "story-lead", "\n\n".join([task, bible_pack(story, batch), "## Đề xuất của người viết\n" +
                                                     proposals, "## Thẻ chương của lô\n" + cards]), batch, "update",
                   check=lambda t: bible_problems(story, t, ["bible.md", "characters.md", "ledger.md"]))
    v = write_bible_files(story, split_files(text), batch, f"cập nhật sau ch.{chapters[0]}–{chapters[-1]}")
    story.log(chapter=batch, step="update", result="ok", note=f"sổ tay v{v}")


# ── G. Giọng đọc ─────────────────────────────────────────────────────────────────────────────────────
def voice_step(story: Story, n: int, force: set[str]) -> None:
    mp3, script = story.p("mp3", n), story.p("edit", n)
    stale = mp3.exists() and mp3.stat().st_mtime < script.stat().st_mtime  # kịch bản sửa sau khi đọc giọng
    if not stale and not need(force, "voice", mp3, story.p("srt", n)):
        return
    t = story.channel["tts"]
    voice = t["voice"]
    dur = tts.vieneu(story.p("edit", n).read_text(encoding="utf-8"), voice, story.p("mp3", n), story.p("srt", n),
                     story.dir / "render" / f"{n:03d}_vieneu_{voice.replace(' ', '_')}", float(t["speed"]),
                     workers=int(story.cfg["pipeline"].get("tts_workers", 3)))
    story.log(chapter=n, step="voice", model=f"vieneu:{voice}", result="ok", note=f"{dur / 60:.1f} phút")


def run(story: Story, chapters: list[int], force: set[str], workers: int) -> list[int]:
    """Chạy từng lô; trả về các chương đã xong trọn (có mp3). Lô lỗi thì dừng, không chạy lô sau."""
    force, done = expand(force), []

    def parallel(fn, todo):
        failed = {}
        with ThreadPoolExecutor(max_workers=workers) as ex:
            futs = {n: ex.submit(fn, story, n, force) for n in todo}
        for n, f in futs.items():
            if e := f.exception():
                if not isinstance(e, Stop):
                    story.log(chapter=n, step="error", result="lỗi", note=f"{type(e).__name__}: {e}"[:500])
                failed[n] = str(e)
        if failed:
            raise Stop("; ".join(f"chương {n}: {why}" for n, why in failed.items()))

    batches: dict[int, list[int]] = {}
    for n in chapters:
        batches.setdefault(story.batch_of(n), []).append(n)
    for batch, chs in batches.items():
        if story.mode == "none":                    # kịch bản nhập sẵn (drama import): không viết/duyệt, đi thẳng sang giọng đọc
            if miss := [n for n in chs if not story.p("edit", n).exists()]:
                raise Stop(f"rewrite: none nhưng thiếu script/{miss[0]:03d}.txt")
            for n in chs:
                voice_step(story, n, force)
            done += chs
            continue
        parallel(card_step, chs)
        plan_step(story, batch, chs, force)
        parallel(text_step, chs)
        continuity_step(story, batch, chs, force, parallel)
        update_step(story, batch, chs, force)
        for n in chs:
            voice_step(story, n, force)
        done += chs
    return done


def do_render(story: Story, chapters: list[int], title: str) -> pathlib.Path:
    a, b = chapters[0], chapters[-1]
    tag = f"{a:03d}-{b:03d}"
    out = story.dir / "output"
    marks = render.join_audio([(story.p("mp3", n), story.p("srt", n)) for n in chapters],
                              story.dir / "render" / f"full_{tag}.mp3", out / f"full_{tag}.srt")
    (out / f"full_{tag}.chapters.txt").write_text(
        "".join(f"{tts.to_ts(t).split(',')[0]} Chương {int(name)}\n" for t, name in marks), encoding="utf-8")
    frame = story.dir / "render" / f"full_{tag}_frame.png"
    render.make_frame(title, f"Chương {a}–{b} · {story.channel['name']} kể",
                      story.channel_dir / story.channel["brand"]["mascot_reference"], frame)
    mp4 = out / f"full_{tag}.mp4"
    dur = render.video(frame, story.dir / "render" / f"full_{tag}.mp3", out / f"full_{tag}.srt", mp4)
    story.log(step="render", result="ok", note=f"{mp4.relative_to(ROOT)} {dur / 60:.1f} phút")
    return mp4


def parse_range(s: str) -> list[int]:
    a, _, b = s.partition("-")
    return list(range(int(a), int(b or a) + 1))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("slug")
    ap.add_argument("--chapters", required=True, help="ví dụ 1-10 hoặc 3")
    ap.add_argument("--workers", type=int, help="số chương làm song song (mặc định theo config.yaml)")
    ap.add_argument("--force", action="append", default=[], choices=STEPS, help="làm lại bước này và các bước sau")
    ap.add_argument("--render", action="store_true", help="ghép các chương thành 1 video")
    ap.add_argument("--title", help="tiêu đề trên khung video (mặc định: title_vi)")
    a = ap.parse_args()
    story, chapters = Story(a.slug), parse_range(a.chapters)
    try:
        run(story, chapters, set(a.force), a.workers or story.cfg["pipeline"]["workers"])
        if a.render:
            print("Video:", do_render(story, chapters, a.title or story.meta["title_vi"]))
    except Stop as e:
        story.log(step="stop", result="dừng", note=str(e))
        print("DỪNG:", e, file=sys.stderr)
        return 2
    except Exception as e:
        story.log(step="error", result="lỗi", note=f"{type(e).__name__}: {e}"[:500])
        raise
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
