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
from dataclasses import dataclass

from src.content.factories.archetypes import spawn_by_role
from src.mechanics.battle import run_battle
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
from src.sim.policies import smart_policy
from src.sim.rng_guard import rng_isolado

ABAIXO = "ABAIXO"
EQUIVALENTE = "EQUIVALENTE"
SUPEROU = "SUPEROU"


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
    """O veredito de `bot_power / benchmark_power`.

    Sem campo de confiabilidade: a guarda de kit foi removida. Deck diferente,
    mana diferente e equipamento diferente NÃO tornam dois gladiadores
    incomparáveis — são exatamente o que `overall_power` existe para medir, e
    vetá-los era a régua se recusando a responder a própria pergunta.
    """

    relativo: float
    veredito: str


def _normalizado(personagem):
    """A BUILD do personagem, sem nada que seja estado da run.

    UMA normalização, usada pelo duelo E pela chave do cache. Enquanto forem dois
    caminhos eles divergem, e a divergência é silenciosa: o cache devolve um
    número plausível medido sobre outra coisa.

    O que sai, e por quê:

    - `rest()` devolve HP/MP ao teto e limpa `active_effects` e `active_buffs`.
      Sem isso o poder cairia porque o herói estava ferido, e a razão de runway
      já mede o desgaste — somar os dois contaria o mesmo atrito duas vezes.
    - `skill_cooldowns` é limpo à mão porque `rest()` NÃO o limpa, e
      `policies._usable_skills` consulta recarga: sem isto o número dependia do
      instante da run em que a medição caiu.
    - `_death_ignore_used` volta a falso. `run_battle` já o zera na entrada do
      combate; normalizar aqui torna o protótipo autocontido em vez de depender
      desse detalhe do motor.
    - Consumíveis saem. Poção e elixir são recurso descartável da run, não força
      do gladiador. A classificação é a CANÔNICA — `Item.is_potion`, que é
      `bool(self.consumable)` —, nunca uma lista de nomes: adivinhar por
      `effect_type` já transformou amuleto com bônus de vida em poção uma vez.
      É o mesmo campo que `policies._consumables` filtra, então some exatamente
      o que o piloto de medição conseguiria beber.

    `Player.rest()` não é alterado globalmente: a normalização pertence à régua.

    `deepcopy` porque `run_battle` machuca quem entra nele, e quem chega aqui
    pode ser o herói da partida em andamento.
    """
    clone = copy.deepcopy(personagem)
    clone.rest()
    clone.skill_cooldowns.clear()
    clone._death_ignore_used = False
    clone.inventory = [item for item in clone.inventory if not item.is_potion]
    return clone


def _maos(heroi) -> tuple:
    """As mãos, no que elas decidem: se a carta do deck pode ser lançada.

    `Player.can_use_skill` lê três coisas das posições de mão — quantas peças
    estão empunhadas (`two_weapons`), `hands_required` de cada uma e o
    `hand_type` de cada uma. Duas builds de números idênticos com espada ou com
    adaga têm decks utilizáveis diferentes, e sem isto dividiriam cache.

    A OCUPAÇÃO entra e não é redundante: `hands_required(None)` devolve 1 e um
    `hand_type` ausente vira `""`, então a mão vazia assinaria `("", 1)` —
    idêntico a uma arma de uma mão sem `hand_type`. Sem o booleano, empunhar uma
    arma e empunhar duas colidiriam, que é justamente a contagem que
    `req.two_weapons` faz.
    """
    maos = []
    for posicao in heroi.HAND_POSITIONS:
        peca = heroi.equipment.get(posicao)
        maos.append(
            (
                peca is not None,
                str(getattr(peca, "hand_type", "") or ""),
                int(heroi.hands_required(peca)) if peca is not None else 0,
            )
        )
    return tuple(maos)


