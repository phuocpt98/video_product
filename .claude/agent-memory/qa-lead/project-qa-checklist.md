---
name: project-qa-checklist
description: QA checklist riêng video_reup cho code gọi LLM/MCP (GLM Z.ai) và các bẫy đã gặp khi review
metadata:
  type: project
---

Checklist khi duyệt code gọi LLM / MCP của video_reup:
- Chạy `.venv/bin/pytest` trần ở gốc repo (đã có pytest.ini testpaths=tests); nếu vỡ vì quét `tool/` là hồi quy.
- Gọi API thật ít nhất một lần qua đúng đường dùng thật (cả chế độ `{{text}}` lẫn không). Z.ai trả 400 code 1213 khi message user rỗng — test giả (mock) không bắt được.
- Kiểm tra `finish_reason == "length"` / content None: output bị cắt không được ghi như đã xong.
- Lỗi mạng ngoài URLError (RemoteDisconnected, TimeoutError khi đọc) cũng phải retry.
- `.mcp.json`: chạy `claude mcp list` ở gốc repo; `${CLAUDE_PROJECT_DIR}` KHÔNG có trong env → cảnh báo Missing environment variables.
- Kiểm tra key không lộ: grep tiền tố key trong output/log, không in .env.

**Why:** lần review client GLM 26/9/2026 các lỗi trên đều lọt qua 11 test mock pass.
**How to apply:** mọi lần duyệt code LLM/MCP/API ngoài trong dự án này.

Checklist pipeline src/run.py (agy):
- verdict phải đọc dòng "Kết luận:", không tìm chuỗi "ĐẠT" (vì "KHÔNG ĐẠT" chứa "ĐẠT").
- --force một bước phải làm lại các bước sau nó; cache TTS theo chỉ số câu dễ lệch khi kịch bản đổi.
- Kiểm tra đầu ra LLM rỗng-nhưng-hợp-lệ (parse_json trả {}) không được ghi như đã xong.
- Chặn quota phải chạy trước MỌI bước gọi LLM, không chỉ bước đầu.

Checklist phòng dựng src/studio (direct.py, stage.py, cutout.py):
- Thử chương KHÔNG có trong cast.yaml `chapters:` và thư viện nền rỗng (dựng root giả trong scratchpad, gán D.ROOT). Giá trị None lọt vào tập "thiếu" làm sorted()/join crash.
- Đạo cụ: chưa có assets/props thì tự tạo PNG giả + props.yaml, gán stage.PROPS, ghép figure mọi pose rồi xem ảnh (tư thế hips/relaxed dán lệch).
- Tương thích ngược: dựng tmp/studio_demo/chibi.yaml và scene.yaml (kiểu cũ assets/characters/), so khung với mp4 cũ.
- cutout: cắt lại source/puppet.jpg ra scratchpad, so từng pixel với parts/ đã commit.

Checklist bảng việc / pool / tagger / stage (thêm 28/9/2026):
- board: thử Ctrl+C (KeyboardInterrupt) giữa lúc dựng: việc có kẹt "doing" không; file rác/ảnh hỏng trong board/inbox có làm sập `run --loop` không.
- Parse JSON của AI: thử trường sai KIỂU (int thay list, list thay str) chứ không chỉ thiếu trường; `x in set` với list → TypeError.
- stage chữ ký khung: so khung có cache với khung vẽ lại (đặt _sig=None) trên storyboard tổng hợp đủ ACTIONS/EFFECTS/SCREEN.
- TTS song song: giả gói `vieneu` qua PYTHONPATH (tiến trình con không thấy monkeypatch).
- Không chạy `python -m src.studio.direct ... --clip` trực tiếp: nó GHI ĐÈ storyboard/NNN.yaml của truyện; dựng clip bằng script riêng trong scratchpad.

Phòng dựng (880816e, 9ab02ff): lượt 1 CHƯA ĐẠT 27/9/2026 (crash chương ngoài cast.chapters). Chờ duyệt lại.
Lô 57e752d..b9afa8a (board, pool, tagger, contracts, tts song song, stage quay đôi, run fast): lượt 1 CHƯA ĐẠT 28/9/2026 (doing kẹt, tagger crash sai kiểu, inbox ảnh hỏng, protocols.md lệch JSON). Chờ duyệt lại.

Checklist diễn viên rối v2 (segment/new_actor/validate_actor, thêm 13/10/2026):
- Ghép thử bằng stage.Puppet (validate_actor.preview) chứ không chỉ đo từng lớp: `overlap` trong stage nhân với CHIỀU CAO KHUNG đầu, khung head_front có tóc dài nên cao gấp ~3 lần đầu → đầu lún, mất cổ.
- halo_ratio luôn 0 với lớp đã defringe (pixel bán trong suốt bị đổi màu): đo thêm pixel ĐỤC sát mép có min(RGB)>235.
- Vòng làm lại của Muse: thay source/master.png rồi chạy lại phải cắt lại (cache theo file tồn tại dễ giữ bộ phận cũ).
- Ảnh không có da / ảnh trắng: phải ra CHƯA ĐẠT, không traceback.

