# Nota de revisão do PR #1 (validação no Windows, Rooch)

Revisão: Gabriel Simionato, 05/11/2026. Merge: commit `88ed8a2`.

## O que foi conferido
- O PR só adiciona arquivos nesta pasta; nenhum arquivo existente do repositório foi alterado.
- pytest: 13 de 13 (texto e `pytest.xml`). Newman: 3 requisições, 10 asserções, 0 falhas
  (texto, `newman.json` e `newman.xml`).
- `camada-qts.jsonl`: 2 eventos, com os mesmos resumos SHA-256 da execução em Linux
  (`bcde70a3d4a51c2f` e `32c967d9fcf4b816`), ou seja, os mesmos textos passaram pela camada.
- `uvicorn-saida.txt`: horários e `id_requisicao` batem com os do `camada-qts.jsonl`; as linhas de
  status batem com os 3 casos (200, 200, 422).
- GitHub Actions do PR (execução 5, commit `6c50358`): verde.

## Histórico das correções
1. `59525d8`: primeira entrega. `uvicorn-saida.txt` continha só comandos do PowerShell; pedido de ajuste
   em comentário no PR.
2. `5c2dc61`: `uvicorn-saida.txt` substituído pela saída real do servidor (copiada do console) e lista de
   arquivos do `RESULTADO.md` completada.
3. `6c50358`: removidas da transcrição 3 linhas de prompt do PowerShell (o `cd` para a pasta e o `notepad`
   usado para salvar). A saída do servidor não foi alterada.

## Observação
`uvicorn-saida.txt` é uma transcrição copiada do console, não uma gravação direta da saída. Para o Henrique,
as instruções passaram a gravar a saída direto em arquivo (`cmd /c ... > uvicorn-saida.txt 2>&1`).
