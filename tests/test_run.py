"""Test dây chuyền src/run.py với agy và TTS giả (không gọi mạng, không tốn quota)."""
import json
import pathlib
import re
import shutil

import pytest
import yaml

import src.run as run

CARD = "# Thẻ chương {n}: x\nNguồn: https://m.qidian.com/chapter/1/{n}/ · Số chữ: 2000\n\n## Tóm tắt 2 câu\nA.\n\n## Diễn biến\n" + "1. nhịp. " * 300
SCRIPT = ("Trần Hán Thăng mở mắt. " * 200).strip()
LEDGER = "| # | Dữ kiện | Chương nguồn | Người nghe biết từ ch. |\n|---|---|---|---|\n" + \
    "".join(f"| {i} | dữ kiện {i} | ch.1 | 1 |\n" for i in range(1, 4))
NAMES = {"_note": "Hán Việt", "characters": {"陈汉升": "Trần Hán Thăng"}, "places": {}, "terms": {}}


def files(**kw) -> str:
    return "\n".join(f"=== FILE: {k} ===\n{v}" for k, v in kw.items())


PLAN = files(**{"bible.md": "# Sổ tay\nQuy ước kể: gọi nhân vật chính là Hán Thăng.", "characters.md": "### Trần Hán Thăng",
                "ledger.md": LEDGER, "arc.md": "# Lô", "rename_map.json": json.dumps(NAMES, ensure_ascii=False),
                "changes.md": "- lập mới"})
UPDATE = files(**{"bible.md": "# Sổ tay", "characters.md": "### Trần Hán Thăng (tiền: 300 tệ, ch.2)",
                  "ledger.md": LEDGER + "| 4 | dữ kiện mới | ch.2 | 2 |\n", "changes.md": "- thêm dữ kiện 4"})


@pytest.fixture
def story(tmp_path, monkeypatch):
    root = tmp_path
    for d in ("prompts/roles", "channels/kenh/brand", "stories/tr"):
        (root / d).mkdir(parents=True)
    real = pathlib.Path(run.__file__).resolve().parents[1]
    for f in ("story-analyst", "story-lead", "scriptwriter", "scriptwriter-light", "editor", "content-reviewer"):
        shutil.copy(real / f"prompts/roles/{f}.md", root / f"prompts/roles/{f}.md")
    shutil.copy(real / "config.yaml", root / "config.yaml")
    (root / "channels/kenh/channel.yaml").write_text(yaml.safe_dump(
        {"name": "Kênh", "brand": {"mascot_reference": "brand/m.png"}, "tts": {"voice": "Ngọc Huyền", "speed": 1.12}}),
        encoding="utf-8")
    (root / "stories/tr/story.yaml").write_text(yaml.safe_dump(
        {"title_vi": "Truyện", "title_zh": "书", "source_url": "https://x", "channel": "kenh", "bible_approved": True,
         "pipeline": {"fast": False}},        # các test cũ kiểm chế độ đầy đủ; chế độ nhanh có test riêng
        allow_unicode=True), encoding="utf-8")
    monkeypatch.setattr(run, "ROOT", root)
    monkeypatch.setattr(run, "ROLES", root / "prompts/roles")
    monkeypatch.setattr(run.agy, "usage", lambda: {"Gemini Models|Five Hour": 90})
    run._QUOTA["at"] = 0.0

    def fake_tts(text, voice, mp3, srt, work, speed, workers=1):
        mp3.parent.mkdir(parents=True, exist_ok=True)
        mp3.write_text("x")
        srt.write_text("1\n00:00:00,000 --> 00:00:01,000\nx\n")
        return 60.0

    monkeypatch.setattr(run.tts, "vieneu", fake_tts)
    return run.Story("tr")


