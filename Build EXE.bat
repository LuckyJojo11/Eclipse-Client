@echo off
setlocal
cd /d "%~dp0"

set "PYTHON=python"
if exist "C:\Program Files\Python312\python.exe" set "PYTHON=C:\Program Files\Python312\python.exe"

if not exist "build_venv\Scripts\python.exe" (
    "%PYTHON%" -m venv build_venv
)

"build_venv\Scripts\python.exe" -m pip install --upgrade pip pyinstaller

set "PYTHONUSERBASE=%CD%\build_venv"
set "PYTHONNOUSERSITE=1"

"build_venv\Scripts\python.exe" -m PyInstaller --clean --noconsole --onefile --name "Eclipse Client" --icon "lib\images\icon.ico" "lib\bootstrap.py"

if exist "dist\Eclipse Client.exe" (
    copy /Y "dist\Eclipse Client.exe" "Eclipse Client.exe"
    echo.
    echo Eclipse Client.exe wurde erstellt.
) else (
    echo.
    echo Build fehlgeschlagen.
)

pause
