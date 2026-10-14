"""Invariantes estruturais: propriedades que não devem mudar por acidente.

Não há banda de balanceamento aqui. Cada teste protege ou uma propriedade
estrutural do motor, ou um defeito concreto que já aconteceu e não deve voltar.
Bandas calibradas para o meta atual vivem em `tests/balance/`, rodam sob demanda
e não bloqueiam o desenvolvimento — porque elas ainda podem mudar de valor
legitimamente, e estas aqui não.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import all_archetypes, spawn_by_role  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.passives import load_passives  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.entities.heroes import POTION_BUFFS, POTION_STATUSES  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effect_core as core
from src.shared import effects as fx  # noqa: E402
from src.sim.encounters import build_encounter  # noqa: E402
from src.sim.harness import ALL_CLASSES, make_hero, simulate, simulate_run  # noqa: E402


class _T:
    """Os três limites de que este arquivo precisa.

    Ficam aqui, e não em `tests/balance/thresholds.py`, para que a suíte
    estrutural não dependa da de balanceamento. Nenhum deles é calibragem: são
    os limites que separam "difícil" de "matematicamente impossível".
    """

    MAX_SCALING_DRIFT = 0.25
    HIT_FLOOR = 20
    HIT_CEIL = 95


T = _T()


class TestLeiDeEscalonamento:
    """Herói e monstro precisam crescer pela mesma curva.

    O defeito original: o herói crescia em percentual composto e o monstro em
    soma fixa. Duas curvas de formas diferentes divergem para sempre, e era daí
    que vinha a taxa de vitória de 100% contra monstro comum em todos os níveis.
    """

    def test_razao_poder_por_hp_do_monstro_fica_estavel(self):
        razoes = []
        for level in range(1, 21):
            monstro = spawn_by_role("bruiser", level)
            for classe in ALL_CLASSES:
                heroi = make_hero(classe, level, "naked")
                razoes.append(heroi.get_avg_damage() / monstro.base_hp)

        media = sum(razoes) / len(razoes)
        desvio = max(abs(r - media) / media for r in razoes)
        assert desvio <= T.MAX_SCALING_DRIFT, (
            f"A razão poder/HP varia {desvio:.0%} ao longo dos níveis. "
            "Herói e monstro voltaram a crescer por curvas diferentes."
        )

    def test_classes_tem_poder_de_ataque_comparavel_em_todo_nivel(self):
        for level in (1, 5, 10, 15, 20):
            poderes = [make_hero(c, level, "naked").get_avg_damage() for c in ALL_CLASSES]
            assert max(poderes) / min(poderes) <= 1.45, (
                f"No nível {level} uma classe bate {max(poderes) / min(poderes):.1f}x "
                "mais que outra. Identidade é distribuição de orçamento, não dominância."
            )


class TestChanceDeAcerto:
    """Nenhum combatente pode ficar imune ou infalível.

    O defeito original: `85 + AG_atacante - AG_defensor`, sem piso. A agilidade
    do Ladino crescia 18% ao nível contra uma agilidade de monstro fixa em 3, e
    a partir do nível 13 o monstro tinha 0% de chance de acertá-lo.
    """

    @pytest.mark.parametrize("level", [1, 5, 10, 13, 15, 20])
    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_monstro_sempre_consegue_acertar_o_heroi(self, classe, level):
        heroi = make_hero(classe, level, "expected")
        for papel in all_archetypes():
            chance = cmb.hit_chance(spawn_by_role(papel, level), heroi)
            assert chance >= T.HIT_FLOOR, (
                f"{classe} no nível {level} é praticamente imune a {papel}: {chance}% de acerto."
            )

    @pytest.mark.parametrize("level", [1, 10, 20])
    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_heroi_nunca_acerta_sempre(self, classe, level):
        heroi = make_hero(classe, level, "expected")
        for papel in all_archetypes():
            assert cmb.hit_chance(heroi, spawn_by_role(papel, level)) <= T.HIT_CEIL

    def test_vantagem_de_agilidade_nao_depende_do_nivel(self):
        # Escala livre: o Ladino tem a mesma vantagem relativa no nível 1 e no 20.
        vantagens = []
        for level in (1, 10, 20):
            heroi = make_hero("Rogue", level, "naked")
            vantagens.append(cmb.hit_chance(spawn_by_role("bruiser", level), heroi))
        assert max(vantagens) - min(vantagens) <= 5


class TestCoberturaDeEfeitos:
    """Todo efeito declarado nos dados precisa existir no motor.

    O defeito original: o motor reconhecia buffs por nome literal, e 16 das 41
    skills, 10 das 29 passivas e 6 dos 11 tipos de poção eram escritos no estado
    e nunca lidos. O conteúdo mais caro do jogo — Fúria, Imortal, Evasão
    Perfeita — não fazia nada.
    """

    # Vem do CATÁLOGO global de efeitos, não de listas paralelas. Os dois nomes
    # extras não são efeitos de catálogo: `damage_reduction` é escrito como
    # dicionário simples pela skill de monstro, e `invisible` é um estado antigo
    # sem família — os dois ainda esperam migração.
    STATUS_CONHECIDOS = set(core.CATALOG) | {"damage_reduction", "invisible"}
    STATS_CONHECIDOS = set(fx.ATTRIBUTE_STATS) | set(fx.COMBAT_MODIFIERS)

    def test_toda_skill_de_buff_declara_o_atributo_que_modifica(self):
        mortas = [
            s.id
            for s in load_skills()
            if s.effect_type == "buff" and s.effect_stat not in self.STATS_CONHECIDOS
        ]
        assert not mortas, f"Buffs sem efeito no motor: {mortas}"

    def test_todo_status_de_skill_tem_tratamento_no_motor(self):
        mortos = [
            (s.id, s.effect_value)
            for s in load_skills()
            if s.effect_type == "status" and str(s.effect_value) not in self.STATUS_CONHECIDOS
        ]
        assert not mortos, f"Status sem tratamento no motor: {mortos}"

    # Famílias cujo consumidor não é o combate: elas mudam recompensa, cura de
    # poção ou sobrevivência, e cada uma tem o próprio ponto de leitura.
    RECOMPENSAS = frozenset(
        {"essence_bonus", "gold_drop_bonus", "potion_heal_bonus", "death_ignore"}
    )

    def test_toda_passiva_e_consumida_por_alguma_regra(self):
        """A lista de consumidores é DERIVADA do código que consome.

        Ela era escrita à mão, e tinha ficado para trás: não sabia de
        `damage_percent` (que o funil lê em `+MULT`) nem dos procs de acerto
        (`bleed_chance`, `poison_chance`, `fear_chance`), então reportava como
        morto o que o motor usa todo turno. Uma lista paralela que envelhece
        sozinha é o mesmo defeito que este arquivo existe para impedir.
        """
        from src.entities.heroes import Player
        from src.mechanics.combat import MULT_MODIFIER, ONHIT_PROCS

        consumidas = (
            set(Player.PASSIVE_FLAT_STATS)  # atributos e recursos do boneco
            | set(fx.COMBAT_MODIFIERS)  # modificadores que o funil consulta
            | set(ONHIT_PROCS.values())  # chances de aplicar status ao acertar
            | {MULT_MODIFIER}  # o bucket +MULT
            | self.RECOMPENSAS
        )
        mortas = [p.id for p in load_passives() if p.effect_type not in consumidas]
        assert not mortas, f"Passivas sem efeito: {mortas}"

    def test_todo_consumivel_produz_algum_efeito(self):
        tratados = set(POTION_BUFFS) | set(POTION_STATUSES) | {"max_hp", "max_mp"}
        mortos = [
            i.name
            for i in get_all_items().values()
            if getattr(i, "consumable", False) and i.effect_type not in tratados
        ]
        assert not mortos, f"Consumíveis sem efeito: {mortos}"

    def test_existem_consumiveis_de_cura(self):
        # Sem cura comprável, remover a cura gratuita torna a run impossível em
        # vez de difícil. O catálogo original não tinha um único consumível.
        curas = [
            i
            for i in get_all_items().values()
            if getattr(i, "consumable", False) and i.effect_type == "max_hp"
        ]
        assert len(curas) >= 3


class TestAtrito:
    """Vencer um combate precisa custar alguma coisa.

    O defeito original: `rest()` era chamado depois de cada vitória, a cada
    nível, ao equipar, ao desequipar e ao fugir. Cada combate começava com
    recursos cheios e nenhum custava nada ao seguinte, o que anulava poções,
    gestão de MP, skills de cura e a própria decisão de extrair.
    """

    def test_equipar_item_nao_cura(self):
        heroi = make_hero("Warrior", 5, "naked")
        heroi.take_damage(heroi.base_hp // 2)
        ferido = heroi.get_hp()
        arma = next(i for i in get_all_items().values() if getattr(i, "slot", None) == "Weapon")
        heroi.add_item_to_inventory(arma)
        heroi.equip(arma)
        assert heroi.get_hp() <= ferido

    def test_subir_de_nivel_nao_cura_por_completo(self):
        heroi = make_hero("Warrior", 5, "naked")
        heroi.take_damage(int(heroi.base_hp * 0.9))
        heroi.add_xp_points(heroi.need_to_up())
        heroi.level_up(show=False)
        assert heroi.get_hp() < heroi.base_hp


class TestDeckDoMonstro:
    """O monstro ganha deck por nível, pela mesma lei do herói.

    Paridade ESTRUTURAL herói/monstro: antes o monstro nascia com o kit inteiro
    no nível 1 e nenhum teste de paridade cobria progressão — por isso a
    divergência sobreviveu verde.
    """

    NIVEIS = (1, 3, 6, 9, 12, 15, 18, 20)

    def test_a_cadencia_e_a_do_heroi(self):
        from src.content.factories.archetypes import deck_for_level

        for papel, arquetipo in all_archetypes().items():
            for nivel, esperado in ((1, 1), (3, 2), (6, 3), (9, 4)):
                tamanho = len(deck_for_level(arquetipo, nivel))
                assert tamanho == min(esperado, len(arquetipo.skills)), (papel, nivel)

    def test_o_deck_nunca_passa_do_teto(self):
        from src.content.factories.archetypes import deck_for_level
        from src.shared.constants import MAX_ACTIVE_SKILLS

        for papel, arquetipo in all_archetypes().items():
            for nivel in range(1, 41):
                assert len(deck_for_level(arquetipo, nivel)) <= MAX_ACTIVE_SKILLS, papel

    def test_a_assinatura_esta_em_todo_nivel(self):
        from src.content.factories.archetypes import deck_for_level

        for papel, arquetipo in all_archetypes().items():
            for nivel in self.NIVEIS:
                assert deck_for_level(arquetipo, nivel)[0] is arquetipo.skills[0], (papel, nivel)

    def test_nenhuma_carta_do_kit_fica_morta(self):
        from src.content.factories.archetypes import deck_for_level

        for papel, arquetipo in all_archetypes().items():
            vistas = {c.id for nivel in range(1, 21) for c in deck_for_level(arquetipo, nivel)}
            assert vistas == {c.id for c in arquetipo.skills}, papel

    def test_o_spawn_entrega_o_deck_do_nivel(self):
        import random

        from src.content.factories.archetypes import deck_for_level

        for papel, arquetipo in all_archetypes().items():
            for nivel in self.NIVEIS:
                ids = [c.id for c in spawn_by_role(papel, nivel, rng=random.Random(7)).skills]
                esperado = deck_for_level(arquetipo, nivel, random.Random(7))
                assert ids == [c.id for c in esperado], (papel, nivel)

    def test_a_mana_restringe_igual_em_todo_nivel(self):
        """Paridade de MP: quantas conjurações cabem no pool não depende do nível.

        Com custo absoluto e pool geométrico, o boss conjurava 2 vezes no Nv.1 e 17
        no Nv.20 — a mana deixava de ser decisão. Custo percentual da mesma curva
        mantém a razão; só o arredondamento dos pools pequenos a move um pouco.
        """
        import random

        for papel, arquetipo in all_archetypes().items():
            razoes = []
            for nivel in (1, 20):
                m = spawn_by_role(papel, nivel, rng=random.Random(0))
                custos = [cmb.skill_mana_cost(m, c) for c in arquetipo.skills]
                razoes.append(m.base_mp / (sum(custos) / len(custos)))
            assert abs(razoes[1] / razoes[0] - 1) < 0.10, (papel, razoes)

    def test_kit_grande_cresce_sem_manutencao(self):
        """A regra de troca não conhece carta nenhuma: vale para um kit de 30.

        A carta recém-liberada sempre entra, a assinatura nunca sai, e o deck não
        repete carta nem carrega carta acima do nível. Mesma semente, mesmo deck.
        """
        import random
        from dataclasses import replace

        from src.content.factories.archetypes import deck_for_level
        from src.shared.constants import MAX_ACTIVE_SKILLS

        base = all_archetypes()["controller"]
        modelo = base.skills[0]
        kit = tuple(
            replace(modelo, id=f"sint_{i}", name=f"Sintética {i}", level_required=max(1, 3 * i))
            for i in range(30)
        )
        grande = replace(base, skills=kit)
        for nivel in range(1, 91):
            deck = deck_for_level(grande, nivel, random.Random(nivel))
            liberadas = [c for c in kit if c.level_required <= nivel]
            assert len(deck) == min(MAX_ACTIVE_SKILLS, len(liberadas)), nivel
            assert deck[0] is kit[0], nivel
            assert liberadas[-1] in deck, f"a carta liberada no Nv.{nivel} não entrou"
            assert len({c.id for c in deck}) == len(deck), nivel
            assert all(c.level_required <= nivel for c in deck), nivel
        um = [c.id for c in deck_for_level(grande, 90, random.Random(11))]
        outro = [c.id for c in deck_for_level(grande, 90, random.Random(11))]
        assert um == outro

    def test_o_save_preserva_o_deck_e_cai_na_regra_quando_nao_pode(self):
        """Recarregar não sorteia de novo; save sem o campo ou com carta extinta
        refaz o deck pela regra normal — nunca um deck pela metade."""
        import copy
        import random

        from src.content.factories.archetypes import deck_for_level, get_archetype
        from src.engine.map import MapOfGame

        papel, nivel = "controller", 18  # kit de 7: o deck do Nv.18 é sorteado
        original = spawn_by_role(papel, nivel, name="Alvo", rng=random.Random(3))
        ids_originais = [c.id for c in original.skills]
        # Uma semente global que sortearia OUTRO deck: se o load sorteasse, apareceria.
        outra = next(
            n
            for n in range(1000)
            if [c.id for c in deck_for_level(get_archetype(papel), nivel, random.Random(n))]
            != ids_originais
        )

        mapa = MapOfGame(height=5, width=5)
        mapa.enemies_pos[(1, 1)] = original
        estado = mapa.get_map_state()

        def recarregar(dados):
            random.seed(outra)
            novo = MapOfGame(height=5, width=5)
            novo.load_map_state(dados)
            return [c.id for c in novo.enemies_pos[(1, 1)].skills]

        assert recarregar(estado) == ids_originais

        antigo = copy.deepcopy(estado)
        del antigo["enemies_pos"]["1,1"]["skills"]
        refeito = recarregar(antigo)
        assert len(refeito) == len(ids_originais) and refeito[0] == ids_originais[0]

        extinta = copy.deepcopy(estado)
        extinta["enemies_pos"]["1,1"]["skills"][1] = "carta_que_saiu_do_jogo"
        refeito = recarregar(extinta)
        assert "carta_que_saiu_do_jogo" not in refeito
        assert len(refeito) == len(ids_originais) and refeito[0] == ids_originais[0]

    def test_toda_lei_tem_um_deck_real_que_a_monta(self):
        """O deck menor não pode matar uma lei: cada uma precisa de ao menos um
        deck sorteável em que um arquétipo a monta sozinho com as próprias cartas."""
        import random

        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
        from audit_interactions import PECAS, _pecas_da_carta

        from src.content.factories.archetypes import deck_for_level

        for lei, pecas in PECAS.items():
            montada = any(
                set(pecas)
                <= {
                    p
                    for c in deck_for_level(arquetipo, nivel, random.Random(semente))
                    for p in _pecas_da_carta(c)
                }
                for arquetipo in all_archetypes().values()
                for nivel in range(1, 21)
                for semente in range(20)
            )
            assert montada, f"{lei}: nenhum deck real de monstro monta a lei"


class TestArquetipos:
    """Cada papel precisa distribuir o orçamento de um jeito diferente."""

    def test_todo_arquetipo_tem_uma_forca_e_uma_fraqueza(self):
        for papel, arquetipo in all_archetypes().items():
            eixos = (arquetipo.hp, arquetipo.st, arquetipo.mg, arquetipo.defense, arquetipo.agility)
            if papel in ("bruiser", "elite", "boss"):
                continue  # referência e marcos: custam mais orçamento, não o redistribuem
            redistribui = max(eixos) > 1.05 and min(eixos) < 0.95
            # Trash e suporte não redistribuem atributos: eles custam menos
            # orçamento e trazem a ameaça em outro lugar — o trash no número, o
            # suporte nas skills. O que nenhum arquétipo pode ser é forte em
            # tudo sem pagar por isso em lugar nenhum.
            barato_ou_por_skill = max(eixos) <= 1.0 or arquetipo.skills
            assert redistribui or barato_ou_por_skill, f"{papel} não troca nada por nada: {eixos}"

    def test_todo_arquetipo_declara_ameaca_e_counterplay(self):
        for papel, arquetipo in all_archetypes().items():
            assert arquetipo.threat and arquetipo.counterplay, (
                f"{papel} não documenta o que ameaça nem como se responde a ele."
            )


class TestCriticoDeFonte:
    """Sem fonte explícita, não existe crítico.

    Todo atacante tinha 10% de crítico sem que nada no jogo dissesse de onde
    vinham. Agora o crítico é concedido — por passiva, item, encantamento, buff,
    poção ou pela carta — e a chance de quem não tem nada disso é zero.
    """

    def test_o_critico_do_monstro_e_exatamente_a_fonte_declarada(self):
        # Sem buff, a chance do monstro é a passiva inata do arquétipo e nada
        # mais: zero para quem não declara, o valor do JSON para quem declara.
        import random

        for papel, arquetipo in all_archetypes().items():
            declarada = dict(arquetipo.passives).get("crit_chance", 0)
            for nivel in (1, 12, 20):
                m = spawn_by_role(papel, nivel, rng=random.Random(0))
                assert cmb.crit_chance(m) == declarada, (papel, nivel)
                for carta in arquetipo.skills:
                    esperado = declarada + carta.crit_chance
                    assert cmb.crit_chance(m, carta) == esperado, (papel, carta.id)

    def test_so_o_controller_declara_critico_inato(self):
        # A fonte é do papel que congela, não um default disfarçado: os outros
        # oito seguem sem crítico até um buff dar um.
        com_fonte = {
            papel: dict(a.passives)["crit_chance"]
            for papel, a in all_archetypes().items()
            if "crit_chance" in dict(a.passives)
        }
        assert com_fonte == {"controller": 10}

    def test_quem_congela_consegue_critar(self):
        # Quebra Gélida e Hemorragia Fria pedem alvo congelado E golpe crítico.
        # Um arquétipo que congela sem nenhuma fonte de crítico tem as duas leis
        # mortas no próprio kit — foi o que o crítico por fonte deixou para trás
        # quando os 10% implícitos saíram.
        import random

        def congela(carta):
            sec = carta.secondary
            return carta.effect_value == "frozen" or (sec is not None and sec.effect == "frozen")

        congeladores = [p for p, a in all_archetypes().items() if any(map(congela, a.skills))]
        assert congeladores, "nenhum monstro congela: o teste perdeu o objeto"
        for papel in congeladores:
            m = spawn_by_role(papel, 12, rng=random.Random(0))
            assert cmb.crit_chance(m) > 0, papel

    def test_arquetipo_com_passiva_desconhecida_e_recusado(self):
        from src.content.factories.archetypes import _passives_from_json

        with pytest.raises(ValueError, match="crit_chanse"):
            _passives_from_json("x", {"passives": {"crit_chanse": 10}})
        assert _passives_from_json("x", {}) == ()

    def test_heroi_sem_equipamento_nao_crita_no_basico(self):
        for classe in ALL_CLASSES:
            assert cmb.crit_chance(make_hero(classe, 1, "naked")) == 0, classe

    def test_a_fonte_da_carta_soma_e_o_teto_segura(self):
        from src.shared.constants import CRIT_CHANCE_CAP

        furtivo = next(s for s in load_skills() if s.id == "ataque_furtivo")
        heroi = make_hero("Rogue", 1, "naked")
        assert cmb.crit_chance(heroi, furtivo) == furtivo.crit_chance
        heroi.active_buffs["x"] = {"stat": "crit_chance", "value": 999, "duration": 1}
        assert cmb.crit_chance(heroi, furtivo) == CRIT_CHANCE_CAP


class TestGolpeLetal:
    """Matar vem antes de curar quando o alvo morre neste turno.

    O bot curava sempre que caía abaixo do limiar, mesmo com o inimigo a um
    golpe da morte. Contra alvo de dano alto isso vira espiral: cura, toma
    dano, cura de novo. O Mago gastava 231 dos 840 turnos de skill curando na
    luta contra o glass cannon do andar 3, levava 5,0 turnos onde o Ladino
    levava 2,7, e vencia 44,8% contra 99,8%. A classe não era fraca — o bot
    jogava mal, e a calibração inteira saiu em cima disso.
    """

    def _cenario(self, classe="Mage", nivel=3):
        heroi = make_hero(classe, nivel, "expected")
        alvo = build_encounter("glass_solo", nivel)[0]
        return heroi, alvo

    def test_com_o_alvo_a_um_golpe_o_bot_ataca_em_vez_de_curar(self):
        from src.sim.policies import smart_policy

        heroi, alvo = self._cenario()
        heroi.take_damage(int(heroi.base_hp * 0.80))  # abaixo do limiar de cura
        alvo.take_damage(alvo.get_hp() - 1)

        acao = smart_policy(heroi, [alvo], turn=3)
        assert acao.kind in ("attack", "skill")
        assert getattr(acao.skill, "effect_type", "damage") != "heal", (
            "o bot curou com o inimigo a um ponto de vida da morte"
        )

    def test_sem_golpe_letal_o_bot_continua_curando(self):
        # A regra não pode ter desligado a cura: com o alvo inteiro e o herói
        # quase morto, curar é a decisão certa.
        from src.sim.policies import smart_policy

        heroi, alvo = self._cenario()
        heroi.take_damage(int(heroi.base_hp * 0.80))

        acao = smart_policy(heroi, [alvo], turn=3)
        curou = acao.kind == "item" or getattr(acao.skill, "effect_type", "") == "heal"
        assert curou, "o bot ignorou a cura com o alvo de vida cheia"

    def test_o_basico_gratuito_tem_prioridade_sobre_a_skill_letal(self):
        # Gastar mana para matar quem o ataque básico já mata é mana perdida.
        from src.sim.policies import smart_policy

        heroi, alvo = self._cenario()
        alvo.take_damage(alvo.get_hp() - 1)

        acao = smart_policy(heroi, [alvo], turn=3)
        assert acao.kind == "attack", f"gastou {acao.kind} para matar um alvo com 1 de vida"


class TestFidelidadeDoAndar:
    """O andar simulado precisa ser o andar que o jogo gera.

    A simulação tinha tabela própria para elite: um em todo andar múltiplo de 3,
    começando no 3. O jogo nunca gera elite antes de
    `generation.advanced_role_min_floor` e, a partir dali, só com
    `generation.elite_spawn_chance`. Esse elite inventado era onde a run
    terminava — 36 das 48 mortes do Guerreiro no andar 3, 66 das 117 do Mago,
    44 das 53 do Ladino — e o scout reportava a "parede do andar 3" como achado
    de design. Era o medidor.
    """

    def test_elite_nao_aparece_antes_do_andar_do_jogo(self):
        from src.content.factories.monsters import generation_rules
        from src.sim.harness import _default_floor_plan

        minimo = int(generation_rules()["advanced_role_min_floor"])
        for _ in range(300):
            for andar in range(1, minimo):
                assert "elite_solo" not in _default_floor_plan(andar), (
                    f"a simulação gerou elite no andar {andar}; o jogo só gera "
                    f"a partir do {minimo}."
                )

    def test_frequencia_de_elite_segue_a_chance_do_jogo(self):
        import random

        from src.content.factories.monsters import generation_rules
        from src.sim.harness import _default_floor_plan

        regras = generation_rules()
        chance = float(regras["elite_spawn_chance"])
        minimo = int(regras["advanced_role_min_floor"])
        # Andar 6: acima do mínimo e fora do ciclo de chefe, então o elite é o
        # único sorteio em jogo.
        random.seed(1337)
        amostras = 4000
        com_elite = sum(
            1 for _ in range(amostras) if "elite_solo" in _default_floor_plan(max(6, minimo))
        )
        taxa = com_elite / amostras
        assert abs(taxa - chance) < 0.03, (
            f"elite aparece em {taxa:.1%} dos andares, e o jogo gera com {chance:.0%}."
        )

    def test_chefe_a_cada_cinco_andares_como_no_jogo(self):
        # `engine/loop.py`: `if dungeon_level % 5 == 0`. Aqui é determinístico,
        # então uma passada basta.
        from src.sim.harness import _default_floor_plan

        for andar in range(1, 21):
            tem_chefe = "boss_solo" in _default_floor_plan(andar)
            assert tem_chefe == (andar % 5 == 0), f"andar {andar}: chefe {tem_chefe}"


class TestReprodutibilidade:
    """Mesma seed, mesmo resultado — senão nenhum número aqui significa nada.

    A simulação semeia o `rng` que injeta no combate, mas a camada de conteúdo
    sorteia pelo gerador global do módulo `random`: oferta de carta, nível do
    monstro, spawn de elite, drop, estoque da loja e Essência. Enquanto só o
    `rng` local era semeado, o mesmo comando dava 7.0 e 7.8 de andar médio em
    execuções seguidas — oscilação maior que quase todo delta medido, o que
    tornava qualquer achado indistinguível de ruído.
    """

    def test_mesma_seed_produz_a_mesma_run(self):
        kwargs = dict(
            hero_class="Warrior",
            max_floor=12,
            iterations=15,
            policy="smart",
            seed=99,
            loadout="expected",
        )
        primeira = simulate_run(**kwargs)
        segunda = simulate_run(**kwargs)
        assert primeira == segunda, (
            "duas execuções com a mesma seed divergiram: algum sorteio escapa do gerador semeado."
        )

    def test_seeds_diferentes_produzem_runs_diferentes(self):
        """A trava não pode ter congelado o sorteio.

        Compara o resultado inteiro, não o `mean_floor`. A média de 15 inteiros
        cai num conjunto pequeno de valores: em doze seedes medidas, 2 dos 66
        pares davam a mesma média — 3% de chance de este teste reprovar por
        coincidência, sem nada de errado no código.
        """
        kwargs = dict(
            hero_class="Warrior", max_floor=12, iterations=15, policy="smart", loadout="expected"
        )
        assert simulate_run(seed=99, **kwargs) != simulate_run(seed=4242, **kwargs)

    def test_a_simulacao_devolve_o_gerador_global_como_encontrou(self):
        # Deixar o `random` global preso numa sequência fixa faria um teste
        # posterior esconder a instabilidade que ele existe para pegar.
        import random

        estado = random.getstate()
        simulate_run("Warrior", 6, 3, "smart", 7, "expected")
        assert random.getstate() == estado


class TestDesempenho:
    """A suíte precisa ser rápida o bastante para ser usada durante o trabalho."""

    def test_mil_combates_em_poucos_segundos(self):
        import time

        inicio = time.time()
        simulate("Warrior", "bruiser_solo", 10, 1000, "smart", loadout="naked")
        duracao = time.time() - inicio
        assert duracao < 8.0, f"1000 combates levaram {duracao:.1f}s."
