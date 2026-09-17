"""O BOT_PADRÃO tem de jogar o jogo, e não uma versão conveniente dele.

O valor desta run é ser revisável. Um trace que mostra opções que não foram
oferecidas, ou um herói que nasce com equipamento que o jogo não dá, produz uma
leitura confiante sobre algo que não aconteceu.
"""

from __future__ import annotations

from src.engine import game_logic, loop
from src.sim import progression
from tools import bot_padrao as bot


class TestNasceComoNoJogo:
    def test_usa_o_caminho_real_de_criacao(self):
        assert bot.create_player_from_data is game_logic.create_player_from_data

    def test_o_estado_inicial_e_o_que_o_jogo_entrega(self):
        # Sem loadout, sem presente: a auditoria anterior media um herói com 10
        # peças equipadas e 3 poções que a criação real nunca dá.
        run = bot.BotPadrao("warrior", seed=1, max_andar=1)
        hero = run.hero
        assert hero.get_level() == 1
        assert hero.coins == 0
        assert list(hero.inventory) == []
        assert all(peca is None for peca in hero.equipment.values())
        assert len(hero.passives) == 0
        # Uma skill: a assinatura da classe, que a criação real entrega.
        assert len(hero.skills) == 1
        assert hero.get_hp() == hero.base_hp


class TestParidadeComAsRegrasDoJogo:
    def test_o_encontro_e_o_core_compartilhado(self):
        # O bot não monta mais a sequência do encontro. Ele PEDE o encontro ao
        # mesmo core que `engine.loop.run_fight` usa, e responde quando o core
        # pergunta. Antes existiam duas orquestrações, e duas divergem.
        from src.engine import encounter

        assert bot.resolve_encounter is encounter.resolve_encounter
        assert loop.resolve_encounter is encounter.resolve_encounter

    def test_as_demais_regras_sao_as_do_jogo(self):
        from src.content import economy, floor_exit

        assert bot.exit_fee is economy.exit_fee
        assert bot.pay_interest is economy.pay_interest
        assert bot.use_exit is floor_exit.use_exit
        assert bot.effective_essence is floor_exit.effective_essence
        assert bot._setup_dungeon_map is loop._setup_dungeon_map
        assert bot.progression.on_level_up is progression.on_level_up
        assert bot.progression.equip_if_better is progression.equip_if_better


class TestOTraceNaoInventa:
    """As opções do trace são as REALMENTE oferecidas.

    A primeira versão sorteava três passivas só para imprimir, enquanto quem
    escolhia sorteava as dela por dentro: o log mostrava cartas nunca
    oferecidas. Depois um registrador capturava a oferta pelo hook de
    telemetria. Agora nem isso é preciso — o core ENTREGA a oferta ao provider,
    e o bot imprime o objeto que recebeu.
    """

    def test_o_bot_imprime_a_oferta_que_o_core_entregou(self):
        from src.content import level_up

        run = bot.BotPadrao("warrior", seed=7, max_andar=1)
        run.andar = 3
        run.trace = bot.Trace()

        oferta = level_up.ofertas_do_nivel(run.hero, 3)
        run._escolher_do_nivel(run.hero, oferta)

        texto = str(run.trace)
        for carta in oferta.passives:
            assert carta.name in texto, f"{carta.name} foi oferecida e não apareceu no trace"
        if oferta.tem_skill:
            for carta in oferta.skills:
                assert carta.name in texto


