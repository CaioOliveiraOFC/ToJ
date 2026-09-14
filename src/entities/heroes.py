from __future__ import annotations

from typing import TYPE_CHECKING

from src.entities.base import Entity
from src.shared import effect_core as core
from src.shared.constants import (
    CLASS_WEIGHTS,
    DAMAGE_FORMULA_DIVISOR,
    LEVEL_UP_RESTORE_PERCENT,
    MAGE_BASE_AG,
    MAGE_BASE_DF,
    MAGE_BASE_HP,
    MAGE_BASE_MG,
    MAGE_BASE_MP,
    MAGE_BASE_ST,
    MAGIC_SHIELD_ABSORB_PERCENT,
    MAX_ACTIVE_SKILLS,
    POTION_BUFF_DURATION,
    ROGUE_BASE_AG,
    ROGUE_BASE_DF,
    ROGUE_BASE_HP,
    ROGUE_BASE_MG,
    ROGUE_BASE_MP,
    ROGUE_BASE_ST,
    SKILL_OFFER_LEVEL_INTERVAL,
    WARRIOR_BASE_AG,
    WARRIOR_BASE_DF,
    WARRIOR_BASE_HP,
    WARRIOR_BASE_MG,
    WARRIOR_BASE_MP,
    WARRIOR_BASE_ST,
)
from src.shared.effects import buff_value, sum_buffs
from src.shared.formulas import geometric, xp_for_level
from src.shared.registries import get_initial_skills_for

if TYPE_CHECKING:
    from src.content.passives import PassiveCard
    from src.content.skills_loader import SkillCard


def percentage(percent: int, whole: int, remainder: bool = True) -> int | float:
    """Calcula a porcentagem de um valor.

    Args:
        percent: Porcentagem a ser calculada.
        whole: Valor base para o cálculo.
        remainder: Se True, retorna float; se False, retorna int (default: True).

    Returns:
        Resultado do cálculo percentual.
    """
    if remainder:
        return (percent * whole) / 100
    return (percent * whole) // 100


# Efeitos de consumível que viram buff temporário, com o atributo que cada um
# modifica. O nome do buff é só rótulo de UI: quem decide o efeito é o atributo.
POTION_BUFFS: dict[str, tuple[str, str]] = {
    "strength": ("st", "Força Aumentada"),
    "defense": ("df", "Defesa Aumentada"),
    "agility": ("ag", "Agilidade Aumentada"),
    "speed": ("ag", "Velocidade Aumentada"),
    "magic_damage": ("mg", "Poder Mágico"),
    "evasion": ("evasion", "Evasão Aumentada"),
    "crit_chance": ("crit_chance", "Chance de Crítico"),
    "crit_damage": ("crit_damage", "Dano Crítico"),
    "life_steal": ("life_steal", "Roubo de Vida"),
    "mana_regen": ("mana_regen", "Regeneração de Mana"),
    "damage_reduction": ("damage_reduction", "Redução de Dano"),
}

# Consumíveis que aplicam um status em vez de um buff de atributo.
POTION_STATUSES = ("poison", "bleed", "stun", "fear", "true_damage", "death_ignore")


