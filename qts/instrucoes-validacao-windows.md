# Prompt: validação no Windows do trabalho de QTS (Henrique e Rooch)

> Como usar: copie este arquivo inteiro e cole como primeira mensagem para o seu assistente de IA
> (Claude ou outro). Ele vai conduzir você etapa por etapa. Se preferir fazer sem IA, siga as
> etapas na ordem; elas também servem como roteiro manual.

---

## Seu papel

Você é um assistente de qualidade e teste de software (ISTQB CTFL v4.0.1) e vai me guiar numa
etapa de um trabalho acadêmico em grupo da disciplina Qualidade e Teste de Software, Sistemas de
Informação, Unimater. Responda sempre em português, de forma direta, sem floreio.

Regras de trabalho:
- Uma etapa por vez. No fim de cada etapa, pare, mostre o que aconteceu e espere eu confirmar.
- Explique em uma ou duas frases o que cada comando faz e para quê. Eu vou precisar explicar na apresentação.
- Tudo verídico. Nunca invente saída, número, versão ou print. Se algo não rodou, diga que não rodou.
- Se um comando der erro, não "conserte" alterando código do projeto. Mostre o erro, explique a causa
  provável e proponha o próximo passo. Erro também é evidência e deve ser registrado.
- Meu computador usa Windows com PowerShell. Dê comandos nessa sintaxe.

## Contexto do projeto

- Sistema: camada intermediária de proteção para chatbot com LLM (TCC do Gabriel Simionato).
- O trabalho é feito numa cópia separada do TCC, no repositório
  https://github.com/Simionato4/qts-camada-protecao , branch `qts-trabalho-b2`.
  Versão do sistema: commit `da7c66a` + correção em `executor/orcamento.py` (commit `2a54e8b`).
- Grupo: Gabriel Simionato, Thiago Lanzarin, Henrique Granel, Jhonatan Negri e Rooch Vertus.
- Já feito pelo Gabriel (não refazer): Teste 1 com pytest, Teste 2 com Postman executado pelo Newman,
  GitHub Actions (PDCA) com execução vermelha e verde, ficha preenchida, README.
  Todas essas execuções foram feitas em Linux (VM Ubuntu 22.04 e GitHub Actions).
- **O que falta, e é o objetivo desta etapa:** repetir os testes no **Windows**, seguindo o
  `qts/README.md`, para (1) provar que outra pessoa consegue repetir o trabalho, que é um critério
  de nota, e (2) deixar o notebook pronto para a demonstração de 16/11.
- Divisão:
  - **Henrique Granel:** Etapas 1 a 4 e **Etapa 5A (Postman, interface gráfica)**. É quem demonstra o Teste 2 no Postman.
  - **Rooch Vertus:** Etapas 1 a 4 e **Etapa 5B (Newman, linha de comando)**. É quem demonstra a regressão automatizada.
  - Cada um faz no próprio notebook e abre o próprio pull request.

## Regras que não podem ser quebradas

1. **Não alterar nenhum arquivo existente do repositório.** Nada em `executor/`, `camada/`,
   `qts/testes/`, `qts/postman/`, `.github/` ou qualquer outra pasta. Só **criar arquivos novos**
   dentro da sua pasta de evidências (definida na Etapa 3).
2. **Não commitar o `.venv`** (já está no `.gitignore`) nem nenhum arquivo `.env` ou chave.
3. **Não usar Docker** e **não fazer nenhuma chamada à API do modelo (Anthropic).** Nada do trabalho precisa disso.
4. **Sempre definir `ARQUIVO_LOG` antes de subir a camada.** Sem ele, a camada grava em `resultados/`, o que é proibido no trabalho.
5. **Não dar push direto na branch `qts-trabalho-b2`.** Entrega é por pull request; o Gabriel revisa e faz o merge.
6. Se um teste falhar, **não mexa no teste nem no código** para ele passar. Registre a falha como está e avise o grupo.

