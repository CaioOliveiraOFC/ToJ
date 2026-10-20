"""KI-001: o BotPadrão não ignora uma recuperação viável antes da próxima luta.

A baseline `fb321d4e` mostrou o Warrior seed 24 consumindo a Loja com 58% de
vida e 30 de ouro contra uma saída de 27: a policy prometia "HP a recuperar"
porque `ouro > taxa`, mas a compra entra só com o orçamento real, que guarda a
reserva da saída, e não pagava nem um passo. Com 36% de vida e 64 de ouro a Loja
já não existia, e ele encostou no próximo `&` e morreu.

A correção NÃO revela o monstro: o mapa continua desenhando `&`, e qual monstro
está lá só se sabe na colisão. O que muda é a gestão de risco com o que o jogador
sabe:

- a Loja só promete a cura que cabe no orçamento com que o jogador entra
  (`ServiceView.cura_hp`, pela mesma regra de compra de `_repair`);
- quando a próxima luta, pelo dano real que a run já recebeu por encontro, me
  derrubaria abaixo do ponto de aposta, uma cura que existe de verdade — Loja
  pagável ou poção na mochila — atende RECUPERAR e vem antes de encostar.
"""

from __future__ import annotations

import random

import pytest

from src.content.economy import recovery_offers
from src.sim import progression
from src.sim.bot import decidir_no_mapa
from src.sim.bot.decision import ActionOption, Need
from src.sim.bot.evaluators import HP_DE_APOSTA, avaliar_mapa
from src.sim.bot.observation import (
    ActionMechanicsView,
    MapState,
    ProgressionState,
    ServiceView,
    TargetView,
)
from tools import bot_adapter as ad
from tools.bot_padrao import BotPadrao

ALVO = TargetView(casa=(3, 3), passos=4, extras=0, chefe=False)
LUTAR = ActionOption(action_id="lutar:3,3", family="lutar", label="& no mapa", target=ALVO)
LOJA = ActionOption(action_id="shop", family="shop", label="shop")
SAIDA = ActionOption(action_id="saida", family="saida", label="saída do andar")
POCAO = ActionOption(
    action_id="pocao", family="pocao", label="poção", mechanics=ActionMechanicsView(healing=150)
)


def _prog(hp=250, hp_max=500, combates=0, dano_por_luta=0.0, **kwargs) -> ProgressionState:
    base = dict(
        nivel=3,
        hp=hp,
        hp_max=hp_max,
        mp=50,
        mp_max=100,
        ouro=100,
        taxa_de_saida=40,
        combates_observados=combates,
        dano_por_luta=dano_por_luta,
    )
    base.update(kwargs)
    return ProgressionState(**base)


def _mapa(cura_hp=0.25, **kwargs) -> MapState:
    base = dict(
        andar=3,
        posicao=(5, 5),
        passos_ate_saida=12,
        alvos=(ALVO,),
        servicos=(ServiceView("shop", desvio=6, cura_hp=cura_hp),),
    )
    base.update(kwargs)
    return MapState(**base)


def _loja(mapa: MapState, prog: ProgressionState):
    return avaliar_mapa(LOJA, mapa, prog)


# --- a Loja só promete o que entrega ---------------------------------------


class TestALojaSoPrometeOQueEntrega:
    def test_sem_orcamento_para_hp_a_loja_nao_tem_prioridade_de_cura(self):
        """Histórico ameaçando o ponto de aposta, mas a cura não cabe: nada de RECUPERAR."""
        prog = _prog(hp=250, combates=3, dano_por_luta=0.3)
        loja = _loja(_mapa(cura_hp=0.0), prog)
        assert loja.need is Need.INVESTIR
        assert "HP a recuperar" not in dict(loja.components)
        decisao = decidir_no_mapa(_mapa(cura_hp=0.0), prog, (LUTAR, LOJA, SAIDA))
        assert decisao.action_id == "lutar:3,3"

    def test_com_cura_pagavel_a_loja_promete_hp(self):
        loja = _loja(_mapa(cura_hp=0.25), _prog(hp=250))
        assert "HP a recuperar" in dict(loja.components)


