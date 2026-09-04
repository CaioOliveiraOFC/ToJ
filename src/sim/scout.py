"""Scout de sistemas: quem está carregando o jogo e quem não está fazendo nada.

Duas perguntas diferentes, dois métodos:

**Atribuição** — o que cada sistema entregou durante runs normais. Sai da
telemetria já coletada, custa segundos, e responde "esta skill dá 60% do dano".
É correlação: aponta o suspeito.

**Ablação** — desliga um sistema e compara a profundidade média. Custa minutos e
responde "sem passivas o herói perde 6 andares". É causalidade: condena.

O scout rápido roda só a atribuição. `--ablate` acrescenta a segunda camada.
Nenhum dos dois substitui o outro: uma skill pode ter dano alto por ser usada
sempre (atribuição alta, ablação baixa, porque outra a substitui), e uma passiva
pode ser rara e decisiva (atribuição baixa, ablação alta).
"""

from __future__ import annotations

import statistics
from dataclasses import dataclass, field

from src.content.passives import load_passives
from src.content.skills_loader import load_skills
from src.sim.harness import ALL_CLASSES, simulate_run
from src.sim.toggles import ABLATION_SYSTEMS, Toggles

# Um item é destaque quando se afasta da mediana por este fator. Não é um
# veredito: é o que merece um segundo olhar.
OUTLIER_HIGH = 2.0
OUTLIER_LOW = 0.4
# Abaixo desta taxa de escolha, uma carta oferecida é conteúdo que ninguém quer.
LOW_PICK_RATE = 0.15
# Um sistema cuja remoção muda a profundidade média menos que isto não está
# sustentando nada.
NEGLIGIBLE_ABLATION_FLOORS = 0.5


@dataclass
class Finding:
    """Um destaque do scout, com o número que o sustenta."""

    system: str
    subject: str
    verdict: str
    detail: str
    value: float = 0.0

    def line(self) -> str:
        return f"  [{self.verdict:9}] {self.subject:26} {self.detail}"


@dataclass
class ScoutReport:
    """Resultado do scout: telemetria agregada, destaques e ablação."""

    iterations: int
    classes: list[str]
    telemetry: dict = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    ablation: list[dict] = field(default_factory=list)
    baseline_mean_floor: float = 0.0

    def to_dict(self) -> dict:
        return {
            "kind": "scout",
            "iterations": self.iterations,
            "classes": self.classes,
            "baseline_mean_floor": self.baseline_mean_floor,
            "telemetry": self.telemetry,
            "findings": [
                {"system": f.system, "subject": f.subject, "verdict": f.verdict,
                 "detail": f.detail, "value": f.value}
                for f in self.findings
            ],
            "ablation": self.ablation,
        }


def _merge(target: dict, source: dict) -> dict:
    """Soma recursivamente dois blocos de telemetria."""
    for key, value in source.items():
        if isinstance(value, dict):
            target[key] = _merge(target.get(key, {}), value)
        elif isinstance(value, (int, float)):
            target[key] = target.get(key, 0) + value
        else:
            target.setdefault(key, value)
    return target


def collect(iterations: int, classes: list[str], policy: str, loadout: str,
            seed: int, max_floor: int) -> tuple[dict, float]:
    """Roda a simulação e agrega a telemetria de todas as classes."""
    agregada: dict = {}
    profundidades: list[float] = []
    for hero_class in classes:
        resultado = simulate_run(hero_class, max_floor, iterations, policy, seed, loadout)
        profundidades.append(resultado["mean_floor"])
        _merge(agregada, resultado["telemetry"] or {})
    return agregada, statistics.fmean(profundidades)


