"""Poder geral do personagem, na unidade que o jogo já tem: NÍVEL DE MONSTRO.

    overall_power(personagem) = L ∈ ℝ tal que
        P(o personagem vence um duelo 1×1 contra o boneco de nível L) = 0,50

A régua anterior era determinística e media só o ataque básico: enxergava BASE,
+MULT, ×MULT, crítico, acerto, HP, defesa e mitigação, e era CEGA a skill, mana,
sustain, poção, status, `death_ignore`, Égide e iniciativa. Medido, ela errava de
1,036× a 1,684× conforme o equipamento — não um deslocamento constante que se
pudesse corrigir, mas um erro que muda de tamanho justamente entre os
personagens que a Arena existe para comparar. Ela invertia pares reais: um Mago
nível 15 pelado lia 1,070 contra um nível 12 equipado (SUPEROU) onde o combate
de verdade diz 0,888 (ABAIXO).

Aqui quem converte é o DUELO. Nenhum peso é inventado porque nenhuma conversão é
escrita: quanto 10 de mana valem em HP é o que o combate mostrar quando a mana
acabar. `run_battle` executa skill, custo de mana, regeneração, roubo de vida,
poção, sangramento, veneno, atordoamento, medo, resistência, `death_ignore`,
Égide, iniciativa e interações de golpe — todos entram por serem executados, não
por serem pontuados.

A taxa de vitória NÃO é a métrica; é só o comparador da busca. Medir "quantos %
eu venço contra o nível 12" satura em 0% e 100% e não é escala nenhuma. Medir
"contra que nível eu empato" usa a mesma saturação a favor: a curva é monótona e
cruza 0,50 uma vez só.

Níveis fracionários são legítimos e não pedem mudança no motor: a curva de
orçamento de monstro (`shared.formulas.geometric`) é contínua e aceita `float`.
Isso remove a última escolha arbitrária que sobrava — não há interpolação entre
níveis inteiros para inventar. O `float` vive DENTRO desta medição; nenhum
monstro de nível quebrado é spawnado na run.

Fronteira: este módulo mede o PERSONAGEM, não a inteligência do bot. O piloto de
medição é `sim.policies.smart_policy`, que é congelado e mora fora de
`sim/bot/` — evoluir o cérebro do bot não move `overall_power`.
"""

from __future__ import annotations

import copy
import random
from collections import Counter
from dataclasses import dataclass

from src.content.factories.archetypes import spawn_by_role
from src.mechanics.battle import run_battle
from src.mechanics.combat import skill_mana_cost
from src.shared import effects as fx
from src.shared.constants import (
    ARENA_BRACKET_GROWTH,
    ARENA_DUELS_PER_PROBE,
    ARENA_EQUIVALENCE_BAND,
    ARENA_LEVEL_BRACKET,
    ARENA_LEVEL_FLOOR,
    ARENA_LEVEL_HARD_LIMIT,
    ARENA_LEVEL_TOLERANCE,
    ARENA_MEASURE_SEED,
    ARENA_REFERENCE_ROLE,
    ARENA_WIN_TARGET,
)

# `_consumables` é privada de uma política congelada, e é de propósito que a
# guarda de kit leia por ela: "kit comparável" tem de significar comparável PARA
# O PILOTO QUE VAI MEDIR. Uma segunda leitura do inventário aqui poderia contar
# como recurso algo que `smart_policy` nunca usaria, e a guarda passaria a
# liberar comparações que o duelo não sustenta.
from src.sim.policies import _consumables, smart_policy
from src.sim.rng_guard import rng_isolado

ABAIXO = "ABAIXO"
EQUIVALENTE = "EQUIVALENTE"
SUPEROU = "SUPEROU"
NAO_CONFIAVEL = "NAO_CONFIAVEL"


class PoderForaDeEscalaError(RuntimeError):
    """A busca bateu no limite técnico sem achar o nível de equilíbrio.

    Erro, e não um número: devolver o próprio limite faria dois personagens
    incomparáveis lerem o mesmo valor, que é precisamente o que a expansão do
    bracket existe para impedir.
    """


# Os modificadores de combate que entram na assinatura de build. São os canais
# por onde equipamento, encantamento e passiva mudam um golpe sem mudar um
# atributo — sem eles, dois personagens com os mesmos atributos e decks
# diferentes em crítico dividiriam a mesma entrada de cache.
_CANAIS_DE_COMBATE = (
    "crit_chance",
    "crit_damage",
    "damage_percent",
    "damage_reduction",
    "evasion",
    "precision",
    "life_steal",
    "mana_regen",
    "death_ignore",
)

_cache: dict[tuple, "PoderGeral"] = {}


