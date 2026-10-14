"""DÂY CHUYỀN CHÍNH: 1 file truyện → video hoàn chỉnh. Chia việc nhỏ, việc nào lỗi thì làm lại, đủ hết thì ghép.

  1. Đọc truyện (.txt / .md / .docx), chia thành PHẦN khoảng `part_chars` ký tự (cắt ở ranh giới chương/đoạn).
  2. Mỗi phần có 2 việc: GIỌNG (VieNeu → audio/NNN.mp3 + .srt) rồi VIDEO (hoạt hình ngẫu nhiên reel.py → video/NNN.mp4).
  3. Trạng thái từng việc ghi ở stories/<slug>/tasks.json. Chạy lại cùng lệnh là LÀM TIẾP: việc xong bỏ qua, việc lỗi làm
     lại (mỗi lượt thử tối đa 1 + retries lần).
  4. Đủ mọi phần → ghép thành output/<slug>.mp4 + .srt + upload.md (tiêu đề, mốc từng phần). Đăng lên mạng làm tay.

python -m src.produce run <file truyện> [--slug S] [--size 1080x1920] [--voice "Ngọc Huyền"] [--speed 1.34]
python -m src.produce run --slug S                 # làm tiếp truyện đã nạp
python -m src.produce run --slug S --redo 003 --redo 007:voice   # làm lại phần 3 (cả giọng + video), giọng phần 7
python -m src.produce status S
Hướng dẫn vận hành: README.md
"""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import re
import shutil
import subprocess
import sys
import time
import traceback
import zipfile

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
STORIES = ROOT / "stories"
HEADING = re.compile(r"^\s*(chương|chapter|phần|hồi|quyển|tập)\s*[\dIVXLC]+\b.*$", re.I)


# ───────────────────────────── đọc + chia truyện ─────────────────────────────

def read_story(path: pathlib.Path) -> str:
    if path.suffix.lower() == ".docx":
        xml = zipfile.ZipFile(path).read("word/document.xml").decode("utf-8")
        paras = []
        for p in re.findall(r"<w:p[ >].*?</w:p>", xml, re.S):
            paras.append("".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p)))
        import html
        text = "\n\n".join(html.unescape(x) for x in paras)
    else:
        raw = path.read_bytes()
        encs = ["utf-16"] if raw[:2] in (b"\xff\xfe", b"\xfe\xff") else []   # utf-16 chỉ khi có BOM
        for enc in encs + ["utf-8-sig", "cp1258"]:
            try:
                text = raw.decode(enc)
                break
            except UnicodeDecodeError:
                continue
        else:
            sys.exit(f"Lỗi: không đọc được {path} (không phải UTF-8/UTF-16). Lưu lại file dạng UTF-8 rồi chạy lại.")
    text = text.replace("\r\n", "\n")
    text = re.sub(r"^#+\s*", "", text, flags=re.M)              # tiêu đề markdown → dòng thường
    text = re.sub(r"[*_]{1,3}([^*_\n]+)[*_]{1,3}", r"\1", text)  # bỏ in đậm/nghiêng markdown
    return text.strip()


def split_story(text: str, part_chars: int) -> tuple[str, list[str]]:
    """Trả về (tiêu đề, các phần). Tiêu đề = dòng đầu nếu ngắn và không phải tên chương. Mỗi tên chương mở phần mới;
    đoạn dài hơn giới hạn được cắt theo câu."""
    paras = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\s*\S)", text) if p.strip()]
    title = ""
    if paras and len(paras[0]) <= 120 and not HEADING.match(paras[0]):
        title = paras.pop(0)
    units = []                                                  # (là tên chương?, đoạn)
    for p in paras:
        if len(p) <= part_chars:
            units.append((bool(HEADING.match(p)), p))
            continue
        cur = ""
        for s in re.split(r"(?<=[.!?…])\s+", p):
            if cur and len(cur) + len(s) > part_chars:
                units.append((False, cur))
                cur = ""
            cur = (cur + " " + s).strip()
        if cur:
            units.append((False, cur))
    parts, cur = [], []
    for is_head, p in units:
        size = sum(len(x) for x in cur)
        if cur and (is_head and size >= part_chars * 0.3 or size + len(p) > part_chars):
            parts.append("\n\n".join(cur))
            cur = []
        cur.append(p)
    if cur:
        if parts and sum(len(x) for x in cur) < part_chars * 0.25:   # đuôi quá ngắn → gộp vào phần trước
            parts[-1] += "\n\n" + "\n\n".join(cur)
        else:
            parts.append("\n\n".join(cur))
    return title, parts


