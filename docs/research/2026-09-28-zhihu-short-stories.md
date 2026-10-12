> **Ghi chú của Điều phối (28/9/2026, CHƯA duyệt).** Báo cáo do researcher trên agy (Gemini) soạn, kèm research Người sáng lập tự tìm. Người sáng lập chốt cách dùng: **tải truyện gốc chỉ làm tài liệu**, tự viết truyện mới và dựng phim (`python -m src.drama new <slug> --motif "…" --ref stories/<slug>/source/goc.txt`). Điều chỉnh khi đọc:
> - **Không dùng** nguồn đăng lậu truyện trả phí (`onehu.xyz`, `ifun.cool` ở mục 6.3) và bản dịch của người khác (group Facebook, Wattpad, Truyenfull, Wikidich). Nguồn text nên dùng: bản web miễn phí chính thức của 番茄 và 七猫, truyện miễn phí trên Zhihu, bài tóm tắt trên 小红书, B站 và 豆瓣.
> - "Rủi ro gần như bằng 0" ở mục 7 là **nói quá**. Bám khung quá sát (cùng chuỗi tình tiết đặc trưng) vẫn có thể bị coi là phái sinh. Vì vậy prompt bắt đổi toàn bộ tên, bối cảnh, chi tiết đặc trưng, tự viết mọi lời và thêm ít nhất 2 tình tiết mới.
> - Danh sách 25 truyện chưa kiểm chứng từng tên và link. Mở nguồn gốc kiểm lại trước khi dùng.
> - Độ dài: giọng đọc của kênh (tốc độ 1,34) đọc khoảng 250–300 chữ Việt mỗi phút, nên video 30 phút cần truyện gốc khoảng 6.000–8.000 chữ Hán.

Dưới đây là báo cáo nghiên cứu chi tiết dành cho kênh YouTube "Khoai Tây Review" về nguồn truyện ngắn Trung Quốc (Zhihu, Fanqie, v.v.), cách thức khai thác (仿写), và rủi ro bản quyền.

# Báo cáo Nghiên cứu: Nguồn Truyện Ngắn (Zhihu/Đại Lục) Cho Kênh YouTube Kể Truyện

## 1. Tóm tắt (5 ý chính)
1. **Nền tảng & Cấu trúc:** Truyện ngắn "kiểu Zhihu" (1-3 vạn chữ) được tối ưu hóa cực đoan cho nền kinh tế sự chú ý. Cốt lõi là "3 chương 1 lần lật mặt (反转)", mở đầu bằng cú sốc (tạo sự tò mò ngay từ 300 chữ đầu) và dùng ngôi thứ nhất để tăng độ chân thực.
2. **Mô-típ ăn khách:** Đa số các truyện hot nhất ở mảng nữ chính xoay quanh các khái niệm: Báo thù, Vả mặt (打脸), Thức tỉnh (từ bỏ mộng tưởng tình yêu), Nhìn thấu tra nam/trà xanh, và Trọng sinh để chuộc lỗi với bản thân. Sự sảng khoái (爽点) đến từ việc nhân vật chính dứt khoát không tha thứ.
3. **Bản quyền & YouTube:** Dịch nguyên văn hoặc cắt ghép thô sơ truyện Zhihu có nguy cơ dính "Gậy Bản Quyền" (Copyright) từ phía tác giả Trung Quốc, và rủi ro dính lỗi "Nội dung sử dụng lại" (Reused Content) của YouTube khiến kênh không thể bật kiếm tiền.
4. **Giải pháp 仿写 (Phỏng tả - Viết theo khung):** Lấy cốt truyện, mô-típ và tình huống của truyện Trung Quốc làm "khung xương", nhưng phải đổi hoàn toàn chi tiết, bối cảnh, tên nhân vật, và quan trọng nhất là "lời thoại" sang lối kể đậm chất Việt Nam. Đây là ranh giới an toàn nhất.
5. **Nguồn đọc Full Text hợp lệ:** Có thể đọc truyện miễn phí trên các trang chính thức có kèm quảng cáo (như Fanqie, Qimao) hoặc qua các trang tổng hợp nội dung Zhihu của bên thứ ba. Tuy nhiên, việc xin cấp quyền làm audio (Audio adaptation) từ Zhihu cực kỳ khó; kênh YouTube Việt hiện tại đa phần đang lách luật bằng cách viết lại.

