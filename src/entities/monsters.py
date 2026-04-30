from __future__ import annotations

from src.entities.base import Entity


class Monster(Entity):
    base_hp, base_mp, base_st, base_ag, base_mg, base_df = 100, 40, 55, 3, 50, 30

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
    ):
        self.nick_name = nick_name
        self.level = max(1, mob_level)
        self.isalive = True

        self._hp = int(hp if hp is not None else self.base_hp)
        self.base_hp = int(hp if hp is not None else self.base_hp)
        self._mp = int(mp if mp is not None else self.base_mp)
        self.base_mp = int(mp if mp is not None else self.base_mp)

        self._st = int(st if st is not None else self.base_st)
        self.base_st = int(st if st is not None else self.base_st)
        self._ag = int(ag if ag is not None else self.base_ag)
        self.base_ag = int(ag if ag is not None else self.base_ag)
        self._mg = int(mg if mg is not None else self.base_mg)
        self.base_mg = int(mg if mg is not None else self.base_mg)
        self._df = int(df if df is not None else self.base_df)
        self.base_df = int(df if df is not None else self.base_df)

        self.avg_damage = (self._st + self._mg) // 3
        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, object] = {}

    def get_avg_damage(self) -> int:
        return self.avg_damage

    @staticmethod
    def my_type() -> str:
        return "COM"

    def get_hp(self) -> int:
        return self._hp

    def get_mp(self) -> int:
        return self._mp

    def get_ag(self) -> int:
        return self._ag

    def get_df(self) -> int:
        return self._df

    def get_st(self) -> int:
        return self._st

    def get_mg(self) -> int:
        return self._mg


