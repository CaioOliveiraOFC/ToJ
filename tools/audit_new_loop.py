"""Auditoria do novo loop: que tipo de run cada comportamento de jogador produz.

O simulador de balanceamento (`src/sim/`) enfrenta TODOS os monstros do andar.
O jogador não: ele anda por um mapa com paredes e pode contornar quem não quiser
encarar. Toda a fase estrutural terminou sem ninguém medir o que acontece quando
o comportamento muda — e o balanceamento global está prestes a ser calibrado.

Esta ferramenta não balanceia e não corrige nada. Ela roda quatro políticas de
jogador sobre o MAPA REAL e mede o que cada uma produz.

O que ela NÃO faz, de propósito:

  * não reimplementa combate, recompensa, loja, ferreiro, taxa de saída,
    Essência, features ou loot — chama as mesmas funções do jogo;
  * não constrói o andar por conta própria — chama `_setup_dungeon_map`, a mesma
    função que a Forge Run usa, então população, evento, serviços e pity saem da
    fonte única;
  * não busca rota própria — usa o Dijkstra de `map_analysis`;
  * não simula teclado. A política escolhe o OBJETIVO; o pathfinding resolve a
    rota.

As quatro políticas são INSTRUMENTO DE MEDIÇÃO, não bots finais. São regras
simples e legíveis de propósito: uma utility AI sofisticada mediria a qualidade
da IA, e a pergunta aqui é sobre o jogo.

    python -m tools.audit_new_loop --runs 50
"""

from __future__ import annotations

import argparse
import random
import statistics
from collections import Counter, defaultdict
from dataclasses import dataclass, field

from src.content.economy import exit_fee, pay_interest
from src.content.factories import features as feat
from src.content.factories.dungeons import (
    altar_hp_cost,
    apply_altar_blessing,
    apply_fountain_heal,
)
from src.content.floor_exit import effective_essence, unpaid_streak, use_exit
from src.content.shop import Shop
from src.engine.loop import _setup_dungeon_map
from src.engine.map_analysis import _dijkstra, campo_de_custo, rota_do_campo
from src.mechanics.battle import run_battle
from src.shared.constants import ESSENCE_PENALTY_FLOOR, FLOOR_CLEAR_RESTORE_PERCENT
from src.sim import progression
from src.sim.harness import _award, make_hero
from src.sim.policies import get_policy
from src.sim.toggles import Toggles

CLASSES = ("Warrior", "Mage", "Rogue")
POLITICAS = ("full_clear", "economica", "exploradora", "rush")
CHECKPOINTS = (5, 10, 20, 30, 50)

# Até onde a auditoria acompanha uma run. Não é teto do jogo: é a janela de
# medição, e o último checkpoint é 50.
MAX_ANDAR = 50

# Desvio que a política ECONÔMICA aceita para passar num serviço, em passos
# além da rota que ela já ia fazer. É parâmetro de AUDITORIA, não regra de
# jogo: existe para dar sentido a "se o desvio for pequeno", e o número está
# aqui em vez de espalhado para poder ser mexido num lugar só.
DESVIO_ACEITAVEL_ECONOMICA = 6


