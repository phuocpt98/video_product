# Giao thức dữ liệu giữa các phòng, công cụ và agent

Cập nhật: 28/9/2026 · Code kiểm: `src/contracts.py` (khi sửa, sửa cả hai nơi). Kiểm tay: `python -m src.contracts <loại> <file>`

## 1. Nguyên tắc
1. **Mỗi loại dữ liệu trao tay có một hợp đồng:** tên trường, kiểu, giá trị cho phép. Người gửi làm đúng; **người nhận luôn kiểm** bằng `check()`/`require()`, sai thì báo lỗi rõ, không chạy lệch.
2. **AI không bao giờ được tin thẳng.**
   - Câu trả lời của AI phải ở dạng máy đọc được: JSON (ưu tiên, bật chế độ JSON của API) hoặc YAML trong khối ```yaml.
   - Kiểm cả **trường sai kiểu** (số thay cho danh sách, danh sách thay cho chuỗi), không chỉ trường thiếu.
   - Câu trả lời bị cắt giữa chừng (hết `max_tokens`) coi là lỗi và chuyển nguồn khác.
   - AI chỉ được chọn trong **danh sách đóng** (tên diễn viên, nền, hành động… có thật trong thư viện).
   - Code kiểm từng trường. Trường sai thì dùng giá trị mặc định hoặc quay về luật từ khoá; không đọc được gì thì thử lại hoặc chuyển nguồn (`pool.py`).
3. **Một đơn vị đếm chung:** "câu" = số thứ tự trong `audio/NNN.srt`, bắt đầu từ 1. Nhãn đạo diễn, phụ đề và kịch bản cảnh đều đếm theo đơn vị này.
4. **File là kênh chung:** dữ liệu nằm trong file YAML hoặc text UTF-8 ở đúng chỗ trong bản đồ thư mục. Không truyền dữ liệu qua chat.
5. **Thời gian tính bằng giây (số thực), tỉ lệ khung tính từ 0 đến 1, id viết không dấu, ngăn bằng gạch ngang.**

## 2. Các hợp đồng

| Loại | File | Ai ghi | Ai đọc | Trường chính |
|---|---|---|---|---|
| Kịch bản chương | `stories/<slug>/script/NNN.txt` | Biên kịch (run.py) | giọng đọc, Đạo diễn | text thuần tiếng Việt, không markdown, thoại trong ngoặc kép |
| Phụ đề theo câu | `stories/<slug>/audio/NNN.srt` | giọng đọc (tts.py) | Đạo diễn, Dựng | SRT chuẩn, mỗi mục = 1 câu |
| Nhãn đạo diễn (`tag`) | `stories/<slug>/storyboard/NNN.tags.yaml` | Đạo diễn (tagger.py, AI) | direct.py | `{số câu: {scene, present[], speaker, actor, action, expr, fx[]}}` |
| Mục lục truyện (`cast`) | `stories/<slug>/cast.yaml` | Thiết kế/Điều phối | direct.py, bảng việc | `lead`, `characters{tên: {actor, outfit, names[], by_scene{nền: {actor, note}}}}`, `scenes{nền: [từ khoá]}`, `chapters{số: {scene}}` |
| Kịch bản cảnh (`storyboard`) | `stories/<slug>/storyboard/NNN.yaml` | direct.py | stage.py | `audio`, `cast{khoá: {actor, outfit}}`, `shots[{start, end, background, cam{zoom[a,b]}, actors[{who, pose, expr, x, height, talk, flip, action, prop, fx[]}], extras{n, seed, exclude[]}, screen[]}]`, `subs[{start, end, text}]` |
| Bản thiết kế nhân vật (`avatar`) | `assets/actors/<id>/avatar.yaml` | trang tạo nhân vật, Thiết kế (AI) | avatar.py | `head, eyes, mouth, nose, extras[], skin, body{outfit, build, colors{gốc: mới}}, look` |
| Thẻ diễn viên (`actor_card`) | `assets/actors/<id>/card.yaml` | new_actor.py, make_actor.py | stage.py, validate_actor.py | `id, kind: actor, rig, heads{biểu cảm: file}, outfits{id: {desc, bodies{tư thế: file}}}, gender, age, look, signature, roles[], notes, made_by` |
| Bộ rig diễn viên (`actor_rig`) | `rig:` trong card.yaml | new_actor.py | stage.py, validate_actor.py | `mode (chibi\|semi\|real), head_scale, overlap, chin_up, head_dx, neck_dx{}, hair_back, hair_back_chin, hands{}` |
| Việc (`task`) | `board/tasks/<id>.yaml` | mọi phòng | mọi phòng | `id, from, to, type, key, need, status, waiting_on[], log[], story, chapter, data{}` |
| Kho bộ phận | `assets/parts/parts.yaml` + `INDEX.md` | make_parts.py | avatar.py, AI Thiết kế | `{id: {file, kind, desc}}`; `INDEX.md` là mục lục có chú thích cho AI |
| Thẻ nền | `assets/scenes/<id>/card.yaml` + `INDEX.md` | make_scene_sheet.py, bảng việc | direct.py, stage.py | `id, tags[], master, ground_y, crowd` |
| Đạo cụ | `assets/props/props.yaml` | make_props.py | stage.py | `{id: {file, size, grip[x,y], mirror}}` |

**Giá trị đóng dùng chung:**
- tư thế: `relaxed | hips | phone | point`
- biểu cảm: `neutral | smirk | shocked | angry | sad`, cộng biến thể `_talk` và `blink` do máy tự chọn
- chế độ rối: `chibi | semi | real`. semi = đầu ≈ 1/4,5 chiều cao người, dải head_ratio 0,18–0,30; real 0,12–0,18; chibi 0,30–0,60
- vóc: `thin | normal | fat`
- trạng thái việc: `open | doing | blocked | done | rejected`
- hành động và hiệu ứng: xem `ACTIONS`, `EFFECTS` trong `src/studio/actions.py`

## 3. Dạng câu trả lời bắt buộc của AI
| Việc | Dạng | Ví dụ |
|---|---|---|
| Gắn nhãn đạo diễn | JSON `{"tags": [{"i", "scene", "present", "speaker", "actor", "action", "expr", "fx"}]}`, mỗi câu một phần tử | `{"tags": [{"i": 14, "scene": "bus-interior", "present": ["Vương Tử Bác", "Trần Hán Thăng"], "speaker": "Vương Tử Bác", "actor": "Vương Tử Bác", "action": "laugh", "expr": "smirk", "fx": []}]}` |
| Thiết kế nhân vật | một khối ```yaml theo hợp đồng `avatar` | xem `prompts/roles/character-designer.md` |
| Duyệt nội dung | dòng `Kết luận: ĐẠT` hoặc `Kết luận: CHƯA ĐẠT` + danh sách lỗi | run.py đọc bằng regex |

## 4. Thêm loại dữ liệu mới
1. Khai báo trong `CONTRACTS` (`src/contracts.py`).
2. Thêm một dòng vào bảng §2.
3. Gọi `require()` ở chỗ nhận dữ liệu.