class TestOFatoDaLojaNoAdaptador:
    """`ServiceView.cura_hp` é o passo de HP que a compra REAL paga — nem mais, nem menos."""

    def _bot(self, hp_frac: float, ouro: int, andar: int = 1) -> BotPadrao:
        random.seed(7)
        bot = BotPadrao("warrior", 7)
        bot.andar = andar
        bot.hero.coins = ouro
        bot.hero.take_damage(int(bot.hero.base_hp * (1 - hp_frac)))
        return bot

    def _passo_de_hp(self, bot) -> dict:
        return next(o for o in recovery_offers(bot.hero, bot.andar) if o["resource"] == "hp")

    def test_com_ouro_que_cobre_o_passo_o_fato_e_o_passo_de_hp(self):
        bot = self._bot(0.4, ouro=500)
        passo = self._passo_de_hp(bot)
        assert passo["price"] <= bot._orcamento()[0]
        assert ad._cura_hp_pagavel(bot) == pytest.approx(passo["amount"] / bot.hero.base_hp)

    def test_a_reserva_da_saida_fica_fora_do_orcamento(self):
        """Ouro acima da taxa, mas o que sobra dela não paga o passo: zero."""
        bot = self._bot(0.5, ouro=0)
        passo = self._passo_de_hp(bot)
        bot.hero.coins = bot._orcamento()[1] + int(passo["price"]) - 1
        assert bot.hero.coins > bot._orcamento()[1]
        assert ad._cura_hp_pagavel(bot) == 0.0

    def test_acima_do_alvo_de_reparo_a_loja_nao_cura(self):
        bot = self._bot(0.9, ouro=500)
        assert ad._cura_hp_pagavel(bot) == 0.0

    @pytest.mark.parametrize(("hp_frac", "ouro"), [(0.4, 500), (0.5, 60), (0.45, 30), (0.9, 500)])
    def test_o_declarado_e_o_que_a_compra_entrega(self, hp_frac, ouro):
        """Paridade: se o fato diz que cura, a visita cura; se diz zero, não cura."""
        bot = self._bot(hp_frac, ouro=ouro)
        declarado = ad._cura_hp_pagavel(bot)
        antes = bot.hero.get_hp()
        bot._comprar_com_orcamento("Loja")
        curado = (bot.hero.get_hp() - antes) / bot.hero.base_hp
        if declarado > 0:
            assert curado >= declarado - 1e-9
        else:
            assert curado == 0

    def test_so_a_loja_carrega_o_fato(self):
        assert progression.primeiro_reparo_de_hp is not None
        assert ServiceView("forge", desvio=3).cura_hp == 0.0


# --- RECUPERAR antecipado pelo histórico observado -------------------------


class TestRecuperacaoAntecipada:
    def test_vida_saudavel_e_historico_que_nao_ameaca_mantem_o_de_antes(self):
        prog = _prog(hp=450, combates=5, dano_por_luta=0.2)
        assert prog.hp_frac - prog.dano_por_luta >= HP_DE_APOSTA
        assert _loja(_mapa(), prog).need is Need.INVESTIR
        assert avaliar_mapa(POCAO, _mapa(), prog).need is Need.INVESTIR
        assert decidir_no_mapa(_mapa(), prog, (LUTAR, LOJA, POCAO, SAIDA)).action_id == "lutar:3,3"

    def test_a_proxima_luta_media_cruza_a_aposta_e_a_cura_pagavel_vem_antes(self):
        prog = _prog(hp=250, combates=4, dano_por_luta=0.3)
        assert prog.hp_frac >= HP_DE_APOSTA > prog.hp_frac - prog.dano_por_luta
        loja = _loja(_mapa(cura_hp=0.25), prog)
        assert loja.need is Need.RECUPERAR
        decisao = decidir_no_mapa(_mapa(cura_hp=0.25), prog, (LUTAR, LOJA, SAIDA))
        assert decisao.action_id == "shop"

    def test_sem_combate_observado_nao_se_inventa_risco(self):
        prog = _prog(hp=250, combates=0, dano_por_luta=0.0)
        assert _loja(_mapa(cura_hp=0.25), prog).need is Need.INVESTIR
        assert decidir_no_mapa(_mapa(cura_hp=0.25), prog, (LUTAR, LOJA, SAIDA)).action_id == (
            "lutar:3,3"
        )

    def test_a_pocao_na_mochila_segue_o_mesmo_historico(self):
        ameaca = _prog(hp=250, combates=4, dano_por_luta=0.3, pocoes_de_cura=1)
        assert avaliar_mapa(POCAO, _mapa(), ameaca).need is Need.RECUPERAR
        assert decidir_no_mapa(_mapa(), ameaca, (LUTAR, POCAO, SAIDA)).action_id == "pocao"

        sem_historico = _prog(hp=250, pocoes_de_cura=1)
        assert avaliar_mapa(POCAO, _mapa(), sem_historico).need is Need.INVESTIR
        assert decidir_no_mapa(_mapa(), sem_historico, (LUTAR, POCAO, SAIDA)).action_id == (
            "lutar:3,3"
        )

    def test_abaixo_da_aposta_continua_sobreviver(self):
        prog = _prog(hp=100, combates=4, dano_por_luta=0.3)
        assert _loja(_mapa(cura_hp=0.25), prog).need is Need.SOBREVIVER

    def test_a_luta_nao_muda(self):
        """`_avaliar_luta` é o mesmo: o histórico mexe na cura, não na luta."""
        sem = avaliar_mapa(LUTAR, _mapa(), _prog(hp=250))
        com = avaliar_mapa(LUTAR, _mapa(), _prog(hp=250, combates=4, dano_por_luta=0.3))
        assert sem == com


