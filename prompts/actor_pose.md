# Tư thế thân của diễn viên (sửa ảnh từ ảnh gốc)

Dùng cho `scripts/new_actor.py` bước 3, một lần cho mỗi tư thế, ảnh tham chiếu = `source/master.png`. Tỉ lệ 9:16.

```
Edit the reference image master.png. Keep EVERYTHING identical: same character, same face, same art style, same flat
colors, same outline, same outfit, same hair behind the back, same scale, same feet position, same white background.
Change ONLY the arms and hands to: {pose}. Head and face unchanged.
No text, no caption, no watermark.
```

| Khoá | `{pose}` |
|---|---|
| relaxed | (ảnh gốc, không cần tạo) |
| hips | both hands on hips, confident |
| phone | right hand holding a smartphone up to the right ear |
| point | right arm extended, index finger pointing forward to the viewer's right |
| walk_a | mid-step walking, left leg forward, arms swinging naturally |
| walk_b | mid-step walking, right leg forward, arms swinging naturally |

Thêm bộ đồ mới: cùng prompt, thay "Change ONLY the arms" bằng "Change ONLY the clothes to: {outfit}", giữ tư thế. Lớp đầu dùng lại từ bộ cũ, nên mặt trong ảnh mới có lệch cũng không sao.
