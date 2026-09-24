"""Quanto cada ação VALE agora. Nenhuma fórmula de combate vive aqui.

O adaptador já respondeu "o que esta ação faz" — dano esperado, chance de
acerto, cura, custo de mana, duração, chance de status, e o golpe de cada lado
DEPOIS da ação. Este módulo só faz aritmética de turnos sobre esses fatos.
Reescrever mitigação, acerto ou crítico aqui criaria um segundo simulador.

## A moeda do combate

A MARGEM DA CORRIDA, em turnos:

    margem = turnos_para_morrer − turnos_para_matar

Positiva, estou ganhando. Toda ação é avaliada pelo que faz com ela, e cada
efeito entra com o próprio nome em `Score.components`:

- **duração** — o que a ação faz com o tamanho do combate (dano agora, DoT ao
  longo do tempo, ritmo reforçado por buff);
- **cura, égide, mitigação, controle, iniciativa, recurso negado** — o que ela
  faz com o tempo que eu tenho e com as respostas que o inimigo ainda dá;
- **estado gasto** — o que ela cobra: gelo consumido, sono acordado;
- **recurso, recarga, escassez** — custo de oportunidade de mana, cooldown e
  consumível finito, os três limitados pelo próprio ganho da ação;
- **déficit** — quanto falta para eu vencer a corrida, com esta ação.

Uma ação que não causa dano custa um turno de duração — e isso aparece como
parcela negativa, não como exceção no código. É a mesma conta para atacar,
curar, buffar, controlar e usar item.

Duas quantizações NÃO se misturam: tudo é fracionário. E a linha de base tem
piso de um turno, porque nenhuma ação leva menos que isso.

## Por que a mana passa a valer

A policy anterior comparava a skill com o ataque básico por dano imediato. Como
o básico é gratuito, mana NUNCA tinha valor, e o Mago morreu com 85–100% de MP
em cinco de cinco runs.

Aqui o custo da mana é uma ESCASSEZ derivada, sem constante inventada:

    cargas  = mp // custo            quantas vezes ainda dá para lançar
    escassez = 0                     se cargas >= horizonte do combate
             = 1 - cargas/horizonte  se não

Com a barra cheia e um combate de três turnos, `cargas` cobre o horizonte,
`escassez` é zero e a skill disputa pelo que ela faz. Com a barra no fim e um
combate longo, `escassez` chega perto de 1 e o custo se aproxima do próprio
ganho. No turno em que morrer é possível, o horizonte é 1 e guardar mana vale
zero.

É regra de qualquer classe: o Mago gasta mais porque tem mais ações que
consomem e que pontuam, não porque exista `if Mage`.
"""

from __future__ import annotations

import math

from src.shared.constants import ARENA_EQUIVALENCE_BAND
from src.sim.bot.decision import ActionOption, Need, Score
from src.sim.bot.observation import CombatState, MapState, ProgressionState

# Abaixo disto continuar é aposta, e sair passa a valer algo. É o ÚNICO limiar
# de HP do cérebro, e ele não é um portão: nenhuma ação é barrada por ele. Ele
# faz a utilidade da retirada ficar positiva, e a retirada ganha por ser de
# necessidade mais urgente — não por impedir as outras de serem avaliadas.
HP_DE_APOSTA = 0.35

# As bandas da build, contra o alvo da Arena. Os nomes vivem aqui porque
# classificar é POLÍTICA; o número que as separa vive em `shared.constants`, que
# é fonte única e também é de onde `sim.arena` o lê.
# Quatro MARCOS COMPORTAMENTAIS, não uma banda estatística de equivalência. Os
# cortes saem do mesmo `ARENA_EQUIVALENCE_BAND` mais o 1,00, que é o ponto de
# igualdade da própria razão — nenhuma constante nova.
ABAIXO = "ABAIXO"  # < 0,95        ainda abaixo do aceitável
CLOSE_ENOUGH = "CLOSE_ENOUGH"  # 0,95 a 1,00 abaixo do alvo, mas aceitável
META_BATIDA = "META_BATIDA"  # 1,00 a 1,05 alvo da Arena atingido
HARD_STOP = "HARD_STOP"  # > 1,05      limite de ganância

# Os estados do fôlego. Não são limiares novos: `runway = 1` é o empate da
# própria razão e `runway = 0` é o fim dela.
SAUDAVEL = "SAUDAVEL"
CURTO = "CURTO"
ESGOTADO = "ESGOTADO"

# A fuga abre mão da recompensa do encontro. O número não converte ouro em
# turnos: é o desconto sobre o valor de fugir quando a luta ainda é vencível.
PESO_DA_RECOMPENSA_PERDIDA = 1.0


# --- combate --------------------------------------------------------------


def _linha_de_base(state: CombatState) -> float:
    """Quantos turnos a luta leva se eu só bater, a partir de agora.

    PISO DE 1 TURNO, e ele é a correção de um defeito: sem piso, um alvo com 13
    de HP diante de um golpe de 100 dava `turnos_base = 0,13`, enquanto qualquer
    ação media pelo menos 1,00. O golpe letal aparecia com `duração −0,87` e
    perdia para a poção, que marcava 0,00. Nenhuma ação leva menos de um turno;
    a linha contra a qual todas são medidas também não pode levar.
    """
    return max(1.0, state.alvo_hp / max(1, state.dano_basico))


