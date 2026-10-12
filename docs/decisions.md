# Quyết định dự án

Cập nhật: 26/9/2026

Đây là nguồn đúng cao nhất: tài liệu nào mâu thuẫn với file này thì sửa tài liệu đó. Quyết định mới thêm vào đầu bảng "Đã chốt", ghi kèm ngày.

## Đã chốt

| Ngày | Quyết định | Chi tiết ở |
|---|---|---|
| 28/9/2026 | **Bật chế độ nhanh khâu chữ mặc định** (`pipeline.fast: true`): thử trên bản sao chương 1–5 (`stories/thu-nhanh/`), phần chữ khoảng 6–7 phút cho 5 chương so với 28 phút; người duyệt chấm cả 5 chương ĐẠT. Tắt riêng từng truyện bằng `pipeline: {fast: false}` trong story.yaml | [plans/studio-org.md](plans/studio-org.md) §3.2 |
| 28/9/2026 | **Tổ chức studio thành phòng ban** (Biên kịch, Thiết kế nhân vật, Bối cảnh, Dựng, Tài nguyên ngoài = Người sáng lập, Kỹ thuật = Claude), trao đổi qua **bảng việc bằng file** `board/` + trang xem local. Thiếu tài nguyên thì treo việc và gửi yêu cầu sang phòng khác | [plans/studio-org.md](plans/studio-org.md) §4–5 |
| 28/9/2026 | **Tăng tốc:** chạy gối đầu chữ → giọng → dựng; giọng đọc song song; **thử rút gọn khâu chữ** (viết kèm tự kiểm, duyệt khi máy báo lỗi, sửa khoanh vùng, gộp chương) trên 5 chương mẫu rồi mới áp dụng | [plans/studio-org.md](plans/studio-org.md) §3 |
| 28/9/2026 | **Video giữ 24 hình/giây** | [plans/studio-org.md](plans/studio-org.md) §3.4 |
| 27/9/2026 | **Dàn cảnh bằng code, không dùng AI** (AI tốn và chậm). Mỗi truyện có mục lục `cast.yaml` trỏ vào thư viện (diễn viên, nền, đạo cụ); luật từ khoá dùng chung ở `data/actions.yaml`; `src/studio/direct.py` sinh kịch bản cảnh. Chấp nhận khớp tương đối với truyện | [plans/chapter1-studio.md](plans/chapter1-studio.md) §4 |
| 27/9/2026 | **Nhân vật nhỏ trong khung: cao 1/4 đến 1/2 khung hình, kể cả cảnh cận**, nên không cần ảnh chất lượng cao. Đạo cụ (súng, dao, túi…) tạo theo bảng 24 món mỗi lần rồi dán vào tay, khớp tương đối | [plans/chapter1-studio.md](plans/chapter1-studio.md) §4 |
| 27/9/2026 | **Phong cách diễn viên: chibi mộc mạc, đầu to không cổ, đầu hạ thấp che cổ nhưng vẫn lộ vai.** Thay cho phong cách 2D đời cũ ở dòng dưới | `assets/actors/nam-18-a/` |
| 27/9/2026 | **Không tạo ảnh bằng model chạy trên máy** (thử Z-Image-Turbo: máy nóng, chậm, RAM sát giới hạn). Đã xoá model ảnh, giữ model giọng VieNeu. Ảnh lấy từ app Gemini (làm tay) hoặc Gemini API có thanh toán (chờ quyết) | [plans/visual-library.md](plans/visual-library.md) §2 |
| 27/9/2026 | **Phong cách hình: 2D nét vẽ tay, tô màu phẳng, kiểu hoạt hình/manhua Trung Quốc đời cũ; không 3D, không giả ảnh thật.** Đoạn phong cách chung lưu ở `channel.yaml` → `visual_style` | [plans/visual-library.md](plans/visual-library.md) §3a |
| 27/9/2026 | **Đăng thử 1 tập (chương 1–5) để lấy số liệu thật** trước khi đầu tư thêm (hình động, video mồi TikTok, API trả phí). Nhiều người xem thì tối ưu dần hoặc thuê API. Video mồi TikTok: không crop watermark dịch vụ miễn phí, không dùng bot web trên tài khoản chính | [research/2026-09-27-ai-film.md](research/2026-09-27-ai-film.md) |
| 26/9/2026 | **Sổ tay truyện + dây chuyền theo lô 5 chương.** Nhóm trưởng (`story-lead`) giữ sổ tay (bible, nhân vật, sổ dữ kiện, cài cắm, đề cương lô, có phiên bản); agent viết song song theo sổ tay và nộp đề xuất; nhóm trưởng kiểm mạch cả lô, cập nhật sổ tay. Lô đầu dừng chờ Người sáng lập duyệt sổ tay v1 | [plans/story-bible.md](plans/story-bible.md) |
| 26/9/2026 | **Mức viết lại mặc định: nhẹ** (`rewrite: light`). Agent đọc chương gốc, giữ cốt truyện, **bối cảnh Trung Quốc** và **tên Hán Việt**, chỉ đổi cách diễn đạt và miêu tả; lời bình người kể khoảng 5%. Bỏ Việt hoá bối cảnh vì nghe không thuận. Rủi ro bản quyền cao hơn, nằm trong hướng a đã chấp nhận. Pipeline làm mỗi chương thành 1 phần việc riêng (text + mp3), chạy song song, leader ghép video | Câu 2 cũ; [src/run.py](../src/run.py) |
| 26/9/2026 | **Giọng đọc: VieNeu-TTS v3 Turbo** (chạy local, Apache-2.0, 0đ). Giọng mặc định **Ngọc Huyền**, dự phòng **Trúc Ly**. edge-tts vẫn chỉ để thử | [channels/khoai-tay-review/channel.yaml](../channels/khoai-tay-review/channel.yaml) |
| 26/9/2026 | **Nhân viên `channel-manager`** (giai đoạn 4): đăng video lên YouTube qua API ở chế độ Riêng tư, Người sáng lập bấm Công khai; kéo số liệu hằng ngày; báo cáo tuần. TikTok API để sau | [plans/agent-team.md](plans/agent-team.md) §4c |
| 26/9/2026 | **Ba tầng dữ liệu: kho chung `assets/`, kênh `channels/<channel>/`, truyện `stories/<slug>/`** (mỗi truyện là một dự án, có `story.yaml`). Nhiều kênh cùng kiểu (Khoai Tây, Bắp Cải…) dùng chung một bộ prompt avatar: linh vật rau củ, chỉ đổi loại rau, phụ kiện và màu | [CLAUDE.md](../CLAUDE.md) §2 |
| 26/9/2026 | **Hàng đợi `jobs/` và worker launchd**: đồng ý thiết kế, nhưng làm sau, khi vào sản xuất hàng loạt. Việc trước mắt là thử 5 chương | [plans/agent-team.md](plans/agent-team.md) §4b |
| 26/9/2026 | **Claude Code dẫn dắt, đội agy làm.** Gói Gemini Pro cá nhân (qua agy) dùng thoải mái; Claude Code (gói team) chỉ dùng cho việc quan trọng. Mỗi vai trò có thang model, được leo thang tự động trong agy và sang GLM; muốn lên Claude Code thì Điều phối quyết. Duyệt nội dung giao `content-reviewer` (Opus 4.6 trên agy), code và cấu trúc vẫn qua `qa-lead` (đã sửa hiến pháp §5). Agy chạy trong thư mục được phép, bật `--sandbox`, không chạy lệnh shell | [plans/agent-team.md](plans/agent-team.md) |
| 26/9/2026 | **Tuyển vai trò `llm-runner`** (dự án, Thực thi, haiku): chạy GLM-4.7-Flash miễn phí theo lô. Gọi GLM qua `src/common/llm.py` (lõi, đọc/ghi file) và một MCP mỏng bọc ngoài để thử prompt nhanh | [.claude/agents/project/llm-runner.md](../.claude/agents/project/llm-runner.md) |
| 26/9/2026 | **Tên kênh: Khoai Tây Review**, dùng chung YouTube + TikTok. (Tài khoản TikTok cũ hay mới: Claude đề xuất tạo mới, chưa chốt) | Câu 1 cũ |
| 26/9/2026 | **Video nền là clip lặp lấy từ thư viện dùng chung**, không làm hoạt hình AI riêng cho từng truyện vì quá tốn. Làm dư clip để dùng lại nhiều lần. Nguồn: gameplay tự động từ game của mình (câu 10) và clip tự tạo. Không dùng gameplay hay phim của người khác. Thay quyết định ngày 23/9 (hình AI theo truyện ~60–70%) | [plans/technical.md](plans/technical.md) Bước 6 (cần sửa theo) |
| 26/9/2026 | **Nguồn truyện: làm cả hướng a (viết lại sâu truyện Trung) và d (tự sáng tác từ mô-típ), a trước.** Người sáng lập chấp nhận rủi ro bản quyền của hướng a. Video kênh khác chỉ dùng để nhận diện truyện gốc rồi lấy bản gốc tiếng Trung; không chép lời kể của họ làm kịch bản | Câu 9 cũ; [research/ai-services.md](research/ai-services.md) §8 |
| 26/9/2026 | **Có phụ đề chạy trên video FULL** | Câu 4 cũ |
| 26/9/2026 | **Đã khởi tạo git** (chỉ trên máy, không đẩy lên remote), vì agy sẽ viết code. Thay quyết định "chưa khởi tạo" cùng ngày | Câu 7 cũ |
| 25/9/2026 | **Mô hình studio 3 tầng** (công ty / gói ngành / dự án), dựng trong `.claude/` của repo này trước. Đội hình: Điều phối + 3 quản lý (`product-lead`, `architect`, `qa-lead`) + 4 thực thi (`researcher`, `developer`, `tester`, `operator`) | [.claude/company/](../.claude/company/README.md) |
| 25/9/2026 | **Tên file, thư mục, vai trò, skill bằng tiếng Anh; nội dung viết tiếng Việt** | [files-and-docs.md](../.claude/company/playbooks/files-and-docs.md) |
| 25/9/2026 | **edge-tts chỉ dùng thử nghiệm**, không dùng cho video đăng kênh (Microsoft cấm dùng thương mại khi không có Azure). TTS ưu tiên thử VieNeu-TTS | [research/ai-services.md](research/ai-services.md) §5 |
| 25/9/2026 | Tổ chức repo theo bản đồ thư mục trong `CLAUDE.md` (hook tự chặn). Mọi tài liệu nằm trong `docs/`, có mục lục | [CLAUDE.md](../CLAUDE.md) §2 |
| 25/9/2026 | Kịch bản làm theo cách **拆书 + 仿写**: rã truyện thành khung, học thẻ phong cách, viết lại thành kịch bản nghe tiếng Việt | [plans/technical.md](plans/technical.md) §2 |
| 25/9/2026 | Repo trong `tool/` **chỉ lấy ý tưởng**, tự viết code và prompt (vì giấy phép GPL/AGPL hoặc không có) | [research/novel-writing-repos.md](research/novel-writing-repos.md) |
| 25/9/2026 | Chưa code. Làm xong nghiên cứu và tổ chức repo trước | [progress.md](progress.md) |
| 23/9/2026 | Tài liệu viết thành file `.md` trong project, không tạo tài liệu online | — |
| 23/9/2026 | Ngách: đô thị, hệ thống, trọng sinh làm giàu. YouTube là kênh chính (bản FULL), TikTok là phễu (10 phút đầu) | [plans/channel.md](plans/channel.md) §1, §4 |

