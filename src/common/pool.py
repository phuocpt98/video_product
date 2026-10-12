"""NHÓM NHÂN VIÊN NHIỀU NGUỒN cho việc xử lý chữ máy móc (gắn nhãn, rã chương, chọn bộ phận, soát): gọi lần lượt các
nguồn miễn phí khai trong config.yaml `providers:` theo thứ tự của loại việc (`pool:`), nguồn nào lỗi/hết lượt (429)
thì nghỉ một lúc và chuyển nguồn kế; cuối cùng mới dùng agy (gói Gemini Pro). Việc viết văn chính vẫn ở run.py/agy.

Nguồn tương thích OpenAI chat completions; key đọc từ biến môi trường hoặc .env (không bao giờ in key).
python -m src.common.pool <loại việc> "<câu hỏi>"      # thử nhanh
"""
import json
import os
import pathlib
import sys
import time
import urllib.error
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[2]
_COOLDOWN: dict[str, float] = {}           # nguồn → thời điểm được gọi lại


def _cfg() -> dict:
    return yaml.safe_load((ROOT / "config.yaml").read_text(encoding="utf-8"))


def _key(name: str) -> str | None:
    if os.environ.get(name):
        return os.environ[name]
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            k, _, v = line.partition("=")
            if k.strip() == name and v.strip():
                return v.strip().strip('"').strip("'")
    return None


def available() -> list[str]:
    """Các nguồn đang có key (agy luôn có)."""
    return [p for p, c in _cfg()["providers"].items() if p == "agy" or _key(c["key_env"])]


def _call_openai(c: dict, prompt: str, system: str | None, max_tokens: int, timeout: int, extra: dict | None = None) -> str:
    msgs = ([{"role": "system", "content": system}] if system else []) + [{"role": "user", "content": prompt}]
    body = json.dumps({"model": c["model"], "messages": msgs, "max_tokens": max_tokens, "temperature": 0.3,
                       **c.get("extra", {}), **(extra or {})}).encode()          # extra: tắt "suy nghĩ" để không ăn hết token trả lời
    req = urllib.request.Request(c["url"], body, {"Content-Type": "application/json",
                                                  "Authorization": f"Bearer {_key(c['key_env'])}"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        data = json.loads(r.read())
    ch = data["choices"][0]
    if ch.get("finish_reason") == "length":           # bị cắt giữa chừng (JSON dở dang): coi là lỗi để thử nguồn khác
        raise RuntimeError("câu trả lời bị cắt vì hết max_tokens")
    return (ch["message"].get("content") or "").strip()


def ask(kind: str, prompt: str, system: str | None = None, max_tokens: int = 4000, timeout: int = 180,
        json_mode: bool = False) -> tuple[str, str]:
    """Trả (câu trả lời, tên nguồn đã dùng). Lỗi hết nguồn thì ném RuntimeError. json_mode: xin nguồn trả JSON."""
    cfg = _cfg()
    order = cfg["pool"].get(kind, cfg["pool"]["default"])
    errors = []
    for name in order:
        c = cfg["providers"].get(name)
        if not c:
            errors.append(f"{name}: không khai trong providers")
            continue
        if _COOLDOWN.get(name, 0) > time.time():
            errors.append(f"{name}: đang nghỉ {int(_COOLDOWN[name] - time.time())} giây")
            continue
        try:
            if name == "agy":
                from src.common import agy
                text = agy.run((system + "\n\n" if system else "") + prompt, c["model"], timeout=max(timeout, 600))["text"]
            else:
                if not _key(c["key_env"]):
                    errors.append(f"{name}: chưa có key {c['key_env']}")
                    continue
                extra = {"response_format": {"type": "json_object"}} if json_mode and c.get("json", True) else None
                if c.get("think") and kind in c["think"]:          # việc cần suy nghĩ: bật lại mức thấp
                    extra = {**(extra or {}), **c["think"][kind]}
                text = _call_openai(c, prompt, system, max_tokens, timeout, extra)
            if text:
                return text, name
            errors.append(f"{name}: trả về rỗng")
        except urllib.error.HTTPError as e:
            errors.append(f"{name}: HTTP {e.code}")
            if e.code in (429, 500, 502, 503, 504, 529):
                _COOLDOWN[name] = time.time() + c.get("cooldown", 60)
        except Exception as e:  # noqa: BLE001  mạng chập chờn, timeout: chuyển nguồn
            msg = str(e)
            if c.get("key_env") and _key(c["key_env"]):
                msg = msg.replace(_key(c["key_env"]), "***")      # không bao giờ lộ key trong báo lỗi
            errors.append(f"{name}: {type(e).__name__} {msg[:80]}")
            _COOLDOWN[name] = time.time() + 20
    raise RuntimeError("Hết nguồn: " + "; ".join(errors))


if __name__ == "__main__":
    print("Nguồn có key:", available())
    t0 = time.time()
    out, src = ask(sys.argv[1], sys.argv[2])
    print(f"[{src}, {time.time() - t0:.1f}s] {out[:500]}")
