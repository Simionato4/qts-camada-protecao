# Teste 2: teste funcional do endpoint /entrada (Postman / Newman)

Responsaveis: Thiago Lanzarin e Rooch Vertus. Nivel do Modelo V: sistema (so a camada,
sem modelo e sem n8n). Tecnica: teste funcional de caixa-preta, com particoes de entrada
(texto comum, texto com dado pessoal, ponto invalido). Reaproveitavel como regressao.

Colecao: `qts/postman/qts-entrada.postman_collection.json` (variavel `base_url` = http://127.0.0.1:8010).
Cada requisicao tem script `pm.test` que compara o observado com o esperado sozinho.

## Condicoes da execucao 1 (29/10/2026, 23:40 UTC)
- Codigo: commit base `da7c66a` (camada sem alteracao), `VERSAO_REGRAS` padrao.
- Camada: `uvicorn camada.app.main:app --port 8010`, Python 3.10.12, VM Ubuntu 22.04.5.
- Log da camada desviado: `ARQUIVO_LOG=qts/evidencias/2026-10-29/postman/camada-qts.jsonl`.
- Executor da colecao: Newman 6.2.3 (linha de comando do Postman).

## Esperado x observado
| Caso | Dado | Esperado | Observado |
|---|---|---|---|
| 01 mensagem comum | `Qual o prazo de entrega do pedido 10482?` | 200, `encaminhar`, texto identico, `versao_regras` presente | 200, `encaminhar`, texto identico, `versao_regras` = `0.0.0-encaminhamento` (4/4 asserções) |
| 02 mensagem com CPF | `Meu CPF e 529.982.247-25 e quero cancelar a compra.` | 200, `encaminhar`, texto identico (sem regra ainda), `versao_regras` presente | igual ao esperado (4/4) |
| 03 ponto invalido | `ponto` = `inexistente` | 422 | 422, `detail` aponta o campo `ponto` (2/2) |

Resultado: 3 requisicoes, 10 asserções, 0 falhas (`exit code: 0`).

Observacao do log: o arquivo `camada-qts.jsonl` registrou 2 eventos (casos 01 e 02; o 03 foi
recusado antes de chegar a camada). O texto nao e gravado, so tamanho e resumo SHA-256,
entao o CPF do caso 02 nao aparece no log.

## Evidencias (`qts/evidencias/2026-10-29/postman/`)
- `newman-execucao-1.txt`: saida completa do Newman.
- `newman-execucao-1.json` e `newman-execucao-1.xml`: relatorios JSON e JUnit.
- `uvicorn-saida.txt`: saida do servidor.
- `camada-qts.jsonl`: log estruturado da camada.
