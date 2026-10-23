"""O modo Arena no terminal: escolher, preparar, conhecer o adversário, duelar, voltar.

Uma experiência LOCAL de validação do duelo, não a ranked: um jogador humano
contra um controlador automático, os dois gladiadores tirados dos saves de
personagens extraídos. Não há fila, relógio, rede nem MMR.

Nada de regra mora aqui. O duelo é `mechanics/pvp_duel` — `run_round` monta as
duas visões antes de qualquer escolha e chama `play_round` —, o gladiador é
`content/gladiator` e o save é `engine/arena_setup`. Este módulo só desenha
(`ui/arena_screens`), lê teclas e pergunta a quem decide:

    p1  o jogador, por `HumanDuelController`, que lê a própria visão e o
        próprio deck;
    p2  `FirstLegalSkillController`, que decide só pela visão do motor.

O duelo roda sobre cópias. Vencer ou perder não mata ninguém, não dá XP, ouro
nem recompensa, e não grava nada. A única escrita da Arena é o equipamento que
o jogador escolher gravar na preparação.
"""

from __future__ import annotations

import random

from src.content.gladiator import prepare_gladiator
from src.engine import arena_setup
from src.engine.events import EventBus
from src.mechanics.pvp_duel import SIDES, Duel, DuelAction, run_round
from src.shared import combat_topics as topics
from src.shared.types import GameEvent
from src.sim.pvp_controllers import FirstLegalSkillController
from src.ui import arena_screens
from src.ui.combat_event_handlers import register_combat_ui_handlers
from src.ui.prompts import safe_get_key
from src.ui.ui_event_handlers import register_ui_handlers

# O jogador é sempre p1 e o controlador automático, p2. O lado não dá
# vantagem nenhuma: a ordem de cada rodada é a iniciativa.
JOGADOR, ADVERSARIO = SIDES

MOTIVOS = {
    "ko": "nocaute",
    "surrender": "rendição",
    "timeout": "tempo esgotado",
    "disconnect": "desconexão",
}

DESFECHOS = {
    "cancelled_control": "cancelada: estava sob controle",
    "cancelled_death": "cancelada: caiu antes de agir",
    "not_reached": "não aconteceu: o duelo já tinha acabado",
}


def _barramento():
    """O bus da Arena: a voz do combate e as telas abertas por evento."""
    bus = EventBus()
    limpar_combate = register_combat_ui_handlers(bus)
    limpar_ui = register_ui_handlers(bus)

    def publish(topic: str, payload_or_event) -> None:
        if isinstance(payload_or_event, GameEvent):
            bus.publish(topic, payload_or_event)
        else:
            bus.publish(topic, GameEvent(type=topic, payload=payload_or_event))

    def limpar() -> None:
        limpar_combate()
        limpar_ui()

    return publish, limpar


# --- o jogador no duelo -------------------------------------------------------


