"""THƯ VIỆN NỀN theo bảng: 1 ảnh = 3 nền (trên trái, trên phải, dưới trái; góc dưới phải để trống cho logo của app tạo
ảnh). Tạo trên web cho đỡ tốn lượt, cắt ra assets/scenes/<id>/master.jpg + card.yaml, cập nhật INDEX.md.

python scripts/make_scene_sheet.py --prompts                 # ghi tmp/scene_prompts.md (8 ảnh = 24 nền)
python scripts/make_scene_sheet.py 3 --sheet tmp/scene_3.png # cắt bảng số 3 (ảnh tạo trên web)
python scripts/make_scene_sheet.py 9                         # agy tự tạo ảnh bảng 9 rồi cắt
Ngày/đêm không cần ảnh riêng: đổi bằng lọc màu khi dựng.
"""
import argparse
import pathlib

import numpy as np
import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
SCENES = ROOT / "assets/scenes"

# bảng: [(id, mô tả tiếng Anh, thẻ tiếng Việt)] × 3
SHEETS = {
    1: ("TRƯỜNG HỌC", [
        ("school-gate", "a Chinese high school front gate with a sliding metal gate, school building behind, trees", "cổng trường, trường cấp 3"),
        ("classroom", "a Chinese classroom with rows of wooden desks, blackboard, windows on the side", "lớp học"),
        ("teacher-office", "a teachers' office with several desks piled with papers and books, a window", "phòng giáo viên")]),
    2: ("NHÀ Ở", [
        ("home-living-room", "a modest Chinese apartment living room: old sofa, small TV on a cabinet, dining table", "phòng khách nhà bình dân"),
        ("bedroom-young", "a small bedroom of a young man: single bed, desk with books, posters, window", "phòng ngủ thanh niên"),
        ("kitchen", "a small home kitchen with a gas stove, sink, cabinets", "nhà bếp")]),
    3: ("ĐƯỜNG PHỐ", [
        ("city-street-day", "a busy Chinese city street in daytime with small shops, awnings, sidewalk", "phố thương mại ban ngày"),
        ("city-street-night", "a Chinese city street at night with glowing shop lights and street lamps", "phố đêm"),
        ("residential-alley", "a narrow residential alley between old apartment buildings, bicycles, laundry", "ngõ khu dân cư")]),
    4: ("CÔNG SỞ", [
        ("ceo-office", "a luxurious CEO office: big wooden desk, leather chair, huge window with city skyline", "phòng giám đốc, tổng tài"),
        ("open-office", "an open-plan office with rows of cubicles and computers", "văn phòng nhân viên"),
        ("meeting-room", "a corporate meeting room with a long table, chairs, projector screen", "phòng họp")]),
    5: ("SANG TRỌNG", [
        ("hotel-banquet", "a luxury hotel VIP banquet room with a round table, chandelier, wine glasses", "phòng tiệc khách sạn"),
        ("luxury-restaurant", "an elegant restaurant with tablecloths, candles, large windows", "nhà hàng sang"),
        ("ktv-bar", "a KTV karaoke private room / bar with a sofa, screen, colorful lights", "quán bar, phòng karaoke")]),
    6: ("GIAO THÔNG", [
        ("car-interior", "the inside of a car seen from the back seat towards the driver seat and windshield", "trong xe hơi"),
        ("bus-interior", "the inside of a city bus with seats, hand rails and windows", "trong xe buýt"),
        ("night-road", "an empty road at night with street lamps and a guardrail", "đường đêm")]),
    7: ("CÔNG CỘNG", [
        ("hospital-ward", "a hospital ward with a bed, IV stand, curtains, window", "phòng bệnh viện"),
        ("rooftop", "the flat rooftop of a tall building with a railing and a city view", "sân thượng"),
        ("park", "a city park with a path, benches, trees and a small lake", "công viên")]),
    8: ("ĐẠI HỌC & QUÁN", [
        ("university-campus", "a Chinese university campus with a big teaching building and a wide plaza", "sân trường đại học"),
        ("dorm-room", "a university dorm room with bunk beds and four desks", "ký túc xá"),
        ("street-food-stall", "a night street food stall with plastic stools, small tables and a grill", "quán nướng vỉa hè")]),
}


