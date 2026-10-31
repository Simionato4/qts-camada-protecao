"""Teste 1 do trabalho de QTS: guarda de orcamento (executor/orcamento.py).

Nivel do Modelo V: componente. Alvo: GuardaOrcamento.antes_de_chamar().

Regra (ficha): a chamada e recusada ANTES de acontecer se
  consumo acumulado + custo estimado da proxima (US$ 0,0025) > teto em dolares (US$ 16,00)
  ou se chamadas ja feitas >= teto de chamadas (4.500).
Tetos informados na configuracao substituem os padroes.

Tecnicas (ISTQB CTFL v4.0.1, 4.2):
  - Analise de valores limite (Jhonatan): casos "limite_*", nos dois lados de cada fronteira.
  - Particionamento de equivalencia (Thiago): casos "particao_*", um representativo
    de cada particao valida (aceita) e invalida (recusa), e a particao "teto informado".

Condicoes: arquivo de consumo em pasta temporaria (tmp_path) e simulado=True.
Nada e gravado em resultados/ e nenhuma chamada a API e feita.
"""

import json

import pytest

from executor.orcamento import GuardaOrcamento, OrcamentoExcedido

VARIAVEIS_DE_CONFIGURACAO = (
    "TETO_USD",
    "TETO_CHAMADAS",
    "CUSTO_ESTIMADO_CHAMADA_USD",
    "MODO_SIMULADO",
    "ARQUIVO_CONSUMO",
)


@pytest.fixture(autouse=True)
def ambiente_limpo(monkeypatch):
    """Sem variaveis de ambiente, valem os padroes declarados na ficha."""
    for nome in VARIAVEIS_DE_CONFIGURACAO:
        monkeypatch.delenv(nome, raising=False)


def criar_guarda(tmp_path, *, usd=0.0, chamadas=0, **tetos):
    """Grava o consumo ja ocorrido e cria a guarda, que o carrega do disco.

    Com simulado=True a guarda le <nome>-simulado.json, por isso o arquivo e
    gravado com esse sufixo.
    """
    (tmp_path / "consumo-simulado.json").write_text(
        json.dumps({"chamadas": chamadas, "usd": usd}), encoding="utf-8"
    )
    return GuardaOrcamento(arquivo=str(tmp_path / "consumo.json"), simulado=True, **tetos)


ACEITA, RECUSA = "aceita", "recusa"

CASOS = [
    # ---- Valores limite, teto em dolares padrao (16,00). Fronteira: consumo + 0,0025 == 16,00
    pytest.param(dict(usd=15.9975), {}, ACEITA, None,
                 id="limite_usd_no_teto_aceita"),          # 15,9975 + 0,0025 = 16,0000, nao passa
    pytest.param(dict(usd=15.9976), {}, RECUSA, "reserva recusada",
                 id="limite_usd_acima_do_teto_recusa"),    # 15,9976 + 0,0025 = 16,0001, passa
    # ---- Valores limite, teto de chamadas padrao (4.500). Fronteira: chamadas feitas == 4.500
    pytest.param(dict(chamadas=4499), {}, ACEITA, None,
                 id="limite_chamadas_abaixo_do_teto_aceita"),
    pytest.param(dict(chamadas=4500), {}, RECUSA, "teto de chamadas",
                 id="limite_chamadas_no_teto_recusa"),
    # ---- Particionamento de equivalencia: um representativo do meio de cada particao
    pytest.param(dict(usd=8.0, chamadas=2000), {}, ACEITA, None,
                 id="particao_dentro_dos_dois_tetos_aceita"),
    pytest.param(dict(usd=20.0), {}, RECUSA, "reserva recusada",
                 id="particao_usd_acima_do_teto_recusa"),
    pytest.param(dict(chamadas=6000), {}, RECUSA, "teto de chamadas",
                 id="particao_chamadas_acima_do_teto_recusa"),
    # ---- Particionamento: teto informado na configuracao substitui o padrao
    pytest.param(dict(usd=5.0), dict(teto_usd=1.0), RECUSA, "reserva recusada",
                 id="particao_teto_usd_informado_1_substitui_padrao_recusa"),
    pytest.param(dict(chamadas=10), dict(teto_chamadas=10), RECUSA, "teto de chamadas",
                 id="particao_teto_chamadas_informado_10_substitui_padrao_recusa"),
    # ---- Teto informado como 0 (limite inferior da configuracao): deve recusar toda chamada
    pytest.param({}, dict(teto_usd=0), RECUSA, "reserva recusada",
                 id="limite_teto_usd_informado_0_recusa"),
    pytest.param({}, dict(teto_chamadas=0), RECUSA, "teto de chamadas",
                 id="limite_teto_chamadas_informado_0_recusa"),
]


@pytest.mark.parametrize("consumo, tetos, esperado, motivo", CASOS)
def test_antes_de_chamar(tmp_path, consumo, tetos, esperado, motivo):
    guarda = criar_guarda(tmp_path, **consumo, **tetos)
    if esperado == ACEITA:
        guarda.antes_de_chamar()  # nao pode levantar excecao
    else:
        with pytest.raises(OrcamentoExcedido, match=motivo):
            guarda.antes_de_chamar()


def test_soma_da_fronteira_e_exata_em_ponto_flutuante():
    """Premissa do caso limite_usd_no_teto_aceita: 15,9975 + 0,0025 da exatamente 16.0."""
    assert 15.9975 + 0.0025 == 16.0
    assert 15.9976 + 0.0025 > 16.0


def test_guarda_nao_grava_ao_verificar(tmp_path):
    """antes_de_chamar() so verifica: o arquivo de consumo nao muda e nada vai para resultados/."""
    guarda = criar_guarda(tmp_path, usd=1.0, chamadas=1)
    antes = (tmp_path / "consumo-simulado.json").read_text(encoding="utf-8")
    guarda.antes_de_chamar()
    assert (tmp_path / "consumo-simulado.json").read_text(encoding="utf-8") == antes
    assert sorted(p.name for p in tmp_path.iterdir()) == ["consumo-simulado.json"]
