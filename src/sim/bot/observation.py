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
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InteractionView:
    """Uma LEI do jogo que esta ação destrava contra este alvo, AGORA.

    Fato, nunca estratégia. Não existe `interaction_is_good` nem
    `interaction_score`: o que vale a pena é pergunta da policy, e ela é
    respondida com estes números, não com uma opinião embutida no adaptador.

    `interactions.py` declara as leis; `interactions.opportunities()` responde
    quais existem no estado atual. O adaptador transporta — não reproduz.
    """

    interaction_id: str
    label: str
    kind: str  # strike | apply | tick
    # A prosa do catálogo, para o trace dizer o que foi visto.
    trigger: str = ""
    requires_critical: bool = False
    # INFORMATIVO, e é preciso ler isto antes de usar: `expected_strike_damage`
    # JÁ INCLUI este fator, porque `combat.damage_modifiers` chama
    # `strike_xmult(strike_interactions(...))` por dentro. Medido: 131 de dano
    # sem invisibilidade, 157 com. Multiplicar de novo conta duas vezes.
    #
    # NEUTRO É 1.0, nunca 0.0: é multiplicador, e 0.0 zeraria o dano — um
    # neutro que zera é a armadilha esperando a primeira multiplicação
    # distraída.
    damage_xmult: float = 1.0
    # Turnos a mais que o efeito entra, quando a lei mexe em duração.
    duration_bonus: int = 0
    # O que a lei GASTA ao disparar, e de quem. "" quando não gasta nada.
    consumes_status: str = ""
    consumes_from_self: bool = False


