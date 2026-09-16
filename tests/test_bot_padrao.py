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
    def test_pos_combate_e_o_do_jogo_e_nao_o_do_simulador(self):
        # `sim/harness._award` é uma SEGUNDA implementação do pós-combate, e
        # diverge: ela nunca paga a consolação da derrota. A run de referência
        # usa a função da Forge Run.
        assert bot.process_post_battle is loop.process_post_battle

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
    def test_as_opcoes_do_trace_sao_as_realmente_oferecidas(self):
        # O registrador entra no MESMO hook que `on_level_up` já chama. Gerar uma
        # "amostra" para imprimir mostrava três cartas que não foram oferecidas.
        registro = bot.RegistroDeOfertas()
        assert hasattr(registro, "record_offer")

        class Carta:
            def __init__(self, nome):
                self.id = nome
                self.name = nome

        oferecidas = [Carta("a"), Carta("b"), Carta("c")]
        registro.record_offer("passive", oferecidas, oferecidas[1])
        assert registro.ofertas == [("passive", oferecidas, oferecidas[1])]

    def test_o_registrador_aceita_os_contadores_de_reroll(self):
        # `_pagar_reroll` escreve contadores no mesmo objeto de telemetria.
        registro = bot.RegistroDeOfertas()
        assert registro.gold_spent_on_passive_reroll == 0
        registro.gold_spent_on_passive_reroll = 12
        registro.rerolls = 1
        assert registro.gold_spent_on_passive_reroll == 12
        assert registro.ofertas == []


class TestFugaNaoPaga:
    """Fugir não pode render recompensa.

    `engine/loop.run_fight` devolve ANTES do pós-combate quando o herói foge, e
    `process_post_battle` decide "venceu" por `get_isalive()` — quem fugiu está
    vivo. Sem a guarda, fugir rendia XP, ouro e loot cheios.

    O teste é de COMPORTAMENTO, e não de texto: a primeira versão procurava a
    ordem das duas palavras no código-fonte e reprovava porque o comentário que
    explica a guarda cita a função que vem depois dela.
    """

    def test_fugir_nao_chama_o_pos_combate(self, monkeypatch):
        from src.content.factories.monsters import create_monster

        class Fuga:
            fled = True
            hero_won = False

        chamou = []
        monkeypatch.setattr(bot, "run_battle", lambda *a, **k: Fuga())
        monkeypatch.setattr(
            bot, "process_post_battle", lambda *a, **k: chamou.append(1) or (0, 0, 0, 0, 0, 0)
        )

        run = bot.BotPadrao("warrior", seed=1, max_andar=1)
        run.andar = 1
        run.essencia = 1.0
        run.combates = 0
        run.mapa = loop._setup_dungeon_map(1, None, 1, run.hero)
        run.trace = bot.Trace()
        ouro_antes, xp_antes = run.hero.coins, run.hero.xp_points

        casa = next(iter(run.mapa.enemies_pos))
        vivo = run._duelo(run.mapa.enemies_pos[casa], casa)

        assert vivo is True
        assert chamou == [], "fugir chamou o pós-combate e pagaria recompensa cheia"
        assert run.hero.coins == ouro_antes
        assert run.hero.xp_points == xp_antes
        assert create_monster  # o import prova que o cenário usa monstro de verdade


class TestDeterminismo:
    def test_a_mesma_seed_produz_o_mesmo_trace(self):
        primeira = bot.BotPadrao("warrior", seed=4242, max_andar=6).jogar()
        segunda = bot.BotPadrao("warrior", seed=4242, max_andar=6).jogar()
        assert primeira == segunda

    def test_seeds_diferentes_produzem_traces_diferentes(self):
        uma = bot.BotPadrao("warrior", seed=1, max_andar=6).jogar()
        outra = bot.BotPadrao("warrior", seed=2, max_andar=6).jogar()
        assert uma != outra


