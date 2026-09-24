"""Gera o candidato a BENCHMARK DA ARENA a partir de runs REAIS.

A pergunta é "como é um personagem que conseguiu chegar vivo ao andar 20?", e a
única resposta honesta é ir buscar um. Nada aqui monta personagem: a população
sai de runs completas do `BotPadrao`, jogando o mesmo mapa, o mesmo combate, o
mesmo loot, o mesmo level-up, a mesma loja e o mesmo ferreiro do jogo. Nível,
atributos, equipamento, `+N`, sockets, gemas, encantamentos, skills, passivas e
consumíveis chegam pela progressão canônica ou não chegam.

FERRAMENTA, não regra. Nada em `src/` sabe que este arquivo existe. Chegar ao
andar 20 não vira objetivo do jogo, não vira condição de vitória e não muda o
bot: o único desvio é que o piloto desta medição não EXTRAI, porque uma run que
extrai no andar 12 não responde a pergunta. O desvio mora numa subclasse local
e some quando o processo termina.

O snapshot é tirado na ENTRADA do andar alvo, antes do mapa ser montado e antes
de qualquer recurso daquele andar ser tocado. E `overall_power` continua sendo
medido com HP/MP cheios, como manda o contrato da régua — o HP e o MP da chegada
são telemetria, não entram no poder.

    python -m tools.arena_benchmark --runs 400
"""

from __future__ import annotations

import argparse
import copy
import statistics
from dataclasses import dataclass, field

from src.sim.arena import assinatura_de_build, overall_power
from src.sim.bot import decidir_no_mapa
from tools import bot_adapter as adapter
from tools.bot_padrao import BotPadrao

CLASSES = ("warrior", "mage", "rogue")
ANDAR_ALVO = 20


class _ChegouAoAlvoError(Exception):
    """Sinal interno: o snapshot foi tirado, não há mais o que medir."""


class PilotoDaArena(BotPadrao):
    """O bot de sempre, com duas diferenças que existem só nesta ferramenta.

    1. NÃO EXTRAI. A opção é retirada antes de o cérebro escolher, então nem a
       policy nem o adaptador nem o driver mudam — o que muda é o cardápio que
       este piloto recebe. Uma run que extrai no andar 12 é um desfecho legítimo
       do jogo e uma resposta inútil para "como é quem chegou ao 20".
    2. PARA AO CHEGAR. O andar alvo não é jogado: o que interessa é o estado de
       quem entrou nele.
    """

    # Declarado para o adaptador, que pergunta antes de pagar a comparação com o
    # alvo da Arena. Sem isto a ferramenta media o poder do bot a cada build
    # nova — centenas de duelos reais — para um número que ela nunca poderia
    # usar, já que aqui extrair não está no cardápio. Medido: 132 min contra ~7
    # nas 900 runs.
    extracao_habilitada = False

    def __init__(self, classe: str, seed: int, andar_alvo: int = ANDAR_ALVO) -> None:
        super().__init__(classe, seed, max_andar=andar_alvo)
        self.andar_alvo = andar_alvo
        self.snapshot = None
        self.chegada: dict = {}

    def _decidir_no_mapa(self):
        mapa, prog = adapter.estado_do_mapa(self)
        opcoes, destinos = adapter.acoes_do_mapa(self, mapa, prog)
        sem_extracao = tuple(o for o in opcoes if o.family != "extrair")
        decisao = decidir_no_mapa(mapa, prog, sem_extracao or opcoes)
        return decisao, destinos.get(decisao.action_id)

    def _jogar_andar(self, andar: int) -> str:
        if andar < self.andar_alvo:
            return super()._jogar_andar(andar)
        heroi = self.hero
        # ANTES de `_setup_dungeon_map`, antes da Essência do andar, antes de
        # qualquer passo: este é o personagem que ATRAVESSOU os 19 anteriores.
        self.snapshot = copy.deepcopy(heroi)
        self.chegada = {
            "hp": heroi.get_hp(),
            "hp_max": heroi.base_hp,
            "mp": heroi.get_mp(),
            "mp_max": heroi.base_mp,
            "ouro": heroi.coins,
        }
        raise _ChegouAoAlvoError


