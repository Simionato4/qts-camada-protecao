@echo off
chcp 65001 >nul
title Teste 1 - pytest ANTES da correcao (75c5da6)
set PYTHONDONTWRITEBYTECODE=1
cd /d "%~dp0..\..\..\..\QTS-trabalho-b2-antes"
echo Teste 1 na versao ANTES da correcao (esperado: 2 falhas no teto 0)
echo Versao: & git log --oneline -1
echo.
"%~dp0..\..\..\.venv\Scripts\python.exe" -m pytest qts\testes -v -p no:cacheprovider
echo.
pause
