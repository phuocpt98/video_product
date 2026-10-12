# Kế hoạch đội agent: Claude dẫn dắt, đội agy làm

Cập nhật: 26/9/2026 · Sơ đồ trực quan: [agent-team.html](agent-team.html) (mở bằng trình duyệt)

## 1. Nguyên tắc

- **Hai nguồn quota:**
  - Gói **Gemini Pro cá nhân**, dùng qua `agy`: dùng thoải mái, ưu tiên trước. Gói có cả Gemini, Claude 4.6 và GPT-OSS.
  - **Claude Code** là gói chung của team: chỉ dùng cho việc quan trọng.
- **Claude Code là trưởng nhóm, đội agy là nhân viên:**
  - Điều phối (Claude Code) lên ý tưởng, kế hoạch và tiêu chí, chia việc thành brief nhỏ, rồi duyệt mẫu.
  - Nhân viên trên agy làm theo brief, ghi kết quả ra file.
- **Không tin mặc định một model:**
  - Mỗi vai trò có **thang model**. Kết quả không đạt thì leo thang lên model mạnh hơn.
  - Việc quan trọng (code, kịch bản đăng kênh) luôn có một lượt duyệt độc lập bằng model khác model đã làm.
- Khi Người sáng lập nói **"gói Pro"**, nghĩa là gói Gemini Pro cá nhân (agy).

## 2. Đội hình

| Tầng | Vai trò | Việc chính | Model mặc định → leo thang | Được ghi vào |
|---|---|---|---|---|
| Dẫn dắt (Claude Code) | Điều phối | Ý tưởng, kế hoạch, chia việc, duyệt mẫu, quyết định cùng Người sáng lập | Claude Opus 5.5 | Toàn repo |
| Dẫn dắt (Claude Code) | `qa-lead` | Cổng chất lượng cho **code pipeline và thay đổi cấu trúc** | Claude Opus (subagent) | Chỉ bộ nhớ QA |
| Dẫn dắt (Claude Code) | `architect` | Kế hoạch kỹ thuật lớn. Hiếm khi gọi | Claude Opus (subagent) | `docs/` |
| Nghiên cứu (agy) | `trend-scout` | Xu hướng YouTube, TikTok Việt Nam, Douyin, Bilibili; truyện đang lên; đối thủ mới | Gemini 3.1 Pro high → Opus 4.6 | `docs/research/trends/` |
| Nghiên cứu (agy) | `source-finder` | Tìm bản gốc tiếng Trung từ video hoặc tên truyện. Tìm nhạc và clip được dùng thương mại | Gemini 3.8 Flash high → Gemini 3.1 Pro high | `stories/<slug>/source/`, `docs/research/trends/` |
| Sản xuất (agy) | `story-analyst` | Rã truyện: thẻ chương, nhân vật, mô-típ, bảng đổi tên | Gemini 3.8 Flash medium → Gemini 3.1 Pro high | `stories/<slug>/outline/` |
| Sản xuất (agy) | `scriptwriter` | Viết lại chương thành kịch bản kể theo thẻ phong cách | Gemini 3.1 Pro high → Opus 4.6 | `stories/<slug>/script/` |
| Sản xuất (agy) | `editor` | Soát văn AI: lặp ý, sáo rỗng, markdown lọt vào, tên còn phiên âm Trung | Gemini 3.8 Flash high → Sonnet 4.6 | `stories/<slug>/script/` (bản sửa) |
| Sản xuất (agy) | `packager` | Tiêu đề, mô tả, câu móc TikTok, ý tưởng thumbnail | Opus 4.6 → Sonnet 4.6 | `stories/<slug>/output/` |
| Sản xuất (agy) | `content-reviewer` | **Cổng nội dung:** chấm kịch bản và báo cáo theo tiêu chí, kết luận ĐẠT hoặc CHƯA ĐẠT | Sonnet 4.6 → Opus 4.6 (chỉ duyệt cuối, việc quan trọng) → Điều phối (Claude Code) | File review cạnh sản phẩm |
| Kỹ thuật (agy) | `coder` | Viết code theo kế hoạch và brief của Điều phối | Opus 4.6 → Sonnet 4.6 → Gemini 3.1 Pro high | Chỉ các file ghi trong brief (`src/`, `scripts/`, `tests/`) |
| Kỹ thuật (agy) | `test-writer` | Viết test theo tiêu chí trong brief. Script sẽ chạy test | Sonnet 4.6 → Gemini 3.1 Pro high | `tests/` |
| Vận hành kênh (script + agy) | `channel-manager` | Tải video lên YouTube ở chế độ **Riêng tư** kèm tiêu đề, mô tả, thumbnail, chapter, playlist; kéo số liệu hằng ngày; viết báo cáo tuần; tóm tắt bình luận và gợi ý trả lời | Script (không dùng LLM) cho đăng video và số liệu; Gemini 3.1 Pro high → Opus 4.6 cho báo cáo | `data/tracking.csv`, `docs/research/trends/` (báo cáo kênh) |
| Dự phòng (Claude Code) | `developer`, `tester`, `researcher`, `operator`, `product-lead`, `llm-runner` | Chỉ gọi khi đội agy làm hỏng 2 lần hoặc việc cần suy luận sâu | sonnet, haiku, opus | Theo file vai trò |
| Máy (không dùng LLM) | Runner, pipeline | Gọi agy/GLM, chọn model, leo thang, ghi log quota; TTS, ffmpeg, dựng video | — | `stories/<slug>/` |

