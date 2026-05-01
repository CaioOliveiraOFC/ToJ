from __future__ import annotations

from src.entities.base import Entity
from src.shared.constants import (
    DAMAGE_FORMULA_DIVISOR,
    MONSTER_BASE_AG,
    MONSTER_BASE_DF,
    MONSTER_BASE_HP,
    MONSTER_BASE_MG,
    MONSTER_BASE_MP,
    MONSTER_BASE_ST,
)


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

    def get_avg_damage(self) -> int:
        """Retorna o dano médio do monstro."""
        return self.avg_damage

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
        """Retorna a agilidade do monstro."""
        return self._ag

    def get_df(self) -> int:
        """Retorna a defesa do monstro."""
        return self._df

    def get_st(self) -> int:
        """Retorna a força do monstro."""
        return self._st

    def get_mg(self) -> int:
        """Retorna a magia do monstro."""
        return self._mg


