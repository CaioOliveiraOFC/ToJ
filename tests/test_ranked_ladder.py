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

from src.ranked import matchmaking as mm  # noqa: E402
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
        assert [ladder.titulo(r.identidade) for r in ordem[:6]] == [ranks.TITULO_DEFINITIVO] * 5 + [
            None
        ]

    def test_a_partida_atualiza_os_dois_lados_e_o_historico(self, sistema):
        ladder = _ladder(sistema)
        antes_a, antes_b = ladder.valor("npc:10"), ladder.valor("npc:30")
        mudou = ladder.registrar("npc:10", "npc:30", "npc:10", origem="npc")
        assert ladder.valor("npc:10") > antes_a and ladder.valor("npc:30") < antes_b
        assert mudou.vencedor == "npc:10" and mudou.probabilidade_do_vencedor < 0.5
        assert (ladder["npc:10"].vitorias, ladder["npc:30"].derrotas) == (1, 1)
        entrada = ladder["npc:10"].historico[-1]
        assert entrada["oponente"] == "npc:30" and entrada["venceu"] and entrada["origem"] == "npc"

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

    def test_sem_resultado_entra_no_historico_e_nao_no_rating(self, sistema):
        ladder = _ladder(sistema)
        antes = (ladder.valor("npc:10"), ladder.valor("jogador:1"))
        ladder.registrar_sem_resultado("npc:10", "jogador:1", origem="mundo")
        assert (ladder.valor("npc:10"), ladder.valor("jogador:1")) == antes
        assert ladder["jogador:1"].partidas == 0 and ladder["npc:10"].vitorias == 0
        entrada = ladder["jogador:1"].historico[-1]
        assert entrada["venceu"] is None and entrada["oponente"] == "npc:10"
        copia = Ladder.de_dict(sistema, ladder.para_dict())
        assert copia["jogador:1"].historico == ladder["jogador:1"].historico

    def test_identidade_repetida_e_recusada(self, sistema):
        ladder = _ladder(sistema)
        with pytest.raises(ValueError):
            ladder.adicionar(Registro("npc:01", "x", "mage", True, sistema.novo()))


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

    def test_quem_jogou_agora_fica_de_fora(self, sistema):
        ladder = _ladder(sistema)
        rng = random.Random(3)
        vistos = []
        for _ in range(mm.RECENTES):
            escolha = mm.escolher_oponente(ladder, "jogador:1", rng)
            vistos.append(escolha.oponente)
            ladder.registrar("jogador:1", escolha.oponente, escolha.oponente, origem="teste")
        proxima = mm.escolher_oponente(ladder, "jogador:1", rng)
        assert proxima.oponente not in vistos[-mm.RECENTES :]

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
        # Confronto sem resultado não conta nem quebra a sequência.
        assert historico((True, 0), (None, 0), (True, 0)) == pytest.approx(2 * passo)
        assert historico((None, 0)) == 0.0

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