## 3. Chuyển model

- **Trong gói Pro (agy):**
  - Tự do. Mỗi lần gọi chọn model riêng.
  - Thang model của từng vai trò nằm trong `config.yaml` (mục `agents:`), sửa lúc nào cũng được.
- **Sang GLM (Z.ai):**
  - Tự do, vì miễn phí.
  - Dùng khi quota agy gần hết (dưới 10%), hoặc cho việc máy móc số lượng lớn.
- **Lên Claude Code (gói team):**
  - Không tự động. Runner dừng lại và báo Điều phối.
  - Điều phối quyết định tự làm, gọi subagent dự phòng, hay sửa brief rồi cho agy làm lại.
- **Khi nào leo thang tự động:**
  - Kết quả sai định dạng: JSON hỏng, rỗng, bị cắt.
  - Kết quả trượt kiểm tra bằng máy: độ dài, tên Trung còn sót, có markdown.
  - `content-reviewer` chấm CHƯA ĐẠT 2 lần liền.
  - Mỗi lần leo thang đều ghi vào log.
- **Duyệt chéo:** model duyệt phải khác model đã làm. Ví dụ Gemini viết thì Opus 4.6 duyệt; Opus 4.6 viết code thì `qa-lead` của Claude Code duyệt.

## 4. Cơ chế kỹ thuật

- **Định nghĩa vai trò agy:**
  - Mỗi vai trò có một file `prompts/roles/<vai-tro>.md` gồm nhiệm vụ, quyền, định dạng đầu ra, và mục "không được làm".
  - Thang model nằm trong `config.yaml`.
- **Runner:** `python -m src.agents.run <vai-tro> --brief <file> --out <thư mục>`. Mỗi lần chạy:
  1. Ghép file vai trò với brief.
  2. Gọi `agy -p` với model mặc định.
  3. Kiểm tra kết quả, leo thang khi cần.
  4. Ghi `run.jsonl`: model đã dùng, token, % quota trước và sau, các lần leo thang.