def _turnos_para_matar(
    state: CombatState,
    *,
    dano_agora: float = 0.0,
    dot_por_turno: int = 0,
    dot_duracao: int = 0,
    dano_por_turno: int = 0,
    turnos_do_ritmo: int = 0,
) -> float:
    """Quantos turnos até o alvo cair, contando turno a turno.

    Contagem DETERMINÍSTICA sobre fatos declarados, não simulação: não há
    rolagem, não há crítico sorteado, não há decisão futura. O que ela preserva é
    a TEMPORALIDADE das mecânicas que acontecem ao longo do tempo:

    - **DoT** tica no FIM do turno (`effect_core.tick_effects`). Somá-lo como
      `dano + dot × N` no instante da ação seria dar veneno a uma luta que acaba
      antes do primeiro tique. Aqui o tique só conta se o alvo chegar vivo ao
      fim daquele turno, e o DoT só rende enquanto durar.
    - **buff ofensivo** vale pelos turnos em que ele está no ar
      (`turnos_do_ritmo`), e depois o ritmo volta ao básico.

    O último turno vem FRACIONÁRIO. Arredondar criava um degrau: uma skill que
    bate 40% mais que o básico marcava zero, porque o inteiro só se movia quando
    ela economizava um turno CHEIO — e a mana ficava parada.
    """
    hp = state.alvo_hp - dano_agora
    if hp <= 0:
        return 1.0
    basico = max(1, state.dano_basico)
    reforcado = max(basico, int(dano_por_turno))
    restante_dot = int(dot_duracao)
    restante_ritmo = int(turnos_do_ritmo)
    # O DoT nunca ALONGA a luta, e o ritmo reforçado nunca é menor que o básico:
    # o teto do laço é o pior caso, que é matar só no básico.
    teto = math.ceil(hp / basico) + 2
    turnos = 1.0
    while turnos <= teto:
        if restante_dot > 0 and dot_por_turno > 0:
            hp -= dot_por_turno
            restante_dot -= 1
            if hp <= 0:
                return turnos
        ritmo = reforcado if restante_ritmo > 0 else basico
        restante_ritmo -= 1
        turnos += 1
        if hp <= ritmo:
            return turnos - 1.0 + hp / ritmo
        hp -= ritmo
    return turnos


def _turnos_para_morrer(hp: float, dano_recebido: float) -> float:
    """Turnos de vida, FRACIONÁRIOS e SEM piso.

    O `ceil` de `CombatState.turnos_para_morrer` vive lá para a leitura humana do
    trace. Aqui ele não pode entrar por dois motivos: `duração` é fracionária, e
    misturar quantizações fazia uma cura minúscula que cruzava a fronteira do
    inteiro valer um turno CHEIO — era assim que a poção ganhava do ataque com
    90% de HP. E o piso de 1,0 escondia justamente a posição mais grave, a de
    quem não sobrevive nem ao próximo golpe.
    """
    return max(0.0, hp) / max(1.0, dano_recebido)


def _acoes_inimigas(matar: float, morrer: float, ajo_antes: bool | None) -> int:
    """Quantas vezes o inimigo ainda age nesta luta.

    Iniciativa NÃO vale um turno automático. Agir primeiro só tira uma resposta
    na VIRADA da luta — é a última ação do inimigo que deixa de acontecer.
    Enquanto a luta continua, trocar a ordem não economiza nada: o inimigo age o
    mesmo número de vezes, só que antes ou depois de mim.

    E numa corrida que eu perco, os dois lados saturam no turno em que eu morro:
    quem morre primeiro não colhe a iniciativa.
    """
    return max(0, min(math.ceil(matar) - (1 if ajo_antes else 0), math.ceil(morrer)))


def _escassez_de_mana(state: CombatState, custo: int) -> float:
    if custo <= 0:
        return 0.0
    cargas = state.mp // custo
    horizonte = state.horizonte
    if cargas >= horizonte:
        return 0.0
    return 1.0 - cargas / horizonte


def _chance_de_resolver(m, alvo_hp: int) -> float:
    """A chance de ESTA ação encerrar a luta neste turno.

    `expected_strike_damage` é média sobre o crítico; declarar "mata agora" a
    partir dela é dizer que a média mata. As duas pontas do funil chegam como
    fatos justamente para isto: o golpe sem crítico é a certeza, o golpe com
    crítico é o que só acontece com `crit_chance`.

    Aritmética exata sobre fatos — nenhuma rolagem é simulada.
    """
    if alvo_hp <= 0 or not m.strike_damage_no_crit:
        return 0.0
    if m.strike_damage_no_crit >= alvo_hp:
        return m.hit_chance
    if m.strike_damage_on_crit >= alvo_hp:
        return m.hit_chance * m.crit_chance
    return 0.0


