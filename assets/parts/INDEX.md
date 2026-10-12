# Kho bộ phận nhân vật (assets/parts/)

Mục lục cho AI và người đọc, sinh tự động từ `parts.yaml` bởi `scripts/make_parts.py`. Ghép bằng `src/studio/avatar.py` theo bản thiết kế `assets/actors/<id>/avatar.yaml`.

## Cách ghép
- Lớp từ sau ra trước: **thân** (bộ đồ × vóc × tư thế) → **đầu nền** (mặt + tai + tóc) → **mắt** (đã kèm lông mày) → mũi → miệng → phụ kiện (râu, má hồng, nốt ruồi, sẹo) → kính.
- Chọn **kiểu** mắt và miệng (ví dụ `eyes2`, `mouth1`); biểu cảm tự ghép: bình thường, nói, cười nhếch, sốc, giận, buồn, chớp mắt.
- Kiểu mắt 6–8 chỉ có 4 biểu cảm (normal, angry, sad, wide); nhắm mắt mượn của kiểu 1.
- Đầu có đuôi `-special` đã vẽ sẵn nét mặt: không ghép mắt, miệng.
- Màu da đổi bằng `skin: "#rrggbb"` trong bản thiết kế.

## Đầu nền (mặt + tóc)

| id | mô tả |
|---|---|
| `head-round` | mặt tròn, trọc (nền để thêm tóc sau) |
| `head-oval` | mặt trái xoan, trọc |
| `head-square` | mặt vuông, trọc |
| `head-chubby` | mặt bầu bĩnh má phúng phính, trọc |
| `head-long` | mặt dài gầy, trọc |
| `head-oval2` | mặt trái xoan thon, trọc |
| `head-pointed` | mặt cằm nhọn xinh, trọc |
| `head-pointed2` | mặt cằm nhọn, trọc |
| `head-old-m-special` | ông già nhiều nếp nhăn, mắt nhắm vẽ sẵn (không ghép mắt được, chỉ dùng làm ông cụ ngủ/lim dim) |
| `head-old-f` | bà già nếp nhăn, tóc bạc hai bên |
| `head-mid-m` | nam trung niên tóc ngắn đen |
| `head-mid-f` | nữ trung niên tóc ngắn ôm mặt |
| `head-kid` | trẻ con đầu tròn nhỏ, trọc |
| `head-mid-m2` | nam tóc ngắn gọn gàng |
| `head-tough-special` | nam mặt ngầu đầu bằng, nét mặt vẽ sẵn (không ghép mắt được) |
| `head-messy` | nam tóc rối (nam chính trẻ) |
| `head-buzz` | nam đầu húi cua |
| `head-sidepart` | nam tóc rẽ ngôi (công tử, nhân viên) |
| `head-slick` | nam tóc vuốt ngược (sếp, đại gia) |
| `head-spiky` | nam tóc dựng đứng (nổi loạn) |
| `head-bowl` | tóc bát úp mái ngố (mọt sách) |
| `head-balding` | nam hói đỉnh (sếp bụng phệ, ông chú) |
| `head-grey-short` | tóc bạc ngắn (ông già) |
| `head-long-bangs` | nữ tóc dài thẳng mái bằng (hoa khôi) |
| `head-long-wavy` | nữ tóc dài xoăn sóng (nữ tổng tài, tiểu tam) |
| `head-ponytail` | nữ buộc đuôi ngựa mái bằng (nữ sinh) |
| `head-twin` | nữ tóc hai bím (em gái, bé) |
| `head-bob` | nữ tóc bob ngang cằm |
| `head-bun` | nữ búi tóc (thư ký, mẹ) |
| `head-perm` | nữ tóc xoăn uốn (bà thím, mẹ) |
| `head-grey-bun` | bà già tóc bạc búi |
| `head-yellow` | nam tóc nhuộm vàng (côn đồ) |
| `head-long-m` | nam tóc dài ngang vai (nghệ sĩ) |
| `head-cap` | đội mũ lưỡi trai |
| `head-brown-long` | nữ tóc nâu dài thẳng |
| `head-short-f` | tóc ngắn rối (nữ cá tính/nam) |
| `head-grey-temples` | nam tóc hoa râm hai bên (bố, sếp) |
| `head-braid` | nữ tóc tết một bím |
| `head-flat` | nam đầu bằng (bảo vệ, cảnh sát) |

## Mắt (kèm lông mày)

