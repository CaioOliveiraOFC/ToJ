from __future__ import annotations

from src.entities.base import Entity
from src.shared import effect_core as core
from src.shared.effects import sum_buffs


class Monster(Entity):
    """Classe para monstros do jogo (inimigos controlados pelo computador).

    Todo monstro nasce de `spawn_by_role`, que resolve cada atributo pelo
    orçamento do arquétipo. Por isso o construtor não tem default de atributo:
    um monstro "sem arquétipo" não existe no jogo, e um default aqui seria um
    segundo modelo de monstro — o `MONSTER_BASE_*` de antes, que não batia com o
    orçamento e só servia a quem esquecesse de passar os números.
    """

    def __init__(
        self,
        nick_name: str,
        mob_level: int = 1,
        *,
        hp: int,
        mp: int,
        st: int,
        ag: int,
        mg: int,
        df: int,
        offensive_weights: tuple[tuple[str, float], ...],
        passives: tuple[tuple[str, float], ...] = (),
    ) -> None:
        """Inicializa um monstro.

        Args:
            nick_name: Nome do monstro.
            mob_level: Nível do monstro (default: 1).
            hp, mp, st, ag, mg, df: Atributos já resolvidos pelo arquétipo.
            offensive_weights: Vetor `(atributo, peso)` de onde nasce o ataque
                básico, com Σpesos = 1.
            passives: Modificadores de combate inatos `(tipo, valor)`, lidos por
                `get_passive_bonus`. Sem eles, o monstro não tem nenhum.
        """
        self.nick_name: str = nick_name
        self.level: int = max(1, mob_level)
        self.isalive: bool = True

        # `hp`/`mp` guardam a base CRUA porque `base_hp` e `base_mp` são
        # propriedades — o teto delas é derivado dos efeitos ativos.
        self._base_hp: int = int(hp)
        self._hp: int = self._base_hp
        self._base_mp: int = int(mp)
        self._mp: int = self._base_mp

        self.base_st: int = int(st)
        self.base_ag: int = int(ag)
        self.base_mg: int = int(mg)
        self.base_df: int = int(df)

        self.offensive_weights: tuple[tuple[str, float], ...] = tuple(
            (str(eixo), float(peso)) for eixo, peso in offensive_weights
        )
        self.passive_bonuses: dict[str, float] = {
            str(tipo): float(valor) for tipo, valor in passives
        }

        self.active_effects: dict[str, object] = {}
        self.active_buffs: dict[str, object] = {}

        # Papel no encontro (ver content/factories/archetypes.py). É só a
        # inicialização: `spawn_by_role` preenche papel, deck e chance de skill.
        self.role: str = "bruiser"
        self.skills: list = []
        self.skill_cooldowns: dict[str, int] = {}
        self.skill_use_chance: int = 0
        self.resistances: dict[str, int] = {}
        # Turnos já tomados NESTE combate. A IA usa para saber se está na
        # abertura, quando um buff de duração rende todos os turnos à frente.
        self.turns_taken: int = 0

    # O teto de HP/MP é DERIVADO, como no herói. Era atributo cru, e por isso
    # Vitalidade e Fragilidade mudavam `get_stat("hp")` mas não `base_hp` — que
    # é o teto que `heal()`, a regeneração de mana e o tick de efeitos leem. Na
    # prática, o efeito de recurso funcionava no herói e não funcionava no
    # monstro: assimetria do resolvedor, não decisão de design.
    @property
    def base_hp(self) -> int:
        return max(1, int(self._base_hp * (1 + core.resource_percent(self, "hp") / 100)))

    @base_hp.setter
    def base_hp(self, valor: int) -> None:
        self._base_hp = int(valor)

    @property
    def base_mp(self) -> int:
        return max(0, int(self._base_mp * (1 + core.resource_percent(self, "mp") / 100)))

    @base_mp.setter
    def base_mp(self, valor: int) -> None:
        self._base_mp = int(valor)

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
            # `base_hp`/`base_mp` já são propriedades que aplicam o efeito de
            # recurso; aplicar de novo aqui contaria o mesmo bônus duas vezes.
            return max(1, com_buff)
        # O mesmo piso do herói: o núcleo não pergunta quem é a entidade.
        return core.apply_attribute_floor(
            base, com_buff * (1 + core.attribute_percent(self, stat) / 100)
        )

    def get_avg_damage(self) -> int:
        """BASE_POWER do monstro, derivado dos atributos COM buffs.

        Deriva dos atributos a cada chamada, para que um buff de força valha
        dano — como já vale no herói.

        E usa `weighted_power`, a MESMA função do herói: o monstro passou a ter um
        vetor ofensivo por arquétipo em vez de `(ST + MG) // 3`. A conta antiga
        era um vetor implícito de soma 0.667 que lia Força e Magia sempre em
        partes iguais — então a Agilidade 2.6× do `skirmisher` contribuía ZERO de
        dano básico, e o `GAME_DESIGN` afirmava que os dois lados usavam a mesma
        gramática enquanto só o herói usava.
        """
        return max(1, int(self.weighted_power(self.offensive_weights)))

    def get_passive_bonus(self, effect_type: str) -> float:
        """Modificadores de combate vindos das passivas inatas do arquétipo.

        Existe explícito porque `shared/effects.combat_modifier` procura este
        método por duck typing: sem ele, o monstro entra no cálculo pela metade
        e ninguém percebe. O valor vem de `passives` no `monsters.json`, e o papel
        que não declara nada devolve zero — sem fonte, sem modificador.

        Equipamento de monstro, quando existir, não entra por aqui: item não se
        disfarça de passiva. Ele terá o próprio caminho, como o herói tem.
        """
        return self.passive_bonuses.get(effect_type, 0.0)

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
