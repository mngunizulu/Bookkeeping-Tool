@echo off
setlocal EnableExtensions
cd /d "%~dp0"
set "NOPAUSE=0"
if /I "%~1"=="/nopause" set "NOPAUSE=1"

echo ==============================================
echo   Asart Bookkeeping - Application Build
echo ==============================================
echo.

if not exist .venv (
  echo Creating Python environment...
  py -3 -m venv .venv
  if errorlevel 1 goto :error
)

call .venv\Scripts\activate.bat
if errorlevel 1 goto :error

python -m pip install --upgrade pip
if errorlevel 1 goto :error
pip install -r requirements.txt
if errorlevel 1 goto :error

if exist "build\Asart Bookkeeping" rmdir /s /q "build\Asart Bookkeeping"
if exist "dist\Asart Bookkeeping" rmdir /s /q "dist\Asart Bookkeeping"

pyinstaller --noconfirm --clean --windowed ^
  --name "Asart Bookkeeping" ^
  --version-file version_info.txt ^
  --collect-all reportlab ^
  --collect-all cv2 ^
  run.py
if errorlevel 1 goto :error

echo.
echo Build complete:
echo   dist\Asart Bookkeeping\Asart Bookkeeping.exe
if "%NOPAUSE%"=="0" pause
exit /b 0

:error
echo.
echo ERROR: Build failed. Review the messages above.
if "%NOPAUSE%"=="0" pause
exit /b 1
