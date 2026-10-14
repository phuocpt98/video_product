"""Giọng đọc VieNeu-TTS (chạy local, Apache-2.0) + phụ đề .srt theo từng cụm.

Cách đọc (chốt 14/10/2026 sau thí nghiệm 3 cách, xem docs/decisions.md):
  1. clean(): bỏ ký hiệu trang trí, link, emoji, chú thích [1]; mở viết tắt kiểu chat (ko, đc...). Số, ngày, tiền, %, đơn vị
     để VieNeu tự đọc (bộ chuẩn hoá của nó đã đúng: "3.000.000đ" → "ba triệu đồng").
  2. chunks(): tách câu (kể cả sau ngoặc kép đóng), gộp câu ngắn, cắt câu dài ở , ; : → cụm ~40–250 ký tự, mỗi cụm kèm
     khoảng nghỉ theo dấu câu (. 0,25 · ?! 0,3 · … 0,45 · hết đoạn 0,6 · sau tên chương 1,0 giây).
  3. Mỗi cụm đọc riêng (có cache, đọc song song nhiều tiến trình), cắt lặng thừa đầu/cuối, cân âm lượng, ghép + nghỉ,
     tăng tốc bằng atempo, chuẩn độ to -16 LUFS (loudnorm). Mỗi cụm = 1 dòng .srt.
"""
import hashlib
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))  # model AI nằm trong dự án

SR = 48000
MIN_CHUNK, MAX_CHUNK = 40, 250
PAUSE = {".": 0.25, "?": 0.3, "!": 0.3, "…": 0.45}
PAUSE_PARA, PAUSE_HEADING, PAUSE_OTHER = 0.6, 1.0, 0.15
HEADING = re.compile(r"^\s*(chương|chapter|phần|hồi|quyển|tập)\s*[\dIVXLC]+\b.{0,80}$", re.I)
ABBR = {"ko": "không", "đc": "được", "ntn": "như thế nào", "trc": "trước", "mk": "mình", "lun": "luôn"}
# chỉ chữ thường đứng riêng (không dính chữ, số, gạch nối); dạng viết hoa ("Ko") chỉ mở ở đầu câu
END = '"”’»)'

_ENGINE = None


# ───────────────────────────── chữ → cụm ─────────────────────────────

def clean(text: str) -> str:
    t = text.replace("\r\n", "\n")
    t = re.sub(r"https?://\S+|www\.\S+", " ", t)                       # link
    t = re.sub(r"\[\d+\]", "", t)                                      # chú thích [1] ("(28)" = tuổi, giữ)
    t = re.sub(r"[*=#~_^<>|\\/]{2,}|^[\s*=#~_\-–—]+$", " ", t, flags=re.M)   # dải ký hiệu trang trí, dòng kẻ
    t = re.sub(r"[*#_~^|<>\\]", " ", t)                                 # ký hiệu lẻ (markdown...)
    t = re.sub(r"[\U0001F000-\U0001FAFF☀-➿️]", " ", t)  # emoji
    t = re.sub(r"\.{3,}|…+", "…", t)                                   # ba chấm → một ký tự
    t = re.sub(r"([!?])[!?]+", r"\1", t)                               # !!! ?!? → một dấu
    t = re.sub(r"^\s*[-–—]\s*", "", t, flags=re.M)                     # gạch đầu dòng thoại
    low = "|".join(map(re.escape, ABBR))
    t = re.sub(r"(?<![\w-])(" + low + r")(?![\w-])", lambda m: ABBR[m.group(1)], t)
    cap = "|".join(re.escape(k.capitalize()) for k in ABBR)            # viết hoa: chỉ đầu dòng / đầu câu (giữa câu = tên riêng)
    t = re.sub(r"(^|[.!?…][\"”]?\s+|^[\"“]|\s[\"“])(" + cap + r")(?![\w-])",
               lambda m: m.group(1) + ABBR[m.group(2).lower()].capitalize(), t, flags=re.M)
    t = re.sub(r"[ \t]+", " ", t)
    return "\n".join(x.strip() for x in t.split("\n")).strip()


def _sentences(para: str) -> list[str]:
    """Tách câu sau . ! ? … (kể cả khi ngay sau đó là ngoặc kép/ngoặc đóng)."""
    out, start = [], 0
    for m in re.finditer(r"[.!?…]+[" + END + r"]*(?=\s+)", para):
        out.append(para[start:m.end()].strip())
        start = m.end()
    out.append(para[start:].strip())
    return [s for s in out if s]


def _split_long(s: str) -> list[str]:
    pieces = []
    while len(s) > MAX_CHUNK:
        cut = max(s.rfind(c, 0, MAX_CHUNK) for c in (", ", "; ", ": "))   # không cắt "3,5"
        if cut < MIN_CHUNK:
            cut = s.rfind(" ", 0, MAX_CHUNK)
            if cut < MIN_CHUNK:
                break
        pieces.append(s[:cut + 1].strip())
        s = s[cut + 1:].strip()
    return pieces + [s] if s else pieces


def _pause(chunk: str) -> float:
    tail = chunk.rstrip(END + " ")
    return PAUSE.get(tail[-1:], PAUSE_OTHER) if tail else PAUSE_OTHER


