
REM Check if Python is installed
py --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    msg * "Python chua duoc cai dat! Vui long tai Python tu: https://python.org"
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    py -m venv venv >nul 2>&1
)

REM Activate virtual environment
call venv\Scripts\activate.bat >nul 2>&1

REM Install dependencies silently
if not exist "venv\installed.flag" (
    pip install -r requirements.txt >nul 2>&1
    echo. > venv\installed.flag
)

REM Create necessary directories
if not exist "src\ui" mkdir src\ui >nul 2>&1
if not exist "src\core" mkdir src\core >nul 2>&1
if not exist "src\utils" mkdir src\utils >nul 2>&1
if not exist "assets\images\emotions" mkdir assets\images\emotions >nul 2>&1
if not exist "assets\sounds" mkdir assets\sounds >nul 2>&1
if not exist "data" mkdir data >nul 2>&1

REM Create __init__.py files
if not exist "src\__init__.py" echo. > src\__init__.py
if not exist "src\ui\__init__.py" echo. > src\ui\__init__.py
if not exist "src\core\__init__.py" echo. > src\core\__init__.py
if not exist "src\utils\__init__.py" echo. > src\utils\__init__.py

REM Add src to PYTHONPATH and run the application silently
set PYTHONPATH=%PYTHONPATH%;%CD%\src
cd /d %~dp0

REM Thử dùng pythonw từ venv trước, nếu không có thì dùng python
if exist "venv\Scripts\pythonw.exe" (
    venv\Scripts\pythonw.exe src\main.py
) else (
    pythonw src\main.py
)

REM Deactivate virtual environment
deactivate >nul 2>&1

