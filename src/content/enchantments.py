"""Encantamentos: a terceira dimensão de progressão do equipamento.

As três não se misturam, e cada uma responde a uma pergunta diferente:

    +N            quanto a PRÓPRIA PEÇA foi aprimorada  (multiplica a base dela)
    Gema          quanto o PERSONAGEM ganha de atributo (percentual de atributo)
    Encantamento  como o GOLPE se comporta              (modificador de combate)

Um encantamento não fortalece a peça nem o atributo: ele acrescenta poder
contextual, e resolve pelos canais que o motor já tem. Nenhum sistema de combate
paralelo — é o mesmo `fx.combat_modifier` que buff, passiva e equipamento já
usam, e o mesmo bucket `+MULT` que o funil de dano já sabe consumir.
"""

from __future__ import annotations

# Teto conceitual de encantamentos por peça. Cinco é bastante: o objetivo é ter
# a infraestrutura, não distribuir cinco para todo item.
MAX_ENCHANTMENTS = 5

# O que um encantamento pode fazer nesta V1, e por onde cada efeito chega ao
# motor. A regra de entrada é a mesma da allowlist de equipamento: só entra o
# que JÁ tem consumidor funcional, para nenhum encantamento nascer placebo.
#
# `damage_percent` é o único que estreia um canal: ele alimenta o bucket `+MULT`
# de `_calculate_damage`, que existe desde a centralização da linguagem de poder
# e nunca tinha sido preenchido. É exatamente para isto que ele foi feito —
# percentuais ADITIVOS entre si, o pool da abundância.
ENCHANT_EFFECTS: dict[str, str] = {
    "damage_percent": "+% de dano causado",
    "crit_chance": "+% de chance de crítico",
    "crit_damage": "+% de dano crítico",
    "damage_reduction": "+% de redução de dano recebido",
    "life_steal": "+% de roubo de vida",
    "evasion": "+ pontos de evasão",
    "mana_regen": "+ MP por turno",
    # A família on-hit. Todas resolvem pelo NÚCLEO de efeitos, pela mesma
    # rolagem que a passiva e a skill usam: o encantamento declara a chance, e o
    # catálogo global decide o que sangramento significa.
    "stun_chance": "+% de chance de atordoar",
    "bleed_chance": "+% de chance de sangramento",
    "poison_chance": "+% de chance de envenenar",
    "fear_chance": "+% de chance de amedrontar",
}


class Enchantment:
    """Um encantamento no exemplar. Efeito e valor, e mais nada.

    Sem `enhancement_level` e sem nível próprio: `+N` é exclusivo de
    equipamento, e a progressão do encantamento é trocá-lo por um melhor. Uma
    terceira escada aqui seria a quarta dimensão que ninguém pediu.
    """

    __slots__ = ("effect", "value")

    def __init__(self, effect: str, value: float) -> None:
        if effect not in ENCHANT_EFFECTS:
            raise ValueError(
                f"Encantamento desconhecido: {effect!r}. Conhecidos: {', '.join(ENCHANT_EFFECTS)}"
            )
        if float(value) <= 0:
            raise ValueError(f"Encantamento precisa de valor positivo, não {value!r}")
        self.effect: str = effect
        self.value: float = float(value)

    @property
    def display_name(self) -> str:
        rotulo = ENCHANT_EFFECTS[self.effect]
        valor = int(self.value) if float(self.value).is_integer() else self.value
        return rotulo.replace("+", f"+{valor}", 1)

    def __repr__(self) -> str:  # pragma: no cover - conveniência de depuração
        return f"Enchantment({self.effect!r}, {self.value})"


def create_enchantment(effect: str, value: float) -> Enchantment:
    """Constrói um encantamento. Ponto de entrada único."""
    return Enchantment(effect, value)


def enchantment_from_dict(dados) -> Enchantment | None:
    """Reconstrói um encantamento salvo. `None` para vazio ou dado inválido."""
    if not isinstance(dados, dict):
        return None
    try:
        return Enchantment(str(dados.get("effect", "")), float(dados.get("value", 0)))
    except (ValueError, TypeError):
        return None


def enchantment_to_dict(ench: Enchantment | None) -> dict | None:
    """O par de `enchantment_from_dict`."""
    if ench is None:
        return None
    return {"effect": ench.effect, "value": ench.value}
