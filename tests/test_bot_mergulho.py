"""KI-003, parte do bot: a espiral de saídas não pagas deixa de ser estratégia.

Na baseline `fb321d4e`, 26 runs chegaram ao andar 10 no nível 5 ou menos, e
nenhuma extraiu. O caso extremo é o Mage seed 59: do andar 5 ao 22 ele saiu de
todo andar com monstros no mapa, sem pagar, buscando o descanso do fim do andar
— inclusive em andares em que o próprio fôlego observado ainda pagava mais de
uma luta média. Sublevel e sem Essência, cada andar era mais difícil que o
anterior.

Contornar e sair sem pagar continuam sendo regras do jogo. O que muda é a
política: sublevel (nível < andar), saída NÃO paga, luta no mapa e fôlego para
pelo menos uma luta média — nesse estado, descer não recupera nada, e lutar é o
que devolve o progresso. Sobrevivência continua acima; sem fôlego, sem evidência
ou com a saída pagável, vale a regra de antes. A saída nunca some.
"""

from __future__ import annotations

import contextlib
import io

import pytest

from src.sim.bot import decidir_no_mapa
from src.sim.bot.decision import ActionOption, Need
from src.sim.bot.evaluators import HP_DE_APOSTA, _mergulho_sem_progresso, avaliar_mapa
from src.sim.bot.observation import ActionMechanicsView, MapState, ProgressionState, TargetView

LIVRE = TargetView(casa=(2, 2), passos=5, extras=0, chefe=False)
ATRAS = TargetView(casa=(8, 8), passos=3, extras=1, chefe=False)
SAIDA = ActionOption(action_id="saida", family="saida", label="saída do andar")


def _lutar(alvo: TargetView) -> ActionOption:
    return ActionOption(
        action_id=f"lutar:{alvo.casa[0]},{alvo.casa[1]}", family="lutar", target=alvo
    )


def _mapa(andar=9, alvos=(LIVRE,), **kwargs) -> MapState:
    return MapState(andar=andar, posicao=(1, 1), passos_ate_saida=15, alvos=alvos, **kwargs)


def _prog(**kwargs) -> ProgressionState:
    """O Mage seed 59 no andar 9 da baseline: Nv3, 175/504, 89 de ouro contra 135."""
    base = dict(
        nivel=3,
        hp=175,
        hp_max=504,
        mp=176,
        mp_max=176,
        ouro=89,
        taxa_de_saida=135,
        streak_nao_pagas=4,
        combates_observados=14,
        dano_por_luta=0.309,
        andares_concluidos=8,
        lutas_por_andar=1.75,
        perda_de_essencia=0.0,
    )
    base.update(kwargs)
    return ProgressionState(**base)


def _escolha(mapa, prog, *opcoes):
    return decidir_no_mapa(mapa, prog, tuple(opcoes))


class TestAEspiralDeixaDeSerEstrategia:
    def test_o_caso_do_mage_seed_59_luta_em_vez_de_descer(self):
        mapa, prog = _mapa(), _prog()
        assert prog.hp_frac < HP_DE_APOSTA
        assert _mergulho_sem_progresso(mapa, prog)
        assert _escolha(mapa, prog, _lutar(LIVRE), SAIDA).action_id == "lutar:2,2"

    def test_a_saida_continua_na_mesa_com_o_custo_real(self):
        """Ela não some e não é barrada: perde, em ENCERRAR, com a Essência que cobra."""
        mapa, prog = _mapa(), _prog(perda_de_essencia=0.2)
        decisao = _escolha(mapa, prog, _lutar(LIVRE), SAIDA)
        saida = next(s for s in decisao.scores if s.action_id == "saida")
        assert saida.need is Need.ENCERRAR
        assert dict(saida.components)["Essência que a saída não paga custa"] == -0.2
        assert _escolha(mapa, prog, SAIDA).action_id == "saida"

    def test_alvo_que_exige_mais_lutas_que_o_folego_paga_perde_para_o_livre(self):
        mapa, prog = _mapa(alvos=(LIVRE, ATRAS)), _prog()
        atras = avaliar_mapa(_lutar(ATRAS), mapa, prog)
        assert atras.utility <= 0
        assert _escolha(mapa, prog, _lutar(ATRAS), _lutar(LIVRE), SAIDA).action_id == "lutar:2,2"


