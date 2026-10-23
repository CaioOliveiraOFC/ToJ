"""KI-003: cair alguns níveis atrás não pode ser um precipício.

O gerador já tinha uma regra de progressão relativa ao herói: nos níveis da
largada, o monstro comum fica no máximo `early_max_above_player` acima dele. No
nível 4 essa regra acabava de uma vez, e o andar inteiro voltava. Na auditoria
`0ab837b9`, nenhuma das 87 runs que caíram 3 ou mais níveis atrás do andar
voltou a ficar a no máximo 1, e os mergulhadores morriam exatamente no degrau:
quem estava para trás e conseguia subir de nível era premiado com monstros 5 a
10 níveis acima.

A regra agora afrouxa em vez de sumir: a folga cresce um nível por nível do
herói. Quem está no ritmo do andar não a sente; quem caiu muito para trás
continua lutando contra monstro acima dele — o risco fica —, e a XP por nível do
monstro, que já existia, paga a volta.
"""

from __future__ import annotations

import random

import pytest

from src.content.factories.monsters import (
    calculate_scaled_monster_level,
    generation_rules,
    hero_level_ceiling,
)
from src.mechanics.math_operations import calculate_monster_xp_reward
from src.shared.formulas import xp_for_level

VARIACAO = generation_rules()["level_variation"]
LARGADA = int(VARIACAO["early_player_level"])
FOLGA_DA_LARGADA = int(VARIACAO["early_max_above_player"])
MAIOR_DESLOCAMENTO = max(int(o) for o in VARIACAO["offsets"])

# Mortes da auditoria `0ab837b9` no degrau: (classe, seed, andar, nível do herói,
# nível do monstro comum que o matou).
MORTES_NO_DEGRAU = (
    ("warrior", 46, 14, 4, 14),
    ("warrior", 68, 11, 4, 11),
    ("mage", 2, 10, 5, 12),
    ("warrior", 85, 10, 5, 10),
    ("warrior", 90, 15, 6, 15),
)
# E uma que a regra NÃO evita, de propósito: nível 6 no andar 11 contra Nv11. A
# folga de um herói de nível 6 já é de 5 níveis — estar cinco atrás do andar
# continua cobrando a luta do andar.
MORTE_QUE_CONTINUA_POSSIVEL = ("warrior", 81, 11, 6, 11)


def _amostra(andar: int, heroi: int, n: int = 400) -> list[int]:
    estado = random.getstate()
    try:
        random.seed(andar * 1000 + heroi)
        return [calculate_scaled_monster_level(andar, heroi) for _ in range(n)]
    finally:
        random.setstate(estado)


class TestOTetoAfrouxaEmVezDeSumir:
    @pytest.mark.parametrize("nivel", range(1, LARGADA + 1))
    def test_na_largada_a_regra_e_a_de_sempre(self, nivel):
        assert hero_level_ceiling(nivel) == nivel + FOLGA_DA_LARGADA

    @pytest.mark.parametrize("nivel", range(1, 60))
    def test_a_folga_cresce_um_nivel_por_nivel(self, nivel):
        """Sem degrau: de um nível para o seguinte o teto sobe 1 ou 2, nunca salta."""
        folga = hero_level_ceiling(nivel) - nivel
        proxima = hero_level_ceiling(nivel + 1) - (nivel + 1)
        assert proxima - folga == (1 if nivel >= LARGADA else 0)

    @pytest.mark.parametrize("andar", range(5, 300, 7))
    def test_no_ritmo_do_andar_o_teto_nao_morde(self, andar):
        """Um nível atrás do andar, o teto passa do monstro mais alto que ele sorteia."""
        assert hero_level_ceiling(andar - 1) >= andar + MAIOR_DESLOCAMENTO

    @pytest.mark.parametrize("andar,heroi", [(14, 4), (20, 5), (30, 8), (60, 20)])
    def test_quem_caiu_para_tras_continua_enfrentando_monstro_acima(self, andar, heroi):
        niveis = _amostra(andar, heroi)
        assert min(niveis) > heroi, "o risco de estar atrasado sumiu"
        assert max(niveis) <= hero_level_ceiling(heroi)

    @pytest.mark.parametrize("andar,heroi", [(14, 4), (20, 5), (30, 8)])
    def test_a_xp_do_monstro_paga_a_volta(self, andar, heroi):
        """Atrasado, cada vitória rende mais nível do que rende a quem está no ritmo."""
        monstro = max(_amostra(andar, heroi))
        atrasado = calculate_monster_xp_reward(monstro) / xp_for_level(heroi)
        no_ritmo = calculate_monster_xp_reward(andar) / xp_for_level(andar - 1)
        assert atrasado > no_ritmo


class TestAsMortesDoDegrau:
    """Fixtures: o monstro que matou cada mergulhador não nasce mais contra ele."""

    @pytest.mark.parametrize("classe,seed,andar,heroi,monstro", MORTES_NO_DEGRAU)
    def test_o_monstro_do_degrau_nao_e_mais_sorteado(self, classe, seed, andar, heroi, monstro):
        del classe, seed  # identificam a run da auditoria; a regra não lê nenhum dos dois
        assert hero_level_ceiling(heroi) < monstro
        assert max(_amostra(andar, heroi)) < monstro

    def test_o_risco_de_estar_atrasado_fica(self):
        _classe, _seed, andar, heroi, monstro = MORTE_QUE_CONTINUA_POSSIVEL
        assert hero_level_ceiling(heroi) >= monstro
        assert monstro in _amostra(andar, heroi)


class TestOModeloDeXPLeAMesmaRegra:
    @pytest.mark.parametrize("andar,heroi", [(14, 4), (20, 5), (30, 8), (10, 11), (6, 4)])
    def test_o_atalho_do_modelo_bate_com_o_gerador(self, andar, heroi):
        """O balde do `xp_model` só junta níveis que o gerador trata igual."""
        import statistics

        from src.sim import xp_model as xp

        real = statistics.fmean(_amostra(andar, heroi, 3000))
        modelo, _ = xp._amostra_do_encontro(andar, heroi)
        assert modelo == pytest.approx(real, abs=0.15)
