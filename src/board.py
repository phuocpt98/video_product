"""BẢNG VIỆC của studio: các phòng giao việc cho nhau qua file (board/), không cần kênh ngoài.

board/tasks/<id>.yaml   1 việc = 1 file (xem mẫu trong docs/plans/studio-org.md §5)
board/events.jsonl      nhật ký chỉ ghi thêm
board/inbox/            Người sáng lập thả ảnh tên <id việc>.png để trả lời việc need-image

Phòng: bien-kich, thiet-ke, boi-canh, dung, nguoi-sang-lap, ky-thuat.
Luồng: dựng chương thiếu diễn viên/nền → treo việc dựng, mở việc sang Thiết kế/Bối cảnh → xong thì việc dựng tự mở lại.

python -m src.board add-render <slug> <chương|a-b>   # giao việc dựng chương
python -m src.board run [--loop 600]                 # chạy các việc máy làm được (lặp mỗi N giây)
python -m src.board list [--all]                     # xem nhanh
python -m src.board done <id> "<ghi chú>"            # đánh dấu xong bằng tay (việc của người)
"""
import argparse
import datetime as dt
import json
import pathlib
import re
import time

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD = ROOT / "board"
TASKS = BOARD / "tasks"
EVENTS = BOARD / "events.jsonl"
INBOX = BOARD / "inbox"
DEPTS = {"bien-kich": "Biên kịch", "thiet-ke": "Thiết kế nhân vật", "boi-canh": "Bối cảnh", "dung": "Dựng",
         "nguoi-sang-lap": "Người sáng lập", "ky-thuat": "Kỹ thuật"}
HUMAN = {"nguoi-sang-lap", "ky-thuat"}          # máy không tự làm việc của hai phòng này


def _now() -> str:
    return dt.datetime.now().strftime("%Y-%m-%d %H:%M")


def _event(**kw) -> None:
    BOARD.mkdir(exist_ok=True)
    with EVENTS.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"at": _now(), **kw}, ensure_ascii=False) + "\n")


