"""Auditoria de ACESSIBILIDADE das interações. Não faz parte do jogo.

O motor conhece 16 leis. Isso não quer dizer que o jogador as encontre: uma lei
cuja peça não existe no catálogo é uma regra que nunca acontece, e nada no
código acusa — os testes do motor passam, porque o motor está certo. O que falta
é CONTEÚDO, e conteúdo se mede contando fontes.

A ferramenta responde três perguntas, nesta ordem:

1. **Quem tem cada peça?** Skills por classe e por arquétipo, passivas com proc
   ao acertar, itens com efeito on-hit. Encantamento entra na conta se algum dia
   o jogo gerar algum — hoje não gera, e a ferramenta diz isso.

2. **Quem monta a interação inteira sozinho?** No 1x1 o monstro precisa colocar
   as DUAS peças com as próprias cartas: não existe aliado para preparar a
   jogada. O herói pode misturar fontes — skill com passiva, skill com item.

3. **Dispara de verdade?** Um smoke determinístico por interação, usando cartas
   e passivas reais do catálogo. Contar fontes diz que o caminho existe;
   percorrê-lo diz que ele chega.

Uso: `python tools/audit_interactions.py`
"""

from __future__ import annotations

import collections
import json
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.passives import load_passives  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.entities.heroes import Player  # noqa: E402
from src.mechanics import combat, monster_ai  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402

CLASSES = ("Warrior", "Mage", "Rogue")
ROLES = (
    "trash",
    "bruiser",
    "tank",
    "glass_cannon",
    "skirmisher",
    "controller",
    "support",
    "elite",
    "boss",
)

# As peças que cada lei nova precisa NO ALVO. Quebra Gélida e Hemorragia Fria
# pedem também um crítico, que é universal — todo mundo crita, e ainda há 4
# passivas e 8 itens de chance de crítico. Emboscada pede a peça no PRÓPRIO
# atacante, e por isso é a única cuja fonte não é o alvo.
PECAS = {
    "Quebra Gélida": ("frozen",),
    "Emboscada": ("invisible",),
    "Ferida Aberta": ("vulnerable", "bleed"),
    "Toxicidade": ("frailty", "poison"),
    "Pânico": ("bleed", "fear"),
    "Hemorragia Fria": ("frozen", "bleed"),
    "Ferida Séptica": ("bleed", "poison"),
    "Colapso Mental": ("clouded", "mana_burn"),
}


def _pecas_da_carta(skill) -> list[str]:
    """O que esta carta consegue colocar no tabuleiro."""
    achadas = []
    if str(getattr(skill, "effect_type", "")) == "status":
        nome = str(getattr(skill, "effect_value", "") or "")
        if core.definition(nome):
            achadas.append(nome)
    secundario = getattr(skill, "secondary", None)
    nome = str(getattr(secundario, "effect", "") or "")
    if core.definition(nome):
        achadas.append(nome)
    return achadas


def fontes_do_heroi() -> dict:
    """Peça -> classe -> ids de carta. Neutral conta para as três classes."""
    mapa: dict = collections.defaultdict(lambda: collections.defaultdict(set))
    for s in load_skills():
        if s.skill_class == "Monster":
            continue
        classes = CLASSES if s.skill_class == "Neutral" else (s.skill_class,)
        for peca in _pecas_da_carta(s):
            for c in classes:
                mapa[peca][c].add(s.id)
    return mapa


def fontes_universais() -> dict:
    """Peça -> fontes que QUALQUER classe alcança: passiva e equipamento."""
    mapa = collections.defaultdict(list)
    por_modificador = {v: k for k, v in combat.ONHIT_PROCS.items()}
    for p in load_passives():
        if p.effect_type in por_modificador:
            mapa[por_modificador[p.effect_type]].append(("passiva", p.name))
    for item in get_all_items().values():
        efeito = getattr(item, "effect_type", None)
        if efeito in Player.EQUIP_ONHIT_EFFECTS:
            mapa[efeito].append(("item", item.name))
    return mapa


def fontes_do_monstro() -> dict:
    """Peça -> arquétipo -> nomes de carta, lido do JSON de monstros."""
    dados = json.loads((Path(__file__).resolve().parents[1] / "src/data/monsters.json").read_text())
    mapa: dict = collections.defaultdict(lambda: collections.defaultdict(set))

    class Carta:
        def __init__(self, raw):
            self.effect_type = raw.get("effect_type", "")
            self.effect_value = raw.get("effect_value", "")
            sec = raw.get("secondary")
            self.secondary = type("S", (), {"effect": sec["effect"]})() if sec else None

    for role, arquetipo in dados["archetypes"].items():
        for raw in arquetipo.get("skills", []):
            for peca in _pecas_da_carta(Carta(raw)):
                mapa[peca][role].add(raw["name"])
    return mapa


