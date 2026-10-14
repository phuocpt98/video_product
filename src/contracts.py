"""HỢP ĐỒNG DỮ LIỆU của kho thư viện (diễn viên, bản thiết kế nhân vật): mỗi loại dữ liệu trao tay có khai báo trường bắt buộc + kiểu,
và hàm check() dùng ở mọi chỗ NHẬN dữ liệu (đọc file, nhận câu trả lời của AI). Sai thì báo rõ, không chạy lệch.
Mô tả cho người và AI đọc: docs/plans/protocols.md (giữ hai nơi khớp nhau khi sửa).

python -m src.contracts <loại> <file.yaml>     # kiểm một file bằng tay
"""
import pathlib
import sys

import yaml

# kiểu: str | int | float | list | dict | bool | "a|b|c" (một trong) ; "?" ở đầu tên = không bắt buộc
CONTRACTS: dict[str, dict] = {
    # Thiết kế nhân vật: bản thiết kế ghép từ kho bộ phận (AI trả về phải khớp)
    "avatar": {"head": str, "eyes": str, "mouth": str, "?nose": str, "?extras": list, "?skin": str, "body": dict,
               "?look": str, "?head_size": float, "?overlap": float, "?adjust": dict, "?roles": list},
    "avatar_body": {"outfit": str, "?build": "thin|normal|fat", "?colors": dict},
    # Diễn viên rối (assets/actors/<id>/card.yaml); hình học kiểm bằng src/studio/validate_actor.py
    "actor_card": {"id": str, "kind": "actor", "rig": dict, "heads": dict, "outfits": dict, "?gender": str,
                   "?age": str, "?look": str, "?signature": str, "?roles": list, "?notes": str, "?made_by": str},
    "actor_rig": {"mode": "chibi|semi|real", "head_scale": float, "overlap": float, "?chin_up": float,
                  "?head_dx": float, "?neck_dx": dict, "?hair_back": str, "?hair_back_chin": float, "?hands": dict},
}


def _type_ok(v, t) -> bool:
    if isinstance(t, str):                            # tập giá trị cho phép
        return v in t.split("|")
    if t is float:
        return isinstance(v, (int, float)) and not isinstance(v, bool)
    return isinstance(v, t)


def check(kind: str, obj, where: str = "") -> list[str]:
    """Trả danh sách lỗi (rỗng = hợp lệ). Kiểm cả phần con: avatar → avatar_body."""
    spec = CONTRACTS[kind]
    at = f"{where or kind}"
    if not isinstance(obj, dict):
        return [f"{at}: phải là dict, nhận {type(obj).__name__}"]
    errs = []
    for key, t in spec.items():
        opt, name = key.startswith("?"), key.lstrip("?")
        if name not in obj or obj[name] is None:
            if not opt:
                errs.append(f"{at}: thiếu '{name}'")
            continue
        if not _type_ok(obj[name], t):
            errs.append(f"{at}.{name}: sai kiểu/giá trị {obj[name]!r} (cần {t if isinstance(t, str) else t.__name__})")
    if kind == "avatar" and isinstance(obj.get("body"), dict):
        errs += check("avatar_body", obj["body"], "body")
    return errs


def require(kind: str, obj, where: str = ""):
    """Như check() nhưng ném ValueError nếu sai; trả lại obj để dùng nối tiếp."""
    errs = check(kind, obj, where)
    if errs:
        raise ValueError(f"Sai hợp đồng '{kind}' ({len(errs)} lỗi): " + "; ".join(errs[:8]))
    return obj


if __name__ == "__main__":
    data = yaml.safe_load(pathlib.Path(sys.argv[2]).read_text(encoding="utf-8"))
    errs = check(sys.argv[1], data)
    print("Hợp lệ" if not errs else "\n".join(errs))
    sys.exit(1 if errs else 0)