# --- a fronteira do mapa continua onde estava -------------------------------


class TestAFronteiraDoMapa:
    def test_o_alvo_continua_sem_identidade_nem_dificuldade(self):
        assert set(TargetView.__dataclass_fields__) == {"casa", "passos", "extras", "chefe"}

    def test_alvos_visualmente_iguais_continuam_empatados(self):
        prog = _prog(hp=300, combates=4, dano_por_luta=0.3)
        a = ActionOption(
            "lutar:1,1", "lutar", target=TargetView(casa=(1, 1), passos=4, extras=0, chefe=False)
        )
        b = ActionOption(
            "lutar:9,9", "lutar", target=TargetView(casa=(9, 9), passos=4, extras=0, chefe=False)
        )
        assert avaliar_mapa(a, _mapa(), prog).utility == avaliar_mapa(b, _mapa(), prog).utility


# --- determinismo e a regressão do Warrior seed 24 --------------------------


class TestDeterminismo:
    @pytest.mark.parametrize(("classe", "seed"), [("warrior", 24), ("mage", 7), ("rogue", 3)])
    def test_mesma_seed_mesma_run(self, classe, seed):
        runs = []
        for _ in range(2):
            bot = BotPadrao(classe, seed, 2)
            runs.append((bot.jogar(), bot.fim))
        assert runs[0] == runs[1]


class TestRegressaoWarriorSeed24:
    """As duas decisões de Loja do andar 1, reduzidas ao estado que as produziu."""

    def _cena(self, hp, ouro, cura_hp, combates, dano_por_luta):
        mapa = _mapa(
            andar=1,
            passos_ate_saida=20,
            alvos=(TargetView(casa=(7, 10), passos=2, extras=0, chefe=False),),
            servicos=(ServiceView("shop", desvio=8, cura_hp=cura_hp),),
        )
        prog = _prog(
            nivel=1,
            hp=hp,
            hp_max=440,
            ouro=ouro,
            taxa_de_saida=27,
            combates=combates,
            dano_por_luta=dano_por_luta,
        )
        luta = ActionOption(
            action_id="lutar:7,10", family="lutar", label="& no mapa", target=mapa.alvos[0]
        )
        return mapa, prog, (luta, LOJA, SAIDA)

    def test_com_58_por_cento_e_sem_orcamento_a_loja_fica_para_depois(self):
        """30 de ouro contra a saída de 27: o orçamento (3) não paga um passo de HP."""
        mapa, prog, opcoes = self._cena(257, 30, 0.0, combates=1, dano_por_luta=0.416)
        assert decidir_no_mapa(mapa, prog, opcoes).action_id == "lutar:7,10"

    def test_com_36_por_cento_e_cura_pagavel_a_loja_vem_antes_da_luta(self):
        mapa, prog, opcoes = self._cena(160, 64, 0.25, combates=2, dano_por_luta=0.318)
        decisao = decidir_no_mapa(mapa, prog, opcoes)
        assert decisao.action_id == "shop"
        assert decisao.scores[0].need is Need.RECUPERAR

    def test_a_run_real_nao_desperdica_a_loja(self):
        """O andar 1 da run real: a única visita à Loja cura."""
        bot = BotPadrao("warrior", 24, 1)
        trace = bot.jogar()
        visitas = [linha for linha in trace.splitlines() if linha.startswith("  Loja: ")]
        assert len(visitas) == 1
        antes, depois = (int(x) for x in visitas[0].split("| HP ")[1].split(" -> "))
        assert depois > antes


# --- KI-004, parte do bot: poção e reposição com intenção -------------------


