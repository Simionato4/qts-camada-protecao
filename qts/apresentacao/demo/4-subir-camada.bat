@echo off
chcp 65001 >nul
title Camada no ar - porta 8010 (feche com Ctrl+C)
cd /d "%~dp0..\..\.."
set ARQUIVO_LOG=qts\apresentacao\demo\saida\camada-demo.jsonl
set PYTHONUNBUFFERED=1
set PYTHONDONTWRITEBYTECODE=1
echo Camada subindo em http://127.0.0.1:8010  (teste: http://127.0.0.1:8010/saude)
echo Log da camada: %ARQUIVO_LOG%
echo Para encerrar: Ctrl+C
echo.
.venv\Scripts\python.exe -m uvicorn camada.app.main:app --port 8010
pause
