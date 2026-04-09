@echo off
REM Start BOTH applications simultaneously
echo.
echo ============================================================
echo Starting EnergyTrack - BOTH APPLICATIONS
echo ============================================================
echo.
echo User App:   http://localhost:5000  (Clients)
echo Admin App:  http://localhost:5001  (Admin Only)
echo.
echo Both servers will run in separate windows
echo ============================================================
echo.

start "EnergyTrack - User Application (Port 5000)" cmd /k python app.py
timeout /t 2 /nobreak >nul
start "EnergyTrack - Admin Portal (Port 5001)" cmd /k python admin_app.py

echo.
echo Both applications are now running!
echo Close those windows to stop the servers.
echo.
pause
