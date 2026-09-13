"""Núcleo de efeitos: um catálogo, um resolvedor, uma linguagem.

Antes disto, "sangramento" era três coisas diferentes conforme quem aplicava: a
skill escrevia um dicionário, o monstro escrevia outro, e o item nem conseguia
aplicar. Cada fonte carregava um pedaço da regra, e mudar a duração do veneno
significava caçar o número em três arquivos.

Aqui a FONTE só declara intenção — "quero aplicar bleed, com esta chance, esta
intensidade, esta duração, vindo de mim". O catálogo diz o que `bleed` É, e o
resolvedor decide se entra, como empilha, quanto dura e como termina.

    FONTE (equipamento / encantamento / skill / passiva / monstro)
        ↓  declara: efeito, chance, intensidade, duração, source_id
    NÚCLEO
        ↓  decide: resistência, stack, refresh, teto, piso, tick, término
    ENTIDADE

Vive em `shared/` porque `entities/` precisa resolver atributo e `mechanics/`
precisa resolver golpe, e `shared/` é a única camada que as duas importam. Não
depende de nada do projeto: lê o estado das entidades por duck typing.
"""

from __future__ import annotations

from dataclasses import dataclass

# --- famílias -------------------------------------------------------------
# A família decide COMO o efeito é resolvido, não o que ele faz.
FAMILY_ATTRIBUTE = "attribute"  # percentual sobre um atributo (st/mg/ag/df)
FAMILY_RESOURCE = "resource"  # percentual sobre o teto de HP/MP, temporário
FAMILY_DOT = "dot"  # dano por turno, empilhável
FAMILY_CONTROL = "control"  # rouba o turno
FAMILY_ACCURACY = "accuracy"  # atrapalha a ação ofensiva
FAMILY_DRAIN = "drain"  # drena recurso ATUAL por turno
FAMILY_CONCEALMENT = "concealment"  # atrapalha QUEM ATACA o portador

# --- regras de empilhamento ------------------------------------------------
# BY_SOURCE: fontes diferentes somam, a mesma fonte RENOVA. É o que impede a
#   mesma skill lançada quatro vezes virar +40% — a contribuição dela é uma só.
# COUNT: acumula stacks até o teto; nova aplicação também renova a duração.
# REFRESH: não acumula nada, só estende. Controle é assim: dois atordoamentos
#   não são um atordoamento mais forte, são o mesmo turno roubado.
STACK_BY_SOURCE = "by_source"
STACK_COUNT = "count"
STACK_REFRESH = "refresh"

# Piso estrutural dos atributos. Nenhum debuff, por maior que seja o acúmulo,
# derruba Força/Magia/Agilidade/Defesa abaixo desta fração da base. Sem ele,
# empilhar redutores vira um combo que zera o personagem — e um jogo em que o
# alvo certo simplesmente não joga não tem counterplay, tem espectador.
MIN_ATTRIBUTE_RATIO = 0.10

# Quantos pontos percentuais de acerto o medo tira de uma ação OFENSIVA, e
# quantos a precisão devolve. Os dois vivem na MESMA família e na mesma soma:
# `Precision +20` com `Fear -10` resolve `+10`, e não "o último a chegar vence".
FEAR_ACCURACY_PENALTY = 20
PRECISION_ACCURACY_BONUS = 20

# Quanto acerto se perde ao atacar um alvo escondido. Espelho do medo, do outro
# lado da troca: um atrapalha quem ataca, o outro protege quem é atacado.
CONCEALMENT_PENALTY = 45


@dataclass(frozen=True)
class EffectDefinition:
    """O que um efeito É. Global, imutável, um por nome."""

    effect_id: str
    family: str
    label: str
    positive: bool
    stack_rule: str
    stat: str | None = None
    max_stacks: int = 1
    default_duration: int = 3
    # Percentual por stack: do atributo (ATTRIBUTE/RESOURCE) ou do HP máximo
    # (DOT). A fonte pode sobrepor; o catálogo dá o valor de referência.
    default_intensity: float = 0.0
    breaks_on_damage: bool = False
    resistible: bool = True

    @property
    def opposes(self) -> str | None:
        """O par oposto, quando existe. `Empowered` ↔ `Weakened`."""
        return OPPOSING_PAIRS.get(self.effect_id)


