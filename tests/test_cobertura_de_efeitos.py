"""Efeito declarado no conteúdo tem de mudar o jogo, ou estar registrado como pendência.

`test_placebo.py` prova carta a carta que passivas e skills mexem no boneco. Este
arquivo faz a pergunta transversal, por FONTE: para cada par (fonte, efeito) que
o conteúdo declara — equipamento, consumível, encantamento, gema, passiva, buff
de skill do herói e do monstro, passiva de monstro, evento do mapa — monta a
mesma entidade com e sem o efeito e compara o que os CONSUMIDORES do motor
devolvem: atributos resolvidos, golpes dados e recebidos, início de turno,
resistência a status, cura de poção, golpe letal, recompensa pós-combate e lutas
completas semeadas contra dois arquétipos. Efeito que não muda nada disso é
efeito sem implementação funcional.

A diferença para `test_placebo` é o que conta como prova. Lá, "mudou o
`active_buffs`" basta para uma skill passar; aqui não: o buff precisa mudar o que
o combate lê. Foi assim que os buffs de vida e mana máxima apareceram — a skill
grava `{"stat": "hp"}`, o teste de placebo vê o dicionário mudar, e nada no motor
soma esse buff ao teto de HP do herói.

Dois desfechos, e só dois:

- funcional: a assinatura muda;
- pendência conhecida: em `PENDENCIAS`, com o tipo e o identificador do débito,
  e marcada `xfail(strict=True)`. Quando a correção chegar, o XPASS reprova e
  obriga a tirar a marca. Os tipos são dois:
  - `bug`: a mecânica existe e o caminho até ela está quebrado;
  - `design`: o conteúdo promete algo que o motor não tem, e falta decidir o que
    é.

Não existe "inerte de propósito". Um item que o jogador pode obter e que declara
um efeito tem de entregá-lo; deixá-lo inerte seria uma decisão de design, e
nenhuma foi tomada. Qualquer efeito inerte fora do registro reprova: é um placebo
novo.

Os valores são INFLADOS para isolar o canal: o teste pergunta se o efeito chega
a algum lugar, não quanto ele vale. Balanceamento é do `-m balance`.
"""

from __future__ import annotations

import json
import random
import sys
from collections.abc import Callable
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.enchantments import ENCHANT_EFFECTS, Enchantment  # noqa: E402
from src.content.factories import dungeons  # noqa: E402
from src.content.factories.archetypes import all_archetypes, spawn_by_role  # noqa: E402
from src.content.gems import GEM_TYPES, Gem  # noqa: E402
from src.content.items import Item, create_item_from_json  # noqa: E402
from src.content.passives import PassiveCard, load_passives  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.engine import encounter  # noqa: E402
from src.mechanics import battle, combat  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.shared import interactions as ix  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402

DADOS = Path(__file__).resolve().parents[1] / "src" / "data"
ITENS = json.loads((DADOS / "items.json").read_text(encoding="utf-8"))["items"]
MONSTROS = json.loads((DADOS / "monsters.json").read_text(encoding="utf-8"))["archetypes"]
SKILLS = load_skills()

NIVEL = 20
CLASSE = "Warrior"
VALOR = 100
SEEDS_GOLPE = range(24)
SEEDS_LUTA = range(3)
PAPEIS_LUTA = ("bruiser", "controller")