def _ganhos_de_vida(
    opcao: ActionOption, state: CombatState, matar: float, morrer_base: float
) -> list[tuple[str, float]]:
    """Cada fonte de tempo de vida que esta ação produz, com o próprio nome.

    Tudo em TURNOS DE VIDA, a mesma unidade dos dois lados da corrida. Nada aqui
    é fórmula de combate: são os fatos que o adaptador mediu, divididos pelo
    golpe que entra.

    Os efeitos aplicados no alvo entram por `m.statuses`, um por peça, e cada um
    desconta a PRÓPRIA chance. Principal e `secondary` são indistinguíveis aqui
    de propósito: é a mesma peça do jogo, e uma carta que aplica dois efeitos
    soma as duas consequências.
    """
    m = opcao.mechanics
    # O inimigo não age depois de morrer: toda janela é limitada pela luta.
    turnos_da_luta = max(1, math.ceil(matar))
    ganhos: list[tuple[str, float]] = []

    if m.healing:
        cura_util = min(m.healing, state.hp_max - state.hp)
        ganhos.append(
            ("cura", _turnos_para_morrer(state.hp + cura_util, state.alvo_dano) - morrer_base)
        )

    if m.aegis_absorbable_damage:
        # A Égide absorve do PRÓXIMO golpe, e só dele: vale como HP extra uma vez.
        escudo = _turnos_para_morrer(state.hp + m.aegis_absorbable_damage, state.alvo_dano)
        ganhos.append(("égide", min(1.0, escudo - morrer_base)))

    def mitigacao(golpe: int, janela: float, certeza: float) -> float:
        """Turnos de vida que um golpe recebido diferente compra — ou cobra."""
        delta = _turnos_para_morrer(state.hp, golpe) - morrer_base
        return max(-janela, min(janela, delta)) * certeza

    # Buff próprio e elixir: consequência CERTA, medida pela sonda do adaptador.
    if m.incoming_damage_after and m.incoming_damage_after != state.alvo_dano:
        # Nos DOIS sentidos: perder a ocultação numa Emboscada faz o golpe dele
        # subir, e isso é custo.
        ganhos.append(
            (
                "mitigação",
                mitigacao(m.incoming_damage_after, min(max(1, m.duration), turnos_da_luta), 1.0),
            )
        )

    if m.acts_before_enemy_after is not None and m.acts_before_enemy_after != m.acts_before_enemy:
        respostas = _acoes_inimigas(matar, morrer_base, m.acts_before_enemy) - _acoes_inimigas(
            matar, morrer_base, m.acts_before_enemy_after
        )
        if respostas:
            ganhos.append(("iniciativa", float(respostas)))

    # Efeitos aplicados NO ALVO — cada um com a própria chance e a própria janela.
    for st in m.statuses:
        if st.already_active or st.chance <= 0:
            continue
        janela = min(max(1, st.duration), turnos_da_luta)
        if st.skips_turn:
            # Turno roubado é turno em que não tomo dano.
            ganhos.append(("controle", st.chance * janela))
        if st.incoming_damage_after and st.incoming_damage_after != state.alvo_dano:
            ganhos.append(("mitigação", mitigacao(st.incoming_damage_after, janela, st.chance)))
        if st.acts_before_enemy_after is not None and st.acts_before_enemy_after != (
            m.acts_before_enemy
        ):
            respostas = _acoes_inimigas(matar, morrer_base, m.acts_before_enemy) - _acoes_inimigas(
                matar, morrer_base, st.acts_before_enemy_after
            )
            if respostas:
                ganhos.append(("iniciativa", respostas * st.chance))
        if st.target_mp_drained and state.alvo_mp_max > 0:
            # Negar recurso vale a FRAÇÃO do recurso negado, aplicada às respostas
            # que o inimigo ainda daria. Precificar pelo custo das skills DELE
            # seria usar propriedade escondida: a ficha do confronto mostra o MP,
            # não o repertório. O modelo é proporcional e conservador de propósito.
            respostas = _acoes_inimigas(matar, morrer_base, m.acts_before_enemy)
            fracao = min(1.0, st.target_mp_drained / state.alvo_mp_max)
            ganhos.append(("recurso negado", fracao * respostas * st.chance))

    if m.forfeited_control_turns:
        # O benefício da interação JÁ está dentro de `expected_strike_damage`.
        # Isto é o preço, e ele já vem em VALOR ESPERADO do adaptador: o gelo só
        # é gasto no crítico que acerta, e o sono só quebra se a ação causar dano.
        ganhos.append(("estado gasto", -min(m.forfeited_control_turns, float(turnos_da_luta))))

    return [(nome, valor) for nome, valor in ganhos if valor]


