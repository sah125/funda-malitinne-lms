@echo off
REM ==========================================================================
REM  Malitinne: update the live website on the VPS in one go.
REM  Double-click this file (or run it in cmd from the project folder).
REM  You will be asked for: the VPS password (twice) and the
REM  hello@malitinne.co.za mailbox password (typed on the server, hidden).
REM ==========================================================================
setlocal
cd /d "%~dp0"
title Malitinne - deploy to VPS

set "VPS_HOST=102.202.192.45"
set "VPS_USER=root"
echo.
echo  Malitinne deploy to %VPS_HOST%
echo  ------------------------------------------------------------
set /p "VPS_USER=  VPS username [root]: "
set "APP_DIR="
set /p "APP_DIR=  Project folder on the VPS (press Enter to find it automatically): "

where ssh >nul 2>nul || (echo  ssh is not installed. Windows Settings ^> Apps ^> Optional features ^> add "OpenSSH Client". & pause & exit /b 1)
where tar >nul 2>nul || (echo  tar was not found ^(needs Windows 10 or newer^). & pause & exit /b 1)

echo.
echo  [1/3] Packing the upgraded code...
set "PKG=%TEMP%\malitinne_upgrade.tar.gz"
if exist "%PKG%" del "%PKG%"
tar -czf "%PKG%" --exclude=__pycache__ --exclude=*.pyc core lms templates static manage.py requirements.txt gunicorn_config.py deploy
if errorlevel 1 (echo  Packing failed. & pause & exit /b 1)

echo  [2/3] Uploading to %VPS_USER%@%VPS_HOST% ^(enter the VPS password if asked^)...
scp -o ServerAliveInterval=30 "%PKG%" %VPS_USER%@%VPS_HOST%:/tmp/malitinne_upgrade.tar.gz
if errorlevel 1 (echo  Upload failed. Check the username/password and that the VPS is online. & pause & exit /b 1)

echo  [3/3] Updating the server ^(enter the VPS password again if asked^)...
ssh -t -o ServerAliveInterval=30 %VPS_USER%@%VPS_HOST% "rm -rf /tmp/malitinne_upgrade && mkdir -p /tmp/malitinne_upgrade && tar -xzf /tmp/malitinne_upgrade.tar.gz -C /tmp/malitinne_upgrade && sed -i 's/\r$//' /tmp/malitinne_upgrade/deploy/server_update.sh && if [ $(id -u) -eq 0 ]; then APP_DIR='%APP_DIR%' bash /tmp/malitinne_upgrade/deploy/server_update.sh /tmp/malitinne_upgrade; else sudo APP_DIR='%APP_DIR%' bash /tmp/malitinne_upgrade/deploy/server_update.sh /tmp/malitinne_upgrade; fi"
if errorlevel 1 (echo. & echo  The server update reported a problem - read the messages above. & pause & exit /b 1)

del "%PKG%" >nul 2>nul
echo.
echo  Finished. Open https://malitinne.co.za to check the site.
pause