class TestFugaNaoPaga:
    """Fugir não pode render recompensa.

    `process_post_battle` decide "venceu" por `get_isalive()`, e quem fugiu está
    vivo. A guarda vive no core, então vale para o humano e para o bot de uma vez
    — antes cada orquestração tinha de lembrar dela por conta própria, e a do
    bot não lembrava.
    """

    def test_o_core_nao_paga_quem_foge(self, monkeypatch):
        from src.engine import encounter

        class Fuga:
            fled = True
            hero_won = False

        chamou = []
        monkeypatch.setattr(encounter.battle, "run_battle", lambda *a, **k: Fuga())
        monkeypatch.setattr(
            encounter,
            "process_post_battle",
            lambda *a, **k: chamou.append(1) or (0, 0, 0, 0, 0, 0),
        )

        run = bot.BotPadrao("warrior", seed=1, max_andar=1)
        ouro_antes, xp_antes = run.hero.coins, run.hero.xp_points

        resultado = encounter.resolve_encounter(
            run.hero, [object()], combat_decision=lambda *a: None
        )

        assert resultado.fled is True
        assert chamou == [], "fugir chamou o pós-combate e pagaria recompensa cheia"
        assert run.hero.coins == ouro_antes
        assert run.hero.xp_points == xp_antes


class TestQuandoEngajar:
    """Existe UMA decisão de encostar no próximo monstro, e ouro não entra nela.

    Havia duas caças: a "obrigatória" (preciso de ouro para a saída) e a
    "opcional" (quero XP). A primeira estava atrás de `coins < taxa`, então PAGAR
    A SAÍDA desligava a principal fonte de combate do bot; a segunda exigia 80%
    de HP, o que na prática significava uma luta por andar. Nas 60 runs da
    auditoria, 101 das 125 saídas de andar aconteceram com monstro ainda no mapa.
    """

    def test_ouro_suficiente_nao_impede_lutar(self):
        run = _run_preparada(_mapa_de_teste(), nivel=8)
        run.andar = 8
        run.hero.coins = 10_000  # a taxa está paga muitas vezes
        assert run._por_que_nao_engajar(1.0, 1.0) is None

    def test_ouro_nao_aparece_no_motivo_de_parar(self):
        """O motivo impresso tem de ser o que realmente fechou o portão.

        A versão anterior dizia "{ouro} de ouro e a saída custa {taxa}: já dá"
        mesmo nas 48 saídas em que quem fechou tinha sido o HP.
        """
        run = _run_preparada(_mapa_de_teste(), nivel=8)
        run.hero.coins = 10_000
        run.hero.take_damage(int(run.hero.base_hp * 0.8))
        motivo = run._por_que_nao_engajar(_frac(run.hero), 1.0)
        assert motivo is not None
        assert "HP" in motivo and "ouro" not in motivo and "saída" not in motivo

    def test_nem_so_por_hp(self):
        """MP é munição — mas a barra é baixa, porque o básico não custa mana."""
        run = _run_preparada(_mapa_de_teste(), nivel=8)
        assert run._por_que_nao_engajar(1.0, 1.0) is None
        assert run._por_que_nao_engajar(1.0, 0.01) is not None

    def test_o_piso_de_engajar_fica_acima_do_critico(self):
        """Com margem: a política de combate cura em 35% e foge em 12%."""
        assert bot.HP_PARA_ENGAJAR > bot.HP_CRITICO

    def test_nenhuma_constante_e_uma_quota(self):
        """A taxa alta de combate tem de EMERGIR das condições, não de uma meta.

        Uma constante do tipo "lute 90% dos monstros" produziria o número pedido
        sem produzir o comportamento — e nenhuma medição feita em cima dela
        significaria coisa alguma.
        """
        for nome in dir(bot):
            if nome.startswith("_") or not nome.isupper():
                continue
            valor = getattr(bot, nome)
            if isinstance(valor, float) and 0 < valor < 1:
                assert "MONSTRO" not in nome and "LIMPAR" not in nome and "QUOTA" not in nome, (
                    f"{nome} parece uma quota de combate"
                )


