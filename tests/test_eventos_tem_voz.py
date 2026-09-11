"""Todo efeito que o motor anuncia precisa chegar à tela.

Um evento emitido e não renderizado é uma regra que o jogo aplica em silêncio.
O jogador não consegue aprender o que não observa — e "o jogador nunca vai se
adaptar, ele só vai spamar uma skill" foi a queixa que originou o rebalanceamento
deste projeto.

O motor emitia dez tipos de evento de turno e a interface tratava quatro. O
atordoamento que o jogador aplicava, a mana que ele perdia por dreno e a Égide
que o mantinha vivo eram todos invisíveis.

Este teste varre os `kind` emitidos em `src/mechanics/` e exige tratamento na UI.
A lista de exceções é explícita e nomeada: o que está nela é dívida conhecida,
não esquecimento. Um evento NOVO nasce falhando aqui.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

MECANICAS = RAIZ / "src" / "mechanics"
INTERFACE = RAIZ / "src" / "ui"

# Eventos que o motor emite e a UI ainda não conta. Backlog registrado, não
# esquecimento: nenhum deles é consequência das mudanças que os outros testes
# cobrem, e dar voz a todos é uma rodada própria.
SEM_VOZ_CONHECIDOS = {
    "bleed_tick",
    "cooldown_expired",
    "damage_reduction_active",
    "death_ignored",
}


def _kinds_emitidos() -> set[str]:
    padrao = re.compile(r'"kind":\s*"([a-z_]+)"')
    achados: set[str] = set()
    for arquivo in sorted(MECANICAS.rglob("*.py")):
        achados |= set(padrao.findall(arquivo.read_text(encoding="utf-8")))
    return achados


def _kinds_renderizados() -> set[str]:
    padrao = re.compile(r'kind (?:==|in) \(?((?:"[a-z_]+"(?:,\s*)?)+)\)?')
    achados: set[str] = set()
    for arquivo in sorted(INTERFACE.rglob("*.py")):
        for grupo in padrao.findall(arquivo.read_text(encoding="utf-8")):
            achados |= set(re.findall(r'"([a-z_]+)"', grupo))
    return achados


def test_a_varredura_encontra_alguma_coisa():
    """Sem esta guarda, um `src/` renomeado faria o teste passar sem olhar nada."""
    assert _kinds_emitidos(), "nenhum evento encontrado em src/mechanics/"
    assert _kinds_renderizados(), "nenhum tratamento de evento encontrado em src/ui/"


def test_todo_evento_emitido_tem_voz_na_interface():
    mudos = _kinds_emitidos() - _kinds_renderizados() - SEM_VOZ_CONHECIDOS
    assert not mudos, (
        f"o motor anuncia {sorted(mudos)} e a tela não mostra: o jogador não "
        "consegue aprender uma regra que não vê acontecer. Renderize em "
        "`src/ui/combat_event_handlers.py` e `src/ui/renderer.py`, ou registre "
        "a dívida em SEM_VOZ_CONHECIDOS com o motivo."
    )


def test_a_lista_de_excecoes_nao_guarda_evento_ja_resolvido():
    """Exceção que sobra vira permissão para o próximo evento nascer mudo."""
    resolvidos = SEM_VOZ_CONHECIDOS & _kinds_renderizados()
    assert not resolvidos, f"já são renderizados, tire de SEM_VOZ_CONHECIDOS: {sorted(resolvidos)}"


def test_os_tres_status_que_roubam_turno_aparecem():
    """`frozen` chegava à tela; `stun` e `sleep`, não — o mesmo efeito, mudo."""
    from src.shared.effects import TURN_SKIPPING_STATUSES

    renderizados = _kinds_renderizados()
    faltando = [e for e in TURN_SKIPPING_STATUSES if e not in renderizados]
    assert not faltando, f"status que rouba turno sem aviso na tela: {faltando}"
