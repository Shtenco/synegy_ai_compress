@echo off
setlocal
cd /d "%~dp0"
if not exist egd256_web_app_v2.py (
  echo ERROR: place the exact egd256_web_app_v2.py beside this file.
  pause
  exit /b 1
)
py -m pip install -r requirements_v4.txt
if errorlevel 1 exit /b 1
py build_exact_v2_graph_ai.py egd256_web_app_v2.py --output egd256_web_app_v5_graph_ai.py
if errorlevel 1 exit /b 1
echo.
echo BUILT: egd256_web_app_v5_graph_ai.py
echo Run it with: py egd256_web_app_v5_graph_ai.py
pause
