import copy
import random

from src.content.enchantments import ENCHANT_EFFECTS, MAX_ENCHANTMENTS
from src.data.loader import load_json
from src.shared.constants import MAX_SOCKETS, RARITY_MULTIPLIERS, SOCKET_WEIGHTS_BY_RARITY
from src.shared.formulas import enhancement_multiplier


class Item:
    """Classe base para todos os itens do jogo.

    Attributes:
        id: Identificador único do item.
        name: Nome do item.
        description: Descrição do item.
        rarity: Raridade do item.
        slot: Slot de equipamento.
        classes: Lista de classes que podem usar o item (None = todas).
    """

    def __init__(
        self,
        item_id: str,
        name: str,
        description: str,
        rarity: str = "Common",
        slot: str = "Body",
        damage_bonus: int = 0,
        defense_bonus: int = 0,
        effect_type: str | None = None,
        effect_value: int = 0,
        classes: list[str] | None = None,
        sold_in_shop: bool = True,
        droppable: bool = True,
        price: int = 50,
        shop_min_floor: int = 1,
        shop_max_floor: int | None = None,
        consumable: bool = False,
        status_resistances: dict[str, int] | None = None,
        hands_required: int = 1,
        hand_type: str | None = None,
        enhancement_level: int = 0,
        socket_count: int = 0,
        enchantments: list | None = None,
    ) -> None:
        self.id: str = item_id
        self.name: str = name
        self.description: str = description
        self.rarity: str = rarity
        self.slot: str = slot
        self.base_damage_bonus: int = damage_bonus
        self.base_defense_bonus: int = defense_bonus
        self.effect_type: str | None = effect_type
        self.base_effect_value: int = effect_value
        self.classes: list[str] | None = classes
        self.sold_in_shop: bool = sold_in_shop
        self.droppable: bool = droppable
        self.price: int = price
        self.shop_min_floor: int = shop_min_floor
        self.shop_max_floor: int | None = shop_max_floor
        self.consumable: bool = consumable
        # Resistência a status negativo que o item concede, por nome canônico
        # (ver `shared/effects.negative_statuses`). Um dicionário, e não um campo
        # por status: um colar pode dar frio e atordoamento ao mesmo tempo, e
        # `frozen_resistance`, `stun_resistance`, … seriam trinta campos para a
        # mesma ideia. Quem soma é `Player.get_status_resistance`; o combate não
        # sabe que equipamento existe.
        self.status_resistances: dict[str, int] = dict(status_resistances or {})
        # Quantas MÃOS a peça toma: 1 ocupa uma posição, 2 toma as duas. Fonte
        # única — não existe `two_handed` ao lado, porque dois campos para o
        # mesmo fato divergem no primeiro item que declarar só um deles.
        #
        # O contrato é fechado: o personagem tem duas mãos, então 3 não é um
        # número maior, é um erro. Um clamp silencioso transformaria a digitação
        # errada num item de duas mãos que ninguém pediu.
        if int(hands_required) not in (1, 2):
            raise ValueError(
                f"hands_required deve ser 1 ou 2, não {hands_required!r} (item {item_id!r})"
            )
        self.hands_required: int = int(hands_required)
        # O que a peça É — sword, dagger, mace, staff, shield, orb, focus, wand.
        # Descritivo por enquanto: nada no motor lê isto. Existe para que
        # proficiência e requisitos tenham onde se apoiar sem migrar o catálogo.
        self.hand_type: str | None = hand_type

        # Rank de aprimoramento. Pertence ao EXEMPLAR, não à definição: duas
        # Espadas de Ferro podem estar +3 e +17 ao mesmo tempo. Sem teto — a
        # masmorra é infinita, e um cap aqui seria o fim da progressão do item.
        self.enhancement_level: int = max(0, int(enhancement_level or 0))

        # Sockets. Uma LISTA, e não um `self.gem`: um item com dois ou três
        # encaixes é conteúdo, não arquitetura nova, e um campo único fecharia
        # essa porta. Pertence ao EXEMPLAR, como o rank — duas Espadas de Ferro
        # podem ter pedras diferentes.
        self.socket_count: int = max(0, min(MAX_SOCKETS, int(socket_count or 0)))
        self.gems: list = [None] * self.socket_count

        # Encantamentos do exemplar. Lista, como os sockets, e pelo mesmo motivo:
        # a peça pode ter vários, e um campo único fecharia a porta.
        self.enchantments: list = list(enchantments or [])[:MAX_ENCHANTMENTS]

        if effect_type and effect_value:
            multiplier = RARITY_MULTIPLIERS.get(rarity, 1.0)
            if effect_type in ("max_hp", "max_mp", "agility", "strength", "defense"):
                self.base_effect_value = int(effect_value * multiplier)

    # O que `+N` fortalece: os stats BASE da própria peça. É exatamente o
    # conjunto que `Player.EQUIP_STAT_SOURCES` consome — Camada A, resolução de
    # atributo. Fica de fora tudo que é modificador de combate (evasão, crítico,
    # roubo de vida) e todo efeito especial (`stun`, `death_ignore`): um item +20
    # não deve atordoar mais só porque foi aprimorado, e resistência a status
    # muito menos, porque 100% é imunidade e o rank não tem teto.
    ENHANCEABLE_EFFECTS = frozenset(
        {"max_hp", "max_mp", "strength", "agility", "speed", "magic_damage", "defense"}
    )

    def _enhanced(self, base: int) -> int:
        """A base deste exemplar, com o rank aplicado.

        Derivado a cada leitura, nunca acumulado no campo: a base original
        continua respondível, e não há deriva de arredondamento por aplicar o
        multiplicador repetidas vezes.

        Valor negativo passa intacto. `defense_bonus` desce a -3 e `effect_value`
        a -5 no catálogo: são desvantagens declaradas da peça, e multiplicá-las
        faria aprimorar a Placa Pesada dobrar a lentidão dela.
        """
        if base <= 0 or self.enhancement_level <= 0:
            return int(base)
        return int(base * enhancement_multiplier(self.enhancement_level) + 0.5)

    @property
    def damage_bonus(self) -> int:
        return self._enhanced(self.base_damage_bonus)

    @property
    def defense_bonus(self) -> int:
        return self._enhanced(self.base_defense_bonus)

    @property
    def effect_value(self) -> int:
        """O efeito da peça, aprimorado SÓ se for um atributo base."""
        if self.effect_type in self.ENHANCEABLE_EFFECTS:
            return self._enhanced(self.base_effect_value)
        return int(self.base_effect_value)

    @property
    def display_name(self) -> str:
        """Como a peça se apresenta. `name` continua sendo a chave do catálogo.

        Anexar " +27" ao `name` contaminaria busca no registro e leitura de save,
        que resolvem a definição pelo nome.
        """
        if self.enhancement_level <= 0:
            return self.name
        return f"{self.name} +{self.enhancement_level}"

    def increase_enhancement(self, amount: int = 1) -> int:
        """Sobe o rank deste exemplar. Devolve o novo rank.

        Sem custo e sem chance de falha: a origem (Ferreiro, ouro, material) é
        conteúdo de outra rodada. Isto é só a mecânica do item.
        """
        self.enhancement_level = max(0, self.enhancement_level + int(amount))
        return self.enhancement_level

    def socket(self, gem, index: int | None = None):
        """Encaixa `gem`. Devolve a pedra que saiu, ou `None` se o socket estava vazio.

        Sem `index`, usa o primeiro socket livre; sem nenhum livre, substitui o
        primeiro. Quem chama decide o que fazer com a devolvida — devolver ao
        inventário é responsabilidade do `Player`, não do item.
        """
        if self.socket_count <= 0:
            raise ValueError(f"{self.name} não tem socket.")
        if index is None:
            index = self.free_socket()
            if index is None:
                index = 0
        if not 0 <= index < self.socket_count:
            raise IndexError(f"{self.name} tem {self.socket_count} socket(s), não o índice {index}")
        anterior = self.gems[index]
        self.gems[index] = gem
        return anterior

    def unsocket(self, index: int):
        """Retira a pedra do socket. Devolve ela, ou `None` se estava vazio."""
        if not 0 <= index < self.socket_count:
            raise IndexError(f"{self.name} tem {self.socket_count} socket(s), não o índice {index}")
        gem, self.gems[index] = self.gems[index], None
        return gem

    def free_socket(self) -> int | None:
        """Índice do primeiro socket vazio, ou `None` se estão todos ocupados."""
        for i, gem in enumerate(self.gems):
            if gem is None:
                return i
        return None

    def enchant(self, enchantment, index: int | None = None):
        """Acrescenta ou substitui um encantamento. Devolve o que saiu, ou `None`.

        Sem `index`, ocupa o primeiro lugar livre até o teto; cheio, substitui o
        primeiro. Simétrico a `socket`, e de propósito: são duas listas do mesmo
        exemplar e não há razão para terem gramáticas diferentes.
        """
        if index is None:
            if len(self.enchantments) < MAX_ENCHANTMENTS:
                self.enchantments.append(enchantment)
                return None
            index = 0
        if not 0 <= index < MAX_ENCHANTMENTS:
            raise IndexError(f"Encantamento vai de 0 a {MAX_ENCHANTMENTS - 1}, não {index}")
        if index >= len(self.enchantments):
            self.enchantments.append(enchantment)
            return None
        anterior = self.enchantments[index]
        self.enchantments[index] = enchantment
        return anterior

    def disenchant(self, index: int):
        """Retira o encantamento da posição. Devolve ele, ou `None` se não havia."""
        if not 0 <= index < len(self.enchantments):
            return None
        return self.enchantments.pop(index)

    def enchantment_bonus(self, kind: str) -> float:
        """Quanto os encantamentos desta peça acrescentam a um modificador.

        Canal PRÓPRIO, ao lado do `effect_type` da peça e das gemas. Os três
        somam no mesmo lugar porque representam a mesma coisa por caminhos
        diferentes — mas continuam três campos distintos, e "de onde veio este
        ponto de poder?" segue tendo resposta.
        """
        if kind not in ENCHANT_EFFECTS:
            return 0.0
        return sum(float(e.value) for e in self.enchantments if e is not None and e.effect == kind)

    def gem_percent(self, stat: str) -> float:
        """Quanto as pedras desta peça acrescentam a um atributo, em %.

        Separado de `damage_bonus` e companhia de propósito: `+N` multiplica a
        base da peça, a gema soma um percentual do atributo do personagem. Somar
        as duas no mesmo campo apagaria a diferença que o desenho quer manter.
        """
        return sum(g.percent for g in self.gems if g is not None and g.stat == stat)

    def spawn(self, rng=None) -> "Item":
        """Um exemplar NOVO, com os sockets sorteados pela raridade.

        Separado de `instance()` de propósito: `instance()` copia e ponto, e é
        o que save/load usa. Se o sorteio morasse lá, carregar o jogo rerrolaria
        os encaixes da sua espada toda vez — o exemplar deixaria de ter história.

        Chamado onde uma peça NASCE: drop, oferta da loja, recompensa, bootstrap.
        """
        novo = self.instance()
        # Só peça equipável recebe encaixe. Poção não tem onde cravar uma gema, e
        # o catálogo tem consumíveis Rare e Epic — sem esta guarda, um Elixir
        # Épico nasceria com dois sockets que nada no jogo saberia usar.
        if novo.consumable or not novo.slot:
            novo.socket_count = 0
        else:
            novo.socket_count = roll_socket_count(novo.rarity, rng)
        novo.gems = [None] * novo.socket_count
        return novo

    def instance(self) -> "Item":
        """Um exemplar novo desta definição.

        `get_all_items()` devolve objetos COMPARTILHADOS: sem esta cópia,
        aprimorar a espada do jogador aprimoraria todas as Espadas de Ferro do
        jogo, inclusive as que ainda estão na loja. Chamado onde um item entra no
        mundo — loja, drop, save, loadout — e não em quem só lê o catálogo.
        """
        novo = copy.copy(self)
        # Lista própria: `copy.copy` é raso, e sem isto dois exemplares da mesma
        # definição dividiriam os sockets — encaixar um Rubi numa espada o
        # encaixaria em todas.
        novo.gems = list(self.gems)
        novo.enchantments = list(self.enchantments)
        novo.status_resistances = dict(self.status_resistances)
        novo.classes = list(self.classes) if self.classes is not None else None
        return novo

    @property
    def is_potion(self) -> bool:
        """Verifica se o item é um consumível.

        Antes isto adivinhava pelo `effect_type`, então qualquer amuleto ou
        armadura com bônus de vida contava como poção: aparecia na lista de
        poções do combate e era destruído ao ser "bebido". Agora o dado diz.
        """
        return bool(self.consumable)

    @property
    def is_usable(self) -> bool:
        """Verifica se o item pode ser usado (não é equipamento)."""
        if not self.effect_type or self.effect_value <= 0:
            return False
        return self.effect_type in (
            "max_hp",
            "max_mp",
            "agility",
            "strength",
            "defense",
            "speed",
            "evasion",
            "crit_chance",
            "crit_damage",
            "life_steal",
            "mana_regen",
        )