class TestPocaoComIntencao:
    """A poção vale quando a run precisa dela, e nunca para transbordar."""

    def test_sem_necessidade_observada_a_pocao_fica_na_mochila(self):
        """Vida boa, nenhum atrito medido: beber "porque tem" não é recuperação."""
        prog = _prog(hp=350, pocoes_de_cura=1)
        score = avaliar_mapa(POCAO, _mapa(), prog)
        assert score.need is Need.INVESTIR and score.utility == 0.0
        mapa = _mapa(alvos=())
        assert decidir_no_mapa(mapa, prog, (POCAO, SAIDA)).action_id == "saida"

    def test_e_usada_quando_o_historico_mostra_necessidade(self):
        prog = _prog(hp=250, combates=4, dano_por_luta=0.3, pocoes_de_cura=1)
        score = avaliar_mapa(POCAO, _mapa(), prog)
        assert score.need is Need.RECUPERAR and score.utility == 150 / 500
        assert decidir_no_mapa(_mapa(), prog, (LUTAR, POCAO, SAIDA)).action_id == "pocao"

    def test_cura_majoritariamente_desperdicada_nao_e_bebida(self):
        """Faltam 200; um frasco de 450 perderia 250. Nem com necessidade."""
        grande = ActionOption(
            "pocao", "pocao", label="poção", mechanics=ActionMechanicsView(healing=450)
        )
        prog = _prog(hp=300, combates=4, dano_por_luta=0.3, pocoes_de_cura=1)
        assert prog.hp_frac - prog.dano_por_luta < HP_DE_APOSTA
        score = avaliar_mapa(grande, _mapa(), prog)
        assert score.utility == 0.0
        assert decidir_no_mapa(_mapa(), prog, (LUTAR, grande, SAIDA)).action_id == "lutar:3,3"

    def test_com_a_vida_no_fim_a_emergencia_continua(self):
        prog = _prog(hp=100, pocoes_de_cura=1)
        score = avaliar_mapa(POCAO, _mapa(), prog)
        assert score.need is Need.SOBREVIVER and score.utility > 0


class TestReposicaoDeCuraNaLoja:
    def _loja_sem_reparo(self, pocao_pagavel: bool) -> MapState:
        servico = ServiceView("shop", desvio=6, cura_hp=0.0, pocao_pagavel=pocao_pagavel)
        return _mapa(servicos=(servico,))

    def test_sem_orcamento_para_pocao_a_loja_nao_promete_reposicao(self):
        prog = _prog(hp=450, ouro=40, taxa_de_saida=40, pocoes_de_cura=0)
        loja = _loja(self._loja_sem_reparo(False), prog)
        assert dict(loja.components)["falta de cura"] == 0.0
        assert loja.utility == 0.0

    def test_com_orcamento_a_reposicao_conta(self):
        prog = _prog(hp=450, ouro=80, taxa_de_saida=40, pocoes_de_cura=0)
        loja = _loja(self._loja_sem_reparo(True), prog)
        assert dict(loja.components)["falta de cura"] == 1.0


class TestOFatoDaPocaoNoAdaptador:
    def _bot(self, hp_frac: float, ouro: int, andar: int = 1) -> BotPadrao:
        random.seed(11)
        bot = BotPadrao("mage", 11)
        bot.andar = andar
        bot.hero.coins = ouro
        bot.hero.take_damage(int(bot.hero.base_hp * (1 - hp_frac)))
        return bot

    def _menor_preco(self, bot) -> int:
        from src.content.economy import price_of

        return min(
            price_of(i, bot.andar)
            for i in ad._pocoes_de_cura_a_venda(bot.andar, bot.hero.get_classname())
        )

    def test_orcamento_vazio_nao_paga_pocao(self):
        bot = self._bot(1.0, ouro=0)
        assert ad._pocao_de_cura_pagavel(bot) is False

    def test_o_reparo_da_visita_sai_antes_da_pocao(self):
        """Ouro que cobre o reparo mas não o reparo + a poção: não paga a poção."""
        bot = self._bot(0.4, ouro=0)
        reserva = bot._orcamento()[1]
        passo = next(o for o in recovery_offers(bot.hero, bot.andar) if o["resource"] == "hp")
        bot.hero.coins = reserva + int(passo["price"]) + self._menor_preco(bot) - 1
        assert ad._cura_hp_pagavel(bot) > 0
        assert ad._pocao_de_cura_pagavel(bot) is False
        bot.hero.coins += 1
        assert ad._pocao_de_cura_pagavel(bot) is True

    @pytest.mark.parametrize("andar", [1, 9, 10])
    def test_as_pocoes_a_venda_sao_as_da_loja_real(self, andar):
        """Paridade com `Shop.get_available_items`, sorteando muitas vitrines."""
        from src.content.shop import Shop

        declaradas = {i.id for i in ad._pocoes_de_cura_a_venda(andar, "Mage")}
        vistas = set()
        estado = random.getstate()
        try:
            for semente in range(60):
                random.seed(semente)
                for oferta in Shop().get_available_items(andar, "Mage"):
                    item = oferta["item"]
                    if getattr(item, "consumable", False) and item.effect_type == "max_hp":
                        vistas.add(item.id)
        finally:
            random.setstate(estado)
        assert vistas == declaradas
