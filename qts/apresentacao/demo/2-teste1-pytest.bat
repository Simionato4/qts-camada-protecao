@echo off
chcp 65001 >nul
title Teste 1 - pytest (versao corrigida)
cd /d "%~dp0..\..\.."
set PYTHONDONTWRITEBYTECODE=1
echo Teste 1: valores limite e particionamento da guarda de orcamento
echo Versao: & git log --oneline -1
echo.
.venv\Scripts\python.exe -m pytest qts\testes -v -p no:cacheprovider
echo.
pause
