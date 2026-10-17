@echo off
setlocal
cd /d %~dp0
if not exist .venv py -3 -m venv .venv
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0create_desktop_shortcut.ps1"
echo.
echo Installed. A desktop shortcut named "Asart Bookkeeping" was created.
pause