def relatorio_estatico() -> None:
    heroi, universal, monstro = fontes_do_heroi(), fontes_universais(), fontes_do_monstro()

    print("=== FONTES POR PEÇA ===")
    print(f"{'peça':12}{'Warrior':>9}{'Mage':>7}{'Rogue':>7}{'passiva/item':>14}   monstros")
    largura = {"Warrior": 9, "Mage": 7, "Rogue": 7}
    for peca in sorted({p for pecas in PECAS.values() for p in pecas}):
        roles = ", ".join(sorted(monstro[peca])) or "nenhum"
        colunas = "".join(f"{len(heroi[peca].get(c, ())):>{largura[c]}}" for c in CLASSES)
        print(f"{peca:12}{colunas}{len(universal.get(peca, [])):>14}   {roles}")

    largura = {"Warrior": 9, "Mage": 7, "Rogue": 7}
    print("\n=== QUEM MONTA A INTERAÇÃO INTEIRA ===")
    print(f"{'interação':17}{'Warrior':>9}{'Mage':>7}{'Rogue':>7}   arquétipos que montam sozinhos")
    for nome, pecas in PECAS.items():
        linha = f"{nome:17}"
        for c in CLASSES:
            ok = all(heroi[p].get(c) or universal.get(p) for p in pecas)
            linha += f"{('sim' if ok else 'NÃO'):>{largura[c]}}"
        sozinhos = [r for r in ROLES if all(monstro[p].get(r) for p in pecas)]
        print(linha + f"   {', '.join(sozinhos) or 'NENHUM'}")

    print("\n=== ENCANTAMENTOS ===")
    encantados = [i for i in get_all_items().values() if getattr(i, "enchantments", None)]
    print(
        f"itens que nascem encantados: {len(encantados)} — nenhum código do jogo chama "
        "`create_enchantment`, então encantamento ainda não é fonte de peça nenhuma."
    )


# --------------------------------------------------------------------------
# Smoke: o caminho existe no papel; aqui ele é percorrido.


class _Certeiro(random.Random):
    """Acerta e crita. A rolagem é a do jogo — aqui ela é fixada, não inventada."""

    def randrange(self, *args, **kwargs):
        return 1


def _heroi(classe, passivas=()):
    catalogo = {p.name: p for p in load_passives()}
    h = make_hero(classe, 20, "naked")
    h._mp = 10**6
    for nome in passivas:
        h.add_passive(catalogo[nome])
    return h


def _alvo():
    m = spawn_by_role("tank", 20)
    m.base_hp = m._hp = 10**6
    m.base_mp = m._mp = 500
    return m


