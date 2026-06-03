@echo off
setlocal
cd /d "%~dp0\..\.."

echo ------------------------------------
echo        ECLIPSE CLIENT SETUP
echo ------------------------------------
echo.

set "PYTHON_CMD="

where py >nul 2>nul
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
)

if "%PYTHON_CMD%"=="" (
    where python >nul 2>nul
    if not errorlevel 1 (
        set "PYTHON_CMD=python"
    )
)

if "%PYTHON_CMD%"=="" (
    echo Python wurde nicht gefunden.
    echo.
    where winget >nul 2>nul
    if not errorlevel 1 (
        echo Installiere Python mit winget...
        winget install --id Python.Python.3.12 -e
        set "PYTHON_CMD=py -3"
    ) else (
        echo winget wurde nicht gefunden.
        echo Bitte Python 3.12 installieren und danach diese Datei nochmal starten:
        echo https://www.python.org/downloads/
        start "" "https://www.python.org/downloads/"
        echo.
        pause
        exit /b 1
    )
)

echo.
echo Aktualisiere pip...
%PYTHON_CMD% -m pip install --upgrade pip
if errorlevel 1 (
    echo.
    echo pip konnte nicht aktualisiert werden.
    pause
    exit /b 1
)

echo.
echo Installiere Bibliotheken...
%PYTHON_CMD% -m pip install -r lib\applicationresources\requirements.txt
if errorlevel 1 (
    echo.
    echo Installation der Bibliotheken fehlgeschlagen.
    pause
    exit /b 1
)

echo.
echo Setup abgeschlossen.
echo Du kannst den Launcher jetzt ueber "lib\applicationresources\Eclipse Client.vbs" starten.
echo.
pause
