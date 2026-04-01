@echo off
REM Run the HTML Frontend with Flask Backend
REM This script installs dependencies, starts the Flask API, waits until it's ready,
REM then starts a simple HTTP server for the static frontend and opens the browser.

setlocal enableextensions enabledelayedexpansion
echo Starting Smart Recommendation System...
echo.

echo 1. Installing dependencies from requirements.txt (uses current Python)
python -m pip install -q -r "%~dp0\requirements.txt"

echo.
echo 2. Starting Flask API server on port 5000...
echo Please wait for the server to start (will poll /api/stats)...
echo.

REM Start Flask in a new window so logs stay visible
start "Flask API Server" cmd /k "cd /d %~dp0 && python app_api.py"

REM Poll Flask health endpoint until it responds or timeout after 20s
powershell -Command "for($i=0;$i -lt 20;$i++) { try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://localhost:5000/api/stats' -TimeoutSec 2; if($r.StatusCode -eq 200) { exit 0 } } catch { } Start-Sleep -Seconds 1 }; exit 1"
if %ERRORLEVEL% NEQ 0 (
	echo Warning: Flask server did not respond within timeout. You can check the 'Flask API Server' window for errors.
) else (
	echo Flask server is up.
)

echo.
echo 3. Starting HTTP Server for frontend on port 8000...
start "Frontend Server" cmd /k "cd /d %~dp0\frontend && python -m http.server 8000"

REM Wait briefly for frontend server
timeout /t 2 /nobreak >nul

echo.
echo 4. Opening HTML Frontend in default browser...
start "" "http://localhost:8000/index.html"

echo.
echo ✅ System started (or attempted to start). If something failed, check the windows titled 'Flask API Server' and 'Frontend Server'.
echo.
echo 📝 Notes:
echo   - Flask API expected at: http://localhost:5000
echo   - HTML Frontend will open at: http://localhost:8000/index.html
echo   - Use Streamlit demo: run `streamlit run frontend/streamlit_app.py` (optional)
echo.
pause

endlocal