- Cắt lại thất bại giữa chừng (master mới hỏng): card.yaml cũ có còn trỏ tới bộ phận đã xoá không; ảnh expr_/pose_ sinh từ master cũ có bị dùng lại không.
- Đo B1 bằng công thức stage: chin_fig = hy0 + anchor_y, đỉnh cổ = neck_top(body).y − top; khoảng cách ≈ 0.12 × (chin_y − head_box[1]).

Checklist nhập truyện (src/drama.py import, thêm 13/10/2026):
- Thử trên slug zz-story rồi xoá, KHÔNG --force trên truyện thật (ghi đè cast.yaml đã gán diễn viên).
- So nội dung script/ gộp với nguồn bỏ dòng đánh số: phải bằng nhau từng ký tự (không mất chữ).
- src.run mode none: kiểm bằng stub voice_step/card_step trong scratchpad, không chạy thật.

Rối v2 + drama import: lượt 1 CHƯA ĐẠT, lượt 2 ĐẠT 13/10/2026 (còn nên sửa: card.yaml cũ sau cắt lại hỏng, --force ghi đè cast.yaml, docs chưa nhắc import).

Client GLM (src/common/llm.py, scripts/glm_mcp.py, .mcp.json): lượt 1 CHƯA ĐẠT, lượt 2 ĐẠT 26/9/2026. 
Pipeline src/run.py: lượt 1 CHƯA ĐẠT, lượt 2 ĐẠT 26/9/2026. Không còn hạng mục chờ duyệt.

Checklist dây chuyền src/produce.py + reel.py (nhánh plan-muse, thêm 14/10/2026):
- Làm tiếp (`run --slug`) phải nhận thay đổi config.yaml (tts_workers/video_workers/retries): settings lưu trong tasks.json dễ che config. Kiểm bằng stub do_voice/do_video trong scratchpad, gán P.STORIES.
- Đổi --size/--voice giữa chừng: ffmpeg concat -c copy khác độ phân giải vẫn exit 0, ra file hỏng im lặng.
- File mới trong tests/ (.md) phải qua hook check_file_placement (chạy hook bằng JSON stdin).
- grep tham chiếu module đã xoá phải dùng `rtk proxy grep` (rtk lọc bớt kết quả), và quét cả docs/plans/collab-protocol.md (Muse đọc).
- Ép nhánh Linux của reel: gán reel.sys giả platform=linux rồi render thật (libx264).

Dây chuyền mới produce/reel (plan-muse, staged): lượt 1 CHƯA ĐẠT 14/10/2026; lượt 2 CHƯA ĐẠT 14/10 (chỉ còn: read_story thử utf-16 không BOM → file cp1258 độ dài chẵn ra chữ rác im lặng; câu lỗi khoá thiết lập khuyên --redo nhưng kiểm khoá chạy TRƯỚC redo). Lượt 3 (a7c770d): 2 lỗi đó ĐÃ SỬA.
- Thử giải mã nhiều bảng mã: utf-16 không BOM giải mã được MỌI chuỗi byte độ dài chẵn → luôn thử file cp1258 cả độ dài chẵn lẫn lẻ.

Checklist giọng đọc tts.py clean()/chunks() (thêm 14/10/2026):
- Từ điển viết tắt + re.I + \b phá chữ thật: "bít tết"→"biết tết", "Washington DC"→"được", "J. K. Rowling"→"gì", "Ko-rê"→"không-rê" (dấu - là ranh giới \b). Luôn thử danh sách ca: tên riêng viết hoa, từ ghép thật, gạch nối.
- Cắt cụm ở dấu phẩy phải tránh số thập phân kiểu Việt "3,5".
- So chunks với clean() bằng norm bỏ khoảng trắng và dấu chấm (tên chương được thêm "."), chạy trên stories/*/script/*.txt + parts/*.txt.
- Đo loudness bản ghép: lượt 14/10 ra -23,5 LUFS (nhỏ so với YouTube -14).

TTS cách (b) (staged sau a7c770d): lượt 1 CHƯA ĐẠT; lượt 2 CHƯA ĐẠT 14/10 (3 lỗi lượt 1 đã sửa; còn: thư mục chương xếp chữ cái "Chương 10" trước "Chương 2", viết tắt viết hoa mở cả giữa câu "Ông Ko"→"Ông Không", thiếu dòng decisions cho "truyện thuần không lời bình"). Lượt 3 ĐẠT 14/10/2026.
- Nhận thư mục file: luôn thử tên không đệm số (1, 2, 10) để bắt sắp xếp theo chữ cái.