class TestCuraNoMapa:
    """A poção parada na mochila não cura ninguém.

    `navigation_menu.py:975` chama `use_potion` fora de combate: é uma ação de
    jogador que existe desde sempre e que o bot nunca tomou. Em 60 partidas ele
    usou poção 22 vezes, todas dentro do combate, e terminou runs com cura na
    bolsa depois de morrer.
    """

    def _pocao(self, valor=30):
        from src.content.items import Item

        return Item(
            "pocao_teste",
            "Poção de Teste",
            "cura",
            effect_type="max_hp",
            effect_value=valor,
            consumable=True,
        )

    def test_bebe_e_a_pocao_some_uma_vez_so(self):
        run = _run_preparada(_mapa_de_teste())
        run.hero.take_damage(int(run.hero.base_hp * 0.6))
        run.hero.inventory.append(self._pocao())
        antes = run.hero.get_hp()

        assert run._beber_pocao() is True
        assert run.hero.get_hp() > antes
        assert run._pocoes() == 0, "consumiu duas poções para curar uma vez"

    def test_ferido_e_com_monstro_no_mapa_a_decisao_e_beber(self):
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        mapa.enemies_pos[(1, 5)] = create_monster("Alvo", 4, "trash")
        run = _run_preparada(mapa)
        run.hero.take_damage(int(run.hero.base_hp * 0.5))
        run.hero.inventory.append(self._pocao())

        acao, _alvo, motivo = run._decidir()
        assert acao == "pocao"
        assert "poç" in motivo

    def test_sem_pocao_e_acima_do_piso_ele_luta_mesmo_assim(self):
        """Cura NÃO é pré-condição universal para lutar.

        Acima do piso de engajamento ele encosta no monstro sem garantia de
        recuperação — exigir o contrário travaria o andar sempre que a loja e a
        fonte não estivessem no mapa.
        """
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        mapa.enemies_pos[(1, 5)] = create_monster("Alvo", 4, "trash")
        run = _run_preparada(mapa)
        run.hero.take_damage(int(run.hero.base_hp * (1 - bot.HP_PARA_ENGAJAR) * 0.9))
        assert run._pocoes() == 0

        acao, _alvo, _motivo = run._decidir()
        assert acao == "lutar"


class TestAParadaDizOMotivoReal:
    def test_sair_com_monstro_no_mapa_nomeia_a_condicao(self):
        """O trace mentia: dizia ouro quando o portão fechado tinha sido o HP."""
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        mapa.enemies_pos[(1, 5)] = create_monster("Alvo", 4, "trash")
        run = _run_preparada(mapa)
        run.hero.coins = 10_000
        # Abaixo do piso de engajamento, acima do crítico, e sem nada que cure
        # no mapa: é o estado exato das 48 saídas que o trace atribuía ao ouro.
        run.hero.take_damage(int(run.hero.base_hp * 0.5))

        acao, _alvo, motivo = run._decidir()
        assert acao == "saida"
        assert "Motivo real" in motivo and "HP" in motivo
        assert "já dá" not in motivo
        assert run.parada and "HP" in run.parada


