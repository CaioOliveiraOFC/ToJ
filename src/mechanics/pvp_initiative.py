"""Iniciativa da Arena: quem age primeiro numa rodada de decisões simultâneas.

No PvE a ordem é fixa e sai da Agilidade (`battle.build_turn_order`). No duelo
ela representa a BUILD inteira, e não um atributo só:

    Build Initiative = média de sqrt(atributo / REF_atributo(nível))
                       sobre HP máx., MP máx., ST, MG, AG e DF efetivos

    Initiative Score = Build Initiative × Level Modifier

A raiz é o retorno decrescente: dobrar um atributo não dobra a contribuição
dele. Os seis pesam igual. HP e MP ATUAIS não entram — quem está ferido não
fica mais lento —, só os tetos.

Tudo aqui é contrato fechado:

- a fórmula, o modificador de nível e a ordem de desempate — score, depois AG
  relativa, depois `SeededCoinTieBreak`, o sorteio pela semente da partida;
- a referência global de cada nível, `foundation_reference`: a MÉDIA das três
  classes jogáveis no nível, pelos atributos-base delas (`CLASS_BASE`) e pelo
  crescimento canônico (`formulas.geometric`). É a mesma conta que o jogo faz
  para um herói sem equipamento, então a referência não tem número próprio.

Referências e desempate continuam injetáveis (`InitiativeReferences`,
`TieBreakPolicy`): é o que deixa um teste fixar a ordem que quer provar.

O poder geral contra o boneco (`overall_power`) é outra métrica e não entra
aqui.
"""

from __future__ import annotations

import functools
import math
import random
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal, Protocol

from src.entities.heroes import Mage, Rogue, Warrior
from src.shared.constants import PVP_INITIATIVE_LEVEL_CAP, PVP_INITIATIVE_LEVEL_STEP
from src.shared.formulas import geometric

# Os seis atributos da build, na ordem da fórmula. HP e MP entram pelo TETO.
INITIATIVE_STATS = ("hp", "mp", "st", "mg", "ag", "df")

# As classes cujos atributos-base formam a referência: as três jogáveis, as
# mesmas da criação de personagem (`engine/game_logic.CLASS_MAP`, conferido por
# teste). Uma referência por nível, comum às três.
REFERENCE_CLASSES = (Warrior, Mage, Rogue)


class MissingInitiativeReferenceError(LookupError):
    """O provedor não tem referência para o nível pedido.

    Erro, e não um valor inventado: completar a tabela por conta própria seria
    escolher a referência que ainda não foi aprovada.
    """


@dataclass(frozen=True)
class InitiativeReference:
    """A referência global de UM nível, comum às três classes."""

    hp: float
    mp: float
    st: float
    mg: float
    ag: float
    df: float

    def __post_init__(self) -> None:
        for nome in INITIATIVE_STATS:
            valor = getattr(self, nome)
            if not (isinstance(valor, (int, float)) and math.isfinite(valor) and valor > 0):
                raise ValueError(f"Referência de iniciativa inválida para {nome!r}: {valor!r}")


class InitiativeReferences(Protocol):
    """Quem fornece a referência de cada nível. Determinístico por contrato."""

    def at_level(self, level: int) -> InitiativeReference: ...


@functools.lru_cache(maxsize=None)
def foundation_reference(level: int) -> InitiativeReference:
    """A referência global do nível, derivada da fundação do jogo.

        REF_s(nível) = média, sobre Warrior, Mage e Rogue,
                       de geometric(CLASS_BASE[s], nível)

    É exatamente a média dos três heróis sem equipamento, passiva nem efeito
    naquele nível, calculada pela mesma função que dá ao herói os atributos
    dele — sem construir herói e sem simulação. Duas consequências, as duas
    verificadas por teste:

    - é NEUTRA: para cada atributo, a média das razões `classe / REF` das três
      classes nuas é 1;
    - não favorece nível: herói e referência crescem pela mesma razão, então a
      build nua de cada classe lê o mesmo número em qualquer nível. Quem leva o
      nível para a ordem é só o modificador de nível.

    Não tem teto próprio: vale em todo nível em que o crescimento do herói
    existe.
    """
    nivel = int(level)
    if nivel != level or nivel < 1:
        raise ValueError(f"Nível inválido para a referência de iniciativa: {level!r}")

    def media(stat: str) -> float:
        valores = (geometric(classe.CLASS_BASE[stat], nivel) for classe in REFERENCE_CLASSES)
        return math.fsum(valores) / len(REFERENCE_CLASSES)

    return InitiativeReference(**{stat: media(stat) for stat in INITIATIVE_STATS})


class FoundationReferences:
    """O provedor canônico: `foundation_reference`, calculada sob demanda."""

    def at_level(self, level: int) -> InitiativeReference:
        return foundation_reference(level)


# O provedor que o duelo usa quando ninguém injeta outro.
FOUNDATION_REFERENCES = FoundationReferences()


