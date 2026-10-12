"""Tạo QUẦN CHÚNG (người qua đường, khách, học sinh…) bằng cách ghép ngẫu nhiên từ kho bộ phận: không tốn ảnh AI.
Ghi ra assets/actors/qc-XX/ (đủ 8 biểu cảm, 4 tư thế). stage.py ưu tiên lấy quần chúng từ nhóm qc-*.

python scripts/make_extras.py [--n 16] [--seed 1]
"""
import argparse
import pathlib
import random
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.studio import avatar  # noqa: E402

SKINS = ["", "", "#f7d2b0", "#e8b98f", "#d9a57a"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1)
    a = ap.parse_args()
    reg = yaml.safe_load((ROOT / "assets/parts/parts.yaml").read_text(encoding="utf-8"))
    rnd = random.Random(a.seed)
    bald = {"head-round", "head-oval", "head-square", "head-chubby", "head-long", "head-oval2", "head-pointed",
            "head-pointed2", "head-kid"}                  # mặt nền chưa có tóc: không dùng cho quần chúng
    heads = [k for k, v in reg.items() if v["kind"] == "heads" and not k.endswith("-special") and k not in bald]
    male = [k.split(":", 1)[1] for k, v in reg.items() if v["kind"] == "bodies" and v.get("gender") == "male"]
    female = [k.split(":", 1)[1] for k, v in reg.items() if v["kind"] == "bodies" and v.get("gender") == "female"]
    fem_heads = {"head-long-bangs", "head-long-wavy", "head-ponytail", "head-twin", "head-bob", "head-bun", "head-perm",
                 "head-grey-bun", "head-brown-long", "head-braid", "head-mid-f", "head-old-f", "head-short-f"}
    for i in range(1, a.n + 1):
        h = rnd.choice(heads)
        f = h in fem_heads
        spec = {"head": h, "eyes": rnd.choice(["eyes3", "eyes5", "eyes8"] if f else ["eyes1", "eyes2", "eyes4", "eyes6", "eyes7"]),
                "mouth": "mouth2" if f else rnd.choice(["mouth1", "mouth1", "mouth3"]), "nose": "nose2",
                "extras": [rnd.choice(["glasses-round", "glasses-square", "blush"] if f else
                                      ["glasses-round", "glasses-square", "mustache", "beard-stubble"])]
                          if rnd.random() < 0.25 else [],
                "skin": rnd.choice(SKINS),
                "body": {"outfit": rnd.choice(female if f else male), "build": rnd.choice(["thin", "normal", "normal", "fat"])},
                "look": "quần chúng", "roles": ["quần chúng"]}
        aid = f"qc-{i:02d}"
        avatar.build_actor(aid, spec)
        print(aid, h, spec["body"]["outfit"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