def slugify(name: str) -> str:
    import unicodedata
    s = unicodedata.normalize("NFD", name.replace("đ", "d").replace("Đ", "D"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return re.sub(r"[^a-z0-9]+", "-", s).strip("-")[:60] or "truyen"


# ───────────────────────────── trạng thái ─────────────────────────────

class Job:
    def __init__(self, slug: str):
        self.dir = STORIES / slug
        self.file = self.dir / "tasks.json"
        self.data = json.loads(self.file.read_text(encoding="utf-8")) if self.file.exists() else None

    def save(self):
        tmp = self.file.with_suffix(".json.part")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=1), encoding="utf-8")
        tmp.replace(self.file)

    def p(self, kind: str, pid: str) -> pathlib.Path:
        return {"text": self.dir / "parts" / f"{pid}.txt", "mp3": self.dir / "audio" / f"{pid}.mp3",
                "srt": self.dir / "audio" / f"{pid}.srt", "mp4": self.dir / "video" / f"{pid}.mp4"}[kind]

    def log(self, **kw):
        kw = {"time": dt.datetime.now().isoformat(timespec="seconds"), **kw}
        with open(self.dir / "log.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(kw, ensure_ascii=False) + "\n")


LOCKED = {"voice": "voice", "speed": "voice", "size": "video", "act": "video"}   # khoá theo truyện → việc bị ảnh hưởng


def load_settings(a) -> tuple[dict, dict]:
    """(thiết lập TRUYỆN, thiết lập MÁY). Truyện: giọng, tốc độ, khung, nhịp hồi, cỡ phần, ghi vào tasks.json lúc nạp.
    Máy: số tiến trình, số lần thử lại, LUÔN đọc lại từ config.yaml (+ cờ dòng lệnh) mỗi lần chạy."""
    cfg = yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8")).get("produce", {})
    ch = yaml.safe_load((ROOT / "channels" / cfg.get("channel", "khoai-tay-review") / "channel.yaml")
                        .read_text(encoding="utf-8")).get("tts", {})
    story = {"voice": ch.get("voice", "Ngọc Huyền"), "speed": float(ch.get("speed", 1.0)),
             "size": cfg.get("size", "1920x1080"), "act": cfg.get("act_seconds", 60),
             "part_chars": cfg.get("part_chars", 2500)}
    machine = {"retries": cfg.get("retries", 2), "tts_workers": cfg.get("tts_workers", 3),
               "video_workers": cfg.get("video_workers", 0)}
    for k in story:
        if getattr(a, k, None) is not None:
            story[k] = getattr(a, k)
    for k in machine:
        if getattr(a, k, None) is not None:
            machine[k] = getattr(a, k)
    return story, machine


def change_settings(job: "Job", a) -> None:
    """Đổi giọng/tốc độ/khung khi làm tiếp: chỉ cho phép nếu CHƯA có việc nào bị ảnh hưởng đã xong (tránh trộn giọng,
    trộn khung → bản ghép hỏng)."""
    cur = job.data["settings"]
    for k, kind in LOCKED.items():
        v = getattr(a, k, None)
        if v is None or v == cur.get(k):
            continue
        done = [p["id"] for p in job.data["parts"] if p[kind]["status"] == "done"]
        if done:
            sys.exit(f"Lỗi: không đổi {k} {cur.get(k)!r} → {v!r} vì đã có {len(done)} phần làm xong theo {k} cũ "
                     f"({', '.join(done[:5])}...). Muốn đổi cho cả truyện: nạp lại với --slug mới.")
        cur[k] = v
    if a.part_chars is not None and a.part_chars != cur.get("part_chars"):
        print(f"Chú ý: truyện đã chia theo {cur.get('part_chars')} ký tự/phần; bỏ qua --part-chars (muốn chia lại: --slug mới).")


def create(src: pathlib.Path, slug: str | None, s: dict) -> "Job":
    text = read_story(src)
    title, parts = split_story(text, int(s["part_chars"]))
    if not parts:
        sys.exit(f"Lỗi: không đọc được chữ nào trong {src}")
    slug = slug or slugify(title or src.stem)
    job = Job(slug)
    sha = hashlib.sha1(text.encode()).hexdigest()[:12]
    if job.data:
        if job.data["source_sha"] != sha:
            sys.exit(f"Lỗi: stories/{slug} đã có truyện KHÁC nội dung. Đặt --slug khác, hoặc xoá thư mục đó nếu muốn làm lại.")
        print(f"Truyện đã nạp trước đó (stories/{slug}): làm tiếp.")
        return job
    (job.dir / "source").mkdir(parents=True, exist_ok=True)
    shutil.copy(src, job.dir / "source" / src.name)
    (job.dir / "parts").mkdir(exist_ok=True)
    seed0 = int(sha, 16) % (1 << 30)
    job.data = {"slug": slug, "title": title or src.stem, "source": src.name, "source_sha": sha,
                "created": dt.datetime.now().isoformat(timespec="seconds"), "settings": s, "parts": []}
    for i, t in enumerate(parts, 1):
        pid = f"{i:03d}"
        job.p("text", pid).write_text(t + "\n", encoding="utf-8")
        job.data["parts"].append({"id": pid, "chars": len(t), "seed": (seed0 + i * 7919) % (1 << 30),
                                  "voice": {"status": "todo", "attempts": 0},
                                  "video": {"status": "todo", "attempts": 0}})
    job.save()
    print(f"Đã nạp '{job.data['title']}' → stories/{slug}: {len(parts)} phần "
          f"({min(map(len, parts))}–{max(map(len, parts))} ký tự/phần)")
    return job


# ───────────────────────────── làm việc ─────────────────────────────

def do_voice(job: Job, part: dict, s: dict):
    from src.common import tts
    pid = part["id"]
    tts.vieneu(job.p("text", pid).read_text(encoding="utf-8"), s["voice"], job.p("mp3", pid), job.p("srt", pid),
               job.dir / "audio" / f"work_{pid}", float(s["speed"]), workers=int(s["tts_workers"]))


def do_video(job: Job, part: dict, s: dict):
    from src.studio import reel
    pid = part["id"]
    mp3 = job.p("mp3", pid)
    level, dur = reel.loudness(mp3, 24)
    plan = reel.make_plan(dur, part["seed"], float(s["act"]))
    out = job.p("mp4", pid)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".plan.json").write_text(json.dumps(plan, ensure_ascii=False), encoding="utf-8")
    tmp = out.with_name(f"{pid}.part.mp4")
    reel.render(plan, s["size"], tmp, 24, mp3, level, int(s["video_workers"]))
    tmp.replace(out)                                        # file có mặt = việc đã xong trọn vẹn