class ReferenceTable:
    """Provedor por tabela explícita, nível a nível. Para teste.

    Não tem valor próprio nem interpola: o nível que não está na tabela levanta
    `MissingInitiativeReferenceError`. Existe para um teste fixar uma ordem que
    as referências canônicas não fixariam.
    """

    def __init__(self, table: Mapping[int, InitiativeReference]) -> None:
        self._table = {int(nivel): ref for nivel, ref in table.items()}

    def at_level(self, level: int) -> InitiativeReference:
        try:
            return self._table[int(level)]
        except KeyError:
            raise MissingInitiativeReferenceError(
                f"Sem referência de iniciativa para o nível {level}."
            ) from None


def build_vector(hero) -> dict[str, float]:
    """Os seis atributos da build, já EFETIVOS.

    Os getters do herói somam equipamento, passiva, buff e efeito de atributo,
    então "modificador explícito aplicável" chega sozinho. HP e MP são os tetos
    (`base_hp`, `base_mp`), que também respondem a efeitos de recurso.
    """
    return {
        "hp": float(hero.base_hp),
        "mp": float(hero.base_mp),
        "st": float(hero.get_st()),
        "mg": float(hero.get_mg()),
        "ag": float(hero.get_ag()),
        "df": float(hero.get_df()),
    }


def build_initiative(hero, reference: InitiativeReference) -> float:
    """A média das raízes normalizadas. Sem arredondamento."""
    vetor = build_vector(hero)
    parcelas = (math.sqrt(max(0.0, vetor[s]) / getattr(reference, s)) for s in INITIATIVE_STATS)
    return math.fsum(parcelas) / len(INITIATIVE_STATS)


def level_modifier(own_level: int, opponent_level: int) -> float:
    """`1 + clamp(Δnível × STEP, −CAP, +CAP)`."""
    delta = (int(own_level) - int(opponent_level)) * PVP_INITIATIVE_LEVEL_STEP
    return 1 + max(-PVP_INITIATIVE_LEVEL_CAP, min(PVP_INITIATIVE_LEVEL_CAP, delta))


@dataclass(frozen=True)
class InitiativeReading:
    """A iniciativa de um lado nesta rodada, com as parcelas que a formaram.

    Uso interno e de auditoria: a UI normal não mostra iniciativa.
    """

    side: str
    level: int
    build: float
    level_modifier: float
    score: float
    relative_ag: float


def read_initiative(
    side: str, hero, opponent, references: InitiativeReferences
) -> InitiativeReading:
    """Lê a iniciativa de `hero` contra `opponent`, no estado atual dos dois."""
    nivel = int(hero.get_level())
    referencia = references.at_level(nivel)
    build = build_initiative(hero, referencia)
    modificador = level_modifier(nivel, int(opponent.get_level()))
    return InitiativeReading(
        side=side,
        level=nivel,
        build=build,
        level_modifier=modificador,
        score=build * modificador,
        # Desempate: a Agilidade relativa ao nível, na mesma normalização da
        # fórmula. Agilidade crua favoreceria o nível alto duas vezes.
        relative_ag=float(hero.get_ag()) / referencia.ag,
    )


class TieBreakPolicy(Protocol):
    """Decide a ordem quando score e AG relativa empatam exatamente."""

    def first(self, a: InitiativeReading, b: InitiativeReading, rng: random.Random) -> str: ...


class SeededCoinTieBreak:
    """O desempate definitivo: uma moeda do gerador da partida.

    A mesma semente dá sempre a mesma ordem. Só é consultada no empate
    absoluto — score e AG relativa exatamente iguais —, e não há alternância
    nem prioridade fixa por lado.
    """

    def first(self, a: InitiativeReading, b: InitiativeReading, rng: random.Random) -> str:
        return a.side if rng.random() < 0.5 else b.side


Criterion = Literal["score", "relative_ag", "fallback"]


@dataclass(frozen=True)
class InitiativeOrder:
    """A ordem travada da rodada e o critério que a decidiu."""

    first: str
    second: str
    decided_by: Criterion


def order_by_initiative(
    a: InitiativeReading,
    b: InitiativeReading,
    tie_break: TieBreakPolicy,
    rng: random.Random,
) -> InitiativeOrder:
    """Maior score primeiro; depois maior AG relativa; depois a política.

    Compara os `float` crus: nenhum arredondamento antes da comparação.
    """
    if a.score != b.score:
        primeiro, segundo = (a, b) if a.score > b.score else (b, a)
        return InitiativeOrder(primeiro.side, segundo.side, "score")
    if a.relative_ag != b.relative_ag:
        primeiro, segundo = (a, b) if a.relative_ag > b.relative_ag else (b, a)
        return InitiativeOrder(primeiro.side, segundo.side, "relative_ag")
    lado = tie_break.first(a, b, rng)
    if lado not in (a.side, b.side):
        raise ValueError(f"A política de desempate devolveu um lado desconhecido: {lado!r}")
    segundo = b.side if lado == a.side else a.side
    return InitiativeOrder(lado, segundo, "fallback")
