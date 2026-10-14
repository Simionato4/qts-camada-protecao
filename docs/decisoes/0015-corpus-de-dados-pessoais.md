# ADR-0015 - Corpus de dados pessoais: 350 positivos mais negativos dificeis

## Contexto
A proposta aprovada declara 350 ocorrencias sinteticas de documentos pessoais
brasileiros, usadas para medir precisao e revocacao do mascaramento.

A revisao externa de 10/09/2026 observou que o corpus, como desenhado, so continha
positivos. Sem negativos, **a precisao e quase nao informativa**: um detector que
marcasse toda sequencia numerica obteria revocacao alta e precisao aparentemente boa,
e so os negativos o denunciariam. O requisito ficou registrado como RQ-02.

## Decisao

O corpus tem **duas contagens declaradas**, e nao uma:

| Parte | Papel na metrica |
|---|---|
| **350 ocorrencias validas** | Positivos. Numero preservado da proposta aprovada |
| **Negativos dificeis** | Sequencias que um detector ingenuo marcaria, e que nao sao documento valido |

Preservar o 350 importa: e numero que consta na proposta aprovada, e altera-lo
exigiria declarar mudanca de escopo por uma razao que nao e de escopo.

### Classes de negativo dificil

| Classe | Por que e dificil |
|---|---|
| Digito verificador invalido | Tem o formato exato de um documento, e so a validacao o distingue |
| Sequencia de mesmo comprimento | Codigo de rastreio, numero de nota, identificador interno |
| Formato parcial | Documento truncado ou incompleto |
| Repeticao trivial | Sequencias como onze digitos iguais, que alguns validadores aceitam por engano |
| Numero em contexto nao pessoal | Valor monetario, CEP, data com pontuacao semelhante |

A classe de **digito verificador invalido** e a que mais importa, e e a razao de a
camada usar validacao de digito e nao apenas correspondencia por padrao. Ela mede
exatamente a diferenca entre as duas abordagens comparadas.

### Natureza de cada ocorrencia
Cada item registra `natureza`, distinguindo `pessoa_natural` de `pessoa_juridica`.
CNPJ identifica pessoa juridica e **nao e, por si, dado pessoal de pessoa natural**
(RQ-03): permanece no corpus como identificador estruturado brasileiro, com o recorte
declarado.

### Gabarito
Tipo, valor e **posicoes no texto original**, antes de qualquer normalizacao (RQ-07),
como ja e feito na base de conhecimento. Geracao com semente fixa e reproducao
verificavel por hash.

## Alternativa considerada
Manter 350 no total, com uma fracao de negativos. Descartada porque reduziria os
positivos e alteraria um numero que consta na proposta aprovada, exigindo declaracao
de mudanca por uma razao que nao e de escopo.

## Consequencia
As metricas do eixo de dados pessoais passam a ter significado:

- **revocacao** medida sobre os 350 positivos;
- **precisao** medida sobre positivos e negativos em conjunto, de modo que marcar um
  negativo dificil **custa**;
- **degradacao por classe de negativo** reportavel, o que expoe onde cada abordagem
  falha.

Sem os negativos, a comparacao entre a camada e a ferramenta externa premiaria o
detector mais permissivo. Com eles, a validacao de digito verificador — que e o
mecanismo proprio da camada — pode ser avaliada pelo que ela realmente faz: separar
o que tem formato de documento do que e documento.

O corpus cresce, e com ele o tempo de geracao e de analise. Nao ha custo de credito:
o corpus e avaliado fora do fluxo do assistente (ADR-0003).

## Data
2026-09-11

---

## Revisao de 08/10/2026: tipos de documento, distribuicao e suporte ao CNPJ

### Tipos e distribuicao
A versao final da proposta localizada no Drive do autor (`propostatccgabriel`, 23/08/2026)
declara "350 ocorrencias sinteticas de documentos pessoais brasileiros, geradas com
semente fixa", sem tipos nem distribuicao. O autor nao sabe dizer qual das versoes de
22 e 23/08/2026 foi a submetida; nenhuma das lidas fixa a distribuicao.

O rascunho `metodologiav2.md` (14/08/2026), do proprio autor, fixa **50 ocorrencias para
cada um de 7 tipos**. Decisao do autor, 08/10/2026: **adotar essa distribuicao.** E a
unica escrita pelo autor, e e coerente com a justificativa da proposta final, que cita
como lacuna do Presidio cinco destes tipos.

