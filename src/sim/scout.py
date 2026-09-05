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
from src.shared.constants import (
    PASSIVE_COMMON_WEIGHT,
    PASSIVE_EPIC_WEIGHT,
    PASSIVE_LEGENDARY_WEIGHT,
    PASSIVE_RARE_WEIGHT,
)
from src.sim.harness import ALL_CLASSES, simulate_run
from src.sim.pick_policies import DELIBERATE_POLICIES, POLICIES
from src.sim.toggles import ABLATION_SYSTEMS, Toggles

# Um item é destaque quando se afasta da mediana por este fator. Não é um
# veredito: é o que merece um segundo olhar.
OUTLIER_HIGH = 2.0
OUTLIER_LOW = 0.4
# Os mesmos pesos que `generate_passive_choices` usa para sortear a oferta.
RARITY_WEIGHTS = {
    "Common": PASSIVE_COMMON_WEIGHT,
    "Rare": PASSIVE_RARE_WEIGHT,
    "Epic": PASSIVE_EPIC_WEIGHT,
    "Legendary": PASSIVE_LEGENDARY_WEIGHT,
}
# Abaixo desta taxa de escolha, uma carta oferecida é conteúdo que ninguém quer.
LOW_PICK_RATE = 0.15
# Ofertas mínimas para que a taxa de escolha signifique alguma coisa. Abaixo
# disso a carta não é julgada: é declarada sem amostra.
MIN_OFFERS_FOR_RATE = 10
# Quantas aparições a amostra precisava prever antes de a ausência de uma carta
# significar "conteúdo morto" em vez de "sorteio não calhou".
MIN_EXPECTED_OFFERS = 3.0
# Um sistema cuja remoção muda a profundidade média menos que isto não está
# sustentando nada.
NEGLIGIBLE_ABLATION_FLOORS = 0.5
# Escolher de propósito precisa render pelo menos isto sobre escolher ao acaso.
# Abaixo disso, o menu de cartas é decorativo.
MIN_CHOICE_VALUE_FLOORS = 0.5
# Acima desta taxa de escolha em todas as políticas, a carta não é uma opção: é
# a resposta certa, e o menu que a oferece não está perguntando nada.
UNIVERSAL_PICK_RATE = 0.7


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
class PolicyComparison:
    """Como cada política de escolha se saiu, e o que cada uma levou."""

    mean_floor_by_policy: dict[str, float] = field(default_factory=dict)
    passive_pick_rate: dict[str, dict[str, float]] = field(default_factory=dict)
    skill_pick_rate: dict[str, dict[str, float]] = field(default_factory=dict)

    def choice_value(self) -> float:
        """Quanto escolher de propósito rende sobre escolher ao acaso.

        É a pergunta que o menu de cartas existe para responder. Se der zero, o
        jogador está apertando um botão que não muda nada.
        """
        deliberadas = [
            self.mean_floor_by_policy[nome]
            for nome in DELIBERATE_POLICIES
            if nome in self.mean_floor_by_policy
        ]
        aleatoria = self.mean_floor_by_policy.get("random")
        if not deliberadas or aleatoria is None:
            return 0.0
        return max(deliberadas) - aleatoria

    def to_dict(self) -> dict:
        return {
            "mean_floor_by_policy": self.mean_floor_by_policy,
            "choice_value_floors": self.choice_value(),
            "passive_pick_rate": self.passive_pick_rate,
            "skill_pick_rate": self.skill_pick_rate,
        }


@dataclass
class ScoutReport:
    """Resultado do scout: telemetria agregada, destaques e ablação."""

    iterations: int
    classes: list[str]
    telemetry: dict = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    ablation: list[dict] = field(default_factory=list)
    baseline_mean_floor: float = 0.0
    policies: PolicyComparison | None = None

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
            "pick_policies": self.policies.to_dict() if self.policies else None,
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


