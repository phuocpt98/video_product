# Mục lục tài liệu

Cập nhật: 13/10/2026

Quy tắc tài liệu (kể cả thứ tự tin khi mâu thuẫn): [.claude/company/playbooks/files-and-docs.md](../.claude/company/playbooks/files-and-docs.md). Luật và đội hình studio ở [.claude/company/](../.claude/company/README.md).

## Điều hành

| Tài liệu | Nội dung | Khi nào đọc |
|---|---|---|
| [progress.md](progress.md) | Đang làm, tiếp theo, đã xong | Đầu mỗi phiên |
| [setup.md](setup.md) | Cài dự án trên máy mới: script tự động, việc làm tay, lỗi đã biết, gỡ bỏ | Máy mới, lỗi môi trường |
| [decisions.md](decisions.md) | Quyết định đã chốt, câu hỏi chờ Người sáng lập | Trước khi đề xuất hướng mới |

## Kế hoạch

| Tài liệu | Nội dung | Khi nào đọc |
|---|---|---|
| [plans/collab-protocol.md](plans/collab-protocol.md) | Giao thức ba bên Claude / Muse (máy cloud) / Người sáng lập: ai làm gì, GitHub Issues làm bảng việc chung (`scripts/hub.py`), dạng bình luận bắt buộc, luồng diễn viên mới, truyện mới, lỗi | Trước khi giao việc cho Muse hoặc nhận việc từ máy khác |
| [plans/channel.md](plans/channel.md) | Kế hoạch kênh: 6 đối thủ, bài học kênh cũ Pel Pel, định vị, chiến lược YouTube/TikTok, kiếm tiền, rủi ro, lộ trình 90 ngày | Việc liên quan nội dung, thương hiệu, tăng trưởng |
| [plans/agent-team.md](plans/agent-team.md) | Đội agent: Claude Code dẫn dắt (gói team, hạn chế), đội agy làm (gói Gemini Pro cá nhân). Vai trò, thang model, luật chuyển model, quyền, lộ trình. Sơ đồ: [agent-team.html](plans/agent-team.html) | Trước khi giao việc, thêm vai trò, đổi model |
| [plans/studio-flow.html](plans/studio-flow.html) | Quy trình sản xuất hiện tại (trang HTML): luồng 4 pha, ai làm, model, file ra, số đo, việc còn thiếu, câu hỏi hướng đi | Muốn nhìn tổng quan studio đang chạy thế nào |
| [plans/story-bible.md](plans/story-bible.md) | Sổ tay truyện + dây chuyền theo lô: nhóm trưởng giữ đề cương, agent viết song song, kiểm mạch, cập nhật sổ tay có phiên bản (đề xuất) | Trước khi sản xuất truyện dài |
| [plans/visual-library.md](plans/visual-library.md) | Thư viện nhân vật + thư viện cảnh tái sử dụng (16:9 và 9:16), luật chống lặp, bước phân cảnh, phản biện luồng hiện tại (đề xuất) | Làm hình cho video, video mồi TikTok |
| [plans/drama-batch-2.md](plans/drama-batch-2.md) | Kế hoạch lô drama 2: 3 truyện (phượng hoàng nam, mẹ kế đình công, phù đệ ma), vai, nền, mồi TikTok, thời gian, quota (đề xuất) | Trước khi sản xuất lô drama 2 |
| [plans/drama-story-templates.md](plans/drama-story-templates.md) | 4 khuôn truyện drama "Zhihu" (con ruột bị ghẻ lạnh, sa thải nhầm, trọng sinh đổi hôn phu, bị trộm bài thi) kèm mồi TikTok 15 giây | Chọn mô-típ truyện drama |
| [plans/tiktok-hook-strategy.md](plans/tiktok-hook-strategy.md) | Video mồi TikTok 10–15 giây, thư viện diễn viên, ảnh bản lề | Làm video mồi TikTok |
| [plans/ai-film-rules.md](plans/ai-film-rules.md) | Luật viết kịch bản phim AI (Muse…): một nhịp một clip, tốc độ thật, khoá bên màn hình, nối khung hình, né bộ lọc, quy trình và âm thanh | Trước khi viết kịch bản hoặc prompt video AI |
| [plans/chapter1-studio.md](plans/chapter1-studio.md) | (Cũ, đã thay bằng studio-org.md + bảng việc) Kế hoạch dựng chương 1 bằng rối cắt ghép | Làm hình cho truyện mẫu |
| [plans/protocols.md](plans/protocols.md) | Giao thức dữ liệu giữa các phòng, công cụ, agent: hợp đồng từng loại file, dạng câu trả lời bắt buộc của AI (code kiểm: `src/contracts.py`) | Trước khi thêm công cụ/agent mới hoặc đổi dạng file |
| [plans/studio-org.md](plans/studio-org.md) | Tổ chức phòng ban (Biên kịch, Thiết kế nhân vật, Bối cảnh, Dựng, Tài nguyên ngoài, Kỹ thuật), bảng việc bằng file, số đo tốc độ và cách tăng tốc (đề xuất) | Trước khi mở rộng sản xuất, khi thấy chậm |
| [plans/technical.md](plans/technical.md) | Pipeline 10 bước: tách chương → rã truyện → thẻ phong cách → viết lại → câu chèn → TTS → clip nền → dựng → thumbnail → TikTok → đăng. Công nghệ, lộ trình triển khai | Trước khi code bất kỳ bước nào |

