"""PHÒNG THIẾT KẾ NHÂN VẬT, bước 2: ghép đầu từ các lớp bộ phận (assets/parts/) theo một bản thiết kế (spec), xuất
thành diễn viên chibi dùng ngay trong puppet.py: 8 đầu biểu cảm + thân mượn từ kho trang phục + card.yaml.

Lớp từ sau ra trước: đầu nền (mặt + tai + tóc, đổi màu da) → mắt (kèm lông mày) → mũi → miệng → phụ kiện → kính.
Vị trí mỗi lớp tính theo khuôn mặt tự dò từ vùng màu da (LAYOUT, đo từ cằm lên theo bề rộng mặt); chỉnh thêm từng
lớp bằng spec.adjust.<lớp> = {dx, dy, scale} (tỉ lệ bề rộng mặt). Mục lục bộ phận: assets/parts/INDEX.md.

spec (assets/actors/<id>/avatar.yaml):
  head: head-messy   skin: "#f2c9a0"   eyes: eyes2   nose: nose1   mouth: mouth1
  extras: [glasses-round]   adjust: {eyes: {dy: 0.02}}
  body: {outfit: m-tshirt-jeans, build: normal, colors: {"#ffffff": "#d04040"}}   # kho thân + đổi màu quần áo
  head_size: 1.0   overlap: 0.06

python -m src.studio.avatar <id>          # dựng lại diễn viên từ assets/actors/<id>/avatar.yaml
"""
import pathlib
import sys

import numpy as np
import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[2]
PARTS = ROOT / "assets/parts"
ACTORS = ROOT / "assets/actors"

# (tâm x theo bề rộng mặt, độ cao tâm TÍNH TỪ CẰM theo bề rộng mặt, bề rộng theo bề rộng mặt)
LAYOUT = {"eyes": (0.5, 0.46, 0.78), "nose": (0.5, 0.31, 0.07), "mouth": (0.5, 0.18, 0.26),
          "beard-stubble": (0.5, 0.12, 0.62), "mustache": (0.5, 0.24, 0.30), "blush": (0.5, 0.30, 0.74),
          "mole": (0.72, 0.24, 0.035), "scar": (0.28, 0.45, 0.12), "glasses-round": (0.5, 0.44, 0.80),
          "glasses-square": (0.5, 0.44, 0.82), "sunglasses": (0.5, 0.44, 0.84),
          "mole-lip": (0.62, 0.14, 0.03), "mole-tear": (0.68, 0.39, 0.03), "freckles": (0.5, 0.32, 0.62),
          "eye-bags": (0.5, 0.39, 0.70), "bandaid": (0.28, 0.30, 0.16), "beard-full": (0.5, 0.10, 0.82),
          "goatee": (0.5, 0.06, 0.20), "wrinkles": (0.5, 0.64, 0.36), "earring-gold": (-0.03, 0.20, 0.07),
          "earring-pearl": (-0.03, 0.18, 0.05)}
# mũi bảng details_v2: cỡ riêng từng kiểu (mũi nét mảnh cần to hơn mũi chấm mới thấy)
LAYOUT.update({f"nose{n}": (0.5, 0.31, w) for n, w in ((5, 0.07), (6, 0.15), (7, 0.10), (8, 0.12), (9, 0.07), (10, 0.16),
                                                        (11, 0.15), (12, 0.10))})
BOTH_EARS = ("earring-gold", "earring-pearl")                       # 1 chiếc, vẽ ở tai trái rồi lật sang tai phải
ON_TOP = ("glasses-round", "glasses-square", "sunglasses")          # vẽ sau cùng
# biểu cảm → (mắt, miệng); kiểu mắt 6–8 không có "closed" → mượn eyes1-closed
EXPRESSIONS = {"neutral": ("normal", "neutral"), "neutral_talk": ("normal", "talk"), "smirk": ("normal", "smirk"),
               "smirk_talk": ("normal", "grin"), "shocked": ("wide", "shock"), "angry": ("angry", "shout"),
               "sad": ("sad", "frown"), "blink": ("closed", "neutral")}


def _registry() -> dict:
    return yaml.safe_load((PARTS / "parts.yaml").read_text(encoding="utf-8"))


def _part(reg: dict, pid: str) -> Image.Image:
    return Image.open(PARTS / reg[pid]["file"]).convert("RGBA")


