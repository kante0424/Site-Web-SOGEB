@echo off
rem Lance le site SOGEB sur ce poste. Double-cliquer sur ce fichier, puis laisser la fenetre ouverte.
cd /d "%~dp0"
title Site SOGEB - serveur de developpement

set PY=
python --version >nul 2>nul && set PY=python
if not defined PY py -3 --version >nul 2>nul && set PY=py -3
if not defined PY (
  echo.
  echo  Python n'est pas installe sur ce poste.
  echo  1. Telecharger Python 3.12 sur https://www.python.org/downloads/
  echo  2. A l'installation, cocher "Add python.exe to PATH"
  echo  3. Relancer ce fichier
  echo.
  start "" https://www.python.org/downloads/
  pause
  exit /b 1
)

if not exist .venv (
  echo Premiere installation : creation de l'environnement Python...
  %PY% -m venv .venv || goto erreur
)
call .venv\Scripts\activate.bat

echo Installation des bibliotheques (quelques minutes la premiere fois)...
python -m pip install -q -r requirements.txt || goto erreur

echo Preparation de la base de donnees...
python manage.py migrate --noinput -v 0 || goto erreur
if exist .site_initialise python manage.py completer_sogeb || goto erreur
if not exist .site_initialise (
  python manage.py initialiser_sogeb || goto erreur
  echo ok> .site_initialise
  echo.
  echo  Creation de votre compte administrateur :
  python manage.py createsuperuser || goto erreur
)

echo.
echo  ============================================================
echo   Le site est demarre :      http://127.0.0.1:8000
echo   Administration :           http://127.0.0.1:8000/gestion/
echo   Laissez cette fenetre ouverte. La fermer arrete le site.
echo  ============================================================
echo.
rem Ouvre le navigateur quelques secondes apres le demarrage du serveur
start "" /b cmd /c "timeout /t 5 /nobreak >nul & start "" http://127.0.0.1:8000/"
python manage.py runserver 127.0.0.1:8000
pause
exit /b 0

:erreur
echo.
echo  Une erreur s'est produite. Faites une capture de cette fenetre et envoyez-la.
pause
exit /b 1