class HumanDuelController:
    """O jogador no terminal, pela interface `DuelController`.

    Decide pela `DuelView` — a mesma que o adversário recebe do lado dele — e
    pelo próprio deck, que é informação dele. A legalidade é a do motor: uma
    carta só é escolhível se está em `view.legal_actions`.
    """

    def __init__(self, hero) -> None:
        self._hero = hero
        # O registro da rodada anterior, para o quadro da próxima escolha.
        self.log: list[str] = []

    def choose(self, view):
        while True:
            arena_screens.render_duel_frame(view, self.log)
            arena_screens.render_duel_actions()
            tecla = safe_get_key(valid_keys=["1", "2", "3"], allow_escape=False)
            if tecla == "1":
                return DuelAction.attack()
            if tecla == "2":
                acao = self._escolher_skill(view)
                if acao is not None:
                    return acao
            elif tecla == "3":
                arena_screens.render_surrender_confirm()
                if safe_get_key(valid_keys=["s", "n"], allow_escape=False) == "s":
                    return DuelAction.surrender()

    def skill_rows(self, view) -> list[tuple]:
        """`(tecla, nome, custo, situação)` de cada carta do deck, na ordem do deck."""
        legais = {a.skill_id for a in view.legal_actions if a.kind == "skill"}
        recargas = dict(view.cooldowns)
        linhas = []
        for tecla, skill in sorted(self._hero.skills.items()):
            situacao = ""
            if skill.id not in legais:
                if not self._hero.can_use_skill(skill):
                    situacao = f"exige {skill.requires.describe()}"
                elif recargas.get(skill.id, 0) > 0:
                    situacao = f"recarga: {recargas[skill.id]}"
                else:
                    situacao = "MP insuficiente"
            linhas.append((tecla, skill.name, self._hero.skill_mana_cost(skill), situacao))
        return linhas

    def _escolher_skill(self, view):
        linhas = self.skill_rows(view)
        por_tecla = {str(t): (self._hero.skills[t], situacao) for t, _, _, situacao in linhas}
        while True:
            arena_screens.render_duel_frame(view, self.log)
            arena_screens.render_duel_skill_panel(linhas)
            tecla = safe_get_key(valid_keys=[*por_tecla, "0"], allow_escape=False)
            if tecla == "0":
                return None
            skill, situacao = por_tecla[tecla]
            if not situacao:
                return DuelAction.use_skill(skill.id)
            arena_screens.render_notice(f"{skill.name}: {situacao}.", "red")
            safe_get_key(allow_escape=False)


# --- o registro da rodada -----------------------------------------------------


def _nome_da_acao(hero, acao: DuelAction) -> str:
    if acao.kind == "skill":
        for skill in hero.skills.values():
            if skill.id == acao.skill_id:
                return skill.name
        return str(acao.skill_id)
    return {"attack": "Ataque básico", "surrender": "Rendição"}[acao.kind]


def round_lines(registro, duelo: Duel) -> list[str]:
    """A rodada em texto, na ordem em que o motor a resolveu.

    A ordem aparece; o Initiative Score não. As ações do adversário só existem
    aqui, depois do lock — antes disso a tela nunca as teve.
    """
    nomes = {lado: duelo.hero(lado).get_nick_name() for lado in SIDES}
    linhas = [f"Rodada {registro.number}: agiu primeiro {nomes[registro.order.first]}."]
    resultado = duelo.result
    if resultado is not None and resultado.reason == "surrender":
        linhas.append(f"{nomes[resultado.loser]} se rendeu.")
    else:
        for passo in registro.steps:
            acao = _nome_da_acao(duelo.hero(passo.side), passo.action)
            if passo.outcome == "executed":
                detalhe = (
                    f"{passo.damage_to_opponent} de dano"
                    if passo.damage_to_opponent
                    else "sem dano direto"
                )
                if passo.mp_spent:
                    detalhe += f", {passo.mp_spent} MP"
            else:
                detalhe = DESFECHOS[passo.outcome]
            linhas.append(f"{nomes[passo.side]}: {acao} — {detalhe}.")
    hp = dict(registro.hp_end)
    linhas.append(
        "HP ao fim: "
        + "  |  ".join(
            f"{nomes[lado]} {max(0, hp[lado])}/{duelo.hero(lado).base_hp}" for lado in SIDES
        )
    )
    return linhas


# --- o fluxo da Arena ---------------------------------------------------------


def _escolher(entradas, titulo: str):
    """Navega a lista e devolve a entrada escolhida, ou `None` para voltar."""
    cursor = 0
    while True:
        arena_screens.render_gladiator_list(titulo, entradas, cursor)
        tecla = safe_get_key(valid_keys=["w", "s", "enter", "q"])
        if tecla in (None, "q"):
            return None
        if tecla == "w":
            cursor = (cursor - 1) % len(entradas)
        elif tecla == "s":
            cursor = (cursor + 1) % len(entradas)
        elif tecla == "enter":
            return entradas[cursor]


def _assinatura_do_equipamento(heroi) -> tuple:
    return tuple((posicao, id(item)) for posicao, item in heroi.equipment.items())