# Declarado, ao alcance do jogador e sem efeito. Cada entrada fica visível como
# `xfail` estrito até a correção, que transforma o XPASS em reprovação.
BUG = "bug"
DESIGN = "design"
PENDENCIAS = {
    ("evento", "altar"): (
        BUG,
        "PVE-01 / KI-007: a bênção é gravada sem `stat`, e nem `LEGACY_BUFF_STATS` a "
        "reconhece. O jogador paga 30% do HP máximo por nada.",
    ),
    ("skill-heroi", "buff:hp"): (
        BUG,
        "N10 / KI-008: o buff `{stat: hp}` vai para `active_buffs`, e o teto de HP do "
        "herói (`_scaled`) só lê `resource_percent`. 'Vida máxima +40%' não muda nada.",
    ),
    ("skill-heroi", "buff:mp"): (
        BUG,
        "N10 / KI-008: o buff `{stat: mp}` vai para `active_buffs`, e o teto de MP do "
        "herói (`_scaled`) só lê `resource_percent`. 'Mana máxima +30%' não muda nada.",
    ),
    ("skill-monstro", "buff:hp"): (
        BUG,
        "N10 / KI-008: no monstro o buff `{stat: hp}` sobe `get_stat('hp')`, que o "
        "combate não lê; teto e cura usam `base_hp`. 'Raízes Fundas' e 'Fôlego "
        "Emprestado' são inertes.",
    ),
    ("equipamento", "defense"): (
        BUG,
        "N11 / KI-009: `equipment_percent` lê `defense_bonus` para `df` e o `elif` "
        "nunca chega ao `effect_type: defense`. O Amuleto de Argila mostra 'defense "
        "+3' e entrega só o `defense_bonus` 1.",
    ),
    ("equipamento", "true_damage"): (
        DESIGN,
        "N4 / KI-013: a Espada do Universo (lendária, cai como drop) mostra "
        "'true_damage +20', e não existe mecânica de dano verdadeiro. Falta decidir "
        "o que o efeito é.",
    ),
    ("equipamento", "armageddon"): (
        DESIGN,
        "N4 / KI-013: o Cajado da Galáxia (lendário, cai como drop) mostra "
        "'armageddon +50', e não existe mecânica de armageddon. Falta decidir o que "
        "o efeito é.",
    ),
}


# --------------------------------------------------------------------------- #
# A assinatura: o que os consumidores do motor devolvem                       #
# --------------------------------------------------------------------------- #

Montador = Callable[[], object]


def _monstro(papel: str, semente: int = 0):
    """Um monstro determinístico. `build_encounter` sortearia o deck pelo
    `random` global, e as duas metades do A/B veriam decks diferentes."""
    return spawn_by_role(papel, NIVEL, name="Prova", rng=random.Random(semente))


def _imortal(papel: str = "trash"):
    m = _monstro(papel)
    m._hp = 10**9
    return m


def _so_ataca(_heroi, monstros, _turno):
    return battle.Action("attack", target=battle.pick_default_target(monstros))


def _perfil(e) -> tuple:
    return (
        e.base_hp,
        e.base_mp,
        e.get_hp(),
        e.get_mp(),
        e.get_st(),
        e.get_ag(),
        e.get_mg(),
        e.get_df(),
    )


def _funil(e) -> tuple:
    """Os baldes de dano e as chances de acerto, nos dois sentidos."""
    alvo = _imortal()
    mods = [combat.damage_modifiers(e, alvo, is_critical=c) for c in (False, True)]
    return (
        tuple((tuple(m.mult), tuple(m.xmult), m.mitigation) for m in mods),
        combat.hit_chance(e, alvo, -30),
        combat.hit_chance(_imortal("skirmisher"), e, -30),
    )


def _golpes_dados(montar: Montador) -> tuple:
    out = []
    for s in SEEDS_GOLPE:
        e, alvo = montar(), _imortal()
        hp_alvo, hp_e = alvo.get_hp(), e.get_hp()
        combat.resolve_physical_attack(e, alvo, 1000, rng=random.Random(s), publish=None)
        out.append((hp_alvo - alvo.get_hp(), tuple(sorted(alvo.active_effects)), e.get_hp() - hp_e))
    return tuple(out)


def _golpes_recebidos(montar: Montador) -> tuple:
    out = []
    for s in SEEDS_GOLPE:
        e, atacante = montar(), _imortal("bruiser")
        hp = e.get_hp()
        combat.resolve_physical_attack(atacante, e, 300, rng=random.Random(s), publish=None)
        out.append(hp - e.get_hp())
    return tuple(out)


def _golpe_letal(montar: Montador) -> bool:
    e = montar()
    e._hp = 1
    combat.resolve_physical_attack(_imortal(), e, 10**6, rng=random.Random(0), publish=None)
    return e.get_hp() > 0


def _inicio_de_turno(montar: Montador) -> tuple:
    e = montar()
    e._mp = 0
    combat.process_turn_start_effects(e, rng=random.Random(0), publish=None)
    return (e.get_hp(), e.get_mp())


def _resistencia(montar: Montador) -> int:
    pegou = 0
    for s in SEEDS_GOLPE:
        pegou += combat.try_apply_status(montar(), "poison", 100, 3, random.Random(s), None)
    return pegou