def avaliar_combate(opcao: ActionOption, state: CombatState) -> Score:
    """A nota de uma ação de combate. Uma necessidade só: resolver esta luta vivo.

    Não há escada de prioridade aqui — atacar, curar, buffar, controlar, usar
    item e fugir atendem a MESMA necessidade e são comparáveis na mesma escala.
    A máquina de `Need` é exclusiva do mapa.

    Duas parcelas, e a separação entre elas é o coração do modelo:

    - **velocidade** (`duração`): acabar a luta antes SEMPRE vale, porque poupa
      recurso e risco. É a linha de base menos o tempo de morte do alvo com esta
      ação.
    - **sobrevivência**: só vale enquanto eu estiver PERDENDO a corrida. Tempo de
      vida além do fim da luta não compra nada — é por isso que curar com 90% de
      HP diante de um inimigo quase morto não pode ganhar do golpe que encerra.

    As duas ficam separadas de propósito: somá-las num "déficit" único cobrava
    duas vezes de toda ação que não causa dano, uma vez na duração e outra no
    déficit, e nenhum buff conseguia pagar o próprio turno.
    """
    m = opcao.mechanics

    if opcao.family == "flee":
        return _avaliar_fuga(opcao, state)

    # Reaplicar o que já está no ar é turno morto — era assim que o combate do
    # Ladino inflava de 11 para 50 turnos. Vale para o buff próprio e para a
    # carta cujos efeitos TODOS já estão no alvo, desde que ela não faça mais
    # nada além de aplicá-los.
    parado = m.already_active or (
        bool(m.statuses)
        and all(st.already_active for st in m.statuses)
        and not m.expected_strike_damage
        and not m.healing
    )
    if parado:
        return Score(
            opcao.action_id,
            Need.PROGREDIR,
            0.0,
            (("já no ar", 0.0),),
            note="o efeito desta ação já está ativo — reaplicar é turno morto",
        )

    nota = ""
    morrer_base = _turnos_para_morrer(state.hp, state.alvo_dano)

    # 1. Velocidade: o que a ação faz com o tamanho do combate.
    #    O DoT de cada efeito aplicado desconta a chance DELE, e o ritmo
    #    reforçado pode vir de um buff meu (certo) ou de um status no alvo que
    #    baixa a defesa dele, como `vulnerable` (provável).
    ativos = [st for st in m.statuses if not st.already_active and st.chance > 0]
    dot_por_turno = sum(int(st.dot_damage_per_turn * st.chance) for st in ativos)
    dot_duracao = max((st.dot_duration for st in ativos if st.dot_damage_per_turn), default=0)

    reforco, turnos_do_reforco = 0, 0
    if m.outgoing_damage_after:
        reforco, turnos_do_reforco = m.outgoing_damage_after, max(1, m.duration)
    else:
        for st in ativos:
            if st.outgoing_damage_after > reforco:
                # A esperança do golpe reforçado: com chance `p`, o ritmo médio
                # fica entre o básico e o reforçado.
                reforco = int(
                    state.dano_basico + (st.outgoing_damage_after - state.dano_basico) * st.chance
                )
                turnos_do_reforco = max(1, st.duration)

    esperado = m.expected_strike_damage * m.hit_chance
    matar = _turnos_para_matar(
        state,
        dano_agora=esperado,
        dot_por_turno=dot_por_turno,
        dot_duracao=dot_duracao,
        dano_por_turno=reforco,
        turnos_do_ritmo=turnos_do_reforco,
    )
    componentes: list[tuple[str, float]] = [("duração", _linha_de_base(state) - matar)]

    p_resolve = _chance_de_resolver(m, state.alvo_hp)
    if p_resolve >= 1.0:
        nota = "mata agora"
    elif p_resolve > 0:
        nota = f"resolve neste turno com {p_resolve:.0%}"

    # 2. Sobrevivência, e só a parte dela que muda o resultado da corrida.
    #    `escala` é a fração do ganho bruto que cai ABAIXO da linha de empate:
    #    ganhar fôlego que eu já tinha não vale nada, e é isso que impede a poção
    #    de vencer o golpe letal. Cada fonte mantém o próprio nome no trace,
    #    proporcional ao que de fato contou.
    if m.healing:
        cura_util = min(m.healing, state.hp_max - state.hp)
        if cura_util < m.healing:
            nota = nota or f"cura {m.healing} com só {cura_util} aproveitável"

    ganhos = _ganhos_de_vida(opcao, state, matar, morrer_base)
    bruto = sum(valor for _n, valor in ganhos)
    if bruto:
        util = min(morrer_base + bruto - matar, 0.0) - min(morrer_base - matar, 0.0)
        escala = util / bruto
        componentes.extend((nome, valor * escala) for nome, valor in ganhos)
        if util == 0.0:
            nota = nota or "já sobrevivo a esta luta — fôlego a mais não muda nada"

    # 3. Recurso: mana, recarga e estoque, os três como custo de OPORTUNIDADE —
    #    limitados pelo próprio ganho da ação, então nunca deixam uma ação boa
    #    pior que o ataque básico só por ela custar algo.
    ganho_bruto = max(0.0, sum(valor for _n, valor in componentes))
    horizonte = state.horizonte
    if m.mana_cost:
        componentes.append(("recurso", -ganho_bruto * _escassez_de_mana(state, m.mana_cost)))
    if m.cooldown and horizonte > 1:
        # Uma skill forte com recarga alta pode ser excelente AGORA. O que a
        # policy precisa entender é só que não poderá repeti-la em seguida.
        componentes.append(("recarga", -ganho_bruto * min(m.cooldown, horizonte - 1) / horizonte))
    if m.uses_left:
        # Escassez é custo de oportunidade, nunca proibição: o último frasco
        # perde no máximo metade do valor, e o desconto some conforme o estoque
        # cresce. "É o último, nunca use" é comportamento de colecionador — se
        # gastá-lo evita morrer, gastar é racional.
        componentes.append(("escassez", -ganho_bruto / (m.uses_left + 1)))

    if morrer_base < matar:
        nota = nota or "não mato antes de morrer"

    utility = sum(valor for _nome, valor in componentes)
    return Score(
        opcao.action_id,
        Need.PROGREDIR,
        utility,
        tuple(componentes),
        # O ataque básico é a LINHA DE BASE: as duas parcelas dele são zero por
        # definição, porque é contra ele que as outras são medidas. Quando nada
        # melhora a posição, é ele que deve vencer — e isso precisa estar escrito,
        # não sair por acidente da ordem alfabética dos `action_id`. O desempate
        # não é somado à utilidade: só ordena empates.
        tiebreak=1.0 if opcao.family == "attack" else 0.0,
        note=nota,
    )


def _avaliar_fuga(opcao: ActionOption, state: CombatState) -> Score:
    """Fugir é candidata, não porteira.

    Ela disputa com buff, controle, cura e item dentro do mesmo sistema. Antes
    uma camada decidia `flee` ANTES de a política tática ser consultada, e as
    alternativas nunca chegavam a ser comparadas.

    MONOTONICIDADE: o que a fuga evita é o DÉFICIT da corrida, e o déficit cresce
    quando a posição piora. A versão anterior media "o que a fuga preserva" pelos
    turnos de vida restantes, e por isso a fuga valia MENOS quanto mais perto da
    morte: +0,50 morrendo em ~3, −0,50 morrendo em ~1. Agora aumentar o perigo
    nunca torna insistir artificialmente mais atraente.
    """
    p = max(0.01, min(1.0, opcao.mechanics.flee_chance))
    margem = _turnos_para_morrer(state.hp, state.alvo_dano) - _linha_de_base(state)
    deficit = max(0.0, -margem)
    componentes = [
        # Só banco o déficit se a fuga der certo.
        ("déficit evitado", deficit * p),
        # Cada tentativa falha é um turno tomando dano. Com chance p, o número
        # esperado de turnos perdidos é 1/p - 1. É a regra do jogo, não um peso.
        ("custo da falha", -(1.0 / p - 1.0)),
    ]
    if deficit <= 0:
        componentes.append(("recompensa perdida", -PESO_DA_RECOMPENSA_PERDIDA))
    utility = sum(valor for _nome, valor in componentes)
    nota = "perco a corrida de dano" if deficit > 0 else "ainda estou ganhando a corrida"
    return Score(opcao.action_id, Need.PROGREDIR, utility, tuple(componentes), note=nota)


