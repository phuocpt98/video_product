#!/usr/bin/env python3
"""Them thumbnail 1s vao dau video + voice chay ngay tu giay 0.

Dung:
    python3 add_intro.py --video final.mp4 --thumb thumb.png \
        --srt final.srt --out final_intro.mp4 [--seconds 1]

- Video: thumbnail hien `seconds` dau (mac dinh 1s), sau do video goc
- Audio: chay ngay tu 0s (KHONG delay, KHONG chen im lang)
- SRT: giu nguyen (khong shift vi audio khong doi)
- upload.md (neu co trong cung thu muc output): doi sang tro file intro.
  QUY TAC: upload.md luon tro file dang cuoi cung (ban co intro).
- Re-encode video (can thiet vi audio khong delay theo video).
"""
import argparse
import re
import subprocess
import tempfile
from pathlib import Path


def update_upload_md(out_dir: str, old_stem: str, new_stem: str):
    """Cap nhat upload.md: doi file tro sang ban intro (khong doi thoi luong)."""
    md = Path(out_dir) / "upload.md"
    if not md.exists():
        print("Khong thay upload.md -> bo qua")
        return
    text = md.read_text(encoding="utf-8")
    old_ref = f"file: {old_stem}.mp4"
    if old_ref not in text:
        print("upload.md da tro dung file intro -> bo qua")
        return
    text = text.replace(old_ref, f"file: {new_stem}.mp4")
    text = text.replace(f"phụ đề: {old_stem}.srt", f"phụ đề: {new_stem}.srt")
    md.write_text(text, encoding="utf-8")
    print(f"upload.md cap nhat -> {new_stem}.mp4")


def add_intro(video: str, thumb: str, out: str, seconds: float = 1.0):
    with tempfile.TemporaryDirectory() as td:
        intro = str(Path(td) / "intro.mp4")
        w, h = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
                               "stream=width,height", "-of", "csv=p=0", video],
                              capture_output=True, text=True, check=True).stdout.strip().split(",")[:2]

        # 1. Tao video thumbnail `seconds` (chi hinh, khong tieng)
        subprocess.run([
            "ffmpeg", "-v", "error", "-y",
            "-loop", "1", "-t", str(seconds), "-i", thumb,
            # khung theo video goc (ngang 1920x1080 hoac doc 1080x1920); thumb khac ti le -> vien den
            "-vf", f"scale={w}:{h}:force_original_aspect_ratio=decrease,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,"
                   "setsar=1,fps=24,format=yuv420p",
            "-c:v", "libx264", "-preset", "ultrafast", "-crf", "23",
            "-an",
            intro,
        ], check=True)

        # 2. Noi video: [thumb][video goc], audio lay truc tiep tu video goc (bat dau 0s)
        subprocess.run([
            "ffmpeg", "-v", "error", "-y",
            "-i", intro, "-i", video,
            "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v]",
            "-map", "[v]", "-map", "1:a",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-c:a", "copy", "-movflags", "+faststart",
            out,
        ], check=True)

    print(f"OK -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--thumb", required=True)
    ap.add_argument("--srt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seconds", type=float, default=1.0)
    a = ap.parse_args()

    # SRT giu nguyen (audio khong delay) -> copy sang ten moi
    out_srt = str(Path(a.out).with_suffix(".srt"))
    Path(out_srt).write_text(Path(a.srt).read_text(encoding="utf-8"), encoding="utf-8")
    print(f"SRT giu nguyen -> {out_srt}")

    add_intro(a.video, a.thumb, a.out, a.seconds)
    update_upload_md(str(Path(a.out).parent), Path(a.video).stem, Path(a.out).stem)


if __name__ == "__main__":
    main()
