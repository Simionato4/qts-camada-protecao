# Trabalho de QTS (2o bimestre): guarda de orcamento da camada de protecao

Copia isolada do TCC "camada intermediaria de protecao para chatbot com LLM", fixada no
commit `da7c66a`, branch `qts-trabalho-b2`. Repositorio do trabalho:
https://github.com/Simionato4/qts-camada-protecao . O repositorio do TCC nao recebe nada deste trabalho.

Grupo: Gabriel Simionato, Thiago Lanzarin, Henrique Granel, Jhonatan Negri e Rooch Vertus.

## O que tem aqui
| Arquivo | Conteudo |
|---|---|
| `ficha-proposta-qts.docx` | Ficha do professor preenchida |
| `qualidade-pdca.md` | Parte de qualidade: GitHub Actions aplicando PDCA |
| `testes/test_guarda_orcamento_qts.py` | Teste 1 (pytest): valores limite e particionamento |
| `postman/qts-entrada.postman_collection.json` | Teste 2 (Postman): colecao do `/entrada` |
| `postman/teste2-esperado-observado.md` | Esperado x observado do Teste 2 |
| `investigacao-defeito-teto-zero.md` | Falha, causa, correcao, antes e depois |
| `roteiro-apresentacao.md` | Roteiro de 16/11 por integrante |
| `instrucoes-validacao-windows.md` | Prompt para Thiago e Rooch repetirem os testes no Windows e abrirem pull request |
| `evidencias/2026-10-29/` | Saidas reais, relatorios JUnit, artefatos do Actions, prints, log da camada |
| `../.github/workflows/qts-testes.yml` | Fluxo do GitHub Actions |

## Versao e condicoes das execucoes registradas
- Codigo: `da7c66a` + correcao em `executor/orcamento.py` (commit `2a54e8b`). A 1a execucao
  do pytest e a execucao 1 do Actions sao anteriores a correcao.
- Local: VM Ubuntu 22.04.5 ligada ao Windows, Python 3.10.12, pytest 8.3.4, Newman 6.2.3.
- GitHub Actions: ubuntu-24.04, Python 3.10.22, pytest 8.3.4.
- Nenhuma chamada a API do modelo. Nada gravado em `resultados/`. Docker nao e usado.

## Como repetir

### 1. Obter o codigo
```bash
git clone https://github.com/Simionato4/qts-camada-protecao.git
cd qts-camada-protecao
git checkout qts-trabalho-b2
```
Para ver o defeito antes da correcao, use `git checkout 75c5da6` (testes ja existem, correcao nao).

### 2. Ambiente Python (3.10) e dependencias minimas
Linux / macOS:
```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r camada/requirements.txt pytest==8.3.4
```
Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r camada\requirements.txt pytest==8.3.4
```
`.venv/` ja esta no `.gitignore`. Para a suite completa do TCC, instale `requirements-dev.txt`
(e o que o GitHub Actions faz).

### 3. Teste 1: pytest (componente)
```bash
.venv/bin/python -m pytest qts/testes -v -p no:cacheprovider --junitxml=qts/evidencias/<data>/pytest.xml
```
Windows: troque `.venv/bin/python` por `.\.venv\Scripts\python.exe`.
Esperado na branch `qts-trabalho-b2`: `13 passed`. No commit `75c5da6`: `2 failed, 11 passed`.

### 4. Teste 2: Postman (sistema)
Suba so a camada, com o log desviado para `qts/` (sem `ARQUIVO_LOG` ela grava em `resultados/`):
```bash
ARQUIVO_LOG=qts/evidencias/<data>/camada-qts.jsonl .venv/bin/python -m uvicorn camada.app.main:app --port 8010
```
Windows (PowerShell):
```powershell
$env:ARQUIVO_LOG = "qts\evidencias\<data>\camada-qts.jsonl"
.\.venv\Scripts\python.exe -m uvicorn camada.app.main:app --port 8010
```
Confira em http://127.0.0.1:8010/saude (deve responder `{"estado":"ok",...}`).

Com a camada no ar, em outro terminal ou no Postman:
- **Postman (interface):** Import > arquivo `qts/postman/qts-entrada.postman_collection.json` >
  na colecao, Run (Collection Runner) > Run. Esperado: 10 testes passam.
- **Newman (linha de comando, precisa de Node.js):**
```bash
npx newman@6 run qts/postman/qts-entrada.postman_collection.json --reporters cli,junit --reporter-junit-export qts/evidencias/<data>/newman.xml
```
Esperado: 3 requisicoes, 10 assercoes, 0 falhas. Encerre a camada com Ctrl+C.

### 5. Qualidade: GitHub Actions
Todo push na branch dispara `.github/workflows/qts-testes.yml`. Resultado em
https://github.com/Simionato4/qts-camada-protecao/actions ; o relatorio fica no artefato
`relatorio-testes-<numero>` de cada execucao. Commits com `[skip ci]` na mensagem nao disparam.

## O que ficou fora
Regras de deteccao da camada (ainda nao existem nesta versao), `/contexto` e `/saida`,
recuperador, modelo, n8n, Docker, desempenho, valores alem dos testados e o mesmo padrao
`x or padrao` em precos e custo estimado (registrado em `investigacao-defeito-teto-zero.md`).
