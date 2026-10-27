"""A IA estratégica como adversária da Arena offline.

Ela escolhe só pela própria `DuelView`, simula só sobre cópias, e é a mesma IA
da Copa Arena 03 v2: mudar de `tools/` para `src/sim/` não mudou uma decisão.
Os duelos daqui são entre gladiadores da população publicada, com sementes
fixas.

E a Arena é offline de verdade: o fluxo inteiro não carrega a camada
multiplayer, nem `websockets`, nem abre conexão.
"""

from __future__ import annotations

import copy
import random
import subprocess
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.engine.arena_populacao import Populacao  # noqa: E402
from src.mechanics.pvp_duel import SIDES, Duel, run_round  # noqa: E402
from src.sim.ia_estrategica import Configuracao, IAEstrategica  # noqa: E402
from src.storage.save_manager import to_save_data  # noqa: E402

RAPIDA = Configuracao(rollouts=2, rollouts_criticos=3)


@pytest.fixture(scope="module")
def populacao() -> Populacao:
    return Populacao()


def _par(populacao, a=("rogue", 0), b=("mage", -1)):
    return (
        populacao.gladiador(populacao.oponentes(a[0])[a[1]]),
        populacao.gladiador(populacao.oponentes(b[0])[b[1]]),
    )


def _estado(heroi) -> tuple:
    return (
        to_save_data(heroi, 1),
        heroi.get_hp(),
        heroi.get_mp(),
        copy.deepcopy(dict(heroi.active_effects)),
        copy.deepcopy(dict(heroi.active_buffs)),
        dict(getattr(heroi, "skill_cooldowns", {}) or {}),
        heroi._death_ignore_used,
    )


def _duelo_ia(populacao, seed, config=RAPIDA, fabrica=IAEstrategica, limite=200):
    a, b = _par(populacao)
    duelo = Duel(a, b, rng=random.Random(seed))
    ias = {"p1": fabrica(a.hero, config), "p2": fabrica(b.hero, config)}
    while not duelo.finished and duelo.round_number <= limite:
        run_round(duelo, ias)
    return duelo, ias


class TestLegalidade:
    def test_toda_escolha_e_legal_e_a_ia_nunca_se_rende(self, populacao):
        acoes = []

        class Conferida(IAEstrategica):
            def choose(self, view):
                acao = super().choose(view)
                assert acao in view.legal_actions
                assert acao.kind != "surrender"
                acoes.append(acao)
                return acao

        duelo, _ = _duelo_ia(populacao, 3, fabrica=Conferida)
        assert duelo.finished
        assert len(acoes) == 2 * duelo.result.rounds

    def test_cada_decisao_registra_o_motivo(self, populacao):
        duelo, ias = _duelo_ia(populacao, 4)
        for ia in ias.values():
            assert len(ia.decisoes) == duelo.result.rounds
            assert all(d["motivo"] and d["acao"] for d in ia.decisoes)
            # Sem referência, nada da Copa 03 entra no registro.
            assert all("politica_copa" not in d for d in ia.decisoes)


class TestDeterminismo:
    def test_mesma_semente_mesma_partida(self, populacao):
        um, ias_um = _duelo_ia(populacao, 21)
        dois, ias_dois = _duelo_ia(populacao, 21)
        assert [r.actions for r in um.history] == [r.actions for r in dois.history]
        assert [r.hp_end for r in um.history] == [r.hp_end for r in dois.history]
        assert um.result == dois.result
        for lado in SIDES:
            assert ias_um[lado].decisoes == ias_dois[lado].decisoes

    def test_a_mudanca_para_src_sim_nao_mudou_decisao(self, populacao):
        """A IA da Copa 03 v2 (com a `PoliticaCopa` só de registro) decide igual."""
        from tools.arena_ia_estrategica import IAEstrategica as DaCopa

        jogo, _ = _duelo_ia(populacao, 8)
        copa, ias = _duelo_ia(populacao, 8, fabrica=DaCopa)
        assert [r.actions for r in jogo.history] == [r.actions for r in copa.history]
        assert all("politica_copa" in d for d in ias["p1"].decisoes)


class TestIsolamento:
    def test_escolher_nao_toca_duelo_herois_nem_random_global(self, populacao):
        a, b = _par(populacao)
        duelo = Duel(a, b, rng=random.Random(5))
        ias = {lado: IAEstrategica(duelo.hero(lado), RAPIDA) for lado in SIDES}
        random.seed(1234)
        for _ in range(6):
            if duelo.finished:
                break
            visoes = {lado: duelo.view(lado) for lado in SIDES}
            antes = (
                random.getstate(),
                duelo._rng.getstate(),
                {lado: _estado(duelo.hero(lado)) for lado in SIDES},
                len(duelo.history),
            )
            escolhas = {lado: ias[lado].choose(visoes[lado]) for lado in SIDES}
            depois = (
                random.getstate(),
                duelo._rng.getstate(),
                {lado: _estado(duelo.hero(lado)) for lado in SIDES},
                len(duelo.history),
            )
            assert depois == antes
            duelo.play_round(escolhas)

    def test_a_arena_nao_carrega_rede_nem_multiplayer(self):
        codigo = (
            "import sys; sys.path.insert(0, '.');"
            "import src.engine.bootstrap, src.engine.arena_mode;"
            "from src.engine.arena_populacao import Populacao; Populacao();"
            "carregados = [m for m in sys.modules"
            " if m.startswith(('src.multiplayer', 'websockets', 'tools'))];"
            "print(carregados)"
        )
        saida = subprocess.run(
            [sys.executable, "-c", codigo], cwd=ROOT, capture_output=True, text=True, check=True
        )
        assert saida.stdout.strip() == "[]", saida.stdout

    def test_uma_partida_inteira_sem_rede(self, populacao, monkeypatch):
        import socket

        def proibido(*_a, **_k):
            raise AssertionError("a Arena offline tentou abrir conexão")

        monkeypatch.setattr(socket.socket, "connect", proibido)
        monkeypatch.setattr(socket, "create_connection", proibido)
        duelo, _ = _duelo_ia(populacao, 6)
        assert duelo.finished


class TestDesempenho:
    def test_a_ia_padrao_decide_rapido(self, populacao):
        """O orçamento padrão (o da Copa 03 v2), medido decisão a decisão."""
        tempos = []

        class Cronometrada(IAEstrategica):
            def choose(self, view):
                inicio = time.perf_counter()
                acao = super().choose(view)
                tempos.append(time.perf_counter() - inicio)
                return acao

        _duelo_ia(populacao, 9, config=Configuracao(), fabrica=Cronometrada, limite=30)
        tempos.sort()
        assert tempos[len(tempos) // 2] < 1.0, tempos
        assert tempos[-1] < 5.0, tempos
