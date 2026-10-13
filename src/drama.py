"""TRUYỆN TỰ VIẾT (drama ngắn 30–60 phút): nhóm trưởng (agy, Gemini Pro) nhận MÔ-TÍP + DÀN Ý THAM KHẢO (bóc cấp cao từ
truyện đang có, kiểu 拆书 + 仿写) và viết TRUYỆN MỚI: sổ tay (bible, nhân vật, sổ dữ kiện, đề cương) + thẻ từng phần theo
đúng định dạng run.py dùng, đánh dấu phần có đoạn mồi TikTok. Sau đó `python -m src.run <slug> --chapters 1-N` viết
kịch bản từng phần, đọc giọng như truyện thường (không đọc truyện gốc vì rewrite: deep).

python -m src.drama import <slug> <file.md> [--force]
  nhập truyện đã viết sẵn (Gemini/người): tên, thể loại, tóm tắt, các phần đánh số → story.yaml (rewrite: none), script/NNN.txt,
  cast.yaml (tên riêng tự dò), outline/hook.md, bible tối thiểu. Dây chuyền bỏ qua bước viết, đi thẳng sang giọng đọc.

python -m src.drama new <slug> --motif "<mô-típ>" [--ref docs/research/...md | stories/<slug>/source/goc.txt] [--parts 6] [--minutes 5]
--ref có thể là cả truyện nguồn tải về (lưu ở stories/<slug>/source/, không sửa): chỉ làm tài liệu, truyện viết ra là truyện mới.
Không chép lời, không giữ tên/chi tiết đặc trưng của truyện tham khảo: chỉ học khung tình tiết.
"""
import argparse
import pathlib
import re
import unicodedata

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORIES = ROOT / "stories"


