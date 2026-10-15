# ADR-0021 - Regressao do pin das imagens de conteiner (10/09 a 14/10/2026)

## Contexto
Em 31/08/2026 (commit `48b2206`) as quatro imagens de servico de terceiros - n8n,
Qdrant, Presidio analyzer e Presidio anonymizer - foram fixadas por digest no
`docker-compose.yml`, e os digests registrados em `docs/versoes.md`.

Em 10/09/2026 o commit `ce29a76` ("Correcoes de revisao externa") voltou as quatro para
a tag `:latest` e restaurou o comentario de cabecalho que dizia que as tags ficariam em
`latest` "apenas ate a tarefa 0.10". O mesmo commit publicou as portas em `127.0.0.1`.
O diff mostra a causa: as correcoes foram aplicadas sobre uma copia do arquivo anterior
a 31/08, que sobrescreveu o pin. A ADR-0010, que descreve o `ce29a76`, nao menciona a
mudanca: ela nao foi decidida, aconteceu.

Desde entao, tres registros afirmavam algo que deixara de ser verdade:
`docs/versoes.md` ("todas fixadas por digest em `docker-compose.yml`"), a mensagem do
commit da Etapa 2 (`1f5783c`, "sete servicos fixados por digest") e o comentario do
proprio compose. Encontrado em 14/10/2026, ao preparar o RQ-11.

## Medicao
Na maquina do experimento, em 14/10/2026, `docker image inspect` sobre as quatro
imagens `:latest` instaladas:

| Imagem | Digest instalado | Digest registrado em 31/08 |
|---|---|---|
| n8n | `a9e2e3c8...4c93d` | igual |
| Qdrant | `057ee3a8...0d1fc` | igual |
| Presidio analyzer | `ae8f6f11...69885` | igual |
| Presidio anonymizer | `e5670138...365c1` | igual |

As imagens instaladas sao as registradas: nenhuma foi baixada de novo depois de 31/08.
**A regressao existiu no arquivo e nao teve efeito sobre as imagens usadas.** A evidencia
da Etapa 2 e a verificacao do Qdrant real de 14/10/2026 (ADR-0014) foram produzidas com
as imagens registradas.

## Decisao
- Os quatro digests sao restaurados no `docker-compose.yml`, com o comentario de
  cabecalho de 31/08, acrescido da referencia a este ADR.
- `scripts/tests/test_imagens_fixadas.py` passa a falhar se qualquer imagem do compose ou
  dos `Dockerfile` usar tag em vez de digest, ou usar digest que nao esteja registrado em
  `docs/versoes.md`.
- O historico nao e reescrito: o `ce29a76` e a mensagem do `1f5783c` permanecem, com este
  ADR apontando para eles.

## Alternativa considerada
Registrar as imagens atuais como nova versao, sem restaurar o pin de 31/08. Descartada
por nao haver diferenca a registrar: os digests sao os mesmos, e restaurar o arquivo
devolve exatamente o estado declarado.

## Consequencia
O ambiente volta a ser o descrito em `docs/versoes.md`, agora com teste que o garante.
Quarta ocorrencia, neste projeto, do padrao de registro que afirma o que deixou de ser
verdade por um passo que falhou sem aviso (ADR-0017, exame de 07/10/2026). Ao contrario
das anteriores, esta foi encontrada por leitura do codigo, e nao por um resultado
estranho; o teste novo existe para que a proxima seja encontrada pela suite.

## Data
2026-10-14