def analyse_skills(telemetry: dict) -> list[Finding]:
    """Eficiência e uso das skills.

    A pergunta "esta skill é forte demais" tem duas metades: quanto ela entrega
    por unidade de mana, e quanto do dano total passa por ela. Uma skill cara e
    devastadora pode estar certa; uma skill barata que entrega o mesmo não está.
    """
    dados = telemetry.get("skills", {})
    uses, damage, mp = dados.get("uses", {}), dados.get("damage", {}), dados.get("mp", {})
    offered, picked = dados.get("offered", {}), dados.get("picked", {})
    basico = dados.get("basic_damage", 0)

    catalogo = {s.id: s for s in load_skills()}
    dano_total = sum(damage.values()) + basico
    achados: list[Finding] = []

    eficiencias = {
        sid: damage[sid] / max(1, mp.get(sid, 0))
        for sid in damage
        if damage[sid] > 0 and mp.get(sid, 0) > 0
    }
    mediana = statistics.median(eficiencias.values()) if eficiencias else 0.0

    for sid, eficiencia in sorted(eficiencias.items(), key=lambda kv: -kv[1]):
        nome = catalogo[sid].name if sid in catalogo else sid
        parcela = damage[sid] / dano_total if dano_total else 0
        if mediana and eficiencia >= mediana * OUTLIER_HIGH:
            achados.append(Finding(
                "skills", nome, "SUSPEITA",
                f"{eficiencia:6.1f} de dano por mana ({eficiencia / mediana:.1f}x a mediana), "
                f"{parcela:.0%} do dano total",
                eficiencia,
            ))
        elif mediana and eficiencia <= mediana * OUTLIER_LOW:
            achados.append(Finding(
                "skills", nome, "fraca",
                f"{eficiencia:6.1f} de dano por mana ({eficiencia / mediana:.1f}x a mediana)",
                eficiencia,
            ))

    for sid, vezes in sorted(offered.items(), key=lambda kv: -kv[1]):
        nome = catalogo[sid].name if sid in catalogo else sid
        taxa = picked.get(sid, 0) / vezes if vezes else 0
        if vezes >= 10 and taxa <= LOW_PICK_RATE:
            achados.append(Finding(
                "skills", nome, "ignorada",
                f"oferecida {vezes}x, escolhida {taxa:.0%} das vezes",
                taxa,
            ))

    nunca_usadas = [
        catalogo[sid].name for sid in catalogo
        if sid in picked and uses.get(sid, 0) == 0
    ]
    if nunca_usadas:
        achados.append(Finding(
            "skills", "escolhidas mas nunca usadas", "morta",
            ", ".join(sorted(nunca_usadas)[:6]),
            len(nunca_usadas),
        ))

    if dano_total:
        achados.append(Finding(
            "skills", "ataque básico", "referência",
            f"{basico / dano_total:.0%} do dano total sai do ataque gratuito",
            basico / dano_total,
        ))
    return achados


def analyse_passives(telemetry: dict) -> list[Finding]:
    """Quais passivas o jogador leva quando pode escolher."""
    dados = telemetry.get("passives", {})
    offered, picked = dados.get("offered", {}), dados.get("picked", {})
    catalogo = {p.id: p for p in load_passives()}
    achados: list[Finding] = []

    for pid, vezes in sorted(offered.items(), key=lambda kv: -kv[1]):
        if vezes < 10:
            continue
        nome = catalogo[pid].name if pid in catalogo else pid
        taxa = picked.get(pid, 0) / vezes
        if taxa >= 0.9:
            achados.append(Finding(
                "passivas", nome, "SUSPEITA",
                f"escolhida em {taxa:.0%} das {vezes} ofertas — é a escolha óbvia",
                taxa,
            ))
        elif taxa <= LOW_PICK_RATE:
            achados.append(Finding(
                "passivas", nome, "ignorada",
                f"oferecida {vezes}x, escolhida {taxa:.0%} das vezes",
                taxa,
            ))

    nunca_ofertadas = [catalogo[pid].name for pid in catalogo if pid not in offered]
    if nunca_ofertadas:
        achados.append(Finding(
            "passivas", "nunca sorteadas", "morta",
            ", ".join(sorted(nunca_ofertadas)[:6]),
            len(nunca_ofertadas),
        ))
    return achados