def compare_pick_policies(iterations: int, classes: list[str], policy: str, loadout: str,
                          seed: int, max_floor: int) -> PolicyComparison:
    """Roda a simulação com cada política de escolha e compara o que cada uma leva.

    Com uma política só, "esta passiva é ignorada" mistura duas causas: a carta é
    fraca, ou a carta serve a uma build que aquele bot não joga. Rodar várias
    separa as duas, e a política aleatória dá a referência.
    """
    comparacao = PolicyComparison()

    for nome in POLICIES:
        telemetria: dict = {}
        profundidades: list[float] = []
        for hero_class in classes:
            resultado = simulate_run(hero_class, max_floor, iterations, policy, seed,
                                     loadout, pick_policy=nome)
            profundidades.append(resultado["mean_floor"])
            _merge(telemetria, resultado["telemetry"] or {})

        comparacao.mean_floor_by_policy[nome] = statistics.fmean(profundidades)
        comparacao.passive_pick_rate[nome] = _pick_rates(telemetria.get("passives", {}))
        comparacao.skill_pick_rate[nome] = _pick_rates(telemetria.get("skills", {}))

    return comparacao


def _pick_rates(bloco: dict) -> dict[str, float]:
    """Taxa de escolha de cada carta, entre as vezes em que foi oferecida."""
    offered, picked = bloco.get("offered", {}), bloco.get("picked", {})
    return {
        cid: picked.get(cid, 0) / vezes
        for cid, vezes in offered.items()
        if vezes >= MIN_OFFERS_FOR_RATE
    }


def analyse_pick_policies(comparacao: PolicyComparison) -> list[Finding]:
    """O que a comparação entre políticas revela sobre as cartas e sobre o menu."""
    achados: list[Finding] = []

    valor = comparacao.choice_value()
    espalhamento = (
        max(comparacao.mean_floor_by_policy.values())
        - min(comparacao.mean_floor_by_policy.values())
    ) if comparacao.mean_floor_by_policy else 0.0

    if valor < MIN_CHOICE_VALUE_FLOORS:
        achados.append(Finding(
            "escolha", "valor de escolher", "SUSPEITA",
            f"a melhor política deliberada rende {valor:+.1f} andar sobre sortear ao acaso "
            "— o menu de cartas não está fazendo pergunta nenhuma",
            valor,
        ))
    else:
        achados.append(Finding(
            "escolha", "valor de escolher", "ok",
            f"escolher de propósito rende {valor:+.1f} andar sobre sortear",
            valor,
        ))

    # A profundidade média de uma run é bimodal, então este número balança entre
    # execuções. Dizer isso é mais honesto que apresentar uma casa decimal que a
    # amostra não sustenta.
    if abs(valor) < espalhamento * 0.4:
        achados.append(Finding(
            "escolha", "confiança da medição", "referência",
            f"o valor da escolha ({valor:+.1f}) é pequeno perto do espalhamento entre "
            f"políticas ({espalhamento:.1f}) — aumente --policy-iterations antes de decidir",
            espalhamento,
        ))

    ordenadas = sorted(comparacao.mean_floor_by_policy.items(), key=lambda kv: -kv[1])
    achados.append(Finding(
        "escolha", "ranking de intenção", "referência",
        " > ".join(f"{nome} {andar:.1f}" for nome, andar in ordenadas),
        0.0,
    ))

    achados += _analyse_cards(comparacao.passive_pick_rate, "passivas")
    achados += _analyse_cards(comparacao.skill_pick_rate, "skills")
    return achados


