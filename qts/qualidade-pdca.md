# Qualidade: integracao continua com GitHub Actions aplicando PDCA

Responsavel: Gabriel Simionato. Ferramenta: GitHub Actions.
Fluxo: `.github/workflows/qts-testes.yml`. Repositorio: https://github.com/Simionato4/qts-camada-protecao

## Problema
No TCC os testes so rodam quando alguem executa `pytest` manualmente. Uma regressao
pode entrar no codigo sem que ninguem perceba.

## Plan (o que o fluxo verifica)
- Gatilho: todo push, todo pull request e execucao manual.
- Ambiente: ubuntu-latest, Python 3.10, dependencias de `requirements-dev.txt`.
- Verifica 1: suite do TCC sem os testes `lento` (regressao). Nenhum sobe Docker; o
  unico teste que baixa o modelo de embeddings (`recuperador/tests/test_indice_real.py`)
  e marcado `lento` e fica fora.
- Verifica 2: `qts/testes/` (valores limite e particionamento da guarda de orcamento).
- Registro: saida em texto, JUnit XML e ambiente, guardados como artefato
  `relatorio-testes-<numero>` de cada execucao.
- Criterio: execucao verde = todos os testes passam. Vermelha = ha falha a investigar.

## Do
Execucao no 1, disparada pelo push do commit `75c5da6` em 29/10/2026 (23:28 UTC).
- Link: https://github.com/Simionato4/qts-camada-protecao/actions/runs/40973424872
- Ambiente registrado pelo fluxo: Python 3.10.22, pytest 8.3.4.
- Sistema (lido no log "Set up job"): ubuntu-24.04, imagem 20261025.353.1
  (`actions-execucao-1/runner-image-execucao-1.txt`).
- Resultado: execucao vermelha (failure).
- Artefato `relatorio-testes-1` baixado e extraido em
  `qts/evidencias/2026-10-29/actions-execucao-1/`.

## Check
Lido em `relatorio-testes-1` (tcc-saida.txt, qts-saida.txt, *.xml):
- Testes do TCC: 230 coletados, 4 desmarcados (`lento`), 226 passaram, 0 falharam,
  0 pulados. Confirma que a suite sem `lento` roda sem Docker e sem o modelo de embeddings.
  Um aviso de depreciacao do starlette (anyio.abc.BlockingPortal), sem efeito no resultado.
- Testes QTS: 13 coletados, 11 passaram, 2 falharam:
  `limite_teto_usd_informado_0_recusa` e `limite_teto_chamadas_informado_0_recusa`,
  ambos com `DID NOT RAISE OrcamentoExcedido`. Mesmo resultado da execucao local da Etapa 2.
- Conclusao: o fluxo detectou automaticamente o defeito do teto 0 na guarda de orcamento.
  Investigacao e correcao na Etapa 5 (Act).

## Act
1. Investigacao e correcao minima em `executor/orcamento.py`, so na copia
   (detalhes em `qts/investigacao-defeito-teto-zero.md`): `x or padrao` virou
   `x if x is not None else padrao` em `teto_chamadas` e `teto_usd`.
2. Fluxo fixado em `ubuntu-24.04` (antes `ubuntu-latest`, que esta migrando para Ubuntu 26)
   e passou a registrar o sistema no `ambiente.txt`. A execucao 1 ja tinha rodado em
   ubuntu-24.04, entao entre a 1 e a 2 so o codigo mudou.
3. Nova execucao, no 2, disparada pelo push do commit `2a54e8b` em 29/10/2026:
   - Link: https://github.com/Simionato4/qts-camada-protecao/actions/runs/40987044030
   - Resultado: verde (success). Ubuntu 24.04.5 LTS, imagem 20261026.354.1, Python 3.10.22.
   - Testes do TCC: 226 passaram, 0 falharam, 4 desmarcados (`lento`). Igual a execucao 1:
     a correcao nao quebrou nenhum teste existente (regressao).
   - Testes QTS: 13 passaram, 0 falharam (antes: 11 e 2).
   - Artefato `relatorio-testes-2` em `qts/evidencias/2026-10-29/actions-execucao-2/`
     (SHA-256 do zip conferido com o digest do GitHub: 19e5efe0...54fcdd83).
   - Prints: `print-execucao-2-resumo.jpg` e `print-execucao-2-testes-qts-verde.jpg`.

| Execucao | Commit | Sistema | TCC | QTS | Resultado |
|---|---|---|---|---|---|
| 1 | `75c5da6` (sem correcao) | ubuntu-24.04 | 226 ok | 11 ok, 2 falhas | vermelha |
| 2 | `2a54e8b` (com correcao) | ubuntu-24.04 | 226 ok | 13 ok | verde |

O ciclo pode recomecar: qualquer push futuro roda os mesmos testes e uma regressao do teto 0
volta a deixar o fluxo vermelho.
