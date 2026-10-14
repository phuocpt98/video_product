# video_product: truyện chữ → video kể truyện

Biến **1 file truyện chữ tiếng Việt** thành **1 video hoàn chỉnh**:
- giọng đọc AI chạy trên máy;
- hình là **hoạt hình chibi ngẫu nhiên**, không khớp nội dung truyện, chỉ để giữ mắt người xem;
- kèm file phụ đề `.srt` và gói thông tin để đăng YouTube.

Chạy được trên **macOS** và **Ubuntu**, không cần màn hình hay card đồ hoạ.

> File này là **hướng dẫn vận hành đầy đủ**, viết cho người và cho mọi AI agent. Đọc từ trên xuống là đủ để cài,
> chạy, sửa lỗi và bổ sung kho hình.

```
truyện.txt/.md/.docx
   │  python -m src.produce run <file>
   ▼
1. NẠP + CHIA PHẦN    mỗi phần ~2500 ký tự, cắt ở tên chương / ranh giới đoạn → stories/<slug>/parts/NNN.txt
   ▼                  (với mỗi phần, lần lượt:)
2. GIỌNG              VieNeu-TTS → audio/NNN.mp3 + NNN.srt
3. VIDEO              hoạt hình ngẫu nhiên khớp độ dài giọng → video/NNN.mp4 (đã có tiếng)
   ▼                  việc lỗi → ghi lỗi, thử lại; chạy lại lệnh = làm tiếp từ chỗ dở
4. GHÉP + XUẤT BẢN    đủ mọi phần → output/<slug>.mp4 + <slug>.srt + upload.md
```

## 1. Cài đặt (máy mới)

```bash
git clone https://github.com/phuocpt98/video_product.git && cd video_product
git checkout plan-muse
bash scripts/setup.sh        # ffmpeg + Python venv + thư viện + model giọng (~540 MB) + chạy test
```

**Yêu cầu máy:**
- Python 3.11 trở lên và ffmpeg. Script tự cài ffmpeg (Homebrew trên Mac, `apt` trên Ubuntu, cần `sudo`). Ubuntu 24.04 có sẵn Python 3.12; Ubuntu 22.04 phải cài thêm `sudo apt install python3.11 python3.11-venv` trước.
- **RAM trống từ 3 GB trở lên.** Mỗi tiến trình đọc giọng tốn khoảng 1,8 GB.
  - Máy 8 GB: đặt `tts_workers: 1` trong `config.yaml`.
  - Trước khi chạy, tắt trình duyệt và các app nặng.
- Đĩa: khoảng 1 GB cho model, cộng khoảng 50 MB cho mỗi phút video thành phẩm.

**Kiểm tra cài đặt:**
```bash
.venv/bin/python -m pytest -q        # phải in "32 passed" (hoặc hơn)
```

## 2. Vận hành

Mọi lệnh chạy ở **gốc repo** với Python của `.venv`.

### 2.1 Làm một truyện
```bash
.venv/bin/python -m src.produce run duong/dan/truyen.md                     # video ngang YouTube 1920x1080
.venv/bin/python -m src.produce run truyen.docx --slug ten-truyen --size 1080x1920   # khung dọc TikTok
```

**File truyện:**
- `.txt`, `.md` hoặc `.docx` (Google Docs: Tệp → Tải xuống → .docx hoặc .txt).
- **Dòng đầu là tiêu đề** (không được đọc thành giọng). Truyện không có tiêu đề thì thêm một dòng tiêu đề lên đầu, nếu không câu mở đầu sẽ bị coi là tiêu đề.
- Các dòng như `Chương 1`, `Phần 2`, `Hồi 3` được dùng làm ranh giới chia phần.
- Markdown (`#`, `**`) tự được bỏ trước khi đọc.

**Kết quả** nằm ở `stories/<slug>/output/`:
- `<slug>.mp4`: video hoàn chỉnh;
- `<slug>.srt`: phụ đề;
- `upload.md`: tiêu đề, mốc từng phần để dán vào mô tả YouTube, việc cần nhớ khi đăng.

**Việc đăng lên mạng làm tay.** Máy không tự đăng.