def _pocao(montar: Montador):
    e = montar()
    if not callable(getattr(e, "use_potion", None)):
        return None
    e._hp = 1
    e.use_potion(SimpleNamespace(effect_type="max_hp", effect_value=25, name="Prova"))
    return e.get_hp()


def _recompensa(montar: Montador):
    """O caminho da derrota: paga XP e moedas de piedade sem rolar loot nem nível,
    que sorteiam pelo `random` global e não pertencem a esta pergunta."""
    e = montar()
    if not callable(getattr(e, "earn_coins", None)):
        return None
    e.set_isalive(False)
    xp, _venceu, _item, _msgs, moedas, _niveis = encounter.process_post_battle(
        e, [_monstro("trash")], dungeon_level=NIVEL
    )
    return (xp, moedas)


def _lutas(montar: Montador, papel_do_sujeito: str) -> tuple:
    """Lutas inteiras, semeadas, só com ataque básico: a decisão fica constante
    para que a única diferença entre A e B seja o efeito."""
    out = []
    for papel in PAPEIS_LUTA:
        for s in SEEDS_LUTA:
            if papel_do_sujeito == "heroi":
                heroi, monstro = montar(), _monstro(papel, s)
            else:
                heroi, monstro = make_hero(CLASSE, NIVEL, "naked"), montar()
            res = battle.run_battle(heroi, [monstro], _so_ataca, rng=random.Random(s), publish=None)
            out.append(
                (
                    res.hero_won,
                    res.turns,
                    res.damage_dealt,
                    res.damage_taken,
                    heroi.get_hp(),
                    monstro.get_hp(),
                )
            )
    return tuple(out)


def assinatura(montar: Montador, papel: str = "heroi") -> dict:
    """Tudo que os consumidores do motor devolvem para esta entidade.

    Cada sonda monta uma entidade NOVA: nenhuma herda o estado que a anterior
    deixou, e a ordem das sondas não muda o resultado.
    """
    return {
        "perfil": _perfil(montar()),
        "funil": _funil(montar()),
        "golpes_dados": _golpes_dados(montar),
        "golpes_recebidos": _golpes_recebidos(montar),
        "golpe_letal": _golpe_letal(montar),
        "inicio_de_turno": _inicio_de_turno(montar),
        "resistencia": _resistencia(montar),
        "pocao": _pocao(montar),
        "recompensa": _recompensa(montar),
        "lutas": _lutas(montar, papel),
    }


def _sondas_que_mudaram(montar_a: Montador, montar_b: Montador, papel: str = "heroi"):
    a, b = assinatura(montar_a, papel), assinatura(montar_b, papel)
    return sorted(k for k in a if a[k] != b[k])


# --------------------------------------------------------------------------- #
# Os casos: um por par (fonte, efeito) que o conteúdo declara                  #
# --------------------------------------------------------------------------- #


