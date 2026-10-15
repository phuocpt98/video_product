"""BẢN DÀI NGANG cho YouTube: lấy giọng đọc đã có của các truyện/chương (sau `produce`) → vẽ lại hoạt hình 1920x1080 →
ghép thành 1 video dài + .srt + youtube.md. Không đọc giọng lại.

  1. Nguồn = 1 hoặc nhiều slug trong stories/ (mỗi slug một chương, hoặc 1 slug nhiều phần), theo thứ tự trên dòng lệnh.
     Mỗi phần cần audio/NNN.wav (hoặc .mp3 bản cũ) + .srt. Chạy TRƯỚC bước dọn rác xoá audio/.
  2. Mỗi phần vẽ lại khung ngang, cùng kế hoạch hoạt hình với bản dọc (video/NNN.plan.json, không có thì dựng theo seed),
     chỉ hình, lưu stories/<series>/long/work/<slug>_NNN.mp4. Chạy lại lệnh là LÀM TIẾP (phần đã vẽ bỏ qua).
  3. Ghép hình (-c copy) + nối giọng (mỗi phần đệm/cắt đúng bằng độ dài hình, mono, mã hoá AAC đúng 1 lần) →
     long/<series>-full.mp4; có --thumb thì ảnh bìa phủ lên vài giây đầu (không chèn thêm, giọng vẫn từ giây 0).
     Xong thì xoá work/.

python -m src.longform <slug> [<slug>...] [--series S] [--title "Tên bộ"] [--thumb bia.png] [--intro 3]
"""
import argparse
import datetime as dt
import json
import pathlib
import shutil
import subprocess
import sys

from src.produce import Job, duration, lock, rel

SIZE, FPS = "1920x1080", 24


def sources(slugs: list[str]) -> list[dict]:
    """Danh sách phần theo thứ tự: slug, id, giọng, srt, kế hoạch hoạt hình, nhãn chương."""
    out = []
    for slug in slugs:
        job = Job(slug)
        if not job.data:
            sys.exit(f"Lỗi: chưa có stories/{slug}/tasks.json (chạy `python -m src.produce run` trước)")
        for p in job.data["parts"]:
            wav = job.p("mp3", p["id"])
            audio = next((f for f in (wav, wav.with_suffix(".mp3")) if f.exists()), None)
            if p["voice"]["status"] != "done" or not audio or not job.p("srt", p["id"]).exists():
                sys.exit(f"Lỗi: {slug} phần {p['id']} thiếu giọng đọc (audio/{p['id']}.wav + .srt). Chạy produce cho xong, "
                         "và chạy bản dài TRƯỚC khi dọn rác audio/.")
            out.append({"slug": slug, "id": p["id"], "audio": audio, "srt": job.p("srt", p["id"]),
                        "plan": job.p("mp4", p["id"]).with_suffix(".plan.json"), "seed": p["seed"],
                        "act": float(job.data["settings"].get("act", 60)), "title": job.data["title"]})
    return out


def render_part(src: dict, out: pathlib.Path, workers: int) -> None:
    from src.studio import reel
    level, dur = reel.loudness(src["audio"], FPS)
    if src["plan"].exists():                                # cùng cảnh, cùng diễn viên với bản dọc
        plan = json.loads(src["plan"].read_text(encoding="utf-8"))
    else:
        plan = reel.make_plan(dur, src["seed"], src["act"])
    tmp = out.with_name(out.stem + ".part.mp4")
    reel.render(plan, SIZE, tmp, FPS, None, level, workers)
    tmp.replace(out)                                        # file có mặt = phần đã vẽ xong


