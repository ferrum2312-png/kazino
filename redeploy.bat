@echo off
setlocal
echo ================================================
echo    KAZINO redeploy (keeps database and balances)
echo ================================================
echo.

echo [1/3] Packing project...
pushd "%~dp0"
tar -czf "%TEMP%\kazino_redeploy.tar.gz" .
popd
if errorlevel 1 (
  echo Packing failed.
  pause
  exit /b 1
)

echo [2/3] Uploading to server...
echo   Type the SERVER PASSWORD when asked (it stays hidden - that is normal).
scp "%TEMP%\kazino_redeploy.tar.gz" root@2.26.125.173:/tmp/kazino_redeploy.tar.gz
if errorlevel 1 (
  echo Upload failed.
  del "%TEMP%\kazino_redeploy.tar.gz" 2>nul
  pause
  exit /b 1
)

echo [3/3] Rebuilding on server (password again)...
ssh root@2.26.125.173 "mkdir -p /opt/kazino && tar -xzf /tmp/kazino_redeploy.tar.gz -C /opt/kazino && rm -f /tmp/kazino_redeploy.tar.gz && cd /opt/kazino && sed -i 's/\r$//' deploy/redeploy.sh && bash deploy/redeploy.sh"

del "%TEMP%\kazino_redeploy.tar.gz" 2>nul
echo.
echo ================================================
echo    Finished. Reopen the Mini App in Telegram.
echo ================================================
pause
