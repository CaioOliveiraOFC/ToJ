"""A Arena Ranqueada no terminal, e o hub da Arena (Duelo Livre, Ranqueada, Classificação).

O jogador escolhe o gladiador extraído e prepara o equipamento, como no Duelo
Livre. Daí em diante quem escolhe o adversário é o matchmaking
(`ranked/matchmaking.py`), com a reserva do `MundoRanqueado`: voltar ao painel
não troca o oponente. O duelo é o mesmo da Arena (`arena_mode.duel`, a IA
estratégica do outro lado), com a semente da partida tirada do mundo.

Depois da partida, a Ladder atualiza os dois lados e grava `saves/ranked.json`.
As 10 primeiras partidas de cada gladiador são de posicionamento; a divisão só
aparece depois delas. Daí em diante o painel mostra a divisão e a barra de PR
(`ranked/progressao.py`), a candidatura a Master e a elite, e a leaderboard
publicada (`ranked/leaderboard.py`), atualizada por ciclos: ao abrir, depois de
cada partida e a cada volta ao painel. Enquanto o jogador está nos menus, o
`AgendadorDoMundo` joga a fila de confrontos NPC × NPC em segundo plano; antes
de cada duelo do jogador, ele para.

O duelo do jogador tem o mesmo árbitro de impasse dos NPCs
(`ranked/impasse.py`): uma partida em que ninguém se desgasta mais vira empate
técnico. Um erro técnico no duelo anula a partida (nada muda além do
histórico); uma interrupção pelo teclado também, e o adversário continua
reservado.

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
from src.ranked import leaderboard, matchmaking, progressao
from src.ranked.impasse import ArbitroDeImpasse
from src.ranked.ladder import ANULADA, DERROTA, EMPATE, POSICIONAMENTO, VITORIA
from src.storage.save_manager import load_save_data
from src.ui import arena_screens, ranked_screens
from src.ui.prompts import safe_get_key

POR_PAGINA = 15
RECENTES_NO_PAINEL = 5


# --- o que as telas mostram ---------------------------------------------------------


def _nome(mundo: MundoRanqueado, identidade: str) -> str:
    return mundo.ladder[identidade].nome


def _ciclo(mundo: MundoRanqueado) -> dict:
    lb = mundo.leaderboard
    return {
        "publicada_em": lb.publicada_em,
        "proxima": lb.proxima(),
        "periodo": lb.periodo,
        "adiada": lb.adiada,
    }


def elegibilidade(mundo: MundoRanqueado, identidade: str) -> dict:
    """O que a próxima atualização vai olhar num Candidato a Master, com os valores de agora."""
    ladder = mundo.ladder
    percentil = ladder.percentil(identidade)
    incerteza = ladder.incerteza(identidade)
    return {
        "percentil": percentil,
        "minimo": leaderboard.MINIMO_DA_ELITE,
        "percentil_ok": percentil is not None and percentil >= leaderboard.MINIMO_DA_ELITE,
        "incerteza": incerteza,
        "incerteza_maxima": leaderboard.RD_MAXIMO_PARA_PROMOVER,
        "incerteza_ok": incerteza <= leaderboard.RD_MAXIMO_PARA_PROMOVER,
    }


def legivel(evento: dict) -> dict:
    """O evento com o nome das divisões, para a tela (que não conhece a régua)."""
    pronto = dict(evento)
    for chave in ("de", "para"):
        valor = evento.get(chave)
        if isinstance(valor, int) and not isinstance(valor, bool):
            pronto[f"{chave}_nome"] = progressao.nome_da_divisao(valor)
    return pronto


def _linha_do_historico(mundo: MundoRanqueado, e: dict) -> dict:
    ladder = mundo.ladder
    resultado = e.get("resultado") or (
        ANULADA if e["venceu"] is None else (VITORIA if e["venceu"] else DERROTA)
    )
    return {
        "n": e["n"],
        "oponente": _nome(mundo, e["oponente"]) if e["oponente"] in ladder else e["oponente"],
        "resultado": resultado,
        "motivo": e.get("motivo"),
        "antes": e["antes"],
        "depois": e["depois"],
        "pr": e.get("pr"),
    }


def status(mundo: MundoRanqueado, identidade: str) -> dict:
    ladder = mundo.ladder
    registro = ladder[identidade]
    p = registro.progresso
    publicada = mundo.leaderboard.linha(identidade)
    return {
        "nome": registro.nome,
        "classe": registro.classe.capitalize(),
        "vitorias": registro.vitorias,
        "derrotas": registro.derrotas,
        "empates": registro.empates,
        "partidas": registro.partidas,
        "posicionamento": POSICIONAMENTO,
        "posicionado": registro.posicionado,
        "fase": matchmaking.fase(registro.partidas),
        "rating": ladder.valor(identidade),
        "incerteza": ladder.incerteza(identidade),
        "posicao": ladder.posicao(identidade),
        "competitivos": ladder.competitivos(),
        "percentil": ladder.percentil(identidade),
        "rank_do_mmr": ladder.rank(identidade),
        "alvo": None if ladder.alvo(identidade) is None else _nome_do_alvo(ladder.alvo(identidade)),
        "divisao": None if p.divisao is None else progressao.nome_da_divisao(p.divisao),
        "pr": p.pr,
        "escudo": p.escudo,
        "candidato": p.candidato,
        "elegibilidade": elegibilidade(mundo, identidade) if p.candidato else None,
        "elite": p.elite,
        "risco": p.risco,
        "titulo": p.titulo,
        "posicao_publicada": None if publicada is None else publicada["posicao"],
        "variacao": mundo.leaderboard.variacao(identidade),
        "ciclo": _ciclo(mundo),
        "eventos": [legivel(e) for e in reversed(registro.eventos[-3:])],
        "recentes": [
            _linha_do_historico(mundo, e)
            for e in reversed(registro.historico[-RECENTES_NO_PAINEL:])
        ],
        "mundo": (
            f"Mundo: {mundo.ladder.partidas_jogadas} partidas registradas, "
            f"{mundo.fila} confrontos NPC × NPC na fila"
        ),
    }


def _nome_do_alvo(meta: float) -> str:
    """A coordenada do alvo em palavras: a divisão, ou o rank de elite que o percentil daria."""
    if meta >= progressao.TOPO:
        indice = min(
            len(progressao.ELITE) - 1, int((meta - progressao.TOPO) // progressao.POR_RANK)
        )
        return progressao.ELITE[indice]
    return progressao.nome_da_divisao(int(meta // progressao.PR_POR_DIVISAO))


def linhas_da_classificacao(mundo: MundoRanqueado) -> list[dict]:
    """A leaderboard PUBLICADA (o último retrato), com a variação desde o anterior."""
    lb = mundo.leaderboard
    linhas = []
    for linha in lb.linhas:
        identidade = linha["identidade"]
        linhas.append(
            {
                **linha,
                "classe": linha["classe"].capitalize(),
                "rank": linha["exibicao"],
                "incerteza": linha["rd"],
                "variacao": lb.variacao(identidade),
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
            linhas[inicio : inicio + POR_PAGINA],
            pagina + 1,
            paginas,
            len(linhas),
            _ciclo(mundo),
        )
        tecla = safe_get_key(valid_keys=["a", "d", "q"])
        if tecla in (None, "q"):
            return
        pagina = (pagina + (1 if tecla == "d" else -1)) % paginas


def _partida(mundo, identidade, personagem, publish, controlador, relogio) -> bool:
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
            "exibicao": ladder.exibicao(oponente_id),
            "titulo": ladder.titulo(oponente_id),
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
    arbitro = ArbitroDeImpasse()
    registro = ladder[identidade]
    antes = {
        "divisao": registro.progresso.divisao,
        "elite": registro.progresso.elite,
        "posicionado": registro.posicionado,
    }
    try:
        duelo = arena_mode.duel(
            personagem,
            gladiador,
            rng=rng,
            publish=publish,
            controlador=controlador,
            arbitro=arbitro,
        )
    except KeyboardInterrupt:
        mundo.registrar_do_jogador(identidade, oponente_id, ANULADA, motivo="interrompida")
        raise
    except Exception as erro:  # noqa: BLE001 — erro técnico anula a partida
        motivo = f"erro técnico: {type(erro).__name__}"
        mundo.registrar_do_jogador(identidade, oponente_id, ANULADA, motivo=motivo)
        arena_screens.render_notice(
            f"A partida foi ANULADA por um erro técnico ({type(erro).__name__}). "
            "Rating, PR e posicionamento não mudaram.",
            "red",
        )
        safe_get_key(allow_escape=False)
        return True
    if duelo.finished:
        venceu = duelo.result.winner == arena_mode.JOGADOR
        resultado, motivo = (VITORIA if venceu else DERROTA), duelo.result.reason
    else:
        resultado, motivo = EMPATE, arbitro.veredito.motivo
    atualizacao = mundo.registrar_do_jogador(identidade, oponente_id, resultado, motivo=motivo)
    resumo = mundo.atualizar_leaderboard(relogio())
    registro = ladder[identidade]
    ranked_screens.render_ranked_result(
        {
            "resultado": resultado,
            "motivo": motivo,
            "rodadas": duelo.result.rounds if duelo.finished else arbitro.rodada,
            "antes": atualizacao.antes[identidade],
            "depois": atualizacao.depois[identidade],
            "probabilidade": probabilidade,
            "pr": atualizacao.pr.get(identidade),
            "eventos": [legivel(e) for e in atualizacao.eventos.get(identidade, [])],
            "acabou_de_posicionar": registro.posicionado and not antes["posicionado"],
            "status": status(mundo, identidade),
        }
    )
    safe_get_key(allow_escape=False)
    _avisar_atualizacao(mundo, identidade, resumo)
    return True


def _avisar_atualizacao(mundo, identidade, resumo) -> None:
    """Se a leaderboard acabou de sair, mostra o que ela decidiu sobre este gladiador."""
    if not resumo:
        return
    meus = [legivel(e) for e in resumo.get("eventos", []) if e.get("identidade") == identidade]
    ranked_screens.render_leaderboard_update(
        {
            "publicada_em": mundo.leaderboard.publicada_em,
            "proxima": mundo.leaderboard.proxima(),
            "pulados": resumo.get("pulados", 0),
            "adiada": resumo.get("adiada", []),
            "eventos": meus,
            "total": len(resumo.get("eventos", [])),
        }
    )
    safe_get_key(allow_escape=False)


def _painel(mundo, identidade, personagem, publish, controlador, agente, relogio) -> None:
    while True:
        if agente is not None:
            agente.coletar()
        _avisar_atualizacao(mundo, identidade, mundo.atualizar_leaderboard(relogio()))
        if agente is not None:
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
        _partida(mundo, identidade, personagem, publish, controlador, relogio)


def run_ranqueada(
    *,
    populacao: Populacao | None = None,
    mundo: MundoRanqueado | None = None,
    controlador=None,
    relogio=None,
    mundo_em_segundo_plano: bool = True,
) -> None:
    """A Arena Ranqueada, da escolha do gladiador de volta ao hub.

    `relogio` devolve o instante atual (segundos, como `time.time`); os testes e
    as simulações injetam o deles.
    """
    relogio = time.time if relogio is None else relogio
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
        # A leaderboard que ficou pendente com o jogo fechado sai com o estado
        # gravado, antes da inatividade e da fila do retorno.
        agora = relogio()
        pendente = mundo.atualizar_leaderboard(agora)
        mundo.ao_retornar(agora)
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
            _avisar_atualizacao(mundo, identidade, pendente)
            pendente = None
            _painel(mundo, identidade, personagem, publish, controlador, agente, relogio)
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
            mundo.atualizar_leaderboard((kwargs.get("relogio") or time.time)())
            mostrar_classificacao(mundo)