| Tipo | Positivos | Natureza | Digito verificador |
|---|---:|---|---|
| CPF | 50 | `pessoa_natural` | sim |
| CNPJ | 50 | `pessoa_juridica` (RQ-03) | sim |
| Cartao Nacional de Saude (CNS) | 50 | `pessoa_natural` | sim |
| NIT / PIS | 50 | `pessoa_natural` | sim |
| Titulo de eleitor | 50 | `pessoa_natural` | sim |
| Telefone | 50 | `pessoa_natural` | nao |
| Endereco eletronico | 50 | `pessoa_natural` | nao |
| **Total** | **350** | | |

O RG fica fora, como no rascunho: nao tem digito verificador padronizado nacionalmente.

Duas consequencias para o desenho (tarefa 3.5), ainda abertas:
- telefone e endereco eletronico nao tem digito verificador, e a classe de negativo
  "digito verificador invalido" nao se aplica a eles; precisam de classes proprias;
- o rascunho dizia que todo o corpus seria gerado pelo Faker. Medido na maquina do
  experimento: o Faker 40.38.0 `pt_BR` oferece `cpf`, `cnpj` e `rg`, e nao CNS, PIS ou
  titulo. A `validate-docbr` 2.0.0 tem `generate` para os cinco documentos. A escolha do
  gerador fica para a 3.5, porque gerar e validar com a mesma biblioteca cria
  dependencia entre o gabarito e o detector avaliado.

### RQ-03: suporte ao CNPJ alfanumerico

| Campo | Registro |
|---|---|
| Claim | a `validate-docbr` 2.0.0 valida CNPJ numerico e alfanumerico pela regra publicada pela Receita Federal |
| Fonte 1 | Receita Federal, "Perguntas e respostas: CNPJ alfanumerico", pergunta 14 (calculo do DV) e 15 (validade dos numeros atuais): https://www.gov.br/receitafederal/pt-br/centrais-de-conteudo/publicacoes/perguntas-e-respostas/cnpj/cnpj-alfanumerico.pdf |
| Fonte 2 | pagina da versao no PyPI: https://pypi.org/project/validate-docbr/2.0.0/ (lancada em 04/04/2026; "numerico e alfanumerico"; licenca MIT) |
| Fonte 3 | codigo da versao instalada, na maquina do experimento: conjunto de caracteres `A-Z` mais digitos, valor `ord(caractere) - 48` |
| Data da consulta | 2026-10-08 |
| O que a fonte oficial diz | inicio da atribuicao a partir de julho de 2026 (IN RFB 2.119/2022, alterada pela IN RFB 2.229/2024); cada caractere vale ASCII menos 48; modulo 11 com pesos de 5 a 2 e de 6 a 2; os numeros atuais continuam validos; exemplo `12.ABC.345/01DE-35` |
| Divergencia | **o documento nao diz o que ocorre quando o resto da divisao e 0 ou 1.** Nao se supoe a regra do CNPJ numerico |
| Decisao | suporte verificado por `scripts/tests/test_suporte_cnpj.py`, que implementa a regra publicada e confere a biblioteca contra ela no exemplo oficial, num CNPJ numerico e em 400 bases sorteadas com semente fixa, todas com resto 2 ou maior |
| Pendencia | regra para resto 0 ou 1: conferir no texto da IN RFB 2.229/2024 ou em nota tecnica oficial antes de o corpus incluir CNPJ com esses restos |
| Impacto | RQ-03 (verificacao por teste unitario); desenho dos formatos de CNPJ do corpus (tarefa 3.5) |

## Data da revisao
2026-10-08

---

## Revisao de 08/10/2026 (segundo bloco): gabarito independente da biblioteca

### Decisao (do autor, 08/10/2026)
Opcao A': cada positivo do corpus precisa ser aceito por **duas implementacoes
independentes** do digito verificador: a `validate-docbr` 2.0.0, que a camada usa, e
`scripts/dv_independente.py`, que nao importa a biblioteca e foi escrita a partir das
fontes abaixo. Motivo: gerar e conferir com a mesma biblioteca usada pelo detector
avaliado faria um erro dela entrar no gabarito e no detector ao mesmo tempo.

A opcao A original pedia implementacao "a partir da regra oficial". Para parte dos
documentos a regra oficial completa nao foi localizada; o nivel de cada fonte fica
declarado.

### Fontes por documento

