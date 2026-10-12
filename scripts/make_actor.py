"""Tạo DIỄN VIÊN rối chibi (thư viện assets/actors/) bằng agy: character sheet + 1 "bảng rối" gộp 8 đầu (không cổ)
và 4 thân (không đầu) cùng cỡ, cùng nét. Một diễn viên có một khuôn mặt, nhiều bộ trang phục, đóng được nhiều vai.

Tạo mới:     python scripts/make_actor.py nam-18-a --look "..." --outfit ao-phong-2002 --outfit-desc "..." [--signature "..."]
Thêm đồ:     python scripts/make_actor.py nam-18-a --outfit vest --outfit-desc "..." --poses "..."
Bước nào đã có file thì bỏ qua (chạy lại để làm tiếp). Mỗi ảnh tốn ~1% quota Gemini; model ảnh giới hạn ~13 ảnh/đợt.
"""
import argparse
import pathlib
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common.imagegen import gen  # noqa: E402
from src.studio.cutout import cut_parts  # noqa: E402

HEADS = [("neutral", "calm neutral, mouth closed"), ("neutral_talk", "calm neutral, mouth open talking"),
         ("smirk", "SIG, mouth closed"), ("smirk_talk", "SIG, mouth open talking"),
         ("shocked", "shocked, eyes wide, mouth open"), ("angry", "angry frown, mouth open shouting"),
         ("sad", "sad, mouth closed"), ("blink", "calm neutral with eyes closed (blink)")]
POSES = ("relaxed:standing relaxed, arms down|hips:hands on hips, confident|"
         "phone:right hand holding a small flip phone up near where the ear would be|point:right arm pointing forward")