# Bản 2 (28/9/2026): tạo lại các nền THIẾU CHỖ DIỄN (đồ đạc chiếm hết khung, nhân vật như đứng trên bàn ghế). Cùng id →
# cắt xong ghi đè master.jpg (bản cũ còn trong source/). Đồ đạc chỉ ở phía sau và hai bên, phía trước là sàn trống.
SHEETS.update({
    9: ("PHÒNG TIỆC & NHÀ HÀNG (bản có chỗ diễn)", [
        ("hotel-banquet", "a luxury hotel banquet hall: round dining tables with white cloths and chandeliers pushed to the BACK "
                          "of the room, a wide empty red carpet floor in the foreground", "phòng tiệc khách sạn"),
        ("luxury-restaurant", "an elegant restaurant: tables with candles along the back wall and sides, big windows, wide "
                              "empty polished floor in the foreground", "nhà hàng sang"),
        ("ktv-bar", "a karaoke/bar private room: long sofa and low table against the back wall, screen on the wall, colorful "
                    "lights, wide empty carpet floor in the foreground", "quán bar, phòng karaoke")]),
    10: ("TRƯỜNG HỌC (bản có chỗ diễn)", [
        ("classroom", "the FRONT of a Chinese classroom seen from the students' side: blackboard and teacher's desk at the back "
                      "wall, a few student desks only at the far left and right edges, wide empty floor in the middle foreground",
         "lớp học"),
        ("teacher-office", "a teachers' office: desks piled with papers along the back wall and one side, window, wide empty "
                           "tiled floor in the foreground", "phòng giáo viên"),
        ("dorm-room", "a university dorm room: bunk beds against the left and right walls, desks at the back, wide empty "
                      "floor in the middle foreground", "ký túc xá")]),
    11: ("CÔNG SỞ (bản có chỗ diễn)", [
        ("ceo-office", "a luxurious CEO office: big wooden desk and leather chair at the BACK in front of a huge window with "
                       "city skyline, wide empty floor with a rug in the foreground", "phòng giám đốc, tổng tài"),
        ("meeting-room", "a corporate meeting room: long table and chairs at the back half of the room, projector screen on the "
                         "back wall, wide empty floor in the foreground", "phòng họp"),
        ("open-office", "an open-plan office: rows of cubicles with computers along the back and sides, a wide empty aisle "
                        "floor in the middle foreground", "văn phòng nhân viên")]),
    12: ("NHÀ & NƠI KHÁC (bản có chỗ diễn)", [
        ("bedroom-young", "a small bedroom of a young man: single bed against the side wall, desk and window at the back, "
                          "wide empty wooden floor in the foreground", "phòng ngủ thanh niên"),
        ("hospital-ward", "a hospital ward: bed with IV stand against the back wall, curtain at one side, wide empty floor in "
                          "the foreground", "phòng bệnh viện"),
        ("car-roadside-night", "a black luxury car parked by the roadside at night under a street lamp, seen from the side "
                               "in the background, wide empty sidewalk pavement in the foreground", "xe sang đỗ bên đường đêm")]),
    13: ("BẾP & QUÁN (bản có chỗ diễn)", [
        ("kitchen", "a small home kitchen: stove, sink and cabinets along the back wall, wide empty tiled floor in the "
                    "foreground", "nhà bếp"),
        ("street-food-stall", "a night street food stall: grill and a few plastic tables and stools at the back and sides, "
                              "hanging lamps, wide empty pavement in the foreground", "quán nướng vỉa hè"),
        ("home-living-room", "a modest Chinese apartment living room: old sofa, TV cabinet and dining table along the back "
                             "wall and sides, wide empty tiled floor in the foreground", "phòng khách nhà bình dân")]),
})

