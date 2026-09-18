"""Propriedades da decisão de mapa: o andar é para ser jogado.

O defeito que estes testes protegem é o medido na auditoria das 60 runs: 101 das
125 saídas de andar aconteceram com monstro ainda no mapa, e só 10 andares foram
limpos. A causa era ter ouro para a saída desligar a fonte de combate.
"""

from __future__ import annotations

from src.sim.bot import decidir_no_mapa
from src.sim.bot.decision import ActionOption, Need
from src.sim.bot.observation import (
    ActionMechanicsView,
    MapState,
    ProgressionState,
    ServiceView,
    TargetView,
)

ALVO = TargetView(casa=(3, 3), passos=5, extras=0, chefe=False)
CHEFE = TargetView(casa=(9, 9), passos=3, extras=0, chefe=True)


def _prog(**kwargs) -> ProgressionState:
    base = dict(nivel=4, hp=450, hp_max=500, mp=90, mp_max=100, ouro=200, taxa_de_saida=50)
    base.update(kwargs)
    return ProgressionState(**base)


def _mapa(**kwargs) -> MapState:
    base = dict(andar=4, posicao=(1, 1), passos_ate_saida=12, alvos=(ALVO,))
    base.update(kwargs)
    return MapState(**base)


def _lutar(alvo=ALVO) -> ActionOption:
    return ActionOption(
        action_id=f"lutar:{alvo.casa[0]},{alvo.casa[1]}",
        family="lutar",
        label="& no mapa",
        target=alvo,
    )


SAIDA = ActionOption(action_id="saida", family="saida", label="saída do andar")
EXTRAIR = ActionOption(action_id="extrair", family="extrair", label="extração")


def _nota(decisao, action_id: str) -> float:
    return next(s.utility for s in decisao.scores if s.action_id == action_id)


class TestOuroNaoEncerraOAndar:
    def test_com_a_taxa_paga_e_monstro_no_mapa_ele_continua(self):
        decisao = decidir_no_mapa(_mapa(), _prog(ouro=10_000), (_lutar(), SAIDA))
        assert decisao.action_id == "lutar:3,3"

    def test_a_nota_de_lutar_nao_muda_com_o_ouro(self):
        """Ouro é parcela da nota de `saida`, nunca condição de `lutar`."""
        opcoes = (_lutar(), SAIDA)
        pobre = decidir_no_mapa(_mapa(), _prog(ouro=0), opcoes)
        rico = decidir_no_mapa(_mapa(), _prog(ouro=10_000), opcoes)
        assert _nota(pobre, "lutar:3,3") == _nota(rico, "lutar:3,3")

    def test_sem_alvo_a_saida_ganha(self):
        decisao = decidir_no_mapa(_mapa(alvos=()), _prog(), (SAIDA,))
        assert decisao.action_id == "saida"


class TestAtrasoNaoImpedeLutar:
    def test_nivel_muito_abaixo_do_andar_ainda_deixa_lutar(self):
        """Um gate de atraso fecharia o ciclo errado: lutar é o que recupera.

        Na seed medida, o Warrior chegou ao andar 5 no Nv3 e foi ali que fez 4
        combates e ganhou 396 XP.
        """
        atrasado = _prog(nivel=1)
        decisao = decidir_no_mapa(_mapa(andar=9), atrasado, (_lutar(), SAIDA))
        assert decisao.action_id == "lutar:3,3"


class TestRiscoPesaSemVirarPortao:
    def test_com_a_vida_muito_baixa_lutar_deixa_de_ser_positivo(self):
        ferido = _prog(hp=50)
        decisao = decidir_no_mapa(_mapa(), ferido, (_lutar(), SAIDA))
        assert _nota(decisao, "lutar:3,3") < 0
        assert decisao.action_id == "saida"

    def test_lutar_continua_sendo_enumerado_e_avaliado_mesmo_ferido(self):
        """Perder a comparação é diferente de ser barrado antes dela."""
        decisao = decidir_no_mapa(_mapa(), _prog(hp=50), (_lutar(), SAIDA))
        assert "lutar:3,3" in {s.action_id for s in decisao.scores}

    def test_sem_cura_no_andar_a_saida_vira_recuperacao(self):
        """Ir buscar o descanso do fim do andar é a resposta de quem não tem cura.

        Quem TEM poção, fonte ou loja pagável resolve sem abandonar o andar — e
        essas atendem SOBREVIVER, que é mais urgente.
        """
        decisao = decidir_no_mapa(_mapa(), _prog(hp=50), (_lutar(), SAIDA))
        need = next(s.need for s in decisao.scores if s.action_id == "saida")
        assert need is Need.RECUPERAR


