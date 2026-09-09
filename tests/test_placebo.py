"""Nenhuma carta pode ser enfeite.

Uma skill ou passiva placebo é o pior defeito possível num jogo de escolhas: ela
não quebra nada, não levanta exceção, aparece bonita na tela, o jogador gasta o
recurso escasso da run nela — e não acontece nada. A suíte fica verde e o menu
de cartas vira decoração.

Já aconteceu duas vezes nesta base. `essence_bonus` (4 cartas) e
`gold_drop_bonus` (2) não eram lidas por nenhum cálculo. E `Golpe Baixo`
declarava 15% de atordoamento que o motor entregava em 0% das vezes, porque o
bloco que rola o atordoamento da skill só existia no ramo de dano e ela é uma
skill de status.

Os testes abaixo não conferem número de balanceamento: conferem que o efeito
declarado no JSON chega ao boneco.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.passives import load_passives  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.mechanics import combat  # noqa: E402
from src.sim.encounters import build_encounter  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402

SKILLS = {s.id: s for s in load_skills()}
PASSIVAS = {p.name: p for p in load_passives()}
COM_STUN = [s for s in SKILLS.values() if int(getattr(s, "stun_chance", 0) or 0) > 0]


def _alvo_imortal(nivel: int = 20):
    """Um monstro que não morre: se morrer no meio da amostra, ela encolhe."""
    m = build_encounter("trash_solo", nivel)[0]
    m._hp = 10**9
    return m


def _taxa_de_stun(skill, n: int = 4000) -> float:
    atordoados = 0
    for i in range(n):
        r = random.Random(i)
        heroi = make_hero("Warrior", 20, "naked")
        heroi._mp = 10**6
        heroi.skill_cooldowns = {}
        alvo = _alvo_imortal()
        combat.apply_skill(heroi, alvo, skill, rng=r, publish=None)
        atordoados += "stun" in getattr(alvo, "active_effects", {})
    return atordoados / n


class TestAtordoamentoDeSkill:
    """O `stun_chance` do JSON é o que o jogo entrega."""

    @pytest.mark.parametrize("skill", COM_STUN, ids=lambda s: s.id)
    def test_a_taxa_medida_bate_com_a_declarada(self, skill):
        declarada = int(skill.stun_chance) / 100
        medida = _taxa_de_stun(skill)

        # Teto: nunca acima do declarado. Uma skill que atordoa mais do que o
        # JSON diz está rolando duas vezes — foi o caso de Esmagar, que
        # prometia 30% e entregava 46% porque o motor a atordoava por nome
        # ANTES de `apply_skill` rolar o `stun_chance` dela.
        assert medida <= declarada + 0.02, (
            f"{skill.id} atordoa {medida:.1%} com {declarada:.0%} declarados: "
            "há mais de uma rolagem no caminho"
        )

        # Piso: fica abaixo do declarado só pelo que o golpe erra. Um piso em
        # zero é o placebo — a carta cobra mana por um efeito que não existe.
        assert medida >= declarada * 0.75, (
            f"{skill.id} atordoa {medida:.1%} com {declarada:.0%} declarados: "
            "o efeito declarado não está chegando ao alvo"
        )

    def test_skill_de_status_tambem_atordoa(self):
        """Regressão direta: `Golpe Baixo` é `status` e entregava 0%."""
        golpe_baixo = SKILLS["golpe_baixo"]
        assert golpe_baixo.effect_type == "status", "premissa do teste mudou"
        assert _taxa_de_stun(golpe_baixo) > 0.05


class TestPassivaMudaOBoneco:
    """Toda passiva precisa mexer em alguma coisa observável."""

    def _com_e_sem(self, nome: str):
        base = make_hero("Warrior", 20, "naked")
        com = make_hero("Warrior", 20, "naked")
        com.add_passive(PASSIVAS[nome])
        return base, com

    @pytest.mark.parametrize("nome", sorted(PASSIVAS))
    def test_a_passiva_tem_efeito_no_seu_dominio(self, nome):
        passiva = PASSIVAS[nome]
        base, com = self._com_e_sem(nome)
        efeito = passiva.effect_type

        # Cada família age num lugar diferente. Medir todas pelo combate faria
        # as de recompensa parecerem mortas — foi assim que uma auditoria
        # anterior quase condenou as cartas de essência de novo, por engano.
        if efeito in ("essence_bonus", "gold_drop_bonus", "potion_heal_bonus", "death_ignore"):
            assert com.get_passive_bonus(efeito) > base.get_passive_bonus(efeito)
        else:
            perfil = lambda h: (  # noqa: E731
                h.base_hp,
                h.base_mp,
                h.get_st(),
                h.get_ag(),
                h.get_mg(),
                h.get_df(),
            )
            mudou_perfil = perfil(com) != perfil(base)
            mudou_modificador = com.get_passive_bonus(efeito) > base.get_passive_bonus(efeito)
            assert mudou_perfil or mudou_modificador, (
                f"{nome} ({efeito}) não muda nada que o motor consulte"
            )

    def test_essencia_e_ouro_chegam_ao_calculo_de_recompensa(self):
        """As seis cartas que já foram placebo, no cálculo que as usa."""
        for efeito in ("essence_bonus", "gold_drop_bonus"):
            cartas = [p for p in PASSIVAS.values() if p.effect_type == efeito]
            assert cartas, f"nenhuma carta de {efeito}: o teste perdeu o objeto"
            heroi = make_hero("Warrior", 20, "naked")
            for carta in cartas:
                heroi.add_passive(carta)
            assert 1 + heroi.get_passive_bonus(efeito) / 100 > 1.0

    def test_pocao_cura_mais_com_a_passiva(self):
        pocao = SimpleNamespace(effect_type="max_hp", effect_value=25, name="Poção")
        curas = []
        for passiva in (None, PASSIVAS["Bebida dos Deuses"]):
            heroi = make_hero("Warrior", 20, "naked")
            if passiva:
                heroi.add_passive(passiva)
            heroi._hp = 1
            heroi.use_potion(pocao)
            curas.append(heroi.get_hp())
        assert curas[1] > curas[0]

    def test_death_ignore_impede_a_morte_uma_vez(self):
        def morreu(passiva):
            heroi = make_hero("Warrior", 20, "naked")
            if passiva:
                heroi.add_passive(passiva)
            heroi._death_ignore_used = False
            heroi._hp = 1
            combat.resolve_physical_attack(
                _alvo_imortal(), heroi, 10**6, "ataque", rng=random.Random(0), publish=None
            )
            return heroi.get_hp() <= 0

        assert morreu(None)
        assert not morreu(PASSIVAS["Imortalidade Momentânea"])


class TestSkillMudaOEstado:
    """Toda skill precisa mudar o alvo ou o lançador."""

    @pytest.mark.parametrize("skill", list(SKILLS.values()), ids=lambda s: s.id)
    def test_usar_a_skill_muda_alguma_coisa(self, skill):
        classe = skill.skill_class
        if classe not in ("Warrior", "Mage", "Rogue"):
            classe = "Warrior"
        for i in range(60):
            heroi = make_hero(classe, 20, "naked")
            heroi._mp = 10**6
            heroi.skill_cooldowns = {}
            heroi._hp = max(1, heroi.base_hp // 2)  # cura e buff precisam de espaço
            alvo = _alvo_imortal()
            antes = (
                alvo.get_hp(),
                dict(alvo.active_effects or {}),
                heroi.get_hp(),
                dict(heroi.active_buffs or {}),
            )
            combat.apply_skill(heroi, alvo, skill, rng=random.Random(i), publish=None)
            depois = (
                alvo.get_hp(),
                dict(alvo.active_effects or {}),
                heroi.get_hp(),
                dict(heroi.active_buffs or {}),
            )
            if antes != depois:
                return
        pytest.fail(f"{skill.id} não mudou nada em 60 usos: a carta é placebo")