@dataclass(frozen=True, slots=True)
class StatusView:
    """Um efeito que ESTA ação aplica no alvo, com a consequência inteira.

    Principal ou `secondary`, é a MESMA peça do jogo: `combat.apply_skill` passa
    as duas pelo mesmo `apply_effect`, com a mesma resistência e as mesmas leis
    de interação. Uma ação que aplica dois efeitos declara dois destes.

    Antes só cabia um efeito por ação, num punhado de campos soltos no view. 66
    das 150 cartas do catálogo têm `secondary` — 24 delas são skills de status
    que aplicam DOIS efeitos —, e o segundo simplesmente não existia para o bot,
    ou chegava sem a consequência que o primeiro tinha.
    """

    effect: str
    # Chance EFETIVA, já descontada a resistência do alvo.
    chance: float = 0.0
    duration: int = 0
    # Se o status rouba turno. É lei do jogo (`shared/effects`), lida pelo
    # adaptador — a policy não classifica efeito, só usa a classificação.
    skips_turn: bool = False
    # Já está no ar? Reaplicar é turno morto, e era assim que o combate do
    # Ladino inflava de 11 para 50 turnos.
    already_active: bool = False
    # Dano por turno e duração, quando o efeito é da família DoT.
    dot_damage_per_turn: int = 0
    dot_duration: int = 0
    # Consequências MEDIDAS quando o efeito é de ATRIBUTO: o golpe dos dois lados
    # e a ordem de turno, com o efeito no ar. Zero/None = não muda.
    incoming_damage_after: int = 0
    outgoing_damage_after: int = 0
    acts_before_enemy_after: bool | None = None
    # MP que o dreno tira do alvo dentro do horizonte, quando o efeito é DRAIN.
    target_mp_drained: int = 0


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
    # INCLUI as INTERAÇÕES DE GOLPE (Emboscada, Quebra Gélida). Elas não são um
    # estágio posterior: `combat.damage_modifiers` chama
    # `strike_xmult(strike_interactions(...))` por dentro e as entrega dentro do
    # bucket ×MULT, ao lado do crítico e sob o mesmo teto. Medido: 131 de dano
    # sem invisibilidade, 157 com. Por isso `InteractionView.damage_xmult` é
    # INFORMATIVO — multiplicar por ele aqui conta a interação duas vezes.
    #
    # NÃO inclui, porque são estágios POSTERIORES no motor: Égide de Mana,
    # procs on-hit, roubo de vida e `death_ignore`. Chamá-lo de `final_damage`
    # seria mentir sobre três estágios.
    expected_strike_damage: int = 0
    # As DUAS pontas da média acima, sem a média. Existem porque "mata agora" não
    # pode sair de uma expectativa: o golpe sem crítico é a certeza, o golpe com
    # crítico é o que só acontece com `crit_chance`. Com os dois, a policy calcula
    # a CHANCE de resolver o turno por aritmética exata, sem rolar nada.
    strike_damage_no_crit: int = 0
    strike_damage_on_crit: int = 0
    hit_chance: float = 1.0
    crit_chance: float = 0.0
    healing: int = 0
    mana_cost: int = 0
    mana_restored: int = 0
    cooldown: int = 0
    duration: int = 0
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
    # Quantas unidades deste consumível restam. Recurso finito é decisão, e sem
    # o número a policy não sabe que está gastando o último.
    uses_left: int = 0
    # O buff que esta ação aplica já está no ar? Reaplicar é turno morto, e era
    # assim que o combate do Ladino inflava de 11 para 50 turnos. Para STATUS a
    # resposta vive em `StatusView.already_active`, um por efeito aplicado.
    already_active: bool = False
    # Os efeitos que esta ação aplica NO ALVO — principal e `secondary`, sem
    # distinção, porque o motor também não faz distinção.
    statuses: tuple[StatusView, ...] = ()
    flee_chance: float = 0.0
    # As leis que ESTA ação destrava contra ESTE alvo, no estado atual.
    interactions: tuple[InteractionView, ...] = ()
    # Os efeitos que a ação QUEBRA ao causar dano — `sleep` é o caso do jogo
    # hoje (`effect_core.definition(...).breaks_on_damage`). Tupla e não string:
    # a ação quebra TODOS os que quebram com dano, e fixar "apenas um" seria
    # limitação artificial do contrato.
    breaks_statuses: tuple[str, ...] = ()
    # Turnos de controle que ESTA ação abre mão, em VALOR ESPERADO. O benefício
    # da interação já está dentro de `expected_strike_damage`; isto é o preço.
    #
    # Fracionário porque a perda quase nunca é certa, e tratá-la como certa
    # cobrava caro demais de todo golpe contra alvo controlado:
    #
    #   - Quebra Gélida gasta o gelo só se o golpe ACERTAR e for CRÍTICO;
    #   - o sono só é quebrado se a ação realmente CAUSAR dano;
    #   - Emboscada é o caso oposto: `invisible` sai NA TENTATIVA, inclusive no
    #     erro — custo certo, e por isso ele viaja em `incoming_damage_after`,
    #     não aqui (ocultação não rouba turno).
    forfeited_control_turns: float = 0.0


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
    """Uma casa de serviço alcançável, e o que o desvio até ela cobra.

    `desvio` é em PASSOS, e passo não tem custo mecânico no jogo: `move_player`
    só move o herói e resolve a casa em que ele pisou — não há contador de
    turnos, fome, decaimento nem respawn. Por isso ele é DESEMPATE, e não
    parcela de utilidade.

    O que o desvio cobra de verdade são os ENCONTROS que ele força, e eles são
    contados por casa ÚNICA: um monstro que caia na ida e na volta é um combate
    só, porque depois do primeiro ele não existe mais.
    """

    tipo: str
    desvio: int
    lutas_no_desvio: int = 0