| id | mô tả |
|---|---|
| `eyes1-normal` | mắt chấm đen đơn giản, bình thường |
| `eyes1-closed` | mắt chấm đen đơn giản, nhắm |
| `eyes1-wide` | mắt chấm đen đơn giản, mở to sốc |
| `eyes1-angry` | mắt chấm đen đơn giản, giận |
| `eyes1-sad` | mắt chấm đen đơn giản, buồn |
| `eyes2-normal` | mắt nam sắc sảo kèm lông mày rậm, bình thường |
| `eyes2-closed` | mắt nam sắc sảo kèm lông mày rậm, nhắm |
| `eyes2-wide` | mắt nam sắc sảo kèm lông mày rậm, mở to sốc |
| `eyes2-angry` | mắt nam sắc sảo kèm lông mày rậm, giận |
| `eyes2-sad` | mắt nam sắc sảo kèm lông mày rậm, buồn |
| `eyes3-normal` | mắt nữ to có mi cong, bình thường |
| `eyes3-closed` | mắt nữ to có mi cong, nhắm |
| `eyes3-wide` | mắt nữ to có mi cong, mở to sốc |
| `eyes3-angry` | mắt nữ to có mi cong, giận |
| `eyes3-sad` | mắt nữ to có mi cong, buồn |
| `eyes4-normal` | mắt trung niên mệt mỏi, bọng mắt, bình thường |
| `eyes4-closed` | mắt trung niên mệt mỏi, bọng mắt, nhắm |
| `eyes4-wide` | mắt trung niên mệt mỏi, bọng mắt, mở to sốc |
| `eyes4-angry` | mắt trung niên mệt mỏi, bọng mắt, giận |
| `eyes4-sad` | mắt trung niên mệt mỏi, bọng mắt, buồn |
| `eyes5-normal` | mắt tròn to trẻ con, bình thường |
| `eyes5-closed` | mắt tròn to trẻ con, nhắm |
| `eyes5-wide` | mắt tròn to trẻ con, mở to sốc |
| `eyes5-angry` | mắt tròn to trẻ con, giận |
| `eyes5-sad` | mắt tròn to trẻ con, buồn |
| `eyes6-normal` | mảnh |
| `eyes6-angry` | mảnh |
| `eyes6-sad` | mảnh |
| `eyes6-wide` | mảnh |
| `eyes7-normal` | rậm |
| `eyes7-angry` | rậm |
| `eyes7-sad` | rậm |
| `eyes7-wide` | rậm |
| `eyes8-normal` | thanh tú |
| `eyes8-angry` | thanh tú |
| `eyes8-sad` | thanh tú |
| `eyes8-wide` | thanh tú |

## Miệng

| id | mô tả |
|---|---|
| `mouth1-neutral` | miệng nam đơn giản, small closed neutral mouth |
| `mouth1-talk` | miệng nam đơn giản, small open talking mouth |
| `mouth1-smile` | miệng nam đơn giản, closed confident smile |
| `mouth1-grin` | miệng nam đơn giản, open happy grin showing teeth |
| `mouth1-shock` | miệng nam đơn giản, round open shocked mouth |
| `mouth1-shout` | miệng nam đơn giản, wide open angry shouting mouth |
| `mouth1-frown` | miệng nam đơn giản, sad frown |
| `mouth1-smirk` | miệng nam đơn giản, one-sided smirk |
| `mouth2-neutral` | miệng nữ môi đỏ, small closed neutral mouth |
| `mouth2-talk` | miệng nữ môi đỏ, small open talking mouth |
| `mouth2-smile` | miệng nữ môi đỏ, closed confident smile |
| `mouth2-grin` | miệng nữ môi đỏ, open happy grin showing teeth |
| `mouth2-shock` | miệng nữ môi đỏ, round open shocked mouth |
| `mouth2-shout` | miệng nữ môi đỏ, wide open angry shouting mouth |
| `mouth2-frown` | miệng nữ môi đỏ, sad frown |
| `mouth2-smirk` | miệng nữ môi đỏ, one-sided smirk |
| `mouth3-neutral` | miệng người già, small closed neutral mouth |
| `mouth3-talk` | miệng người già, small open talking mouth |
| `mouth3-smile` | miệng người già, closed confident smile |
| `mouth3-grin` | miệng người già, open happy grin showing teeth |
| `mouth3-shock` | miệng người già, round open shocked mouth |
| `mouth3-shout` | miệng người già, wide open angry shouting mouth |
| `mouth3-frown` | miệng người già, sad frown |
| `mouth3-smirk` | miệng người già, one-sided smirk |
| `mouth4-neutral` | full glamorous red lipstick lips, small closed neutral mouth |
| `mouth4-talk` | full glamorous red lipstick lips, small open talking mouth |
| `mouth4-smile` | full glamorous red lipstick lips, closed confident smile |
| `mouth4-grin` | full glamorous red lipstick lips, open happy grin showing teeth |
| `mouth4-shock` | full glamorous red lipstick lips, round open shocked mouth |
| `mouth4-shout` | full glamorous red lipstick lips, wide open angry shouting mouth |
| `mouth4-frown` | full glamorous red lipstick lips, sad frown |
| `mouth4-smirk` | full glamorous red lipstick lips, one-sided smirk |

## Mũi, kính, chi tiết mặt

