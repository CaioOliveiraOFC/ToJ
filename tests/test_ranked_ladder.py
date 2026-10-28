"""A Ladder, os ranks por percentil e o matchmaking da Ranked, com estados pequenos.

Os gladiadores daqui são registros sintéticos: o que se testa é a regra da
Ladder (quem aparece, em que posição, com que rank, o que uma partida muda) e a
do matchmaking (a etapa, a faixa, a sequência, a repetição), não a força de
build nenhuma. Os dois sistemas de rating passam pelos mesmos testes.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ranked import leaderboard as lb  # noqa: E402
from src.ranked import matchmaking as mm  # noqa: E402
from src.ranked import progressao as pg  # noqa: E402
from src.ranked import ranks  # noqa: E402
from src.ranked.glicko2 import Glicko2  # noqa: E402
from src.ranked.ladder import POSICIONAMENTO, Ladder, Registro  # noqa: E402
from src.ranked.trueskill import TrueSkill  # noqa: E402

SISTEMAS = [Glicko2(), TrueSkill()]


def _ladder(sistema, n=40, jogador=True) -> Ladder:
    """n NPCs espalhados em força, e um gladiador do jogador recém-chegado."""
    ladder = Ladder(sistema)
    for i in range(n):
        if isinstance(sistema, Glicko2):
            rating = sistema.novo(1200 + 15 * i, 60)
        else:
            rating = sistema.novo(15 + 0.5 * i, 1.5)
        ladder.adicionar(Registro(f"npc:{i:02d}", f"N{i}", "warrior", True, rating))
    if jogador:
        ladder.adicionar(Registro("jogador:1", "Eu", "mage", False, sistema.novo()))
    return ladder


@pytest.mark.parametrize("sistema", SISTEMAS, ids=lambda s: s.nome)
class TestLadder:
    def test_quem_posiciona_nao_aparece_e_nao_tem_rank(self, sistema):
        ladder = _ladder(sistema)
        assert ladder.posicao("jogador:1") is None
        assert ladder.rank("jogador:1") is None and ladder.percentil("jogador:1") is None
        assert len(ladder.classificacao()) == ladder.competitivos() == 40

    def test_posicao_percentil_e_rank_seguem_a_classificacao(self, sistema):
        ladder = _ladder(sistema)
        ordem = ladder.classificacao()
        for i, r in enumerate(ordem, start=1):
            assert ladder.posicao(r.identidade) == i
        assert ordem[0].identidade == "npc:39"
        assert ladder.percentil("npc:39") == 100.0 and ladder.percentil("npc:00") == 0.0
        assert ladder.rank("npc:39") == "Distinguished Master"
        assert ladder.rank("npc:00") == "Iron"
        # O título é da leaderboard publicada, não da posição de agora: os cinco
        # primeiros DA ELITE. Com 40, a elite (percentil ≥ 92) tem só 4.
        assert ladder.titulo("npc:39") is None
        lb.publicar(ladder, lb.Leaderboard(), None, numero=None, fundacao=True)
        assert [ladder.titulo(r.identidade) for r in ordem[:5]] == [ranks.TITULO_DEFINITIVO] * 4 + [
            None
        ]

    def test_a_partida_atualiza_os_dois_lados_e_o_historico(self, sistema):
        ladder = _ladder(sistema)
        antes_a, antes_b = ladder.valor("npc:10"), ladder.valor("npc:30")
        mudou = ladder.registrar("npc:10", "npc:30", "npc:10", origem="npc")
        assert ladder.valor("npc:10") > antes_a and ladder.valor("npc:30") < antes_b
        assert mudou.vencedor == "npc:10" and mudou.probabilidade_do_vencedor < 0.5
        assert mudou.perdedor == "npc:30" and not mudou.empate
        assert (ladder["npc:10"].vitorias, ladder["npc:30"].derrotas) == (1, 1)
        entrada = ladder["npc:10"].historico[-1]
        assert entrada["oponente"] == "npc:30" and entrada["venceu"] and entrada["origem"] == "npc"
        assert entrada["resultado"] == "vitoria"
        assert ladder["npc:30"].historico[-1]["resultado"] == "derrota"

    def test_dez_partidas_posicionam_o_jogador(self, sistema):
        ladder = _ladder(sistema)
        for k in range(POSICIONAMENTO):
            assert ladder.posicao("jogador:1") is None
            ladder.registrar("jogador:1", f"npc:{k:02d}", "jogador:1", origem="ranqueada")
        assert ladder.posicao("jogador:1") is not None
        assert ladder.competitivos() == 41

    def test_ida_e_volta_pelo_dicionario(self, sistema):
        ladder = _ladder(sistema)
        ladder.registrar("npc:01", "jogador:1", "jogador:1", origem="ranqueada")
        copia = Ladder.de_dict(sistema, ladder.para_dict())
        assert copia.para_dict() == ladder.para_dict()
        assert [r.identidade for r in copia.classificacao()] == [
            r.identidade for r in ladder.classificacao()
        ]

    def test_anulada_entra_no_historico_e_nao_no_rating(self, sistema):
        ladder = _ladder(sistema)
        antes = (ladder.valor("npc:10"), ladder.valor("jogador:1"))
        ladder.registrar_anulada("npc:10", "jogador:1", origem="mundo", motivo="erro técnico: X")
        ladder.registrar_sem_resultado("npc:10", "jogador:1", origem="mundo")  # o da Fase 6
        assert (ladder.valor("npc:10"), ladder.valor("jogador:1")) == antes
        assert ladder["jogador:1"].partidas == 0 and ladder["npc:10"].vitorias == 0
        entrada = ladder["jogador:1"].historico[-2]
        assert (entrada["resultado"], entrada["motivo"]) == ("anulada", "erro técnico: X")
        assert entrada["venceu"] is None and entrada["oponente"] == "npc:10"
        assert ladder["jogador:1"].historico[-1]["motivo"] == "limite"
        copia = Ladder.de_dict(sistema, ladder.para_dict())
        assert copia["jogador:1"].historico == ladder["jogador:1"].historico

    def test_identidade_repetida_e_recusada_e_resultado_incoerente_tambem(self, sistema):
        ladder = _ladder(sistema)
        with pytest.raises(ValueError):
            ladder.registrar("npc:01", "npc:02", "npc:03", origem="x")
        with pytest.raises(ValueError):
            ladder.registrar_empate("npc:01", "npc:01", origem="x", motivo="impasse")

    def test_identidade_repetida_e_recusada(self, sistema):
        ladder = _ladder(sistema)
        with pytest.raises(ValueError):
            ladder.adicionar(Registro("npc:01", "x", "mage", True, sistema.novo()))


class TestEmpateEProgressao:
    """Empate e PR, no sistema do jogo (o TrueSkill só empata com margem de empate)."""

    def test_empate_vale_meio_ponto_e_conta_como_partida(self):
        sistema = Glicko2()
        ladder = _ladder(sistema)
        antes_forte, antes_fraco = ladder.valor("npc:30"), ladder.valor("npc:10")
        mudou = ladder.registrar_empate("npc:30", "npc:10", origem="mundo", motivo="impasse")
        assert mudou.empate and mudou.vencedor is None and mudou.perdedor is None
        assert ladder.valor("npc:30") < antes_forte and ladder.valor("npc:10") > antes_fraco
        r = ladder["npc:30"]
        assert (r.vitorias, r.derrotas, r.empates, r.partidas) == (0, 0, 1, 1)
        entrada = r.historico[-1]
        assert (entrada["resultado"], entrada["motivo"], entrada["venceu"]) == (
            "empate",
            "impasse",
            None,
        )

    def test_empates_contam_no_posicionamento_e_a_divisao_nasce_no_alvo(self):
        sistema = Glicko2()
        ladder = _ladder(sistema)
        for k in range(POSICIONAMENTO - 1):
            ladder.registrar_empate("jogador:1", f"npc:{20 + k:02d}", origem="r", motivo="impasse")
        assert ladder["jogador:1"].progresso.divisao is None and ladder.posicao("jogador:1") is None
        mudou = ladder.registrar("jogador:1", "npc:30", "jogador:1", origem="r")
        eu = ladder["jogador:1"]
        assert eu.posicionado and eu.progresso.divisao is not None
        assert mudou.eventos["jogador:1"][0]["evento"] == "posicionamento"
        assert mudou.pr["jogador:1"] is None  # a partida que posiciona não dá PR
        assert eu.progresso.coordenada == min(4400, int(ladder.alvo("jogador:1")))
        assert eu.eventos[-1]["evento"] == "posicionamento"
        assert ladder.exibicao("jogador:1").endswith("PR")

    def test_depois_de_posicionado_cada_partida_mexe_no_pr_dos_dois(self):
        sistema = Glicko2()
        ladder = _ladder(sistema)
        lb.publicar(ladder, lb.Leaderboard(), None, numero=None, fundacao=True)
        a, b = "npc:10", "npc:12"
        pr_a, pr_b = ladder[a].progresso.coordenada, ladder[b].progresso.coordenada
        mudou = ladder.registrar(a, b, a, origem="mundo")
        assert mudou.pr[a] > 0 > mudou.pr[b]
        assert ladder[a].progresso.coordenada == pr_a + mudou.pr[a] or mudou.eventos[a]
        assert ladder[b].historico[-1]["pr"] == mudou.pr[b]
        assert ladder[b].progresso.coordenada <= pr_b

    def test_a_elite_nao_tem_pr(self):
        sistema = Glicko2()
        ladder = _ladder(sistema)
        lb.publicar(ladder, lb.Leaderboard(), None, numero=None, fundacao=True)
        mudou = ladder.registrar("npc:39", "npc:38", "npc:38", origem="mundo")
        assert mudou.pr["npc:39"] is None and ladder["npc:39"].progresso.elite in pg.ELITE

    def test_ida_e_volta_com_progresso_e_eventos(self):
        sistema = Glicko2()
        ladder = _ladder(sistema)
        lb.publicar(ladder, lb.Leaderboard(), None, numero=None, fundacao=True)
        ladder.registrar_empate("npc:05", "npc:06", origem="mundo", motivo="teto")
        copia = Ladder.de_dict(sistema, ladder.para_dict())
        assert copia.para_dict() == ladder.para_dict()
        assert copia["npc:05"].empates == 1


class TestRanks:
    def test_doze_ranks_em_ordem_e_limites_crescentes(self):
        assert len(ranks.RANKS) == 12
        assert ranks.RANKS[0] == "Iron" and ranks.RANKS[-1] == "Distinguished Master"
        assert ranks.rank_do_percentil(0) == "Iron"
        assert ranks.rank_do_percentil(99.9) == "Distinguished Master"
        for nome, minimo in zip(ranks.RANKS, ranks.LIMITES):
            assert ranks.rank_do_percentil(minimo) == nome

    def test_com_186_nenhum_rank_fica_vazio(self):
        nomes = {ranks.rank_do_percentil(ranks.percentil(p, 186)) for p in range(1, 187)}
        assert nomes == set(ranks.RANKS)

    def test_percentil_fora_da_populacao(self):
        with pytest.raises(ValueError):
            ranks.percentil(0, 10)


@pytest.mark.parametrize("sistema", SISTEMAS, ids=lambda s: s.nome)
class TestMatchmaking:
    def test_as_etapas_do_posicionamento(self, sistema):
        assert [mm.fase(k) for k in range(12)] == (
            [mm.DESCOBERTA] * 4 + [mm.NIVELAMENTO] * 3 + [mm.VALIDACAO] * 3 + [mm.RANQUEADA] * 2
        )

    def test_e_deterministico_pelo_gerador(self, sistema):
        ladder = _ladder(sistema)
        a = mm.escolher_oponente(ladder, "jogador:1", random.Random(5))
        b = mm.escolher_oponente(ladder, "jogador:1", random.Random(5))
        assert a == b and a.oponente.startswith("npc:")

    def test_a_descoberta_espalha_e_a_validacao_aperta(self, sistema):
        ladder = _ladder(sistema)
        rng = random.Random(1)
        largos = {mm.escolher_oponente(ladder, "jogador:1", rng).oponente for _ in range(40)}
        for k in range(7):
            ladder.registrar("jogador:1", f"npc:{k:02d}", f"npc:{k:02d}", origem="teste")
            ladder.registrar("jogador:1", f"npc:{39 - k:02d}", "jogador:1", origem="teste")
        assert mm.fase(ladder["jogador:1"].partidas) == mm.RANQUEADA
        ladder["jogador:1"].vitorias, ladder["jogador:1"].derrotas = 3, 4  # volta à validação
        ladder["jogador:1"].historico.clear()
        assert mm.fase(ladder["jogador:1"].partidas) == mm.VALIDACAO
        estreitos = {mm.escolher_oponente(ladder, "jogador:1", rng).oponente for _ in range(40)}
        assert len(largos) > len(estreitos)
        meu = ladder.valor("jogador:1")
        distancia = max(abs(ladder.valor(o) - meu) for o in estreitos)
        assert distancia <= 0.6 * mm.desvio_da_populacao(
            ladder, [r.identidade for r in ladder.npcs()]
        )

    def test_quem_jogou_agora_fica_de_fora_e_os_recentes_custam(self, sistema):
        ladder = _ladder(sistema)
        rng = random.Random(3)
        vistos = []
        for k in range(30):
            escolha = mm.escolher_oponente(ladder, "jogador:1", rng)
            assert not vistos or escolha.oponente != vistos[-1]
            vistos.append(escolha.oponente)
            vencedor = "jogador:1" if k % 2 else escolha.oponente
            ladder.registrar("jogador:1", escolha.oponente, vencedor, origem="teste")
        # No meio de 40 NPCs, nenhum adversário volta dentro de 5 partidas.
        assert all(o not in vistos[max(0, i - 5) : i] for i, o in enumerate(vistos))

    def test_o_custo_de_repeticao_pesa_frequencia_e_recencia(self, sistema):
        ladder = _ladder(sistema)
        for oponente in ("npc:01", "npc:02", "npc:01", "npc:03"):
            ladder.registrar("jogador:1", oponente, oponente, origem="teste")
        custo = mm.custo_de_repeticao(ladder, "jogador:1")
        peso, meia = mm.PESO_DA_REPETICAO, mm.MEIA_VIDA
        assert custo["npc:03"] == pytest.approx(peso)
        assert custo["npc:01"] == pytest.approx(peso * (0.5 ** (1 / meia) + 0.5 ** (3 / meia)))
        assert custo["npc:01"] > custo["npc:02"] and "npc:04" not in custo

    def test_sem_alternativa_o_matchmaking_repete_e_nao_trava(self, sistema):
        ladder = _ladder(sistema, n=2)
        ladder.registrar("jogador:1", "npc:00", "npc:00", origem="teste")
        escolha = mm.escolher_oponente(ladder, "jogador:1", random.Random(1), excluir={"npc:01"})
        assert escolha.oponente == "npc:00"

    def test_a_sequencia_so_conta_contra_quem_nao_e_muito_mais_fraco(self, sistema):
        ladder = _ladder(sistema)
        desvio = 100.0

        def historico(*entradas):
            ladder["jogador:1"].historico = [
                {"venceu": v, "antes": 1000.0, "oponente_antes": 1000.0 + d} for v, d in entradas
            ]
            return mm.empurrao_da_sequencia(ladder, "jogador:1", desvio)

        passo = mm.EMPURRAO_POR_RESULTADO * desvio
        # Três vitórias contra quem estava muito abaixo (mais de meio desvio): nada.
        assert historico((True, -80), (True, -60), (True, -51)) == 0.0
        # Contra o mesmo nível ou acima, cada vitória empurra, até o teto.
        assert historico((True, -40), (True, 0)) == pytest.approx(2 * passo)
        assert historico(*[(True, 30)] * 5) == pytest.approx(mm.SEQUENCIA_MAXIMA * passo)
        # A sequência acaba no primeiro resultado do outro tipo.
        assert historico((True, 0), (True, 0), (False, 0)) == pytest.approx(-passo)
        # Derrota só conta se o vencedor não estava muito acima.
        assert historico((False, 80), (False, 10)) == pytest.approx(-passo)
        assert historico() == 0.0
        # Partida anulada (ou sem resultado, da Fase 6) não conta nem quebra a sequência.
        assert historico((True, 0), (None, 0), (True, 0)) == pytest.approx(2 * passo)
        assert historico((None, 0)) == 0.0
        # O empate quebra a sequência.
        ladder["jogador:1"].historico = [
            {"venceu": True, "resultado": "vitoria", "antes": 1000.0, "oponente_antes": 1000.0},
            {"venceu": None, "resultado": "empate", "antes": 1000.0, "oponente_antes": 1000.0},
            {"venceu": True, "resultado": "vitoria", "antes": 1000.0, "oponente_antes": 1000.0},
        ]
        assert mm.empurrao_da_sequencia(ladder, "jogador:1", desvio) == pytest.approx(passo)
        ladder["jogador:1"].historico.pop()
        assert mm.empurrao_da_sequencia(ladder, "jogador:1", desvio) == 0.0

    def test_o_proprio_gladiador_e_excluidos_nunca_saem(self, sistema):
        ladder = _ladder(sistema, n=6)
        rng = random.Random(9)
        for _ in range(30):
            escolha = mm.escolher_oponente(ladder, "jogador:1", rng, excluir={"npc:03"})
            assert escolha.oponente not in {"jogador:1", "npc:03"}

    def test_rodada_suica_e_pares_de_npc_sem_repeticao(self, sistema):
        ladder = _ladder(sistema, jogador=False)
        pares = mm.rodada_suica(ladder, random.Random(2))
        nomes = [i for par in pares for i in par]
        assert len(pares) == 20 and len(set(nomes)) == 40
        lote = mm.parear_npcs(ladder, random.Random(2), 10)
        nomes = [i for par in lote for i in par]
        assert len(lote) == 10 and len(set(nomes)) == 20
