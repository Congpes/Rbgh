

REM Check if Python is installed
py --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long tai Python tu: https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [INFO] Tao virtual environment...
    py -m venv venv
)

REM Activate virtual environment
echo [INFO] Kich hoat virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
if not exist "venv\installed.flag" (
    echo [INFO] Cai dat dependencies...
    pip install -r requirements.txt
    echo. > venv\installed.flag
) else (
    echo [INFO] Dependencies da duoc cai dat.
)

REM Create necessary directories
echo [INFO] Tao thu muc can thiet...
if not exist "src\ui" mkdir src\ui
if not exist "src\core" mkdir src\core  
if not exist "src\utils" mkdir src\utils
if not exist "assets\images\emotions" mkdir assets\images\emotions
if not exist "assets\sounds" mkdir assets\sounds
if not exist "data" mkdir data

REM Create __init__.py files
if not exist "src\__init__.py" echo. > src\__init__.py
if not exist "src\ui\__init__.py" echo. > src\ui\__init__.py
if not exist "src\core\__init__.py" echo. > src\core\__init__.py
if not exist "src\utils\__init__.py" echo. > src\utils\__init__.py

echo.
echo [INFO] Bat dau chay ung dung...
echo ===============================================
echo.

REM Add src to PYTHONPATH and run the application
set PYTHONPATH=%PYTHONPATH%;%CD%\src
cd /d %~dp0
python src\main.py

REM Check if application ran successfully
if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] Ung dung gap loi! Chi tiet:
    echo - Kiem tra file main.py co ton tai khong
    echo - Kiem tra cac file UI da duoc tao chua  
    echo - Xem log loi o tren de biet chi tiet
    echo.
    pause
) else (
    echo.
    echo [INFO] Ung dung da dong thanh cong.
)

REM Deactivate virtual environment
deactivate

pause