def prompt(motif: str, ref: str, parts: int, minutes: int) -> str:
    return f"""Nhiệm vụ: VIẾT TRUYỆN DRAMA NGẮN MỚI cho kênh kể chuyện hoạt hình (người kể giọng nữ, tiếng Việt), dài khoảng
{parts * minutes} phút, chia {parts} PHẦN (mỗi phần ~{minutes} phút đọc, ~{minutes * 230} từ khi viết thành kịch bản).

Mô-típ: {motif}

Yêu cầu nội dung:
- Truyện HOÀN TOÀN MỚI: đặt tên nhân vật mới (tên Hán Việt kiểu truyện Trung, bối cảnh thành phố Trung Quốc hiện đại),
  tình tiết và chiêu trò viết khác đi. Dàn ý tham khảo bên dưới CHỈ để học khung nhịp; không giữ tên, câu thoại, chi tiết
  đặc trưng của nó.
- Nhịp "sảng văn": phần 1 vào thẳng lúc bị ức hiếp (không kể xuất thân dài); cuối phần 2 có cú vả mặt nhỏ đầu tiên; giữa
  truyện kẻ ác dồn ép, nữ chính âm thầm giăng lưới; phần cuối lật mặt trước đám đông, kẻ ác trả giá, kết sảng khoái.
- Mỗi phần kết bằng một móc câu.
- Thẻ phần 1 có thêm mục "## Mở đầu 30 giây": 2–3 câu đầu giữ chân người nghe (cảnh đắt nhất kể vượt lên trước, hoặc câu
  sốc, hoặc câu hỏi), chưa chào kênh.
- Chọn đoạn MỒI TIKTOK (3–5 phút) theo công thức: 1–2 câu mở đầu → CAO TRÀO 1 trọn vẹn (cú vả mặt nhỏ đầu tiên,
  thường cuối phần 2) → leo tiếp tới sát ĐỈNH 2 và NGẮT ngay trước khi đỉnh 2 nổ (người xem phải sang YouTube để biết kết
  quả/hậu quả). Có thể ghép nhiều khúc từ phần 1–3. Tuyệt đối không lấy từ phần cuối (lộ kết).
- Nhân vật ít (4–7 vai), mỗi vai có ngoại hình ngắn (để phòng Thiết kế ghép diễn viên chibi) và bối cảnh chính (để chọn nền:
  phòng khách, phòng ngủ, văn phòng, phòng giám đốc, nhà hàng, quán bar, phố, bệnh viện…).

Trả về các file theo đúng định dạng nhiều file:
- bible.md, characters.md, ledger.md, arc.md (đề cương cả truyện: coi là lô 1), rename_map.json (JSON:
  {{"_note": "...", "characters": {{"<tên>": "<tên>"}}, "places": {{}}, "terms": {{}}, "banned": {{}}}}), changes.md
- card_01.md … card_{parts:02d}.md: thẻ từng phần, mỗi thẻ bắt đầu bằng dòng "# Thẻ chương N" và có mục "## Diễn biến"
  (10–16 nhịp đánh số, mỗi nhịp 1–2 câu, có thoại chính trong ngoặc kép), "## Nhân vật xuất hiện", "## Bối cảnh",
  "## Móc câu cuối phần". Thẻ dài ít nhất 1500 ký tự.
- cast.yaml: mục lục truyện → thư viện, YAML đúng dạng:
  lead: <tên nữ chính>
  characters: {{<tên>: {{actor: {{slug}}-<vai không dấu, vd vo, chong, tieu-tam>, outfit: "", names: [<cách gọi khác>],
                note: "<giới, tuổi, ngoại hình, trang phục 1 dòng>"}}}}
  scenes: {{<id nền trong danh sách dưới>: [<3–6 từ khoá tiếng Việt xuất hiện trong lời kể khi ở nơi đó>]}}
  chapters: {{1: {{scene: <id nền mở đầu phần 1>}}, 2: ..., ...}}
  Danh sách nền được phép (chỉ chọn trong này): {{scenes}}
- hook.md: dòng đầu "Phần N" (phần chứa cao trào 1, phải là 1 hoặc 2); dòng "Cao trào 1: phần X nhịp a–b"; dòng
  "Đỉnh 2 (ngắt trước): phần Y nhịp c–d"; 2–3 câu tóm tắt; dòng
  "Câu chữ lớn: ..." (≤ 12 từ) gây ức chế/tò mò nhưng KHÔNG LỘ KẾT QUẢ (không nói ai thắng, không nói bí mật).
- title.md: 5 tiêu đề video tiếng Việt câu view (không giật tít sai sự thật), 1 dòng mô tả truyện.

Tài liệu tham khảo: dàn ý hoặc CẢ TRUYỆN NGUỒN (thường tiếng Trung). Cách dùng "giữ khung, thay thịt": được giữ mạch tình
tiết, các cú lật và điểm sảng; PHẢI thay toàn bộ tên người và nơi chốn, nghề nghiệp, chi tiết đặc trưng (đồ vật, sự kiện gây
mâu thuẫn), và TỰ VIẾT MỚI mọi lời kể, lời thoại (không dịch câu nào). Thêm ít nhất 2 tình tiết mới của riêng mình.
{ref or "(không có — tự dựng theo mô-típ)"}
"""


