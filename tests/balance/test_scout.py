"""Testes do scout de sistemas.

O scout responde "qual skill é forte demais, qual passiva ninguém leva, quanto a
Essência decide a run". Ele só vale se a telemetria estiver realmente sendo
coletada e se os interruptores de ablação realmente desligarem o sistema — dois
defeitos que passam despercebidos, porque em ambos o relatório continua saindo,
só que com zeros.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.sim import scout  # noqa: E402
from src.sim.harness import simulate_run  # noqa: E402
from src.sim.pick_policies import (  # noqa: E402
    DELIBERATE_POLICIES,
    PASSIVE_PRIORITIES,
    POLICIES,
    SKILL_PRIORITIES,
    get_pick_policy,
)
from src.sim.toggles import ABLATION_SYSTEMS, Toggles  # noqa: E402

pytestmark = pytest.mark.balance

RUNS = 12


@pytest.fixture(scope="module")
def telemetria():
    return simulate_run("Warrior", 20, RUNS, "smart", 1337, "expected")["telemetry"]


class TestTelemetria:
    """A run precisa registrar o que cada sistema entregou."""

    def test_registra_combate(self, telemetria):
        assert telemetria["battles"] > 0
        assert telemetria["turns"] > telemetria["battles"], "menos de um turno por batalha"

    def test_registra_dano_por_skill_e_por_mana(self, telemetria):
        skills = telemetria["skills"]
        assert skills["damage"], "nenhuma skill causou dano"
        assert skills["mp"], "nenhuma skill consumiu mana"
        assert skills["basic_damage"] > 0, "o ataque básico nunca foi usado"
        # Sem dano por mana não dá para dizer se uma skill é eficiente demais.
        assert any(m > 0 for m in skills["mp"].values())

    def test_registra_ofertas_e_escolhas(self, telemetria):
        for sistema in ("skills", "passives"):
            assert telemetria[sistema]["offered"], f"{sistema} sem oferta registrada"
        assert telemetria["passives"]["picked"], "nenhuma passiva escolhida"

    def test_registra_equipamento_e_economia(self, telemetria):
        equipamento = telemetria["equipment"]
        assert equipamento["power_samples"] == RUNS
        assert equipamento["power_equipped_sum"] >= equipamento["power_naked_sum"], (
            "equipar não pode reduzir o poder"
        )
        assert telemetria["economy"]["gold_earned"] > 0

    def test_essencia_fica_dentro_do_intervalo_do_jogo(self, telemetria):
        from src.shared.constants import ESSENCE_MULT_MAX, ESSENCE_MULT_MIN

        essencia = telemetria["essence"]
        assert essencia["rolls"] > 0
        media = essencia["sum"] / essencia["rolls"]
        assert ESSENCE_MULT_MIN <= media <= ESSENCE_MULT_MAX, (
            f"média de {media:.2f} fora de [{ESSENCE_MULT_MIN}, {ESSENCE_MULT_MAX}]: "
            "o agregador está somando médias em vez de somas."
        )
        assert essencia["xp_after"] >= essencia["xp_base"]

    def test_todo_evento_sorteado_tem_tratamento(self, telemetria):
        from src.content.factories.dungeons import RANDOM_EVENT_TYPES

        tratados = {"fountain", "altar", "merchant"}
        assert set(RANDOM_EVENT_TYPES) <= tratados, (
            "existe evento que o jogo sorteia e a simulação ignora — ele apareceria "
            "no scout como 'morta' sem ser culpa do design."
        )


class TestDerrota:
    """A luta que encerra a run é a que mais informa, e era a única descartada.

    `simulate_run` saía do laço assim que o herói morria, antes de registrar a
    batalha. Com isso a telemetria via 100% das vitórias e 0% das derrotas: a
    duração média do combate caía, uma skill usada só na luta fatal aparecia
    como "escolhida mas nunca usada", e não havia como perguntar o que o herói
    estava fazendo quando morreu.
    """

    def test_a_batalha_fatal_e_registrada(self):
        # Mago pelado, sem usar skill, contra um chefe no andar 1: toda run
        # morre no primeiro combate. Se a batalha fatal fosse descartada, a
        # telemetria não teria batalha nenhuma.
        resultado = simulate_run(
            "Mage", 20, 20, "greedy", 7, "naked",
            encounters_per_floor=lambda andar: ["boss_solo"],
        )
        telemetria = resultado["telemetry"]
        assert resultado["mean_floor"] == 0.0, "o cenário precisa matar toda run no andar 1"
        assert telemetria["defeats"] == 20
        assert telemetria["battles"] == 20, (
            "a luta que encerrou a run não entrou na telemetria"
        )
        assert telemetria["turns"] > 0

    def test_derrota_conta_a_run_que_o_heroi_nao_terminou(self):
        runs = 40
        resultado = simulate_run("Warrior", 20, runs, "smart", 1337, "expected")
        sobreviventes = round(resultado["reached_20_rate"] * runs)
        assert resultado["telemetry"]["defeats"] == runs - sobreviventes

    def test_toda_run_derrotada_deixa_pelo_menos_uma_batalha(self):
        resultado = simulate_run("Warrior", 20, RUNS, "smart", 1337, "expected")
        telemetria = resultado["telemetry"]
        assert telemetria["battles"] >= telemetria["defeats"] > 0


class TestAblacao:
    """Desligar um sistema precisa realmente desligá-lo."""

    @pytest.mark.parametrize("sistema", ABLATION_SYSTEMS)
    def test_interruptor_muda_a_run(self, sistema):
        desligado = Toggles().without(**{sistema: False})
        assert getattr(desligado, sistema) is False
        assert sistema in desligado.label()

    def test_sem_passivas_a_run_nao_ganha_passiva(self):
        resultado = simulate_run(
            "Warrior", 10, 5, "smart", 1337, "expected",
            toggles=Toggles().without(passives=False),
        )
        assert resultado["passives_at_end_mean"] == 0

    def test_sem_essencia_o_xp_nao_e_multiplicado(self):
        resultado = simulate_run(
            "Warrior", 10, 5, "smart", 1337, "expected",
            toggles=Toggles().without(essence=False),
        )
        essencia = resultado["telemetry"]["essence"]
        assert essencia["xp_after"] == essencia["xp_base"]

    def test_banir_carta_a_remove_da_oferta(self):
        from src.content.skills_loader import load_skills

        alvo = next(s for s in load_skills() if not s.is_initial and s.skill_class == "Warrior")
        resultado = simulate_run(
            "Warrior", 20, 8, "smart", 1337, "expected",
            toggles=Toggles().without(banned_skills=frozenset({alvo.id})),
        )
        assert alvo.id not in resultado["telemetry"]["skills"]["picked"]

    def test_rotulo_descreve_o_que_foi_desligado(self):
        assert Toggles().label() == "completo"
        assert Toggles().without(loot=False, shop=False).label() == "loot+shop"


class TestRelatorio:
    """O scout precisa produzir destaques legíveis a partir da telemetria."""

    def test_produz_achados_em_todos_os_sistemas(self, telemetria):
        achados = (
            scout.analyse_skills(telemetria)
            + scout.analyse_passives(telemetria)
            + scout.analyse_equipment(telemetria)
            + scout.analyse_essence_and_events(telemetria)
        )
        sistemas = {f.system for f in achados}
        assert {"skills", "passivas", "equipamento", "economia", "essência"} <= sistemas

    def test_texto_do_relatorio_menciona_os_sistemas(self, telemetria):
        relatorio = scout.ScoutReport(
            iterations=RUNS, classes=["Warrior"], telemetry=telemetria,
            findings=scout.analyse_skills(telemetria) + scout.analyse_equipment(telemetria),
            baseline_mean_floor=5.0,
        )
        texto = scout.format_report(relatorio)
        assert "SKILLS" in texto and "EQUIPAMENTO" in texto

    def test_relatorio_serializa_para_json(self, telemetria):
        import json

        relatorio = scout.ScoutReport(
            iterations=RUNS, classes=["Warrior"], telemetry=telemetria,
            findings=scout.analyse_skills(telemetria), baseline_mean_floor=5.0,
        )
        assert json.dumps(relatorio.to_dict())


class TestAmostraPequena:
    """Carta ausente por sorteio não é carta ausente do jogo.

    A oferta de passiva é ponderada por raridade: uma Lendária pesa 2 contra 60
    de uma Comum. Numa amostra curta ela falta porque o sorteio não calhou, e
    declarar isso "conteúdo morto" manda corrigir um problema que não existe.
    """

    def test_amostra_curta_nao_declara_carta_morta(self):
        curta = {"passives": {"offered": {"coracao_ferro": 40},
                              "picked": {"coracao_ferro": 40}}}
        assuntos = {f.subject for f in scout.analyse_passives(curta)}
        assert "nunca sorteadas" not in assuntos

    def test_amostra_longa_ainda_acusa_carta_morta(self):
        # A guarda não pode virar desculpa: com amostra grande a ausência volta
        # a ser achado.
        longa = {"passives": {"offered": {"coracao_ferro": 4000},
                              "picked": {"coracao_ferro": 4000}}}
        mortas = [f for f in scout.analyse_passives(longa) if f.subject == "nunca sorteadas"]
        assert mortas and mortas[0].value > 0


class TestPoliticasDeEscolha:
    """Várias intenções de build, para separar carta fraca de carta de nicho.

    Com uma política só, "esta passiva é ignorada" mistura duas causas: a carta
    é ruim, ou serve a uma build que aquele bot não joga. É a diferença entre
    corrigir o conteúdo e corrigir o medidor.
    """

    def test_toda_politica_deliberada_cobre_todo_efeito_de_passiva(self):
        from src.content.passives import load_passives

        efeitos = {p.effect_type for p in load_passives()}
        for nome, ordem in PASSIVE_PRIORITIES.items():
            faltando = efeitos - set(ordem)
            assert not faltando, (
                f"a política {nome} não sabe ordenar {faltando}: essas passivas "
                "cairiam no desempate por valor e o ranking viraria ruído."
            )

    def test_toda_politica_cobre_todo_tipo_de_skill(self):
        from src.content.skills_loader import load_skills

        tipos = {s.effect_type for s in load_skills()}
        for nome, ordem in SKILL_PRIORITIES.items():
            assert tipos <= set(ordem), f"a política {nome} não ordena {tipos - set(ordem)}"

    def test_politicas_diferentes_escolhem_cartas_diferentes(self):
        # Se todas escolhessem igual, comparar não separaria nada.
        import random as _random

        from src.content.passives import load_passives

        cartas = load_passives()[:3]
        heroi = None
        escolhas = {
            nome: get_pick_policy(nome).pick_passive(heroi, cartas, _random.Random(1)).id
            for nome in DELIBERATE_POLICIES
        }
        assert len(set(escolhas.values())) > 1, (
            f"todas as intenções levaram a mesma carta: {escolhas}"
        )

    def test_desempate_dentro_do_efeito_e_por_valor(self):
        """A ordem da oferta não pode decidir entre duas cartas do mesmo efeito.

        `max_hp` tem seis cartas, de +15 a +200. Se a política levasse a
        primeira da lista, a Lendária apareceria como ignorada em metade das
        ofertas em que aparece ao lado da Comum — e o scout reportaria um
        defeito de conteúdo que é, na verdade, defeito do medidor.
        """
        import random as _random

        from src.content.passives import get_passive_by_id

        fraca = get_passive_by_id("coracao_ferro")
        forte = get_passive_by_id("coracao_tita")
        assert fraca.effect_type == forte.effect_type

        for ordem in ([fraca, forte], [forte, fraca]):
            escolhida = get_pick_policy("survival").pick_passive(None, ordem, _random.Random(1))
            assert escolhida.id == forte.id, (
                f"a oferta {[c.id for c in ordem]} levou a carta mais fraca"
            )

    def test_politica_aleatoria_nao_e_deliberada(self):
        assert POLICIES["random"].deliberate is False
        assert "random" not in DELIBERATE_POLICIES

    def test_politica_desconhecida_falha_alto(self):
        with pytest.raises(ValueError, match="Política de escolha desconhecida"):
            get_pick_policy("nao_existe")

    def test_a_run_aceita_cada_politica(self):
        for nome in POLICIES:
            resultado = simulate_run("Warrior", 8, 4, "smart", 1337, "expected",
                                     pick_policy=nome)
            assert resultado["pick_policy"] == nome

    def test_comparacao_produz_taxa_por_politica(self):
        comparacao = scout.compare_pick_policies(
            iterations=5, classes=["Warrior"], policy="smart",
            loadout="expected", seed=1337, max_floor=12,
        )
        assert set(comparacao.mean_floor_by_policy) == set(POLICIES)
        assert comparacao.passive_pick_rate, "nenhuma taxa de escolha de passiva registrada"
        assert isinstance(comparacao.choice_value(), float)

    def test_carta_sem_amostra_nao_e_confundida_com_carta_recusada(self):
        """Falta de oferta e recusa do jogador são causas diferentes.

        A carta que uma política ofereceu pouco fica de fora da tabela daquela
        política. Lida como taxa zero, ela era condenada como fraca — e o viés
        não é aleatório: as intenções que morrem mais raso nunca chegam às
        cartas de fim de jogo, então eram sempre elas as condenadas.
        """
        comparacao = scout.PolicyComparison()
        comparacao.mean_floor_by_policy = {nome: 8.0 for nome in POLICIES}
        # `apocalipse` só tem taxa numa intenção; `cutelada` tem em todas.
        comparacao.skill_pick_rate = {
            "survival": {"cutelada": 0.0},
            "offense": {"cutelada": 0.0},
            "economy": {"cutelada": 0.0, "apocalipse": 1.0},
            "random": {},
        }
        por_assunto = {
            f.subject: f.detail
            for f in scout._analyse_cards(comparacao.skill_pick_rate, "skills")
        }

        assert "Apocalipse" in por_assunto.get("sem amostra suficiente", "")
        assert "Apocalipse" not in por_assunto.get("recusadas por toda intenção", "")
        assert "Apocalipse" not in por_assunto.get("cartas de identidade", "")
        # A carta com amostra em todas continua sendo julgada.
        assert "Cutelada" in por_assunto.get("recusadas por toda intenção", "")

    def test_comparacao_gera_achados_classificando_cartas(self):
        comparacao = scout.compare_pick_policies(
            iterations=5, classes=["Warrior"], policy="smart",
            loadout="expected", seed=1337, max_floor=12,
        )
        achados = scout.analyse_pick_policies(comparacao)
        assuntos = {f.subject for f in achados}
        assert "valor de escolher" in assuntos
        assert "ranking de intenção" in assuntos
