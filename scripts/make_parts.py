"""PHÒNG THIẾT KẾ NHÂN VẬT, bước 1: tạo KHO BỘ PHẬN MẶT (assets/parts/) từ các bảng icon do AI vẽ, cắt ra PNG nền
trong, ghi parts.yaml. src/studio/avatar.py ghép các lớp (mặt → mắt → mày → mũi → miệng → tóc → phụ kiện) thành đầu
diễn viên đủ biểu cảm.

python scripts/make_parts.py --prompt heads             # in prompt để tạo trên web (heads | eyes_mouths | details)
python scripts/make_parts.py heads --sheet ảnh.png       # cắt ảnh tạo trên web
python scripts/make_parts.py all                         # agy tạo mọi bảng còn thiếu (mỗi bảng 1 ảnh)
Bảng đã có source/<tên>.jpg thì bỏ qua bước tạo ảnh.
"""
import argparse
import pathlib
import sys

import numpy as np
import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.common.imagegen import gen  # noqa: E402
from src.studio.cutout import cut_rows  # noqa: E402

STYLE = ("simple rustic chibi cartoon parts, thick uniform black outlines, flat solid colors, no shading, no highlights, "
         "minimal details, early-2000s Chinese TV cartoon / Flash animation look, no 3D, no gradients")
EXPR_EYES = [("normal", "calm open eyes"), ("closed", "closed eyes (blink)"), ("wide", "shocked wide round eyes"),
             ("angry", "angry narrowed eyes"), ("sad", "sad droopy eyes")]
EXPR_MOUTH = [("neutral", "small closed neutral mouth"), ("talk", "small open talking mouth"),
              ("smile", "closed confident smile"), ("grin", "open happy grin showing teeth"),
              ("shock", "round open shocked mouth"), ("shout", "wide open angry shouting mouth"),
              ("frown", "sad frown"), ("smirk", "one-sided smirk")]

FACES = [("face-round", "round young face"), ("face-oval", "oval young face"), ("face-square", "square jaw male face"),
         ("face-chubby", "chubby round face with full cheeks"), ("face-thin", "thin long face"),
         ("face-pointed", "pretty face with small pointed chin"), ("face-old-m", "old man face with a few wrinkles"),
         ("face-old-f", "old woman face with a few wrinkles"), ("face-mid-m", "middle-aged man face"),
         ("face-mid-f", "middle-aged woman face"), ("face-kid", "small child face, very round"),
         ("face-tough", "tough square face with strong jaw")]
HAIR = [("hair-messy-m", "short messy black hair, male"), ("hair-buzz", "black buzz cut"),
        ("hair-sidepart", "neat side-part black hair"), ("hair-slick", "slicked back black hair"),
        ("hair-spiky", "spiky black hair"), ("hair-bowl", "black bowl cut with bangs"),
        ("hair-bald-top", "balding: a thin ring of hair at the sides, bald top"), ("hair-grey-short", "short grey hair"),
        ("hair-long-bangs", "long straight black hair with bangs, falling to the shoulders"),
        ("hair-long-wavy", "long wavy black hair falling past the shoulders"), ("hair-ponytail", "black ponytail with bangs"),
        ("hair-twin", "black twin tails"), ("hair-bob", "black chin-length bob"), ("hair-bun", "black hair in a bun"),
        ("hair-perm", "short curly permed black hair, middle-aged woman"), ("hair-grey-bun", "grey hair in a bun"),
        ("hair-dyed-yellow", "short messy dyed yellow hair"), ("hair-long-m", "shoulder-length male hair"),
        ("hair-cap", "black baseball cap over short hair"), ("hair-brown-long", "long straight brown hair"),
        ("hair-pixie", "short black pixie cut, female"), ("hair-mid-m", "short neat hair with grey temples"),
        ("hair-braid", "long black side braid"), ("hair-flat", "flat top black hair")]
EYES = [[(f"eyes{s}-{k}", d) for k, d in EXPR_EYES] for s in range(1, 6)]
MOUTHS = [[(f"mouth{s}-{k}", d) for k, d in EXPR_MOUTH] for s in range(1, 4)]
BROWS = [[(f"brows{s}-{k}", f"{st} eyebrows, {k}") for s, st in ((1, "thin"), (2, "thick"), (3, "elegant"))
          for k in ("normal", "angry", "sad", "raised")][r * 6:(r + 1) * 6] for r in range(2)]
