"""A Arena offline no terminal: escolher, preparar, conhecer o adversário, duelar, de novo.

O modo competitivo do ToJ 1.0, 100% local. O jogador leva um gladiador
extraído dos próprios saves contra a POPULAÇÃO OFFLINE (`engine/arena_populacao`):
gladiadores extraídos de runs PvE reais, controlados pela IA estratégica
(`sim/ia_estrategica`). Não há rede, fila, relógio nem conta; o multiplayer das
Fases 3 e 4 continua no repositório, fora deste fluxo.

Nada de regra mora aqui. O duelo é `mechanics/pvp_duel` — `run_round` monta as
duas visões antes de qualquer escolha e chama `play_round` —, o gladiador é
`content/gladiator` e o save é `engine/arena_setup`. Este módulo só desenha
(`ui/arena_screens`), lê teclas e pergunta a quem decide:

    p1  o jogador, por `HumanDuelController`, que lê a própria visão e o
        próprio deck;
    p2  a IA estratégica, que decide pela visão do lado dela e simula só
        sobre cópias.

O duelo roda sobre cópias. Vencer ou perder não mata ninguém, não dá XP, ouro
nem recompensa, e não grava nada. A única escrita da Arena é o equipamento que
o jogador escolher gravar na preparação. Cada partida terminada vira um
`ResultadoDaPartida` no histórico da sessão e passa pela `Classificacao` — hoje
a nula; a fórmula do MMR é da Fase 6.
"""

from __future__ import annotations

import random

from src.content.gladiator import prepare_gladiator
from src.engine import arena_setup
from src.engine.arena_historico import (
    Classificacao,
    Historico,
    HistoricoDaSessao,
    Participante,
    ResultadoDaPartida,
    SemClassificacao,
    identidade_do_gladiador,
)
from src.engine.arena_populacao import (
    VERSAO_DO_CATALOGO,
    Oponente,
    Populacao,
    PopulacaoInvalidaError,
)
from src.engine.events import EventBus
from src.engine.game_logic import CLASS_MAP
from src.mechanics.pvp_duel import SIDES, Duel, DuelAction, run_round
from src.shared import combat_topics as topics
from src.shared.types import GameEvent
from src.sim.ia_estrategica import IAEstrategica
from src.storage.save_manager import load_save_data
from src.ui import arena_screens
from src.ui.combat_event_handlers import register_combat_ui_handlers
from src.ui.prompts import safe_get_key
from src.ui.ui_event_handlers import register_ui_handlers

# O jogador é sempre p1 e a IA, p2. O lado não dá vantagem nenhuma: a ordem de
# cada rodada é a iniciativa.
JOGADOR, ADVERSARIO = SIDES

# A lista da população: filtro de classe (None = todas) e tamanho da página.
FILTROS = (None, "warrior", "mage", "rogue")
POR_PAGINA = 15

# O histórico desta sessão do jogo: sobrevive à volta ao menu principal e some
# quando o jogo fecha. A persistência é da Fase 6.
HISTORICO = HistoricoDaSessao()

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


def _escolher_oponente(populacao: Populacao) -> Oponente | None:
    """Navega a população, com filtro de classe e páginas. `None` volta."""
    filtro = cursor = 0
    while True:
        lista = populacao.oponentes(FILTROS[filtro])
        cursor = max(0, min(cursor, len(lista) - 1))
        pagina, paginas = cursor // POR_PAGINA, max(1, -(-len(lista) // POR_PAGINA))
        inicio = pagina * POR_PAGINA
        rotulo = "todas" if FILTROS[filtro] is None else CLASS_MAP[FILTROS[filtro]][1]
        arena_screens.render_opponent_list(
            lista[inicio : inicio + POR_PAGINA],
            cursor - inicio,
            rotulo,
            pagina + 1,
            paginas,
            len(lista),
        )
        tecla = safe_get_key(valid_keys=["w", "s", "a", "d", "f", "enter", "q"])
        if tecla in (None, "q"):
            return None
        if tecla == "f":
            filtro, cursor = (filtro + 1) % len(FILTROS), 0
        elif not lista:
            continue
        elif tecla == "w":
            cursor = (cursor - 1) % len(lista)
        elif tecla == "s":
            cursor = (cursor + 1) % len(lista)
        elif tecla == "a":
            cursor = max(0, cursor - POR_PAGINA)
        elif tecla == "d":
            cursor = min(len(lista) - 1, cursor + POR_PAGINA)
        elif tecla == "enter":
            return lista[cursor]


def _ficha_do_oponente(populacao: Populacao, oponente: Oponente):
    """A ficha pública do oponente antes de confirmar. O gladiador, ou `None`."""
    try:
        gladiador = populacao.gladiador(oponente)
    except PopulacaoInvalidaError as erro:
        arena_screens.render_notice(f"{oponente.apelido} não pode lutar: {erro}", "red")
        safe_get_key(allow_escape=False)
        return None
    arena_screens.render_arena_header("ADVERSÁRIO")
    arena_screens.render_build_sheet(gladiador.hero, "Adversário")
    arena_screens.render_opponent_origin(oponente)
    arena_screens.render_opponent_menu()
    if safe_get_key(valid_keys=["enter", "q"]) == "enter":
        return gladiador
    return None


