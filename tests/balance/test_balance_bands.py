"""Bandas de balanceamento: medição, não lei.

Cada número aqui foi calibrado para o meta de uma versão do jogo e pode mudar
legitimamente quando o design mudar. Por isso este arquivo é marcado `balance` e
fica fora da execução padrão: uma banda estourada é informação sobre o jogo, não
um defeito no código.

O que NÃO pode mudar sem ser um bug está em `tests/test_structural_invariants.py`
e roda sempre.

    python -m pytest -q -m balance
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.sim.harness import ALL_CLASSES, make_hero, simulate, simulate_run  # noqa: E402
from src.sim.metrics import curve_deltas, spread, variance_explained  # noqa: E402
from tests.balance import thresholds as T  # noqa: E402

pytestmark = pytest.mark.balance


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


class TestAtrito:
    """Vencer um combate precisa custar alguma coisa.

    O defeito original: `rest()` era chamado depois de cada vitória, a cada
    nível, ao equipar, ao desequipar e ao fugir. Cada combate começava com
    recursos cheios e nenhum custava nada ao seguinte, o que anulava poções,
    gestão de MP, skills de cura e a própria decisão de extrair.
    """

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_combate_de_rotina_custa_recurso(self, classe):
        resultado = simulate(
            classe, "bruiser_solo", 8, T.FAST_ITERATIONS, "smart", loadout="expected"
        )
        assert resultado.hp_left_pct_on_win < T.MAX_HP_LEFT_ON_WIN, (
            f"{classe} termina o combate com {resultado.hp_left_pct_on_win:.0%} da vida: "
            "o combate não custou nada."
        )


class TestEncontros:
    """Nenhum encontro pode ser decorativo, nenhum pode ser um muro."""

    @pytest.mark.parametrize(
        "encontro", ["trash_solo", "bruiser_solo", "tank_solo", "elite_solo", "boss_solo"]
    )
    def test_duracao_dentro_da_banda(self, encontro):
        minimo, maximo = T.TTK_BANDS[encontro]
        for level in (5, 15):
            resultado = simulate(
                "Warrior", encontro, level, T.FAST_ITERATIONS, "smart", loadout="expected"
            )
            assert minimo <= resultado.turns_mean <= maximo, (
                f"{encontro} no nível {level} dura {resultado.turns_mean:.1f} turnos, "
                f"fora da banda {minimo}-{maximo}."
            )

    def test_nenhum_combate_termina_em_um_turno(self):
        # Todo combate do jogo durava 1 ou 2 turnos, o que não deixava espaço
        # para nenhuma decisão — nem para punir uma decisão ruim.
        for encontro in ("trash_solo", "bruiser_solo"):
            for level in (1, 10, 20):
                resultado = simulate(
                    "Mage", encontro, level, T.FAST_ITERATIONS, "smart", loadout="expected"
                )
                assert resultado.turns_mean >= T.MIN_TTK_ANY_ENCOUNTER

    @pytest.mark.parametrize(
        "encontro", ["elite_solo", "boss_solo", "tank_solo", "controller_solo", "skirmisher_solo"]
    )
    def test_marco_de_andar_cobra_um_preco(self, encontro):
        # Um encontro isolado começado com a vida cheia não deve matar — a
        # dificuldade mora na sequência. O que mede se ele importa é o custo:
        # antes do rebalanceamento, o jogador terminava toda luta com a vida
        # cheia, porque `rest()` rodava depois de cada vitória.
        custos = [
            1
            - simulate(
                c, encontro, 12, T.FAST_ITERATIONS, "smart", loadout="expected"
            ).hp_left_pct_on_win
            for c in ALL_CLASSES
        ]
        assert max(custos) >= T.MIN_HP_COST_MILESTONE, (
            f"{encontro} custa no máximo {max(custos):.0%} da vida. Conteúdo decorativo."
        )

    @pytest.mark.parametrize("encontro", ["elite_solo", "boss_solo", "tank_solo"])
    def test_encontro_nao_e_intransponivel_para_todas_as_classes(self, encontro):
        taxas = [
            simulate(c, encontro, 12, T.FAST_ITERATIONS, "smart", loadout="expected").win_rate
            for c in ALL_CLASSES
        ]
        assert max(taxas) > T.IMPOSSIBLE_WIN_RATE, (
            f"{encontro} é um muro para as três classes: {taxas}."
        )


# ---------------------------------------------------------- skill gap e runs


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
        # `spread` vem de metrics.py em vez de ser recalculado aqui: era a
        # mesma conta escrita em dois lugares, e a função lá estava morta —
        # nenhuma chamada em todo o repositório. Duas cópias de uma fórmula
        # divergem na primeira mudança.
        distancia = spread(list(medias.values()))
        assert distancia <= T.MAX_CLASS_MEAN_FLOOR_SPREAD, (
            f"Distância de {distancia:.1f} andares entre a melhor e a pior classe: {medias}"
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
    def test_nenhum_andar_sozinho_decide_a_run(self, runs, classe):
        """A curva precisa distribuir o atrito, não concentrá-lo num degrau.

        Substitui um teste que verificava se a curva era monotônica. Ela é
        monotônica **por construção**: `survival_by_floor` só incrementa o andar
        que a run alcançou, e alcançar o andar N+1 exige ter alcançado o N. O
        teste não podia falhar, então não media nada.

        A pergunta que vale é outra: onde a run é decidida. Hoje a maior queda
        está sempre no andar 3, e vale 0.19 no Guerreiro, 0.21 no Ladino e 0.47
        no Mago — quase metade das runs do Mago termina num andar só. A parede
        do andar 3 é achado de design em aberto; o limite aqui existe para pegar
        piora, não para dizer que está bom.
        """
        deltas = curve_deltas(runs[(classe, "smart")]["survival_by_floor"])
        andar, queda = max(deltas, key=lambda item: item[1])
        assert queda <= T.MAX_FLOOR_DROP, (
            f"{classe}: o andar {andar} sozinho encerra {queda:.0%} das runs."
        )

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_a_curva_cai_de_verdade(self, runs, classe):
        # Sem atrito acumulado, a masmorra é um corredor: o teste de andar médio
        # ainda passaria com uma curva quase plana e uma cauda curta.
        sobrevivencia = runs[(classe, "smart")]["survival_by_floor"]
        atrito = sobrevivencia[1] - sobrevivencia[20]
        assert atrito >= T.MIN_TOTAL_ATTRITION, (
            f"{classe}: só {atrito:.0%} das runs se perdem entre o andar 1 e o 20."
        )

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_dificuldade_cresce_de_fato(self, runs, classe):
        sobrevivencia = runs[(classe, "smart")]["survival_by_floor"]
        assert sobrevivencia[5] > sobrevivencia[20], (
            f"{classe}: chegar ao andar 20 não é mais difícil que chegar ao 5."
        )


class TestArquetipos:
    """Cada papel precisa distribuir o orçamento de um jeito diferente."""

    def test_skirmisher_neutraliza_a_esquiva_do_ladino(self):
        # A fraqueza declarada do Ladino. Se ela não aparecer nos números, a
        # classe volta a não ter contra o que perder.
        ladino = make_hero("Rogue", 10, "expected")
        contra_bruiser = cmb.hit_chance(spawn_by_role("bruiser", 10), ladino)
        contra_skirmisher = cmb.hit_chance(spawn_by_role("skirmisher", 10), ladino)
        assert contra_skirmisher > contra_bruiser + 5


class TestPesoDaSorte:
    """A moeda não pode decidir a run mais que o jogador.

    A Essência sorteada nos cinco primeiros andares explicava 38,7% da variância
    da profundidade final. Nesse trecho o herói ainda não tem passiva,
    equipamento nem nível para compensar um sorteio ruim, então o número decide
    antes de existir decisão. Para comparação, escolher carta de propósito em
    vez de sortear vale 1,5 andar, e a distância entre o quartil azarado e o
    sortudo era de 12,4.

    O desvio do sorteio caiu de 0.5 para 0.2. A média não mudou, então o ritmo
    do jogo é o mesmo; o que sai é o peso da sorte.
    """

    @pytest.mark.parametrize("classe", ALL_CLASSES)
    def test_a_essencia_sorteada_nao_decide_a_run(self, classe):
        dados = simulate_run(classe, 20, T.FAST_RUN_ITERATIONS, "smart", loadout="expected")
        explicado = variance_explained(
            dados["early_essence_by_run"],
            [float(d) for d in dados["deepest_by_run"]],
        )
        assert explicado <= T.MAX_LUCK_VARIANCE_EXPLAINED, (
            f"{classe}: a Essência dos primeiros andares explica {explicado:.0%} "
            "da profundidade final — a run é da moeda, não do jogador."
        )

    def test_reduzir_a_sorte_nao_mudou_o_ritmo_do_jogo(self):
        # A média do sorteio não mudou, então o andar médio tem de continuar na
        # banda. Se cair fora, quem mexeu no desvio mexeu na média junto.
        medias = {
            classe: simulate_run(classe, 20, T.FAST_RUN_ITERATIONS, "smart", loadout="expected")[
                "mean_floor"
            ]
            for classe in ALL_CLASSES
        }
        for classe, media in medias.items():
            assert T.MIN_CLASS_MEAN_FLOOR <= media <= T.MAX_CLASS_MEAN_FLOOR, (
                f"{classe} chega ao andar {media:.1f}, fora da banda."
            )
