# Investigacao e correcao: teto informado como 0 e ignorado

Responsavel pela investigacao: Thiago Lanzarin. Correcao aplicada SO na copia do trabalho;
levar ao TCC e decisao do autor, fora deste trabalho.

## Falha observada
- Casos `limite_teto_usd_informado_0_recusa` e `limite_teto_chamadas_informado_0_recusa`
  falharam com `DID NOT RAISE OrcamentoExcedido`: a guarda aceitou a chamada.
- Local (Etapa 2): `qts/evidencias/2026-10-29/etapa2-pytest-1a-execucao.txt`.
- GitHub Actions, execucao no 1: `qts/evidencias/2026-10-29/actions-execucao-1/`.

## Causa
`executor/orcamento.py` (commit `da7c66a`), linhas 69 e 70:
```python
self.teto_chamadas = teto_chamadas or int(os.getenv("TETO_CHAMADAS", "4500"))
self.teto_usd = teto_usd or float(os.getenv("TETO_USD", "16.00"))
```
O `or` devolve o lado direito quando o esquerdo e falso, e em Python `0` e `0.0` sao falsos.
Teto informado como 0 vira o padrao (16.0 e 4500). Confirmado executando
`GuardaOrcamento(teto_usd=0, teto_chamadas=0)`: resultou em `teto_usd = 16.0` e `teto_chamadas = 4500`.

## Correcao (minima, so as duas linhas da regra testada)
```python
self.teto_chamadas = (
    teto_chamadas if teto_chamadas is not None else int(os.getenv("TETO_CHAMADAS", "4500"))
)
self.teto_usd = (
    teto_usd if teto_usd is not None else float(os.getenv("TETO_USD", "16.00"))
)
```
So `None` (nao informado) cai no padrao; 0 passa a ser respeitado.

## Antes x depois (pytest local, qts/testes)
| Execucao | Codigo | Resultado |
|---|---|---|
| 1a (Etapa 2) | `da7c66a` | 11 passaram, 2 falharam (teto 0) |
| 2a (Etapa 5) | `da7c66a` + correcao | 13 passaram, 0 falharam |
Evidencia da 2a: `qts/evidencias/2026-10-29/etapa5-pytest-2a-execucao.txt` e `.xml`.

## Achado fora do escopo (nao corrigido)
As linhas 71 a 79 usam o mesmo padrao `x or padrao` em `preco_entrada_usd_mtok`,
`preco_saida_usd_mtok` e `custo_estimado_chamada`: informar 0 tambem cai no padrao.
Nao faz parte da regra testada e `custo_estimado_chamada=0.0` e usado nos testes do proprio
TCC; alterar mudaria o comportamento que eles exercitam. Fica registrado para decisao no TCC.