- **Giới hạn quyền của agy** (đã kiểm chứng ngày 26/9/2026):
  - Ở chế độ không tương tác (`-p`), agy **tự từ chối mọi lệnh ghi file và mọi lệnh shell**, kể cả ghi trong thư mục làm việc (lỗi "headless mode cannot prompt… auto-denied").
  - Vì vậy agy **chỉ trả về chữ**: nội dung đầu vào đưa thẳng trong prompt, runner ghi kết quả ra đúng file.
  - Không thêm quyền ghi cho agy. Không dùng `--dangerously-skip-permissions`. Luôn bật `--sandbox` và chạy trong một thư mục trống.
  - `coder` trả về nội dung file trong khối có đánh dấu; runner ghi các file đó (chỉ những file có trong brief), rồi chạy test.
  - **Đọc web:** `search_web` được phép sẵn, còn đọc nội dung trang (`read_url`) cần quyền theo **từng tên miền**, cú pháp `read_url(<tên miền>)`; không dùng `read_url(*)`. Thiếu quyền thì agy bị từ chối và trả về rỗng; đây là nguyên nhân lỗi trả về rỗng gặp trước đó. Danh sách tên miền nghiên cứu nằm trong `~/.gemini/antigravity-cli/settings.json` (`permissions.allow`), thêm khi cần.
  - Bản tạm: `scripts/agy_run.py` (file vai trò + brief → gọi agy trong thư mục trống → ghi báo cáo và `.run.jsonl`).
- **Luồng một việc:**
  1. Điều phối viết brief, dùng mẫu trong [delegation.md](../../.claude/company/playbooks/delegation.md).
  2. Runner chạy vai trò trên agy.
  3. Script kiểm tra bằng máy.
  4. Người duyệt chấm: `content-reviewer`, hoặc `qa-lead` nếu là code.
  5. Điều phối đọc bản tóm tắt và vài mẫu, rồi báo Người sáng lập.

## 4b. Hàng đợi việc và worker (dùng khi sản xuất hàng loạt; Người sáng lập đã đồng ý thiết kế ngày 26/9/2026, chưa làm)

- **Hàng đợi `jobs/`:**
  - Các thư mục `pending/`, `running/`, `done/`, `failed/`, mỗi việc là 1 file JSON: vai trò, brief, đầu vào và đầu ra, bậc model đang dùng, `after` (việc phải xong trước), số lần đã thử.
  - `status.md` tự sinh để Điều phối đọc nhanh.
- **Agent giao việc cho nhau:** agent ghi đề xuất việc tiếp theo. Worker kiểm tra (vai trò có trong danh sách cho phép, không có lệnh shell) rồi mới đưa vào hàng đợi. Có mẫu quy trình để tạo cả chuỗi việc cho một truyện.
- **Worker:** launchd gọi `python -m src.agents.worker` mỗi 10 phút. Mỗi lần chạy:
  1. Đọc quota bằng `agy -p /usage`. Kho nào dưới 10% thì nghỉ đến giờ làm mới.
  2. Lấy việc đã đủ điều kiện, chạy tuần tự, có khoá để không chạy đè.
  3. Xử lý lỗi theo loại:
     - Hết quota hoặc 429: trả việc về hàng chờ, không tính là lỗi.
     - Lỗi tạm thời: thử lại tối đa 3 lần, lần sau chờ lâu hơn.
     - Kết quả kém: leo thang model.
     - Hết thang: chuyển vào `failed/` và gửi thông báo macOS.
  4. Khi còn việc và máy đang cắm sạc thì giữ máy thức bằng `caffeinate`.
- **Làm khi nào:** sau khi thí nghiệm 5 chương cho thấy quy trình ổn. Lúc đó thêm `jobs/` vào bản đồ thư mục và cài job launchd.

## 4c. Quản lý kênh YouTube (`channel-manager`, Người sáng lập đồng ý ngày 26/9/2026, làm ở giai đoạn 4)

