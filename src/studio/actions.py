"""Bộ HÀNH ĐỘNG và HIỆU ỨNG dùng chung cho mọi diễn viên: logic chuyển động viết một lần, diễn viên chỉ là "da".

Hành động = hàm (st, t, dur) → biến đổi của cả hình nhân vật trong khung đó:
  dx, dy: dịch theo chiều cao nhân vật (dx > 0 = về phía nhân vật đang nhìn); rot: xoay quanh chân (độ, dương = ngả
  ra sau); head_rot: xoay riêng đầu; flip: quay mặt đi; expr: ép biểu cảm; fx: hiệu ứng thêm.
  st = tiến độ trong cảnh 0..1, t = giây tính từ đầu cảnh, dur = độ dài cảnh (giây).
Hiệu ứng = vẽ đơn giản lên đầu (máu = vệt đỏ, xước = vài nét kẻ...), toạ độ theo khung đầu, không cần ảnh.
Thêm hành động mới: viết 1 hàm + thêm vào ACTIONS. Tên lạ trong kịch bản cảnh → "idle" (xem direct.py).
"""
import math

from PIL import Image, ImageDraw


def ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def _step(t: float, speed: float = 7.0) -> float:
    return abs(math.sin(t * speed))


def idle(st, t, dur):
    return {}


def walk_in(st, t, dur):            # đi vào từ phía sau lưng tới chỗ đứng trong 1,2 giây đầu
    p = min(t / 1.2, 1.0)
    return {"dx": -1.6 * (1 - ease(p)), "dy": -0.03 * _step(t) * (p < 1)}


def walk_out(st, t, dur):           # đứng yên rồi đi ra phía trước mặt trong 1,2 giây cuối
    p = max(0.0, 1 - (dur - t) / 1.2)
    return {"dx": 2.0 * ease(p), "dy": -0.03 * _step(t) * (p > 0)}


def walk(st, t, dur):               # đi ngang qua khung suốt cảnh
    return {"dx": -1.2 + 2.4 * st, "dy": -0.03 * _step(t), "rot": -2 * math.sin(t * 7)}


def run(st, t, dur):
    return {"dx": -1.8 + 3.6 * st, "dy": -0.06 * _step(t, 12), "rot": -10}


def hit(st, t, dur):                # bị đánh: giật lùi, ngả ra sau, rung, mặt sốc
    p = t - 0.25
    if p < 0:
        return {}
    k = math.exp(-p * 4)
    return {"dx": -0.25 * (1 - k), "rot": 14 * k, "shake": 0.03 * k, "expr": "shocked"}


def attack(st, t, dur):             # đấm/tát: lao tới rồi lùi về
    p = t - 0.15
    lunge = math.sin(min(max(p / 0.4, 0), 1) * math.pi)
    return {"dx": 0.3 * lunge, "rot": -8 * lunge, "pose": "point", "expr": "angry"}


def fall(st, t, dur):               # bị đánh gục, ngã: đổ ngửa ra sau, nảy nhẹ, nằm yên
    p = t - 0.3
    if p < 0:
        return {"expr": "shocked"}
    r = 90 * ease(p / 0.35)
    bounce = 0.04 * abs(math.sin(p * 10)) * math.exp(-p * 5) if p > 0.35 else 0
    # nằm hơi cao hơn mặt đất một chút để không đè lên phụ đề (stage.py còn đổi hướng ngã về phía giữa khung)
    return {"rot": r, "dy": -bounce - 0.12 * ease(p / 0.35), "fall": True, "expr": "shocked" if p < 0.6 else "blink", "fx": ["dizzy"] if p > 0.6 else []}


def faint(st, t, dur):              # ngất: đổ từ từ
    p = t - 0.4
    return {"rot": 88 * ease(p / 1.2), "expr": "blink"} if p > 0 else {"expr": "sad"}


def nod(st, t, dur):
    return {"head_rot": -8 * math.sin(t * 9) if t < 1.5 else 0}


def shake_head(st, t, dur):
    return {"head_dx": 0.04 * math.sin(t * 16) if t < 1.5 else 0}


def laugh(st, t, dur):
    return {"dy": -0.05 * _step(t, 14), "expr": "smirk_talk"}


def cry(st, t, dur):
    return {"shake": 0.004, "expr": "sad", "fx": ["tears"]}


def tremble(st, t, dur):            # sợ hãi, run rẩy
    return {"shake": 0.008, "expr": "shocked", "fx": ["sweat"]}


def jump(st, t, dur):               # nhảy cẫng / giật bắn mình
    p = t - 0.1
    return {"dy": -0.35 * math.sin(math.pi * p / 0.5) if 0 < p < 0.5 else 0}


def turn_away(st, t, dur):          # quay lưng bỏ đi: quay mặt đi rồi bước ra khỏi khung theo hướng đó
    p = max(0.0, (t - 0.5) / max(dur - 0.5, 0.5))
    return {"exit": t > 0.4, "dx": 2.8 * ease(p), "dy": -0.03 * _step(t) * (p > 0)}   # stage chọn mép gần nhất


