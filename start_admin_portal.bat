@echo off
REM Start Admin Portal on Port 5001
echo.
echo ============================================================
echo Starting EnergyTrack ADMIN PORTAL
echo ============================================================
echo.
echo This runs on: http://localhost:5001
echo Admin-only access - Separate from user application
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

python admin_app.py

pause