def _preparar(entrada, personagem, publish) -> bool:
    """Ficha, equipamento e confirmação. Devolve se o jogador confirmou.

    O equipamento muda no personagem carregado do save, pelas regras de sempre
    (classe, posição, mãos). Gravar no save é escolha explícita do jogador, e
    grava só o equipamento.
    """
    inicial = _assinatura_do_equipamento(personagem)
    while True:
        arena_screens.render_arena_header("PREPARAÇÃO")
        arena_screens.render_build_sheet(prepare_gladiator(personagem).hero, "Seu gladiador")
        arena_screens.render_prep_menu()
        tecla = safe_get_key(valid_keys=["e", "enter", "q"])
        if tecla in (None, "q"):
            return False
        if tecla == "e":
            publish(topics.UI_OPEN_ARENA_LOADOUT, {"player": personagem})
            continue
        if _assinatura_do_equipamento(personagem) != inicial:
            arena_screens.render_save_loadout_prompt()
            if safe_get_key(valid_keys=["s", "n"], allow_escape=False) == "s":
                gravado = arena_setup.store_loadout(entrada.slot, personagem)
                arena_screens.render_notice(
                    gravado["message"], "green" if gravado["success"] else "red"
                )
                safe_get_key(allow_escape=False)
        return True


def _escolher_adversario(entradas):
    """Escolhe o adversário e mostra a build dele antes de confirmar."""
    while True:
        escolhida = _escolher(entradas, "ESCOLHA O ADVERSÁRIO")
        if escolhida is None:
            return None
        gladiador = arena_setup.gladiator_from_slot(escolhida.slot)
        arena_screens.render_arena_header("ADVERSÁRIO")
        arena_screens.render_build_sheet(gladiador.hero, "Adversário")
        arena_screens.render_opponent_menu()
        if safe_get_key(valid_keys=["enter", "q"]) == "enter":
            return gladiador


def duel(personagem, adversario, *, rng: random.Random, publish=None) -> Duel:
    """Um duelo completo: o jogador contra o controlador automático.

    Uma rodada por vez, pelo motor: `run_round` pede as duas ações e chama
    `play_round`. Durante a resolução a voz do combate chega pelo bus, na
    ordem em que as ações acontecem; depois, o resumo da rodada.
    """
    meu = prepare_gladiator(personagem)
    duelo = Duel(meu, adversario, rng=rng, publish=publish)
    humano = HumanDuelController(meu.hero)
    controladores = {JOGADOR: humano, ADVERSARIO: FirstLegalSkillController()}
    while not duelo.finished:
        registro = run_round(duelo, controladores)
        humano.log = round_lines(registro, duelo)
        arena_screens.render_round_summary(humano.log)
        safe_get_key(allow_escape=False)
    return duelo


def _mostrar_resultado(duelo: Duel) -> None:
    resultado = duelo.result
    arena_screens.render_arena_header("RESULTADO")
    arena_screens.render_duel_result(
        resultado.winner == JOGADOR,
        resultado.winner_name,
        resultado.loser_name,
        MOTIVOS[resultado.reason],
        resultado.rounds,
    )
    safe_get_key(allow_escape=False)


def run_arena(rng: random.Random | None = None) -> None:
    """A Arena, do menu principal de volta a ele.

    `rng` é o gerador dos duelos; sem ele, cada duelo sorteia o próprio.
    """
    rng = rng if rng is not None else random.Random()
    publish, limpar = _barramento()
    try:
        while True:
            entradas = arena_setup.list_gladiators()
            if len(entradas) < 2:
                arena_screens.render_arena_unavailable(len(entradas))
                safe_get_key(allow_escape=False)
                return
            minha = _escolher(entradas, "ESCOLHA SEU GLADIADOR")
            if minha is None:
                return
            personagem = arena_setup.load_character(minha.slot)
            if not _preparar(minha, personagem, publish):
                continue
            adversario = _escolher_adversario([e for e in entradas if e.slot != minha.slot])
            if adversario is None:
                continue
            _mostrar_resultado(duel(personagem, adversario, rng=rng, publish=publish))
    finally:
        limpar()
