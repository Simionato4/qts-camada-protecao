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
(preenchido na Etapa 5: correcao e nova execucao)
