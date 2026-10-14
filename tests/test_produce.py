"""Test dây chuyền chính (chia truyện, đọc .docx) và hoạt hình ngẫu nhiên (kế hoạch + vẽ khung mọi vi kịch bản)."""
import pathlib
import zipfile

from src import produce
from src.studio import reel

DATA = pathlib.Path(__file__).parent / "data"


def test_split_sample_story():
    title, parts = produce.split_story(produce.read_story(DATA / "sample_story.txt"), 500)
    assert title == "Chiếc Ô Màu Vàng"
    assert len(parts) == 2
    assert parts[0].startswith("Chương 1") and parts[1].startswith("Chương 2")
    assert "**" not in "".join(parts) and "#" not in "".join(parts)


def test_split_long_paragraph_by_sentence():
    text = "Tiêu đề\n\n" + " ".join(f"Câu số {i} khá dài để thử cắt." for i in range(200))
    title, parts = produce.split_story(text, 1000)
    assert title == "Tiêu đề"
    assert len(parts) > 3
    assert all(len(p) <= 1000 for p in parts[:-1])
    assert "".join(parts).replace("\n", " ").count("Câu số") == 200      # không mất câu nào


def test_short_tail_merged():
    _, parts = produce.split_story("A" * 900 + "\n\n" + "B" * 100, 1000)
    assert len(parts) == 1


def test_read_docx(tmp_path):
    doc = tmp_path / "t.docx"
    body = "".join(f"<w:p><w:r><w:t>{x}</w:t></w:r></w:p>" for x in ["Tên Truyện", "Chương 1", "Một &amp; hai."])
    with zipfile.ZipFile(doc, "w") as z:
        z.writestr("word/document.xml", f'<w:document xmlns:w="x"><w:body>{body}</w:body></w:document>')
    assert produce.read_story(doc) == "Tên Truyện\n\nChương 1\n\nMột & hai."


def test_read_legacy_encodings(tmp_path):
    for text in ("Đêm nay cô đi xa.\n\nChương 1\n\nCô đi..", "Đêm nay cô đi xa.\n\nChương 1\n\nCô đi."):  # byte chẵn/lẻ
        f = tmp_path / "c.txt"
        f.write_bytes(text.encode("cp1258"))
        assert produce.read_story(f) == text
        f.write_bytes(text.encode("utf-16"))
        assert produce.read_story(f) == text


def test_slugify():
    assert produce.slugify("Đế Vương Trọng Sinh!") == "de-vuong-trong-sinh"


def test_plan_covers_duration_and_is_deterministic():
    p1, p2 = reel.make_plan(185, 3, 60), reel.make_plan(185, 3, 60)
    assert p1 == p2
    acts = p1["acts"]
    assert acts[0]["start"] == 0 and abs(acts[-1]["end"] - 185) < 1e-6
    for a in acts:
        assert 2 <= len(a["cast"]) <= 3
        assert a["beats"][0]["start"] == a["start"] and abs(a["beats"][-1]["end"] - a["end"]) < 1e-6
        for b0, b1 in zip(a["beats"], a["beats"][1:]):
            assert b0["end"] == b1["start"]
        for b in a["beats"]:
            assert reel.BEATS[b["kind"]][0] <= len(a["cast"])


def test_every_beat_renders(tmp_path):
    """Vẽ vài khung của MỌI vi kịch bản ở cỡ nhỏ (16:9 và 9:16): không lỗi, đúng số byte."""
    for size in ("320x180", "180x320"):
        plan = reel.make_plan(20, 1, 60)
        a = plan["acts"][0]
        a["beats"] = [dict(a["beats"][0], kind=k, start=i * 2.0, end=i * 2.0 + 2.0, shot=reel.BEATS[k][1][0])
                      for i, k in enumerate(reel.BEATS)]
        a["end"] = plan["duration"] = len(reel.BEATS) * 2.0
        r = reel.Renderer(plan, size, 6, None)
        w, h = map(int, size.split("x"))
        for fi in range(0, int(plan["duration"] * 6), 2):
            assert len(r.frame(fi)) == w * h * 3


# ───── trạng thái: làm tiếp, thử lại, redo, khoá thiết lập (giọng/video giả, không gọi model) ─────
import subprocess  # noqa: E402
import sys  # noqa: E402

import pytest  # noqa: E402


