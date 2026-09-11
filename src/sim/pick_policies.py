"""Políticas de escolha de carta: qual passiva e qual skill o bot leva.

O scout mede as escolhas do bot, não as do jogador. Com uma política só, "esta
passiva é ignorada" mistura duas causas muito diferentes: a carta é fraca, ou a
carta é boa para uma build que aquele bot não joga. Ranking de carta tirado de
um único jeito de jogar é o ranking daquele jeito de jogar, não do conteúdo.

Com várias políticas o scout consegue separar:

- ignorada por **todas** as políticas deliberadas: carta fraca de verdade;
- levada por **uma** e recusada pelas outras: identidade de build, o que é
  saudável e não deve ser corrigido;
- levada por **todas**: é a resposta certa, e portanto não é escolha.

A política `random` é o grupo de controle. Ela escolhe uniformemente entre as
três cartas oferecidas, então dá a taxa de referência (cerca de 33%) e permite
medir o **valor da escolha**: se jogar deliberadamente não vai mais longe que
sortear, o sistema de escolha é decorativo.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

# Ordem de preferência de passivas por intenção de build. A mesma carta pode ser
# a primeira de uma lista e a última de outra — é isso que revela identidade.
PASSIVE_PRIORITIES: dict[str, tuple[str, ...]] = {
    # Manter a run viva. Numa masmorra de permadeath decidida por atrito, é o
    # que encerra a run que importa primeiro.
    "survival": (
        "max_hp",
        "defense",
        "damage_reduction",
        "death_ignore",
        "strength",
        "crit_chance",
        "agility",
        "potion_heal_bonus",
        "max_mp",
        "dodge_chance",
        "stun_chance",
        "essence_bonus",
        "gold_drop_bonus",
    ),
    # Encurtar o combate. Menos turnos é menos dano recebido, por outro caminho.
    "offense": (
        "strength",
        "crit_chance",
        "stun_chance",
        "agility",
        "max_hp",
        "damage_reduction",
        "defense",
        "death_ignore",
        "max_mp",
        "dodge_chance",
        "potion_heal_bonus",
        "essence_bonus",
        "gold_drop_bonus",
    ),
    # Acelerar a progressão e a economia, apostando que nível e equipamento
    # resolvem melhor que atributo bruto.
    "economy": (
        "essence_bonus",
        "gold_drop_bonus",
        "potion_heal_bonus",
        "max_mp",
        "max_hp",
        "defense",
        "strength",
        "damage_reduction",
        "crit_chance",
        "agility",
        "dodge_chance",
        "stun_chance",
        "death_ignore",
    ),
}

# Ordem de preferência de tipo de skill por intenção.
SKILL_PRIORITIES: dict[str, tuple[str, ...]] = {
    "survival": ("heal", "damage_reduction", "buff", "status", "damage"),
    "offense": ("damage", "status", "heal", "damage_reduction", "buff"),
    "economy": ("damage", "buff", "status", "heal", "damage_reduction"),
}

# Valor atribuído a uma skill de status, que não tem valor numérico. Controle
# vale como um dano médio: nem descartável, nem a melhor carta da mão.
STATUS_SKILL_VALUE = 25.0

# Quantas skills o herói carrega ao mesmo tempo. Era um 4 literal dentro da
# política de escolha, onde ninguém procuraria pelo teto de deck do jogo.
MAX_EQUIPPED_SKILLS = 4


def _skill_value(skill) -> float:
    """Valor bruto de uma skill, para comparar candidatas."""
    try:
        return float(skill.effect_value)
    except (TypeError, ValueError):
        return STATUS_SKILL_VALUE


@dataclass(frozen=True)
class PickPolicy:
    """Como o bot escolhe entre as cartas oferecidas."""

    name: str
    deliberate: bool = True

    def pick_passive(self, hero, choices: list, rng: random.Random):
        """Escolhe uma passiva entre as oferecidas."""
        if not choices:
            return None
        if not self.deliberate:
            return rng.choice(choices)

        for efeito in PASSIVE_PRIORITIES[self.name]:
            mesmas = [c for c in choices if c.effect_type == efeito]
            if mesmas:
                # Dentro de um mesmo efeito o valor é comparável (+15 HP e
                # +200 HP medem a mesma coisa), então o desempate é por valor.
                # Sem isso a ordem da oferta decidia, e uma Lendária aparecia
                # como "carta ignorada" metade das vezes em que era oferecida
                # ao lado da Comum do mesmo tipo — defeito do medidor lido
                # como defeito do conteúdo.
                return max(mesmas, key=lambda c: _numeric(c.effect_value))
        return max(choices, key=lambda c: _numeric(c.effect_value))

    def pick_skill(self, hero, choices: list, rng: random.Random):
        """Escolhe uma skill nova e o slot que ela substitui.

        Devolve `(None, None)` quando nenhuma oferta supera o que o herói já tem
        — trocar por algo pior é desperdiçar a escolha, e um bot que troca
        sempre mede um jogador que não olha a carta.

        A comparação é feita pela MESMA chave que escolhe a carta: primeiro o
        lugar do tipo na ordem da intenção, e só dentro do mesmo tipo pelo valor.
        Antes a troca comparava `effect_value` puro entre tipos diferentes, e
        esses números não medem a mesma coisa: 140 de uma skill de dano é
        percentual de dano, 30 de um buff é ponto de atributo, e status não tem
        número nenhum (entra com a constante 25). Com o deck cheio de skills de
        dano, isso barrava 22 das 24 cartas de status, buff e cura — nenhuma
        alcançava os 60 da pior skill de dano.

        O efeito no relatório era pior que no jogo: o scout declarava nove
        dessas cartas "recusadas por toda intenção", que é o seu veredito de
        carta fraca. Elas nunca tinham sido oferecidas a um bot capaz de aceitá-las.
        """
        if not choices:
            return None, None

        if not self.deliberate:
            # Grupo de controle: escolhe e troca ao acaso. Se ele também filtrasse
            # a troca por valor, o "acaso" herdaria a preferência por dano e
            # deixaria de ser referência para o valor da escolha deliberada.
            nova = rng.choice(choices)
            if len(hero.skills) < MAX_EQUIPPED_SKILLS:
                return nova, max(hero.skills, default=0) + 1
            return nova, rng.choice(sorted(hero.skills))

        ordem = SKILL_PRIORITIES[self.name]

        def chave(skill) -> tuple[int, float]:
            """Menor é melhor: tipo preferido primeiro, valor alto depois."""
            posicao = ordem.index(skill.effect_type) if skill.effect_type in ordem else len(ordem)
            return (posicao, -_skill_value(skill))

        nova = min(choices, key=chave)

        if len(hero.skills) < MAX_EQUIPPED_SKILLS:
            return nova, max(hero.skills, default=0) + 1

        pior = max(hero.skills, key=lambda k: chave(hero.skills[k]))
        if chave(nova) >= chave(hero.skills[pior]):
            return None, None
        return nova, pior


def _numeric(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


POLICIES: dict[str, PickPolicy] = {
    "survival": PickPolicy("survival"),
    "offense": PickPolicy("offense"),
    "economy": PickPolicy("economy"),
    # Grupo de controle: escolhe ao acaso entre as três cartas oferecidas.
    "random": PickPolicy("random", deliberate=False),
}

# A política padrão da simulação de balanceamento. As outras existem para o
# scout comparar, não para trocar a calibração.
DEFAULT_PICK_POLICY = "survival"

# As que representam um jogador com intenção. `random` fica de fora: ela é a
# referência contra a qual as deliberadas são medidas.
DELIBERATE_POLICIES = tuple(name for name, p in POLICIES.items() if p.deliberate)


def get_pick_policy(name: str) -> PickPolicy:
    """Resolve o nome da política. Nome desconhecido é erro, não silêncio."""
    if name not in POLICIES:
        raise ValueError(
            f"Política de escolha desconhecida: {name!r}. Use uma de {sorted(POLICIES)}."
        )
    return POLICIES[name]
