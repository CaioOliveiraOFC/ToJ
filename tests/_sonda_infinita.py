"""Sonda estrutural: valida invariantes do motor em horizontes altos.

Não é um teste — é o instrumento que `test_horizonte_infinito.py` usa. Mora
separado porque a sonda tem lógica própria (o que checar, contra o quê) e
misturá-la com os `assert` transformaria cada invariante num teste solto.

Uma regra atravessa o arquivo: **a sonda nunca lê a constante que está
verificando**. Durante a construção, três checagens eram tautologias — o piso de
atributo lia `MIN_ATTRIBUTE_RATIO`, o cap de crítico recalculava o clamp do
motor, e o alvo de prova do crítico escalava com o andar até o dano virar 1 nos
dois lados. As três passavam com o motor quebrado de propósito. Os contratos
agora estão escritos aqui, em número.
"""

import math
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1]))

from src.content.enchantments import create_enchantment
from src.content.factories.archetypes import all_archetypes, spawn_by_role
from src.content.gems import GEM_TYPES, create_gem
from src.content.items import Item
from src.entities.heroes import Mage, Rogue, Warrior
from src.mechanics import combat as cmb
from src.shared import effect_core as core
from src.shared import effects as fx
from src.shared.constants import CRIT_CHANCE_CAP, HIT_CHANCE_CEIL, HIT_CHANCE_FLOOR
from src.shared.formulas import enhancement_multiplier

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}
PAPEIS = sorted(all_archetypes())
ATRIBUTOS = ("st", "mg", "ag", "df")


class Rng:
    def __init__(self, *v):
        self._v, self._i = list(v) or [1], 0

    def randrange(self, a, b):
        x = self._v[min(self._i, len(self._v) - 1)]
        self._i += 1
        return x

    def random(self):
        return 0.5

    def randint(self, a, b):
        return a

    def choice(self, s):
        return s[0]


def finito(x) -> bool:
    try:
        v = float(x)
    except (TypeError, ValueError, OverflowError):
        return False
    return not (math.isnan(v) or math.isinf(v))


class Falhas(list):
    def checar(self, cond, sistema, ponto, quem, esperado, obtido):
        if not cond:
            self.append(
                dict(sistema=sistema, ponto=ponto, quem=quem, esperado=esperado, obtido=obtido)
            )
        return cond


def heroi(classe, nivel):
    h = CLASSES[classe](f"H{nivel}")
    h.level = nivel
    h._hp, h._mp = h.base_hp, h.base_mp
    return h


def valida_stats(f: Falhas, e, ponto, quem):
    for a in ATRIBUTOS + ("hp", "mp"):
        v = e.get_stat(a) if hasattr(e, "get_stat") else getattr(e, f"base_{a}")
        f.checar(finito(v), "stats", ponto, quem, "finito", v)
        f.checar(v >= (1 if a != "mp" else 0), "stats", ponto, quem, ">=0", f"{a}={v}")
    f.checar(e.base_hp > 0, "resources", ponto, quem, "hp max > 0", e.base_hp)
    f.checar(e.base_mp >= 0, "resources", ponto, quem, "mp max >= 0", e.base_mp)
    f.checar(
        finito(e.get_avg_damage()) and e.get_avg_damage() >= 1,
        "stats",
        ponto,
        quem,
        "poder >= 1",
        e.get_avg_damage(),
    )


# O piso está escrito AQUI, e não lido de `core.MIN_ATTRIBUTE_RATIO`. Ler a
# constante que se quer verificar transforma o teste numa tautologia: zerando o
# piso no motor, a sonda zerava junto e não acusava nada. É o contrato de 10%
# que está sendo protegido, não a variável.
PISO_CONTRATADO = 0.10


def valida_piso(f: Falhas, e, ponto, quem):
    """Piso de 10% da base, com o debuff mais brutal possível."""
    f.checar(
        core.MIN_ATTRIBUTE_RATIO == PISO_CONTRATADO,
        "effects/piso",
        ponto,
        "constante",
        PISO_CONTRATADO,
        core.MIN_ATTRIBUTE_RATIO,
    )
    for a, efeito in (("st", "weakened"), ("mg", "hexed"), ("ag", "slowed"), ("df", "vulnerable")):
        base = e.get_stat(a)
        core.apply_effect(e, efeito, source_id="sonda", intensity=100000)
        v = e.get_stat(a)
        piso = max(1, int(base * PISO_CONTRATADO))
        f.checar(v == piso, "effects/piso", ponto, quem, f"{a}=={piso}", v)
        core.remove_effect(e, efeito)
        f.checar(e.get_stat(a) == base, "effects/reversao", ponto, quem, base, e.get_stat(a))