class Player(Entity):
    """Classe base para personagens jogáveis (heróis).

    Attributes:
        nick_name: Nome do jogador.
        level: Nível atual.
        xp_points: Pontos de experiência acumulados.
        isalive: Indica se o jogador está vivo.
        avg_damage: Dano médio calculado.
        kill_streak: Sequência de kills.
        wins: Vitórias.
        coins: Moedas do jogador.
        skill_points: Pontos de habilidade disponíveis.
        inventory: Lista de itens no inventário.
        equipment: Dicionário de equipamentos por slot.
        skills: Habilidades aprendidas.
        learnable_skills: Habilidades disponíveis para aprender.
        active_effects: Efeitos ativos no jogador.
        active_buffs: Buffs ativos no jogador.
    """

    # Atributos base do nível 1, definidos por cada subclasse.
    CLASS_BASE: dict[str, int] = {}

    def __init__(self, nick_name: str) -> None:
        # `_growth` guarda os valores do nível 1 e nunca muda; o valor atual de
        # cada atributo é derivado do nível. `_bonus` acumula os acréscimos
        # planos de passivas e equipamento.
        #
        # Antes, o level up fazia `base_hp += 20% de base_hp`, um crescimento
        # composto que divergia para sempre do crescimento aditivo do monstro.
        # Derivar do nível também evita o erro de arredondamento que congelaria
        # um atributo pequeno: `int(8 * 1.12)` é 8, então a agilidade do Mago
        # nunca sairia do lugar se o valor fosse acumulado em inteiro.
        self._growth: dict[str, int] = dict(self.CLASS_BASE)
        self._bonus: dict[str, int] = {"hp": 0, "mp": 0, "st": 0, "ag": 0, "mg": 0, "df": 0}

        self.nick_name = nick_name
        self.level = 1
        self.xp_points = 0
        self.isalive = True
        self.avg_damage = 0
        self.kill_streak = 0
        self.wins = 0
        self.coins = 0
        # Livro-caixa da run. Permadeath: o ouro morre com o personagem e não
        # existe banco global — isto é histórico, não recurso. Serve para
        # responder "para onde foi o dinheiro desta run", que é a pergunta que
        # o balanceamento econômico precisa fazer e hoje não conseguia.
        self.ledger: dict[str, int] = {
            "gold_earned": 0,
            "gold_spent": 0,
            "max_gold_held": 0,
            "purchases": 0,
            "interest_payments": 0,
            "items_dropped": 0,
            "items_sold": 0,
            "items_equipped": 0,
        }
        # Último andar cujos juros já foram pagos. Mora no herói, e não no laço
        # de jogo, porque é salvo com ele: sem isso, carregar um save no meio do
        # andar pagaria os juros daquele andar de novo.
        self.last_interest_floor = 0
        self.skill_points = 0
        self.unspent_attribute_points: int = 0
        self.inventory: list[object] = []
        self.equipment = {posicao: None for posicao in self.EQUIPMENT_POSITIONS}
        self.skills: dict[int, SkillCard] = {}
        self.initial_skills_learned: int = 0
        # Cartas que esta RUN já mostrou — aprendidas, recusadas ou esquecidas.
        # Serve para a oferta preferir o inédito: ver a mesma carta três vezes
        # antes de conhecer metade do catálogo é o que faz a escolha parecer
        # sorteio. Vive no herói porque é estado de run, e é salvo com ele.
        self.seen_skill_ids: set[str] = set()
        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, dict[str, object]] = {}
        self.passives: list[PassiveCard] = []
        self.skill_cooldowns: dict[str, int] = {}
        # Resistência a status negativo, por nome canônico. Vazio: nenhum herói
        # nasce resistente. Ver `Entity.get_status_resistance`.
        self.resistances: dict[str, int] = {}
        # Bolsa de gemas soltas. Lista própria e não `inventory`: gema não é
        # equipamento nem consumível, e todo consumidor de `inventory` teria de
        # aprender a ignorá-la — a loja, o descarte do bot, a tela de itens do
        # combate. Separar é a solução menor.
        self.gems: list = []

    # As posições físicas do personagem, na ordem em que a UI as mostra.
    #
    # POSIÇÃO não é CATEGORIA. O item declara a categoria em que se encaixa
    # ("Weapon", "Ring"), o personagem tem as posições onde ela cabe
    # ("Weapon1"/"Weapon2", "Ring1"/"Ring2"). Separar os dois evita duplicar o
    # catálogo inteiro para dizer que uma adaga serve nas duas mãos.
    EQUIPMENT_POSITIONS = (
        "Helmet",
        "Amulet",
        "Weapon1",
        "Weapon2",
        "Body",
        "Legs",
        "Hands",
        "Shoes",
        "Ring1",
        "Ring2",
        "Accessory",
    )

    # Categoria declarada pelo item -> posições que a aceitam, em ordem de
    # preferência. Duas posições da mesma categoria são EQUIVALENTES: não há
    # anel esquerdo e direito, só a primeira livre.
    CATEGORY_POSITIONS: dict[str, tuple[str, ...]] = {
        "Weapon": ("Weapon1", "Weapon2"),
        "Ring": ("Ring1", "Ring2"),
    }

    # As duas posições de mão. Toda classe tem as duas: `Weapon2` não é "a
    # segunda arma do dual wield", é a segunda mão — onde cabe escudo, orbe,
    # foco ou uma segunda lâmina. O Mago não tem menos mãos que o Guerreiro.
    #
    # Restrição futura pertence ao ITEM (`classes`, proficiência, requisito), e
    # não ao fato de a classe ser Mago. Anatomia não se negocia por classe.
    HAND_POSITIONS = ("Weapon1", "Weapon2")

    @classmethod
    def category_of(cls, position: str) -> str:
        """A categoria de item que uma posição aceita. `Ring2` -> `Ring`."""
        for categoria, posicoes in cls.CATEGORY_POSITIONS.items():
            if position in posicoes:
                return categoria
        return position

    @classmethod
    def positions_for(cls, category: str | None) -> tuple[str, ...]:
        """As posições que aceitam uma categoria de item."""
        if not category:
            return ()
        if category in cls.CATEGORY_POSITIONS:
            return cls.CATEGORY_POSITIONS[category]
        return (category,) if category in cls.EQUIPMENT_POSITIONS else ()

    @staticmethod
    def hands_required(item: object) -> int:
        """Quantas mãos a peça toma. Sem o campo, uma."""
        return max(1, int(getattr(item, "hands_required", 1) or 1))

    def can_equip_in_hand(self, item: object, position: str) -> bool:
        """Se `item` pode ocupar esta posição de mão.

        Duas regras, e nenhuma delas olha a classe:

        - peça de duas mãos entra só pela primeira posição, e leva a outra junto;
        - nenhuma peça entra numa mão que uma peça de duas mãos já ocupa.

        Espada + escudo, cajado + orbe e duas adagas são todos o mesmo caso:
        duas peças de uma mão em duas posições de mão.
        """
        if position not in self.HAND_POSITIONS:
            return False
        if self.hands_required(item) > 1:
            return position == self.HAND_POSITIONS[0]
        return not any(
            self.hands_required(self.equipment.get(outra)) > 1
            for outra in self.HAND_POSITIONS
            if outra != position
        )

    def free_position_for(self, item: object) -> str | None:
        """Primeira posição livre para o item, ou `None` se todas estão ocupadas.

        Não decide substituição: quem escolhe qual peça sai é quem chama, e é
        por isso que `equip` aceita uma posição explícita.
        """
        for posicao in self.available_positions_for(item):
            if self.equipment.get(posicao) is None:
                return posicao
        return None

    def occupant_for(self, item: object) -> object | None:
        """A peça que sairia se este item fosse equipado agora, ou `None`.

        A UI comparava contra `equipment[item.slot]`, o que deixou de existir
        para arma e anel. Havendo posição livre, nada sai — e é isso que faz o
        segundo anel aparecer como aquisição, não como troca.
        """
        posicoes = self.available_positions_for(item)
        if not posicoes:
            return None
        return self.equipment.get(self.free_position_for(item) or posicoes[0])

    def available_positions_for(self, item: object) -> tuple[str, ...]:
        """As posições que este item pode ocupar NESTE personagem, agora.

        Difere de `positions_for` por aplicar as regras do portador: a segunda
        arma só aparece para quem consegue usá-la, e some enquanto a mão
        principal segura uma peça de duas mãos.
        """
        posicoes = self.positions_for(getattr(item, "slot", None))
        return tuple(
            p for p in posicoes if p not in self.HAND_POSITIONS or self.can_equip_in_hand(item, p)
        )

    # Qual campo do item alimenta cada atributo. O bônus do item é lido como
    # PERCENTUAL do atributo, não como soma fixa: a melhor arma do jogo dava +30
    # de dano sobre um poder base de ~860 no nível 20, ou seja 3%, e o conjunto
    # completo de defesa somava 52 pontos. Equipamento não decidia nada.
    EQUIP_STAT_SOURCES = {
        "hp": ("max_hp",),
        "mp": ("max_mp",),
        "st": ("strength",),
        "ag": ("agility", "speed"),
        "mg": ("magic_damage",),
        "df": ("defense",),
    }

    # Quais modificadores de COMBATE o equipamento pode alimentar. Lista de
    # permissão, e não "qualquer effect_type que o item declare": o catálogo tem
    # 58 itens de equipamento declarando efeitos que nada lê, e um canal genérico
    # acordaria os 58 de uma vez — sem ninguém ter decidido que deviam acordar,
    # e sem ninguém ter medido o que isso faz com o jogo.
    #
    # É a diferença entre um canal e um alçapão. Cada família nova entra aqui por
    # escolha, numa rodada que mede o impacto dela. Um `effect_type` novo no JSON
    # nunca deve mudar gameplay sozinho: foi assim que 58 itens viraram placebo.
    #
    # O critério para entrar: a mecânica já existe, já tem consumidor funcional no
    # motor, e só faltava o equipamento chegar até ela. Ficam de fora os efeitos
    # on-hit (`stun`, `bleed`, `poison`, `fear`), que precisam de resolução de proc
    # que ainda não existe, e os que não têm mecânica nenhuma.
    # Os quatro `effect_type` on-hit do catálogo. O valor declarado no item é a
    # CHANCE de aplicar, e vira o modificador que o golpe consulta: um item que
    # diz `bleed: 5` dá 5% de chance de sangramento. A mecânica em si é do
    # núcleo — o item não redefine o que sangramento é, só quer aplicá-lo.
    EQUIP_ONHIT_EFFECTS: dict[str, str] = {
        "stun": "stun_chance",
        "bleed": "bleed_chance",
        "poison": "poison_chance",
        "fear": "fear_chance",
    }

    EQUIP_COMBAT_EFFECTS = frozenset(
        {
            "evasion",  # hit_chance()
            "damage_reduction",  # incoming_damage_multiplier() -> mitigation
            "crit_chance",  # resolve_physical_attack()
            "crit_damage",  # damage_modifiers() -> xmult
            "life_steal",  # resolve_physical_attack(), depois do dano
            "mana_regen",  # process_turn_start_effects()
            "death_ignore",  # _survive_lethal_blow()
        }
    )

    def get_equipment_bonus(self, kind: str) -> float:
        """Quanto o que está equipado acrescenta a um modificador de combate.

        Fonte PRÓPRIA, ao lado de buff e passiva — não um disfarce de passiva.
        `shared/effects.combat_modifier` soma as três por caminhos separados,
        para que a pergunta "de onde veio este número?" continue tendo resposta.

        Derivado do equipamento atual, nunca copiado para o personagem: tirar a
        peça devolve o valor de antes, sem resíduo. Mesma escolha de
        `equipment_percent` e `get_status_resistance`, pelo mesmo motivo.
        """
        permitido = kind in self.EQUIP_COMBAT_EFFECTS
        total = 0.0
        for item in self.equipment.values():
            if item is None:
                continue
            efeito_do_item = getattr(item, "effect_type", None)
            if permitido and efeito_do_item == kind:
                total += float(getattr(item, "effect_value", 0) or 0)
            elif self.EQUIP_ONHIT_EFFECTS.get(efeito_do_item) == kind:
                total += float(getattr(item, "effect_value", 0) or 0)
            # Encantamento tem allowlist PRÓPRIA, aplicada dentro de
            # `enchantment_bonus`. São duas fontes na mesma peça, e nem sempre
            # com o mesmo vocabulário: `damage_percent` só existe encantado.
            encantado = getattr(item, "enchantment_bonus", None)
            if callable(encantado):
                total += float(encantado(kind))
        return total

    def equipment_percent(self, key: str) -> float:
        """Soma, em percentual, o que o equipamento acrescenta a um atributo.

        Duas contribuições, somadas e nunca misturadas: o que a PEÇA declara
        (já com o `+N` dela resolvido) e o que as GEMAS encaixadas nela trazem.
        A gema entra aqui, e não num canal próprio, porque é exatamente isto que
        ela é — percentual de atributo. Assim ela funciona nas onze posições sem
        uma linha de código por slot.
        """
        total = 0.0
        sources = self.EQUIP_STAT_SOURCES.get(key, ())
        for item in self.equipment.values():
            if item is None:
                continue
            obter_gemas = getattr(item, "gem_percent", None)
            if callable(obter_gemas):
                total += float(obter_gemas(key))
            if key == "df":
                total += float(getattr(item, "defense_bonus", 0))
            # `elif`: os dois ramos não eram exclusivos, então um item com
            # `defense_bonus` E `effect_type: "defense"` somava as duas vias e
            # rendia mais defesa do que declara. Afeta `amuleto_argila`.
            elif getattr(item, "effect_type", None) in sources:
                total += float(getattr(item, "effect_value", 0))
        return total

    def get_status_resistance(self, status: str) -> float:
        """Resistência própria mais a soma do que está equipado, capada em 100.

        Somada e não composta: 40% de anel, 35% de colar e 25% de armadura dão
        imunidade, e é justamente esse o pacto — se o jogador gastou três slots
        para não congelar, ele não congela. Acima de 100 o excedente se perde,
        sem conversão em outro bônus e sem retorno decrescente.

        Derivada do equipamento atual, nunca copiada para o personagem: tirar o
        anel devolve a resistência ao valor de antes, sem resíduo. É a mesma
        escolha de `equipment_percent`, e pelo mesmo motivo.

        O combate continua perguntando só `get_status_resistance` e não sabe que
        equipamento existe.
        """
        total = super().get_status_resistance(status)
        for item in self.equipment.values():
            if item is None:
                continue
            total += float((getattr(item, "status_resistances", None) or {}).get(status, 0) or 0)
        return max(0.0, min(100.0, total))

    def weapon_percent(self) -> float:
        """Percentual de dano acrescentado pelas armas equipadas.

        Soma as posições de arma, como todo agregador de equipamento já faz. Com
        uma arma só o resultado é o mesmo de antes, que é o requisito desta
        rodada; com duas, somar é a menor regra que deixa a segunda existir.

        Quanto uma segunda arma DEVE render — soma, média, penalidade — é
        balanceamento de dual wield, e fica para quando houver conteúdo de duas
        armas para medir. Hoje nenhum personagem gerado equipa duas.
        """
        return float(
            sum(
                getattr(self.equipment.get(posicao), "damage_bonus", 0) or 0
                for posicao in self.CATEGORY_POSITIONS["Weapon"]
            )
        )

    def _scaled(self, key: str) -> int:
        """Valor do atributo no nível atual, com equipamento e efeitos ativos.

        Ordem: nível → passiva plana → equipamento e gemas (percentual) →
        efeitos do núcleo (percentual) → piso.

        O piso é do núcleo e vale para os quatro atributos de combate: nenhum
        acúmulo de debuff derruba Força, Magia, Agilidade ou Defesa abaixo de
        10% da base. Recurso (hp/mp) não tem piso de atributo — quem cuida do
        teto temporário deles é `resource_percent`, e zerar vida por debuff é
        outra conversa.
        """
        grown = geometric(self._growth.get(key, 0), self.level) + self._bonus.get(key, 0)
        com_equipamento = grown * (1 + self.equipment_percent(key) / 100)
        if key in ("hp", "mp"):
            resolvido = com_equipamento * (1 + core.resource_percent(self, key) / 100)
            return max(1, int(resolvido))
        resolvido = com_equipamento * (1 + core.attribute_percent(self, key) / 100)
        return core.apply_attribute_floor(int(com_equipamento), resolvido)

    def _add_bonus(self, key: str, value: int) -> None:
        self._bonus[key] = self._bonus.get(key, 0) + int(value)

    @property
    def base_hp(self) -> int:
        return max(1, self._scaled("hp"))

    @base_hp.setter
    def base_hp(self, value: int) -> None:
        self._add_bonus("hp", int(value) - self.base_hp)

    @property
    def base_mp(self) -> int:
        return max(0, self._scaled("mp"))

    @base_mp.setter
    def base_mp(self, value: int) -> None:
        self._add_bonus("mp", int(value) - self.base_mp)

    @property
    def base_st(self) -> int:
        return max(0, self._scaled("st"))

    @base_st.setter
    def base_st(self, value: int) -> None:
        self._add_bonus("st", int(value) - self.base_st)

    @property
    def base_ag(self) -> int:
        return max(0, self._scaled("ag"))

    @base_ag.setter
    def base_ag(self, value: int) -> None:
        self._add_bonus("ag", int(value) - self.base_ag)

    @property
    def base_mg(self) -> int:
        return max(0, self._scaled("mg"))

    @base_mg.setter
    def base_mg(self, value: int) -> None:
        self._add_bonus("mg", int(value) - self.base_mg)

    @property
    def base_df(self) -> int:
        return max(0, self._scaled("df"))

    @base_df.setter
    def base_df(self, value: int) -> None:
        self._add_bonus("df", int(value) - self.base_df)

    def socket_gem(self, item, gem, index: int | None = None) -> bool:
        """Encaixa uma gema da bolsa numa peça. A pedra trocada volta para a bolsa.

        Mora no `Player` porque é aqui que a posse existe: o item sabe encaixar,
        mas não sabe de onde a pedra veio nem para onde a antiga vai. É a mesma
        divisão de `equip`, e é o que garante que nenhuma gema se perca no meio.
        """
        if int(getattr(item, "socket_count", 0) or 0) <= 0:
            return False
        anterior = item.socket(gem, index)
        if gem in self.gems:
            self.gems.remove(gem)
        if anterior is not None:
            self.gems.append(anterior)
        return True

    def unsocket_gem(self, item, index: int):
        """Retira a gema do socket e devolve à bolsa. Retorna a pedra, ou `None`."""
        gem = item.unsocket(index)
        if gem is not None:
            self.gems.append(gem)
        return gem

    def add_item_to_inventory(self, item: object) -> str | None:
        """Adiciona item ao inventário.

        Args:
            item: Item a ser adicionado.

        Returns:
            Mensagem de confirmação ou None.
        """
        if item:
            self.inventory.append(item)
            return f"Você obteve: {getattr(item, 'name', 'Item')}!"
        return None

    def remove_item_from_inventory(self, item: object) -> bool:
        """Remove item do inventário.

        Args:
            item: Item a ser removido.

        Returns:
            True se o item foi removido, False caso contrário.
        """
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False

    def spend_coins(self, amount: int, source: str = "other") -> bool:
        """Gasta moedas se houver saldo suficiente, e registra a saída.

        Todo ouro que sai do jogador passa por aqui — loja, mercador errante,
        recuperação paga. É por isso que o livro-caixa é escrito neste ponto e
        não em cada chamador: um chamador novo que esquecesse de registrar
        produziria ouro que some do saldo sem aparecer na contabilidade, e a
        taxa de utilização mediria errado sem dar sinal nenhum.

        Args:
            amount: Quantidade de moedas a gastar.
            source: Em que o ouro foi gasto (`gear`, `consumable`, `recovery`).

        Returns:
            True se a transação foi bem-sucedida, False caso contrário.
        """
        if amount < 0 or self.coins < amount:
            return False
        self.coins -= amount
        self.ledger["gold_spent"] += amount
        self.ledger[f"gold_spent_on_{source}"] = (
            self.ledger.get(f"gold_spent_on_{source}", 0) + amount
        )
        self.ledger["purchases"] += 1
        return True

    def earn_coins(self, amount: int, source: str = "combat") -> None:
        """Adiciona moedas ao jogador, e registra a entrada.

        Args:
            amount: Quantidade de moedas a adicionar.
            source: De onde veio (`combat`, `sale`, `interest`, `event`).
        """
        if amount <= 0:
            return
        self.coins += amount
        self.ledger["gold_earned"] += amount
        self.ledger[f"gold_from_{source}"] = self.ledger.get(f"gold_from_{source}", 0) + amount
        if source == "interest":
            self.ledger["interest_payments"] += 1
        self.ledger["max_gold_held"] = max(self.ledger["max_gold_held"], self.coins)

    def restore_mp(self, amount: int) -> int:
        """Devolve mana, sem passar do máximo. Retorna o que de fato entrou."""
        antes = self._mp
        self._mp = min(self.base_mp, self._mp + max(0, int(amount)))
        return int(self._mp - antes)

    def equip(self, item_to_equip: object, position: str | None = None) -> str | None:
        """Equipa um item no slot correspondente.

        A categoria do item ("Weapon", "Ring") não é a posição onde ele fica
        ("Weapon1", "Ring2"). Sem `position`, ocupa a primeira posição livre da
        categoria; com todas ocupadas, substitui a primeira — que é o
        comportamento de antes, quando cada categoria tinha uma posição só.

        Args:
            item_to_equip: Item a ser equipado.
            position: Posição física específica. A UI passa quando o jogador
                escolhe qual anel trocar; sem ela o personagem decide.

        Returns:
            Mensagem de confirmação ou mensagem de erro.
        """
        nome = getattr(item_to_equip, "name", "Item")
        disponiveis = self.available_positions_for(item_to_equip)
        if not disponiveis:
            return f"{nome} não pode ser equipado."
        if position is not None and position not in disponiveis:
            return f"{nome} não vai em {position}."

        item_classes = getattr(item_to_equip, "classes", None)
        if item_classes is not None and self.get_classname() not in item_classes:
            return f"Sua classe ({self.get_classname()}) não pode equipar {nome}."

        slot = position or self.free_position_for(item_to_equip) or disponiveis[0]

        if self.equipment[slot]:
            self.unequip(slot)
        # Uma peça de duas mãos toma a outra mão ao entrar. Ela NÃO é escrita
        # nas duas posições: os agregadores somam `equipment.values()`, e a mesma
        # peça em dois lugares contaria os bônus dela duas vezes.
        if slot == self.HAND_POSITIONS[0] and self.hands_required(item_to_equip) > 1:
            for outra in self.HAND_POSITIONS[1:]:
                self.unequip(outra)
        # `remove` sem guarda levantava ValueError quando o item não estava no
        # inventário — o que acontecia em todo carregamento de save com
        # equipamento, porque load_game já havia retirado o item. A exceção era
        # engolida por `except Exception` e o jogador via "save corrompido".
        if item_to_equip in self.inventory:
            self.inventory.remove(item_to_equip)
        self.equipment[slot] = item_to_equip
        self.ledger["items_equipped"] = self.ledger.get("items_equipped", 0) + 1
        # Sem soma de atributo aqui: o bônus é lido dinamicamente das
        # propriedades, o que evita contabilidade duplicada. E sem `rest()`:
        # equipar um item era uma cura completa gratuita e ilimitada.
        self._hp = min(self._hp, self.base_hp)
        return getattr(item_to_equip, "name", "Item")

    def unequip(self, slot: str) -> str | None:
        """Desequipa um item da posição indicada.

        Recebe POSIÇÃO (`Weapon1`), não categoria (`Weapon`). Uma posição que
        não existe levanta erro em vez de devolver `None`: as duas respostas
        eram indistinguíveis, então `unequip("Weapon")` — a grafia de antes das
        11 posições — parecia funcionar e deixava a arma equipada.

        Args:
            slot: Posição física a esvaziar.

        Returns:
            Nome da peça retirada, ou None se a posição estava vazia.

        Raises:
            KeyError: se a posição não existe neste personagem.
        """
        if slot not in self.equipment:
            raise KeyError(
                f"{slot!r} não é uma posição de equipamento. "
                f"Posições: {', '.join(self.EQUIPMENT_POSITIONS)}"
            )
        item_to_unequip = self.equipment.get(slot)
        if not item_to_unequip:
            return None
        self.equipment[slot] = None
        self.inventory.append(item_to_unequip)
        return getattr(item_to_unequip, "name", "Item")

    def use_potion(self, item: object) -> str:
        """Usa um consumível e aplica seu efeito.

        A versão anterior era uma cadeia de `if` por nome de efeito que escrevia
        buffs com nomes literais no dicionário de estado. Seis dos onze tipos
        gravavam um buff que `get_stat` nunca lia — a poção era consumida e não
        fazia nada. Agora o efeito declara o atributo que modifica, e o motor
        consulta o atributo.

        Args:
            item: Item a ser usado.

        Returns:
            Mensagem descrevendo o efeito aplicado.
        """
        effect_type = getattr(item, "effect_type", None)
        effect_value = int(getattr(item, "effect_value", 0))
        item_name = getattr(item, "name", "Item")

        if effect_type == "max_hp":
            # Percentual do máximo: uma poção de valor fixo cura 25% no nível 1
            # e 3% no nível 20, então deixa de ser uma decisão exatamente onde
            # ela deveria pesar mais.
            healed = max(1, int(self.base_hp * effect_value / 100))
            healed += int(healed * self.get_passive_bonus("potion_heal_bonus") / 100)
            self.heal(healed)
            msg = f"Você usou {item_name} e recuperou {healed} de HP."
        elif effect_type == "max_mp":
            restored = max(1, int(self.base_mp * effect_value / 100))
            self._mp = min(self.base_mp, self._mp + restored)
            msg = f"Você usou {item_name} e recuperou {restored} de MP."
        elif effect_type in POTION_BUFFS:
            stat, label = POTION_BUFFS[effect_type]
            self.active_buffs[label] = {
                "stat": stat,
                "value": buff_value(self, stat, effect_value),
                "duration": POTION_BUFF_DURATION,
            }
            msg = (
                f"Você usou {item_name}. {label} +{effect_value} por {POTION_BUFF_DURATION} turnos!"
            )
        elif effect_type in POTION_STATUSES:
            self.active_effects[effect_type] = {
                "value": effect_value,
                "duration": POTION_BUFF_DURATION,
            }
            msg = (
                f"Você usou {item_name}. "
                f"Efeito {effect_type} ativo por {POTION_BUFF_DURATION} turnos!"
            )
        else:
            msg = f"Você usou {item_name}, mas não teve efeito aparente."

        if item in self.inventory:
            self.inventory.remove(item)
        return msg

    def rest(self) -> None:
        """Restaura HP e MP ao máximo e limpa efeitos.

        Só deve ser usado na construção do personagem. Durante a run, chamar
        isto anula o atrito: era invocado depois de cada vitória, a cada nível,
        ao equipar, ao fugir e ao concluir o andar, e o efeito somado era que
        nenhum combate custava nada ao seguinte.
        """
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.active_effects.clear()
        self.active_buffs.clear()
        self.set_isalive(True)

    def recover(self, percent: int) -> int:
        """Restaura um percentual do máximo de HP e MP, e limpa efeitos de combate.

        É o descanso com custo: devolve o suficiente para o próximo andar ser
        jogável, e pouco o bastante para a decisão de extrair continuar existindo.

        Args:
            percent: Percentual do máximo a restaurar.

        Returns:
            HP efetivamente recuperado.
        """
        before = self._hp
        self.heal(int(self.base_hp * percent / 100))
        self._mp = min(self.base_mp, self._mp + int(self.base_mp * percent / 100))
        self.active_effects.clear()
        self.active_buffs.clear()
        self.skill_cooldowns.clear()
        self._death_ignore_used = False
        return self._hp - before

    def get_stat(self, stat: str) -> int:
        """Valor de um atributo somando todos os buffs ativos que o modificam.

        A versão anterior comparava o nome do buff com cinco literais. Qualquer
        buff com outro nome — o que incluía 12 das 14 skills de buff do jogo —
        era escrito e nunca lido.

        Args:
            stat: Nome do atributo ('st', 'ag', 'mg', 'df').

        Returns:
            Valor do atributo com buffs aplicados.
        """
        return int(getattr(self, f"base_{stat}")) + sum_buffs(self, stat)

    def add_passive(self, passive: PassiveCard) -> str:
        self.passives.append(passive)
        self._apply_passive_stats(passive)
        return f"Passiva adquirida: {passive.name}!"

    # Passivas que somam um valor PLANO num atributo ou recurso. Declarado como
    # dado, e não como cadeia de `if`, porque quem audita a cobertura precisa
    # poder PERGUNTAR quais famílias o motor consome. A lista paralela que
    # existia no teste de invariantes já tinha ficado para trás — ela não sabia
    # de `damage_percent` nem dos procs de acerto, e reportava como morto o que
    # o funil lê todo turno.
    #
    # `magic` entrou aqui e fechou a lacuna: havia passiva plana de Força,
    # Defesa, Agilidade, HP e MP, e nenhuma de Magia — a classe que escala em MG
    # não tinha carta de atributo. A semântica é a das outras: sobe `base_mg`, a
    # MG resolvida muda, e toda skill que escala em Magia recebe o BASE novo
    # sozinha. `combat.py` não fica sabendo que a Magia veio de uma passiva.
    PASSIVE_FLAT_STATS = {
        "max_hp": "hp",
        "max_mp": "mp",
        "strength": "st",
        "magic": "mg",
        "defense": "df",
        "agility": "ag",
    }

    def _apply_passive_stats(self, passive: PassiveCard) -> None:
        chave = self.PASSIVE_FLAT_STATS.get(passive.effect_type)
        if chave is None:
            # Modificador de combate ou de recompensa: não muda o boneco, é lido
            # pelo consumidor dele via `get_passive_bonus`.
            return
        valor = int(passive.effect_value)
        antes = getattr(self, f"base_{chave}")
        setattr(self, f"base_{chave}", antes + valor)
        if chave in ("hp", "mp"):
            # O teto sobe; o valor ATUAL sobe na mesma fração, para a passiva não
            # virar cura nem deixar o herói com a barra pela metade de graça.
            atual = self._hp if chave == "hp" else self._mp
            fracao = atual / antes if antes > 0 else 1
            novo_teto = getattr(self, f"base_{chave}")
            if chave == "hp":
                self._hp = min(int(novo_teto * fracao), novo_teto)
            else:
                self._mp = min(int(novo_teto * fracao), novo_teto)
        elif chave in ("st", "mg"):
            self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR

    def add_passive_load(self, passive: PassiveCard) -> None:
        self.passives.append(passive)
        self._apply_passive_stats(passive)

    def get_passive_bonus(self, effect_type: str) -> float:
        return sum(float(p.effect_value) for p in self.passives if p.effect_type == effect_type)

    @staticmethod
    def my_type() -> str:
        """Retorna o tipo da entidade."""
        return "Human"

    def get_mp(self) -> int:
        """Retorna os pontos de mana atuais."""
        return int(self._mp)

    def get_st(self) -> int:
        """Retorna a força com buffs aplicados."""
        return self.get_stat("st")

    def get_ag(self) -> int:
        """Retorna a agilidade com buffs aplicados."""
        return self.get_stat("ag")

    def get_mg(self) -> int:
        """Retorna a magia com buffs aplicados."""
        return self.get_stat("mg")

    def get_df(self) -> int:
        """Retorna a defesa com buffs aplicados."""
        return self.get_stat("df")

    @staticmethod
    def get_classname() -> str:
        """Nome da classe. Cada subclasse concreta redefine."""
        return "Player"

    def weighted_power(self, weights) -> float:
        """Como o da entidade, amplificado pelo que o herói empunha.

        A arma entra AQUI, num só lugar, e vale igual para o ataque básico e
        para qualquer skill: as duas são ações do mesmo personagem com a mesma
        arma na mão. Também é o que mantém `mechanics/combat.py` sem uma leitura
        de equipamento — ele pede o poder, não o inventário.
        """
        return super().weighted_power(weights) * (1 + self.weapon_percent() / 100)

    def get_avg_damage(self) -> int:
        """BASE_POWER = (W_classe · [ST, MG, AG]) + poder da arma.

        Os pesos ficam em CLASS_WEIGHTS e são a identidade ofensiva da classe.
        A arma soma sobre esse total; o valor é lido do equipamento e não do
        campo `avg_damage`, para não contar o bônus duas vezes.

        O ataque básico é a skill de pesos fixos: mesma conta, mesmos pesos da
        classe. Por isso passa por `weighted_power` como todo o resto.
        """
        weights = CLASS_WEIGHTS[self.get_classname()]
        return max(1, int(self.weighted_power(tuple((k, weights[k]) for k in ("st", "mg", "ag")))))

    def add_xp_points(self, amount: int) -> None:
        """Adiciona pontos de experiência.

        Args:
            amount: Quantidade de XP a adicionar.
        """
        if self.isalive:
            self.xp_points += amount

    def level_up(self, show: bool = True) -> list[str]:
        """Processa um level up quando XP é suficiente.

        Args:
            show: Se True, retorna mensagens de exibição (default: True).

        Returns:
            Lista de mensagens sobre level up e novas habilidades.
            Retorna lista vazia se não houver XP suficiente.
        """
        needed_xp = self.need_to_up()
        messages: list[str] = []
        if self.xp_points >= needed_xp:
            self.xp_points -= needed_xp
            self.level += 1
            if show:
                messages.append(f"Level up! Agora você está no nível: {self.level}!")
            self._update_stats_on_level_up()
            skill_msgs = self.learn_new_skills(show)
            messages.extend(skill_msgs)
            if show:
                messages.append(f"Você precisa de {self.need_to_next()} XP para o próximo nível.")
        return messages

    MAX_ACTIVE_SKILLS = MAX_ACTIVE_SKILLS

    def learn_new_skills(self, show: bool = True) -> list[str]:
        """Garante a skill inicial da classe. Uma só, no nível 1.

        Era uma por nível até o quarto: o jogador chegava ao nível 4 com o deck
        cheio sem ter escolhido nada. Agora o nível 1 entrega a ASSINATURA da
        classe — fixa, declarada no JSON — e todo o resto do deck vem de escolha.
        """
        messages: list[str] = []
        iniciais = get_initial_skills_for(self.get_classname())
        if not iniciais or self.initial_skills_learned:
            return messages
        skill = iniciais[0]
        self.skills[1] = skill
        self.initial_skills_learned = 1
        self.seen_skill_ids.add(skill.id)
        if show:
            messages.append(f"Nova habilidade aprendida: {skill.name}!")
        return messages

    def active_skill_ids(self) -> list[str]:
        """Os ids das skills ativas, na ordem dos slots."""
        return [s.id for _, s in sorted(self.skills.items())]

    def has_free_skill_slot(self) -> bool:
        return len(self.skills) < self.MAX_ACTIVE_SKILLS

    def is_skill_offer_level(self) -> bool:
        """Se este nível oferece uma escolha de skill. O 1 não oferece: é fixo."""
        return self.level > 1 and self.level % SKILL_OFFER_LEVEL_INTERVAL == 0

    def learn_skill(self, skill) -> str:
        """Aprende no primeiro slot livre. Sem slot, não faz nada.

        Trocar exige `add_skill_with_replacement`, porque a decisão de qual
        carta sai é do jogador — o motor não escolhe por ele.
        """
        self.seen_skill_ids.add(skill.id)
        if not self.has_free_skill_slot():
            return f"Deck cheio: escolha qual carta {skill.name} substitui."
        chave = next(k for k in range(1, self.MAX_ACTIVE_SKILLS + 1) if k not in self.skills)
        self.skills[chave] = skill
        return f"Nova habilidade aprendida: {skill.name}!"

    def can_use_skill(self, skill) -> bool:
        """Se o equipamento atual satisfaz o requisito da carta.

        Requisito bloqueia o USO, nunca a aquisição: o jogador pode aprender uma
        carta de escudo e sair atrás de um escudo. É o que permite pivotar uma
        build em vez de só reagir ao que caiu.
        """
        req = getattr(skill, "requires", None)
        if req is None:
            return True
        maos = [self.equipment.get(p) for p in self.HAND_POSITIONS]
        empunhadas = [p for p in maos if p is not None]
        if req.two_weapons and len(empunhadas) < 2:
            return False
        if req.hands and not any(self.hands_required(p) == req.hands for p in empunhadas):
            return False
        if req.hand_type and not any(
            getattr(p, "hand_type", None) == req.hand_type for p in empunhadas
        ):
            return False
        return True

    def add_skill_with_replacement(self, new_skill: "SkillCard", replace_key: int) -> str:
        """Adiciona nova skill substituindo uma existente na chave especificada.

        Args:
            new_skill: A nova skill a ser adicionada.
            replace_key: A chave da skill a ser substituída.

        Returns:
            Mensagem de confirmação.
        """
        old_skill = self.skills.get(replace_key)
        self.skills[replace_key] = new_skill
        old_name = old_skill.name if old_skill else "Nenhuma"
        return f"Skill {old_name} substituída por {new_skill.name}!"

    def _update_stats_on_level_up(self) -> None:
        """Atualiza o estado derivado do nível e devolve parte dos recursos.

        Os atributos em si não são recalculados aqui: eles são derivados de
        `self.level` pelas propriedades `base_*`, com a mesma razão de
        crescimento que os monstros usam. Subir de nível restaura apenas
        `LEVEL_UP_RESTORE_PERCENT` do máximo — a cura completa a cada nível era
        uma das cinco fontes de cura gratuita que anulavam o atrito da run.
        """
        self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        self.heal(int(self.base_hp * LEVEL_UP_RESTORE_PERCENT / 100))
        self._mp = min(self.base_mp, self._mp + int(self.base_mp * LEVEL_UP_RESTORE_PERCENT / 100))

    def need_to_next(self) -> int:
        """Retorna a quantidade de XP necessária para o próximo nível."""
        return max(0, self.need_to_up() - self.xp_points)

    def need_to_up(self) -> int:
        """XP total necessária para subir de nível.

        A curva vive em `shared/formulas.py` porque `mechanics/` também precisa
        dela: existiam duas curvas de XP no código, e a que ninguém chamava era
        a que parecia oficial. Agora há uma só, e ela fica na camada que as
        duas podem importar.
        """
        return xp_for_level(self.level)

    def set_level(self, target_level: int) -> str:
        """Define o nível do jogador ajustando atributos.

        Args:
            target_level: Nível desejado.

        Returns:
            Mensagem de confirmação.
        """
        self.level = 1
        self.skills.clear()
        self.initial_skills_learned = 0
        for _ in range(target_level - 1):
            self.level += 1
            self._update_stats_on_level_up()
            self.learn_new_skills(show=False)
        self.rest()
        return f"{self.nick_name} foi definido para o nível {self.level}."