EXTRAS = [[("nose1", "small dot nose"), ("nose2", "small curved nose"), ("nose3", "small triangle nose"),
           ("nose4", "round nose"), ("glasses-round", "round glasses"), ("glasses-square", "square glasses")],
          [("sunglasses", "black sunglasses"), ("beard-stubble", "short stubble beard area"),
           ("mustache", "small mustache"), ("blush", "pair of pink blush ovals"), ("mole", "small mole dot"),
           ("scar", "small scar mark")]]

# Bảng thực tế đã tạo trên web 28/9/2026 (AI vẽ khác đề: tóc liền mặt, mắt kèm lông mày) → khai đúng những gì có
E4 = ("normal", "angry", "sad", "wide")
V1 = {
    "heads_v1": [("heads", [(f"head-{k}", k) for k in ("round", "oval", "square", "chubby", "long", "oval2", "pointed",
                                                         "pointed2")]),
                 ("heads", [("head-old-m-special", "ông già nhắm mắt (có sẵn nét mặt)"), ("head-old-f", "bà già nếp nhăn"),
                            ("head-mid-m", "tóc ngắn đen"), ("head-mid-f", "tóc ngắn nữ"), ("head-kid", "trẻ con trọc"),
                            ("head-mid-m2", "tóc ngắn gọn"), ("head-tough-special", "mặt ngầu (có sẵn nét mặt)")]),
                 ("heads", [(f"head-{k}", k) for k in ("messy", "buzz", "sidepart", "slick", "spiky", "bowl", "balding",
                                                         "grey-short")]),
                 ("heads", [(f"head-{k}", k) for k in ("long-bangs", "long-wavy", "ponytail", "twin", "bob", "bun", "perm",
                                                         "grey-bun")]),
                 ("heads", [(f"head-{k}", k) for k in ("yellow", "long-m", "cap", "brown-long", "short-f", "grey-temples",
                                                         "braid", "flat")])],
    "eyes_mouths_v1": [("eyes", [(f"eyes{s}-{k}", f"mắt {st}, {vi}") for k, vi in (("normal", "bình thường"),
                         ("closed", "nhắm"), ("wide", "mở to sốc"), ("angry", "giận"), ("sad", "buồn"))])
                        for s, st in ((1, "chấm đen đơn giản"), (2, "nam sắc sảo kèm lông mày rậm"),
                                      (3, "nữ to có mi cong"), (4, "trung niên mệt mỏi, bọng mắt"),
                                      (5, "tròn to trẻ con"))] +
                      [("mouths", [(f"mouth{s}-{k}", f"miệng {st}, {d}") for k, d in EXPR_MOUTH])
                       for s, st in ((1, "nam đơn giản"), (2, "nữ môi đỏ"), (3, "người già"))],
    "details_v1": [("eyes", [(f"eyes6-{k}", "mảnh") for k in E4] + [(f"eyes7-{k}", "rậm") for k in E4[:2]]),
                   ("eyes", [(f"eyes7-{k}", "rậm") for k in E4[2:]] + [(f"eyes8-{k}", "thanh tú") for k in E4]),
                   ("extras", [("nose1", ""), ("nose2", ""), ("nose3", ""), ("nose4", ""), ("glasses-round", ""),
                               ("glasses-square", "")]),
                   ("extras", [("sunglasses", ""), ("beard-stubble", ""), ("mustache", ""), ("blush", ""), ("mole", ""),
                               ("scar", "")])],
}

# mỗi bảng = các hàng (kind, danh sách (id, mô tả)); hàng tóc cần xoá vùng trắng khép kín (lỗ mặt)
NOSES2 = [("nose5", "small curved hook line nose like the letter J, no nostrils"),
          ("nose6", "tiny button nose: two small nostril dots with a short curve above"),
          ("nose7", "small L-shaped line nose seen slightly from the side"),
          ("nose8", "cute tiny upturned nose with a soft rounded tip outline"),
          ("nose9", "elegant thin straight nose line with a small curve at the bottom"),
          ("nose10", "wide flat older person's nose outline"), ("nose11", "long pointed sharp nose outline (villain)"),
          ("nose12", "small nose shown only by a light pink nostril curve")]