class TestOrcamentoDeCompra:
    """O jogador decide quanto leva à loja. A loja gasta o que vê."""

    def _run_no_andar(self, ouro: int, hp_fracao: float):
        run = bot.BotPadrao("warrior", seed=7, max_andar=1)
        run.andar = 1
        run.trace = bot.Trace()
        run.reserva_gasta = 0
        run.hero.coins = ouro
        run.hero.take_damage(int(run.hero.base_hp * (1 - hp_fracao)))
        return run

    def test_saudavel_reserva_a_taxa_de_saida(self):
        taxa = bot.exit_fee(1)
        run = self._run_no_andar(taxa * 3, hp_fracao=1.0)
        orcamento, reserva, quebrou = run._orcamento()
        assert reserva == taxa
        assert quebrou is False
        assert orcamento == taxa * 3 - taxa

    def test_ferido_quebra_a_reserva_conscientemente(self):
        taxa = bot.exit_fee(1)
        run = self._run_no_andar(taxa * 3, hp_fracao=0.3)
        orcamento, reserva, quebrou = run._orcamento()
        assert quebrou is True
        assert orcamento == taxa * 3, "sobrevivência leva a carteira inteira"

    def test_a_loja_so_enxerga_o_orcamento_e_a_reserva_volta(self, monkeypatch):
        # A loja gasta TUDO que vê. A prova de que o orçamento segura é esta:
        # com a loja gastando o saldo até zero, o herói sai com a reserva.
        taxa = bot.exit_fee(1)
        run = self._run_no_andar(taxa * 3, hp_fracao=1.0)
        visto = {}

        def loja_gastando_tudo(hero, *a, **k):
            visto["levou"] = hero.coins
            hero.coins = 0

        monkeypatch.setattr(bot.progression, "visit_shop", loja_gastando_tudo)
        run._comprar_com_orcamento("Loja")

        assert visto["levou"] == taxa * 2, "a loja enxergou mais que o orçamento"
        assert run.hero.coins == taxa, "a reserva não voltou para a carteira"
        assert run.reserva_gasta == 0

    def test_quebrar_a_reserva_e_registrado_em_voz_alta(self, monkeypatch):
        run = self._run_no_andar(bot.exit_fee(1) * 3, hp_fracao=0.3)
        monkeypatch.setattr(bot.progression, "visit_shop", lambda *a, **k: None)
        run._comprar_com_orcamento("Loja")
        assert "sacrificar a saída paga" in str(run.trace)
        assert run.reserva_gasta == 1


class TestExtracaoEAvaliadaAntesDaEmergencia:
    def _run(self, nivel: int, andar: int, hp_fracao: float):
        # Mapa sem monstro: assim não há SINAL GRAVE, e o teste isola os sinais
        # normais. `_sinais_de_risco` precisa de um mapa para olhar os alvos.
        run = _run_preparada(_mapa_de_teste(), nivel=nivel)
        run.andar = andar
        run.hero.take_damage(int(run.hero.base_hp * (1 - hp_fracao)))
        return run

    def test_sem_nada_acumulado_recusa_e_diz_o_porque(self):
        run = self._run(nivel=1, andar=5, hp_fracao=0.2)
        extrair, veredito = run._avaliar_extracao((0, 0))
        assert extrair is False
        assert "não acumulei nada que valha preservar" in veredito

    def test_com_acumulo_e_sem_risco_continua_descendo(self):
        run = self._run(nivel=6, andar=5, hp_fracao=1.0)
        extrair, veredito = run._avaliar_extracao((0, 0))
        assert extrair is False
        assert "nenhum sinal de risco" in veredito

    def test_com_acumulo_e_risco_suficiente_extrai_fora_da_emergencia(self):
        # HP em 45% NÃO é emergência (acima de HP_CRITICO), e mesmo assim a
        # Extração é avaliada — era exatamente isso que faltava.
        run = self._run(nivel=4, andar=8, hp_fracao=0.45)
        assert 0.45 > bot.HP_CRITICO, "o cenário precisa estar fora da emergência"
        extrair, veredito = run._avaliar_extracao((0, 0))
        assert extrair is True
        assert "sair vivo vale mais" in veredito


def _frac(heroi) -> float:
    return heroi.get_hp() / max(1, heroi.base_hp)


def _mapa_de_teste(altura=9, largura=15):
    from src.engine.map import MapOfGame

    m = MapOfGame(height=altura, width=largura)
    m.grid = [
        ["#" if (y in (0, altura - 1) or x in (0, largura - 1)) else "." for x in range(largura)]
        for y in range(altura)
    ]
    m.player_pos = {"y": 1, "x": 1}
    m.exit_pos = {"y": altura - 2, "x": largura - 2}
    m.grid[altura - 2][largura - 2] = "X"
    return m


