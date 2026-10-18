"""Hoạt hình nền NGẪU NHIÊN cho video kể truyện: không khớp truyện, chỉ để giữ mắt. Chạy không cần màn hình.

Đạo diễn ngẫu nhiên (plan) chia video thành HỒI (~1 phút: 1 nền + 1–3 diễn viên + tông màu) và NHỊP (5–9 giây: 1 vi
kịch bản + 1 góc máy). Lõi vẽ pygame (SDL dummy, không mở cửa sổ) vẽ từng khung rồi đẩy thẳng vào ffmpeg; nhiều tiến
trình vẽ song song từng đoạn rồi nối lại và ghép giọng đọc. Nhân vật nhép miệng theo độ to giọng đọc.
Kho tự quét: assets/actors/*/card.yaml (diễn viên), assets/scenes/*/card.yaml (nền). Thêm vào kho là tự vào vòng random.

python -m src.studio.reel --audio stories/<slug>/audio/001.mp3 --out tmp/reel/001.mp4 [--seed 7] [--size 1920x1080]
python -m src.studio.reel --seconds 90 --out tmp/reel/demo.mp4          # không giọng: video câm để xem thử
"""
import argparse
import json
import math
import os
import pathlib
import random
import shutil
import subprocess
import sys
import tempfile
import time

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

import numpy as np  # noqa: E402
import yaml  # noqa: E402

ROOT = pathlib.Path(__file__).resolve().parents[2]
FONT = ROOT / "assets/fonts/BeVietnamPro-ExtraBold.ttf"
SKIP_SCENES = {"sky-day", "sky-night"}          # nền không có mặt đất
# Diễn viên HỎNG (không dùng): asset bị lỗi, render ra nhân vật không đầu/khuyết thân.
# - uyen-thanh (2026-10-18): head_*.png chỉ là mảnh vụn (không phải đầu), body f-wedding-dress
#   thiếu thân trên — do new_actor.py cắt sai từ source. validate_actor báo CHƯA ĐẠT.
SKIP_ACTORS = {"uyen-thanh"}
HEADS = ("neutral", "smirk", "shocked", "angry", "sad")
THEMES = [(255, 196, 0), (255, 92, 120), (64, 196, 255), (120, 220, 90), (190, 120, 255)]   # màu dải chuyển hồi
TINTS = {"day": None, "sunset": (255, 205, 160), "night": (120, 140, 210)}


# ───────────────────────────── ĐẠO DIỄN NGẪU NHIÊN ─────────────────────────────
# Mỗi vi kịch bản: số diễn viên tối thiểu, góc máy cho phép (wide/medium/close).
BEATS = {
    "chat": (2, ("wide", "medium", "medium", "close")),
    "chase": (2, ("wide",)),
    "dance": (1, ("wide", "wide", "medium")),
    "jump_joy": (1, ("wide", "medium")),
    "surprise": (2, ("wide",)),
    "angry": (1, ("wide", "medium", "close")),
    "sad": (1, ("medium", "close")),
    "lightning": (1, ("wide",)),
    "slip": (1, ("wide", "medium")),
    "spin": (1, ("wide", "medium")),
    "phone": (1, ("medium", "close")),
    "laugh_at": (2, ("wide", "medium")),
    "parade": (1, ("wide",)),
    "wave": (2, ("wide",)),
    "sleep": (1, ("medium", "close")),
    "love": (2, ("wide", "medium")),
    "pop_in": (1, ("wide",)),
}


def library() -> tuple[list[str], list[str]]:
    actors = sorted(p.parent.name for p in (ROOT / "assets/actors").glob("*/card.yaml")
                    if p.parent.name not in SKIP_ACTORS)
    scenes = sorted(p.parent.name for p in (ROOT / "assets/scenes").glob("*/card.yaml")
                    if p.parent.name not in SKIP_SCENES)
    return actors, scenes


class Deck:
    """Bốc không hoàn lại (hết thì xáo lại), không lặp món trong `gap` lần bốc gần nhất."""

    def __init__(self, items, rnd, gap):
        self.items, self.rnd, self.gap, self.pile, self.recent = list(items), rnd, gap, [], []

    def draw(self, ok=lambda x: True):
        for _ in range(3):
            if not self.pile:
                self.pile = self.items[:]
                self.rnd.shuffle(self.pile)
            for i, x in enumerate(self.pile):
                if ok(x) and x not in self.recent[-self.gap:]:
                    self.recent.append(self.pile.pop(i))
                    return x
            self.pile = []
        x = self.rnd.choice([x for x in self.items if ok(x)])
        self.recent.append(x)
        return x


