"""O golpe passa por um funil matemático só, e o funil não muda o jogo.

Os valores abaixo foram gravados contra o motor antes da centralização. Eles não
são alvo de balanceamento: são a prova de que mover multiplicações para dentro do
pipeline não mexeu em dano nenhum. Se um deles mudar por causa de refatoração, é
bug da refatoração.

Mudança deliberada de balanceamento pode alterá-los — nesse caso o commit tem de
dizer isso, e regravá-los é parte da mudança, não um conserto.

Regravados quando o herói de medição ganhou a segunda mão: o loadout `expected`
passou a equipar `Weapon2`, e `weapon_percent` subiu junto (Guerreiro 8 -> 16).
A mudança é de CONTEÚDO, não do funil: 149 x (1,16/1,08) = 160,0, que é o valor
novo, e `monstro_contra_mago_com_egide` não se mexeu porque o atacante ali é o
monstro, que não tem equipamento.

Isto expõe uma fragilidade destes cenários: eles usam `make_hero(..., "expected")`,
então congelam o catálogo junto com a matemática, e toda mudança de loadout os
derruba sem que o pipeline tenha mudado. Uma fixture de equipamento explícita
resolveria — fica registrado, não é desta rodada.

Regravados de novo quando o medo mudou de família. `fear` deixou de multiplicar
o dano e passou a tirar pontos de ACERTO: ele não faz o golpe bater mais fraco,
faz o golpe errar mais. Como a rolagem roteirizada destes cenários sempre
acerta, `atacante_com_fear` virou igual a `basico_sem_crit` (128 -> 160) e
`dois_redutores` igual a `defensor_com_reducao` (89 -> 112).

Os dois cenários ficam, mas hoje não exercitam nada que os outros já não
exercitem — o medo é testado onde ele agora vive, em `test_efeitos_nucleo.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared.constants import XMULT_CAP  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402


class RngRoteirizado:
    """RNG determinístico: devolve a sequência dada, repetindo o último valor.

    Fixar a rolagem é o que torna o dano comparável: sem isso, "antes == depois"
    dependeria de acerto e crítico caírem iguais por sorte.
    """

    def __init__(self, *valores: int) -> None:
        self._v = list(valores) or [1]
        self._i = 0

    def randrange(self, a: int, b: int) -> int:
        valor = self._v[min(self._i, len(self._v) - 1)]
        self._i += 1
        return valor

    def random(self) -> float:
        return 0.5


ACERTA_SEM_CRIT = (1, 100)
ACERTA_COM_CRIT = (1, 1)


def _skill(nome: str):
    return next(s for s in load_skills() if s.name == nome)


def _golpe(atacante, defensor, base: int, nome: str, rolagem) -> int:
    hp = defensor.get_hp()
    cmb.resolve_physical_attack(atacante, defensor, base, nome, rng=RngRoteirizado(*rolagem))
    return hp - defensor.get_hp()


# --- os oito cenários -------------------------------------------------------


def basico_sem_crit() -> int:
    h, m = make_hero("Warrior", 8, "expected"), spawn_by_role("bruiser", 8)
    return _golpe(h, m, cmb.basic_attack_power(h), "", ACERTA_SEM_CRIT)


def basico_com_crit() -> int:
    h, m = make_hero("Warrior", 8, "expected"), spawn_by_role("bruiser", 8)
    return _golpe(h, m, cmb.basic_attack_power(h), "", ACERTA_COM_CRIT)


def skill_de_dano() -> int:
    h, m = make_hero("Mage", 8, "expected"), spawn_by_role("tank", 8)
    sk = _skill("Bola de Fogo")
    return _golpe(h, m, cmb.skill_damage_base(h, sk, m), sk.name, ACERTA_SEM_CRIT)


def skill_com_condicao() -> int:
    h, m = make_hero("Rogue", 8, "expected"), spawn_by_role("trash", 8)
    sk = next(
        s
        for s in load_skills()
        if s.bonus_condition == "target_wounded"
        and s.effect_type == "damage"
        and s.skill_class == "Rogue"
    )
    m._hp = max(1, int(m.base_hp * 0.10))
    return _golpe(h, m, cmb.skill_damage_base(h, sk, m), sk.name, ACERTA_SEM_CRIT)


def atacante_com_fear() -> int:
    h, m = make_hero("Warrior", 8, "expected"), spawn_by_role("bruiser", 8)
    h.active_effects["fear"] = {"duration": 3}
    return _golpe(h, m, cmb.basic_attack_power(h), "", ACERTA_SEM_CRIT)


def defensor_com_reducao() -> int:
    h, m = make_hero("Warrior", 8, "expected"), spawn_by_role("bruiser", 8)
    m.active_buffs["Redução de Dano"] = {
        "stat": "damage_reduction",
        "value": 30,
        "duration": 3,
    }
    return _golpe(h, m, cmb.basic_attack_power(h), "", ACERTA_SEM_CRIT)


def dois_redutores() -> int:
    h, m = make_hero("Warrior", 8, "expected"), spawn_by_role("bruiser", 8)
    h.active_effects["fear"] = {"duration": 3}
    m.active_buffs["Redução de Dano"] = {
        "stat": "damage_reduction",
        "value": 30,
        "duration": 3,
    }
    return _golpe(h, m, cmb.basic_attack_power(h), "", ACERTA_SEM_CRIT)


def monstro_contra_mago_com_egide() -> int:
    m, h = spawn_by_role("bruiser", 8), make_hero("Mage", 8, "expected")
    return _golpe(m, h, cmb.basic_attack_power(m), "", ACERTA_SEM_CRIT)


CENARIOS = {
    "basico_sem_crit": basico_sem_crit,
    "basico_com_crit": basico_com_crit,
    "skill_de_dano": skill_de_dano,
    "skill_com_condicao": skill_com_condicao,
    "atacante_com_fear": atacante_com_fear,
    "defensor_com_reducao": defensor_com_reducao,
    "dois_redutores": dois_redutores,
    "monstro_contra_mago_com_egide": monstro_contra_mago_com_egide,
}

# Gravados contra o motor pré-centralização.
GOLDEN = {
    "basico_sem_crit": 160,
    "basico_com_crit": 240,
    "skill_de_dano": 300,
    "skill_com_condicao": 476,
    "atacante_com_fear": 160,
    "defensor_com_reducao": 112,
    "dois_redutores": 112,
    "monstro_contra_mago_com_egide": 87,
}


@pytest.mark.parametrize("nome", sorted(CENARIOS))
def test_o_dano_de_cada_cenario_nao_mudou(nome):
    assert CENARIOS[nome]() == GOLDEN[nome]


def test_o_cenario_da_egide_realmente_gasta_mana():
    """Sem isto, o cenário passaria mesmo que a égide parasse de existir."""
    m, h = spawn_by_role("bruiser", 8), make_hero("Mage", 8, "expected")
    mp = h.get_mp()
    _golpe(m, h, cmb.basic_attack_power(m), "", ACERTA_SEM_CRIT)
    assert h.get_mp() < mp


# --- os quatro contratos ----------------------------------------------------


class TestLinguagemDePoder:
    """As quatro regras da linguagem. Tudo o mais é consequência delas."""

    def test_mult_e_aditivo(self):
        """+10% e +20% resolvem ×1,30, nunca ×1,10 × 1,20."""
        base = 1000.0
        somado = cmb._calculate_damage(base, mult_mods=[0.10, 0.20])
        assert somado == cmb._calculate_damage(base, mult_mods=[0.30])
        assert somado < cmb._calculate_damage(base, xmult_mods=[1.10, 1.20])

    def test_xmult_e_multiplicativo(self):
        """×1,2 e ×1,5 resolvem ×1,8, nunca ×2,7.

        Comparado com tolerância porque o produto binário de 1,2 por 1,5 é
        1,7999999999999998 e o funil trunca para inteiro — a diferença é de um
        ponto de dano, não de regra.
        """
        base = 1000.0
        assert cmb._calculate_damage(base, xmult_mods=[1.2, 1.5]) == pytest.approx(
            cmb._calculate_damage(base, xmult_mods=[1.8]), abs=1
        )
        assert cmb._calculate_damage(base, xmult_mods=[1.2, 1.5]) < cmb._calculate_damage(
            base, xmult_mods=[2.7]
        )

    def test_o_cap_limita_so_a_amplificacao(self):
        """Redutor não entra no produto capado — senão o teto mede o saldo.

        Se mitigação e amplificação dividissem o mesmo produto, uma redução
        forte deixaria um crítico absurdo passar por baixo do teto.
        """
        base = 1000.0
        no_teto = cmb._calculate_damage(base, xmult_mods=[XMULT_CAP])
        assert cmb._calculate_damage(base, xmult_mods=[XMULT_CAP * 4]) == no_teto

        com_redutor = cmb._calculate_damage(base, xmult_mods=[XMULT_CAP * 4], mitigation=[0.5])
        assert com_redutor == pytest.approx(no_teto * 0.5, abs=1)

    def test_um_golpe_passa_uma_vez_pelo_funil(self, monkeypatch):
        """Impede que a próxima fonte de poder volte a multiplicar por fora."""
        chamadas = []
        original = cmb._calculate_damage

        def espiao(*args, **kwargs):
            chamadas.append(1)
            return original(*args, **kwargs)

        monkeypatch.setattr(cmb, "_calculate_damage", espiao)
        h, m = make_hero("Warrior", 8, "expected"), spawn_by_role("bruiser", 8)
        cmb.resolve_physical_attack(
            h, m, cmb.basic_attack_power(h), "", rng=RngRoteirizado(*ACERTA_SEM_CRIT)
        )
        assert len(chamadas) == 1
