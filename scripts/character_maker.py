"""TRANG TẠO NHÂN VẬT chạy local (kiểu màn tạo nhân vật trong game): chọn đầu, mắt, miệng, mũi, phụ kiện, màu da,
bộ đồ, vóc, màu quần áo → xem ngay → Lưu thành diễn viên (assets/actors/<id>/) dùng được trong stage.py.
Ghép ảnh do src/studio/avatar.py làm (một nguồn duy nhất), trang web chỉ để chọn và xem.

python scripts/character_maker.py [--port 8765]   → mở http://localhost:8765
"""
import argparse
import io
import re
import json
import pathlib
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

import yaml
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.studio import avatar  # noqa: E402

PAGE = ROOT / "src/studio/maker/index.html"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,40}$")            # id diễn viên: chữ thường không dấu, số, gạch ngang
PARTS = ROOT / "assets/parts"


def catalog() -> dict:
    reg = yaml.safe_load((PARTS / "parts.yaml").read_text(encoding="utf-8"))
    by = {}
    for k, v in reg.items():
        by.setdefault(v["kind"], []).append({"id": k, "desc": v.get("desc", ""), "file": v["file"], **(
            {"gender": v.get("gender"), "missing": v.get("missing", [])} if v["kind"] == "bodies" else {})})
    eyes = sorted({k.split("-")[0] for k in reg if k.startswith("eyes")}, key=lambda s: int(s[4:]))
    mouths = sorted({k.split("-")[0] for k in reg if k.startswith("mouth")})
    extras = [x for x in by.get("extras", []) if not x["id"].startswith("nose")]
    noses = [x for x in by.get("extras", []) if x["id"].startswith("nose")]
    actors = sorted(p.parent.name for p in (ROOT / "assets/actors").glob("*/avatar.yaml"))
    return {"heads": by.get("heads", []), "eyes": [{"id": e, "file": reg[f"{e}-normal"]["file"],
                                                     "desc": reg[f"{e}-normal"].get("desc", "")} for e in eyes],
            "mouths": [{"id": m, "file": reg[f"{m}-smile"]["file"], "desc": reg[f"{m}-smile"].get("desc", "")}
                       for m in mouths],
            "noses": noses, "extras": extras,
            "outfits": [{"id": b["id"].split(":", 1)[1], "desc": b["desc"], "gender": b["gender"]}
                        for b in by.get("bodies", [])],
            "expressions": list(avatar.EXPRESSIONS), "poses": list(avatar.POSE_LIST), "actors": actors}


def png(img: Image.Image, max_h: int) -> bytes:
    if img.height > max_h:
        img = img.resize((int(img.width * max_h / img.height), max_h), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()


class H(BaseHTTPRequestHandler):
    def _send(self, body: bytes, ctype: str, code: int = 200):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(json.dumps(obj, ensure_ascii=False).encode(), "application/json; charset=utf-8", code)

    def log_message(self, *a):
        pass

    def do_GET(self):
        u = urlparse(self.path)
        q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            if u.path == "/":
                self._send(PAGE.read_bytes(), "text/html; charset=utf-8")
            elif u.path == "/api/catalog":
                self._json(catalog())
            elif u.path.startswith("/parts/"):                   # ảnh bộ phận để làm hình thu nhỏ
                f = (PARTS / u.path[len("/parts/"):]).resolve()
                if PARTS.resolve() not in f.parents:
                    return self._send(b"", "text/plain", 403)
                self._send(f.read_bytes(), "image/png")
            elif u.path == "/api/palette":
                self._json(avatar.palette(q["outfit"], q.get("build", "normal")))
            elif u.path == "/api/load":
                if not ID_RE.match(q.get("id", "")):
                    return self._json({"error": "id không hợp lệ"}, 400)
                self._json(yaml.safe_load((ROOT / "assets/actors" / q["id"] / "avatar.yaml").read_text(encoding="utf-8")))
            else:
                self._send(b"not found", "text/plain", 404)
        except Exception as e:  # noqa: BLE001  trả lỗi về trang cho dễ thấy (không lộ đường dẫn máy)
            self._json({"error": str(e).replace(str(ROOT) + "/", "")}, 500)

    def do_POST(self):
        u = urlparse(self.path)
        origin = self.headers.get("Origin") or self.headers.get("Referer") or ""
        host = self.headers.get("Host", "")
        if origin and urlparse(origin).netloc != host:          # chặn trang web khác gửi lệnh vào máy chủ local
            return self._json({"error": "sai nguồn gửi"}, 403)
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])) or b"{}")
        try:
            if u.path == "/api/render":                       # 1 nhân vật theo biểu cảm + tư thế
                self._send(png(avatar.figure(body["spec"], body.get("expr", "neutral"), body.get("pose", "relaxed")),
                               620), "image/png")
            elif u.path == "/api/strip":                      # dải 8 biểu cảm
                spec = body["spec"]
                heads = [avatar.scaled_head(spec, e) for e in avatar.EXPRESSIONS]
                hh = max(h.height for h in heads)
                strip = Image.new("RGBA", (sum(h.width + 10 for h in heads), hh), (0, 0, 0, 0))
                x = 0
                for h in heads:
                    strip.alpha_composite(h, (x, hh - h.height))
                    x += h.width + 10
                self._send(png(strip, 140), "image/png")
            elif u.path == "/api/save":
                aid = body["id"].strip().lower().replace(" ", "-")
                if not ID_RE.match(aid):
                    return self._json({"error": "id không hợp lệ (chữ thường không dấu, số, gạch ngang)"}, 400)
                avatar.build_actor(aid, body["spec"])
                out = avatar.preview(aid)
                self._json({"ok": True, "id": aid, "preview": str(out.relative_to(ROOT))})
            else:
                self._send(b"not found", "text/plain", 404)
        except Exception as e:  # noqa: BLE001
            self._json({"error": str(e).replace(str(ROOT) + "/", "")}, 500)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    print(f"Trang tạo nhân vật: http://localhost:{a.port}  (Ctrl+C để tắt)")
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