# --- mapa -----------------------------------------------------------------


def avaliar_mapa(opcao: ActionOption, mapa: MapState, prog: ProgressionState) -> Score:
    """A nota de uma ação de mapa: necessidade + utilidade local.

    Ouro, sobrevivência, extração e turnos não são conversíveis, então a
    comparação acontece DENTRO de uma necessidade. A `need` sai do estado, não de
    um rótulo fixo: a Loja atende RECUPERAR com o HP baixo e INVESTIR sem ele.
    """
    familia = opcao.family
    if familia == "lutar":
        return _avaliar_luta(opcao, prog)
    if familia == "pocao":
        return _avaliar_pocao(opcao, prog)
    if familia == "extrair":
        return _avaliar_extracao(opcao, mapa, prog)
    if familia == "saida":
        return _avaliar_saida(opcao, mapa, prog)
    if familia == "evento":
        return _avaliar_evento(opcao, mapa, prog)
    return _avaliar_servico(opcao, mapa, prog)


def _avaliar_luta(opcao: ActionOption, prog: ProgressionState) -> Score:
    """Lutar é o objetivo do andar, e ouro NÃO entra nesta conta.

    Ter a taxa da saída paga era o que desligava a principal fonte de combate do
    bot. Aqui o que pesa é a capacidade de absorver uma luta cuja dificuldade o
    mapa não revela — e a única coisa que o jogador sabe antes de encostar é o
    próprio estado.
    """
    alvo = opcao.target
    if alvo is None:
        return Score(opcao.action_id, Need.PROGREDIR, 0.0, note="alvo sem rota")
    # A capacidade é medida CONTRA o ponto de aposta, não em absoluto. Com
    # `hp_frac` puro a nota nunca ficava negativa, e o bot aceitava a próxima
    # luta com 16% de vida — o mesmo defeito do gate antigo, pelo avesso.
    #
    # As lutas que esta escolha obriga: a do alvo, as do caminho, e mais uma se o
    # mapa marcou `B` — a única pista de perigo que ele dá.
    #
    # A margem é DIVIDIDA entre elas, não subtraída. Subtrair misturava unidades
    # com uma taxa de câmbio inventada (uma luta valia uma barra de vida
    # inteira), e o efeito era um veto silencioso: a margem vale no máximo
    # `1 - HP_DE_APOSTA = 0,65`, então QUALQUER alvo com um encontro no caminho
    # ficava negativo e nunca era escolhido — e o chefe, que já vinha com 0,0
    # fixo, era intocável mesmo com a barra cheia.
    #
    # Dividir mantém tudo numa unidade só, preserva a ordem (menos encontros é
    # melhor), não inventa constante, e devolve o veto para onde ele pertence: o
    # ponto de aposta, que é o único limiar de HP do cérebro.
    lutas = 1 + alvo.extras + (1 if alvo.chefe else 0)
    componentes = [("capacidade por luta", (prog.hp_frac - HP_DE_APOSTA) / lutas)]
    return Score(
        opcao.action_id,
        Need.PROGREDIR,
        sum(v for _n, v in componentes),
        tuple(componentes),
        # Passos desempatam sem serem somados: passo não tem custo mecânico no
        # jogo, e converter passo em vida seria a constante inventada.
        tiebreak=-float(alvo.passos),
        note=f"{lutas} luta(s) até resolver este alvo" if lutas > 1 else "",
    )


def _necessidade_de_cura(prog: ProgressionState) -> Need:
    """Curar é SOBREVIVER quando a falta de vida é o que barra progredir.

    Com a vida no fim, restaurar é a melhor jogada de sobrevivência que existe:
    é instantânea, não custa passo e não abandona o andar. Precisa estar acima de
    "ir buscar o descanso na saída", ou o bot troca uma poção na mochila por um
    andar inteiro.

    Acima do ponto de aposta, curar é INVESTIR: disputa com Ferreiro e compras,
    e perde para lutar. Sem esta distinção, qualquer arranhão tornava a cura mais
    urgente que o andar — o defeito antigo pelo avesso, porque `RECUPERAR`
    vence `PROGREDIR` por construção.

    O ponto de aposta é o MESMO das outras duas leituras: é o único limiar de HP
    do cérebro, e as três decisões giram em torno dele.
    """
    return Need.SOBREVIVER if prog.hp_frac < HP_DE_APOSTA else Need.INVESTIR


def _avaliar_pocao(opcao: ActionOption, prog: ProgressionState) -> Score:
    """Beber é de graça em passos e em ouro. Poção parada não cura ninguém."""
    util = min(opcao.mechanics.healing, prog.hp_max - prog.hp)
    componentes = [("HP recuperável", util / max(1, prog.hp_max))]
    nota = ""
    if util < opcao.mechanics.healing:
        nota = f"cura {opcao.mechanics.healing} com só {util} aproveitável"
    return Score(
        opcao.action_id,
        _necessidade_de_cura(prog),
        sum(v for _n, v in componentes),
        tuple(componentes),
        note=nota,
    )