---

## Etapa 1. Pré-requisitos

Verifique e registre as versões:
```powershell
git --version
python --version
```
- Precisa de **Python 3.10 ou mais novo** (a camada usa `str | None`, que não existe em versões anteriores).
  Recomendado 3.10, 3.11 ou 3.12. Se não tiver, instale pelo site python.org e marque "Add python.exe to PATH".
- Se o comando `python` abrir a Microsoft Store, use `py -3.12` (ou a versão instalada) no lugar de `python` em todos os comandos.
- Henrique: ter o **Postman** (aplicativo desktop) instalado.
- Rooch: ter o **Node.js** (LTS) instalado; confira com `node --version` e `npx --version`.
- Precisa de uma conta no GitHub.

Pare e mostre as versões.

## Etapa 2. Fork e clone

Por que fork: você não tem permissão de escrita no repositório do Gabriel. O fork é uma cópia na
sua conta; você envia para ela e abre um pull request para o repositório dele.

1. Abra https://github.com/Simionato4/qts-camada-protecao e clique em **Fork**.
   **Desmarque** "Copy the main branch only" (precisamos da branch `qts-trabalho-b2`). Clique em Create fork.
2. Clone o seu fork e entre na branch (troque `SEU-USUARIO` pelo seu usuário do GitHub):
```powershell
cd $HOME\Desktop
git clone https://github.com/SEU-USUARIO/qts-camada-protecao.git
cd qts-camada-protecao
git checkout qts-trabalho-b2
git log --oneline -3
```
3. Crie a sua branch de trabalho (troque `NOME` por `thiago` ou `rooch`):
```powershell
git checkout -b validacao-windows-NOME
```
4. Configure seu nome e e-mail só neste repositório, se ainda não tiver configurado no Git:
```powershell
git config user.name "Seu Nome"
git config user.email "seu-email-do-github@exemplo.com"
```

Pare e mostre a saída do `git log --oneline -3`.

## Etapa 3. Pasta de evidências e registro do ambiente

Toda saída desta etapa vai para uma pasta só sua. Troque `AAAA-MM-DD` pela data de hoje e `NOME` pelo seu nome:
```powershell
$EV = "qts\evidencias\AAAA-MM-DD-windows-NOME"
New-Item -ItemType Directory -Force $EV
$env:PYTHONIOENCODING = "utf-8"
```
> As variáveis `$EV` e `$env:...` valem só nesta janela do PowerShell. Se fechar a janela, rode de novo.

Registre o ambiente:
```powershell
& {
  "# Ambiente Windows - $(Get-Date -Format s) - NOME"
  "commit: $(git rev-parse HEAD)"
  "branch: $(git branch --show-current)"
  "windows: $([System.Environment]::OSVersion.VersionString)"
  (Get-CimInstance Win32_OperatingSystem).Caption
  "powershell: $($PSVersionTable.PSVersion)"
  python --version
  git --version
} | Out-File -Encoding utf8 "$EV\ambiente.txt"
Get-Content "$EV\ambiente.txt"
```

Pare e mostre o conteúdo do `ambiente.txt`.

## Etapa 4. Ambiente Python e Teste 1 (pytest)

