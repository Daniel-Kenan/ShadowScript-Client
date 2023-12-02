@ECHO OFF

:retry
python client.py --url shadowscript-production.up.railway.app --room room1 --retry-interval 10 --debug

if errorlevel 1 (
    echo Python script failed. Retrying in 60 seconds...
    timeout /nobreak /t 60 >nul
    goto retry
)

echo Script completed successfully.
