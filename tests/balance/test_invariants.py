"""Regressão de balanceamento.

Cada teste aqui falharia no código anterior ao rebalanceamento, e é essa a razão
de existirem: eles nomeiam os defeitos estruturais que a auditoria encontrou e
impedem que voltem sem ninguém notar.

Rodar rápido:    python -m pytest tests/balance -q
Rodar completo:  python -m pytest tests/balance -q -m balance_full
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.content.factories.archetypes import all_archetypes, spawn_by_role  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.passives import load_passives  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.entities.heroes import POTION_BUFFS, POTION_STATUSES  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effects as fx  # noqa: E402
from src.sim.harness import ALL_CLASSES, make_hero, simulate, simulate_run  # noqa: E402
from tests.balance import thresholds as T  # noqa: E402

pytestmark = pytest.mark.balance


# --------------------------------------------------------------- escalonamento


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


# ---------------------------------------------------------------------- acerto


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


# -------------------------------------------------------- cobertura de efeitos


class TestCoberturaDeEfeitos:
    """Todo efeito declarado nos dados precisa existir no motor.

    O defeito original: o motor reconhecia buffs por nome literal, e 16 das 41
    skills, 10 das 29 passivas e 6 dos 11 tipos de poção eram escritos no estado
    e nunca lidos. O conteúdo mais caro do jogo — Fúria, Imortal, Evasão
    Perfeita — não fazia nada.
    """

    STATUS_CONHECIDOS = (
        set(fx.TURN_SKIPPING_STATUSES)
        | set(fx.OUTGOING_DAMAGE_PENALTY)
        | set(fx.DAMAGE_OVER_TIME)
        | set(fx.RESOURCE_DRAIN)
        | {"damage_reduction", "invisible"}
    )
    STATS_CONHECIDOS = set(fx.ATTRIBUTE_STATS) | set(fx.COMBAT_MODIFIERS)

    def test_toda_skill_de_buff_declara_o_atributo_que_modifica(self):
        mortas = [
            s.id for s in load_skills()
            if s.effect_type == "buff" and s.effect_stat not in self.STATS_CONHECIDOS
        ]
        assert not mortas, f"Buffs sem efeito no motor: {mortas}"

    def test_todo_status_de_skill_tem_tratamento_no_motor(self):
        mortos = [
            (s.id, s.effect_value) for s in load_skills()
            if s.effect_type == "status" and str(s.effect_value) not in self.STATUS_CONHECIDOS
        ]
        assert not mortos, f"Status sem tratamento no motor: {mortos}"

    def test_toda_passiva_e_consumida_por_alguma_regra(self):
        consumidas = self.STATS_CONHECIDOS | {
            "max_hp", "max_mp", "strength", "defense", "agility",
            "essence_bonus", "gold_drop_bonus", "potion_heal_bonus", "death_ignore",
        }
        mortas = [p.id for p in load_passives() if p.effect_type not in consumidas]
        assert not mortas, f"Passivas sem efeito: {mortas}"

    def test_todo_consumivel_produz_algum_efeito(self):
        tratados = set(POTION_BUFFS) | set(POTION_STATUSES) | {"max_hp", "max_mp"}
        mortos = [
            i.name for i in get_all_items().values()
            if getattr(i, "consumable", False) and i.effect_type not in tratados
        ]
        assert not mortos, f"Consumíveis sem efeito: {mortos}"

    def test_existem_consumiveis_de_cura(self):
        # Sem cura comprável, remover a cura gratuita torna a run impossível em
        # vez de difícil. O catálogo original não tinha um único consumível.
        curas = [
            i for i in get_all_items().values()
            if getattr(i, "consumable", False) and i.effect_type == "max_hp"
        ]
        assert len(curas) >= 3


# ------------------------------------------------------------- escala relativa


class TestEscalaRelativa:
    """Skill, cura e equipamento precisam manter o peso ao longo dos níveis.

    O defeito original: todos eram somas fixas sobre um poder base que crescia,
    então viravam ruído no fim do jogo. O Apocalipse, a skill mais cara do jogo,
    entregava +30% sobre um ataque básico gratuito no nível 20.
    """

    def test_skill_de_dano_mantem_peso_relativo(self):
        skill = next(s for s in load_skills() if s.effect_type == "damage")
        pesos = []
        for level in (1, 10, 20):
            heroi = make_hero("Warrior", level, "naked")
            pesos.append(cmb.skill_damage_base(heroi, skill) / heroi.get_avg_damage())
        assert max(pesos) - min(pesos) < 0.01

    def test_cura_de_skill_mantem_peso_relativo(self):
        skill = next(s for s in load_skills() if s.effect_type == "heal")
        for level in (1, 20):
            heroi = make_hero("Mage", level, "naked")
            heroi.take_damage(heroi.base_hp - 1)
            antes = heroi.get_hp()
            cmb.apply_skill(heroi, heroi, skill)
            curado = (heroi.get_hp() - antes) / heroi.base_hp
            assert 0.05 <= curado <= 0.80

    def test_equipamento_mantem_peso_relativo(self):
        ganhos = []
        for level in (1, 20):
            pelado = make_hero("Warrior", level, "naked").get_avg_damage()
            equipado = make_hero("Warrior", level, "best").get_avg_damage()
            ganhos.append(equipado / pelado)
        assert abs(ganhos[0] - ganhos[1]) / ganhos[0] < 0.35


# -------------------------------------------------------------------- atrito


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

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_combate_de_rotina_custa_recurso(self, classe):
        resultado = simulate(classe, "bruiser_solo", 8, T.FAST_ITERATIONS, "smart", loadout="expected")
        assert resultado.hp_left_pct_on_win < T.MAX_HP_LEFT_ON_WIN, (
            f"{classe} termina o combate com {resultado.hp_left_pct_on_win:.0%} da vida: "
            "o combate não custou nada."
        )


# ------------------------------------------------------------------ encontros


class TestEncontros:
    """Nenhum encontro pode ser decorativo, nenhum pode ser um muro."""

    @pytest.mark.parametrize("encontro", ["trash_solo", "bruiser_solo", "tank_solo",
                                          "elite_solo", "boss_solo"])
    def test_duracao_dentro_da_banda(self, encontro):
        minimo, maximo = T.TTK_BANDS[encontro]
        for level in (5, 15):
            resultado = simulate("Warrior", encontro, level, T.FAST_ITERATIONS,
                                 "smart", loadout="expected")
            assert minimo <= resultado.turns_mean <= maximo, (
                f"{encontro} no nível {level} dura {resultado.turns_mean:.1f} turnos, "
                f"fora da banda {minimo}-{maximo}."
            )

    def test_nenhum_combate_termina_em_um_turno(self):
        # Todo combate do jogo durava 1 ou 2 turnos, o que não deixava espaço
        # para nenhuma decisão — nem para punir uma decisão ruim.
        for encontro in ("trash_solo", "bruiser_solo"):
            for level in (1, 10, 20):
                resultado = simulate("Mage", encontro, level, T.FAST_ITERATIONS,
                                     "smart", loadout="expected")
                assert resultado.turns_mean >= T.MIN_TTK_ANY_ENCOUNTER

    @pytest.mark.parametrize("encontro", ["elite_solo", "boss_solo", "tank_plus_glass",
                                          "trash_trio", "skirmisher_pair"])
    def test_marco_de_andar_cobra_um_preco(self, encontro):
        # Um encontro isolado começado com a vida cheia não deve matar — a
        # dificuldade mora na sequência. O que mede se ele importa é o custo:
        # antes do rebalanceamento, o jogador terminava toda luta com a vida
        # cheia, porque `rest()` rodava depois de cada vitória.
        custos = [
            1 - simulate(c, encontro, 12, T.FAST_ITERATIONS, "smart", loadout="expected").hp_left_pct_on_win
            for c in ALL_CLASSES
        ]
        assert max(custos) >= T.MIN_HP_COST_MILESTONE, (
            f"{encontro} custa no máximo {max(custos):.0%} da vida. Conteúdo decorativo."
        )

    @pytest.mark.parametrize("encontro", ["elite_solo", "boss_solo", "tank_plus_glass"])
    def test_encontro_nao_e_intransponivel_para_todas_as_classes(self, encontro):
        taxas = [
            simulate(c, encontro, 12, T.FAST_ITERATIONS, "smart", loadout="expected").win_rate
            for c in ALL_CLASSES
        ]
        assert max(taxas) > T.IMPOSSIBLE_WIN_RATE, (
            f"{encontro} é um muro para as três classes: {taxas}."
        )


# ---------------------------------------------------------- skill gap e runs


@pytest.mark.balance_full
class TestRunCompleta:
    """As invariantes que só a run inteira revela.

    São lentas porque simulam 20 andares com atrito. Ficam fora da suíte rápida
    e rodam ao fechar cada mudança de balanceamento.
    """

    @pytest.fixture(scope="class")
    def runs(self):
        return {
            (classe, politica): simulate_run(
                classe, 20, T.FAST_RUN_ITERATIONS, politica, loadout="expected"
            )
            for classe in ALL_CLASSES
            for politica in ("smart", "greedy")
        }

    def test_nenhuma_classe_domina_nem_e_inutil(self, runs):
        medias = {c: runs[(c, "smart")]["mean_floor"] for c in ALL_CLASSES}
        for classe, media in medias.items():
            assert T.MIN_CLASS_MEAN_FLOOR <= media <= T.MAX_CLASS_MEAN_FLOOR, (
                f"{classe} chega em média ao andar {media:.1f}, fora da banda aceitável."
            )
        spread = max(medias.values()) - min(medias.values())
        assert spread <= T.MAX_CLASS_MEAN_FLOOR_SPREAD, (
            f"Distância de {spread:.1f} andares entre a melhor e a pior classe: {medias}"
        )

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_jogar_bem_precisa_valer_a_pena(self, runs, classe):
        # A métrica central do balanceamento. Antes ela era ZERO — e contra o
        # chefe era negativa, porque usar as skills de controle do jogo era pior
        # que ignorá-las: elas não tinham efeito no motor.
        gap = runs[(classe, "smart")]["mean_floor"] - runs[(classe, "greedy")]["mean_floor"]
        assert gap >= T.MIN_SKILL_GAP_FLOORS, (
            f"{classe}: jogar bem rende só {gap:.1f} andares a mais que só atacar."
        )

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_paciencia_nao_substitui_competencia(self, runs, classe):
        taxa = runs[(classe, "greedy")]["reached_20_rate"]
        assert taxa <= T.MAX_GREEDY_REACH_20, (
            f"{classe}: o bot que só ataca termina a masmorra em {taxa:.0%} das runs."
        )

    def test_chegar_ao_20_e_conquista_mas_e_possivel(self, runs):
        taxas = {c: runs[(c, "smart")]["reached_20_rate"] for c in ALL_CLASSES}
        assert max(taxas.values()) >= T.MIN_SMART_REACH_20, (
            f"Nenhuma classe termina a masmorra jogando bem: {taxas}"
        )
        assert max(taxas.values()) <= T.MAX_SMART_REACH_20, (
            f"Terminar a masmorra ficou fácil demais: {taxas}"
        )

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_a_run_entrega_a_progressao_do_jogo(self, runs, classe):
        # O jogo dá uma passiva por nível e uma escolha de skill nos níveis
        # ímpares a partir do 5. Uma simulação que não entrega isso mede um
        # herói que ninguém joga, e todo número calibrado em cima dela é falso.
        dados = runs[(classe, "smart")]
        assert dados["passives_at_end_mean"] >= T.MIN_PASSIVES_AT_END, (
            f"{classe} termina a run com {dados['passives_at_end_mean']:.1f} passivas: "
            "a progressão parou de rodar na simulação."
        )
        assert dados["skills_at_end_mean"] >= 3.0

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_curva_de_dificuldade_e_monotonica(self, runs, classe):
        sobrevivencia = runs[(classe, "smart")]["survival_by_floor"]
        andares = sorted(sobrevivencia)
        for anterior, atual in zip(andares, andares[1:]):
            assert sobrevivencia[atual] <= sobrevivencia[anterior] + 0.001, (
                f"{classe}: o andar {atual} é mais seguro que o {anterior}."
            )

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_dificuldade_cresce_de_fato(self, runs, classe):
        sobrevivencia = runs[(classe, "smart")]["survival_by_floor"]
        assert sobrevivencia[5] > sobrevivencia[20], (
            f"{classe}: chegar ao andar 20 não é mais difícil que chegar ao 5."
        )


# ----------------------------------------------------------------- arquétipos


class TestArquetipos:
    """Cada papel precisa distribuir o orçamento de um jeito diferente."""

    def test_todo_arquetipo_tem_uma_forca_e_uma_fraqueza(self):
        for papel, arquetipo in all_archetypes().items():
            eixos = (arquetipo.hp, arquetipo.attack, arquetipo.defense, arquetipo.agility)
            if papel in ("bruiser", "elite", "boss"):
                continue  # referência e marcos: custam mais orçamento, não o redistribuem
            redistribui = max(eixos) > 1.05 and min(eixos) < 0.95
            # Trash e suporte não redistribuem atributos: eles custam menos
            # orçamento e trazem a ameaça em outro lugar — o trash no número, o
            # suporte nas skills. O que nenhum arquétipo pode ser é forte em
            # tudo sem pagar por isso em lugar nenhum.
            barato_ou_por_skill = max(eixos) <= 1.0 or arquetipo.skills
            assert redistribui or barato_ou_por_skill, (
                f"{papel} não troca nada por nada: {eixos}"
            )

    def test_todo_arquetipo_declara_ameaca_e_counterplay(self):
        for papel, arquetipo in all_archetypes().items():
            assert arquetipo.threat and arquetipo.counterplay, (
                f"{papel} não documenta o que ameaça nem como se responde a ele."
            )

    def test_skirmisher_neutraliza_a_esquiva_do_ladino(self):
        # A fraqueza declarada do Ladino. Se ela não aparecer nos números, a
        # classe volta a não ter contra o que perder.
        ladino = make_hero("Rogue", 10, "expected")
        contra_bruiser = cmb.hit_chance(spawn_by_role("bruiser", 10), ladino)
        contra_skirmisher = cmb.hit_chance(spawn_by_role("skirmisher", 10), ladino)
        assert contra_skirmisher > contra_bruiser + 5


# ------------------------------------------------------------------ desempenho


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
        kwargs = dict(hero_class="Warrior", max_floor=12, iterations=15,
                      policy="smart", seed=99, loadout="expected")
        primeira = simulate_run(**kwargs)
        segunda = simulate_run(**kwargs)
        assert primeira == segunda, (
            "duas execuções com a mesma seed divergiram: algum sorteio escapa "
            "do gerador semeado."
        )

    def test_seeds_diferentes_produzem_runs_diferentes(self):
        # A trava não pode ter congelado o sorteio: sem variação, a média de
        # N runs seria a mesma run repetida N vezes.
        kwargs = dict(hero_class="Warrior", max_floor=12, iterations=15,
                      policy="smart", loadout="expected")
        assert (
            simulate_run(seed=99, **kwargs)["mean_floor"]
            != simulate_run(seed=4242, **kwargs)["mean_floor"]
        )

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
