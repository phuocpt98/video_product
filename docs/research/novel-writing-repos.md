# Nghiên cứu repo viết truyện bằng AI

Cập nhật: 25/9/2026 · Code đã clone vào `tool/` (chỉ bản mới nhất, không kèm lịch sử commit) · Dùng cho Bước 2–3 trong [plans/technical.md](../plans/technical.md)

Mục đích: tìm cách biến **truyện có sẵn** → **khung truyện** (dàn ý, nhân vật, thế giới) → **học phong cách** → **viết lại thành kịch bản nghe tiếng Việt**. Người Trung gọi cách này là **拆书 + 仿写** (rã sách + viết phỏng theo).

## 1. Kết luận nhanh

- **Không cài nguyên repo nào.** Cả 6 repo đều viết tiếng Trung, làm ra tiểu thuyết để đọc chứ không phải kịch bản để nghe, và code gắn chặt với giao diện riêng của chúng.
- **Lấy phương pháp, tự viết code và prompt bằng lời của mình.** Hai repo dùng giấy phép copyleft (GPL/AGPL), hai repo không có giấy phép. Copy nguyên văn code hoặc prompt là rủi ro, lấy ý tưởng thì không sao.
- **Chưa repo nào có lời bình người kể hay nhịp đọc cho audio.** Phần này phải tự thiết kế.

