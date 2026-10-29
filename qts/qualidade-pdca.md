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
(preenchido com a 1a execucao real)

## Check
(preenchido com o relatorio da 1a execucao)

## Act
(preenchido na Etapa 5: correcao e nova execucao)