class TestChefeContaMasNaoVeta:
    """`B` é a única pista de perigo do mapa — pista, não proibição.

    Este teste exigia `saida` contra um chefe: era o VETO, porque `_avaliar_luta`
    devolvia 0,0 para o chefe e só vence quem tem utilidade > 0. O andar 5, 10 e
    15 eram atravessados sem que o `B` jamais fosse encarado. Agora ele custa uma
    luta a mais na rota, e o go/no-go continua sendo o ponto de aposta — o mesmo
    para `&` e para `B`, porque o cérebro tem um limiar de HP só.
    """

    def test_o_chefe_vale_menos_que_um_monstro_comum_equivalente(self):
        decisao = decidir_no_mapa(_mapa(alvos=(ALVO, CHEFE)), _prog(), (_lutar(), _lutar(CHEFE)))
        assert decisao.action_id == "lutar:3,3"
        assert _nota(decisao, "lutar:9,9") < _nota(decisao, "lutar:3,3")

    def test_de_barra_cheia_o_chefe_deixa_de_ser_intocavel(self):
        decisao = decidir_no_mapa(
            _mapa(alvos=(CHEFE,)), _prog(hp=500, hp_max=500), (_lutar(CHEFE), SAIDA)
        )
        assert decisao.action_id == "lutar:9,9"

    def test_abaixo_do_ponto_de_aposta_o_chefe_e_recusado_como_qualquer_alvo(self):
        decisao = decidir_no_mapa(
            _mapa(alvos=(CHEFE,)), _prog(hp=100, hp_max=500), (_lutar(CHEFE), SAIDA)
        )
        assert decisao.action_id == "saida"


class TestCuraSoEUrgenteQuandoBarraProgredir:
    # Restaurar com a vida no fim é SOBREVIVER; com a vida boa é INVESTIR.
    def _pocao(self) -> ActionOption:
        return ActionOption(
            action_id="pocao",
            family="pocao",
            label="beber poção",
            mechanics=ActionMechanicsView(healing=200),
        )

    def test_arranhao_nao_torna_a_cura_mais_urgente_que_o_andar(self):
        """RECUPERAR vence PROGREDIR por construção — então o rótulo importa.

        Sem esta distinção, qualquer perda de vida encerrava o combate do andar:
        o defeito antigo pelo avesso.
        """
        decisao = decidir_no_mapa(
            _mapa(), _prog(hp=450, pocoes_de_cura=1), (_lutar(), self._pocao(), SAIDA)
        )
        assert decisao.action_id == "lutar:3,3"

    def test_com_a_vida_baixa_beber_vem_antes_de_lutar(self):
        decisao = decidir_no_mapa(
            _mapa(), _prog(hp=100, pocoes_de_cura=1), (_lutar(), self._pocao(), SAIDA)
        )
        assert decisao.action_id == "pocao"
        need = next(s.need for s in decisao.scores if s.action_id == "pocao")
        assert need is Need.SOBREVIVER


class TestExtracaoEUmaDecisaoSo:
    def test_sem_acumulo_nao_extrai(self):
        cru = _prog(nivel=1, passivas=0, pecas_equipadas=0)
        decisao = decidir_no_mapa(_mapa(desvio_extracao=2), cru, (_lutar(), EXTRAIR, SAIDA))
        assert decisao.action_id != "extrair"

    def test_um_sinal_so_nao_convence(self):
        prog = _prog(nivel=5, passivas=3, sinais_de_risco=("HP em 40%",))
        decisao = decidir_no_mapa(_mapa(desvio_extracao=2), prog, (_lutar(), EXTRAIR, SAIDA))
        assert _nota(decisao, "extrair") <= 0

    def test_dois_sinais_com_acumulo_convencem(self):
        prog = _prog(
            hp=200,
            nivel=5,
            passivas=3,
            sinais_de_risco=("HP em 40%", "3 saídas não pagas seguidas"),
        )
        decisao = decidir_no_mapa(_mapa(desvio_extracao=2), prog, (_lutar(), EXTRAIR, SAIDA))
        assert decisao.action_id == "extrair"


class TestServicoDepoisDoCombate:
    def test_com_alvo_no_mapa_o_servico_espera(self):
        forge = ActionOption(action_id="forge", family="forge", label="ferreiro")
        mapa = _mapa(servicos=(ServiceView(tipo="forge", desvio=1),))
        decisao = decidir_no_mapa(mapa, _prog(pecas_equipadas=2), (_lutar(), forge, SAIDA))
        assert decisao.action_id == "lutar:3,3", "gastou no Ferreiro com monstro vivo no andar"