def _atributo(effect_id, label, stat, positive, intensidade):
    return EffectDefinition(
        effect_id=effect_id,
        family=FAMILY_ATTRIBUTE,
        label=label,
        positive=positive,
        stack_rule=STACK_BY_SOURCE,
        stat=stat,
        default_duration=3,
        default_intensity=intensidade,
        resistible=not positive,
    )


def _recurso(effect_id, label, stat, positive, intensidade):
    return EffectDefinition(
        effect_id=effect_id,
        family=FAMILY_RESOURCE,
        label=label,
        positive=positive,
        stack_rule=STACK_BY_SOURCE,
        stat=stat,
        default_duration=3,
        default_intensity=intensidade,
        resistible=not positive,
    )


# --- o catálogo ------------------------------------------------------------
# Os dois lados sempre: para cada amplificação existe a redução oposta, e o
# saldo é a soma delas. É a filosofia do jogo escrita em dados — amplificar o
# forte do personagem e reduzir o forte do adversário, com counterplay dos dois
# lados.
CATALOG: dict[str, EffectDefinition] = {}


def _registrar(*definicoes: EffectDefinition) -> None:
    for d in definicoes:
        CATALOG[d.effect_id] = d


_registrar(
    # atributos, em percentual
    _atributo("empowered", "Fortalecido", "st", True, 20.0),
    _atributo("weakened", "Enfraquecido", "st", False, 20.0),
    _atributo("arcane_surge", "Surto Arcano", "mg", True, 20.0),
    _atributo("hexed", "Amaldiçoado", "mg", False, 20.0),
    _atributo("quickened", "Acelerado", "ag", True, 20.0),
    _atributo("slowed", "Lentificado", "ag", False, 20.0),
    _atributo("fortified", "Fortificado", "df", True, 20.0),
    _atributo("vulnerable", "Vulnerável", "df", False, 20.0),
    # recursos: teto de HP/MP, temporário e reversível
    _recurso("vitality", "Vitalidade", "hp", True, 20.0),
    _recurso("frailty", "Fragilidade", "hp", False, 20.0),
    _recurso("focused", "Concentrado", "mp", True, 20.0),
    _recurso("clouded", "Mente Turva", "mp", False, 20.0),
    # dano por turno: identidades opostas de propósito
    EffectDefinition(
        effect_id="bleed",
        family=FAMILY_DOT,
        label="Sangramento",
        positive=False,
        stack_rule=STACK_COUNT,
        max_stacks=5,
        default_duration=2,  # curto
        default_intensity=4.0,  # % do HP máximo por stack, por turno — forte
    ),
    EffectDefinition(
        effect_id="poison",
        family=FAMILY_DOT,
        label="Veneno",
        positive=False,
        stack_rule=STACK_COUNT,
        max_stacks=5,
        default_duration=5,  # longo
        default_intensity=1.5,  # fraco por turno, mas insiste
    ),
    # controle: renova, nunca empilha
    EffectDefinition(
        effect_id="stun",
        family=FAMILY_CONTROL,
        label="Atordoado",
        positive=False,
        stack_rule=STACK_REFRESH,
        default_duration=1,
    ),
    EffectDefinition(
        effect_id="frozen",
        family=FAMILY_CONTROL,
        label="Congelado",
        positive=False,
        stack_rule=STACK_REFRESH,
        default_duration=2,
    ),
    EffectDefinition(
        effect_id="sleep",
        family=FAMILY_CONTROL,
        label="Adormecido",
        positive=False,
        stack_rule=STACK_REFRESH,
        default_duration=3,
        breaks_on_damage=True,
    ),
    # precisão: o lado positivo do medo, e o par dele. Não é `never_miss` — o
    # teto global de acerto continua valendo, por maior que seja o acúmulo.
    EffectDefinition(
        effect_id="precision",
        family=FAMILY_ACCURACY,
        label="Preciso",
        positive=True,
        stack_rule=STACK_BY_SOURCE,
        default_duration=3,
        default_intensity=float(PRECISION_ACCURACY_BONUS),
        resistible=False,
    ),
    # medo: não mexe em Agilidade, mexe na confiabilidade da ação ofensiva
    EffectDefinition(
        effect_id="fear",
        family=FAMILY_ACCURACY,
        label="Amedrontado",
        positive=False,
        stack_rule=STACK_REFRESH,
        default_duration=3,
        default_intensity=float(FEAR_ACCURACY_PENALTY),
    ),
    # ocultação: o espelho defensivo do medo. Positivo para quem o tem, e lido
    # por quem ataca — é a única entrada do catálogo cujo efeito acontece na
    # ficha do OUTRO, e por isso tem família própria em vez de virar evasão.
    EffectDefinition(
        effect_id="invisible",
        family=FAMILY_CONCEALMENT,
        label="Invisível",
        positive=True,
        stack_rule=STACK_REFRESH,
        default_duration=2,
        default_intensity=float(CONCEALMENT_PENALTY),
        resistible=False,
    ),
    # dreno de recurso ATUAL — perda real, não teto temporário
    EffectDefinition(
        effect_id="mana_burn",
        family=FAMILY_DRAIN,
        label="Queima de Mana",
        positive=False,
        stack_rule=STACK_REFRESH,
        stat="mp",
        default_duration=2,
        default_intensity=12.0,
    ),
)