### 2.2 Theo dõi, làm tiếp, làm lại
```bash
.venv/bin/python -m src.produce status <slug>                 # bảng trạng thái từng phần + lỗi
.venv/bin/python -m src.produce run --slug <slug>             # LÀM TIẾP: việc xong bỏ qua, việc lỗi/dở làm lại
.venv/bin/python -m src.produce run --slug <slug> --redo 003          # làm lại cả phần 3 (giọng + video)
.venv/bin/python -m src.produce run --slug <slug> --redo 005:video    # chỉ dựng lại hình phần 5
.venv/bin/python -m src.produce run --slug <slug> --tts-workers 1 --video-workers 1   # máy yếu / thiếu RAM
```

**Quy tắc trạng thái:**
- Trạng thái lưu ở `stories/<slug>/tasks.json`. Mỗi phần có 2 việc: `voice` và `video`.
- Mỗi việc ở một trong các trạng thái `todo`, `running`, `done`, `failed`.
- Một việc lỗi được thử lại tối đa `retries` lần trong một lượt chạy (mặc định 2). Hết lượt mà vẫn lỗi thì ghi `failed` kèm câu lỗi, rồi chuyển sang phần khác.
- Vết lỗi đầy đủ nằm ở `stories/<slug>/log.jsonl`.
- **Chỉ ghép khi mọi việc đều `done`.** Lệnh trả mã thoát 0 khi đã xuất bản xong, 1 khi còn việc chưa xong.
- File chỉ xuất hiện khi việc đã làm trọn (ghi ra file tạm rồi mới đổi tên). Máy tắt giữa chừng thì chạy lại lệnh là đủ.
- Làm lại giọng của một phần thì video phần đó cũng tự được dựng lại.
- Nạp lại **cùng** file truyện thì làm tiếp. Nạp file **khác** nội dung mà trùng slug thì lệnh báo lỗi; đặt `--slug` khác.
- **Giọng, tốc độ, khung hình, độ dài hồi được khoá theo truyện** (ghi trong `tasks.json` lúc nạp). Chỉ đổi được bằng `--voice/--speed/--size` khi CHƯA có phần nào làm xong theo giá trị cũ, nếu không lệnh báo lỗi (tránh video ghép lẫn giọng, lẫn khung). Muốn đổi cả truyện: nạp lại với `--slug` mới.
- **Số tiến trình và số lần thử lại theo máy**: luôn đọc lại từ `config.yaml` (hoặc `--tts-workers`, `--video-workers`, `--retries`) mỗi lần chạy.
- Hai lệnh `run` cùng một truyện cùng lúc bị chặn (file `stories/<slug>/.lock`).

### 2.3 Tham số (`config.yaml`, mục `produce`)
| Khoá | Mặc định | Ý nghĩa |
|---|---|---|
| `channel` | `khoai-tay-review` | Lấy giọng (`tts.voice`) và tốc độ đọc (`tts.speed`) từ `channels/<channel>/channel.yaml` |
| `part_chars` | 2500 | Cỡ một phần. Phần nhỏ thì lỗi làm lại rẻ hơn, nhưng file nhiều hơn |
| `retries` | 2 | Số lần thử lại mỗi việc trong một lượt chạy |
| `size` | 1920x1080 | 1080x1920 cho TikTok |
| `act_seconds` | 60 | Hoạt hình đổi nền và diễn viên sau mỗi khoảng này |
| `tts_workers` | 3 | Số tiến trình đọc giọng song song. **Máy RAM 8 GB: để 1** |
| `video_workers` | 0 | Số tiến trình vẽ song song. 0 = tự chọn (số nhân trừ 2, tối thiểu 1) |

- Tham số dòng lệnh ghi đè `config.yaml`: `--voice`, `--speed`, `--size`, `--part-chars` (chỉ có tác dụng lúc nạp truyện, xem quy tắc khoá ở 2.2); `--retries`, `--tts-workers`, `--video-workers` (mỗi lần chạy).
- Giọng có sẵn (VieNeu): Ngọc Huyền (mặc định), Trúc Ly, Quỳnh Anh, Ngọc Linh, Mai Anh, Thùy Dung, Đoan Trang, Mỹ Duyên, Kim Thanh, Ngọc Trân, Thục Đoan, Thiện Minh, Hải Đăng, Quang Sơn, Minh Đức, Thái Sơn, Thanh Bình, Minh Triết, Đức Trí, Quốc Tuấn, Xuân Vĩnh, Phạm Tuyên, Thiền Tâm Đức, Adam, Adam bựa. Mẫu nghe thử: chưa có, chạy truyện mẫu với `--voice` để nghe.
- Tên giọng sai thì câu báo lỗi in ra danh sách giọng hợp lệ.

