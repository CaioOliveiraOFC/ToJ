"""A sonda de status mede cada tentativa, e não muda o combate (KI-015).

A sonda anterior contava o evento `<status>_applied`, que o ramo principal das
skills de status não publica: `frozen`, `sleep` e `invisible` saíam com zero
aplicações na matriz enquanto as leis que dependem deles disparavam.

Os testes aqui são DIRIGIDOS e EXATOS. Cada um põe o combate numa situação
conhecida e confere a contagem da sonda contra a verdade observada na própria
entidade, chamada a chamada. Nenhum compara totais agregados de uma run: um
invariante de soma ("se a lei disparou, o status foi contado") daria falso
positivo sempre que a lei e o status vivessem em janelas de contagem diferentes.
"""

from __future__ import annotations

import collections
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import all_archetypes, spawn_by_role  # noqa: E402
from src.content.passives import PassiveCard  # noqa: E402
from src.mechanics import battle, combat  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from tools import cobertura_pve as cob  # noqa: E402

NIVEL = 20


def _skill_de_monstro(skill_id: str):
    for arquetipo in all_archetypes().values():
        for skill in arquetipo.skills:
            if skill.id == skill_id:
                return skill
    raise LookupError(skill_id)


def _monstro(papel: str = "controller"):
    m = spawn_by_role(papel, NIVEL, name="Prova", rng=random.Random(0))
    m._mp = 10**6
    return m


class _Sonda:
    """A sonda instalada com um filtro explícito: só os alvos registrados contam."""

    def __init__(self):
        self.contagem = collections.Counter()
        self._lados: dict[int, str] = {}
        self._desinstalar = cob.sonda_de_status(self._registrar, self._lado)

    def _registrar(self, chave, valor):
        self.contagem[chave] += valor

    def _lado(self, alvo):
        return self._lados.get(id(alvo))

    def marcar(self, alvo, lado: str):
        self._lados[id(alvo)] = lado

    def total(self, prefixo: str) -> int:
        return sum(v for k, v in self.contagem.items() if k.startswith(prefixo))

    def desinstalar(self):
        self._desinstalar()


@pytest.fixture
def sonda():
    s = _Sonda()
    yield s
    s.desinstalar()


