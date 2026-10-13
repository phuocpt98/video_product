"""Cắt rối bằng code (không AI) từ MỘT ảnh gốc toàn thân: màu phẳng, viền mực đen, nền trắng thuần.

Ra các lớp: hair_back (tóc dưới cằm, vẽ SAU thân), head_front (mặt + tóc trên cằm, vẽ TRÊN thân),
body_<pose> (thân từ cổ xuống, có mẩu cổ kéo lên để đầu che). hair_back và head_front cùng khung (stage.py resize
hair_back về cỡ ảnh đầu). Cách làm: docs/research/2026-10-13-puppet-v2.md §2 và §4 hướng A.
"""
from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

WHITE = 245
PAD = 6


# ---------------------------------------------------------------- mặt nạ
def _big_parts(mask: np.ndarray, min_px: int) -> np.ndarray:
    lab, n = ndi.label(mask)
    if n == 0:
        return np.zeros_like(mask)
    sizes = ndi.sum(mask, lab, range(1, n + 1))
    keep = np.zeros(n + 1, bool)
    keep[1:] = sizes >= min_px
    return keep[lab]


def masks(img: Image.Image, hair_dark: int = 70) -> dict[str, np.ndarray]:
    """bool masks cùng cỡ ảnh: fg (tiền cảnh = không phải nền trắng thông ra mép; ĐÓNG hình thái 2–3 px mặt nạ
    "không trắng" trước khi flood để lỗ ren/kẽ tóc không nối ra ngoài), hair, skin, cloth, line (nét mực mỏng)."""
    rgb = np.asarray(img.convert("RGB"))
    mn, mx = rgb.min(axis=2), rgb.max(axis=2)
    nonwhite = mn < WHITE
    closed = ndi.binary_closing(np.pad(nonwhite, 4), structure=np.ones((3, 3), bool), iterations=3)[4:-4, 4:-4]
    closed |= nonwhite
    lab, n = ndi.label(~closed)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bg = np.isin(lab, edge[edge > 0])
    fg = ~bg
    total = int(fg.sum())

    dark = (mx < hair_dark) & fg
    hair = _big_parts(ndi.binary_opening(dark, iterations=4), max(1, int(total * 0.01)))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    h, s, v = hsv[..., 0], hsv[..., 1], hsv[..., 2]
    skin_raw = (h >= 5) & (h <= 30) & (s >= 40) & (s <= 140) & (v > 150) & fg
    skin = ndi.binary_opening(skin_raw, iterations=2)
    if hair.sum() < 0.03 * total:                       # tóc không đen (nâu, bạc): lấy màu trội ở 1/3 trên
        hair = _fallback_hair(rgb, fg, skin, dark, total)
    skin &= ~hair
    cloth = fg & ~hair & ~skin
    line = dark & ~hair
    return {"fg": fg, "hair": hair, "skin": skin, "cloth": cloth, "line": line}