def _run_preparada(mapa, nivel=4):
    run = bot.BotPadrao("warrior", seed=7, max_andar=1)
    run.hero.set_level(nivel)
    run.andar = 5
    run.mapa = mapa
    run.posicao = (mapa.player_pos["y"], mapa.player_pos["x"])
    run.saida = (mapa.exit_pos["y"], mapa.exit_pos["x"])
    run.passos = 0
    run.combates = 0
    run.essencia = 1.0
    run.trace = bot.Trace()
    run.reserva_gasta = 0
    run.extraiu = False
    run.parada = ""
    run._ultimo_veredito_extracao = ""
    return run


class TestMovimentoRespeitaTodaCasa:
    """O herói não pode ser intangível às casas do andar."""

    def test_o_passo_usa_o_movimento_real_do_engine(self, monkeypatch):
        # Quem decide o que acontece ao pisar é `move_player`, e não uma cópia
        # da regra dentro da ferramenta.
        mapa = _mapa_de_teste()
        run = _run_preparada(mapa)
        chamadas = []
        original = mapa.move_player
        monkeypatch.setattr(mapa, "move_player", lambda d: (chamadas.append(d), original(d))[1])
        run._ir_ate(run.saida, evitando=True)
        assert chamadas, "andou sem chamar move_player"
        assert set(chamadas) <= {"w", "a", "s", "d"}

    def test_pisar_num_servico_a_caminho_de_outro_lugar_resolve_a_casa(self):
        # O caso que a v2 errava: atravessar o Ferreiro indo para a saída, como
        # se a casa fosse chão.
        mapa = _mapa_de_teste()
        mapa.features[(1, 5)] = bot.feat.FORGE
        run = _run_preparada(mapa)
        run.hero.coins = 0  # sem ouro: vai passar reto, mas TEM de ver a casa
        run._ir_ate(run.saida, evitando=True)
        assert "Pisou no Ferreiro" in str(run.trace)

    def test_pisar_num_evento_consome_a_casa_como_no_jogo(self):
        mapa = _mapa_de_teste()
        mapa.place_event("fountain")
        run = _run_preparada(mapa)
        alvo = mapa.event_pos
        run._ir_ate(alvo, evitando=True)
        assert mapa.event_pos is None, "o evento continuou no mapa depois de pisado"


class TestEscolhaDeAlvo:
    """A régua é o MAPA. O jogador vê `&` e `B`, não nome nem nível."""

    def test_escolhe_por_custo_de_rota_e_nao_por_distancia_crua(self):
        """Menos lutas no caminho vence menos passos.

        Um monstro a 3 passos com dois outros na frente custa três lutas; um a 9
        passos com o caminho livre custa uma.
        """
        run = _run_preparada(_mapa_de_teste(), nivel=4)
        alvos = [
            {"casa": (1, 4), "passos": 3, "extras": 2, "chefe": False},
            {"casa": (1, 9), "passos": 9, "extras": 0, "chefe": False},
        ]
        assert run._melhor_alvo(alvos)["casa"] == (1, 9)

    def test_a_selecao_nao_le_nome_nem_nivel_do_monstro(self):
        """`draw_map` desenha `&`. Nome e nível só existem depois da colisão.

        Escolher alvo por defasagem de nível era jogar com informação que nenhum
        jogador tem — e é uma regressão fácil de reintroduzir sem perceber, por
        isso a prova é sobre as CHAVES que a seleção enxerga.
        """
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        mapa.enemies_pos[(1, 4)] = create_monster("Bandido", 9, "bruiser")
        mapa.enemies_pos[(1, 8)] = create_monster("Rato", 5, "trash")
        run = _run_preparada(mapa, nivel=4)

        alvos = run._alvos_visiveis()
        assert alvos
        for a in alvos:
            assert set(a) == {"casa", "passos", "extras", "chefe"}, (
                f"o alvo carrega informação que o mapa não mostra: {sorted(a)}"
            )

    def test_chefe_nao_e_alvo_opcional(self):
        """`B` é a única marca de perigo que o mapa dá. Ignorá-la é jogar pior."""
        run = _run_preparada(_mapa_de_teste(), nivel=4)
        so_chefe = [{"casa": (1, 4), "passos": 2, "extras": 0, "chefe": True}]
        assert run._melhor_alvo(so_chefe) is None
        com_um_comum = so_chefe + [{"casa": (1, 9), "passos": 9, "extras": 0, "chefe": False}]
        assert run._melhor_alvo(com_um_comum)["casa"] == (1, 9)


