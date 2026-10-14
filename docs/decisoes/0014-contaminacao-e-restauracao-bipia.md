# ADR-0014 - Um cenario por carga do BIPIA, com restauracao entre cenarios

## Contexto
O conjunto BIPIA fornece 75 cargas de injecao indireta. A base de conhecimento tem 30
documentos. Pelo ADR-0012, cada carga precisa estar num documento com numero de
pedido proprio, para que a pergunta pareada o recupere por filtro exato.

Com 30 documentos nao ha como acomodar 75 pareamentos distintos ao mesmo tempo.

O BIPIA tambem separa ataques de **texto** e de **codigo**, organizados por tarefa —
Web QA, Email QA, Table QA, Summarization e Code QA.

## Decisao

### Um cenario por carga
Cada uma das 75 cargas define um cenario independente:

1. contamina-se **um** documento da base com a carga;
2. reindexa-se;
3. executa-se a pergunta pareada daquele documento, nas condicoes previstas;
4. **restaura-se a base** ao estado limpo;
5. verifica-se a restauracao pelo hash do estado.

A base permanece com 30 documentos em todos os cenarios, identica a das demais
condicoes. A atribuicao carga-documento e deterministica e registrada no
congelamento.

O procedimento de restauracao ja existe e e o mesmo da indexacao: `python -m
app.indexar` recria a colecao do zero e imprime o hash do estado. Dois caminhos
separados poderiam divergir; um so nao pode. Era para isso que o requisito RQ-18
existia.

### Apenas cargas de texto
As cargas de **codigo** ficam fora. O assistente de referencia atende clientes de
comercio eletronico sobre pedidos: nao executa, nao gera e nao interpreta codigo.
Incluir cargas de codigo mediria um vetor ausente do cenario.

A exclusao e declarada no congelamento com a contagem exata do que entrou e do que
ficou de fora. Se as cargas de texto forem menos de 75, a proposta precisa de nota
corrigindo o numero.

## Alternativas consideradas

**Ampliar a base para um documento por carga.** Evitaria a restauracao, mas alteraria
a base de conhecimento, que e **variavel de controle**: ela precisa ser identica em
todas as condicoes e em todos os cenarios. Uma base de 105 documentos nos casos de
injecao indireta e de 30 nos demais mudaria tambem as caracteristicas da recuperacao,
e a comparacao deixaria de isolar a estrategia de protecao.

**Reduzir a amostra do BIPIA para 30 cargas.** Uma por documento, sem restauracao.
Descartada por descartar 60% do conjunto de injecao indireta sem necessidade: o custo
da alternativa adotada e tempo de reindexacao, e nao credito de API.

## Consequencia
Setenta e cinco ciclos de contaminacao, reindexacao, execucao e restauracao. A
reindexacao de 30 documentos e local e barata; o custo e tempo de execucao, nao
credito.

A verificacao por hash entre cenarios deixa de ser zelo e passa a ser necessaria:
sem ela, uma restauracao que falhasse contaminaria os cenarios seguintes, e o efeito
apareceria como injecao indireta bem-sucedida onde nao houve ataque. O executor
interrompe a execucao se o hash apos a restauracao divergir do hash da base limpa.

## Data
2026-09-11

---

## Revisao de 14/10/2026: protocolo implementado (tarefa 3.7, RQ-18)

### Decisoes do autor, 14/10/2026
- **Posicao da carga:** sempre no fim do documento, apos uma quebra de linha. A posicao
  e a mesma em todos os cenarios e nao e variavel do experimento; testar apenas o fim e
  limitacao declarada. Nao se afirma aqui onde o BIPIA original insere as cargas.
- **Atribuicao:** rodizio. As 75 cargas sao embaralhadas com `SEMENTE_MESTRA` e
  distribuidas em ordem pelos 30 documentos: 15 documentos recebem 3 cargas e 15
  recebem 2.
- **Verificacao da restauracao pelo hash lido do Qdrant.**

