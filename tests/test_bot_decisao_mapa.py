"""O bot enxerga o ANDAR e decide de forma plausível dentro dele?

Fechado o combate, a pergunta muda de escala. Aqui as posições são andares
montados à mão, em que uma pessoa razoável reconheceria a decisão — e o que se
prova é que o bot chega à mesma, com a informação que o JOGADOR tem.

Três achados da auditoria moram nestes testes:

- o tipo do evento vazava (`MapState.evento` era "fountain"/"altar"/"merchant",
  e o mapa desenha `?`);
- o chefe recebia utilidade 0,0, e como só vence quem tem utilidade > 0 ele
  NUNCA era engajado;
- o custo de sair sem pagar era um `-0,5` inventado, e o preço real é a Essência
  do andar seguinte.
"""

from __future__ import annotations

from src.sim.bot import decidir_no_mapa
from src.sim.bot.decision import ActionOption, Need
from src.sim.bot.evaluators import avaliar_mapa
from src.sim.bot.observation import (
    ActionMechanicsView,
    EventoView,
    MapState,
    ProgressionState,
    ServiceView,
    TargetView,
)


def _mapa(**kwargs) -> MapState:
    base = dict(andar=3, posicao=(5, 5), passos_ate_saida=12)
    base.update(kwargs)
    return MapState(**base)


def _prog(**kwargs) -> ProgressionState:
    base = dict(
        nivel=3,
        hp=400,
        hp_max=500,
        mp=80,
        mp_max=100,
        ouro=100,
        taxa_de_saida=40,
        pecas_equipadas=2,
        pecas_para_o_ferreiro=2,
        perda_de_essencia=0.2,
    )
    base.update(kwargs)
    return ProgressionState(**base)


def _lutar(casa=(1, 1), passos=4, extras=0, chefe=False) -> ActionOption:
    return ActionOption(
        action_id=f"lutar:{casa[0]},{casa[1]}",
        family="lutar",
        label="& no mapa" if not chefe else "B no mapa (chefe)",
        target=TargetView(casa=casa, passos=passos, extras=extras, chefe=chefe),
    )


def _saida() -> ActionOption:
    return ActionOption(action_id="saida", family="saida", label="saída do andar")


def _pocao(cura=150) -> ActionOption:
    return ActionOption(
        action_id="pocao",
        family="pocao",
        label="poção",
        mechanics=ActionMechanicsView(healing=cura),
    )


def _servico(tipo: str) -> ActionOption:
    return ActionOption(action_id=tipo, family=tipo, label=tipo)


def _evento() -> ActionOption:
    return ActionOption(action_id="evento", family="evento", label="? no mapa (evento)")


def _view_do_evento(**kwargs) -> EventoView:
    base = dict(
        desvio=3,
        lutas_no_desvio=0,
        cura_da_fonte=0.5,
        custo_do_altar=0.3,
        altar_mataria=False,
        desfechos=3,
    )
    base.update(kwargs)
    return EventoView(**base)


def _nota(opcao: ActionOption, mapa: MapState, prog: ProgressionState) -> float:
    return avaliar_mapa(opcao, mapa, prog).utility


# --- A, B: o que o mapa mostra de um `&` ------------------------------------


class TestAlvosIguaisDecidemIgual:
    """O mapa desenha `&`. Nome, nível, HP e recompensa só existem na colisão."""

    def test_dois_alvos_visualmente_iguais_empatam(self):
        mapa = _mapa()
        prog = _prog()
        a = _lutar(casa=(1, 1), passos=4, extras=0)
        b = _lutar(casa=(9, 9), passos=4, extras=0)
        assert _nota(a, mapa, prog) == _nota(b, mapa, prog)

    def test_a_view_do_alvo_tem_quatro_campos_e_nenhum_identifica(self):
        campos = set(TargetView.__dataclass_fields__)
        assert campos == {"casa", "passos", "extras", "chefe"}

    def test_alvo_atras_de_duas_lutas_perde_para_o_livre(self):
        """A margem é DIVIDIDA pelas lutas que a rota obriga, não subtraída.

        Subtrair misturava unidades a uma taxa inventada — uma luta valia uma
        barra de vida inteira — e vetava em silêncio: a margem vale no máximo
        0,65, então qualquer alvo com um encontro no caminho ficava negativo.
        """
        mapa, prog = _mapa(), _prog()
        livre = _lutar(casa=(1, 1), extras=0)
        atras = _lutar(casa=(9, 9), extras=2)
        assert _nota(livre, mapa, prog) > _nota(atras, mapa, prog)
        assert _nota(atras, mapa, prog) == _nota(livre, mapa, prog) / 3

    def test_um_encontro_no_caminho_nao_veta_o_alvo(self):
        mapa, prog = _mapa(), _prog(hp=400, hp_max=500)
        assert _nota(_lutar(extras=1), mapa, prog) > 0

    def test_passos_nao_entram_na_utilidade_so_desempatam(self):
        mapa, prog = _mapa(), _prog()
        perto = _lutar(casa=(1, 1), passos=2)
        longe = _lutar(casa=(9, 9), passos=18)
        assert _nota(perto, mapa, prog) == _nota(longe, mapa, prog)
        decisao = decidir_no_mapa(mapa, prog, (longe, perto))
        assert decisao.action_id == perto.action_id