def _avaliar_servico(opcao: ActionOption, mapa: MapState, prog: ProgressionState) -> Score:
    """Loja e Ferreiro. São as ÚNICAS casas de serviço do jogo.

    `FEATURE_CHARS` tem três entradas — `$`, `F` e `E` —, e a Extração tem
    avaliador próprio. Fonte, Altar e Mercador NÃO são serviços: são os três
    desfechos do EVENTO, que o mapa desenha como `?`. Eles tinham ramo aqui, e
    esse ramo só era alcançável porque o tipo do evento vazava para o cérebro
    antes de o jogador pisar na casa.

    O custo de ir até o serviço são as LUTAS do desvio, não os passos: andar não
    tem custo mecânico no jogo, e passo segue sendo desempate.
    """
    servico = mapa.servico(opcao.family)
    desvio = servico.desvio if servico else 0
    lutas = servico.lutas_no_desvio if servico else 0
    falta = (prog.hp_max - prog.hp) / max(1, prog.hp_max)
    # Mesma correção de unidade da luta: o que o serviço vale é DIVIDIDO pelos
    # encontros que o desvio obriga, e não subtraído deles. Subtrair equivalia a
    # dizer que um combate custa uma barra de ouro inteira.
    por_encontro = 1 + lutas

    if opcao.family == "shop":
        if falta > 0 and prog.ouro > prog.taxa_de_saida:
            componentes = [
                ("HP a recuperar", falta),
                # A reserva da saída é o que mantém a run sustentável.
                (
                    "folga de ouro",
                    min(1.0, (prog.ouro - prog.taxa_de_saida) / max(1, prog.taxa_de_saida)),
                ),
            ]
            return Score(
                opcao.action_id,
                _necessidade_de_cura(prog),
                sum(v for _n, v in componentes) / por_encontro,
                tuple(componentes),
                tiebreak=-float(desvio),
            )
        componentes = [
            (
                "folga de ouro",
                max(0.0, (prog.ouro - prog.taxa_de_saida) / max(1, prog.taxa_de_saida)),
            ),
            ("falta de cura", 1.0 if prog.pocoes_de_cura == 0 else 0.0),
        ]
        return Score(
            opcao.action_id,
            Need.INVESTIR,
            sum(v for _n, v in componentes) / por_encontro,
            tuple(componentes),
            tiebreak=-float(desvio),
        )

    # Ferreiro. A elegibilidade é FATO, pelas funções canônicas do jogo: sem peça
    # que ele possa aprimorar ou engastar, visitar não rende nada. "Tem peça
    # equipada" era proxy, e dava valor a quem já estava no teto.
    if not prog.pecas_para_o_ferreiro:
        # FATO, não limiar: `forge.enhanceable` e `forge.socketable` dizem que não
        # há o que aprimorar nem onde engastar. A visita não faz nada, e folga de
        # ouro não compra o que não existe — somá-la aqui dava valor a ir a um
        # lugar que não tem serviço a prestar.
        return Score(
            opcao.action_id,
            Need.INVESTIR,
            0.0,
            (("peça para investir", 0.0),),
            tiebreak=-float(desvio),
            note="nenhuma peça que o Ferreiro possa aprimorar ou engastar",
        )
    componentes = [
        ("folga de ouro", max(0.0, (prog.ouro - prog.taxa_de_saida) / max(1, prog.taxa_de_saida))),
        ("peça para investir", 1.0),
    ]
    return Score(
        opcao.action_id,
        Need.INVESTIR,
        sum(v for _n, v in componentes) / por_encontro,
        tuple(componentes),
        tiebreak=-float(desvio),
    )


def _avaliar_evento(opcao: ActionOption, mapa: MapState, prog: ProgressionState) -> Score:
    """O `?`. O jogador sabe que existe; NÃO sabe qual dos três desfechos é.

    O tipo só é revelado por `move_player`, que ao revelar já consumiu a casa.
    Então o que se avalia aqui é uma LOTERIA, com as consequências públicas de
    cada desfecho e a probabilidade real de cada um.

    NÃO se soma cura, HP perdido e ouro numa média só. Normalizar os três para
    caberem numa conta seria inventar uma moeda comum que o jogo não tem: HP e
    ouro não se convertem. Entram só as parcelas que já estão na MESMA unidade —
    fração da barra de vida —, cada uma com a chance real do sorteio.

    O MERCADOR fica fora da soma de propósito: uma oferta que ninguém viu não tem
    valor declarável, e transformá-la em HP seria exatamente a moeda artificial.
    A conta fica conservadora, e é melhor assim — subestimar um desfecho neutro é
    barato; inventar uma taxa de câmbio contamina toda decisão que a usar.

    Nunca SOBREVIVER: com a vida no fim, ir ao `?` é apostar que não é o Altar.
    """
    evento = mapa.evento
    if evento is None:
        return Score(opcao.action_id, Need.INVESTIR, 0.0, note="sem evento no andar")

    chance = 1.0 / max(1, evento.desfechos)
    falta = (prog.hp_max - prog.hp) / max(1, prog.hp_max)
    # Perder a run não é perder 30% da barra. A moeda desta conta é FRAÇÃO DA
    # BARRA, e nela não existe custo maior que a barra inteira — então morrer
    # custa 1,0, que é o teto da unidade e não um peso escolhido a dedo. Usar
    # `hp_frac` aqui seria pior que errado: com pouca vida, morrer sairia MAIS
    # BARATO que pagar os 30%.
    custo = 1.0 if evento.altar_mataria else evento.custo_do_altar
    componentes = [
        ("chance de cura", chance * min(falta, evento.cura_da_fonte)),
        ("risco do altar", -chance * custo),
    ]
    nota = "o `?` pode ser o Altar, e ele me mataria" if evento.altar_mataria else ""
    return Score(
        opcao.action_id,
        Need.INVESTIR,
        # Mesma divisão por encontro das outras casas do andar.
        sum(v for _n, v in componentes) / (1 + evento.lutas_no_desvio),
        tuple(componentes),
        tiebreak=-float(evento.desvio),
        note=nota,
    )


