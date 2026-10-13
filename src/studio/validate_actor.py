"""Kiểm diễn viên rối (assets/actors/<id>): trường card + file + hình học. Rỗng = ĐẠT.

python -m src.studio.validate_actor <id> [--preview]     # exit 0 = ĐẠT, 1 = CHƯA ĐẠT
Dải tỉ lệ đầu và quy ước chế độ: docs/plans/protocols.md ("Giá trị đóng dùng chung").
"""
import argparse
import pathlib
import sys

import numpy as np
import yaml
from PIL import Image
from scipy import ndimage

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from src.contracts import check  # noqa: E402
from src.studio.cutout import neck_top  # noqa: E402

RATIO = {"chibi": (0.30, 0.60), "semi": (0.18, 0.30), "real": (0.12, 0.18)}
WIDTH_TOL = 0.08          # bề rộng bbox đầu lệch so với neutral
HALO_ERR, HALO_WARN = 0.25, 0.10
warnings: list[str] = []


def _load(d: pathlib.Path, rel: str, errs: list[str], what: str):
    p = d / rel
    if not p.exists():
        errs.append(f"{what}: thiếu file {rel}")
        return None
    try:
        img = Image.open(p)
        img.load()
    except Exception as e:  # noqa: BLE001
        errs.append(f"{what}: không mở được {rel} ({e})")
        return None
    if img.mode != "RGBA":
        errs.append(f"{what}: {rel} phải là PNG RGBA, nhận {img.mode}")
        return None
    if img.getchannel("A").getbbox() is None:
        errs.append(f"{what}: {rel} trong suốt hoàn toàn (bbox rỗng)")
        return None
    return img


def halo_ratio(img: Image.Image) -> float:
    a = np.asarray(img)
    semi = (a[..., 3] >= 1) & (a[..., 3] <= 254)
    n = int(semi.sum())
    if n == 0:
        return 0.0
    white = semi & (a[..., :3].min(axis=2) > 235)
    return float(white.sum()) / n


def caption_suspect(body: Image.Image) -> bool:
    """Ở 15% đáy: >= 4 mảng liền nhỏ (cao < 3% ảnh) cùng một hàng → nghi chữ chú thích."""
    a = np.asarray(body.getchannel("A")) > 128
    H = a.shape[0]
    y0 = int(H * 0.85)
    lab, n = ndimage.label(a[y0:])
    if n < 4:
        return False
    objs = ndimage.find_objects(lab)
    small = [(s[0].start + s[0].stop) / 2 for s in objs if (s[0].stop - s[0].start) < 0.03 * H]
    small.sort()
    tol = 0.02 * H
    for i, y in enumerate(small):
        if sum(1 for z in small[i:] if z - y <= tol) >= 4:
            return True
    return False