@dataclass(frozen=True, slots=True)
class EventoView:
    """O `?` do mapa: o que o jogador sabe ANTES de pisar nele.

    O mapa desenha `?` e nada mais. O tipo — Mercador, Altar ou Fonte — só é
    revelado por `move_player`, que ao revelar JÁ consumiu a casa. Por isso esta
    view não tem campo de tipo: ela carrega o desvio e as consequências
    PÚBLICAS dos três desfechos possíveis, que são regra de jogo e não segredo
    do andar.

    O tipo chegava ao cérebro em `MapState.evento` e virava a FAMÍLIA da opção,
    e o evaluator entrava direto no ramo da Fonte ou do Altar. O bot escolhia o
    caminho sabendo o resultado escondido.
    """

    desvio: int
    lutas_no_desvio: int = 0
    # Fração do HP máximo que a Fonte devolve, e que o Altar cobra. Constantes
    # canônicas do jogo, não estimativas.
    cura_da_fonte: float = 0.0
    custo_do_altar: float = 0.0
    # O custo do Altar derrubaria o herói AGORA? `take_damage` não tem piso, e
    # `get_hp() <= 0` encerra a run.
    altar_mataria: bool = False
    # Quantos desfechos o sorteio tem. Regra pública (`RANDOM_EVENT_TYPES`), e é
    # o denominador honesto da chance de cada um.
    desfechos: int = 1


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
    alvo_mp: int
    alvo_mp_max: int
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
    # BOOLEANO, e nunca o tipo: o mapa desenha `?`. O que o bot pode saber sobre
    # o desfecho vive em `EventoView`, e é só regra pública.
    tem_evento: bool = False
    evento: EventoView | None = None
    desvio_extracao: int | None = None
    # Encontros obrigatórios na rota até o `E`, por casa ÚNICA. A extração
    # TERMINA nele — não há "e depois a saída" —, então o que conta é o custo de
    # chegar, e não o desvio de passar por ele antes de sair do andar.
    lutas_ate_extracao: int = 0

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
    # Tenho a Chave de Extração? Ela cai de monstro derrotado, o teto é uma, e
    # sem ela a casa `E` não deixa encerrar a run. É informação do próprio
    # bolso do herói — o jogador sabe o que carrega.
    tem_chave: bool = False
    # Quantas peças o Ferreiro REALMENTE pode mexer, pelas funções canônicas
    # `forge.enhanceable` e `forge.socketable`. "Tem peça equipada" era proxy: um
    # herói com tudo no teto ganhava valor por visitar quem não tem o que fazer.
    pecas_para_o_ferreiro: int = 0
    # Quanto do multiplicador de Essência a PRÓXIMA saída não paga custaria, já
    # com o piso de `essence_after_penalty`. É o preço real de sair sem pagar —
    # o evaluator usava um `-0.5` inventado no lugar dele.
    perda_de_essencia: float = 0.0
    # --- HISTÓRICO OBSERVADO DA RUN -------------------------------------
    #
    # Aqui NÃO entram sinais pré-digeridos. Havia uma tupla de textos
    # (`HP em 22%`, `3 saídas não pagas`) que o cérebro só conseguia CONTAR, e
    # `len(sinais) - 1` era a decisão inteira: dois textos convenciam, um não.
    # Magnitude não existia — HP 34% e HP 4% eram o mesmo voto.
    #
    # O que entra são números que a própria run mediu. O jogador os conhece:
    # ele viu cada golpe que tomou e cada andar que atravessou.

    # DANO REAL RECEBIDO por encontro, em fração do teto de HP. Não é
    # `HP de entrada - HP de saída`: o delta líquido é contaminado por cura e
    # Égide, e diria que uma luta cara foi barata porque o herói bebeu no meio.
    # Cada encontro é normalizado pelo teto DAQUELE momento, porque o teto cresce.
    dano_por_luta: float = 0.0
    # Quantos encontros sustentam esse número. Zero significa SEM EVIDÊNCIA, e
    # sem evidência não se inventa média — ver `_runway_relativo`.
    combates_observados: int = 0
    # Quantas lutas custou um andar, pela média dos andares já CONCLUÍDOS.
    lutas_por_andar: float = 0.0
    andares_concluidos: int = 0
    # Cura DETERMINÍSTICA que já está na mão, em fração do teto de HP. Só entra o
    # que é conhecido e certo: poção que já possuo. NÃO entram o `?` que talvez
    # seja Fonte, o drop que talvez caia, o preço que a Loja talvez tenha, nem o
    # descanso do próximo andar — nenhum deles é conhecido agora.
    cura_garantida: float = 0.0

    @property
    def hp_frac(self) -> float:
        return self.hp / max(1, self.hp_max)

    @property
    def mp_frac(self) -> float:
        return self.mp / max(1, self.mp_max)