@dataclass
class Acumulador:
    """O que uma política produziu. Só contadores — nenhuma regra mora aqui."""

    runs: int = 0
    mortes: int = 0
    andar_alcancado: list[int] = field(default_factory=list)
    andar_da_morte: list[int] = field(default_factory=list)
    nivel_final: list[int] = field(default_factory=list)

    combates: int = 0
    andares_jogados: int = 0
    monstros_no_andar: int = 0
    monstros_enfrentados: int = 0
    passos: int = 0
    hp_fim_de_andar: list[float] = field(default_factory=list)

    # Economia sai do livro-caixa REAL do herói, nunca recontada aqui.
    ledger: Counter = field(default_factory=Counter)
    ouro_final: list[int] = field(default_factory=list)

    saidas_pagas: int = 0
    saidas_nao_pagas: int = 0
    streaks: list[int] = field(default_factory=list)
    streak_max: int = 0

    essencia_rolada: list[float] = field(default_factory=list)
    essencia_efetiva: list[float] = field(default_factory=list)
    andares_no_piso: int = 0

    # Serviços: apareceu / alcançável / visitado, e o desvio que custou.
    surgiu: Counter = field(default_factory=Counter)
    alcancavel: Counter = field(default_factory=Counter)
    visitado: Counter = field(default_factory=Counter)
    desvio: dict[str, list[int]] = field(default_factory=lambda: defaultdict(list))

    passivas_fim: list[int] = field(default_factory=list)
    skills_fim: list[int] = field(default_factory=list)

    checkpoints: dict[int, list[dict]] = field(default_factory=lambda: defaultdict(list))


def _pos(d: dict) -> tuple[int, int]:
    return (d["y"], d["x"])


def _rota(game_map, origem, destino, evitando: bool):
    """Rota e caminho. `evitando=True` prioriza menos combate; senão, menos passos."""
    return _dijkstra(game_map, origem, destino, por_combate=evitando)


def _casas_de(game_map, tipo: str) -> list[tuple[int, int]]:
    return [casa for casa, nome in game_map.features.items() if nome == tipo]


def _andar_ate(estado, destino, evitando: bool) -> bool:
    """Move o herói até a casa, lutando com quem estiver no caminho.

    Devolve False SÓ quando a run acabou (morte). Destino inalcançável devolve
    True: a política simplesmente não conseguiu ir, e isso não é morrer.

    Cada encontro tira o monstro do mapa, como `move_player` faz, então a rota
    seguinte já enxerga o andar mudado.
    """
    game_map = estado.game_map

    # O monstro pode estar NA CASA DO HERÓI: `place_enemy` evita outros monstros
    # mas não o jogador, então a casa inicial do andar pode nascer ocupada. Sem
    # este caso, a rota até ele tem comprimento zero, ninguém luta, e quem
    # procura "o monstro mais perto" recebe o mesmo alvo para sempre.
    if destino == estado.posicao:
        monstro = game_map.enemies_pos.get(destino)
        return _lutar(estado, monstro, destino) if monstro is not None else True

    rota, caminho = _rota(game_map, estado.posicao, destino, evitando)
    if not rota.alcancavel:
        return True

    for casa in caminho[1:]:
        estado.acc.passos += 1
        estado.posicao = casa
        monstro = game_map.enemies_pos.get(casa)
        if monstro is None:
            continue
        if not _lutar(estado, monstro, casa):
            return False
    return True


def _lutar(estado, monstro_tile, casa) -> bool:
    """Um duelo, pelas regras reais. Devolve False se o herói morreu."""
    hero, acc = estado.hero, estado.acc
    # `move_player` tira o monstro da casa AO COLIDIR, antes de saber o
    # resultado. Fazer igual aqui importa: no jogo, fugir também consome o
    # encontro, e recolocá-lo daria ao bot uma segunda chance que o jogador
    # não tem.
    estado.game_map.enemies_pos.pop(casa, None)
    estado.game_map.grid[casa[0]][casa[1]] = "D"

    monstros = [monstro_tile]
    resultado = run_battle(
        hero, monstros, lambda h, m, t: estado.decide(h, m, t), rng=estado.rng, publish=None
    )
    acc.combates += 1
    acc.monstros_enfrentados += 1
    if not hero.get_isalive() or hero.get_hp() <= 0:
        return False
    if resultado.hero_won:
        _award(
            hero,
            monstros,
            estado.essencia,
            estado.rng,
            estado.toggles,
            None,
            None,
            floor=estado.andar,
        )
    return True


