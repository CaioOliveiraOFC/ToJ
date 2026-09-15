"""Gemas: a segunda dimensão de progressão do equipamento.

Gema NÃO é `+N`. O rank fortalece a peça — a base que ela já declara, vezes um
multiplicador. A gema traz poder de FORA e usa a peça só como suporte: ela
acrescenta um percentual ao atributo do personagem, e o mesmo Rubi vale o mesmo
encaixado numa espada ou num anel.

As duas progressões vivem em campos diferentes do exemplar, resolvem por
caminhos diferentes e usam curvas diferentes. É de propósito: quando
Encantamentos chegarem, precisa continuar sendo possível responder de onde cada
ponto de poder veio.
"""

from __future__ import annotations

from src.shared.constants import GEM_DROP_CHANCE, GEM_LEVEL_FLOORS_PER_RANK
from src.shared.formulas import gem_percent

# Cada tipo de gema alimenta UM atributo, pela mesma chave que
# `Player.EQUIP_STAT_SOURCES` usa. Seis tipos, um por atributo: sem sobreposição,
# ninguém precisa decidir qual das duas gemas de força é a boa.
GEM_TYPES: dict[str, str] = {
    "Rubi": "st",
    "Safira": "mg",
    "Esmeralda": "ag",
    "Topázio": "df",
    "Ametista": "mp",
    "Ônix": "hp",
}


class Gem:
    """Um exemplar de gema. Tipo e nível, e mais nada.

    Sem `enhancement_level`: o nível da gema JÁ é a progressão dela, e um
    "Rubi +10" seriam duas escadas para a mesma pedra. `+N` é exclusivo de
    equipamento.
    """

    __slots__ = ("gem_type", "level")

    def __init__(self, gem_type: str, level: int = 1) -> None:
        if gem_type not in GEM_TYPES:
            raise ValueError(
                f"Tipo de gema desconhecido: {gem_type!r}. Conhecidos: {', '.join(GEM_TYPES)}"
            )
        if int(level) < 1:
            raise ValueError(f"Nível de gema começa em 1, não {level!r}")
        self.gem_type: str = gem_type
        self.level: int = int(level)

    @property
    def stat(self) -> str:
        """A chave de atributo que esta gema alimenta."""
        return GEM_TYPES[self.gem_type]

    @property
    def percent(self) -> float:
        """Quanto ela acrescenta ao atributo, em pontos percentuais."""
        return gem_percent(self.level)

    @property
    def display_name(self) -> str:
        return f"{self.gem_type} Nv. {self.level}"

    def __repr__(self) -> str:  # pragma: no cover - conveniência de depuração
        return f"Gem({self.gem_type!r}, {self.level})"


def create_gem(gem_type: str, level: int = 1) -> Gem:
    """Constrói uma gema. Ponto de entrada único, para drop e para teste."""
    return Gem(gem_type, level)


def gem_from_dict(dados) -> Gem | None:
    """Reconstrói uma gema salva. `None` para socket vazio ou dado inválido."""
    if not isinstance(dados, dict):
        return None
    try:
        return Gem(str(dados.get("gem_type", "")), int(dados.get("level", 1)))
    except (ValueError, TypeError):
        return None


def gem_to_dict(gem: Gem | None) -> dict | None:
    """O par de `gem_from_dict`."""
    if gem is None:
        return None
    return {"gem_type": gem.gem_type, "level": gem.level}


def gem_max_level(dungeon_level: int) -> int:
    """Teto de nível da gema encontrada neste andar: `1 + andar // 5`.

    Bem mais lento que o andar, e de propósito. Com o teto em `andar`, o andar 20
    já entregaria uma pedra Nv.20 — poder demais entrando no jogo antes de
    alguém ter medido o sistema. Continua sem teto absoluto, então acompanha a
    masmorra infinita: andar 50 dá Nv.10–11.
    """
    return 1 + max(1, int(dungeon_level)) // GEM_LEVEL_FLOORS_PER_RANK


def random_gem(dungeon_level: int, rng) -> Gem:
    """Uma gema do patamar deste andar. Tipo sorteado entre os seis."""
    teto = gem_max_level(dungeon_level)
    return Gem(rng.choice(sorted(GEM_TYPES)), rng.randint(max(1, teto - 1), teto))


def roll_gem_drop(dungeon_level: int, rng) -> Gem | None:
    """A rolagem de gema de UMA vitória. `None` quase sempre.

    INDEPENDENTE do loot de item: o monstro pode largar os dois na mesma morte, e
    a gema nunca ocupa o lugar do item. São duas perguntas diferentes feitas ao
    mesmo cadáver.
    """
    if rng.random() >= GEM_DROP_CHANCE:
        return None
    return random_gem(dungeon_level, rng)
