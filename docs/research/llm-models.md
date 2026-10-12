# So sánh model LLM cho việc khối lượng lớn (rã truyện, dịch/viết lại, kiểm tra)

Cập nhật: 26/9/2026 · Tỷ giá tạm tính 26.000 VND/USD (giống [ai-services.md](ai-services.md)) · Giá tra trực tiếp trên trang chính thức của từng hãng qua WebSearch/WebFetch ngày 26/9/2026, trừ khi ghi "(3P)" = số của bên thứ ba, chưa xác minh trên trang chính thức. **Chất lượng tiếng Việt và đọc tiếng Trung của các model dưới đây chưa được tự kiểm chứng bằng cách chạy thật** — dựa vào benchmark công khai và bài viết cộng đồng, độ tin cậy ghi rõ từng dòng. Việc tự đo trên 5 chương mẫu (đã có trong [technical.md](../plans/technical.md) §5) vẫn là bước bắt buộc trước khi chốt.

## 1. Kết luận

- **Chi phí LLM văn bản rất nhỏ so với TTS/ảnh/video** (xem [ai-services.md](ai-services.md) — 110–1.500 USD/tháng). Cả 3 mức ngân sách LLM dưới đây đều dưới 35 USD/tháng cho 4 truyện. **Không nên chọn model theo giá rẻ nhất tuyệt đối — hãy ưu tiên chất lượng tiếng Việt** đo được từ bước thử 5 chương.
- **Rã truyện (đọc tiếng Trung, tóm tắt không bịa):** ưu tiên model gốc Trung Quốc (đọc hiểu tiếng Trung tốt, giá rẻ nhất theo token). Đề xuất chính **Qwen3.5-Flash** hoặc **GLM-4.7-Flash** (miễn phí), dự phòng **DeepSeek** (đọc rất tốt nhưng khó đăng ký trực tiếp, xem §4).
- **Viết lại kịch bản tiếng Việt (仿写):** cần văn phong tự nhiên nhất trong nhóm giá phải chăng. Đề xuất chính **Gemini Flash** (3.7/3.8), dự phòng **Qwen3.5-Plus** — theo benchmark SEA-HELM, Qwen hiện dẫn đầu nhóm model mở ở các ngôn ngữ Đông Nam Á bao gồm khả năng tiếng Việt, nhưng **chưa có bài đo riêng cho tiếng Việt của cả hai**, cần tự test.
- **Kiểm tra văn AI (biên tập 1 lượt):** việc máy móc, giao model rẻ nhất còn đủ để làm theo hướng dẫn. Đề xuất chính **Gemini Flash-Lite**, dự phòng **GLM-4.7-Flash** (miễn phí) hoặc **Claude Haiku 4.5** nếu Flash-Lite bỏ lỗi.
- **Rào cản thực tế:** `platform.deepseek.com` hiện (26/9/2026) **chặn đăng ký không có số điện thoại Trung Quốc đại lục** (tạm thời, do hãng công bố chống tấn công). Muốn dùng DeepSeek phải qua cổng gộp như OpenRouter hoặc bên trung gian thứ ba — thêm phụ phí và một lớp rủi ro. Zhipu (z.ai), Alibaba Cloud Model Studio (vùng Singapore), Moonshot (platform.moonshot.ai, đăng nhập Google) có vẻ đăng ký được từ Việt Nam không cần SĐT Trung Quốc, nhưng **chưa tự đăng ký kiểm chứng, cần thử thật trước khi phụ thuộc**.
- **Ước tính chi phí 1 truyện mẫu (100 chương × ~3.000 chữ Hán):** khoảng **1–8 USD** tuỳ mức, xem §3.
- **3 mức ngân sách/tháng cho 4 truyện/tháng:** Tiết kiệm ~4 USD, Cân bằng ~9 USD, Chất lượng ~22–32 USD — xem §5.

## 2. Bảng giá theo hãng

Giá theo USD/1 triệu token trừ khi ghi khác. "Batch/cache" là mức giảm khi dùng chế độ xử lý theo lô hoặc cache prompt lặp.