@dataclass(frozen=True)
class PoderGeral:
    """O poder do personagem e o que custou medi-lo."""

    nivel_equivalente: float
    duelos: int
    sondagens: int


@dataclass(frozen=True)
class Comparacao:
    """O veredito de `bot_power / benchmark_power`, e se dá para confiar nele."""

    relativo: float
    veredito: str
    confiavel: bool
    motivo: str


def assinatura_de_build(personagem) -> tuple:
    """A identidade do personagem para efeito de poder.

    Assina o que o DUELO lê, não a lista de peças: atributos já resolvidos
    (nível, equipamento, `+N`, gema e encantamento chegam dentro deles), deck,
    passivas, consumíveis e os modificadores de combate. Assinar o inventário
    cru deixaria de fora o aprimoramento; assinar só os atributos deixaria de
    fora o crítico.
    """
    consumiveis = Counter(
        getattr(item, "name", "?")
        for item in getattr(personagem, "inventory", [])
        if getattr(item, "consumable", False)
    )
    return (
        personagem.get_classname(),
        int(personagem.get_level()),
        int(personagem.base_hp),
        int(personagem.base_mp),
        int(personagem.get_st()),
        int(personagem.get_mg()),
        int(personagem.get_ag()),
        int(personagem.get_df()),
        tuple(sorted(personagem.active_skill_ids())),
        tuple(sorted(p.id for p in getattr(personagem, "passives", []))),
        tuple(sorted(consumiveis.items())),
        tuple(
            (canal, float(fx.combat_modifier(personagem, canal))) for canal in _CANAIS_DE_COMBATE
        ),
        int(getattr(personagem, "magic_shield_percent", 0) or 0),
    )


def _prototipo(personagem):
    """A cópia em repouso que o duelo vai usar, sem tocar no personagem da run.

    `deepcopy` porque `run_battle` machuca quem entra nele, e o herói que chega
    aqui pode ser o da partida em andamento. `rest()` porque `overall_power` é
    propriedade da BUILD: o desgaste do momento é o que a razão de runway mede,
    e somar as duas coisas num número só contaria o mesmo atrito duas vezes.
    """
    clone = copy.deepcopy(personagem)
    clone.rest()
    return clone


def _taxa_de_vitoria(prototipo, nivel: float, duelos: int, semente: int) -> float:
    """Fração dos duelos 1×1 que o personagem vence contra o boneco neste nível."""
    vitorias = 0
    for i in range(duelos):
        # A camada de conteúdo sorteia pelo gerador global; semeá-lo aqui é o que
        # torna a medição repetível. `rng_isolado` no chamador devolve o estado.
        random.seed(semente + i)
        heroi = copy.deepcopy(prototipo)
        monstro = spawn_by_role(ARENA_REFERENCE_ROLE, nivel)
        run_battle(heroi, [monstro], smart_policy, rng=random.Random(semente + i))
        if heroi.isalive and heroi.get_hp() > 0 and monstro.get_hp() <= 0:
            vitorias += 1
    return vitorias / duelos


def overall_power(
    personagem,
    *,
    duelos: int = ARENA_DUELS_PER_PROBE,
    semente: int = ARENA_MEASURE_SEED,
    usar_cache: bool = True,
) -> PoderGeral:
    """O nível de monstro contra o qual este personagem fica em equilíbrio.

    Não consome sorteio da run e não altera o personagem: o gerador global volta
    ao estado anterior e o duelo roda sobre uma cópia em repouso.
    """
    chave = (assinatura_de_build(personagem), duelos, semente)
    if usar_cache and chave in _cache:
        return _cache[chave]

    prototipo = _prototipo(personagem)
    sondagens = 0

    with rng_isolado():

        def taxa(nivel: float) -> float:
            nonlocal sondagens
            sondagens += 1
            return _taxa_de_vitoria(prototipo, nivel, duelos, semente)

        baixo, alto = ARENA_LEVEL_FLOOR, ARENA_LEVEL_BRACKET
        if taxa(baixo) < ARENA_WIN_TARGET:
            # Perde até para o menor monstro que o jogo constrói. O piso é a
            # resposta honesta; inventar um número abaixo dele seria extrapolar
            # uma curva de orçamento que não existe.
            leitura = PoderGeral(baixo, sondagens * duelos, sondagens)
        else:
            # O bracket inicial é PALPITE, não teto. Enquanto o personagem
            # continuar vencendo no topo, o topo sobe: a dungeon é infinita, e um
            # teto fixo faria dois campeões diferentes saturarem no mesmo número
            # — `relative_power` entre eles daria 1,000 sem que nenhum dos dois
            # tivesse sido medido. A expansão é mecanismo de BUSCA e não toca em
            # fórmula, piloto, amostra nem banda.
            while taxa(alto) >= ARENA_WIN_TARGET:
                if alto >= ARENA_LEVEL_HARD_LIMIT:
                    # Trava técnica contra laço infinito. Ela FALHA em vez de
                    # devolver o próprio limite: um teto que vira resultado é
                    # exatamente o defeito que a expansão existe para corrigir,
                    # e devolvê-lo calado seria trocar um número medido por um
                    # número escolhido.
                    raise PoderForaDeEscalaError(
                        f"{personagem.get_classname()} ainda vence no nível "
                        f"{alto:.0f}, o limite técnico da busca. O resultado não "
                        f"foi medido — aumente ARENA_LEVEL_HARD_LIMIT ou "
                        f"investigue por que o personagem não tem oponente."
                    )
                baixo = alto
                alto = min(alto * ARENA_BRACKET_GROWTH, ARENA_LEVEL_HARD_LIMIT)

            while alto - baixo > ARENA_LEVEL_TOLERANCE * (baixo + alto) / 2:
                meio = (baixo + alto) / 2
                if taxa(meio) >= ARENA_WIN_TARGET:
                    baixo = meio
                else:
                    alto = meio
            leitura = PoderGeral((baixo + alto) / 2, sondagens * duelos, sondagens)

    if usar_cache:
        _cache[chave] = leitura
    return leitura


