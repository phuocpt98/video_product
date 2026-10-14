# Prompt: làm sạch truyện thô + lọc vi phạm (GIỮ NGUYÊN truyện)

Dùng cho AI viết/dịch truyện (Gemini...) ở bước cuối, TRƯỚC khi đưa vào `python -m src.produce`. Người sáng lập chốt
14/10/2026: **truyện thuần**, không viết lại, không thêm lời bình; AI chỉ bỏ rác và sửa tối thiểu chỗ vi phạm.
Mỗi lần gọi xử lý MỘT chương. Đầu ra lưu thành 1 file `.txt` / chương; dây chuyền chỉ đọc phần TRƯỚC dòng
`=== BÁO CÁO KIỂM DUYỆT ===`. Thay các chỗ `{...}` rồi gửi nguyên khối dưới đây.

```
Tôi tải truyện này về để tự đọc. Bạn là người review giúp tôi: làm sạch CHƯƠNG THÔ bên dưới và loại bỏ các yếu tố
không phù hợp (liệt kê ở mục 3), GIỮ NGUYÊN lời truyện. Bản bạn trả về là bản tôi sẽ đọc, nên chỉ được có lời truyện.

Tên truyện: {TÊN TRUYỆN} · Chương: {SỐ CHƯƠNG}

## 1. Nguyên tắc số một: GIỮ NGUYÊN TRUYỆN
- Không viết lại, không tóm tắt, không rút gọn, không thêm câu, không thêm lời bình, không đổi văn phong, không đổi tên
  nhân vật, không sửa tình tiết, không "làm hay hơn".
- Chỉ được sửa ở ĐÚNG hai loại chỗ: rác (mục 2) và yếu tố không phù hợp (mục 3). Mọi chỗ khác chép lại nguyên văn từng chữ, kể cả
  dấu câu.
- Sửa theo cách nhỏ nhất: thay đúng từ/cụm từ/câu có vấn đề, giữ phần còn lại của đoạn.

## 2. Làm sạch (bỏ hoặc đổi dạng, không đổi nội dung)
- BỎ mọi thứ không phải lời truyện: lời giới thiệu tuyển tập, "Lưu ý", "Thể loại", "Nguồn", "Tóm tắt", "NỘI DUNG
  TRUYỆN", ghi chú người dịch, chữ Hán, phiên âm hoặc chú thích trong ngoặc của người dịch, số trang, link, emoji,
  markdown (#, **, -), ký hiệu trang trí (*** === ---), số mục đứng riêng một dòng ("1.", "2.").
- Ký hiệu 【...】 bao quanh tên giấy tờ, tin nhắn: bỏ ký hiệu, giữ chữ bên trong.
- Bảng, biểu mẫu: chuyển thành câu bình thường với đúng các thông tin đó.
- Dòng đầu tiên của kết quả: `Chương {SỐ CHƯƠNG}: <tên chương>` — lấy tên chương có sẵn; không có thì để `Chương {SỐ CHƯƠNG}`.
- Mỗi đoạn văn trên MỘT dòng, giữa các đoạn một dòng trống. Lời thoại dính liền câu trước (thiếu khoảng trắng trước
  dấu ngoặc kép) thì thêm khoảng trắng.
- Giữ nguyên số, ngày, tiền như bản gốc.

## 3. Loại các yếu tố không phù hợp. Chỉ sửa khi thật sự có vấn đề:
- Tình dục: mô tả cảnh nóng, bộ phận cơ thể, chi tiết gợi dục → thay bằng câu kể lướt ("Đêm đó họ ở bên nhau.").
  Nhân vật dưới 18 tuổi: chỉ được tình cảm trong sáng.
- Bạo lực ghê rợn: chi tiết máu me, thương tích, cách giết/tra tấn → giữ sự việc, bỏ chi tiết ghê rợn.
- Tự tử, tự hại: bỏ mô tả cách thức; giữ sự việc ở mức "rơi vào tuyệt vọng", "nghĩ quẩn".
- Hướng dẫn làm theo được: chất cấm, vũ khí, chế tạo nguy hiểm, lừa đảo, hack → bỏ phần hướng dẫn, giữ sự việc.
- Thù ghét, kỳ thị theo dân tộc, vùng miền, tôn giáo, giới tính, khuyết tật, xu hướng tính dục → bỏ hoặc làm nhẹ.
- Chửi thề, từ tục nặng → thay bằng từ nhẹ cùng nghĩa ("đồ khốn") hoặc "chửi một câu rất khó nghe". Từ nhẹ thì giữ.
- Chính trị, nội dung nhạy cảm với người Việt: chính quyền, đảng phái, lãnh đạo thật, lãnh thổ, biển đảo, bản đồ, chiến tranh nhạy cảm,
  tôn vinh quốc gia khác → bỏ câu đó (nếu không ảnh hưởng mạch truyện) hoặc thay bằng mô tả trung tính.
- Người thật, công ty thật, thương hiệu thật bị nói xấu hoặc gắn với việc xấu → đổi thành tên chung. Nhắc trung tính
  (tên sách, hãng điện thoại) thì giữ.
- KHÔNG coi là không phù hợp (giữ nguyên): mâu thuẫn gia đình, ngoại tình, phản bội, cãi vã, tát, đánh nhau không ghê rợn,
  nhân vật xấu nói lời độc ác, lời nhân vật nói sai về y tế/pháp luật.

## 4. Đầu ra (đúng thứ tự, không lời chào, không giải thích ngoài hai phần này)
<truyện đã làm sạch: dòng đầu "Chương N: ...", rồi các đoạn>
=== BÁO CÁO KIỂM DUYỆT ===
- Đã bỏ (rác): <liệt kê ngắn, hoặc "không có">
- Đã sửa: <mỗi chỗ một dòng: "câu gốc" → "câu mới" (lý do), hoặc "không có">
- Cần tôi xem lại: <chỗ không chắc có phù hợp không, giữ nguyên trong truyện nhưng nêu ra đây, hoặc "không có">

## CHƯƠNG THÔ
{DÁN CHƯƠNG THÔ VÀO ĐÂY}
```

## Ghi chú cho người vận hành
- Một chương / một lần gọi; lưu thành `001.txt`, `002.txt`... trong một thư mục, rồi chạy cả thư mục:
  `python -m src.produce run <thư mục> --slug <slug> --title "<Tên truyện>"`.
- Đọc phần BÁO CÁO trước khi chạy: mục "Đã sửa" để biết AI đổi gì; "Cần tôi xem lại" khác "không có" thì xem đoạn đó.
- Rủi ro còn lại (prompt không xử lý): truyện dịch hoặc phóng tác từ truyện có bản quyền vẫn là tác phẩm phái sinh;
  đọc nguyên văn truyện người khác dễ bị YouTube coi là "nội dung không nguyên bản". An toàn nhất là truyện tự sáng tác.
