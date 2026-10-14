# Hoạt hình nền ngẫu nhiên tự động cho kênh kể truyện audio

14/10/2026 (chưa duyệt) · Đề bài: [tmp/briefs/random-animation.md](../../tmp/briefs/random-animation.md)

## Kết luận và khuyến nghị (đọc phần này là đủ)

1. **Làm "đạo diễn ngẫu nhiên" sinh storyboard rồi dùng lại `stage.py`.** Không viết mới bằng PixiJS/canvas ở giai đoạn đầu. Lý do: `stage.py` đã có nền, ghép đầu+thân, hành động, zoom/lia, quần chúng, xuất 16:9 và 9:16, mã hoá `h264_videotoolbox`, chạy song song; số đo trong repo là 26 giây video dựng trong 6 giây (`docs/plans/studio-org.md`), tức 30 phút video khoảng 7–8 phút nếu tuyến tính (suy ra, chưa đo ở 30 phút). Viết mới tốn nhiều ngày mà thư viện hình vẫn là ảnh PNG đó.
2. **Việc cần thêm vào `actions.py` là từ vựng hành động hài/không lời** (hiện chỉ có 17 hành động nghiêng về drama: đánh, ngã, khóc...). Cần khoảng 15–20 hành động mới + ký hiệu manga + 6–8 hiệu ứng toàn khung.
3. **Rủi ro chính sách là rủi ro lớn nhất, không phải kỹ thuật.** Hình ngẫu nhiên lặp mẫu + giọng AI dễ bị xếp vào "inauthentic content" nếu video cảm giác "đổi truyện, giữ khuôn". Giảm rủi ro bằng: lời kể có biên tập/bình luận thật (đã là ràng buộc của dự án), hình biến thiên theo từng tập (hạt giống riêng, bộ nền/diễn viên riêng theo truyện), không đăng dồn hàng loạt.
4. **Đừng tin con số giữ chân trên mạng.** Không tìm được nghiên cứu độc lập nào; mọi số "89% hoàn thành", "cắt mỗi 8–12 giây giảm rớt từ 22% xuống 8%" đều là blog/nhà bán công cụ. Cách đúng: tự đo bằng YouTube Analytics (A/B hai nhịp cắt).

## 1. Thể loại nền đang chạy dưới giọng kể

