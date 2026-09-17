"""Partidas do BOT_PADRÃO, com o diário por andar e um compilado no topo.

Não é amostra estatística e não deve virar uma: são as três runs que dizem se a
mudança de INTENÇÃO fez o bot jogar o andar. O que importa aqui é a linha
"parou porque", que na policy anterior mentia — dizia ouro quando o portão
fechado tinha sido o HP.

    python -m tools.bot_3runs
    python -m tools.bot_3runs --classes mage --seeds 20260916,20260917,20260918
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path

from src.shared.formulas import xp_for_level
from tools.bot_padrao import BotPadrao

CLASSES = ("warrior", "mage", "rogue")
SEED = 20260918
DESTINO = Path("reports/bot_3runs_diario.txt")
REGUA = "_" * 100


def jogar(classe: str, seed: int, max_andar: int) -> BotPadrao:
    bot = BotPadrao(classe, seed, max_andar)
    bot.jogar()
    return bot


def _xp_do_andar(a: dict) -> int:
    """XP ganho no andar. O balde ZERA no level-up, então subtrair mente.

    `Player.level_up` faz `xp_points -= need_to_up()`. Uma diferença crua de
    `xp_points` devolve número negativo em todo andar que subiu de nível — foi
    assim que a primeira versão desta tabela mostrou -87 num andar de 2 vitórias.
    """
    if "xp_depois" not in a:
        return 0
    atravessados = sum(
        xp_for_level(n) for n in range(a["nivel"], a.get("nivel_depois", a["nivel"]))
    )
    return a["xp_depois"] - a["xp_antes"] + atravessados


def _motivo(a: dict, bot: BotPadrao) -> str:
    """O motivo da parada, ou o que encerrou a run neste andar."""
    if "motivo_da_parada" in a:
        return a["motivo_da_parada"]
    return f"a run terminou aqui — {bot.fim.split()[0].lower()}"


def _tabela(bot: BotPadrao) -> list[str]:
    linhas = [
        f"{'and':>4} {'nv':>3} {'monstros':>9} {'lutou':>6} {'fugiu':>6} {'poção':>6} "
        f"{'HP ini':>7} {'HP fim':>7} {'MP ini':>7} {'XP':>6} {'ouro':>7} "
        f"{'saída':>9}  motivo para parar de lutar",
        "-" * 148,
    ]
    for a in bot.por_andar:
        paga = {True: "paga", False: "NÃO paga", None: "—"}[a.get("saida_paga")]
        ouro = a.get("ouro_depois", a["ouro_antes"]) - a["ouro_antes"]
        fim = a.get("hp_saida")
        linhas.append(
            f"{a['andar']:>4} {a['nivel']:>3} {a['oferecidos']:>9} {a['combates']:>6} "
            f"{a['fugas']:>6} {a['pocoes_bebidas']:>6} "
            f"{a['hp_entrada']:>6.0%} {'—' if fim is None else format(fim, '.0%'):>6} "
            f"{a['mp_entrada']:>6.0%} "
            f"{_xp_do_andar(a):>+6} {ouro:>+7} {paga:>9}  {_motivo(a, bot)}"
        )
    oferecidos = sum(a["oferecidos"] for a in bot.por_andar)
    lutou = sum(a["combates"] for a in bot.por_andar)
    linhas.append("-" * 148)
    linhas.append(
        f"  {lutou} combate(s) de {oferecidos} monstro(s) oferecidos = "
        f"{(lutou / oferecidos if oferecidos else 0):.0%} de engajamento | "
        f"{sum(a['fugas'] for a in bot.por_andar)} fuga(s) decidida(s) na ficha | "
        f"{sum(a['pocoes_bebidas'] for a in bot.por_andar)} poção(ões) bebida(s) no mapa"
    )
    return linhas


def _motivos(bot: BotPadrao) -> list[str]:
    contagem = Counter(_motivo(a, bot).split(",")[0] for a in bot.por_andar)
    return [f"    {v}x  {k}" for k, v in contagem.most_common()]


def bloco(bot: BotPadrao) -> str:
    hero = bot.hero
    out = [REGUA, f"RUN {hero.get_classname().upper()} seed {bot.seed} — {bot.fim}", REGUA, ""]
    out += _tabela(bot)
    out += ["", "  Por que parou de lutar, agrupado:"]
    out += _motivos(bot)
    out += [
        "",
        f"  Estado final: nível {hero.get_level()} | XP {hero.xp_points}/{hero.need_to_up()} | "
        f"HP {hero.get_hp()}/{hero.base_hp} | MP {hero.get_mp()}/{hero.base_mp} | "
        f"ouro {hero.coins}",
        f"  ST {hero.get_st()}  MG {hero.get_mg()}  AG {hero.get_ag()}  DF {hero.get_df()}",
        f"  Passivas ({len(hero.passives)}): "
        + (", ".join(p.name for p in hero.passives) or "nenhuma"),
        f"  Skills ({len(hero.skills)}): "
        + ", ".join(f"slot {k}: {v.name}" for k, v in sorted(hero.skills.items())),
        f"  Equipamento ({sum(1 for i in hero.equipment.values() if i)} peças):",
    ]
    for slot, item in hero.equipment.items():
        if item is not None:
            out.append(f"    {slot:<10} {item.display_name} [{getattr(item, 'rarity', '?')}]")
    if not any(hero.equipment.values()):
        out.append("    (nada equipado)")
    out.append(
        f"  Mochila ({len(hero.inventory)}): "
        + (", ".join(getattr(i, "name", "?") for i in hero.inventory) or "vazia")
    )
    obs = bot.observador
    out += [
        f"  Combate: {bot.combates_na_run} duelo(s) | ações "
        + (", ".join(f"{k} {v}x" for k, v in sorted(bot.acoes.items())) or "—")
        + f" | MP gasto {bot.mp_gasto} de {bot.mp_disponivel}",
        f"  Dano: causou {obs.dado_total} (maior {obs.dado_max}), "
        f"sofreu {obs.recebido_total} (maior {obs.recebido_max})",
    ]
    if bot.fatal:
        f = bot.fatal
        out.append(
            f"  Morte: {f['monstro']} (Nv{f['nivel']}, {f['gap']:+d}) no andar {f['andar']}, "
            f"aceito com {f['hp_frac']:.0%} de HP e {f['mp_frac']:.0%} de MP, "
            f"{f.get('turnos', '?')} turno(s)"
        )
    out += ["", "DIÁRIO COMPLETO", "-" * 15, "", str(bot.trace), ""]
    return "\n".join(out)


def _lista(texto: str, conversor=str) -> list:
    return [conversor(x.strip()) for x in texto.split(",") if x.strip()]


def compilado(bots: list[BotPadrao]) -> list[str]:
    """As N runs numa tabela só. Só agrega o que as partidas já mediram."""
    out = ["", "=" * 148, f"COMPILADO — {len(bots)} partida(s)", "=" * 148]
    out.append(
        f"{'seed':>9} {'classe':<8} {'desfecho':<9} {'and':>4} {'nv':>3} "
        f"{'ofer':>5} {'lutou':>6} {'fugiu':>6} {'engaj':>6} {'limpos':>7} {'poção':>6} "
        f"{'XP':>7} {'dano dado':>10} {'sofrido':>8} {'ouro':>6} {'eq':>3} {'ps':>3}"
    )
    out.append("-" * 148)
    for b in bots:
        a = b.por_andar
        ofer = sum(x["oferecidos"] for x in a)
        lutou = sum(x["combates"] for x in a)
        limpos = sum(1 for x in a if x.get("motivo_da_parada") == "andar limpo")
        xp = sum(_xp_do_andar(x) for x in a)
        obs = b.observador
        out.append(
            f"{b.seed:>9} {b.hero.get_classname():<8} {b.fim.split()[0]:<9} "
            f"{len(a):>4} {b.hero.get_level():>3} {ofer:>5} {lutou:>6} "
            f"{sum(x['fugas'] for x in a):>6} {(lutou / ofer if ofer else 0):>6.0%} "
            f"{f'{limpos}/{len(a)}':>7} {sum(x['pocoes_bebidas'] for x in a):>6} "
            f"{xp:>7} {obs.dado_total:>10} {obs.recebido_total:>8} "
            f"{b.hero.coins:>6} {sum(1 for i in b.hero.equipment.values() if i):>3} "
            f"{len(b.hero.passives):>3}"
        )
    ofer = sum(x["oferecidos"] for b in bots for x in b.por_andar)
    lutou = sum(x["combates"] for b in bots for x in b.por_andar)
    andares = sum(len(b.por_andar) for b in bots)
    limpos = sum(1 for b in bots for x in b.por_andar if x.get("motivo_da_parada") == "andar limpo")
    out.append("-" * 148)
    out.append(
        f"  AGREGADO: {lutou} de {ofer} monstros = {(lutou / ofer if ofer else 0):.0%} de "
        f"engajamento | {limpos} de {andares} andares limpos | "
        f"{sum(x['fugas'] for b in bots for x in b.por_andar)} fuga(s) na ficha | "
        f"{sum(x['pocoes_bebidas'] for b in bots for x in b.por_andar)} poção(ões) no mapa"
    )
    desfechos = Counter(b.fim.split()[0] for b in bots)
    out.append("  Desfechos: " + ", ".join(f"{k} {v}x" for k, v in desfechos.most_common()))

    # Os motivos de parada, somados. É a coluna que existe para o trace parar de
    # atribuir ao ouro o que sempre foi HP.
    motivos = Counter(
        _motivo(x, b).split(",")[0] for b in bots for x in b.por_andar if "restantes" in x
    )
    out.append("")
    out.append("  Por que parou de lutar, nas 5 partidas:")
    for k, v in motivos.most_common():
        out.append(f"    {v:>3}x  {k}")
    return out


def main() -> None:
    p = argparse.ArgumentParser(description="Partidas do BOT_PADRÃO, com diário por andar.")
    p.add_argument("--max-floor", type=int, default=20)
    p.add_argument("--classes", default=",".join(CLASSES))
    p.add_argument("--seeds", default=None, help="Lista separada por vírgula.")
    # Apelido de uma `--seeds` de um item só: mantém vivo o comando da rodada
    # em que esta ferramenta nasceu.
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--saida", default=str(DESTINO))
    args = p.parse_args()

    classes = _lista(args.classes)
    seeds = _lista(args.seeds, int) if args.seeds else [args.seed]
    bots = [jogar(c, s, args.max_floor) for c in classes for s in seeds]

    destino = Path(args.saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        "\n".join(compilado(bots)) + "\n\n" + "\n".join(bloco(b) for b in bots),
        encoding="utf-8",
    )

    for b in bots:
        print(f"\n{'=' * 148}")
        print(f"{b.hero.get_classname().upper()} seed {b.seed} — {b.fim}")
        print("=" * 148)
        print("\n".join(_tabela(b)))
        print("  Por que parou de lutar:")
        print("\n".join(_motivos(b)))
    print("\n".join(compilado(bots)))
    print(f"\nDiário completo: {destino}")


if __name__ == "__main__":
    main()