# Pares opostos. Coexistem e se compensam: `+20%` e `-15%` resolvem `+5%`, e não
# "o último ganha". Compensação é o que dá counterplay aos dois lados.
OPPOSING_PAIRS: dict[str, str] = {}
for _a, _b in (
    ("precision", "fear"),
    ("empowered", "weakened"),
    ("arcane_surge", "hexed"),
    ("quickened", "slowed"),
    ("fortified", "vulnerable"),
    ("vitality", "frailty"),
    ("focused", "clouded"),
):
    OPPOSING_PAIRS[_a] = _b
    OPPOSING_PAIRS[_b] = _a


def definition(effect_id: str) -> EffectDefinition | None:
    """A definição global do efeito, ou `None` se o nome não existe."""
    return CATALOG.get(effect_id)


def negative_effects() -> tuple[str, ...]:
    """Os efeitos resistíveis, na grafia que o motor usa."""
    return tuple(d.effect_id for d in CATALOG.values() if d.resistible)


def effects_of_family(family: str) -> tuple[str, ...]:
    return tuple(d.effect_id for d in CATALOG.values() if d.family == family)


class EffectInstance(dict):
    """Um efeito ATIVO numa entidade.

    É um `dict` de propósito, e não só por compatibilidade: o estado ativo é
    serializado no save e lido pela UI, e um objeto opaco exigiria conversão nas
    duas pontas. As chaves são o formato em disco; as propriedades são a leitura
    de quem escreve regra.

    `value` espelha `intensity` porque o motor já lia essa chave antes do núcleo
    existir — um alias, não um segundo campo.
    """

    def __init__(
        self,
        effect: str,
        source_id: str = "",
        intensity: float = 0.0,
        duration: int = 1,
        stacks: int = 1,
    ) -> None:
        super().__init__(
            effect=str(effect),
            source_id=str(source_id),
            intensity=float(intensity),
            value=float(intensity),
            duration=int(duration),
            stacks=int(stacks),
        )

    @property
    def effect(self) -> str:
        return str(self["effect"])

    @property
    def source_id(self) -> str:
        return str(self["source_id"])

    @property
    def intensity(self) -> float:
        return float(self["intensity"])

    @intensity.setter
    def intensity(self, valor: float) -> None:
        self["intensity"] = float(valor)
        self["value"] = float(valor)

    @property
    def duration(self) -> int:
        return int(self["duration"])

    @duration.setter
    def duration(self, valor: int) -> None:
        self["duration"] = int(valor)

    @property
    def stacks(self) -> int:
        return int(self["stacks"])

    @stacks.setter
    def stacks(self, valor: int) -> None:
        self["stacks"] = int(valor)

    @property
    def definition(self) -> EffectDefinition | None:
        return CATALOG.get(self.effect)

    @property
    def total_intensity(self) -> float:
        """Intensidade vezes stacks. É o que o resolvedor consome."""
        return self.intensity * self.stacks