class TestDesproporcaoSeJulgaNaFicha:
    """Depois da colisão, com a tela de confronto à vista — nunca antes."""

    def _par(self, nivel_monstro: int):
        from src.content.factories.monsters import create_monster

        run = _run_preparada(_mapa_de_teste(), nivel=4)
        return run, create_monster("Alvo", nivel_monstro, "bruiser")

    def test_foge_da_corrida_de_dano_que_perde(self):
        run, monstro = self._par(12)
        acao = run._ler_a_ficha(run.hero, monstro)
        assert acao is not None and acao.kind == "flee"

    def test_luta_a_corrida_que_ganha(self):
        run, monstro = self._par(1)
        assert run._ler_a_ficha(run.hero, monstro) is None

    def test_insiste_na_fuga_enquanto_a_corrida_seguir_perdida(self):
        """Fugir é 50% por turno. Tentar uma vez é aceitar a primeira moeda."""
        run, monstro = self._par(12)
        politica = run._com_leitura_de_ficha(lambda h, m, t: bot.Action(kind="attack"))
        for turno in range(4):
            assert politica(run.hero, [monstro], turno).kind == "flee"

    def test_trocar_a_politica_troca_tambem_a_leitura_da_ficha(self):
        """A leitura é parte da política do bot, não um enxerto no encontro.

        É o que permite a um teste fixar a decisão para isolar o núcleo do
        encontro — e é por isso que a composição mora no `__init__`.
        """
        run, monstro = self._par(12)
        run.decide = lambda h, m, t: bot.Action(kind="attack")
        assert run.decide(run.hero, [monstro], 0).kind == "attack"


class TestAtrasoNaoImpedeLutar:
    """Estar atrás do andar é ALERTA, nunca portão.

    Um gate de `nível < andar - 1` fecharia o ciclo errado: o herói atrasado para
    de lutar, e lutar é a única coisa que recupera o atraso. Na seed 20260918 o
    Warrior chegou ao andar 5 no Nv3 e foi ali que fez 4 combates e ganhou 396 XP.
    """

    def test_o_atraso_e_sinal_de_risco(self):
        run = _run_preparada(_mapa_de_teste(), nivel=1)
        run.andar = 8
        assert any("contra andar" in s for s in run._sinais_de_risco())

    def test_mas_nao_impede_engajar(self):
        run = _run_preparada(_mapa_de_teste(), nivel=1)
        run.andar = 8
        assert run._por_que_nao_engajar(1.0, 1.0) is None, (
            "o atraso de nível virou portão de combate — é o ciclo de subprogressão"
        )