def _runway_em_andares(mapa: MapState, prog: ProgressionState) -> float | None:
    """Quantos ANDARES ADICIONAIS a run ainda sustenta.

    NÃO é probabilidade de ruína, e não é valor esperado. É capacidade restante
    estimada, em andares — a unidade do progresso. Tudo vem da própria run:

        custo de uma luta    dano REAL recebido / encontros medidos
        HP útil              vida agora + cura que já está na mão
        lutas que absorvo    HP útil / custo de uma luta
        runway               lutas que absorvo / lutas por andar observadas

    ANTES isto era dividido por `mapa.andar`, e a razão respondia "quanto isso
    representa em relação a tudo que já percorri". Medido em 900 runs, essa
    escala comprimia o eixo até ele não decidir nada: 461 de 461 oportunidades
    caíam em CURTO, nenhuma em SAUDÁVEL, nenhuma em ESGOTADO. Pior, o valor CAÍA
    com a profundidade justamente enquanto a capacidade ABSOLUTA crescia — 0,314
    no andar 3 (≈0,94 andar restante) contra 0,085 no andar 20 (≈1,70 andar
    restante). O divisor media a pergunta errada para esta decisão.

    Sem ele, o número é comparável entre profundidades: dois heróis com o mesmo
    estado mecânico restante leem o mesmo runway, estejam no andar 4 ou no 18.

    A rota até o `E` é descontada em LUTAS, na mesma unidade: quem precisa
    atravessar dois encontros para alcançar o portal tem dois encontros a menos
    de fôlego para o resto da run.

    Devolve `None` quando NÃO HÁ EVIDÊNCIA — sem encontro medido ou sem andar
    concluído, não existe custo observado, e inventar uma média global seria
    trocar medição por chute. Quem trata esse caso é `_avaliar_extracao`, com
    regra separada e declarada.
    """
    if prog.combates_observados < 1 or prog.andares_concluidos < 1:
        return None
    if prog.dano_por_luta <= 0 or prog.lutas_por_andar <= 0:
        return None

    hp_util = prog.hp_frac + prog.cura_garantida
    lutas = hp_util / prog.dano_por_luta - mapa.lutas_ate_extracao
    if lutas <= 0:
        # Nem o portal é alcançável com o fôlego que resta.
        return 0.0
    return lutas / prog.lutas_por_andar


def _banda_da_build(poder_relativo: float) -> str:
    """Onde a build está em relação ao alvo da Arena, em quatro marcos.

    Os cortes são os MESMOS de `sim.arena.classificar` — `ARENA_EQUIVALENCE_BAND`
    para 0,95 e 1,05, com `>` no topo, para que exatamente 1,05 continue sendo
    "alvo atingido" e não "limite de ganância". O 1,00 no meio não é limiar novo:
    é o ponto de igualdade da razão, onde a build empata com o alvo.

    O cérebro tem QUATRO bandas onde a régua tem três, porque aqui elas
    descrevem comportamento e lá descrevem equivalência. O mapeamento é fechado —
    `ABAIXO→ABAIXO`, `{CLOSE_ENOUGH, META_BATIDA}→EQUIVALENTE`,
    `HARD_STOP→SUPEROU` — e um teste de paridade o verifica numa grade que inclui
    as fronteiras. Existem duas implementações porque o cérebro não pode importar
    `sim.arena`: ela importa `content` e `mechanics`, e este pacote é fechado
    para os dois. A constante única é o que impede a divergência.
    """
    if poder_relativo < 1 - ARENA_EQUIVALENCE_BAND:
        return ABAIXO
    if poder_relativo < 1.0:
        return CLOSE_ENOUGH
    if poder_relativo > 1 + ARENA_EQUIVALENCE_BAND:
        return HARD_STOP
    return META_BATIDA


def _estado_do_runway(runway: float) -> str:
    """Os pontos são os naturais da própria razão, não limiares escolhidos.

    `runway = 1` é o empate: aguento mais um tanto igual ao que já atravessei.
    `runway = 0` é o fim: depois do custo da rota até o portal não sobra
    capacidade para outra luta.
    """
    if runway > 1:
        return SAUDAVEL
    if runway > 0:
        return CURTO
    return ESGOTADO


# A matriz. Ela é a autoridade da decisão, e é DISCRETA de propósito: `runway` e
# `poder_relativo` medem coisas diferentes — andares que ainda sustento e
# qualidade da build — e somá-las exigiria um câmbio inventado. Ler a tabela é a
# conversão.
#
#                       SAUDÁVEL   CURTO      ESGOTADO
#   ABAIXO              continua   continua   PRESERVA
#   CLOSE_ENOUGH        continua   PRESERVA   PRESERVA
#   META_BATIDA         continua   PRESERVA   PRESERVA
#   HARD_STOP           PRESERVA   PRESERVA   PRESERVA
#
# CLOSE_ENOUGH e META_BATIDA têm a MESMA linha, e isso é decisão tomada, não
# duplicação a simplificar: com três estados de runway, quatro bandas não
# produzem quatro linhas distintas sem inventar comportamento para diferenciá-las.
# As duas seguem separadas no trace e na telemetria — uma é "abaixo do alvo mas
# aceitável", a outra é "alvo atingido" — e divergirão sozinhas no dia em que
# houver um quarto estado de fôlego ou outro eixo de decisão. Fundi-las aqui
# apagaria a distinção semântica para economizar duas linhas de tabela.
_MATRIZ = {
    (ABAIXO, SAUDAVEL): False,
    (ABAIXO, CURTO): False,
    (ABAIXO, ESGOTADO): True,
    (CLOSE_ENOUGH, SAUDAVEL): False,
    (CLOSE_ENOUGH, CURTO): True,
    (CLOSE_ENOUGH, ESGOTADO): True,
    (META_BATIDA, SAUDAVEL): False,
    (META_BATIDA, CURTO): True,
    (META_BATIDA, ESGOTADO): True,
    (HARD_STOP, SAUDAVEL): True,
    (HARD_STOP, CURTO): True,
    (HARD_STOP, ESGOTADO): True,
}


