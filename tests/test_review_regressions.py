"""Regressões dos seis defeitos apontados na revisão do PR #3.

Nenhum deles levantava exceção. Os seis passavam por uma suíte verde porque
todos falham em silêncio: um buff que é escrito e nunca lido, uma passiva que
promete "uma vez por combate" e vale uma vez por andar, um evento que a UI
espera e ninguém publica, um campo omitido numa cópia manual de construtor, e
duas divergências entre a masmorra simulada e a de produção.

O padrão é o mesmo dos onze defeitos anteriores: o código roda, o relatório sai
bonito, e o número está errado. Por isso cada teste aqui olha o EFEITO, não a
chamada.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.factories.loot import _build_loot_table  # noqa: E402
from src.mechanics import combat as combat_mech  # noqa: E402
from src.mechanics.battle import Action, run_battle  # noqa: E402
from src.sim.encounters import build_encounter  # noqa: E402


class TestBuffDeMonstroTemEfeito:
    """`Monster.get_*` devolvia o atributo cru e ignorava `active_buffs`."""

    def test_buff_de_defesa_muda_a_defesa(self):
        monstro = spawn_by_role("support", 5)
        antes = monstro.get_df()
        monstro.active_buffs["Bênção Sombria"] = {"stat": "df", "value": 40, "duration": 3}
        assert monstro.get_df() == antes + 40

    def test_buff_de_forca_muda_o_dano(self):
        monstro = spawn_by_role("bruiser", 5)
        antes = monstro.get_avg_damage()
        monstro.active_buffs["Fúria"] = {"stat": "st", "value": 60, "duration": 3}
        assert monstro.get_avg_damage() > antes

    def test_a_skill_de_buff_do_suporte_chega_ao_atributo(self):
        """O caminho completo: `apply_skill` -> `active_buffs` -> `get_df`."""
        monstro = spawn_by_role("support", 5)
        buff = next(s for s in monstro.skills if s.effect_type == "buff")
        antes = monstro.get_df()
        combat_mech.apply_skill(monstro, monstro, buff, rng=random.Random(1), publish=None)
        assert monstro.get_df() > antes, "o suporte gastou mana e turno em nada"

    def test_defesa_maior_reduz_o_dano_recebido(self):
        """Sem isto, o buff poderia aparecer no getter e não no pipeline de dano."""
        atacante = spawn_by_role("glass_cannon", 8)
        base = spawn_by_role("tank", 8)
        buffado = spawn_by_role("tank", 8)
        buffado.active_buffs["Muralha"] = {"stat": "df", "value": 200, "duration": 3}

        # Agilidade zerada dos dois lados: acerto garantido, sem ruído de esquiva.
        for alvo in (base, buffado):
            alvo.base_ag = 0
            alvo._ag = 0

        rolagens = [random.Random(s) for s in range(40)]
        dano_base = sum(
            combat_mech.resolve_physical_attack(
                atacante, base, atacante.get_avg_damage(), "", rng=r
            ).damage
            for r in rolagens
        )
        dano_buff = sum(
            combat_mech.resolve_physical_attack(
                atacante, buffado, atacante.get_avg_damage(), "", rng=random.Random(s)
            ).damage
            for s in range(40)
        )
        assert dano_buff < dano_base


class TestDeathIgnoreEPorCombate:
    """A marca só era apagada no descanso de fim de andar."""

    def _heroi_com_death_ignore(self):
        from src.entities.heroes import Warrior

        heroi = Warrior("Teste")
        heroi._death_ignore_used = True
        return heroi

    def test_o_inicio_da_batalha_limpa_a_marca(self):
        heroi = self._heroi_com_death_ignore()
        monstros = [spawn_by_role("trash", 1)]
        run_battle(
            heroi, monstros, lambda h, m, t: Action(kind="attack"),
            rng=random.Random(7), publish=None, max_turns=1,
        )
        assert heroi._death_ignore_used is False

    def test_o_monstro_tambem_entra_limpo(self):
        heroi = self._heroi_com_death_ignore()
        monstro = spawn_by_role("trash", 1)
        monstro._death_ignore_used = True
        run_battle(
            heroi, [monstro], lambda h, m, t: Action(kind="attack"),
            rng=random.Random(7), publish=None, max_turns=1,
        )
        assert monstro._death_ignore_used is False


class TestFugaEPublicada:
    """A UI inscreve `_on_flee_result` num tópico que ninguém publicava."""

    def _corre(self, semente: int) -> list[tuple[str, object]]:
        from src.entities.heroes import Warrior

        eventos: list[tuple[str, object]] = []
        run_battle(
            Warrior("Teste"), [spawn_by_role("trash", 1)],
            lambda h, m, t: Action(kind="flee"),
            rng=random.Random(semente),
            publish=lambda topico, evento: eventos.append((topico, evento)),
            max_turns=1,
        )
        return eventos

    def test_a_tentativa_de_fuga_publica_o_resultado(self):
        from src.shared import combat_topics as T

        topicos = {t for semente in range(6) for t, _ in self._corre(semente)}
        assert T.COMBAT_FLEE_RESULT in topicos

    def test_o_evento_carrega_o_sucesso_da_rolagem(self):
        from src.shared import combat_topics as T

        vistos = set()
        for semente in range(30):
            for topico, evento in self._corre(semente):
                if topico == T.COMBAT_FLEE_RESULT:
                    vistos.add(bool(evento.payload["success"]))
        assert vistos == {True, False}, "a UI precisa distinguir fuga que deu de fuga que falhou"


class TestConsumivelDeLoot:
    """`_build_loot_table` copiava o construtor à mão e omitia `consumable`."""

    def test_pocoes_dropadas_sao_usaveis(self):
        pocoes = [i for i in _build_loot_table() if i.is_potion]
        assert pocoes, "nenhum consumível utilizável na tabela de loot"

    def test_todo_consumivel_droppable_do_json_chega_utilizavel(self):
        from src.data.loader import load_items_data

        esperado = {
            i["id"]
            for i in load_items_data()["items"]
            if i.get("consumable") and i.get("droppable", True)
        }
        obtido = {i.id for i in _build_loot_table() if i.is_potion}
        assert obtido == esperado

    def test_o_preco_do_json_sobrevive(self):
        """A cópia manual também zerava `price` no default do construtor."""
        from src.data.loader import load_items_data

        precos = {i["id"]: i.get("price", 50) for i in load_items_data()["items"]}
        for item in _build_loot_table():
            assert item.price == precos[item.id]


class TestNivelDoEncontroSorteia:
    """A run simulada fixava todo monstro no andar; o jogo sorteia +0/+1/+2."""

    def test_sem_sorteador_o_nivel_e_o_andar(self):
        monstros = build_encounter("trash_trio", 6)
        assert [m.level for m in monstros] == [6, 6, 6]

    def test_com_sorteador_cada_monstro_sorteia(self):
        contador = iter([7, 8, 9])
        monstros = build_encounter("trash_trio", 6, lambda: next(contador))
        assert [m.level for m in monstros] == [7, 8, 9]

    def test_o_chefe_ignora_o_sorteio(self):
        monstros = build_encounter("boss_solo", 5, lambda: 99)
        assert [m.level for m in monstros] == [5]

    def test_a_run_simulada_gera_monstros_acima_do_andar(self):
        """Regressão de integração: a masmorra medida tem de ter a variação."""
        from src.sim.harness import simulate_run

        niveis: list[int] = []
        original = build_encounter

        import src.sim.harness as harness

        def espiao(name, level, level_fn=None):
            monstros = original(name, level, level_fn)
            niveis.extend(m.level - level for m in monstros)
            return monstros

        harness.build_encounter = espiao
        try:
            simulate_run("Warrior", iterations=12, seed=3, max_floor=8)
        finally:
            harness.build_encounter = original

        assert niveis, "nenhum encontro foi construído"
        assert any(d > 0 for d in niveis), "nenhum monstro acima do andar: a variação sumiu"
        assert all(d >= 0 for d in niveis), "monstro abaixo do andar não existe no jogo"


class TestFugaEncerraOAndar:
    """`run_fight` retorna ao mapa; a simulação seguia para o próximo encontro."""

    def test_fugir_nao_encadeia_o_proximo_combate(self):
        from src.sim.harness import simulate_run

        combates: list[str] = []
        import src.sim.harness as harness

        original = harness.run_battle

        def sempre_foge(hero, monsters, decide, *, rng, publish=None, **kw):
            combates.append("luta")
            resultado = original(
                hero, monsters, lambda h, m, t: Action(kind="flee"),
                rng=random.Random(0), publish=None,
            )
            object.__setattr__(resultado, "fled", True)
            return resultado

        harness.run_battle = sempre_foge
        try:
            simulate_run(
                "Warrior", iterations=1, seed=1, max_floor=3,
                encounters_per_floor=lambda floor: ["trash_solo", "trash_solo", "trash_solo"],
            )
        finally:
            harness.run_battle = original

        # Três andares, um combate cada: o segundo e o terceiro encontro de cada
        # andar não acontecem porque o herói fugiu do primeiro.
        assert len(combates) == 3, f"esperado 1 combate por andar, houve {len(combates)}"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
