@echo off
echo ============================================================
echo  COMIC GENERATOR - Custom Topic Run
echo ============================================================
echo.

if "%~1"=="" (
    set /p TOPIC="Enter your comic topic: "
) else (
    set TOPIC=%~1
)

echo.
echo Topic: %TOPIC%
echo.

cd /d "%~dp0backend"
set PYTHONUNBUFFERED=1
uv run python -u tests\test_full_run.py "%TOPIC%"
pause
