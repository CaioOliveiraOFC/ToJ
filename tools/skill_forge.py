"""Ferramenta de autoria do catálogo de skills. Não faz parte do jogo.

Escrever 109 cartas à mão em JSON é escrever 109 oportunidades de errar um peso,
esquecer um campo obrigatório ou inventar um `power` no chute. Esta ferramenta
faz três coisas que a mão não faz bem:

1. **Deriva `power` do orçamento pretendido.** O autor diz "quero uma carta de
   180% do ataque básico da classe"; a ferramenta resolve o `power` que produz
   isso contra o personagem de referência. Sem ela, `power` viraria número
   mágico — e um mágico diferente por classe, porque a Agilidade 92 do Ladino e
   a Força 191 do Guerreiro não são o mesmo número.

2. **Fecha as portas que o motor deixa abertas.** `secondary` em carta de buff é
   dado morto (o motor só o consulta nos ramos de dano e status);
   `accuracy_modifier` fora de carta de dano idem; `chance != 100` fora de
   status idem. São os placebos clássicos desta base, e aqui eles são erro de
   autoria, não descoberta em playtest.

3. **Audita similaridade conceitual.** 150 cartas não podem ser 40 ideias e 110
   renomes. A assinatura de uma carta é o que ela DECIDE — classe, tipo, de
   quais atributos nasce, o que aplica, o que exige, quando rende mais. Duas
   cartas com a mesma assinatura são a mesma carta com dois nomes.

Uso: `python tools/skill_forge.py` valida e reescreve o catálogo a partir dos
lotes em `tools/skill_batches/`.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.skill_validator import (  # noqa: E402
    _referencia,
    monster_reference,
    offensive_budget,
    skill_signature,
    validate,
)
from src.content.skills_loader import card_from_json  # noqa: E402

SKILLS_JSON = RAIZ / "src" / "data" / "skills.json"
MONSTERS_JSON = RAIZ / "src" / "data" / "monsters.json"

# Como a condição situacional é dita ao jogador. O texto entra na descrição, e a
# integridade de dados exige que o número do bônus apareça nela.
TEXTO_DA_CONDICAO = {
    "target_healthy": "contra alvo intacto",
    "target_wounded": "contra alvo ferido",
    "target_afflicted": "contra alvo sob efeito",
    "target_controlled": "contra alvo sem ação",
    "caster_wounded": "quando você está ferido",
}


@dataclass
class Carta:
    """Uma carta em forma de intenção. `power` e o JSON saem daqui."""

    id: str
    name: str
    cls: str
    rar: str
    lvl: int
    tipo: str
    desc: str
    # dano
    esc: str = ""  # "st" | "ag.6+st.4"
    bud: int = 0  # orçamento ofensivo pretendido, em % do ataque da referência
    cond: str = ""
    bonus: int = 0
    acc: int = 0
    # efeito
    ev: int | str = 0  # buff: valor; status: nome do efeito; heal: % do HP
    stat: str = ""  # buff: atributo modificado
    dur: int = 0
    chance: int = 100
    sec: tuple | None = None  # (efeito, chance, duração) ou (efeito, chance, duração, intens.)
    # custo e acesso
    cd: int = 2
    mp: float = 6.0
    req: dict | None = None
    inicial: bool = False
    papel: str = ""  # arquétipo, só para carta de monstro

    def escala(self) -> list[dict]:
        if not self.esc:
            return []
        termos = []
        for parte in self.esc.split("+"):
            parte = parte.strip()
            if "." in parte:
                nome, peso = parte.split(".", 1)
                termos.append({"stat": nome, "weight": float("0." + peso)})
            else:
                termos.append({"stat": parte, "weight": 1.0})
        return termos

    def referencia(self) -> dict:
        return monster_reference(self.papel) if self.papel else _referencia(self.cls)

    def power(self) -> float:
        """O `power` que entrega o orçamento pedido para esta referência."""
        termos = self.escala()
        if not termos or not self.bud:
            return 0.0
        ref = self.referencia()
        soma = sum(ref[t["stat"]] * t["weight"] for t in termos)
        alvo = self.bud / 100 * ref["avg"] * (1 + self.bonus / 100) ** -1
        return round(alvo / soma, 3)

    def descricao(self) -> str:
        """A descrição do jogador, com o que a integridade de dados exige nela.

        Carta de dano precisa citar o bônus condicional (é ele que decide a
        jogada); carta de buff precisa citar o próprio valor (ele é percentual
        do atributo, então esconder o número esconde o efeito).
        """
        texto = self.desc.rstrip()
        if self.tipo == "damage" and self.cond:
            marca = f"+{self.bonus}%"
            if str(self.bonus) not in texto:
                texto = f"{texto.rstrip('.')} {marca} {TEXTO_DA_CONDICAO[self.cond]}."
        if self.tipo == "buff" and str(self.ev) not in texto:
            texto = f"{texto.rstrip('.')} ({self.ev}%)."
        return texto

    def json(self) -> dict:
        d = {
            "id": self.id,
            "name": self.name,
            "level_required": self.lvl,
            "mana_cost": max(1, int(self.mp * 3)),
            "effect_type": self.tipo,
            "effect_value": self.ev,
            "description": self.descricao(),
            "target": "self" if self.tipo in ("buff", "heal", "damage_reduction") else "enemy",
            "duration": self.dur,
            "chance": self.chance,
            "rarity": self.rar,
            "cooldown": self.cd,
            "effect_stat": self.stat,
            "mana_cost_percent": self.mp,
            "accuracy_modifier": self.acc,
        }
        if self.papel:
            # A carta de monstro não declara classe nem nível de aquisição: os
            # padrões vivem em `archetypes.PADROES_DE_MONSTRO`.
            for morto in ("level_required", "rarity"):
                d.pop(morto, None)
            # E paga em MANA ABSOLUTA, como as cartas de monstro que já existem.
            # Misturar as duas formas dentro do mesmo arquétipo faria o bicho
            # pagar 15 fixos por uma skill e 7% da referência por outra. Migrar
            # o monstro para custo percentual é decisão de balanceamento, e não
            # cabe num lote de conteúdo — o validador continua creditando certo,
            # porque converte o absoluto contra a mana da referência.
            d.pop("mana_cost_percent", None)
            d["mana_cost"] = int(self.mp)
        else:
            d["skill_class"] = self.cls
            d["is_initial"] = self.inicial
        if self.tipo == "damage":
            d["bonus_condition"] = self.cond
            d["bonus_percent"] = self.bonus
            d["scaling"] = self.escala()
            d["power"] = self.power()
        if self.sec:
            efeito, chance, duracao = self.sec[0], self.sec[1], self.sec[2]
            d["secondary"] = {"effect": efeito, "chance": chance, "duration": duracao}
            if len(self.sec) > 3:
                d["secondary"]["intensity"] = self.sec[3]
        if self.req:
            d["requires"] = dict(self.req)
        return d


# --- as portas que o motor deixa abertas -----------------------------------
#
# Cada regra aqui é um placebo que esta base já pagou para descobrir. Elas não
# são gosto: são o conjunto de campos que o motor LÊ em cada ramo de
# `combat.apply_skill`. Fora do ramo certo, o campo fica no JSON e não acontece.

RAMOS_QUE_LEEM_SECUNDARIO = ("damage", "status")
RAMOS_QUE_LEEM_ACERTO = ("damage",)


# O que pode dar identidade a uma carta de dano. A condição situacional é UMA
# das formas, e por um tempo ela foi exigida de todas — o que é forte demais:
# uma carta pode se distinguir pelo efeito que aplica, pela mira, pelo
# equipamento que pede, pela escala de onde nasce, ou pelo preço. Exigir a
# condição de todas empurrava o catálogo para uma forma só.
#
# O que continua proibido é a carta de dano SEM NENHUMA delas: essa é
# literalmente um ataque básico mais caro, e a escolha entre ela e as outras
# vira aritmética fixa.
def _identidade_da_carta(c: Carta) -> list[str]:
    marcas = []
    if c.cond and c.bonus:
        marcas.append("condição situacional")
    if c.sec:
        marcas.append("efeito secundário")
    if c.acc:
        marcas.append("mira própria")
    if c.req:
        marcas.append("requisito de equipamento")
    return marcas


def problemas_de_autoria(c: Carta) -> list[str]:
    erros = []
    if c.tipo == "damage":
        if not c.esc or not c.bud:
            erros.append("carta de dano sem escala ou sem orçamento")
        if not _identidade_da_carta(c):
            erros.append(
                "carta de dano sem nenhuma identidade (condição, efeito, mira ou "
                "requisito): é um ataque básico mais caro"
            )
        if bool(c.cond) != bool(c.bonus):
            erros.append("condição sem bônus, ou bônus sem condição")
    else:
        if c.esc or c.bud:
            erros.append(f"`scaling` em carta de {c.tipo}: o motor só o usa em dano")
    if c.sec and c.tipo not in RAMOS_QUE_LEEM_SECUNDARIO:
        erros.append(f"`secondary` em carta de {c.tipo}: o motor não o aplica nesse ramo")
    if c.acc and c.tipo not in RAMOS_QUE_LEEM_ACERTO:
        erros.append(f"`accuracy_modifier` em carta de {c.tipo}: só o golpe consulta o acerto")
    if c.chance != 100 and c.tipo != "status":
        erros.append("`chance` != 100 fora de status: o motor ignora o campo")
    if c.tipo == "buff" and not c.stat:
        erros.append("buff sem `effect_stat`: o motor não saberia o que aumentar")
    if c.tipo in ("buff", "status", "heal", "damage_reduction") and not c.ev:
        erros.append(f"carta de {c.tipo} sem `effect_value`")
    if c.tipo in ("buff", "status", "damage_reduction") and not c.dur:
        erros.append(f"carta de {c.tipo} sem duração")
    return erros


# --- auditoria de similaridade ---------------------------------------------


def assinatura(c: Carta) -> tuple:
    """A assinatura da carta, pela MESMA regra que o jogo aplica.

    A lei mora em `content/skill_validator.skill_signature`: ela vale para o
    catálogo publicado e é verificada por teste. Aqui só se traduz a intenção de
    autoria para uma carta de verdade antes de perguntar.
    """
    return skill_signature(card_from_json(_json_completo(c)), c.papel)


def _json_completo(c: Carta) -> dict:
    dados = c.json()
    if c.papel:
        from src.content.factories.archetypes import PADROES_DE_MONSTRO

        return {**PADROES_DE_MONSTRO, **dados}
    return dados


@dataclass
class Relatorio:
    aprovadas: list = field(default_factory=list)
    erros: list = field(default_factory=list)
    clones: list = field(default_factory=list)
    # Clones que já estavam no jogo antes deste lote. Não bloqueiam — não foi
    # este lote que os criou —, mas aparecem no relatório para não passarem
    # como conteúdo aprovado.
    herdados: list = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.erros and not self.clones


def auditar(cartas: list[Carta], existentes: list | None = None) -> Relatorio:
    """`existentes` aceita `SkillCard` ou pares `(papel, SkillCard)`."""
    """Valida autoria, valida orçamento e caça clones conceituais."""
    rel = Relatorio()
    vistos: dict[tuple, str] = {}
    ids: Counter = Counter()

    for antiga in existentes or []:
        papel, antiga = antiga if isinstance(antiga, tuple) else ("", antiga)
        chave = _assinatura_de_carregada(antiga, papel)
        if chave in vistos:
            rel.herdados.append(f"{antiga.id} repete {vistos[chave]} (as duas já no catálogo)")
        else:
            vistos[chave] = antiga.id

    for c in cartas:
        ids[c.id] += 1
        for problema in problemas_de_autoria(c):
            rel.erros.append(f"{c.id}: {problema}")
        dados = c.json()
        if c.papel:
            from src.content.factories.archetypes import PADROES_DE_MONSTRO

            dados = {**PADROES_DE_MONSTRO, **dados}
        veredito = validate(card_from_json(dados), reference=c.referencia() if c.papel else None)
        if not veredito.ok:
            rel.erros.append(f"{c.id}: {'; '.join(veredito.erros)}")
        else:
            rel.aprovadas.append((c, veredito))
        chave = assinatura(c)
        if chave in vistos:
            rel.clones.append(f"{c.id} é conceitualmente a mesma carta que {vistos[chave]}")
        else:
            vistos[chave] = c.id

    for repetido, n in ids.items():
        if n > 1:
            rel.erros.append(f"id repetido {n}x: {repetido}")
    return rel


def _assinatura_de_carregada(s, papel: str = "") -> tuple:
    """Apelido de `skill_signature`, para os pontos que já liam este nome."""
    return skill_signature(s, papel)


def imprimir(rel: Relatorio, titulo: str) -> bool:
    print(
        f"\n=== {titulo}: {len(rel.aprovadas)} aprovadas, "
        f"{len(rel.erros)} erros, {len(rel.clones)} clones"
    )
    for e in rel.erros:
        print("  ERRO  ", e)
    for c in rel.clones:
        print("  CLONE ", c)
    for c in rel.herdados:
        print("  HERDADO", c)
    if rel.aprovadas:
        orcamentos = sorted(v.orcamento for _, v in rel.aprovadas)
        print(
            f"  orçamento: min {orcamentos[0]}  mediana {orcamentos[len(orcamentos) // 2]}  "
            f"max {orcamentos[-1]}  (teto {rel.aprovadas[0][1].teto})"
        )
    return rel.ok


# --- escrita ---------------------------------------------------------------

# Legendary é jackpot, e jackpot precisa ser raro: uma por classe, três no jogo
# inteiro. O catálogo tinha SEIS. Estas três descem para Epic — e a escolha não
# é aritmética, é sobre o que cada carta entrega:
#
#   `imortal`    buff de redução de dano. Um buff, por melhor que seja, não
#                produz o momento "eu dei muita sorte" — ele produz um turno
#                mais seguro. Epic é o lugar dele.
#   `esmagar`    ótima carta de dano com atordoamento, mas orçamento 275 contra
#                371 e 373 das capstones de Mago e Ladino. Como Legendary do
#                Guerreiro ela seria a mais fraca das três por larga margem;
#                como Epic, é uma das melhores do jogo.
#   `ressurgir`  cura de 55%. Cura forte é sustento, não jackpot, e o jogo já
#                trata cura direta como recurso raro.
#   `fantasma`   invisibilidade por dois turnos. É utilidade excelente e
#                orçamento -9: não há como chamar isso de prêmio máximo.
#
# `apocalipse` (371) e `morte_subita` (373) ficam: são as duas cartas que já
# entregavam a sensação de jackpot. `fortaleza_viva` (384) é a nova do Guerreiro.
REBAIXADAS_PARA_EPIC = ("imortal", "esmagar", "ressurgir", "fantasma")


def escrever_skills(novas: list[Carta]) -> None:
    """Acrescenta as cartas novas a `skills.json` e aplica os rebaixamentos."""
    dados = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))
    for s in dados["skills"]:
        if s["id"] in REBAIXADAS_PARA_EPIC:
            s["rarity"] = "Epic"
    dados["skills"] += [c.json() for c in novas]
    SKILLS_JSON.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def escrever_monstros(novas: list[Carta]) -> None:
    """Acrescenta as cartas novas ao arquétipo de cada uma."""
    dados = json.loads(MONSTERS_JSON.read_text(encoding="utf-8"))
    for c in novas:
        dados["archetypes"][c.papel].setdefault("skills", []).append(c.json())
    MONSTERS_JSON.write_text(
        json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def razoes_por_classe(c: Carta) -> dict:
    """Quanto a carta vale em ATAQUES BÁSICOS, para cada classe que pode usá-la.

    É a régua do `test_toda_skill_de_dano_vale_mais_que_bater`: abaixo dela,
    gastar mana e recarga é matematicamente pior que não gastar nada. Uma carta
    de classe é medida só contra a classe dela; uma Neutral, contra as três — e
    a pior das três é a que decide, porque é para essa classe que a carta seria
    uma armadilha.
    """
    from src.content.skills_loader import card_from_json
    from src.entities.heroes import Mage, Rogue, Warrior
    from src.mechanics.combat import basic_attack_power, skill_damage_base

    if c.tipo != "damage":
        return {}
    # Medido com um HERÓI DE VERDADE no nível da carta, e não contra o vetor de
    # referência: é assim que o guardrail mede, e uma ferramenta de autoria que
    # medisse de outro jeito aprovaria cartas que o teste depois reprova. O
    # vetor de referência inclui o equipamento esperado; o herói aqui está nu, e
    # a proporção entre atributo e ataque básico não é a mesma nos dois.
    classes = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}
    alvos = classes if c.cls == NEUTRAL else {c.cls: classes[c.cls]}
    carta = card_from_json(c.json())
    saida = {}
    for nome, fabrica in alvos.items():
        h = fabrica("Medida")
        h.set_level(max(1, c.lvl))
        saida[nome] = skill_damage_base(h, carta) / basic_attack_power(h)
    return saida


NEUTRAL = "Neutral"


def calibrar(c: Carta, piso: float = 1.80) -> int:
    """O menor `bud` que faz a carta valer `piso` ataques básicos na PIOR classe.

    O piso existe para que gastar mana e recarga seja melhor que não gastar
    nada. Uma carta de classe é medida contra a classe dela; uma Neutral contra
    as três, e vale a pior — é para essa classe que ela seria uma armadilha.

    **1,80 é margem de autoria, não lei do jogo.** O contrato está em
    `MIN_SKILL_TO_BASIC_RATIO` (1,7) e continua onde sempre esteve; escrever um
    pouco acima dele evita que um arredondamento derrube a carta. Subir o
    contrato junto tornaria o ataque básico irrelevante, e ele precisa continuar
    sendo uma jogada de verdade — é o que dá sentido a economizar mana.
    """
    if c.tipo != "damage":
        return c.bud
    baixo, alto = c.bud, max(c.bud, 50)
    while min(razoes_por_classe(_com_bud(c, alto)).values()) < piso:
        alto = int(alto * 1.4) + 5
        if alto > 4000:
            raise ValueError(f"{c.id}: nenhum orçamento razoável alcança {piso}")
    while alto - baixo > 1:
        meio = (alto + baixo) // 2
        if min(razoes_por_classe(_com_bud(c, meio)).values()) < piso:
            baixo = meio
        else:
            alto = meio
    return alto


def _com_bud(c: Carta, bud: int) -> Carta:
    from dataclasses import replace

    return replace(c, bud=bud)


# --- preço: a regra que torna a dominação impossível ------------------------
#
# Uma carta é DOMINADA quando custa o mesmo ou mais e entrega o mesmo ou menos.
# Perseguir cada par com mais orçamento não resolve: duas cartas de custo
# idêntico se alternam para sempre, cada correção invertendo a anterior.
#
# A regra que fecha a porta de uma vez é de PREÇO: dentro de uma classe, custar
# mais tem de significar entregar mais. Com o custo estritamente crescente no
# dano, `custo_a >= custo_b` só é verdade quando `teto_a >= teto_b`, e a
# conjunção que define dominação nunca fecha.
#
# A curva de preço não é inventada: ela é lida das cartas que JÁ existem, que a
# respeitam (Golpe Poderoso 140% por 4,5% de mana; Apocalipse 431% por 20,6%).
# As cartas novas são interpoladas nessa mesma curva.


def _curva_da_classe(cls: str, existentes: list) -> list[tuple[float, float]]:
    """Pares (teto de dano, custo em % de mana) das cartas já publicadas."""
    pontos = [
        (offensive_budget(s), float(s.mana_cost_percent or s.mana_cost))
        for s in existentes
        if s.effect_type == "damage" and s.skill_class == cls and s.scaling
    ]
    return sorted(set(pontos))


def _interpolar(curva: list[tuple[float, float]], teto: float) -> float:
    """Custo que a curva da classe cobra por este nível de dano."""
    if not curva:
        return max(4.0, teto / 22)
    if teto <= curva[0][0]:
        return curva[0][1] * teto / max(1.0, curva[0][0])
    if teto >= curva[-1][0]:
        return curva[-1][1] * teto / max(1.0, curva[-1][0])
    for (d0, c0), (d1, c1) in zip(curva, curva[1:]):
        if d0 <= teto <= d1:
            fatia = (teto - d0) / max(1e-9, d1 - d0)
            return c0 + fatia * (c1 - c0)
    return curva[-1][1]


def precificar(minhas: list[Carta], existentes: list) -> list[str]:
    """Põe cada carta nova na curva de preço da classe dela.

    Também separa tetos empatados: duas cartas com exatamente o mesmo dano e o
    mesmo custo continuariam sendo a mesma escolha, e o desempate volta a ser a
    ordem do arquivo.
    """
    notas = []
    por_classe: dict[str, list[Carta]] = {}
    for c in minhas:
        if c.tipo == "damage":
            por_classe.setdefault(c.cls, []).append(c)

    for cls, cartas in por_classe.items():
        curva = _curva_da_classe(cls, existentes)
        ocupados = {offensive_budget(s) for s in existentes if s.skill_class == cls}
        for c in sorted(cartas, key=lambda x: x.bud):
            while c.bud in ocupados:
                c.bud += 1
            ocupados.add(c.bud)
            novo = round(_interpolar(curva, c.bud), 2)
            if abs(novo - c.mp) > 0.05:
                notas.append(f"{c.id}: mana {c.mp} -> {novo} (dano {c.bud}%)")
                c.mp = novo
    return notas


def preparar(minhas: list[Carta], existentes: list) -> list[str]:
    """Fecha as duas contas que uma carta de dano precisa passar antes de existir.

    1. PISO: gastar mana e recarga tem de render mais que o ataque básico, que é
       gratuito. Abaixo disso a carta é um imposto, e a linha ótima do jogador
       passa a ser não usar skill nenhuma.
    2. PREÇO: dentro da classe, custar mais tem de significar entregar mais.
       É o que impede uma carta de nascer dominada — pior em tudo que outra que
       o jogador já tem na mão.

    Os `bud` e `mp` escritos nos lotes são INTENÇÃO; os valores finais saem
    daqui. É de propósito: ajustar 36 números à mão a cada carta nova é como a
    tabela de preços ficou com 13 pares dominados da primeira vez.
    """
    notas = []
    for c in minhas:
        if c.tipo == "damage":
            antes = c.bud
            novo = calibrar(c)
            if novo != antes:
                notas.append(f"{c.id}: dano {antes}% -> {novo}% (piso de 1,8 ataques básicos)")
                c.bud = novo
    notas += precificar(minhas, existentes)
    return notas