SHEETS = {
    "heads": [("faces", FACES[:6]), ("faces", FACES[6:]), ("hair", HAIR[:8]), ("hair", HAIR[8:16]), ("hair", HAIR[16:])],
    "eyes_mouths": [("eyes", r) for r in EYES] + [("mouths", r) for r in MOUTHS],
    "details": [("brows", r) for r in BROWS] + [("extras", r) for r in EXTRAS],
    # bổ sung 28/9/2026: mũi đẹp thay mũi chấm đen, môi đỏ dày (tiểu tam, quý bà), chi tiết mặt; gộp 1 ảnh cho đỡ tốn lượt
    "details_v2": [("extras", NOSES2),
                   ("mouths", [(f"mouth4-{k}", f"full glamorous red lipstick lips, {d}") for k, d in EXPR_MOUTH]),
                   ("extras", [("mole-lip", "small black beauty mole dot"), ("mole-tear", "tiny black tear mole dot"),
                               ("freckles", "a band of small light brown freckle dots across both cheeks and nose"),
                               ("eye-bags", "pair of tired under-eye bag curves"),
                               ("bandaid", "small beige adhesive bandage"), ("beard-full", "full black beard around the jaw"),
                               ("goatee", "small black goatee"), ("wrinkles", "three short forehead wrinkle lines")]),
                   # bảng web 28/9 vẽ 4 chiếc lẻ (không thành đôi): ghép 1 chiếc cho cả 2 tai; bản -b là chiếc thứ hai, dự phòng
                   ("extras", [("earring-gold", "single gold hoop earring"), ("earring-gold-b", "single gold hoop earring"),
                               ("earring-pearl", "single pearl drop earring"),
                               ("earring-pearl-b", "single pearl drop earring")])],
}
INTRO = {
    "heads": "Rows 1-2: BLANK chibi HEADS seen from the FRONT, all the same size, bald (NO hair), with ears, light warm "
             "skin tone, NO eyes, NO eyebrows, NO nose, NO mouth (completely empty face), no neck. Rows 3-5: HAIRSTYLES "
             "ONLY (NO face, NO head, NO ears), each drawn as it would sit on those heads seen from the front, with an "
             "EMPTY face-shaped opening in the middle; long hair hangs down on both sides of the opening",
    "eyes_mouths": "Rows 1-5: PAIRS OF EYES (both eyes together as one item, front view, no face, no skin around). Each "
                   "row is one eye style (row 1 simple black dot eyes, row 2 sharp confident male eyes, row 3 big pretty "
                   "female eyes with lashes, row 4 small tired middle-aged eyes, row 5 cute round kid eyes); columns: calm "
                   "open, closed (blink, curved lines), shocked wide round, angry narrowed, sad droopy. Rows 6-8: MOUTHS "
                   "only (lips, front view, no face, no skin around): row 6 simple male, row 7 female with light red lips, "
                   "row 8 old person",
    "details": "Small separate face pieces, front view, no face, no skin background. Rows 1-2: PAIRS of eyebrows "
               "(both brows together as one item). Rows 3-4: noses, glasses and small face details",
    "details_v2": "Small separate face pieces for a cute chibi face, front view, no face, no skin background. Row 1: NOSES "
                  "(simple cute cartoon noses, NOT a plain black dot). Row 2: MOUTHS only (lips, no face): full red "
                  "lipstick lips in 8 expressions. Rows 3-4: small face details",
}


# KHO THÂN theo bộ đồ: 1 ảnh = 1 bộ đồ × 3 vóc (hàng) × 4 tư thế (cột), nhìn thẳng, không đầu
BUILDS = [("thin", "thin slim build"), ("normal", "average build"), ("fat", "chubby fat build with a round belly")]
POSES = [("relaxed", "standing relaxed, arms down"), ("hips", "hands on hips"),
         ("phone", "right hand holding a small phone up near the head"), ("point", "right arm pointing to the side")]
