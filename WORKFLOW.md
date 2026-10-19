# Workflow: Truyện → Video (video_product trên cloud)

## Hệ thống đã sẵn sàng
- Repo: `~/workspace/video_product/` (venv riêng `.venv/`, đã fix chạy Linux)
- Model TTS: `~/workspace/models/vieneu-onnx/` + `~/workspace/models/moss-codec/` (tải 1 lần, dùng lại)
- Thư viện: 20+ diễn viên rối (`assets/actors/`), 30+ bối cảnh (`assets/scenes/`), đạo cụ, font BeVietnamPro

## Quy tắc dàn dựng storyboard (pipeline — rút từ lỗi thực tế 2026-10-12)

### 1. Vùng an toàn 9:16
- Portrait squeeze: `x_render = 0.5 + (x - 0.5) × 0.3` — x=0.88 chỉ ra 0.61 chứ không ra mép như tưởng
- NHƯNG nhân vật pose `point` + cầm prop rộng gấp 1.66x thân thường → validator tự cảnh báo khi `tâm ± nửa_rộng` vượt [0.15, 0.85]
- Quy tắc ngón tay cái: đừng đặt actor quá x<0.2 hoặc x>0.8 nếu họ giơ tay/cầm đồ

### 2. walk_in/walk_out tự chọn mép (từ 2026-10-12)
- TỰ ĐỘNG vào/ra từ mép GẦN NHẤT theo x đích + quay mặt đúng hướng di chuyển
- Không cần thêm `flip` thủ công nữa (trước đây walk_in cứng vào từ trái — bug đã fix)

### 3. Validator storyboard
- Mỗi lần render tự chạy `validate_storyboard()`: báo actor/prop/background không tồn tại, actor có nguy cơ ra khỏi khung
- Prop trong kịch bản PHẢI có file trong `assets/props/` hoặc `props.yaml` — không thì validator báo ngay

### 4. Khớp cổ tự động
- `stage.py` tự feather 18% mép dưới đầu + cầu nối cổ màu da lấy từ giữa mặt
- Không cần chỉnh tay từng nhân vật nữa

### 5. Vật dụng quan trọng trong kịch bản
- Nếu kịch bản nhắc vật chứng (bình vỡ, giấy tờ...), phải có asset hoặc background-variant riêng cho shot đó
- Kỹ thuật: vẽ prop bằng PIL → ghép lên bản sao background → dùng `background:` riêng cho shot

### 6. Thư viện mắt có hồn (từ 2026-10-12)
- eyes1-8: mắt đơn giản cũ (chấm tròn, nét cơ bản)
- **eyes9** (hiền): mắt to tròn có highlight long lanh, lông mày cong mềm
- **eyes10** (khí chất): mắt xếch sắc sảo, highlight sao, lông mày đậm quyết đoán
- **eyes11** (trà xanh): mắt rưng rưng ngây thơ, có nét mưu mô ẩn
- **eyes12** (tinh nghịch): mắt sáng long lanh, năng động vui vẻ
- **eyes13** (lạnh lùng): mắt hờ hững xa cách, ít highlight
- Quy tắc: nhân vật cần "có hồn" → dùng eyes9-13 thay vì eyes1-8
- Nhân vật mẫu: `nu-hien` (eyes9), `nu-khichat` (eyes10), `nu-tra-xanh` (eyes11), `nu-tinh-nghich` (eyes12), `nu-lanh-lung` (eyes13)

### 7. Giới hạn cử động tay chân (ghi nhận 2026-10-12)
- Body là PNG phẳng, tay chân dính liền → không tách rig tự động đáng tin cậy
- Pose "chống hông" khiến tay dính sát thân, mask hình chữ nhật bao cả váy
- Đã tăng cường tối đa: walk nhún sâu hơn (-0.045), nghiêng rõ hơn (-3.5°), đầu lắc (2.0°)
- Giải pháp dài hạn: vẽ lại body thành part riêng (tay/chân/thân) hoặc gen thêm pose trung gian

