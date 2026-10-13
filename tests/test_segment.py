import numpy as np
from PIL import Image, ImageDraw

from src.studio import segment
from src.studio.cutout import neck_top

SKIN = (240, 190, 160)
INK = (10, 10, 10)


def fake_figure(scale: float = 1.0, shift: int = 0) -> Image.Image:
    """Nhân vật giả: tóc đen dài sau lưng xuống eo, mặt tròn da, cổ hẹp, thân áo xanh, chân, viền đen 3 px."""
    S = scale
    W, H = int(400 * S), int(900 * S)
    im = Image.new("RGB", (W, H), "white")
    d = ImageDraw.Draw(im)

    def sc(*v):
        return [int(x * S) + shift for x in v]

    d.rectangle(sc(110, 60, 290, 520), fill=(15, 15, 15))                       # tóc dài
    d.rectangle(sc(180, 215, 220, 280), fill=SKIN, outline=INK, width=3)         # cổ
    d.rectangle(sc(130, 275, 270, 520), fill=(40, 90, 200), outline=INK, width=3)  # thân
    d.rectangle(sc(150, 520, 195, 850), fill=(60, 60, 150), outline=INK, width=3)  # chân
    d.rectangle(sc(205, 520, 250, 850), fill=(60, 60, 150), outline=INK, width=3)
    d.ellipse(sc(130, 80, 270, 230), fill=SKIN, outline=INK, width=3)            # mặt
    d.ellipse(sc(165, 140, 180, 152), fill=(0, 0, 0))                            # mắt
    d.ellipse(sc(220, 140, 235, 152), fill=(0, 0, 0))
    d.arc(sc(175, 180, 225, 205), 20, 160, fill=(150, 40, 40), width=3)          # miệng
    return im


def test_cut_figure(tmp_path):
    src = tmp_path / "master.png"
    fake_figure().save(src)
    out = tmp_path / "out"
    r = segment.cut_figure(src, out)
    for f in ("hair_back.png", "head_front.png", "body_relaxed.png"):
        assert (out / f).exists(), f
    head, back, body = (Image.open(out / n) for n in ("head_front.png", "hair_back.png", "body_relaxed.png"))
    assert head.size == back.size
    assert r["hair_back"] is True

    chin_local = r["chin_y"] - (r["head_box"][1] - segment.PAD)
    ha = np.asarray(head)[..., 3]
    assert ha[chin_local + 3:].max() == 0                       # dưới cằm trong suốt
    assert ha[:chin_local - 5].max() == 255
    assert np.asarray(back)[..., 3][chin_local + 10:].max() == 255   # tóc sau đục dưới cằm

    ba = np.asarray(body)[..., 3]
    nx, ny = neck_top(body)
    bb = Image.fromarray(ba).getbbox()
    assert bb[0] + (bb[2] - bb[0]) / 3 <= nx <= bb[0] + 2 * (bb[2] - bb[0]) / 3
    assert ny <= segment.PAD + 2                                   # đỉnh thân = đỉnh mẩu cổ
    assert 0.18 <= r["head_ratio"] <= 0.30


def test_neck_stub_above_chin(tmp_path):
    src = tmp_path / "m.png"
    fake_figure().save(src)
    r = segment.cut_figure(src, tmp_path / "o")
    body = np.asarray(Image.open(tmp_path / "o" / "body_relaxed.png"))[..., 3]
    rows_above_shoulder = np.where(body.max(axis=1) > 0)[0]
    # cằm cách đỉnh thân: head_h * overlap (cổ giả cao 65 px từ cằm 230 xuống 275 -> mẩu cổ tối đa 0.12*head_h)
    stub = round(0.12 * (r["chin_y"] - r["head_box"][1]))
    first = rows_above_shoulder[0] - segment.PAD
    assert stub >= 10 and first == 0


def test_cut_head_scaled(tmp_path):
    src = tmp_path / "m.png"
    fake_figure().save(src)
    ref = segment.cut_figure(src, tmp_path / "o")
    big = tmp_path / "big.png"
    fake_figure(1.3, 0).save(big)
    r2 = segment.cut_head(big, tmp_path / "expr.png", ref)
    head = Image.open(tmp_path / "expr.png")
    assert head.size == tuple(ref["frame"]) == Image.open(tmp_path / "o" / "head_front.png").size
    a = np.asarray(head)[..., 3]
    assert a.max() == 255
    assert r2["face_w"] > ref["face_w"] * 1.2                       # ảnh gốc to hơn 1.3x, đã được co lại
    # cằm trùng neo
    assert a[int(ref["anchor"][1]) + 4:].max() == 0


def test_cut_body_scaled(tmp_path):
    src = tmp_path / "m.png"
    fake_figure().save(src)
    ref = segment.cut_figure(src, tmp_path / "o")
    big = tmp_path / "big.png"
    fake_figure(1.3).save(big)
    segment.cut_body(big, tmp_path / "b.png", ref)
    a = Image.open(tmp_path / "b.png")
    b = Image.open(tmp_path / "o" / "body_relaxed.png")
    assert abs(a.height - b.height) <= 3


def test_defringe_white_matte():
    px = np.zeros((1, 1, 4), np.uint8)
    px[0, 0] = (255, 127, 127, 128)      # đỏ thuần trộn 50% với trắng
    out = segment.defringe(px)
    assert tuple(int(v) for v in out[0, 0, :3]) == (255, 0, 0)
    assert out[0, 0, 3] == 128


def test_blank_image_value_error(tmp_path):
    src = tmp_path / "blank.png"
    Image.new("RGB", (200, 300), "white").save(src)
    import pytest
    with pytest.raises(ValueError):
        segment.cut_figure(src, tmp_path / "o")


def test_cut_head_bad_ref(tmp_path):
    import pytest
    src = tmp_path / "m.png"
    fake_figure().save(src)
    with pytest.raises(ValueError, match="ref phải là"):
        segment.cut_head(src, tmp_path / "h.png", {"face_w": 10})
    with pytest.raises(ValueError, match="ref phải là"):
        segment.cut_body(src, tmp_path / "b.png", {})
