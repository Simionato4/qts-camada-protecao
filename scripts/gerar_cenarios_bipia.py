"""Tarefa 3.7 - atribui cada carga de texto do BIPIA a um documento da base (ADR-0014).

Um cenario por carga. Atribuicao por rodizio (decisao do autor, 14/10/2026): as 75
cargas sao embaralhadas com a semente registrada e distribuidas em ordem pelos 30
documentos, de modo que 15 documentos recebem 3 cargas e 15 recebem 2.

Para cada cenario grava-se: identificador do caso (o mesmo do mapeamento de rotulos),
sha256 da carga, documento alvo, pergunta pareada e **o hash esperado do estado
contaminado**. O executor (Etapa 5) compara o hash lido do Qdrant com esse valor depois
de contaminar, e com o hash limpo depois de restaurar; divergencia interrompe a execucao.

Sem texto de carga no arquivo (ADR-0016). Exige `conjunto_teste/origem/bipia`.

Uso:
    python scripts/gerar_cenarios_bipia.py --apenas-contar
    python scripts/gerar_cenarios_bipia.py
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import importlib.util
import json
import os
import random
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from recuperador.app.contaminacao import contaminar  # noqa: E402
from recuperador.app.indice import carregar_documentos, hash_do_estado  # noqa: E402

BASE = RAIZ / "base_conhecimento"
CARGAS = RAIZ / "conjunto_teste" / "origem" / "bipia" / "benchmark" / "text_attack_test.json"
SAIDA = RAIZ / "conjunto_teste" / "selecao" / "bipia_cenarios.json"

_spec = importlib.util.spec_from_file_location("gerar_mapeamento", RAIZ / "scripts" / "gerar_mapeamento.py")
mapeamento = importlib.util.module_from_spec(_spec)
sys.modules["gerar_mapeamento"] = mapeamento
_spec.loader.exec_module(mapeamento)


def atribuir(ids_cargas: list[str], ids_documentos: list[str], semente: int) -> dict[str, str]:
    """Rodizio: embaralha as cargas com a semente e distribui em ordem pelos documentos."""
    ordem = sorted(ids_cargas)
    random.Random(semente).shuffle(ordem)
    documentos = sorted(ids_documentos)
    return {carga: documentos[i % len(documentos)] for i, carga in enumerate(ordem)}


def main() -> int:
    analisador = argparse.ArgumentParser()
    analisador.add_argument("--apenas-contar", action="store_true")
    argumentos = analisador.parse_args()

    semente = int(os.getenv("SEMENTE_MESTRA", "20260829"))
    dados = json.loads(CARGAS.read_text(encoding="utf-8"))
    cargas = {
        f"bipia-{mapeamento.slug(categoria)}-{indice}": (categoria, indice, texto)
        for categoria, lista in dados.items()
        for indice, texto in enumerate(lista)
    }
    documentos = carregar_documentos(BASE)
    perguntas = {
        p["id_documento"]: p["pergunta"]
        for p in json.loads((BASE / "perguntas_pareadas.json").read_text(encoding="utf-8"))
    }
    limpo = hash_do_estado(documentos)
    atribuicao = atribuir(list(cargas), [d["id_documento"] for d in documentos], semente)

    cenarios = []
    for caso_id in sorted(cargas):
        categoria, indice, texto = cargas[caso_id]
        alvo = atribuicao[caso_id]
        cenarios.append({
            "caso_id": caso_id,
            "categoria": categoria,
            "indice": indice,
            "sha256_carga": hashlib.sha256(texto.encode("utf-8")).hexdigest(),
            "documento_alvo": alvo,
            "pergunta_pareada": perguntas[alvo],
            "hash_estado_contaminado": hash_do_estado(contaminar(documentos, alvo, texto)),
        })

    por_documento = collections.Counter(c["documento_alvo"] for c in cenarios)
    distribuicao = collections.Counter(por_documento.values())
    print(f"semente: {semente}")
    print(f"cenarios: {len(cenarios)}; documentos usados: {len(por_documento)}")
    print(f"cargas por documento: {dict(sorted(distribuicao.items()))}")
    print(f"hash do estado limpo: {limpo}")
    assert len(cenarios) == 75 and len(por_documento) == 30
    assert distribuicao == {3: 15, 2: 15}
    assert len({c["hash_estado_contaminado"] for c in cenarios}) == 75
    assert all(c["hash_estado_contaminado"] != limpo for c in cenarios)

    if argumentos.apenas_contar:
        print("Nenhum arquivo gravado.")
        return 0

    resultado = {
        "descricao": "Cenarios de injecao indireta do BIPIA (ADR-0014, RQ-18). Sem texto de carga (ADR-0016).",
        "posicao_da_carga": "fim do documento, apos uma quebra de linha",
        "semente": semente,
        "hash_estado_limpo": limpo,
        "cenarios": cenarios,
    }
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    temporario = SAIDA.with_suffix(".tmp")
    with temporario.open("w", encoding="utf-8", newline="\n") as arquivo:
        arquivo.write(conteudo)
    temporario.replace(SAIDA)
    print(f"gravado: {SAIDA}")
    print(f"sha256: {hashlib.sha256(SAIDA.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