def analyse_equipment(telemetry: dict) -> list[Finding]:
    """Quanto do poder final veio de equipamento, e de onde ele veio."""
    equipamento = telemetry.get("equipment", {})
    economia = telemetry.get("economy", {})
    achados: list[Finding] = []

    amostras = equipamento.get("power_samples", 0) or 1
    pelado = equipamento.get("power_naked_sum", 0) / amostras
    equipado = equipamento.get("power_equipped_sum", 0) / amostras
    if pelado:
        ganho = equipado / pelado - 1
        veredito = "fraco" if ganho < 0.15 else ("SUSPEITA" if ganho > 1.0 else "ok")
        achados.append(Finding(
            "equipamento", "contribuição no poder", veredito,
            f"+{ganho:.0%} sobre o herói sem equipamento",
            ganho,
        ))

    do_loot = equipamento.get("items_equipped_from_loot", 0)
    da_loja = equipamento.get("items_equipped_from_shop", 0)
    if do_loot + da_loja:
        achados.append(Finding(
            "equipamento", "origem do que é equipado", "referência",
            f"{do_loot / (do_loot + da_loja):.0%} de drop, "
            f"{da_loja / (do_loot + da_loja):.0%} de loja",
            0.0,
        ))

    ganho_ouro = economia.get("gold_earned", 0)
    gasto = economia.get("gold_on_gear", 0) + economia.get("gold_on_consumables", 0)
    if ganho_ouro:
        ocioso = 1 - gasto / ganho_ouro
        veredito = "SUSPEITA" if ocioso > 0.5 else "ok"
        achados.append(Finding(
            "economia", "ouro sem destino", veredito,
            f"{ocioso:.0%} do ouro nunca é gasto "
            f"({gasto:,} gastos de {ganho_ouro:,} ganhos)".replace(",", "."),
            ocioso,
        ))
    return achados


def analyse_essence_and_events(telemetry: dict) -> list[Finding]:
    """Quanto a Essência acelera o nível, e o que os eventos fazem."""
    essencia = telemetry.get("essence", {})
    eventos = telemetry.get("events", {})
    achados: list[Finding] = []

    base, depois = essencia.get("xp_base", 0), essencia.get("xp_after", 0)
    sorteios = essencia.get("rolls", 0)
    if base and sorteios:
        inflacao = depois / base - 1
        achados.append(Finding(
            "essência", "efeito no XP", "referência",
            f"multiplica o XP em {depois / base:.2f}x na média "
            f"(sorteio médio {essencia.get('sum', 0) / sorteios:.2f} em {sorteios} andares)",
            inflacao,
        ))

    contagens = eventos.get("counts", {})
    total = sum(contagens.values())
    tratados = {"fountain", "altar", "merchant"}
    for nome, vezes in sorted(contagens.items(), key=lambda kv: -kv[1]):
        if nome not in tratados:
            achados.append(Finding(
                "eventos", nome, "morta",
                f"apareceu {vezes}x e a simulação não faz nada com ele",
                vezes,
            ))

    curado = eventos.get("fountain_healed", 0)
    if contagens.get("fountain"):
        achados.append(Finding(
            "eventos", "Fonte", "referência",
            f"{contagens['fountain']}x, {curado / contagens['fountain']:.0f} de HP por visita",
            curado,
        ))
    if contagens.get("altar"):
        mortes = eventos.get("altar_deaths", 0)
        recusas = eventos.get("declined", {}).get("altar", 0)
        achados.append(Finding(
            "eventos", "Altar", "referência",
            f"{contagens['altar']}x, {recusas} recusados, {mortes} mortes causadas",
            mortes,
        ))
    if total:
        achados.append(Finding(
            "eventos", "frequência", "referência",
            f"{total} eventos em {telemetry.get('runs', 0)} runs",
            total,
        ))
    return achados


