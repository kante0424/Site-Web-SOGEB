@echo off
rem Ouvre un lien public temporaire vers le site pour une personne a distance.
rem Le lien ne marche que tant que cette fenetre reste ouverte et que le PC est allume.
cd /d "%~dp0"
title Site SOGEB - lien public (tunnel)

if not exist .venv (
  echo Lancez d'abord LANCER_LE_SITE.bat une fois pour installer le site.
  pause
  exit /b 1
)

set CF=
where cloudflared >nul 2>nul && set CF=cloudflared
if not defined CF if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set CF="%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
if not defined CF if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set CF="%ProgramFiles%\cloudflared\cloudflared.exe"
if not defined CF (
  echo Installation de l'outil de tunnel cloudflared (une seule fois^)...
  winget install --id Cloudflare.cloudflared -e --accept-source-agreements --accept-package-agreements
  if exist "%ProgramFiles(x86)%\cloudflared\cloudflared.exe" set CF="%ProgramFiles(x86)%\cloudflared\cloudflared.exe"
  if exist "%ProgramFiles%\cloudflared\cloudflared.exe" set CF="%ProgramFiles%\cloudflared\cloudflared.exe"
)
if not defined CF (
  echo cloudflared est introuvable. Fermez cette fenetre et relancez ce fichier.
  pause
  exit /b 1
)

rem Serveur dedie au tunnel, sans mode debogage, sur le port 8001 (le 8000 reste pour vous).
start "Site SOGEB - serveur du tunnel" /min cmd /c "set SOGEB_TUNNEL=1&& .venv\Scripts\python.exe manage.py runserver 127.0.0.1:8001 --insecure --noreload"
timeout /t 5 /nobreak >nul

echo.
echo  ============================================================
echo   Le lien public s'affiche ci-dessous, sur une ligne
echo   https://....trycloudflare.com  : c'est lui qu'il faut envoyer.
echo   Fermer cette fenetre coupe le lien.
echo  ============================================================
echo.
%CF% tunnel --no-autoupdate --url http://127.0.0.1:8001
pause