def roll_socket_count(rarity: str, rng=None) -> int:
    """Quantos sockets um exemplar desta raridade recebe ao nascer.

    Lê `SOCKET_WEIGHTS_BY_RARITY`. Raridade desconhecida nasce sem encaixe: um
    default generoso faria conteúdo novo ganhar sockets por engano, e ninguém
    perceberia até a economia já estar torta.
    """
    pesos = SOCKET_WEIGHTS_BY_RARITY.get(str(rarity))
    if not pesos:
        return 0
    r = rng if rng is not None else random
    return int(r.choices(range(len(pesos)), weights=pesos, k=1)[0])


def create_item_from_json(item_data: dict) -> Item:
    """Cria um objeto Item a partir de dados do JSON."""
    return Item(
        item_id=item_data.get("id", ""),
        name=item_data.get("name", ""),
        description=item_data.get("description", ""),
        rarity=item_data.get("rarity", "Common"),
        slot=item_data.get("slot", "Body"),
        damage_bonus=item_data.get("damage_bonus", 0),
        defense_bonus=item_data.get("defense_bonus", 0),
        effect_type=item_data.get("effect_type"),
        effect_value=item_data.get("effect_value", 0),
        classes=item_data.get("classes"),
        sold_in_shop=item_data.get("sold_in_shop", True),
        droppable=item_data.get("droppable", True),
        price=item_data.get("price", 50),
        shop_min_floor=item_data.get("shop_min_floor", 1),
        shop_max_floor=item_data.get("shop_max_floor", None),
        consumable=item_data.get("consumable", False),
        status_resistances=item_data.get("status_resistances"),
        hands_required=item_data.get("hands_required", 1),
        enhancement_level=item_data.get("enhancement_level", 0),
        socket_count=item_data.get("socket_count", 0),
        enchantments=item_data.get("enchantments"),
        hand_type=item_data.get("hand_type"),
    )


