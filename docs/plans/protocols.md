# Giao thức dữ liệu (kho thư viện + dây chuyền)

Cập nhật: 14/10/2026 · Code kiểm: `src/contracts.py` (sửa thì sửa cả hai nơi). Kiểm tay: `python -m src.contracts <loại> <file>`. Vận hành: [README.md](../../README.md).

## 1. Nguyên tắc
1. Mỗi loại dữ liệu trao tay có một hợp đồng: tên trường, kiểu, giá trị cho phép. **Người nhận luôn kiểm** bằng `check()`/`require()`, sai thì báo lỗi rõ.
2. AI không bao giờ được tin thẳng: câu trả lời phải ở dạng máy đọc được (JSON hoặc khối ```yaml), chỉ chọn trong danh sách đóng có thật trong kho.
3. File là kênh chung: YAML/JSON/text UTF-8 ở đúng chỗ trong bản đồ thư mục.
4. Thời gian tính bằng giây (số thực), tỉ lệ khung từ 0 đến 1, id không dấu, ngăn bằng gạch ngang.

## 2. Các hợp đồng

| Loại | File | Ai ghi | Ai đọc | Trường chính |
|---|---|---|---|---|
| Trạng thái truyện | `stories/<slug>/tasks.json` | produce.py | produce.py, người/AI vận hành | `slug, title, source_sha, settings{}, parts[{id, chars, seed, voice{status, attempts, error}, video{...}}], final{file, seconds}`; status: `todo\|running\|done\|failed` |
| Phần truyện | `stories/<slug>/parts/NNN.txt` | produce.py | tts.py | text thuần tiếng Việt |
| Phụ đề theo câu | `stories/<slug>/audio/NNN.srt` | tts.py | produce.py (ghép) | SRT chuẩn, mỗi mục = 1 câu |
| Kế hoạch hoạt hình | `stories/<slug>/video/NNN.plan.json` | reel.py | reel.py | `seed, duration, acts[{start, end, scene, tint, cast[{actor, outfit}], beats[{start, end, kind, shot, move, subject, seed}]}]` |
| Bản thiết kế nhân vật (`avatar`) | `assets/actors/<id>/avatar.yaml` | trang tạo nhân vật, AI | avatar.py | `head, eyes, mouth, nose, extras[], skin, body{outfit, build, colors{gốc: mới}}, look` |
| Thẻ diễn viên (`actor_card`) | `assets/actors/<id>/card.yaml` | new_actor.py, avatar.py | puppet.py, validate_actor.py | `id, kind: actor, rig, heads{biểu cảm: file}, outfits{id: {desc, bodies{tư thế: file}}}, gender, age, look` |
| Bộ rig diễn viên (`actor_rig`) | `rig:` trong card.yaml | new_actor.py | puppet.py, validate_actor.py | `mode (chibi\|semi\|real), head_scale, overlap, chin_up, head_dx, neck_dx{}, hair_back, hands{}` |
| Kho bộ phận | `assets/parts/parts.yaml` + `INDEX.md` | (tạo một lần, script cũ ở nhánh main) | avatar.py, AI | `{id: {file, kind, desc}}` |
| Thẻ nền | `assets/scenes/<id>/card.yaml` | make_scene_sheet.py, người | reel.py | `id, tags[], master, ground_y` |
| Đạo cụ | `assets/props/props.yaml` | (tạo một lần) | puppet.py | `{id: {file, size, grip[x,y], mirror}}` |

**Giá trị đóng dùng chung:**
- tư thế: `relaxed | hips | phone | point`
- biểu cảm: `neutral | smirk | shocked | angry | sad`, cộng biến thể `_talk` và `blink` do máy tự chọn
- chế độ rối: `chibi | semi | real` (dải tỉ lệ đầu: chibi 0,30–0,60; semi 0,18–0,30; real 0,12–0,18)
- vóc: `thin | normal | fat`
- vi kịch bản hoạt hình: khoá của `BEATS` trong `src/studio/reel.py`

## 3. Thêm loại dữ liệu mới
1. Khai báo trong `CONTRACTS` (`src/contracts.py`).
2. Thêm một dòng vào bảng §2.
3. Gọi `require()` ở chỗ nhận dữ liệu.
