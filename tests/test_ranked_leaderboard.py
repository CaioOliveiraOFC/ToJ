"""A leaderboard publicada: ciclos, a fundação, a candidatura a Master e a elite.

Ladders sintéticas e pequenas (Glicko-2, ratings espaçados): o que se testa é a
regra do retrato — quem é promovido, quem fica em risco, quem sai, quem leva o
título —, não a força de build nenhuma.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.ranked import leaderboard as lb  # noqa: E402
from src.ranked import progressao as pg  # noqa: E402
from src.ranked import ranks  # noqa: E402
from src.ranked.glicko2 import Glicko2  # noqa: E402
from src.ranked.ladder import Ladder, Registro  # noqa: E402
from src.ranked.leaderboard import Leaderboard  # noqa: E402
from src.ranked.progressao import Progresso  # noqa: E402


def _ladder(n=100) -> Ladder:
    """n NPCs, do npc:00 (o mais fraco) ao último, 10 pontos de rating entre vizinhos."""
    sistema = Glicko2()
    return Ladder(
        sistema,
        [
            Registro(f"npc:{i:02d}", f"N{i}", "warrior", True, sistema.novo(1000 + 10 * i, 60))
            for i in range(n)
        ],
    )


def _fundada(n=100) -> tuple[Ladder, Leaderboard]:
    ladder, quadro = _ladder(n), Leaderboard()
    lb.publicar(ladder, quadro, None, numero=None, fundacao=True)
    return ladder, quadro


def _mover(ladder, identidade, rating, rd=60.0):
    registro = ladder[identidade]
    registro.rating = ladder.sistema.novo(rating, rd)


class TestCiclos:
    def test_o_ciclo_e_alinhado_ao_periodo(self):
        assert lb.ciclo(0) == 0 and lb.ciclo(3599) == 0 and lb.ciclo(3600) == 1
        assert lb.ciclo(86_400 * 3 + 5, 86_400) == 3
        assert lb.inicio(5, 3600) == 18_000
        quadro = Leaderboard(periodo=86_400, ciclo=2)
        assert quadro.proxima() == 3 * 86_400
        assert not quadro.pendente(86_400 * 3 - 1) and quadro.pendente(86_400 * 3)

    def test_ida_e_volta_pelo_dicionario(self):
        ladder, quadro = _fundada(20)
        quadro.ciclo, quadro.publicada_em = 7, 25_200.0
        copia = Leaderboard.de_dict(quadro.para_dict())
        assert copia.para_dict() == quadro.para_dict()


class TestFundacao:
    def test_a_elite_sai_do_percentil_e_o_resto_recebe_a_divisao_do_alvo(self):
        ladder, quadro = _fundada(100)
        ordem = ladder.classificacao()
        for r in ordem:
            pct = ladder.percentil(r.identidade)
            if pct >= lb.MINIMO_DA_ELITE:
                assert r.progresso.elite == ranks.rank_do_percentil(pct)
            else:
                assert r.progresso.elite is None
                assert r.progresso.coordenada == min(4400, int(pg.alvo(pct)))
        assert [ladder.titulo(r.identidade) for r in ordem[:6]] == [ranks.TITULO_DEFINITIVO] * 5 + [
            None
        ]
        assert len(quadro.linhas) == 100 and quadro.linhas[0]["posicao"] == 1
        assert not ladder.problemas()


class TestCandidatura:
    def _candidato(self, ladder, identidade):
        ladder[identidade].progresso = Progresso(divisao=pg.ULTIMA, pr=100, candidato=True)

    def test_promovido_quando_esta_na_posicao_de_master(self):
        ladder, quadro = _fundada()
        self._candidato(ladder, "npc:50")
        _mover(ladder, "npc:50", 1945)  # entre os 8% de cima
        resumo = lb.publicar(ladder, quadro, 3600.0, numero=1)
        p = ladder["npc:50"].progresso
        assert p.elite in pg.ELITE and not p.candidato
        evento = next(e for e in resumo["eventos"] if e["identidade"] == "npc:50")
        assert evento["evento"] == "promocao_a_elite"
        assert ladder["npc:50"].eventos[-1]["evento"] == "promocao_a_elite"

    def test_cem_pr_sem_posicao_nao_promove(self):
        ladder, quadro = _fundada()
        self._candidato(ladder, "npc:50")
        resumo = lb.publicar(ladder, quadro, 3600.0, numero=1)
        p = ladder["npc:50"].progresso
        assert p.elite is None and p.candidato  # continua candidato
        evento = next(e for e in resumo["eventos"] if e["identidade"] == "npc:50")
        assert evento["evento"] == "candidatura_mantida"
        assert "percentil" in evento["motivos"][0]

    def test_incerteza_alta_segura_a_promocao(self):
        ladder, quadro = _fundada()
        self._candidato(ladder, "npc:50")
        _mover(ladder, "npc:50", 1990, rd=200)
        resumo = lb.publicar(ladder, quadro, 3600.0, numero=1)
        assert ladder["npc:50"].progresso.candidato
        evento = next(e for e in resumo["eventos"] if e["identidade"] == "npc:50")
        assert any("incerteza" in m for m in evento["motivos"])

    def test_npc_e_jogador_seguem_a_mesma_regra(self):
        ladder, quadro = _fundada()
        sistema = ladder.sistema
        eu = Registro("jogador:1", "Eu", "mage", False, sistema.novo(1945, 60), vitorias=12)
        eu.progresso = Progresso(divisao=pg.ULTIMA, pr=100, candidato=True)
        ladder.adicionar(eu)
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        assert eu.progresso.elite in pg.ELITE


class TestElite:
    def test_risco_primeiro_e_rebaixamento_no_retrato_seguinte(self):
        ladder, quadro = _fundada()
        membro = next(r for r in ladder.classificacao() if r.progresso.elite == "Master")
        # Logo abaixo do mínimo de Master, dentro da faixa de risco.
        _mover(ladder, membro.identidade, 1000 + 10 * 89 + 5)
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        assert membro.progresso.elite == "Master" and membro.progresso.risco
        lb.publicar(ladder, quadro, 7200.0, numero=2)
        assert membro.progresso.elite is None
        assert membro.progresso.divisao is not None and membro.progresso.divisao <= pg.ULTIMA
        assert [e["evento"] for e in membro.eventos[-2:]] == ["em_risco", "rebaixamento_da_elite"]

    def test_voltar_ao_minimo_tira_do_risco(self):
        ladder, quadro = _fundada()
        membro = next(r for r in ladder.classificacao() if r.progresso.elite == "Master")
        original = ladder.valor(membro.identidade)
        _mover(ladder, membro.identidade, 1000 + 10 * 89 + 5)
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        _mover(ladder, membro.identidade, original)
        lb.publicar(ladder, quadro, 7200.0, numero=2)
        assert membro.progresso.elite is not None and not membro.progresso.risco

    def test_queda_grande_rebaixa_de_uma_vez(self):
        ladder, quadro = _fundada()
        membro = ladder.classificacao()[0]
        _mover(ladder, membro.identidade, 1500)
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        assert membro.progresso.elite is None and not membro.progresso.risco

    def test_ninguem_precisa_jogar_entre_retratos(self):
        ladder, quadro = _fundada()
        antes = [(r.identidade, r.progresso.elite) for r in ladder.classificacao()]
        for numero in range(1, 6):
            lb.publicar(ladder, quadro, 3600.0 * numero, numero=numero)
        assert [(r.identidade, r.progresso.elite) for r in ladder.classificacao()] == antes

    def test_os_definitive_masters_sao_os_cinco_da_elite_mais_bem_colocados(self):
        ladder, quadro = _fundada()
        # O terceiro colocado cai para fora da elite: o sexto da elite herda o título.
        terceiro = ladder.classificacao()[2]
        _mover(ladder, terceiro.identidade, 1200)
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        titulados = {r.identidade for r in ladder.registros() if r.progresso.titulo}
        elite = [r for r in ladder.classificacao() if r.progresso.elite]
        assert titulados == {r.identidade for r in elite[:5]}
        assert terceiro.identidade not in titulados

    def test_a_variacao_de_posicoes_entre_retratos(self):
        ladder, quadro = _fundada()
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        _mover(ladder, "npc:50", 1000 + 10 * 60 + 5)
        lb.publicar(ladder, quadro, 7200.0, numero=2)
        assert quadro.variacao("npc:50") == 10
        assert quadro.variacao("npc:59") == -1


class TestIntegridade:
    def test_estado_inconsistente_adia_a_atualizacao(self):
        ladder, quadro = _fundada()
        lb.publicar(ladder, quadro, 3600.0, numero=1)
        ladder["npc:10"].progresso.candidato = True  # candidato fora de Obsidian I
        resumo = lb.publicar(ladder, quadro, 7200.0, numero=2)
        assert resumo["adiada"] and quadro.ciclo == 1 and quadro.adiada
        ladder["npc:10"].progresso.candidato = False
        assert not lb.publicar(ladder, quadro, 7300.0, numero=2)["adiada"]
        assert quadro.ciclo == 2 and not quadro.adiada

    @pytest.mark.parametrize(
        "estrago",
        [
            lambda r: setattr(r.progresso, "pr", 140),
            lambda r: setattr(r.progresso, "elite", "Lenda"),
            lambda r: setattr(r, "vitorias", -1),
        ],
    )
    def test_os_problemas_que_a_ladder_acusa(self, estrago):
        ladder, _ = _fundada(20)
        estrago(ladder["npc:03"])
        assert any("npc:03" in p for p in ladder.problemas())