# --- GERADOR DINÂMICO DE ITENS ---

_ALL_ITEMS_CACHE: dict[str, Item] | None = None


def _load_all_items() -> dict[str, Item]:
    """Carrega todos os itens do JSON e gera ALL_ITEMS."""
    global _ALL_ITEMS_CACHE
    if _ALL_ITEMS_CACHE is not None:
        return _ALL_ITEMS_CACHE

    data = load_json("items.json")
    items_list = data.get("items", [])

    _ALL_ITEMS_CACHE = {}
    for item_data in items_list:
        item = create_item_from_json(item_data)
        _ALL_ITEMS_CACHE[item.name] = item

    return _ALL_ITEMS_CACHE


def get_all_items() -> dict[str, Item]:
    """Retorna o dicionário de todos os itens (gerado dinamicamente do JSON)."""
    return _load_all_items()


# Alias para compatibilidade
ALL_ITEMS = property(lambda self: _load_all_items())


def reload_items() -> None:
    """Recarrega os itens (útil para desenvolvimento)."""
    global _ALL_ITEMS_CACHE
    _ALL_ITEMS_CACHE = None
    _load_all_items()


# --- COMPATIBILIDADE COM CÓDIGO EXISTENTE ---
# Para acesso direto via Item class (não recomendado, use get_all_items())


def __getattr__(name: str) -> Item:
    items = _load_all_items()
    if name in items:
        return items[name]
    raise AttributeError(f"Item '{name}' not found")


# Garante que ALL_ITEMS esteja carregado ao importar
_load_all_items()


# --- COMPATIBILIDADE COM CÓDIGO EXISTENTE ---
# Para manter compatibilidade com código que espera classes separadas


class Weapon(Item):
    """Classe de compatibilidade para armas."""

    pass


class Armor(Item):
    """Classe de compatibilidade para armaduras."""

    pass


class Potion(Item):
    """Classe de compatibilidade para poções."""

    pass


# Exporta ALL_ITEMS para compatibilidade (propriedade dinâmica)
class _AllItemsDict:
    """Proxy para manter compatibilidade com ALL_ITEMS."""

    def __getitem__(self, key):
        return _load_all_items()[key]

    def __contains__(self, key):
        return key in _load_all_items()

    def keys(self):
        return _load_all_items().keys()

    def values(self):
        return _load_all_items().values()

    def items(self):
        return _load_all_items().items()

    def __len__(self):
        return len(_load_all_items())

    def get(self, key, default=None):
        return _load_all_items().get(key, default)


ALL_ITEMS = _AllItemsDict()
