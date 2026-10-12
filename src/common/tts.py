"""Giọng đọc VieNeu-TTS (chạy local, Apache-2.0) + phụ đề .srt theo từng câu."""
import hashlib
import os
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))  # model AI nằm trong dự án

_ENGINE = None


def sentences(text: str) -> list[str]:
    return [x.strip() for p in text.split("\n\n") for x in re.split(r"(?<=[.!?…])\s+", p) if x.strip()]


def _say(job) -> str:
    """Đọc 1 câu ra wav (chạy trong tiến trình con; mỗi tiến trình nạp model một lần)."""
    global _ENGINE
    sent, voice, wav = job
    if _ENGINE is None:
        from vieneu import Vieneu
        _ENGINE = Vieneu()
    tmp = wav + ".part.wav"
    _ENGINE.save(_ENGINE.infer(sent, voice=voice), tmp)
    os.replace(tmp, wav)
    return wav


def vieneu(text: str, voice: str, mp3: pathlib.Path, srt: pathlib.Path, work: pathlib.Path,
           speed: float = 1.0, gap: float = 0.05, workers: int = 3) -> float:
    """Đọc từng câu (có cache trong `work`), ghép, tăng tốc bằng atempo. Trả về thời lượng (giây).
    Câu chưa có được đọc song song bằng `workers` tiến trình (mỗi tiến trình ~1,8 GB RAM)."""
    import numpy as np
    import soundfile as sf

    work.mkdir(parents=True, exist_ok=True)
    sents = sentences(text)
    wavs = [work / f"{i:04d}_{hashlib.sha1(f'{voice}|{s}'.encode()).hexdigest()[:10]}.wav"  # đổi câu/giọng → tên đổi
            for i, s in enumerate(sents)]
    todo = [(s, voice, str(w)) for s, w in zip(sents, wavs) if not w.exists()]
    if len(todo) >= 12 and workers > 1:                # ít câu thì nạp thêm model không đáng
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=workers) as ex:
            list(ex.map(_say, todo, chunksize=2))
    else:
        for job in todo:
            _say(job)
    sr, chunks, cues, t = 48000, [], [], 0.0
    for sent, wav in zip(sents, wavs):
        data, sr = sf.read(str(wav), dtype="float32")
        data = data if data.ndim == 1 else data.mean(axis=1)
        chunks += [data, np.zeros(int(sr * gap), dtype="float32")]
        dur = len(data) / sr
        cues.append((t / speed, (t + dur) / speed, sent))
        t += dur + gap
    full = work / "full.wav"
    sf.write(str(full), np.concatenate(chunks), sr)
    write_srt(srt, cues)
    mp3.parent.mkdir(parents=True, exist_ok=True)
    tmp = mp3.with_suffix(".part.mp3")  # ghi xong mới đổi tên: mp3 tồn tại nghĩa là bước giọng đã xong
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(full), "-af", f"atempo={speed}", "-c:a", "libmp3lame",
                    "-b:a", "160k", str(tmp)], check=True)
    tmp.replace(mp3)
    return t / speed


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