def make_plan(duration: float, seed: int, act_len: float = 60.0) -> dict:
    rnd = random.Random(seed)
    actors, scenes = library()
    a_deck, s_deck = Deck(actors, rnd, min(8, len(actors) // 2)), Deck(scenes, rnd, min(10, len(scenes) // 2))
    b_deck = Deck(list(BEATS), rnd, 4)
    acts, t = [], 0.0
    n_acts = max(1, round(duration / act_len))
    for ai in range(n_acts):
        end = duration if ai == n_acts - 1 else t + duration / n_acts
        n = rnd.choice([2, 3]) if len(actors) >= 3 else len(actors)   # 1 người diễn cả hồi thì đơn điệu
        cast = []
        while len(cast) < n:
            a = a_deck.draw(lambda x: x not in cast)
            outfits = list(yaml.safe_load((ROOT / "assets/actors" / a / "card.yaml").read_text(encoding="utf-8"))
                           .get("outfits", {}) or {"": None})
            cast.append({"actor": a, "outfit": rnd.choice(outfits) or None})
        scene = s_deck.draw()
        tint = "day" if "night" in scene else rnd.choices(list(TINTS), [0.7, 0.15, 0.15])[0]
        beats, bt = [], t
        while bt < end - 0.01:
            d = rnd.uniform(5.0, 9.0)
            if end - (bt + d) < 4.0:                       # đoạn thừa ngắn thì gộp vào nhịp cuối
                d = end - bt
            kind = b_deck.draw(lambda k: BEATS[k][0] <= n)
            shot = rnd.choice(BEATS[kind][1])
            beats.append({"start": round(bt, 3), "end": round(bt + d, 3), "kind": kind,
                          "seed": rnd.randrange(1 << 30), "shot": shot,
                          "subject": rnd.randrange(n),
                          "move": rnd.choice(["push", "push", "pull", "pan", "still"]),
                          "punch": rnd.random() < 0.3})
            bt += d
        acts.append({"start": round(t, 3), "end": round(end, 3), "scene": scene, "tint": tint, "cast": cast,
                     "x0": rnd.uniform(-0.12, 0.12), "theme": rnd.randrange(len(THEMES)), "beats": beats})
        t = end
    return {"seed": seed, "duration": duration, "acts": acts}


# ───────────────────────────── VI KỊCH BẢN ─────────────────────────────
# Mỗi hàm (b, t, dur, n, R) → (states, fx, scr). t = giây trong nhịp, R = Random riêng của nhịp (gọi trong hàm phải
# cho cùng kết quả ở mọi khung: chỉ dùng R ở đầu hàm với số lần gọi cố định).
# state của diễn viên: xr (lệch khỏi chỗ đứng, đơn vị = chiều cao người), dy (âm = lên), rot (độ), sx/sy (co giãn),
# face (+1 phải / -1 trái / 0 = mặc định), expr, pose, talk, sil (cháy đen), hide.
# fx: (loại, chỉ số diễn viên, tham số). scr: dark/flash (0..1), shake (0..1).

def ease(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def hop(t, f=2.5, a=0.06):
    return -abs(math.sin(t * f * math.pi)) * a


def _base(n, **kw):
    return [dict(kw) for _ in range(n)]


def b_chat(b, t, dur, n, R):
    turn = R.uniform(1.8, 3.0)
    react = R.choice(["shocked", "angry", "smirk", "sad"])
    mark = {"shocked": "!", "angry": "anger", "smirk": "sparkle", "sad": "sweat"}[react]
    tr = R.uniform(0.45, 0.7) * dur
    sp = int(t / turn) % 2
    st = _base(n, expr="neutral")
    for i in range(n):
        st[i]["face"] = 1 if i == 0 else -1
    st[sp]["talk"] = True
    st[sp]["expr"] = "smirk" if sp == 0 else "neutral"
    st[sp]["dy"] = hop(t, 1.2, 0.015)
    fx = []
    if n > 1 and t > tr:
        o = 1 - sp
        st[o]["expr"] = react
        st[o]["dy"] = -0.08 * max(0, 1 - (t - tr) / 0.3)
        fx.append((mark, o, t - tr))
    if n > 2:
        st[2]["face"] = -1 if sp == 0 else 1
    return st, fx, {}


def b_chase(b, t, dur, n, R):
    span = b["span"]
    st = _base(n, expr="neutral")
    half = dur / 2
    k = (t % half) / half
    dir_ = 1 if t < half else -1
    x = (-span + 2 * span * k) * dir_
    st[0].update(xa=x, dy=hop(t, 3.2, 0.1), rot=-10 * dir_, face=dir_, expr="shocked" if dir_ > 0 else "angry")
    st[1].update(xa=x - 0.9 * dir_, dy=hop(t + 0.15, 3.2, 0.1), rot=-10 * dir_, face=dir_,
                 expr="angry" if dir_ > 0 else "shocked")
    fx = [("dust", 0, t), ("dust", 1, t), ("speed", 0, dir_), ("speed", 1, dir_)]
    fx.append(("sweat", 0 if dir_ > 0 else 1, t))
    fx.append(("anger", 1 if dir_ > 0 else 0, t))
    for i in range(2, n):
        st[i].update(expr="shocked", face=1 if x > 0 else -1, dy=hop(t, 0.8, 0.02))
    return st, fx, {}


def b_dance(b, t, dur, n, R):
    bpm = R.uniform(1.8, 2.4)
    st = []
    for i in range(n):
        ph = i * 0.25
        st.append({"dy": hop(t + ph, bpm, 0.08), "rot": 10 * math.sin((t + ph) * bpm * math.pi),
                   "face": 1 if int((t + ph) * bpm) % 2 else -1, "expr": "smirk",
                   "pose": "point" if int((t + ph) * bpm / 2) % 2 else "hips"})
    return st, [("notes", i, t) for i in range(n)], {}


def b_jump_joy(b, t, dur, n, R):
    st = []
    for i in range(n):
        ph = (t * 1.6 + i * 0.33) % 1.0
        dy = -0.35 * math.sin(ph * math.pi) if ph < 0.75 else 0
        squash = 0.12 * math.sin((ph - 0.75) / 0.25 * math.pi) if ph >= 0.75 else 0
        st.append({"dy": dy * (0.75 / 0.75), "sx": 1 + squash, "sy": 1 - squash, "expr": "smirk",
                   "rot": 8 * math.sin(ph * 2 * math.pi)})
    return st, [("stars", i, t) for i in range(n)], {}


def b_surprise(b, t, dur, n, R):
    k = n - 1
    arrive = 1.6
    st = _base(n, expr="neutral")
    p = min(t / arrive, 1)
    st[k].update(xr=3.0 * (1 - ease(p)), dy=hop(t, 3, 0.05) if p < 1 else 0, face=-1, expr="smirk")
    fx = []
    if t >= arrive:
        q = t - arrive
        for i in range(k):
            st[i].update(expr="shocked", dy=-0.2 * max(0, math.sin(min(q / 0.35, 1) * math.pi)),
                         face=1, rot=-12 * max(0, 1 - q / 0.5))
            fx.append(("!", i, q))
            if q > 1.0:
                fx.append(("sweat", i, q - 1.0))
        st[k]["talk"] = True
    return st, fx, {"shake": 0.6 * max(0, 1 - abs(t - arrive) / 0.3)}


def b_angry(b, t, dur, n, R):
    st = _base(n, expr="sad")
    stomp = abs(math.sin(t * 5))
    st[0].update(expr="angry", sy=1 - 0.05 * stomp, sx=1 + 0.03 * stomp, talk=True, face=1, pose="point")
    fx = [("anger", 0, t), ("steam", 0, t)]
    for i in range(1, n):
        st[i].update(xr=0.5 * ease(t / dur), face=1 if t > dur * 0.6 else -1, dy=hop(t, 4, 0.01))
        fx.append(("sweat", i, t))
    return st, fx, {"shake": 0.15 * stomp}


def b_sad(b, t, dur, n, R):
    st = _base(n, expr="neutral")
    st[0].update(expr="sad", sy=0.95, rot=4 * math.sin(t * 1.2))
    fx = [("rain", 0, t), ("gloom", 0, t)]
    for i in range(1, n):
        p = ease(t / (dur * 0.6))
        st[i].update(xr=-0.35 * p * (1 if i == 1 else -1), expr="sad", face=-1 if i == 1 else 1, pose="hips")
    return st, fx, {"dark": 0.25}


def b_lightning(b, t, dur, n, R):
    victim = R.randrange(n)
    strike = R.uniform(1.6, 2.4)
    st = _base(n, expr="neutral")
    fx = []
    scr = {"dark": 0.55 * ease(t / 1.2)}
    if t < strike:                                        # mây đen kéo tới, mọi người ngước nhìn, run
        for i in range(n):
            st[i].update(expr="shocked" if t > 0.8 else "neutral", dy=hop(t, 6, 0.008 * (t > 0.8)))
        fx.append(("cloud", None, t))
    else:
        q = t - strike
        fx.append(("cloud", None, t))
        if q < 0.3:
            fx.append(("bolt", victim, q))
        scr["flash"] = max(0, 1 - q / 0.35)
        scr["shake"] = max(0, 1 - q / 0.5)
        st[victim].update(sil=True, dy=-0.05 * max(0, math.sin(min(q / 0.2, 1) * math.pi)),
                          sx=1 + 0.06 * math.sin(q * 30) * max(0, 1 - q / 0.6))
        fx.append(("smoke", victim, q))
        if q > 1.2:
            st[victim]["rot"] = -90 * ease((q - 1.2) / 0.35) if q > 2.4 else 0
        for i in range(n):
            if i != victim:
                st[i].update(expr="shocked", dy=-0.18 * max(0, math.sin(min(q / 0.35, 1) * math.pi)),
                             face=1 if i < victim else -1)
                fx.append(("!", i, q))
    return st, fx, scr


def b_slip(b, t, dur, n, R):
    who = b["subject"]
    t0 = R.uniform(0.8, 1.4)
    up = R.uniform(3.2, 4.2)
    st = _base(n, expr="neutral")
    fx = []
    if t < t0:
        st[who].update(xr=-0.4 + 0.4 * t / t0, dy=hop(t, 3, 0.04), face=1)
    elif t < up:
        q = t - t0
        st[who].update(rot=88 * ease(q / 0.25), expr="shocked", dy=-0.08 * math.sin(min(q / 0.25, 1) * math.pi))
        fx.append(("dizzy", who, q))
        for i in range(n):
            if i != who:
                st[i].update(expr="smirk", talk=True, dy=hop(t, 4, 0.03), face=1 if i < who else -1)
    else:
        q = t - up
        st[who].update(rot=88 * (1 - ease(q / 0.4)) + 6 * math.sin(q * 6), expr="sad")
        fx.append(("dizzy", who, q + 5))
    return st, fx, {"shake": 0.5 * max(0, 1 - abs(t - t0 - 0.25) / 0.2)}


def b_spin(b, t, dur, n, R):
    who = b["subject"]
    st = _base(n, expr="neutral")
    spin_end = dur * 0.6
    if t < spin_end:
        ang = (t / spin_end) ** 1.6 * 8 * math.pi        # nhanh dần
        c = math.cos(ang)
        st[who].update(sx=max(0.08, abs(c)), face=1 if c >= 0 else -1, expr="smirk", dy=hop(t, 2, 0.03))
        fx = [("whirl", who, t)]
    else:
        q = t - spin_end
        st[who].update(rot=10 * math.sin(q * 5) * max(0, 1 - q / 2), expr="shocked")
        fx = [("dizzy", who, q)]
    for i in range(n):
        if i != who:
            st[i].update(expr="shocked" if t > spin_end else "neutral")
    return st, fx, {}


def b_phone(b, t, dur, n, R):
    who = b["subject"]
    mid = R.uniform(0.4, 0.6) * dur
    st = _base(n, expr="neutral")
    if t < mid:
        st[who].update(pose="phone", expr="neutral", rot=3 * math.sin(t * 2))
        fx = [("?", who, t)]
    else:
        q = t - mid
        st[who].update(pose="phone", expr="shocked", dy=-0.22 * max(0, math.sin(min(q / 0.35, 1) * math.pi)))
        fx = [("!", who, q), ("sweat", who, q)]
    for i in range(n):
        if i != who:
            st[i]["face"] = 1 if i < who else -1
    return st, fx, {"shake": 0.4 * max(0, 1 - abs(t - mid) / 0.25)}


def b_laugh_at(b, t, dur, n, R):
    st = _base(n, expr="neutral")
    st[0].update(pose="point", expr="smirk", talk=True, dy=hop(t, 3.5, 0.04), rot=-6 * abs(math.sin(t * 7)), face=1)
    st[1].update(expr="angry", face=-1, sx=1 + 0.04 * math.sin(t * 20) * (t > dur * 0.5))
    fx = [("haha", 0, t)] + ([("anger", 1, t)] if t > dur * 0.4 else [("sweat", 1, t)])
    for i in range(2, n):
        st[i].update(expr="smirk", dy=hop(t + 0.3, 3.5, 0.03))
    return st, fx, {}


def b_parade(b, t, dur, n, R):
    span = b["span"] + 0.75 * (n - 1)
    x = -span + 2 * span * t / dur
    st = []
    for i in range(n):
        st.append({"xa": x - i * 0.75, "dy": hop(t + i * 0.2, 2.6, 0.06), "rot": 5 * math.sin(t * 8 + i), "face": 1,
                   "expr": "smirk" if i == 0 else "neutral", "talk": i == 0})
    return st, [("dust", i, t) for i in range(n)] + [("notes", 0, t)], {}


def b_wave(b, t, dur, n, R):
    st = []
    for i in range(n):
        ph = t * 1.3 - i * 0.18
        up = max(0.0, math.sin(ph * 2 * math.pi))
        st.append({"dy": -0.18 * up, "sy": 1 + 0.06 * up, "sx": 1 - 0.04 * up, "expr": "smirk" if up > 0.5 else "neutral",
                   "pose": "point" if up > 0.6 else "relaxed"})
    return st, [("sparkle", i, t) for i in range(n)], {}


def b_sleep(b, t, dur, n, R):
    who = b["subject"]
    st = _base(n, expr="neutral")
    wake = R.uniform(0.6, 0.8) * dur
    if t < wake:
        st[who].update(expr="blink", rot=6 * math.sin(t * 1.4), sy=1 + 0.02 * math.sin(t * 2.5))
        fx = [("zzz", who, t)]
    else:
        q = t - wake
        st[who].update(expr="shocked", dy=-0.25 * max(0, math.sin(min(q / 0.35, 1) * math.pi)))
        fx = [("!", who, q)]
    for i in range(n):
        if i != who:
            st[i].update(expr="smirk" if t < wake else "shocked", face=1 if i < who else -1)
    return st, fx, {"dark": 0.15 if t < wake else 0}


def b_love(b, t, dur, n, R):
    st = _base(n, expr="neutral")
    st[0].update(expr="smirk", face=1, dy=hop(t, 1.5, 0.04), xr=0.25 * ease(t / dur))
    st[1].update(expr="smirk" if t > dur * 0.5 else "shocked", face=-1, dy=hop(t + 0.3, 1.5, 0.04))
    fx = [("hearts", 0, t)] + ([("hearts", 1, t - dur * 0.5)] if t > dur * 0.5 else [])
    for i in range(2, n):
        st[i].update(expr="sad", face=-1)
        fx.append(("sweat", i, t))
    return st, fx, {}


def b_pop_in(b, t, dur, n, R):
    st = []
    fx = []
    for i in range(n):
        t0 = 0.3 + i * 0.6
        q = t - t0
        if q < 0:
            st.append({"hide": True})
            continue
        s = 1.0 + 0.25 * math.sin(min(q / 0.35, 1) * math.pi) * max(0, 1 - q / 0.6) if q < 0.6 else 1.0
        s = s * min(1.0, q / 0.15 + 0.2)
        st.append({"sx": s, "sy": s, "expr": "smirk" if q > 0.5 else "shocked", "dy": hop(t, 1.5, 0.02 * (q > 1))})
        if q < 0.6:
            fx.append(("puff", i, q))
    return st, fx, {}


BEAT_FN = {k: globals()[f"b_{k}"] for k in BEATS}


# ───────────────────────────── LÕI VẼ (pygame) ─────────────────────────────

class Renderer:
    def __init__(self, plan: dict, size: str, fps: int, level: np.ndarray | None):
        import pygame as pg
        self.pg = pg
        pg.init()
        pg.display.set_mode((1, 1))
        self.W, self.H = map(int, size.lower().split("x"))
        self.portrait = self.H > self.W
        self.plan, self.fps = plan, fps
        self.level = level
        self.out = pg.Surface((self.W, self.H))
        self._act_i, self._act = None, None
        self._figs, self._cache = {}, {}
        self._fonts = {}
        self.vignette = self._make_vignette()
        self.blinks = set()
        rnd = random.Random(plan["seed"])
        t = 1.0
        while t < plan["duration"]:
            self.blinks.update(range(int(t * fps), int(t * fps) + max(1, fps // 10)))
            t += rnd.uniform(2.5, 5)

    # ---- tài nguyên ----
    def _make_vignette(self):
        pg = self.pg
        w, h = self.W // 4, self.H // 4
        yy, xx = np.mgrid[0:h, 0:w]
        d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 + ((yy - h / 2) / (h / 2)) ** 2)
        a = (np.clip((d - 0.75) / 0.6, 0, 1) ** 1.5 * 110).astype(np.uint8)
        s = pg.Surface((w, h), pg.SRCALPHA)
        pg.surfarray.pixels_alpha(s)[:] = a.T
        return pg.transform.smoothscale(s, (self.W, self.H))

    def font(self, px):
        px = max(12, int(px) // 4 * 4)
        if px not in self._fonts:
            self._fonts[px] = self.pg.font.Font(str(FONT), px)
        return self._fonts[px]

    def act(self, i):
        if i == self._act_i:
            return self._act
        from PIL import Image
        from src.studio.puppet import Puppet
        pg = self.pg
        a = self.plan["acts"][i]
        card = yaml.safe_load((ROOT / "assets/scenes" / a["scene"] / "card.yaml").read_text(encoding="utf-8"))
        bg = Image.open(ROOT / "assets/scenes" / a["scene"] / card.get("master", "master.jpg")).convert("RGB")
        k = max(self.H * 1.15 / bg.height, self.W * 1.15 / bg.width)
        bg = bg.resize((int(bg.width * k), int(bg.height * k)), Image.LANCZOS)
        if TINTS[a["tint"]]:
            bg = Image.fromarray((np.asarray(bg, np.float32) * np.array(TINTS[a["tint"]]) / 255).astype(np.uint8))
        world = pg.image.frombytes(bg.tobytes(), bg.size, "RGB").convert()
        gy = card.get("ground_y", 0.9) * world.get_height()
        ah = self.H * 0.68 if not self.portrait else self.W * 0.55         # chiều cao người trong "thế giới"
        n = len(a["cast"])
        gap = min(0.95 * ah, (self.W * (0.9 if self.portrait else 0.8)) / max(n, 1))
        cx0 = world.get_width() / 2 + a["x0"] * world.get_width() * 0.5
        slots = [cx0 + (i - (n - 1) / 2) * gap for i in range(n)]
        pups = [Puppet(ROOT / "assets/actors" / c["actor"], c.get("outfit")) for c in a["cast"]]
        self._figs.clear()
        self._cache.clear()
        self._act_i = i
        self._act = {"plan": a, "world": world, "gy": gy, "ah": ah, "slots": slots, "pups": pups,
                     "theme": THEMES[a["theme"]]}
        return self._act

    def fig(self, ci, pose, head, sil):
        """Ảnh nhân vật (pygame) + khung đầu, chuẩn hoá chiều cao = 1000 px để mọi diễn viên cùng cỡ."""
        key = (ci, pose, head, sil)
        if key not in self._figs:
            pg = self.pg
            pup = self._act["pups"][ci]
            img, foot = pup.figure(pose, head)
            hb = pup.head_box[pup.last_key]
            k = 1000 / img.height
            from PIL import Image
            img = img.resize((max(1, int(img.width * k)), 1000), Image.LANCZOS)
            s = pg.image.frombytes(img.tobytes(), img.size, "RGBA").convert_alpha()
            if sil:
                s.fill((0, 0, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
                s.fill((28, 26, 30, 0), special_flags=pg.BLEND_RGBA_ADD)
            self._figs[key] = (s, [v * k for v in hb])
        return self._figs[key]

    # ---- một khung ----
    def frame(self, fi: int) -> bytes:
        pg = self.pg
        t = fi / self.fps
        acts = self.plan["acts"]
        ai = next((i for i, a in enumerate(acts) if a["start"] <= t < a["end"]), len(acts) - 1)
        A = self.act(ai)
        a = A["plan"]
        bi, b = next(((i, x) for i, x in enumerate(a["beats"]) if x["start"] <= t < x["end"]),
                     (len(a["beats"]) - 1, a["beats"][-1]))
        bt, dur = t - b["start"], b["end"] - b["start"]
        n = len(a["cast"])
        ah, gy, world = A["ah"], A["gy"], A["world"]
        b = dict(b, span=self.W / ah / 2 + 0.7)            # nửa bề ngang khung toàn (đơn vị chiều cao người) + lề
        st, fx, scr = BEAT_FN[b["kind"]](b, bt, dur, n, random.Random(b["seed"]))
        lvl = float(self.level[min(fi, len(self.level) - 1)]) if self.level is not None else \
            0.5 + 0.5 * math.sin(t * 9) * math.sin(t * 2.3)

        WW, WH = world.get_size()
        # vị trí thế giới: xr = lệch khỏi chỗ đứng riêng, xa = tính từ giữa nhóm (chạy ngang qua khung)
        mid = sum(A["slots"]) / n
        xs = [mid + st[i]["xa"] * ah if "xa" in st[i] else A["slots"][i] + st[i].get("xr", 0) * ah for i in range(n)]
        # máy quay
        z0 = {"wide": 1.0, "medium": 1.45, "close": 2.05}[b["shot"]]
        p = bt / dur
        z = z0 * {"push": 1 + 0.12 * ease(p), "pull": 1.12 - 0.12 * ease(p)}.get(b["move"], 1.0)
        if b["punch"] and bt < 0.18:
            z *= 1 + 0.08 * (1 - bt / 0.18)
        vw, vh = self.W / z, self.H / z
        subj = min(b["subject"], n - 1)
        if b["shot"] == "wide":
            cx = mid
            cy = gy - 0.42 * vh
        elif b["shot"] == "medium":
            cx, cy = xs[subj], gy - 0.5 * ah
        else:
            cx, cy = xs[subj], gy - 0.74 * ah
        if b["move"] == "pan":
            cx += (p - 0.5) * vw * 0.25
        cx += math.sin(t * 0.6) * vw * 0.004                     # máy cầm tay: trôi rất nhẹ
        cy += math.sin(t * 0.45 + 1) * vh * 0.003
        sh = scr.get("shake", 0)
        if sh:
            cx += math.sin(t * 73) * vw * 0.012 * sh
            cy += math.cos(t * 61) * vh * 0.008 * sh
        left = min(max(cx - vw / 2, 0), WW - vw)
        top = min(max(cy - vh / 2, 0), WH - vh)
        sub = world.subsurface(pg.Rect(int(left), int(top), int(min(vw, WW - int(left))), int(min(vh, WH - int(top)))))
        pg.transform.smoothscale(sub, (self.W, self.H), self.out)
        S = self.out

        def to_s(X, Y):
            return (X - left) * z, (Y - top) * z

        heads = [None] * n
        order = sorted(range(n), key=lambda i: st[i].get("dy", 0))     # ai nhảy cao vẽ sau
        for i in order:
            s = st[i]
            if s.get("hide"):
                continue
            pup = A["pups"][i]
            head = s.get("expr", "neutral")
            if s.get("talk") and lvl > 0.18 and f"{head}_talk" in pup.card["heads"]:
                head = f"{head}_talk"
            elif fi in self.blinks and head in ("neutral", "smirk"):
                head = "blink"
            face = s.get("face", 0) or (1 if A["slots"][i] <= sum(A["slots"]) / n else -1)
            sil = bool(s.get("sil"))
            base, hb = self.fig(i, s.get("pose", "relaxed"), head, sil)
            sx, sy, rot = s.get("sx", 1.0), s.get("sy", 1.0), s.get("rot", 0.0) * face
            hpx = ah * z                                          # cao trên màn hình
            k = hpx / 1000
            fx_, fy_ = to_s(xs[i], gy + s.get("dy", 0) * ah)
            key = (i, base.get_size(), id(base), round(k * sx, 3), round(k * sy, 3), round(rot), face)
            img = self._cache.get(key)
            if img is None:
                img = base if face > 0 else pg.transform.flip(base, True, False)
                w2, h2 = max(1, int(img.get_width() * k * sx)), max(1, int(1000 * k * sy))
                img = pg.transform.smoothscale(img, (w2, h2))
                if round(rot):
                    img = pg.transform.rotozoom(img, round(rot), 1.0)
                if len(self._cache) > 600:
                    self._cache.clear()
                self._cache[key] = img
            h_scaled = 1000 * k * sy
            off = pg.math.Vector2(0, h_scaled / 2).rotate(-round(rot))
            cxs, cys = fx_ - off.x, fy_ - off.y
            S.blit(img, (int(cxs - img.get_width() / 2), int(cys - img.get_height() / 2)))
            # tâm đầu trên màn hình (để vẽ ký hiệu)
            bw = base.get_width()
            hx = (hb[0] + hb[2] / 2 - bw / 2) * k * sx * face
            hy = (hb[1] + hb[3] / 2 - 1000) * k * sy
            v = pg.math.Vector2(hx, hy).rotate(-round(rot))
            heads[i] = (fx_ + v.x, fy_ + v.y, hb[3] * k, fx_, fy_, face)

        dark = scr.get("dark", 0)
        if dark:
            ov = pg.Surface((self.W, self.H))
            ov.fill((10, 12, 30))
            ov.set_alpha(int(255 * dark))
            S.blit(ov, (0, 0))
        for kind, i, arg in fx:
            self.draw_fx(S, kind, heads[i] if i is not None else None, arg, t, b["seed"])
        S.blit(self.vignette, (0, 0))
        fl = scr.get("flash", 0)
        if fl > 0.01:
            ov = pg.Surface((self.W, self.H))
            ov.fill((255, 255, 240))
            ov.set_alpha(int(255 * min(1, fl)))
            S.blit(ov, (0, 0))
        self.transition(S, t, ai)
        return pg.image.tobytes(S, "RGB")

    def transition(self, S, t, ai):
        """Dải màu chéo quét ngang 0,5 giây ở ranh giới hai hồi (che kín màn hình đúng lúc đổi nền)."""
        acts = self.plan["acts"]
        for j in range(1, len(acts)):
            q = (t - (acts[j]["start"] - 0.25)) / 0.5
            if 0 <= q <= 1:
                pg = self.pg
                W, H = self.W, self.H
                sl = 0.35 * H
                col = THEMES[acts[j]["theme"]]
                right = -sl + (W + 2 * sl) * min(1, q / 0.5)
                lft = -sl + (W + 2 * sl) * max(0, (q - 0.5) / 0.5) - sl
                pts = [(lft, H), (lft + sl, 0), (right + sl, 0), (right, H)]
                pg.draw.polygon(S, col, pts)
                pg.draw.line(S, (255, 255, 255), (right, H), (right + sl, 0), max(4, H // 60))

    # ---- ký hiệu manga ----
    def draw_fx(self, S, kind, h, a, t, seed):
        pg = self.pg
        if h is None and kind not in ("cloud",):
            return
        if h:
            hx, hy, hs, fx_, fy_, face = h
        if kind == "sweat":
            y = hy - 0.15 * hs + (a * 0.25 % 0.4) * hs
            x, r = hx + 0.45 * hs * face, 0.07 * hs
            pg.draw.polygon(S, (120, 200, 255), [(x, y - 2.6 * r), (x - r, y), (x + r, y)])
            pg.draw.circle(S, (120, 200, 255), (x, y), r)
            pg.draw.circle(S, (40, 90, 160), (x, y), r, max(2, int(r / 4)))
            pg.draw.circle(S, (255, 255, 255), (x - r * 0.35, y - r * 0.3), max(1, r * 0.25))
        elif kind == "anger":
            s = 0.14 * hs * (1 + 0.15 * abs(math.sin(a * 8)))
            x, y = hx + 0.38 * hs * face, hy - 0.38 * hs
            w = max(3, int(s / 4))
            for ang in (45, 135, 225, 315):
                v = pg.math.Vector2(1, 0).rotate(ang)
                p1 = (x + v.x * s * 0.25, y + v.y * s * 0.25)
                p2 = (x + v.x * s, y + v.y * s)
                pg.draw.line(S, (230, 30, 40), p1, p2, w)
                pg.draw.line(S, (230, 30, 40), p2, (p2[0] + v.rotate(90).x * s * 0.35, p2[1] + v.rotate(90).y * s * 0.35), w)
        elif kind in ("!", "?", "haha", "zzz"):
            txt = {"!": "!", "?": "?", "haha": "HAHA", "zzz": "Z z z"}[kind]
            px = hs * (0.5 if kind in "!?" else 0.3)
            pop = min(1, a / 0.15) if kind in "!?" else 1
            yb = hy - 0.75 * hs - (a * 0.08 * hs if kind == "zzz" else 0) % (0.4 * hs)
            col = {"!": (255, 60, 60), "?": (255, 200, 0), "haha": (255, 140, 0), "zzz": (160, 200, 255)}[kind]
            self.text(S, txt, hx + (0.35 * hs * face if kind != "!" else 0), yb, px * pop, col)
        elif kind == "sparkle" or kind == "stars":
            for j in range(3):
                ph = a * 2 + j * 2.1
                r = (0.06 + 0.04 * abs(math.sin(ph * 2))) * hs
                x = hx + math.cos(j * 2.1 + seed) * 0.6 * hs
                y = hy - 0.5 * hs + math.sin(j * 1.7) * 0.3 * hs
                self.star(S, x, y, r, ph * 40, (255, 230, 80), 4 if kind == "sparkle" else 5)
        elif kind == "dizzy":
            for j in range(3):
                ang = a * 4 + j * 2.094
                x = hx + math.cos(ang) * 0.45 * hs
                y = hy - 0.45 * hs + math.sin(ang) * 0.12 * hs
                self.star(S, x, y, 0.07 * hs, a * 200, (255, 220, 60), 5)
        elif kind == "notes":
            for j in range(2):
                ph = (a * 0.6 + j * 0.5) % 1
                x = hx + (0.5 + 0.2 * j) * hs * (1 if j else -1) + math.sin(ph * 6) * 0.08 * hs
                y = hy - 0.2 * hs - ph * 0.7 * hs
                self.note(S, x, y, 0.09 * hs, (255, 120, 180) if j else (90, 170, 255))
        elif kind == "hearts":
            for j in range(3):
                ph = (a * 0.5 + j / 3) % 1
                x = hx + 0.5 * hs * face * (0.6 + ph * 1.4) + math.sin(ph * 8 + j) * 0.06 * hs
                y = hy - 0.1 * hs - ph * 0.6 * hs
                self.heart(S, x, y, 0.1 * hs * (1 - 0.4 * ph), (255, 70, 110))
        elif kind == "steam":
            for j in range(2):
                ph = (a * 1.5 + j * 0.5) % 1
                for side in (-1, 1):
                    x = hx + side * 0.45 * hs + side * ph * 0.15 * hs
                    y = hy - 0.45 * hs - ph * 0.3 * hs
                    pg.draw.circle(S, (245, 245, 245), (x, y), 0.06 * hs * (1 - ph * 0.5))
        elif kind == "dust" or kind == "puff":
            for j in range(3):
                ph = (a * (2.5 if kind == "dust" else 1.6) + j / 3) % 1 if kind == "dust" else min(1, a / 0.6)
                x = fx_ - face * (0.15 + ph * 0.35) * hs * (1 if kind == "dust" else (j - 1) * 2)
                y = fy_ - ph * 0.2 * hs
                pg.draw.circle(S, (235, 228, 215), (x, y), max(1, 0.12 * hs * (1 - ph)))
        elif kind == "speed":
            for j in range(4):
                y = hy + (0.2 + j * 0.35) * hs
                x0 = fx_ - a * (0.5 + 0.1 * j) * hs
                pg.draw.line(S, (255, 255, 255), (x0, y), (x0 - a * 0.7 * hs, y), max(2, int(hs / 40)))
        elif kind == "rain":
            cx, cy = hx, hy - 0.85 * hs
            for dx, r in ((-0.25, 0.18), (0, 0.24), (0.25, 0.18)):
                pg.draw.circle(S, (110, 115, 130), (cx + dx * hs, cy), r * hs)
            for j in range(6):
                ph = (a * 2 + j / 6) % 1
                x = cx + (-0.35 + j * 0.14) * hs
                y = cy + 0.15 * hs + ph * 0.5 * hs
                pg.draw.line(S, (110, 170, 255), (x, y), (x - 0.02 * hs, y + 0.08 * hs), max(2, int(hs / 50)))
        elif kind == "gloom":
            for j in range(3):
                x = hx + (-0.3 + 0.3 * j) * hs
                for k in range(3):
                    y = hy - 0.55 * hs + k * 0.13 * hs
                    pg.draw.line(S, (120, 90, 170), (x, y), (x, y + 0.07 * hs), max(2, int(hs / 45)))
        elif kind == "whirl":
            for j in range(3):
                r = (0.5 + 0.15 * j) * hs
                st_ = a * 10 + j
                pg.draw.arc(S, (255, 255, 255), pg.Rect(fx_ - r, hy - 0.2 * hs - r * 0.3, 2 * r, r * 0.6 + hs),
                            st_, st_ + 1.4, max(2, int(hs / 35)))
        elif kind == "cloud":
            W = self.W
            for j in range(7):
                x = (j / 6) * W + math.sin(t * 0.5 + j) * W * 0.03
                pg.draw.circle(S, (40, 42, 58), (x, -self.H * 0.02), self.H * (0.13 + 0.03 * (j % 2)))
        elif kind == "bolt":
            R = random.Random(seed)
            pts = [(hx + R.uniform(-0.3, 0.3) * self.W * 0.3, 0)]
            steps = 7
            for j in range(1, steps):
                fy = (hy - 0.5 * hs) * j / steps
                pts.append((hx + R.uniform(-0.12, 0.12) * self.W * 0.3 * (1 - j / steps), fy))
            pts.append((hx, hy - 0.45 * hs))
            pg.draw.lines(S, (255, 240, 120), False, pts, max(8, int(self.H / 45)))
            pg.draw.lines(S, (255, 255, 255), False, pts, max(3, int(self.H / 120)))
        elif kind == "smoke":
            for j in range(4):
                ph = (a * 0.7 + j / 4) % 1
                x = hx + math.sin(ph * 5 + j) * 0.2 * hs
                y = hy - 0.5 * hs - ph * 0.9 * hs
                c = int(90 + 80 * ph)
                pg.draw.circle(S, (c, c, c), (x, y), 0.1 * hs * (0.6 + ph))

    def text(self, S, txt, x, y, px, col):
        if px < 6:
            return
        f = self.font(px)
        o = max(2, int(px / 10))
        out = f.render(txt, True, (20, 16, 24))
        fg = f.render(txt, True, col)
        r = fg.get_rect(center=(int(x), int(y)))
        for dx, dy in ((-o, 0), (o, 0), (0, -o), (0, o), (-o, -o), (o, o), (-o, o), (o, -o)):
            S.blit(out, r.move(dx, dy))
        S.blit(fg, r)

    def star(self, S, x, y, r, rot, col, pts=5):
        P = []
        for j in range(pts * 2):
            rr = r if j % 2 == 0 else r * (0.45 if pts == 5 else 0.3)
            v = self.pg.math.Vector2(0, -rr).rotate(rot + j * 180 / pts)
            P.append((x + v.x, y + v.y))
        self.pg.draw.polygon(S, col, P)
        self.pg.draw.polygon(S, (60, 40, 10), P, max(1, int(r / 6)))

    def heart(self, S, x, y, r, col):
        pg = self.pg
        pg.draw.circle(S, col, (x - r * 0.5, y), r * 0.55)
        pg.draw.circle(S, col, (x + r * 0.5, y), r * 0.55)
        pg.draw.polygon(S, col, [(x - r * 1.03, y + r * 0.15), (x + r * 1.03, y + r * 0.15), (x, y + r * 1.25)])

    def note(self, S, x, y, r, col):
        pg = self.pg
        pg.draw.ellipse(S, col, pg.Rect(x - r, y - r * 0.7, 2 * r, 1.4 * r))
        w = max(2, int(r / 3))
        pg.draw.line(S, col, (x + r * 0.85, y), (x + r * 0.85, y - 3 * r), w)
        pg.draw.line(S, col, (x + r * 0.85, y - 3 * r), (x + r * 1.8, y - 2.3 * r), w)


# ───────────────────────────── DỰNG ─────────────────────────────

def loudness(audio: pathlib.Path, fps: int) -> tuple[np.ndarray, float]:
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", str(audio), "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
                         capture_output=True, check=True).stdout
    d = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    hop_ = 16000 // fps
    n = len(d) // hop_
    rms = np.sqrt(np.mean(d[: n * hop_].reshape(n, hop_) ** 2, axis=1))
    return rms / (np.percentile(rms, 98) + 1e-9), len(d) / 16000


def encoder_args() -> list[str]:
    if sys.platform == "darwin":
        return ["-c:v", "h264_videotoolbox", "-b:v", "6M"]
    return ["-c:v", "libx264", "-preset", "veryfast", "-crf", "23"]


def _render_part(job) -> str:
    plan, size, fps, f0, f1, out, level = job
    os.nice(10)
    r = Renderer(plan, size, fps, level)
    W, H = r.W, r.H
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
                            "-r", str(fps), "-i", "-", *encoder_args(), "-pix_fmt", "yuv420p", out],
                           stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        enc.stdin.write(r.frame(fi))
    enc.stdin.close()
    if enc.wait():
        raise RuntimeError("ffmpeg lỗi")
    return out


def render(plan: dict, size: str, out: pathlib.Path, fps: int, audio: pathlib.Path | None, level, workers: int):
    from concurrent.futures import ProcessPoolExecutor
    frames = int(plan["duration"] * fps)
    n = workers or max(1, (os.cpu_count() or 2) - 2)
    chunk = max(fps * 10, -(-frames // n))
    with tempfile.TemporaryDirectory() as tmp:
        jobs = [(plan, size, fps, f0, min(f0 + chunk, frames), f"{tmp}/part_{i:04d}.mp4", level)
                for i, f0 in enumerate(range(0, frames, chunk))]
        if n == 1:
            parts = [_render_part(j) for j in jobs]
        else:
            with ProcessPoolExecutor(max_workers=n) as ex:
                parts = list(ex.map(_render_part, jobs))
        lst = pathlib.Path(tmp) / "list.txt"
        lst.write_text("".join(f"file '{p}'\n" for p in parts))
        out.parent.mkdir(parents=True, exist_ok=True)
        cmd = ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(lst)]
        if audio:
            cmd += ["-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k", "-shortest"]
        cmd += ["-c:v", "copy", "-movflags", "+faststart", str(out)]
        subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--audio", help="giọng đọc (mp3/wav); có .srt cùng tên thì chép theo")
    ap.add_argument("--seconds", type=float, help="độ dài khi không có giọng đọc (hoặc cắt ngắn giọng để xem thử)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--size", default="1920x1080")
    ap.add_argument("--fps", type=int, default=24)
    ap.add_argument("--act", type=float, default=60.0, help="độ dài mỗi hồi (giây): đổi nền + diễn viên")
    ap.add_argument("--workers", type=int, default=0)
    a = ap.parse_args()
    out = pathlib.Path(a.out)
    seed = a.seed if a.seed is not None else random.randrange(1 << 30)
    level, dur, audio = None, a.seconds, None
    if a.audio:
        audio = pathlib.Path(a.audio)
        level, adur = loudness(audio, a.fps)
        dur = min(adur, a.seconds) if a.seconds else adur
    if not dur:
        ap.error("cần --audio hoặc --seconds")
    t0 = time.time()
    plan = make_plan(dur, seed, a.act)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.with_suffix(".plan.json").write_text(json.dumps(plan, ensure_ascii=False, indent=1), encoding="utf-8")
    render(plan, a.size, out, a.fps, audio, level, a.workers)
    if audio and audio.with_suffix(".srt").exists() and not a.seconds:
        shutil.copy(audio.with_suffix(".srt"), out.with_suffix(".srt"))
    took = time.time() - t0
    print(f"Xong: {out} ({dur:.0f} giây video, dựng {took:.0f} giây = {dur / took:.1f}x thời gian thực, seed {seed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