OUTFITS = {   # id: (giới, mô tả tiếng Anh, mô tả tiếng Việt cho mục lục)
    "m-tshirt-jeans": ("male", "plain white T-shirt, blue jeans, white sneakers", "áo phông trắng, quần bò"),
    "m-school": ("male", "white short-sleeve school shirt, dark blue trousers, black shoes", "đồng phục học sinh nam"),
    "m-office": ("male", "light blue long-sleeve office shirt tucked in, grey trousers, belt, black shoes", "sơ mi công sở"),
    "m-suit": ("male", "dark navy suit, white shirt, red tie, black leather shoes", "vest cà vạt (sếp, doanh nhân)"),
    "m-polo": ("male", "branded polo shirt, beige chinos, white sneakers", "polo hàng hiệu (công tử)"),
    "m-tank": ("male", "white sleeveless undershirt, grey shorts, plastic slippers", "áo ba lỗ, quần đùi (ở nhà)"),
    "m-hoodie": ("male", "grey hoodie, black jeans, sneakers", "áo hoodie"),
    "m-leather": ("male", "black leather jacket, black T-shirt, ripped jeans, boots", "áo da (côn đồ, đại ca)"),
    "m-worker": ("male", "dirty blue work overalls, rubber boots", "quần áo lao động"),
    "m-guard": ("male", "black security guard uniform, cap-less, black shoes", "bảo vệ, vệ sĩ"),
    "m-police": ("male", "Chinese police uniform, light blue shirt, dark trousers", "cảnh sát"),
    "m-doctor": ("male", "white doctor coat over shirt and tie, stethoscope", "bác sĩ"),
    "m-waiter": ("male", "white shirt, black vest, bow tie, black trousers", "phục vụ, quản gia"),
    "m-oldman": ("male", "old-fashioned grey Zhongshan tunic suit, cloth shoes", "áo Tôn Trung Sơn (ông già)"),
    "f-school": ("female", "white short-sleeve blouse, light blue pleated skirt, white canvas shoes", "đồng phục nữ sinh"),
    "f-office": ("female", "black blazer, white blouse, black pencil skirt, high heels", "công sở (thư ký, nữ tổng tài)"),
    "f-evening": ("female", "long red evening gown, high heels", "đầm dạ hội đỏ"),
    "f-casual": ("female", "white T-shirt, denim shorts, sneakers", "áo phông quần short"),
    "f-dress": ("female", "light floral summer dress, sandals", "váy hoa mùa hè"),
    "f-home": ("female", "floral short-sleeve blouse, dark trousers, apron", "đồ ở nhà có tạp dề (mẹ, bà thím)"),
    "f-nurse": ("female", "white nurse uniform", "y tá"),
    "f-qipao": ("female", "elegant blue qipao dress, heels", "sườn xám"),
    "f-sport": ("female", "tracksuit jacket and pants, sneakers", "đồ thể thao"),
    "f-oldwoman": ("female", "dark old-fashioned blouse and trousers, cloth shoes", "bà già"),
    # bổ sung 28/9/2026 cho truyện drama (thứ tự tạo: board/image_queue.yaml)
    "f-white-dress": ("female", "simple plain white knee-length dress, white flats", "váy trắng đơn giản (trà xanh)"),
    "f-lady": ("female", "elegant beige wool coat over a dark dress, pearl necklace, heels", "quý phu nhân, mẹ nhà giàu"),
    "f-wedding": ("female", "white wedding gown with a long skirt, white heels", "váy cưới"),
    "m-groom": ("male", "white wedding suit, white shirt, red bow tie, white shoes", "vest chú rể"),
    "f-pajama": ("female", "pink long-sleeve pajamas, slippers", "đồ ngủ nữ"),
    "f-patient": ("female", "blue and white striped hospital patient clothes, slippers", "áo bệnh nhân nữ"),
    "m-patient": ("male", "blue and white striped hospital patient clothes, slippers", "áo bệnh nhân nam"),
    "f-poor": ("female", "faded old patched blouse and loose trousers, worn cloth shoes", "quần áo cũ vá (nghèo)"),
    "m-poor": ("male", "faded old patched shirt and loose trousers, worn cloth shoes", "quần áo cũ vá (nghèo)"),
}


def prompt_body(outfit: str) -> str:
    gender, desc, _ = OUTFITS[outfit]
    rows = " ".join(f"Row {i + 1}: {b} {gender}." for i, (_, b) in enumerate(BUILDS))
    poses = "; ".join(f"({i + 1}) {d}" for i, (_, d) in enumerate(POSES))
    return (f"BODY PARTS SHEET for a cut-out cartoon character maker. {STYLE}. Pure flat white background. Exactly 12 "
            f"HEADLESS chibi bodies (NO head, NO neck, the top ends flat at the shoulders with a closed black outline "
            f"across the collar), all seen from the FRONT, short chibi proportions, {gender}, wearing: {desc}. Arranged in 3 "
            f"clear rows x 4 columns with generous white space, nothing overlapping or touching, no text, no borders. "
            f"Leave the BOTTOM-RIGHT CORNER of the image completely EMPTY (white). {rows} Columns in every row: {poses}.")