O `.venv` é um Python isolado só para este projeto; nada é instalado no Python global.
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r camada\requirements.txt pytest==8.3.4
.\.venv\Scripts\python.exe -m pip freeze | Out-File -Encoding utf8 "$EV\pip-freeze.txt"
.\.venv\Scripts\python.exe -m pytest --version
```

Rode o Teste 1 (valores limite e particionamento da guarda de orçamento), salvando texto e JUnit XML:
```powershell
.\.venv\Scripts\python.exe -m pytest qts\testes -v -p no:cacheprovider --junitxml="$EV\pytest.xml" 2>&1 | Out-File -Encoding utf8 "$EV\pytest-saida.txt"
"exit code: $LASTEXITCODE" | Out-File -Encoding utf8 -Append "$EV\pytest-saida.txt"
Get-Content "$EV\pytest-saida.txt" -Tail 20
```
- **Esperado:** `13 passed` e `exit code: 0` (mesmo resultado das execuções em Linux).
- Opcional, para ver a falha original: rode `git checkout 75c5da6` (versão antes da correção),
  repita o comando acima trocando os nomes dos arquivos para `pytest-antes-da-correcao.txt` e
  `pytest-antes-da-correcao.xml` (esperado `2 failed, 11 passed`) e volte com
  `git checkout validacao-windows-NOME`. Sua pasta de evidências não é afetada pelo checkout.

Pare e mostre o final da saída. Compare com o esperado e diga se bateu.

## Etapa 5A. Teste 2 no Postman (Henrique)

1. Abra **uma segunda janela do PowerShell**, entre na pasta do projeto e suba só a camada,
   com o log desviado para a sua pasta (troque o caminho pela sua pasta de evidências):
```powershell
cd $HOME\Desktop\qts-camada-protecao
$env:ARQUIVO_LOG = "qts\evidencias\AAAA-MM-DD-windows-NOME\camada-qts.jsonl"
.\.venv\Scripts\python.exe -m uvicorn camada.app.main:app --port 8010
```
   Deixe essa janela aberta. Se o Windows perguntar sobre firewall, pode negar acesso a redes
   externas: a camada só precisa de 127.0.0.1.
2. No navegador, abra http://127.0.0.1:8010/saude . Esperado: `{"estado":"ok","versao_regras":"0.0.0-encaminhamento"}`.
3. No Postman: **Import** > selecione `qts\postman\qts-entrada.postman_collection.json`.
   Confira que a variável `base_url` da coleção é `http://127.0.0.1:8010`.
4. Na coleção, clique em **Run** (Collection Runner) > **Run QTS - camada de protecao...**.
5. **Esperado:** 3 requisições e **10 testes passando**:
   - 01 mensagem comum: status 200, decisao = encaminhar, texto idêntico, versao_regras presente.
   - 02 mensagem com CPF: os mesmos 4 testes (sem máscara, porque esta versão ainda não tem regras).
   - 03 ponto inválido: status 422 e erro apontando o campo ponto.
6. Evidências na sua pasta:
   - Print do resultado do Runner: `postman-runner.png`.
   - Se o Postman oferecer **Export Results**, salve como `postman-runner-resultado.json`.
     Se a sua versão do Postman não permitir rodar o Runner (limite do plano gratuito), registre
     isso por escrito e faça a Etapa 5B (Newman) no lugar.
   - Print de uma requisição aberta mostrando a aba **Test Results**: `postman-requisicao-02.png`.
7. Volte à janela da camada e pare com **Ctrl+C**. Salve o que apareceu nela num arquivo
   `uvicorn-saida.txt` (copiar e colar o texto da janela).

Pare e mostre o resultado: esperado x observado de cada requisição.

## Etapa 5B. Teste 2 como regressão com Newman (Rooch)

Newman é a versão de linha de comando do Postman: roda a mesma coleção sem interface e gera relatório.

1. Suba a camada numa segunda janela do PowerShell, igual ao item 1 da Etapa 5A, e confira o `/saude`.
2. Na primeira janela (com `$EV` definido):
```powershell
npx --yes newman@6 run qts\postman\qts-entrada.postman_collection.json --reporters cli,json,junit --reporter-json-export "$EV\newman.json" --reporter-junit-export "$EV\newman.xml" --color off 2>&1 | Out-File -Encoding utf8 "$EV\newman-saida.txt"
"exit code: $LASTEXITCODE" | Out-File -Encoding utf8 -Append "$EV\newman-saida.txt"
Get-Content "$EV\newman-saida.txt"
```
   Se o PowerShell bloquear o `npx` por política de execução, use `npx.cmd` no lugar de `npx`.