def _avaliar_extracao(opcao: ActionOption, mapa: MapState, prog: ProgressionState) -> Score:
    """Preservar o personagem inteiro, ou seguir construindo.

    Morrer apaga tudo (`delete_save`); extrair grava tudo e encerra a run. Duas
    coisas decidem, e elas NÃO se somam:

        poder_relativo   qualidade PERMANENTE da build, contra o alvo da Arena
        runway           fôlego RESTANTE da run

    Uma diz se o gladiador já está pronto; a outra, se ainda há estrada. São
    grandezas diferentes, e `a·runway + b·poder` precisaria de um câmbio que
    ninguém mediu. Por isso a decisão é uma MATRIZ discreta, resolvida num
    booleano — e é a `Need` que carrega o resultado, que é para isso que a
    escada de necessidades existe.

    Quando preserva, a ação atende `PRESERVAR`: acima de recuperar e progredir,
    abaixo de não morrer agora. Quando não preserva, ela continua enumerada,
    avaliada e no trace, com utility 0,0 — `escolher` só deixa vencer quem tem
    utility positiva, e a saída do andar tem piso positivo, então nunca falta
    candidata.

    Decidida UMA vez: quem alcança a casa executa a decisão que veio, e não
    reavalia. Era esse o loop EXTRAIR -> anda -> NÃO EXTRAIR.
    """
    runway = _runway_em_andares(mapa, prog)
    poder = prog.poder_relativo

    if poder <= 0:
        # AUSÊNCIA DE MEDIÇÃO, e não "build fraca". Sem banda a matriz não se
        # aplica, e tratar isto como ABAIXO seria decidir o destino da run com um
        # número que ninguém mediu. Não deveria acontecer numa oportunidade real:
        # o adaptador mede quando há chave, casa alcançável e extração habilitada.
        return Score(
            opcao.action_id,
            Need.ENCERRAR,
            0.0,
            (("poder não medido", 0.0),),
            note="poder relativo não foi medido: sem banda de build, a matriz não decide",
        )

    banda = _banda_da_build(poder)

    if runway is None:
        # EVIDÊNCIA INSUFICIENTE de runway: sem luta medida ou sem andar
        # concluído não há custo observado, e uma média inventada decidiria a run
        # com um número que ninguém mediu. Só quem já superou o alvo preserva
        # assim mesmo — para esse, continuar não constrói mais nada.
        preserva = banda == HARD_STOP
        nota = f"{banda} ({poder:.2f}), runway sem evidência: nenhuma luta medida ainda — " + (
            "alvo da Arena superado, preservar." if preserva else "seguir construindo."
        )
        return _score_da_extracao(opcao, preserva, nota)

    estado = _estado_do_runway(runway)
    preserva = _MATRIZ[(banda, estado)]
    nota = (
        f"{banda} ({poder:.2f}), runway {runway:.2f} andar(es) ({estado.lower()}); "
        f"{mapa.lutas_ate_extracao} luta(s) até o portal — "
        + ("preservar a build." if preserva else "a run ainda constrói: continuar.")
    )
    return _score_da_extracao(opcao, preserva, nota)


def _score_da_extracao(opcao: ActionOption, preserva: bool, nota: str) -> Score:
    """O veredito da matriz, traduzido para a escada de necessidades.

    A utility quando preserva é 1,0 e poderia ser qualquer positivo: `PRESERVAR`
    não tem outra ação disputando o tier, então o número não é comparado com
    nada. É a `Need` que decide, e a matriz que decide a `Need`.
    """
    if preserva:
        return Score(opcao.action_id, Need.PRESERVAR, 1.0, (("preservar a build", 1.0),), note=nota)
    return Score(opcao.action_id, Need.ENCERRAR, 0.0, (("preservar a build", 0.0),), note=nota)


def _avaliar_saida(opcao: ActionOption, mapa: MapState, prog: ProgressionState) -> Score:
    """Encerrar o andar. A última necessidade, e por isso sempre disponível.

    Com o HP abaixo do ponto de aposta ela sobe para SOBREVIVER: o descanso de
    fim de andar é a única cura garantida do jogo, e buscá-lo deixa de ser
    encerrar o andar e passa a ser não morrer nele.
    """
    if prog.hp_frac < HP_DE_APOSTA:
        valor = HP_DE_APOSTA - prog.hp_frac
        return Score(
            opcao.action_id,
            # RECUPERAR, e não SOBREVIVER: ir buscar o descanso do fim do andar
            # é a resposta de quem NÃO tem como restaurar aqui. Quem tem poção,
            # fonte ou loja pagável resolve sem abandonar o andar, e essas
            # atendem SOBREVIVER.
            Need.RECUPERAR,
            valor,
            (("HP abaixo do ponto de aposta", valor),),
            note=f"HP em {prog.hp_frac:.0%}; o descanso do fim do andar é a cura",
        )
    componentes = [("andar sem mais alvo", 1.0 if not mapa.alvos else 0.0)]
    if prog.ouro < prog.taxa_de_saida:
        # O preço REAL de sair sem pagar, não um número inventado. `use_exit` não
        # cobra nada quando falta ouro — não existe pagamento parcial nem recusa
        # voluntária —, e a punição aparece no multiplicador de Essência do andar
        # seguinte, já com o piso de `essence_after_penalty`. O adaptador entrega
        # essa perda medida; o `-0,5` que estava aqui não representava nada.
        componentes.append(("Essência que a saída não paga custa", -prog.perda_de_essencia))
    return Score(
        opcao.action_id,
        Need.ENCERRAR,
        # Piso positivo: o andar sempre tem saída, e ela é o que sobra quando
        # nada mais rende. Sem isso a escolha poderia ficar sem candidata.
        max(0.01, sum(v for _n, v in componentes)),
        tuple(componentes),
    )