def save(t: dict) -> dict:
    from src.contracts import require
    require("task", t, t.get("id", "task"))
    TASKS.mkdir(parents=True, exist_ok=True)
    (TASKS / f"{t['id']}.yaml").write_text(yaml.safe_dump(t, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return t


def get(tid: str) -> dict:
    return yaml.safe_load((TASKS / f"{tid}.yaml").read_text(encoding="utf-8"))


def tasks(status: str | None = None, to: str | None = None) -> list[dict]:
    out = [yaml.safe_load(p.read_text(encoding="utf-8")) for p in sorted(TASKS.glob("*.yaml"))] if TASKS.exists() else []
    return [t for t in out if (status is None or t["status"] == status) and (to is None or t["to"] == to)]


def log(t: dict, by: str, msg: str) -> dict:
    t.setdefault("log", []).append({"at": _now(), "by": by, "msg": msg})
    _event(task=t["id"], by=by, msg=msg, status=t["status"])
    return save(t)


def new(frm: str, to: str, type_: str, need: str, key: str, story: str | None = None, chapter: int | None = None,
        data: dict | None = None) -> dict:
    """Mở việc mới; nếu đã có việc chưa xong cùng key thì dùng lại việc đó (không mở trùng)."""
    for t in tasks():
        if t.get("key") == key and t["status"] != "done":
            return t
    nums = [int(p.stem.rsplit("-", 1)[-1]) for p in TASKS.glob("*.yaml")] if TASKS.exists() else []
    n = max(nums, default=0) + 1                     # số lớn nhất + 1: xoá file việc không làm trùng id
    t = {"id": f"{dt.date.today():%Y%m%d}-{n:04d}", "from": frm, "to": to, "type": type_, "key": key, "story": story,
         "chapter": chapter, "need": need, "data": data or {}, "status": "open", "waiting_on": [], "log": []}
    return log(save(t), frm, f"Mở việc: {need}")


def block(t: dict, deps: list[dict], by: str) -> dict:
    t["status"] = "blocked"
    t["waiting_on"] = sorted({*t.get("waiting_on", []), *(d["id"] for d in deps)})
    return log(t, by, "Treo, chờ: " + ", ".join(f"{d['id']} ({d['need']})" for d in deps))


def done(t: dict, by: str, msg: str) -> dict:
    t["status"] = "done"
    log(t, by, msg)
    for w in tasks(status="blocked"):                 # mở lại việc đang chờ việc này nếu đã đủ
        if t["id"] in w.get("waiting_on", []):
            w["waiting_on"] = [x for x in w["waiting_on"] if get(x)["status"] != "done"]
            if not w["waiting_on"]:
                w["status"] = "open"
                log(w, "board", f"Đủ điều kiện (nhờ {t['id']}), mở lại")
            else:
                save(w)
    return t


# ------------------------------------------------------------------ người làm của từng phòng

def _bible_block(story: str, name: str) -> str:
    md = (ROOT / "stories" / story / "bible" / "characters.md")
    if not md.exists():
        return name
    m = re.search(r"^### " + re.escape(name) + r".*?(?=^### |\Z)", md.read_text(encoding="utf-8"), re.S | re.M)
    return m.group(0).strip() if m else name


def work_render(t: dict) -> None:
    """Dựng: dàn cảnh; thiếu diễn viên → việc Thiết kế, thiếu nền → việc Bối cảnh; đủ thì dựng video."""
    from src.studio import direct, tagger
    slug, ch = t["story"], t["chapter"]
    if not (ROOT / "stories" / slug / "storyboard" / f"{ch:03d}.tags.yaml").exists():
        try:                                          # đạo diễn gắn nhãn (AI miễn phí qua pool); lỗi thì dùng luật từ khoá
            n = len(tagger.tag(slug, ch))
            log(t, "dung", f"Gắn nhãn đạo diễn: {n} câu")
        except Exception as e:  # noqa: BLE001
            log(t, "dung", f"Không gắn được nhãn, dùng luật từ khoá: {str(e)[:120]}")
    sb, missing = direct.direct(slug, ch)
    cast = yaml.safe_load((ROOT / "stories" / slug / "cast.yaml").read_text(encoding="utf-8"))
    deps = []
    for item in sorted(missing["diễn viên"]):
        name, actor = re.match(r"(.+) \((.+)\)$", item).groups()
        c = cast["characters"][name]
        look = next((v for v in (c.get("by_scene") or {}).values() if v.get("actor") == actor), None)
        deps.append(new("dung", "thiet-ke", "need-actor", f"Diễn viên cho {name} ({actor})", f"actor:{actor}", slug, ch,
                        {"name": name, "actor": actor, "outfit_hint": (look or c).get("outfit", ""),
                         "note": (look or c).get("note", "")}))
    for sid in sorted(missing["nền"]):
        deps.append(new("dung", "boi-canh", "need-scene", f"Nền {sid}", f"scene:{sid}", slug, ch, {"scene": sid}))
    if missing["đạo cụ"]:
        log(t, "dung", "Thiếu đạo cụ (bỏ qua, không treo): " + ", ".join(sorted(missing["đạo cụ"])))
    if deps:
        block(t, deps, "dung")
        return
    out = ROOT / "stories" / slug / "storyboard" / f"{ch:03d}.yaml"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.safe_dump(sb, allow_unicode=True, sort_keys=False), encoding="utf-8")
    from src.studio.stage import render
    video = ROOT / "stories" / slug / "output" / f"studio_{ch:03d}_1920x1080.mp4"
    t["status"] = "doing"
    log(t, "dung", "Đủ diễn viên và nền, bắt đầu dựng")
    render(out, "1920x1080", video)
    done(t, "dung", f"Dựng xong {video.relative_to(ROOT)} ({len(sb['shots'])} cảnh)")


def used_heads(story: str, me: str) -> set[str]:
    """Các đầu nền (kiểu tóc) diễn viên khác trong cùng truyện đã dùng."""
    cast = yaml.safe_load((ROOT / "stories" / story / "cast.yaml").read_text(encoding="utf-8"))
    ids = {c["actor"] for c in cast["characters"].values()} | \
        {v["actor"] for c in cast["characters"].values() for v in (c.get("by_scene") or {}).values()}
    out = set()
    for aid in ids - {me}:
        f = ROOT / "assets/actors" / aid / "avatar.yaml"
        if f.exists():
            out.add(yaml.safe_load(f.read_text(encoding="utf-8")).get("head", ""))
    return out - {""}


def work_actor(t: dict) -> None:
    """Thiết kế nhân vật: agy chọn bộ phận từ mục lục kho theo mô tả trong sổ tay → ghép thành diễn viên."""
    from src.studio import avatar
    d = t["data"]
    if (ROOT / "assets/actors" / d["actor"] / "card.yaml").exists():
        done(t, "thiet-ke", f"Đã có sẵn diễn viên {d['actor']} trong thư viện")
        return
    prompt = "\n\n".join([(ROOT / "prompts/roles/character-designer.md").read_text(encoding="utf-8"),
                          "## Mục lục kho bộ phận\n" + (ROOT / "assets/parts/INDEX.md").read_text(encoding="utf-8"),
                          f"## Nhân vật cần thiết kế\n{_bible_block(t['story'], d['name'])}\n"
                          f"Gợi ý trang phục trong mục lục truyện: {d.get('outfit_hint', '')}",
                          "TRÁNH TRÙNG với vai khác cùng truyện (khán giả phải phân biệt được): đầu nền đã dùng: "
                          + ", ".join(sorted(used_heads(t["story"], d["actor"]))),
                          f"GHI CHÚ QUAN TRỌNG (ưu tiên hơn sổ tay): {d['note']}" if d.get("note") else ""])
    from src.common import pool
    spec, res = None, {}
    for _ in range(3):                                   # nhóm nguồn (Gemini API → … → agy); rỗng thì thử lại
        try:
            text, _src = pool.ask("design", prompt, max_tokens=2000)
        except RuntimeError as e:
            text = ""
            log(t, "thiet-ke", f"Nhóm nguồn lỗi: {str(e)[:120]}")
        res = {"text": text}
        m = re.search(r"```(?:yaml)?\s*(.*?)```", res.get("text") or "", re.S)
        try:
            spec = yaml.safe_load(m.group(1) if m else res.get("text") or "")
        except yaml.YAMLError:
            spec = None
        if isinstance(spec, dict):
            break
    if not isinstance(spec, dict):
        raise RuntimeError(f"agy không trả về YAML hợp lệ sau 3 lần: {(res.get('text') or '')[:120]!r}")
    reg = yaml.safe_load((ROOT / "assets/parts/parts.yaml").read_text(encoding="utf-8"))
    outfits = [k.split(":", 1)[1] for k in reg if k.startswith("outfit:")]
    # kiểm và sửa về giá trị hợp lệ thay vì tin AI
    if spec.get("head") not in reg or reg[spec["head"]]["kind"] != "heads":
        spec["head"] = "head-messy"
    if f"{spec.get('eyes')}-normal" not in reg:
        spec["eyes"] = "eyes1"
    if f"{spec.get('mouth')}-neutral" not in reg:
        spec["mouth"] = "mouth1"
    note = (d.get("note") or "").strip().lower()
    sex = "f" if note.startswith("nữ") else "m" if note.startswith("nam") else None     # ghi chú mục lục: "Nữ, 22 tuổi, …"
    body = spec.get("body") or {}
    if body.get("outfit") not in outfits or (sex and not body["outfit"].startswith(sex + "-")):   # AI từng cho nữ mặc đồ nam
        hint = d.get("outfit_hint") or ""
        body["outfit"] = hint if hint in outfits and (not sex or hint.startswith(sex + "-")) else \
            {"f": "f-dress", "m": "m-office"}.get(sex, outfits[0])
    # mũi mặc định Người sáng lập chốt 28/9/2026: nữ nose8, nam nose7 (nose1 chấm đen, nose2 cũ quá mờ)
    if spec.get("nose") not in reg or spec.get("nose") in ("nose1", "nose2"):
        spec["nose"] = "nose8" if body["outfit"].startswith("f-") else "nose7"
    spec["extras"] = [x for x in spec.get("extras") or [] if x in reg]
    if body.get("build") not in ("thin", "normal", "fat"):
        body["build"] = "normal"
    spec["body"] = body
    spec.update({"head_size": 1.0, "adjust": {}, "roles": [f"{d['name']} ({t['story']})"]})
    avatar.build_actor(d["actor"], spec)
    prev = avatar.preview(d["actor"])
    done(t, "thiet-ke", f"Đã ghép {d['actor']}: {spec.get('look', '')} — xem {prev.relative_to(ROOT)} (sửa được ở trang "
                        "tạo nhân vật)")


def work_scene(t: dict) -> None:
    """Bối cảnh: nền đã có thì xong; chưa có thì mở việc xin ảnh gửi Người sáng lập (kèm prompt) và chờ."""
    sid = t["data"]["scene"]
    if (ROOT / "assets/scenes" / sid / "master.jpg").exists():
        done(t, "boi-canh", f"Nền {sid} đã có trong thư viện")
        return
    style = yaml.safe_load((ROOT / "channels/khoai-tay-review/channel.yaml").read_text(encoding="utf-8"))["visual_style"]
    ask = new("boi-canh", "nguoi-sang-lap", "need-image", f"Ảnh nền {sid}", f"image:scene:{sid}", t["story"],
              t["chapter"], {"scene": sid, "save_as": f"board/inbox/<id việc này>.png",
                             "prompt": f"Background for a 2D animated story, NO people, NO text. {style}. Scene: "
                                       f"{sid.replace('-', ' ')}. Eye-level medium-wide 16:9, lower-middle area open "
                                       "for characters to stand. Leave the bottom-right corner plain."})
    block(t, [ask], "boi-canh")


def check_inbox() -> None:
    """Ảnh Người sáng lập thả vào board/inbox/<id>.png → xử lý theo việc tương ứng rồi đánh dấu xong."""
    for f in sorted(INBOX.glob("*.*")) if INBOX.exists() else []:
        try:
            _inbox_one(f)
        except Exception as e:  # noqa: BLE001  ảnh hỏng: cất sang inbox/bad/, ghi vào việc, không làm sập vòng chạy
            bad = INBOX / "bad"
            bad.mkdir(exist_ok=True)
            f.rename(bad / f.name)
            if (TASKS / f"{f.stem}.yaml").exists():
                log(get(f.stem), "board", f"Ảnh trong inbox hỏng ({type(e).__name__}), đã cất vào board/inbox/bad/")


def _inbox_one(f: pathlib.Path) -> None:
    from PIL import Image
    tid = f.stem
    if not (TASKS / f"{tid}.yaml").exists():
        return
    t = get(tid)
    if t["status"] == "done":
        return
    sid = t["data"].get("scene")
    if sid:
        d = ROOT / "assets/scenes" / sid
        d.mkdir(parents=True, exist_ok=True)
        Image.open(f).convert("RGB").save(d / "master.jpg", quality=95)
        if not (d / "card.yaml").exists():
            (d / "card.yaml").write_text(yaml.safe_dump({"id": sid, "type": "establishing", "tags": [sid],
                                                         "characters": [], "master": "master.jpg",
                                                         "frames": ["16:9", "9:16"], "ground_y": 0.9,
                                                         "notes": "Ảnh từ board/inbox", "used_in": []},
                                                        allow_unicode=True, sort_keys=False), encoding="utf-8")
        f.rename(d / f"source_{f.name}")
        done(t, "nguoi-sang-lap", f"Đã nhận ảnh, lưu thành nền {sid}")


WORKERS = {("dung", "render"): work_render, ("thiet-ke", "need-actor"): work_actor, ("boi-canh", "need-scene"): work_scene}


def run_once() -> int:
    """Chỉ một người chạy việc một lúc (khoá board/.lock theo pid). Việc "doing" còn sót (lần trước bị ngắt, Ctrl+C) được
    đưa về "open" để làm lại."""
    import os
    lock = BOARD / ".lock"
    BOARD.mkdir(exist_ok=True)
    if lock.exists():
        try:
            os.kill(int(lock.read_text()), 0)
            print("Đang có người chạy việc khác (board/.lock), bỏ qua lượt này")
            return 0
        except (ProcessLookupError, ValueError):
            pass
    lock.write_text(str(os.getpid()))
    try:
        for t in tasks(status="doing"):
            t["status"] = "open"
            log(t, "board", "Lần trước bị ngắt giữa chừng, mở lại")
        return _run_once()
    finally:
        lock.unlink(missing_ok=True)


def _run_once() -> int:
    check_inbox()
    n = 0
    for t in tasks(status="open"):
        fn = WORKERS.get((t["to"], t["type"]))
        if not fn:
            continue
        try:
            fn(t)
            n += 1
        except Exception as e:  # noqa: BLE001  lỗi (thường là hết quota) ghi vào việc, lần sau thử lại
            t2 = get(t["id"])
            if t2["status"] == "doing":
                t2["status"] = "open"
            log(t2, t["to"], f"Lỗi, sẽ thử lại: {str(e)[:200]}")
    return n


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("add-render")
    a1.add_argument("slug")
    a1.add_argument("chapters")
    a2 = sub.add_parser("run")
    a2.add_argument("--loop", type=int, default=0)
    a3 = sub.add_parser("list")
    a3.add_argument("--all", action="store_true")
    a4 = sub.add_parser("done")
    a4.add_argument("id")
    a4.add_argument("msg")
    a = ap.parse_args()
    if a.cmd == "add-render":
        lo, _, hi = a.chapters.partition("-")
        for ch in range(int(lo), int(hi or lo) + 1):
            t = new("dieu-phoi", "dung", "render", f"Dựng chương {ch}", f"render:{a.slug}:{ch}", a.slug, ch)
            print(t["id"], t["need"], t["status"])
    elif a.cmd == "run":
        while True:
            print(_now(), "làm", run_once(), "việc")
            if not a.loop:
                break
            time.sleep(a.loop)
    elif a.cmd == "list":
        for t in tasks():
            if a.all or t["status"] != "done":
                print(f"{t['id']} [{t['status']:>7}] {DEPTS.get(t['from'], t['from'])} → {DEPTS.get(t['to'], t['to'])}: "
                      f"{t['need']}" + (f"  (chờ {', '.join(t['waiting_on'])})" if t.get("waiting_on") else ""))
    elif a.cmd == "done":
        done(get(a.id), "nguoi-sang-lap", a.msg)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
