"""Test cho src/common/llm.py: split_text, complete (HTTP giả), CLI (complete giả)."""

from __future__ import annotations

import http.client
import io
import json
import urllib.error

import pytest

from src.common import llm


class FakeResponse:
    """Giả lập response 200 với body JSON hợp lệ (dict Python)."""

    def __init__(self, payload: dict):
        self._data = json.dumps(payload).encode("utf-8")

    def read(self) -> bytes:
        return self._data

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeRawResponse:
    """Giả lập response 200 với body thô (bytes), dùng để test JSON hỏng."""

    def __init__(self, raw: bytes):
        self._raw = raw

    def read(self) -> bytes:
        return self._raw

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def _ok_payload(text: str = "ok", tokens: int = 10, finish_reason: str = "stop") -> dict:
    return {
        "choices": [{"message": {"content": text}, "finish_reason": finish_reason}],
        "usage": {"total_tokens": tokens},
    }


# --- split_text ---


def test_split_text_gop_doan_ngan():
    text = "Đoạn một.\n\nĐoạn hai.\n\nĐoạn ba."
    chunks = llm.split_text(text, max_chars=1000)
    assert chunks == ["Đoạn một.\n\nĐoạn hai.\n\nĐoạn ba."]


def test_split_text_cat_theo_doan_van():
    text = "A" * 50 + "\n\n" + "B" * 50 + "\n\n" + "C" * 50
    chunks = llm.split_text(text, max_chars=60)
    assert len(chunks) == 3
    assert chunks[0] == "A" * 50
    assert chunks[1] == "B" * 50
    assert chunks[2] == "C" * 50


def test_split_text_doan_don_dai_qua_cat_theo_cau():
    para = "Câu một. Câu hai. Câu ba."
    chunks = llm.split_text(para, max_chars=12)
    assert all(len(c) <= 12 or " " not in c for c in chunks)
    assert "".join(chunks).replace(" ", "") != ""
    # ghép lại phải còn đủ nội dung các câu
    joined = " ".join(chunks)
    assert "Câu một." in joined
    assert "Câu ba." in joined


# --- complete: thành công / retry ---