class TestChefeNaoEVeto:
    """`B` é pista de perigo, não proibição."""

    def test_chefe_custa_uma_luta_a_mais_que_o_monstro_comum(self):
        mapa, prog = _mapa(), _prog()
        comum = _lutar(casa=(1, 1), extras=0)
        chefe = _lutar(casa=(9, 9), extras=0, chefe=True)
        assert _nota(chefe, mapa, prog) == _nota(comum, mapa, prog) / 2

    def test_entre_o_chefe_e_um_monstro_comum_o_comum_vem_primeiro(self):
        mapa, prog = _mapa(), _prog(hp=500, hp_max=500)
        decisao = decidir_no_mapa(mapa, prog, (_lutar(casa=(9, 9), chefe=True), _lutar()))
        assert decisao.action_id == "lutar:1,1"

    def test_de_posicao_forte_o_chefe_e_engajavel(self):
        """Antes ele valia 0,0, e 0,0 nunca vence: o `B` era intocável."""
        mapa, prog = _mapa(), _prog(hp=500, hp_max=500)
        decisao = decidir_no_mapa(mapa, prog, (_lutar(chefe=True), _saida()))
        assert decisao.action_id.startswith("lutar:")

    def test_abaixo_do_ponto_de_aposta_nenhum_alvo_e_escolhido(self):
        """O go/no-go é o ponto de aposta, e vale igual para `&` e para `B`.

        Exigir MAIS do chefe do que do monstro comum precisaria de um segundo
        limiar de HP, e o cérebro tem um só.
        """
        mapa, prog = _mapa(), _prog(hp=150, hp_max=500)
        for alvo in (_lutar(chefe=True), _lutar()):
            assert _nota(alvo, mapa, prog) < 0
            assert decidir_no_mapa(mapa, prog, (alvo, _saida())).action_id == "saida"


# --- C, E: recuperação não quebra a exploração ------------------------------


class TestRecuperacao:
    def test_hp_baixo_com_pocao_nao_abandona_o_andar(self):
        """Poção na mochila resolve aqui; ir à saída descansar troca um andar."""
        mapa, prog = _mapa(alvos=(TargetView((1, 1), 4, 0, False),)), _prog(hp=100, hp_max=500)
        decisao = decidir_no_mapa(mapa, prog, (_pocao(), _saida(), _lutar()))
        assert decisao.action_id == "pocao"

    def test_a_pocao_atende_sobreviver_e_a_saida_recuperar(self):
        prog = _prog(hp=100, hp_max=500)
        mapa = _mapa()
        assert avaliar_mapa(_pocao(), mapa, prog).need is Need.SOBREVIVER
        assert avaliar_mapa(_saida(), mapa, prog).need is Need.RECUPERAR

    def test_um_arranhao_nao_para_a_exploracao(self):
        mapa, prog = _mapa(), _prog(hp=470, hp_max=500)
        decisao = decidir_no_mapa(mapa, prog, (_pocao(), _lutar(), _saida()))
        assert decisao.action_id.startswith("lutar:")

    def test_com_hp_cheio_a_cura_vale_zero(self):
        mapa, prog = _mapa(), _prog(hp=500, hp_max=500)
        assert _nota(_pocao(), mapa, prog) == 0.0

    def test_cura_que_excede_o_hp_faltante_so_conta_o_aproveitavel(self):
        mapa, prog = _mapa(), _prog(hp=480, hp_max=500)
        score = avaliar_mapa(_pocao(cura=300), mapa, prog)
        assert "aproveitável" in score.note
        assert score.utility == 20 / 500


