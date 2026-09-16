"""O encontro, do primeiro turno à última escolha de nível. Uma orquestração só.

Havia duas. O jogador passava por `engine.loop.run_fight`; o bot montava a mesma
sequência por fora — batalha, guarda de fuga, pós-combate, ofertas, escolha.
Mesmo chamando várias funções iguais, eram dois roteiros, e dois roteiros
divergem: foi assim que o bot passou a pagar recompensa por fuga, e assim que a
ordem das ofertas de nível ficou diferente entre os dois.

Aqui a REGRA é uma. O que muda é quem responde às perguntas:

    combat_decision   o que fazer neste turno       (tela do jogador / política)
    level_up_provider o que levar deste nível       (tela do jogador / política)

Sem UI. Quem desenha é o adaptador — `engine.loop.run_fight` para o humano,
`tools.bot_padrao` para o bot.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from src.content import level_up
from src.mechanics import battle

if TYPE_CHECKING:
    from src.entities.heroes import Player


@dataclass
class EncounterResult:
    """O que o encontro produziu. Tudo que o adaptador precisa para desenhar."""

    fled: bool = False
    hero_won: bool = False
    xp_gained: int = 0
    coins_gained: int = 0
    dropped_item: Any = None
    levels_gained: int = 0
    level_up_messages: list[str] = field(default_factory=list)
    outcome: Any = None

    @property
    def alive(self) -> bool:
        return not self.fled and self.hero_won


def resolve_encounter(
    player: "Player",
    monsters: list,
    *,
    combat_decision: Callable,
    level_up_provider: Callable[["Player", level_up.OfertaDeNivel], None] | None = None,
    rng: random.Random | None = None,
    essence_multiplier: float = 1.0,
    dungeon_level: int = 1,
    publish: Callable | None = None,
    on_turn_start: Callable | None = None,
    on_results: Callable[[EncounterResult], None] | None = None,
) -> EncounterResult:
    """Resolve um encontro inteiro e devolve o resultado.

    A ordem é a do jogo, e agora existe num lugar só:

      1. batalha;
      2. FUGA ENCERRA — quem foge não recebe nada. `process_post_battle` decide
         "venceu" por `get_isalive()`, e quem fugiu está vivo: sem esta guarda,
         fugir pagaria XP, ouro e loot cheios;
      3. pós-combate (XP, ouro, loot, gema, subida de nível);
      4. apresentação, se o adaptador quiser;
      5. uma oferta por nível ganho, passiva antes de skill.

    `level_up_provider` recebe a oferta e é responsável por escolher E aplicar —
    mas aplicando por `content.level_up.aplicar_passiva` / `aplicar_skill`, que é
    o que mantém humano e bot no mesmo caminho.
    """
    from src.engine.loop import process_post_battle

    rng = rng or random.Random()
    nivel_antes = player.get_level()

    outcome = battle.run_battle(
        player,
        monsters,
        combat_decision,
        rng=rng,
        publish=publish,
        on_turn_start=on_turn_start,
    )
    if outcome.fled:
        return EncounterResult(fled=True, outcome=outcome)

    xp, venceu, drop, mensagens, moedas, niveis = process_post_battle(
        player, monsters, essence_multiplier, dungeon_level
    )
    resultado = EncounterResult(
        fled=False,
        hero_won=venceu,
        xp_gained=xp,
        coins_gained=moedas,
        dropped_item=drop,
        levels_gained=niveis,
        level_up_messages=list(mensagens),
        outcome=outcome,
    )

    if on_results is not None:
        on_results(resultado)

    if venceu and niveis > 0 and level_up_provider is not None:
        for lvl in level_up.niveis_ganhos(player.get_level(), player.get_level() - nivel_antes):
            level_up_provider(player, level_up.ofertas_do_nivel(player, lvl))

    return resultado
