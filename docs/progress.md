# Tiến độ

Cập nhật: 15/10/2026

Cập nhật cuối mỗi nhiệm vụ (hiến pháp §4 bước 6). Mục "Đã xong" chỉ giữ khoảng 15 việc gần nhất.

## Đang làm
- **15/10/2026 (nhánh `youtube-long`): bản dài ngang YouTube `python -m src.longform <slug>...`** (yêu cầu [YEUCAAU-PIPELINE-MOI.md](YEUCAAU-PIPELINE-MOI.md) §3). Dùng lại giọng các chương đã làm, vẽ lại hình 1920x1080 theo plan.json bản dọc, ghép 1 video + .srt + youtube.md; ảnh bìa phủ 3 giây đầu; chạy lại = làm tiếp. Test 2 chương/4 phần: 1,3 phút video mất 29 giây, hình = giọng 80,79 giây, mono, khớp giọng từng phần (lag 0). qa-lead lượt 1 CHƯA ĐẠT (thiếu kiểm .srt, chưa ghi quyết định) → đã sửa. Cũng sửa: `tts.py` của Muse làm hỏng giọng trên Mac, `add_intro.py` nhận khổ ngang (đã push `plan-muse`). Còn lại của yêu cầu (đăng TikTok/YouTube/Facebook, Drive, dọn rác) chưa làm. Ghi chú qa-lead: wav TTS đang 192 kHz (thừa), cảnh cận đôi khi cắt đỉnh đầu (reel).
- **14/10/2026: prompt làm sạch + lọc vi phạm `prompts/story_narration.md` (Người sáng lập: truyện thuần, không viết lại, không lời bình; tên kênh "Khoai Tây").** Thử trên 2 truyện của Người sáng lập (`tmp/test_truyen/`) bằng agy Gemini 3.8 Flash (~2 phút/chương): so từng từ với bản gốc, giữ nguyên 99,9% và 97,4%; chỉ bỏ rác (giới thiệu tuyển tập, chữ Hán, 【】, số mục), sửa khoảng trắng trước thoại, 1 chỗ vi phạm ("ôm con nhảy lầu" → "nghĩ quẩn"), nêu "con súc sinh"/"đồ khốn nạn" để xem lại. `produce` nhận thư mục chương + `--title`, tự bỏ phần `=== BÁO CÁO KIỂM DUYỆT ===`. Sửa 3 lỗi qa-lead ở `tts.clean` ("bít tết", "DC", "J", "Ko-rê", "(28)", cắt "3,5") + chuẩn độ to -16 LUFS. 40 test pass. qa-lead lượt 3 ĐẠT (41 test).
- **14/10/2026: giọng đọc cách (b) cắt cụm (Người sáng lập chốt).** Thí nghiệm 3 cách trên cùng đoạn 1435 ký tự (`tmp/voice_exp/`): tốc độ (19,5–21,9 giây) và âm thanh đo được (số chỗ nghỉ, độ đều âm lượng) gần như nhau; (a) cũ dính câu sau ngoặc kép. `tts.py` mới: làm sạch (ký hiệu trang trí, link, emoji, viết tắt chat; số/ngày/tiền để VieNeu tự đọc, đã kiểm bộ chuẩn hoá của nó), cụm 40–250 ký tự, nghỉ theo dấu câu, cắt lặng + cân âm lượng. `infer_batch` không nhanh hơn trên CPU (ONNX tuần tự). README thêm §0 quy trình vận hành ai làm gì. Chạy thật 2 phần 3500 ký tự: 2,4 phút video mất 1,4 phút. 37 test pass.
- **14/10/2026 (nhánh `plan-muse`): dây chuyền mới gọn cho mọi AI chạy.** `python -m src.produce run <truyện.txt|.md|.docx>`: chia phần (~2500 ký tự, theo tên chương) → giọng VieNeu → hoạt hình ngẫu nhiên → trạng thái `tasks.json`, việc lỗi thử lại, chạy lại = làm tiếp, `--redo` → ghép `output/<slug>.mp4` + `.srt` + `upload.md`. Chạy thật truyện thử 3 phần: 2,4 phút video mất 1,6 phút; giả lập giọng sai → phần 2 `failed`, các phần khác vẫn xong, sửa giọng chạy lại → ghép đủ. **Hướng dẫn vận hành gộp vào `README.md` gốc** (cài Mac/Ubuntu, chạy, lỗi, bổ sung kho), xoá `docs/setup.md`. Đã xoá (vẫn còn ở nhánh main): dây chuyền viết lại AI (run.py, drama.py, board.py, llm/pool), dàn cảnh theo truyện (stage/direct/tagger/actions), script cũ, 10 kế hoạch cũ, clip game. `Puppet` tách sang `src/studio/puppet.py`. 32 test pass. qa-lead: lượt 1 CHƯA ĐẠT (7 lỗi), lượt 2 CHƯA ĐẠT (2 lỗi nhỏ: đọc cp1258, câu báo lỗi) → đã sửa + có test; theo qa-lead sửa 2 lỗi này là đủ ĐẠT, chưa chạy lượt 3. Thí nghiệm giọng 3 cách: tmp/voice_exp/ (chờ Người sáng lập nghe). Còn treo: vai trò `llm-runner` mất công cụ (llm.py đã xoá), chờ Người sáng lập cho cắt; nghiên cứu giọng đọc (lượt sau).
- **14/10/2026: hướng mới, hoạt hình nền NGẪU NHIÊN (Muse làm kém → bỏ hình khớp truyện).** Truyện chữ → giọng → hình random (không khớp truyện, chỉ giữ mắt), không phụ đề trên hình (chỉ .srt). Nghiên cứu: [research/2026-10-14-random-animation.md](research/2026-10-14-random-animation.md) (bản agy Gemini để ở `tmp/`). Đo lõi vẽ khi máy quay chạy liên tục, 1 nhân, 1080p: Pillow 24 ms/khung, **pygame (SDL dummy, không màn hình) 6,9 ms**, OpenCV 35 ms; HTML + Chrome quay màn hình chậm khoảng 10 lần → bỏ HTML. Đã làm `src/studio/reel.py`: hồi ~1 phút (nền + 2–3 diễn viên + tông ngày/hoàng hôn/đêm), nhịp 5–9 giây (17 vi kịch bản: sét đánh hoá bóng đen, đuổi, nhảy, ngã sao xoay, xoay vòng, điện thoại, ngủ Zzz, tim…; góc toàn/trung/cận + đẩy/kéo/lia), nhép miệng theo giọng, dải màu chuyển hồi, ghi `.plan.json` (seed). Demo: `tmp/reel/demo_16x9.mp4` (150 giây dựng 23 giây = 6,4x) và `demo_9x16.mp4` (45 giây). **Chờ Người sáng lập duyệt demo; code CHƯA qua qa-lead, chưa có test.** Tiếp theo: lệnh 1 bước truyện chữ → giọng → reel; thêm tư thế (chạy, nhảy, ngồi, ngã) và nền "đã mắt"; đổi màu áo lúc dựng; đo trên máy Ubuntu 2 nhân (RAM trống ~220 MB là điểm nghẽn).
- **13/10/2026: hệ rối v2 + giao thức ba bên (qa-lead ĐẠT lượt 2, 94 test pass).** Nghiên cứu: [research/2026-10-13-puppet-v2.md](research/2026-10-13-puppet-v2.md) (file "đầu" trong PR #1 là ảnh bán thân, "toàn thân" cắt ở eo). Đã làm: `src/studio/segment.py` (tách lớp bằng màu + hình thái, thử trên ảnh thật: đầu, tóc sau vá kín, thân có mẩu cổ, ghép lại khớp ảnh gốc), `validate_actor.py` + hợp đồng `actor_card`, `scripts/new_actor.py` (ảnh gốc → bộ phận → card `semi`, cắt lại khi đổi ảnh gốc, `--no-gen` liệt kê ảnh thiếu), `prompts/actor_*.md`, `scripts/hub.py` + [plans/collab-protocol.md](plans/collab-protocol.md) (GitHub Issues làm bảng việc chung), `python -m src.drama import` (truyện Gemini → script/cast/story.yaml, `rewrite: none` đi thẳng giọng đọc; đã nhập `ngay-cuoi-doi-dau`, 4 phần 218–670 chữ). **Chưa có ảnh gốc thật**: agy hết lượt ảnh tới ~22h20 13/10; issue #1 giao Muse tạo `uyen-thanh`. **Tiếp theo:** duyệt PR của Muse bằng `validate_actor --preview`; tạo 3 nhân vật còn lại (Tống Hạo, Bà Trương, Liễu Tuyết); thở + tóc lắc trong `stage.py` (research §3); bước nở văn cho truyện nhập ngắn; xoá 4 actor `*-v2` trên nhánh PR #1 khi đóng PR.
- **Tạm dừng (26/9, Người sáng lập yêu cầu): nghiên cứu lại luồng vì quá chậm.** Lô 1 truyện mẫu dừng giữa chừng: chương 2–5 đã ĐẠT, kiểm mạch báo chương 1 LỆCH ("Nhị bản/Nhất bản" chưa đổi), đang viết lại chương 1. Chạy lại `python -m src.run ta-that-su-khong-muon-trong-sinh --chapters 1-5 --render` là làm tiếp. Code dây chuyền theo lô **chưa qua qa-lead**.
- **Số đo lô 1 (5 chương, phần chữ, chưa tính giọng): 28 phút**, trung bình 5,6 phút/chương dù đã chạy 3 chương song song:
  | Bước | Số lần | Trung bình | Tổng |
  |---|---|---|---|
  | viết (Gemini 3.1 Pro) | 6 | 96 giây | 9 phút |
  | viết lại (Opus 4.6) | 3 | 184 giây | 9 phút |
  | soát (Gemini Flash) | 8 | 72 giây | 9 phút |
  | **duyệt (Sonnet 4.6)** | 7 | **153 giây** | **17 phút** |
  | kiểm mạch (Opus 4.6) | 1 | 347 giây | 6 phút |
  Chưa tính: mỗi lần gọi agy còn gọi thêm `agy -p /usage` để kiểm quota (chưa đo). Giọng đọc khoảng 2–3 phút/chương.
- **Hướng tăng tốc đã nghĩ, chưa làm:**
  1. **Kiểm máy theo sổ tay trước khi gọi người duyệt:** danh sách từ cấm lấy từ sổ tay ("Nhất bản", "Nhị bản", "anh"/"hắn" chỉ nhân vật chính, tên Việt hoá). Bắt lỗi rẻ, không tốn một vòng duyệt và viết lại.
  2. **Sửa khoanh vùng thay vì viết lại cả chương:** khi duyệt hoặc kiểm mạch chỉ ra vài câu sai, cho Gemini Flash sửa đúng các câu đó (khoảng 30 giây) thay vì Opus viết lại cả chương (khoảng 3 phút + soát + duyệt lại).
  3. **Gộp soát + duyệt, hoặc duyệt bằng model nhanh hơn:** duyệt là bước chậm nhất (153 giây). Thử Gemini Flash duyệt theo checklist, chỉ khi nghi ngờ mới gọi Sonnet.
  4. **Cache kết quả quota** vài phút thay vì gọi `/usage` trước mọi lần gọi.
  5. **Chạy cả lô cùng lúc** (workers = 5 = cỡ lô), và **đọc giọng ngay khi chương đã ĐẠT**, chạy song song với kiểm mạch (chỉ đọc lại chương bị sửa).
  6. Chế độ viết lại nhẹ: cân nhắc bỏ bước soát riêng, để máy kiểm; chỉ gọi editor khi máy báo lỗi.
- Chờ Người sáng lập: 5 chương truyện mẫu; cài và đăng nhập `agy` nếu muốn dùng gói Gemini Pro

- **8/10/2026: `nguoi-giu-deo` bản 5.** Bản nháp video v4 của Muse: đoạn đầu đẹp, đoạn đánh nhau rời rạc (thiếu 7 cảnh, quay chậm, clip lệch nhau). Học từ báo cáo `docs/research/2026-10-08-ai-action-animation.html` → viết luật `docs/plans/ai-film-rules.md` (chờ chốt, decisions #11), ghi bài học. Kịch bản bản 5: phần đánh 4 khối 13 nhịp, ~1:50, chỉ 5 clip Muse tạo mới (nhịp 3, 5, 6, 11, 12). Muse tạo ảnh, Người sáng lập duyệt, Claude không tạo ảnh cho dự án Muse.
- **7/10/2026: phim ngắn thử nghiệm `nguoi-giu-deo`** (tự sáng tác, 3 phút, hình làm bằng Muse của Meta). Kịch bản `stories/nguoi-giu-deo/script/001.md` ĐẠT content-reviewer (Gemini 3.1 Pro) ở lượt 3; 5 ảnh hình tượng ở `assets/`; cả hai chờ Người sáng lập duyệt. Sửa `src/common/imagegen.py`: agy giờ tạo ảnh qua subagent `image-generator`, prompt cũ cấm subagent nên mọi lần tạo ảnh đều hỏng (chưa qua qa-lead). Còn phải kiểm trong `story.yaml` (`open_checks`): điều khoản thương mại của Meta, watermark, quota, nhạc nền. Đã xoá MCP `glm` (`.mcp.json`, `scripts/glm_mcp.py`, gói `mcp`).

## Tiếp theo
- **Trạng thái 28/9/2026 20:45 (dừng theo lệnh Người sáng lập):**
  - `thien-kim-that`: xong trọn bộ, đã tăng tốc 1,2× (full 29:25, TikTok 4:05, .srt, thumbnail, `upload.md`), chờ đăng. `vo-cao-tay` cũng đã tăng tốc (full 27:23, TikTok 3:28).
  - `trong-sinh-vo-on`: đã viết 6 phần; phần 4 bị chấm CHƯA ĐẠT nhiều vòng (viết lại liên tục từ 19:50 đến 20:40), chưa lồng tiếng. Xem nguyên nhân trước khi chạy tiếp: `python scripts/drama_pipeline.py trong-sinh-vo-on --parts 6 --full`.
  - Lô drama 2: kế hoạch plans/drama-batch-2.md (đã xoá ở nhánh plan-muse) chờ Người sáng lập chốt (đường A/B, thứ tự, xem trước sổ tay).
  - Chốt mới hôm nay: giọng đọc 1,34× (video vẫn 24 hình/s), TikTok tối đa 5 hashtag, drama kiểm mạch 1 vòng, mũi nữ nose8 / nam nose7 tô theo màu da.
  - Kênh gforce.vn: TikTok chặn đọc tự động; chờ Người sáng lập gửi video lưu về hoặc ảnh chụp kênh.
  - Code quy trình chạy đến cuối (duyệt không chặn, `make_tiktok.py --auto`, `make_upload.py`) CHƯA qua `qa-lead`.
  - Ảnh: agy hết lượt ảnh tới ~16h 3/10; việc còn lại ở `board/image_queue.yaml`.
- **Cải tiến cho video sau (Người sáng lập chốt 28/9/2026, sau khi đăng "Rút Củi Đáy Nồi"):**
  - Nối 15 giây kết (nền kênh + linh vật, không phụ đề) vào cuối video full để đặt màn hình kết thúc YouTube.
  - Xem vài khung hình mỗi phần trước khi ghép bản full (lần này mẹ chồng lên hình như cụ già trọc do đầu `head-old-f`; đã ghi cảnh báo vào `assets/parts/INDEX.md` và vai trò thiết kế nhân vật).
  - Mỗi truyện có `output/upload.md` (tiêu đề, mô tả, mốc phần, thẻ, .srt, thumbnail `make_thumbnail.py drama`); nhắc: không dành cho trẻ em, bật bình luận, danh mục Giải trí.
  - Script dọn rác `scripts/clean_story.py` (giữ tập ngắn `studio_NNN` cho TikTok): để sau.
0. **Dựng đội agent trên agy** theo [plans/agent-team.md](plans/agent-team.md) §6: giai đoạn 0 kiểm agy → 1 runner và vai trò → 2 nghiên cứu thị trường → 3 thí nghiệm 5 chương.
1. Người sáng lập gửi truyện mẫu (câu 5) và mẫu phong cách (câu 6). Claude tìm bản gốc tiếng Trung.
2. Thí nghiệm 5 chương: Claude rã truyện và viết lại làm bản chuẩn → `llm-runner` chạy GLM với cùng việc, chia nhỏ → so sánh, tối ưu prompt. Chốt video nền từ game (câu 10).
3. **Thử viết lại 5 chương** và **MVP tuần 1** theo plans/technical.md (đã xoá ở nhánh plan-muse) §5. Luồng giao việc: `architect` lên kế hoạch và tiêu chí → `developer`/`tester` làm → `qa-lead` duyệt.

## Đã xong
- 28/9/2026: **Tăng tốc + phòng ban:** bảng việc `src/board.py` (dựng thiếu diễn viên/nền thì treo và mở việc; phòng Thiết kế tự ghép diễn viên bằng agy); trang tạo nhân vật (`scripts/character_maker.py`); kho 112 bộ phận mặt + 24 bộ đồ × 3 vóc; 24 nền đô thị; đạo diễn gắn nhãn (`tagger.py`, Gemini API qua `pool.py`); quần chúng (16 người ghép từ kho); hợp đồng dữ liệu (`src/contracts.py`, `docs/plans/protocols.md`). **Số đo chương 1** (6,3 phút video): giọng 58 giây (3 tiến trình), gắn nhãn 50–150 giây, dựng 53 giây (quay đôi, CPU giảm 4,3 lần). **Chữ chế độ nhanh**: 5 chương khoảng 6–7 phút (trước 28 phút), cả 5 ĐẠT → bật mặc định. Chưa qua qa-lead: board, tagger, pool, contracts, tts song song.
- 28/9/2026: **Thư viện 24 đạo cụ** (`assets/props/`, bảng tạo trên web, cắt sạch, dán vào tay đã thử). **Tiếp theo:** tạo diễn viên chính bằng `python scripts/make_roster.py nam-18-b nu-18-a nu-28-a nu-45-a nam-48-a nam-18-c nam-50-a nam-35-a` (agy hết lượt ảnh 429 đêm 27/9, chưa tạo được ai; make_actor lấy bảng rối nam-18-a làm mẫu nét vẽ).
- 27/9/2026: **Đạo diễn bằng luật** `python -m src.studio.direct <slug> <chương> [--clip a-b] [--render]`: chương 1 ra 84 cảnh (trung bình 4,5 giây), demo 26 giây `tmp/direct_clip/clip_1920x1080.mp4` dựng mất 41 giây. Sân khấu đổi nền theo cảnh, dán đạo cụ vào tay. Chờ: bảng 24 đạo cụ (agy hết lượt ảnh, Người sáng lập tạo trên web), diễn viên nhóm 1, 4 nền chương 1. qa-lead CHƯA ĐẠT lần 1 (2 lỗi crash khi thiếu nền), đã sửa và chạy lại bằng script tái hiện của qa-lead.
- 27/9/2026: **Diễn viên chibi đầu tiên `nam-18-a`** (ảnh Người sáng lập tạo trên web Gemini): cắt 8 đầu + 4 thân, ráp đầu che cổ, lộ vai, dựng thử 18 giây `tmp/studio_demo/chibi_1920x1080.mp4`. `cutout.cut` giờ tách theo mảng liền (hàng đầu và hàng thân dính nhau vẫn cắt đúng); thân relaxed hở viền cổ áo phải vẽ nối tay. Prompt thân trong `make_actor.py` thêm yêu cầu viền cổ áo kín, có vai và tay áo.
- 26/9/2026: **Pipeline `python -m src.run <slug> --chapters a-b [--render]`**, chờ `qa-lead` duyệt. Mỗi chương: rã (agy) → cập nhật bảng đổi tên → viết → soát + kiểm máy → duyệt (CHƯA ĐẠT thì viết lại bằng model cao hơn) → giọng VieNeu; `--render` ghép thành 1 video kèm file mốc chương. Chạy thật chương 1–3 truyện mẫu: khoảng 9,5 phút/chương (agy ~7 phút + giọng ~2 phút), cả 3 ĐẠT ngay lần đầu, video 17,1 phút. 29 test pass.
- 26/9/2026: Mọi thứ tải về cho dự án nằm trong repo (git bỏ qua): model AI ở `.cache/huggingface/` (code tự đặt `HF_HOME`), thư viện ở `.venv/`. Máy mới: `bash scripts/setup.sh`, hướng dẫn ở setup.md (đã xoá ở nhánh plan-muse).
- 26/9/2026: **Cài VieNeu-TTS v3 Turbo** (chạy local, Apache-2.0, `pip install vieneu`), tạo nhanh gấp khoảng 4 lần thời gian thực trên CPU Mac.
  - Lỗi đã gặp: onnxruntime 1.30 từ chối file model vì HuggingFace lưu dạng symlink ("External data path escapes model directory"). Cách sửa đã đưa vào `scripts/setup_models.py`.
  - Mẫu 4 giọng nữ Bắc (Ngọc Huyền, Trúc Ly, Quỳnh Anh, Ngọc Linh; bản thường và bản tăng tốc x1.4) nằm trong `stories/ta-that-su-khong-muon-trong-sinh/audio/voice_samples/`.
- 26/9/2026: **Bản mẫu 1 chương chạy đủ luồng** (truyện 我真没想重生啊, `stories/ta-that-su-khong-muon-trong-sinh/`):
  - agy tự đọc chương 1 trên m.qidian.com rồi lập thẻ chương (Gemini 3.8 Flash); repo không lưu nguyên văn.
  - Viết lại (Gemini 3.1 Pro) → soát văn (Gemini 3.8 Flash) → duyệt (Sonnet 4.6): ĐẠT.
  - edge-tts (chỉ để thử) → video 7 phút, khung tĩnh có linh vật, phụ đề mềm và file .srt.
  - Tốn khoảng 3–4% quota Gemini khung 5 giờ; Claude Code chỉ điều phối.
- 26/9/2026: Nghiên cứu xu hướng lượt 1: 3 báo cáo `trend-scout` + duyệt chéo, cả 3 CHƯA ĐẠT (dẫn nguồn kém, có bịa). Đã siết file vai trò.
- 26/9/2026: Bản đồ thư mục có thêm tầng kênh `channels/<channel>/`, `stories/<slug>/story.yaml` và `assets/` riêng của truyện; kho chung `assets/`. Hook đã nhận đúng đường dẫn mới. Chưa qua QA (gộp vào lượt QA giai đoạn 1).
- 26/9/2026: Client GLM-4.7-Flash: `src/common/llm.py` (hàm + CLI chạy lô, cắt đoạn, log `run.jsonl`), MCP `glm` (`scripts/glm_mcp.py`, `.mcp.json`, cần mở `claude` từ gốc repo và duyệt 1 lần). QA lượt 1 CHƯA ĐẠT (5 lỗi), lượt 2 ĐẠT: 22 test pass, gọi API thật OK. Tuyển vai trò `llm-runner`. Gemini CLI đã ngừng cho gói cá nhân từ 18/6/2026 → cân nhắc Antigravity CLI (`agy -p`).
- 26/9/2026: So sánh model LLM theo giá → [research/llm-models.md](research/llm-models.md). Chưa chạy thử thật; chọn model viết lại sau đợt thử 5 chương. Chốt câu 4, 7, 9 và nền video lặp trong [decisions.md](decisions.md).
- 25/9/2026: Dựng khung studio trong `.claude/`:
  - hiến pháp, sơ đồ tổ chức 7 vai trò
  - playbook giao việc, bộ nhớ quản lý, đặt file
  - hook chặn đặt sai chỗ (đọc bản đồ từ `CLAUDE.md`)
  - 4 skill quản trị: `hire-role`, `retire-role`, `new-project`, `record-lesson`
  - template dự án mới
  - QA: lượt 1 CHƯA ĐẠT (9 lỗi nhỏ và vừa, đã sửa hết); lượt 2 kiểm bằng script: 13/13 mục đạt, 0 link hỏng, hook đúng 11/11 trường hợp
- 25/9/2026: Đổi tên toàn bộ tài liệu và thư mục dự kiến sang tiếng Anh. Gom tài liệu vào `docs/plans/`, `docs/research/`.
- 25/9/2026: Nghiên cứu repo tạo video AI và dịch vụ AI trả phí (Motion Studio, Kling, Hailuo, Veo, TTS Việt). Phát hiện edge-tts không được dùng thương mại và rủi ro bản quyền truyện dịch.
- 25/9/2026: Nghiên cứu 6 repo viết truyện bằng AI (clone vào `tool/`). Thiết kế lại Bước 2–3 theo cách 拆书 + 仿写.
- 25/9/2026: Rà repo cũ `tiktok_content`, rút bài học và danh sách module dùng lại.
- 23/9/2026: Phân tích 6 kênh đối thủ, viết kế hoạch kênh và kế hoạch kỹ thuật.
