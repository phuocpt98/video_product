"""Gọi model LLM ngoài (mặc định GLM-4.7-Flash của Z.ai), API tương thích OpenAI chat completions.

Dùng stdlib `urllib`, không thêm thư viện cho lõi. Key lấy từ biến môi trường
`ZAI_API_KEY`, nếu thiếu thì đọc file `.env` ở gốc repo. Không bao giờ in key.
"""

from __future__ import annotations

import argparse
import glob as _glob
import http.client
import json
import os
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_BASE_URL = "https://api.z.ai/api/paas/v4/chat/completions"
DEFAULT_MODEL = "glm-4.7-flash"
_SENTENCE_SPLIT_RE = re.compile(r"(?<=[。！？.!?])\s*")
_NETWORK_ERRORS = (urllib.error.URLError, http.client.HTTPException, OSError)


def _load_api_key() -> str:
    key = os.environ.get("ZAI_API_KEY")
    if key:
        return key
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            if k.strip() == "ZAI_API_KEY":
                return v.strip().strip('"').strip("'")
    raise RuntimeError(
        "Thiếu ZAI_API_KEY: đặt biến môi trường hoặc thêm dòng ZAI_API_KEY=... vào .env ở gốc repo."
    )


def _parse_response(raw: bytes) -> dict:
    """Kiểm và rút text/usage từ body JSON. Ném RuntimeError nếu bất thường (không lộ key)."""
    raw_text = raw.decode("utf-8", errors="replace")
    try:
        body = json.loads(raw_text)
    except json.JSONDecodeError:
        raise RuntimeError(f"Phản hồi API không phải JSON: {raw_text[:300]!r}") from None
    if isinstance(body, dict) and body.get("error"):
        raise RuntimeError(
            f"API GLM báo lỗi: {json.dumps(body['error'], ensure_ascii=False)[:300]}"
        ) from None
    try:
        choice = body["choices"][0]
        message = choice["message"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError(f"Phản hồi API thiếu choices/message: {raw_text[:300]!r}") from None
    content = message.get("content")
    finish_reason = choice.get("finish_reason")
    if finish_reason != "stop" or not content:
        raise RuntimeError(
            f"Kết quả không hợp lệ: finish_reason={finish_reason!r}, content_rong={not content}"
        )
    usage = body.get("usage", {})
    return {"text": content, "usage": usage}


def complete(
    system: str,
    user: str,
    model: str = DEFAULT_MODEL,
    thinking: bool = False,
    max_tokens: int = 8192,
    temperature: Optional[float] = None,
    base_url: str = DEFAULT_BASE_URL,
    retries: int = 3,
) -> dict:
    """Gọi API chat completions. Trả về {"text": str, "usage": dict, "seconds": float}.

    Retry (backoff 2**n giây) khi HTTP 429, 5xx, hoặc lỗi mạng (URLError, HTTPException,
    OSError như mất kết nối/timeout). Response 200 nhưng JSON hỏng, có "error", thiếu
    choices/message, finish_reason khác "stop" hoặc content rỗng thì coi là lỗi không
    retry (raise ngay, không lộ key trong thông điệp).
    """
    api_key = _load_api_key()
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "thinking": {"type": "enabled" if thinking else "disabled"},
    }
    if temperature is not None:
        payload["temperature"] = temperature
    data = json.dumps(payload).encode("utf-8")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    last_err = "không rõ"
    for attempt in range(retries):
        start = time.time()
        request = urllib.request.Request(base_url, data=data, headers=headers, method="POST")
        try:
            with urllib.request.urlopen(request, timeout=120) as resp:
                raw = resp.read()
        except urllib.error.HTTPError as e:
            status = e.code
            try:
                err_text = e.read().decode("utf-8", errors="replace")[:300]
            except Exception:
                err_text = ""
            last_err = f"HTTP {status}: {err_text}" if err_text else f"HTTP {status}"
            retryable = status == 429 or 500 <= status < 600
            if retryable and attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"Gọi API GLM thất bại: {last_err}") from None
        except _NETWORK_ERRORS as e:
            last_err = f"lỗi mạng: {e}"
            if attempt < retries - 1:
                time.sleep(2**attempt)
                continue
            raise RuntimeError(f"Gọi API GLM thất bại: {last_err}") from None
        else:
            seconds = time.time() - start
            parsed = _parse_response(raw)
            return {"text": parsed["text"], "usage": parsed["usage"], "seconds": seconds}
    raise RuntimeError(f"Gọi API GLM thất bại sau {retries} lần: {last_err}")


