"""Cắt bảng bộ phận (nền trắng, lưới ô đều) thành PNG nền trong cho nhân vật rối cắt ghép.

Nền được xoá bằng tô loang từ mép ảnh: chỉ vùng gần trắng thông ra mép mới thành trong suốt, nên áo trắng nằm trong
viền mực đen vẫn giữ nguyên.

python -m src.studio.cutout <sheet.jpg> <cột>x<hàng> <thư_mục_ra> tên1,tên2,...
"""
import pathlib
import sys

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter
from scipy import ndimage


def remove_background(img: Image.Image, tol: int = 28) -> Image.Image:
    rgb = img.convert("RGB")
    w, h = rgb.size
    # ảnh nhị phân: 255 = gần trắng
    gray = rgb.convert("L").point(lambda v: 255 if v >= 255 - tol else 0)
    mask = gray.copy()
    for x, y in [(0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1)] + [(x, 0) for x in range(0, w, 16)] + \
            [(x, h - 1) for x in range(0, w, 16)] + [(0, y) for y in range(0, h, 16)] + [(w - 1, y) for y in range(0, h, 16)]:
        if mask.getpixel((x, y)) == 255:
            ImageDraw.floodfill(mask, (x, y), 128)          # 128 = nền thông ra mép
    alpha = mask.point(lambda v: 0 if v == 128 else 255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.7))
    out = rgb.convert("RGBA")
    out.putalpha(alpha)
    return out


def cut(sheet: pathlib.Path, cols: int, rows: int, out_dir: pathlib.Path, names: list[str], pad: int = 6) -> list[pathlib.Path]:
    img = remove_background(Image.open(sheet))
    w, h = img.size
    a = img.getchannel("A")
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = []

    def splits(n, length, occupied):
        """Chia theo khe trống: chọn n-1 khe trống rộng nhất gần các vạch chia đều (tay vươn sang ô bên vẫn đúng người)."""
        if n == 1:
            return [0, length]
        gaps, start = [], None
        for i in range(length):
            if not occupied(i) and start is None:
                start = i
            if occupied(i) and start is not None:
                gaps.append((start, i))
                start = None
        cuts = []
        for k in range(1, n):
            ideal = length * k / n
            near = [g for g in gaps if abs((g[0] + g[1]) / 2 - ideal) < length / n * 0.6]
            cuts.append(round((max(near, key=lambda g: g[1] - g[0])[0] + max(near, key=lambda g: g[1] - g[0])[1]) / 2)
                        if near else round(ideal))
        return [0] + cuts + [length]

    # mỗi mảng liền (đầu, thân kèm tay cầm đồ) thuộc về ô chứa tâm của nó: hai ô chồng nhau theo chiều dọc
    # (điện thoại giơ lên sát cằm của đầu hàng trên) vẫn tách đúng
    lab, n = ndimage.label(np.array(a) > 128)
    ids = np.arange(1, n + 1)
    areas = ndimage.sum(np.ones_like(lab), lab, ids)
    centers = ndimage.center_of_mass(np.ones_like(lab), lab, ids)
    rows_px = splits(rows, h, lambda y: any(a.getpixel((x, y)) > 128 for x in range(0, w, 3)))
    for i, name in enumerate(names):
        c, r = i % cols, i // cols
        band = a.crop((0, rows_px[r], w, rows_px[r + 1]))
        cols_px = splits(cols, w, lambda x: any(band.getpixel((x, y)) > 128 for y in range(0, band.height, 3)))
        mine = [k for k, (cy, cx) in zip(ids, centers)
                if rows_px[r] <= cy < rows_px[r + 1] and cols_px[c] <= cx < cols_px[c + 1]]
        if not mine:
            raise ValueError(f"ô {i} ({name}) trống")
        big = max(areas[k - 1] for k in mine)
        keep = np.isin(lab, [k for k in mine if areas[k - 1] >= big * 0.005])   # bỏ vụn nhỏ (logo mờ, chấm bẩn)
        mask = Image.fromarray(np.where(keep, np.array(a), 0).astype(np.uint8))
        l, t, rr, b = mask.getbbox()
        box = (max(0, l - pad), max(0, t - pad), min(w, rr + pad), min(h, b + pad))
        part = img.crop(box)
        part.putalpha(mask.crop(box))
        p = out_dir / f"{name}.png"
        part.save(p)
        paths.append(p)
    return paths