def _heroi(classe: str = CLASSE):
    """Herói no meio da luta: ferido e com mana pela metade, para que cura,
    roubo de vida e regeneração tenham espaço para aparecer."""
    h = make_hero(classe, NIVEL, "naked")
    h._hp = max(1, h.base_hp // 2)
    h._mp = max(0, h.base_mp // 2)
    return h


def _peca_neutra(**extra) -> Item:
    return Item(
        item_id="prova",
        name="Peça de Prova",
        description="",
        slot="Ring",
        price=1,
        **extra,
    )


def _caso_passiva(efeito):
    def montar(com: bool):
        h = _heroi()
        if com:
            h.add_passive(PassiveCard("prova", "Prova", "Prova", "Common", "", efeito, VALOR))
        return h

    return montar


def _vestir(h, peca):
    """Equipa e CONFERE. Uma peça recusada (classe, mãos) deixaria as duas
    metades nuas, e o teste mediria o vazio como se fosse placebo."""
    h.equip(peca)
    assert any(p is peca for p in h.equipment.values()), f"{peca.name} não entrou no corpo"
    return h


def _caso_equipamento(efeito):
    # A primeira peça do catálogo que declara o efeito com valor positivo. As
    # duas metades são a MESMA peça; só o efeito muda.
    dados = next(
        i
        for i in sorted(ITENS, key=lambda i: i["name"])
        if not i.get("consumable")
        and i.get("effect_type") == efeito
        and (i.get("effect_value") or 0) > 0
    )
    classe = next(iter(dados.get("classes") or [CLASSE]))

    def montar(com: bool):
        variante = dict(dados, effect_type=efeito if com else None, effect_value=VALOR)
        return _vestir(_heroi(classe), create_item_from_json(variante))

    return montar


def _caso_consumivel(efeito):
    dados = next(
        i
        for i in sorted(ITENS, key=lambda i: i["name"])
        if i.get("consumable") and i.get("effect_type") == efeito
    )

    def montar(com: bool):
        h = _heroi()
        if com:
            h.use_potion(create_item_from_json(dict(dados, effect_value=VALOR)))
        return h

    return montar


def _caso_encanto(efeito):
    def montar(com: bool):
        peca = _peca_neutra(enchantments=[Enchantment(efeito, VALOR)] if com else [])
        return _vestir(_heroi(), peca)

    return montar


def _caso_gema(tipo):
    def montar(com: bool):
        peca = _peca_neutra(socket_count=1)
        if com:
            peca.socket(Gem(tipo, 10))
        return _vestir(_heroi(), peca)

    return montar


def _lancar(entidade, skill):
    """Lança a carta pelo caminho do jogo e devolve a mana gasta: o custo não é
    o efeito, e entraria na assinatura como uma diferença falsa."""
    mp = entidade._mp
    entidade._mp = 10**6
    combat.apply_skill(entidade, _imortal(), skill, rng=random.Random(0), publish=None)
    # Carta recusada (requisito, recarga) não grava nada, e o teste mediria a
    # recusa como se fosse placebo.
    assert str(skill.name) in entidade.active_buffs, f"{skill.id} não foi lançada"
    entidade._mp = mp
    entidade.skill_cooldowns = {}


def _armar(h, skill):
    """Põe nas mãos o que a carta exige, nas DUAS metades do A/B: a arma é
    condição do lançamento, não o efeito medido."""
    req = getattr(skill, "requires", None)
    if req is None:
        return h
    tipo = req.hand_type or "sword"
    arma = Item(
        item_id=f"prova_{tipo}",
        name=f"Arma de Prova ({tipo})",
        description="",
        slot="Weapon",
        damage_bonus=1,
        price=1,
        hand_type=tipo,
    )
    h.equip(arma, "Weapon1")
    if req.two_weapons:
        h.equip(arma.instance(), "Weapon2")
    return h


def _do_canal(skill, canal) -> bool:
    tipo, stat = canal
    return skill.effect_type == tipo and (tipo != "buff" or str(skill.effect_stat) == stat)


def _caso_skill_heroi(canal):
    # Uma carta por canal: o leitor é do atributo, não do nome da carta.
    skill = min((s for s in SKILLS if _do_canal(s, canal)), key=lambda s: s.id)
    classe = skill.skill_class if skill.skill_class in ("Warrior", "Mage", "Rogue") else CLASSE

    def montar(com: bool):
        h = _armar(_heroi(classe), skill)
        if com:
            _lancar(h, skill)
        return h

    return montar


def _kit_de_monstro():
    return [(papel, s) for papel, a in sorted(all_archetypes().items()) for s in a.skills]


def _caso_skill_monstro(canal):
    papel, skill = min(
        ((p, s) for p, s in _kit_de_monstro() if _do_canal(s, canal)),
        key=lambda ps: ps[1].id,
    )

    def montar(com: bool):
        m = _monstro(papel)
        if com:
            _lancar(m, skill)
        return m

    return montar


def _caso_passiva_monstro(papel, efeito):
    def montar(com: bool):
        m = _monstro(papel)
        m.passive_bonuses = {efeito: float(VALOR)} if com else {}
        return m

    return montar


def _caso_evento(nome):
    aplicar = {
        "altar": dungeons.apply_altar_blessing,
        "fonte": dungeons.apply_fountain_heal,
    }[nome]

    def montar(com: bool):
        h = _heroi()
        if com:
            aplicar(h)
        return h

    return montar


def _canais_de_skill(skills) -> list[tuple[str, str]]:
    canais = set()
    for s in skills:
        if s.effect_type == "buff":
            canais.add(("buff", str(s.effect_stat)))
        elif s.effect_type == "damage_reduction":
            canais.add(("damage_reduction", ""))
    return sorted(canais)


def _nome_do_canal(canal) -> str:
    tipo, stat = canal
    return f"{tipo}:{stat}" if stat else tipo


def _casos():
    """Gerados do CONTEÚDO, nunca listados à mão: um efeito novo no JSON entra
    aqui sozinho e precisa provar que funciona."""
    casos = []
    for efeito in sorted({p.effect_type for p in load_passives()}):
        casos.append(("passiva", efeito, _caso_passiva(efeito), "heroi"))
    equip = {i["effect_type"] for i in ITENS if i.get("effect_type") and not i.get("consumable")}
    for efeito in sorted(equip):
        casos.append(("equipamento", efeito, _caso_equipamento(efeito), "heroi"))
    consum = {i["effect_type"] for i in ITENS if i.get("effect_type") and i.get("consumable")}
    for efeito in sorted(consum):
        casos.append(("consumivel", efeito, _caso_consumivel(efeito), "heroi"))
    for efeito in sorted(ENCHANT_EFFECTS):
        casos.append(("encanto", efeito, _caso_encanto(efeito), "heroi"))
    for tipo in sorted(GEM_TYPES):
        casos.append(("gema", tipo, _caso_gema(tipo), "heroi"))
    for canal in _canais_de_skill(SKILLS):
        casos.append(("skill-heroi", _nome_do_canal(canal), _caso_skill_heroi(canal), "heroi"))
    for canal in _canais_de_skill([s for _p, s in _kit_de_monstro()]):
        casos.append(
            ("skill-monstro", _nome_do_canal(canal), _caso_skill_monstro(canal), "monstro")
        )
    for papel, dados in sorted(MONSTROS.items()):
        for efeito in sorted(dados.get("passives") or {}):
            casos.append(
                (
                    "passiva-monstro",
                    f"{papel}:{efeito}",
                    _caso_passiva_monstro(papel, efeito),
                    "monstro",
                )
            )
    for nome in ("altar", "fonte"):
        casos.append(("evento", nome, _caso_evento(nome), "heroi"))
    return casos


CASOS = _casos()


def _marcas(fonte, efeito):
    chave = (fonte, efeito)
    if chave in PENDENCIAS:
        tipo, motivo = PENDENCIAS[chave]
        return [pytest.mark.xfail(strict=True, reason=f"[{tipo}] {motivo}")]
    return []


class TestEfeitoDeclaradoMudaOJogo:
    @pytest.mark.parametrize(
        "fonte,efeito,caso,papel",
        [pytest.param(f, e, c, p, id=f"{f}:{e}", marks=_marcas(f, e)) for f, e, c, p in CASOS],
    )
    def test_o_efeito_chega_a_um_consumidor(self, fonte, efeito, caso, papel):
        mudou = _sondas_que_mudaram(lambda: caso(False), lambda: caso(True), papel)
        assert mudou, (
            f"{fonte} declara '{efeito}' e nenhum consumidor do motor muda: "
            "efeito sem implementação funcional"
        )

    def test_o_registro_aponta_para_conteudo_que_existe(self):
        """Uma entrada de registro sem caso é lixo: esconde o próximo efeito
        com o mesmo nome."""
        existentes = {(f, e) for f, e, _c, _p in CASOS}
        assert set(PENDENCIAS) <= existentes
        assert {tipo for tipo, _motivo in PENDENCIAS.values()} <= {BUG, DESIGN}

    def test_a_assinatura_e_deterministica(self):
        """Sem isto, A ≠ B poderia ser só ruído, e todo placebo passaria."""
        heroi = _caso_passiva("strength")
        assert assinatura(lambda: heroi(False)) == assinatura(lambda: heroi(False))
        monstro = _caso_skill_monstro(("buff", "st"))
        assert assinatura(lambda: monstro(True), "monstro") == assinatura(
            lambda: monstro(True), "monstro"
        )


# --------------------------------------------------------------------------- #
# Fontes do catálogo de efeitos e alcance das leis (PVE-02)                    #
# --------------------------------------------------------------------------- #

# O que cada lei precisa no alvo (ou no atacante) para disparar. Explícito, e
# conferido contra o catálogo: uma lei nova sem linha aqui reprova.
EXIGE: dict[str, frozenset[str]] = {
    "empowered_weakened": frozenset({"empowered", "weakened"}),
    "arcane_surge_hexed": frozenset({"arcane_surge", "hexed"}),
    "quickened_slowed": frozenset({"quickened", "slowed"}),
    "fortified_vulnerable": frozenset({"fortified", "vulnerable"}),
    "vitality_frailty": frozenset({"vitality", "frailty"}),
    "focused_clouded": frozenset({"focused", "clouded"}),
    "precision_fear": frozenset({"precision", "fear"}),
    "sleep_damage": frozenset({"sleep"}),
    "quebra_gelida": frozenset({"frozen"}),
    "emboscada": frozenset({"invisible"}),
    "ferida_aberta": frozenset({"bleed", "vulnerable"}),
    "toxicidade": frozenset({"poison", "frailty"}),
    "panico": frozenset({"fear", "bleed"}),
    "hemorragia_fria": frozenset({"frozen", "bleed"}),
    "ferida_septica": frozenset({"bleed", "poison"}),
    "colapso_mental": frozenset({"mana_burn", "clouded"}),
}

# Os sete efeitos positivos dos pares opostos. O núcleo os implementa e as leis
# de par dependem deles, mas nenhuma carta, item, passiva ou monstro os aplica.
# A passiva `precision` é MODIFICADOR de acerto, não o efeito do catálogo.
# Pendência sem decisão (PVE-02): o conjunto fica travado para que uma mudança
# nele seja notada, e não porque alguém tenha decidido que deve ficar assim.
SEM_FONTE_PVE02 = frozenset(
    {"empowered", "arcane_surge", "quickened", "fortified", "vitality", "focused", "precision"}
)

LEIS_DE_PAR = frozenset(
    {
        "empowered_weakened",
        "arcane_surge_hexed",
        "quickened_slowed",
        "fortified_vulnerable",
        "vitality_frailty",
        "focused_clouded",
        "precision_fear",
    }
)


def _efeitos_com_fonte() -> set[str]:
    """Os efeitos do catálogo que algum conteúdo consegue colocar numa entidade."""
    fontes = set()
    for s in list(SKILLS) + [s for _p, s in _kit_de_monstro()]:
        fontes.update(ix.applicable_effects(s))
    # Procs de acerto: chegam pelo modificador `<efeito>_chance`, que o
    # conteúdo declara em passiva, encanto ou equipamento.
    chances = {p.effect_type for p in load_passives()} | set(ENCHANT_EFFECTS)
    chances |= {
        combat.ONHIT_PROCS[i["effect_type"]]
        for i in ITENS
        if not i.get("consumable") and i.get("effect_type") in combat.ONHIT_PROCS
    }
    fontes.update(e for e, mod in combat.ONHIT_PROCS.items() if mod in chances)
    return fontes


class TestFontesDoCatalogo:
    def test_os_efeitos_sem_fonte_sao_os_sete_positivos_do_pve02(self):
        sem_fonte = set(core.CATALOG) - _efeitos_com_fonte()
        assert sem_fonte == SEM_FONTE_PVE02, (
            f"sem fonte: {sorted(sem_fonte)}. Um efeito novo sem conteúdo que o aplique "
            "é mecânica morta; um efeito do PVE-02 que ganhou fonte sai do registro."
        )

    def test_a_tabela_de_exigencias_cobre_todas_as_leis(self):
        assert set(EXIGE) == set(ix.CATALOG)
        for lei, exigidos in EXIGE.items():
            assert exigidos <= set(core.CATALOG), f"{lei} exige efeito fora do catálogo"

    def test_as_leis_inalcancaveis_sao_as_sete_de_par(self):
        """Condição NECESSÁRIA: cada efeito exigido tem fonte. Se eles chegam a
        coexistir no mesmo alvo numa run é medição, e fica com a instrumentação."""
        com_fonte = _efeitos_com_fonte()
        inalcancaveis = {lei for lei, exigidos in EXIGE.items() if not exigidos <= com_fonte}
        assert inalcancaveis == LEIS_DE_PAR
