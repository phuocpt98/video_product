"""Quay gameplay tự động của game HTML (game của Người sáng lập) làm clip nền. Chạy Chrome ẩn, không cần thao tác.

Mở game trong Chromium headless, ẩn khung panel/nút, bấm AUTO rồi quay. Mặc định quay TỪNG KHUNG HÌNH: đồng hồ của
trang được thay bằng đồng hồ ảo (performance.now, requestAnimationFrame), mỗi khung tiến đúng 1/fps giây rồi chụp ảnh
chất lượng cao, đưa thẳng vào ffmpeg. Video mượt đều, nét, không phụ thuộc máy nhanh hay chậm.
(--mode live: quay bằng record video có sẵn của Playwright, nhanh nhưng mờ ~1 Mbps VP8.)

python scripts/record_game.py --seconds 60 --size 1920x1080 --name p04_world
python scripts/record_game.py --seconds 60 --size 1080x1920 --name p04_world     # khung dọc cho TikTok
"""
import argparse
import os
import pathlib
import subprocess
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".cache/ms-playwright"))  # trình duyệt nằm trong dự án
GAME = pathlib.Path.home() / "Documents/project/personal/game_ideal/prototypes/p04-world/index.html"
VCLOCK = """(() => {
  let t = 0; const q = [];
  const t0 = Date.now();
  performance.now = () => t;
  Date.now = () => t0 + t;
  window.requestAnimationFrame = cb => { q.push(cb); return q.length; };
  window.cancelAnimationFrame = () => {};
  window.__advance = ms => { t += ms; const cbs = q.splice(0); for (const cb of cbs) cb(t); };
})();"""
HIDE = "#panel, .fab, #autoBtn { display: none !important; } #stage { flex: 1 1 100% !important; }"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--game", default=str(GAME))
    ap.add_argument("--seconds", type=int, default=60)
    ap.add_argument("--size", default="1920x1080", help="RỘNGxCAO, ví dụ 1920x1080 hoặc 1080x1920")
    ap.add_argument("--name", default="p04_world")
    ap.add_argument("--warmup", type=float, default=3.0, help="giây chờ game chạy ổn định, cắt bỏ khỏi clip")
    ap.add_argument("--mode", choices=["frames", "live"], default="frames")
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--bitrate", default="12M", help="bitrate H.264 đầu ra")
    a = ap.parse_args()
    w, h = map(int, a.size.lower().split("x"))
    out_dir = ROOT / "assets/clips"
    out_dir.mkdir(parents=True, exist_ok=True)
    n = len(list(out_dir.glob(f"game_{a.name}_{w}x{h}_*.mp4"))) + 1
    out = out_dir / f"game_{a.name}_{w}x{h}_{n:02d}.mp4"

    if a.mode == "frames":
        record_frames(a, w, h, out)
    else:
        record_live(a, w, h, out)
    print("Xong:", out.relative_to(ROOT))
    return 0


def open_game(p, a, w, h, **ctx_kw):
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": w, "height": h}, device_scale_factor=1, **ctx_kw)
    if a.mode == "frames":
        ctx.add_init_script(VCLOCK)
    page = ctx.new_page()
    page.goto(pathlib.Path(a.game).resolve().as_uri())
    page.wait_for_timeout(800)
    page.evaluate("document.getElementById('autoBtn')?.click()")      # bật AUTO trước khi ẩn nút
    page.add_style_tag(content=HIDE)
    page.evaluate("window.dispatchEvent(new Event('resize'))")         # canvas giãn ra toàn khung
    return browser, ctx, page


def record_frames(a, w, h, out):
    from playwright.sync_api import sync_playwright

    step = 1000 / a.fps
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "image2pipe", "-framerate", str(a.fps), "-i", "-",
                            "-c:v", "h264_videotoolbox", "-b:v", a.bitrate, "-maxrate", a.bitrate, "-pix_fmt", "yuv420p",
                            "-movflags", "+faststart", str(out)], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        browser, ctx, page = open_game(p, a, w, h)
        for _ in range(int(a.warmup * a.fps)):          # cho game chạy trước, không ghi
            page.evaluate(f"__advance({step})")
        for _ in range(a.seconds * a.fps):
            page.evaluate(f"__advance({step})")
            enc.stdin.write(page.screenshot(type="jpeg", quality=95))
        browser.close()
    enc.stdin.close()
    if enc.wait():
        raise RuntimeError("ffmpeg lỗi khi ghép khung hình")


def record_live(a, w, h, out):
    from playwright.sync_api import sync_playwright

    with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
        browser, ctx, page = open_game(p, a, w, h, record_video_dir=tmp, record_video_size={"width": w, "height": h})
        page.wait_for_timeout(int((a.seconds + a.warmup) * 1000))
        webm = page.video.path()
        ctx.close()
        browser.close()
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(a.warmup), "-i", webm, "-t", str(a.seconds),
                        "-an", "-c:v", "h264_videotoolbox", "-b:v", a.bitrate, "-pix_fmt", "yuv420p", "-r", str(a.fps),
                        str(out)], check=True)


if __name__ == "__main__":
    raise SystemExit(main())