def kneel(st, t, dur):              # quỵ xuống: thấp người, cúi
    p = ease(t / 0.5)
    return {"dy": 0.18 * p, "rot": -6 * p, "expr": "sad"}


ACTIONS = {f.__name__: f for f in (idle, walk_in, walk_out, walk, run, hit, attack, fall, faint, nod, shake_head,
                                   laugh, cry, tremble, jump, turn_away, kneel)}


# ---------------------------------------------------------------- hiệu ứng vẽ lên đầu (hb = x, y, w, h của đầu)

def _pt(hb, fx, fy):
    return hb[0] + hb[2] * fx, hb[1] + hb[3] * fy


def blood(d, hb, t):
    x, y = _pt(hb, 0.38, 0.30)
    w = hb[2] * 0.06
    d.line([(x, y), (x - w * 0.3, y + hb[3] * 0.18)], fill=(200, 20, 20, 255), width=int(w))
    d.ellipse([x - w, y - w * 0.8, x + w, y + w * 0.8], fill=(200, 20, 20, 255))


def scratch(d, hb, t):
    for i in range(3):
        x, y = _pt(hb, 0.62 + i * 0.05, 0.60)
        d.line([(x, y), (x + hb[2] * 0.05, y + hb[3] * 0.08)], fill=(170, 30, 30, 230), width=max(2, hb[2] // 90))


def bruise(d, hb, t):
    x, y = _pt(hb, 0.42, 0.55)
    r = hb[2] * 0.07
    d.ellipse([x - r, y - r * 0.8, x + r, y + r * 0.8], fill=(120, 60, 150, 110))


def tears(d, hb, t):
    for ex in (0.38, 0.66):
        x, y0 = _pt(hb, ex, 0.62)
        y = y0 + ((t * 0.9 + ex) % 1.0) * hb[3] * 0.25
        r = hb[2] * 0.025
        d.ellipse([x - r, y - r * 1.4, x + r, y + r], fill=(90, 170, 255, 230), outline=(30, 30, 30, 255))


def sweat(d, hb, t):
    x, y = _pt(hb, 0.88, 0.30 + (t * 0.3 % 0.2))
    r = hb[2] * 0.04
    d.polygon([(x, y - r * 2), (x - r, y), (x + r, y)], fill=(120, 190, 255, 240))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(120, 190, 255, 240), outline=(30, 30, 30, 255))


def anger(d, hb, t):                # dấu gân tức giận kiểu truyện tranh ở góc trán
    x, y = _pt(hb, 0.80, 0.18)
    r = hb[2] * 0.06 * (1 + 0.15 * math.sin(t * 12))
    for ax, ay, bx, by in ((-1, -0.2, -0.2, -1), (1, -0.2, 0.2, -1), (-1, 0.2, -0.2, 1), (1, 0.2, 0.2, 1)):
        d.line([(x + ax * r, y + ay * r), (x + bx * r, y + by * r)], fill=(220, 20, 20, 255), width=max(3, hb[2] // 60))


def dizzy(d, hb, t):                # sao quay quanh đầu
    cx, cy = _pt(hb, 0.5, 0.02)
    for i in range(3):
        a = t * 4 + i * 2 * math.pi / 3
        x, y = cx + math.cos(a) * hb[2] * 0.35, cy + math.sin(a) * hb[3] * 0.08
        r = hb[2] * 0.045
        pts = [(x + r * math.cos(k * math.pi / 5 - math.pi / 2) * (1 if k % 2 == 0 else 0.45),
                y + r * math.sin(k * math.pi / 5 - math.pi / 2) * (1 if k % 2 == 0 else 0.45)) for k in range(10)]
        d.polygon(pts, fill=(255, 220, 40, 255), outline=(30, 30, 30, 255))


def blush(d, hb, t):
    for ex in (0.32, 0.72):
        x, y = _pt(hb, ex, 0.72)
        r = hb[2] * 0.06
        d.ellipse([x - r, y - r * 0.5, x + r, y + r * 0.5], fill=(255, 110, 130, 120))


EFFECTS = {f.__name__: f for f in (blood, scratch, bruise, tears, sweat, anger, dizzy, blush)}


def draw_effects(fig: Image.Image, head_box, names, t: float) -> Image.Image:
    """Vẽ hiệu ứng lên bản sao hình nhân vật (trước khi xoay/lật)."""
    names = [n for n in names if n in EFFECTS]
    if not names:
        return fig
    fig = fig.copy()
    layer = Image.new("RGBA", fig.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for n in names:
        EFFECTS[n](d, head_box, t)
    fig.alpha_composite(layer)
    return fig


# hiệu ứng toàn màn hình theo cảnh (shot.screen): flash (chớp trắng đầu cảnh), fade_in, fade_out, sepia (hồi tưởng),
# shake (rung máy quay), black (màn đen)
SCREEN = ("flash", "fade_in", "fade_out", "sepia", "shake", "black")