| id | mô tả |
|---|---|
| `nose1` | mũi chấm nhỏ (mặc định) |
| `nose2` | mũi nét cong |
| `nose3` | mũi tam giác hồng |
| `nose4` | mũi tròn to (hề, say rượu) |
| `glasses-round` | kính tròn (mọt sách, thầy giáo) |
| `glasses-square` | kính vuông (công sở, nghiêm) |
| `sunglasses` | kính đen (đại ca, vệ sĩ) |
| `beard-stubble` | râu lún phún quanh cằm |
| `mustache` | ria mép |
| `blush` | má hồng (ngại, say) |
| `mole` | nốt ruồi |
| `scar` | vết sẹo (côn đồ) |
| `nose5` | small curved hook line nose like the letter J, no nostrils |
| `nose6` | tiny button nose: two small nostril dots with a short curve above |
| `nose7` | small L-shaped line nose seen slightly from the side |
| `nose8` | cute tiny upturned nose with a soft rounded tip outline |
| `nose9` | elegant thin straight nose line with a small curve at the bottom |
| `nose10` | wide flat older person's nose outline |
| `nose11` | long pointed sharp nose outline (villain) |
| `nose12` | small nose shown only by a light pink nostril curve |
| `mole-lip` | small black beauty mole dot |
| `mole-tear` | tiny black tear mole dot |
| `freckles` | a band of small light brown freckle dots across both cheeks and nose |
| `eye-bags` | pair of tired under-eye bag curves |
| `bandaid` | small beige adhesive bandage |
| `beard-full` | full black beard around the jaw |
| `goatee` | small black goatee |
| `wrinkles` | three short forehead wrinkle lines |
| `earring-gold` | single gold hoop earring |
| `earring-gold-b` | single gold hoop earring |
| `earring-pearl` | single pearl drop earring |
| `earring-pearl-b` | single pearl drop earring |

## Thân theo bộ đồ (thư mục bodies/<bộ đồ>/<vóc>-<tư thế>.png)

| id | mô tả |
|---|---|
| `outfit:m-tshirt-jeans` | áo phông trắng, quần bò; vóc thin/normal/fat; tư thế relaxed/hips/phone/point |
| `outfit:m-school` | đồng phục học sinh nam; vóc thin/normal/fat; tư thế relaxed/hips/phone/point |
| `outfit:m-office` | sơ mi công sở; vóc thin/normal/fat; tư thế relaxed/hips/phone/point |
| `outfit:m-suit` | vest cà vạt (sếp, doanh nhân); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-relaxed, fat-point |
| `outfit:m-polo` | polo hàng hiệu (công tử); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: normal-phone, fat-phone |
| `outfit:m-tank` | áo ba lỗ, quần đùi (ở nhà); vóc thin/normal/fat; tư thế relaxed/hips/phone/point |
| `outfit:m-hoodie` | áo hoodie; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, fat-point |
| `outfit:m-leather` | áo da (côn đồ, đại ca); vóc thin/normal/fat; tư thế relaxed/hips/phone/point |
| `outfit:m-worker` | quần áo lao động; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-hips, fat-phone |
| `outfit:m-police` | cảnh sát; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips |
| `outfit:m-doctor` | bác sĩ; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-hips, fat-phone |
| `outfit:m-oldman` | áo Tôn Trung Sơn (ông già); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips, fat-point |
| `outfit:m-waiter` | phục vụ, quản gia; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: normal-hips, fat-hips, fat-point |
| `outfit:f-school` | đồng phục nữ sinh; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-phone, fat-point |
| `outfit:f-office` | công sở (thư ký, nữ tổng tài); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-phone, fat-hips |
| `outfit:f-evening` | đầm dạ hội đỏ; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-relaxed, normal-relaxed, fat-hips |
| `outfit:f-casual` | áo phông quần short; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: normal-phone, fat-phone |
| `outfit:f-dress` | váy hoa mùa hè; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: normal-hips, fat-hips, fat-point |
| `outfit:f-home` | đồ ở nhà có tạp dề (mẹ, bà thím); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips |
| `outfit:f-qipao` | sườn xám; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-phone, fat-phone, fat-point |
| `outfit:f-nurse` | y tá; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-hips, normal-hips, fat-hips |
| `outfit:f-oldwoman` | bà già; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, fat-point |
| `outfit:f-sport` | đồ thể thao; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips |
| `outfit:m-guard` | bảo vệ, vệ sĩ; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips, fat-point |
| `outfit:f-lady` | quý phu nhân, mẹ nhà giàu; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips, fat-point |
| `outfit:f-white-dress` | váy trắng đơn giản (trà xanh); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-phone, fat-phone |
| `outfit:f-wedding` | váy cưới; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, fat-point |
| `outfit:m-groom` | vest chú rể; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-hips, fat-hips |
| `outfit:f-poor` | quần áo cũ vá (nghèo); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips, fat-point |
| `outfit:f-patient` | áo bệnh nhân nữ; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-hips, fat-point |
| `outfit:f-pajama` | đồ ngủ nữ; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: fat-phone |
| `outfit:m-patient` | áo bệnh nhân nam; vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: normal-phone, fat-phone, fat-point |
| `outfit:m-poor` | quần áo cũ vá (nghèo); vóc thin/normal/fat; tư thế relaxed/hips/phone/point; THIẾU: thin-phone, normal-phone, fat-phone |