def valida_recursos(f: Falhas, e, ponto, quem):
    for efeito, sobe in (
        ("vitality", True),
        ("frailty", False),
        ("focused", True),
        ("clouded", False),
    ):
        stat = core.CATALOG[efeito].stat
        base = getattr(e, f"base_{stat}")
        core.apply_effect(e, efeito, source_id="sonda", intensity=50)
        v = getattr(e, f"base_{stat}")
        f.checar(finito(v), "resources", ponto, quem, "finito", v)
        f.checar(v > 0 if stat == "hp" else v >= 0, "resources", ponto, quem, ">0", v)
        if base > 10:
            f.checar(
                (v > base) is sobe,
                "resources",
                ponto,
                quem,
                f"{efeito} {'sobe' if sobe else 'desce'}",
                f"{base}->{v}",
            )
        core.remove_effect(e, efeito)
        f.checar(
            getattr(e, f"base_{stat}") == base,
            "resources/reversao",
            ponto,
            quem,
            base,
            getattr(e, f"base_{stat}"),
        )


def valida_chances(f: Falhas, atacante, defensor, ponto, quem):
    hc = cmb.hit_chance(atacante, defensor)
    f.checar(
        HIT_CHANCE_FLOOR <= hc <= HIT_CHANCE_CEIL,
        "hit_chance",
        ponto,
        quem,
        f"{HIT_CHANCE_FLOOR}..{HIT_CHANCE_CEIL}",
        hc,
    )
    # O cap de crítico é verificado pelo COMPORTAMENTO, e não recalculando o
    # clamp aqui: replicar a conta do motor faz a sonda concordar consigo mesma.
    # Uma rolagem logo acima do teto não pode virar crítico, por mais crítico
    # que o atacante acumule.
    # Com crítico MUITO acima do teto: só o cap pode impedir a rolagem logo
    # acima dele de virar crítico.
    guardado = dict(getattr(atacante, "active_buffs", {}))
    atacante.active_buffs["Sonda"] = {"stat": "crit_chance", "value": 10000, "duration": 9}

    def dano_com(rolagem):
        # Boneco de nível 1 SEMPRE: o cap de crítico é propriedade global do
        # motor, e um alvo do andar 500 reduz qualquer golpe ao piso de 1 —
        # com e sem crítico —, o que torna a comparação cega.
        alvo = spawn_by_role("bruiser", 1)
        alvo._hp = 10**9
        hp = alvo.get_hp()
        cmb.resolve_physical_attack(atacante, alvo, 1000, "", rng=Rng(1, rolagem))
        return hp - alvo.get_hp()

    f.checar(
        dano_com(CRIT_CHANCE_CAP + 1) < dano_com(1),
        "crit",
        ponto,
        quem,
        f"rolagem {CRIT_CHANCE_CAP + 1} nao critica",
        f"{dano_com(CRIT_CHANCE_CAP + 1)} vs {dano_com(1)}",
    )
    atacante.active_buffs.clear()
    atacante.active_buffs.update(guardado)
    dm = cmb._defense_modifier(defensor.get_df())
    f.checar(finito(dm) and 0 < dm <= 1.0, "defense", ponto, quem, "0<x<=1", dm)
    im = fx.incoming_damage_multiplier(defensor)
    f.checar(finito(im) and 0.1 <= im <= 1.0, "damage_reduction", ponto, quem, "0.1..1", im)
    for st in core.negative_effects():
        r = fx.status_resistance(defensor, st)
        c = fx.effective_status_chance(100, r)
        f.checar(
            0 <= r <= 100 and 0 <= c <= 100,
            "status_resistance",
            ponto,
            quem,
            "0..100",
            f"{st}: r={r} c={c}",
        )


def valida_golpe(f: Falhas, atacante, defensor, ponto, quem):
    for crit in (False, True):
        mods = cmb.damage_modifiers(atacante, defensor, is_critical=crit)
        for nome, lista in (
            ("flat", mods.flat),
            ("mult", mods.mult),
            ("xmult", mods.xmult),
            ("mitigation", mods.mitigation),
        ):
            for v in lista:
                f.checar(finito(v), "damage/modifiers", ponto, quem, f"{nome} finito", v)
        d = cmb._calculate_damage(
            base_power=float(cmb.basic_attack_power(atacante)),
            flat_mods=mods.flat,
            mult_mods=mods.mult,
            xmult_mods=mods.xmult,
            defense_target=defensor.get_df(),
            mitigation=mods.mitigation,
        )
        f.checar(finito(d) and d >= 1, "damage", ponto, quem, ">=1 e finito", d)


def valida_combate_real(f: Falhas, atacante, defensor, ponto, quem):
    hp = defensor.get_hp()
    r = cmb.resolve_physical_attack(
        atacante, defensor, cmb.basic_attack_power(atacante), "", rng=Rng(1, 100)
    )
    f.checar(finito(r.damage) and r.damage >= 1, "damage/real", ponto, quem, ">=1", r.damage)
    f.checar(
        defensor.get_hp() == hp - r.damage,
        "damage/hp",
        ponto,
        quem,
        hp - r.damage,
        defensor.get_hp(),
    )


