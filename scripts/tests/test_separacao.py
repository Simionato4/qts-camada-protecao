"""RQ-06: o conjunto de desenvolvimento nao contem caso do conjunto de teste.

Roda a cada execucao da suite: todo exemplo novo que a Etapa 4 acrescentar ao
conjunto de desenvolvimento e conferido automaticamente. Falha, e nao pula, se o
conjunto de desenvolvimento nao existir.
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("verificar_separacao", RAIZ / "scripts" / "verificar_separacao.py")
mod = importlib.util.module_from_spec(_spec)
sys.modules["verificar_separacao"] = mod
_spec.loader.exec_module(mod)


def test_nenhum_caso_do_teste_no_desenvolvimento():
    r = mod.verificar()
    assert r["textos_desenvolvimento"] > 0
    assert r["textos_em_comum"] == []
    assert r["valores_em_comum"] == []


def test_valores_de_espaco_finito_sao_os_unicos_ignorados():
    textos = [{"ocorrencias": [
        {"valor": "111.111.111-11", "classe_negativo": "N4"},
        {"valor": "@example.com", "classe_negativo": "E1"},
        {"valor": "07:30-19:00", "classe_negativo": "T2"},
        {"valor": "fulano@", "classe_negativo": "E1"},
        {"valor": "(20) 91234-5678", "classe_negativo": "T2"},
        {"valor": "280.012.389-38", "classe_negativo": None},
    ]}]
    assert mod.valores_de_documento(textos) == {"28001238938", "FULANO", "20912345678"}