### 2.4 Tốc độ đã đo (Mac M-series 10 nhân)
- Giọng: khoảng 15–25 giây cho mỗi phần ~1500 ký tự.
- Video: khoảng 6 lần thời gian thực ở 1080p (150 giây video dựng mất 23 giây).
- Truyện thử 3 phần (2,4 phút video) chạy hết 1,6 phút.
- Máy Ubuntu 2 nhân chưa đo. Ước tính chậm hơn 3–5 lần.

### 2.5 Lỗi thường gặp
| Triệu chứng | Cách xử lý |
|---|---|
| `Voice '...' not found` | Sai tên giọng. Chạy lại với `--voice "<tên trong danh sách lỗi>"` |
| Máy treo, tiến trình bị `Killed`, lỗi bộ nhớ | Thiếu RAM: chạy lại `run --slug <slug> --tts-workers 1 --video-workers 1` (hoặc đặt trong `config.yaml`), đóng app khác |
| `External data path escapes model directory` | Chạy `.venv/bin/python scripts/setup_models.py` (đổi symlink model thành file thật) |
| `ffmpeg: command not found` | Chạy lại `bash scripts/setup.sh` |
| Cảnh báo `unauthenticated requests to the HF Hub` | Vô hại, bỏ qua |
| Việc kẹt ở `running` sau khi máy tắt | Chạy lại `run --slug <slug>`: việc dở tự quay về `todo` |
| Video một phần trông lỗi (nhân vật méo, khung trống) | `--redo NNN:video`: dựng lại với cùng seed. Muốn hình khác thì đổi `seed` của phần đó trong `tasks.json` rồi `--redo NNN:video` |

## 3. Hoạt hình ngẫu nhiên (`src/studio/reel.py`)

**Cách hoạt động:**
- Video được chia thành **hồi** khoảng 1 phút. Mỗi hồi random: 1 nền, 2–3 diễn viên, tông ngày, hoàng hôn hoặc đêm.
- Mỗi hồi gồm các **nhịp** 5–9 giây. Mỗi nhịp random một **vi kịch bản** và một **góc máy** (toàn, trung, cận; đẩy vào, kéo ra, lia).
- Bốc không hoàn lại, nên trong vài lần bốc gần nhau không lặp nền, diễn viên hay vi kịch bản.
- Nhân vật nhép miệng theo độ to của giọng đọc.
- Giữa hai hồi có dải màu chéo quét ngang để đổi cảnh.
- Mọi thứ tất định theo `seed`: cùng seed thì ra cùng video. Seed của từng phần nằm trong `tasks.json`; kế hoạch cảnh lưu ở `video/NNN.plan.json`.

**17 vi kịch bản hiện có:**

| Tên | Diễn biến |
|---|---|
| `chat` | Nói chuyện qua lại |
| `chase` | Rượt đuổi qua khung |
| `dance` | Nhảy múa |
| `jump_joy` | Nhảy cẫng |
| `surprise` | Người mới bước vào, cả nhóm giật mình |
| `angry` | Nổi giận, dậm chân |
| `sad` | Buồn, có mây mưa trên đầu |
| `lightning` | Sét đánh, người trúng hoá bóng đen |
| `slip` | Trượt ngã, sao xoay quanh đầu |
| `spin` | Xoay vòng |
| `phone` | Nghe điện thoại rồi giật mình |
| `laugh_at` | Chỉ trỏ cười HAHA |
| `parade` | Diễu hành ngang khung |
| `wave` | Sóng người |
| `sleep` | Ngủ gật có Zzz |
| `love` | Thả tim |
| `pop_in` | Lần lượt bật ra |

**Thêm một vi kịch bản:**
1. Viết hàm `b_<tên>(b, t, dur, n, R)` theo mẫu các hàm có sẵn. Hàm trả về 3 thứ:
   - trạng thái từng diễn viên;
   - ký hiệu (`sweat`, `anger`, `!`, `?`, `hearts`, `stars`, `dizzy`, `zzz`, `notes`, `smoke`, `rain`, `bolt`…);
   - hiệu ứng màn hình (`dark`, `flash`, `shake`).
2. Thêm dòng `"<tên>": (số diễn viên tối thiểu, (góc máy cho phép))` vào `BEATS`.
3. Chạy `pytest`. Test vẽ thử mọi vi kịch bản ở cả 16:9 và 9:16.