@dataclass
class Sobrevivente:
    classe: str
    seed: int
    heroi: object
    chegada: dict
    poder: float = 0.0


@dataclass
class Populacao:
    tentativas: int = 0
    sobreviventes: list[Sobrevivente] = field(default_factory=list)
    desfechos: dict = field(default_factory=dict)

    @property
    def taxa(self) -> float:
        return len(self.sobreviventes) / max(1, self.tentativas)


def correr(seeds, classes=CLASSES, andar_alvo: int = ANDAR_ALVO) -> Populacao:
    """Roda a população de runs reais e devolve quem entrou vivo no andar alvo."""
    pop = Populacao()
    for seed in seeds:
        for classe in classes:
            pop.tentativas += 1
            piloto = PilotoDaArena(classe, seed, andar_alvo)
            try:
                piloto.jogar()
            except _ChegouAoAlvoError:
                pop.sobreviventes.append(
                    Sobrevivente(classe, seed, piloto.snapshot, piloto.chegada)
                )
                pop.desfechos["chegou"] = pop.desfechos.get("chegou", 0) + 1
                continue
            chave = piloto.fim.split(" no andar ")[0]
            pop.desfechos[chave] = pop.desfechos.get(chave, 0) + 1
    return pop


def medir(pop: Populacao, **kwargs) -> None:
    """Preenche `overall_power` de cada sobrevivente. HP/MP cheios, por contrato."""
    for s in pop.sobreviventes:
        s.poder = overall_power(s.heroi, **kwargs).nivel_equivalente


def reproduz(s: Sobrevivente, andar_alvo: int = ANDAR_ALVO) -> bool:
    """Roda a MESMA seed de novo e confere se a build sai idêntica.

    É a prova de proveniência que vale alguma coisa: se o snapshot tivesse sido
    tocado por fora — um item injetado, um atributo ajustado, uma skill escolhida
    à mão — a segunda passagem não bateria. A assinatura é a mesma que a régua
    usa para o cache, então ela cobre atributos, deck, passivas, consumíveis e os
    canais de combate.
    """
    piloto = PilotoDaArena(s.classe, s.seed, andar_alvo)
    try:
        piloto.jogar()
    except _ChegouAoAlvoError:
        return assinatura_de_build(piloto.snapshot) == assinatura_de_build(s.heroi)
    return False


def representante(sobreviventes: list[Sobrevivente]) -> Sobrevivente:
    """O snapshot REAL mais próximo da mediana da população.

    A mediana só escolhe QUAL personagem representa; ela nunca é montada. Um
    "personagem médio" com o elmo de um e a arma de outro não existiu, não
    atravessou 19 andares e não pode ser alvo de nada.
    """
    meio = statistics.median(s.poder for s in sobreviventes)
    return min(sobreviventes, key=lambda s: (abs(s.poder - meio), s.classe, s.seed))


# --- relatório -------------------------------------------------------------


def _peca(item) -> str:
    nome = getattr(item, "display_name", None) or item.name
    partes = [nome]
    gemas = [g.display_name for g in getattr(item, "gems", []) if g is not None]
    vazios = sum(1 for g in getattr(item, "gems", []) if g is None)
    if gemas or vazios:
        partes.append(f"sockets {len(getattr(item, 'gems', []))}")
    if gemas:
        partes.append("gemas: " + ", ".join(gemas))
    encantos = [f"{e.effect} {e.value:g}" for e in getattr(item, "enchantments", [])]
    if encantos:
        partes.append("encantos: " + ", ".join(encantos))
    return " | ".join(partes)


