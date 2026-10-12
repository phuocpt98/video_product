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

Client GLM (src/common/llm.py, scripts/glm_mcp.py, .mcp.json): lượt 1 CHƯA ĐẠT, lượt 2 ĐẠT 26/9/2026. 
Pipeline src/run.py: lượt 1 CHƯA ĐẠT, lượt 2 ĐẠT 26/9/2026. Không còn hạng mục chờ duyệt.