def assinatura_de_build(personagem) -> tuple:
    """A identidade ESTRUTURAL do personagem, para efeito de poder.

    Calculada sobre o clone normalizado, e não sobre o personagem cru: do jeito
    cru ela carregava estado temporário, porque `get_st`/`get_mg`/`get_ag`/
    `get_df` somam buffs e `fx.combat_modifier` soma `active_buffs` junto com
    passiva e equipamento. Assinar o que o duelo mede é o que garante que a
    chave e o valor nunca falem de personagens diferentes.

    Assina o que o DUELO lê, e não a lista de peças: nível, `+N`, gema e
    encantamento chegam já resolvidos dentro dos atributos e dos canais. A
    mochila não entra — item não equipado não toca o combate.

    Quatro coisas entram por terem sido colisões reais:

    - `get_avg_damage()`, que é o BASE_POWER canônico. Ele passa por
      `weighted_power`, que aplica `weapon_percent()` por cima da soma ponderada;
      `get_st()` sozinho não carrega isso, então duas builds de atributos iguais
      com armas de `damage_bonus` diferente tinham BASE diferente e a MESMA
      assinatura.
    - `_maos()`, pelo requisito de carta (acima).
    - A ORDEM do deck, SEM `sorted`. `policies._melhor` é `max(candidatos, key=…)`
      sobre uma lista tirada de `hero.skills.values()`, e `max` devolve o
      PRIMEIRO máximo: a ordem dos slots é o desempate, como o docstring de
      `_melhor` declara. As mesmas quatro cartas em ordens diferentes jogam
      diferente.
    - As passivas, estas SIM ordenadas. `get_passive_bonus` soma e
      `_apply_passive_stats` acumula flat, então a ordem delas não muda nada, e
      ordenar mantém duplicatas comparáveis. A assimetria com o deck é
      deliberada: cada lado segue o que a mecânica faz com ele.
    """
    return _assinatura_do_clone(_normalizado(personagem))


def _assinatura_do_clone(h) -> tuple:
    """A assinatura de um clone JÁ normalizado.

    Existe para que `overall_power` normalize UMA vez e use o mesmo clone para a
    chave e para os duelos. Corpo único: `assinatura_de_build` é esta função
    depois de `_normalizado`, e não uma segunda cópia da lista de campos.
    """
    return (
        h.get_classname(),
        int(h.get_level()),
        int(h.base_hp),
        int(h.base_mp),
        int(h.get_st()),
        int(h.get_mg()),
        int(h.get_ag()),
        int(h.get_df()),
        int(h.get_avg_damage()),
        tuple(h.active_skill_ids()),
        tuple(sorted(p.id for p in getattr(h, "passives", []))),
        _maos(h),
        tuple((canal, float(fx.combat_modifier(h, canal))) for canal in _CANAIS_DE_COMBATE),
        int(getattr(h, "magic_shield_percent", 0) or 0),
    )


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
    # UMA normalização: o mesmo clone responde pela chave do cache e entra nos
    # duelos. Chave e valor não conseguem falar de personagens diferentes.
    prototipo = _normalizado(personagem)
    chave = (_assinatura_do_clone(prototipo), duelos, semente)
    if usar_cache and chave in _cache:
        return _cache[chave]

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


def classificar(relativo: float) -> str:
    """Onde o personagem cai em relação ao alvo, dentro da banda aprovada."""
    if relativo < 1 - ARENA_EQUIVALENCE_BAND:
        return ABAIXO
    if relativo > 1 + ARENA_EQUIVALENCE_BAND:
        return SUPEROU
    return EQUIVALENTE


def comparar(personagem, benchmark, **kwargs) -> Comparacao:
    """`bot_power / benchmark_power`, medidos pela mesma régua.

    Não há guarda na frente. A antiga `kit_comparavel` vetava a comparação
    quando os dois lados diferiam em deck, em poção ou na mana que o deck exige,
    e marcava o resultado como não-confiável — 93,7% das vezes, medido em 378
    momentos reais, e 81% disso só por poção de mana.

    Ela caiu por duas razões. A primeira é que consumível saiu da régua, então a
    diferença que dominava a reprovação deixou de existir. A segunda é mais
    forte: deck, mana e equipamento diferentes NÃO tornam dois gladiadores
    incomparáveis — são exatamente o que `overall_power` existe para medir.
    Vetá-los era a régua se recusando a responder a pergunta que ela foi feita
    para responder.
    """
    meu = overall_power(personagem, **kwargs).nivel_equivalente
    alvo = overall_power(benchmark, **kwargs).nivel_equivalente
    relativo = meu / alvo if alvo > 0 else 0.0
    return Comparacao(relativo, classificar(relativo))


def limpar_cache() -> None:
    """Esvazia o cache de medições. Existe para o teste, não para a run."""
    _cache.clear()
