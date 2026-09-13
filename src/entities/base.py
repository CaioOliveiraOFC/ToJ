from __future__ import annotations

from src.shared.constants import SKILL_COST_REFERENCE_MP
from src.shared.formulas import geometric


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

    def get_status_resistance(self, status: str) -> float:
        """Resistência a um status negativo, em percentual de 0 a 100.

        Herói e monstro respondem por aqui, e os dois começam em zero. É o único
        ponto que o combate consulta, então um item que dê `+40% de resistência a
        atordoamento` entra somando neste retorno — sem exceção nova dentro do
        combate.

        Não confundir com resistência a DANO: esta muda a chance de o estado
        pegar, não o tamanho do golpe.
        """
        return float((getattr(self, "resistances", None) or {}).get(status, 0) or 0)

    def weighted_power(self, weights) -> float:
        """Σ(atributo × peso): o BASE de uma ação, antes de entrar no funil.

        A AÇÃO traz os pesos — a classe, no ataque básico; a carta, na skill. A
        ENTIDADE traz os números. É a divisão que impede a skill de virar um
        segundo sistema de dano: a carta escolhe de quais atributos o golpe
        nasce, e nunca quanto ele vale.

        Fica aqui, e não em `mechanics/combat.py`, porque resolver atributo é da
        camada de entidade. O combate resolve o GOLPE; quanto vale o atributo
        que entra nele é resposta de quem é dono do atributo — inclusive do que
        o personagem empunha, que o combate não pode enxergar.

        `weights` é uma sequência de pares `(atributo, peso)`. Dado puro: a
        entidade não conhece `SkillCard` nem `ScalingTerm`.
        """
        return sum(float(self.get_stat(stat)) * float(peso) for stat, peso in weights)

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

    def skill_mana_cost(self, skill) -> int:
        """Quanto esta entidade paga para lançar `skill`.

        Mora aqui, e não no motor, porque quem lança é quem tem o teto de mana —
        e porque `ui/` precisa mostrar o mesmo número que `mechanics/` vai
        cobrar, sem poder importar `mechanics/`. Um custo calculado num lugar e
        exibido em outro é como a tela promete 25 e o motor tira 67.

        Cartas com `mana_cost_percent` pagam essa fração da mana de REFERÊNCIA do
        nível — não da própria. A diferença é a identidade das classes: cobrar
        uma fração da mana de quem lança faz todo mundo lançar o mesmo número de
        skills, e a reserva do Mago deixa de valer alguma coisa. Com a
        referência comum, quem tem mana acima dela lança mais vezes, que é o
        ponto de ter mais mana.

        As demais pagam o valor absoluto do JSON. Nunca zero: skill de graça não
        tem decisão por trás.
        """
        percentual = float(getattr(skill, "mana_cost_percent", 0) or 0)
        if percentual <= 0:
            return int(getattr(skill, "mana_cost", 0) or 0)
        referencia = geometric(SKILL_COST_REFERENCE_MP, int(getattr(self, "level", 1) or 1))
        return max(1, int(referencia * percentual / 100))

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