def _usar_servico(estado, tipo: str, casa) -> None:
    """Abre o serviço em que o herói pisou, pelas regras reais do jogo."""
    game_map, hero, acc = estado.game_map, estado.hero, estado.acc
    if tipo == feat.SHOP:
        game_map.take_feature(casa)
        progression.visit_shop(hero, Shop(), estado.andar, estado.rng, estado.toggles, None)
    elif tipo == feat.FORGE:
        game_map.take_feature(casa)
        progression.visit_forge(hero, estado.andar, estado.toggles, None)
    elif tipo == feat.EXTRACTION:
        # `never_extract` nesta auditoria. A casa NÃO é consumida — recusar a
        # Extração a deixa no mapa, e é assim que o jogo se comporta.
        pass
    acc.visitado[tipo] += 1


def _usar_evento(estado) -> bool:
    """O evento da casa, pelas funções reais. False se o Altar matou o herói."""
    game_map, hero = estado.game_map, estado.hero
    tipo = game_map.event_type
    game_map.take_event()
    estado.acc.visitado["event"] += 1
    if tipo == "fountain":
        apply_fountain_heal(hero)
    elif tipo == "altar":
        hero.take_damage(altar_hp_cost(hero))
        apply_altar_blessing(hero)
        if hero.get_hp() <= 0:
            hero.set_isalive(False)
            return False
    elif tipo == "merchant":
        progression.visit_shop(hero, Shop(), estado.andar, estado.rng, estado.toggles, None)
    return True


# --------------------------------------------------------------------------
# As quatro políticas. Cada uma escolhe OBJETIVOS; o pathfinding faz a rota.
# --------------------------------------------------------------------------


def _monstro_mais_perto(estado):
    """A casa de monstro alcançável com menos passos, ou None.

    UMA varredura responde por todos os monstros. Perguntar um a um custava um
    Dijkstra por monstro, dentro de um laço que já roda uma vez por monstro.
    """
    campo = campo_de_custo(estado.game_map, estado.posicao, por_combate=False)
    visto = campo[0]
    alcancaveis = [(visto[c][0], c) for c in estado.game_map.enemies_pos if c in visto]
    return min(alcancaveis)[1] if alcancaveis else None


def _desvio_por(estado, casa) -> int | None:
    """Passos a mais para passar por esta casa antes da saída. None se inalcançável."""
    saida = _pos(estado.game_map.exit_pos)
    daqui = campo_de_custo(estado.game_map, estado.posicao, por_combate=True)
    ate, _ = rota_do_campo(daqui, casa, por_combate=True)
    direto, _ = rota_do_campo(daqui, saida, por_combate=True)
    if not ate.alcancavel or not direto.alcancavel:
        return None
    de_la, _ = _rota(estado.game_map, casa, saida, evitando=True)
    if not de_la.alcancavel:
        return None
    return max(0, ate.passos + de_la.passos - direto.passos)


def _servicos_presentes(estado) -> list[tuple[str, tuple[int, int]]]:
    alvos = [(tipo, casa) for casa, tipo in estado.game_map.features.items()]
    if estado.game_map.event_pos is not None:
        alvos.append(("event", estado.game_map.event_pos))
    return alvos


def _visitar(estado, tipo, casa, evitando: bool) -> bool:
    """Vai até a casa e usa o que há nela. False se a run acabou."""
    if not _andar_ate(estado, casa, evitando=evitando):
        return False
    if tipo == "event":
        return _usar_evento(estado)
    _usar_servico(estado, tipo, casa)
    return True


def _politica_rush(estado) -> bool:
    """Saída, e só. Ignora monstro, Loja, Ferreiro, Evento e Extração.

    Subir muitos andares assim NÃO é bug: ela abre mão de XP, ouro, loot, gemas,
    serviços e progressão. Medir esse preço é o ponto.
    """
    return _andar_ate(estado, _pos(estado.game_map.exit_pos), evitando=True)


