"""RQ-06: nenhum caso do conjunto de teste aparece no conjunto de desenvolvimento.

Duas comparacoes, por hash, caso a caso:

1. **Texto inteiro.** O sha256 de cada texto do desenvolvimento e comparado com o de
   cada caso do teste, tirado de `conjunto_teste/selecao/mapeamento_rotulos.json`
   (Do-Not-Answer, BIPIA, HackAPrompt, corpus de PII e, quando existirem, mensagens
   legitimas). A comparacao e do texto exato.
2. **Valor de documento.** O mesmo CPF, CNPJ, CNS, PIS/NIT, titulo, telefone ou endereco
   nao pode estar nos dois corpus de PII, ainda que em frases diferentes.

   Excecoes declaradas (ADR-0015): valores de classes cujo espaco de valores e finito e
   pequeno por definicao, e que por isso coincidem entre quaisquer dois corpus gerados
   pelo mesmo desenho. Nao sao casos copiados; sao o mesmo padrao.
   - N4: as 10 sequencias de digitos iguais de cada comprimento;
   - E1 sem parte local: "@" seguido de um dos 3 dominios reservados;
   - T2 de horario: intervalos sorteados entre 180 combinacoes.

Leitura pura. Sai com codigo 1 se houver sobreposicao.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
MAPEAMENTO = RAIZ / "conjunto_teste" / "selecao" / "mapeamento_rotulos.json"
CORPUS_TESTE = RAIZ / "conjunto_teste" / "pii" / "corpus.jsonl"
DESENVOLVIMENTO = RAIZ / "conjunto_desenvolvimento"

_spec = importlib.util.spec_from_file_location("gerar_corpus_pii", RAIZ / "scripts" / "gerar_corpus_pii.py")
pii = importlib.util.module_from_spec(_spec)
sys.modules["gerar_corpus_pii"] = pii
_spec.loader.exec_module(pii)


def _jsonl(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as arquivo:
        return [json.loads(linha) for linha in arquivo if linha.strip()]


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def espaco_finito(o: dict) -> bool:
    classe, valor = o.get("classe_negativo"), o["valor"]
    return (
        classe == "N4"
        or (classe == "E1" and valor.startswith("@"))
        or (classe == "T2" and ":" in valor)
    )


def valores_de_documento(textos: list[dict]) -> set[str]:
    return {
        pii._so_caracteres(o["valor"])
        for t in textos
        for o in t["ocorrencias"]
        if not espaco_finito(o)
    }


def verificar() -> dict:
    hashes_teste = {
        r["sha256_texto"]
        for r in json.loads(MAPEAMENTO.read_text(encoding="utf-8"))["registros"]
    }
    valores_teste = valores_de_documento(_jsonl(CORPUS_TESTE))

    arquivos = sorted(DESENVOLVIMENTO.rglob("*.jsonl"))
    if not arquivos:
        raise FileNotFoundError(f"nenhum arquivo em {DESENVOLVIMENTO}")

    textos_dev, valores_dev = 0, set()
    textos_em_comum, valores_em_comum = [], set()
    for caminho in arquivos:
        registros = _jsonl(caminho)
        for r in registros:
            textos_dev += 1
            if _sha(r["texto"]) in hashes_teste:
                textos_em_comum.append(r["id"])
            if "ocorrencias" in r:
                valores_dev |= valores_de_documento([r])
            if "valor_normalizado_esperado" in r:
                valores_dev.add(r["valor_normalizado_esperado"])
    valores_em_comum = valores_dev & valores_teste
    return {
        "arquivos": [str(c.relative_to(RAIZ)) for c in arquivos],
        "casos_teste": len(hashes_teste),
        "textos_desenvolvimento": textos_dev,
        "textos_em_comum": textos_em_comum,
        "valores_teste": len(valores_teste),
        "valores_desenvolvimento": len(valores_dev),
        "valores_em_comum": sorted(valores_em_comum),
    }


def main() -> int:
    r = verificar()
    print(f"arquivos do desenvolvimento: {', '.join(r['arquivos'])}")
    print(f"casos do teste (mapeamento): {r['casos_teste']}")
    print(f"textos do desenvolvimento:   {r['textos_desenvolvimento']}")
    print(f"textos em comum:             {len(r['textos_em_comum'])}")
    print(f"valores de documento: teste {r['valores_teste']}, desenvolvimento {r['valores_desenvolvimento']}, "
          f"em comum {len(r['valores_em_comum'])} (excluidos os de espaco finito: N4, E1 sem parte local, T2 de horario)")
    if r["textos_em_comum"] or r["valores_em_comum"]:
        print("SOBREPOSICAO ENCONTRADA:", r["textos_em_comum"][:10], r["valores_em_comum"][:10])
        return 1
    print("Separacao verificada: nenhum caso do teste no desenvolvimento.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