def valida_efeitos(f: Falhas, e, ponto, quem):
    for efeito in ("bleed", "poison", "stun", "frozen", "sleep", "fear", "mana_burn"):
        for _ in range(9):
            core.apply_effect(e, efeito, source_id="sonda")
        d = core.CATALOG[efeito]
        s = core.stacks_of(e, efeito)
        f.checar(s == d.max_stacks, f"effects/{efeito}", ponto, quem, d.max_stacks, s)
    for efeito in ("bleed", "poison"):
        dano = core.dot_damage(e, efeito, e.base_hp)
        f.checar(finito(dano) and dano >= 0, f"dot/{efeito}", ponto, quem, ">=0", dano)
    f.checar(
        core.accuracy_penalty(e) == core.FEAR_ACCURACY_PENALTY,
        "effects/fear",
        ponto,
        quem,
        core.FEAR_ACCURACY_PENALTY,
        core.accuracy_penalty(e),
    )
    rel = core.tick_effects(e)
    f.checar(rel["skip_turn"] is True, "effects/control", ponto, quem, True, rel["skip_turn"])
    f.checar(e.base_mp >= 0, "resources", ponto, quem, "mp>=0 pos mana_burn", e.base_mp)
    for k in list(e.active_effects):
        del e.active_effects[k]


def valida_equipamento(f: Falhas, h, ponto, quem):
    espada = Item(
        item_id="s",
        name="Espada",
        description="p",
        slot="Weapon",
        damage_bonus=10,
        defense_bonus=-3,
        socket_count=3,
    )
    escudo = Item(item_id="e", name="Escudo", description="p", slot="Weapon", defense_bonus=8)
    h.equip(espada)
    h.equip(escudo)
    f.checar(
        h.equipment["Weapon1"] is espada and h.equipment["Weapon2"] is escudo,
        "duas_maos",
        ponto,
        quem,
        "duas peças",
        list(h.equipment),
    )
    for rank in (0, 1, 10, 100, 1000, 10000):
        espada.enhancement_level = rank
        m = enhancement_multiplier(rank)
        f.checar(finito(m) and m >= 1.0, "+N", ponto, quem, ">=1 finito", m)
        f.checar(
            finito(espada.damage_bonus) and espada.damage_bonus >= 10,
            "+N",
            ponto,
            quem,
            ">=base",
            espada.damage_bonus,
        )
        f.checar(espada.defense_bonus == -3, "+N/negativo", ponto, quem, -3, espada.defense_bonus)
    espada.enhancement_level = 0
    for nivel in (1, 10, 100, 1000, 10000):
        g = create_gem("Rubi", nivel)
        f.checar(finito(g.percent) and 0 < g.percent, "gemas", ponto, quem, ">0 finito", g.percent)
    espada.gems = [create_gem(t, 10000) for t in list(GEM_TYPES)[:3]]
    f.checar(
        finito(h.equipment_percent("st")),
        "sockets",
        ponto,
        quem,
        "finito",
        h.equipment_percent("st"),
    )
    valida_stats(f, h, ponto, quem)
    espada.enchant(create_enchantment("damage_percent", 10000))
    espada.enchant(create_enchantment("crit_chance", 10000))
    f.checar(
        finito(fx.combat_modifier(h, "damage_percent")),
        "encantamentos",
        ponto,
        quem,
        "finito",
        fx.combat_modifier(h, "damage_percent"),
    )
    m = spawn_by_role("bruiser", min(ponto, 6000))
    valida_chances(f, h, m, ponto, quem + "+encantado")
    valida_golpe(f, h, m, ponto, quem + "+encantado")
    for slot in ("Weapon1", "Weapon2"):
        h.unequip(slot)


def checkpoint(f: Falhas, ponto: int, completo: bool = True):
    """Valida um andar. `completo` liga as sondas caras (equipamento, combate real)."""
    for classe in CLASSES:
        quem = f"{classe}@{ponto}"
        h = heroi(classe, ponto)
        valida_stats(f, h, ponto, quem)
        valida_piso(f, h, ponto, quem)
        valida_recursos(f, h, ponto, quem)
        valida_efeitos(f, h, ponto, quem)
        if completo:
            valida_equipamento(f, heroi(classe, ponto), ponto, quem)
    papel = PAPEIS[ponto % len(PAPEIS)]
    m = spawn_by_role(papel, ponto)
    quem_m = f"{papel}@{ponto}"
    valida_stats(f, m, ponto, quem_m)
    valida_piso(f, m, ponto, quem_m)
    valida_recursos(f, m, ponto, quem_m)
    valida_efeitos(f, m, ponto, quem_m)
    h = heroi("Warrior", ponto)
    valida_chances(f, h, m, ponto, f"W->{papel}@{ponto}")
    valida_chances(f, m, h, ponto, f"{papel}->W@{ponto}")
    valida_golpe(f, h, m, ponto, f"W->{papel}@{ponto}")
    valida_golpe(f, m, h, ponto, f"{papel}->W@{ponto}")
    if completo:
        valida_combate_real(f, h, spawn_by_role(papel, ponto), ponto, f"W->{papel}@{ponto}")
        valida_combate_real(f, m, heroi("Mage", ponto), ponto, f"{papel}->M@{ponto}")