### 8. Render song song (parallel_render.py, 2026-10-12)
- `scripts/parallel_render.py <job> --jobs 2`: chia shots tại ranh giới, render N đoạn song song, nối bằng ffmpeg
- Voice gen 1 lần rồi cắt theo đoạn (tránh lệch); mọi thời gian tuyệt đối (shots/subs/overlay) được rebase
- KẾT QUẢ ĐO: trên VM 2 CPU, --jobs 2 KHÔNG nhanh hơn tuần tự (44.9s vs 45.2s cho video 20s)
  → nghẽn ở PIL compositing từng frame, 2 tiến trình tranh nhau 2 core
- Chỉ có lợi khi VM có 4+ CPU. Giữ script cho tương lai nâng cấp.

## Cải tiến đã áp dụng (so với bản gốc)
1. Encoder `libx264` thay `h264_videotoolbox` (chạy Linux)
2. Nhân vật **thở** (nhún + đung đưa nhẹ) thay vì đứng đóng băng
3. **Cầu nối cổ** bằng màu da — fix đầu/thân không khớp
4. Hiệu ứng **mưa** (`screen: [rain]`)
5. Overlay hỗ trợ `top_to` (tiêu đề ẩn đúng lúc)
6. **Secondary motion cho tóc**: tóc dài đung đưa liên tục (lệch pha mỗi nhân vật) + trễ ngược khi đầu xoay (tham số `hair_sway` trong `Puppet.figure()`)
7. **Spring physics** cho gật/lắc đầu: dao động tắt dần, dừng tự nhiên thay vì khựng đột ngột (hàm `_spring()` trong `actions.py`)
8. **Bước đi cải thiện**: nhún theo nhịp bước + nghiêng người + đầu lắc nhẹ đồng bộ
9. **Khóc cải thiện**: rung vai + nức nở (người nhún theo nhịp nấc) + đầu cúi theo
10. **draw_fps=24** cho bản final (mượt gấp đôi so với mặc định 12)

## Cách giao việc (bạn → Muse)
1. Bạn đưa truyện/kịch bản: file `.md` hoặc `.txt` vào Drive folder
   `video/kênh khoai tây/<tên truyện>/` (hoặc gửi trực tiếp trong chat)
2. Format kịch bản chuẩn: `~/workspace/video/format-kich-ban-input.md`
   (Muse đã viết sẵn để bạn gửi cho bên viết kịch bản)
3. Muse sẽ: viết `voice.txt` + `canh.yaml` → chạy render → up video final lên Drive

## Lệnh render (1 lệnh duy nhất)
```bash
cd ~/workspace/video_product
.venv/bin/python scripts/cloud_render.py <job_dir> [--voice "Ngọc Huyền"] [--speed 1.34] [--size 1080x1920]
```
- `<job_dir>/voice.txt`: lời dẫn, mỗi dòng 1 câu
- `<job_dir>/canh.yaml`: storyboard (xem `~/workspace/video/hook10s/canh.yaml` mẫu)
- Output: `<job_dir>/final.mp4` (đã có voice + phụ đề + chữ overlay)

## Storyboard YAML (tóm tắt)
```yaml
audio: voice.mp3            # tự gen từ voice.txt
background: <đường dẫn nền> # hoặc theo từng shot
overlay:                    # chữ kiểu TikTok
  top: "TIÊU ĐỀ"
  top_to: 5.3               # ẩn sau giây 5.3
  cta: "KÊU GỌI CUỐI"
  cta_from: 8.2
cast:
  ten_nv: {actor: <id>}     # id trong assets/actors/
shots:
  - start: 0.0
    end: 1.4
    cam: {zoom: [1.0, 1.15]}
    screen: [rain]           # hiệu ứng: rain/shake/flash/fade_in/fade_out/sepia/black
    actors:
      - {who: ten_nv, x: 0.3, expr: neutral, pose: relaxed,
         action: cry, fx: [tears], height: 0.42, flip: true, prop: contract}
```
- `expr`: neutral/smirk/shocked/angry/sad (+ _talk)
- `pose`: relaxed/hips/phone/point
- `action`: idle/walk_in/walk_out/walk/run/cry/laugh/tremble/nod/shake_head/turn_away/kneel...
- `fx`: tears/sweat/anger/bruise/blush/dizzy/scratch

