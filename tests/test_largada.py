"""KI-002: a largada continua perigosa, mas um encontro comum não é condenação.

Na auditoria do instrumento (`0ab837b9`), com o BotPadrão já corrigido, 45 de 300
runs morriam no andar 1 e 185 até o andar 5 — e as MESMAS 6 runs morriam na
primeira luta do andar 1 com a vida cheia, antes de qualquer decisão que importe.

O que pesava ali era um papel: o glass cannon, um em cada dez monstros, matava
quase metade das runs dos andares 1-3. O duelo dele é a corrida para matar antes
de morrer, e o contra-jogo (atordoar, explodir primeiro) não existe no herói de
nível 1 com uma skill e nada na mochila. Ele passou a entrar com os papéis
avançados, a partir de `advanced_role_min_floor`.

O arquétipo não foi tocado: o mesmo orçamento, os mesmos pesos, o mesmo deck. O
que mudou foi QUANDO ele entra na população do andar.
"""

from __future__ import annotations

import contextlib
import io
import random

import pytest

from src.content.factories.archetypes import routine_role_weights
from src.content.factories.monsters import (
    create_monster,
    floor_role_plan,
    generation_rules,
)
from src.engine.encounter import resolve_encounter

PRIMEIRO_AVANCADO = int(generation_rules()["advanced_role_min_floor"])

# As seis runs da `0ab837b9` que morriam na primeira luta do andar 1, com 100% de
# HP: Assassino das Sombras Nv.2 (três), Necromante Nv.3, Aparição Nv.2, Orc Nv.1.
PRIMEIRA_LUTA_FATAL = (
    ("mage", 16),
    ("mage", 62),
    ("mage", 93),
    ("rogue", 4),
    ("rogue", 16),
    ("rogue", 98),
)


class TestAPopulacaoDaLargada:
    def test_o_glass_cannon_e_papel_avancado(self):
        assert "glass_cannon" in generation_rules()["advanced_roles"]

    def test_nao_aparece_antes_do_andar_dos_avancados(self):
        for andar in range(1, PRIMEIRO_AVANCADO):
            for semente in range(200):
                plano = floor_role_plan(andar, random.Random(semente))
                assert "glass_cannon" not in plano, f"andar {andar}, semente {semente}"

    def test_a_partir_dali_entra_com_o_peso_de_sempre(self):
        """Ele não sumiu do jogo: a fatia dele no andar 4 é a do peso declarado."""
        pesos = routine_role_weights()
        esperado = pesos["glass_cannon"] / sum(pesos.values())
        papeis = [
            p
            for semente in range(1500)
            for p in floor_role_plan(PRIMEIRO_AVANCADO, random.Random(semente))
            if p != "elite"
        ]
        assert papeis.count("glass_cannon") / len(papeis) == pytest.approx(esperado, abs=0.02)

    def test_o_arquetipo_nao_mudou(self):
        """Mesmo orçamento: um glass cannon do andar 4 é o de antes."""
        canhao = create_monster("x Nv.4", 4, "glass_cannon")
        assert canhao.get_mg() > canhao.get_st()
        assert routine_role_weights()["glass_cannon"] == 10


def _letalidade(classe: str, papel: str, nivel: int, amostras: int = 200) -> float:
    """P(morrer) de um herói de nível 1, vida cheia, contra este duelo no andar 1."""
    import tools.bot_padrao as bp

    mortes = 0
    for semente in range(1, amostras + 1):
        bot = bp.BotPadrao(classe, semente, 1)
        bot.andar = 1
        monstro = create_monster(f"x Nv.{nivel}", nivel, papel)
        with contextlib.redirect_stdout(io.StringIO()):
            resolve_encounter(
                bot.hero,
                [monstro],
                combat_decision=bot.decide,
                level_up_provider=bot._escolher_do_nivel,
                rng=bot.rng,
                dungeon_level=1,
                publish=bot.observador,
            )
        mortes += not (bot.hero.get_isalive() and bot.hero.get_hp() > 0)
    return mortes / amostras


def _papel(nome: str) -> str:
    from src.data.loader import load_monsters_data

    base = nome.rsplit(" Nv.", 1)[0]
    for papel, arq in load_monsters_data()["archetypes"].items():
        if base in arq.get("names", []):
            return papel
    raise AssertionError(f"monstro sem papel: {nome}")


@pytest.fixture(scope="module")
def primeiras_lutas():
    """O andar 1 de cada fixture: a luta fatal, se a run morreu na primeira, com HP cheio."""
    import tools.bot_padrao as bp

    lutas = {}
    for classe, semente in PRIMEIRA_LUTA_FATAL:
        bot = bp.BotPadrao(classe, semente, 1)
        with contextlib.redirect_stdout(io.StringIO()):
            bot.jogar()
        fatal = bot.fatal
        primeira = (
            fatal is not None
            and fatal["andar"] == 1
            and bot.combates_na_run == 1
            and fatal["hp_frac"] >= 0.999
        )
        lutas[(classe, semente)] = fatal if primeira else None
    return lutas


class TestAsSeisRunsDaPrimeiraLuta:
    """Fixtures obrigatórios: a morte some, ou passa a ser exceção do duelo."""

    def test_a_maioria_deixa_de_morrer_na_primeira_luta(self, primeiras_lutas):
        mortes = [k for k, fatal in primeiras_lutas.items() if fatal is not None]
        assert len(mortes) <= len(PRIMEIRA_LUTA_FATAL) // 2, mortes

    def test_quem_ainda_morre_cai_num_duelo_que_raramente_mata(self, primeiras_lutas):
        """O mesmo duelo, repetido com outras seeds, mata menos de 1 em 10.

        É a diferença entre azar e condenação: a morte que sobra é exceção do
        encontro, não um encontro que mata quem o sorteia.
        """
        for (classe, _semente), fatal in primeiras_lutas.items():
            if fatal is None:
                continue
            papel = _papel(fatal["monstro"])
            assert papel not in generation_rules()["advanced_roles"]
            assert _letalidade(classe, papel, fatal["nivel"]) < 0.10, (classe, fatal["monstro"])