def validate(actor_dir: pathlib.Path) -> list[str]:
    warnings.clear()
    errs: list[str] = []
    cp = actor_dir / "card.yaml"
    try:
        card = yaml.safe_load(cp.read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        return [f"card.yaml: không đọc được ({e})"]
    errs += check("actor_card", card, "card")
    if not isinstance(card, dict):
        return errs
    rig = card.get("rig")
    rig_errs = check("actor_rig", rig, "rig") if isinstance(rig, dict) else []
    errs += rig_errs
    heads, outfits = card.get("heads"), card.get("outfits")
    if not isinstance(heads, dict) or not isinstance(outfits, dict) or not isinstance(rig, dict):
        return errs
    if "neutral" not in heads:
        errs.append("heads: thiếu 'neutral'")
    good_bodies: dict[str, dict] = {}
    for oid, o in outfits.items():
        bodies = o.get("bodies") if isinstance(o, dict) else None
        if not isinstance(bodies, dict):
            errs.append(f"outfits.{oid}: bodies phải là dict, thiếu bodies.relaxed")
            continue
        if "relaxed" not in bodies:
            errs.append(f"outfits.{oid}: thiếu bodies.relaxed")
        good_bodies[oid] = bodies

    himg = {}
    for k, v in heads.items():
        if not isinstance(v, str):
            errs.append(f"heads.{k}: đường dẫn phải là chuỗi, nhận {type(v).__name__}")
            continue
        himg[k] = _load(actor_dir, v, errs, f"heads.{k}")
    bimg = {}
    for oid, bodies in good_bodies.items():
        for k, v in bodies.items():
            if not isinstance(v, str):
                errs.append(f"outfits.{oid}.bodies.{k}: đường dẫn phải là chuỗi, nhận {type(v).__name__}")
                continue
            bimg[(oid, k)] = _load(actor_dir, v, errs, f"outfits.{oid}.bodies.{k}")
    back = None
    if rig.get("hair_back"):
        back = _load(actor_dir, rig["hair_back"], errs, "rig.hair_back")

    neutral = himg.get("neutral")
    nb = neutral.getchannel("A").getbbox() if neutral else None
    # tỉ lệ đầu / (đầu + thân)
    if nb and not rig_errs:
        rel = next(((oid, "relaxed") for oid in good_bodies if bimg.get((oid, "relaxed"))), None)
        if rel:
            hh = (nb[3] - nb[1]) * rig["head_scale"]
            bb = bimg[rel].getchannel("A").getbbox()
            ratio = hh / (nb[3] - nb[1] + (bb[3] - bb[1]))
            lo, hi = RATIO[rig["mode"]]
            if not lo <= ratio <= hi:
                errs.append(f"tỉ lệ đầu/(đầu+thân) {ratio:.3f} ngoài dải {rig['mode']} {lo}–{hi}")
    # cổ nằm 1/3 giữa thân
    for (oid, k), img in bimg.items():
        if img is None:
            continue
        x, _ = neck_top(img)
        if not img.width / 3 <= x <= img.width * 2 / 3:
            errs.append(f"outfits.{oid}.bodies.{k}: cổ x={x} ngoài 1/3 giữa bề rộng {img.width}")
    # bề rộng đầu
    if nb:
        w0 = nb[2] - nb[0]
        for k, img in himg.items():
            if img is None or k == "neutral":
                continue
            b = img.getchannel("A").getbbox()
            if abs((b[2] - b[0]) - w0) / w0 >= WIDTH_TOL:
                errs.append(f"heads.{k}: bề rộng {b[2] - b[0]} lệch neutral {w0} quá {WIDTH_TOL:.0%}")
    if back is not None and neutral is not None and back.size != neutral.size:
        errs.append(f"rig.hair_back: kích thước {back.size} != head neutral {neutral.size}")
    # viền trắng
    layers = [(f"heads.{k}", i) for k, i in himg.items()] + [(f"bodies.{o}.{k}", i) for (o, k), i in bimg.items()]
    for name, img in layers:
        if img is None:
            continue
        r = halo_ratio(img)
        if r >= HALO_ERR:
            errs.append(f"{name}: viền trắng {r:.0%} pixel bán trong suốt (>= {HALO_ERR:.0%})")
        elif r >= HALO_WARN:
            warnings.append(f"{name}: cảnh báo viền trắng {r:.0%}")
    # chữ chú thích
    for oid in good_bodies:
        img = bimg.get((oid, "relaxed"))
        if img is not None and caption_suspect(img):
            errs.append(f"outfits.{oid}.bodies.relaxed: nghi có chữ chú thích ở đáy ảnh")
    return errs


def preview(actor_dir: pathlib.Path) -> list[pathlib.Path]:
    from src.studio.stage import Puppet
    card = yaml.safe_load((actor_dir / "card.yaml").read_text(encoding="utf-8"))
    outs = []
    for oid, o in card["outfits"].items():
        pup = Puppet(actor_dir, oid)
        poses = list(o["bodies"])
        exprs = [e for e in ("neutral", "smirk", "shocked", "angry", "sad") if e in card["heads"]]
        cw, ch = 300, 560
        canvas = Image.new("RGBA", (cw * len(poses), ch * len(exprs)), (120, 130, 150, 255))
        for r, e in enumerate(exprs):
            for c, p in enumerate(poses):
                fig, _ = pup.figure(p, e)
                k = min((ch - 20) / fig.height, (cw - 20) / fig.width)
                fig = fig.resize((max(1, int(fig.width * k)), max(1, int(fig.height * k))), Image.LANCZOS)
                canvas.alpha_composite(fig, (c * cw + cw // 2 - fig.width // 2, r * ch + ch - 10 - fig.height))
        out = actor_dir / f"preview_{oid}.jpg"
        canvas.convert("RGB").save(out)
        outs.append(out)
    return outs


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--preview", action="store_true")
    a = ap.parse_args(argv)
    d = ROOT / "assets/actors" / a.id
    errs = validate(d)
    for w in warnings:
        print("cảnh báo:", w)
    if errs:
        print("CHƯA ĐẠT")
        for e in errs:
            print(" -", e)
        return 1
    print("ĐẠT")
    if a.preview:
        for p in preview(d):
            print("preview:", p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