# --- F, M: o `?` é desconhecido ---------------------------------------------


class TestEventoDesconhecido:
    """O mapa desenha `?`. O tipo só é revelado por `move_player`."""

    def test_o_estado_do_mapa_nao_tem_campo_de_tipo_de_evento(self):
        assert "tem_evento" in MapState.__dataclass_fields__
        campos = set(EventoView.__dataclass_fields__)
        assert not any("tipo" in c or "type" in c for c in campos)

    def test_ouro_nao_aparece_em_nenhuma_parcela_do_evento(self):
        """Cura, HP perdido e ouro não se convertem. Só HP entra na conta."""
        mapa = _mapa(tem_evento=True, evento=_view_do_evento())
        score = avaliar_mapa(_evento(), mapa, _prog(hp=250, hp_max=500))
        nomes = {nome for nome, _v in score.components}
        assert nomes == {"chance de cura", "risco do altar"}
        assert not any("ouro" in nome for nome in nomes)

    def test_o_evento_nunca_atende_sobreviver(self):
        """Com a vida no fim, ir ao `?` é apostar que não é o Altar."""
        mapa = _mapa(tem_evento=True, evento=_view_do_evento())
        for hp in (10, 100, 250, 500):
            score = avaliar_mapa(_evento(), mapa, _prog(hp=hp, hp_max=500))
            assert score.need is Need.INVESTIR

    def test_quando_o_altar_mataria_o_valor_despenca(self):
        mapa_seguro = _mapa(tem_evento=True, evento=_view_do_evento(altar_mataria=False))
        mapa_fatal = _mapa(tem_evento=True, evento=_view_do_evento(altar_mataria=True))
        prog = _prog(hp=120, hp_max=500)
        assert _nota(_evento(), mapa_fatal, prog) < _nota(_evento(), mapa_seguro, prog)

    def test_com_hp_cheio_o_risco_do_altar_domina(self):
        """Nada a curar, e um terço de chance de perder 30% da barra."""
        mapa = _mapa(tem_evento=True, evento=_view_do_evento())
        assert _nota(_evento(), mapa, _prog(hp=500, hp_max=500)) < 0

    def test_as_lutas_do_desvio_entram_e_os_passos_nao(self):
        prog = _prog(hp=250, hp_max=500)
        perto = _mapa(tem_evento=True, evento=_view_do_evento(desvio=1))
        longe = _mapa(tem_evento=True, evento=_view_do_evento(desvio=30))
        assert _nota(_evento(), perto, prog) == _nota(_evento(), longe, prog)
        com_luta = _mapa(tem_evento=True, evento=_view_do_evento(lutas_no_desvio=1))
        assert _nota(_evento(), com_luta, prog) == _nota(_evento(), perto, prog) / 2


# --- G, H: serviços ----------------------------------------------------------


class TestServicos:
    def test_ferreiro_sem_peca_elegivel_nao_ganha_valor(self):
        mapa = _mapa(servicos=(ServiceView(tipo="forge", desvio=3),))
        com = _prog(pecas_para_o_ferreiro=2)
        sem = _prog(pecas_para_o_ferreiro=0)
        assert _nota(_servico("forge"), mapa, com) > _nota(_servico("forge"), mapa, sem)
        # Zero, e zero nunca vence: a folga de ouro não compra o que não existe.
        assert _nota(_servico("forge"), mapa, sem) == 0.0
        assert decidir_no_mapa(mapa, sem, (_servico("forge"), _saida())).action_id == "saida"

    def test_a_elegibilidade_e_do_ferreiro_nao_de_ter_peca_equipada(self):
        """Herói com tudo equipado e nada a melhorar não ganha por visitar."""
        mapa = _mapa(servicos=(ServiceView(tipo="forge", desvio=2),))
        prog = _prog(pecas_equipadas=6, pecas_para_o_ferreiro=0)
        assert _nota(_servico("forge"), mapa, prog) == 0.0

    def test_servico_distante_nao_e_penalizado_por_passo(self):
        prog = _prog()
        perto = _mapa(servicos=(ServiceView(tipo="forge", desvio=1),))
        longe = _mapa(servicos=(ServiceView(tipo="forge", desvio=40),))
        assert _nota(_servico("forge"), perto, prog) == _nota(_servico("forge"), longe, prog)

    def test_servico_atras_de_luta_paga_a_luta(self):
        prog = _prog()
        livre = _mapa(servicos=(ServiceView(tipo="forge", desvio=6),))
        atras = _mapa(servicos=(ServiceView(tipo="forge", desvio=6, lutas_no_desvio=2),))
        assert _nota(_servico("forge"), atras, prog) == _nota(_servico("forge"), livre, prog) / 3

    def test_a_distancia_desempata(self):
        mapa = _mapa(
            servicos=(
                ServiceView(tipo="forge", desvio=20),
                ServiceView(tipo="shop", desvio=2),
            )
        )
        prog = _prog(hp=500, hp_max=500, pocoes_de_cura=0)
        forge = avaliar_mapa(_servico("forge"), mapa, prog)
        shop = avaliar_mapa(_servico("shop"), mapa, prog)
        assert forge.tiebreak == -20.0 and shop.tiebreak == -2.0

    def test_fonte_altar_e_mercador_nao_sao_servicos_do_jogo(self):
        """São desfechos do EVENTO. Ter ramo próprio aqui era o vazamento."""
        from src.engine.map import FEATURE_CHARS

        assert set(FEATURE_CHARS) == {"shop", "forge", "extraction"}