def mux(srcs: list[dict], clips: list[pathlib.Path], out: pathlib.Path, thumb: str | None, intro: float) -> list[float]:
    """Nối hình (copy) + giọng (mỗi phần đệm lặng/cắt cho bằng đúng độ dài hình → phụ đề không trôi). Có ảnh bìa thì
    PHỦ lên `intro` giây đầu (không chèn thêm → hình, giọng, phụ đề vẫn khớp), khi đó hình mã hoá lại 1 lần.
    Trả về độ dài từng phần."""
    lens = [duration(c) for c in clips]
    lst = out.with_name("concat.txt")
    lst.write_text("".join(f"file '{c.resolve()}'\n" for c in clips))
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
    for s in srcs:
        cmd += ["-i", str(s["audio"])]
    chain = "".join(f"[{i + 1}:a]aformat=sample_rates=48000:channel_layouts=mono,apad=whole_dur={d:.6f},"
                    f"atrim=0:{d:.6f},asetpts=PTS-STARTPTS[a{i}];" for i, d in enumerate(lens))
    chain += "".join(f"[a{i}]" for i in range(len(srcs))) + f"concat=n={len(srcs)}:v=0:a=1[a]"
    vmap, venc = ["-map", "0:v"], ["-c:v", "copy"]
    if thumb:
        from src.studio.reel import encoder_args
        w, h = SIZE.split("x")
        cmd += ["-loop", "1", "-t", str(intro), "-i", thumb]
        chain += (f";[{len(srcs) + 1}:v]scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                  f"setsar=1,fps={FPS},format=yuv420p[t];[0:v][t]overlay=eof_action=pass,format=yuv420p[v]")
        vmap, venc = ["-map", "[v]"], encoder_args()
    tmp = out.with_name(out.stem + ".part.mp4")
    cmd += ["-filter_complex", chain, *vmap, "-map", "[a]", *venc, "-c:a", "aac", "-b:a", "192k",
            "-ac", "1", "-movflags", "+faststart", str(tmp)]
    subprocess.run(cmd, check=True)
    tmp.replace(out)
    lst.unlink()
    return lens


def stamp(x: float) -> str:
    return f"{int(x // 3600)}:{int(x // 60 % 60):02d}:{int(x % 60):02d}" if x >= 3600 else f"{int(x // 60):02d}:{int(x % 60):02d}"


def write_meta(srcs: list[dict], lens: list[float], out: pathlib.Path, title: str) -> None:
    from src.common.tts import read_srt, write_srt
    cues, marks, t, seen = [], [], 0.0, set()
    multi = len({s["slug"] for s in srcs}) > 1
    for s, d in zip(srcs, lens):
        if multi and s["slug"] not in seen:                 # nhiều slug: mỗi slug = 1 chương
            seen.add(s["slug"])
            marks.append((t, f"Chương {len(seen)}: {s['title']}"))
        elif not multi:
            marks.append((t, f"Phần {len(marks) + 1}"))
        cues += [(a + t, b + t, x) for a, b, x in read_srt(s["srt"])]
        t += d
    write_srt(out.with_suffix(".srt"), cues)                # ảnh bìa chỉ phủ hình → không dời mốc
    (out.parent / "youtube.md").write_text(
        f"# {title} (Full trọn bộ)\n\nFile: {out.name} · phụ đề: {out.stem}.srt · thời lượng {stamp(t)} · "
        f"khung {SIZE} (video thường, không phải Shorts)\n\n## Mốc chương (dán vào mô tả YouTube)\n" +
        "".join(f"{stamp(a)} {x}\n" for a, x in marks) +
        "\n## Nhắc khi đăng\n- Tiêu đề/mô tả/tags viết riêng cho YouTube (tên truyện + full + trọn bộ)\n"
        "- Khai báo nội dung có yếu tố AI (giọng TTS, hình tự tạo) · Không dành cho trẻ em\n- Tải .srt lên mục Phụ đề\n",
        encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("slugs", nargs="+", help="slug trong stories/, theo thứ tự chương")
    ap.add_argument("--series", help="tên thư mục bản dài trong stories/ (mặc định: slug đầu tiên)")
    ap.add_argument("--title", help="tên bộ truyện (mặc định: tên truyện của slug đầu)")
    ap.add_argument("--thumb", help="ảnh bìa phủ mấy giây đầu video (ảnh dọc thì có viền đen 2 bên)")
    ap.add_argument("--intro", type=float, default=3.0, help="số giây ảnh bìa (khi có --thumb)")
    ap.add_argument("--video-workers", type=int, default=0, help="tiến trình vẽ song song; 0 = tự chọn")
    a = ap.parse_args()
    srcs = sources(a.slugs)
    if a.thumb and not pathlib.Path(a.thumb).is_file():
        sys.exit(f"Lỗi: không thấy ảnh bìa {a.thumb}")
    series = Job(a.series or a.slugs[0])
    title = a.title or Job(a.slugs[0]).data["title"]
    base = series.dir / "long"
    work = base / "work"
    work.mkdir(parents=True, exist_ok=True)
    with lock(series):
        clips = []
        for i, s in enumerate(srcs, 1):
            clip = work / f"{s['slug']}_{s['id']}.mp4"
            if not clip.exists() or clip.stat().st_mtime < s["audio"].stat().st_mtime:   # giọng làm lại → vẽ lại
                print(f"Vẽ ngang {i}/{len(srcs)}: {s['slug']} phần {s['id']}")
                render_part(s, clip, a.video_workers)
            clips.append(clip)
        out = base / f"{series.dir.name}-full.mp4"
        lens = mux(srcs, clips, out, a.thumb, a.intro)
        write_meta(srcs, lens, out, title)
        shutil.rmtree(work)
    (base / "long.json").write_text(json.dumps(
        {"title": title, "file": rel(out), "seconds": round(duration(out)), "parts": [f"{s['slug']}/{s['id']}" for s in srcs],
         "made": dt.datetime.now().isoformat(timespec="seconds")}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"XONG: {rel(out)} ({duration(out) / 60:.1f} phút, {len(srcs)} phần). Gói đăng: {rel(base)}/youtube.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
