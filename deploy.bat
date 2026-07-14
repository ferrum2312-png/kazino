@echo off
setlocal
echo ================================================
echo    KAZINO deploy to titorovka.icu
echo ================================================
echo.
set /p TOKEN=Paste BotFather token and press Enter:
if "%TOKEN%"=="" (
  echo Token is empty - aborting.
  pause
  exit /b 1
)

echo.
echo [1/3] Packing project...
pushd "%~dp0"
tar -czf "%TEMP%\kazino_deploy.tar.gz" .
popd
if errorlevel 1 (
  echo Packing failed.
  pause
  exit /b 1
)

echo [2/3] Uploading to server...
echo   If asked "Are you sure you want to continue connecting" type: yes
echo   Then type the SERVER PASSWORD (it stays hidden - that is normal).
scp "%TEMP%\kazino_deploy.tar.gz" root@2.26.125.173:/tmp/kazino_deploy.tar.gz
if errorlevel 1 (
  echo Upload failed.
  del "%TEMP%\kazino_deploy.tar.gz" 2>nul
  pause
  exit /b 1
)

echo [3/3] Deploying on server (type the password again)...
ssh root@2.26.125.173 "rm -rf /opt/kazino && mkdir -p /opt/kazino && tar -xzf /tmp/kazino_deploy.tar.gz -C /opt/kazino && rm -f /tmp/kazino_deploy.tar.gz && cd /opt/kazino && sed -i 's/\r$//' deploy/update.sh && bash deploy/update.sh '%TOKEN%'"

del "%TEMP%\kazino_deploy.tar.gz" 2>nul
echo.
echo ================================================
echo    Finished. Open the Mini App in Telegram.
echo ================================================
pause
