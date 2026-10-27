"""A Arena Ranqueada no terminal, e o hub da Arena (Duelo Livre, Ranqueada, Classificação).

O jogador escolhe o gladiador extraído e prepara o equipamento, como no Duelo
Livre. Daí em diante quem escolhe o adversário é o matchmaking
(`ranked/matchmaking.py`), com a reserva do `MundoRanqueado`: voltar ao painel
não troca o oponente. O duelo é o mesmo da Arena (`arena_mode.duel`, a IA
estratégica do outro lado), com a semente da partida tirada do mundo.

Depois da partida, a Ladder atualiza os dois lados e grava `saves/ranked.json`.
As 10 primeiras partidas de cada gladiador são de posicionamento; o rank só
aparece depois delas. Enquanto o jogador está nos menus, o `AgendadorDoMundo`
joga a fila de confrontos NPC × NPC em segundo plano; antes de cada duelo do
jogador, ele para.

Como no Duelo Livre, ninguém morre, o save do personagem não muda e não há XP
nem ouro.
"""

from __future__ import annotations

import random
import time

from src.engine import arena_mode, arena_setup
from src.engine.arena_historico import identidade_do_gladiador
from src.engine.arena_populacao import Populacao, PopulacaoInvalidaError
from src.engine.ranked_mundo import AgendadorDoMundo, MundoRanqueado, RankedInvalidaError
from src.ranked import matchmaking
from src.ranked.ladder import POSICIONAMENTO
from src.storage.save_manager import load_save_data
from src.ui import arena_screens, ranked_screens
from src.ui.prompts import safe_get_key

POR_PAGINA = 15
RECENTES_NO_PAINEL = 5


# --- o que as telas mostram ---------------------------------------------------------


def _nome(mundo: MundoRanqueado, identidade: str) -> str:
    return mundo.ladder[identidade].nome


def status(mundo: MundoRanqueado, identidade: str) -> dict:
    ladder = mundo.ladder
    registro = ladder[identidade]
    recentes = [
        {
            "n": e["n"],
            "oponente": _nome(mundo, e["oponente"]) if e["oponente"] in ladder else e["oponente"],
            "venceu": e["venceu"],
            "antes": e["antes"],
            "depois": e["depois"],
        }
        for e in reversed(registro.historico[-RECENTES_NO_PAINEL:])
    ]
    return {
        "nome": registro.nome,
        "classe": registro.classe.capitalize(),
        "vitorias": registro.vitorias,
        "derrotas": registro.derrotas,
        "partidas": registro.partidas,
        "posicionamento": POSICIONAMENTO,
        "posicionado": registro.posicionado,
        "fase": matchmaking.fase(registro.partidas),
        "rating": ladder.valor(identidade),
        "incerteza": ladder.incerteza(identidade),
        "posicao": ladder.posicao(identidade),
        "competitivos": ladder.competitivos(),
        "percentil": ladder.percentil(identidade),
        "rank": ladder.rank(identidade),
        "titulo": ladder.titulo(identidade),
        "recentes": recentes,
        "mundo": (
            f"Mundo: {mundo.ladder.partidas_jogadas} partidas registradas, "
            f"{mundo.fila} confrontos NPC × NPC na fila"
        ),
    }


def linhas_da_classificacao(mundo: MundoRanqueado) -> list[dict]:
    ladder = mundo.ladder
    total = ladder.competitivos()
    linhas = []
    for posicao, registro in enumerate(ladder.classificacao(), start=1):
        linhas.append(
            {
                "posicao": posicao,
                "identidade": registro.identidade,
                "nome": registro.nome,
                "classe": registro.classe.capitalize(),
                "rank": ladder.rank(registro.identidade),
                "titulo": ladder.titulo(registro.identidade),
                "percentil": 100.0 if total == 1 else 100.0 * (total - posicao) / (total - 1),
                "rating": ladder.valor(registro.identidade),
                "incerteza": ladder.incerteza(registro.identidade),
                "vitorias": registro.vitorias,
                "derrotas": registro.derrotas,
                "jogador": not registro.npc,
            }
        )
    return linhas


# --- telas com teclado --------------------------------------------------------------


