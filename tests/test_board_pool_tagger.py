import io
import json
import pathlib
import time
import urllib.error

import pytest
import yaml
from PIL import Image

from src import board
from src.common import pool
from src.studio import tagger


# ---------------------------------------------------------------- board
@pytest.fixture
def B(tmp_path, monkeypatch):
    monkeypatch.setattr(board, "ROOT", tmp_path)
    monkeypatch.setattr(board, "BOARD", tmp_path / "board")
    monkeypatch.setattr(board, "TASKS", tmp_path / "board/tasks")
    monkeypatch.setattr(board, "EVENTS", tmp_path / "board/events.jsonl")
    monkeypatch.setattr(board, "INBOX", tmp_path / "board/inbox")
    return tmp_path


def test_new_khong_trung(B):
    a = board.new("dung", "thiet-ke", "need-actor", "x", "actor:a", "s", 1, {"actor": "a", "name": "A"})
    b = board.new("dung", "thiet-ke", "need-actor", "x", "actor:a", "s", 2, {"actor": "a", "name": "A"})
    assert a["id"] == b["id"]
    assert len(list(board.TASKS.glob("*.yaml"))) == 1


def test_block_va_mo_lai(B, monkeypatch):
    calls = []

    def fake_direct(slug, ch):
        have = (B / "assets/actors/a/card.yaml").exists() and (B / "assets/scenes/s1/master.jpg").exists()
        miss = {"diễn viên": set() if (B / "assets/actors/a/card.yaml").exists() else {"A (a)"},
                "nền": set() if (B / "assets/scenes/s1/master.jpg").exists() else {"s1"}, "đạo cụ": set()}
        return {"shots": [1]}, miss
    import src.studio.direct as D
    monkeypatch.setattr(D, "direct", fake_direct)
    (B / "stories/st").mkdir(parents=True)
    (B / "stories/st/cast.yaml").write_text(yaml.safe_dump({"lead": "A", "characters": {"A": {"actor": "a"}}}))
    (B / "channels/khoai-tay-review").mkdir(parents=True)
    (B / "channels/khoai-tay-review/channel.yaml").write_text("visual_style: flat\n")

    def fake_actor(t):
        calls.append(("actor", t["id"]))
        (B / "assets/actors/a").mkdir(parents=True, exist_ok=True)
        (B / "assets/actors/a/card.yaml").write_text("x: 1")
        board.done(t, "thiet-ke", "ok")
    monkeypatch.setattr(board, "WORKERS", {**board.WORKERS, ("thiet-ke", "need-actor"): fake_actor})
    import src.studio.stage as S
    monkeypatch.setattr(S, "render", lambda *a, **k: calls.append(("render",)))

    r = board.new("dieu-phoi", "dung", "render", "Dựng 1", "render:st:1", "st", 1)
    board.run_once()
    r = board.get(r["id"])
    assert r["status"] == "blocked" and len(r["waiting_on"]) == 2
    board.run_once()          # actor done; scene -> need-image, still blocked
    r = board.get(r["id"])
    assert r["status"] == "blocked"
    img_task = [t for t in board.tasks() if t["type"] == "need-image"][0]
    board.INBOX.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (32, 18), "red").save(board.INBOX / f"{img_task['id']}.png")
    board.run_once()          # inbox -> image done -> scene reopen ; scene done -> render reopen
    board.run_once()
    board.run_once()
    r = board.get(r["id"])
    assert r["status"] == "done", r
    assert ("render",) in calls


def test_loi_khong_ket_doing(B, monkeypatch):
    import src.studio.direct as D
    import src.studio.stage as S
    monkeypatch.setattr(D, "direct", lambda s, c: ({"shots": []}, {"diễn viên": set(), "nền": set(), "đạo cụ": set()}))
    (B / "stories/st").mkdir(parents=True)
    (B / "stories/st/cast.yaml").write_text("lead: A\ncharacters: {}\n")

    def boom(*a, **k):
        raise RuntimeError("ffmpeg lỗi")
    monkeypatch.setattr(S, "render", boom)
    r = board.new("dieu-phoi", "dung", "render", "Dựng 1", "render:st:1", "st", 1)
    board.run_once()
    assert board.get(r["id"])["status"] == "open"


def test_inbox_anh_hong_lam_sap_run(B):
    t = board.new("boi-canh", "nguoi-sang-lap", "need-image", "Ảnh", "image:scene:s9", "st", 1, {"scene": "s9"})
    board.INBOX.mkdir(parents=True, exist_ok=True)
    (board.INBOX / f"{t['id']}.png").write_bytes(b"not an image")
    board.run_once()   # expected: not crash whole loop


def test_id_trung_khi_xoa_file(B):
    a = board.new("x", "dung", "render", "a", "k1")
    b = board.new("x", "dung", "render", "b", "k2")
    (board.TASKS / f"{a['id']}.yaml").unlink()
    c = board.new("x", "dung", "render", "c", "k3")
    assert c["id"] != b["id"]


# ---------------------------------------------------------------- pool
CFG = {"providers": {"p1": {"url": "http://x", "model": "m", "key_env": "K1", "cooldown": 60},
                     "p2": {"url": "http://y", "model": "m", "key_env": "K2", "cooldown": 60},
                     "p3": {"url": "http://z", "model": "m", "key_env": "K3_NOKEY"}},
       "pool": {"default": ["p3", "p1", "p2"]}}


