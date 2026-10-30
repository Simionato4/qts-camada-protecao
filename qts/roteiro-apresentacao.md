# Roteiro da apresentacao (16/11)

Ordem sugerida: sistema e regra, qualidade, Teste 1, falha e correcao, Teste 2, fechamento.
Cada integrante explica a propria parte e os conceitos que usou.

## Antes de comecar (preparo)
- Ter clonado o repositorio e criado o `.venv` (README, passos 1 e 2) no notebook da apresentacao.
- Testar no Windows, antes do dia, os passos 3 e 4 do README (pytest e camada + Postman).
- Abas abertas: repositorio no GitHub, execucoes 1 e 2 do Actions, Postman com a colecao importada.
- Plano B se a rede ou o notebook falharem: prints e relatorios em `qts/evidencias/2026-10-29/`.

## 1. Gabriel: sistema, parte escolhida e qualidade (PDCA)
- Sistema: camada intermediaria entre usuario e LLM (TCC). Versao `da7c66a`: so encaminha, sem regras.
- Parte e regra: guarda de orcamento (`executor/orcamento.py`). Recusa antes da chamada se
  consumo + US$ 0,0025 > US$ 16,00 ou se chamadas >= 4.500. Tetos informados substituem os padroes.
- Isolamento: trabalho numa copia em repositorio proprio; o TCC nao mudou (linha de base registrada).
- Niveis do Modelo V: guarda = componente; `/entrada` com a camada rodando = sistema.
- Qualidade: no TCC os testes so rodam manualmente. Fluxo do GitHub Actions roda tudo a cada push.
  - Plan: o que o fluxo verifica (suite do TCC sem `lento` + `qts/testes`, relatorio como artefato).
  - Do: execucao 1, vermelha.
  - Check: relatorio mostra 226 ok no TCC e 2 falhas no QTS (teto 0).
  - Act: correcao + execucao 2, verde, mesmo sistema (ubuntu-24.04).
- Mostrar: arquivo do fluxo, execucao 1 x execucao 2, artefato baixado.
- Conceitos: garantia da qualidade, PDCA, automacao de verificacao, regressao. Teste dinamico x estatico:
  o fluxo executa testes (dinamico); ESLint/SonarQube seriam analise estatica, que nao fizemos.

## 2. Jhonatan: Teste 1, valores limite (pytest)
- Por que pytest: equivalente a Vitest/Jest/JUnit para Python (aceito pelo professor).
- Fronteira em dolares: 15,9975 + 0,0025 = 16,0000 (nao passa do teto: aceita);
  15,9976 + 0,0025 = 16,0001 (passa: recusa). Teste auxiliar prova que a soma e exata no Python.
- Fronteira de chamadas: 4.499 feitas (aceita), 4.500 (recusa).
- Limite da configuracao: teto informado 0 deve recusar tudo.
- Preparacao: consumo gravado em pasta temporaria, `simulado=True`, variaveis de ambiente limpas.
- Demonstrar: `python -m pytest qts/testes -v` (execucao dinamica automatizada, compara sozinho).
- Conceitos: analise de valores limite (ISTQB 4.2.2), teste de componente.

## 3. Henrique: Teste 1, particionamento de equivalencia e investigacao da falha
- Particoes: dentro dos dois tetos (aceita), acima do teto em dolares (recusa), acima do teto
  de chamadas (recusa), teto informado na configuracao (substitui o padrao). Um representativo de cada.
- Falha: teto 0 (dolares e chamadas, separados) foi aceito: `DID NOT RAISE`.
- Causa: `teto_usd or padrao` trata 0 como falso e usa 16,00 / 4.500.
- Correcao minima: `teto_usd if teto_usd is not None else padrao`, so na copia.
- Mostrar: 1a execucao (11 ok, 2 falhas) e 2a (13 ok); `investigacao-defeito-teto-zero.md`.
- Achado fora do escopo: o mesmo padrao em precos e custo estimado, registrado e nao corrigido.
- Conceitos: particionamento de equivalencia (ISTQB 4.2.1), defeito x falha, depuracao, reteste.

## 4. Thiago: Teste 2, teste funcional do /entrada (Postman)
- Subir so a camada com uvicorn na porta 8010 (sem Docker, sem modelo, sem n8n), log desviado.
- Colecao com 3 requisicoes e scripts `pm.test` que conferem sozinhos:
  mensagem comum e com CPF: 200, `encaminhar`, texto identico, `versao_regras` presente;
  `ponto` invalido: 422.
- Demonstrar no Postman: Collection Runner com 10 testes passando.
- Explicar: o CPF passa sem mascara porque esta versao ainda nao tem regras; e o esperado aqui.
- Conceitos: teste funcional de caixa-preta, teste de sistema, esperado x observado.

## 5. Rooch: Teste 2 como regressao automatizada (Newman)
- Newman e a linha de comando do Postman: roda a mesma colecao sem interface e gera relatorio JUnit/JSON.
- Mostrar: `newman-execucao-1.txt` (3 requisicoes, 10 assercoes, 0 falhas) e o log da camada,
  que guarda so tamanho e resumo do texto (o CPF nao aparece).
- Regressao: quando as regras de deteccao existirem, a mesma colecao mostra o que mudou no `/entrada`.
- Conceitos: teste de regressao, automacao, rastreabilidade do registro (`versao_regras`).

## 6. Fechamento (Gabriel ou quem o grupo escolher)
- Esperado x observado dos dois testes; falha encontrada, corrigida e reexecutada.
- O que ficou fora: regras de deteccao, `/contexto` e `/saida`, recuperador, modelo, n8n, Docker,
  desempenho, valores alem dos testados.
- Como outra pessoa repete: `qts/README.md`.