def _skin_mask(img: Image.Image) -> tuple[np.ndarray, np.ndarray]:
    a = np.array(img).astype(np.float32)
    rgb, alpha = a[..., :3], a[..., 3]
    # màu da = sáng, ấm (R > G > B), không phải trắng
    warm = (alpha > 128) & (rgb[..., 0] > 170) & (rgb[..., 0] > rgb[..., 2] + 30) & (rgb.min(axis=2) < 235)
    base = np.median(rgb[warm], axis=0) if warm.any() else np.array([250, 200, 170])
    near = (alpha > 128) & (np.abs(rgb - base).sum(axis=2) < 70)
    return near, base


def face_box(img: Image.Image) -> tuple[int, int, int, int]:
    """Khung khuôn mặt (không tính tai, không tính tóc): vùng màu da, bỏ các cột mỏng hai bên (tai). Tóc dài che má làm
    mặt đo được hẹp đi: nới bề rộng tối thiểu = 58% bề ngang cả đầu (tính quanh tâm mặt) để mắt, miệng không bé tí."""
    near, _ = _skin_mask(img)
    cols = near.sum(axis=0)
    keep = np.nonzero(cols > cols.max() * 0.45)[0]
    rows = np.nonzero(near[:, keep.min():keep.max() + 1].any(axis=1))[0]
    l, r = int(keep.min()), int(keep.max())
    ab = img.getchannel("A").getbbox()
    min_w = 0.58 * (ab[2] - ab[0])
    if r - l < min_w:
        cx = (l + r) / 2
        l, r = int(cx - min_w / 2), int(cx + min_w / 2)
    return l, int(rows.min()), r, int(rows.max())