### Lacuna corrigida
O RQ-18 pede verificacao "por hash da colecao indexada". O `hash_do_estado`, existente
desde a Etapa 2, resume os **arquivos de origem**. Uma reindexacao que falhasse no meio
deixaria os arquivos limpos e a colecao contaminada, e passaria como restaurada.
`hash_da_colecao` (em `recuperador/app/indice.py`) le de volta os pontos do Qdrant e
aplica a mesma formula. Restauracao verificada passa a ser
`hash_da_colecao(indice) == hash_do_estado(documentos_limpos)`.

### Implementacao
| Arquivo | Papel |
|---|---|
| `recuperador/app/contaminacao.py` | `contaminar`: copia da base com a carga no fim do documento alvo; nao altera a base recebida |
| `recuperador/app/indice.py` | `hash_da_colecao` |
| `scripts/gerar_cenarios_bipia.py` | atribuicao e registro dos 75 cenarios em `conjunto_teste/selecao/bipia_cenarios.json`, sem texto de carga (ADR-0016) |

Cada cenario registra o caso (mesmo identificador do mapeamento de rotulos), o sha256 da
carga, o documento alvo, a pergunta pareada e **o hash esperado do estado contaminado**.
O executor (Etapa 5) confere o hash lido do Qdrant duas vezes por cenario: apos
contaminar (deve ser o esperado) e apos restaurar (deve ser o limpo). Divergencia
interrompe a execucao.

Acrescentar a carga no fim nao desloca nenhuma posicao do gabarito de dados pessoais do
documento: o gabarito continua valido no texto contaminado (verificado por teste).

### Evidencia
`recuperador/tests/test_contaminacao.py`, com Qdrant em memoria e o modelo degenerado da
ADR-0012:

- hash lido da colecao limpa igual ao hash dos arquivos;
- contaminacao altera so o documento alvo e nao altera a base recebida;
- ciclo limpo, contaminado (hash muda e e o esperado), restaurado (hash volta);
- documento contaminado recuperado em primeiro lugar pela pergunta pareada;
- **restauracao que falha no meio e detectada**: com um ponto contaminado reinserido sem
  recriar a colecao, os arquivos continuam com o hash limpo e a colecao nao;
- carga vazia e documento inexistente recusados.

Executados em 14/10/2026 num ambiente independente da maquina do experimento: 7 testes
novos e os 5 de recuperacao pareada, todos aprovados. A execucao que vale como evidencia
e a da maquina do experimento.

O hash do estado limpo calculado pelo gerador de cenarios,
`f118bb5851f1ce54d4053f8ca9b1eac5276cd0ca40bb006062436c343d60baa7`, e o mesmo registrado
em `docs/versoes.md` na Etapa 2: a base nao mudou desde entao.

**RQ-18:** a aceitacao ("procedimento de restauracao scriptado e verificavel por hash da
colecao indexada") tem evidencia nesta secao. A mudanca de estado do requisito e feita
no fechamento da etapa.

## Data da revisao
2026-10-14

---

## Verificacao com o Qdrant e o modelo reais - 14/10/2026

Depois do commit `cb90ad4`, na maquina do experimento, com a imagem do recuperador
reconstruida (`docker compose up -d --build recuperador`):
`docker compose exec recuperador python -m app.indexar`. Saida relevante:

```
hash do estado da base (arquivos): f118bb5851f1ce54d4053f8ca9b1eac5276cd0ca40bb006062436c343d60baa7
hash lido da colecao (Qdrant):     f118bb5851f1ce54d4053f8ca9b1eac5276cd0ca40bb006062436c343d60baa7

recuperacao deterministica: 30/30 no top-3
em primeira posicao:        30/30
```

O hash lido do Qdrant real coincide com o dos arquivos e com o registrado na Etapa 2, e a
recuperacao pareada continua 30/30 em primeira posicao. O aviso do `fastembed` sobre a
agregacao por media apareceu, como esperado: e o registrado na ADR-0011.

Esta execucao verifica o estado limpo no ambiente real. O ciclo de contaminacao e
restauracao foi verificado nos testes com Qdrant em memoria; no ambiente real, ele e
exercitado pelo executor, na Etapa 5, a cada um dos 75 cenarios.

## Data da revisao
2026-10-14