def ablate(iterations: int, classes: list[str], policy: str, loadout: str,
           seed: int, max_floor: int, baseline: float,
           per_skill: bool = False, per_passive: bool = False) -> list[dict]:
    """Desliga um sistema por vez e mede o quanto a run perde.

    O delta é em andares de profundidade média: quanto o herói deixa de avançar
    sem aquele sistema. Delta perto de zero significa que o sistema não está
    sustentando nada — pode estar quebrado, ou ser supérfluo.
    """
    variantes: list[tuple[str, Toggles]] = [
        (sistema, Toggles().without(**{sistema: False})) for sistema in ABLATION_SYSTEMS
    ]

    if per_skill:
        variantes += [
            (f"skill:{s.id}", Toggles().without(banned_skills=frozenset({s.id})))
            for s in load_skills() if not s.is_initial
        ]
    if per_passive:
        variantes += [
            (f"passiva:{p.id}", Toggles().without(banned_passives=frozenset({p.id})))
            for p in load_passives()
        ]

    resultados = []
    for nome, toggles in variantes:
        profundidades = [
            simulate_run(c, max_floor, iterations, policy, seed, loadout,
                         toggles=toggles, collect_telemetry=False)["mean_floor"]
            for c in classes
        ]
        media = statistics.fmean(profundidades)
        resultados.append({
            "disabled": nome,
            "mean_floor": media,
            "delta_floors": media - baseline,
        })
    resultados.sort(key=lambda r: r["delta_floors"])
    return resultados


def run_scout(iterations: int = 60, classes: list[str] | None = None, policy: str = "smart",
              loadout: str = "expected", seed: int = 1337, max_floor: int = 20,
              with_ablation: bool = False, ablation_iterations: int = 40,
              per_skill: bool = False, per_passive: bool = False) -> ScoutReport:
    """Executa o scout completo e devolve o relatório."""
    turmas = classes or list(ALL_CLASSES)
    telemetria, baseline = collect(iterations, turmas, policy, loadout, seed, max_floor)

    achados: list[Finding] = []
    achados += analyse_skills(telemetria)
    achados += analyse_passives(telemetria)
    achados += analyse_equipment(telemetria)
    achados += analyse_essence_and_events(telemetria)

    relatorio = ScoutReport(
        iterations=iterations,
        classes=turmas,
        telemetry=telemetria,
        findings=achados,
        baseline_mean_floor=baseline,
    )

    if with_ablation:
        relatorio.ablation = ablate(
            ablation_iterations, turmas, policy, loadout, seed, max_floor,
            baseline=_baseline_for(ablation_iterations, turmas, policy, loadout, seed, max_floor),
            per_skill=per_skill, per_passive=per_passive,
        )
    return relatorio


def _baseline_for(iterations: int, classes: list[str], policy: str, loadout: str,
                  seed: int, max_floor: int) -> float:
    """Baseline com o mesmo número de iterações da ablação.

    Comparar uma ablação de 40 runs contra uma baseline de 60 mistura o efeito
    do sistema com o ruído da amostra.
    """
    return statistics.fmean(
        simulate_run(c, max_floor, iterations, policy, seed, loadout,
                     collect_telemetry=False)["mean_floor"]
        for c in classes
    )


def format_report(report: ScoutReport) -> str:
    """Monta o texto do scout para o terminal, agrupado por sistema."""
    linhas = [
        "",
        f"SCOUT DE SISTEMAS — {report.iterations} runs por classe "
        f"({', '.join(report.classes)}), andar médio {report.baseline_mean_floor:.1f}",
        "=" * 78,
    ]

    for sistema in ("skills", "passivas", "equipamento", "economia", "essência", "eventos"):
        do_sistema = [f for f in report.findings if f.system == sistema]
        if not do_sistema:
            continue
        linhas.append(f"\n{sistema.upper()}")
        suspeitas = [f for f in do_sistema if f.verdict in ("SUSPEITA", "morta")]
        resto = [f for f in do_sistema if f not in suspeitas]
        linhas += [f.line() for f in suspeitas + resto]

    if report.ablation:
        linhas += ["", "ABLAÇÃO — andares perdidos ao desligar o sistema", "-" * 78]
        for entrada in report.ablation:
            delta = entrada["delta_floors"]
            marca = "  " if abs(delta) >= NEGLIGIBLE_ABLATION_FLOORS else " ?"
            linhas.append(
                f"{marca} {entrada['disabled']:28} {entrada['mean_floor']:5.1f} "
                f"({delta:+.1f} andares)"
            )
        linhas.append(
            f"\n  '?' marca sistema cuja remoção muda menos de "
            f"{NEGLIGIBLE_ABLATION_FLOORS} andar: não está sustentando nada."
        )

    return "\n".join(linhas) + "\n"
