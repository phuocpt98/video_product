"""Sân khấu rối cắt ghép: dựng video từ nền + nhân vật (đầu/thân rời) + kịch bản cảnh + giọng đọc. Không cần trình duyệt.

Mỗi khung hình ghép bằng Pillow rồi đưa thẳng vào ffmpeg. Nhép miệng theo độ to của audio, chớp mắt ngẫu nhiên,
nhún khi nói, rung khi sốc, máy quay zoom/lia có gia tốc, phụ đề. Một kịch bản xuất được 16:9 và 9:16.

python -m src.studio.stage <cảnh.yaml> [--size 1920x1080] [--out file.mp4]
"""
import argparse
import json
import math
import pathlib
import random
import subprocess

import numpy as np
import soundfile as sf
import yaml
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from src.studio.actions import ACTIONS, draw_effects
from src.studio.cutout import neck_top

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONT = ROOT / "assets/fonts/BeVietnamPro-ExtraBold.ttf"
FEET = 0.98            # chân nhân vật (thực ra mép dưới hình, ngang đùi) ở 98% chiều cao sân khấu
PROPS = ROOT / "assets/props"


def ease(t: float) -> float:
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


class Puppet:
    """Diễn viên chibi (assets/actors/<id>): ghép đầu (biểu cảm) lên thân (tư thế của bộ trang phục `outfit`), đầu KHÔNG
    cổ đặt TRƯỚC thân, cằm chồng lên cổ áo; có cache."""

    def __init__(self, char_dir: pathlib.Path, outfit: str | None = None):
        self.dir = char_dir
        self.card = yaml.safe_load((char_dir / "card.yaml").read_text(encoding="utf-8"))
        self.outfit = outfit or next(iter(self.card["outfits"]))
        self.card["bodies"] = self.card["outfits"][self.outfit]["bodies"]
        self._cache = {}
        self._props = None
        self.head_box = {}

    def _img(self, rel):
        return Image.open(self.dir / rel).convert("RGBA")

    def figure(self, pose: str, head: str, prop: str | None = None, head_rot: int = 0,
               head_dx: int = 0) -> tuple[Image.Image, tuple[int, int]]:
        """Ảnh nhân vật đã ghép + điểm chân (giữa mép dưới) để đặt lên sân khấu. `prop`: đạo cụ dán vào tay;
        head_rot/head_dx: xoay (độ) / dịch (px) riêng đầu cho gật, lắc. Khung đầu lưu ở self.head_box[key]."""
        pose = pose if pose in self.card["bodies"] else "relaxed"
        head = head if head in self.card["heads"] else "neutral"
        key = (pose, head, prop, head_rot, head_dx)
        self.last_key = key
        if key in self._cache:
            return self._cache[key]
        rig = self.card["rig"]
        h = self._img(self.card["heads"][head])
        s = rig["head_scale"]
        h = h.resize((int(h.width * s), int(h.height * s)), Image.LANCZOS)
        back = None
        if rig.get("hair_back"):                         # tóc dài dưới cằm: lớp riêng vẽ SAU thân (cùng khung với đầu)
            back = self._img(rig["hair_back"]).resize(h.size, Image.LANCZOS)
        if head_rot:
            h = h.rotate(head_rot, resample=Image.BICUBIC, center=(h.width // 2, h.height), expand=False)
            if back is not None:
                back = back.rotate(head_rot, resample=Image.BICUBIC, center=(back.width // 2, back.height), expand=False)
        body = self._img(self.card["bodies"][pose])
        bx, by = neck_top(body)
        bx += int(rig.get("neck_dx", {}).get(pose, 0) * body.width)          # chỉnh tay vị trí cổ theo tư thế
        hb = h.getchannel("A").getbbox()
        hx, hy = (hb[0] + hb[2]) // 2, hb[3] - int(rig.get("chin_up", 0) * h.height)   # giữa cằm (bỏ phần tóc dưới cằm)
        hx0 = bx - hx + head_dx + int(h.width * rig.get("head_dx", 0))        # head_dx < 0: dời đầu sang trái
        hy0 = by - hy + int(h.height * rig.get("overlap", 0.1))
        left, top = min(0, hx0), min(0, hy0)
        W = max(body.width, hx0 + h.width) - left
        H = max(body.height, hy0 + h.height) - top
        fig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        layers = ([(back, (hx0 - left, hy0 - top))] if back is not None else []) + \
            [(body, (-left, -top)), (h, (hx0 - left, hy0 - top))]
        for img, pos in layers:                               # tóc sau → thân → mặt + tóc trên (có chiều sâu)
            fig.alpha_composite(img, pos)
        foot = (fig.width // 2, fig.height)
        hbox = [hx0 - left, hy0 - top, h.width, h.height]
        if prop:
            fig, foot, shift = self._hold(fig, foot, body, (-left, -top), pose, prop, h.height)
            hbox[0] += shift[0]
            hbox[1] += shift[1]
        self.head_box[key] = tuple(hbox)
        self._cache[key] = (fig, foot)
        return self._cache[key]

    def _hold(self, fig, foot, body, at, pose, prop, head_h):
        """Dán đạo cụ (assets/props/<id>.png) lên tay: điểm cầm của đạo cụ trùng điểm tay của thân. Khớp tương đối."""
        if self._props is None:
            self._props = yaml.safe_load((PROPS / "props.yaml").read_text(encoding="utf-8"))
        spec = self._props[prop]
        img = Image.open(PROPS / spec["file"]).convert("RGBA")
        if spec.get("mirror"):                                              # lật ngang (vd. đầu lửa điếu thuốc ra trước)
            img = img.transpose(Image.FLIP_LEFT_RIGHT)
        k = spec.get("size", 0.5) * head_h / max(img.size)                  # cỡ theo chiều cao đầu
        img = img.resize((max(1, int(img.width * k)), max(1, int(img.height * k))), Image.LANCZOS)
        if spec.get("angle"):
            img = img.rotate(spec["angle"], expand=True, resample=Image.BICUBIC)
        hx, hy = hand_point(body, self.card["rig"].get("hands", {}).get(pose))
        gx, gy = spec.get("grip", [0.5, 0.5])
        px, py = at[0] + hx - int(gx * img.width), at[1] + hy - int(gy * img.height)
        left, top = min(0, px), min(0, py)
        W, H = max(fig.width, px + img.width) - left, max(fig.height, py + img.height) - top
        out = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        out.alpha_composite(fig, (-left, -top))
        out.alpha_composite(img, (px - left, py - top))
        return out, (foot[0] - left, foot[1] - top), (-left, -top)


def hand_point(body: Image.Image, override=None) -> tuple[int, int]:
    """Điểm tay cầm đồ của thân: chỉnh tay trong card (rig.hands.<pose> = [x, y] theo tỉ lệ) hoặc tự tìm là điểm
    xa trục thân nhất ở 70% trên (tay chỉ, tay giơ điện thoại; tay buông thì ra bàn tay bên phải)."""
    if override:
        return int(override[0] * body.width), int(override[1] * body.height)
    a = np.array(body.getchannel("A"))[: int(body.height * 0.7)] > 128
    ys, xs = np.nonzero(a)
    cx = np.nonzero(np.array(body.getchannel("A"))[int(body.height * 0.9)] > 128)[0].mean()   # trục = giữa hai chân
    far = xs.max() if xs.max() - cx >= cx - xs.min() else xs.min()
    near = abs(xs - far) < body.width * 0.04
    return int(xs[near].mean()), int(ys[near].mean())


def loudness(wav: pathlib.Path, fps: int) -> tuple[np.ndarray, float]:
    data, sr = sf.read(str(wav), dtype="float32")
    data = data if data.ndim == 1 else data.mean(axis=1)
    hop = int(sr / fps)
    n = len(data) // hop
    rms = np.sqrt(np.mean(data[: n * hop].reshape(n, hop) ** 2, axis=1))
    return rms / (rms.max() + 1e-9), len(data) / sr


def draw_sub(img: Image.Image, text: str, portrait: bool) -> None:
    if not text:
        return
    d = ImageDraw.Draw(img)
    W, H = img.size
    size = int(W * (0.05 if portrait else 0.03))
    f = ImageFont.truetype(str(FONT), size)
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= W * 0.86:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    y = H * (0.80 if portrait else 0.86) - len(lines) * size * 0.6
    for line in lines:
        x = (W - d.textlength(line, font=f)) / 2
        d.text((x, y), line, font=f, fill=(255, 255, 255), stroke_width=max(3, size // 10), stroke_fill=(20, 12, 6))
        y += size * 1.25


class Scene:
    """Chuẩn bị một lần (nền, diễn viên, âm lượng, lịch chớp mắt) rồi vẽ từng khung độc lập, nên chia được cho nhiều
    tiến trình vẽ song song."""

    def __init__(self, scene_file: pathlib.Path, size: str, fps: int):
        from src.contracts import require
        self.sc = require("storyboard", yaml.safe_load(scene_file.read_text(encoding="utf-8")), scene_file.name)
        self.W, self.H = map(int, size.split("x"))
        self.portrait = self.H > self.W
        self.base = scene_file.parent
        self.fps = fps
        self.stages = {}
        # ground: mặt đất trên nền (tỉ lệ chiều cao); feet_at: chân nằm ở đâu trong khung nhìn (1 = sát đáy).
        # Nhân vật nhỏ thì để feet_at ~0.8 cho phụ đề nằm dưới chân, không che người
        self.ground, self.feet_at = self.sc.get("ground", FEET), self.sc.get("feet_at", 1.0 + 0.01 * 1.25)
        self.audio = self.base / self.sc["audio"]
        self.level, self.dur = loudness(self.audio, fps)
        # cast: tên → {actor: <id>, outfit: <bộ đồ>} (diễn viên chibi trong assets/actors/)
        self.puppets = {k: Puppet(ROOT / "assets/actors" / v["actor"], v.get("outfit")) for k, v in self.sc["cast"].items()}
        self.shots = self.sc["shots"]
        rnd = random.Random(7)
        self.blinks = set()
        t = 1.0
        while t < self.dur:                                  # lịch chớp mắt: mỗi 2,5–5 giây, khoảng 0,1 giây
            f0 = int(t * fps)
            self.blinks.update(range(f0, f0 + max(1, fps // 10)))
            t += rnd.uniform(2.5, 5)
        self.frames = int(self.dur * fps)

    def stage(self, rel, extras: dict | None = None):
        """Nền phủ kín khung (cắt giữa), phóng to thêm để máy quay có chỗ lia. extras = quần chúng {n, seed, exclude}:
        diễn viên ngẫu nhiên (cố định theo seed) đứng phía sau, nhỏ và nhạt hơn, dán sẵn vào nền một lần."""
        key = (rel, json.dumps(extras, sort_keys=True) if extras else "")
        if key not in self.stages:
            if rel not in self.stages:
                bg = Image.open(self.base / rel).convert("RGBA")
                cover = max(self.W / bg.width, self.H / bg.height) * 1.25
                self.stages[rel] = bg.resize((int(bg.width * cover), int(bg.height * cover)), Image.LANCZOS)
            img = self.stages[rel]
            if extras and extras.get("n"):
                img = img.copy()
                SW, SH = img.size
                pool = sorted(p.parent.name for p in (ROOT / "assets/actors").glob("qc-*/card.yaml"))  # quần chúng
                if len(pool) < extras["n"]:              # chưa đủ thì lấy thêm diễn viên không có vai trong truyện
                    pool += sorted(p.parent.name for p in (ROOT / "assets/actors").glob("*/card.yaml")
                                   if p.parent.name not in set(extras.get("exclude", [])) and p.parent.name not in pool)
                rnd = random.Random(extras.get("seed", 0))
                n = min(extras["n"], len(pool))
                who = rnd.sample(pool, n)
                # chỉ đứng ở hai dải rìa (0,04–0,28 và 0,72–0,96), chừa giữa khung cho nhân vật chính
                side = [0.04 + 0.24 * (k + 0.5) / ((n + 1) // 2) for k in range((n + 1) // 2)]
                xs = [(x if k % 2 == 0 else 1 - x) + rnd.uniform(-0.02, 0.02)
                      for k, x in enumerate(sorted(side * 2)[:n])]
                for aid, x in zip(who, xs):
                    pup = Puppet(ROOT / "assets/actors" / aid)
                    fig, (fx, fy) = pup.figure(rnd.choice(["relaxed", "relaxed", "hips"]), "neutral")
                    k = 0.18 * (SH / 1.25) / fig.height         # nhỏ hơn nhân vật chính (0,3) để thấy lùi xa
                    fig = fig.resize((max(1, int(fig.width * k)), max(1, int(fig.height * k))), Image.BILINEAR)
                    if rnd.random() < 0.5:
                        fig = fig.transpose(Image.FLIP_LEFT_RIGHT)
                    a = fig.getchannel("A")
                    fig = Image.blend(fig.convert("RGB"), Image.new("RGB", fig.size, (235, 232, 225)), 0.3).convert("RGBA")
                    fig.putalpha(a)                       # nhạt hơn nhân vật chính
                    img.alpha_composite(fig, (int(x * SW - fig.width / 2), int((self.ground - 0.10) * SH - fig.height)))
            self.stages[key] = img
        return self.stages[key]

    def xpos(self, a: dict) -> float:
        """Vị trí ngang của nhân vật (0..1 bề rộng sân khấu). Khung dọc hẹp: dồn nhân vật về gần giữa để không ra mép."""
        x = a.get("x", 0.5)
        return 0.5 + (x - 0.5) * 0.3 if self.portrait else x

    def frame(self, fi: int) -> bytes:
        """Bước 1 (rẻ): tính mọi thứ quyết định khung hình thành một "chữ ký"; trùng khung trước thì trả lại ảnh cũ
        (cảnh người kể đứng yên, máy quay đã dừng). Bước 2: vẽ. Nhân vật đã co giãn được nhớ sẵn."""
        W, H, fps = self.W, self.H, self.fps
        t = fi / fps
        si, shot = next(((k, s) for k, s in enumerate(self.shots) if s["start"] <= t < s["end"]),
                        (len(self.shots) - 1, self.shots[-1]))
        dur = max(shot["end"] - shot["start"], 1e-3)
        ts = t - shot["start"]
        st = ts / dur                                        # tiến độ trong cảnh 0..1
        bg = shot.get("background", self.sc.get("background"))
        extras = shot.get("extras")
        SW, SH = self.stage(bg, extras).size
        plan, focus = [], []
        for a in shot.get("actors", []):
            pup = self.puppets[a["who"]]
            tf = ACTIONS.get(a.get("action", "idle"), ACTIONS["idle"])(st, ts, dur)
            talking = a.get("talk", False)
            head = tf.get("expr", a.get("expr", "neutral"))
            if talking and self.level[min(fi, len(self.level) - 1)] > 0.18 and f"{head}_talk" in pup.card["heads"]:
                head = f"{head}_talk"
            elif not talking and fi in self.blinks and head in ("neutral", "smirk"):
                head = "blink"
            pose = tf.get("pose", a.get("pose", "relaxed"))
            hr, hd = int(tf.get("head_rot", 0)), tf.get("head_dx", 0)
            fxs = tuple(a.get("fx", [])) + tuple(tf.get("fx", []))
            face_left = bool(a.get("flip")) != bool(tf.get("flip"))
            if tf.get("exit"):                           # rời cảnh: quay về mép gần nhất rồi đi ra (không băng qua khung)
                face_left = a.get("x", 0.5) < 0.5
            h_px = a.get("height", 0.72) * (SH / 1.25)
            ax = self.xpos(a)
            x = ax * SW + (-1 if face_left else 1) * tf.get("dx", 0) * h_px
            enter = a.get("enter") == "left" and st < 0.25
            y = self.ground * SH + tf.get("dy", 0) * h_px
            if talking:
                y -= abs(math.sin(t * 9)) * SH * 0.006          # nhún khi nói
            if a.get("shake") and st < 0.2:
                x += math.sin(t * 90) * SW * 0.006
            if tf.get("shake"):
                x += math.sin(t * 80) * h_px * tf["shake"] * 3
            rot = tf.get("rot", 0)
            if tf.get("fall") and rot:                  # ngã luôn đổ về phía giữa khung, không đổ ra mép
                falls_left = (rot > 0) != face_left
                if falls_left == (x < SW / 2):
                    rot = -rot
            plan.append((a["who"], pose, head, a.get("prop"), hr, round(hd, 3), fxs, round(ts, 2) if fxs else 0,
                         a.get("height", 0.72), round(rot, 1), face_left, int(x), int(y), enter,
                         round(st, 3) if enter else 0))
            focus.append(ax * SW)
        # máy quay bám nhân vật: zoom [từ, tới] có gia tốc trong ~1,2 giây đầu cảnh rồi ĐỨNG YÊN (khung sau trùng
        # khung trước thì dùng lại, rẻ hơn nhiều); tâm ngang = trung bình nhân vật (+ pan)
        cam = shot.get("cam", {})
        z0, z1 = cam.get("zoom", [1.0, 1.08])
        z = z0 + (z1 - z0) * ease(ts / min(1.2, dur * 0.6))
        vh = SH / 1.25 / z
        vw = vh * W / H
        vw, vh = min(vw, SW), min(vh, SH)
        cx = (sum(focus) / len(focus) if focus else SW / 2) + cam.get("pan", 0) * SW
        screen = tuple(shot.get("screen", []))
        if "shake" in screen:
            cx += math.sin(t * 70) * vw * 0.01 * max(0.0, 1 - ts / 0.6)
        left = min(max(cx - vw / 2, 0), SW - vw)
        top = min(max(self.ground * SH - vh * self.feet_at, 0), SH - vh)
        sub = next((s["text"] for s in self.sc.get("subs", []) if s["start"] <= t < s["end"]), "")
        timed = any(k in screen for k in ("flash", "fade_in", "fade_out", "shake")) or \
            t >= (self.sc.get("overlay") or {}).get("cta_from", 1e9)
        sig = (si, bg, json.dumps(extras, sort_keys=True) if extras else "", tuple(plan), int(left), int(top), int(vw), sub, screen, round(ts, 2) if timed else 0)
        if sig == getattr(self, "_sig", None):
            return self._bytes

        frame = self.stage(bg, extras).copy()                 # mỗi cảnh có thể đổi nền (+ quần chúng dán sẵn)
        for (who, pose, head, prop, hr, hd, fxs, _, height, rot, face_left, x, y, enter, _st) in plan:
            pup = self.puppets[who]
            base_h = pup.figure(pose, head)[0].height          # chiều cao người (không tính đạo cụ) để chia tỉ lệ
            scale = height * (SH / 1.25) / base_h
            fig, (fx, fy) = pup.figure(pose, head, prop, hr, 0)
            if hd:                                           # lắc đầu: dịch đầu theo tỉ lệ chiều cao đầu (làm tròn 4 px)
                hb0 = pup.head_box[pup.last_key]
                fig, (fx, fy) = pup.figure(pose, head, prop, hr, int(hd * hb0[3]) // 4 * 4)
            key = (who, pup.last_key, round(scale, 4))
            if fxs:
                fig = draw_effects(fig, pup.head_box[pup.last_key], list(fxs), ts)
                fig = fig.resize((max(1, int(fig.width * scale)), max(1, int(fig.height * scale))), Image.BILINEAR)
            else:
                cache = self.__dict__.setdefault("_scaled", {})
                if key not in cache:
                    if len(cache) > 300:
                        cache.clear()
                    cache[key] = fig.resize((max(1, int(fig.width * scale)), max(1, int(fig.height * scale))),
                                            Image.BILINEAR)
                fig = cache[key]
            fx, fy = int(fx * scale), int(fy * scale)
            if rot:                                          # xoay quanh chân; ngả ra sau = ngược hướng mặt
                side = 2 * max(fig.width, fig.height) + 4
                pad = Image.new("RGBA", (side, side), (0, 0, 0, 0))
                c = side // 2
                pad.alpha_composite(fig, (c - fx, c - fy))
                fig = pad.rotate(rot, resample=Image.BILINEAR)   # xoay quanh tâm = điểm chân
                fx, fy = c, c
            if face_left:
                fig = fig.transpose(Image.FLIP_LEFT_RIGHT)
                fx = fig.width - fx
            if enter:
                x = int(-fig.width + (x + fig.width) * ease(_st / 0.25))
            frame.alpha_composite(fig, (int(x - fx), int(y - fy)))
        view = frame.crop((int(left), int(top), int(left + vw), int(top + vh))).resize((W, H), Image.BILINEAR)
        view = screen_fx(view.convert("RGB"), list(screen), ts, dur)
        draw_sub(view, sub, self.portrait)
        ov = self.sc.get("overlay")
        if ov:                                               # chữ lớn cho clip mồi (TikTok): tiêu đề trên, kêu gọi ở cuối
            draw_banner(view, ov.get("top", ""), 0.07)
            if ov.get("cta") and t >= ov.get("cta_from", 1e9):
                draw_banner(view, ov["cta"], 0.22, color=(255, 255, 255))   # ngay dưới tiêu đề, trên đầu nhân vật
        self._sig, self._bytes = sig, view.tobytes()
        return self._bytes


def draw_banner(img: Image.Image, text: str, y_frac: float, color=(255, 214, 0)) -> None:
    """Chữ to viền đen dày (kiểu tiêu đề TikTok), tự xuống dòng, căn giữa ở độ cao y_frac."""
    if not text:
        return
    d = ImageDraw.Draw(img)
    W, H = img.size
    size = int(W * 0.075)
    f = ImageFont.truetype(str(FONT), size)
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if d.textlength(t, font=f) <= W * 0.9:
            cur = t
        else:
            lines.append(cur)
            cur = w
    lines.append(cur)
    y = H * y_frac
    for line in lines:
        d.text(((W - d.textlength(line, font=f)) / 2, y), line, font=f, fill=color, stroke_width=max(4, size // 8),
               stroke_fill=(0, 0, 0))
        y += size * 1.2


def screen_fx(img: Image.Image, names, ts: float, dur: float) -> Image.Image:
    if "sepia" in names:                                     # hồi tưởng
        g = img.convert("L")
        img = Image.merge("RGB", (g.point(lambda v: min(255, int(v * 1.07 + 20))), g.point(lambda v: int(v * 0.95 + 8)),
                                  g.point(lambda v: int(v * 0.75))))
    k = 0.0
    if "black" in names:
        k = 1.0
    if "fade_in" in names:
        k = max(k, 1 - ts / 0.6)
    if "fade_out" in names:
        k = max(k, 1 - (dur - ts) / 0.6)
    if k > 0:
        img = Image.blend(img, Image.new("RGB", img.size, (0, 0, 0)), min(k, 1.0))
    if "flash" in names and ts < 0.35:
        img = Image.blend(img, Image.new("RGB", img.size, (255, 255, 255)), 1 - ts / 0.35)
    return img


def _render_part(job) -> str:
    scene_file, size, fps, f0, f1, out, out_fps = job
    import os
    os.nice(10)                                          # ưu tiên thấp: máy vẫn mượt khi đang dựng
    sc = Scene(pathlib.Path(scene_file), size, fps)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{sc.W}x{sc.H}",
                            "-r", str(fps), "-i", "-", "-r", str(out_fps), "-c:v", "h264_videotoolbox", "-b:v", "4M",
                            "-pix_fmt", "yuv420p", out], stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        enc.stdin.write(sc.frame(fi))
    enc.stdin.close()
    if enc.wait():
        raise RuntimeError("ffmpeg lỗi")
    return out


def render(scene_file: pathlib.Path, size: str, out: pathlib.Path, fps: int = 24, workers: int = 0,
           draw_fps: int = 12) -> None:
    """Vẽ song song: chia các khung thành từng đoạn cho nhiều tiến trình, mỗi đoạn ra một file hình (không tiếng),
    rồi nối lại và ghép giọng đọc ở tốc độ gốc. Hình và tiếng tách rời nên vẽ nhanh hay chậm không ảnh hưởng tiếng."""
    import os
    import tempfile
    from concurrent.futures import ProcessPoolExecutor
    # "quay đôi": vẽ draw_fps hình/giây (12), mỗi hình phát 2 lần → video fps (24) như hoạt hình truyền thống
    head = Scene(scene_file, size, draw_fps)
    n = workers or max(1, (os.cpu_count() or 2) - 3)
    chunk = max(draw_fps * 5, -(-head.frames // n))
    with tempfile.TemporaryDirectory() as tmp:
        jobs = [(str(scene_file), size, draw_fps, f0, min(f0 + chunk, head.frames), f"{tmp}/part_{i:04d}.mp4", fps)
                for i, f0 in enumerate(range(0, head.frames, chunk))]
        with ProcessPoolExecutor(max_workers=n) as ex:
            parts = list(ex.map(_render_part, jobs))
        lst = pathlib.Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        out.parent.mkdir(parents=True, exist_ok=True)
        r = subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst), "-i",
                            str(head.audio), "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                            "-shortest", "-movflags", "+faststart", str(out)])
        if r.returncode:
            raise RuntimeError("ffmpeg nối đoạn lỗi")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("scene")
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--out")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--draw-fps", type=int, default=12, help="số hình vẽ thật mỗi giây (12 = quay đôi, 8 = quay ba)")
    a = ap.parse_args()
    scene = pathlib.Path(a.scene)
    out = pathlib.Path(a.out or scene.with_name(f"{scene.stem}_{a.size}.mp4"))
    render(scene, a.size, out, a.fps, draw_fps=a.draw_fps)
    print("Xong:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
