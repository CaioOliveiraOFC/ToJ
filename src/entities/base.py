from __future__ import annotations


class Entity:
    """
    Classe base (estado puro).

    Nota: Mantém o estilo e a API usadas pelo código legado (getters/setters),
    mas sem dependências de UI (`rich`) ou de outras camadas.
    """

    def reduce_hp(self, quantty: int) -> None:
        self._hp -= quantty

    def take_damage(self, amount: int) -> None:
        """Reduz HP encapsulado (preferido por `mechanics/`)."""
        self.reduce_hp(int(amount))

    def heal(self, amount: int) -> None:
        """Recupera HP até o máximo base."""
        cur = int(self.get_hp())
        cap = int(getattr(self, "base_hp", cur))
        self._hp = min(cap, cur + int(amount))

    def reduce_mp(self, cost: int) -> None:
        self._mp -= cost

    def get_isalive(self) -> bool:
        return self.isalive

    def set_isalive(self, state: bool = True) -> None:
        self.isalive = state

    def get_nick_name(self) -> str:
        return self.nick_name

    def get_level(self) -> int:
        return self.level

    def get_hp(self) -> int:
        return int(self._hp)