# Bản 3 (28/9/2026): nền mới cho truyện drama (nhà giàu, bệnh viện, pháp lý, mua sắm, nhà nghèo, trời và đường cho xe cộ).
# Tạo 1 nền/ảnh bằng --single <id>, thứ tự và độ ưu tiên ở board/image_queue.yaml. Id bắt đầu "sky-" = trời, không cần sàn.
SHEETS.update({
    14: ("NHÀ GIÀU", [
        ("villa-living-room", "a luxurious villa living room: big leather sofas, marble coffee table, grand staircase and a "
                              "crystal chandelier at the BACK, tall windows, wide empty marble floor in the foreground",
         "phòng khách biệt thự"),
        ("villa-gate", "the front gate and driveway of a rich family's villa: iron gate, garden hedges and a big white house "
                       "in the background, wide empty paved driveway in the foreground", "cổng, sân biệt thự"),
        ("rich-bedroom", "a luxurious master bedroom: big double bed with headboard, wardrobe and vanity table against the "
                         "back wall, wide empty carpet floor in the foreground", "phòng ngủ vợ chồng nhà giàu")]),
    15: ("BỆNH VIỆN & PHÁP LÝ", [
        ("hospital-corridor", "a hospital corridor: row of waiting chairs along the back wall, doors to exam rooms, a small "
                              "ultrasound room door, wide empty clean floor in the foreground", "hành lang bệnh viện"),
        ("police-station", "a police station reception room: counter and desks with computers at the back, notice board, "
                           "wide empty floor in the foreground", "đồn công an"),
        ("courtroom", "a courtroom: judge's bench on a raised platform at the back, wooden railings at the sides, wide empty "
                      "floor in the foreground", "toà án")]),
    16: ("MUA SẮM & NHÀ NGHÈO", [
        ("jewelry-store", "a luxury jewelry store: glass display counters with necklaces and rings along the back and sides, "
                          "bright lights, wide empty polished floor in the foreground", "cửa hàng trang sức"),
        ("poor-village-house", "a poor countryside house interior: old wooden table, worn bench, earthen walls, small "
                               "window at the back, wide empty packed-earth floor in the foreground", "nhà quê nghèo"),
        ("rented-room", "a tiny cheap rented room in the city: narrow bed and a small plastic wardrobe at the sides, peeling "
                        "wall, wide empty concrete floor in the foreground", "phòng trọ")]),
    17: ("TRỜI & ĐƯỜNG", [
        ("sky-day", "clear blue sky with a few big white cartoon clouds, nothing else", "bầu trời ban ngày"),
        ("sky-night", "dark blue night sky with stars, a crescent moon and a few clouds, nothing else", "bầu trời đêm"),
        ("highway", "a wide city road seen from the side: grey asphalt lanes across the lower half, sidewalk and city "
                    "buildings in the background", "đường lớn cho xe chạy")]),
    18: ("NƠI KHÁC", [
        ("cafe", "a cozy cafe: counter with coffee machine and shelves at the back, small tables at the far sides, wide "
                 "empty wooden floor in the foreground", "quán cà phê"),
        ("company-lobby", "a modern company lobby: reception desk with a blank logo wall at the back, potted plants at the "
                          "sides, wide empty shiny floor in the foreground", "sảnh công ty"),
        ("airport-hall", "an airport departure hall: check-in counters and a big window with a parked airplane at the back, "
                         "wide empty floor in the foreground", "sân bay")]),
})


def style() -> str:
    return yaml.safe_load((ROOT / "channels/khoai-tay-review/channel.yaml").read_text(encoding="utf-8"))["visual_style"]


def prompt(n: int) -> str:
    _, items = SHEETS[n]
    s = style().split(",")
    flat = ", ".join(x for x in s if "head" not in x and "neck" not in x and "body" not in x and "face" not in x)
    tl, tr, bl = (d for _, d, _ in items)
    return ("BACKGROUND SHEET: exactly 3 separate cartoon backgrounds for a 2D animated story, NO people, NO characters, "
            f"NO text, no signs with words. Style: {flat}. The image is split into 4 equal quarters by thin white gaps: "
            f"TOP-LEFT quarter: {tl}. TOP-RIGHT quarter: {tr}. BOTTOM-LEFT quarter: {bl}. The BOTTOM-RIGHT quarter is "
            "completely EMPTY plain white. Each background fills its whole quarter as a 16:9 rectangle, eye-level "
            "medium-wide view like a THEATER STAGE: the LOWER 40% of every background is an EMPTY open floor area "
            "(carpet, tiles, pavement or ground) with NO furniture and NO objects in the lower-middle, so characters can "
            "stand and act there; furniture and props only at the back and at the far left/right sides."
            + (" EXCEPTION: the sky backgrounds are full-frame sky with no floor." if any(i.startswith("sky-") for i, _, _
                                                                                        in items) else ""))