def duel(personagem, adversario, *, rng: random.Random, publish=None, controlador=None) -> Duel:
    """Um duelo completo: o jogador contra o adversário automático.

    `controlador` recebe o herói do adversário NO DUELO e devolve o
    `DuelController` dele; sem ele, é a IA estratégica. Uma rodada por vez,
    pelo motor: `run_round` pede as duas ações e chama `play_round`. Durante a
    resolução a voz do combate chega pelo bus, na ordem em que as ações
    acontecem; depois, o resumo da rodada.
    """
    meu = prepare_gladiator(personagem)
    duelo = Duel(meu, adversario, rng=rng, publish=publish)
    humano = HumanDuelController(meu.hero)
    fabrica = controlador if controlador is not None else IAEstrategica
    controladores = {JOGADOR: humano, ADVERSARIO: fabrica(adversario.hero)}
    while not duelo.finished:
        registro = run_round(duelo, controladores)
        humano.log = round_lines(registro, duelo)
        arena_screens.render_round_summary(humano.log)
        safe_get_key(allow_escape=False)
    return duelo


def resultado_da_partida(duelo: Duel, identidade: str, oponente: Oponente) -> ResultadoDaPartida:
    """O registro da partida terminada, para o histórico e a classificação."""
    resultado = duelo.result
    meu, dele = duelo.hero(JOGADOR), duelo.hero(ADVERSARIO)
    return ResultadoDaPartida(
        jogador=Participante(identidade, meu.get_nick_name(), meu.get_classname(), meu.get_level()),
        oponente=Participante(
            oponente.identidade,
            oponente.apelido,
            dele.get_classname(),
            dele.get_level(),
            oponente.op,
        ),
        venceu=resultado.winner == JOGADOR,
        motivo=resultado.reason,
        rodadas=resultado.rounds,
        versao_do_catalogo=VERSAO_DO_CATALOGO,
    )


def _mostrar_resultado(duelo: Duel, historico: Historico, identidade: str) -> str:
    """O fim da partida e o próximo passo: "revanche", "outro" ou "voltar"."""
    resultado = duelo.result
    arena_screens.render_arena_header("RESULTADO")
    arena_screens.render_duel_result(
        resultado.winner == JOGADOR,
        resultado.winner_name,
        resultado.loser_name,
        MOTIVOS[resultado.reason],
        resultado.rounds,
    )
    arena_screens.render_after_match_menu(*historico.placar(identidade))
    tecla = safe_get_key(valid_keys=["r", "a", "q", "enter"])
    return {"r": "revanche", "a": "outro"}.get(tecla, "voltar")


def _partidas(
    personagem,
    identidade: str,
    populacao: Populacao,
    *,
    rng: random.Random,
    publish,
    controlador,
    historico,
    classificacao: Classificacao,
) -> None:
    """Partidas seguidas do mesmo gladiador, até o jogador voltar à lista."""
    oponente = gladiador = None
    while True:
        if gladiador is None:
            oponente = _escolher_oponente(populacao)
            if oponente is None:
                return
            gladiador = _ficha_do_oponente(populacao, oponente)
            if gladiador is None:
                continue
        duelo = duel(personagem, gladiador, rng=rng, publish=publish, controlador=controlador)
        resultado = resultado_da_partida(duelo, identidade, oponente)
        historico.registrar(resultado)
        classificacao.atualizar(resultado)
        proximo = _mostrar_resultado(duelo, historico, identidade)
        if proximo == "voltar":
            return
        # A revanche é o mesmo oponente, montado de novo do catálogo (o duelo
        # anterior gastou a instância dele) e conferido de novo.
        gladiador = None
        if proximo == "revanche":
            try:
                gladiador = populacao.gladiador(oponente)
            except PopulacaoInvalidaError as erro:
                arena_screens.render_notice(f"{oponente.apelido} não pode lutar: {erro}", "red")
                safe_get_key(allow_escape=False)


def run_arena(
    rng: random.Random | None = None,
    *,
    populacao: Populacao | None = None,
    controlador=None,
    historico: Historico | None = None,
    classificacao: Classificacao | None = None,
) -> None:
    """A Arena offline, do menu principal de volta a ele.

    `rng` é o gerador dos duelos; sem ele, cada duelo sorteia o próprio. Os
    outros parâmetros existem para teste e para a Fase 6: a população (o
    catálogo do jogo), o controlador do adversário (a IA), o histórico (o da
    sessão) e a classificação (a nula).
    """
    rng = rng if rng is not None else random.Random()
    historico = historico if historico is not None else HISTORICO
    classificacao = classificacao if classificacao is not None else SemClassificacao()
    publish, limpar = _barramento()
    try:
        if populacao is None:
            try:
                populacao = Populacao()
            except PopulacaoInvalidaError as erro:
                arena_screens.render_population_unavailable(str(erro))
                safe_get_key(allow_escape=False)
                return
        while True:
            entradas = arena_setup.list_gladiators()
            if not entradas:
                arena_screens.render_arena_unavailable(0)
                safe_get_key(allow_escape=False)
                return
            minha = _escolher(entradas, "ESCOLHA SEU GLADIADOR")
            if minha is None:
                return
            personagem = arena_setup.load_character(minha.slot)
            if not _preparar(minha, personagem, publish):
                continue
            identidade = identidade_do_gladiador(load_save_data(minha.slot), minha.slot)
            _partidas(
                personagem,
                identidade,
                populacao,
                rng=rng,
                publish=publish,
                controlador=controlador,
                historico=historico,
                classificacao=classificacao,
            )
    finally:
        limpar()