@pytest.fixture
def fake(tmp_path, monkeypatch):
    monkeypatch.setattr(produce, "STORIES", tmp_path / "stories")
    calls = {"voice": [], "video": [], "fail": set(), "s": []}

    def voice(job, part, s):
        calls["voice"].append(part["id"])
        calls["s"].append(dict(s))
        if part["id"] in calls["fail"]:
            raise RuntimeError("giả lập lỗi")
        job.p("mp3", part["id"]).parent.mkdir(parents=True, exist_ok=True)
        job.p("mp3", part["id"]).write_bytes(b"x")
        from src.common.tts import write_srt
        write_srt(job.p("srt", part["id"]), [(0.0, 0.5, f"câu {part['id']}")])

    def video(job, part, s):
        calls["video"].append(part["id"])
        out = job.p("mp4", part["id"])
        out.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=red:s=64x36:d=1", "-f", "lavfi",
                        "-i", "anullsrc=r=48000:cl=mono", "-t", "1", "-c:v", "libx264", "-c:a", "aac", "-pix_fmt",
                        "yuv420p", str(out)], check=True)

    monkeypatch.setattr(produce, "do_voice", voice)
    monkeypatch.setattr(produce, "do_video", video)
    return calls


def cli(*args):
    sys_argv = ["produce", *args]
    import unittest.mock as m
    with m.patch.object(sys, "argv", sys_argv):
        try:
            return produce.main()
        except SystemExit as e:
            return e.code


def test_resume_retry_redo(fake):
    story = str(DATA / "sample_story.txt")
    fake["fail"].add("002")
    assert cli("run", story, "--slug", "t", "--part-chars", "500", "--retries", "1") == 1
    job = produce.Job("t")
    assert job.data["parts"][1]["voice"]["status"] == "failed" and job.data["parts"][1]["voice"]["attempts"] == 2
    assert job.data["parts"][0]["video"]["status"] == "done" and "final" not in job.data
    fake["fail"].clear()
    fake["voice"].clear()
    assert cli("run", "--slug", "t") == 0                       # làm tiếp: chỉ làm phần lỗi
    assert fake["voice"] == ["002"]
    job = produce.Job("t")
    out = job.dir / "output" / "t.mp4"
    assert out.exists() and (job.dir / "output" / "upload.md").exists()
    srt = (job.dir / "output" / "t.srt").read_text(encoding="utf-8")
    assert "00:00:01,000 --> 00:00:01,500" in srt                  # câu phần 2 lệch đúng 1 giây
    fake["voice"].clear()
    fake["video"].clear()
    assert cli("run", "--slug", "t", "--redo", "001:voice") == 0
    assert fake["voice"] == ["001"] and fake["video"] == ["001"]   # giọng mới → video dựng lại
    assert cli("run", "--slug", "t", "--redo", "001:foo") != 0


def test_locked_settings_and_machine_settings(fake):
    story = str(DATA / "sample_story.txt")
    assert cli("run", story, "--slug", "k", "--part-chars", "500") == 0
    assert "Lỗi" in str(cli("run", "--slug", "k", "--size", "1080x1920"))     # đã có video xong → không đổi khung
    assert produce.Job("k").data["settings"]["size"] == "1920x1080"
    fake["s"].clear()
    assert cli("run", "--slug", "k", "--redo", "001", "--tts-workers", "1") == 0
    assert fake["s"][-1]["tts_workers"] == 1                         # khoá máy luôn lấy mới


def test_lock_blocks_second_run(fake):
    import os
    assert cli("run", str(DATA / "sample_story.txt"), "--slug", "l", "--part-chars", "500") == 0
    job = produce.Job("l")
    (job.dir / ".lock").write_text(str(os.getpid()))                # giả như tiến trình này đang chạy
    assert "đang được chạy" in str(cli("run", "--slug", "l"))
    (job.dir / ".lock").write_text("999999")                         # PID đã chết → khoá thừa, chạy được
    assert cli("run", "--slug", "l") == 0


def test_folder_of_chapters_with_report(fake, tmp_path):
    d = tmp_path / "chuong"
    d.mkdir()
    (d / "002.txt").write_text("Chương 2: Sau đó\n\nAnh ấy quay lại.\n=== BÁO CÁO KIỂM DUYỆT ===\n- Đã bỏ: không có",
                               encoding="utf-8")
    (d / "001.txt").write_text("Chương 1: Bắt đầu\n\nCô ấy đi xa.\n=== BÁO CÁO KIỂM DUYỆT ===\n- Đã sửa: x → y",
                               encoding="utf-8")
    assert cli("run", str(d), "--slug", "f", "--title", "Truyện Thử", "--part-chars", "30") == 0
    job = produce.Job("f")
    assert job.data["title"] == "Truyện Thử"
    texts = [job.p("text", p["id"]).read_text(encoding="utf-8") for p in job.data["parts"]]
    full = "\n".join(texts)
    assert full.index("Chương 1") < full.index("Chương 2")
    assert "BÁO CÁO" not in full and "Đã sửa" not in full
    assert sorted(x.name for x in (job.dir / "source").iterdir()) == ["001.txt", "002.txt"]


def test_folder_natural_order(tmp_path):
    for n in (1, 2, 10):
        (tmp_path / f"Chương {n}.txt").write_text(f"Chương {n}", encoding="utf-8")
    assert [f.name for f in produce.story_files([tmp_path])] == ["Chương 1.txt", "Chương 2.txt", "Chương 10.txt"]
