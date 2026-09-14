"""O combate é 1x1, e esta é a rede que impede o encontro em grupo de voltar.

Houve uma fase em que uma casa do mapa guardava dois ou três monstros e a
batalha era 1x3. Foi um erro de direção: o jogo é um herói contra um monstro,
sempre. O andar pode ter dez inimigos — dez casas, dez batalhas.

Os testes abaixo não medem balanceamento. Medem o INVARIANTE: o motor recusa
mais de um monstro, o mapa recusa uma casa com grupo, o jogador não escolhe
alvo porque não há o que escolher, e o simulador mede o jogo que existe.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.engine import loop  # noqa: E402
from src.mechanics import battle, monster_ai  # noqa: E402
from src.sim import encounters, policies  # noqa: E402
from src.sim.harness import _default_floor_plan  # noqa: E402
from src.ui import renderer, screens  # noqa: E402


def _heroi(nivel: int = 10):
    from src.entities.heroes import Warrior

    heroi = Warrior("Teste")
    heroi.set_level(nivel)
    return heroi


class TestOMotorRecusaGrupo:
    def test_run_battle_aceita_exatamente_um_monstro(self):
        batalha = battle.run_battle(
            _heroi(),
            [spawn_by_role("trash", 1)],
            lambda h, m, t: battle.Action(kind="attack"),
            rng=random.Random(7),
            publish=None,
            max_turns=1,
        )
        assert batalha is not None

    @pytest.mark.parametrize("quantidade", [0, 2, 3])
    def test_run_battle_recusa_qualquer_outra_quantidade(self, quantidade):
        with pytest.raises(ValueError):
            battle.run_battle(
                _heroi(),
                [spawn_by_role("trash", 1) for _ in range(quantidade)],
                lambda h, m, t: battle.Action(kind="attack"),
                rng=random.Random(7),
                publish=None,
                max_turns=1,
            )

    def test_o_erro_aparece_antes_do_primeiro_turno(self):
        """Falhar no meio da luta seria pior que não falhar: o jogador já pagou."""
        monstros = [spawn_by_role("trash", 1) for _ in range(2)]
        vidas = [m.get_hp() for m in monstros]
        with pytest.raises(ValueError):
            battle.run_battle(
                _heroi(),
                monstros,
                lambda h, m, t: battle.Action(kind="attack"),
                rng=random.Random(7),
                publish=None,
            )
        assert [m.get_hp() for m in monstros] == vidas


class TestNaoExisteSelecaoDeAlvo:
    """Um inimigo, um alvo: a pergunta deixou de existir, e não só a resposta."""

    def test_o_jogador_nao_tem_mais_menu_de_alvo(self):
        assert not hasattr(loop, "_choose_target")
        assert not hasattr(screens, "render_target_select_panel")
        assert not hasattr(renderer, "render_target_select_panel")

    def test_o_bot_do_simulador_tambem_nao_escolhe(self):
        assert not hasattr(policies, "_choose_target")
        assert not hasattr(policies, "PRIORITY_ROLES")

    def test_o_alvo_padrao_e_o_unico_inimigo(self):
        monstro = spawn_by_role("trash", 1)
        assert battle.pick_default_target([monstro]) is monstro
        assert battle.sole_monster([monstro]) is monstro


class TestSupportLutaSozinho:
    """O papel mudou de "apoia outro monstro" para "sustain e preparação"."""

    def test_nenhuma_skill_de_support_depende_de_aliado(self):
        monstro = spawn_by_role("support", 12)
        assert monstro.skills, "O Suporte precisa continuar tendo cartas."
        assert {getattr(s, "target", "enemy") for s in monstro.skills} <= {"self", "enemy"}

    def test_o_support_ferido_se_cura_sozinho(self):
        """A rotina dele é sustain: com um alvo só, ainda tem o que fazer."""
        monstro = spawn_by_role("support", 12)
        monstro.take_damage(int(monstro.base_hp * 0.7))
        ferido = monstro.get_hp()
        heroi = _heroi(12)
        for _ in range(6):
            monster_ai.decide_monster_action(monstro, heroi, rng=random.Random(3), publish=None)
            if monstro.get_hp() > ferido:
                break
        assert monstro.get_hp() > ferido, "O Suporte não conseguiu se sustentar no duelo."

    def test_o_duelo_contra_support_acontece_e_termina(self):
        from src.sim.harness import simulate

        resultado = simulate("Warrior", "support_solo", 12, 40, "smart", loadout="expected")
        assert 0.0 <= resultado.win_rate <= 1.0
        assert resultado.turns_mean > 0


class TestOSimuladorMedeODuelo:
    def test_o_catalogo_de_encontros_so_tem_duelo(self):
        for nome, fabrica in encounters.ENCOUNTERS.items():
            assert len(fabrica(5)) == 1, f"{nome} não é um duelo."

    def test_nao_sobrou_conjunto_de_encontro_em_grupo(self):
        assert not hasattr(encounters, "GROUP_ENCOUNTERS")
        assert encounters.MATRIX_ENCOUNTERS == encounters.SOLO_ENCOUNTERS
        assert all(nome.endswith("_solo") for nome in encounters.ROUTINE_ENCOUNTERS)

    @pytest.mark.parametrize("andar", [1, 5, 10, 15, 20])
    def test_o_plano_de_andar_so_marca_duelos(self, andar):
        random.seed(0)
        for nome in _default_floor_plan(andar):
            assert len(encounters.build_encounter(nome, andar)) == 1
