"""Tạo THƯ VIỆN ĐẠO CỤ (assets/props/): 1 bảng 6 cột x 4 hàng = 24 đạo cụ bằng agy, cắt ra PNG nền trong, ghi props.yaml.
Đạo cụ được stage.py dán vào tay diễn viên (`prop: pistol` trong cảnh), khớp tương đối.

python scripts/make_props.py --prompt                                   # in prompt để tạo trên web
python scripts/make_props.py [--sheet đường/dẫn/ảnh_tạo_trên_web.png]   # có --sheet thì không gọi agy
Đã có source/sheet_1.jpg thì bỏ qua bước tạo ảnh. size = cạnh dài so với chiều cao đầu; grip = điểm cầm (tỉ lệ).
"""
import argparse
import pathlib
import sys

import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common.imagegen import gen  # noqa: E402
from src.studio.cutout import cut  # noqa: E402

# id, mô tả vẽ, size, grip [x, y]
PROPS = [
    ("flip-phone", "small silver flip phone, opened, early-2000s", 0.35, [0.5, 0.7]),
    ("smartphone", "black smartphone, screen facing viewer", 0.35, [0.5, 0.6]),
    ("pistol", "black handgun in side view, barrel pointing right", 0.55, [0.2, 0.75]),
    ("kitchen-knife", "kitchen knife in side view, blade pointing right", 0.6, [0.15, 0.5]),
    ("handbag", "red women's handbag with a top handle", 0.55, [0.5, 0.1]),
    ("backpack", "blue school backpack", 0.7, [0.5, 0.1]),
    ("briefcase", "black leather briefcase with handle on top", 0.7, [0.5, 0.1]),
    ("cash", "thick stack of red banknotes", 0.4, [0.5, 0.5]),
    ("black-card", "black bank card", 0.25, [0.3, 0.5]),
    ("wine-glass", "glass of red wine", 0.4, [0.5, 0.65]),
    ("cigarette", "lit cigarette with a small curl of smoke", 0.25, [0.25, 0.7]),
    ("car-key", "car key with remote fob", 0.25, [0.4, 0.4]),
    ("envelope", "thick brown paper envelope", 0.45, [0.3, 0.5]),
    ("contract", "sheet of paper document with lines of text scribbles", 0.5, [0.3, 0.6]),
    ("beer-bottle", "green glass beer bottle", 0.5, [0.5, 0.65]),
    ("flowers", "bouquet of red roses wrapped in paper", 0.7, [0.5, 0.8]),
    ("suitcase", "brown travel suitcase with handle", 0.8, [0.5, 0.05]),
    ("laptop", "open grey laptop", 0.6, [0.5, 0.8]),
    ("gift-box", "red gift box with a gold ribbon", 0.5, [0.5, 0.6]),
    ("ring-box", "small open ring box with a diamond ring", 0.25, [0.5, 0.7]),
    ("tea-cup", "white porcelain tea cup with steam", 0.3, [0.5, 0.6]),
    ("steel-pipe", "short steel pipe used as a street-fight weapon", 0.8, [0.15, 0.5]),
    ("umbrella", "closed black umbrella", 0.9, [0.5, 0.1]),
    ("newspaper", "folded newspaper", 0.45, [0.3, 0.5]),
]
COLS, ROWS = 6, 4


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", help="ảnh bảng đạo cụ tạo sẵn (6x4, đúng thứ tự PROPS)")
    ap.add_argument("--prompt", action="store_true", help="chỉ in prompt")
    a = ap.parse_args()
    d = ROOT / "assets/props"
    sheet = d / "source/sheet_1.jpg"
    if a.sheet and not sheet.exists():
        sheet.parent.mkdir(parents=True, exist_ok=True)
        Image.open(a.sheet).convert("RGB").save(sheet, quality=95)
    # chỉ lấy phần nét vẽ của phong cách kênh, bỏ phần tả nhân vật để AI không vẽ người vào bảng đạo cụ
    style = ("simple rustic cartoon objects, thick uniform black outlines, flat solid colors, no shading, no highlights, "
             "minimal details, early-2000s Chinese TV cartoon / Flash animation look, no 3D, no photorealism, no gradients")
    items = "; ".join(f"({i + 1}) {desc}" for i, (_, desc, _, _) in enumerate(PROPS))
    prompt = (f"PROPS SHEET for a cut-out cartoon animation. {style}. Pure flat white background, a clean grid of "
              f"{len(PROPS)} separate objects in {ROWS} rows x {COLS} columns with generous white space, nothing overlapping "
              "or touching, no hands, no people, no borders, no text. Each object drawn alone, whole, with a closed thick "
              f"black outline. In reading order (left to right, top to bottom): {items}.")
    if a.prompt:
        print(prompt)
        return 0
    gen(prompt, [], sheet)
    cut(sheet, COLS, ROWS, d, [p[0] for p in PROPS])
    yml = d / "props.yaml"
    old = yaml.safe_load(yml.read_text(encoding="utf-8")) if yml.exists() else {}
    for pid, desc, size, grip in PROPS:
        old.setdefault(pid, {"file": f"{pid}.png", "desc": desc, "size": size, "grip": grip})
    yml.write_text(yaml.safe_dump(old, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("Xong:", len(PROPS), "đạo cụ trong", d.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
