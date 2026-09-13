from __future__ import annotations

from src.entities.base import Entity
from src.shared import effect_core as core
from src.shared.constants import (
    DAMAGE_FORMULA_DIVISOR,
    MONSTER_BASE_AG,
    MONSTER_BASE_DF,
    MONSTER_BASE_HP,
    MONSTER_BASE_MG,
    MONSTER_BASE_MP,
    MONSTER_BASE_ST,
)
from src.shared.effects import sum_buffs


class Monster(Entity):
    """Classe para monstros do jogo (inimigos controlados pelo computador).

    Attributes:
        base_hp: HP base do monstro (constante de classe).
        base_mp: MP base do monstro (constante de classe).
        base_st: Força base do monstro (constante de classe).
        base_ag: Agilidade base do monstro (constante de classe).
        base_mg: Magia base do monstro (constante de classe).
        base_df: Defesa base do monstro (constante de classe).
    """

    base_hp: int = MONSTER_BASE_HP
    base_mp: int = MONSTER_BASE_MP
    base_st: int = MONSTER_BASE_ST
    base_ag: int = MONSTER_BASE_AG
    base_mg: int = MONSTER_BASE_MG
    base_df: int = MONSTER_BASE_DF

    def __init__(
        self,
        nick_name: str,
        mob_level: int = 1,
        *,
        hp: int | None = None,
        mp: int | None = None,
        st: int | None = None,
        ag: int | None = None,
        mg: int | None = None,
        df: int | None = None,
    ) -> None:
        """Inicializa um monstro.

        Args:
            nick_name: Nome do monstro.
            mob_level: Nível do monstro (default: 1).
            hp: HP personalizado (opcional).
            mp: MP personalizado (opcional).
            st: Força personalizada (opcional).
            ag: Agilidade personalizada (opcional).
            mg: Magia personalizada (opcional).
            df: Defesa personalizada (opcional).
        """
        self.nick_name: str = nick_name
        self.level: int = max(1, mob_level)
        self.isalive: bool = True

        self._hp: int = int(hp if hp is not None else self.base_hp)
        self.base_hp: int = int(hp if hp is not None else self.base_hp)
        self._mp: int = int(mp if mp is not None else self.base_mp)
        self.base_mp: int = int(mp if mp is not None else self.base_mp)

        self._st: int = int(st if st is not None else self.base_st)
        self.base_st: int = int(st if st is not None else self.base_st)
        self._ag: int = int(ag if ag is not None else self.base_ag)
        self.base_ag: int = int(ag if ag is not None else self.base_ag)
        self._mg: int = int(mg if mg is not None else self.base_mg)
        self.base_mg: int = int(mg if mg is not None else self.base_mg)
        self._df: int = int(df if df is not None else self.base_df)
        self.base_df: int = int(df if df is not None else self.base_df)

        self.avg_damage: int = (self._st + self._mg) // DAMAGE_FORMULA_DIVISOR
        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, object] = {}

        # Papel no encontro (ver content/factories/archetypes.py). O default
        # mantém o monstro histórico: bruiser sem skills, só ataque básico.
        self.role: str = "bruiser"
        self.skills: list = []
        self.skill_cooldowns: dict[str, int] = {}
        self.skill_use_chance: int = 0
        self.resistances: dict[str, int] = {}
        # Turnos já tomados NESTE combate. A IA usa para saber se está na
        # abertura, quando um buff de duração rende todos os turnos à frente.
        self.turns_taken: int = 0

    def get_stat(self, stat: str) -> int:
        """Valor de um atributo somando os buffs ativos que o modificam.

        Existia só no `Player`. O monstro devolvia o atributo cru, então todo
        buff que ele lançava era escrito em `active_buffs` e nunca lido: a
        Bênção Sombria do suporte gastava mana, turno e recarga para não mudar
        nada. Um arquétipo cujo comportamento não altera o combate não é um
        arquétipo — é uma animação.
        """
        base = int(getattr(self, f"base_{stat}"))
        com_buff = base + sum_buffs(self, stat)
        if stat in ("hp", "mp"):
            return max(1, int(com_buff * (1 + core.resource_percent(self, stat) / 100)))
        # O mesmo piso do herói: o núcleo não pergunta quem é a entidade.
        return core.apply_attribute_floor(
            base, com_buff * (1 + core.attribute_percent(self, stat) / 100)
        )

    def get_avg_damage(self) -> int:
        """BASE_POWER do monstro, derivado dos atributos COM buffs.

        Deriva em vez de devolver `self.avg_damage` congelado no spawn, para
        que um buff de força valha dano — como já vale no herói.
        """
        return max(1, (self.get_st() + self.get_mg()) // DAMAGE_FORMULA_DIVISOR)

    def get_passive_bonus(self, effect_type: str) -> float:
        """Modificadores de combate vindos de passivas. O monstro ainda não tem.

        Existe explícito porque `shared/effects.combat_modifier` procura este
        método por duck typing: sem ele, o monstro entra no cálculo pela metade
        e ninguém percebe. Devolver zero é a resposta correta hoje.

        Equipamento de monstro, quando existir, não entra por aqui: item não se
        disfarça de passiva. Ele terá o próprio caminho, como o herói tem.
        """
        return 0.0

    @staticmethod
    def my_type() -> str:
        """Retorna o tipo da entidade (COM = Computador)."""
        return "COM"

    def get_hp(self) -> int:
        """Retorna os pontos de vida atuais."""
        return self._hp

    def get_mp(self) -> int:
        """Retorna os pontos de mana atuais."""
        return self._mp

    def get_ag(self) -> int:
        """Retorna a agilidade do monstro, com buffs aplicados."""
        return self.get_stat("ag")

    def get_df(self) -> int:
        """Retorna a defesa do monstro, com buffs aplicados."""
        return self.get_stat("df")

    def get_st(self) -> int:
        """Retorna a força do monstro, com buffs aplicados."""
        return self.get_stat("st")

    def get_mg(self) -> int:
        """Retorna a magia do monstro, com buffs aplicados."""
        return self.get_stat("mg")