## Lưu ý
- Video dài = độ dài audio. Nếu storyboard dài hơn voice, script tự pad silence.
- Khung 9:16: tọa độ x bị nén về giữa (0.35–0.65), dùng x 0.3/0.7 để tách trái-phải.
- Render 10s 1080x1920 mất ~45s trên cloud (2 CPU).

## Quy tắc nhân vật (cập nhật 2026-10-12)
- `head_size: 0.85` (mặc định mới): đầu nhỏ hơn, cân đối với thân. Không dùng 1.0.
- `overlap: 0.12`: đầu đặt thấp, giấu đường cắt tóc sau vai.
- Feather theo nội dung (tự động trong stage.py): tóc fade 30%, da fade 10%, blur nhẹ viền cằm.
- Outfit váy cưới: `f-wedding-dress` (có relaxed/hips/point). Dùng cho nhân vật cô dâu.

## Thư viện khuôn mặt (2026-10-12)
5 khuôn mới với hình dáng khác biệt rõ:
- `head-xoan2`: trái xoan, cằm nhọn
- `head-vuong2`: vuông chữ điền, quai hàm góc cạnh
- `head-le2`: quả lê, trán hẹp cằm rộng
- `head-tao2`: quả táo, tròn má phính
- `head-bi2`: quả bí, cực tròn
Dùng khi tạo nhân vật mới cần đa dạng khuôn mặt.

## Quy trình tạo nhân vật 4 lớp (user chốt 2026-10-13)

Áp dụng cho nhân vật TÓC DÀI. Tóc ngắn giữ nguyên (tóc gắn với mặt).

**Thứ tự lớp (từ sau ra trước):**
1. **Tóc sau** — full wig, không mặt, tóc xoã dài 2 bên
2. **Thân** — từ cổ trở xuống (váy/áo), đè lên tóc, cổ che ~1/5 tóc
3. **Mặt** — tròn/xoan/lê tùy, có mắt mũi tai, KHÔNG tóc
4. **Mái trước** — khối đen đặc, cùng màu/style tóc sau, đè lên trán

**Quy tắc:**
- Mái là 1 khối đặc, KHÔNG sợi lơ thơ
- Tóc sau nằm SAU thân (không đè lên người)
- Mặt đè lên cả tóc và thân
- Mái đè lên trán (trước mặt)

**Script:** `scripts/character_factory.py --name <ten> --spec "<mô tả>" --hair long|short`

**File output:** `assets/actors/<name>/parts/` chứa 4 lớp + `card.yaml`

## Flow nhân vật theo mẫu tham khảo (2026-10-13)

Chi tiết: `reference/README.md`

Tóm tắt: Thu thập ảnh mẫu → Phân tích (khuôn mặt/mắt/tóc/tỉ lệ/trang phục) → Gen từng bộ phận kèm ảnh mẫu → Lắp 4 lớp → Đối chiếu với mẫu gốc.

Quy tắc: luôn có reference trước khi gen; lỗi bộ phận nào gen lại bộ phận đó.

## Pipeline render chia shot (2026-10-13, ý tưởng của user)

Render nguyên khối 62s chết ở giây 50 là mất cả 8 phút. Chia mỗi shot trong
`canh.yaml` thành 1 task render độc lập, log vào `tasks.json`, cron 5 phút
check 1 lần: task nào failed/stuck thì chạy lại chỉ task đó, xong hết mới
ffmpeg concat thành `final.mp4`.

**Script:**
- `scripts/shotctl.py <job> init` — đọc `canh.yaml`, tạo `tasks.json`
  (shot → [f0,f1) frame tuyệt đối, pending/running/done/failed/dead)
