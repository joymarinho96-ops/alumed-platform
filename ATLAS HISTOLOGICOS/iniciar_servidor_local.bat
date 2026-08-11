@echo off
title ALUMED | ATLAS HISTOLOGICO - PROFE JOYCE MARINHO
echo ========================================================
echo   ALUMED | ATLAS HISTOLOGICO - PROFE JOYCE MARINHO
echo ========================================================
echo.
echo Servidor Local HTTP iniciado: http://localhost:8080
echo.
python -m http.server 8080 --directory "%~dp0"
pause
