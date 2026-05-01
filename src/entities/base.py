from __future__ import annotations


class Entity:
    """Classe base para todas as entidades do jogo (estado puro).

    Mantém o estilo e a API usadas pelo código legado (getters/setters),
    mas sem dependências de UI ou de outras camadas.

    Attributes:
        _hp: Pontos de vida atuais (protegido).
        _mp: Pontos de mana atuais (protegido).
        isalive: Indica se a entidade está viva.
        nick_name: Nome da entidade.
        level: Nível da entidade.
    """

    def reduce_hp(self, quantty: int) -> None:
        """Reduz HP da entidade pela quantidade especificada.

        Args:
            quantty: Quantidade de dano a ser aplicada.
        """
        self._hp -= quantty

    def take_damage(self, amount: int) -> None:
        """Reduz HP encapsulado (preferido por mechanics/)."""
        self.reduce_hp(int(amount))

    def heal(self, amount: int) -> None:
        """Recupera HP até o máximo base.

        Args:
            amount: Quantidade de HP a ser recuperada.
        """
        cur = int(self.get_hp())
        cap = int(getattr(self, "base_hp", cur))
        self._hp = min(cap, cur + int(amount))

    def reduce_mp(self, cost: int) -> None:
        """Reduz MP da entidade pelo custo especificado.

        Args:
            cost: Custo de mana a ser reduzido.
        """
        self._mp -= cost

    def get_isalive(self) -> bool:
        """Retorna True se a entidade está viva."""
        return self.isalive

    def set_isalive(self, state: bool = True) -> None:
        """Define o estado de vida da entidade.

        Args:
            state: True para vivo, False para morto (default: True).
        """
        self.isalive = state

    def get_nick_name(self) -> str:
        """Retorna o nome da entidade."""
        return self.nick_name

    def get_level(self) -> int:
        """Retorna o nível da entidade."""
        return self.level

    def get_hp(self) -> int:
        """Retorna os pontos de vida atuais."""
        return int(self._hp)


