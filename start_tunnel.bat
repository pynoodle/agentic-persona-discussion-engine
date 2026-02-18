@echo off
echo ================================================================================
echo  Cloudflare Tunnel Starting...
echo ================================================================================
echo.
echo  Your PersonaBot app will be accessible via HTTPS
echo  Press Ctrl+C to stop the tunnel
echo.
echo ================================================================================
echo.

cloudflared.exe tunnel --url http://localhost:7886

pause