class Warrior(Player):
    """Guerreiro — o maior HP efetivo do jogo, o menor pico de dano.

    Identidade: ganha por atrito. Sobrevive a combates longos que matam as
    outras classes, e por isso é quem melhor absorve um encontro que deu errado.
    Fraqueza: contra o tank, que também ganha por atrito e tem mais HP.
    """

    CLASS_BASE = {
        "hp": WARRIOR_BASE_HP,
        "mp": WARRIOR_BASE_MP,
        "st": WARRIOR_BASE_ST,
        "ag": WARRIOR_BASE_AG,
        "mg": WARRIOR_BASE_MG,
        "df": WARRIOR_BASE_DF,
    }

    def __init__(self, nick_name: str) -> None:
        super().__init__(nick_name)
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        self.learn_new_skills(show=False)

    @staticmethod
    def get_classname() -> str:
        """Retorna o nome da classe."""
        return "Warrior"


class Mage(Player):
    """Mago — converte mana em sobrevivência; sem mana, é o mais frágil.

    Identidade: a reserva de mana é o recurso dele para as duas coisas, atacar e
    aguentar. A Égide de Mana absorve parte de cada golpe cobrando MP, então
    toda skill lançada é vida que ele deixa de ter depois — e um Mago sem mana
    fica com o pior orçamento de sobrevivência do jogo.

    É a terceira resposta à mesma pergunta: o Guerreiro absorve com HP e defesa,
    o Ladino evita com agilidade, o Mago paga. Antes da Égide ele não tinha
    resposta nenhuma — mesma vida do Ladino, sem a esquiva — e morria no andar 4
    contra encontros comuns.

    Fraqueza: contra o controlador, que rouba turnos e queima mana, atacando a
    ofensiva e a defesa dele de uma vez.
    """

    # Fração de cada golpe que a barreira pode absorver, se houver mana.
    magic_shield_percent = MAGIC_SHIELD_ABSORB_PERCENT

    CLASS_BASE = {
        "hp": MAGE_BASE_HP,
        "mp": MAGE_BASE_MP,
        "st": MAGE_BASE_ST,
        "ag": MAGE_BASE_AG,
        "mg": MAGE_BASE_MG,
        "df": MAGE_BASE_DF,
    }

    def __init__(self, nick_name: str) -> None:
        super().__init__(nick_name)
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        self.learn_new_skills(show=False)

    @staticmethod
    def get_classname() -> str:
        """Retorna o nome da classe."""
        return "Mage"


class Rogue(Player):
    """Ladino — escolhe quando lutar; evita dano em vez de absorvê-lo.

    Identidade: a agilidade dá a ele a vantagem de acerto e de iniciativa mais
    alta do jogo, permanente mas limitada — a chance de acerto é relativa, então
    ele nunca fica imune como ficava antes. Fraqueza: contra o skirmisher, que
    tem agilidade suficiente para anular essa vantagem.
    """

    CLASS_BASE = {
        "hp": ROGUE_BASE_HP,
        "mp": ROGUE_BASE_MP,
        "st": ROGUE_BASE_ST,
        "ag": ROGUE_BASE_AG,
        "mg": ROGUE_BASE_MG,
        "df": ROGUE_BASE_DF,
    }

    def __init__(self, nick_name: str) -> None:
        super().__init__(nick_name)
        self._hp = self.base_hp
        self._mp = self.base_mp
        self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        self.learn_new_skills(show=False)

    @staticmethod
    def get_classname() -> str:
        """Retorna o nome da classe."""
        return "Rogue"