def run_task(job: Job, part: dict, kind: str, s: dict) -> bool:
    task = part[kind]
    for _ in range(int(s["retries"]) + 1):
        task["attempts"] += 1
        task["status"] = "running"
        job.save()
        t0 = time.time()
        try:
            (do_voice if kind == "voice" else do_video)(job, part, s)
            task.update(status="done", seconds=round(time.time() - t0), error=None)
            job.save()
            job.log(part=part["id"], task=kind, result="done", seconds=task["seconds"])
            print(f"  [{part['id']}] {kind}: xong ({task['seconds']} giây)")
            return True
        except Exception as e:                              # noqa: BLE001 - ghi lỗi, thử lại, không dừng cả truyện
            task.update(status="failed", error=f"{type(e).__name__}: {e}"[:500])
            job.save()
            job.log(part=part["id"], task=kind, result="failed", error=task["error"],
                    trace=traceback.format_exc()[-1500:])
            print(f"  [{part['id']}] {kind}: LỖI lần {task['attempts']}: {task['error']}")
    return False


def merge(job: Job) -> pathlib.Path:
    from src.common.tts import read_srt, write_srt
    out_dir = job.dir / "output"
    out_dir.mkdir(exist_ok=True)
    slug = job.data["slug"]
    lst = out_dir / "concat.txt"
    lst.write_text("".join(f"file '{job.p('mp4', p['id']).resolve()}'\n" for p in job.data["parts"]))
    out = out_dir / f"{slug}.mp4"
    tmp = out_dir / f"{slug}.part.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                    "-movflags", "+faststart", str(tmp)], check=True)
    tmp.replace(out)
    lst.unlink()
    cues, marks, t = [], [], 0.0
    for i, p in enumerate(job.data["parts"], 1):
        marks.append((t, i))
        cues += [(a + t, b + t, x) for a, b, x in read_srt(job.p("srt", p["id"]))]
        t += duration(job.p("mp4", p["id"]))
    write_srt(out.with_suffix(".srt"), cues)
    stamp = lambda x: f"{int(x // 3600)}:{int(x // 60 % 60):02d}:{int(x % 60):02d}" if x >= 3600 else \
        f"{int(x // 60):02d}:{int(x % 60):02d}"
    (out_dir / "upload.md").write_text(
        f"# {job.data['title']}\n\nThời lượng: {stamp(t)} · {len(marks)} phần · file: {out.name}, phụ đề: {out.stem}.srt\n\n"
        "## Mốc phần (dán vào mô tả YouTube)\n" + "".join(f"{stamp(a)} Phần {i}\n" for a, i in marks) +
        "\n## Nhắc khi đăng (làm tay)\n- Không dành cho trẻ em · bật bình luận · danh mục Giải trí\n"
        "- Tải .srt lên mục Phụ đề\n- Khai báo nội dung có dùng AI (giọng đọc)\n", encoding="utf-8")
    job.data["final"] = {"file": str(rel(out)), "seconds": round(t),
                         "made": dt.datetime.now().isoformat(timespec="seconds")}
    job.save()
    return out