class TestCacaObrigatoriaESeparadaDaOpcional:
    """Precisar de ouro e querer XP não podem dividir o mesmo limiar.

    Recusar a caça obrigatória custa Essência no andar seguinte; recusar a
    opcional não custa nada agora. Foi a opcional, autorizada a 67% de HP, que
    matou a run anterior no andar 6.
    """

    def test_a_opcional_exige_mais_que_a_obrigatoria(self):
        assert bot.HP_PARA_CACA_OPCIONAL > bot.HP_PARA_CACA_OBRIGATORIA
        assert bot.MP_PARA_CACA_OPCIONAL > bot.MP_PARA_CACA_OBRIGATORIA

    def test_nenhuma_das_duas_decide_so_por_hp(self):
        # MP é munição: cheio de vida e sem mana, o herói briga no ataque básico.
        import inspect

        fonte = inspect.getsource(bot.BotPadrao._decidir)
        assert "MP_PARA_CACA_OBRIGATORIA" in fonte
        assert "MP_PARA_CACA_OPCIONAL" in fonte


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
    """Nunca 'o mais perto'. O nível do alvo está visível e conta primeiro."""

    def test_prefere_o_proporcional_ao_proximo(self):
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        mapa.enemies_pos[(1, 4)] = create_monster("Bandido", 9, "bruiser")
        mapa.enemies_pos[(1, 8)] = create_monster("Rato", 5, "trash")
        run = _run_preparada(mapa, nivel=4)

        alvos = run._alvos_visiveis()
        escolhido = run._melhor_alvo(alvos)
        assert escolhido is not None
        assert escolhido["nivel"] == 5, "escolheu o Nv9 só porque estava mais perto"

    def test_alvo_desproporcional_e_recusado(self):
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        mapa.enemies_pos[(1, 4)] = create_monster("Bandido", 9, "bruiser")
        run = _run_preparada(mapa, nivel=4)

        alvos = run._alvos_visiveis()
        assert alvos and not run._razoavel(alvos[0])
        assert run._melhor_alvo(alvos) is None


class TestCacaPorNecessidadePodeRecusar:
    def test_sem_alvo_proporcional_aceita_a_saida_nao_paga(self):
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        for casa in ((1, 4), (1, 6), (3, 5)):
            mapa.enemies_pos[casa] = create_monster("Bandido", 9, "bruiser")
        run = _run_preparada(mapa, nivel=4)
        run.hero.coins = 0  # não consegue pagar a taxa

        acao, _alvo, motivo = run._decidir()
        assert acao == "saida"
        assert "níveis de mim" in motivo
        assert "Essência se recupera, personagem não" in motivo


class TestSinalGraveNaExtracao:
    def test_um_sinal_grave_basta_para_considerar_extracao(self):
        from src.content.factories.monsters import create_monster

        mapa = _mapa_de_teste()
        for casa in ((1, 4), (1, 6)):
            mapa.enemies_pos[casa] = create_monster("Bandido", 9, "bruiser")
        run = _run_preparada(mapa, nivel=4)
        # HP cheio e MP cheio: NENHUM sinal normal. Só o grave.
        sinais, grave = run._sinais_de_risco()
        assert grave, "não detectou que nenhum combate acessível é proporcional"

        extrair, veredito = run._avaliar_extracao((1, 1))
        assert extrair is True
        assert "SINAL GRAVE" in veredito


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
        assert (
            bot.SOBREVIVENCIA
            < bot.EVITAR_DESPROPORCIONAL
            < bot.RECUPERACAO
            < bot.CONTINUIDADE
            < bot.INVESTIMENTO
            < bot.COMBATE_OPCIONAL
        )

    def test_ferido_com_ouro_a_necessidade_e_recuperacao(self):
        run = self._run(hp_fracao=0.52)
        necessidade, _porque = run._necessidade_atual()
        assert necessidade == bot.RECUPERACAO

    def test_inteiro_e_com_folga_a_necessidade_e_investimento(self):
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