| Thể loại | Cơ chế giữ mắt (theo nguồn) | Độ tin cậy |
|---|---|---|
| Reddit story + Minecraft parkour / Subway Surfers (chia đôi màn hình: chữ trên, game dưới) | Chuyển động liên tục chống lướt qua; giọng kể mang nội dung, nền không tranh chú ý. Subway Surfers hợp truyện nhịp nhanh, Minecraft hợp nội dung phức tạp | Chỉ có bài của nhà bán công cụ: [flowshorts](https://flowshorts.app/blog/gameplay-video-generator), [hooked.so](https://www.hooked.so/tools/subway-surfers-video-generator). Số liệu hoàn thành là quảng cáo, **chưa xác minh** |
| 小说推文 / 解压视频 Douyin | Nền là "解压" (cắt xà phòng, làm bánh, địa铁跑酷) + giọng AI đọc tiểu thuyết + phụ đề + nhạc; mở đầu 2–3 câu nêu tiền đề rồi liên tục treo悬念. Chỉ số cốt lõi của nền tảng: tỷ lệ xem hết, tương tác, theo dõi | Bài ngành/khởi nghiệp, có tính tiếp thị: [woshipm](https://www.woshipm.com/ai/6248372.html), [chinawriter](https://www.chinawriter.com.cn/n1/2024/0902/c404027-40311031.html). Không có số hoàn thành cụ thể; số tiền kiếm là lời tự khai, chưa xác minh |
| Hoạt hình cắt giấy kiểu South Park | Không phải nguồn giữ chân mà là bằng chứng kỹ thuật: nhân vật phẳng, bộ phận rời, rẻ mà vẫn có phong cách ([AWN](https://www.awn.com/animationworld/dig-using-computers-simulate-cut-out-animation-techniques-south-park-and-blues-clues), [FAQ chính thức](https://southpark.cc.com/news/712d55/faq-do-you-still-use-construction-paper-to-animate-the-show)) | Tốt cho kỹ thuật |
| Gacha Life, kênh truyện audio Việt | **Chưa xác minh**: lượt tìm không ra nguồn đáng tin về số liệu | - |

Rút ra: cái duy nhất mọi nguồn đồng ý là **nền phải luôn có chuyển động và không tranh với giọng**. Hoạt hình chibi tự tạo có lợi thế hơn gameplay vì không dính bản quyền game và khác biệt hoá được thương hiệu.

## 2. Ngữ pháp máy quay cho hoạt hình rẻ

Không có quy tắc chính thức. Tổng hợp từ blog biên tập video (chỉ là kinh nghiệm):
- YouTube không quy định khoảng cách pattern interrupt; khuyên cố định theo giây dễ gây "dựng quá tay"; chỉ nên đổi hình có chủ ý tại điểm chú ý tự nhiên. Một nguồn cho rằng dựng dày giảm giữ chân với khán giả từ 25 tuổi (không rõ dữ liệu). Nguồn: [AIR Media-Tech](https://air.io/en/youtube-hacks/advanced-retention-editing-cutting-patterns-that-keep-viewers-past-minute-8), [gofaceless](https://www.gofaceless.ai/blog/optimize-video-engagement-pattern-breaks), [creatoressentials](https://www.creatoressentials.com/glossary/pattern-interrupt/).
- Khoảng khuyến nghị lan truyền: đổi hình mỗi 8–15 giây ở phần mở, 30–45 giây nói chung. Các con số này là kinh nghiệm, **chưa có nghiên cứu**.

**Đề xuất áp dụng (giả thuyết cần đo, không phải sự thật):** vì hình chỉ là nền cho giọng kể, dùng nhịp hai tầng:
- Tầng chuyển động nhỏ liên tục (nhân vật nhún, chớp mắt, máy quay trôi chậm) luôn chạy.
- Tầng "cắt cảnh" mỗi 6–12 giây (đổi vi kịch bản, góc máy hoặc nền), cộng một "gợi sự chú ý" lớn hơn (đổi nền + hiệu ứng) mỗi 45–90 giây.
- 9:16: rút còn 3–6 giây/cảnh, mở đầu 3 giây phải có chuyển động mạnh.
- Cỡ cảnh: toàn (giới thiệu nền) → trung (hành động chính) → cận (phản ứng/biểu cảm). `stage.py` hiện có zoom [từ,tới] và pan; thêm cỡ cảnh = chọn zoom tới đầu/thân.
- Chuyển cảnh rẻ: cắt thẳng, whip pan (lia nhanh + mờ ngang), flash trắng, trượt ngang. `screen_fx` đã có flash/fade/shake.

## 3. Từ vựng hành động cho rối 2D không khung xương

Nguyên tắc nền: squash & stretch (giữ thể tích, nở ngang khi nén) và anticipation (ngả lùi/khuỵu trước khi nhảy) làm biến hình đơn giản trông "sống" ([tổng quan 12 nguyên tắc Disney](https://people.wku.edu/joon.sung/edu/anim/3d/animation/principles.html)).

**Đã có trong `src/studio/actions.py`:** idle, walk_in, walk_out, walk, run, hit, attack, fall, faint, nod, shake_head, laugh, cry, tremble, jump, turn_away, kneel. Hiệu ứng đầu: blood, scratch, bruise, tears, sweat, anger, dizzy, blush. Hiệu ứng toàn khung: flash, fade_in, fade_out, sepia, shake, black. Tham số biến hình sẵn: dx, dy, rot, head_rot, flip, expr, shake.

**Cần thêm (đều là hàm biến hình `dx/dy/rot/scale`, không cần khung xương):**
- Cơ thể: `bounce` (nhún liên tục), `squash_land` (đáp đất nén ngang), `spin` (xoay quanh chân), `spin_head`, `wobble` (lắc như bị chóng mặt), `slide` (trượt ngang giữ tư thế), `pop_in` (bật từ nhỏ ra to có nảy), `shrink_out`, `backflip` (xoay 360 độ khi nhảy), `bow`, `peek` (ló từ mép khung), `point_shake`, `hop_chase` (nhảy đuổi).
- Ký hiệu manga vẽ bằng PIL (không cần ảnh): chấm hỏi, chấm than, tim bay, sao, bong bóng "...", giọt mồ hôi to, đám mây giận, bóng đèn, "Zzz", nốt nhạc, ký hiệu tiền. Hiệu ứng toàn khung: confetti, vệt tốc độ (speed lines), khói bụi dưới chân, hạt mưa/lá rơi, vignette, zoom-punch.
- Bong bóng emoji: có thể dùng bộ biểu tượng có giấy phép cho phép (ví dụ Twemoji/Noto Emoji; **chưa kiểm tra điều khoản cụ thể**, cần kiểm trước khi dùng).

**Vi kịch bản 3–8 giây (40 mục, dùng được ngay với tài nguyên đang có).** Ký hiệu: [A]=1 diễn viên, [AB]=2, [N]=quần chúng. "Mới" = cần hành động/hiệu ứng thêm; còn lại ghép từ cái có sẵn. Đạo cụ lấy từ 24 món (điện thoại, tiền, hoa, dù, ly rượu, cặp, dao bếp...). Tránh dao/súng/ống thép/bia/thuốc lá trong vi kịch bản để giảm nguy cơ bị gắn nhãn nhạy cảm.

*Một người*
1. Đi ngang khung nhìn điện thoại, vấp, ngã nhẹ, đứng dậy ngượng (walk + fall + blush). [A]
2. Nhận tin nhắn, mặt neutral → shocked, bật giật mình, dấu chấm than (jump + ký hiệu). Đạo cụ: smartphone. [A]
3. Đếm tiền, mắt sáng, ký hiệu tiền bay quanh (cash + ký hiệu mới). [A]
4. Ngửi hoa, ngất vì thơm, tim bay (flowers + faint + tim). [A]
5. Che dù, mưa rơi, dù bị gió thổi bay (umbrella + hạt mưa + slide). [A]
6. Uống trà, nóng quá, phun, sao xoay đầu (tea-cup + dizzy). [A]
7. Chạy muộn giờ, vệt tốc độ, đâm vào mép khung rồi dội lại (run + speed lines + squash). [A]
8. Nhảy múa ăn mừng, confetti (jump/bounce + spin + confetti). [A]
9. Khóc lóc to, nước mắt phun hai bên (cry + tears). [A]
10. Nghĩ ra ý tưởng, bóng đèn trên đầu, nhảy lên (nod + ký hiệu bóng đèn). [A]
11. Ngủ gật ở bàn, Zzz, đầu gật gù, giật tỉnh (lắc head_rot + Zzz). Hợp văn phòng, lớp học. [A]
12. Gõ laptop điên cuồng, mồ hôi, tức giận gạt máy (laptop + sweat + anger). [A]
13. Đi theo dấu chấm hỏi, tìm đồ (walk + head_rot + chấm hỏi). [A]
14. Lén ló đầu từ mép khung rồi rụt lại (peek). [A]
15. Chống nạnh đắc ý, smirk, nâng ly (hips + smirk + wine-glass). [A]
16. Đứng chờ xe buýt, xe chạy qua, gió thổi tóc/áo, rùng mình (nền bus-stop-2002, tremble). [A]

*Hai người*
17. Đuổi nhau vòng khung (run đối pha + vệt tốc độ). [AB]
18. Một người đưa quà, người kia bất ngờ rồi ôm (gift-box + jump + tim). [AB]
19. Cãi nhau: hai bên anger, rung nhẹ, bong bóng "!!!" (point + anger). [AB]
20. Đưa phong bì/hợp đồng, người nhận xem, gật hoặc lắc đầu (envelope/contract + nod/shake_head). [AB]
21. Va nhau ở góc, văng ngược ra, sao xoay (hit + dizzy). [AB]
22. Một người kể chuyện, người kia ngáp, gục (idle + laugh/cry đối lập). [AB]
23. Chụp ảnh selfie chung, flash trắng (smartphone + flash). [AB]
24. Đánh gối giả bằng túi/cặp, không máu, nảy nhẹ (attack + backpack, hit nhẹ, bỏ hiệu ứng máu). [AB]
25. Trốn tìm: một người ló đầu sau mép phải, người kia quay lưng đếm (turn_away + peek). [AB]
26. Khiêu vũ đối xứng (spin + bounce, flip đối). [AB]
27. Nhường đường lúng túng, bước qua trái phải đồng pha (walk đối ngược + blush). [AB]
28. Người này cười, người kia lây cười, rồi cả hai lăn ra (laugh + fall nhẹ). [AB]

*Quần chúng và cảnh*
29. Quần chúng đồng loạt quay đầu về một phía, chấm than (N + head_rot). [N]
30. Đám đông vỗ tay/nhảy theo nhịp (N + bounce lệch pha). [N]
31. Nhân vật chính đi bộ giữa phố, quần chúng đi ngược chiều (walk + N). [A+N]
32. Hoàng hôn/ban đêm đổi nền sky-day → sky-night, vi kịch bản nhẹ để nghỉ mắt. Chuyển cảnh chậm, không nhân vật. [cảnh]
33. Xe chạy qua cửa kính car-interior/highway, cảnh trôi chậm (pan + nền). [cảnh]
34. Mưa rơi lên cửa sổ rented-room, nhân vật ngồi nhìn buồn (sad + hạt mưa). [A]
35. Cảnh đông nghịt ở cafe/ktv-bar, mỗi người một nhún nhịp khác nhau. [N]
36. Hành lang bệnh viện: đẩy xe tưởng tượng bằng suitcase, vấp, đồ rơi (suitcase + fall). [A]
37. Cổng trường: vẫy tay chào, chạy tới ôm (walk_in + jump). [AB]
38. Nhà bếp: nấu ăn bốc khói, cháy, hoảng (khói + tremble). Dùng hiệu ứng khói. [A]
39. Mái nhà nhìn xa, gió thổi, máy quay zoom out từ cận ra toàn (rooftop). [A]
40. Cảnh tĩnh "thở": một nhân vật idle + máy quay trôi rất chậm 6–8 giây, dùng để giảm mệt mắt giữa hai cảnh động. [A]

## 4. Thư viện mã nguồn mở (kiểm giấy phép trên GitHub API ngày 14/10/2026)

| Thư viện | Giấy phép | Dựng mp4 hàng loạt trên Mac |
|---|---|---|
| [PixiJS](https://github.com/pixijs/pixijs) | MIT | Chạy trong trình duyệt/Playwright, chụp từng khung rồi ffmpeg. Chậm hơn Python vì chụp màn hình |
| [Motion Canvas](https://github.com/motion-canvas/motion-canvas) | MIT | Có xuất khung hình; hợp hoạt hình kiểu giải thích, ít hợp rối ảnh |
| [matter.js](https://github.com/liabru/matter-js) | MIT | Vật lý 2D (rơi, va chạm); dùng khi muốn đồ vật rơi tự nhiên. Không cần cho phiên bản đầu |
| [Rive runtime](https://github.com/rive-app/rive-wasm) | MIT (runtime). Trình soạn Rive là sản phẩm riêng, điều khoản **chưa xác minh** | Cần dựng file .riv bằng công cụ của Rive, thêm việc |
| [lottie-web](https://github.com/airbnb/lottie-web) | MIT | Cần file Lottie, không hợp ảnh PNG ghép |
| [DragonBonesJS](https://github.com/dragonbones/DragonBonesJS) | MIT | Cần dựng xương, ngược với hướng "rối không khung xương" |
| [Manim](https://github.com/ManimCommunity/manim) | MIT | Hợp toán/đồ hoạ vector, không hợp chibi ảnh |
| [skia-python](https://github.com/kyamagu/skia-python) | BSD-3-Clause | Vẽ nhanh hơn PIL, nhưng chưa cần |
| Remotion | **Không phải mã mở thuần**: miễn phí cho cá nhân, công ty tối đa 3 người, phi lợi nhuận hoặc dùng thử; từ 4 người phải mua giấy phép công ty. Gói trả phí: $25/tháng mỗi chỗ cho creator, $0.01/lần render (tối thiểu $100/tháng), Enterprise từ $500/tháng | Nguồn: [remotion.dev/pricing](https://remotion.dev/pricing), [điều khoản](https://cloudrun.remotion.dev/docs/license). Giá tra ngày 14/10/2026 qua tìm kiếm, nên đọc LICENSE.md chính thức trước khi dùng |

Kết luận: với tài nguyên PNG ghép sẵn, **Pillow + ffmpeg hiện tại là hợp nhất**. Thư viện web chỉ đáng cân nhắc nếu sau này cần hạt/vật lý phức tạp.

## 5. Chính sách YouTube

- Tháng 7/2025 YouTube đổi tên "repetitious content" thành **"inauthentic content"** (hiệu lực 15/7/2025), nói đây là làm rõ chính sách cũ chứ không cấm nội dung AI; nội dung AI hay tái sử dụng vẫn được nếu có giá trị gốc như bình luận, biên tập, lời kể ([ppc.land](https://ppc.land/youtube-clarifies-inauthentic-content-policy-changes/), [plagiarismtoday](https://www.plagiarismtoday.com/2025/07/08/youtube-targets-inauthentic-content/)).
- Trang chính thức [Chính sách kiếm tiền của kênh](https://support.google.com/youtube/answer/1311392?hl=en) nêu vi phạm như: slideshow ảnh, cốt truyện theo khuôn, chữ cuộn với rất ít tường thuật/bình luận; kênh có các video "có thể thay thế cho nhau" không được kiếm tiền; nội dung AI dựng từ khuôn chung chung tạo cảm giác sản xuất hàng loạt; chỉ đọc lại văn bản người khác viết cũng không đủ điều kiện. (Tóm lược từ kết quả tìm kiếm; cần đọc nguyên văn trước khi chốt.)
- Quy tắc áp dụng cho **cả kênh**, không chỉ video vi phạm.

**Đánh giá cho hướng này:** giọng kể AI trên nền hình ngẫu nhiên không liên quan **có rủi ro thật** ở khía cạnh "khuôn lặp, hình không phục vụ nội dung". Điểm cứu là kịch bản được viết lại + có lời bình người kể (ràng buộc sẵn của dự án), hình tự tạo.

**Giảm rủi ro:**
1. Mỗi truyện một "bộ nhận diện" riêng: bộ diễn viên, bộ nền, bảng màu, nhạc khác nhau (đạo diễn nhận seed + `cast.yaml` của truyện).
2. Mật độ biến thiên lớn: ít nhất 100+ tổ hợp vi kịch bản × nền × diễn viên, tránh một khuôn dễ nhận ra.
3. Hình có liên hệ nhẹ với lời kể: dùng từ khoá (đã có trong `direct.py`/`actions.yaml`) để ưu tiên nền và biểu cảm cho đúng tâm trạng chương (ví dụ chương buồn → sad). Vẫn ngẫu nhiên nhưng không ngược nghĩa.
4. Không đăng dày; giữ chất lượng giọng và lời bình ổn định; theo dõi thông báo kiếm tiền trong YouTube Studio.
5. Khai báo nội dung AI/tổng hợp theo mẫu của YouTube khi tính chất phù hợp (nguồn chưa kiểm cụ thể, cần đọc điều khoản).
6. Với truyện có bản quyền: chỉ dùng văn đã viết lại (đã là luật của dự án), tránh bản dịch/đọc nguyên văn.

## 6. Đề xuất kiến trúc "đạo diễn ngẫu nhiên"

### So sánh hai hướng

| Tiêu chí | Sinh storyboard rồi dùng `stage.py` | Viết mới HTML canvas / PixiJS |
|---|---|---|
| Công sức | Thấp: viết `director_random.py` (~300–400 dòng) + 15–20 hành động + ký hiệu manga (~300 dòng) | Cao: dựng lại ghép nhân vật, nhép miệng theo audio, máy quay, quần chúng, xuất 2 tỉ lệ, kiểm thử |
| Tốc độ 30 phút | `stage.py` đã đo 4× thời gian thực (≈7–8 phút/30 phút, suy ra), có nhân bản khung quay đôi (draw_fps 12) và bỏ qua khung trùng | Phải chụp từng khung qua trình duyệt, thường chậm hơn; **chưa đo** |
| Rủi ro | Giới hạn của PIL (không GPU) nhưng đủ cho ảnh phẳng | Phải viết lại mọi thứ, dễ lệch phong cách |
| Khi nào đổi hướng | Khi cần hàng trăm hạt/vật lý nặng hoặc xem trước tương tác | - |

Khuyến nghị: **hướng 1**. Cân nhắc PixiJS chỉ nếu đo thực tế thấy hiệu ứng hạt làm PIL quá chậm.

### Luồng

```
seed + story.yaml (kênh, cast, bảng nền)  →  Đạo diễn ngẫu nhiên  →  storyboard/NNN.yaml  →  stage.py  →  mp4
```

Đạo diễn là vòng lặp trên trục thời gian (độ dài = audio):
1. **Chọn "chương" nhịp:** chia audio thành các khối 45–90 giây ("hồi"), mỗi hồi chọn 1 nền chủ đạo + 1–2 diễn viên (trọng số theo tâm trạng nếu có nhãn).
2. **Trong hồi, lặp các cảnh 6–12 giây:** bốc 1 vi kịch bản (mục 3) từ danh sách có điều kiện (đủ số diễn viên, nền hợp: ví dụ "ngủ gật" chỉ ở văn phòng/lớp học), bốc cỡ cảnh + chuyển động máy.
3. **Nhịp:** theo mẫu hai tầng (mục 2). Cuối hồi luôn có một cảnh "thở" (mục 40) hoặc đổi nền.
4. **Xuất storyboard YAML** theo hợp đồng `src/contracts.py`, `stage.py` dựng.

### Tránh lặp trong 30 phút
- Hàng đợi xáo bài (shuffle bag): bốc không hoàn lại cho tới khi hết rồi mới xáo lại.
- Bộ nhớ gần nhất: cấm cùng vi kịch bản trong 10 cảnh gần đây, cùng nền trong 2 hồi, cùng cặp diễn viên trong 4 cảnh, cùng cỡ cảnh/chuyển cảnh 3 lần liên tiếp.
- Trọng số theo hiếm: món đạo cụ, nền, hiệu ứng hiếm được tăng điểm nếu chưa dùng.
- Mỗi cảnh sinh ngẫu nhiên tham số liên tục (hướng nhìn, biên độ, tốc độ ±20%, vị trí) nên cùng vi kịch bản trông khác.
- Ghi nhật ký (seed + id mỗi cảnh) để tái lập và để đo.

### Giữ hình không lấn giọng
- Hạn chế chuyển động nhanh khi giọng kể ở câu căng thẳng; độ mạnh hành động theo biên độ audio (đã có `loudness`): nhép miệng và nhún nhẹ khi nói, hành động lớn rơi vào chỗ ngắt nghỉ.
- Giới hạn độ tương phản và màu rực; hiệu ứng flash/shake ≤ 1 lần mỗi 60 giây; không dùng nhấp nháy (an toàn cho người nhạy sáng).
- Âm thanh hiệu ứng nhỏ hơn giọng ít nhất 15–20 dB (giả thuyết, cần nghe thử), hoặc không dùng.
- Phụ đề giữ cố định vị trí để mắt không phải đi tìm.

### Lộ trình tối thiểu (đề xuất)
1. Thêm ~12 hành động và ~8 ký hiệu vào `actions.py`, 1 đoạn thử 60 giây.
2. Viết `director_random` với 15 vi kịch bản đầu, render 5 phút, xem bằng mắt.
3. Mở rộng tới 40 vi kịch bản, đo thời gian dựng 30 phút.
4. Đăng thử 2 video với nhịp cắt khác nhau, so sánh biểu đồ giữ chân.

## Hạn chế của báo cáo
- Không có nghiên cứu độc lập về giữ chân theo nhịp cắt; mọi số liệu là kinh nghiệm/quảng cáo.
- Không tìm được nguồn tin cậy cho Gacha Life và kênh truyện audio Việt.
- Giá/điều khoản Remotion lấy qua kết quả tìm kiếm; trang chính sách YouTube chỉ thấy đoạn trích.
- Thời gian dựng 30 phút là suy ra từ số đo 26 giây, chưa chạy thật.