def test_complete_thanh_cong(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")

    def fake_urlopen(request, timeout=None):
        assert request.get_header("Authorization") == "Bearer test-key"
        return FakeResponse(_ok_payload("xin chào"))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    result = llm.complete(system="s", user="u")
    assert result["text"] == "xin chào"
    assert result["usage"]["total_tokens"] == 10
    assert result["seconds"] >= 0


def test_complete_retry_429_roi_thanh_cong(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def fake_urlopen(request, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise urllib.error.HTTPError(
                request.full_url, 429, "Too Many Requests", {}, io.BytesIO(b"{}")
            )
        return FakeResponse(_ok_payload("ok sau retry"))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    result = llm.complete(system="s", user="u")
    assert result["text"] == "ok sau retry"
    assert calls["n"] == 2


def test_complete_loi_5xx_het_luot_retry(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)

    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 503, "Service Unavailable", {}, io.BytesIO(b"{}")
        )

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError):
        llm.complete(system="s", user="u", retries=2)


def test_complete_retry_os_error_mat_ket_noi(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def fake_urlopen(request, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise ConnectionResetError("mất kết nối")
        return FakeResponse(_ok_payload("ok sau lỗi mạng"))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    result = llm.complete(system="s", user="u")
    assert result["text"] == "ok sau lỗi mạng"
    assert calls["n"] == 2


def test_complete_retry_http_client_exception(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    calls = {"n": 0}

    def fake_urlopen(request, timeout=None):
        calls["n"] += 1
        if calls["n"] == 1:
            raise http.client.RemoteDisconnected("server đóng kết nối")
        return FakeResponse(_ok_payload("ok"))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    result = llm.complete(system="s", user="u")
    assert result["text"] == "ok"
    assert calls["n"] == 2


def test_complete_het_luot_retry_do_timeout(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(llm.time, "sleep", lambda s: None)

    def fake_urlopen(request, timeout=None):
        raise TimeoutError("hết thời gian chờ")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError):
        llm.complete(system="s", user="u", retries=2)


# --- complete: key ---


def test_complete_thieu_key_bao_loi_ro(monkeypatch, tmp_path):
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.setattr(llm, "REPO_ROOT", tmp_path)  # không có .env ở đây
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    assert "ZAI_API_KEY" in str(exc_info.value)


def test_complete_loi_khong_lo_key(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "SECRET-KHONG-DUOC-LO")

    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(
            request.full_url, 400, "Bad Request", {}, io.BytesIO(b"{}")
        )

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    assert "SECRET-KHONG-DUOC-LO" not in str(exc_info.value)


def test_complete_loi_http_kem_body_preview_khong_lo_key(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "SECRET-KEY-XYZ")
    body = (
        b'{"error": {"code": 1213, '
        b'"message": "The prompt parameter was not received normally"}}'
    )

    def fake_urlopen(request, timeout=None):
        raise urllib.error.HTTPError(request.full_url, 400, "Bad Request", {}, io.BytesIO(body))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    msg = str(exc_info.value)
    assert "1213" in msg or "prompt parameter" in msg
    assert "SECRET-KEY-XYZ" not in msg


def test_complete_doc_key_tu_env_file(monkeypatch, tmp_path):
    monkeypatch.delenv("ZAI_API_KEY", raising=False)
    monkeypatch.setattr(llm, "REPO_ROOT", tmp_path)
    (tmp_path / ".env").write_text("ZAI_API_KEY=tu-file-env\n", encoding="utf-8")

    def fake_urlopen(request, timeout=None):
        assert request.get_header("Authorization") == "Bearer tu-file-env"
        return FakeResponse(_ok_payload("ok"))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    result = llm.complete(system="s", user="u")
    assert result["text"] == "ok"


# --- complete: response 200 nhưng bất thường ---


def test_complete_response_khong_phai_json(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm.urllib.request,
        "urlopen",
        lambda request, timeout=None: FakeRawResponse(b"<html>loi server</html>"),
    )
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    assert "JSON" in str(exc_info.value)


def test_complete_response_co_truong_error(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    payload = {
        "error": {"code": 1213, "message": "The prompt parameter was not received normally"}
    }
    monkeypatch.setattr(
        llm.urllib.request, "urlopen", lambda request, timeout=None: FakeResponse(payload)
    )
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    assert "1213" in str(exc_info.value) or "prompt parameter" in str(exc_info.value)


def test_complete_finish_reason_khac_stop_khong_retry(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    calls = {"n": 0}

    def fake_urlopen(request, timeout=None):
        calls["n"] += 1
        return FakeResponse(_ok_payload("bị cắt cụt", finish_reason="length"))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    assert "finish_reason" in str(exc_info.value)
    assert calls["n"] == 1  # không retry lỗi này


def test_complete_content_rong_bao_loi(monkeypatch):
    monkeypatch.setenv("ZAI_API_KEY", "test-key")
    monkeypatch.setattr(
        llm.urllib.request,
        "urlopen",
        lambda request, timeout=None: FakeResponse(_ok_payload(text="", finish_reason="stop")),
    )
    with pytest.raises(RuntimeError) as exc_info:
        llm.complete(system="s", user="u")
    assert "content_rong" in str(exc_info.value) or "không hợp lệ" in str(exc_info.value)


# --- CLI ---


def _fake_complete_factory():
    def fake_complete(system, user, model=llm.DEFAULT_MODEL, thinking=False, max_tokens=8192, **kwargs):
        return {
            "text": f"[{model}] {system[:20]}|{user[:20]}",
            "usage": {"total_tokens": 3},
            "seconds": 0.01,
        }

    return fake_complete


def test_cli_tao_file_dau_ra_va_log(monkeypatch, tmp_path):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Viết lại: {{text}}", encoding="utf-8")
    input_file = tmp_path / "001.txt"
    input_file.write_text("Đoạn một.\n\nĐoạn hai.", encoding="utf-8")
    out_dir = tmp_path / "out"

    monkeypatch.setattr(llm, "complete", _fake_complete_factory())

    rc = llm._run_cli(
        [
            "--prompt", str(prompt_file),
            "--input", str(input_file),
            "--out", str(out_dir),
            "--chunk-chars", "1000",
        ]
    )
    assert rc == 0

    out_file = out_dir / "001.txt"
    assert out_file.exists()
    assert "Viết lại:" in out_file.read_text(encoding="utf-8")

    log_lines = (out_dir / "run.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) == 1
    record = json.loads(log_lines[0])
    assert record["file"] == str(input_file)
    assert record["chunk_index"] == 0
    assert record["error"] is None
    assert record["usage"]["total_tokens"] == 3

    meta = json.loads((out_dir / "meta.json").read_text(encoding="utf-8"))
    assert meta["model"] == llm.DEFAULT_MODEL
    assert meta["prompt"] == str(prompt_file)


def test_cli_bo_qua_file_da_co(monkeypatch, tmp_path):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Hệ thống", encoding="utf-8")
    input_file = tmp_path / "002.txt"
    input_file.write_text("Nội dung.", encoding="utf-8")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    (out_dir / "002.txt").write_text("ĐÃ CÓ TRƯỚC", encoding="utf-8")

    monkeypatch.setattr(llm, "complete", _fake_complete_factory())

    rc = llm._run_cli(
        [
            "--prompt", str(prompt_file),
            "--input", str(input_file),
            "--out", str(out_dir),
        ]
    )
    assert rc == 0
    assert (out_dir / "002.txt").read_text(encoding="utf-8") == "ĐÃ CÓ TRƯỚC"

    rc = llm._run_cli(
        [
            "--prompt", str(prompt_file),
            "--input", str(input_file),
            "--out", str(out_dir),
            "--force",
        ]
    )
    assert rc == 0
    assert (out_dir / "002.txt").read_text(encoding="utf-8") != "ĐÃ CÓ TRƯỚC"


def test_cli_placeholder_gui_user_khong_rong_khong_dung_system(monkeypatch, tmp_path):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Tóm tắt: {{text}}", encoding="utf-8")
    input_file = tmp_path / "003.txt"
    input_file.write_text("Nội dung cần tóm tắt.", encoding="utf-8")
    out_dir = tmp_path / "out"

    captured = {}

    def fake_complete(system, user, model=llm.DEFAULT_MODEL, thinking=False, max_tokens=8192, **kwargs):
        captured["system"] = system
        captured["user"] = user
        return {"text": "tóm tắt xong", "usage": {}, "seconds": 0.0}

    monkeypatch.setattr(llm, "complete", fake_complete)
    rc = llm._run_cli(
        ["--prompt", str(prompt_file), "--input", str(input_file), "--out", str(out_dir)]
    )
    assert rc == 0
    assert captured["system"] == ""
    assert captured["user"].strip() != ""
    assert "{{text}}" not in captured["user"]
    assert "Nội dung cần tóm tắt." in captured["user"]


def test_cli_loi_finish_reason_khong_ghi_file_va_rerun_khong_bo_qua(monkeypatch, tmp_path, capsys):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Hệ thống đơn giản", encoding="utf-8")
    input_file = tmp_path / "004.txt"
    input_file.write_text("Nội dung.", encoding="utf-8")
    out_dir = tmp_path / "out"

    calls = {"n": 0}

    def fake_complete_bad(system, user, model=llm.DEFAULT_MODEL, thinking=False, max_tokens=8192, **kwargs):
        calls["n"] += 1
        raise RuntimeError("Kết quả không hợp lệ: finish_reason='length', content_rong=False")

    monkeypatch.setattr(llm, "complete", fake_complete_bad)

    rc = llm._run_cli(
        ["--prompt", str(prompt_file), "--input", str(input_file), "--out", str(out_dir)]
    )
    assert rc == 1
    assert not (out_dir / "004.txt").exists()

    captured = capsys.readouterr()
    assert "Traceback" not in captured.out
    assert "Traceback" not in captured.err
    assert any(line.startswith("Lỗi:") for line in captured.out.splitlines())

    log_lines = (out_dir / "run.jsonl").read_text(encoding="utf-8").strip().splitlines()
    assert len(log_lines) == 1
    record = json.loads(log_lines[0])
    assert record["error"] is not None

    # chạy lại: chưa có file .txt nên không bị bỏ qua, complete được gọi lại
    rc2 = llm._run_cli(
        ["--prompt", str(prompt_file), "--input", str(input_file), "--out", str(out_dir)]
    )
    assert rc2 == 1
    assert calls["n"] == 2


def test_cli_trung_ten_file_bao_loi_ngay_tu_dau(monkeypatch, tmp_path):
    prompt_file = tmp_path / "prompt.md"
    prompt_file.write_text("Hệ thống", encoding="utf-8")
    dir_a = tmp_path / "a"
    dir_a.mkdir()
    dir_b = tmp_path / "b"
    dir_b.mkdir()
    (dir_a / "005.txt").write_text("nội dung a", encoding="utf-8")
    (dir_b / "005.txt").write_text("nội dung b", encoding="utf-8")
    out_dir = tmp_path / "out"

    called = {"n": 0}

    def fake_complete(*a, **k):
        called["n"] += 1
        return {"text": "x", "usage": {}, "seconds": 0.0}

    monkeypatch.setattr(llm, "complete", fake_complete)

    rc = llm._run_cli(
        [
            "--prompt", str(prompt_file),
            "--input", str(dir_a / "005.txt"), str(dir_b / "005.txt"),
            "--out", str(out_dir),
        ]
    )
    assert rc == 1
    assert called["n"] == 0  # báo lỗi ngay từ đầu, chưa gọi complete
    assert not out_dir.exists()
