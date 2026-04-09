@echo off
REM Start User Application on Port 5000
echo.
echo ============================================================
echo Starting EnergyTrack USER APPLICATION
echo ============================================================
echo.
echo This runs on: http://localhost:5000
echo For clients on WiFi, use: http://[YOUR_IP]:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python app.py

pause
