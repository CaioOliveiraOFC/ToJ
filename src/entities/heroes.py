from __future__ import annotations

from typing import TYPE_CHECKING

from src.content.skills_loader import get_initial_skills
from src.entities.base import Entity
from src.mechanics.effects import buff_value, sum_buffs
from src.shared.constants import (
    CLASS_WEIGHTS,
    DAMAGE_FORMULA_DIVISOR,
    GROWTH_RATE,
    LEVEL_UP_RESTORE_PERCENT,
    MAGE_BASE_AG,
    MAGE_BASE_DF,
    MAGE_BASE_HP,
    MAGE_BASE_MG,
    MAGE_BASE_MP,
    MAGE_BASE_ST,
    ROGUE_BASE_AG,
    ROGUE_BASE_DF,
    ROGUE_BASE_HP,
    ROGUE_BASE_MG,
    ROGUE_BASE_MP,
    ROGUE_BASE_ST,
    WARRIOR_BASE_AG,
    WARRIOR_BASE_DF,
    WARRIOR_BASE_HP,
    WARRIOR_BASE_MG,
    WARRIOR_BASE_MP,
    WARRIOR_BASE_ST,
)

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
    "magic_resist": ("damage_reduction", "Resistência Mágica"),
    "fire_resist": ("damage_reduction", "Resistência ao Fogo"),
}

# Consumíveis que aplicam um status em vez de um buff de atributo.
POTION_STATUSES = ("poison", "bleed", "stun", "fear", "true_damage", "death_ignore")

