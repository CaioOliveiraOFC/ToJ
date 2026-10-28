"""O empate técnico por impasse: quando a partida para de andar, e só aí.

O árbitro lê o HP e o MP de cada lado ao fim da rodada. Os casos sintéticos
fixam a regra (mínimo novo zera a contagem, a folga, o teto); os casos reais
vêm das trajetórias gravadas em `reports/ranked/fase61/trajetorias.jsonl` —
uma dupla que não termina em 1.500 rodadas e uma longa que termina em KO com
desgaste contínuo.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.engine import ranked_partidas  # noqa: E402
from src.engine.arena_populacao import Populacao  # noqa: E402
from src.ranked.impasse import (  # noqa: E402
    IMPASSE,
    JANELA,
    NO_TETO,
    ArbitroDeImpasse,
    Observador,
)

MAXIMOS = [[1000, 1000], [100, 100]]


def _rodar(arbitro, estados):
    for rodada, (hp, mp) in enumerate(estados, start=1):
        veredito = arbitro.observar(rodada, hp, mp, MAXIMOS)
        if veredito is not None:
            return veredito
    return None


class TestRegra:
    def test_quem_se_cura_tanto_quanto_apanha_empata_na_janela(self):
        # Os dois oscilam entre 900 e 1000 de HP, com o MP no chão: nada novo.
        estados = [([900 + 100 * (r % 2), 950], [0, 0]) for r in range(400)]
        veredito = _rodar(ArbitroDeImpasse(janela=50), estados)
        assert veredito is not None and veredito.motivo == IMPASSE
        assert veredito.rodada == 51

    def test_desgaste_continuo_nunca_empata(self):
        """Uma build de cura que está ganhando: o outro chega a HP cada vez mais baixo."""
        estados = []
        for r in range(400):
            # Cai 2% a cada 30 rodadas, com a cura devolvendo o resto no meio.
            base = 1000 - 20 * (r // 30)
            estados.append(([base - (r % 30), 1000], [50, 50]))
        assert _rodar(ArbitroDeImpasse(janela=50), estados) is None

    def test_o_mp_que_ainda_cai_conta_como_desgaste(self):
        estados = [([900, 900], [100 - r // 3, 100]) for r in range(200)]
        assert _rodar(ArbitroDeImpasse(janela=50), estados) is None

    def test_a_folga_ignora_minimos_de_ruido(self):
        # Mínimos novos de 0,5% não contam (folga de 1%).
        estados = [([900 - (r % 2) * 5 - r // 100, 900], [0, 0]) for r in range(300)]
        veredito = _rodar(ArbitroDeImpasse(janela=60, margem=0.01), estados)
        assert veredito is not None and veredito.motivo == IMPASSE

    def test_o_teto_encerra_mesmo_andando(self):
        estados = [([1000 - r, 1000], [0, 0]) for r in range(50)]
        veredito = _rodar(ArbitroDeImpasse(janela=1000, teto=20), estados)
        assert veredito is not None and (veredito.motivo, veredito.rodada) == (NO_TETO, 20)

    def test_a_contagem_e_o_que_falta(self):
        arbitro = ArbitroDeImpasse(janela=10)
        arbitro.observar(1, [500, 500], [0, 0], MAXIMOS)
        for r in range(2, 6):
            arbitro.observar(r, [600, 600], [0, 0], MAXIMOS)
        assert (arbitro.sem_desgaste, arbitro.faltam) == (4, 6)
        arbitro.observar(6, [400, 600], [0, 0], MAXIMOS)
        assert (arbitro.sem_desgaste, arbitro.faltam) == (0, 10)
        assert arbitro.veredito is None


def _trajetoria(a: str, b: str, motivo: str) -> dict:
    caminho = ROOT / "reports" / "ranked" / "fase61" / "trajetorias.jsonl"
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        r = json.loads(linha)
        if (r["a"], r["b"]) == (a, b) and r["motivo"] == motivo:
            return r
    raise AssertionError(f"trajetória {a}×{b} ({motivo}) não gravada")


class TestTrajetoriasReais:
    def test_a_dupla_sem_fim_vira_empate(self):
        r = _trajetoria("M33", "R31", "limite")
        arbitro = ArbitroDeImpasse()
        veredito = None
        for rodada, (hp, mp) in enumerate(zip(r["hp"], r["mp"]), start=1):
            veredito = arbitro.observar(rodada, hp, mp, r["maximos"])
            if veredito:
                break
        assert veredito is not None and veredito.motivo == IMPASSE
        assert JANELA < veredito.rodada < 500

    def test_a_partida_longa_que_anda_termina_em_ko(self):
        r = _trajetoria("W05", "W44", "ko")
        assert r["rodadas"] == 242
        arbitro = ArbitroDeImpasse()
        for rodada, (hp, mp) in enumerate(zip(r["hp"], r["mp"]), start=1):
            assert arbitro.observar(rodada, hp, mp, r["maximos"]) is None


class TestNoMotor:
    def test_o_confronto_vira_empate_tecnico_pelo_arbitro(self):
        confronto = ranked_partidas.jogar(
            Populacao(), "W30", "W31", 4, arbitro=ArbitroDeImpasse(teto=3)
        )
        assert confronto.vencedor is None and confronto.perdedor is None
        assert (confronto.motivo, confronto.rodadas, confronto.resultado) == (
            NO_TETO,
            3,
            ranked_partidas.EMPATE,
        )
        assert confronto.para_dict()["resultado"] == "empate"

    def test_o_observador_ve_os_lados_na_ordem_a_b(self):
        pop = Populacao()
        par, impar = Observador(teto=2), Observador(teto=2)
        ranked_partidas.jogar(pop, "W30", "M30", 4, arbitro=par)
        ranked_partidas.jogar(pop, "W30", "M30", 5, arbitro=impar)
        # W30 vem primeiro nas duas, qualquer que seja o lado que a seed deu.
        assert par.maximos == impar.maximos

    @pytest.mark.parametrize("semente", [4, 5])
    def test_a_vitoria_continua_vitoria(self, semente):
        confronto = ranked_partidas.jogar(Populacao(), "W30", "W31", semente)
        assert confronto.vencedor in ("W30", "W31") and confronto.resultado == "vitoria"
