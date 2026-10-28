import pathlib
"""Verificações mecânicas dirigidas (A/B). Só lê e executa o motor; não altera src/."""
import copy, json, random, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[3]))
from src.engine.game_logic import create_player_for_new_run
from src.content.factories.dungeons import apply_altar_blessing, altar_hp_cost
from src.content.factories.monsters import create_monster
from src.mechanics import battle
from src.sim import progression as prog

def luta(heroi, monstro, seed, publish=None):
    random.seed(seed)
    dec = lambda h, m, t: battle.Action(kind="attack", target=m[0] if isinstance(m, list) else m)
    out = battle.run_battle(heroi, [monstro], dec, rng=random.Random(seed), publish=publish)
    return (out.fled, heroi.get_hp(), monstro.get_hp(), getattr(out, "turns", None))

print("== 1. Benção do Altar em batalha real (A/B, mesma seed)")
iguais = 0; total = 0
for classe in ("warrior", "mage", "rogue"):
    for seed in range(20):
        base = create_player_for_new_run(classe, "ab", rng=random.Random(seed))
        for _ in range(4):
            base.level_up(show=False) if False else None
        papel = ("bruiser", "tank", "trash", "glass_cannon")[seed % 4]
        mon = create_monster("Alvo", 2, papel)
        a_h, a_m = copy.deepcopy(base), copy.deepcopy(mon)
        b_h, b_m = copy.deepcopy(base), copy.deepcopy(mon)
        apply_altar_blessing(b_h)
        ra = luta(a_h, a_m, 1000 + seed); rb = luta(b_h, b_m, 1000 + seed)
        total += 1; iguais += ra == rb
print(f"  lutas idênticas com e sem a bênção: {iguais}/{total}")

print("== 2. equip_if_better troca a posição errada (anéis)")
h = create_player_for_new_run("warrior", "eq", rng=random.Random(3))
from src.content.items import get_all_items
itens = get_all_items()
aneis = sorted([i for i in itens.values() if str(getattr(i, "slot", "")) == "Ring" and not getattr(i, "classes", None)], key=prog._peso_do_item)
forte, medio, fraco = aneis[-1], aneis[len(aneis)//2], aneis[0]
from src.content.items import Item
def inst(i):
    return i.instance() if hasattr(i, "instance") else copy.deepcopy(i)
for p in ("Ring1", "Ring2"):
    if h.equipment.get(p): h.unequip(p)
h.equip(inst(forte), "Ring1"); h.equip(inst(fraco), "Ring2")
antes = {p: (h.equipment[p].name, prog._peso_do_item(h.equipment[p])) for p in ("Ring1", "Ring2")}
ok = prog.equip_if_better(h, inst(medio))
depois = {p: (h.equipment[p].name, prog._peso_do_item(h.equipment[p])) for p in ("Ring1", "Ring2")}
print(f"  antes {antes}\n  equip_if_better({medio.name}, peso {prog._peso_do_item(medio)}) -> {ok}\n  depois {depois}")
print(f"  saiu o mais forte? {depois['Ring1'][0] == medio.name and depois['Ring2'][0] == fraco.name}")

print("== 3. Elixir de mana_regen no cardápio de combate do bot")
from tools import bot_adapter as adapter
cons = {i.effect_type: i for i in itens.values() if getattr(i, "consumable", False)}
print("  tipos de consumível no catálogo:", sorted(cons))
print("  famílias que o adaptador oferece:", adapter.CURA + adapter.MANA + adapter.ELIXIR)
print("  fora do cardápio:", sorted(set(cons) - set(adapter.CURA + adapter.MANA + adapter.ELIXIR)))

print("== 4. Mercador: oferta real × o que o bot abre")
from src.content.factories.dungeons import get_merchant_offers
from src.content.shop import Shop
random.seed(7)
ofertas = get_merchant_offers(12, random.Random(7))
print("  jogo (andar 12):", [(o['item'].name, o['item'].rarity, o['price']) for o in ofertas])
v = Shop().visit(12, "Warrior")
print("  bot abre a Loja inteira:", len(v.stock), "ofertas, raridades", sorted({str(o['item'].rarity) for o in v.stock}))
