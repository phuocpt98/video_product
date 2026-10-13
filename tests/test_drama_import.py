import pytest
import yaml

from src import drama

FILLER = " ".join(["Tôi nhìn quanh căn phòng yên lặng và chờ đợi."] * 3)


def make(marker: str, header: bool = True) -> str:
    head = ("TRUYỆN 1: CÔ DÂU (新娘)\nThể loại: Drama, Đô thị\nNguồn cảm hứng: Zhihu\nTóm tắt: Cô dâu lật mặt.\n\nNỘI DUNG TRUYỆN\n"
            if header else "")
    parts = []
    for i in (1, 2, 3):
        parts.append(f'{marker.format(i)}\nTôi bước vào. "Uyển Thanh, em đứng lại!" Tống Hạo gọi. {FILLER}\n'
                     f'Tống Hạo cười. Bà Trương nhìn Tống Hạo. Tống Hạo im lặng. Bà Trương gật đầu. Bà Trương bước ra.\n'
                     f'"Uyển Thanh, cô làm gì vậy?" Bà Trương hỏi. Tôi đáp: "Uyển Thanh không làm gì." '
                     f'Lâm Uyển Thanh nói tiếp. Lâm Uyển Thanh bình thản. Tôi cười.\n')
    return head + "\n".join(parts)


@pytest.fixture
def stories(tmp_path, monkeypatch):
    monkeypatch.setattr(drama, "STORIES", tmp_path / "stories")
    return tmp_path


def run(tmp, text, slug="truyen-thu", **kw):
    f = tmp / "story.md"
    f.write_text(text, encoding="utf-8")
    return drama.import_story(slug, str(f), **kw), tmp / "stories" / slug


def test_import_basic(stories):
    r, d = run(stories, make("{}."))
    meta = yaml.safe_load((d / "story.yaml").read_text(encoding="utf-8"))
    assert meta["source"] == "imported" and meta["rewrite"] == "none" and meta["parts"] == 3
    assert meta["title_vi"] == "CÔ DÂU" and meta["genre"] == ["Drama", "Đô thị"] and meta["motif"] == "Cô dâu lật mặt."
    assert meta["pipeline"] == {"fast": True, "batch_size": 3, "continuity_rounds": 0} and meta["bible_approved"] is True
    for i in (1, 2, 3):
        t = (d / "script" / f"{i:03d}.txt").read_text(encoding="utf-8")
        assert t.startswith("Tôi bước vào.") and '"Uyển Thanh, em đứng lại!"' in t
    cast = yaml.safe_load((d / "cast.yaml").read_text(encoding="utf-8"))
    assert cast["lead"] == "Lâm Uyển Thanh"
    assert {"Tống Hạo", "Bà Trương", "Lâm Uyển Thanh"} <= set(cast["characters"])
    assert "Uyển Thanh" in cast["characters"]["Lâm Uyển Thanh"]["names"]
    assert (d / "outline" / "hook.md").read_text(encoding="utf-8").startswith("Phần 1")
    assert (d / "bible" / "bible.md").exists() and r["words"]


def test_exists_needs_force(stories):
    run(stories, make("{}."))
    with pytest.raises(SystemExit):
        run(stories, make("{}."))
    run(stories, make("{}."), force=True)


@pytest.mark.parametrize("marker", ["Phần {}", "## {}", "{})"])
def test_marker_variants(stories, marker):
    _, d = run(stories, make(marker))
    assert len(list((d / "script").glob("*.txt"))) == 3


def test_no_header_title_is_slug(stories):
    _, d = run(stories, make("Phần {}", header=False))
    meta = yaml.safe_load((d / "story.yaml").read_text(encoding="utf-8"))
    assert meta["title_vi"] == "truyen-thu" and meta["genre"] == ["drama"]
    assert yaml.safe_load((d / "cast.yaml").read_text(encoding="utf-8"))["lead"] == "Lâm Uyển Thanh"


def test_no_parts_errors(stories):
    with pytest.raises(SystemExit):
        run(stories, "chỉ có một đoạn văn")