def _analyse_cards(taxas_por_politica: dict[str, dict[str, float]], sistema: str) -> list[Finding]:
    """Classifica cada carta pelo padrão de escolha entre as políticas.

    Três padrões, três diagnósticos diferentes:
    ignorada por todas as intenções é carta fraca; levada por todas é a resposta
    certa disfarçada de escolha; levada por uma só é identidade de build, que é
    exatamente o que se quer e não deve ser mexido.

    Só entra na classificação a carta que **toda** política deliberada ofereceu
    o bastante para render uma taxa. Antes, a carta ausente da tabela de uma
    política era lida como taxa zero — descartada por falta de amostra e
    recusada pelo jogador viravam a mesma coisa. O viés não era aleatório:
    `survival` e `offense` morrem mais raso e nunca chegam aos níveis em que as
    cartas de fim de jogo são oferecidas, então eram justamente elas que
    apareciam como fracas. `ressurgir` era condenada assim, e `apocalipse` e
    `morte_subita` eram promovidas a "identidade" pelo mesmo engano.
    """
    from src.content.passives import load_passives
    from src.content.skills_loader import load_skills

    catalogo = (
        {p.id: p.name for p in load_passives()} if sistema == "passivas"
        else {s.id: s.name for s in load_skills()}
    )
    deliberadas = [n for n in DELIBERATE_POLICIES if n in taxas_por_politica]
    if not deliberadas:
        return []

    todas_cartas = {cid for nome in deliberadas for cid in taxas_por_politica[nome]}
    fracas, universais, identidade, sem_amostra = [], [], [], []

    for cid in sorted(todas_cartas):
        nome = catalogo.get(cid, cid)
        ausentes = [n for n in deliberadas if cid not in taxas_por_politica[n]]
        if ausentes:
            sem_amostra.append(nome)
            continue
        taxas = [taxas_por_politica[n][cid] for n in deliberadas]
        if max(taxas) <= LOW_PICK_RATE:
            fracas.append(nome)
        elif min(taxas) >= UNIVERSAL_PICK_RATE:
            universais.append(nome)
        elif sum(1 for t in taxas if t >= 0.4) == 1:
            identidade.append(nome)

    achados: list[Finding] = []
    if fracas:
        achados.append(Finding(
            sistema, "recusadas por toda intenção", "morta",
            f"{len(fracas)} cartas: " + ", ".join(fracas[:8]),
            len(fracas),
        ))
    if universais:
        achados.append(Finding(
            sistema, "levadas por toda intenção", "SUSPEITA",
            f"{len(universais)} cartas: " + ", ".join(universais[:8])
            + " — não são opção, são a resposta certa",
            len(universais),
        ))
    if identidade:
        achados.append(Finding(
            sistema, "cartas de identidade", "ok",
            f"{len(identidade)} escolhidas por uma intenção só: " + ", ".join(identidade[:8]),
            len(identidade),
        ))
    if sem_amostra:
        achados.append(Finding(
            sistema, "sem amostra suficiente", "referência",
            f"{len(sem_amostra)} cartas oferecidas menos de {MIN_OFFERS_FOR_RATE}x a alguma "
            f"intenção, não classificadas: " + ", ".join(sem_amostra[:8])
            + " — aumente --policy-iterations para julgá-las",
            len(sem_amostra),
        ))
    return achados


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

    # Conteúdo morto e amostra pequena produzem o mesmo sintoma — a carta não
    # aparece —, mas só o primeiro é problema. `generate_passive_choices` é
    # ponderada por raridade: uma Lendária vale 2 contra 60 de uma Comum, então
    # numa amostra curta ela falta por sorteio, não por estar fora da tabela.
    # Só é declarada morta a carta que a amostra deveria ter mostrado.
    total_ofertas = sum(offered.values())
    nunca_ofertadas = [
        catalogo[pid].name for pid in catalogo
        if pid not in offered
        and _ofertas_esperadas(catalogo[pid], catalogo.values(), total_ofertas)
        >= MIN_EXPECTED_OFFERS
    ]
    if nunca_ofertadas:
        achados.append(Finding(
            "passivas", "nunca sorteadas", "morta",
            ", ".join(sorted(nunca_ofertadas)[:6]),
            len(nunca_ofertadas),
        ))
    return achados


def _ofertas_esperadas(carta, catalogo, total_ofertas: int) -> float:
    """Quantas vezes a carta deveria ter aparecido, dada a amostra e a raridade."""
    pesos = sum(RARITY_WEIGHTS.get(c.rarity, 1) for c in catalogo)
    if not pesos:
        return 0.0
    return total_ofertas * RARITY_WEIGHTS.get(carta.rarity, 1) / pesos


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
              per_skill: bool = False, per_passive: bool = False,
              with_pick_policies: bool = True, policy_iterations: int = 40) -> ScoutReport:
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

    if with_pick_policies:
        relatorio.policies = compare_pick_policies(
            policy_iterations, turmas, policy, loadout, seed, max_floor,
        )
        relatorio.findings += analyse_pick_policies(relatorio.policies)

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

    for sistema in ("escolha", "skills", "passivas", "equipamento", "economia",
                    "essência", "eventos"):
        do_sistema = [f for f in report.findings if f.system == sistema]
        if not do_sistema:
            continue
        linhas.append(f"\n{sistema.upper()}")
        # Particiona numa passada. Com `f not in suspeitas`, o `in` comparava
        # `Finding` por valor — dois achados de campos iguais colapsariam num só.
        suspeitas, resto = [], []
        for achado in do_sistema:
            (suspeitas if achado.verdict in ("SUSPEITA", "morta") else resto).append(achado)
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