class Resp(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *a):
        pass


@pytest.fixture
def P(monkeypatch, tmp_path):
    monkeypatch.setattr(pool, "_cfg", lambda: CFG)
    monkeypatch.setattr(pool, "ROOT", tmp_path)
    monkeypatch.setenv("K1", "sk-SECRET1234")
    monkeypatch.setenv("K2", "sk-SECRET5678")
    monkeypatch.delenv("K3_NOKEY", raising=False)
    pool._COOLDOWN.clear()
    return monkeypatch


def test_pool_429_chuyen_nguon(P):
    seen = []

    def fake(req, timeout):
        seen.append(req.full_url)
        if req.full_url == "http://x":
            raise urllib.error.HTTPError(req.full_url, 429, "too many", {}, None)
        return Resp(json.dumps({"choices": [{"message": {"content": "ok"}}]}).encode())
    P.setattr(pool.urllib.request, "urlopen", fake)
    assert pool.ask("default", "hi") == ("ok", "p2")
    assert "http://z" not in seen
    assert pool._COOLDOWN["p1"] > time.time()
    seen.clear()
    assert pool.ask("default", "hi") == ("ok", "p2")
    assert seen == ["http://y"]


def test_pool_het_nguon(P):
    def fake(req, timeout):
        raise urllib.error.HTTPError(req.full_url, 503, "down " + req.headers.get("Authorization", ""), {}, None)
    P.setattr(pool.urllib.request, "urlopen", fake)
    with pytest.raises(RuntimeError) as e:
        pool.ask("default", "hi")
    assert "SECRET" not in str(e.value)
    print(e.value)
    with pytest.raises(RuntimeError) as e:     # all in cooldown now
        pool.ask("default", "hi")
    print("lần 2:", repr(str(e.value)))


def test_pool_bi_cat_length(P):
    def fake(req, timeout):
        return Resp(json.dumps({"choices": [{"message": {"content": '{"tags": [{"i": 1'},
                                             "finish_reason": "length"}]}).encode())
    P.setattr(pool.urllib.request, "urlopen", fake)
    with pytest.raises(RuntimeError, match="bị cắt"):          # bị cắt thì coi là lỗi, chuyển nguồn khác
        pool.ask("default", "hi")


def test_pool_loi_khong_lo_key(P):
    def fake(req, timeout):
        raise ValueError("bad " + req.headers.get("Authorization", ""))
    P.setattr(pool.urllib.request, "urlopen", fake)
    with pytest.raises(RuntimeError) as e:
        pool.ask("default", "hi")
    assert "Bearer" not in str(e.value) or "***" in str(e.value)


# ---------------------------------------------------------------- tagger.parse
V = {"characters": {"A B": [], "C D": []}, "scenes": ["s1", "s2"], "actions": ["idle", "laugh"],
     "exprs": ["neutral", "sad"], "fx": ["tears"]}


@pytest.mark.parametrize("txt", [
    "", "không có json", "{", '{"tags": 5}', '{"x": []}', '[1,2]', '{"tags": [1, "a", null]}',
    '{"tags": [{"i": "1"}]}',
    '{"tags": [{"i": 1, "present": 5}]}',
    '{"tags": [{"i": 1, "fx": 3}]}',
    '{"tags": [{"i": 1, "speaker": ["A B"]}]}',
    '{"tags": [{"i": 1, "actor": {"x": 1}}]}',
    '{"tags": [{"i": 1, "present": [["A B"]]}]}',
    '{"tags": [{"i": 1, "fx": [["tears"]]}]}',
    '{"tags": [{"i": 1, "scene": ["s1"]}]}',
])
def test_parse_khong_crash(txt):
    out = tagger.parse(txt, V)
    for v in out.values():
        assert v["scene"] in (None, *V["scenes"])


def test_parse_dung():
    out = tagger.parse('```json\n{"tags": [{"i": 1, "scene": "s1", "present": ["A B", "X", "C D", "A B"], '
                       '"speaker": "Z", "actor": "C D", "action": "fly", "expr": "sad", "fx": ["tears", "boom"]}]}\n```', V)
    assert out[1] == {"scene": "s1", "present": ["A B", "C D"], "speaker": None, "actor": "C D", "action": "idle",
                      "expr": "sad", "fx": ["tears"]}


def test_ctrl_c_giua_luc_dung(B, monkeypatch):
    import src.studio.direct as D
    import src.studio.stage as S
    monkeypatch.setattr(D, "direct", lambda s, c: ({"shots": []}, {"diễn viên": set(), "nền": set(), "đạo cụ": set()}))
    (B / "stories/st").mkdir(parents=True)
    (B / "stories/st/cast.yaml").write_text("lead: A\ncharacters: {}\n")

    def stop(*a, **k):
        raise KeyboardInterrupt
    monkeypatch.setattr(S, "render", stop)
    r = board.new("dieu-phoi", "dung", "render", "Dựng 1", "render:st:1", "st", 1)
    with pytest.raises(KeyboardInterrupt):
        board.run_once()
    st = board.get(r["id"])["status"]
    board.run_once.__wrapped__ if False else None
    monkeypatch.setattr(S, "render", lambda *a, **k: None)
    n = board.run_once()
    print("sau Ctrl+C:", st, "run_once lần sau làm", n, "việc; trạng thái", board.get(r["id"])["status"])