def rel(path: pathlib.Path) -> str:
    """Đường dẫn để in: tương đối từ gốc repo nếu nằm trong repo."""
    try:
        return str(path.resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


def duration(path: pathlib.Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


def run(job: "Job", s: dict, redo: list[str]) -> int:
    """s = thiết lập truyện + thiết lập máy (đã gộp)."""
    for r in redo:                                          # "003" = cả phần; "003:voice" / "003:video" = 1 việc
        pid, _, kind = r.partition(":")
        if kind not in ("", "voice", "video"):
            sys.exit(f"Lỗi: --redo {r}: sau dấu ':' chỉ được 'voice' hoặc 'video'")
        part = next((p for p in job.data["parts"] if p["id"] == pid.zfill(3)), None)
        if not part:
            sys.exit(f"Lỗi: không có phần {pid}")
        for k in ([kind] if kind else ["voice", "video"]):
            part[k].update(status="todo", attempts=0)
            if k == "voice":                                # giọng mới thì video cũng phải dựng lại
                part["video"].update(status="todo", attempts=0)
                shutil.rmtree(job.dir / "audio" / f"work_{part['id']}", ignore_errors=True)
    job.data.pop("final", None)
    for part in job.data["parts"]:                          # việc dở dang (máy tắt giữa chừng) → làm lại
        for k in ("voice", "video"):
            if part[k]["status"] == "running":
                part[k]["status"] = "todo"
            if part[k]["status"] == "failed":
                part[k]["attempts"] = 0
    job.save()
    t0 = time.time()
    for part in job.data["parts"]:
        print(f"Phần {part['id']}/{len(job.data['parts']):03d}")
        for kind in ("voice", "video"):
            if part[kind]["status"] == "done":
                continue
            if kind == "video" and part["voice"]["status"] != "done":
                break
            if not run_task(job, part, kind, s):
                break
    bad = [f"{p['id']}:{k}" for p in job.data["parts"] for k in ("voice", "video") if p[k]["status"] != "done"]
    if bad:
        print(f"\nCHƯA XONG {len(bad)} việc: {', '.join(bad)}. Xem lỗi: python -m src.produce status "
              f"{job.data['slug']}. Sửa nguyên nhân rồi chạy lại cùng lệnh để làm tiếp.")
        return 1
    out = merge(job)
    print(f"\nXONG: {rel(out)} ({job.data['final']['seconds'] / 60:.1f} phút video, "
          f"lượt này mất {(time.time() - t0) / 60:.1f} phút). Gói đăng: {rel(out.parent)}/upload.md")
    return 0


def status(job: Job) -> int:
    d = job.data
    print(f"{d['title']} (stories/{d['slug']}), {len(d['parts'])} phần, giọng {d['settings']['voice']}, "
          f"khung {d['settings']['size']}")
    for p in d["parts"]:
        line = f"  {p['id']}  giọng: {p['voice']['status']:7s}  video: {p['video']['status']:7s}"
        for k in ("voice", "video"):
            if p[k].get("error") and p[k]["status"] != "done":
                line += f"\n        {k} lỗi (thử {p[k]['attempts']} lần): {p[k]['error']}"
        print(line)
    if d.get("final"):
        print(f"Bản hoàn chỉnh: {d['final']['file']} ({d['final']['seconds'] / 60:.1f} phút)")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Truyện → giọng + hoạt hình ngẫu nhiên → video hoàn chỉnh")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run")
    r.add_argument("story", nargs="?", help="file truyện .txt/.md/.docx (bỏ trống nếu làm tiếp bằng --slug)")
    r.add_argument("--slug")
    r.add_argument("--size", help="1920x1080 (YouTube) hoặc 1080x1920 (TikTok)")
    r.add_argument("--voice")
    r.add_argument("--speed", type=float)
    r.add_argument("--part-chars", type=int)
    r.add_argument("--retries", type=int)
    r.add_argument("--tts-workers", type=int, help="ghi đè config: số tiến trình đọc giọng (máy RAM 8 GB: 1)")
    r.add_argument("--video-workers", type=int, help="ghi đè config: số tiến trình vẽ video")
    r.add_argument("--redo", action="append", default=[], help="NNN hoặc NNN:voice / NNN:video, lặp được")
    st = sub.add_parser("status")
    st.add_argument("slug")
    a = ap.parse_args()
    if a.cmd == "status":
        job = Job(a.slug)
        if not job.data:
            sys.exit(f"Lỗi: chưa có stories/{a.slug}/tasks.json")
        return status(job)
    story, machine = load_settings(a)
    if a.story:
        job = create(pathlib.Path(a.story), a.slug, story)
    elif a.slug and Job(a.slug).data:
        job = Job(a.slug)
    else:
        sys.exit("Lỗi: cần file truyện, hoặc --slug của truyện đã nạp")
    with lock(job):
        change_settings(job, a)
        for k in ("retries", "tts_workers", "video_workers"):      # bản cũ từng lưu các khoá máy vào truyện
            job.data["settings"].pop(k, None)
        return run(job, {**job.data["settings"], **machine}, a.redo)


class lock:
    """Chặn hai lệnh `run` cùng một truyện: file stories/<slug>/.lock ghi PID; PID đã chết thì coi như khoá thừa."""

    def __init__(self, job):
        self.f = job.dir / ".lock"

    def __enter__(self):
        import os
        if self.f.exists():
            try:
                pid = int(self.f.read_text().strip())
                try:
                    os.kill(pid, 0)
                except PermissionError:                      # tiến trình của user khác: vẫn đang sống
                    pass
                sys.exit(f"Lỗi: truyện này đang được chạy bởi tiến trình {pid}. Chờ nó xong (hoặc dừng nó) rồi chạy lại.")
            except (ValueError, ProcessLookupError):         # khoá thừa của lần chạy đã chết
                pass
        self.f.write_text(str(os.getpid()))

    def __exit__(self, *exc):
        self.f.unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
