param()

# Tạo các thư mục cần thiết cho models và dữ liệu
$dirs = @(
  "data/models/vosk",
  "data/models/piper",
  "data/models/llm",
  "data/models/wakeword",
  "data/models/vad",
  "data/models/noise_suppression",
  "data/chroma",
  "data/kb",
  "data/samples",
  "assets/fonts"
)

foreach ($d in $dirs) {
  if (-not (Test-Path $d)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
  }
}

# Tạo .gitkeep trong các thư mục rỗng (nếu chưa có)
foreach ($d in $dirs) {
  $keep = Join-Path $d ".gitkeep"
  if (-not (Test-Path $keep)) {
    New-Item -ItemType File -Force -Path $keep | Out-Null
  }
}

Write-Host "Thư mục và .gitkeep đã được chuẩn bị. Hãy tải file theo DOWNLOAD_CHECKLIST.md và đặt vào đúng chỗ." -ForegroundColor Green