class Fake:
    """agy giả: trả lời theo loại nhiệm vụ; `reviews`, `checks` là hàng đợi câu trả lời cho duyệt và kiểm mạch."""

    def __init__(self, monkeypatch, reviews=None, checks=None, plan=PLAN, patch='{"fixes": []}'):
        self.calls, self.reviews, self.checks, self.plan, self.prompts = [], list(reviews or []), list(checks or []), plan, []
        self.patch = patch
        monkeypatch.setattr(run.agy, "run", self)

    def __call__(self, prompt, model, timeout=1800):
        self.prompts.append(prompt)
        if m := re.search(r"Lập thẻ chương số (\d+)", prompt):
            kind, text = "card", CARD.format(n=m.group(1))
        elif "LẬP ĐỀ CƯƠNG" in prompt:
            kind, text = "plan", self.plan
            if "LÔ 1" not in prompt:  # lô sau: giữ dữ kiện đã có
                text = text.replace(LEDGER, LEDGER + "| 4 | dữ kiện mới | ch.2 | 2 |\n")
        elif "KIỂM MẠCH" in prompt:
            a, b = map(int, re.search(r"chương (\d+)–(\d+)", prompt).groups())
            kind = "continuity"
            text = self.checks.pop(0) if self.checks else \
                "Kết luận: ĐẠT\n" + "".join(f"Chương {n}: KHỚP\n" for n in range(a, b + 1))
        elif "CẬP NHẬT SỔ TAY sau lô" in prompt:
            kind, text = "update", UPDATE
        elif "Duyệt KỊCH BẢN" in prompt:
            kind, text = "review", self.reviews.pop(0) if self.reviews else "Kết luận: ĐẠT"
        elif "SỬA ĐÚNG các câu" in prompt:
            kind, text = "patch", self.patch
        elif "Soát kịch bản" in prompt:
            kind, text = "edit", SCRIPT
        else:
            kind, text = "write", SCRIPT + "\n\n=== ĐỀ XUẤT SỔ TAY ===\n- Hán Thăng có 300 tệ (ch.2)"
        self.calls.append((kind, model))
        return {"text": text, "status": "SUCCESS", "usage": {}, "seconds": 1, "rc": 0, "notices": [],
                "conversation_id": None}

    def kinds(self):
        return [k for k, _ in self.calls]


def test_mot_lo_tao_du_file_va_so_tay(story, monkeypatch):
    fake = Fake(monkeypatch)
    assert run.run(story, [1, 2], set(), workers=2) == [1, 2]
    for n in (1, 2):
        for k in ("card", "draft", "edit", "review", "proposal", "mp3", "srt"):
            assert story.p(k, n).exists(), (n, k)
    assert "SỔ TAY" not in story.p("edit", 2).read_text(encoding="utf-8")        # đề xuất đã tách khỏi kịch bản
    assert "300 tệ" in story.p("proposal", 2).read_text(encoding="utf-8")
    assert story.p("arc", 1).exists() and story.p("check", 1).exists()
    assert story.version() == 2                                                    # v1 lập + v2 cập nhật
    assert ledger_count(story) == 4
    assert fake.kinds().count("plan") == 1 and fake.kinds().count("update") == 1
    assert "SỔ TAY TRUYỆN v1" in next(p for p in fake.prompts if "Viết bản kể" in p or "Viết kịch bản" in p)


def ledger_count(story):
    return run.ledger_rows((story.bible / "ledger.md").read_text(encoding="utf-8"))


def test_chay_lai_khong_goi_agy(story, monkeypatch):
    Fake(monkeypatch)
    run.run(story, [1, 2], set(), workers=2)
    fake = Fake(monkeypatch)
    run.run(story, [1, 2], set(), workers=2)
    assert fake.calls == []


def test_so_tay_v1_dung_cho_duyet(story, monkeypatch):
    story.meta["bible_approved"] = False
    Fake(monkeypatch)
    with pytest.raises(run.Stop, match="duyệt"):
        run.run(story, [1, 2], set(), workers=2)
    assert (story.bible / "bible.md").exists() and not story.p("draft", 1).exists()
    story.meta["bible_approved"] = True
    fake = Fake(monkeypatch)
    assert run.run(story, [1, 2], set(), workers=2) == [1, 2]
    assert "plan" not in fake.kinds()                                              # không lập lại sổ tay