## Đang chờ Người sáng lập chốt

| # | Câu hỏi | Ghi chú |
|---|---|---|
| 3 | **Ngân sách hằng tháng** cho LLM, TTS, tạo hình/video AI | 26/9: đang so sánh model LLM theo giá (Claude điều phối, việc khối lượng lớn giao model rẻ) → `research/llm-models.md` |
| 5 | **Truyện mẫu đầu tiên** | 26/9: Người sáng lập gửi 1 truyện ngắn (video hoặc nội dung), Claude tìm bản gốc tiếng Trung |
| 6 | **Nguồn mẫu phong cách:** 2–3 truyện hoặc kênh muốn học giọng kể | 26/9: Người sáng lập sẽ gửi |
| 8 | **Tên studio** (dùng trong hiến pháp, dự án sau) | Hiện gọi tạm là "studio" |
| 10 | **Video nền bằng gameplay tự động từ game của mình** (`~/Documents/project/personal/game_ideal`)? | Đề xuất 26/9, xem ghi chú trong phiên. Cần xác nhận tài nguyên hình/nhạc trong game cho phép dùng thương mại |
| 11 | **Luật viết kịch bản phim AI** ([plans/ai-film-rules.md](plans/ai-film-rules.md)) có thành quy định cho mọi phim làm bằng Muse/AI video không | 8/10/2026: rút từ phim thử `nguoi-giu-deo` (đoạn đánh nhau rời rạc, 5 cảnh bị bộ lọc chặn). Bài học ghi ở `.claude/company/lessons.md` |
