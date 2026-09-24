"""As ofertas que um nível novo abre. Uma fonte, dois consumidores.

A cadência da oferta estava escrita DUAS vezes — em `engine/loop.py`, para o
jogador, e em `sim/progression.py`, para o bot. As duas diziam
`lvl > 1 and lvl % SKILL_OFFER_LEVEL_INTERVAL == 0`, e as duas atualizavam
`seen_skill_ids` por conta própria. Enquanto forem duas, uma pode mudar sem a
outra, e o balanceamento passa a medir um jogo que o jogador não joga.

Este módulo não escolhe nada. Ele responde "o que este nível oferece", e quem
escolhe é o humano na tela ou a política do bot.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.content.passives import generate_passive_choices
from src.content.skills_loader import generate_skill_choices
from src.shared.constants import SKILL_OFFER_LEVEL_INTERVAL, SKILL_OFFER_SIZE

# Quantas passivas o jogo mostra por nível.
PASSIVE_OFFER_SIZE = 3


@dataclass(frozen=True)
class OfertaDeNivel:
    """O que um nível específico colocou na mesa."""

    level: int
    passives: list
    # `None` quando o nível não oferece skill — diferente de "ofereceu e a lista
    # veio vazia", que é catálogo esgotado.
    skills: list | None

    @property
    def tem_skill(self) -> bool:
        return self.skills is not None


def oferece_skill(level: int) -> bool:
    """Este nível abre escolha de skill?

    O nível 1 não oferece: ele ENTREGA a assinatura da classe. A partir daí é a
    cada `SKILL_OFFER_LEVEL_INTERVAL`.
    """
    return level > 1 and level % SKILL_OFFER_LEVEL_INTERVAL == 0


def ofertas_de_passiva(count: int = PASSIVE_OFFER_SIZE) -> list:
    """As cartas de passiva desta oferta. Um reroll chama de novo."""
    return generate_passive_choices(count=count)


def ofertas_de_skill(player, level: int) -> list:
    """As cartas de skill desta oferta, e o registro de que foram VISTAS.

    Ver é conhecer, mesmo que o jogador recuse: sem isto a oferta seguinte
    devolveria as mesmas três. Vale para o reroll também, e é por isso que a
    marcação mora aqui e não no chamador.
    """
    cartas = generate_skill_choices(
        player.get_classname(),
        level,
        player.active_skill_ids(),
        count=SKILL_OFFER_SIZE,
        seen_ids=player.seen_skill_ids,
    )
    player.seen_skill_ids.update(c.id for c in cartas)
    return cartas


def ofertas_do_nivel(player, level: int) -> OfertaDeNivel:
    """Tudo que este nível oferece, na ordem em que o jogo pergunta.

    Passiva primeiro, skill depois. A ordem importa porque as duas consomem o
    mesmo gerador: inverter muda o sorteio.
    """
    passivas = ofertas_de_passiva()
    skills = ofertas_de_skill(player, level) if oferece_skill(level) else None
    return OfertaDeNivel(level=level, passives=passivas, skills=skills)


def niveis_ganhos(nivel_final: int, quantidade: int) -> range:
    """Os níveis abertos por um ganho, do primeiro ao último."""
    return range(nivel_final - quantidade + 1, nivel_final + 1)


def aplicar_passiva(player, carta) -> str:
    """Aplica a passiva escolhida. Humano e bot passam por aqui."""
    return player.add_passive(carta)


def aplicar_skill(player, carta, slot: int | None = None) -> str:
    """Aprende a skill escolhida, substituindo a do slot quando o deck está cheio.

    O bot escrevia direto em `player.skills[slot]`, o que pulava
    `learn_skill`/`add_skill_with_replacement` — as funções que a tela usa.
    Escolher qual carta sai continua sendo do jogador; aplicar é do jogo.
    """
    if slot is None or player.has_free_skill_slot():
        return player.learn_skill(carta)
    return player.add_skill_with_replacement(carta, slot)