| Documento | Fonte da implementacao independente | Nivel | Consulta |
|---|---|---|---|
| CPF | Receita Federal, Manual de Preenchimento da e-Financeira, Anexo II, `REGRA_VALIDA_CPF` (versao 2.0, dez/2025, p. 34, conforme pesquisa do autor; trecho conferido em captura de tela fornecida pelo autor; o site bloqueia acesso automatizado) | regra oficial | 2026-10-08 |
| CNPJ numerico | mesmo manual, `REGRA_VALIDA_CNPJ` | regra oficial | 2026-10-08 |
| CNPJ alfanumerico | Receita Federal, perguntas e respostas sobre o CNPJ alfanumerico, pergunta 14 | regra oficial, sem tratamento do resto 0 ou 1 | 2026-10-08 |
| PIS/NIT | ANS, "Algoritmos do Aplicativo de Carga", item 7 (`isDvPisPasepValido`), publicado em 06/04/2021: https://www.gov.br/ans/pt-br/centrais-de-conteudo/manuais-do-portal-operadoras/sib-manual-de-instalacao-historico-de-versao-e-outros-arquivos/manual/algoritmos-do-aplicativo-de-carga | documentacao tecnica oficial; a ANS nao e o orgao emissor | 2026-10-08 |
| CNS | ANS, mesma pagina, item 4 (`validaCns`, `validaCnsProv`); separacao por prefixo pela documentacao de integracao do e-SUS APS v2.1.1 | documentacao tecnica oficial | 2026-10-08 |
| Titulo de eleitor | estrutura: Resolucao TSE 23.659/2021, art. 36, paragrafo unico (8 + 2 + 2, modulo 11). Pesos e restos: OBMEP, "A Matematica nos Documentos: Titulo de Eleitor": https://clubes.obmep.org.br/blog/a-matematica-nos-documentos-titulo-de-eleitor/ | estrutura oficial; pesos e restos de fonte academica secundaria | 2026-10-08 |

Os exemplos publicados nas fontes sao reproduzidos pela implementacao independente:
CPF `280012389-38` e CNPJ `18781203/0001-28` (e-Financeira), CNPJ `12.ABC.345/01DE-35`
(Receita Federal) e titulo `1023 8501 06 71` (OBMEP).

**Pendencia do CNPJ reduzida.** A regra numerica da e-Financeira (DV = resto, resto 10
vale 0) e a forma "11 - resto" da pergunta 14 deram o mesmo DV em 20.000 bases numericas
sorteadas: para CNPJ numerico, resto 0 ou 1 resulta em DV 0, por regra oficial. Para
base com letra, a pergunta 14 continua sem tratar esse caso, e `completar_cnpj` devolve
None; o corpus nao gera CNPJ alfanumerico nessa situacao.

**A fonte de uma IA foi descartada.** Uma das pesquisas trazidas ao projeto atribuia a
Resolucao TSE 23.659/2021 os pesos do titulo e uma excecao para SP e MG, e dava regra do
CNS provisorio diferente da ANS. A resolucao foi lida: nao contem pesos, tratamento de
resto nem excecao por UF. Nada dessa pesquisa foi usado.

### Achados sobre a biblioteca

`scripts/tests/test_dv_independente.py` confere as duas implementacoes nos dois
sentidos, com semente fixa: numeros completados aqui sao aceitos pela biblioteca e
recusados com o ultimo digito alterado; numeros gerados pela biblioteca sao aceitos aqui.
CPF, CNPJ (numerico e alfanumerico), PIS/NIT e CNS (definitivo e provisorio) concordam.
O titulo de eleitor tem **duas divergencias**, verificadas no codigo da versao instalada:

1. **A biblioteca nao aplica a excecao de SP (01) e MG (02)** descrita pela OBMEP
   (resto 0 vale 1). Nos casos em que as duas convencoes diferem, a biblioteca aceita o
   numero calculado sem a excecao e recusa o calculado com ela. Medido sobre 10.000
   sequenciais sorteados, **18,7%** dos titulos de SP e MG caem nesse caso. Como a
   excecao so tem fonte secundaria, nao se decide aqui qual convencao esta certa.
2. **`generate()` so sorteia UF de 01 a 18**, embora a tabela do TSE va ate 28. Nao
   afeta a validacao, so a geracao.

Consequencias para o corpus:
- titulos de SP e MG em que as convencoes divergem (`titulo_ambiguo`) **nao entram como
  positivos**: nao tem gabarito inequivoco;
- os titulos do corpus nao sao gerados pela `generate()` da biblioteca, para cobrir as 28
  UFs;
- a divergencia entra nas limitacoes: o detector da camada herda a convencao da
  biblioteca, e titulos reais de SP e MG que sigam a excecao seriam recusados por ele.
  Isso e propriedade do detector avaliado, medida aqui antes do congelamento, e nao
  defeito a corrigir na camada depois de ver resultado.

Os testes caracterizam as duas divergencias de forma explicita; nao as escondem.

## Data da revisao
2026-10-08

---

## Revisao de 14/10/2026: regras dos negativos dificeis e contagem