# --- I, J, K, L: saída do andar ---------------------------------------------


class TestSaidaDoAndar:
    def test_com_ouro_suficiente_nao_existe_opcao_de_nao_pagar(self):
        mapa, prog = _mapa(), _prog(ouro=100, taxa_de_saida=40)
        score = avaliar_mapa(_saida(), mapa, prog)
        assert all("não paga" not in nome for nome, _v in score.components)

    def test_sem_ouro_o_custo_e_a_essencia_e_nao_um_numero_inventado(self):
        mapa = _mapa()
        prog = _prog(ouro=10, taxa_de_saida=40, perda_de_essencia=0.2)
        score = avaliar_mapa(_saida(), mapa, prog)
        perda = dict(score.components)["Essência que a saída não paga custa"]
        assert perda == -0.2

    def test_no_piso_da_essencia_sair_sem_pagar_nao_custa_mais_nada(self):
        """`essence_after_penalty` tem piso: quem já está nele não perde mais."""
        mapa = _mapa()
        prog = _prog(ouro=0, taxa_de_saida=40, perda_de_essencia=0.0)
        assert (
            dict(avaliar_mapa(_saida(), mapa, prog).components)[
                "Essência que a saída não paga custa"
            ]
            == 0.0
        )

    def test_andar_sem_alvo_faz_a_saida_coerente(self):
        mapa, prog = _mapa(alvos=()), _prog()
        decisao = decidir_no_mapa(mapa, prog, (_saida(),))
        assert decisao.action_id == "saida"
        assert dict(avaliar_mapa(_saida(), mapa, prog).components)["andar sem mais alvo"] == 1.0

    def test_com_alvo_no_andar_a_saida_nao_vence_so_por_existir(self):
        alvo = TargetView((1, 1), 4, 0, False)
        mapa, prog = _mapa(alvos=(alvo,)), _prog()
        decisao = decidir_no_mapa(mapa, prog, (_lutar(), _saida()))
        assert decisao.action_id.startswith("lutar:")

    def test_a_saida_e_a_ultima_necessidade(self):
        mapa, prog = _mapa(), _prog()
        assert avaliar_mapa(_saida(), mapa, prog).need is Need.ENCERRAR


# --- N: legalidade -----------------------------------------------------------


class TestLegalidade:
    def test_a_decisao_aponta_para_uma_das_opcoes_recebidas(self):
        mapa, prog = _mapa(), _prog()
        opcoes = (_lutar(), _saida(), _pocao())
        assert decidir_no_mapa(mapa, prog, opcoes).action_id in {o.action_id for o in opcoes}

    def test_alvo_sem_rota_nao_pode_ser_escolhido(self):
        """Inalcançável não entra como candidata; se entrar, não vence."""
        mapa, prog = _mapa(), _prog()
        sem_rota = ActionOption(action_id="lutar:9,9", family="lutar", label="&", target=None)
        decisao = decidir_no_mapa(mapa, prog, (sem_rota, _saida()))
        assert decisao.action_id == "saida"