- **API:** YouTube Data API v3 (tải lên, metadata, playlist, bình luận), YouTube Analytics API và Reporting API (số liệu). Cần một project Google Cloud miễn phí và đăng nhập OAuth một lần bằng tài khoản kênh.
- **Giới hạn** (tra ngày 26/9/2026):
  - Quota mặc định 10.000 đơn vị mỗi ngày. Việc tải video có hạn mức riêng, khoảng 100 lần mỗi ngày.
  - Project **chưa qua kiểm duyệt** thì mọi video tải lên đều bị để ở chế độ Riêng tư. Muốn tải lên công khai phải nộp đơn kiểm duyệt (audit); thời gian chờ từ vài tuần đến vài tháng, không chắc được duyệt. Nguồn: [Google](https://developers.google.com/youtube/v3/guides/quota_and_compliance_audits).
- **Cách làm:**
  - Script tải lên ở chế độ Riêng tư, điền đủ thông tin, rồi báo Người sáng lập.
  - Người sáng lập bấm Công khai hoặc hẹn giờ trong Studio. Đây cũng là bước duyệt trước khi đăng, theo hiến pháp §6.
  - Trả lời bình luận chỉ gửi đi khi Người sáng lập đã duyệt.
- **Số liệu:** kéo hằng ngày vào `data/tracking.csv` (lượt xem, giờ xem, giữ chân, nguồn lưu lượng, đặc biệt là lưu lượng từ TikTok). Báo cáo tuần là đầu vào cho `trend-scout`.
- **Bí mật:** file OAuth và token nằm ngoài git (thêm vào `.gitignore` khi làm), không in ra.
- **TikTok:** Content Posting API phải xét duyệt ứng dụng, chưa duyệt thì bài chỉ ở chế độ riêng tư. Để sau.

## 5. Cổng chất lượng (sửa hiến pháp §5, Người sáng lập đã đồng ý ngày 26/9/2026)

- **Nội dung** (kịch bản, báo cáo nghiên cứu, tiêu đề): `content-reviewer`, chạy Opus 4.6 trên agy.
- **Code pipeline và thay đổi cấu trúc:** vẫn qua `qa-lead` của Claude Code.

## 6. Lộ trình

| Giai đoạn | Việc | Ai làm | Tiêu chí xong |
|---|---|---|---|
| 0. Kiểm agy | ✅ 26/9: chế độ không tương tác từ chối mọi lệnh ghi và lệnh shell; đo quota bằng `agy -p /usage`; JSON trả về cần đọc ở chế độ không chặt (`strict=False`). Còn phải tìm hiểu: tìm kiếm web có lần trả kết quả rỗng | Điều phối | Đã có bằng chứng |
| 1. Runner và vai trò | `src/agents/run.py` và backend agy trong `src/common/llm.py`, mục `agents:` trong `config.yaml`, 9 file `prompts/roles/`, sửa hiến pháp §5 | `coder` (agy) viết, Điều phối lên kế hoạch, `qa-lead` duyệt | Test pass; chạy thật 1 vai trò, có leo thang giả lập; `qa-lead` kết luận ĐẠT |
| 2. Nghiên cứu thị trường | Báo cáo xu hướng đầu tiên, sau đó chạy hằng tuần | `trend-scout`, `source-finder`, `content-reviewer` | Báo cáo có nguồn, được `content-reviewer` kết luận ĐẠT |
| 3. Thí nghiệm 5 chương | Rã truyện, viết lại, soát; so sánh các model; tối ưu prompt | Đội sản xuất; Điều phối chấm mẫu | Bảng so sánh model theo từng bước, chốt thang model |
| 4. Nối pipeline | TTS, dựng video, TikTok; `channel-manager` (xem §4c) | `coder` và script | Theo [technical.md](technical.md) |

## 7. Ghi chú

- Đã khởi tạo git ngày 26/9/2026 (Người sáng lập đồng ý).
- **Thứ tự ưu tiên** (Người sáng lập chốt ngày 26/9/2026): thử rã và viết lại 5 chương đầu của một truyện trước. Hàng đợi và worker (§4b) để sau, khi vào sản xuất hàng loạt.