---

## 2. Nền tảng truyện ngắn Trung Quốc
Dưới đây là các nền tảng chính cung cấp thể loại truyện ngắn/tiểu thuyết đẩy mạnh:

| Nền tảng | Loại truyện nổi bật | Độ dài điển hình | Phí & Mô hình | Bảng xếp hạng |
| :--- | :--- | :--- | :--- | :--- |
| **知乎 (Zhihu - 盐言故事)** | Truyện góc nhìn thứ nhất, vả mặt, hồi hộp, kịch tính, não động (ý tưởng lạ). | 1–3 vạn chữ | **Trả phí** (Gói tháng/năm). Đọc thử miễn phí chương đầu. | [Zhihu Short Story Ranking](https://www.zhihu.com/) (Xem trong app 盐言故事) |
| **番茄小说 (Fanqie)** | Hệ thống, trọng sinh, sủng ngọt, làm giàu thập niên. Rất nhiều "mã giáp" (giấu nghề). | 2–5 vạn chữ (ngắn), đa phần là truyện dài | **Miễn phí** (Xem quảng cáo). | Bảng xếp hạng minh bạch trên web/app. |
| **七猫小说 (Qimao)** | Ngôn tình, tổng tài, gia đấu, điền văn. Tương tự Fanqie. | 3–5 vạn chữ | **Miễn phí** (Xem quảng cáo). | Bảng xếp hạng trong app. |
| **豆瓣阅读 (Douban)** | Văn học hiện thực, nữ quyền, trinh thám, chữa lành, tâm lý xã hội. | 3-10 vạn chữ | **Trả phí / Miễn phí** đan xen. | Bảng xếp hạng chất lượng văn học cao. |
| **每天读点故事 (Meitian)** | Truyện kinh dị, tình cảm đời thường, kịch tính gia đình. | 1-2 vạn chữ | **Trả phí/Miễn phí**. | Nổi tiếng với truyện ngắn chất lượng. |
| **抖音/快手 小说推文** | Không phải nền tảng đọc, mà là kênh review tóm tắt truyện, dẫn link đọc. | Review 3-5 phút | N/A | Bảng trend TikTok Trung Quốc (Douyin). |

---

## 3. Danh sách 25 truyện ngắn nữ chính hot (2025–2026 & Kinh điển)
*Lưu ý: Bảng tổng hợp bao gồm các truyện đang làm mưa làm gió trong vài năm gần đây và các truyện kinh điển tạo ra trào lưu trên Zhihu / Fanqie.*

| Tên gốc (Tiếng Trung) | Nền tảng | Mô-típ (1 câu) | Vì sao hot (Điểm sáng) |
| :--- | :--- | :--- | :--- |
| 1. 河清海晏 | Zhihu | Nữ cường, quyền mưu triều chính. | Nữ chính dùng mưu lược xoay chuyển càn khôn, không lụy tình. |
| 2. 洗铅华 | Zhihu | Ác nữ phụ trọng sinh tẩy trắng. | Góc nhìn nữ phụ tự cứu lấy mình, đã chuyển thể thành phim (Vi Hữu Ám Hương Lai). |
| 3. 照殿红 | Zhihu | Vòng lặp thời gian, cứu bạch nguyệt quang. | Cấu trúc kể truyện không gian/thời gian kín (closed loop) cực kỳ hack não. |
| 4. 宫墙柳 | Zhihu | Phản sủng ái chốn hậu cung. | Các phi tần không cung đấu mà yêu thương nhau, phơi bày sự tàn khốc của đế vương. |
| 5. 扳命人 | Zhihu | Huyền nghi, thế thân phục thù. | Yếu tố trinh thám và lột mặt nạ từng lớp cực gắt. |
| 6. 真假千金之觉醒 | Fanqie | **真假千金 (Thật giả thiên kim)** | Nữ chính (thật) thức tỉnh, không thèm tình thương của gia đình, trực tiếp rời đi tự lập. |
| 7. 离婚冷静期，我中了一亿 | Zhihu | **离婚冷静期 (Kỳ hòa giải ly hôn)** | Bị chồng ruồng bỏ, đột nhiên trúng số nhưng phải giấu kín để chia tài sản. |
| 8. 恶毒婆婆重生了 | Zhihu | **恶毒婆婆 (Mẹ chồng ác độc)** | Mẹ chồng kiếp trước hành hạ con dâu, kiếp này trọng sinh bênh vực con dâu đánh tra nam. |
| 9. 拒绝扶弟魔后 | Zhihu | **扶弟魔 (Phù đệ ma - Bóc lột vì em trai)** | Chặt đứt quan hệ với gia đình ruột thịt hút máu, tìm lại cuộc sống tự do. |
| 10. 替身拒绝转正 | Zhihu | **替身 (Thế thân)** | Tổng tài muốn thế thân thành vợ thật, nhưng nữ chính lấy đủ tiền bồi thường rồi cao chạy xa bay. |
| 11. 夫人马甲轰动全城 | Fanqie | **马甲 (Mã giáp - Giấu nghề)** | Nữ chính nhìn yếu đuối nhưng thực chất là đại ca giang hồ, hacker, thần y... |
| 12. 黑月光拿稳be剧本 | Qimao | **虐恋 (Ngược luyến, BE)** | Nữ chính dứt tình dứt nghĩa, khiến nam chính hối hận suốt đời (Truy thê hỏa táng tràng). |
| 13. 拯救恋爱脑弟弟 | Zhihu | **打脸小三 (Vả mặt tiểu tam)** | Chị gái ra tay chỉnh đốn đứa em trai não yêu đương và cô bạn gái bòn rút tài sản. |
| 14. 慕洋女友翻车了 | Zhihu | **凤凰男/崇洋 (Sính ngoại/Phượng hoàng nam)** | Vạch trần bản chất người yêu tham phú phụ bần, sính ngoại. |
| 15. 七十新生 | Zhihu | **大女主 (Đại nữ chủ, Thức tỉnh tuổi xế chiều)**| Bà lão 70 tuổi ly hôn người chồng gia trưởng để sống cho mình, đâm trúng tâm lý độc lập. |
| 16. 被全网黑后靠发疯洗白 | Fanqie | **娱乐圈 (Giới giải trí, Phát điên)** | Thay vì nhẫn nhịn, nữ chính "phát điên" chửi thẳng mặt anti-fan và đồng nghiệp trà xanh lại được yêu thích. |
| 17. 穿成年代文娇娇女 | Qimao | **年代文 (Niên đại văn 70-80s)** | Xuyên không về thời bao cấp, làm giàu từ hai bàn tay trắng, nữ chính tháo vát. |
| 18. 近视眼勇闯恐怖游戏 | Zhihu | **规则怪谈 (Luật lệ kinh dị)** | Pha trộn giữa kinh dị và hài hước, nữ chính phá đảo game kinh dị vì... cận thị không thấy ma. |
| 19. 重生不当舔狗 | Fanqie | **重生复仇 (Trọng sinh báo thù)** | Kiếp trước hy sinh tất cả cho nam chính/người thân bị hãm hại, kiếp này cự tuyệt làm lốp dự phòng. |
| 20. 假少爷逼我退婚 | Zhihu | **假少爷 (Thiếu gia giả)** | Nam chính là thiếu gia giả làm loạn, nữ chính quyết định cưới thiếu gia thật đang ở đáy xã hội. |
| 21. 影后她只会种田 | Douban | **种田/治愈 (Điền văn, Chữa lành)** | Bỏ phố về quê, không đấu đá, tập trung tận hưởng cuộc sống bình dị. |
| 22. 全家读心术，吃瓜 | Fanqie | **读心术 (Thuật đọc tâm)** | Gia đình nghe được tiếng lòng của nữ chính bé nhỏ, từ đó thay đổi vận mệnh diệt vong. |
| 23. 假千金是玄学大佬 | Qimao | **玄学 (Huyền học/Tâm linh)** | Bị đuổi khỏi nhà giàu, nữ chính dùng thuật phong thủy/bắt ma để làm tỷ phú. |
| 24. 绿茶女配不想干了 | Zhihu | **女配觉醒 (Nữ phụ thức tỉnh)** | Kịch bản bắt làm trà xanh nữ phụ, nhưng nữ chính lười biếng đình công, vô tình thu hút nam chính. |
| 25. 渣男叔叔宠我上天 | Fanqie | **换男主 (Đổi nam chính)** | Bị nam chính cắm sừng, nữ chính quay xe yêu luôn chú ruột/kẻ thù của nam chính để làm trưởng bối. |

---

## 4. 12 Mô-típ (套路) thống kê & Cấu trúc nhịp điệu điển hình
**Cấu trúc nhịp điệu của một truyện Zhihu chuẩn (1 - 3 vạn chữ):**
- **Độ dài:** 10,000 - 30,000 chữ (Chia làm 10-15 chương nhỏ, mỗi chương 800-1500 chữ).
- **Mở đầu (100 chữ đầu):** Bắt buộc phải có câu sốc (Hook). VD: *"Ngày sinh nhật con gái, chồng tôi lại đang đăng ảnh đi chọn nhẫn cưới cho tình đầu của anh ta."*
- **Ngôi kể:** 99% dùng ngôi thứ nhất "Tôi (我)" để tăng tối đa tính chân thật.
- **Nút thắt (Sự cố):** Xuất hiện ngay trong 500 chữ đầu. Không miêu tả bối cảnh dài dòng.
- **Nhịp lật mặt (反转):** Cứ 2000-3000 chữ phải có một lần lật mặt. VD: Tưởng tiểu tam mang thai con chồng, hóa ra là con của tài xế.
- **Điểm sảng (爽点):** Nằm ở việc nữ chính tuyệt đối **không tha thứ, không quay đầu**. Sự trừng phạt dành cho phe phản diện phải mang tính triệt để (mất hết tài sản, vào tù, bị dư luận chà đạp).

**12 Mô-típ (套路) nữ chính được ưa chuộng nhất:**
1. **真假千金 (Thật giả thiên kim):** Xung đột huyết thống, thiên kim thật thường chọn tự lập thay vì tranh giành tình thương.
2. **追妻火葬场 (Truy thê hỏa táng tràng):** Nam chính nhận ra sai lầm, theo đuổi lại vợ nhưng vợ cự tuyệt đến cùng (Thường dẫn đến kết BE cho nam chính).
3. **恶毒女配觉醒 (Ác nữ phụ thức tỉnh):** Biết mình là bia đỡ đạn trong tiểu thuyết, quyết định không đi theo kịch bản để tránh cái chết.
4. **替身逆袭 (Thế thân nghịch tập):** Bị coi là thế thân cho "bạch nguyệt quang", nhưng lấy tiền rồi rời đi mở sự nghiệp riêng.
5. **重男轻女/扶弟魔 (Trọng nam khinh nữ):** Trả thù/cắt đứt với cha mẹ tồi và em trai ăn bám.
6. **手撕绿茶/小三 (Xé xác trà xanh/tiểu tam):** Dùng IQ và bằng chứng để đập tan bộ mặt giả tạo của tiểu tam, ly hôn lấy sạch tài sản.
7. **重生搞钱 (Trọng sinh kiếm tiền):** Thay vì yêu đương, nữ chính sống lại chỉ quan tâm đến việc học và làm giàu.
8. **读心术吃瓜 (Thuật đọc tâm):** Xung quanh ai cũng nghe được tiếng lòng của nhân vật chính, tạo ra yếu tố hài hước, giải oan.
9. **真假少爷/凤凰男 (Thiếu gia giả/Phượng hoàng nam):** Bóc trần bộ mặt thật của kẻ nam đào mỏ hoặc giả mạo thân phận.
10. **婆媳大战 (Đại chiến mẹ chồng nàng dâu):** Nhưng có biến tấu (VD: Mẹ chồng và con dâu liên thủ đánh chồng ngoại tình).
11. **玄学打脸 (Huyền học vả mặt):** Dùng năng lực tâm linh, phong thủy để vạch mặt kẻ xấu hoặc thay đổi số mệnh.
12. **换亲/退婚 (Đổi chồng/Từ hôn):** Bị từ hôn, lập tức gả cho người quyền thế hơn (thường là người chú/bác/sếp của tra nam).

---

## 5. Bản quyền và rủi ro: Ranh giới an toàn cho "仿写"
* **Bản quyền Zhihu (盐选):** Các truyện trả phí trên Zhihu đều được Zhihu mua đứt độc quyền hoặc chia sẻ doanh thu gắt gao. 
* **Tình trạng YouTube Việt Nam hiện tại:** Các kênh đang làm "truyện ngắn Zhihu" đa phần lấy bản text gốc, dịch (bằng AI/người), và chuyển thành giọng đọc. Hành động này **vi phạm bản quyền**. Dù ghi nguồn tác giả, nếu tác giả hoặc đại diện Zhihu report, kênh vẫn sẽ "bay" gậy bản quyền.
* **YouTube Reused Content:** Dù không bị đánh gậy, nhưng nếu chỉ là dịch -> đọc AI -> chèn hình tĩnh / game play / video stock, YouTube sẽ xếp vào diện "Reused Content" (Nội dung sử dụng lại) và từ chối bật kiếm tiền.

**Ranh giới an toàn cho 仿写 (Phỏng tả - Viết theo khung):**
Để kênh an toàn 100%, áp dụng quy tắc **"Giữ Khung - Đập Thịt"**:
- **ĐƯỢC GIỮ:** Tuyến tình cảm, cấu trúc lật mặt, mô-típ (VD: Bị từ hôn -> Lấy chú của người yêu -> Vả mặt lúc đám cưới). 
- **PHẢI THAY ĐỔI (Ranh giới an toàn):** 
  1. Tên nhân vật, địa danh, nghề nghiệp (Đổi bối cảnh sang Việt Nam hoặc bối cảnh hư cấu hoàn toàn).
  2. Lời thoại (Tuyệt đối không dịch word-by-word. Phải tự viết lại bằng văn phong mạng Việt Nam).
  3. Chi tiết đặc trưng (Nếu truyện Trung mâu thuẫn vì "bát canh gà", bạn đổi thành mâu thuẫn vì "tiền bỉm sữa").
  *Định nghĩa pháp lý: Bản quyền bảo hộ "hình thức thể hiện" (câu chữ), không bảo hộ "ý tưởng" (cốt truyện). Nếu bạn tự viết lại bằng lời văn của mình dựa trên ý tưởng đó, nó trở thành tác phẩm Original của bạn.*

---

## 6. Cách lấy dữ liệu hợp lệ & Nguồn TEXT
*Lưu ý: Không ủng hộ cào dữ liệu (crawl) hay mua bán lậu.*

1. **Đọc văn bản miễn phí hợp pháp:**
   - **Fanqie (番茄小说网页版) & Qimao (七猫网页版):** Cung cấp đọc trực tiếp trên trình duyệt máy tính, miễn phí toàn bộ nội dung (họ thu tiền từ quảng cáo banner). Không cần đăng nhập app vẫn đọc được. Khung truyện ở đây rất đa dạng.
   - **Zhihu miễn phí:** Biết cách tìm kiếm trên Zhihu với từ khóa `免费小说`, hoặc sử dụng tính năng đọc thử chương đầu (đủ để lấy được cấu trúc mở màn).

2. **Các trang tổng hợp, Review, tóm tắt (Spoil):**
   - Rất tốt cho việc tìm mô-típ: Lên Tiểu Hồng Thư (Xiaohongshu), Bilibili, Douban, tìm các từ khóa như `知乎短篇小说推荐`, `知乎盐选小说解说`. Các tài khoản review thường tóm tắt toàn bộ cốt truyện từ đầu đến cuối. Bạn chỉ cần lấy bản tóm tắt đó để tự viết lại kịch bản, không cần đọc full text gốc.

3. **Web bên thứ ba (Rủi ro đạo đức, nhưng tiếp cận text dễ):**
   - Các trang web như `onehu.xyz` (Tôi không phải Diêm Vương / Tôi không phải Diêm Thần) hoặc các kho lưu trữ `ifun.cool/zhihuyanxuan` chứa bản copy text của truyện Zhihu trả phí. Rất nhiều người dùng cách này để đọc văn bản đầy đủ mà không cần tài khoản, tuy nhiên chỉ nên dùng để tham khảo cốt truyện, **tuyệt đối không bôi đen copy-paste dịch thẳng**.

4. **Tác giả cho phép chuyển thể Audio?**
   - Rất hiếm. Tại Trung Quốc, bản quyền Audio (Hữu thanh) thường được các nền tảng bán cho Ximalaya hoặc các xưởng kịch truyền thanh. Không có "giấy phép mở" cho truyện thương mại. Do đó, kênh của bạn BẮT BUỘC phải đi theo con đường 仿写 (viết lại) để sở hữu bản quyền tác phẩm phái sinh.

---

## 7. So sánh: AI tự viết truyện từ mô-típ vs. Mượn cốt truyện có sẵn
| Tiêu chí | Kể lại truyện có sẵn (Dịch nguyên văn) | Tự viết/AI viết (Dựa trên khung có sẵn - 仿写) |
| :--- | :--- | :--- |
| **Chất lượng, Cảm xúc** | Rất tốt, vì đã được thị trường Trung Quốc kiểm chứng, tâm lý sâu sắc. | Ban đầu có thể hơi sượng nếu AI viết, cần biên tập viên người thật "mông má" lại câu chữ, thoại. |
| **Rủi ro Bản quyền** | **Cao** (Có thể bị khóa kênh bất cứ lúc nào). | **Gần như Bằng 0** (Ý tưởng không có bản quyền). |
| **Kiếm tiền YouTube** | Rủi ro "Reused Content" rất cao. | **An toàn.** Kịch bản gốc do bạn tạo ra + hình tự vẽ/AI render = Sáng tạo 100%. |
| **Đề xuất sử dụng** | Chỉ dùng khi muốn test thị trường kênh ẩn danh ngắn hạn (Hit & Run). | **Dùng cho kênh xây dựng thương hiệu lâu dài.** |

---

## 8. Đề xuất 5 Mô-típ nên làm tiếp cho kênh
*(Khác với 3 truyện kênh đã làm: Vợ trị chồng ngoại tình, Thiên kim thật giả, Trọng sinh không cứu kẻ vô ơn)*

1. **Kế mẫu không làm đá lót đường (后妈不干了):**
   - **Lý do:** Đánh trúng tâm lý ức chế về những đứa con riêng (hoặc con nuôi) phản nghịch. Nữ chính kiếp trước hầu hạ con riêng của chồng nhưng cuối cùng bị chúng ruồng bỏ. Trọng sinh, nữ chính thả cửa cho chúng hư hỏng rồi lấy tài sản rời đi, từ chối vinh quang "người mẹ vĩ đại".
2. **Cứu rỗi nam phụ thâm tình (男配救赎):**
   - **Lý do:** Mang lại yếu tố chữa lành (Heal) sau những drama mệt mỏi. Nữ chính bỏ qua nam chính tổng tài bạo chúa, quay sang yêu thương nam phụ dịu dàng, tàn tật hoặc có thân phận thấp kém nhưng yêu cô chân thành.
3. **Thanh mai trúc mã đả bại "Nhất kiến chung tình" (天降不敌竹马):**
   - **Lý do:** Trái với mô-típ cũ (tình yêu sét đánh thắng bạn thân), mô-típ mới trên Zhihu ủng hộ tình cảm thực tế, gắn bó lâu dài. Nữ chính từ chối trai đẹp hào nhoáng (nam chính) để chọn người bạn thanh mai trúc mã luôn âm thầm bảo vệ mình.
4. **Lột mặt nạ Phượng hoàng nam sính ngoại (撕下凤凰男伪装):**
   - **Lý do:** Vấn nạn rất thực tế. Gia đình bạn trai xuất thân nghèo khó nhưng gia trưởng, liên tục bòn rút tiền của nữ chính để nuôi nhà nội, tỏ vẻ bề trên. Nữ chính thu thập chứng cứ, khiến nhà trai mất cả chì lẫn chài ngay trong đám cưới.
5. **Đổi vận / Cướp hào quang (气运夺回):**
   - **Lý do:** Yếu tố hơi hướng tâm linh/huyền ảo. Nữ chính phát hiện vận may, nhan sắc hay thành tích của mình bị chị/em gái dùng bùa ngải hoặc hệ thống cướp đoạt. Quá trình lấy lại khí vận và phản phệ kẻ thù cực kỳ cuốn hút.

---

## 9. Điểm chưa xác minh
- **Biến động bảng xếp hạng 2026:** Do đặc thù thông tin thời gian thực, một số tác phẩm top 1 trên app *Zhihu* hay *Fanqie* thay đổi mỗi ngày/tuần. Danh sách 25 truyện nêu trên là những tác phẩm đã đạt độ "bạo hồng" và có sức sống kéo dài (kinh điển của mô-típ), không đại diện cho top trending chính xác của ngày hôm nay. (Cần truy cập trực tiếp app để xem Real-time rank).
- **Thuật toán quét Reused Content mới nhất của YouTube:** YouTube liên tục cập nhật AI nhận diện nội dung. Dù bạn viết lại kịch bản, nếu giọng đọc AI quá giống các kênh reup khác, vẫn có tỉ lệ (chưa xác minh được % cụ thể) bị bot YouTube đánh giá thấp. Ưu tiên thu âm bằng giọng người thật hoặc AI cao cấp ít người dùng.

## 10. Nguồn tham khảo
1. Phân tích mô-típ Zhihu và cách viết: [Cấu trúc tiểu thuyết Zhihu - Phi Thư](https://www.feishu.cn/) (Theo dữ liệu tìm kiếm web về "知乎短篇套路").
2. Đọc truyện miễn phí (Web bên thứ 3/Fanqie): Tham chiếu tìm kiếm web về các thư viện như `onehu.xyz`, `ifun.cool/zhihuyanxuan`, `番茄小说网页版`.
3. Phân biệt Bản quyền và Reused Content: Chính sách kiếm tiền của [Chương trình đối tác YouTube](https://support.google.com/youtube/answer/1311392). 
4. Tổng hợp list 20-30 truyện: Dữ liệu từ các bài Review / Bảng xếp hạng Zhihu Yanxuan năm 2024-2025 qua công cụ tìm kiếm web.
