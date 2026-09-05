"""Integridade do texto dos dados de conteúdo.

Seis skills chegaram ao repositório com o nome duplamente codificado — os bytes
UTF-8 de "Lançar Adaga" lidos como latin-1 e regravados, virando
"LanÃ§ar Adaga". O jogo carrega o JSON corretamente, então nada quebra: o
defeito só aparece na tela do jogador e no relatório do scout, onde a carta
passa a ter dois nomes possíveis conforme quem a imprime.

Nenhum teste pegava isso porque nenhum teste olhava o texto. Este olha.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DADOS = sorted((RAIZ / "src" / "data").glob("*.json"))

# Assinatura de UTF-8 lido como latin-1: um 'Ã' ou 'Â' seguido de um byte de
# continuação. Em português correto, 'Ã' só ocorre em maiúsculas isoladas
# ("ÃGUA" não existe), então a sequência é sempre erro de codificação.
MOJIBAKE = re.compile(r"[ÃÂ][\x80-\xbf\xa0-\xff\xad]")

CAMPOS_DE_TEXTO = ("name", "description")


def _todos_os_registros(valor):
    """Percorre a estrutura carregada e devolve cada dicionário encontrado."""
    if isinstance(valor, dict):
        yield valor
        for filho in valor.values():
            yield from _todos_os_registros(filho)
    elif isinstance(valor, list):
        for filho in valor:
            yield from _todos_os_registros(filho)


@pytest.mark.parametrize("arquivo", DADOS, ids=lambda p: p.name)
def test_arquivo_nao_tem_texto_mal_codificado(arquivo: Path):
    conteudo = arquivo.read_text(encoding="utf-8")
    achados = sorted({m.group(0) for m in MOJIBAKE.finditer(conteudo)})
    assert not achados, (
        f"{arquivo.name} tem texto duplamente codificado ({achados}). "
        "Corrija com texto.encode('latin-1').decode('utf-8')."
    )


@pytest.mark.parametrize("arquivo", DADOS, ids=lambda p: p.name)
def test_todo_registro_tem_nome_legivel(arquivo: Path):
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    for registro in _todos_os_registros(dados):
        for campo in CAMPOS_DE_TEXTO:
            texto = registro.get(campo)
            if not isinstance(texto, str):
                continue
            assert texto.strip(), f"{arquivo.name}: {campo} vazio em {registro.get('id')}"
            assert not MOJIBAKE.search(texto), (
                f"{arquivo.name}: {campo} de {registro.get('id')!r} = {texto!r}"
            )
