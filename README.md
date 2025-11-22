<<<<<<< HEAD
## Robot Service GUI

### Yêu cầu hệ thống
- Python 3.9+ (Windows/Linux)
- Trên Linux cần thư viện hệ thống cho PyQt5 multimedia (để phát `assets/sounds/nhanhang.mp3`):
  - Debian/Ubuntu:
    - `libqt5multimedia5 libqt5multimedia5-plugins`
    - `gstreamer1.0-plugins-base gstreamer1.0-plugins-good`
    - `libasound2`

### Cài đặt và chạy

#### Windows
1. Mở `run.bat` (double click) hoặc chạy trong PowerShell:
   ```powershell
   .\run.bat
   ```

#### Linux
1. Cấp quyền thực thi và chạy script:
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
2. Nếu không nghe được âm thanh, cài thêm gói hệ thống:
   ```bash
   sudo apt update && sudo apt install -y \
     libqt5multimedia5 libqt5multimedia5-plugins \
     gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
     libasound2
   ```

### Cấu trúc thư mục chính
- `src/`: mã nguồn ứng dụng (PyQt5)
- `assets/sounds/nhanhang.mp3`: âm thanh nhận cuộc gọi
- `data/`: dữ liệu `rooms.json`, `session.json`
- `data/models/`: thư mục chứa các file model (không được commit vào git do kích thước lớn)

### Tải Model Files

Các file model có kích thước lớn (>100MB) không được lưu trữ trên GitHub. Bạn cần tải chúng từ nguồn gốc:

1. **Vosk Model (STT)**: Tải từ [Vosk Models](https://alphacephei.com/vosk/models)
   - Model: `vosk-model-vn-0.4` (tiếng Việt)
   - Đặt vào: `data/models/vosk/vosk-model-vn-0.4/`

2. **Piper Model (TTS)**: Tải từ [Piper Models](https://github.com/rhasspy/piper/releases)
   - Model: `vi_VN-vais1000-medium.onnx`
   - Đặt vào: `data/models/piper/piper/`

Hoặc chạy script chuẩn bị thư mục:
```powershell
.\scripts\prepare_dirs.ps1
```

### Xử lý file lớn trên GitHub

Nếu gặp lỗi "file vượt quá 100MB" khi push lên GitHub, xem file `fix_git_large_files.md` để biết cách xử lý.

### Ghi chú
- Ứng dụng dùng PyQt5. Trên Linux nếu chạy qua WSL, hãy dùng môi trường có display server (X11) hoặc chạy trực tiếp trên máy Linux.
- Các file model không được commit vào git. Sử dụng `.gitignore` để loại trừ chúng.

=======
# Rbgh
>>>>>>> 4a2bfadde478c33fe7cb02dce8670faee4a8c309
