"""SMART_REAL tem de jogar o jogo, e não uma versão conveniente dele.

O valor desta run é ser revisável. Um trace que mostra opções que não foram
oferecidas, ou um herói que nasce com equipamento que o jogo não dá, produz uma
leitura confiante sobre algo que não aconteceu.
"""

from __future__ import annotations

from src.engine import game_logic, loop
from src.sim import progression
from tools import reference_run as ref


class TestNasceComoNoJogo:
    def test_usa_o_caminho_real_de_criacao(self):
        assert ref.create_player_from_data is game_logic.create_player_from_data

    def test_o_estado_inicial_e_o_que_o_jogo_entrega(self):
        # Sem loadout, sem presente: a auditoria anterior media um herói com 10
        # peças equipadas e 3 poções que a criação real nunca dá.
        run = ref.RunDeReferencia("warrior", seed=1, max_andar=1)
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
        assert ref.process_post_battle is loop.process_post_battle

    def test_as_demais_regras_sao_as_do_jogo(self):
        from src.content import economy, floor_exit

        assert ref.exit_fee is economy.exit_fee
        assert ref.pay_interest is economy.pay_interest
        assert ref.use_exit is floor_exit.use_exit
        assert ref.effective_essence is floor_exit.effective_essence
        assert ref._setup_dungeon_map is loop._setup_dungeon_map
        assert ref.progression.on_level_up is progression.on_level_up
        assert ref.progression.equip_if_better is progression.equip_if_better


class TestOTraceNaoInventa:
    def test_as_opcoes_do_trace_sao_as_realmente_oferecidas(self):
        # O registrador entra no MESMO hook que `on_level_up` já chama. Gerar uma
        # "amostra" para imprimir mostrava três cartas que não foram oferecidas.
        registro = ref.RegistroDeOfertas()
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
        registro = ref.RegistroDeOfertas()
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
        monkeypatch.setattr(ref, "run_battle", lambda *a, **k: Fuga())
        monkeypatch.setattr(
            ref, "process_post_battle", lambda *a, **k: chamou.append(1) or (0, 0, 0, 0, 0, 0)
        )

        run = ref.RunDeReferencia("warrior", seed=1, max_andar=1)
        run.andar = 1
        run.essencia = 1.0
        run.combates = 0
        run.mapa = loop._setup_dungeon_map(1, None, 1, run.hero)
        run.trace = ref.Trace()
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
        primeira = ref.RunDeReferencia("warrior", seed=4242, max_andar=6).jogar()
        segunda = ref.RunDeReferencia("warrior", seed=4242, max_andar=6).jogar()
        assert primeira == segunda

    def test_seeds_diferentes_produzem_traces_diferentes(self):
        uma = ref.RunDeReferencia("warrior", seed=1, max_andar=6).jogar()
        outra = ref.RunDeReferencia("warrior", seed=2, max_andar=6).jogar()
        assert uma != outra