def _politica_full_clear(estado) -> bool:
    """Limpa o andar: todo monstro alcançável, depois os serviços, depois a saída."""
    restantes = len(estado.game_map.enemies_pos)
    for _ in range(restantes + 1):
        casa = _monstro_mais_perto(estado)
        if casa is None:
            break
        if not _andar_ate(estado, casa, evitando=False):
            return False
    for tipo, casa in _servicos_presentes(estado):
        if tipo == feat.EXTRACTION:
            continue
        if _desvio_por(estado, casa) is None:
            continue
        if not _visitar(estado, tipo, casa, evitando=False):
            return False
    return _andar_ate(estado, _pos(estado.game_map.exit_pos), evitando=False)


def _politica_exploradora(estado) -> bool:
    """Quer o que o andar oferece: Loja, Ferreiro e Evento. Não limpa o andar.

    Aceita os combates que estiverem no caminho das features — usa a rota que
    evita combate, então luta por necessidade e não por escolha.
    """
    for tipo in (feat.SHOP, feat.FORGE, "event"):
        for nome, casa in _servicos_presentes(estado):
            if nome != tipo:
                continue
            if _desvio_por(estado, casa) is None:
                continue
            if not _visitar(estado, nome, casa, evitando=True):
                return False
    return _andar_ate(estado, _pos(estado.game_map.exit_pos), evitando=True)


def _politica_economica(estado) -> bool:
    """Luta quando existe motivo econômico, e não por hábito.

    Regra simples e explicável, de propósito:
      1. se o ouro não paga a taxa de saída, busca o monstro mais perto e luta,
         repetindo enquanto faltar dinheiro e houver monstro alcançável;
      2. passa num serviço se o desvio couber em `DESVIO_ACEITAVEL_ECONOMICA`;
      3. vai para a saída pela rota que evita combate.
    """
    taxa = exit_fee(estado.andar)
    # O teto de iterações é o número de monstros do andar: cada volta consome um
    # encontro, e um laço que depende só do ouro pendura a auditoria se algum
    # alvo não puder ser consumido.
    for _ in range(len(estado.game_map.enemies_pos) + 1):
        if estado.hero.coins >= taxa:
            break
        casa = _monstro_mais_perto(estado)
        if casa is None:
            break
        if not _andar_ate(estado, casa, evitando=False):
            return False

    for tipo, casa in _servicos_presentes(estado):
        if tipo == feat.EXTRACTION:
            continue
        desvio = _desvio_por(estado, casa)
        if desvio is None or desvio > DESVIO_ACEITAVEL_ECONOMICA:
            continue
        if not _visitar(estado, tipo, casa, evitando=True):
            return False

    return _andar_ate(estado, _pos(estado.game_map.exit_pos), evitando=True)


CONDUTORES = {
    "rush": _politica_rush,
    "full_clear": _politica_full_clear,
    "exploradora": _politica_exploradora,
    "economica": _politica_economica,
}


# --------------------------------------------------------------------------
# O motor: monta o andar real, deixa a política andar, fecha o andar.
# --------------------------------------------------------------------------


@dataclass
class Estado:
    hero: object
    game_map: object
    acc: Acumulador
    rng: random.Random
    decide: object
    toggles: Toggles
    andar: int = 1
    essencia: float = 1.0
    posicao: tuple[int, int] = (0, 0)


def _medir_geometria(estado) -> None:
    """Quanto o andar cobra para chegar em cada coisa. Antes de qualquer passo."""
    acc, game_map = estado.acc, estado.game_map
    acc.monstros_no_andar += len(game_map.enemies_pos)
    for tipo, casa in _servicos_presentes(estado):
        acc.surgiu[tipo] += 1
        desvio = _desvio_por(estado, casa)
        if desvio is not None:
            acc.alcancavel[tipo] += 1
            acc.desvio[tipo].append(desvio)


