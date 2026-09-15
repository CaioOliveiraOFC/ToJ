"""O simulador e a Forge Run contam os mesmos monstros.

Havia duas regras tentando representar a mesma coisa: o jogo povoava o andar por
`generate_monsters_for_level` e o simulador por uma tabela escrita à mão, por
faixa de profundidade. Elas divergiram — no andar 20 a tabela levava 14 lutas
contra os 10 monstros que o jogo gera, 39% a mais — e toda medição de
dificuldade e de renda feita em cima disso mediu uma masmorra que não existe.

A correção não é aproximar os dois números: é ter um número só. Estes testes
cobram a FONTE ÚNICA, não uma semelhança de média.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.monsters import (  # noqa: E402
    floor_role_plan,
    generate_monsters_for_level,
    routine_monster_count,
)
from src.shared.constants import BOSS_FLOOR_INTERVAL  # noqa: E402
from src.sim import encounters  # noqa: E402
from src.sim.harness import _default_floor_plan  # noqa: E402

ANDARES = (1, 2, 5, 10, 15, 20, 50)
SEMENTES = (0, 1, 7, 42, 1337)


class TestFonteUnica:
    @pytest.mark.parametrize("andar", ANDARES)
    @pytest.mark.parametrize("semente", SEMENTES)
    def test_o_plano_do_sim_e_o_do_jogo_para_a_mesma_semente(self, andar, semente):
        """Mesma semente, mesmo plano: quantidade E composição."""
        papeis = floor_role_plan(andar, random.Random(semente))
        lutas = _default_floor_plan(andar, random.Random(semente))

        chefes = [n for n in lutas if n == "boss_solo"]
        comuns = [n for n in lutas if n != "boss_solo"]

        assert comuns == [encounters.solo_for_role(p) for p in papeis]
        assert len(chefes) == (1 if andar % BOSS_FLOOR_INTERVAL == 0 else 0)

    @pytest.mark.parametrize("andar", ANDARES)
    def test_a_quantidade_do_sim_e_a_que_o_jogo_gera(self, andar):
        """Contra o gerador de verdade, e não contra a fórmula de novo."""
        esperado = routine_monster_count(andar) + (1 if andar % BOSS_FLOOR_INTERVAL == 0 else 0)
        semente = random.Random(99)
        lutas = _default_floor_plan(andar, semente)
        # O elite é sorteado (12% a partir do andar 4), então a contagem bate
        # exatamente ou tem um elite a mais — nunca a tabela inventada de antes.
        assert len(lutas) in (esperado, esperado + 1)

    def test_o_elite_segue_a_regra_do_jogo(self):
        """Nada de elite antes do andar mínimo, nem em todo andar múltiplo de 3."""
        from src.content.factories.monsters import generation_rules

        minimo = int(generation_rules()["advanced_role_min_floor"])
        for andar in range(1, minimo):
            for semente in range(40):
                assert "elite" not in floor_role_plan(andar, random.Random(semente))

    def test_o_sim_nao_tem_mais_tabela_propria_de_andar(self):
        """A regressão que este arquivo existe para impedir."""
        import inspect

        from src.sim import harness

        fonte = inspect.getsource(harness._default_floor_plan)
        assert "floor_role_plan" in fonte
        for inventado in ("floor <= 5", "floor <= 10", "3 + floor //"):
            assert inventado not in fonte, f"Tabela própria de volta: {inventado!r}"


class TestOQueNaoMudou:
    def test_o_combate_continua_1x1(self):
        semente = random.Random(3)
        for andar in ANDARES:
            for nome in _default_floor_plan(andar, semente):
                assert len(encounters.build_encounter(nome, andar)) == 1

    def test_os_cenarios_isolados_continuam_disponiveis(self):
        """Cenário de TESTE e plano de RUN são coisas diferentes, e ambas ficam."""
        for nome in encounters.SOLO_ENCOUNTERS:
            assert len(encounters.build_encounter(nome, 10)) == 1
        assert encounters.MATRIX_ENCOUNTERS == encounters.SOLO_ENCOUNTERS

    def test_o_jogo_continua_gerando_pelo_proprio_plano(self):
        """A extração do plano não pode ter mudado o que o jogo coloca no mapa."""
        for andar in (1, 5, 20):
            monstros = generate_monsters_for_level(andar, andar)
            assert len(monstros) >= routine_monster_count(andar)
            assert all(m.get_level() >= 1 for m in monstros)