def _store(entity) -> dict:
    """O dicionário de efeitos ativos da entidade, criado sob demanda."""
    ativo = getattr(entity, "active_effects", None)
    if ativo is None:
        ativo = {}
        entity.active_effects = ativo
    return ativo


def instance_key(effect_id: str, source_id: str) -> str:
    """Onde a instância mora no estado ativo.

    Efeitos que somam por fonte precisam de uma entrada por fonte; o resto tem
    uma entrada só, com o nome do efeito, que é o que a UI e o save já esperam.
    """
    definicao = CATALOG.get(effect_id)
    if definicao is not None and definicao.stack_rule == STACK_BY_SOURCE:
        return f"{effect_id}#{source_id}"
    return effect_id


def apply_effect(
    entity,
    effect_id: str,
    *,
    source_id: str = "",
    intensity: float | None = None,
    duration: int | None = None,
) -> EffectInstance | None:
    """Aplica (ou renova) um efeito. Devolve a instância ativa, ou `None`.

    Quem chama já decidiu que o efeito PEGOU — resistência é resolvida antes,
    por `effective_chance`, porque a rolagem pertence a quem tem o RNG.

    Aqui mora o resto: qual regra de empilhamento vale, se a duração renova, se
    o stack sobe, e qual entrada do estado ativo é tocada.
    """
    definicao = CATALOG.get(effect_id)
    if definicao is None:
        return None

    valor = definicao.default_intensity if intensity is None else float(intensity)
    turnos = definicao.default_duration if duration is None else int(duration)
    if turnos <= 0:
        return None

    adopt_legacy(entity)
    ativo = _store(entity)
    chave = instance_key(effect_id, source_id)
    atual = ativo.get(chave)

    if not isinstance(atual, EffectInstance):
        nova = EffectInstance(effect_id, source_id, valor, turnos, stacks=1)
        ativo[chave] = nova
        return nova

    # Já existia. O que acontece depende da regra do catálogo.
    if definicao.stack_rule == STACK_COUNT:
        atual.stacks = min(definicao.max_stacks, atual.stacks + 1)
        atual.intensity = valor
    elif definicao.stack_rule == STACK_BY_SOURCE:
        # Mesma fonte: substitui a contribuição dela, nunca soma em cima. É o
        # que impede a mesma skill lançada quatro vezes virar uma escada.
        atual.intensity = valor
    # A duração sempre renova, em qualquer regra: reaplicar um efeito nunca
    # deve deixar o alvo mais perto de se livrar dele.
    atual.duration = max(atual.duration, turnos)
    return atual


def remove_effect(entity, effect_id: str, source_id: str | None = None) -> list[EffectInstance]:
    """Retira o efeito. Sem `source_id`, retira todas as fontes dele."""
    ativo = _store(entity)
    removidas = []
    for chave, instancia in list(ativo.items()):
        if not isinstance(instancia, EffectInstance):
            continue
        if instancia.effect != effect_id:
            continue
        if source_id is not None and instancia.source_id != source_id:
            continue
        removidas.append(ativo.pop(chave))
    return removidas


