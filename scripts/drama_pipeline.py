"""CHUỖI TRUYỆN DRAMA TỰ VIẾT, một lệnh: (tạo truyện nếu chưa có) → viết/duyệt/đọc giọng các phần (run.py) → bảng việc
ghép diễn viên còn thiếu + dựng phần có đoạn mồi → cắt đoạn TikTok 3–5 phút (make_tiktok.py). Chạy lại thì làm tiếp.

python scripts/drama_pipeline.py <slug> [--motif "..." --ref <file>] [--parts 6] [--full]
  --full: dựng MỌI phần + ghép bản đầy đủ + gói đăng (phụ đề, thumbnail, upload.md). Mặc định chỉ dựng phần 1–3 + TikTok
"""
import argparse
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
PY = sys.executable


def sh(*args) -> int:
    print("▶", " ".join(map(str, args)), flush=True)
    return subprocess.run([PY, *map(str, args)], cwd=ROOT).returncode


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--motif")
    ap.add_argument("--ref")
    ap.add_argument("--parts", type=int, default=6)
    ap.add_argument("--full", action="store_true")
    a = ap.parse_args()
    t0 = time.time()
    sd = ROOT / "stories" / a.slug
    if not (sd / "story.yaml").exists():
        if not a.motif:
            raise SystemExit("Truyện mới cần --motif")
        args = ["-m", "src.drama", "new", a.slug, "--motif", a.motif, "--parts", a.parts]
        if a.ref:
            args += ["--ref", a.ref]
        if sh(*args):
            return 1
    t1 = time.time()
    if sh("-m", "src.run", a.slug, "--chapters", f"1-{a.parts}"):
        return 2
    t2 = time.time()
    hook = int(re.search(r"Phần\s*(\d+)", (sd / "outline/hook.md").read_text(encoding="utf-8")).group(1))
    # TikTok theo công thức (28/9/2026): cao trào 1 → leo tới sát đỉnh 2 rồi ngắt, lấy từ phần 1–3 → dựng sẵn 1–3
    parts = range(1, a.parts + 1) if a.full else range(1, min(3, a.parts) + 1)
    sh("-m", "src.board", "add-render", a.slug, f"{min(parts)}-{max(parts)}")
    for _ in range(4):                                   # thiết kế diễn viên → mở lại việc dựng → dựng
        sh("-m", "src.board", "run")
    t3 = time.time()
    rc = sh("scripts/make_tiktok.py", a.slug, "--auto")  # AI chọn khúc theo công thức (cao trào 1 → ngắt trước đỉnh 2)
    if a.full:
        out = sd / "output"
        lst = out / "concat.txt"
        lst.write_text("".join(f"file '{out / f'studio_{n:03d}_1920x1080.mp4'}'\n" for n in parts), encoding="utf-8")
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy",
                        "-movflags", "+faststart", str(out / f"full_{a.slug}.mp4")], check=False)
        lst.unlink()
        sh("scripts/make_upload.py", a.slug, "--parts", a.parts)   # phụ đề gộp, thumbnail, upload.md
    print(f"ĐO {a.slug}: tạo truyện {t1 - t0:.0f}s | viết+giọng {t2 - t1:.0f}s | thiết kế+dựng {t3 - t2:.0f}s | "
          f"tiktok {time.time() - t3:.0f}s | tổng {time.time() - t0:.0f}s")
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
