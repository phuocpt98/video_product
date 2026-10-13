# Biểu cảm của diễn viên (sửa ảnh từ ảnh gốc)

Dùng cho `scripts/new_actor.py` bước 2, gọi một lần cho mỗi biểu cảm, ảnh tham chiếu = `source/master.png`. Tỉ lệ 9:16, cùng khung với ảnh gốc để cắt đầu theo cùng tọa độ.

```
Edit the reference image master.png. Keep EVERYTHING identical: same character, same art style, same flat colors,
same outline, same pose, same outfit, same hair, same size and position on the canvas, same white background.
Change ONLY the facial expression to: {expr}.
Do not move or resize the figure. No text, no caption, no watermark.
```

Giá trị `{expr}` theo hợp đồng (`docs/plans/protocols.md`):

| Khoá | `{expr}` |
|---|---|
| neutral | calm neutral, mouth closed |
| neutral_talk | calm neutral, mouth slightly open as if talking |
| smirk | {signature}, mouth closed |
| smirk_talk | {signature}, mouth open talking |
| shocked | shocked, eyes wide open, mouth open |
| angry | angry, brows down, mouth open shouting |
| sad | sad, brows up in the middle, eyes glistening, mouth closed |
| blink | calm neutral with both eyes closed |

`{signature}` = nét đặc trưng trong card, ví dụ "confident half smirk" hay "cold elegant smile".
