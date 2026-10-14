"""Implementacao independente dos DV contra os exemplos das fontes e contra a
validate-docbr 2.0.0 (ADR-0015, opcao A').

Concordancia nos dois sentidos, com semente fixa:
- todo numero completado aqui e aceito pela biblioteca, e recusado com o ultimo digito
  alterado;
- todo numero gerado pela biblioteca e aceito aqui.
Uma falha e achado sobre a biblioteca ou sobre a fonte, e nao defeito a contornar.
"""

from __future__ import annotations

import importlib.util
import random
import string
import sys
from pathlib import Path

import pytest
from validate_docbr import CNPJ, CNS, CPF, PIS, TituloEleitoral

RAIZ = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("dv_independente", RAIZ / "scripts" / "dv_independente.py")
dv = importlib.util.module_from_spec(_spec)
sys.modules["dv_independente"] = dv
_spec.loader.exec_module(dv)

SEMENTE = 20260829
N = 300


def _base(sorteio: random.Random, n: int, alfabeto: str = string.digits) -> str:
    return "".join(sorteio.choice(alfabeto) for _ in range(n))


def _altera_ultimo(numero: str) -> str:
    return numero[:-1] + str((int(numero[-1]) + 1) % 10)


# ------------------------------------------------------ exemplos publicados nas fontes

def test_exemplo_cpf_da_e_financeira():
    assert dv.completar_cpf("280012389") == "28001238938"


def test_exemplo_cnpj_numerico_da_e_financeira():
    assert dv.completar_cnpj("187812030001") == "18781203000128"


def test_exemplo_cnpj_alfanumerico_da_receita():
    assert dv.completar_cnpj("12ABC34501DE") == "12ABC34501DE35"


def test_exemplo_titulo_da_obmep():
    assert dv.completar_titulo("10238501", "06") == "102385010671"


# ------------------------------------------------- concordancia com a validate-docbr

def test_cpf_concorda():
    s = random.Random(SEMENTE)
    for _ in range(N):
        n = dv.completar_cpf(_base(s, 9))
        if len(set(n)) == 1:
            continue  # sequencias repetidas: tratadas como negativo no desenho
        assert CPF().validate(n), n
        assert not CPF().validate(_altera_ultimo(n)), n


@pytest.mark.parametrize("alfabeto", [string.digits, string.digits + string.ascii_uppercase])
def test_cnpj_concorda(alfabeto):
    s = random.Random(SEMENTE)
    conferidos = 0
    while conferidos < N:
        n = dv.completar_cnpj(_base(s, 12, alfabeto))
        if n is None or len(set(n)) == 1:
            continue
        assert CNPJ().validate(n), n
        assert not CNPJ().validate(_altera_ultimo(n)), n
        conferidos += 1


def test_pis_concorda():
    s = random.Random(SEMENTE)
    for _ in range(N):
        n = dv.completar_pis(_base(s, 10))
        if len(set(n)) == 1:
            continue
        assert PIS().validate(n), n
        assert not PIS().validate(_altera_ultimo(n)), n


def test_cns_definitivo_concorda():
    s = random.Random(SEMENTE)
    for _ in range(N):
        n = dv.completar_cns_definitivo(s.choice("12") + _base(s, 10))
        assert CNS().validate(n), n
        assert not CNS().validate(_altera_ultimo(n)), n


def test_cns_provisorio_concorda():
    s = random.Random(SEMENTE)
    conferidos = 0
    while conferidos < N:
        n = dv.completar_cns_provisorio(s.choice("789") + _base(s, 13))
        if n is None:
            continue
        assert CNS().validate(n), n
        assert not CNS().validate(_altera_ultimo(n)), n
        conferidos += 1


def test_titulo_concorda_fora_dos_casos_ambiguos():
    s = random.Random(SEMENTE)
    conferidos = 0
    i = 0
    while conferidos < N:
        uf = f"{i % 28 + 1:02d}"
        i += 1
        seq = _base(s, 8)
        if dv.titulo_ambiguo(seq, uf):
            continue
        n = dv.completar_titulo(seq, uf)
        assert TituloEleitoral().validate(n), n
        assert not TituloEleitoral().validate(_altera_ultimo(n)), n
        conferidos += 1


def test_titulo_divergencia_caracterizada_em_sp_e_mg():
    """ACHADO (ADR-0015): nos casos ambiguos de SP e MG, a biblioteca aceita o numero
    calculado SEM a excecao descrita pela OBMEP e recusa o calculado COM ela."""
    s = random.Random(SEMENTE)
    encontrados = 0
    while encontrados < 50:
        uf = s.choice(["01", "02"])
        seq = _base(s, 8)
        if not dv.titulo_ambiguo(seq, uf):
            continue
        assert TituloEleitoral().validate(dv.completar_titulo(seq, uf, excecao_sp_mg=False))
        assert not TituloEleitoral().validate(dv.completar_titulo(seq, uf, excecao_sp_mg=True))
        encontrados += 1


