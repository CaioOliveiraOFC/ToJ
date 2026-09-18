"""O que o bot SABE. Dataclasses frozen, escalares, e nada mais.

Este módulo é a fronteira de informação, e ela é estrutural e não disciplinar: o
cérebro não recebe `Hero`, `Monster`, `Skill` nem `Item`, então não existe o gesto
"ler `.level` do monstro" — ele não tem o monstro. A regressão anterior entrou
exatamente por aí, com a seleção de alvo lendo `get_nick_name()` e `.level` de uma
casa que o jogador vê como `&`.

Divisão de trabalho, e ela é a regra central deste pacote:

    ADAPTADOR  responde "o que esta ação FAZ"   -> ActionMechanicsView
    POLICY     responde "quanto isso VALE agora" -> Score

Nenhuma fórmula de combate vive aqui nem em `evaluators.py`. Dano, mitigação,
chance de acerto, crítico e cura são calculados pelo adaptador com as funções
canônicas do jogo (`mechanics/combat.py`) e entregam FATOS. Copiar essas contas
para cá criaria um segundo simulador, que é exatamente o que a refatoração
existe para não fazer.

`sim/` não importa `engine/` (regra em `tests/test_architecture.py`), e este
pacote também não importa `entities/`, `content/` nem `mechanics/`.

Nada aqui carrega RNG futuro, próximo drop, próxima oferta ou resultado.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class ActionMechanicsView:
    """O que uma ação FAZ. Fatos mecânicos, nenhuma decisão.

    Produzido pelo adaptador a partir das funções canônicas do jogo. A policy lê
    estes números e decide o valor; ela não os recalcula, e não conhece a
    fórmula que os gerou.

    Todos os campos são opcionais porque uma ação usa poucos: um golpe preenche
    dano e acerto, um buff preenche atributo e duração, uma fuga preenche só a
    chance.
    """

    # NOME PELO ESTÁGIO REAL DO PIPELINE, e não pelo que seria conveniente.
    #
    # Isto é o que sai do FUNIL de `mechanics.combat._calculate_damage`:
    # BASE + flat, ×(1+Σmult), ×Πxmult capado, × curva de defesa, × mitigação —
    # já com a expectativa do crítico embutida pelo adaptador.
    #
    # NÃO inclui, porque são estágios POSTERIORES no motor: Égide de Mana,
    # procs on-hit, roubo de vida, `death_ignore` e as interações de golpe.
    # Chamá-lo de `final_damage` seria mentir sobre três estágios.
    expected_strike_damage: int = 0
    hit_chance: float = 1.0
    crit_chance: float = 0.0
    healing: int = 0
    mana_cost: int = 0
    mana_restored: int = 0
    cooldown: int = 0
    duration: int = 0
    # Chance EFETIVA, já descontada a resistência do alvo.
    status_chance: float = 0.0
    status_effect: str = ""
    # Se o status rouba turno. É lei do jogo (`shared/effects`), lida pelo
    # adaptador — a policy não classifica efeito, só usa a classificação.
    status_skips_turn: bool = False
    buff_stat: str = ""
    buff_value: float = 0.0
    # O que esta ação faz com os dois golpes, se ela os altera. Zero = não altera.
    # Existem para que a policy não precise da fórmula de defesa: ela recebe o
    # golpe DEPOIS da ação como fato e faz aritmética de turnos sobre ele.
    # Ambos são dano ESPERADO — mesma unidade de `CombatState.alvo_dano` e
    # `dano_basico`, com a chance de acerto embutida. É por isso que agilidade e
    # evasão aparecem aqui: elas só existem dentro de `hit_chance`.
    incoming_damage_after: int = 0
    outgoing_damage_after: int = 0
    # Iniciativa, derivada de `battle.build_turn_order`. `None` quando a ação não
    # mexe na ordem. Agilidade muda TRÊS coisas no motor — acerto, esquiva e
    # ordem —, e sem este campo a terceira não existia para o bot.
    acts_before_enemy: bool | None = None
    acts_before_enemy_after: bool | None = None
    # Quanto do próximo golpe a Égide ainda absorve com o MP ATUAL. Leitura
    # não-mutante: não gasta mana e não simula ataque.
    aegis_absorbable_damage: int = 0
    # Dano por turno e duração do efeito ao longo do tempo que a ação aplica.
    dot_damage_per_turn: int = 0
    dot_duration: int = 0
    # Quantas unidades deste consumível restam. Recurso finito é decisão, e sem
    # o número a policy não sabe que está gastando o último.
    uses_left: int = 0
    # O buff/status que esta ação aplica já está no ar? Reaplicar é turno morto,
    # e era assim que o combate do Ladino inflava de 11 para 50 turnos.
    already_active: bool = False
    flee_chance: float = 0.0


@dataclass(frozen=True, slots=True)
class TargetView:
    """Um monstro como o MAPA o mostra.

    `MapOfGame.draw_map` desenha `&`, ou `B` se for chefe. Nome, nível e
    atributos NÃO estão no mapa: aparecem na ficha, depois da colisão. Por isso
    esta view tem quatro campos e nenhum identifica o monstro.
    """

    casa: tuple[int, int]
    passos: int
    # Quantas OUTRAS lutas a rota até ele obriga. Um monstro a 3 passos com dois
    # na frente custa três lutas; um a 9 com o caminho livre custa uma.
    extras: int
    chefe: bool


@dataclass(frozen=True, slots=True)
class ServiceView:
    """Uma casa de serviço alcançável, e o desvio que ela cobra."""

    tipo: str
    desvio: int


@dataclass(frozen=True, slots=True)
class CombatState:
    """A posição de combate, do ponto de vista do herói, NESTE turno.

    É **estado observado**, e só isso: as ações legais chegam à policy por outro
    caminho (`tuple[ActionOption]`), para que exista uma fonte só de cada coisa.

    Só existe depois da colisão. A colisão é o evento que revela — não a chamada
    de render: em headless `render_fight_intro` nunca roda, e o bot não pode
    depender da UI para saber o que sabe. O adaptador guarda o que a ficha humana
    revelaria e remonta este estado a cada turno do herói.

    `alvo_*` carrega SÓ o que `render_compare_opponents` mostra.
    """

    turno: int
    hp: int
    hp_max: int
    mp: int
    mp_max: int
    # Meu golpe básico contra ESTE alvo, já calculado pelo adaptador.
    dano_basico: int
    alvo_nivel: int
    alvo_hp: int
    alvo_hp_max: int
    # O golpe dele em mim, já calculado pelo adaptador.
    alvo_dano: int
    alvo_efeitos: tuple[str, ...] = ()
    meus_efeitos: tuple[str, ...] = ()

    @property
    def hp_frac(self) -> float:
        return self.hp / max(1, self.hp_max)

    @property
    def mp_frac(self) -> float:
        return self.mp / max(1, self.mp_max)

    def turnos_para_matar(self, dano_por_turno: int | None = None) -> int:
        """Quantos turnos até o alvo cair, no ritmo informado.

        Aritmética sobre um fato que o adaptador entregou, não fórmula de
        combate: não há mitigação, acerto nem crítico nesta conta.
        """
        dano = self.dano_basico if dano_por_turno is None else dano_por_turno
        return max(1, math.ceil(max(0, self.alvo_hp) / max(1, dano)))

    def turnos_para_morrer(self, hp: int | None = None) -> int:
        vida = self.hp if hp is None else hp
        return max(1, math.ceil(max(0, vida) / max(1, self.alvo_dano)))

    @property
    def horizonte(self) -> int:
        """Quantos turnos este combate ainda deve durar, pelo ritmo atual.

        É o denominador de toda decisão de recurso: mana só vale o que ainda pode
        virar ação, e o que decide isso é quantos turnos sobram.
        """
        return max(1, min(self.turnos_para_matar(), self.turnos_para_morrer()))


@dataclass(frozen=True, slots=True)
class MapState:
    """O andar como o jogador o vê na tela do mapa."""

    andar: int
    posicao: tuple[int, int]
    passos_ate_saida: int | None
    alvos: tuple[TargetView, ...] = ()
    monstros_no_andar: int = 0
    servicos: tuple[ServiceView, ...] = ()
    evento: str | None = None
    desvio_evento: int | None = None
    desvio_extracao: int | None = None

    def servico(self, tipo: str) -> ServiceView | None:
        for s in self.servicos:
            if s.tipo == tipo:
                return s
        return None


@dataclass(frozen=True, slots=True)
class ProgressionState:
    """O que a run acumulou, e o que ela deve.

    NÃO tem limiar de apetite. `Perfil.hp_engajar`/`mp_engajar` continuam
    existindo no driver por compatibilidade de CLI e de teste, mas fora do
    caminho de decisão novo: reintroduzi-los aqui seria o gate voltando pela
    porta dos fundos, e a macro policy decide por necessidade e utilidade.
    """

    nivel: int
    hp: int
    hp_max: int
    mp: int
    mp_max: int
    ouro: int
    taxa_de_saida: int
    streak_nao_pagas: int = 0
    pocoes_de_cura: int = 0
    passivas: int = 0
    pecas_equipadas: int = 0
    # Sinais de risco JÁ apurados pelo adaptador, como texto. Entram na decisão
    # de extrair; nenhum deles freia combate — um gate de "estou atrasado" fecha
    # o ciclo errado, porque lutar é o que recupera o atraso.
    sinais_de_risco: tuple[str, ...] = field(default_factory=tuple)

    @property
    def hp_frac(self) -> float:
        return self.hp / max(1, self.hp_max)

    @property
    def mp_frac(self) -> float:
        return self.mp / max(1, self.mp_max)

    @property
    def tem_o_que_preservar(self) -> bool:
        return self.nivel >= 3 or self.passivas >= 2 or self.pecas_equipadas >= 2
