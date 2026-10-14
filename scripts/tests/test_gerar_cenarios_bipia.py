"""Atribuicao das cargas do BIPIA aos documentos (ADR-0014). Nao le o conjunto."""

from __future__ import annotations

import collections
import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("gerar_cenarios_bipia", RAIZ / "scripts" / "gerar_cenarios_bipia.py")
mod = importlib.util.module_from_spec(_spec)
sys.modules["gerar_cenarios_bipia"] = mod
_spec.loader.exec_module(mod)

CARGAS = [f"carga-{i:02d}" for i in range(75)]
DOCUMENTOS = [f"doc-{i:03d}" for i in range(1, 31)]


def test_rodizio_distribui_tres_e_duas_cargas():
    a = mod.atribuir(CARGAS, DOCUMENTOS, 20260829)
    assert sorted(a) == sorted(CARGAS)
    por_documento = collections.Counter(a.values())
    assert set(por_documento) == set(DOCUMENTOS)
    assert collections.Counter(por_documento.values()) == {3: 15, 2: 15}


def test_atribuicao_e_deterministica_e_independe_da_ordem_de_entrada():
    a = mod.atribuir(CARGAS, DOCUMENTOS, 20260829)
    b = mod.atribuir(list(reversed(CARGAS)), list(reversed(DOCUMENTOS)), 20260829)
    assert a == b


def test_semente_diferente_muda_a_atribuicao():
    assert mod.atribuir(CARGAS, DOCUMENTOS, 1) != mod.atribuir(CARGAS, DOCUMENTOS, 2)