def cut_parts(sheet: pathlib.Path, heads: list[str], bodies: list[str], out_dir: pathlib.Path, pad: int = 6) -> None:
    """Cắt bảng rối KHÔNG cần đúng lưới (AI hay vẽ lệch: 7 đầu một hàng, thân dính sát đầu...). Tách mảng liền lớn;
    thân = các mảng có chân thấp nhất (hàng cuối), đầu = còn lại; bộ phận chạm nhau thì tách ở hàng hẹp nhất; đầu xếp theo hàng rồi trái→phải, thân trái→phải; vụn nhỏ gộp vào mảng
    gần nhất. Đếm sai số lượng thì báo lỗi (ValueError) để tạo lại ảnh."""
    img = remove_background(Image.open(sheet))
    w, h = img.size
    a = np.array(img.getchannel("A"))
    solid = a > 128
    need = len(heads) + len(bodies)
    for _ in range(need):
        lab, n = ndimage.label(solid)
        ids = np.arange(1, n + 1)
        areas = ndimage.sum(np.ones_like(lab), lab, ids)
        boxes = ndimage.find_objects(lab)
        big = [k for k in ids if areas[k - 1] >= areas.max() * 0.03]
        if len(big) >= need:
            break
        # ít mảng hơn cần: có bộ phận chạm nhau (cằm đầu hàng trên dính cổ áo thân hàng dưới) → tách mảng cao nhất
        # ở hàng hẹp nhất trong khoảng giữa
        k = max(big, key=lambda k: boxes[k - 1][0].stop - boxes[k - 1][0].start)
        ys, xs = boxes[k - 1]
        m = lab[ys, xs] == k
        wid = m.sum(axis=1)
        lo, hi = int(len(wid) * 0.2), int(len(wid) * 0.8)
        cut_y = lo + int(np.argmin(wid[lo:hi]))
        solid[ys.start + cut_y, xs][m[cut_y]] = False
    bh = {k: boxes[k - 1][0].stop - boxes[k - 1][0].start for k in big}
    body_ids = sorted(big, key=lambda k: -boxes[k - 1][0].stop)[:len(bodies)]   # thân ở hàng cuối (chân thấp nhất)
    head_ids = [k for k in big if k not in body_ids]
    if len(head_ids) != len(heads) or len(body_ids) != len(bodies):
        raise ValueError(f"{sheet.name}: đếm được {len(head_ids)} đầu + {len(body_ids)} thân, cần {len(heads)} + {len(bodies)}")
    if heads:                                            # kiểm cỡ: đầu cỡ gần bằng nhau, thân cao hơn hẳn đầu
        hmed = float(np.median([bh[k] for k in head_ids]))
        if any(not 0.7 <= bh[k] / hmed <= 1.4 for k in head_ids) or any(bh[k] < hmed * 0.8 for k in body_ids):
            raise ValueError(f"{sheet.name}: cỡ bộ phận bất thường (đầu {sorted(bh[k] for k in head_ids)}, "
                             f"thân {sorted(bh[k] for k in body_ids)})")
    groups = {k: [k] for k in big}
    for k in ids:                                        # vụn nhỏ (tóc rời, khói, đồ vật rời tay) → mảng lớn gần nhất
        if k in groups:
            continue
        cy, cx = ndimage.center_of_mass(lab == k)

        def dist(b):
            ys, xs = boxes[b - 1]
            return max(ys.start - cy, 0, cy - ys.stop) + max(xs.start - cx, 0, cx - xs.stop)
        groups[min(big, key=dist)].append(k)

    def order(ks):
        cen = {k: ((boxes[k - 1][0].start + boxes[k - 1][0].stop) / 2, (boxes[k - 1][1].start + boxes[k - 1][1].stop) / 2)
               for k in ks}
        tol = np.median([bh.get(k, 1) for k in ks]) * 0.5 if ks else 0
        rows = []
        for k in sorted(ks, key=lambda k: cen[k][0]):
            if rows and abs(cen[k][0] - cen[rows[-1][0]][0]) < tol:
                rows[-1].append(k)
            else:
                rows.append([k])
        return [k for r in rows for k in sorted(r, key=lambda k: cen[k][1])]
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, k in list(zip(heads, order(head_ids))) + list(zip(bodies, order(body_ids))):
        mask = Image.fromarray(np.where(np.isin(lab, groups[k]), a, 0).astype(np.uint8))
        l, t, r, b = mask.getbbox()
        box = (max(0, l - pad), max(0, t - pad), min(w, r + pad), min(h, b + pad))
        part = img.crop(box)
        part.putalpha(mask.crop(box))
        (out_dir / f"{name}.png").parent.mkdir(parents=True, exist_ok=True)
        part.save(out_dir / f"{name}.png")


