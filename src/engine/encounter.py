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
from src.content.extraction import award_key
from src.content.factories.loot import get_loot
from src.content.forge import award_gem
from src.mechanics import battle
from src.mechanics.math_operations import (
    calculate_mini_boss_coin_reward,
    calculate_mini_boss_xp_reward,
    calculate_monster_coin_reward,
    calculate_monster_xp_reward,
)

if TYPE_CHECKING:
    from src.entities.heroes import Player
    from src.entities.monsters import Monster


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


def process_post_battle(
    player: "Player",
    monster: "Monster | list",
    essence_multiplier: float = 1.0,
    dungeon_level: int = 1,
) -> tuple[int, bool, object | None, list[str], int, int]:
    """
    Processa a lógica de pós-combate (XP, loot, moedas, level up).

    Esta função pertence à camada de engine - ela pode importar de
    mechanics/ e content/, e pode mutar estado de entidades.

    A batalha é 1x1, então a recompensa é a do monstro derrotado. A lista de um
    elemento continua aceita porque o mapa e os saves ainda falam nessa forma.

    Retorna tupla com:
    - xp_gained: quantidade de XP ganha
    - player_won: True se jogador venceu, False se foi derrotado
    - dropped_item: item dropado ou None
    - level_up_messages: lista de mensagens de level up (strings)
    - coins_gained: quantidade de moedas ganhas
    - levels_gained: quantidade de níveis ganhos
    """
    mob = battle.sole_monster(list(monster) if isinstance(monster, list) else [monster])

    if getattr(mob, "is_boss", False):
        xp_base_reward = calculate_mini_boss_xp_reward(mob.level)
        coins_base_reward = calculate_mini_boss_coin_reward(mob.level)
    else:
        xp_base_reward = calculate_monster_xp_reward(mob.level)
        coins_base_reward = calculate_monster_coin_reward(mob.level)

    player_won = player.get_isalive()
    dropped_item = None
    coins_gained = 0

    # Passivas de essência e de ouro eram lidas por ninguém: `essence_bonus`
    # (4 cartas) e `gold_drop_bonus` (2 cartas) não apareciam em nenhum cálculo.
    essence_passive = 1 + player.get_passive_bonus("essence_bonus") / 100
    gold_passive = 1 + player.get_passive_bonus("gold_drop_bonus") / 100

    if not player_won:
        pity_xp = int((xp_base_reward // 10) * essence_multiplier * essence_passive)
        pity_coins = int((coins_base_reward // 10) * gold_passive)
        player.add_xp_points(pity_xp)
        player.earn_coins(pity_coins)
        xp_gained = pity_xp
        coins_gained = pity_coins
    else:
        xp_gained = int(xp_base_reward * essence_multiplier * essence_passive)
        player.add_xp_points(xp_gained)
        coins_gained = int(coins_base_reward * gold_passive)
        player.earn_coins(coins_gained)
        dropped_item = get_loot()
        if dropped_item:
            player.add_item_to_inventory(dropped_item)
            player.ledger["items_dropped"] = player.ledger.get("items_dropped", 0) + 1
        # Rolagem SEPARADA da do item: a gema não ocupa o lugar dele, e a mesma
        # vitória pode largar os dois.
        award_gem(player, dungeon_level)
        # E a Chave de Extração, terceira rolagem independente. Ela só cai de
        # monstro derrotado: não se compra, não se vende, nenhum serviço a dá.
        # Quem já tem a chave nem rola — ver `extraction.award_key`.
        award_key(player)

    level_up_messages: list[str] = []
    levels_gained = 0
    if player_won:
        # Processa um level up por vez para permitir escolhas apropriadas
        while True:
            msgs = player.level_up(show=True)
            if not msgs:
                break
            level_up_messages.extend(msgs)
            levels_gained += 1

    # Sem `rest()`: curar por completo depois de cada vitória tornava todo
    # combate independente do anterior e zerava o atrito do andar. Poções,
    # skills de cura e a Fonte existem justamente para pagar esse custo.

    return xp_gained, player_won, dropped_item, level_up_messages, coins_gained, levels_gained


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