def new(slug: str, motif: str, ref_path: str | None, parts: int, minutes: int) -> pathlib.Path:
    from src import run
    from src.common import agy
    d = ROOT / "stories" / slug
    if (d / "story.yaml").exists():
        raise SystemExit(f"Đã có truyện {slug}")
    d.mkdir(parents=True, exist_ok=True)              # có thể đã có source/ (truyện nguồn tải về)
    (d / "story.yaml").write_text(yaml.safe_dump({
        "title_vi": slug, "title_zh": "", "channel": "khoai-tay-review", "genre": ["drama"], "status": "thu-nghiem",
        "source": "original", "motif": motif, "reference": ref_path or "", "rewrite": "deep", "parts": parts,
        "bible_approved": True,          # thử nghiệm: Người sáng lập xem bản TikTok trước rồi mới duyệt cả truyện
        "pipeline": {"fast": True, "batch_size": parts, "continuity_rounds": 1}}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    ref = (ROOT / ref_path).read_text(encoding="utf-8")[:60000] if ref_path else ""   # dàn ý, hoặc cả truyện nguồn (1–3 vạn chữ)
    role = (ROOT / "prompts/roles/story-lead.md").read_text(encoding="utf-8")
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))
    model = cfg["agents"]["story-lead"][0]
    need = ["bible.md", "characters.md", "ledger.md", "arc.md", "rename_map.json", "hook.md", "cast.yaml"] + \
        [f"card_{i:02d}.md" for i in range(1, parts + 1)]
    files = {}
    for _ in range(2):
        scenes = ", ".join(sorted(p.parent.name for p in (ROOT / "assets/scenes").glob("*/master.jpg")))
        task = prompt(motif, ref, parts, minutes).replace("{slug}", slug).replace("{scenes}", scenes)
        text = agy.run(role + "\n\n## Nhiệm vụ lần này\n" + task, model, timeout=1800)["text"]
        files = run.split_files(text)
        if all(k in files for k in need):
            break
    missing = [k for k in need if k not in files]
    if missing:
        raise SystemExit(f"Nhóm trưởng trả thiếu file: {missing}")
    story = run.Story(slug)
    run.write_bible_files(story, files, 1, f"lập truyện tự viết từ mô-típ: {motif[:60]}")
    for i in range(1, parts + 1):
        story.p("card", i).parent.mkdir(parents=True, exist_ok=True)
        card = files[f"card_{i:02d}.md"]
        if not re.search(rf"#\s*Thẻ chương\s*{i}\b", card):
            card = f"# Thẻ chương {i}\n\n" + card
        story.p("card", i).write_text(card.strip() + "\n", encoding="utf-8")
    from src.contracts import require
    cast = yaml.safe_load(re.sub(r"^```\w*|```$", "", files["cast.yaml"].strip(), flags=re.M))
    require("cast", cast, "cast.yaml (nhóm trưởng)")
    (d / "cast.yaml").write_text(yaml.safe_dump(cast, allow_unicode=True, sort_keys=False), encoding="utf-8")
    (d / "outline").mkdir(exist_ok=True)
    for extra in ("hook.md", "title.md"):
        if extra in files:
            (d / "outline" / extra).write_text(files[extra].strip() + "\n", encoding="utf-8")
    m = re.search(r"#\s*(?:Tiêu đề|1\.)\s*(.+)", files.get("title.md", ""))
    meta = yaml.safe_load((d / "story.yaml").read_text(encoding="utf-8"))
    if m:
        meta["title_vi"] = m.group(1).strip().strip("*")
    (d / "story.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return d


# ── drama import: truyện viết sẵn → thư mục truyện ─────────────────────────────────────────────────────
PART_RX = re.compile(r"^\s*(?:#+\s*)?\**\s*(?:ph[ầa]n\s*)?(\d+)\s*[.):：]?\s*\**\s*$", re.I)
META_RX = re.compile(r"^\s*(Thể loại|Nguồn cảm hứng|Tóm tắt)\s*[:：]\s*(.*)$", re.I)
HEAD_RX = re.compile(r"^\W*TRUYỆN\s*\d*\s*[:：.\-–]\s*(.+)$", re.I)
CONTENT_RX = re.compile(r"^\W*NỘI DUNG(\s+TRUYỆN)?\W*$", re.I)
HONORIFICS = {"bà", "ông", "cô", "anh", "chị", "bác", "chú", "dì", "cậu", "mợ", "thím", "lão", "tiểu", "a"}
ALIAS_FIRST = {"tiểu", "a", "lão"}
MIN_WORDS = 600


def parse_story(text: str, slug: str) -> dict:
    """Tách khối đầu (tên, thể loại, tóm tắt) và các phần đánh số. Phần phải đánh số liên tiếp 1, 2, 3…"""
    lines = text.replace("\r\n", "\n").split("\n")
    marks, want = [], 1
    for i, ln in enumerate(lines):
        m = PART_RX.match(ln)
        if m and int(m.group(1)) == want:
            marks.append(i)
            want += 1
    if not marks:
        raise SystemExit("Không thấy phần đánh số (dòng riêng '1.', 'Phần 1', '## 1', '1)')")
    title, orig, meta = slug, "", {}
    for ln in lines[:marks[0]]:
        s = ln.strip().strip("*#").strip()
        if (h := HEAD_RX.match(s)) and title == slug:
            title = h.group(1).strip()
            if (o := re.search(r"\(([^()]*)\)\s*$", title)):
                orig, title = o.group(1).strip(), title[:o.start()].strip()
        elif (m := META_RX.match(s)):
            meta[m.group(1).lower()] = m.group(2).strip()
    parts = []
    for k, a in enumerate(marks):
        b = marks[k + 1] if k + 1 < len(marks) else len(lines)
        body = [ln.strip() for ln in lines[a + 1:b]]
        parts.append(re.sub(r"\n{3,}", "\n\n", "\n".join(body)).strip())
    genre = [g.strip() for g in re.split(r"[,;]", meta.get("thể loại", "")) if g.strip()]
    return {"title": title, "title_zh": orig, "genre": genre or ["drama"], "motif": meta.get("tóm tắt", ""), "parts": parts}


def ascii_slug(name: str) -> str:
    s = unicodedata.normalize("NFD", name.replace("đ", "d").replace("Đ", "D"))
    return re.sub(r"[^a-z0-9]+", "-", "".join(c for c in s if not unicodedata.combining(c)).lower()).strip("-")


def find_names(text: str, min_count: int = 3) -> tuple[str, dict]:
    """Dò tên riêng: chuỗi 2–4 từ viết hoa chữ đầu (hoặc xưng hô thường + tên: 'bà Trương') lặp ≥ min_count lần.
    Tên ngắn nằm trong tên dài (Uyển Thanh / Lâm Uyển Thanh) và 'Tiểu X' gộp vào một nhân vật. Trả về (lead, {tên: {names, count}})."""
    low = {}
    for w in re.findall(r"[^\W\d_]+", text):
        low[w] = low.get(w, 0) + 1
    runs = []
    for line in text.split("\n"):
        run = []
        for m in re.finditer(r"[^\W\d_]+|[^\w\s]|\d+", line):
            w = m.group(0)
            gap = line[m.start() - 1] == " " if m.start() else False
            if w[:1].isalpha() and w[0].isupper() and w.upper() != w and (not run or gap):
                run.append(w)
            elif w[:1].isalpha() and w.lower() in HONORIFICS and not run:
                run = [w.capitalize() + "\0"]                  # xưng hô viết thường: giữ nếu liền sau là tên viết hoa
            else:
                if len(run) > 1 or (run and not run[0].endswith("\0")):
                    runs.append(run)
                run = []
        if len(run) > 1 or (run and not run[0].endswith("\0")):
            runs.append(run)
    cnt: dict[str, int] = {}
    for run in runs:
        run = [w.rstrip("\0") if i else w for i, w in enumerate(run)]
        run[0] = run[0].rstrip("\0")
        # bỏ từ đầu câu không phải tên (xuất hiện viết thường nhiều hơn viết hoa), trừ xưng hô
        while len(run) > 1 and run[0].lower() not in HONORIFICS and low.get(run[0].lower(), 0) >= low.get(run[0], 1):
            run = run[1:]
        for n in (2, 3, 4):
            for i in range(len(run) - n + 1):
                g = run[i:i + n]
                cnt[" ".join(g)] = cnt.get(" ".join(g), 0) + 1
    cands = {k: v for k, v in cnt.items() if v >= min_count}
    # bỏ ứng viên dài chỉ là tên ngắn cộng một từ đệm (số đếm gần bằng và từ đệm là từ thường gặp)
    for k in list(cands):
        for j in cands:
            if j != k and j in k and len(j.split()) < len(k.split()) and cands[k] < cands[j] * 0.7 \
                    and k.split()[0].lower() not in HONORIFICS and not k.endswith(j):
                cands.pop(k, None)
                break
    # tên ngắn nằm trong tên dài → nhân vật dài; "Tiểu X" → ứng viên kết thúc bằng X
    chars: dict[str, dict] = {}
    for k in sorted(cands, key=lambda x: -len(x.split())):
        host = next((h for h in chars if k != h and f" {k} " in f" {h} "), None)
        if host is None and k.split()[0].lower() in ALIAS_FIRST and len(k.split()) == 2:
            host = next((h for h in chars if h.split()[-1] == k.split()[1]), None)
        if host and k.split()[-1] != host.split()[-1]:
            continue                                         # mảnh đầu tên ("Lâm Uyển"): bỏ, không phải cách gọi
        if host:
            chars[host]["alias"].add(k)
            chars[host]["count"] = max(chars[host]["count"], cands[k]) + (cands[k] if k.split()[0].lower() in ALIAS_FIRST else 0)
        else:
            chars[k] = {"alias": set(), "count": cands[k]}
    for k, c in chars.items():
        w = k.split()
        extra = {" ".join(w[-2:])} if len(w) >= 3 else ({w[-1]} if w[0].lower() in HONORIFICS else set())
        c["names"] = sorted((c["alias"] | extra) - {k}, key=lambda x: (-len(x), x))
    if not chars:
        return "", {}
    quote = re.compile(r'"[^"]*"|“[^”]*”')
    inside = " ".join(quote.findall(text))
    first_person = len(re.findall(r"(?<!\w)tôi(?!\w)", text, re.I)) >= 10

    def share(k):                      # tỉ lệ tên xuất hiện trong thoại (người kể ngôi "tôi" chỉ bị gọi trong thoại)
        forms = [k, *chars[k]["names"]]
        tot = sum(len(re.findall(rf"(?<!\w){re.escape(f)}(?!\w)", text, re.I)) for f in forms)
        ins = sum(len(re.findall(rf"(?<!\w){re.escape(f)}(?!\w)", inside, re.I)) for f in forms)
        return ins / tot if tot else 0
    pool = [k for k in chars if k.split()[0].lower() not in HONORIFICS or len(chars) == 1] or list(chars)
    lead = max(pool, key=(lambda k: (round(share(k), 2), chars[k]["count"])) if first_person else (lambda k: chars[k]["count"]))
    return lead, {k: {"names": c["names"], "count": c["count"]} for k, c in sorted(chars.items(), key=lambda x: -x[1]["count"])}


def import_story(slug: str, src: str, force: bool = False) -> dict:
    from src.contracts import require
    d = STORIES / slug
    if (d / "story.yaml").exists() and not force:
        raise SystemExit(f"Đã có truyện {slug} (thêm --force để ghi đè)")
    path = pathlib.Path(src)
    path = path if path.is_absolute() else ROOT / path
    text = path.read_text(encoding="utf-8")
    st = parse_story(text, slug)
    parts = st["parts"]
    body = "\n\n".join(parts)
    lead, found = find_names(body)
    if not lead:
        raise SystemExit("Không dò được tên nhân vật nào (tên riêng lặp ≥ 3 lần)")
    cast = {"lead": lead, "characters": {k: {"actor": f"{slug}-{ascii_slug(k)}", "outfit": "", "names": v["names"], "note": ""}
                                         for k, v in found.items()}}
    require("cast", cast, "cast.yaml (import)")
    for c in cast["characters"].values():
        require("cast_character", c, "cast.yaml nhân vật (import)")
    try:
        rel = str(path.resolve().relative_to(d.resolve()))
    except ValueError:
        rel = "source/story.md"
    meta = {"title_vi": st["title"], "title_zh": st["title_zh"], "channel": "khoai-tay-review", "genre": st["genre"],
            "status": "thu-nghiem", "source": "imported", "source_file": rel, "motif": st["motif"], "rewrite": "none",
            "parts": len(parts), "bible_approved": True,
            "pipeline": {"fast": True, "batch_size": len(parts), "continuity_rounds": 0}}
    for sub in ("script", "outline", "bible"):
        (d / sub).mkdir(parents=True, exist_ok=True)
    (d / "story.yaml").write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
    for i, p in enumerate(parts, 1):
        (d / "script" / f"{i:03d}.txt").write_text(p + "\n", encoding="utf-8")
    for f in (d / "script").glob("*.txt"):               # nhập lại ít phần hơn: bỏ phần thừa của lần trước
        if f.stem.isdigit() and int(f.stem) > len(parts):
            f.unlink()
    cast_p = d / "cast.yaml"
    if cast_p.exists():                                  # --force: giữ diễn viên đã gán, chỉ thêm nhân vật mới
        old = yaml.safe_load(cast_p.read_text(encoding="utf-8")) or {}
        for k, v in (old.get("characters") or {}).items():
            cast["characters"][k] = v
        cast["lead"] = old.get("lead") or cast["lead"]
    cast_p.write_text(yaml.safe_dump(cast, allow_unicode=True, sort_keys=False), encoding="utf-8")
    sents = re.findall(r".+?(?:[.!?…]+[\"”]?(?=\s|$)|$)", parts[0].replace("\n", " "), re.S)
    first2 = " ".join(s.strip() for s in sents[:2] if s.strip())
    (d / "outline" / "hook.md").write_text(f"Phần 1\n\n{first2}\n", encoding="utf-8")
    (d / "bible" / "bible.md").write_text(f"# {st['title']}\n\n## Tóm tắt\n{st['motif'] or '(không có)'}\n\n"
                                          f"Truyện nhập sẵn ({len(parts)} phần), kịch bản giữ nguyên, không viết lại.\n", encoding="utf-8")
    (d / "bible" / "characters.md").write_text("# Nhân vật\n\n" + "\n".join(
        f"### {k}\n- Gọi khác: {', '.join(v['names']) or '(không)'}\n- Số lần nhắc: {found[k]['count']}"
        + ("\n- Nhân vật chính" if k == lead else "") + "\n" for k, v in cast["characters"].items()), encoding="utf-8")
    (d / "bible" / "ledger.md").write_text("# Sổ dữ kiện\n\n(truyện nhập sẵn, chưa ghi)\n", encoding="utf-8")
    import datetime as dt
    with open(d / "bible" / "CHANGELOG.md", "w", encoding="utf-8") as fh:
        fh.write(f"## v1 — lô 1: nhập truyện viết sẵn từ {rel} ({dt.date.today().isoformat()})\n- sổ tay tối thiểu\n\n")
    (d / "rename_map.json").write_text('{"characters": {}, "places": {}, "terms": {}, "banned": {}}\n', encoding="utf-8")
    return {"dir": d, "lead": lead, "found": found, "words": [len(p.split()) for p in parts]}


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("new")
    a1.add_argument("slug")
    a1.add_argument("--motif", required=True)
    a1.add_argument("--ref")
    a1.add_argument("--parts", type=int, default=6)
    a1.add_argument("--minutes", type=int, default=5)
    a2 = sub.add_parser("import")
    a2.add_argument("slug")
    a2.add_argument("file")
    a2.add_argument("--force", action="store_true")
    a = ap.parse_args()
    if a.cmd == "import":
        r = import_story(a.slug, a.file, a.force)
        for i, w in enumerate(r["words"], 1):
            print(f"Phần {i}: {w} chữ" + (f"  CẢNH BÁO: dưới {MIN_WORDS} chữ, giọng đọc ngắn hơn 3 phút" if w < MIN_WORDS else ""))
        print(f"Số phần: {len(r['words'])}")
        print("Nhân vật:", "; ".join(f"{k} ({v['count']}" + (f", gọi: {', '.join(v['names'])}" if v["names"] else "") + ")"
                                     for k, v in r["found"].items()), "| chính:", r["lead"])
        print("Còn trống: actor là slug giữ chỗ, bảng việc sẽ mở việc thiếu diễn viên; note/outfit để trống.")
        print(f"Tiếp theo: python scripts/drama_pipeline.py {a.slug} --parts {len(r['words'])} --full")
        return 0
    d = new(a.slug, a.motif, a.ref, a.parts, a.minutes)
    print("Xong:", d.relative_to(ROOT), "→ xem outline/hook.md, bible/; rồi: python -m src.run", a.slug,
          f"--chapters 1-{a.parts}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