## Nghiên cứu

| Tài liệu | Nội dung | Khi nào đọc |
|---|---|---|
| [research/novel-writing-repos.md](research/novel-writing-repos.md) | 6 repo viết truyện bằng AI (trong `tool/`): rã truyện, thẻ phong cách, kiểm tra văn AI, giữ mạch truyện dài, câu móc. Module lấy lại từ `tiktok_content` | Làm Bước 2–3 (rã truyện, viết lại) |
| [research/open-source-video-ai.md](research/open-source-video-ai.md) | Repo mã nguồn mở: pipeline truyện → video, mô hình video chạy trên Mac, chân dung động, nhân vật nhất quán, TTS tiếng Việt (VieNeu-TTS), phụ đề (stable-ts) | Làm Bước 5–7, 9 (TTS, hình, dựng, TikTok) |
| [research/ai-services.md](research/ai-services.md) | Dịch vụ trả phí: Motion Studio, Kling, Hailuo, Veo, Seedance…; ảnh; TTS Việt (FPT, Vbee, Gemini…); ước tính chi phí tháng; rủi ro YouTube và bản quyền | Chọn dịch vụ, lập ngân sách |
| [research/2026-09-27-ai-film.md](research/2026-09-27-ai-film.md) | Công cụ phim AI ngắn cho video mồi TikTok: flowkit (Google Flow/Veo), Wan2.1, LTX-Video, điều khoản gói miễn phí Kling/Hailuo (chưa duyệt) | Làm video mồi TikTok |
| [research/2026-09-27-visual-library.md](research/2026-09-27-visual-library.md) | Chính sách YouTube về nội dung lặp, repo quản lý kho hình, kỹ thuật biến thể ảnh (chưa duyệt) | Làm thư viện hình |
| [research/2026-10-08-ai-action-animation.html](research/2026-10-08-ai-action-animation.html) | Cách creator AI Trung Quốc làm cảnh đánh liền mạch: frame chain, keypose, nhịp 4 khối, âm thanh hit-stop, repo và case tham khảo (số liệu chưa xác minh) | Làm cảnh hành động bằng AI video |
| [research/2026-09-28-drama-outlines-ngoai-tinh.md](research/2026-09-28-drama-outlines-ngoai-tinh.md) | Dàn ý cấp cao mô-típ vợ trị chồng ngoại tình (5 video mẫu), công thức tên video, quy tắc thumbnail chibi, mẫu câu mở đầu giữ chân (chưa duyệt) | Viết truyện drama, đặt tên, làm thumbnail |
| [research/2026-09-28-drama-short-stories.md](research/2026-09-28-drama-short-stories.md) | Truyện drama ngắn 30–60 phút: nữ/nam chính, nhịp ức chế → vả mặt, cắt đoạn mồi TikTok, 15 mô-típ, rủi ro chính sách, 3 truyện nên thử (chưa duyệt) | Làm truyện drama tự viết |
| [research/2026-09-28-story-video-production.md](research/2026-09-28-story-video-production.md) | Các kênh làm video truyện có hình thế nào (SaaS, rối cắt ghép, quay đôi…), đề xuất cải tiến: Rhubarb lip-sync… (chưa duyệt) | Tối ưu phòng Dựng |
| [research/2026-09-28-free-llm-apis.md](research/2026-09-28-free-llm-apis.md) | API LLM miễn phí/giá rẻ (Gemini free, GLM Flash, Groq, OpenRouter, DeepSeek, Qwen…): hạn mức, tiếng Việt/Trung, điều khoản, đề xuất phân việc (chưa duyệt, cần kiểm bằng lần gọi thật) | Thêm nhân viên xử lý chữ, tăng tốc |
| [research/2026-09-28-zhihu-short-stories.md](research/2026-09-28-zhihu-short-stories.md) | Nguồn truyện ngắn Zhihu/番茄/七猫: nền tảng, 25 truyện nữ chính hot, 12 mô-típ, nhịp truyện, bản quyền, cách dùng truyện gốc làm tài liệu để viết truyện mới (chưa duyệt) | Chọn truyện/mô-típ drama mới |
| [research/2026-10-13-puppet-v2.md](research/2026-10-13-puppet-v2.md) | Hệ rối v2: chẩn đoán PR #1 ("đầu" thực ra là bán thân), cắt lớp bằng màu + hình thái không cần AI, vá lego, tóc lắc bằng remap, kiểm actor, thay đồ, phân công Claude xây thư viện / Muse chạy, bộ nhập truyện Gemini (chưa duyệt) | Làm nhân vật rối mới, nối Muse vào dây chuyền |
| [research/llm-models.md](research/llm-models.md) | So sánh model LLM cho việc khối lượng lớn (rã truyện, dịch/viết lại tiếng Việt, kiểm tra văn AI): giá Gemini/DeepSeek/Qwen/Kimi/GLM/OpenAI/Claude/Grok, OpenRouter, ước tính chi phí 1 truyện mẫu, đề xuất phân công theo bước, ngân sách tháng | Chọn model LLM cho Bước 2–3, lập ngân sách LLM |