def mostrar_classificacao(mundo: MundoRanqueado, destaque: str | None = None) -> None:
    linhas = linhas_da_classificacao(mundo)
    paginas = max(1, -(-len(linhas) // POR_PAGINA))
    pagina = 0
    for i, linha in enumerate(linhas):
        if linha["identidade"] == destaque:
            pagina = i // POR_PAGINA
    while True:
        inicio = pagina * POR_PAGINA
        ranked_screens.render_leaderboard(
            linhas[inicio : inicio + POR_PAGINA], pagina + 1, paginas, len(linhas)
        )
        tecla = safe_get_key(valid_keys=["a", "d", "q"])
        if tecla in (None, "q"):
            return
        pagina = (pagina + (1 if tecla == "d" else -1)) % paginas


def _partida(mundo, identidade, personagem, publish, controlador) -> bool:
    """Busca o adversário, mostra, joga e registra. `False` se o jogador voltou."""
    oponente_id = mundo.adversario(identidade)
    oponente = mundo.populacao.get(oponente_id)
    try:
        gladiador = mundo.populacao.gladiador(oponente)
    except PopulacaoInvalidaError as erro:
        mundo.reservas.pop(identidade, None)
        mundo.salvar()
        arena_screens.render_notice(f"{oponente.apelido} não pode lutar: {erro}", "red")
        safe_get_key(allow_escape=False)
        return False
    ladder = mundo.ladder
    arena_screens.render_arena_header("ADVERSÁRIO")
    arena_screens.render_build_sheet(gladiador.hero, "Adversário")
    ranked_screens.render_opponent_found(
        {
            "nome": oponente.apelido,
            "classe": oponente.nome_da_classe,
            "nivel": oponente.nivel,
            "rank": ladder.rank(oponente_id),
            "percentil": ladder.percentil(oponente_id),
            "rating": ladder.valor(oponente_id),
            "fase": matchmaking.fase(ladder[identidade].partidas),
            "probabilidade": ladder.esperado(identidade, oponente_id),
        }
    )
    if safe_get_key(valid_keys=["enter", "q"]) != "enter":
        return False
    probabilidade = ladder.esperado(identidade, oponente_id)
    rng = random.Random(mundo.semente_da_partida(identidade))
    duelo = arena_mode.duel(
        personagem, gladiador, rng=rng, publish=publish, controlador=controlador
    )
    venceu = duelo.result.winner == arena_mode.JOGADOR
    estava_posicionado = ladder[identidade].posicionado
    atualizacao = mundo.registrar_do_jogador(identidade, oponente_id, venceu)
    registro = ladder[identidade]
    ranked_screens.render_ranked_result(
        {
            "venceu": venceu,
            "antes": atualizacao.antes[identidade],
            "depois": atualizacao.depois[identidade],
            "probabilidade": probabilidade,
            "acabou_de_posicionar": registro.posicionado and not estava_posicionado,
            "rank": ladder.rank(identidade),
            "posicao": ladder.posicao(identidade),
            "competitivos": ladder.competitivos(),
            "percentil": ladder.percentil(identidade),
            "partidas": registro.partidas,
            "posicionamento": POSICIONAMENTO,
        }
    )
    safe_get_key(allow_escape=False)
    return True


def _painel(mundo, identidade, personagem, publish, controlador, agente) -> None:
    while True:
        if agente is not None:
            agente.coletar()
            agente.iniciar()
        ranked_screens.render_ranked_panel(status(mundo, identidade))
        tecla = safe_get_key(valid_keys=["enter", "c", "q"])
        if tecla in (None, "q"):
            return
        if tecla == "c":
            mostrar_classificacao(mundo, destaque=identidade)
            continue
        if agente is not None:
            agente.parar()
        _partida(mundo, identidade, personagem, publish, controlador)


def run_ranqueada(
    *,
    populacao: Populacao | None = None,
    mundo: MundoRanqueado | None = None,
    controlador=None,
    agora: float | None = None,
    mundo_em_segundo_plano: bool = True,
) -> None:
    """A Arena Ranqueada, da escolha do gladiador de volta ao hub."""
    publish, limpar = arena_mode._barramento()
    agente = None
    try:
        try:
            populacao = populacao if populacao is not None else Populacao()
            mundo = mundo if mundo is not None else MundoRanqueado.carregar(populacao)
        except (PopulacaoInvalidaError, RankedInvalidaError) as erro:
            arena_screens.render_population_unavailable(str(erro))
            safe_get_key(allow_escape=False)
            return
        mundo.ao_retornar(time.time() if agora is None else agora)
        agente = AgendadorDoMundo(mundo) if mundo_em_segundo_plano else None
        while True:
            entradas = arena_setup.list_gladiators()
            if not entradas:
                arena_screens.render_arena_unavailable(0)
                safe_get_key(allow_escape=False)
                return
            minha = arena_mode._escolher(entradas, "RANQUEADA: ESCOLHA SEU GLADIADOR")
            if minha is None:
                return
            personagem = arena_setup.load_character(minha.slot)
            if not arena_mode._preparar(minha, personagem, publish):
                continue
            identidade = identidade_do_gladiador(load_save_data(minha.slot), minha.slot)
            mundo.inscrever(identidade, personagem.get_nick_name(), personagem.get_classname())
            mundo.salvar()
            _painel(mundo, identidade, personagem, publish, controlador, agente)
    finally:
        if agente is not None:
            agente.parar()
        limpar()


def run_arena_hub(**kwargs) -> None:
    """O menu da Arena: Duelo Livre, Arena Ranqueada ou a Classificação."""
    while True:
        ranked_screens.render_arena_hub()
        tecla = safe_get_key(valid_keys=["1", "2", "3", "q"])
        if tecla in (None, "q"):
            return
        if tecla == "1":
            arena_mode.run_arena()
        elif tecla == "2":
            run_ranqueada(**kwargs)
        else:
            try:
                populacao = kwargs.get("populacao") or Populacao()
                mundo = kwargs.get("mundo") or MundoRanqueado.carregar(populacao)
            except (PopulacaoInvalidaError, RankedInvalidaError) as erro:
                arena_screens.render_population_unavailable(str(erro))
                safe_get_key(allow_escape=False)
                continue
            mostrar_classificacao(mundo)
