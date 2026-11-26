@echo off
setlocal
if /i "%~1"=="test" (
    python -m unittest discover -s "%~dp0tests" -v
    exit /b
)
python "%~dp0src\main.py" %*
exit /b
