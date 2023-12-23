@ECHO OFF
set useServerLocal=true

if "%useServerLocal%"=="true" (
    set "url=localhost:8765"
) else (
    set "url=shadowscript-production.up.railway.app"
)
:retry
python client.py --url %url% --room room1 --retry-interval 10 --debug

if errorlevel 1 (
    echo Python script failed. Retrying in 60 seconds...
    timeout /nobreak /t 60 >nul
    goto retry
)
echo Script completed successfully.
