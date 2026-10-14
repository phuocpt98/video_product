"""Diễn viên chibi rối cắt ghép (assets/actors/<id>/card.yaml): ghép đầu (biểu cảm) lên thân (tư thế), dán đạo cụ
vào tay. Dùng chung cho reel.py (hoạt hình ngẫu nhiên) và các công cụ kho (validate_actor...)."""
import pathlib

import numpy as np
import yaml
from PIL import Image

from src.studio.cutout import neck_top

ROOT = pathlib.Path(__file__).resolve().parents[2]
PROPS = ROOT / "assets/props"


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