def recolor_skin(img: Image.Image, hex_color: str | None) -> Image.Image:
    """Đổi màu da: điểm ảnh gần màu da gốc → màu mới, giữ độ sáng tương đối (viền đen, tóc giữ nguyên)."""
    if not hex_color:
        return img
    near, base = _skin_mask(img)
    a = np.array(img).astype(np.float32)
    target = np.array([int(hex_color.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)
    ratio = (a[..., :3].mean(axis=2) / max(base.mean(), 1))[..., None]
    a[..., :3][near] = np.clip(target * ratio, 0, 255)[near]
    return Image.fromarray(a.astype(np.uint8))


def head(spec: dict, expr: str, reg: dict | None = None) -> Image.Image:
    """Ghép một đầu theo biểu cảm: đầu nền (mặt + tóc) + mắt + mũi + miệng + phụ kiện."""
    reg = reg or _registry()
    base = _part(reg, spec["head"])
    base = recolor_skin(base.crop(base.getchannel("A").getbbox()), spec.get("skin"))
    if spec["head"].endswith("-special"):
        return base
    fl, ft, fr, fb = face_box(base)
    FW = fr - fl
    e_eyes, e_mouth = EXPRESSIONS[expr]
    eyes = f"{spec['eyes']}-{e_eyes}"
    if eyes not in reg:
        eyes = f"eyes1-{e_eyes}" if f"eyes1-{e_eyes}" in reg else f"{spec['eyes']}-normal"
    layers = [("eyes", eyes), ("nose", spec.get("nose", "nose2")), ("mouth", f"{spec['mouth']}-{e_mouth}")]
    layers += [(x, x) for x in spec.get("extras", []) if x not in ON_TOP]
    layers += [(x, x) for x in spec.get("extras", []) if x in ON_TOP]
    adjust = spec.get("adjust", {})
    out = base.copy()
    for slot, pid in layers:
        if not pid or pid not in reg:
            continue
        img = _part(reg, pid)
        img = img.crop(img.getchannel("A").getbbox())
        if slot == "nose":                   # mũi tô sẵn màu hồng/trắng (nose8, 10, 12) lệch màu da → tô lại theo da mặt
            a = np.array(img)
            fill = (a[..., 3] > 0) & (a[..., :3].min(axis=2) > 140)
            a[fill, :3] = (_skin_mask(base)[1] * 0.93).astype(np.uint8)
            img = Image.fromarray(a)
        cx, up, w = LAYOUT.get(pid) or LAYOUT.get(slot) or (0.5, 0.4, 0.3)
        adj = adjust.get(slot, {})
        k = w * adj.get("scale", 1.0) * FW / img.width
        img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
        x = fl + (cx + adj.get("dx", 0)) * FW - img.width / 2
        y = fb - (up - adj.get("dy", 0)) * FW - img.height / 2
        out.alpha_composite(img, (int(x), int(y)))
        if pid in BOTH_EARS:
            out.alpha_composite(img.transpose(Image.FLIP_LEFT_RIGHT), (int(fl + (1 - cx) * FW - img.width / 2), int(y)))
    return out


FACE_K = 0.53          # bề rộng khuôn mặt = FACE_K × chiều cao thân (nhân vật chính nam-18-a: 0,49; to hơn chuẩn một chút)
OVERLAP = 0.06         # cằm đè xuống dưới đường vai bao nhiêu (theo chiều cao đầu)
POSE_LIST = ("relaxed", "hips", "phone", "point")


def _hex(c) -> str:
    return "#%02x%02x%02x" % tuple(int(v) for v in c[:3])


def _rgb(h: str) -> np.ndarray:
    return np.array([int(h.lstrip("#")[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def _cloth_mask(a: np.ndarray) -> np.ndarray:
    """Điểm ảnh quần áo: không trong suốt, không phải viền đen, không phải màu da."""
    rgb, alpha = a[..., :3], a[..., 3]
    skin = (rgb[..., 0] > 170) & (rgb[..., 0] > rgb[..., 2] + 30) & (rgb[..., 0] > rgb[..., 1] + 10) & \
        (rgb.min(axis=2) < 235)
    return (alpha > 128) & (rgb.max(axis=2) > 42) & ~skin


def body_file(outfit: str, build: str, pose: str) -> pathlib.Path:
    d = PARTS / "bodies" / outfit
    for p in (pose, "relaxed", *POSE_LIST):
        f = d / f"{build}-{p}.png"
        if f.exists():
            return f
    return next(d.glob("*.png"))


def palette(outfit: str, build: str = "normal", n: int = 8) -> list[str]:
    """Các màu chính của bộ đồ (để đổi màu): gom màu quần áo, bỏ màu chiếm < 3%."""
    a = np.array(Image.open(body_file(outfit, build, "relaxed")).convert("RGBA"))
    px = a[..., :3][_cloth_mask(a.astype(np.float32))]
    if not len(px):
        return []
    q = Image.fromarray(px.reshape(1, -1, 3).astype(np.uint8)).quantize(n)
    counts = sorted(q.getcolors(), reverse=True)
    pal = q.getpalette()
    out = []
    for c, k in counts:                              # gộp màu gần nhau (trắng #fefefe ~ #ffffff)
        col = np.array(pal[k * 3:k * 3 + 3], dtype=np.float32)
        if c > len(px) * 0.03 and all(np.abs(col - _rgb(o)).sum() > 60 for o in out):
            out.append(_hex(col))
    return out


def recolor_clothes(img: Image.Image, mapping: dict) -> Image.Image:
    """Đổi màu quần áo: {"#màu gốc": "#màu mới"}; điểm gần màu gốc → màu mới, giữ đậm nhạt tương đối."""
    if not mapping:
        return img
    a = np.array(img).astype(np.float32)
    cloth = _cloth_mask(a)
    lum = a[..., :3].mean(axis=2)
    for src, dst in mapping.items():
        s, d = _rgb(src), _rgb(dst)
        near = cloth & (np.abs(a[..., :3] - s).sum(axis=2) < 60)
        ratio = (lum / max(s.mean(), 1))[..., None]
        a[..., :3][near] = np.clip(d * ratio, 0, 255)[near]
    return Image.fromarray(a.astype(np.uint8))


def trim_neck_stub(img: Image.Image) -> Image.Image:
    """Gọt mẩu cổ thò lên trên đường vai (bảng thân mỗi bộ đồ vẽ cổ dài ngắn khác nhau), để đầu đặt ngay đường vai và
    đè kín cổ như nhân vật chính. Mẩu cổ = đoạn liền qua trục thân ở các hàng trên cùng, hẹp hơn hẳn vai."""
    a = np.array(img)
    solid = a[..., 3] > 128
    h = solid.shape[0]
    legs = np.nonzero(solid[int(h * 0.9)])[0]
    rows = np.nonzero(solid.any(axis=1))[0]
    if not len(legs) or not len(rows):
        return img
    cx, top = int((legs.min() + legs.max()) / 2), int(rows.min())

    def run(y):
        if not solid[y, cx]:
            return None
        lo = hi = cx
        while lo > 0 and solid[y, lo - 1]:
            lo -= 1
        while hi < solid.shape[1] - 1 and solid[y, hi + 1]:
            hi += 1
        return lo, hi
    first = [run(y) for y in range(top, min(h, top + max(3, int(h * 0.02))))]
    widths = [r[1] - r[0] for r in first if r]
    if not widths:
        return img
    neck_w = float(np.median(widths))
    shoulder = next((y for y in range(top, int(h * 0.4)) if (r := run(y)) and r[1] - r[0] > neck_w * 2.2), top)
    if shoulder - top < h * 0.012:                     # không có cổ đáng kể
        return img
    for y in range(top, shoulder - 1):
        r = run(y)
        if r:
            a[y, r[0]:r[1] + 1, 3] = 0
    from scipy import ndimage                        # bỏ vụn nhỏ còn sót (viền cổ), kẻo máy tưởng là đường vai
    lab, n = ndimage.label(a[..., 3] > 128)
    if n > 1:
        areas = ndimage.sum(np.ones_like(lab), lab, range(1, n + 1))
        a[..., 3][np.isin(lab, np.nonzero(areas < areas.max() * 0.01)[0] + 1)] = 0
    return Image.fromarray(a)


def body(spec: dict, pose: str) -> Image.Image:
    b = spec["body"]
    img = Image.open(body_file(b["outfit"], b.get("build", "normal"), pose)).convert("RGBA")
    img = recolor_clothes(img, b.get("colors", {}))
    return trim_neck_stub(recolor_skin(img, spec.get("skin")))


def scaled_head(spec: dict, expr: str, reg: dict | None = None) -> Image.Image:
    """Đầu đã co theo cỡ thân: bề rộng mặt = FACE_K × chiều cao thân (thân thả tay) × head_size. Đo theo chiều cao thân
    (không theo vai) nên thân gầy/béo đều ra cùng tỉ lệ đầu–người như nhân vật chính."""
    h = head(spec, expr, reg)
    bb = body(spec, "relaxed").getchannel("A").getbbox()
    fl, _, fr, _ = face_box(h) if not spec["head"].endswith("-special") else (0, 0, h.width * 0.8, 0)
    k = FACE_K * (bb[3] - bb[1]) * spec.get("head_size", 1.0) / max(1, fr - fl)
    return h.resize((max(1, int(h.width * k)), max(1, int(h.height * k))), Image.LANCZOS)


def split_hair(h: Image.Image) -> tuple[Image.Image, Image.Image | None]:
    """Tách đầu tóc dài thành 2 lớp theo mép cằm: (mặt + tóc trên → vẽ TRÊN thân, tóc dưới cằm → vẽ SAU thân).
    Không có tóc thò dưới cằm thì lớp sau = None."""
    up = chin_up(h)
    if up < 0.03:
        return h, None
    hb = h.getchannel("A").getbbox()
    cut = hb[3] - int(up * h.height) + 2                  # hàng ngay dưới cằm
    a = np.array(h)
    front, back = a.copy(), a.copy()
    front[cut:, :, 3] = 0
    back[:cut, :, 3] = 0
    return Image.fromarray(front), Image.fromarray(back)


def chin_up(h: Image.Image) -> float:
    """Khoảng từ cằm (mép dưới vùng da mặt) tới đáy khung đầu, theo chiều cao đầu: > 0 khi tóc dài/bím thò dưới cằm."""
    try:
        _, _, _, fb = face_box(h)
    except ValueError:
        return 0.0
    hb = h.getchannel("A").getbbox()
    return max(0.0, (hb[3] - fb) / h.height - 0.01)


def figure(spec: dict, expr: str = "neutral", pose: str = "relaxed", reg: dict | None = None) -> Image.Image:
    """Nhân vật hoàn chỉnh để xem trước (cùng cách ghép với puppet.py chế độ chibi)."""
    from src.studio.cutout import neck_top
    bd = body(spec, pose)
    h = scaled_head(spec, expr, reg)
    bx, by = neck_top(bd)
    hb = h.getchannel("A").getbbox()
    hx0 = bx - (hb[0] + hb[2]) // 2
    hy0 = by - (hb[3] - int(chin_up(h) * h.height)) + int(h.height * spec.get("overlap", OVERLAP))
    front, back = split_hair(h)
    left, top = min(0, hx0), min(0, hy0)
    W, H = max(bd.width, hx0 + h.width) - left, max(bd.height, hy0 + h.height) - top
    out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if back is not None:                                  # tóc dưới cằm sau thân → có chiều sâu
        out.alpha_composite(back, (hx0 - left, hy0 - top))
    out.alpha_composite(bd, (-left, -top))
    out.alpha_composite(front, (hx0 - left, hy0 - top))
    return out


def build_actor(actor_id: str, spec: dict) -> pathlib.Path:
    """Dựng diễn viên từ spec: 8 đầu biểu cảm (đã co theo thân) + 4 thân (đã đổi màu) + card.yaml."""
    from src.contracts import require
    require("avatar", spec, f"avatar {actor_id}")
    reg = _registry()
    d = ACTORS / actor_id
    outfit = spec["body"]["outfit"]
    (d / "parts" / outfit).mkdir(parents=True, exist_ok=True)
    (d / "avatar.yaml").write_text(yaml.safe_dump(spec, allow_unicode=True, sort_keys=False), encoding="utf-8")
    heads, up, hair_back = {}, 0.0, None
    for expr in EXPRESSIONS:
        h = scaled_head(spec, expr, reg)
        if expr == "neutral":
            up = chin_up(h)
        front, back = split_hair(h)                       # mặt + tóc trên vẽ trên thân; tóc dưới cằm để lớp sau
        front.save(d / "parts" / f"head_{expr}.png")
        heads[expr] = f"parts/head_{expr}.png"
        if back is not None and hair_back is None:
            back.save(d / "parts" / "hair_back.png")
            hair_back = "parts/hair_back.png"
    bodies = {}
    for p in POSE_LIST:
        body(spec, p).save(d / "parts" / outfit / f"body_{p}.png")
        bodies[p] = f"parts/{outfit}/body_{p}.png"
    card = {"id": actor_id, "kind": "actor", "made_by": "avatar", "gender": spec.get("gender", ""),
            "age": spec.get("age", ""), "look": spec.get("look", ""), "signature": "smirk",
            "rig": {"mode": "chibi", "head_scale": 1.0, "overlap": spec.get("overlap", OVERLAP), "head_dx": 0,
                    "chin_up": 0.0 if hair_back else round(up, 4),   # đầu đã cắt ở cằm thì cằm = đáy khung
                    **({"hair_back": hair_back, "hair_back_chin": round(up, 4)} if hair_back else {}),
                    "neck_dx": {}},
            "heads": heads, "outfits": {outfit: {"desc": outfit, "bodies": bodies}}, "roles": spec.get("roles", []),
            "notes": "Ghép bằng src/studio/avatar.py từ avatar.yaml (trang tạo nhân vật); sửa avatar.yaml rồi chạy lại."}
    (d / "card.yaml").write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return d


def preview(actor_id: str) -> pathlib.Path:
    spec = yaml.safe_load((ACTORS / actor_id / "avatar.yaml").read_text(encoding="utf-8"))
    exprs = list(EXPRESSIONS)
    canvas = Image.new("RGBA", (220 * len(exprs), 520), (120, 130, 150, 255))
    for i, e in enumerate(exprs):
        fig = figure(spec, e, POSE_LIST[i % 4])
        k = min(480 / fig.height, 210 / fig.width)
        fig = fig.resize((int(fig.width * k), int(fig.height * k)), Image.LANCZOS)
        canvas.alpha_composite(fig, (i * 220 + 110 - fig.width // 2, 505 - fig.height))
    out = ACTORS / actor_id / "preview_avatar.jpg"
    canvas.convert("RGB").save(out)
    return out


def main() -> int:
    aid = sys.argv[1]
    spec = yaml.safe_load((ACTORS / aid / "avatar.yaml").read_text(encoding="utf-8"))
    build_actor(aid, spec)
    print("Xong:", preview(aid).relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