def _fallback_hair(rgb, fg, skin, dark, total) -> np.ndarray:
    ys = np.where(fg.any(axis=1))[0]
    third = ys[0] + (ys[-1] - ys[0]) // 3
    zone = np.zeros_like(fg)
    zone[:third + 1] = True
    cand = fg & zone & ~skin & ~dark & (rgb.min(axis=2) < 235)
    if cand.sum() < 50:
        return ndi.binary_opening(dark, iterations=4)
    q = (rgb[cand] // 24).astype(int)
    key = q[:, 0] * 100 + q[:, 1] * 10 + q[:, 2]
    vals, cnt = np.unique(key, return_counts=True)
    k = vals[cnt.argmax()]
    color = np.median(rgb[cand][key == k], axis=0)
    near = (np.linalg.norm(rgb.astype(float) - color, axis=2) < 40) & fg
    return _big_parts(ndi.binary_opening(near, iterations=2), max(1, int(total * 0.01)))


# ---------------------------------------------------------------- đo
def _face_comp(m: dict) -> np.ndarray:
    skin = m["skin"]
    fg_rows = np.where(m["fg"].any(axis=1))[0]
    if len(fg_rows) == 0:
        raise ValueError("không thấy hình nhân vật nào (ảnh toàn nền trắng?)")
    ymid = fg_rows[0] + (fg_rows[-1] - fg_rows[0]) / 2
    lab, n = ndi.label(skin)
    if n == 0:
        raise ValueError("không thấy vùng da nào để nhận mặt")
    idx = range(1, n + 1)
    sizes = np.array(ndi.sum(skin, lab, idx))
    cy = np.array(ndi.center_of_mass(skin, lab, idx))[:, 0]
    sizes = np.where(cy < ymid, sizes, 0)
    if sizes.max() == 0:
        raise ValueError("không thấy mảng da ở nửa trên ảnh")
    return lab == (sizes.argmax() + 1)


def _face_geom(m: dict):
    comp = _face_comp(m)
    rows = np.where(comp.any(axis=1))[0]
    top, bot = rows[0], rows[-1]
    ext = {}
    for y in range(top, bot + 1):
        xs = np.where(comp[y])[0]
        ext[y] = (xs[0], xs[-1]) if len(xs) else None
    run_max, chin = 0, None
    for y in range(top, bot + 1):
        if ext[y] is None:
            continue
        w = ext[y][1] - ext[y][0] + 1
        run_max = max(run_max, w)
        if run_max >= 20 and w < 0.55 * run_max:
            ahead = [ext[yy] for yy in range(y, min(y + 3, bot + 1)) if ext[yy] is not None]
            if all((e[1] - e[0] + 1) < 0.55 * run_max for e in ahead):
                chin = y
                break
    if chin is None:
        chin = bot
    sub = comp[top:chin + 1]
    cols = np.where(sub.any(axis=0))[0]
    return comp, (int(cols[0]), int(top), int(cols[-1]) + 1, int(chin))


def face_box(m: dict) -> tuple[int, int, int, int]:
    """Hộp mặt (l, t, r, b): mảng da lớn nhất ở nửa trên ảnh; b = cằm = hàng mà bề rộng da co hẹp xuống bề rộng cổ
    (< 55% bề rộng mặt lớn nhất) lần đầu tiên bên dưới điểm rộng nhất."""
    return _face_geom(m)[1]


def _bbox(mask: np.ndarray):
    ys, xs = np.where(mask)
    if len(ys) == 0:
        return None
    return int(xs.min()), int(ys.min()), int(xs.max()) + 1, int(ys.max()) + 1


def _head_hair(m: dict, fb) -> np.ndarray:
    """Chỉ các mảng tóc chạm quanh hộp mặt (tránh nhầm áo/quần đen)."""
    l, t, r, b = fb
    mg = max(4, int((r - l) * 0.1))
    probe = np.zeros_like(m["fg"])
    probe[max(0, t - mg):b + mg, max(0, l - mg):r + mg] = True
    lab, n = ndi.label(m["hair"])
    ids = np.unique(lab[probe & (lab > 0)])
    return np.isin(lab, ids[ids > 0])


def _head_parts(m: dict):
    """(hair đầu, mặt-trên-cằm, hộp mặt, cằm, mặt nạ đầu y<chin+2, mặt nạ tóc sau)."""
    comp, fb = _face_geom(m)
    l, t, r, b = fb
    chin = b
    hair = _head_hair(m, fb)
    hair_d = ndi.binary_dilation(hair, iterations=2) & m["fg"]
    box = np.zeros_like(m["fg"])
    g = 4
    box[max(0, t - g):b + 1, max(0, l - g):r + g] = True
    face_fg = m["fg"] & box & ~(m["cloth"] & ~box)
    rows = np.arange(m["fg"].shape[0])[:, None]
    above = rows < chin + 2
    head_mask = (hair_d | m["skin"] & box | face_fg) & above
    # da của mặt: cắt phần cổ/ngực khỏi mặt nạ bằng điều kiện hàng
    back = hair_d & (rows >= chin - 2)
    return hair, hair_d, fb, chin, head_mask, back


def measure(m: dict, parts: tuple | None = None) -> dict:
    """{face_w, face_h, chin_y, neck_x, neck_y, head_box: [l,t,r,b], body_h, fig_h, head_ratio}.
    `parts`: kết quả _head_parts(m) nếu đã tính (tránh tính lại)."""
    hair, hair_d, fb, chin, head_mask, back = parts or _head_parts(m)
    l, t, r, b = fb
    full = head_mask | (back & True)
    hb = _bbox(full)
    fgb = _bbox(m["fg"])
    if hb is None or fgb is None:
        raise ValueError("không tách được đầu/thân khỏi nền")
    fig_h = fgb[3] - fgb[1]
    nl, nr = _neck_cols(m, chin, (l + r) // 2, r - l)
    return {
        "face_w": int(r - l), "face_h": int(b - t), "chin_y": int(chin),
        "neck_x": int((nl + nr) // 2), "neck_y": int(chin),
        "head_box": [int(v) for v in hb],
        "body_h": int(fgb[3] - chin), "fig_h": int(fig_h),
        "head_ratio": float((chin - hb[1]) / fig_h),
        "face_cx": float((l + r) / 2),
    }


def _neck_cols(m: dict, chin: int, cx: int, face_w: int):
    sk = m["skin"][chin + 1:chin + 6]
    votes = sk.sum(axis=0) >= 3 if len(sk) else np.zeros(m["fg"].shape[1], bool)
    lab, n = ndi.label(votes)
    if n:                                               # đoạn cột da gần trục mặt nhất
        best, bd = None, 1e9
        for i in range(1, n + 1):
            xs = np.where(lab == i)[0]
            d = abs((xs[0] + xs[-1]) / 2 - cx)
            if d < bd:
                best, bd = xs, d
        if best is not None and bd < face_w * 0.5:
            return int(best[0]), int(best[-1]) + 1
    half = max(3, int(face_w * 0.1))
    return cx - half, cx + half


def _analyze(m: dict):
    """(_head_parts, measure) tính MỘT lần cho mỗi ảnh."""
    parts = _head_parts(m)
    return parts, measure(m, parts)


# ---------------------------------------------------------------- xuất ảnh
def defringe(rgba: np.ndarray) -> np.ndarray:
    """Khử viền trắng: pixel alpha 1–254 có màu trộn với trắng, màu thật = (c − 255(1−α))/α."""
    out = rgba.copy()
    a = out[..., 3].astype(np.float32) / 255
    sel = (out[..., 3] > 0) & (out[..., 3] < 255)
    if sel.any():
        c = out[..., :3].astype(np.float32)
        al = a[sel][:, None]
        c[sel] = np.clip((c[sel] - 255 * (1 - al)) / al, 0, 255)
        out[..., :3] = np.round(c).astype(np.uint8)
    return out


def _compose(rgb: np.ndarray, mask: np.ndarray, fg: np.ndarray) -> np.ndarray:
    """RGBA từ mask: alpha 255, riêng vòng 1 px ngoài rìa tiền cảnh lấy alpha mềm từ độ đậm nét mực."""
    ring = fg & ~ndi.binary_erosion(fg, border_value=1)
    a = np.full(mask.shape, 255, np.float32)
    soft = np.clip(255 - rgb.min(axis=2).astype(np.float32), 0, 255)
    a = np.where(ring, soft, a)
    a = np.where(mask, a, 0)
    a[a < 12] = 0
    out = np.dstack([rgb, np.round(a).astype(np.uint8)])
    return defringe(out)


def _crop(arr: np.ndarray, box, pad: int = PAD) -> Image.Image:
    l, t, r, b = box
    return Image.fromarray(arr).crop((l - pad, t - pad, r + pad, b + pad))


def _patch_hair(rgb: np.ndarray, back: np.ndarray, chin: int) -> np.ndarray:
    """Tô kín bao lồi của tóc dưới cằm bằng màu tóc trội, viền đen 2 px; giữ pixel gốc nơi có tóc."""
    h, w = back.shape
    ys, xs = np.where(back)
    pts = np.stack([xs, ys], axis=1).astype(np.int32)
    hull = cv2.convexHull(pts)
    color = [int(v) for v in np.median(rgb[back], axis=0)]
    canvas = np.zeros((h, w, 3), np.uint8)
    cv2.fillPoly(canvas, [hull], color)
    cv2.polylines(canvas, [hull], True, (15, 15, 15), 2)
    hullm = np.zeros((h, w), np.uint8)
    cv2.fillPoly(hullm, [hull], 1)
    cv2.polylines(hullm, [hull], True, 1, 2)
    hullm = hullm.astype(bool)
    hullm[:max(0, chin - 2)] = False
    canvas[back] = rgb[back]
    return np.dstack([canvas, hullm.astype(np.uint8) * 255])


def _head_layers(img: Image.Image, m: dict, pm: tuple | None = None) -> dict:
    """Lớp đầu ở cỡ ảnh gốc: {'front': RGBA, 'back': RGBA|None, 'box': hộp khung chung, 'meas': ...}"""
    rgb = np.asarray(img.convert("RGB")).copy()
    parts, meas = pm or _analyze(m)
    hair, hair_d, fb, chin, head_mask, back = parts
    front = _compose(rgb, head_mask, m["fg"])
    back_rgba = None
    if back.sum() > 0.05 * meas["face_w"] ** 2:
        back_rgba = _patch_hair(rgb, back, chin)
    return {"front": front, "back": back_rgba, "meas": meas}


def _body_layer(img: Image.Image, m: dict, overlap: float, pm: tuple | None = None):
    rgb = np.asarray(img.convert("RGB")).copy()
    parts, meas = pm or _analyze(m)
    hair, hair_d, fb, chin, head_mask, back = parts
    rows = np.arange(rgb.shape[0])[:, None]
    mask = m["fg"] & ~hair_d & (rows >= chin)
    # hàng chin..: giữ phần da cổ/vai; loại pixel thuộc mặt nằm ngoài (không có: đã cắt y<chin)
    rgba = _compose(rgb, mask, m["fg"])
    head_h = chin - meas["head_box"][1]
    top = int(round(chin - overlap * head_h))
    nl, nr = _neck_cols(m, chin, int(meas["face_cx"]), meas["face_w"])
    sk = m["skin"][chin + 1:chin + 6, nl:nr]
    col = np.median(rgb[chin + 1:chin + 6, nl:nr][sk], axis=0) if sk.any() else np.median(rgb[m["skin"]], axis=0)
    col = np.round(col).astype(np.uint8)
    top = max(top, 0)
    if top < chin:
        rgba[top:chin, nl:nr, :3] = col
        rgba[top:chin, nl:nr, 3] = 255
        rgba[top:chin, nl:nl + 2, :3] = 15
        rgba[top:chin, max(nl, nr - 2):nr, :3] = 15
    box = _bbox(rgba[..., 3] > 0)
    return rgba, box, meas


def cut_figure(master: Path, out_dir: Path, overlap: float = 0.12) -> dict:
    """Cắt ảnh gốc: ghi out_dir/hair_back.png (không ghi nếu không có tóc dưới cằm), head_front.png, body_relaxed.png.
    Trả về dict measure + {"hair_back": bool, "frame": [w, h], "anchor": [x, y]} (người gọi tự ghi measure.yaml).
    Ném ValueError có nghĩa nếu ảnh không tách được."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    img = Image.open(master).convert("RGB")
    m = masks(img)
    pm = _analyze(m)
    hl = _head_layers(img, m, pm)
    meas = hl["meas"]
    hbox = meas["head_box"]
    head = _crop(hl["front"], hbox)
    head.save(out_dir / "head_front.png")
    has_back = hl["back"] is not None
    if has_back:
        _crop(hl["back"], hbox).save(out_dir / "hair_back.png")
    elif (out_dir / "hair_back.png").exists():
        (out_dir / "hair_back.png").unlink()
    rgba, bbox, _ = _body_layer(img, m, overlap, pm)
    _crop(rgba, bbox).save(out_dir / "body_relaxed.png")
    meas = dict(meas)
    meas["hair_back"] = has_back
    meas["frame"] = [head.width, head.height]
    meas["anchor"] = [round(meas["face_cx"] - (hbox[0] - PAD), 2), meas["chin_y"] - (hbox[1] - PAD)]
    return meas


def _need(ref: dict, *keys: str) -> None:
    miss = [k for k in keys if not isinstance(ref, dict) or k not in ref]
    if miss:
        raise ValueError(f"ref phải là kết quả cut_figure hoặc measure.yaml (thiếu {', '.join(miss)})")


def cut_head(img: Path, out: Path, ref: dict) -> dict:
    """Ảnh biểu cảm: cắt head_front như cut_figure, CO cho face_w = ref["face_w"], đặt vào khung head_front của ảnh gốc
    (neo ở tâm cằm). `ref` = kết quả cut_figure hoặc measure.yaml (cần face_w, frame, anchor), thiếu thì ValueError.
    Trả về measure của ảnh này."""
    _need(ref, "face_w", "frame", "anchor")
    im = Image.open(img).convert("RGB")
    m = masks(im)
    hl = _head_layers(im, m)
    meas = hl["meas"]
    s = ref["face_w"] / meas["face_w"]
    layer = Image.fromarray(hl["front"])
    layer = layer.resize((max(1, round(layer.width * s)), max(1, round(layer.height * s))), Image.LANCZOS)
    ax, ay = meas["face_cx"] * s, meas["chin_y"] * s
    fw, fh = ref["frame"]
    rx, ry = ref["anchor"]
    l, t = round(ax - rx), round(ay - ry)
    res = layer.crop((l, t, l + fw, t + fh))
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    res.save(out)
    return meas


def cut_body(img: Path, out: Path, ref: dict, overlap: float = 0.12) -> dict:
    """Ảnh tư thế: cắt thân như cut_figure, co theo tỉ lệ fig_h của ref (kết quả cut_figure hoặc measure.yaml, cần
    fig_h; thiếu thì ValueError). Trả về measure."""
    _need(ref, "fig_h")
    im = Image.open(img).convert("RGB")
    m = masks(im)
    rgba, box, meas = _body_layer(im, m, overlap)
    s = ref["fig_h"] / meas["fig_h"]
    res = _crop(rgba, box)
    res = res.resize((max(1, round(res.width * s)), max(1, round(res.height * s))), Image.LANCZOS)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    res.save(out)
    return meas