def pose_of(part: Image.Image) -> str:
    """Nhận tư thế của một thân không đầu theo hình dáng (AI hay vẽ thừa/thiếu, sai thứ tự nên không tin vị trí).
    Đo trên bảng chuẩn 28/9: phần trên (0–25% cao) lệch phải = tay giơ; tay chỉ thì phần giữa bên phải trống,
    tay cầm điện thoại thì không; thả tay: bề ngang ở 55% cao > 1,15 lần ở vai, chống nạnh thì nhỏ hơn."""
    a = np.array(part.getchannel("A")) > 128
    h, w = a.shape
    cols = np.nonzero(a[int(h * 0.9)])[0]                     # trục thân = giữa hai bàn chân
    cx = (cols.min() + cols.max()) / 2 if len(cols) else w / 2

    def ext(y0, y1):
        c = np.nonzero(a[int(h * y0):int(h * y1)].any(axis=0))[0]
        return c.max() - cx, cx - c.min()

    def width(y):
        c = np.nonzero(a[int(h * y)])[0]
        return (c.max() - c.min()) if len(c) else 0
    r1, l1 = ext(0, 0.25)
    r2, l2 = ext(0.25, 0.5)
    if l1 > r1 * 1.2:                                          # tay giơ bên trái: lật ảnh cho về quy ước tay phải
        return "mirror"
    if r1 > l1 * 2.0 or (r1 > l1 * 1.2 and r2 < l2 * 0.9):
        return "point"
    if r1 > l1 * 1.2:
        return "phone"
    return "relaxed" if width(0.55) > width(0.12) * 1.15 else "hips"


def cut_bodies(sheet: pathlib.Path, out_dir: pathlib.Path) -> list[str]:
    """3 hàng = 3 vóc; mỗi hàng tách thân theo khe trống, nhận tư thế từng thân, giữ thân đầu tiên của mỗi tư thế.
    Trả về các tổ hợp còn thiếu (vóc-tư thế) để tạo bù."""
    from scipy import ndimage
    from src.studio.cutout import remove_background
    img = remove_background(Image.open(sheet))
    a = np.array(img.getchannel("A"))
    H, W = a.shape
    a[int(H * 0.90):, int(W * 0.93):] = 0                     # góc logo
    occ = (a > 128).any(axis=1)
    runs, start = [], None                                    # dải hàng: các đoạn có nét, gộp đoạn quá mỏng
    for y in range(H + 1):
        v = occ[y] if y < H else False
        if v and start is None:
            start = y
        if not v and start is not None:
            runs.append([start, y])
            start = None
    runs = [r for r in runs if r[1] - r[0] > H * 0.05]
    runs = sorted(sorted(runs, key=lambda r: r[0] - r[1])[:3])
    rgba = np.array(img)
    out_dir.mkdir(parents=True, exist_ok=True)
    missing = []
    for (b, _), (y0, y1) in zip(BUILDS, runs):
        band = a[y0:y1] > 128
        lab, n = ndimage.label(band)
        objs = [o for o in ndimage.find_objects(lab)
                if (o[0].stop - o[0].start) > (y1 - y0) * 0.5]          # thân (bỏ vụn)
        got = {}
        for o in sorted(objs, key=lambda o: o[1].start):
            k = next(k for k, oo in enumerate(ndimage.find_objects(lab), 1) if oo == o)
            m = np.zeros_like(a)
            m[y0:y1][lab == k] = 255
            part = rgba.copy()
            part[..., 3] = np.minimum(part[..., 3], m)
            pi = Image.fromarray(part)
            pi = pi.crop(pi.getchannel("A").getbbox())
            pose = pose_of(pi)
            if pose == "mirror":
                pi = pi.transpose(Image.FLIP_LEFT_RIGHT)
                pose = pose_of(pi)
            if pose not in got:
                got[pose] = pi
        for p, _ in POSES:
            if p in got:
                got[p].save(out_dir / f"{b}-{p}.png")
            else:
                missing.append(f"{b}-{p}")
    for b, _ in BUILDS[len(runs):]:
        missing += [f"{b}-{p}" for p, _ in POSES]
    return missing