def ficha(s: Sobrevivente) -> str:
    h = s.heroi
    linhas = [
        f"CLASSE            {h.get_classname()}",
        f"SEED              {s.seed}",
        f"NÍVEL             {h.get_level()}",
        f"overall_power     {s.poder:.2f}",
        "",
        f"CHEGADA NO ANDAR  HP {s.chegada['hp']}/{s.chegada['hp_max']}"
        f"  MP {s.chegada['mp']}/{s.chegada['mp_max']}"
        f"  ouro {s.chegada['ouro']}   (telemetria; o poder é medido com HP/MP cheios)",
        "",
        f"ATRIBUTOS         HP {h.base_hp}  MP {h.base_mp}  ST {h.get_st()}  "
        f"MG {h.get_mg()}  AG {h.get_ag()}  DF {h.get_df()}",
        "",
        "EQUIPAMENTO",
    ]
    for posicao in h.EQUIPMENT_POSITIONS:
        peca = h.equipment.get(posicao)
        linhas.append(f"  {posicao:10} {_peca(peca) if peca else '—'}")
    linhas += ["", "SKILLS"]
    for slot, carta in sorted(h.skills.items()):
        linhas.append(f"  {slot}  {carta.name} ({carta.rarity}, {carta.effect_type})")
    linhas += ["", f"PASSIVAS ({len(h.passives)})"]
    for p in h.passives:
        linhas.append(f"  {p.name} ({p.rarity}, {p.effect_type} {p.effect_value})")
    consumiveis = [i for i in h.inventory if getattr(i, "consumable", False)]
    linhas += ["", f"CONSUMÍVEIS ({len(consumiveis)})"]
    for nome in sorted({i.name for i in consumiveis}):
        linhas.append(f"  {sum(1 for i in consumiveis if i.name == nome)}x {nome}")
    guardados = [i for i in h.inventory if not getattr(i, "consumable", False)]
    linhas += [
        "",
        f"MOCHILA (não equipado): {len(guardados)} peças",
        f"GEMAS NA BOLSA: {len(h.gems)}"
        + (("  — " + ", ".join(g.display_name for g in h.gems)) if h.gems else ""),
    ]
    return "\n".join(linhas)


