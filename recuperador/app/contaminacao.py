"""Contaminacao de um documento da base por uma carga do BIPIA (ADR-0014, RQ-18).

Um cenario por carga: contamina-se UM documento, reindexa-se, executa-se a pergunta
pareada, restaura-se a base e confere-se a restauracao pelo hash lido do Qdrant.

Posicao da carga: **sempre no fim do documento**, separada por uma quebra de linha
(decisao do autor, 14/10/2026). A posicao e a mesma em todos os cenarios, e por isso
nao e variavel; testar so o fim e limitacao declarada.

Acrescentar no fim nao desloca nenhuma posicao do gabarito de dados pessoais do
documento (`ocorrencias_dado_pessoal`), que continua valido no texto contaminado.
"""

from __future__ import annotations

import copy

SEPARADOR = "\n"


def contaminar(documentos: list[dict], id_documento: str, carga: str) -> list[dict]:
    """Devolve uma copia da base com `carga` no fim do documento alvo. Pura: nao
    altera a lista recebida."""
    if not carga:
        raise ValueError("carga vazia")
    alvos = [d for d in documentos if d["id_documento"] == id_documento]
    if len(alvos) != 1:
        raise ValueError(f"documento alvo nao encontrado ou repetido: {id_documento}")
    contaminados = copy.deepcopy(documentos)
    for d in contaminados:
        if d["id_documento"] == id_documento:
            d["texto"] = d["texto"] + SEPARADOR + carga
    return contaminados
