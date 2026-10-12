# Hàng đợi tạo ảnh bằng agy theo board/image_queue.yaml (ưu tiên 1 trước). Hết lượt ảnh → chờ 20 phút rồi thử lại.
# Chạy nền: ./scripts/image_queue.sh   (log: tmp/image_queue.log)
cd "$(dirname "$0")/.." && source .venv/bin/activate
next() {   # in "loai id" của việc chưa xong có ưu tiên cao nhất; rỗng = hết việc
  python - <<'EOF'
import pathlib, yaml
R = pathlib.Path(".")
done = {"sheet": lambda i: (R / f"assets/parts/source/{i}.jpg").exists(),
        "scene": lambda i: (R / f"assets/scenes/source/{i}_agy.jpg").exists(),
        "outfit": lambda i: (R / f"assets/parts/bodies/{i}").exists(),
        "fill": lambda i: (R / "tmp/.fill_done").exists()}
for t in sorted(yaml.safe_load((R / "board/image_queue.yaml").read_text(encoding="utf-8")), key=lambda t: t["uu_tien"]):
    if t["loai"] in done and not done[t["loai"]](t["id"]):
        print(t["loai"], t["id"])
        break
EOF
}
while true; do
  set -- $(next)
  [ -z "$1" ] && { echo "HẾT VIỆC $(date +%H:%M)" >> tmp/image_queue.log; exit 0; }
  echo "▶ $1 $2 $(date +%H:%M)" >> tmp/image_queue.log
  case $1 in
    sheet)  python scripts/make_parts.py "$2" >> tmp/image_queue.log 2>&1 ;;
    scene)  python scripts/make_scene_sheet.py --single "$2" >> tmp/image_queue.log 2>&1 ;;
    outfit) python scripts/make_parts.py --body "$2" >> tmp/image_queue.log 2>&1 ;;
    fill)   python scripts/make_parts.py --todo >> tmp/image_queue.log 2>&1 && touch tmp/.fill_done ;;
  esac || { echo "chờ $(date +%H:%M)" >> tmp/image_queue.log; sleep 1200; }
done
