#!/usr/bin/env python3
"""Tao thumbnail 1080x1920 cho video truyen: badge the loai + ten truyen + so tap.

Layout da duoc user duyet (mau /tmp/thumb-tap1.png):
  - Badge the loai: pill do (200,60,40) bo tron, chu trang, can giua top (y=80)
  - Lam toi nua duoi anh bang gradient den (trong suot -> 60% den)
  - Title: trang, vien den 3px, can giua, wrap ~16 ky tu/dong, vung y ~ H-700
  - So tap: vang gold (255,200,80), vien den, duoi title

Dung:
    python3 make_thumbnail.py --cover anh-nen.png --genre "Do thi, Tri tue, Va mat" \
        --title "Ban Than Cuop Ban Quyen Cua Toi" --episode "TAP 1" --output thumb.png
"""
import argparse
import textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920

# font BeVietnamPro trong repo (hien thi dung dau tieng Viet)
REPO = Path(__file__).resolve().parent.parent
FONT_BOLD = str(REPO / "assets" / "fonts" / "BeVietnamPro-ExtraBold.ttf")
FONT_SEMI = str(REPO / "assets" / "fonts" / "BeVietnamPro-SemiBold.ttf")

BADGE_COLOR = (200, 60, 40)
GOLD = (255, 200, 80)


def fit_cover(path: str) -> Image.Image:
    """Crop giua + resize ve dung 1080x1920."""
    im = Image.open(path).convert("RGB")
    target = W / H
    r = im.width / im.height
    if r > target:  # anh rong hon -> cat 2 ben
        new_w = int(im.height * target)
        x0 = (im.width - new_w) // 2
        im = im.crop((x0, 0, x0 + new_w, im.height))
    else:  # anh cao hon -> cat tren/duoi
        new_h = int(im.width / target)
        y0 = (im.height - new_h) // 2
        im = im.crop((0, y0, im.width, y0 + new_h))
    return im.resize((W, H), Image.LANCZOS)


def darken_bottom(im: Image.Image) -> Image.Image:
    """Phu gradient den: trong suot o giua -> 60% den o day anh."""
    overlay = Image.new("L", (1, H), 0)
    for y in range(H):
        alpha = int(160 * max(0, (y - H * 0.45) / (H * 0.55)))
        overlay.putpixel((0, y), alpha)
    black = Image.new("RGB", (W, H), (0, 0, 0))
    return Image.composite(black, im, overlay.resize((W, H)))


def draw_badge(d: ImageDraw.Draw, label: str):
    """Pill do, chu trang, can giua top."""
    label = label.upper()
    size = 44
    # thu nho font neu badge qua dai
    while size > 28:
        f = ImageFont.truetype(FONT_SEMI, size)
        bb = d.textbbox((0, 0), label, font=f)
        if bb[2] - bb[0] + 60 <= W - 80:
            break
        size -= 4
    f = ImageFont.truetype(FONT_SEMI, size)
    bb = d.textbbox((0, 0), label, font=f)
    bw = bb[2] - bb[0] + 60
    bx = (W - bw) // 2
    by = 80
    d.rounded_rectangle([bx, by, bx + bw, by + 80], radius=40, fill=BADGE_COLOR)
    d.text((bx + 30, by + 12), label, font=f, fill="white")


def make_thumbnail(cover: str, genre: str, title: str, episode: str, out: str):
    im = darken_bottom(fit_cover(cover))
    d = ImageDraw.Draw(im)

    draw_badge(d, genre)

    f_title = ImageFont.truetype(FONT_BOLD, 72)
    f_ep = ImageFont.truetype(FONT_SEMI, 44)

    lines = textwrap.wrap(title, width=16)[:4]
    y = H - 700
    for line in lines:
        bb = d.textbbox((0, 0), line, font=f_title)
        lw = bb[2] - bb[0]
        d.text(((W - lw) // 2, y), line, font=f_title, fill="white",
               stroke_width=3, stroke_fill="black")
        y += 100

    bb = d.textbbox((0, 0), episode, font=f_ep)
    lw = bb[2] - bb[0]
    d.text(((W - lw) // 2, y + 20), episode, font=f_ep, fill=GOLD,
           stroke_width=2, stroke_fill="black")

    im.save(out)
    print(f"OK -> {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cover", required=True, help="anh nen dai dien")
    ap.add_argument("--genre", required=True, help='the loai, vd "Do thi, Tri tue"')
    ap.add_argument("--title", required=True, help="ten truyen")
    ap.add_argument("--episode", required=True, help='so tap, vd "TAP 1"')
    ap.add_argument("--output", required=True)
    a = ap.parse_args()
    make_thumbnail(a.cover, a.genre, a.title, a.episode, a.output)


if __name__ == "__main__":
    main()
