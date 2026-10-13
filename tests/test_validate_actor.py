"""Test kiểm diễn viên rối bằng ảnh PIL vẽ giả (không gọi agy)."""
import pathlib

import pytest
import yaml
from PIL import Image, ImageDraw

from src.studio import validate_actor as va


def head(path, h=120, w=100):
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((2, 2, w - 3, h - 3), fill=(200, 150, 120, 255), outline=(0, 0, 0, 255))
    im.save(path)


def body(path):
    im = Image.new("RGBA", (100, 330), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle((42, 0, 58, 20), fill=(200, 150, 120, 255))          # cổ giữa
    d.rectangle((15, 20, 85, 200), fill=(30, 60, 160, 255))          # thân
    d.rectangle((30, 200, 70, 329), fill=(20, 20, 20, 255))          # chân
    im.save(path)


@pytest.fixture
def actor(tmp_path):
    d = tmp_path / "x"
    (d / "parts/o").mkdir(parents=True)
    for k in ("neutral", "smirk"):
        head(d / f"parts/head_{k}.png")
    body(d / "parts/o/body_relaxed.png")
    head(d / "parts/hair_back.png")
    card = {"id": "x", "kind": "actor",
            "rig": {"mode": "semi", "head_scale": 1.0, "overlap": 0.12, "hair_back": "parts/hair_back.png"},
            "heads": {"neutral": "parts/head_neutral.png", "smirk": "parts/head_smirk.png"},
            "outfits": {"o": {"desc": "d", "bodies": {"relaxed": "parts/o/body_relaxed.png"}}}}
    (d / "card.yaml").write_text(yaml.safe_dump(card), encoding="utf-8")
    return d


def edit(d, fn):
    p = d / "card.yaml"
    c = yaml.safe_load(p.read_text())
    fn(c)
    p.write_text(yaml.safe_dump(c))


def test_valid(actor):
    assert va.validate(actor) == []


def test_missing_mode(actor):
    edit(actor, lambda c: c["rig"].pop("mode"))
    assert any("mode" in e for e in va.validate(actor))


def test_head_too_big(actor):
    head(actor / "parts/head_neutral.png", h=240)
    head(actor / "parts/hair_back.png", h=240)
    assert any("tỉ lệ" in e for e in va.validate(actor))


def test_hair_back_size(actor):
    head(actor / "parts/hair_back.png", h=90)
    assert any("hair_back" in e for e in va.validate(actor))


def test_missing_file(actor):
    (actor / "parts/head_smirk.png").unlink()
    assert any("thiếu file" in e for e in va.validate(actor))


def test_malformed_bodies_and_heads_no_crash(tmp_path):
    import yaml as _y
    from src.studio import validate_actor as va
    d = tmp_path / "bad"
    d.mkdir()
    card = {"id": "bad", "kind": "actor", "rig": {"mode": "semi", "head_scale": 1.0, "overlap": 0.1},
            "heads": {"neutral": 5}, "outfits": {"o": {"bodies": ["x"]}, "p": {"bodies": {"relaxed": 3}}}}
    (d / "card.yaml").write_text(_y.safe_dump(card), encoding="utf-8")
    errs = va.validate(d)
    assert any("heads.neutral" in e for e in errs) and any("outfits.o" in e for e in errs)
    assert any("outfits.p.bodies.relaxed" in e for e in errs)
