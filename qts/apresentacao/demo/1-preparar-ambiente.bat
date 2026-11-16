@echo off
chcp 65001 >nul
mkdir "%~dp0saida" 2>nul
if not "%~1"=="_log" (
  echo Preparando o ambiente... isso pode levar alguns minutos.
  call "%~f0" _log > "%~dp0saida\preparar-log.txt" 2>&1
  type "%~dp0saida\preparar-log.txt"
  echo.
  echo Pronto. Pode fechar esta janela.
  pause
  exit /b
)
cd /d "%~dp0..\..\.."
echo Pasta: %CD%
echo Data: %DATE% %TIME%
set PY=
for %%v in (3.12 3.13 3.11 3.10) do (
  if not defined PY ( py -%%v -c "import sys" >nul 2>&1 && set "PY=py -%%v" )
)
if not defined PY (
  echo ERRO: nenhum Python entre 3.10 e 3.13 encontrado pelo comando py.
  py -0p
  exit /b 1
)
echo Python escolhido: %PY%
%PY% --version
if not exist .venv\Scripts\python.exe %PY% -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r camada\requirements.txt pytest==8.3.4
set PYTHONDONTWRITEBYTECODE=1
echo.
echo ===== Teste 1 (versao corrigida) =====
.venv\Scripts\python.exe -m pytest qts\testes -q -p no:cacheprovider
echo exit code: %ERRORLEVEL%
echo.
echo ===== Copia da versao antes da correcao (75c5da6) =====
if not exist "..\QTS-trabalho-b2-antes\qts\testes" git worktree add --detach "..\QTS-trabalho-b2-antes" 75c5da6
cd /d "..\QTS-trabalho-b2-antes"
git log --oneline -1
"%~dp0..\..\..\.venv\Scripts\python.exe" -m pytest qts\testes -q -p no:cacheprovider
echo exit code: %ERRORLEVEL%
echo FIM