def _fechar_andar(estado) -> None:
    """Saída, descanso e juros — na ordem do jogo, pelas funções do jogo."""
    hero, acc = estado.hero, estado.acc
    saida = use_exit(hero, estado.andar)
    if saida.was_paid:
        acc.saidas_pagas += 1
    else:
        acc.saidas_nao_pagas += 1
    acc.streaks.append(saida.streak)
    acc.streak_max = max(acc.streak_max, saida.streak)

    hero.recover(FLOOR_CLEAR_RESTORE_PERCENT)
    pay_interest(hero, estado.andar)


def _snapshot(estado) -> dict:
    hero = estado.hero
    return {
        "nivel": hero.get_level(),
        "ouro": hero.coins,
        "passivas": len(hero.passives),
        "skills": len(hero.skills),
        "hp": hero.get_hp() / max(1, hero.base_hp),
    }


def rodar_uma(classe: str, politica: str, seed: int, max_andar: int = MAX_ANDAR) -> dict:
    """Uma run completa sob uma política. Devolve o que ela produziu."""
    random.seed(seed)
    rng = random.Random(seed)
    # `expected` é o cenário de referência do próprio simulador: o que um
    # jogador daquele nível plausivelmente teria. Com `naked` a auditoria mediria
    # um herói que ninguém joga — e o Full Clear morria no andar 1 em 100% das
    # runs, o que diz mais sobre o loadout que sobre a política.
    hero = make_hero(classe, 1, "expected")
    # A ASSINATURA DA CLASSE. `make_hero` não a entrega, então todo herói do
    # simulador nasce sem nenhuma skill — ver os achados A do relatório. Aqui a
    # auditoria chama o MÉTODO REAL do jogo, o mesmo que a criação de
    # personagem usa, em vez de montar um deck por fora.
    hero.learn_new_skills(show=False)
    acc = Acumulador()
    toggles = Toggles()
    decide = get_policy("smart")
    conduzir = CONDUTORES[politica]

    alcancado = 0
    morreu_em = None

    for andar in range(1, max_andar + 1):
        game_map = _setup_dungeon_map(andar, None, andar, hero)
        rolada = progression.floor_essence_multiplier(andar)
        efetiva = effective_essence(hero, rolada)
        acc.essencia_rolada.append(rolada)
        acc.essencia_efetiva.append(efetiva)
        if efetiva <= ESSENCE_PENALTY_FLOOR:
            acc.andares_no_piso += 1

        estado = Estado(
            hero=hero,
            game_map=game_map,
            acc=acc,
            rng=rng,
            decide=decide,
            toggles=toggles,
            andar=andar,
            essencia=efetiva,
            posicao=_pos(game_map.player_pos),
        )
        _medir_geometria(estado)
        acc.andares_jogados += 1

        vivo = conduzir(estado)
        if not vivo or not hero.get_isalive() or hero.get_hp() <= 0:
            morreu_em = andar
            break

        acc.hp_fim_de_andar.append(hero.get_hp() / max(1, hero.base_hp))
        _fechar_andar(estado)
        alcancado = andar
        if andar in CHECKPOINTS:
            acc.checkpoints[andar].append(_snapshot(estado))

    acc.runs = 1
    acc.andar_alcancado.append(alcancado)
    acc.nivel_final.append(hero.get_level())
    acc.ouro_final.append(hero.coins)
    acc.passivas_fim.append(len(hero.passives))
    acc.skills_fim.append(len(hero.skills))
    acc.streaks.append(unpaid_streak(hero))
    if morreu_em is not None:
        acc.mortes = 1
        acc.andar_da_morte.append(morreu_em)
    for chave, valor in hero.ledger.items():
        if isinstance(valor, (int, float)):
            acc.ledger[chave] += valor
    return {"acc": acc, "classe": classe, "politica": politica}