- `scripts/shotctl.py <job> check` — watchdog: stuck (>15 phút không
  heartbeat) hoặc failed → chạy lại (tối đa 3 lần → dead, cần người xem);
  hết pending → render shot tiếp; xong hết → concat `final.mp4`
- `scripts/render_shot.py <job> --shot N` — render shot N (khung hình là hàm
  thuần túy của frame tuyệt đối → đúng pixel như render nguyên khối, KHÔNG
  cần carry state nhân vật giữa các shot) + audio slice cắt chính xác
  (`-ss` sau `-i`, bắt đầu đúng `f0/draw_fps`) → `shots/shot_NN.mp4`
- `scripts/shotctl.py <job> status` — xem bảng trạng thái

**Cron (khi có job Tập 2):**
`*/5 * * * *` → `shotctl.py <job> check` (có lock chống chạy chồng)

**Đã test 2026-10-13:** job 2 shot × 4s → render ok (4.000s/shot, 1080x1920);
kill -9 giữa chừng → check phát hiện stuck → chạy lại → done; concat ra
final.mp4 8.02s. Áp dụng từ Tập 2 (Tập 1 đã render xong nguyên khối).

## Pipeline thumbnail + intro 3s (2026-10-14, user duyệt mẫu)

- `scripts/make_thumbnail.py`: gen thumbnail theo mẫu đã duyệt — ảnh nền AI từ
  tóm tắt truyện + badge thể loại trên cùng (VD "HÔN NHÂN GIA ĐÌNH",
  "ĐÔ THỊ, TRÍ TUỆ, VẢ MẶT" — badge theo thể loại từng truyện) + tên truyện
  in đậm giữa + "TẬP N" dưới. 1 ảnh đại diện/truyện, tái dùng mọi tập.
- `scripts/add_intro.py --video final.mp4 --thumb thumb.png --srt final.srt
  --out final-intro.mp4`: ghép intro 3s (ảnh thumbnail, audio im lặng) vào đầu
  video bằng concat `-c copy` (chỉ encode 3s intro, ~5 giây thay vì re-encode
  5-8 phút); SRT shift +3s để khớp lip-sync.
- QUY TẮC: `upload.md` luôn trỏ file đăng cuối cùng (bản `-intro.mp4`).
  `add_intro.py` tự cập nhật upload.md (đổi file/phụ đề, +3s vào thời lượng
  và mốc phần) — idempotent, chạy lại không shift 2 lần.

### Lỗi đã gặp 2026-10-14 (ghi để không tái phạm)
- LỖI: `upload.md` do `merge()` trong `src/produce.py` viết TRƯỚC khi chạy
  `add_intro.py` → vẫn trỏ bản mp4 chưa intro (tập 1), thậm chí trỏ file không
  tồn tại (tập 2/3 chỉ còn bản `-intro.mp4`). Nếu đăng theo upload.md sẽ đăng
  nhầm bản không intro.
- NGUYÊN NHÂN: add_intro là bước thủ công chạy sau merge, không cập nhật
  upload.md.
- KHẮC PHỤC (tại gốc): thêm `update_upload_md()` vào `add_intro.py` — tự sửa
  upload.md mỗi lần ghép intro; đã sửa 3 upload.md của truyện "Bạn Thân Cướp
  Bản Quyền Của Tôi" (2026-10-14) trỏ đúng bản `-intro`.

