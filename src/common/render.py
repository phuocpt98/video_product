"""Dựng video: khung tĩnh có linh vật (tạm, chưa có thư viện clip lặp) + audio + phụ đề mềm."""
import pathlib
import subprocess

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from src.common.tts import read_srt, write_srt

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONT = ROOT / "assets/fonts"


def make_frame(title: str, subtitle: str, mascot: pathlib.Path, out: pathlib.Path) -> None:
    W, H = 1920, 1080
    bg = Image.new("RGB", (W, H), (242, 155, 54))
    glow = Image.new("L", (W, H), 0)
    ImageDraw.Draw(glow).ellipse((300, 150, 1600, 950), fill=90)
    bg = Image.composite(Image.new("RGB", (W, H), (250, 178, 82)), bg, glow.filter(ImageFilter.GaussianBlur(200)))
    m = Image.open(mascot).convert("RGB").resize((720, 720), Image.LANCZOS)
    mask = Image.new("L", (720, 720), 0)
    ImageDraw.Draw(mask).ellipse((25, 25, 695, 695), fill=255)
    bg.paste(m, (120, 180), mask.filter(ImageFilter.GaussianBlur(18)))
    d = ImageDraw.Draw(bg)
    f1 = ImageFont.truetype(str(FONT / "BeVietnamPro-ExtraBold.ttf"), 76)
    f2 = ImageFont.truetype(str(FONT / "BeVietnamPro-SemiBold.ttf"), 44)
    y = 380
    for line in _wrap(d, title, f1, 980):
        d.text((900, y), line, font=f1, fill=(59, 35, 20))
        y += 96
    d.text((904, y + 20), subtitle, font=f2, fill=(74, 42, 18))
    out.parent.mkdir(parents=True, exist_ok=True)
    bg.save(out)


def _wrap(d, text, font, width):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=font) <= width:
            cur = t
        else:
            lines.append(cur)
            cur = w
    return lines + [cur] if cur else lines


def duration(path: pathlib.Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout.strip()
    return float(out)


def join_audio(parts: list[tuple[pathlib.Path, pathlib.Path]], mp3: pathlib.Path, srt: pathlib.Path,
               chapter_gap: float = 0.8) -> list[tuple[float, str]]:
    """Ghép (mp3, srt) của nhiều chương; trả về mốc bắt đầu từng chương (cho chapter YouTube)."""
    work = mp3.parent / f"{mp3.stem}_join"
    work.mkdir(parents=True, exist_ok=True)
    silence = work / "gap.mp3"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=mono", "-t",
                    str(chapter_gap), "-c:a", "libmp3lame", "-b:a", "64k", str(silence)], check=True)
    lst, cues, marks, offset = [], [], [], 0.0
    for a, s in parts:
        marks.append((offset, a.stem))
        lst += [f"file '{a.resolve()}'", f"file '{silence.resolve()}'"]
        cues += [(x + offset, y + offset, t) for x, y, t in read_srt(s)]
        offset += duration(a) + chapter_gap
    (work / "list.txt").write_text("\n".join(lst) + "\n", encoding="utf-8")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(work / "list.txt"),
                    "-c:a", "libmp3lame", "-b:a", "160k", str(mp3)], check=True)
    write_srt(srt, cues)
    return marks


def video(frame: pathlib.Path, mp3: pathlib.Path, srt: pathlib.Path, mp4: pathlib.Path) -> float:
    mp4.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "2", "-i", str(frame), "-i", str(mp3),
                    "-i", str(srt), "-map", "0:v", "-map", "1:a", "-map", "2:s", "-c:v", "h264_videotoolbox",
                    "-b:v", "1500k", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "160k",
                    "-c:s", "mov_text", "-metadata:s:s:0", "language=vie", "-shortest", str(mp4)], check=True)
    return duration(mp4)