def instances(entity, family: str | None = None) -> list[EffectInstance]:
    """As instâncias ativas, opcionalmente filtradas por família.

    Adota estado legado antes de ler: um efeito escrito como dicionário simples
    precisa contar para o resolvedor, ou o save antigo carrega um veneno que não
    envenena.
    """
    adopt_legacy(entity)
    resultado = []
    for instancia in getattr(entity, "active_effects", {}).values():
        if not isinstance(instancia, EffectInstance):
            continue
        if family is not None:
            definicao = instancia.definition
            if definicao is None or definicao.family != family:
                continue
        resultado.append(instancia)
    return resultado


def has_effect(entity, effect_id: str) -> bool:
    return any(i.effect == effect_id for i in instances(entity))


def stacks_of(entity, effect_id: str) -> int:
    return sum(i.stacks for i in instances(entity) if i.effect == effect_id)


def attribute_percent(entity, stat: str) -> float:
    """Saldo percentual dos efeitos de atributo sobre `stat`.

    Positivos e negativos somam no MESMO lugar: `+20` e `-15` resolvem `+5`.
    Compensação matemática, e não "o último a chegar decide" — é o que faz um
    dispel valer a pena sem existir ainda, e o que dá counterplay aos dois lados.
    """
    total = 0.0
    for instancia in instances(entity, FAMILY_ATTRIBUTE):
        definicao = instancia.definition
        if definicao is None or definicao.stat != stat:
            continue
        total += instancia.total_intensity if definicao.positive else -instancia.total_intensity
    return total


def resource_percent(entity, stat: str) -> float:
    """Saldo percentual dos efeitos de recurso sobre o teto de `hp`/`mp`."""
    total = 0.0
    for instancia in instances(entity, FAMILY_RESOURCE):
        definicao = instancia.definition
        if definicao is None or definicao.stat != stat:
            continue
        total += instancia.total_intensity if definicao.positive else -instancia.total_intensity
    return total


def apply_attribute_floor(base: int, valor: float) -> int:
    """Prende o atributo resolvido no piso de `MIN_ATTRIBUTE_RATIO` da base.

    Central, e não repetido em cada getter: um piso que existe em três lugares é
    um piso que vai divergir no quarto.
    """
    piso = max(1, int(base * MIN_ATTRIBUTE_RATIO))
    return max(piso, int(valor))


def concealment_penalty(entity) -> int:
    """Pontos de acerto que QUEM ATACA esta entidade perde.

    Espelho de `accuracy_penalty`: aquele mede o que o atacante carrega, este o
    que o defensor esconde. Os dois entram na mesma soma de `hit_chance`, e
    nenhum cria rolagem nova.
    """
    return int(sum(i.total_intensity for i in instances(entity, FAMILY_CONCEALMENT)))


def accuracy_shift(entity) -> int:
    """Saldo de acerto que a entidade leva para uma ação OFENSIVA, com sinal.

    Positivo de `precision`, negativo de `fear`, somados no MESMO lugar. Nenhum
    dos dois mexe em Agilidade e nenhum cria rolagem nova: os dois entram na
    conta de acerto que já existe. Duas rolagens para a mesma pergunta é como
    `Esmagar` acabou atordoando por dois caminhos independentes.
    """
    total = 0.0
    for instancia in instances(entity, FAMILY_ACCURACY):
        definicao = instancia.definition
        if definicao is None:
            continue
        total += instancia.total_intensity if definicao.positive else -instancia.total_intensity
    return int(total)


def dot_damage(entity, effect_id: str, max_hp: int) -> int:
    """Dano de um DoT neste turno: `% do HP máximo × stacks`.

    Percentual, e não pontos fixos: a masmorra é infinita, e um veneno de 5
    pontos por turno seria letal no andar 1 e invisível no andar 40.
    """
    total = 0.0
    for instancia in instances(entity, FAMILY_DOT):
        if instancia.effect == effect_id:
            total += max_hp * instancia.total_intensity / 100
    return int(total) if total >= 1 else (1 if total > 0 else 0)