def _somar(destino: Acumulador, origem: Acumulador) -> None:
    destino.runs += origem.runs
    destino.mortes += origem.mortes
    destino.combates += origem.combates
    destino.andares_jogados += origem.andares_jogados
    destino.monstros_no_andar += origem.monstros_no_andar
    destino.monstros_enfrentados += origem.monstros_enfrentados
    destino.passos += origem.passos
    destino.saidas_pagas += origem.saidas_pagas
    destino.saidas_nao_pagas += origem.saidas_nao_pagas
    destino.andares_no_piso += origem.andares_no_piso
    destino.streak_max = max(destino.streak_max, origem.streak_max)
    for campo in (
        "andar_alcancado",
        "andar_da_morte",
        "nivel_final",
        "hp_fim_de_andar",
        "ouro_final",
        "streaks",
        "essencia_rolada",
        "essencia_efetiva",
        "passivas_fim",
        "skills_fim",
    ):
        getattr(destino, campo).extend(getattr(origem, campo))
    destino.ledger.update(origem.ledger)
    destino.surgiu.update(origem.surgiu)
    destino.alcancavel.update(origem.alcancavel)
    destino.visitado.update(origem.visitado)
    for tipo, valores in origem.desvio.items():
        destino.desvio[tipo].extend(valores)
    for andar, linhas in origem.checkpoints.items():
        destino.checkpoints[andar].extend(linhas)


# --------------------------------------------------------------------------
# Relatório
# --------------------------------------------------------------------------


def _media(valores) -> float:
    return statistics.fmean(valores) if valores else 0.0


def _mediana(valores) -> float:
    return statistics.median(valores) if valores else 0.0


def _por_run(acc: Acumulador, chave: str) -> float:
    return acc.ledger.get(chave, 0) / max(1, acc.runs)


def linha_resumo(nome: str, acc: Acumulador) -> str:
    mobs = acc.monstros_enfrentados / acc.monstros_no_andar * 100 if acc.monstros_no_andar else 0.0
    return (
        f"{nome:13} "
        f"{_media(acc.andar_alcancado):6.2f} "
        f"{_mediana(acc.andar_alcancado):7.1f} "
        f"{_media(acc.nivel_final):6.1f} "
        f"{acc.combates / max(1, acc.andares_jogados):8.2f} "
        f"{mobs:6.0f}% "
        f"{_media(acc.ouro_final):9.0f} "
        f"{_por_run(acc, 'gold_spent_on_enhancement'):7.0f} "
        f"{acc.ledger.get('gems_socketed', 0) / max(1, acc.runs):6.2f} "
        f"{_media(acc.essencia_efetiva):8.3f}"
    )


CABECALHO = (
    f"{'Política':13} {'Andar':>6} {'Mediana':>7} {'Nível':>6} "
    f"{'Comb/and':>8} {'% mobs':>7} {'Ouro fim':>9} {'+N ouro':>7} {'Gemas':>6} {'Essência':>8}"
)