class TestPrioridadeGlobal:
    """Serviço não é avaliado isoladamente. Existe uma escada, e ela manda.

    A v3 gastava no Ferreiro logo antes de precisar do ouro para curar na Loja,
    porque cada casa decidia sozinha. A correção é genérica: enquanto houver uma
    necessidade mais alta pendente, a mais baixa espera — em qualquer andar, com
    qualquer ouro, a qualquer distância.
    """

    def _run(self, hp_fracao=1.0, ouro=10_000, nivel=8, andar=5):
        run = _run_preparada(_mapa_de_teste(), nivel=nivel)
        run.andar = andar
        run.hero.coins = ouro
        run.hero.take_damage(int(run.hero.base_hp * (1 - hp_fracao)))
        return run

    def test_a_escada_esta_ordenada(self):
        assert bot.SOBREVIVENCIA < bot.RECUPERACAO < bot.PROGREDIR < bot.INVESTIMENTO < bot.ENCERRAR

    def test_progredir_vem_antes_de_investir_e_de_encerrar(self):
        """Serviço e saída são o que vem DEPOIS de jogar o andar, não o atalho."""
        assert bot.PROGREDIR < bot.INVESTIMENTO
        assert bot.PROGREDIR < bot.ENCERRAR

    def test_ferido_com_ouro_a_necessidade_e_recuperacao(self):
        run = self._run(hp_fracao=0.52)
        necessidade, _porque = run._necessidade_atual()
        assert necessidade == bot.RECUPERACAO

    def test_inteiro_e_com_folga_a_necessidade_e_progredir(self):
        """Com ouro sobrando e um monstro no mapa, a resposta é LUTAR.

        Era `INVESTIMENTO`: ter ouro bastava para o andar virar uma ida às
        compras. Ouro é consequência do combate, não substituto dele.
        """
        from src.content.factories.monsters import create_monster

        run = self._run(hp_fracao=1.0)
        run.mapa.enemies_pos[(1, 5)] = create_monster("Alvo", 5, "trash")
        run.hero.equipment[next(iter(run.hero.equipment))] = object()
        necessidade, _porque = run._necessidade_atual()
        assert necessidade == bot.PROGREDIR

    def test_sem_alvo_e_com_folga_ai_sim_investe(self):
        run = self._run(hp_fracao=1.0)
        run.hero.equipment[next(iter(run.hero.equipment))] = object()
        necessidade, _porque = run._necessidade_atual()
        assert necessidade == bot.INVESTIMENTO

    def test_ferreiro_espera_quando_a_necessidade_e_mais_alta(self, monkeypatch):
        # O caso genérico do que a v3 errava no andar 7.
        run = self._run(hp_fracao=0.52)
        mexeu = []
        monkeypatch.setattr(run, "_usar_ferreiro", lambda casa: mexeu.append(casa))

        run._resolver_feature(bot.feat.FORGE, (1, 5))

        assert mexeu == [], "gastou no Ferreiro com recuperação pendente"
        assert "investimento espera" in str(run.trace)

    def test_ferreiro_abre_quando_nada_mais_urgente_pende(self, monkeypatch):
        run = self._run(hp_fracao=1.0)
        run.hero.equipment[next(iter(run.hero.equipment))] = object()
        mexeu = []
        monkeypatch.setattr(run, "_usar_ferreiro", lambda casa: mexeu.append(casa))

        run._resolver_feature(bot.feat.FORGE, (1, 5))

        assert mexeu == [(1, 5)]
        assert "nada mais urgente pendente" in str(run.trace)


