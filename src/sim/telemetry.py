"""Telemetria por sistema durante uma run simulada.

Saber que uma classe chega ao andar 8 não diz qual sistema a levou até lá. Sem
atribuição, "esta skill é forte demais" e "esta passiva é inútil" continuam
sendo palpite, e a única forma de responder é desligar coisas uma a uma — o que
custa minutos.

Este coletor registra, durante a run que já está rodando, o que cada sistema
efetivamente entregou: dano por skill e por mana, quantas vezes cada passiva foi
oferecida e escolhida, de onde veio o equipamento, quanto o ouro comprou, quanto
a Essência multiplicou e o que os eventos aleatórios fizeram.

É atribuição, não causalidade: um número alto aqui aponta o suspeito. Quem
condena é a ablação em `sim/scout.py`, que desliga o sistema e mede o delta.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class RunTelemetry:
    """Acumulador de contribuição por sistema, ao longo de muitas runs."""

    runs: int = 0

    # --- Skills ---
    skill_uses: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_damage: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_mp: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_offered: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_picked: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    basic_damage: int = 0

    # --- Passivas ---
    passive_offered: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    passive_picked: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # --- Equipamento e economia ---
    items_from_loot: int = 0
    items_equipped_from_loot: int = 0
    items_bought: int = 0
    items_equipped_from_shop: int = 0
    gold_earned: int = 0
    gold_on_gear: int = 0
    gold_on_consumables: int = 0
    gold_unspent: int = 0
    equipped_by_slot: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    final_power_naked: list[float] = field(default_factory=list)
    final_power_equipped: list[float] = field(default_factory=list)

    # --- Consumíveis ---
    consumables_used: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # --- Essência ---
    essence_rolls: list[float] = field(default_factory=list)
    xp_base: int = 0
    xp_after_essence: int = 0

    # --- Eventos aleatórios ---
    event_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    fountain_healed: int = 0
    altar_hp_paid: int = 0
    altar_deaths: int = 0
    event_declined: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # --- Combate ---
    battles: int = 0
    turns: int = 0
    # Runs que terminaram com o herói morto. Separar vitória de derrota é o que
    # permite perguntar "o que ele estava fazendo quando morreu" — a pergunta
    # mais útil num jogo de permadeath.
    defeats: int = 0

    def record_battle(self, outcome) -> None:
        """Soma o que uma batalha entregou, por skill e por consumível."""
        self.battles += 1
        self.turns += outcome.turns
        self.basic_damage += outcome.basic_damage
        for skill_id, count in outcome.skill_uses.items():
            self.skill_uses[skill_id] += count
        for skill_id, dano in outcome.skill_damage.items():
            self.skill_damage[skill_id] += dano
        for skill_id, mana in outcome.skill_mp.items():
            self.skill_mp[skill_id] += mana
        for efeito, count in outcome.items_by_effect.items():
            self.consumables_used[efeito] += count

    def record_offer(self, kind: str, offered: list, chosen) -> None:
        """Registra uma escolha oferecida ao jogador e o que ele levou.

        A taxa de escolha quando oferecida separa a carta que ninguém quer da
        carta que raramente aparece — duas causas muito diferentes para o mesmo
        sintoma de "quase nunca vista".
        """
        alvo_oferta = self.skill_offered if kind == "skill" else self.passive_offered
        alvo_escolha = self.skill_picked if kind == "skill" else self.passive_picked
        for carta in offered:
            alvo_oferta[carta.id] += 1
        if chosen is not None:
            alvo_escolha[chosen.id] += 1

    def to_dict(self) -> dict:
        """Serializa para JSON, convertendo os defaultdict em dict comum."""
        return {
            "runs": self.runs,
            "battles": self.battles,
            "turns": self.turns,
            "defeats": self.defeats,
            "skills": {
                "uses": dict(self.skill_uses),
                "damage": dict(self.skill_damage),
                "mp": dict(self.skill_mp),
                "offered": dict(self.skill_offered),
                "picked": dict(self.skill_picked),
                "basic_damage": self.basic_damage,
            },
            "passives": {
                "offered": dict(self.passive_offered),
                "picked": dict(self.passive_picked),
            },
            "equipment": {
                "items_from_loot": self.items_from_loot,
                "items_equipped_from_loot": self.items_equipped_from_loot,
                "items_bought": self.items_bought,
                "items_equipped_from_shop": self.items_equipped_from_shop,
                "equipped_by_slot": dict(self.equipped_by_slot),
                "power_naked_sum": sum(self.final_power_naked),
                "power_equipped_sum": sum(self.final_power_equipped),
                "power_samples": len(self.final_power_naked),
            },
            "economy": {
                "gold_earned": self.gold_earned,
                "gold_on_gear": self.gold_on_gear,
                "gold_on_consumables": self.gold_on_consumables,
                "gold_unspent": self.gold_unspent,
            },
            "consumables": dict(self.consumables_used),
            # Somas e contagens, nunca médias: o agregador soma bloco a bloco,
            # e somar três médias produz um número sem significado — foi assim
            # que a Essência apareceu com média 4,02 num intervalo de 0,5 a 3,0.
            "essence": {
                "rolls": len(self.essence_rolls),
                "sum": sum(self.essence_rolls),
                "xp_base": self.xp_base,
                "xp_after": self.xp_after_essence,
            },
            "events": {
                "counts": dict(self.event_counts),
                "declined": dict(self.event_declined),
                "fountain_healed": self.fountain_healed,
                "altar_hp_paid": self.altar_hp_paid,
                "altar_deaths": self.altar_deaths,
            },
        }


