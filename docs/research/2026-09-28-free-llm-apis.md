# API LLM miễn phí và giá rẻ để tăng nhân viên xử lý chữ

> **Ghi chú của Điều phối (28/9/2026, CHƯA duyệt):** báo cáo do nhân viên nghiên cứu trên agy viết. Một số tên model (Gemini 1.5 Flash, Llama 3.1) có thể đã cũ và nhiều hạn mức ghi từ trí nhớ của model, **phải kiểm lại bằng lần gọi thật** trước khi dùng. Hướng dùng được ngay: GLM Flash (đã có key, không huấn luyện trên dữ liệu API) cho rã chương và gắn nhãn; Groq cho việc trả YAML ngắn; DeepSeek làm dự phòng trả phí rất rẻ. Gemini API bản miễn phí dùng dữ liệu để huấn luyện: chỉ dùng cho việc không nhạy cảm.

Chào bạn, dưới đây là báo cáo nghiên cứu chi tiết về các nguồn cung cấp API LLM miễn phí và giá rẻ, phục vụ việc tự động hóa và tăng tốc luồng công việc xử lý truyện tiếng Trung – Việt cho "Khoai Tây Review".

### Tóm tắt (5 ý chính)
1. **GLM-4 Flash và Groq là "mỏ vàng" xử lý song song:** Zhipu (Z.ai) đang miễn phí hoàn toàn model GLM-4-Flash (128K context, hiểu tiếng Trung xuất sắc), trong khi Groq cung cấp Llama 3.1 miễn phí với tốc độ siêu tốc (>300 token/s), lý tưởng cho các tác vụ trả YAML ngắn.
2. **Nhiều dịch vụ đã khai tử gói miễn phí (Free Tier):** Cerebras, SambaNova hiện chỉ cấp $5 credit dùng thử ban đầu (Pay-as-you-go). GitHub Models API độc lập cũng đã bị ngừng hoạt động và tích hợp vào Copilot trả phí.
3. **Rủi ro rò rỉ kịch bản với Gemini & Mistral:** Gói Free Tier của Gemini (AI Studio) và gói Experiment của Mistral có điều khoản cho phép nhà cung cấp dùng dữ liệu input/output để huấn luyện AI. Nếu nội dung truyện có tính bảo mật cao, không nên dùng.
4. **Giải pháp siêu rẻ (Vài USD/tháng):** DeepSeek-Flash ($0.15/1M token) và Qwen/DashScope là những khoản đầu tư cực kỳ hiệu quả nếu hết hạn mức miễn phí. Cả hai cam kết KHÔNG dùng dữ liệu API để huấn luyện model.
5. **Khả năng tương thích:** Ngoại trừ Cloudflare Workers AI cần điều chỉnh SDK, toàn bộ các API còn lại (Z.ai, Groq, OpenRouter, DeepSeek, DashScope) đều tương thích chuẩn OpenAI (chỉ cần đổi `base_url` và `api_key`).

---

### Bảng so sánh các nhà cung cấp (Ngày tra cứu: 28/09/2026)

| Nhà cung cấp | Model Tốt Nhất / Context | Hạn mức Miễn phí / Giá | Chất lượng VN & Trung | Tốc độ | Thương mại & Huấn luyện dữ liệu | Tương thích OpenAI |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Gemini API (Free)** | Gemini 1.5 Flash (1M) | 15 RPM, 500 RPD, 1M TPM. Cần tài khoản Google. | Xuất sắc cả hai | Rất nhanh | Cho phép thương mại. **Bị dùng để huấn luyện** | Có |
| **Z.ai (Zhipu)** | GLM-4.5/4.7-Flash (128K) | $0 / 1M token vĩnh viễn. Không cần thẻ tín dụng. | Tốt VN, Xuất sắc Trung | Nhanh | Cho phép. **Không huấn luyện API** | Có |
| **Groq** | Llama 3.1 70B/8B (8K/128K) | ~30 RPM, 14.400 RPD. Tùy tài khoản. Không cần thẻ. | Khá VN, Khá Trung | Siêu tốc | Cho phép. Không giữ log, **Không huấn luyện** | Có |
| **OpenRouter** | Llama 3 / Mistral (`:free`) | 20 RPM, 50 RPD (nếu nạp < $10 trọn đời). | Tùy model | Biến động | Tùy model gốc. OR **Không log/huấn luyện** | Có |
| **Mistral La Plateforme** | Mistral NeMo / Small | Rất thấp (~1 RPS, động). Không cần thẻ. | Khá VN & Trung | Nhanh | Thử nghiệm. **Có thể bị dùng huấn luyện** | Có |
| **Cloudflare Workers AI** | Llama 3 (8K) | 10.000 Neuron/ngày. Không thẻ. | Tốt VN | Nhanh | Cho phép. **Không huấn luyện** | Có (Qua wrapper) |
| **DeepSeek** *(Giá rẻ)* | DeepSeek-Flash (128K) | **Không Free.** $0.15/1M Input, $0.60/1M Output | Xuất sắc cả hai | Rất nhanh | Cho phép. **Không huấn luyện** | Có |
| **DashScope (Qwen)** *(Giá rẻ)* | Qwen-Plus/Long (1M) | **Không Free.** Trả phí theo Tier (~$0.5-$1/1M token) | Xuất sắc cả hai | Nhanh | Cho phép. **Không huấn luyện** | Có |
| **Cerebras / SambaNova** | Llama 3.1 70B/405B | **Không Free.** Chỉ tặng $5 credit dùng thử 30 ngày. | - | Siêu tốc | - | Có |
| **GitHub Models** | (Đã khai tử API) | Không còn cung cấp API độc lập. | - | - | - | - |