class TestContagemExata:
    def test_status_principal_de_skill_e_contado_chamada_a_chamada(self, sonda):
        """O caso que a sonda antiga perdia: `frozen` vindo do ramo principal."""
        teia = _skill_de_monstro("mob_teia_de_gelo")
        assert teia.effect_type == "status" and teia.effect_value == "frozen"
        congelou = sangrou = 0
        for semente in range(200):
            heroi, monstro = make_hero("Warrior", NIVEL, "naked"), _monstro()
            sonda.marcar(heroi, "heroi")
            combat.apply_skill(monstro, heroi, teia, rng=random.Random(semente), publish=None)
            congelou += "frozen" in heroi.active_effects
            sangrou += "bleed" in heroi.active_effects
        c = sonda.contagem
        assert c["status.tentativa:frozen:skill_principal:em_heroi"] == 200
        assert c["status.aplicado:frozen:skill_principal:em_heroi"] == congelou
        assert 0 < congelou < 200, (
            "a chance da carta não é 0 nem 100: a amostra mede as duas pontas"
        )
        # O secundário só rola quando o principal pegou, e vem com a origem dele.
        assert c["status.tentativa:bleed:skill_secundario:em_heroi"] == congelou
        assert c["status.aplicado:bleed:skill_secundario:em_heroi"] == sangrou

    def test_todo_desfecho_soma_a_tentativa(self, sonda):
        teia = _skill_de_monstro("mob_teia_de_gelo")
        for semente in range(100):
            heroi, monstro = make_hero("Mage", NIVEL, "naked"), _monstro()
            sonda.marcar(heroi, "heroi")
            combat.apply_skill(monstro, heroi, teia, rng=random.Random(semente), publish=None)
        desfechos = sum(sonda.total(f"status.{d}:") for d in cob.DESFECHOS_DE_STATUS)
        assert desfechos == sonda.total("status.tentativa:")

    def test_proc_de_acerto_tem_origem_propria(self, sonda):
        heroi = make_hero("Warrior", NIVEL, "naked")
        heroi.add_passive(PassiveCard("prova", "Prova", "Prova", "Common", "", "bleed_chance", 100))
        aplicados = 0
        for semente in range(40):
            alvo = _monstro("trash")
            alvo._hp = 10**9
            sonda.marcar(alvo, "monstro")
            combat.resolve_physical_attack(
                heroi, alvo, 500, rng=random.Random(semente), publish=None
            )
            aplicados += "bleed" in alvo.active_effects
        c = sonda.contagem
        assert c["status.aplicado:bleed:proc_de_acerto:em_monstro"] == aplicados
        assert aplicados > 0

    def test_imunidade_e_contada_sem_consumir_rolagem(self, sonda):
        heroi = make_hero("Warrior", NIVEL, "naked")
        heroi.resistances = {"frozen": 100}
        sonda.marcar(heroi, "heroi")
        r = random.Random(7)
        antes = r.getstate()
        assert not combat.try_apply_status(heroi, "frozen", 80, 2, r, None)
        assert r.getstate() == antes, "imunidade não rola: o RNG do turno não pode andar"
        origem = "outro_test_imunidade_e_contada_sem_consumir_rolagem"
        assert sonda.contagem[f"status.imune:frozen:{origem}:em_heroi"] == 1
        assert sonda.total("status.aplicado:") == 0

    def test_recusa_do_nucleo_e_distinta_da_rolagem(self, sonda):
        heroi = make_hero("Warrior", NIVEL, "naked")
        sonda.marcar(heroi, "heroi")
        # Chance 100 passa da rolagem; um efeito fora do catálogo o núcleo recusa.
        assert not combat.try_apply_status(heroi, "inexistente", 100, 2, random.Random(1), None)
        assert sonda.total("status.recusado_nucleo:inexistente:") == 1
        assert sonda.total("status.falhou_rolagem:") == 0

    def test_resistencia_parcial_e_chance_esperada(self, sonda):
        heroi = make_hero("Warrior", NIVEL, "naked")
        heroi.resistances = {"poison": 50}
        sonda.marcar(heroi, "heroi")
        combat.try_apply_status(heroi, "poison", 80, 3, random.Random(2), None)
        sufixo = "poison:outro_test_resistencia_parcial_e_chance_esperada:em_heroi"
        assert sonda.contagem[f"status.resistencia_parcial:{sufixo}"] == 1
        # 80% de base contra 50% de resistência: 40% efetivos, em centésimos.
        assert sonda.contagem[f"status.chance_centesimos:{sufixo}"] == 4000


class TestNaoInterferencia:
    def test_alvo_fora_do_filtro_nao_conta(self, sonda):
        heroi = make_hero("Warrior", NIVEL, "naked")
        combat.try_apply_status(heroi, "poison", 100, 3, random.Random(0), None)
        assert not sonda.contagem

    def test_a_luta_sai_identica_com_e_sem_a_sonda(self):
        """Mesma seed, mesma luta, bit a bit — e o mesmo estado final do RNG."""

        def luta(com_sonda: bool):
            heroi, monstro = make_hero("Rogue", NIVEL, "naked"), _monstro()
            s = _Sonda() if com_sonda else None
            if s:
                s.marcar(heroi, "heroi")
                s.marcar(monstro, "monstro")
            r = random.Random(11)
            try:
                res = battle.run_battle(
                    heroi,
                    [monstro],
                    lambda h, ms, t: battle.Action("attack", target=ms[0]),
                    rng=r,
                    publish=None,
                )
            finally:
                if s:
                    s.desinstalar()
            efeitos = sorted(core.instances(heroi), key=lambda i: (i.effect, i.source))
            return (
                (res.hero_won, res.turns, res.damage_dealt, res.damage_taken),
                (heroi.get_hp(), heroi.get_mp(), monstro.get_hp()),
                [(i.effect, i.source, i.duration) for i in efeitos],
                r.getstate(),
                s.total("status.tentativa:") if s else None,
            )

        sem, com = luta(False), luta(True)
        assert sem[:4] == com[:4]
        assert com[4] > 0, "a luta precisa ter tentativas de status, ou não prova nada"

    def test_desinstalar_devolve_as_funcoes_originais(self):
        antes = (combat.try_apply_status, core.apply_effect)
        s = _Sonda()
        assert (combat.try_apply_status, core.apply_effect) != antes
        s.desinstalar()
        assert (combat.try_apply_status, core.apply_effect) == antes