def build_bodies(outfit: str, sheet_arg: str | None) -> None:
    d = ROOT / "assets/parts"
    sheet = d / "source" / f"body_{outfit}.jpg"
    if sheet_arg and not sheet.exists():
        sheet.parent.mkdir(parents=True, exist_ok=True)
        Image.open(sheet_arg).convert("RGB").save(sheet, quality=95)
    gen(prompt_body(outfit), [], sheet)
    missing = cut_bodies(sheet, d / "bodies" / outfit)
    reg = d / "parts.yaml"
    data = yaml.safe_load(reg.read_text(encoding="utf-8")) if reg.exists() else {}
    gender, _, vi = OUTFITS[outfit]
    data[f"outfit:{outfit}"] = {"file": f"bodies/{outfit}", "kind": "bodies", "gender": gender,
                                 "desc": f"{vi}; vóc thin/normal/fat; tư thế relaxed/hips/phone/point"
                                         + (f"; THIẾU: {', '.join(missing)}" if missing else ""),
                                 "missing": missing}
    reg.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    write_index()
    print("Xong bộ đồ", outfit, "| thiếu:", ", ".join(missing) or "không")


def prompt_of(name: str) -> str:
    rows = {**SHEETS, **V1}[name]
    listing = " ".join(f"Row {r + 1} ({len(items)} items): " + "; ".join(d or pid for pid, d in items) + "."
                       for r, (_, items) in enumerate(rows))
    total = sum(len(items) for _, items in rows)
    return (f"PARTS SHEET for a cut-out cartoon character maker. {STYLE}. Pure flat white background. Exactly {total} "
            f"separate items arranged in {len(rows)} clear ROWS, each item alone in its own block with generous white "
            "space between items and between rows, nothing overlapping or touching, all items in a row the same size, no "
            "borders, no grid lines, no text, no numbers. Leave the BOTTOM-RIGHT CORNER of the image completely EMPTY "
            f"(white). {INTRO.get(name, '')}. {listing}")


def build(name: str, sheet_arg: str | None) -> None:
    d = ROOT / "assets/parts"
    rows = {**SHEETS, **V1}[name]
    sheet = d / "source" / f"{name}.jpg"
    if sheet_arg and not sheet.exists():
        sheet.parent.mkdir(parents=True, exist_ok=True)
        Image.open(sheet_arg).convert("RGB").save(sheet, quality=95)
    gen(prompt_of(name), [], sheet)
    names = [[f"{kind}/{pid}" for pid, _ in items] for kind, items in rows]
    cut_rows(sheet, names, d, {r for r, (kind, _) in enumerate(rows) if kind == "hair"})
    reg = d / "parts.yaml"
    data = yaml.safe_load(reg.read_text(encoding="utf-8")) if reg.exists() else {}
    for kind, items in rows:
        for pid, desc in items:
            data[pid] = {"file": f"{kind}/{pid}.png", "kind": kind, "desc": desc}
    reg.write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    write_index()
    print("Xong bảng", name, sum(len(i) for _, i in rows), "bộ phận")


