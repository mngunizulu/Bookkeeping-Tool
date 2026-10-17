@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ==============================================
echo   Asart Bookkeeping - Windows Installer Build
echo ==============================================
echo.

call build_windows.bat /nopause
if errorlevel 1 (
  echo.
  echo ERROR: Application build failed.
  pause
  exit /b 1
)

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if not defined ISCC if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if not defined ISCC for /f "delims=" %%I in ('where ISCC.exe 2^>nul') do if not defined ISCC set "ISCC=%%I"

if not defined ISCC (
  echo.
  echo Inno Setup 6 was not found.
  echo.
  echo Install Inno Setup 6 once, then run this file again.
  echo Official download: https://jrsoftware.org/isdl.php
  echo.
  echo Your application itself WAS built successfully under:
  echo   dist\Asart Bookkeeping\
  pause
  exit /b 2
)

if exist installer rmdir /s /q installer
mkdir installer

echo.
echo Building installer...
"%ISCC%" installer.iss
if errorlevel 1 (
  echo.
  echo ERROR: Installer build failed.
  pause
  exit /b 1
)

echo.
echo ==============================================
echo SUCCESS
 echo Installer created:
echo   installer\AsartBookkeeping_Setup_v0.2.1.exe
echo.
echo Copy that ONE file to your USB drive.
echo ==============================================
pause
