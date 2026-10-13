"""Test scripts/new_actor.py với agy và segment giả."""
import importlib.util
import pathlib
import sys
import types

import pytest
import yaml
from PIL import Image, ImageDraw

from tests.test_validate_actor import body, head

spec = importlib.util.spec_from_file_location("new_actor", pathlib.Path(__file__).resolve().parents[1] / "scripts/new_actor.py")


@pytest.fixture
def na(tmp_path, monkeypatch):
    seg = types.ModuleType("src.studio.segment")           # segment.py do người khác viết: luôn thay bằng bản giả
    monkeypatch.setitem(sys.modules, "src.studio.segment", seg)
    import src.studio
    monkeypatch.setattr(src.studio, "segment", seg, raising=False)
    calls = {"gen": 0}

    def fake_gen(prompt, refs, out, tries=2, aspect="16:9"):
        calls["gen"] += 1
        Image.new("RGBA", (90, 160), (255, 255, 255, 255)).save(out)

    def cut_figure(master, out_dir, overlap=0.12):
        head(out_dir / "head_front.png")
        head(out_dir / "hair_back.png")
        body(out_dir / "body_relaxed.png")
        return {"face_w": 90, "hair_back": True, "chin_y": 100, "head_box": [0, 10, 90, 100], "frame": [102, 102]}

    def cut_head(img, out, ref):
        head(out)
        return {}

    def cut_body(img, out, ref):
        body(out)
        return {}

    seg.cut_figure, seg.cut_head, seg.cut_body = cut_figure, cut_head, cut_body
    import src.common.imagegen as ig
    monkeypatch.setattr(ig, "gen", fake_gen)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ACTORS", tmp_path / "actors")
    mod.calls = calls
    return mod


def run(na, tmp_path):
    m = tmp_path / "m.png"
    Image.new("RGBA", (90, 160), (255, 255, 255, 255)).save(m)
    return na.main(["t1", "--look", "a woman", "--hair", "long black", "--outfit", "vest", "--outfit-desc", "grey vest",
                    "--gender", "nu", "--age", "25-30", "--master", str(m), "--exprs", "neutral,smirk,blink",
                    "--poses", "hips"])


def test_new_actor(na, tmp_path):
    assert run(na, tmp_path) == 0
    assert na.calls["gen"] == 3                         # smirk, blink, hips (master có sẵn)
    d = tmp_path / "actors/t1"
    c = yaml.safe_load((d / "card.yaml").read_text())
    assert c["kind"] == "actor" and c["rig"]["mode"] == "semi" and c["rig"]["hair_back"] == "parts/hair_back.png"
    assert set(c["heads"]) == {"neutral", "smirk", "blink"}
    assert set(c["outfits"]["vest"]["bodies"]) == {"relaxed", "hips"}
    assert c["gender"] == "nu" and c["signature"] == "confident half smirk"
    assert (d / "source/measure.yaml").exists() and (d / "preview_vest.jpg").exists()
    na.calls["gen"] = 0
    assert run(na, tmp_path) == 0
    assert na.calls["gen"] == 0


def test_no_gen_missing(na, tmp_path):
    assert na.main(["t2", "--look", "x", "--hair", "y", "--outfit", "o", "--outfit-desc", "z", "--no-gen"]) == 1


def _real(tmp_path, monkeypatch):
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    monkeypatch.setattr(mod, "ACTORS", tmp_path / "actors")
    return mod


ARGS = ["--look", "x", "--hair", "y", "--outfit", "o", "--outfit-desc", "d", "--no-gen", "--exprs", "neutral", "--poses", ""]


def test_rig_overlap_matches_neck_stub(tmp_path, monkeypatch):
    """B1: cằm trong figure() thấp hơn đỉnh cổ đúng 0.12 × head_h dù khung đầu cao hơn vì tóc dài."""
    from src.studio.stage import Puppet
    from tests.test_segment import fake_figure
    na = _real(tmp_path, monkeypatch)
    m = tmp_path / "m.png"
    fake_figure().save(m)
    na.main(["z1", *ARGS, "--master", str(m)])
    d = na.ACTORS / "z1"
    card_p = d / "card.yaml"
    if not card_p.exists():                                   # tỉ lệ giả có thể CHƯA ĐẠT; ghép vẫn kiểm được
        (d / "card.yaml").write_text((d / "card.rejected.yaml").read_text())
    meas = yaml.safe_load((d / "source/measure.yaml").read_text())
    head_h = meas["chin_y"] - meas["head_box"][1]
    assert meas["frame"][1] > head_h * 1.3                    # tóc dài: khung cao hơn nhiều so với head_h
    pup = Puppet(d, "o")
    fig, _ = pup.figure("relaxed", "neutral")
    hx, hy, hw, hh = pup.head_box[pup.last_key]
    head = Image.open(d / "parts/head_neutral.png")
    chin_fig = hy + head.getchannel("A").getbbox()[3]
    from src.studio.cutout import neck_top
    body_img = Image.open(d / "parts/o/body_relaxed.png")
    body_off = fig.height - body_img.height                   # thân cao nhất nằm sát đáy figure
    neck_fig = body_off + neck_top(body_img)[1]
    assert abs((chin_fig - neck_fig) - 0.12 * head_h) <= 3


def test_stale_master_recut(tmp_path, monkeypatch):
    """B2: đổi ảnh gốc thì head_neutral đổi; B5: CHƯA ĐẠT ghi card.rejected.yaml, không card.yaml."""
    import hashlib
    from tests.test_segment import fake_figure
    na = _real(tmp_path, monkeypatch)
    m1, m2 = tmp_path / "m1.png", tmp_path / "m2.png"
    fake_figure().save(m1)
    fake_figure(1.2).save(m2)
    na.main(["z2", *ARGS, "--master", str(m1)])
    d = na.ACTORS / "z2"
    h, mp = d / "parts/head_neutral.png", d / "source/measure.yaml"
    a = hashlib.md5(h.read_bytes()).hexdigest()
    assert yaml.safe_load(mp.read_text())["source_md5"] == hashlib.md5(m1.read_bytes()).hexdigest()
    assert (d / "card.rejected.yaml").exists() != (d / "card.yaml").exists()      # không bao giờ có cả hai
    na.main(["z2", *ARGS, "--master", str(m2)])
    assert hashlib.md5(h.read_bytes()).hexdigest() != a
    assert yaml.safe_load(mp.read_text())["source_md5"] == hashlib.md5(m2.read_bytes()).hexdigest()
    assert (d / "source/master.png").read_bytes() == m2.read_bytes()


def test_no_gen_lists_all_missing(na, tmp_path, capsys):
    assert na.main(["t3", "--look", "x", "--hair", "y", "--outfit", "o", "--outfit-desc", "z", "--no-gen",
                    "--exprs", "neutral,smirk,blink", "--poses", "hips,phone"]) == 1
    out = capsys.readouterr().out
    for f in ("master.png", "expr_smirk.png", "expr_blink.png", "pose_hips.png", "pose_phone.png"):
        assert f in out


def test_unsplittable_image_no_traceback(tmp_path, monkeypatch, capsys):
    na = _real(tmp_path, monkeypatch)
    m = tmp_path / "blank.png"
    Image.new("RGB", (200, 300), "white").save(m)
    assert na.main(["z3", *ARGS, "--master", str(m)]) == 1
    assert "CHƯA ĐẠT:" in capsys.readouterr().out