def effective_chance(base_chance: float, resistance: float) -> float:
    """`base × (1 - resistência/100)`, as duas pontas presas em 0..100.

    Resistência age na CHANCE DE ENTRAR, nunca na intensidade: ela não reduz o
    dano do sangramento nem a força do enfraquecimento. 100% é imunidade real,
    sem piso — se o jogador pagou o preço, a imunidade é dele.
    """
    return _clamp_percent(_clamp_percent(base_chance) * (1 - _clamp_percent(resistance) / 100))


def _clamp_percent(valor) -> float:
    return max(0.0, min(100.0, float(valor or 0)))


def adopt_legacy(entity) -> list[str]:
    """Converte entradas antigas de `active_effects` em instâncias do núcleo.

    Save anterior ao núcleo grava `{"poison": {"duration": 2}}` — dicionário
    simples, sem fonte e sem stacks. Sem esta adoção o núcleo não os enxergaria:
    não tickariam, não expirariam, e um veneno carregado de um save antigo
    duraria para sempre.

    Entrada cujo nome não está no catálogo fica como está. `damage_reduction` é
    o caso vivo disso, e continua com o ciclo antigo de propósito.
    """
    ativo = _store(entity)
    adotadas = []
    for chave, dados in list(ativo.items()):
        if isinstance(dados, EffectInstance) or not isinstance(dados, dict):
            continue
        definicao = CATALOG.get(chave)
        if definicao is None:
            continue
        intensidade = dados.get("value", dados.get("intensity"))
        ativo[instance_key(chave, "")] = EffectInstance(
            chave,
            source_id=str(dados.get("source_id", "")),
            intensity=definicao.default_intensity if intensidade is None else float(intensidade),
            duration=int(dados.get("duration", definicao.default_duration)),
            stacks=int(dados.get("stacks", 1)),
        )
        if instance_key(chave, "") != chave:
            del ativo[chave]
        adotadas.append(chave)
    return adotadas


def tick_effects(entity) -> dict:
    """Passa um turno: aplica dano/dreno, decrementa e expira.

    Devolve o que aconteceu, para quem chama dar voz na tela. O núcleo não
    publica evento nem imprime nada — ele não conhece UI.
    """
    adopt_legacy(entity)
    ativo = _store(entity)
    relatorio: dict = {"dot": {}, "drain": {}, "expired": [], "skip_turn": False}
    max_hp = int(getattr(entity, "base_hp", getattr(entity, "get_hp", lambda: 1)()))

    for effect_id in effects_of_family(FAMILY_DOT):
        dano = dot_damage(entity, effect_id, max_hp)
        if dano > 0:
            entity.take_damage(dano)
            relatorio["dot"][effect_id] = dano

    for instancia in instances(entity, FAMILY_DRAIN):
        quanto = int(instancia.total_intensity)
        if quanto > 0:
            entity.reduce_mp(quanto)
            if entity.get_mp() < 0:
                entity._mp = 0
            relatorio["drain"][instancia.effect] = quanto

    if instances(entity, FAMILY_CONTROL):
        relatorio["skip_turn"] = True

    for chave, instancia in list(ativo.items()):
        if not isinstance(instancia, EffectInstance):
            continue
        instancia.duration -= 1
        if instancia.duration <= 0:
            del ativo[chave]
            relatorio["expired"].append(instancia.effect)
    return relatorio


def break_on_damage(entity) -> list[str]:
    """Remove os efeitos que quebram ao levar dano. Devolve o que saiu."""
    removidos = []
    for instancia in instances(entity):
        definicao = instancia.definition
        if definicao is not None and definicao.breaks_on_damage:
            removidos.append(instancia.effect)
    for effect_id in removidos:
        remove_effect(entity, effect_id)
    return removidos