def test_duyet_chua_dat_viet_lai_model_cao_hon(story, monkeypatch):
    fake = Fake(monkeypatch, reviews=["Kết luận: CHƯA ĐẠT\nsai xưng hô"])
    run.run(story, [1], set(), workers=1)
    ladder = story.cfg["agents"]["scriptwriter"]
    writes = [m for k, m in fake.calls if k == "write"]
    assert writes == ladder[:2]


def test_kiem_mach_lech_thi_viet_lai_dung_chuong(story, monkeypatch):
    lech = "Kết luận: CHƯA ĐẠT\nChương 1: KHỚP\nChương 2: LỆCH — gọi 'anh' thay vì 'Hán Thăng' → sửa xưng hô\n"
    fake = Fake(monkeypatch, checks=[lech])
    assert run.run(story, [1, 2], set(), workers=2) == [1, 2]
    rewrite = [p for p in fake.prompts if "Nhóm trưởng kiểm mạch báo lệch" in p and "SỬA ĐÚNG" not in p]
    assert len(rewrite) == 1 and "CHƯƠNG 2" in rewrite[0].upper()
    assert fake.kinds().count("continuity") == 2


def test_kiem_mach_lech_mai_thi_dung(story, monkeypatch):
    lech = "Kết luận: CHƯA ĐẠT\nChương 1: LỆCH — x → y\n"
    Fake(monkeypatch, checks=[lech] * 5)
    with pytest.raises(run.Stop, match="kiểm mạch"):
        run.run(story, [1], set(), workers=1)
    assert story.version() == 1 and not story.p("mp3", 1).exists()               # không cập nhật sổ tay, không đọc giọng


def test_de_cuong_thieu_file_thi_dung(story, monkeypatch):
    Fake(monkeypatch, plan=files(**{"bible.md": "x"}))
    with pytest.raises(run.Stop):
        run.run(story, [1], set(), workers=1)
    assert not story.bible.exists()


def test_kiem_may_so_tay(story):
    story.bible.mkdir(parents=True)
    (story.bible / "ledger.md").write_text(LEDGER, encoding="utf-8")
    assert "mất dòng" in run.bible_problems(story, files(**{"ledger.md": "| 1 | a | ch.1 | 1 |"}), ["ledger.md"])
    story.names.write_text(json.dumps(NAMES, ensure_ascii=False), encoding="utf-8")
    renamed = json.dumps({**NAMES, "characters": {"陈汉升": "Trần Hải Đăng"}}, ensure_ascii=False)
    assert "đổi tên cũ" in run.bible_problems(story, files(**{"rename_map.json": renamed}), ["rename_map.json"])


def test_force_write_lam_lai_tu_viet_tro_di(story, monkeypatch):
    Fake(monkeypatch)
    run.run(story, [1], set(), workers=1)
    fake = Fake(monkeypatch)
    run.run(story, [1], {"write"}, workers=1)
    assert set(fake.kinds()) == {"write", "edit", "review", "continuity", "update"}  # không rã lại, không lập lại đề cương


def test_hai_lo_lo_sau_dung_so_tay_moi(story, monkeypatch):
    story.cfg["pipeline"]["batch_size"] = 2
    fake = Fake(monkeypatch)
    assert run.run(story, [1, 2, 3], set(), workers=2) == [1, 2, 3]
    assert story.p("arc", 1).exists() and story.p("arc", 2).exists()
    plan2 = [p for p in fake.prompts if "LẬP ĐỀ CƯƠNG LÔ 2" in p][0]
    assert "SỔ TAY TRUYỆN v2" in plan2                                             # đã có cập nhật sau lô 1
    assert story.version() == 4


def test_mot_chuong_ra_loi_thi_dung_lo(story, monkeypatch):
    fake = Fake(monkeypatch)
    real = fake.__call__

    def fail_ch2(prompt, model, timeout=1800):
        r = real(prompt, model, timeout)
        return {**r, "text": ""} if "Lập thẻ chương số 2" in prompt else r

    monkeypatch.setattr(run.agy, "run", fail_ch2)
    with pytest.raises(run.Stop, match="chương 2"):
        run.run(story, [1, 2], set(), workers=2)
    assert not story.bible.exists()