def relatorio(pop: Populacao, quantos: int = 5) -> str:
    out = [
        "=" * 78,
        "POPULAÇÃO",
        "=" * 78,
        f"runs executadas            {pop.tentativas}",
        f"chegaram vivas ao andar {ANDAR_ALVO}   {len(pop.sobreviventes)}  ({pop.taxa:.2%})",
        "",
        "desfechos: " + ", ".join(f"{k} {v}" for k, v in sorted(pop.desfechos.items())),
    ]
    if not pop.sobreviventes:
        return "\n".join(out)

    out += ["", "SOBREVIVENTES POR CLASSE"]
    for classe in CLASSES:
        do_classe = [s for s in pop.sobreviventes if s.classe == classe]
        tentou = pop.tentativas // len(CLASSES)
        poderes = [s.poder for s in do_classe]
        resumo = (
            f"mediana {statistics.median(poderes):6.2f}  "
            f"min {min(poderes):6.2f}  max {max(poderes):6.2f}"
            if poderes
            else "—"
        )
        taxa = len(do_classe) / max(1, tentou)
        out.append(f"  {classe:8} {len(do_classe):4} de {tentou:4} ({taxa:6.2%})   {resumo}")

    poderes = sorted(s.poder for s in pop.sobreviventes)
    out += [
        "",
        "DISTRIBUIÇÃO DE overall_power",
        f"  min      {poderes[0]:.2f}",
        f"  p25      {_percentil(poderes, 0.25):.2f}",
        f"  mediana  {statistics.median(poderes):.2f}",
        f"  p75      {_percentil(poderes, 0.75):.2f}",
        f"  max      {poderes[-1]:.2f}",
    ]

    out += ["", "A MEDIANA GLOBAL É ARTEFATO DE UMA CLASSE?"]
    todos = statistics.median(poderes)
    for classe in CLASSES:
        sem = [s.poder for s in pop.sobreviventes if s.classe != classe]
        if sem:
            out.append(
                f"  sem {classe:8} n={len(sem):4}  mediana {statistics.median(sem):6.2f}  "
                f"({statistics.median(sem) - todos:+.2f} vs a global)"
            )

    niveis = sorted(s.heroi.get_level() for s in pop.sobreviventes)
    out += [
        "",
        "COMO CHEGOU QUEM CHEGOU",
        f"  nível na entrada do {ANDAR_ALVO}: min {niveis[0]}  "
        f"mediana {statistics.median(niveis):.0f}  max {niveis[-1]}",
    ]
    for rotulo, conta in (
        (
            "com ao menos um +N",
            lambda h: any(
                getattr(i, "enhancement_level", 0) > 0 for i in h.equipment.values() if i
            ),
        ),
        (
            "com ao menos uma gema",
            lambda h: any(
                g is not None for i in h.equipment.values() if i for g in getattr(i, "gems", [])
            ),
        ),
        (
            "com ao menos um encantamento",
            lambda h: any(getattr(i, "enchantments", []) for i in h.equipment.values() if i),
        ),
        (
            "com os 11 slots ocupados",
            lambda h: all(h.equipment.get(p) for p in h.EQUIPMENT_POSITIONS),
        ),
    ):
        atende = sum(1 for s in pop.sobreviventes if conta(s.heroi))
        out.append(f"  {rotulo:30} {atende:4} de {len(pop.sobreviventes)}")

    meio = statistics.median(poderes)
    perto = sorted(pop.sobreviventes, key=lambda s: (abs(s.poder - meio), s.classe, s.seed))
    out += ["", f"OS {quantos} SNAPSHOTS MAIS PRÓXIMOS DA MEDIANA ({meio:.2f})"]
    out.append(f"  {'#':<3} {'classe':9} {'seed':>10} {'nível':>6} {'poder':>7} {'desvio':>8}")
    for i, s in enumerate(perto[:quantos], 1):
        out.append(
            f"  {i:<3} {s.classe:9} {s.seed:>10} {s.heroi.get_level():>6} "
            f"{s.poder:>7.2f} {s.poder - meio:>+8.2f}"
        )

    escolhido = representante(pop.sobreviventes)
    out += ["", "=" * 78, "CANDIDATO RECOMENDADO — ARENA BENCHMARK V1", "=" * 78, ficha(escolhido)]
    out += [
        "",
        "PROVENIÊNCIA",
        f"  a seed {escolhido.seed} ({escolhido.classe}) reproduz a MESMA build: "
        f"{'SIM' if reproduz(escolhido) else 'NÃO'}",
        "  origem de cada componente, toda pelo caminho do jogo:",
        "    personagem      engine.game_logic.create_player_from_data",
        "    andar           engine.loop._setup_dungeon_map",
        "    combate         mechanics.battle.run_battle",
        "    pós-combate     engine.loop.process_post_battle",
        "    loot / equipar  sim.progression.equip_if_better",
        "    level-up        sim.progression.on_level_up (passiva e skill)",
        "    loja            sim.progression.visit_shop (consumíveis, gemas)",
        "    ferreiro        sim.progression.visit_forge (+N, sockets, encantos)",
        "    eventos         content.factories.dungeons",
        "    saída/Essência  content.floor_exit",
        "  único desvio desta ferramenta: o piloto não recebe a opção de EXTRAIR.",
    ]
    return "\n".join(out)


def _percentil(ordenados: list[float], q: float) -> float:
    if len(ordenados) == 1:
        return ordenados[0]
    pos = q * (len(ordenados) - 1)
    baixo = int(pos)
    resto = pos - baixo
    if baixo + 1 >= len(ordenados):
        return ordenados[-1]
    return ordenados[baixo] * (1 - resto) + ordenados[baixo + 1] * resto


def main() -> None:
    parser = argparse.ArgumentParser(description="Candidatos a benchmark da Arena, de runs reais.")
    parser.add_argument("--runs", type=int, default=300, help="seeds por classe")
    parser.add_argument("--seed-inicial", type=int, default=20260919)
    parser.add_argument("--duelos", type=int, default=None, help="duelos por sondagem da régua")
    args = parser.parse_args()

    seeds = range(args.seed_inicial, args.seed_inicial + args.runs)
    pop = correr(seeds)
    if pop.sobreviventes:
        medir(pop, **({"duelos": args.duelos} if args.duelos else {}))
    print(relatorio(pop))


if __name__ == "__main__":
    main()