**Xem thử nhanh, không cần giọng:**
```bash
.venv/bin/python -m src.studio.reel --seconds 60 --out tmp/reel/thu.mp4 [--seed 7] [--size 1080x1920]
```

Lõi vẽ dùng pygame ở chế độ không màn hình (`SDL_VIDEODRIVER=dummy`), đẩy khung hình thẳng vào ffmpeg. Đã đo nhanh hơn Pillow khoảng 3,5 lần, và nhanh hơn quay trình duyệt khoảng 10 lần.

## 4. Kho thư viện (tài nguyên hình)

**Kho được tự quét:** cứ thêm đúng cấu trúc là hoạt hình tự dùng, không phải sửa code.
**Chỉ đưa vào kho hình tự tạo hoặc có giấy phép dùng thương mại.**

| Kho | Ở đâu | Hiện có |
|---|---|---|
| Diễn viên | `assets/actors/<id>/card.yaml` + `parts/` | 36 người chibi: 9 diễn viên chính, 16 quần chúng `qc-*`, 11 vai của truyện cũ |
| Nền | `assets/scenes/<id>/card.yaml` + `master.jpg` | 41 nền (đô thị: văn phòng, phố, nhà, bệnh viện…). `sky-day` và `sky-night` không dùng làm nền hồi |
| Bộ phận nhân vật | `assets/parts/` (`INDEX.md`, `parts.yaml`) | 112 bộ phận mặt, 24 bộ đồ × 3 vóc: nguyên liệu để ghép diễn viên mới không cần AI |
| Đạo cụ | `assets/props/` (`props.yaml`) | 24 đạo cụ cầm tay (hoạt hình chưa dùng) |
| Font | `assets/fonts/` | Be Vietnam Pro (OFL) |

### 4.1 Diễn viên
**Cấu trúc một diễn viên:**
- `card.yaml` gồm:
  - `rig`: cách ghép đầu lên thân;
  - `heads`: 8 biểu cảm `neutral`, `neutral_talk`, `smirk`, `smirk_talk`, `shocked`, `angry`, `sad`, `blink`, mỗi cái trỏ tới 1 file PNG nền trong suốt;
  - `outfits.<bộ đồ>.bodies`: 4 tư thế `relaxed`, `hips`, `phone`, `point`.
- Đầu và thân là ảnh rời. Code ghép đầu lên cổ (`src/studio/puppet.py`).

**Ba cách thêm diễn viên:**
1. **Quần chúng ngẫu nhiên, không cần AI:**
   ```bash
   .venv/bin/python scripts/make_extras.py --n 8 --seed 5
   ```
   Ghép ngẫu nhiên từ kho bộ phận, ra `qc-XX`.
2. **Tự chọn từng bộ phận trên trang web:**
   ```bash
   .venv/bin/python scripts/character_maker.py
   ```
   Mở http://localhost:8765, chọn đầu, mắt, miệng, da, bộ đồ, màu, rồi bấm Lưu.
3. **Từ một ảnh gốc** (ảnh chibi toàn thân, nền trơn):
   ```bash
   .venv/bin/python scripts/new_actor.py <id> --master anh.png --look "..." --hair "..." --outfit <bo-do> --outfit-desc "..." --no-gen
   ```
   - Script tách lớp tóc, đầu, thân, rồi liệt kê các ảnh biểu cảm và tư thế còn thiếu.
   - Bỏ `--no-gen` thì script gọi `agy` (Gemini) để tạo ảnh thiếu.
   - Prompt nằm ở `prompts/actor_*.md`.

**Kiểm tra trước khi dùng:**
```bash
.venv/bin/python -m src.studio.validate_actor <id> --preview
```
Exit 0 là ĐẠT.

Thêm tư thế mới (chạy, nhảy, ngồi…) bằng cách thêm ảnh thân vào `outfits.<bộ đồ>.bodies`. Hoạt hình hiện chỉ dùng 4 tư thế chuẩn.

### 4.2 Nền
**Cách 1, tạo thủ công:**
- Tạo thư mục `assets/scenes/<id>/`, đặt vào đó `master.jpg` (khoảng 1400×760, ngang) và `card.yaml`:
  ```yaml
  id: beach
  type: establishing
  tags: [bãi biển]
  master: master.jpg
  ground_y: 0.9      # chân nhân vật đứng ở 90% chiều cao ảnh
  ```
