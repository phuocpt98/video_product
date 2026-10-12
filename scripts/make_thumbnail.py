"""Thumbnail YouTube 1280x720: chữ hai tầng (dòng nhỏ + dòng to) + nhãn tập.

python scripts/make_thumbnail.py <kênh> "<dòng nhỏ>" "<dòng to>" "<nhãn>" <file.png>          # linh vật kênh
python scripts/make_thumbnail.py drama <slug> "<dòng nhỏ>" "<dòng to>" "<nhãn>" <file.png> \
    --bg <id nền> --lead <diễn viên>:<biểu cảm> --back <diễn viên>:<biểu cảm>[:hiệu ứng],...
  Bố cục tam giác drama: nữ chính to phía trước, phe ác nhỏ phía sau (hiệu ứng tears/sweat/anger), mũi tên đỏ chỉ vào.
"""
import pathlib
import sys

import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
FONT = ROOT / "assets/fonts"


def fit(d, text, path, size, width):
    while size > 20:
        f = ImageFont.truetype(str(path), size)
        if d.textlength(text, font=f) <= width:
            return f
        size -= 4
    return ImageFont.truetype(str(path), size)


def wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur]


def drama(argv) -> int:
    import argparse
    sys.path.insert(0, str(ROOT))
    from src.studio.actions import draw_effects
    from src.studio.stage import Puppet
    ap = argparse.ArgumentParser()
    for k in ("slug", "small", "big", "badge", "out"):
        ap.add_argument(k)
    ap.add_argument("--bg", required=True)
    ap.add_argument("--lead", required=True)
    ap.add_argument("--back", default="")
    a = ap.parse_args(argv)
    W, H = 1280, 720
    bg = Image.open(ROOT / "assets/scenes" / a.bg / "master.jpg").convert("RGB")
    bg = bg.resize((W, int(bg.height * W / bg.width)), Image.LANCZOS).crop((0, 0, W, H)).filter(ImageFilter.GaussianBlur(3))
    img = Image.blend(bg, Image.new("RGB", (W, H), (20, 10, 30)), 0.55).convert("RGBA")
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((620, 0, 1320, 760), fill=120)
    img = Image.composite(Image.new("RGBA", (W, H), (255, 190, 90, 255)), img, glow.filter(ImageFilter.GaussianBlur(140)))

    def fig(spec, height):
        actor, expr, *fx = spec.split(":")
        p = Puppet(ROOT / "assets/actors" / actor)
        pose = "hips" if "hips" in p.card["bodies"] else "relaxed"
        f, _ = p.figure(pose, expr)
        f = draw_effects(f, p.head_box[p.last_key], fx, 0.3)
        f = f.crop(f.getchannel("A").getbbox())
        return f.resize((int(f.width * height / f.height), height), Image.LANCZOS)

    backs = [b for b in a.back.split(",") if b]
    targets = []
    for i, b in enumerate(backs):                         # phe ác: nhỏ, phía sau, góc phải trên
        f = fig(b, 380)
        x, y = W - 20 - (len(backs) - i) * 170 - f.width // 2 + 85, 220 + (i % 2) * 40
        img.alpha_composite(f, (x, y))
        targets.append((x + f.width // 2, y + f.height // 4))
    f = fig(a.lead, 760)                                  # nữ chính: to, phía trước, cắt ngang hông
    sh = Image.new("RGBA", f.size, (0, 0, 0, 0))
    sh.putalpha(f.getchannel("A").point(lambda v: v // 2))
    lx = 560
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)), (lx + 10, 60))
    img.alpha_composite(f, (lx, 50))
    d = ImageDraw.Draw(img)
    for sx, sy, r in ((lx + 40, 150, 22), (lx + f.width - 30, 110, 16), (lx + 20, 330, 12)):   # lấp lánh quyền lực
        d.polygon([(sx, sy - r), (sx + r // 4, sy - r // 4), (sx + r, sy), (sx + r // 4, sy + r // 4), (sx, sy + r),
                   (sx - r // 4, sy + r // 4), (sx - r, sy), (sx - r // 4, sy - r // 4)], fill=(255, 245, 170))
    if targets:                                           # mũi tên đỏ chỉ vào phe ác
        tx, ty = targets[0]
        x0, y0 = tx - 20, ty - 150
        d.line([(x0, y0), (tx, ty - 40)], fill=(230, 30, 30), width=14)
        d.polygon([(tx - 26, ty - 62), (tx + 22, ty - 52), (tx + 2, ty - 10)], fill=(230, 30, 30))
    bold = FONT / "BeVietnamPro-ExtraBold.ttf"
    fs = fit(d, a.small.upper(), bold, 50, 600)
    d.text((44, 60), a.small.upper(), font=fs, fill=(255, 255, 255), stroke_width=4, stroke_fill=(20, 12, 6))
    fb = ImageFont.truetype(str(bold), 104)
    lines = wrap(d, a.big.upper(), fb, 540)
    if len(lines) > 3:
        raise SystemExit(f"Dòng to quá dài ({len(lines)} dòng > 3): rút còn 3–6 từ")
    y = 150
    for line in lines:
        d.text((40, y), line, font=fb, fill=(255, 220, 50), stroke_width=9, stroke_fill=(150, 10, 10))
        y += 122
    fbadge = ImageFont.truetype(str(bold), 44)
    bw = d.textlength(a.badge, font=fbadge)
    d.rounded_rectangle((44, 610, 44 + bw + 48, 680), radius=18, fill=(214, 40, 40))
    d.text((68, 616), a.badge, font=fbadge, fill=(255, 255, 255))
    pathlib.Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(a.out)
    print("Xong:", a.out)
    return 0


def main() -> int:
    if sys.argv[1] == "drama":
        return drama(sys.argv[2:])
    channel, small, big, badge, out = sys.argv[1:6]
    ch = ROOT / "channels" / channel
    cfg = yaml.safe_load((ch / "channel.yaml").read_text(encoding="utf-8"))
    W, H = 1280, 720
    img = Image.new("RGB", (W, H), (32, 20, 12))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((700, -100, 1500, 800), fill=150)
    img = Image.composite(Image.new("RGB", (W, H), (242, 155, 54)), img, glow.filter(ImageFilter.GaussianBlur(160)))
    m = Image.open(ch / cfg["brand"]["mascot_reference"]).convert("RGB").resize((560, 560), Image.LANCZOS)
    mask = Image.new("L", (560, 560), 0)
    ImageDraw.Draw(mask).ellipse((20, 20, 540, 540), fill=255)
    img.paste(m, (730, 110), mask.filter(ImageFilter.GaussianBlur(16)))
    d = ImageDraw.Draw(img)
    bold = FONT / "BeVietnamPro-ExtraBold.ttf"
    fs = fit(d, small.upper(), bold, 56, 700)
    d.text((48, 70), small.upper(), font=fs, fill=(255, 236, 205), stroke_width=4, stroke_fill=(20, 12, 6))
    fb = ImageFont.truetype(str(bold), 96)
    y = 160
    for line in wrap(d, big.upper(), fb, 720)[:3]:
        d.text((44, y), line, font=fb, fill=(255, 214, 64), stroke_width=7, stroke_fill=(20, 12, 6))
        y += 112
    fbadge = ImageFont.truetype(str(bold), 44)
    bw = d.textlength(badge, font=fbadge)
    d.rounded_rectangle((44, 610, 44 + bw + 48, 680), radius=18, fill=(214, 40, 40))
    d.text((68, 616), badge, font=fbadge, fill=(255, 255, 255))
    pathlib.Path(out).parent.mkdir(parents=True, exist_ok=True)
    img.save(out)
    print("Xong:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