| Repo | Giấy phép | Ngôn ngữ, công nghệ | Lấy gì |
|---|---|---|---|
| [pikachuNovel](https://github.com/nqclymt/pikachuNovel) | **GPL-3.0**: chỉ lấy ý tưởng | Python, FastAPI, ~19k dòng | **Quy trình rã truyện tốt nhất:** thẻ chương, đoạn truyện, bản thiết lập, học văn người thật, luật khử văn AI |
| [Long-Novel-GPT](https://github.com/MaoXiaoYuZ/Long-Novel-GPT) | **Không có**: coi như giữ bản quyền | Python, Flask, ~4,5k dòng | Mô hình 3 tầng dàn ý → tình tiết → văn, prompt rút tình tiết, prompt căn khớp sau khi viết lại |
| [FuFu-Novel-Writing](https://github.com/usagifufu/FuFu-Novel-Writing) | **Không có** (thư mục `references/` bên thứ ba là MIT) | Skill cho Claude Code, script Python thuần | **Thẻ phong cách bằng số liệu**, bộ kiểm tra văn AI, giao thức Sepia, sổ theo dõi tình tiết cài cắm |
| [AI_NovelGenerator](https://github.com/YILING0013/AI_NovelGenerator) | **AGPL-3.0**: chỉ lấy ý tưởng | Python, langchain, Chroma | **Giữ mạch truyện dài:** 3 file trạng thái, cây trạng thái nhân vật, quy trình chuẩn bị trước mỗi chương |
| [ai-novel-lab](https://github.com/xindoo/ai-novel-lab) | MIT | Chỉ có AGENTS.md và prompt | Quy tắc "bản tóm tắt thắng dàn ý", cấm nhắc kiểu "như chương 40", checklist từng chương |
| [chinese-novelist-skill](https://github.com/PenglongHuang/chinese-novelist-skill) | MIT | Skill, 1 script | **13 kiểu câu móc cuối chương**, thang độ căng 5 mức, từ điển thiết lập có cột "người đọc đã biết" |

## 2. pikachuNovel: quy trình rã truyện (nên theo)

Đơn vị xử lý là **một chương**, không cắt ngắn. Kết quả mỗi chương được lưu cache theo mã băm (hash) nội dung, nên chạy lại chỉ xử lý chương đã thay đổi. Rã truyện gồm 4 lớp:

1. **Thẻ chương**, mỗi chương 1 file JSON. LLM chạy ở nhiệt độ 0,2. JSON sai thì gửi lại lỗi cho LLM sửa, tối đa 3 lần. Các trường:
   - `tom_tat` ~600 chữ: chuyện gì xảy ra, nguyên nhân, hành động, xung đột, câu móc cuối chương. Không đánh giá chung chung.
   - `nhip_chuong`:
     - nội dung lõi, ví dụ "nguy cơ + phát hiện bàn tay vàng + cảm xúc"
     - tông cảm xúc, ví dụ "căng thẳng + mong chờ + hoảng"
     - chi tiết nhịp
   - `tuyen_truyen`: các mốc nối bằng "+", ví dụ "xuyên không + nguy cơ đầu + nhân vật phụ xuất hiện + bàn tay vàng + câu móc".
   - `diem_sang` 1–6: câu thoại đắt, điểm "vả mặt" khiến người đọc muốn bình luận.
   - Quy tắc: **không bịa nhân vật hoặc năng lực không có trong truyện.**
2. **Học văn người thật.** Mỗi chương lấy 1–3 đoạn gốc ở đầu, giữa và cuối (~1.000–2.400 chữ). Đoạn được gắn nhãn loại cảnh và đo độ dài câu, độ dài đoạn, tỉ lệ thoại. Từ đó sinh "hồ sơ tác giả" (Author Bible).
3. **Đoạn truyện theo ranh giới tự nhiên.** Cửa sổ trượt khoảng 8 thẻ chương, đoạn dài tối đa 12 chương. Phần chưa khép lại được chuyển sang cửa sổ sau, không cắt cho đủ số chương.
   - Ranh giới là chỗ: đạt hoặc hỏng mục tiêu, xung đột được giải quyết, thân phận hoặc quan hệ thay đổi, khủng hoảng leo thang sang vấn đề mới.
   - Các trường: cấu trúc (khởi → dồn ép → lật → giải quyết), hành động nhân vật chính, nhịp cảm xúc, **điểm sướng**, thay đổi nhân vật, được và mất, tình tiết cài cắm.
4. **Khung tổng.**
   - **Dàn ý quyển:** tổng quan, 3 hồi, danh sách nhân vật (chính, phản diện, chức năng), tình tiết cài cắm, 2–3 cao trào.
   - **Dàn ý toàn truyện:** thế giới, **bàn tay vàng** (năng lực đặc biệt của nhân vật chính), 3–5 cao trào kèm đoạn dồn nén trước mỗi cao trào, hồ sơ nhân vật, 5–8 tình tiết cài cắm dài hơi, **ai biết gì**, hệ thống sức mạnh.

**Luật khử văn AI** (dựa trên Humanizer-zh, viết cho tiếng Trung, cần làm lại danh sách cho tiếng Việt):
- **Nguyên tắc:** không đổi sự kiện, thứ tự, con số, câu móc. Độ dài giữ trong 95–110%. Chẩn đoán trước, chỉ sửa chỗ thật sự có vấn đề.
- **Lỗi cần sửa:**
  - câu đối xứng quá gọn
  - giải thích lại điều hành động đã cho thấy
  - gọi tên cảm xúc thẳng ra
  - câu nào cũng có ẩn dụ, đoạn nào cũng kết bằng câu chốt
  - nhịp câu ngắn rập khuôn
- **Cụm phải viết lại:**
  - "không phải A mà là B"
  - "khoảnh khắc này hắn cuối cùng đã hiểu"
  - "bánh xe vận mệnh"
  - "cả thế giới như ngừng lại"
  - "trong mắt loé lên…"
  - "khoé môi cong lên"
  - "hít một ngụm khí lạnh" (tối đa 1 lần mỗi chương)
- **Kiểm tra cuối:** xem lại ngẫu nhiên 3 chỗ đã sửa. Nếu câu mới chỉ đẹp hơn mà không đúng hay tự nhiên hơn thì trả về câu cũ.

**Viết chương** (chỉ tham khảo, vì repo này làm truyện mới):
- Dàn ý chương là **bản thiết kế duy nhất**.
- Đoạn văn người thật là chuẩn phong cách cao nhất.
- Không chép nhân vật, câu văn hay ẩn dụ đặc trưng của mẫu.

**Không hợp với mình:**
- Giai đoạn 仿写 được làm ra để tạo truyện **khác** truyện gốc.
- Chỉ nhìn dàn ý của đúng chương trước, nên yếu mạch dài.
- Nặng thể loại tu tiên.
- Tốn khoảng 4 lần gọi LLM cho mỗi chương.

## 3. Long-Novel-GPT: mô hình 3 tầng

- **Mô hình dữ liệu.** Mọi thứ lưu dạng cặp (tầng trên, tầng dưới):
  - dàn ý truyện ↔ dàn ý chương
  - dàn ý chương ↔ **tình tiết** (mỗi dòng ≤50 chữ, một cảnh hoặc bước ngoặt)
  - tình tiết ↔ văn
- **Tình tiết là trục giữa.** Đây là chỗ hợp với mình nhất: rút tình tiết từ truyện gốc, rồi viết lời kể theo từng khối tình tiết.
- **Prompt rút tình tiết:** khớp 1–1 với văn gốc, không mở rộng, không suy diễn trước kết cục. Bỏ tả cảnh, nội tâm, ngoại hình, thoại.
- **Prompt rút dàn ý chương:** theo mạch nhân → diễn biến → cao trào → kết quả, không liệt kê.
- **Căn khớp sau khi viết lại.** LLM phụ trả về JSON `{"1":[1,2],...}` ghép mỗi tình tiết với các đoạn văn tương ứng, nhờ vậy sửa một chỗ không làm lệch chỗ khác.
- **Vòng duyệt → viết lại:**
  - Vai "tổng biên tập" chấm nhịp (quá nhanh, quá chậm, quá phẳng).
  - Sau đó viết lại theo nhận xét. Nếu không cần sửa thì giữ nguyên.
- **Bước dọn format:**
  - không để đoạn quá dài
  - giữ một điểm nhìn
  - xoá câu lặp và tiêu đề
- **Phong cách:** chỉ là danh sách câu cửa miệng của tác giả viết tay vào prompt, không phải học từ văn bản.
- **Điểm yếu:**
  - Chỉ xử lý 20.000 chữ đầu.
  - Dàn ý tổng bị cắt còn các mẩu 100 chữ.
  - Giới hạn 4.096 token.
  - **Không rút nhân vật hay thế giới**, dù README có nói.
  - Tách chương chỉ theo mẫu "第N章".

## 4. FuFu-Novel-Writing: thẻ phong cách và kiểm tra văn AI

**Thẻ phong cách** (`scripts/style_analyze.py`, tính bằng số liệu, không dùng LLM):
- Độ dài câu trung bình và tỉ lệ câu ngắn/vừa/dài/rất dài.
- Độ dài đoạn, tỉ lệ đoạn ngắn/dài.
- Dấu câu trên 1.000 chữ, tần suất dấu hỏi và chấm than.
- Tỉ lệ chữ trong thoại, tỉ lệ đoạn có thoại.
- Cặp chữ hay dùng, trợ từ ngữ khí, câu hỏi tu từ, cấu trúc "không phải… mà là".

Quy trình:
1. Làm sạch mẫu.
2. Đo số liệu.
3. LLM mô tả phong cách theo 6 chiều: từ vựng, câu, miêu tả, thoại, nhịp, lời kể.
4. Gộp thành `style_card.md`, trong đó có mục **"nét không được chép"**.
5. Viết thử 300–500 chữ để hiệu chỉnh.

**Kiểm tra văn AI.** Mọi cảnh báo chỉ là bằng chứng, không phải kết luận. Các phép đo **chuyển sang tiếng Việt được**:
- Hệ số biến thiên độ dài câu < 0,42: câu dài đều nhau quá, dấu hiệu văn AI.
- ≥4 đoạn mở đầu giống nhau.
- ≥3 dòng liền nhau bắt đầu bằng đại từ ("Hắn…").
- Cụm 4 từ lặp lại ≥4 lần.
- Mật độ liên từ > 7 trên 1.000 chữ.
- Ẩn dụ dồn cục: ≥3 trong 800 chữ.
- Cụm từ sáo rỗng, từ "biển báo" ("đáng chú ý là", "suy cho cùng").
- **Văn bị hỏng:** lặp đoạn, cụt giữa câu, lộ lời AI ("là một AI"), lộ từ kỹ thuật ("dàn ý", "chương sau").

**Lưu ý:** kịch bản nghe cố tình dùng câu ngắn, nên các cảnh báo "câu ngắn liên tiếp" và "đoạn một câu" phải nới ngưỡng.

**Giao thức Sepia** (MIT, dựa trên nghiên cứu StoryScope: chỉ riêng cấu trúc truyện đã nhận ra văn AI với F1 93%, sửa bề mặt câu chữ gần như không giúp). Sửa từ sâu ra nông:
1. **Tầng truyện:**
   - không nói thẳng chủ đề
   - không để nhân quả một đường thẳng
   - tránh kết kiểu "trưởng thành, chấp nhận, lựa chọn"
   - có neo vào đời thực
   - thỉnh thoảng nói trực tiếp với người nghe
2. **Tầng đoạn.** "Phép thử dàn ý": ghép các câu đầu đoạn lại mà thành bản tóm tắt thì đó là văn máy.
3. **Tầng câu chữ.**

Mỗi bài chỉ áp dụng 3–5 thay đổi, nhắm mức vừa phải, không lật sang cực ngược lại.

**Sổ tình tiết cài cắm:** ID | lời hứa | phụ thuộc | chương cài | chương đẩy | chương trả | trạng thái. Mỗi chương trả tối đa 2–3 tình tiết.

## 5. AI_NovelGenerator: giữ mạch truyện dài

Sau mỗi chương, cập nhật 3 thứ:
1. `tom_tat_chung.txt`: bản tóm tắt cuộn, tối đa ~2.000 từ, khách quan, không suy đoán.
2. `trang_thai_nhan_vat.txt`: mỗi nhân vật có đồ vật, năng lực, trạng thái thể chất và tinh thần, quan hệ, sự kiện đã kích hoạt. LLM sửa trực tiếp trên file cũ.
3. Kho vector, mỗi mẩu khoảng 500 chữ.

Trước mỗi chương:
1. Tóm tắt ngắn 3 chương gần nhất kèm dàn ý chương này và chương sau. Chỗ mâu thuẫn đánh dấu [!].
2. Sinh 3–5 cụm từ khoá.
3. Tìm trong kho vector.
4. LLM lọc kết quả: bỏ nội dung lặp, đánh dấu mâu thuẫn.
5. Đưa **đoạn kết của chương trước** vào prompt.

`Character_Import_Prompt` rút trạng thái nhân vật từ văn có sẵn, dùng thẳng được cho bước rã truyện.

## 6. chinese-novelist-skill và ai-novel-lab: câu móc và checklist

**13 kiểu câu móc cuối chương:**
- hé lộ bất ngờ
- nguy cơ ập tới
- hành động bị cắt ngang
- lật thân phận
- thế khó
- vật bí ẩn
- hạn chót
- lời hứa hoặc đe doạ
- biến mất khó tin
- lời có ẩn ý
- hình ảnh lặp lại
- vọng lại câu mở đầu
- **móc im lặng** (chỉ tả phản ứng)

**Thang độ căng 5 mức:** tò mò → lo → gấp → sống còn → tột cùng. Nhịp đi theo sóng: thấp–vừa–cao–thấp–vừa–cao–cao hơn.

**Từ điển thiết lập** có cột **"người đọc đã biết"** đến chương nào. Lời kể không được tiết lộ quá cột này. Cột này rất quan trọng khi kể lại truyện có sẵn, để không lỡ tiết lộ trước.

**Thứ tự đưa vào prompt:** bảng biểu đặt trước, **văn đặt sau cùng** (500–800 chữ cuối chương trước và đoạn mẫu phong cách), để LLM "nghe" văn ngay trước khi viết.

**Checklist của ai-novel-lab:**
- Nhân vật nhất quán, dòng thời gian khớp.
- Không nhắc kiểu "như chương 40".
- Mỗi chương có ≥3 điểm sướng nhỏ và 1 cao trào.
- Chương nào cũng kết bằng câu móc.
- Xung đột được "trả" trong 1–3 chương.
- Bài học: chỉ dựa vào bản tóm tắt thì mạch bắt đầu trôi sau khoảng 50 chương.

## 7. Module lấy lại từ repo cũ `tiktok_content`

| Module | Dùng cho |
|---|---|
| `src/tts-engine.py` (edge-tts HoaiMy/NamMinh) | Khung gọi TTS. edge-tts chỉ dùng thử nghiệm, không dùng thương mại (xem [ai-services.md](ai-services.md) §5) |
| `src/video-assembler.py`, `photo-to-video.py`, `text-overlay.py` | Bước 7 dựng video, phụ đề, Bước 9 cắt clip TikTok |
| `docs/video-production-format.md` (1080×1920, 30fps, CRF 21) | Chuẩn xuất clip TikTok |
| `scripts/analyze-channel.py` (yt-dlp và tikwm) | Theo dõi đối thủ định kỳ |
| `scripts/split-video-by-scenes.py` (scenedetect) | Cắt clip AI **tự tạo** thành kho clip nền |
| `src/gemini-client.py` | Ứng viên LLM |

**Không lấy:**
- Kho clip cắt từ kênh khác.
- Tool tự đăng TikTok bằng cookie.
- `.env` và `cookies.json`.