### Lỗi đã gặp 2026-10-14 tối (tiếng ồn + intro dài)
- LỖI 1: User báo video gen từ trưa có "tiếng ồn khó chịu", nghi từ khâu xử lý audio (không phải voice TTS).
- NGUYÊN NHÂN: Audio bị encode lossy 2 lần: `tts.vieneu()` xuất MP3 160k → `reel.render()` transcode MP3→AAC 192k. Mỗi lần encode lossy chồng thêm artifact.
- KHẮC PHỤC (tại gốc): `src/common/tts.py` đổi xuất WAV lossless (pcm_s16le) thay vì MP3; `src/produce.py` đổi path `audio/NNN.mp3` → `audio/NNN.wav`. Giờ chỉ encode lossy 1 lần (WAV→AAC ở khâu video).
- LỖI 2: Intro thumbnail 3s im lặng mới có voice → user muốn voice ngay từ 0s, thumbnail chỉ 1s.
- KHẮC PHỤC (tại gốc): viết lại `scripts/add_intro.py` — thumbnail 1s (mặc định), audio lấy trực tiếp từ video gốc (không delay, không chen im lặng), SRT giữ nguyên không shift. Cần re-encode video (concat video + map audio riêng), dùng preset veryfast.

### Lỗi 2026-10-14 tối (tiếng ồn loa PHẢI) — ROOT CAUSE
- LỖI: Video gen từ trưa (có intro) bị tiếng rè ở loa PHẢI, loa trái sạch. 3 video sáng (không intro) không bị.
- NGUYÊN NHÂN (tại gốc): `add_intro.py` v1 tạo 3s intro với audio im lặng STEREO (`anullsrc=cl=stereo`), rồi concat `-c copy` với audio chính MONO → channel layout bị vỡ, player đọc lệch kênh (loa phải thành tiếng rè).
- KHẮC PHỤC (tại gốc): viết lại `add_intro.py` — intro chỉ có hình (`-an`, không audio), audio lấy trực tiếp từ video gốc (`-map 1:a -c:a copy`) giữ nguyên mono; thumbnail 1s + voice từ giây 0. Verify: output ffprobe channels=1.
- QUY TẮC: không bao giờ concat audio khác channel layout bằng `-c copy`.

## Quy tắc nhân vật hỏng (2026-10-18)
- Mọi character mới tạo bằng `new_actor.py` PHẢI chạy `python -m src.studio.validate_actor <id>` và ĐẠT trước khi đưa vào kho.
- Nếu CHƯA ĐẠT: hoặc sửa asset cho đạt, hoặc thêm id vào `SKIP_ACTORS` trong `src/studio/reel.py` ngay lập tức.
- `SKIP_ACTORS` hiện tại: `{"uyen-thanh"}` (head là mảnh vụn, body váy cưới thiếu thân trên — lỗi cắt từ 13/10/2026).
- Chi tiết lỗi: xem `docs/VAN-DE-NHAN-VAT-PUPPET.md` Lỗi 9.

## Quy tắc asset body mới (2026-10-19, từ Lỗi 10)
- Body asset (thân không đầu) KHÔNG được có chi tiết nào vượt quá mép trên vùng cổ: voan, tóc, khăn, phụ kiện chĩa lên trên. Lý do: `neck_top()` trong `cutout.py` tìm mép trên đầu tiên ở dải giữa thân để đặt đầu — chi tiết thừa sẽ (1) làm sai anchor, (2) lòi ra phía trên/sau đầu khi render (đầu nhỏ hơn chi tiết thừa).
- Cách kiểm tra nhanh sau khi tạo body mới: `python -m src.studio.validate_actor <id>` + composite thử `Puppet.figure('relaxed','neutral')` xem có vật lạ trên đầu không.
- Chi tiết: xem `docs/VAN-DE-NHAN-VAT-PUPPET.md` Lỗi 10 (voan cô dâu nu-khichat).

## Quy tắc actor WIP (2026-10-19, từ Lỗi 11)
- CẤM đưa actor đang làm dở vào `assets/actors/`: `reel.py library()` tự quét mọi `*/card.yaml`, actor WIP sẽ bị bốc vào cast ngẫu nhiên và render hỏng.
- Actor kiểu "lego nhiều mảnh" chỉ được vào kho khi đã có code lắp ráp đầy đủ + `validate_actor` ĐẠT. Trước đó giữ ở `reference/` hoặc branch riêng.
- `SKIP_ACTORS` hiện tại: `{"uyen-thanh", "uyen-thanh-lego"}`.