### Google Gemini ([ai.google.dev/gemini-api/docs/pricing](https://ai.google.dev/gemini-api/docs/pricing), tra 26/9/2026)

| Model | Input | Output | Batch | Cache | Cửa sổ ngữ cảnh | Free tier |
|---|---|---|---|---|---|---|
| Gemini 2.5 Flash-Lite | $0,10 | $0,40 | -50% | ~10% giá input | 1M | Có, **ngừng bán 16/10/2026** |
| Gemini 3.1 Flash-Lite | $0,25 (văn bản) | $1,50 | -50% | ~10% giá input | 1M | Miễn phí AI Studio: 15 RPM / 1.000 request/ngày / 250k token/phút (tính đến 26/9/2026, có thể đổi) |
| Gemini 3.7 / 3.8 Flash | $0,75 | $3,75 | -50% | ~10% giá input | 1M | 10 RPM / 250 request/ngày (bản 2.5 Flash, số liệu 3.7/3.8 free tier chưa xác minh riêng) |
| Gemini 3.1 Pro | $2,00 (≤200k) / $4,00 (>200k) | $12,00 / $18,00 | -50% | ~10% giá input | 1M | Đã gỡ khỏi free tier từ 4/2026 (3P, chưa xác minh chính thức) |

Lưu ý: giá Flash 3.x giữ nguyên đến 31/12/2026 rồi tăng gấp đôi theo trang giá. **Free tier trả phí = 0 nhưng prompt/response có thể dùng để cải thiện sản phẩm** (chỉ paid tier mới cam kết không dùng để huấn luyện). Thương mại: paid tier cho phép dùng đầu ra thương mại, không tính phí bản quyền, Google không giữ quyền sở hữu đầu ra ([điều khoản Gemini API](https://ai.google.dev/gemini-api/terms), tra 26/9/2026).

### DeepSeek ([api-docs.deepseek.com/quick_start/pricing](https://api-docs.deepseek.com/quick_start/pricing), tra 26/9/2026)

| Model | Input (cache miss) | Input (cache hit) | Output | Cửa sổ ngữ cảnh |
|---|---|---|---|---|
| DeepSeek-Flash, giờ thường | $0,15 | $0,003 | $0,60 | 1M |
| DeepSeek-Flash, giờ cao điểm | $0,30 | $0,006 | $1,20 | 1M |
| DeepSeek-V4-Pro, giờ thường | $0,66 | $0,022 | $1,98 | 1M |
| DeepSeek-V4-Pro, giờ cao điểm | $1,32 | $0,044 | $3,96 | 1M |

Giờ cao điểm: 01:00–04:00 và 06:00–10:00 UTC, thứ Hai–Sáu (trừ nghỉ lễ Trung Quốc); còn lại và cuối tuần là giờ thường, giá bằng nửa. **Nên đặt lịch chạy hàng loạt vào giờ thường/cuối tuần để được giá rẻ nhất.** Thương mại: điều khoản DeepSeek gán quyền đầu ra cho người dùng, cho phép dùng thương mại và phi thương mại, không thu phí thêm, nhưng hãng **giữ quyền dùng input/output để "cung cấp, vận hành, cải thiện" dịch vụ** ([điều khoản DeepSeek](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html), tra 26/9/2026). **Rào cản đăng ký:** cổng chính thức yêu cầu SĐT Trung Quốc đại lục tại thời điểm tra (3P, nhiều bài viết cộng đồng xác nhận, chưa tự thử).

### Qwen / Alibaba Cloud Model Studio ([alibabacloud.com/help/en/model-studio/model-pricing](https://www.alibabacloud.com/help/en/model-studio/model-pricing), tra 26/9/2026)

| Model | Input | Output | Cửa sổ ngữ cảnh | Free tier |
|---|---|---|---|---|
| Qwen3.5-Flash | $0,10 | $0,40 | đến 1M | 1 triệu token/model, 90 ngày, chỉ vùng Singapore |
| Qwen3.5-Plus | $0,40 (≤256k) / $0,50 (256k–1M) | $2,40 / $3,00 | 1M | như trên |
| Qwen3.8-Max | $2,00 | $6,00 | — | như trên |
| Qwen3.7-Max | $2,50 | $7,50 | — | như trên |

Batch: 50% giá thời gian thực. Cache hit: ~10% giá input. Thương mại: điều khoản Qwen Chat (bản chat miễn phí) ghi "chỉ dùng học tập/nghiên cứu, cần xin phép trước khi dùng thương mại", và bản mở trọng số Qwen3.8-Max có ngưỡng doanh thu 50 triệu USD/năm mới cần xin license riêng — nhưng đây là điều khoản cho **Qwen Chat và trọng số tải về**, khác với **API trả phí qua Model Studio** (dịch vụ cloud trả tiền, thường theo điều khoản dịch vụ Alibaba Cloud quốc tế thông thường). **Chưa xác minh 100% điều khoản thương mại riêng cho API trả phí — đọc kỹ Alibaba Cloud International Service Terms trước khi dùng ở quy mô lớn.**

### Kimi / Moonshot ([platform.kimi.ai/docs/pricing](https://platform.kimi.ai/docs/pricing), tra 26/9/2026, tên miền cũ platform.moonshot.ai chuyển hướng sang đây)

| Model | Input (cache miss) | Input (cache hit) | Output | Cửa sổ ngữ cảnh |
|---|---|---|---|---|
| Kimi K2.6 | $0,95 | $0,16 | $4,00 | 262k |
| Kimi K2.7-code | $0,95 | $0,19 | $4,00 | 262k |
| Kimi K3 | $3,00 | $0,30 | $15,00 | 1.048.576 |

Batch (K2.x, chưa áp dụng cho K3): 60% giá chuẩn. Thương mại: chỉ cần xin phép/ghi công khi vượt 100 triệu người dùng/tháng hoặc 20 triệu USD doanh thu/tháng — dưới ngưỡng đó dùng tự do ([điều khoản mô hình Kimi](https://platform.kimi.ai/docs/agreement/modeluse), tra 26/9/2026). Đăng ký: có tuỳ chọn đăng nhập bằng Google, có vẻ không cần SĐT Trung Quốc (3P, chưa tự thử).

### GLM / Zhipu — bản quốc tế Z.ai ([docs.z.ai/guides/overview/pricing](https://docs.z.ai/guides/overview/pricing), tra 26/9/2026)

| Model | Input | Cache | Output | Free? |
|---|---|---|---|---|
| GLM-4.7-Flash | — | — | — | **Miễn phí**, có giới hạn tần suất (chưa rõ số RPM/ngày cụ thể) |
| GLM-4.5-Flash | — | — | — | Miễn phí |
| GLM-5.3-Flash | $0,15 | $0,03 | $0,50 | — |
| GLM-5.3-FlashX | $0,37 | $0,075 | $1,25 | — |
| GLM-5.3 / GLM-5.2 | $1,40 | $0,26 | $4,40 | — |
| GLM-5 | $1,00 | $0,20 | $3,20 | — |

Bản Trung Quốc đại lục (`open.bigmodel.cn`, [docs.bigmodel.cn/cn/guide/start/pricing](https://docs.bigmodel.cn/cn/guide/start/pricing), tra 26/9/2026) tính bằng CNY, ví dụ GLM-5.3 8 CNY input / 28 CNY output mỗi triệu token — **không dùng bản này**, dùng bản z.ai quốc tế để thanh toán bằng thẻ quốc tế và tránh vướng pháp lý dữ liệu nội địa Trung Quốc. Dữ liệu z.ai xử lý tại Singapore, không dùng để huấn luyện theo DPA (3P, theo tổng hợp bài viết, chưa tự đọc hợp đồng gốc). GLM-4.5/4.7 mã nguồn mở theo **MIT license — dùng thương mại tự do** nếu tự host; bản API trả phí theo điều khoản dịch vụ Z.ai riêng, cần đọc trước khi dùng số lượng lớn.

### OpenAI ([developers.openai.com/api/docs/pricing](https://developers.openai.com/api/docs/pricing), tra 26/9/2026)

| Model | Input | Cache | Output | Batch |
|---|---|---|---|---|
| GPT-5-nano | $0,05 | $0,005 | $0,40 | -50% |
| GPT-5-mini | $0,25 | $0,025 | $2,00 | -50% |
| GPT-5 | $1,25 | $0,125 | $10,00 | -50% |
| GPT-5.6-luna (rẻ nhất dòng 5.6) | $0,20 | $0,02 | $1,20 | -50% |
| GPT-6-luna (nếu đã phát hành, cần xác nhận lại) | $0,10 (3P) | $0,01 | $0,50 | -50% |

Thương mại: OpenAI gán quyền sở hữu đầu ra cho người dùng, cho phép bán lại, không thu phí bản quyền; không bảo đảm đầu ra không vi phạm quyền của bên thứ ba ([điều khoản dịch vụ OpenAI](https://openai.com/policies/service-terms/), tra 26/9/2026). Không có ưu thế đặc biệt cho tiếng Trung/tiếng Việt so với Gemini hay các model Trung Quốc, giá nano/mini rẻ nhưng không rẻ hơn Gemini Flash-Lite hoặc GLM-4.7-Flash.

### Anthropic Claude ([claude.com/pricing](https://claude.com/pricing), tra 26/9/2026)

| Model | Input | Cache read | Cache write | Output | Batch |
|---|---|---|---|---|---|
| Haiku 4.5 | $1,00 | $0,10 | $1,25 | $5,00 | -50% |
| Sonnet 5 | $2,00 | $0,20 | $2,50 | $10,00 | -50% |

**Lưu ý mâu thuẫn giá:** trang chính thức tra ngày 26/9/2026 hiển thị Sonnet 5 ở $2/$10, nhưng một số bài tổng hợp bên thứ ba nói giá ưu đãi ra mắt đã hết ngày 31/8/2026 và giá chuẩn hiện là $3/$15. **Chưa xác minh được nguyên nhân mâu thuẫn — kiểm tra lại giá thật khi tính chi phí chính thức.** Thương mại: Anthropic cho dùng đầu ra API thương mại theo điều khoản dịch vụ chuẩn (không tìm thấy điều khoản hạn chế đặc biệt trong lần tra này).

### xAI Grok ([docs.x.ai/developers/pricing](https://docs.x.ai/developers/pricing), tra 26/9/2026)

| Model | Input | Cache | Output | Cửa sổ ngữ cảnh |
|---|---|---|---|---|
| grok-build-0.1 | $1,00 | $0,20 | $2,00 | 256k |
| grok-4.7 (≤200k) | $2,00 | $0,50 | $6,00 | 500k |

**Không đưa vào đề xuất chính:** không có ưu thế biết đến về tiếng Trung/tiếng Việt, giá không rẻ hơn nhóm Gemini/GLM/Qwen ở tầng rẻ, không tìm thấy benchmark hay đánh giá cộng đồng riêng cho việc viết truyện/dịch tiếng Việt.

### OpenRouter — cổng gộp ([openrouter.ai/pricing](https://openrouter.ai/pricing), [openrouter.ai/models](https://openrouter.ai/models), tra 26/9/2026)

- Giá theo đúng giá gốc của hãng (pass-through), cộng phụ phí **5,5% khi nạp bằng thẻ** (tối thiểu 0,80 USD), 5% khi nạp bằng crypto, 5% khi dùng key riêng (bring-your-own-key) sau khi vượt 25.000 USD/tháng.
- Có model miễn phí (đuôi `:free`), giới hạn 20 request/phút, 200 request/ngày.
- **Lợi ích cho dự án này:** một API key, một hoá đơn, dùng được cả model Trung Quốc mà không cần tự đăng ký từng hãng (giải quyết vấn đề DeepSeek chặn SĐT Trung Quốc ở trên) — đổi lại mất 5,5% và thêm một bên trung gian giữ log dữ liệu.

## 3. Ước tính chi phí 1 truyện mẫu (100 chương × ~3.000 chữ Hán)

### Giả định quy đổi token (ghi rõ vì đây là ước tính, không đo thật)

- **Tiếng Trung → token:** dùng xấp xỉ **1 token ≈ 1 chữ Hán** cho các tokenizer kiểu BPE dùng chung (Gemini/OpenAI/Claude); cộng đồng báo cáo khoảng 0,75–1,3 token/chữ tuỳ tokenizer (3P, [ví dụ thảo luận token hoá CJK](https://tonybaloney.github.io/posts/cjk-chinese-japanese-korean-llm-ai-best-practices.html)). Các tokenizer gốc Trung Quốc (Qwen/DeepSeek/GLM/Kimi) nhiều khả năng nén tiếng Trung hiệu quả hơn nhưng **chưa tìm được số liệu chính thức riêng** — dùng cùng giả định 1 token/chữ cho mọi model để so sánh công bằng, biết là có thể lệch.
- **Tiếng Việt → token:** tiếng Việt token hoá kém hiệu quả do dấu (cộng đồng OpenAI báo cáo có thể tăng tới 4,5 lần so với tiếng Anh, 3P, [OpenAI Developer Community](https://community.openai.com/t/tokenizer-is-so-high-in-vietnamese/27692)). Dùng giả định thận trọng **1 từ tiếng Việt ≈ 2,5 token**.
- 3.000 chữ Hán một chương truyện mạng Trung Quốc dịch sang tiếng Việt thường ra khoảng 1.800–2.000 từ tiếng Việt (giả định riêng của người viết báo cáo này, chưa đo thật).

### Khối lượng token mỗi truyện (100 chương)

| Bước | Input/chương | Output/chương | Input tổng | Output tổng |
|---|---|---|---|---|
| Rã truyện (đọc hết + thẻ chương JSON) | ~3.500 token (3.000 chữ truyện + ~500 token khung prompt) | ~2.000 token (tóm tắt + beats + nhân vật, ~800 từ Việt) | 350.000 | 200.000 |
| Viết lại kịch bản (~70% độ dài, kể sát) | ~4.500 token (3.000 chữ truyện + ~1.500 token dàn ý/trạng thái/style card) | ~3.500 token (~1.400 từ Việt) | 450.000 | 350.000 |
| Kiểm tra 1 lượt (biên tập viên) | ~4.500 token (đọc lại script + dàn ý tham chiếu) | ~1.000 token (chỉ sửa chỗ lỗi, không viết lại toàn bộ) | 450.000 | 100.000 |

### Chi phí theo model (USD/truyện, không gồm phụ phí OpenRouter nếu dùng)

| Bước | Model rẻ | Chi phí | Model cân bằng | Chi phí | Model chất lượng | Chi phí |
|---|---|---|---|---|---|---|
| Rã truyện | GLM-4.7-Flash | $0 (miễn phí) | Gemini 3.1 Flash-Lite | $0,39 | Qwen3.5-Flash | $0,12 |
| Viết lại | Qwen3.5-Plus | $1,02 | Gemini 3.7/3.8 Flash | $1,65 | Claude Sonnet 5 (giá $2/$10) | $4,40 |
| Kiểm tra | GLM-4.7-Flash | $0 (miễn phí) | Gemini 3.1 Flash-Lite | $0,26 | Claude Haiku 4.5 | $0,95 |
| **Tổng/truyện** | | **~$1,00** | | **~$2,30** | | **~$5,50** |

Nếu giá Sonnet 5 thật đã tăng lên $3/$15 (xem cảnh báo mâu thuẫn ở §2), mức "chất lượng" cho bước viết lại tăng lên ~$6,60, tổng ~$7,90/truyện — vẫn nhỏ so với chi phí video/TTS.

## 4. Đề xuất phân công theo bước pipeline

| Bước kỹ thuật | Việc | Model chính | Model dự phòng | Vì sao |
|---|---|---|---|---|
| Bước 2 — Rã truyện thành khung, thẻ chương | Đọc hết tiếng Trung, tóm tắt không bịa, xuất JSON | **Qwen3.5-Flash** (hoặc GLM-4.7-Flash để chạy miễn phí ở giai đoạn thử) | **DeepSeek-Flash** qua OpenRouter (đọc tiếng Trung được đánh giá tốt nhưng khó đăng ký trực tiếp) | Việc máy móc, khối lượng lớn (100 lần gọi/truyện), cần đọc tiếng Trung chính xác, giá rẻ nhất |
| Bước 3 — Viết lại kịch bản nghe (仿写) | Dịch + viết lại theo dàn ý, giữ văn phong kênh | **Gemini 3.7/3.8 Flash** | **Qwen3.5-Plus** (SEA-HELM gợi ý Qwen mạnh tiếng Việt trong nhóm mở, cần tự đo) | Cần chất lượng tiếng Việt tốt nhất có thể ở mức giá vừa phải; Gemini có cửa sổ 1M token đủ chứa toàn bộ ngữ cảnh (dàn ý + trạng thái nhân vật + đoạn mẫu phong cách) |
| Bước 3 — Kiểm tra văn AI (biên tập 1 lượt) | Chấm nhịp, phát hiện lặp/sáo rỗng, sửa cục bộ | **Gemini 3.1 Flash-Lite** | **GLM-4.7-Flash** (miễn phí) hoặc **Claude Haiku 4.5** nếu cần độ chính xác cao hơn | Việc máy móc, chỉ cần theo đúng checklist, không cần model mạnh nhất |
| (Tham khảo) Bước 8 — Tiêu đề, mô tả | Gợi ý tiêu đề, tóm tắt ngắn | Có thể dùng cùng model Bước 3 kiểm tra (Flash-Lite), việc nhỏ không cần tính riêng | | Ngoài phạm vi câu hỏi chính, ghi lại để không bỏ sót |

**Quan trọng:** đây là đề xuất dựa trên giá và benchmark công khai, **chưa chạy thật trên truyện mẫu**. Bước "Thử nghiệm viết lại" đã có sẵn trong lộ trình ([technical.md](../plans/technical.md) §5) — dùng chính bước đó để so sánh Gemini Flash vs Qwen3.5-Plus vs Claude Haiku trên 5 chương thật, chấm bằng mắt trước khi chốt.

## 5. Ngân sách LLM văn bản theo tháng (giả định 4 truyện/tháng, mỗi truyện 100 chương)

| Mức | Model dùng | Chi phí/truyện | Chi phí/tháng (4 truyện) |
|---|---|---|---|
| **Tiết kiệm** | GLM-4.7-Flash (rã truyện, kiểm tra) + Qwen3.5-Plus (viết lại) | ~$1,00 | **~$4 (~104.000 VND)** |
| **Cân bằng** | Gemini 3.1 Flash-Lite (rã truyện, kiểm tra) + Gemini 3.7/3.8 Flash (viết lại) | ~$2,30 | **~$9,2 (~239.000 VND)** |
| **Chất lượng** | Qwen3.5-Flash (rã truyện) + Claude Sonnet 5 (viết lại) + Claude Haiku 4.5 (kiểm tra) | ~$5,50–7,90 | **~$22–32 (~572.000–832.000 VND)** |

So với ngân sách video/TTS ước tính ở [ai-services.md](ai-services.md) §7 (~110–1.500 USD/tháng), **LLM văn bản chỉ chiếm 1–3% tổng chi phí sản xuất** — không phải nơi cần tối ưu giá, nên chọn theo chất lượng tiếng Việt đo được.

## 6. Điểm chưa chắc / cần tự kiểm chứng

- **Chất lượng tiếng Việt và đọc tiếng Trung thật của từng model** — mọi nhận định trong tài liệu này dựa trên benchmark công khai (Artificial Analysis, SEA-HELM) và bài viết cộng đồng, **không phải test tự chạy**. Bắt buộc đo trên 5 chương mẫu như kế hoạch đã ghi.
- **Giá Claude Sonnet 5:** mâu thuẫn giữa trang chính thức ($2/$10) và một số bài tổng hợp nói giá đã tăng lên $3/$15 sau 31/8/2026 — cần xác nhận lại tại thời điểm mua.
- **Khả năng đăng ký DeepSeek, Qwen (Model Studio), Kimi, GLM từ Việt Nam** không qua trung gian — chỉ tổng hợp từ tìm kiếm, **chưa tự đăng ký thử tài khoản nào**.
- **Điều khoản thương mại API trả phí của Qwen (Model Studio)** — điều khoản "chỉ dùng phi thương mại" tìm được có vẻ áp cho Qwen Chat/trọng số mở, chưa xác minh điều khoản riêng của API cloud trả phí.
- **Free tier / giới hạn tần suất GLM-4.7-Flash** — biết là miễn phí nhưng chưa tìm được số RPM/ngày cụ thể trên trang chính thức.
- **Tỷ lệ token/chữ Hán và token/từ Việt** dùng trong ước tính chi phí là giả định làm tròn, không phải số đo thật từ tokenizer của từng hãng.

## Nguồn

- **Gemini:** [giá](https://ai.google.dev/gemini-api/docs/pricing), [điều khoản](https://ai.google.dev/gemini-api/terms) — tra 26/9/2026
- **DeepSeek:** [giá](https://api-docs.deepseek.com/quick_start/pricing), [điều khoản](https://cdn.deepseek.com/policies/en-US/deepseek-open-platform-terms-of-service.html) — tra 26/9/2026
- **Qwen / Alibaba Cloud:** [giá Model Studio](https://www.alibabacloud.com/help/en/model-studio/model-pricing), [điều khoản Qwen](https://qwen.ai/termsservice) — tra 26/9/2026
- **Kimi / Moonshot:** [giá](https://platform.kimi.ai/docs/pricing), [điều khoản mô hình](https://platform.kimi.ai/docs/agreement/modeluse) — tra 26/9/2026
- **GLM / Zhipu:** [giá quốc tế z.ai](https://docs.z.ai/guides/overview/pricing), [giá Trung Quốc](https://docs.bigmodel.cn/cn/guide/start/pricing) — tra 26/9/2026
- **OpenAI:** [giá](https://developers.openai.com/api/docs/pricing), [điều khoản dịch vụ](https://openai.com/policies/service-terms/) — tra 26/9/2026
- **Claude:** [giá](https://claude.com/pricing) — tra 26/9/2026
- **xAI Grok:** [giá](https://docs.x.ai/developers/pricing) — tra 26/9/2026
- **OpenRouter:** [giá/phụ phí](https://openrouter.ai/pricing), [danh sách model](https://openrouter.ai/models) — tra 26/9/2026
- **Benchmark chất lượng đa ngôn ngữ (mức tin cậy trung bình, không tự kiểm chứng):** [SEA-HELM leaderboard](https://leaderboard.sea-lion.ai/), [Artificial Analysis Intelligence Index tổng hợp qua bài viết](https://www.morphllm.com/best-open-source-coding-model-2026)
- **Quy đổi token (3P, chưa xác minh chính thức):** [token hoá CJK](https://tonybaloney.github.io/posts/cjk-chinese-japanese-korean-llm-ai-best-practices.html), [tiếng Việt token hoá kém hiệu quả](https://community.openai.com/t/tokenizer-is-so-high-in-vietnamese/27692)
- **Rào cản đăng ký DeepSeek không SĐT Trung Quốc (3P):** [dev.to — hướng dẫn dùng DeepSeek không cần SĐT Trung Quốc](https://dev.to/neutrino-api/how-to-use-deepseek-models-without-a-chinese-phone-number-a-guide-for-non-chinese-developers-5b7a)