def face_right(body_dir: pathlib.Path) -> None:
    """Đầu chibi luôn nhìn sang phải; AI đôi khi vẽ thân quay trái (tay chỉ về bên trái) thì lật cả bộ thân."""
    from PIL import Image, ImageOps
    from src.studio.stage import hand_point
    point = body_dir / "body_point.png"
    if not point.exists():
        return
    img = Image.open(point)
    if hand_point(img)[0] < img.width / 2:
        for f in body_dir.glob("body_*.png"):
            ImageOps.mirror(Image.open(f)).save(f)
        print("đã lật thân cho cùng hướng đầu:", body_dir.name)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id")
    ap.add_argument("--look", help="ngoại hình cố định (tiếng Anh), bắt buộc khi tạo mới")
    ap.add_argument("--gender", default="")
    ap.add_argument("--age", default="")
    ap.add_argument("--signature", default="confident half smirk")
    ap.add_argument("--outfit", required=True, help="id bộ trang phục, ví dụ ao-phong-2002")
    ap.add_argument("--outfit-desc", required=True)
    ap.add_argument("--poses", default=POSES)
    ap.add_argument("--style-ref", default="assets/actors/nam-18-a/source/puppet.jpg",
                    help="bảng rối của diễn viên đã duyệt, chỉ để bắt chước nét vẽ (diễn viên mới)")
    a = ap.parse_args()
    style = yaml.safe_load((ROOT / "channels/khoai-tay-review/channel.yaml").read_text(encoding="utf-8"))["visual_style"]
    d = ROOT / "assets/actors" / a.id
    src = d / "source"
    card_p = d / "card.yaml"
    card = yaml.safe_load(card_p.read_text(encoding="utf-8")) if card_p.exists() else None
    if card is None and not a.look:
        raise SystemExit("Diễn viên mới cần --look")
    look = card["look"] if card else a.look
    sig = card["signature"] if card else a.signature
    poses = [p.split(":", 1) for p in a.poses.split("|")]
    bodies = "; ".join(f"({i + 1}) {desc}" for i, (_, desc) in enumerate(poses))

    first = card is None or not (src / "puppet.jpg").exists()
    sheet = src / f"sheet_{a.outfit}.jpg"
    ref = ROOT / a.style_ref
    use_ref = first and ref.exists() and ref.parent.parent.name != a.id
    style_note = ("Copy EXACTLY the art style of the reference image (line weight, flat colors, chibi proportions, head "
                  "size, face drawing) but draw a DIFFERENT person as described. " if use_ref else "")
    gen(f"Character reference sheet. {style_note}{style}. {look}. Outfit: {a.outfit_desc}. The same character 4 times side by side on "
        "a plain white background: front view, three-quarter view, side profile, back view. Full body, identical face, "
        "hair and outfit. No text.", [src / "puppet.jpg"] if not first else ([ref] if use_ref else []), sheet)
    if first:
        heads = "; ".join(f"({i + 1}) {desc.replace('SIG', sig)}" for i, (_, desc) in enumerate(HEADS))
        for attempt in range(2):                     # AI vẽ sai số bộ phận thì tạo lại 1 lần
            gen("PUPPET PARTS SHEET for a cut-out animation of exactly this character (same face, hair, outfit, line art). "
              f"{style}. Pure flat white background, a clean grid of 12 separate parts in 3 rows x 4 columns with generous "
              "white space, nothing overlapping or touching, no borders, no text. EXACTLY 12 parts: 8 heads + 4 bodies. All parts at the SAME scale as each other "
              "(heads match the bodies), all at the SAME slight three-quarter angle. Rows 1 and 2: 8 HEADS ONLY (big chibi "
              f"heads, NO neck, NO shoulders, ending at the chin; long hair is NOT cut flat: it hangs naturally in full down to shoulder level as part of the head), same size and position in each cell, in reading order: {heads}. "
              "Row 3: 4 HEADLESS chibi BODIES (NO head, NO neck, the top ends flat at the shoulders/collar line, with a CLOSED black outline across the collar, shoulders and sleeves clearly drawn), "
              f"full body down to the feet, poses: {bodies}.", [sheet], src / "puppet.jpg")
            try:
                cut_parts(src / "puppet.jpg", [f"head_{k}" for k, _ in HEADS], [f"{a.outfit}/body_{k}" for k, _ in poses],
                          d / "parts")
                break
            except ValueError as e:
                print("bảng rối sai:", e)
                if attempt:
                    raise
                (src / "puppet.jpg").rename(src / "puppet_rejected.jpg")
    else:
        gen(f"BODY PARTS SHEET for the same character in a new outfit ({a.outfit_desc}), same chibi proportions and scale "
            f"as the bodies in puppet.jpg. {style}. Pure flat white background. {len(poses)} separate HEADLESS chibi bodies "
            "(NO head, NO neck, top ends flat at the shoulders/collar line, with a CLOSED black outline across the collar, shoulders and sleeves clearly drawn), full body down to the feet, same slight "
            f"three-quarter angle, in {len(poses)} equal columns, generous white space, nothing overlapping, no text. "
            f"Poses: {bodies}.", [src / "puppet.jpg", sheet], src / f"bodies_{a.outfit}.jpg")
        cut_parts(src / f"bodies_{a.outfit}.jpg", [], [f"{a.outfit}/body_{k}" for k, _ in poses], d / "parts")

    face_right(d / "parts" / a.outfit)
    card = card or {"id": a.id, "kind": "actor", "gender": a.gender, "age": a.age, "look": look, "signature": sig,
                    "rig": {"mode": "chibi", "head_scale": 1.0, "overlap": 0.10, "neck_dx": {}},
                    "heads": {k: f"parts/head_{k}.png" for k, _ in HEADS}, "outfits": {}, "roles": []}
    card["outfits"][a.outfit] = {"desc": a.outfit_desc, "sheet": f"source/{sheet.name}",
                                 "bodies": {k: f"parts/{a.outfit}/body_{k}.png" for k, _ in poses}}
    card_p.write_text(yaml.safe_dump(card, allow_unicode=True, sort_keys=False), encoding="utf-8")

    from PIL import Image
    from src.studio.stage import Puppet
    pup = Puppet(d, a.outfit)
    ks = list(card["outfits"][a.outfit]["bodies"])
    canvas = Image.new("RGBA", (400 * len(ks), 560), (120, 130, 150, 255))
    for i, b in enumerate(ks):
        fig, _ = pup.figure(b, ["neutral", "smirk", "shocked", "angry"][i % 4])
        k = min(520 / fig.height, 380 / fig.width)
        fig = fig.resize((int(fig.width * k), int(fig.height * k)), Image.LANCZOS)
        canvas.alpha_composite(fig, (i * 400 + 200 - fig.width // 2, 545 - fig.height))
    canvas.convert("RGB").save(d / f"preview_{a.outfit}.jpg")
    print("Xong:", (d / f"preview_{a.outfit}.jpg").relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