def relatorio(por_politica: dict[str, Acumulador], por_classe: dict) -> list[str]:
    out = ["", "=" * 96, "AUDITORIA DO NOVO LOOP", "=" * 96, "", CABECALHO, "-" * 96]
    for nome in POLITICAS:
        out.append(linha_resumo(nome, por_politica[nome]))

    out += ["", "POR CLASSE", "-" * 96]
    for nome in POLITICAS:
        for classe in CLASSES:
            out.append(linha_resumo(f"{nome[:8]}/{classe[:6]}", por_classe[(nome, classe)]))

    out += ["", "SERVIÇOS — apareceu / alcançável / visitado / desvio médio (passos)", "-" * 96]
    for nome in POLITICAS:
        acc = por_politica[nome]
        partes = []
        for tipo in (feat.SHOP, feat.FORGE, "event", feat.EXTRACTION):
            surgiu = acc.surgiu.get(tipo, 0)
            alc = acc.alcancavel.get(tipo, 0)
            vis = acc.visitado.get(tipo, 0)
            desv = _media(acc.desvio.get(tipo, []))
            partes.append(f"{tipo[:5]}: {surgiu:4}/{alc:4}/{vis:4} d={desv:4.1f}")
        out.append(f"{nome:13} " + "  ".join(partes))

    out += ["", "SAÍDA E ESSÊNCIA", "-" * 96]
    for nome in POLITICAS:
        acc = por_politica[nome]
        total = acc.saidas_pagas + acc.saidas_nao_pagas
        pagas = acc.saidas_pagas / total * 100 if total else 0.0
        out.append(
            f"{nome:13} pagas {pagas:5.1f}%  não pagas {acc.saidas_nao_pagas:5}  "
            f"streak médio {_media(acc.streaks):5.2f}  máx {acc.streak_max:3}  "
            f"rolada {_media(acc.essencia_rolada):5.3f} -> efetiva "
            f"{_media(acc.essencia_efetiva):5.3f}  andares no piso {acc.andares_no_piso:5}"
        )

    out += ["", "ECONOMIA (média por run)", "-" * 96]
    chaves = (
        "gold_earned",
        "gold_spent",
        "gold_from_combat",
        "gold_from_sale",
        "gold_from_interest",
        "gold_spent_on_gear",
        "gold_spent_on_consumable",
        "gold_spent_on_recovery",
        "gold_spent_on_rerolls",
        "gold_spent_on_enhancement",
        "gold_spent_on_socket",
        "gold_spent_on_enchant",
        "gold_spent_on_exit_fee",
    )
    out.append(f"{'':13} " + " ".join(f"{c.replace('gold_', '')[:9]:>10}" for c in chaves))
    for nome in POLITICAS:
        acc = por_politica[nome]
        out.append(f"{nome:13} " + " ".join(f"{_por_run(acc, c):10.0f}" for c in chaves))

    out += ["", "PROGRESSÃO (média por run)", "-" * 96]
    for nome in POLITICAS:
        acc = por_politica[nome]
        out.append(
            f"{nome:13} passos/andar {acc.passos / max(1, acc.andares_jogados):6.1f}  "
            f"HP fim de andar {_media(acc.hp_fim_de_andar) * 100:5.1f}%  "
            f"mortes {acc.mortes:4}/{acc.runs:4}  "
            f"andar da morte {_media(acc.andar_da_morte):5.1f}  "
            f"passivas {_media(acc.passivas_fim):5.1f}  skills {_media(acc.skills_fim):4.1f}  "
            f"itens {_por_run(acc, 'items_equipped'):4.1f}  gemas achadas "
            f"{_por_run(acc, 'gems_found'):4.1f}"
        )

    out += ["", "CHECKPOINTS — sobreviventes / runs iniciadas", "-" * 96]
    for nome in POLITICAS:
        acc = por_politica[nome]
        partes = []
        for andar in CHECKPOINTS:
            vivos = len(acc.checkpoints.get(andar, []))
            nivel = _media([x["nivel"] for x in acc.checkpoints.get(andar, [])])
            partes.append(f"and.{andar}: {vivos:3}/{acc.runs:3} nv{nivel:5.1f}")
        out.append(f"{nome:13} " + "  ".join(partes))

    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="Auditoria do novo loop do ToJ.")
    parser.add_argument("--runs", type=int, default=50, help="runs por classe × política")
    parser.add_argument("--seed", type=int, default=20260915)
    parser.add_argument("--max-floor", type=int, default=MAX_ANDAR)
    args = parser.parse_args()

    por_politica = {nome: Acumulador() for nome in POLITICAS}
    por_classe = {(nome, c): Acumulador() for nome in POLITICAS for c in CLASSES}

    for politica in POLITICAS:
        for classe in CLASSES:
            for i in range(args.runs):
                resultado = rodar_uma(classe, politica, args.seed + i, args.max_floor)
                _somar(por_politica[politica], resultado["acc"])
                _somar(por_classe[(politica, classe)], resultado["acc"])

    print("\n".join(relatorio(por_politica, por_classe)))


if __name__ == "__main__":
    main()
