# Validação no Windows - rooch - 2026-10-30
- Commit testado: 19a0f516bc29c225ef25ad0d01db40d892abe8c2 (branch validacao-windows-rooch, a partir de qts-trabalho-b2)
- Ambiente: Windows 11 Pro (NT 10.0.26200.0) / PowerShell 5.1.26100.9711 / Python 3.13.3 / pytest 8.3.4 / Node v22.20.0 / npx 11.19.0 / Newman 6.2.3 / Git 2.49.0.windows.1
- Teste 1 (pytest): esperado 13 passed | observado: 13 passed in 0.43s, exit code 0
- Teste 2 (Newman): esperado 3 requisições, 10 testes, 0 falhas | observado: 3 requisições, 10 asserções, 0 falhas, exit code 0
- Log da camada: esperado 2 eventos sem o texto | observado: 2 eventos (casos 01 e 02), só tamanho e resumo SHA-256, sem o texto da mensagem. O caso 03 não gerou evento (barrado pela validação, 422).
- Diferenças em relação ao README ou problemas encontrados:
  1. Python 3.13.3 foi usado, versão acima da recomendada (3.10 a 3.12). A instalação das dependências e os testes funcionaram sem erro.
  2. O fork foi criado com o nome regressao-automatizada, então a pasta local é regressao-automatizada e não qts-camada-protecao.
  3. No PowerShell 5.1, o comando do Newman com 2>&1 transformou avisos do npm (npm warn deprecated) em um bloco vermelho NativeCommandError. Não afetou o resultado.
  4. No PowerShell 5.1, o newman-saida.txt ficou com caracteres estranhos no lugar das linhas da tabela e dos checks (problema de codificação ao redirecionar). Os arquivos newman.json e newman.xml não são afetados.
  5. O texto do console do uvicorn tem códigos de cor soltos (como ←[32m) porque o PowerShell 5.1 não os interpreta. Não afeta a execução.
  6. Copiar o texto do console do uvicorn com Get-Clipboard não funcionou de primeira (a área de transferência veio com os próprios comandos). O texto foi salvo pelo Bloco de Notas, mas como a variável $EV não existia na janela nova, o arquivo foi criado fora da pasta de evidências e a primeira versão commitada de uvicorn-saida.txt continha só comandos. Corrigido em um segundo commit, com o arquivo certo.
  7. O campo instante do log da camada está em UTC (2026-10-31T01:33), enquanto o ambiente.txt está em horário local (2026-10-30 22:23). É o mesmo momento, com 3 horas de diferença de fuso.
- Arquivos desta pasta: ambiente.txt, pip-freeze.txt, pytest-saida.txt, pytest.xml, newman-saida.txt, newman.json, newman.xml, camada-qts.jsonl, uvicorn-saida.txt, RESULTADO.md