def chunks(text: str) -> list[tuple[str, float]]:
    """Cụm đọc + khoảng nghỉ sau cụm. Đoạn = dòng (truyện thường xuống dòng một lần giữa các đoạn)."""
    out = []
    for para in [p.strip() for p in clean(text).split("\n") if p.strip()]:
        if HEADING.match(para):
            out.append((para.rstrip(".") + ".", PAUSE_HEADING))
            continue
        pieces = [x for s in _sentences(para) for x in _split_long(s)]
        merged = []
        for s in pieces:                                   # câu ngắn → gộp với cụm trước trong cùng đoạn
            if merged and (len(s) < MIN_CHUNK or len(merged[-1]) < MIN_CHUNK) and len(merged[-1]) + len(s) < MAX_CHUNK:
                merged[-1] += " " + s
            else:
                merged.append(s)
        out += [(s, PAUSE_PARA if i == len(merged) - 1 else _pause(s)) for i, s in enumerate(merged)]
    return out


# ───────────────────────────── đọc ─────────────────────────────

def _say(job) -> str:
    """Đọc 1 cụm ra wav (chạy trong tiến trình con; mỗi tiến trình nạp model một lần)."""
    global _ENGINE
    sent, voice, wav = job
    if _ENGINE is None:
        from vieneu import Vieneu
        _ENGINE = Vieneu()
    tmp = wav + ".part.wav"
    _ENGINE.save(_ENGINE.infer(sent, voice=voice), tmp)
    os.replace(tmp, wav)
    return wav


def _trim_norm(a, target_rms: float = 0.08):
    """Cắt lặng thừa đầu/cuối (chừa 30 ms), đưa âm lượng về cùng mức để các cụm đều nhau."""
    import numpy as np
    idx = np.nonzero(np.abs(a) > 0.01)[0]
    if len(idx):
        pad = int(0.03 * SR)
        a = a[max(0, idx[0] - pad): idx[-1] + pad]
    rms = float(np.sqrt(np.mean(a ** 2))) if len(a) else 0.0
    return np.clip(a * min(target_rms / (rms + 1e-9), 4.0), -1, 1).astype("float32")


def vieneu(text: str, voice: str, mp3: pathlib.Path, srt: pathlib.Path, work: pathlib.Path,
           speed: float = 1.0, workers: int = 3) -> float:
    """Đọc từng cụm (có cache trong `work`), ghép, tăng tốc bằng atempo. Trả về thời lượng (giây).
    Cụm chưa có được đọc song song bằng `workers` tiến trình (mỗi tiến trình ~1,8 GB RAM)."""
    import numpy as np
    import soundfile as sf

    work.mkdir(parents=True, exist_ok=True)
    cs = chunks(text)
    if not cs:
        raise ValueError("không có chữ nào để đọc")
    wavs = [work / f"{i:04d}_{hashlib.sha1(f'{voice}|{c}'.encode()).hexdigest()[:10]}.wav"   # đổi cụm/giọng → tên đổi
            for i, (c, _) in enumerate(cs)]
    todo = [(c, voice, str(w)) for (c, _), w in zip(cs, wavs) if not w.exists()]
    if len(todo) >= 12 and workers > 1:                    # ít cụm thì nạp thêm model không đáng
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            list(ex.map(_say, todo, chunksize=2))
    else:
        for job in todo:
            _say(job)
    parts, cues, t = [], [], 0.0
    for (c, pause), wav in zip(cs, wavs):
        data, sr = sf.read(str(wav), dtype="float32")
        data = data if data.ndim == 1 else data.mean(axis=1)
        data = _trim_norm(data)
        dur = len(data) / sr
        parts += [data, np.zeros(int(sr * pause), dtype="float32")]
        cues.append((t / speed, (t + dur) / speed, c))
        t += dur + pause
    full = work / "full.wav"
    sf.write(str(full), np.concatenate(parts), sr)
    write_srt(srt, cues)
    mp3.parent.mkdir(parents=True, exist_ok=True)
    tmp = mp3.with_suffix(".part.mp3")  # ghi xong mới đổi tên: mp3 tồn tại nghĩa là bước giọng đã xong
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(full), "-af", f"atempo={speed},loudnorm=I=-16:TP=-1.5:LRA=11", "-c:a", "libmp3lame",
                    "-b:a", "160k", str(tmp)], check=True)
    tmp.replace(mp3)
    return t / speed


# ───────────────────────────── .srt ─────────────────────────────

def write_srt(path: pathlib.Path, cues: list[tuple[float, float, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(f"{n}\n{to_ts(a)} --> {to_ts(b)}\n{x}\n\n" for n, (a, b, x) in enumerate(cues, 1)),
                    encoding="utf-8")


def read_srt(path: pathlib.Path) -> list[tuple[float, float, str]]:
    cues = []
    for block in path.read_text(encoding="utf-8").strip().split("\n\n"):
        lines = block.splitlines()
        if len(lines) >= 3:
            a, b = (to_sec(x) for x in lines[1].split(" --> "))
            cues.append((a, b, " ".join(lines[2:])))
    return cues


def to_sec(ts: str) -> float:
    h, m, rest = ts.strip().replace(".", ",").split(":")
    s, ms = rest.split(",")
    return int(h) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000


def to_ts(x: float) -> str:
    ms = round(x * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