class TestAsFronteirasNaturais:
    """Fora da espiral, a saída abaixo da aposta continua sendo recuperação."""

    def _saida(self, mapa, prog):
        return next(
            s for s in _escolha(mapa, prog, _lutar(LIVRE), SAIDA).scores if s.action_id == "saida"
        )

    def test_sem_folego_para_uma_luta_media_nao_se_forca_combate(self):
        """O Mage seed 59 no andar 8: 49/504 contra um custo de 0,309 por luta."""
        mapa, prog = _mapa(andar=8), _prog(hp=49, ouro=85, taxa_de_saida=101)
        assert not _mergulho_sem_progresso(mapa, prog)
        assert _escolha(mapa, prog, _lutar(LIVRE), SAIDA).action_id == "saida"
        assert self._saida(mapa, prog).need is Need.RECUPERAR

    def test_com_a_saida_pagavel_o_problema_nao_e_o_mesmo(self):
        mapa, prog = _mapa(), _prog(ouro=200)
        assert not _mergulho_sem_progresso(mapa, prog)
        assert self._saida(mapa, prog).need is Need.RECUPERAR

    def test_no_nivel_do_andar_nao_ha_espiral(self):
        mapa, prog = _mapa(), _prog(nivel=9)
        assert not _mergulho_sem_progresso(mapa, prog)
        assert self._saida(mapa, prog).need is Need.RECUPERAR

    def test_sem_evidencia_nao_se_inventa_media(self):
        mapa, prog = _mapa(), _prog(combates_observados=0, dano_por_luta=0.0)
        assert not _mergulho_sem_progresso(mapa, prog)
        assert self._saida(mapa, prog).need is Need.RECUPERAR

    def test_sem_luta_no_mapa_descer_e_o_que_resta(self):
        mapa, prog = _mapa(alvos=()), _prog()
        assert not _mergulho_sem_progresso(mapa, prog)
        assert _escolha(mapa, prog, SAIDA).action_id == "saida"

    def test_sobrevivencia_continua_acima(self):
        """Poção na mochila com a vida no fim: bebe antes de lutar."""
        pocao = ActionOption(
            "pocao", "pocao", label="poção", mechanics=ActionMechanicsView(healing=150)
        )
        mapa, prog = _mapa(), _prog(pocoes_de_cura=1)
        decisao = _escolha(mapa, prog, _lutar(LIVRE), pocao, SAIDA)
        assert decisao.action_id == "pocao"
        assert decisao.scores[0].need is Need.SOBREVIVER

    def test_acima_da_aposta_a_luta_e_a_de_sempre(self):
        com = avaliar_mapa(_lutar(LIVRE), _mapa(), _prog(hp=300))
        fora = avaliar_mapa(_lutar(LIVRE), _mapa(), _prog(hp=300, nivel=9))
        assert com == fora


class TestARunReal:
    def test_o_mage_seed_59_nao_desce_sem_pagar_quando_ainda_pode_lutar(self, monkeypatch):
        """Em nenhuma decisão da run ele escolhe a saída no estado da espiral."""
        import tools.bot_padrao as bp

        original = bp.decidir_no_mapa
        violacoes, estados = [], []

        def espiao(mapa, prog, opcoes):
            decisao = original(mapa, prog, opcoes)
            if _mergulho_sem_progresso(mapa, prog):
                estados.append(mapa.andar)
                luta_util = any(
                    s.utility > 0 for s in decisao.scores if s.action_id.startswith("lutar")
                )
                if decisao.action_id == "saida" and luta_util:
                    violacoes.append((mapa.andar, prog.hp_frac))
            return decisao

        monkeypatch.setattr(bp, "decidir_no_mapa", espiao)
        bot = bp.BotPadrao("mage", 59, 12)
        with contextlib.redirect_stdout(io.StringIO()):
            bot.jogar()
        assert estados, "a run não passou pelo estado da espiral: o teste não verificou nada"
        assert violacoes == []


@pytest.mark.parametrize("classe", ["warrior", "mage", "rogue"])
def test_a_regra_e_a_mesma_para_as_tres_classes(classe):
    """O estado decide, não a classe: a mesma posição dá a mesma escolha."""
    del classe  # a policy não recebe classe — o parâmetro só documenta isso
    assert _escolha(_mapa(), _prog(), _lutar(LIVRE), SAIDA).action_id == "lutar:2,2"