POTION_BUFF_DURATION = 3


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
        self.skill_points = 0
        self.unspent_attribute_points: int = 0
        self.inventory: list[object] = []
        self.equipment = {
            "Weapon": None,
            "Helmet": None,
            "Body": None,
            "Legs": None,
            "Shoes": None,
            "Hands": None,
            "Amulet": None,
            "Ring": None,
        }
        self.skills: dict[int, SkillCard] = {}
        self.initial_skills_learned: int = 0
        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, dict[str, object]] = {}
        self.passives: list[PassiveCard] = []
        self.skill_cooldowns: dict[str, int] = {}

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

    def equipment_percent(self, key: str) -> float:
        """Soma, em percentual, o que o equipamento acrescenta a um atributo."""
        total = 0.0
        sources = self.EQUIP_STAT_SOURCES.get(key, ())
        for item in self.equipment.values():
            if item is None:
                continue
            if key == "df":
                total += float(getattr(item, "defense_bonus", 0))
            if getattr(item, "effect_type", None) in sources:
                total += float(getattr(item, "effect_value", 0))
        return total

    def weapon_percent(self) -> float:
        """Percentual de dano acrescentado pela arma equipada."""
        return float(getattr(self.equipment.get("Weapon"), "damage_bonus", 0))

    def _scaled(self, key: str) -> int:
        """Valor do atributo no nível atual: base do nível 1 vezes a razão comum."""
        base = self._growth.get(key, 0)
        grown = int(round(base * (GROWTH_RATE ** (self.level - 1)))) + self._bonus.get(key, 0)
        return int(grown * (1 + self.equipment_percent(key) / 100))

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

    def spend_coins(self, amount: int) -> bool:
        """Gasta moedas se houver saldo suficiente.

        Args:
            amount: Quantidade de moedas a gastar.

        Returns:
            True se a transação foi bem-sucedida, False caso contrário.
        """
        if self.coins >= amount:
            self.coins -= amount
            return True
        return False

    def earn_coins(self, amount: int) -> None:
        """Adiciona moedas ao jogador.

        Args:
            amount: Quantidade de moedas a adicionar.
        """
        self.coins += amount

    def equip(self, item_to_equip: object) -> str | None:
        """Equipa um item no slot correspondente.

        Args:
            item_to_equip: Item a ser equipado.

        Returns:
            Mensagem de confirmação ou mensagem de erro.
        """
        slot = getattr(item_to_equip, "slot", None)
        if not slot or slot not in self.equipment:
            return f"{getattr(item_to_equip, 'name', 'Item')} não pode ser equipado."

        item_classes = getattr(item_to_equip, "classes", None)
        if item_classes is not None and self.get_classname() not in item_classes:
            return f"Sua classe ({self.get_classname()}) não pode equipar {getattr(item_to_equip, 'name', 'Item')}."

        if self.equipment[slot]:
            self.unequip(slot)
        # `remove` sem guarda levantava ValueError quando o item não estava no
        # inventário — o que acontecia em todo carregamento de save com
        # equipamento, porque load_game já havia retirado o item. A exceção era
        # engolida por `except Exception` e o jogador via "save corrompido".
        if item_to_equip in self.inventory:
            self.inventory.remove(item_to_equip)
        self.equipment[slot] = item_to_equip
        # Sem soma de atributo aqui: o bônus é lido dinamicamente das
        # propriedades, o que evita contabilidade duplicada. E sem `rest()`:
        # equipar um item era uma cura completa gratuita e ilimitada.
        self._hp = min(self._hp, self.base_hp)
        return getattr(item_to_equip, "name", "Item")

    def unequip(self, slot: str) -> str | None:
        """Desequipa um item do slot especificado.

        Args:
            slot: Slot do item a ser desequipado.

        Returns:
            Mensagem de confirmação ou None se slot estava vazio.
        """
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
                f"Você usou {item_name}. {label} +{effect_value} "
                f"por {POTION_BUFF_DURATION} turnos!"
            )
        elif effect_type in POTION_STATUSES:
            self.active_effects[effect_type] = {
                "value": effect_value,
                "duration": POTION_BUFF_DURATION,
            }
            msg = f"Você usou {item_name}. Efeito {effect_type} ativo por {POTION_BUFF_DURATION} turnos!"
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

    def _apply_passive_stats(self, passive: PassiveCard) -> None:
        effect_type = passive.effect_type
        value = int(passive.effect_value)

        if effect_type == "max_hp":
            old_base_hp = self.base_hp
            self.base_hp += value
            hp_ratio = self._hp / old_base_hp if old_base_hp > 0 else 1
            self._hp = min(int(self.base_hp * hp_ratio), self.base_hp)
        elif effect_type == "max_mp":
            old_base_mp = self.base_mp
            self.base_mp += value
            mp_ratio = self._mp / old_base_mp if old_base_mp > 0 else 1
            self._mp = min(int(self.base_mp * mp_ratio), self.base_mp)
        elif effect_type == "strength":
            self.base_st += value
            self.avg_damage = (self.base_st + self.base_mg) // DAMAGE_FORMULA_DIVISOR
        elif effect_type == "defense":
            self.base_df += value
        elif effect_type == "agility":
            # Sem teto: com a chance de acerto relativa, agilidade alta é
            # vantagem limitada pela fórmula, não imunidade.
            self.base_ag += value

    def add_passive_load(self, passive: PassiveCard) -> None:
        self.passives.append(passive)
        self._apply_passive_stats(passive)

    def get_passive_bonus(self, effect_type: str) -> float:
        return sum(
            float(p.effect_value)
            for p in self.passives
            if p.effect_type == effect_type
        )

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

    def get_avg_damage(self) -> int:
        """BASE_POWER = (W_classe · [ST, MG, AG]) + poder da arma.

        Os pesos ficam em CLASS_WEIGHTS e são a identidade ofensiva da classe.
        A arma soma sobre esse total; o valor é lido do equipamento e não do
        campo `avg_damage`, para não contar o bônus duas vezes.
        """
        weights = CLASS_WEIGHTS[self.get_classname()]
        base_power = (
            self.get_st() * weights["st"]
            + self.get_mg() * weights["mg"]
            + self.get_ag() * weights["ag"]
        )
        return max(1, int(base_power * (1 + self.weapon_percent() / 100)))

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

    def learn_new_skills(self, show: bool = True) -> list[str]:
        """Aprende skills iniciais uma por nível (níveis 1-4).

        Args:
            show: Se True, inclui mensagens de novas habilidades.

        Returns:
            Lista de mensagens sobre habilidades aprendidas.
        """
        messages: list[str] = []
        # Apenas aprende skills iniciais nos níveis 1-4, uma por nível
        if 1 <= self.level <= 4 and self.initial_skills_learned < self.level:
            initial_skills = get_initial_skills(self.get_classname())
            while self.initial_skills_learned < self.level and self.initial_skills_learned < len(initial_skills):
                skill = initial_skills[self.initial_skills_learned]
                new_key = self.initial_skills_learned + 1
                self.skills[new_key] = skill
                self.initial_skills_learned += 1
                if show:
                    messages.append(f"Nova habilidade aprendida: {skill.name}!")
        return messages

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

        Delega para `math_operations`: existiam duas curvas de XP no código, e
        a que ninguém chamava era a que parecia oficial. Agora há uma só.
        """
        from src.mechanics.math_operations import calculate_xp_for_next_level

        return calculate_xp_for_next_level(self.level)

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
    """Mago — maior pico de dano, menor HP efetivo, refém de MP.

    Identidade: vence rápido ou não vence. Tem o burst para derrubar um alvo
    antes que ele aja, e o menor orçamento de sobrevivência para quando isso
    falha. Fraqueza: contra o controlador, que rouba turnos e queima mana.
    """

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