def prompt_single(desc: str) -> str:
    """Prompt 1 nền / 1 ảnh (agy xuất ~1376×768: cắt 3 nền/ảnh thì mỗi nền quá nhỏ cho video 1080p)."""
    s = style().split(",")
    flat = ", ".join(x for x in s if "head" not in x and "neck" not in x and "body" not in x and "face" not in x)
    if desc.startswith(("clear blue sky", "dark blue night sky")):     # nền trời (máy bay bay, cảnh chuyển): không cần sàn
        return (f"Background for a 2D animated story, NO people, NO text. Style: {flat}. Scene: {desc}. 16:9, full frame.")
    return ("Background for a 2D animated story, NO people, NO characters, NO text, no signs with words. "
            f"Style: {flat}. Scene: {desc}. 16:9, eye-level medium-wide view like a THEATER STAGE: the LOWER 40% of the "
            "image is an EMPTY open floor area (carpet, tiles, pavement or ground) with NO furniture and NO objects in the "
            "lower-middle, so characters can stand and act there; furniture and props only at the back and far sides.")


def single(sid: str) -> None:
    """agy tạo 1 nền riêng (đủ nét), ghi đè master.jpg; bản cũ cất vào source/."""
    import sys
    sys.path.insert(0, str(ROOT))
    from src.common.imagegen import gen
    desc, vi, title = next((d, v, t) for t, items in SHEETS.values() for i, d, v in items if i == sid)
    d = SCENES / sid
    d.mkdir(parents=True, exist_ok=True)
    out = SCENES / "source" / f"{sid}_agy.jpg"
    gen(prompt_single(desc), [], out)
    if (d / "master.jpg").exists():
        (d / "master.jpg").rename(SCENES / "source" / f"{sid}_old.jpg")
    Image.open(out).convert("RGB").save(d / "master.jpg", quality=95)
    card = d / "card.yaml"
    c = yaml.safe_load(card.read_text(encoding="utf-8")) if card.exists() else {
        "id": sid, "type": "establishing", "group": title.lower(), "tags": [vi], "characters": [], "master": "master.jpg",
        "frames": ["16:9", "9:16"], "ground_y": 0.9, "used_in": [], "prompt": desc}
    c["size"] = list(Image.open(d / "master.jpg").size)
    c["notes"] = "agy tạo 1 nền/ảnh, có sàn trống phía trước (bản có chỗ diễn 28/9/2026)."
    card.write_text(yaml.safe_dump(c, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print("nền:", sid, c["size"])
    write_index()


def write_prompts() -> pathlib.Path:
    L = ["# Prompt bảng NỀN (1 ảnh = 3 nền, góc dưới phải để trống). Lưu tmp/scene_<số>.png", "",
         "Tạo xong báo Claude cắt: `python scripts/make_scene_sheet.py <số> --sheet tmp/scene_<số>.png`", ""]
    for n, (title, items) in SHEETS.items():
        if n < 9:                                       # bản 1 đã tạo xong; chỉ xuất các bảng cần tạo (lại)
            continue
        L += [f"## {n}. {title} → lưu tmp/scene_{n}.png", "Nền: " + "; ".join(f"`{i}` {vi}" for i, _, vi in items),
              "```", prompt(n), "```", ""]
    out = ROOT / "tmp/scene_prompts.md"
    out.write_text("\n".join(L), encoding="utf-8")
    return out


def split_quarters(img: Image.Image) -> list[Image.Image]:
    """Cắt 3 nền (trên trái, trên phải, dưới trái) theo vùng có hình, không cần khe trắng: nền dưới trái cho mép phải
    của cột trái, nền trên phải cho mép dưới của hàng trên. Dùng tỉ lệ điểm có hình theo cột/hàng nên logo mờ nhỏ ở
    góc dưới phải không làm lệch. Gọt vào 4 px để bỏ viền đen khung."""
    occ = np.array(img.convert("L")) < 235
    h, w = occ.shape

    def last(frac: np.ndarray) -> int:
        idx = np.nonzero(frac > 0.3)[0]
        return int(idx.max()) + 1

    def first(frac: np.ndarray) -> int:
        return int(np.nonzero(frac > 0.3)[0].min())
    x0, y0 = first(occ.mean(axis=0)), first(occ.mean(axis=1))
    xm = last(occ[int(h * 0.8):].mean(axis=0))                  # mép phải nền dưới trái
    x1 = last(occ[:int(h * 0.2)].mean(axis=0))                  # mép phải hàng trên
    ym = last(occ[:, min(w - 1, xm + 10):].mean(axis=1))        # mép dưới nền trên phải
    y1 = last(occ[:, :max(1, xm - 10)].mean(axis=1))            # mép dưới cột trái
    k = 4
    boxes = ((x0, y0, xm, ym), (xm, y0, x1, ym), (x0, ym, xm, y1))
    return [img.crop((a + k, b + k, c - k, d - k)).convert("RGB") for a, b, c, d in boxes]


def cut(n: int, sheet: str | None) -> None:
    """Cắt bảng n. Không có ảnh từ web (sheet=None) thì agy tự tạo ảnh (hết lượt ảnh thì ném RuntimeError)."""
    title, items = SHEETS[n]
    if sheet is None:
        import sys
        sys.path.insert(0, str(ROOT))
        from src.common.imagegen import gen
        sheet = str(SCENES / "source" / f"scene_sheet_{n}_agy.jpg")
        gen(prompt(n), [], pathlib.Path(sheet))
    img = Image.open(sheet)
    (SCENES / "source").mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(SCENES / "source" / f"scene_sheet_{n}.jpg", quality=95)
    for (sid, desc, vi), q in zip(items, split_quarters(img)):
        d = SCENES / sid
        d.mkdir(parents=True, exist_ok=True)
        q.save(d / "master.jpg", quality=95)
        card = d / "card.yaml"
        if not card.exists():
            card.write_text(yaml.safe_dump({
                "id": sid, "type": "establishing", "group": title.lower(), "tags": [vi], "characters": [],
                "master": "master.jpg", "size": list(q.size), "frames": ["16:9", "9:16"], "ground_y": 0.9,
                "notes": "Bảng nền tạo trên web; ngày/đêm đổi bằng lọc màu khi dựng.", "used_in": [], "prompt": desc},
                allow_unicode=True, sort_keys=False), encoding="utf-8")
        print("nền:", sid, q.size)
    write_index()


def write_index() -> None:
    rows = []
    for card in sorted(SCENES.glob("*/card.yaml")):
        c = yaml.safe_load(card.read_text(encoding="utf-8"))
        rows.append(f"| [{c['id']}]({c['id']}/card.yaml) | {c.get('type', '')} | {', '.join(map(str, c.get('tags', [])))} | "
                    f"{', '.join(map(str, c.get('frames', [])))} | {c.get('notes', '')} |")
    (SCENES / "INDEX.md").write_text("\n".join([
        "# Thư viện cảnh (nền)", "", "Nền không có nhân vật, dùng chung nhiều truyện. Chi tiết: `card.yaml` trong từng "
        "thư mục. Sinh bởi `scripts/make_scene_sheet.py`.", "", "| id | Loại | Thẻ | Khung | Ghi chú |",
        "|---|---|---|---|---|"] + rows) + "\n", encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("n", nargs="?", type=int)
    ap.add_argument("--sheet")
    ap.add_argument("--prompts", action="store_true")
    ap.add_argument("--single", help="id nền: agy tạo riêng 1 nền/ảnh (đủ nét)")
    a = ap.parse_args()
    if a.single:
        single(a.single)
    elif a.prompts:
        print("Đã ghi", write_prompts().relative_to(ROOT))
    elif a.n:
        cut(a.n, a.sheet)                               # không có --sheet: agy tự tạo ảnh
    else:
        ap.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
