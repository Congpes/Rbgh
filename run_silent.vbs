Set WshShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Lấy đường dẫn thư mục hiện tại
scriptDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Chuyển đến thư mục dự án
WshShell.CurrentDirectory = scriptDir

' Chạy run_silent.bat nhưng ẩn console window (0 = hidden)
WshShell.Run "cmd.exe /c run_silent.bat", 0, False

Set WshShell = Nothing
Set fso = Nothing

