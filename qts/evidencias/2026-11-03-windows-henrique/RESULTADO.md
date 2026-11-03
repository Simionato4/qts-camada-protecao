# Validação no Windows - Henrique Granel - 2026-11-03

Execução conduzida com assistente de IA (Claude Code), seguindo `qts/instrucoes-validacao-windows.md`
(versão do commit `b2ca4e5`). A parte gráfica do Postman (Import, Runner, prints) foi feita por mim.

- Commit testado: `b2ca4e5295825deb2b32a39ffd84de30a9d7ca16` (branch `qts-trabalho-b2`; contém `da7c66a` e a
  correção `2a54e8b`, sem mudança em `executor/orcamento.py` depois dela)
- Windows 11 Pro (10.0.26200) / PowerShell 5.1.26100.9711 / Python 3.12.10 / pytest 8.3.4 / Postman 12.35.1
  (detalhes em `ambiente.txt` e `pip-freeze.txt`)
- Teste 1 (pytest): esperado 13 passed | observado: **13 passed, exit code 0** (`pytest-saida.txt`, `pytest.xml`)
- Teste 1 antes da correção (`75c5da6`, opcional): esperado 2 failed, 11 passed | observado: **2 failed, 11 passed,
  exit code 1**, os dois casos de teto informado 0 com `DID NOT RAISE OrcamentoExcedido`
  (`pytest-antes-da-correcao.txt`, `pytest-antes-da-correcao.xml`)
- `/saude`: esperado `{"estado":"ok","versao_regras":"0.0.0-encaminhamento"}` | observado: idêntico
- Teste 2 (Postman, Collection Runner): esperado 3 requisições, 10 testes, 0 falhas | observado: **3 requisições,
  10 testes PASS, 0 falhas** (`postman-runner.png`)

  | Requisição | Esperado | Observado |
  |---|---|---|
  | 01 mensagem comum | 200, decisao = encaminhar, texto idêntico, versao_regras presente | 200, 4/4 PASS |
  | 02 mensagem com CPF | os mesmos 4 testes (sem máscara nesta versão) | 200, 4/4 PASS |
  | 03 ponto inválido | 422 e erro apontando o campo ponto | 422, 2/2 PASS |

  Requisição 02 reenviada sozinha (Send) para o print da aba Test Results: 200 OK, 4/4 PASSED
  (`postman-requisicao-02.png`).
- Saída do servidor (`uvicorn-saida.txt`): `Uvicorn running`, `GET /saude 200`, três `POST /entrada 200`
  (01 e 02 do Runner e o reenvio da 02), um `POST /entrada 422` e o encerramento limpo pelo Ctrl+C
  (`Shutting down` ... `Finished server process`). As linhas JSON do log da camada também aparecem nessa saída.
- Log da camada: esperado 2 eventos sem o texto | observado: **3 eventos**, `decisao` = encaminhar, só tamanho e
  resumo SHA-256, nenhum texto e nenhum CPF (`camada-qts.jsonl`). O terceiro evento é o reenvio manual da
  requisição 02 para o print (mesmo resumo `32c967d9fcf4b816` e tamanho 51 do evento da 02 no Runner). O caso 03
  não gerou evento, como esperado (barrado pela validação).
- Diferenças em relação ao README ou problemas encontrados:
  1. **Python 3.14 não funciona.** O `qts/README.md` (seção 2) usa `python -m venv .venv`, e as instruções pedem
     "Python 3.10 ou mais novo". Nesta máquina o `python` do PATH era o 3.14.5, e o `pip install` falha com
     `No matching distribution found for pydantic-core==2.27.2` (o `pydantic==2.10.4` fixado exige
     `pydantic-core` 2.27.2, sem pacote pronto para 3.14). Saída completa em `python314-pip-erro.txt`.
     O que fiz: instalei o Python 3.12.10 (winget, `Python.Python.3.12`) e criei o ambiente com
     `py -3.12 -m venv .venv`; daí em diante tudo seguiu o README. Sugestão: trocar "3.10 ou mais novo" por um
     intervalo fechado (3.12 funcionou aqui, 3.14 falhou; 3.13 não testei) e usar `py -3.12 -m venv .venv` no
     comando do Windows.
  2. O `/saude` foi conferido com `curl.exe` no PowerShell, não no navegador. Mesma resposta esperada.
  3. A camada foi iniciada com os mesmos comandos do item 1 da Etapa 5A, salvos num script `.ps1` e rodados
     numa aba de terminal separada. Parada com Ctrl+C.
  4. Não salvei o `postman-runner-resultado.json` (Export Results).
  5. No `postman-requisicao-02.png` recortei a barra lateral, que mostrava coleções minhas de outros projetos;
     o print mantém o caminho da coleção QTS, a URL, o 200 OK e a aba Test Results.
- Arquivos desta pasta: `RESULTADO.md`, `ambiente.txt`, `pip-freeze.txt`, `python314-pip-erro.txt`,
  `pytest-saida.txt`, `pytest.xml`, `pytest-antes-da-correcao.txt`, `pytest-antes-da-correcao.xml`,
  `uvicorn-saida.txt`, `camada-qts.jsonl`, `postman-runner.png`, `postman-requisicao-02.png`
