"""Tải model AI chạy local vào .cache/ của dự án và sửa lỗi symlink của onnxruntime.

python scripts/setup_models.py   (scripts/setup.sh gọi file này)
"""
import os
import pathlib
import shutil

ROOT = pathlib.Path(__file__).resolve().parent.parent
os.environ.setdefault("HF_HOME", str(ROOT / ".cache/huggingface"))


def unsymlink(hub: pathlib.Path) -> int:
    """onnxruntime >= 1.30 từ chối file .data nằm khác thư mục với .onnx; HuggingFace lưu dạng symlink tới blobs/."""
    n = 0
    for p in hub.glob("models--*/snapshots/**/*"):
        if p.is_symlink():
            target = p.resolve()
            p.unlink()
            shutil.move(str(target), str(p))
            n += 1
    return n


def main() -> int:
    from vieneu import Vieneu

    hub = pathlib.Path(os.environ["HF_HOME"]) / "hub"
    try:
        Vieneu()  # lần đầu: tải model; có thể lỗi symlink
    except Exception as e:  # noqa: BLE001
        print("Lần tải đầu báo lỗi (thường là symlink), sửa rồi thử lại:", str(e)[:120])
    print("Đã chuyển symlink thành file thật:", unsymlink(hub))
    v = Vieneu()
    out = ROOT / "tmp" / "setup_check.wav"
    out.parent.mkdir(exist_ok=True)
    v.save(v.infer("Cài đặt VieNeu thành công.", voice="Ngọc Huyền"), str(out))
    print("VieNeu OK:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