- Ảnh nền cần:
  - **không có người, không có chữ**;
  - **sàn trống ở nửa dưới** để nhân vật đứng;
  - cùng phong cách: chibi hoạt hình phẳng, viền đen, màu đặc, không 3D.

**Cách 2, cắt từ bảng 3 nền tạo trên web:**
```bash
.venv/bin/python scripts/make_scene_sheet.py --prompts             # in prompt ra tmp/scene_prompts.md
.venv/bin/python scripts/make_scene_sheet.py <số> --sheet bang.png # cắt bảng thành 3 nền
```

## 5. Cấu trúc repo

```
README.md            hướng dẫn này (nguồn chính)
config.yaml          tham số dây chuyền
src/produce.py       DÂY CHUYỀN CHÍNH: nạp → chia → giọng → video → làm lại → ghép
src/studio/reel.py   hoạt hình ngẫu nhiên (đạo diễn random + lõi vẽ pygame)
src/studio/puppet.py ghép đầu + thân diễn viên
src/studio/          công cụ kho: cutout, segment, avatar, validate_actor, maker/ (trang tạo nhân vật)
src/common/tts.py    giọng đọc VieNeu + .srt
src/common/agy.py, imagegen.py   gọi Gemini (agy) để tạo ảnh bổ sung kho (tuỳ chọn)
src/contracts.py     kiểm định dạng card diễn viên / bản thiết kế nhân vật
scripts/             setup.sh, setup_models.py, công cụ bổ sung kho, hub.py (bảng việc GitHub Issues)
assets/              KHO THƯ VIỆN (mục 4)
channels/<kênh>/channel.yaml     giọng, tốc độ, thương hiệu của kênh
prompts/             prompt tạo ảnh diễn viên, vai trò agent agy
tests/               pytest; tests/data/sample_story.txt = truyện mẫu để chạy thử
docs/                kế hoạch, quyết định, nghiên cứu (lịch sử dự án)
stories/<slug>/      DỮ LIỆU TỪNG TRUYỆN, sinh ra khi chạy, KHÔNG đưa lên git
tmp/                 nháp, xoá lúc nào cũng được, không lên git
```

## 6. Quy tắc cho AI làm việc trên repo
1. **Đọc README này trước.** Việc chạy truyện chỉ cần mục 2. Việc sửa hình đọc thêm mục 3–4.
2. **Báo trung thực:**
   - "Xong" nghĩa là lệnh chạy ra file thật: `status` không còn việc chưa `done` và có `output/<slug>.mp4`.
   - Lỗi thì dán đúng câu lỗi từ `status` hoặc `log.jsonl`.
   - Không bịa kết quả của việc chưa chạy.
3. **Không commit:**
   - `stories/`, `tmp/`, `.venv/`, `.cache/`, `.env`, file media lớn (`*.mp4`, `*.wav`);
   - nội dung truyện của người khác.
4. Sửa code xong thì chạy `.venv/bin/python -m pytest -q`. Thêm tính năng thì thêm test vào `tests/`.
5. **Mỗi thông tin chỉ nằm một chỗ.** Đổi cách vận hành thì sửa README này cho khớp.
6. **Không tự đăng video, không tiêu tiền, không xoá dữ liệu ngoài `tmp/`** khi chưa được Người sáng lập đồng ý.
7. Repo trong `tool/` (nếu có) chỉ để tham khảo ý tưởng. Không import, không chép code.
8. Phối hợp giữa các máy (Claude ↔ Muse ↔ Người sáng lập) qua GitHub Issues: `scripts/hub.py`, giao thức ở `docs/plans/collab-protocol.md`.

## 7. Rủi ro cần biết
- **YouTube "inauthentic content"** (từ 15/7/2025): video giọng AI trên hình lặp khuôn có thể bị tắt kiếm tiền cả kênh. Để giảm rủi ro:
  - dùng truyện tự viết, hoặc có lời bình của người kể;
  - mỗi video một seed (dây chuyền đã tự làm);
  - không đăng dồn;
  - khai báo nội dung có dùng AI.
- **Bản quyền truyện:** đọc nguyên văn truyện của người khác là vi phạm. Chỉ dùng truyện có quyền.
- **Giấy phép:**
  - VieNeu-TTS: Apache-2.0;
  - pygame-ce: LGPL, dùng như thư viện, không sửa;
  - font Be Vietnam Pro: OFL;
  - hình trong `assets/`: tự tạo.