def test_titulo_ambiguidade_so_existe_em_sp_e_mg():
    s = random.Random(SEMENTE)
    for i in range(N):
        uf = f"{i % 26 + 3:02d}"  # 03 a 28
        assert not dv.titulo_ambiguo(_base(s, 8), uf)


def test_generate_da_biblioteca_so_sorteia_uf_de_01_a_18():
    """ACHADO (ADR-0015): a tabela do TSE vai de 01 a 28; o gerador da biblioteca nao."""
    random.seed(SEMENTE)
    ufs = {int(TituloEleitoral().generate()[8:10]) for _ in range(2000)}
    assert max(ufs) <= 18


@pytest.mark.parametrize(
    "classe, aceita",
    [
        (CPF, lambda n: dv.completar_cpf(n[:9]) == n),
        (CNPJ, lambda n: dv.completar_cnpj(n[:12]) == n),
        (PIS, lambda n: dv.completar_pis(n[:10]) == n),
        (CNS, dv.cns_valido),
        # sem a excecao de SP e MG, que a biblioteca nao aplica (ver teste acima)
        (TituloEleitoral, lambda n: dv.completar_titulo(n[:8], n[8:10], excecao_sp_mg=False) == n),
    ],
)
def test_gerados_pela_biblioteca_sao_aceitos_aqui(classe, aceita):
    random.seed(SEMENTE)  # a generate() da biblioteca usa o modulo random global
    for _ in range(N):
        n = classe().generate()
        assert aceita(n), n


# ------------------------------------------------------------- estado (tres valores)

def test_repetidos_sao_invalidos_em_cpf_cnpj_e_pis_mesmo_fechando_a_conta():
    # 111.111.111-11 fecha a conta do DV do CPF; a regra RV_01 o recusa.
    assert dv.completar_cpf("111111111") == "11111111111"
    for d in "0123456789":
        assert dv.estado("cpf", d * 11) == dv.INVALIDO
        assert dv.estado("cnpj", d * 14) == dv.INVALIDO
        assert dv.estado("pis", d * 11) == dv.INVALIDO


def test_titulo_com_uf_fora_da_tabela_do_tse_e_invalido():
    for uf in ("00", "29", "99"):
        numero = dv.completar_titulo("12345678", "01", excecao_sp_mg=False)[:8] + uf
        assert dv.estado("titulo", numero + "00") == dv.INVALIDO


def test_biblioteca_aceita_titulo_com_uf_fora_da_tabela():
    """ACHADO (ADR-0015): a validate-docbr 2.0.0 nao confere a UF; aceita 00 e 29 a 99
    quando a conta do DV fecha."""
    for uf in ("00", "29", "99"):
        s = [int(c) for c in "12345678"]
        r = sum(a * b for a, b in zip(s, range(2, 10))) % 11
        d1 = 0 if r == 10 else r
        r2 = (int(uf[0]) * 7 + int(uf[1]) * 8 + d1 * 9) % 11
        numero = "12345678" + uf + f"{d1}{0 if r2 == 10 else r2}"
        assert TituloEleitoral().validate(numero)
        assert dv.estado("titulo", numero) == dv.INVALIDO


def test_titulo_ambiguo_e_indefinido_nas_duas_convencoes():
    s = random.Random(SEMENTE)
    while True:
        seq, uf = _base(s, 8), s.choice(["01", "02"])
        if dv.titulo_ambiguo(seq, uf):
            break
    assert dv.estado("titulo", dv.completar_titulo(seq, uf, True)) == dv.INDEFINIDO
    assert dv.estado("titulo", dv.completar_titulo(seq, uf, False)) == dv.INDEFINIDO


def test_cnpj_alfanumerico_sem_regra_para_o_resto_e_indefinido():
    s = random.Random(SEMENTE)
    while True:
        base = _base(s, 12, string.digits + string.ascii_uppercase)
        if not base.isdigit() and dv.completar_cnpj(base) is None:
            break
    assert dv.estado("cnpj", base + "00") == dv.INDEFINIDO


def test_estado_concorda_com_completar_nos_validos():
    s = random.Random(SEMENTE)
    for _ in range(N):
        assert dv.estado("cpf", dv.completar_cpf(_base(s, 9))) in (dv.VALIDO, dv.INVALIDO)
        assert dv.estado("pis", dv.completar_pis(_base(s, 10))) in (dv.VALIDO, dv.INVALIDO)
    assert dv.estado("cpf", "28001238938") == dv.VALIDO
    assert dv.estado("cnpj", "18781203000128") == dv.VALIDO
    assert dv.estado("cnpj", "12ABC34501DE35") == dv.VALIDO
    assert dv.estado("titulo", "102385010671") == dv.VALIDO