*(Ghi chú: RPM = Lượt/phút, RPD = Lượt/ngày, TPM = Token/phút)*

---

### Đề xuất phân chia công việc cho Studio

Dựa trên cấu hình hiện có (đã có key Gemini Pro 5h/lần và Z.ai), đây là luồng kết hợp tối ưu nhằm tối đa hoá số token miễn phí mà vẫn bảo mật:

**1. Rã chương truyện Trung → thẻ chương (Đầu vào Trung, cần Context lớn)**
*   **Chính:** **Z.ai (GLM-4-Flash)**. Context 128K dư sức xử lý 1-2 chương cùng lúc. Tiếng Trung là tiếng mẹ đẻ của Zhipu, giá $0 trọn đời và không huấn luyện dữ liệu.
*   **Dự phòng:** **DeepSeek-Flash**. Giá siêu rẻ ($0.15/1M token). Tránh dùng Gemini Free vì rủi ro lộ kịch bản nếu cốt truyện độc quyền.

**2. Gắn nhãn đạo diễn (Output YAML, cần tốc độ cao)**
*   **Chính:** **Groq (Llama 3.1 8B hoặc 70B)**. Tác vụ phân loại (classification) theo danh sách đóng không đòi hỏi suy luận quá sâu, nhưng cần xuất JSON/YAML nhanh và chuẩn. Groq cho tốc độ >300 token/giây, hạn mức 14.400 RPD, dư sức gánh hàng ngàn dòng thoại mỗi ngày.
*   **Dự phòng:** **Z.ai GLM-4-Flash** (tốc độ tốt, không bị giới hạn RPD cứng).

**3. Soát lỗi và kiểm máy văn tiếng Việt (Theo checklist)**
*   **Chính:** Dành quota của **Gemini Pro (agy)** hiện tại của bạn cho việc này. Soát lỗi cần một model thông minh, văn phong mượt và hiểu tiếng Việt sâu sắc.
*   **Dự phòng:** **DeepSeek-V4-Pro** hoặc **Gemini 1.5 Flash (API Free)** (Nếu không ngại điều khoản chia sẻ dữ liệu huấn luyện).

**4. Chọn bộ phận nhân vật từ mục lục (Output YAML)**
*   **Chính:** **Groq (Llama 3.1)**. Bắn text mục lục vào và lấy YAML ngay lập tức mà không bị nghẽn (bottleneck).

**5. (Tuỳ chọn) Viết lại nhẹ tiếng Việt từ bản Trung**
*   **Chính:** Dùng **DeepSeek-V4-Pro** hoặc **Qwen-Plus** (DashScope). Chi phí chỉ khoảng $1-$2/tháng cho hàng chục tiểu thuyết, nhưng chất lượng văn phong tiếng Việt từ tiếng Trung của 2 model này cực kỳ xuất sắc, sát nghĩa và tự nhiên.

**Ước tính tổng năng suất miễn phí gộp lại (Mỗi ngày):**
Bạn có thể vắt kiệt khoảng **20.000+ request miễn phí/ngày** (14.400 từ Groq, 500 từ Gemini, hàng ngàn request concurrent từ GLM-4 Flash). Vấn đề lớn nhất chỉ là cấu trúc code API của bạn gọi luân phiên (Load Balancing) cho khéo và quản lý lỗi `HTTP 429` (Rate limit).

---

### Điểm chưa xác minh (Cần test thực tế)
*   **Giới hạn RPM ngầm của Z.ai Flash:** Zhipu tuyên bố miễn phí hoàn toàn, nhưng hệ thống vẫn có lớp bảo vệ chống DDoS hoặc spam. Giới hạn concurrency (số request chạy cùng lúc) chính xác trên tài khoản miễn phí quốc tế chưa được công bố công khai dạng số tĩnh.
*   **Độ ổn định của OpenRouter `:free`:** Các model miễn phí trên OpenRouter được cung cấp dạng "Best effort" (có thì chạy, quá tải thì từ chối). Nếu dùng trong luồng tự động hoá, tỷ lệ lỗi mạng (drop rate) có thể khá cao.

---

### Nguồn tra cứu (Link trực tiếp)
1.  **Gemini API Limits:** [Google AI for Developers - Pricing](https://ai.google.dev/pricing)
2.  **Zhipu Z.ai Pricing:** [Z.ai Docs - Pricing (Flash Tier)](https://docs.z.ai/guides/overview/pricing)
3.  **Groq Rate Limits:** [GroqCloud Docs - Rate Limits](https://console.groq.com/docs/rate-limits)
4.  **OpenRouter Limits:** [OpenRouter - Limits & Pricing](https://openrouter.ai/docs#limits)
5.  **Cloudflare Workers AI:** [Cloudflare Docs - AI Pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/)
6.  **DeepSeek Pricing:** [DeepSeek Platform - Pricing](https://platform.deepseek.com/api-docs/pricing/)
7.  **Alibaba DashScope Qwen:** [DashScope Console](https://dashscope.console.aliyun.com/) (Yêu cầu login để xem chiết khấu USD chính xác theo ngày).
