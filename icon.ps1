# Script tạo shortcut trên desktop để chạy app ẩn log

$ErrorActionPreference = "Stop"

# Lấy đường dẫn thư mục dự án
$projectPath = Split-Path -Parent $MyInvocation.MyCommand.Path
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Robot Giao Do An.lnk"

# Đường dẫn đến file chạy
$targetPath = Join-Path $projectPath "run_silent.vbs"

# Tạo shortcut
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = "wscript.exe"
$Shortcut.Arguments = "`"$targetPath`""
$Shortcut.WorkingDirectory = $projectPath
$Shortcut.Description = "Robot Giao Do An - Food Delivery Robot"
$Shortcut.WindowStyle = 7  # Minimized

# Tim icon (uu tien icon co san, neu khong thi dung icon Python)
$iconPath = Join-Path $projectPath "assets\images\robot_icon.ico"
if (-not (Test-Path $iconPath)) {
    # Dung icon Python lam mac dinh
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonPath) {
        $iconPath = $pythonPath
        $Shortcut.IconLocation = "$iconPath,0"
    }
} else {
    $Shortcut.IconLocation = $iconPath
}

$Shortcut.Save()

Write-Host "Da tao shortcut tren desktop: $shortcutPath" -ForegroundColor Green
Write-Host "  Ban co the nhan dup vao shortcut de chay app (an log)" -ForegroundColor Yellow