Decisoes do autor, 14/10/2026. Escritas antes de qualquer geracao (tarefa 3.6).

### Regras que valem para todo o corpus

- **Colisao entre tipos de mesmo comprimento.** CPF e PIS/NIT tem 11 digitos; um numero
  truncado de outro tipo pode cair no mesmo comprimento. Positivo: valido **so** no
  proprio tipo, nas duas implementacoes (`validate-docbr` e `scripts/dv_independente.py`).
  Negativo: invalido em **todos** os tipos do seu comprimento, nas duas implementacoes.
- **Gabarito dos negativos.** Cada negativo registra tipo imitado, posicao no texto
  original e `classe_negativo`. E assim que um falso positivo e localizado e contado.
- **Titulo de eleitor.** Numeros de SP e MG em que as duas convencoes divergem
  (`titulo_ambiguo`) nao entram nem como positivo nem como negativo.

### Classes para os cinco tipos com digito verificador (CPF, CNPJ, CNS, PIS/NIT, titulo)

| Classe | Regra de geracao | Casos por tipo |
|---|---|---:|
| N1 - digito verificador invalido | base valida, com a mascara do tipo, ultimo digito trocado; invalido nas duas implementacoes | 10 |
| N2 - mesmo comprimento, sem mascara | sequencia de digitos do comprimento do tipo, em contexto de outro identificador (protocolo, nota fiscal, pedido), invalida em todos os tipos do comprimento | 10 |
| N3 - formato parcial | documento valido com um digito a menos, com e sem mascara | 10 |
| N4 - repeticao trivial | todos os digitos iguais | 10 |
| N5 - numero em contexto nao pessoal | valor monetario, CEP ou data com pontuacao parecida com a do tipo | 10 |

Na N4 existem exatamente 10 sequencias de digitos iguais por comprimento (0 a 9): a
classe as cobre todas. Parte delas fecha a conta do DV (por exemplo, o CPF de onze
algarismos 1). A recusa de digitos todos iguais esta nas regras RV_01 a RV_03 da
Previdencia ("Regras de Validacao", v1.14), fonte oficial ja citada nesta ADR.

### Classes para telefone e endereco eletronico (sem digito verificador)

| Tipo | Classe | Regra | Casos |
|---|---|---|---:|
| Telefone | T1 - quantidade errada de digitos | DDD seguido de 7 ou de 10 digitos | 25 |
| Telefone | T2 - sequencia que parece telefone | horario, intervalo numerico ou codigo com a mesma pontuacao | 25 |
| Endereco eletronico | E1 - incompleto | sem parte local ou sem dominio | 25 |
| Endereco eletronico | E2 - arroba que nao e endereco | perfil de rede social, nome de arquivo com arroba | 25 |

**Cortadas:**
- **T3 (telefone de servico publico):** exigiria uma lista oficial de numeros; sem fonte,
  nao se inventa. Volta so se houver fonte.
- **E3 (endereco ofuscado legivel, como "nome [arroba] dominio"):** fica **fora do
  corpus**. Correcao de uma proposta anterior desta mesma tarefa, que a classificava como
  negativo: um endereco ofuscado continua identificando a pessoa, e o gabarito puniria
  quem o mascara. Como positivo, ampliaria a normalizacao alem do que a proposta aprovada
  define (conteudo codificado, caracteres invisiveis e separadores entre digitos).
  Registrado como trabalho futuro.

### Contagem

| | Positivos | Negativos | Total |
|---|---:|---:|---:|
| Cinco tipos com DV | 250 | 250 (5 classes x 10 x 5 tipos) | 500 |
| Telefone | 50 | 50 (2 classes x 25) | 100 |
| Endereco eletronico | 50 | 50 (2 classes x 25) | 100 |
| **Corpus** | **350** | **350** | **700** |

Motivo (alternativa de 25 negativos por tipo descartada): com 50 negativos por tipo e
nenhum falso positivo observado, o limite superior do intervalo de 95% fica em cerca de
6% (regra de tres, 3/50); com 25, em cerca de 12%, o que mal separa um detector bom de um
ruim. O custo de API e zero nos dois casos (ADR-0003). O intervalo por classe, com 10 ou
25 casos, e largo e declarado junto de cada resultado (RQ-13); a comparacao principal se
apoia no agregado por tipo.

### Ainda aberto na tarefa 3.5
Formato dos textos (frases-modelo, mascaras, sobreposicao, mais de uma ocorrencia por
texto), geracao de telefone e endereco eletronico sem coincidir com dados reais, e o
tratamento do numero sintetico valido que coincida com documento emitido.

## Data da revisao
2026-10-14