def _lanca_alguma_carta(personagem) -> bool:
    """Se o deck tem ao menos uma carta que este personagem consegue lançar.

    Um deck que o teto de mana não paga, ou cujo requisito o equipamento não
    satisfaz, é kit no papel e nada no duelo.
    """
    return any(
        personagem.base_mp >= skill_mana_cost(personagem, carta) and personagem.can_use_skill(carta)
        for carta in personagem.skills.values()
    )


def kit_comparavel(um, outro) -> tuple[bool, str]:
    """Se os dois lados têm as mesmas CLASSES de recurso que o piloto sabe usar.

    Verifica DIRETAMENTE, ponta por ponta — deck, consumível, e mana que o
    próprio deck exige. Nada de proxy: "tem chave, está no andar 3 e está
    equipado" não prova kit comparável, porque um personagem pode ter as três
    coisas e ter gastado a última poção no andar anterior.

    Não é igualdade de inventário: é presença. `relative_power` só cancela a
    pilotagem quando os dois lados perdem as mesmas coisas ao trocar de piloto.
    Medido: entre personagens de kit compatível o resíduo entre pilotos tem
    mediana de 3,5% e máximo observado de 6,3% — o máximo NÃO cabe na banda de
    ±5%, e isso está aceito como limitação conhecida desta versão. Já comparando
    um personagem sem poção contra um benchmark com poção, o resíduo vai a ~20%:
    aí a razão deixa de medir poder e passa a medir a diferença de inventário.
    """
    faltas = []
    if bool(um.skills) != bool(outro.skills):
        faltas.append("deck")
    if bool(_consumables(um, ("max_hp",))) != bool(_consumables(outro, ("max_hp",))):
        faltas.append("poção de cura")
    if bool(_consumables(um, ("max_mp",))) != bool(_consumables(outro, ("max_mp",))):
        faltas.append("poção de mana")
    if _lanca_alguma_carta(um) != _lanca_alguma_carta(outro):
        faltas.append("mana para o deck")
    if not faltas:
        return True, ""
    return False, "kit incompatível: " + ", ".join(faltas)


def classificar(relativo: float) -> str:
    """Onde o personagem cai em relação ao alvo, dentro da banda aprovada."""
    if relativo < 1 - ARENA_EQUIVALENCE_BAND:
        return ABAIXO
    if relativo > 1 + ARENA_EQUIVALENCE_BAND:
        return SUPEROU
    return EQUIVALENTE


def comparar(personagem, benchmark, **kwargs) -> Comparacao:
    """`bot_power / benchmark_power`, com a guarda de kit na frente.

    Quando os kits não são comparáveis o veredito sai NAO_CONFIAVEL em vez de um
    número que já se sabe deslocado. Um veredito que se conhece errado não pode
    entrar na decisão de extrair disfarçado de medida.
    """
    meu = overall_power(personagem, **kwargs).nivel_equivalente
    alvo = overall_power(benchmark, **kwargs).nivel_equivalente
    relativo = meu / alvo if alvo > 0 else 0.0
    ok, motivo = kit_comparavel(personagem, benchmark)
    if not ok:
        return Comparacao(relativo, NAO_CONFIAVEL, False, motivo)
    return Comparacao(relativo, classificar(relativo), True, "")


def limpar_cache() -> None:
    """Esvazia o cache de medições. Existe para o teste, não para a run."""
    _cache.clear()
