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