def test_het_quota_thi_dung(story, monkeypatch):
    Fake(monkeypatch)
    monkeypatch.setattr(run.agy, "usage", lambda: {"Gemini Models|Five Hour": 3})
    run._QUOTA["at"] = 0.0
    with pytest.raises(run.Stop):
        run.run(story, [1], set(), workers=1)


def test_ham_nho(story):
    assert run.script_problems(SCRIPT, story) is None
    assert "chữ Hán" in run.script_problems(SCRIPT + " 陈汉升", story)
    assert "markdown" in run.script_problems("## Tiêu đề\n" + SCRIPT, story)
    assert run.verdict("Kết luận: KHÔNG ĐẠT") is False and run.verdict("**Kết luận: ĐẠT**") is True
    assert run.verdict("không có") is None
    assert run.parse_range("2-4") == [2, 3, 4]
    assert run.split_files(files(**{"a.md": "x", "b.md": "y"})) == {"a.md": "x\n", "b.md": "y\n"}
    assert run.expand({"write"}) == {"write", "edit", "review", "continuity", "update", "voice"}


def test_tu_cam_theo_so_tay(story):
    story.names.write_text(json.dumps({**NAMES, "banned": {"Nhất bản": "trường top đầu"}}, ensure_ascii=False),
                           encoding="utf-8")
    assert "từ cấm" in run.script_problems(SCRIPT + " Cậu đỗ Nhất bản.", story)
    assert run.script_problems(SCRIPT, story) is None
    run.write_bible_files(story, {"rename_map.json": json.dumps(NAMES, ensure_ascii=False)}, 1, "x")
    assert "banned" in run.load_names(story)                                        # nhóm trưởng quên trả thì vẫn giữ


def test_kich_ban_moi_hon_mp3_thi_doc_lai(story, monkeypatch):
    import os
    import time
    Fake(monkeypatch)
    run.run(story, [1], set(), workers=1)
    mp3 = story.p("mp3", 1)
    mp3.write_text("cũ")
    old = time.time() - 100
    os.utime(mp3, (old, old))
    Fake(monkeypatch)
    run.run(story, [1], set(), workers=1)
    assert mp3.read_text() == "x"


def test_che_do_nhanh_may_soat_bo_qua_soat_va_duyet_ai(story, monkeypatch):
    story.cfg["pipeline"]["fast"] = True
    fake = Fake(monkeypatch)
    assert run.run(story, [1, 2], set(), workers=2) == [1, 2]
    kinds = fake.kinds()
    assert "edit" not in kinds and "review" not in kinds                        # máy soát đạt, không phải chương thứ 5
    for n in (1, 2):
        assert "chế độ nhanh" in story.p("review", n).read_text(encoding="utf-8")
        assert story.p("edit", n).exists()
    assert "TỰ KIỂM" in next(p for p in fake.prompts if "Viết bản kể" in p or "Viết kịch bản" in p)


def test_sua_khoanh_vung_dat_thi_khong_viet_lai(story, monkeypatch):
    old = SCRIPT.strip().split(".")[0].strip()
    patch = json.dumps({"fixes": [{"old": old, "new": old + " (đã sửa)"}]}, ensure_ascii=False)
    fake = Fake(monkeypatch, reviews=["Kết luận: CHƯA ĐẠT\nsai một câu"], patch=patch)
    run.run(story, [1], set(), workers=1)
    kinds = fake.kinds()
    assert kinds.count("write") == 1 and kinds.count("patch") == 1           # không viết lại cả chương
    assert "(đã sửa)" in story.p("edit", 1).read_text(encoding="utf-8")


def test_sua_khoanh_vung_cau_khong_co_thi_viet_lai(story, monkeypatch):
    patch = json.dumps({"fixes": [{"old": "câu không hề có trong kịch bản", "new": "x"}]}, ensure_ascii=False)
    fake = Fake(monkeypatch, reviews=["Kết luận: CHƯA ĐẠT\nsai"], patch=patch)
    run.run(story, [1], set(), workers=1)
    assert fake.kinds().count("write") == 2                                   # không đoán: viết lại cả chương