def fill_missing(outfit: str) -> list[str]:
    """Tạo bù các ô thân còn thiếu của một bộ đồ: 1 ảnh, 1 hàng, đúng thứ tự các ô thiếu, lấy thân đã có làm mẫu."""
    d = ROOT / "assets/parts"
    data = yaml.safe_load((d / "parts.yaml").read_text(encoding="utf-8"))
    missing = data.get(f"outfit:{outfit}", {}).get("missing", [])
    if not missing:
        return []
    gender, desc, vi = OUTFITS[outfit]
    bdesc, pdesc = dict(BUILDS), dict(POSES)
    items = "; ".join(f"({i + 1}) {bdesc[m.split('-')[0]]}, {pdesc[m.split('-')[1]]}" for i, m in enumerate(missing))
    ref = next((d / "bodies" / outfit).glob("normal-relaxed.png"), None) or next((d / "bodies" / outfit).glob("*.png"))
    sheet = d / "source" / f"body_{outfit}_fill.jpg"
    if sheet.exists():
        sheet.unlink()
    gen(f"Same character body style as the reference image (same outfit, same colors, same line art). {STYLE}. Pure flat "
        f"white background. Exactly {len(missing)} HEADLESS chibi bodies (NO head, NO neck, the top ends flat at the "
        f"shoulders with a closed black outline across the collar), seen from the FRONT, {gender}, wearing: {desc}. "
        f"One single row, left to right, generous white space, nothing touching, no text. Leave the BOTTOM-RIGHT CORNER "
        f"empty. In order: {items}.", [ref], sheet)
    tmp = d / "bodies" / f"_{outfit}_fill"
    cut_rows(sheet, [[m for m in missing]], tmp)
    for m in missing:
        (tmp / f"{m}.png").rename(d / "bodies" / outfit / f"{m}.png")
    tmp.rmdir()
    data[f"outfit:{outfit}"]["missing"] = []
    data[f"outfit:{outfit}"]["desc"] = data[f"outfit:{outfit}"]["desc"].split("; THIẾU")[0]
    (d / "parts.yaml").write_text(yaml.safe_dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return missing


def todo() -> int:
    """Việc tồn: bộ đồ chưa có bảng thân → tạo; bộ đồ còn ô thiếu → tạo bù. Lỗi (thường là hết lượt ảnh) → mã 1."""
    d = ROOT / "assets/parts"
    for outfit in OUTFITS:
        try:
            if not (d / "bodies" / outfit).exists():
                build_bodies(outfit, None)
            got = fill_missing(outfit)
            if got:
                print("Đã bù", outfit, ", ".join(got))
        except RuntimeError as e:
            print("Dừng (thường là hết lượt ảnh):", str(e)[:120])
            return 1
    write_index()
    print("Hết việc tồn")
    return 0


def write_index() -> None:
    """assets/parts/INDEX.md: mục lục có chú thích cho AI (đạo diễn, người thiết kế nhân vật) đọc để chọn bộ phận."""
    d = ROOT / "assets/parts"
    data = yaml.safe_load((d / "parts.yaml").read_text(encoding="utf-8"))
    groups = {}
    for k, v in data.items():
        groups.setdefault(v["kind"], []).append((k, v.get("desc", "")))
    L = ["# Kho bộ phận nhân vật (assets/parts/)", "",
         "Mục lục cho AI và người đọc, sinh tự động từ `parts.yaml` bởi `scripts/make_parts.py`. Ghép bằng "
         "`src/studio/avatar.py` theo bản thiết kế `assets/actors/<id>/avatar.yaml`.", "", "## Cách ghép",
         "- Lớp từ sau ra trước: **thân** (bộ đồ × vóc × tư thế) → **đầu nền** (mặt + tai + tóc) → **mắt** (đã kèm "
         "lông mày) → mũi → miệng → phụ kiện (râu, má hồng, nốt ruồi, sẹo) → kính.",
         "- Chọn **kiểu** mắt và miệng (ví dụ `eyes2`, `mouth1`); biểu cảm tự ghép: bình thường, nói, cười nhếch, "
         "sốc, giận, buồn, chớp mắt.",
         "- Kiểu mắt 6–8 chỉ có 4 biểu cảm (normal, angry, sad, wide); nhắm mắt mượn của kiểu 1.",
         "- Đầu có đuôi `-special` đã vẽ sẵn nét mặt: không ghép mắt, miệng.",
         "- Màu da đổi bằng `skin: \"#rrggbb\"` trong bản thiết kế.", ""]
    names = {"heads": "Đầu nền (mặt + tóc)", "eyes": "Mắt (kèm lông mày)", "mouths": "Miệng",
             "extras": "Mũi, kính, chi tiết mặt", "bodies": "Thân theo bộ đồ (thư mục bodies/<bộ đồ>/<vóc>-<tư thế>.png)"}
    for kind, title in names.items():
        if kind in groups:
            L += [f"## {title}", "", "| id | mô tả |", "|---|---|"] + [f"| `{k}` | {v} |" for k, v in groups[kind]] + [""]
    (d / "INDEX.md").write_text("\n".join(L), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", default="all", help=f"một trong {list(SHEETS) + list(V1)} hoặc all")
    ap.add_argument("--prompt", nargs="?", const="1", help="chỉ in prompt của bảng này (hoặc của --body)")
    ap.add_argument("--sheet")
    ap.add_argument("--todo", action="store_true", help="làm việc tồn: bộ đồ chưa có + ô thân thiếu (agy)")
    ap.add_argument("--body", help="bộ đồ trong OUTFITS: tạo/cắt bảng thân (kèm --sheet nếu tạo trên web)")
    a = ap.parse_args()
    if a.todo:
        return todo()
    if a.body:
        if a.prompt:
            print(prompt_body(a.body))
        else:
            build_bodies(a.body, a.sheet)
        return 0
    if a.prompt:
        print(prompt_of(a.prompt))
        return 0
    for n in (SHEETS if a.name == "all" else [a.name]):
        build(n, a.sheet if a.name != "all" else None)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
