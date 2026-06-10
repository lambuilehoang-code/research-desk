# Cập nhật cho bạn bè (Research Desk)

Hướng dẫn ngắn: lấy bản mới từ GitHub và chạy lại app.

---

## Bạn đã cài app rồi — chỉ cần update

### Cách 1: Download ZIP (không cần Git)

1. Mở: https://github.com/lambuilehoang-code/research-desk.git  
2. **Code** → **Download ZIP**  
3. Giải nén vào thư mục mới (hoặc thay thế thư mục cũ, **giữ lại** file `.env` và folder `.venv` nếu đã setup xong)  
4. Copy file `.env` cũ sang thư mục mới (nếu giải nén chỗ khác)  
5. Chạy app:

```powershell
cd C:\đường-dẫn-đến-thư-mục-có-app.py
.venv\Scripts\python.exe app.py
```

### Cách 2: Git pull (nếu đã clone)

```powershell
cd C:\đường-dẫn-research-desk
git pull
.venv\Scripts\python.exe app.py
```

---

## Đổi tài khoản Google (lưu trên máy, không cần đặt tên)

1. App → **Switch account**
2. **Mở Chromium** → ảnh Google → chọn tài khoản hoặc **Thêm tài khoản**
3. Enter trong terminal → **Xong — tải notebook**

Google lưu tài khoản trong Chromium — lần sau chỉ chọn lại.

## Ngôn ngữ theo câu hỏi
|---------|-------------|
| Tiếng Việt (có dấu hoặc nhiều từ Việt) | Tiếng Việt |
| Tiếng Anh | English |

**Không cần** đổi `LANGUAGE=en` trong `.env` để hỏi tiếng Anh — chỉ cần **gõ câu hỏi bằng tiếng Anh**.

Ví dụ:

- `Tóm tắt notebook này` → báo cáo tiếng Việt  
- `Summarize this notebook` → English report  

**Settings → Default language** chỉ dùng khi câu hỏi trống (fallback).

---

## File `.env` (tùy chọn)

Trong `.env` có thể có:

```env
LANGUAGE=vi
```

Đó là **mặc định dự phòng**, không ép mọi câu trả lời sang tiếng Việt. Có thể xóa `LANGUAGE=en` nếu không cần.

---

## Lỗi thường gặp sau khi update

| Lỗi | Cách xử lý |
|-----|------------|
| `No module named 'PyQt6'` | Chạy `.venv\Scripts\python.exe app.py`, không dùng `py app.py` |
| Vẫn bản cũ | Đóng app, mở đúng thư mục mới, chạy lại |
| Trả lời sai ngôn ngữ | Hỏi rõ bằng tiếng bạn muốn; câu Việt không dấu có thể bị nhận là English |

---

## Người maintain push lên GitHub

```powershell
cd C:\AIResearch
git add research_agent.py UI/workers.py UI/settings_dialog.py README.md .env.example UPDATE_FRIENDS.md
git commit -m "Auto-detect reply language from user question (vi/en)"
git push
```

*(Chỉ chạy nếu đã có git remote; không commit file `.env`.)*