def split_text(text: str, max_chars: int) -> list[str]:
    """Cắt văn bản theo đoạn (dòng trống), gộp đoạn cho tới max_chars.

    Đoạn đơn dài hơn max_chars thì cắt tiếp theo câu (。！？.!?).
    """
    paragraphs = [p for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(para) <= max_chars:
            current = para
            continue
        # đoạn đơn dài quá max_chars: cắt theo câu
        sentences = [s for s in _SENTENCE_SPLIT_RE.split(para) if s]
        piece = ""
        for sentence in sentences:
            candidate_piece = f"{piece} {sentence}".strip() if piece else sentence
            if len(candidate_piece) <= max_chars:
                piece = candidate_piece
            else:
                if piece:
                    chunks.append(piece)
                piece = sentence
        current = piece
    if current:
        chunks.append(current)
    return chunks


def _iter_input_files(patterns: list[str]) -> list[Path]:
    files: list[Path] = []
    for pattern in patterns:
        matched = sorted(_glob.glob(pattern))
        if not matched and Path(pattern).exists():
            matched = [pattern]
        files.extend(Path(m) for m in matched)
    seen: set[Path] = set()
    unique: list[Path] = []
    for f in files:
        if f not in seen:
            seen.add(f)
            unique.append(f)
    return unique


def _run(args: argparse.Namespace) -> int:
    prompt_path = Path(args.prompt)
    system_prompt = prompt_path.read_text(encoding="utf-8")
    has_placeholder = "{{text}}" in system_prompt

    input_files = _iter_input_files(args.input)
    if not input_files:
        raise RuntimeError(f"Không tìm thấy file đầu vào khớp: {args.input}")

    stems = [f.stem for f in input_files]
    dup_stems = sorted({s for s in stems if stems.count(s) > 1})
    if dup_stems:
        raise RuntimeError(
            f"Có file đầu vào trùng tên (cùng tạo ra một file đầu ra): {dup_stems}"
        )

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    log_path = out_dir / "run.jsonl"
    meta_path = out_dir / "meta.json"

    meta = {
        "prompt": str(prompt_path),
        "model": args.model,
        "thinking": args.thinking,
        "max_tokens": args.max_tokens,
        "chunk_chars": args.chunk_chars,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    for input_file in input_files:
        out_file = out_dir / f"{input_file.stem}.txt"
        if out_file.exists() and not args.force:
            print(f"Bỏ qua (đã có): {out_file}")
            continue
        text = input_file.read_text(encoding="utf-8")
        chunks = split_text(text, args.chunk_chars)
        outputs = []
        with log_path.open("a", encoding="utf-8") as log_f:
            for i, chunk in enumerate(chunks):
                if has_placeholder:
                    # prompt đã có {{text}}: gộp cả chỉ dẫn + văn bản làm user, không dùng system
                    # (system rỗng + user rỗng bị Z.ai từ chối với lỗi "prompt not received")
                    system = ""
                    user = system_prompt.replace("{{text}}", chunk)
                else:
                    system = system_prompt
                    user = chunk
                error = None
                result_text = ""
                usage: dict = {}
                seconds = 0.0
                try:
                    result = complete(
                        system=system,
                        user=user,
                        model=args.model,
                        thinking=args.thinking,
                        max_tokens=args.max_tokens,
                    )
                    result_text = result["text"]
                    usage = result["usage"]
                    seconds = result["seconds"]
                except Exception as e:  # noqa: BLE001 - ghi lỗi vào log rồi dừng
                    error = str(e)
                log_f.write(
                    json.dumps(
                        {
                            "file": str(input_file),
                            "chunk_index": i,
                            "chars_in": len(chunk),
                            "usage": usage,
                            "seconds": seconds,
                            "error": error,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )
                if error:
                    # không ghi ra out_file, để lần chạy sau thử lại đoạn/file này
                    raise RuntimeError(f"Lỗi khi gọi GLM cho {input_file} đoạn {i}: {error}")
                outputs.append(result_text)
        out_file.write_text("\n\n".join(outputs), encoding="utf-8")
        print(f"Đã ghi: {out_file}")
    return 0


def _run_cli(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Chạy một prompt qua GLM cho một hoặc nhiều file văn bản."
    )
    parser.add_argument("--prompt", required=True, help="File .md chứa system prompt")
    parser.add_argument(
        "--input", required=True, nargs="+", help="File hoặc glob đầu vào, có thể nhiều"
    )
    parser.add_argument("--out", required=True, help="Thư mục ghi kết quả")
    parser.add_argument("--chunk-chars", type=int, default=4000)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--thinking", action="store_true")
    parser.add_argument("--max-tokens", type=int, default=8192)
    parser.add_argument("--force", action="store_true", help="Ghi lại file đầu ra đã có")
    args = parser.parse_args(argv)

    try:
        return _run(args)
    except Exception as e:  # noqa: BLE001 - in gọn 1 dòng, không traceback
        print(f"Lỗi: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(_run_cli())