class TestParidadeDeEncontro:
    """Humano e bot têm de executar o MESMO encontro.

    Dadas as mesmas respostas — as mesmas ações de combate, a mesma passiva, a
    mesma skill —, o estado final tem de ser igual. O que muda é quem responde,
    nunca o que acontece.
    """

    CAMPOS = (
        "hp",
        "mp",
        "xp",
        "nivel",
        "ouro",
        "inventario",
        "equipamento",
        "gemas",
        "passivas",
        "skills",
        "vistas",
        "vivo",
    )

    def _heroi(self):
        from src.engine.game_logic import create_player_from_data

        heroi = create_player_from_data("warrior", "Paridade")
        heroi.set_level(5)
        # A um passo do nível 6: assim UMA vitória sobe de nível e o encontro
        # exercita a oferta, a escolha e a aplicação — que é o trecho que este
        # teste existe para comparar. Sem isto ele media só dano e ouro.
        heroi.xp_points = max(0, heroi.need_to_up() - 1)
        return heroi

    def _monstro(self):
        from src.content.factories.monsters import create_monster

        return create_monster("Alvo", 6, "bruiser")

    def _foto(self, heroi) -> dict:
        return {
            "hp": heroi.get_hp(),
            "mp": heroi.get_mp(),
            "xp": heroi.xp_points,
            "nivel": heroi.get_level(),
            "ouro": heroi.coins,
            "inventario": sorted(getattr(i, "name", str(i)) for i in heroi.inventory),
            "equipamento": {
                slot: (peca.name if peca else None) for slot, peca in heroi.equipment.items()
            },
            "gemas": len(getattr(heroi, "gems", []) or []),
            "passivas": [p.id for p in heroi.passives],
            "skills": heroi.active_skill_ids(),
            "vistas": sorted(heroi.seen_skill_ids),
            "vivo": heroi.get_isalive(),
        }

    def _sempre_atacar(self, *_args, **_kwargs):
        from src.mechanics.battle import Action

        return Action(kind="attack")

    def _primeira_opcao(self, jogador, oferta):
        """A 'resposta determinística': leva sempre a primeira carta da oferta."""
        from src.content import level_up

        if oferta.passives:
            level_up.aplicar_passiva(jogador, oferta.passives[0])
        if oferta.tem_skill and oferta.skills:
            level_up.aplicar_skill(jogador, oferta.skills[0], 1)

    def test_humano_e_bot_terminam_no_mesmo_estado(self, monkeypatch):
        import random

        from src.engine import encounter

        # --- A) adaptador "humano": respostas roteirizadas direto no core.
        random.seed(99)
        heroi_a = self._heroi()
        encounter.resolve_encounter(
            heroi_a,
            [self._monstro()],
            combat_decision=self._sempre_atacar,
            level_up_provider=self._primeira_opcao,
            rng=random.Random(99),
            essence_multiplier=1.0,
            dungeon_level=6,
        )

        # --- B) BOT_PADRÃO, com as MESMAS respostas.
        random.seed(99)
        run = bot.BotPadrao("warrior", seed=99, max_andar=1)
        run.hero = self._heroi()
        run.andar = 6
        run.essencia = 1.0
        run.combates = 0
        run.trace = bot.Trace()
        run.rng = random.Random(99)
        run.decide = self._sempre_atacar
        monkeypatch.setattr(run, "_escolher_do_nivel", self._primeira_opcao)
        run.mapa = _mapa_de_teste()
        casa = (1, 5)
        run.mapa.enemies_pos[casa] = self._monstro()
        run._duelo(run.mapa.enemies_pos[casa], casa)

        foto_a, foto_b = self._foto(heroi_a), self._foto(run.hero)
        for campo in self.CAMPOS:
            assert foto_a[campo] == foto_b[campo], (
                f"{campo} divergiu entre humano e bot: {foto_a[campo]!r} != {foto_b[campo]!r}"
            )

    def test_a_fuga_tambem_e_identica(self, monkeypatch):
        import random

        from src.engine import encounter
        from src.mechanics.battle import Action

        def sempre_fugir(*_a, **_k):
            return Action(kind="flee")

        random.seed(7)
        heroi_a = self._heroi()
        resultado = encounter.resolve_encounter(
            heroi_a,
            [self._monstro()],
            combat_decision=sempre_fugir,
            level_up_provider=self._primeira_opcao,
            rng=random.Random(7),
            dungeon_level=6,
        )

        random.seed(7)
        run = bot.BotPadrao("warrior", seed=7, max_andar=1)
        run.hero = self._heroi()
        run.andar = 6
        run.essencia = 1.0
        run.combates = 0
        run.trace = bot.Trace()
        run.rng = random.Random(7)
        run.decide = sempre_fugir
        run.mapa = _mapa_de_teste()
        casa = (1, 5)
        run.mapa.enemies_pos[casa] = self._monstro()
        run._duelo(run.mapa.enemies_pos[casa], casa)

        if resultado.fled:
            assert self._foto(heroi_a) == self._foto(run.hero)
            # Fugir não paga: o XP tem de ser exatamente o que era antes do
            # encontro, nos dois caminhos.
            intacto = self._heroi().xp_points
            assert heroi_a.xp_points == run.hero.xp_points == intacto
            assert heroi_a.coins == run.hero.coins == 0
