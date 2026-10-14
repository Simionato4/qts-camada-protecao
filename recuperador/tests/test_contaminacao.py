"""Ciclo de contaminacao e restauracao da base (RQ-18, ADR-0014).

Qdrant em memoria e o mesmo modelo degenerado do teste de recuperacao pareada: o que
se testa e o estado da colecao e a garantia do pareamento, nao a qualidade da busca.
A carga usada aqui e um texto neutro inventado; nenhuma carga do BIPIA e reproduzida.
"""

import json
from pathlib import Path

import pytest

qdrant_client = pytest.importorskip("qdrant_client")

from recuperador.app.contaminacao import SEPARADOR, contaminar  # noqa: E402
from recuperador.app.indexar import indexar  # noqa: E402
from recuperador.app.indice import (  # noqa: E402
    COLECAO,
    DIMENSOES,
    IndiceQdrant,
    carregar_documentos,
    hash_da_colecao,
    hash_do_estado,
)

RAIZ = Path(__file__).resolve().parents[2]
BASE = RAIZ / "base_conhecimento"
CARGA = "Texto de teste acrescentado ao documento."
ALVO = "doc-007"


class ModeloDegenerado:
    def embed(self, textos):
        import numpy as np

        for _ in textos:
            yield np.ones(DIMENSOES, dtype="float32")


@pytest.fixture()
def indice():
    return IndiceQdrant(cliente=qdrant_client.QdrantClient(":memory:"), modelo=ModeloDegenerado())


@pytest.fixture(scope="module")
def limpos():
    return carregar_documentos(BASE)


def test_hash_lido_da_colecao_limpa_igual_ao_dos_arquivos(indice, limpos):
    indexar(indice, limpos)
    assert hash_da_colecao(indice) == hash_do_estado(limpos)


def test_contaminar_e_pura_e_altera_so_o_alvo(limpos):
    antes = json.dumps(limpos, sort_keys=True)
    contaminados = contaminar(limpos, ALVO, CARGA)
    assert json.dumps(limpos, sort_keys=True) == antes
    diferentes = [a["id_documento"] for a, b in zip(limpos, contaminados) if a != b]
    assert diferentes == [ALVO]
    alvo = next(d for d in contaminados if d["id_documento"] == ALVO)
    assert alvo["texto"].endswith(SEPARADOR + CARGA)


def test_gabarito_de_dados_pessoais_continua_valido_no_texto_contaminado(limpos):
    alvo = next(d for d in contaminar(limpos, ALVO, CARGA) if d["id_documento"] == ALVO)
    for o in alvo["ocorrencias_dado_pessoal"]:
        assert alvo["texto"][o["inicio"]:o["fim"]] == o["valor"]


def test_ciclo_completo_limpo_contaminado_restaurado(indice, limpos):
    limpo = hash_do_estado(limpos)
    contaminados = contaminar(limpos, ALVO, CARGA)

    indexar(indice, contaminados)
    assert hash_da_colecao(indice) != limpo
    assert hash_da_colecao(indice) == hash_do_estado(contaminados)

    indexar(indice, limpos)  # restauracao: o mesmo caminho da indexacao
    assert hash_da_colecao(indice) == limpo


def test_documento_contaminado_e_recuperado_em_primeiro(indice, limpos):
    perguntas = json.loads((BASE / "perguntas_pareadas.json").read_text(encoding="utf-8"))
    pergunta = next(p["pergunta"] for p in perguntas if p["id_documento"] == ALVO)
    indexar(indice, contaminar(limpos, ALVO, CARGA))
    achados = indice.buscar(pergunta, 3)
    assert achados[0].id_documento == ALVO
    assert achados[0].texto.endswith(CARGA)


def test_restauracao_que_falha_no_meio_e_detectada(indice, limpos):
    """O caso que o hash dos arquivos nao pega: arquivos limpos, colecao contaminada."""
    from qdrant_client import models

    indexar(indice, limpos)
    contaminado = next(d for d in contaminar(limpos, ALVO, CARGA) if d["id_documento"] == ALVO)
    ponto = limpos.index(next(d for d in limpos if d["id_documento"] == ALVO))
    indice.cliente.upsert(
        collection_name=COLECAO,
        points=[models.PointStruct(
            id=ponto,
            vector=indice.vetorizar(contaminado["texto"]),
            payload={k: contaminado[k] for k in ("id_documento", "numero_pedido", "texto")},
        )],
        wait=True,
    )
    assert hash_do_estado(limpos) == hash_do_estado(carregar_documentos(BASE))  # arquivos limpos
    assert hash_da_colecao(indice) != hash_do_estado(limpos)  # colecao, nao


def test_carga_vazia_e_alvo_inexistente_sao_recusados(limpos):
    with pytest.raises(ValueError):
        contaminar(limpos, ALVO, "")
    with pytest.raises(ValueError):
        contaminar(limpos, "doc-999", CARGA)