def cut_rows(sheet: pathlib.Path, rows: list[list[str]], out_dir: pathlib.Path, clear_white_rows: set[int] = frozenset(),
             pad: int = 6, clear_white_names: tuple[str, ...] = ("glasses-round", "glasses-square")) -> list[pathlib.Path]:
    """Cắt bảng icon theo HÀNG (mỗi hàng dài ngắn tuỳ ý): chia hàng ở các dải trống ngang rộng nhất, trong hàng chia
    món ở các khe trống dọc rộng nhất, nên món gồm nhiều mảng rời (cặp mắt, cặp lông mày) vẫn là một. Bỏ góc dưới phải
    (logo mờ của app tạo ảnh) và vụn nhỏ. clear_white_rows: hàng cần xoá cả vùng trắng khép kín (tóc có lỗ mặt)."""
    img = remove_background(Image.open(sheet))
    w, h = img.size
    a = np.array(img.getchannel("A"))
    a[int(h * 0.90):, int(w * 0.93):] = 0                   # góc dưới phải: logo
    lab, n = ndimage.label(a > 128)
    if n:
        areas = ndimage.sum(np.ones_like(lab), lab, np.arange(1, n + 1))
        tiny = np.isin(lab, np.nonzero(areas < np.median(areas[areas > areas.max() * 0.02]) * 0.02)[0] + 1)
        a[tiny] = 0

    def split(occ: np.ndarray, parts: int, counts: np.ndarray | None = None) -> list[int]:
        """Chia dải theo parts-1 khe trống rộng nhất (bỏ khe ở hai mép)."""
        idx = np.nonzero(occ)[0]
        lo, hi = idx.min(), idx.max() + 1
        gaps, start = [], None
        for i in range(lo, hi):
            if not occ[i] and start is None:
                start = i
            if occ[i] and start is not None:
                gaps.append((start, i))
                start = None
        best = sorted(sorted(gaps, key=lambda g: g[0] - g[1])[:parts - 1])
        if len(best) == parts - 1:
            return [lo] + [(g0 + g1) // 2 for g0, g1 in best] + [hi]
        # khối chạm nhau (tóc dài chạm hàng dưới): chia ở chỗ thưa nét nhất quanh vạch chia đều
        cnt = counts if counts is not None else occ.astype(int)
        span = (hi - lo) / parts
        cuts = []
        for k in range(1, parts):
            c0, c1 = int(lo + span * (k - 0.35)), int(lo + span * (k + 0.35))
            cuts.append(c0 + int(np.argmin(cnt[c0:c1])))
        return [lo] + cuts + [hi]

    ys = split((a > 128).any(axis=1), len(rows), (a > 128).sum(axis=1))
    rgba = np.array(img)
    paths = []
    out_dir.mkdir(parents=True, exist_ok=True)
    for r, names in enumerate(rows):
        band = a[ys[r]:ys[r + 1]]
        xs = split((band > 128).any(axis=0), len(names), (band > 128).sum(axis=0))
        for c, name in enumerate(names):
            m = np.zeros_like(a)
            m[ys[r]:ys[r + 1], xs[c]:xs[c + 1]] = a[ys[r]:ys[r + 1], xs[c]:xs[c + 1]]
            part_rgba = rgba.copy()
            part_rgba[..., 3] = m
            # vụn của hàng/ô bên cạnh lọt vào: mảng nhỏ chạm mép ô thì bỏ (chấm râu lún phún nằm giữa ô vẫn giữ)
            cl, cn = ndimage.label(m > 128)
            if cn > 1:
                car = ndimage.sum(np.ones_like(cl), cl, np.arange(1, cn + 1))
                for k, obj in enumerate(ndimage.find_objects(cl), 1):
                    edge = obj[0].start <= ys[r] + 1 or obj[0].stop >= ys[r + 1] - 1 or \
                        obj[1].start <= xs[c] + 1 or obj[1].stop >= xs[c + 1] - 1
                    if edge and car[k - 1] < car.max() * 0.05:
                        part_rgba[..., 3][cl == k] = 0
            if r in clear_white_rows or name.endswith(tuple(clear_white_names)):
                part_rgba[(part_rgba[..., :3].min(axis=2) > 235), 3] = 0
            part = Image.fromarray(part_rgba)
            l, t, rr, b = part.getchannel("A").getbbox()
            part = part.crop((max(0, l - pad), max(0, t - pad), min(w, rr + pad), min(h, b + pad)))
            p = out_dir / f"{name}.png"
            p.parent.mkdir(parents=True, exist_ok=True)
            part.save(p)
            paths.append(p)
    return paths


def neck_top(part: Image.Image) -> tuple[int, int]:
    """Điểm giữa mép trên phần cổ của thân không đầu. Chỉ xét dải giữa thân (quanh trục của nửa dưới),
    để tay giơ cao hay đồ vật (điện thoại) không bị nhận nhầm là cổ."""
    a = part.getchannel("A")
    lower = a.crop((0, a.height // 2, a.width, a.height)).getbbox() or (0, 0, a.width, 0)
    cx = (lower[0] + lower[2]) // 2
    band = max(8, (lower[2] - lower[0]) // 5)
    for y in range(a.height):
        xs = [x for x in range(max(0, cx - band), min(a.width, cx + band)) if a.getpixel((x, y)) > 128]
        if xs:
            return (xs[0] + xs[-1]) // 2, y
    return cx, 0