def relatorio_smoke() -> None:
    skills = {s.id: s for s in load_skills()}
    vistos: list[str] = []

    def publicar(_topico, evento):
        if evento.payload.get("kind") == "interaction":
            vistos.append(evento.payload["label"])

    def lancar(h, m, sid):
        combat.apply_skill(h, m, skills[sid], rng=_Certeiro(0), publish=publicar)

    def caso(nome, fn):
        vistos.clear()
        fn()
        print(f"{nome:18} {sorted(set(vistos)) or 'NÃO DISPAROU'}")

    print("\n=== SMOKE — HERÓI, com cartas e passivas reais ===")

    def quebra_gelida():
        h, m = _heroi("Mage"), _alvo()
        lancar(h, m, "raio_congelante")
        combat.resolve_physical_attack(h, m, 400, "", rng=_Certeiro(0), publish=publicar)

    def emboscada():
        h, m = _heroi("Rogue"), _alvo()
        lancar(h, h, "fantasma")
        combat.resolve_physical_attack(h, m, 400, "", rng=_Certeiro(0), publish=publicar)

    def ferida_aberta():
        h, m = _heroi("Warrior"), _alvo()
        lancar(h, m, "sangue_nos_olhos")  # vulnerable + secundário bleed, uma carta

    def toxicidade():
        h, m = _heroi("Mage"), _alvo()
        lancar(h, m, "troca_de_sangue")  # secundário frailty
        lancar(h, m, "marca_ardente")  # secundário poison

    def panico():
        h, m = _heroi("Warrior"), _alvo()
        lancar(h, m, "sangue_nos_olhos")
        lancar(h, m, "berro_de_ferro")  # secundário fear

    def hemorragia_fria():
        h, m = _heroi("Mage", ["Agulha no Osso"]), _alvo()  # a passiva dá o sangramento
        lancar(h, m, "raio_congelante")
        combat.resolve_physical_attack(h, m, 400, "", rng=_Certeiro(0), publish=publicar)

    def ferida_septica():
        h, m = _heroi("Rogue", ["Fio Serrilhado"]), _alvo()
        lancar(h, m, "envenenar")
        for _ in range(3):
            combat.process_turn_start_effects(m, rng=random.Random(0), publish=None)
        combat.resolve_physical_attack(h, m, 200, "", rng=_Certeiro(0), publish=publicar)

    def colapso_mental():
        h, m = _heroi("Rogue"), _alvo()
        lancar(h, m, "bolso_furado")  # mana_burn + secundário clouded
        combat.process_turn_start_effects(m, rng=random.Random(0), publish=publicar)

    for nome, fn in (
        ("Quebra Gélida", quebra_gelida),
        ("Emboscada", emboscada),
        ("Ferida Aberta", ferida_aberta),
        ("Toxicidade", toxicidade),
        ("Pânico", panico),
        ("Hemorragia Fria", hemorragia_fria),
        ("Ferida Séptica", ferida_septica),
        ("Colapso Mental", colapso_mental),
    ):
        caso(nome, fn)

    print("\n=== SMOKE — MONSTRO, sequência dirigida com as cartas dele ===")

    def _mob(role):
        mob = spawn_by_role(role, 20)
        mob._mp = 10**6
        return mob

    def _vitima():
        h = make_hero("Warrior", 20, "naked")
        h.base_hp = h._hp = 10**6
        h.base_mp = h._mp = 500
        return h

    def _lancar_mob(mob, alvo, sid):
        """Lança a carta REAL do monstro. `self` vai no monstro, como no jogo."""
        carta = next(s for s in mob.skills if s.id == sid)
        destino = mob if getattr(carta, "target", "enemy") == "self" else alvo
        combat.apply_skill(mob, destino, carta, rng=_Certeiro(0), publish=publicar)

    def emboscada_skirmisher():
        mob, h = _mob("skirmisher"), _vitima()
        _lancar_mob(mob, h, "mob_evasao_mob")  # some de vista
        combat.resolve_physical_attack(mob, h, 300, "", rng=_Certeiro(0), publish=publicar)

    def gelo_controller():
        mob, h = _mob("controller"), _vitima()
        _lancar_mob(mob, h, "mob_teia_de_gelo")  # frozen + secundário bleed
        combat.resolve_physical_attack(mob, h, 300, "", rng=_Certeiro(0), publish=publicar)

    def panico_controller():
        mob, h = _mob("controller"), _vitima()
        _lancar_mob(mob, h, "mob_teia_de_gelo")  # o bleed vem daqui
        _lancar_mob(mob, h, "mob_medo")  # Presságio num alvo que sangra

    def colapso_controller():
        mob, h = _mob("controller"), _vitima()
        _lancar_mob(mob, h, "mob_queima_mana")  # mana_burn + secundário clouded
        combat.process_turn_start_effects(h, rng=random.Random(0), publish=publicar)

    def toxicidade_support():
        mob, h = _mob("support"), _vitima()
        _lancar_mob(mob, h, "mob_praga_lenta")  # frailty primeiro, veneno depois

    def septica_skirmisher():
        """O bote vem DEPOIS, como no duelo: `mob_bote` tem 3 de recarga.

        Os turnos no meio não são enfeite. Ferida Séptica renova a duração do
        outro efeito, e renovar só significa alguma coisa se ela já tiver
        caído — um sangramento recém-aplicado não tem o que renovar.
        """
        mob, h = _mob("skirmisher"), _vitima()
        _lancar_mob(mob, h, "mob_ferida")  # bleed, duração 3
        for _ in range(2):
            combat.process_turn_start_effects(h, rng=random.Random(0), publish=None)
        _lancar_mob(mob, h, "mob_bote")  # dano + secundário poison

    def ferida_aberta_elite():
        mob, h = _mob("elite"), _vitima()
        _lancar_mob(mob, h, "mob_golpe_de_arauto")  # vulnerable
        _lancar_mob(mob, h, "mob_lamina_negra")  # bleed num alvo vulnerável

    for nome, fn in (
        ("skirmisher: Esquiva Felina → ataque", emboscada_skirmisher),
        ("controller: Teia de Gelo → crítico", gelo_controller),
        ("controller: Teia de Gelo → Presságio", panico_controller),
        ("controller: Queima de Mana → tick", colapso_controller),
        ("support: Praga Lenta", toxicidade_support),
        ("skirmisher: Ferida Aberta → Bote", septica_skirmisher),
        ("elite: Golpe de Arauto → Lâmina Negra", ferida_aberta_elite),
    ):
        vistos.clear()
        fn()
        print(f"{nome:42} {sorted(set(vistos)) or 'NÃO DISPAROU'}")

    print("\n=== SMOKE — MONSTRO, jogando sozinho os próprios turnos ===")
    for role in ROLES:
        achou: list[str] = []
        for semente in range(25):
            h = make_hero("Warrior", 20, "naked")
            h.base_hp = h._hp = 10**6
            h.base_mp = h._mp = 500
            mob = spawn_by_role(role, 20)
            vistos.clear()
            for _ in range(25):
                mob._mp = 10**6
                monster_ai.decide_monster_action(
                    mob, h, rng=random.Random(semente), publish=publicar
                )
                if vistos:
                    break
            if vistos:
                achou = sorted(set(vistos))
                break
        print(f"{role:14} {achou or 'NÃO DISPAROU'}")


if __name__ == "__main__":
    relatorio_estatico()
    relatorio_smoke()