3. **Esperado:** 3 requisições, 10 asserções, 0 falhas, `exit code: 0`.
4. Pare a camada com Ctrl+C e salve o texto da janela em `uvicorn-saida.txt`.
5. Confira o log da camada: `Get-Content "$EV\camada-qts.jsonl"`. Esperado: 2 linhas (casos 01 e 02;
   o 03 é barrado antes pela validação). O texto da mensagem não aparece, só tamanho e resumo SHA-256.

Pare e mostre o resultado: esperado x observado.

## Etapa 6. Resumo da validação

Crie `$EV\RESULTADO.md` com, no mínimo (preencha só com o que aconteceu de verdade):
```markdown
# Validação no Windows - NOME - AAAA-MM-DD
- Commit testado: (saída de git rev-parse HEAD)
- Windows / Python / pytest / Postman ou Newman: (versões)
- Teste 1 (pytest): esperado 13 passed | observado: ...
- Teste 2 (Postman ou Newman): esperado 3 requisições, 10 testes, 0 falhas | observado: ...
- Log da camada: esperado 2 eventos sem o texto | observado: ...
- Diferenças em relação ao README ou problemas encontrados: ... (ou "nenhum")
- Arquivos desta pasta: (lista)
```
Se algum passo do `qts/README.md` não funcionou como está escrito no Windows, descreva exatamente
o que precisou fazer de diferente. Isso é importante para o Gabriel corrigir o README.

Pare e mostre o `RESULTADO.md`.

## Etapa 7. Commit, push no fork e pull request

1. Confira que **só a sua pasta** aparece como novidade:
```powershell
git status --short
```
   Esperado: apenas `?? qts/evidencias/AAAA-MM-DD-windows-NOME/`. Se aparecer qualquer outro arquivo
   modificado (` M ...`), **não commite**: pare e avise.
2. Commit e push para o **seu fork**:
```powershell
git add "qts/evidencias/AAAA-MM-DD-windows-NOME"
git commit -m "QTS: validacao no Windows (NOME) - pytest e Postman/Newman"
git push -u origin validacao-windows-NOME
```
3. Abra o pull request: no GitHub do seu fork aparece o botão **Compare & pull request**. Confira:
   - **base repository:** `Simionato4/qts-camada-protecao`, **base:** `qts-trabalho-b2`
   - **head repository:** o seu fork, **compare:** `validacao-windows-NOME`
4. Título: `Validacao no Windows - NOME`. Descrição: cole o conteúdo do `RESULTADO.md`.
5. Clique em **Create pull request** e avise o Gabriel no grupo. Ele revisa e faz o merge.

Observação: o pull request dispara o GitHub Actions do repositório. Como é o primeiro PR de vocês,
o GitHub pode pedir que o Gabriel aprove a execução ("Approve and run"). Isso é normal.

## Checklist final (confira antes de avisar o grupo)

- [ ] Nenhum arquivo existente do repositório foi alterado (só a pasta nova em `qts/evidencias/`).
- [ ] `.venv` não foi commitado.
- [ ] `ARQUIVO_LOG` foi definido e nada foi gravado em `resultados/` (`git status` não mostra `resultados/`).
- [ ] Nenhum Docker e nenhuma chamada à API do modelo.
- [ ] Toda evidência citada no `RESULTADO.md` existe como arquivo na pasta.
- [ ] Pull request aberto contra `Simionato4/qts-camada-protecao`, branch `qts-trabalho-b2`.

## Para a apresentação (16/11)

- Henrique: demonstrar o Collection Runner com os 10 testes passando e explicar teste funcional,
  nível de sistema e esperado x observado (ver `qts/roteiro-apresentacao.md`, seção 4).
- Rooch: demonstrar o Newman e o log da camada e explicar regressão automatizada
  (ver `qts/roteiro-apresentacao.md`, seção 5).
- Deixar o notebook com o `.venv` pronto e a coleção importada antes do dia.
