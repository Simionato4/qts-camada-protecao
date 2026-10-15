"""Toda imagem de conteiner fixada por digest, e o digest igual ao registrado.

Existe por causa de uma regressao real: em 10/09/2026 o commit `ce29a76` voltou as
quatro imagens de servico para `:latest` sem que ninguem percebesse, e o
`docs/versoes.md` continuou afirmando que estavam fixadas (ADR-0021). Este teste falha
se isso voltar a acontecer, em qualquer imagem do compose ou dos Dockerfile.
"""

from __future__ import annotations

import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
DIGEST = re.compile(r"@sha256:([0-9a-f]{64})")


def _referencias() -> list[tuple[str, str]]:
    refs = [
        ("docker-compose.yml", m.group(1).strip())
        for m in re.finditer(r"^\s*image:\s*(\S+)", (RAIZ / "docker-compose.yml").read_text(encoding="utf-8"), re.M)
    ]
    for dockerfile in sorted(RAIZ.glob("*/Dockerfile")):
        for m in re.finditer(r"^\s*FROM\s+(\S+)", dockerfile.read_text(encoding="utf-8"), re.M):
            refs.append((str(dockerfile.relative_to(RAIZ)), m.group(1)))
    return refs


def test_toda_imagem_tem_digest_e_nenhuma_usa_latest():
    refs = _referencias()
    assert refs, "nenhuma referencia de imagem encontrada"
    for origem, ref in refs:
        assert ":latest" not in ref, (origem, ref)
        assert DIGEST.search(ref), (origem, ref)


def test_digests_sao_os_registrados_em_versoes():
    texto = (RAIZ / "docs" / "versoes.md").read_text(encoding="utf-8")
    registrados = set(re.findall(r"sha256:([0-9a-f]{64})", texto))
    for origem, ref in _referencias():
        assert DIGEST.search(ref).group(1) in registrados, (origem, ref)
