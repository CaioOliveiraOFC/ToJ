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

from src.sim.bot.decision import ActionOption, Need, Score
from src.sim.bot.observation import CombatState, MapState, ProgressionState

# Abaixo disto continuar é aposta, e sair passa a valer algo. É o ÚNICO limiar
# de HP do cérebro, e ele não é um portão: nenhuma ação é barrada por ele. Ele
# faz a utilidade da retirada ficar positiva, e a retirada ganha por ser de
# necessidade mais urgente — não por impedir as outras de serem avaliadas.
HP_DE_APOSTA = 0.35

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
    """
    m = opcao.mechanics
    # Consequência de STATUS é probabilística; consequência de buff próprio e de
    # item é certa. O adaptador já entrega a chance efetiva, com resistência
    # descontada.
    certeza = m.status_chance if opcao.family == "status" else 1.0
    # O inimigo não age depois de morrer: toda janela é limitada pela luta.
    turnos_da_luta = max(1, math.ceil(matar))
    janela = min(max(1, m.duration), turnos_da_luta)
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

    if m.incoming_damage_after and m.incoming_damage_after != state.alvo_dano:
        # O adaptador já disse qual fica o golpe dele — nos DOIS sentidos. Perder
        # a ocultação numa Emboscada faz o golpe dele subir, e isso é custo.
        delta = _turnos_para_morrer(state.hp, m.incoming_damage_after) - morrer_base
        ganhos.append(("mitigação", max(-janela, min(janela, delta)) * certeza))

    if m.status_skips_turn and m.status_chance > 0:
        # Turno roubado é turno em que não tomo dano.
        ganhos.append(("controle", m.status_chance * janela))

    if m.acts_before_enemy_after is not None and m.acts_before_enemy_after != m.acts_before_enemy:
        respostas = _acoes_inimigas(matar, morrer_base, m.acts_before_enemy) - _acoes_inimigas(
            matar, morrer_base, m.acts_before_enemy_after
        )
        if respostas:
            ganhos.append(("iniciativa", respostas * certeza))

    if m.target_mp_drained and state.alvo_mp_max > 0:
        # Negar recurso vale a FRAÇÃO do recurso negado, aplicada às respostas que
        # o inimigo ainda daria. Precificar pelo custo das skills DELE seria usar
        # propriedade escondida: a ficha do confronto mostra o MP, não o
        # repertório. O modelo é proporcional e deliberadamente conservador.
        respostas = _acoes_inimigas(matar, morrer_base, m.acts_before_enemy)
        fracao = min(1.0, m.target_mp_drained / state.alvo_mp_max)
        ganhos.append(("recurso negado", fracao * respostas * certeza))

    if m.forfeited_control_turns:
        # O benefício da interação JÁ está dentro de `expected_strike_damage`.
        # Isto é o preço: o gelo que a Quebra Gélida gasta e o sono que o dano
        # acorda eram turnos em que o inimigo não agia.
        ganhos.append(("estado gasto", -float(min(m.forfeited_control_turns, turnos_da_luta))))

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

    if m.already_active:
        return Score(
            opcao.action_id,
            Need.PROGREDIR,
            0.0,
            (("já no ar", 0.0),),
            note="o efeito desta ação já está ativo — reaplicar é turno morto",
        )

    nota = ""
    certeza = m.status_chance if opcao.family == "status" else 1.0
    morrer_base = _turnos_para_morrer(state.hp, state.alvo_dano)

    # 1. Velocidade: o que a ação faz com o tamanho do combate.
    esperado = m.expected_strike_damage * m.hit_chance
    matar = _turnos_para_matar(
        state,
        dano_agora=esperado,
        dot_por_turno=int(m.dot_damage_per_turn * certeza),
        dot_duracao=m.dot_duration,
        dano_por_turno=int(m.outgoing_damage_after * certeza) if m.outgoing_damage_after else 0,
        turnos_do_ritmo=max(1, m.duration) if m.outgoing_damage_after else 0,
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
        return _avaliar_extracao(opcao, prog)
    if familia == "saida":
        return _avaliar_saida(opcao, mapa, prog)
    return _avaliar_servico(opcao, mapa, prog)


def _avaliar_luta(opcao: ActionOption, prog: ProgressionState) -> Score:
    """Lutar é o objetivo do andar, e ouro NÃO entra nesta conta.

    Ter a taxa da saída paga era o que desligava a principal fonte de combate do
    bot. Aqui o que pesa é a capacidade de absorver uma luta cuja dificuldade o
    mapa não revela — e a única coisa que o jogador sabe antes de encostar é o
    próprio estado.
    """
    alvo = opcao.target
    if alvo is None or alvo.chefe:
        return Score(
            opcao.action_id,
            Need.PROGREDIR,
            0.0,
            note="chefe: o mapa marca `B`, e é a única pista de perigo que ele dá",
        )
    # A capacidade é medida CONTRA o ponto de aposta, não em absoluto. Com
    # `hp_frac` puro a nota nunca ficava negativa, e o bot aceitava a próxima
    # luta com 16% de vida — o mesmo defeito do gate antigo, pelo avesso.
    componentes = [
        ("capacidade", prog.hp_frac - HP_DE_APOSTA),
        ("lutas no caminho", -float(alvo.extras)),
    ]
    return Score(
        opcao.action_id,
        Need.PROGREDIR,
        sum(v for _n, v in componentes),
        tuple(componentes),
        # Passos desempatam sem serem somados: passo e luta têm unidades
        # diferentes, e converter uma na outra seria a constante inventada.
        tiebreak=-float(alvo.passos),
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
    """Loja, Fonte, Altar, Ferreiro e Mercador.

    A Fonte cura de graça; a Loja cura pagando. As duas atendem RECUPERAR quando
    há o que curar, e só então. Ferreiro e Mercador atendem INVESTIR.
    """
    servico = mapa.servico(opcao.family)
    desvio = servico.desvio if servico else (mapa.desvio_evento or 0)
    falta = (prog.hp_max - prog.hp) / max(1, prog.hp_max)

    if opcao.family == "fountain":
        return Score(
            opcao.action_id,
            _necessidade_de_cura(prog),
            falta,
            (("HP a recuperar", falta),),
            tiebreak=-float(desvio),
            note="cura de graça",
        )
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
                sum(v for _n, v in componentes),
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
            sum(v for _n, v in componentes),
            tuple(componentes),
            tiebreak=-float(desvio),
        )
    if opcao.family == "altar":
        # Altar cobra vida. Só vale com folga real.
        valor = prog.hp_frac - 0.5
        return Score(
            opcao.action_id,
            Need.INVESTIR,
            valor,
            (("folga de vida", valor),),
            tiebreak=-float(desvio),
        )
    # forge e merchant
    componentes = [
        ("folga de ouro", max(0.0, (prog.ouro - prog.taxa_de_saida) / max(1, prog.taxa_de_saida))),
        ("peça para investir", 1.0 if prog.pecas_equipadas else -1.0),
    ]
    return Score(
        opcao.action_id,
        Need.INVESTIR,
        sum(v for _n, v in componentes),
        tuple(componentes),
        tiebreak=-float(desvio),
    )


def _avaliar_extracao(opcao: ActionOption, prog: ProgressionState) -> Score:
    """Sair vivo com o que foi acumulado.

    Decidida UMA vez: quem alcança a casa executa a decisão que veio, e não
    reavalia. Era esse o loop EXTRAIR -> anda -> NÃO EXTRAIR.
    """
    if not prog.tem_o_que_preservar:
        return Score(
            opcao.action_id,
            Need.SOBREVIVER,
            0.0,
            note="ainda não acumulei nada que valha preservar",
        )
    # O acúmulo NÃO entra na soma: ele é pré-condição, e já foi checada acima.
    # Somá-lo empurrava para a extração por ter progredido bem, e um único sinal
    # de risco passava a bastar.
    componentes = [
        ("sinais de risco", float(len(prog.sinais_de_risco))),
        # Um sinal só não convence; dois começam a convencer.
        ("dúvida", -1.0),
    ]
    resumo = f"{prog.nivel} de nível e {prog.passivas} passivas a preservar; " + (
        ", ".join(prog.sinais_de_risco) or "sem sinal de risco"
    )
    return Score(
        opcao.action_id,
        Need.SOBREVIVER,
        sum(v for _n, v in componentes),
        tuple(componentes),
        note=resumo,
    )


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
        componentes.append(("saída não paga", -0.5))
    return Score(
        opcao.action_id,
        Need.ENCERRAR,
        # Piso positivo: o andar sempre tem saída, e ela é o que sobra quando
        # nada mais rende. Sem isso a escolha poderia ficar sem candidata.
        max(0.01, sum(v for _n, v in componentes)),
        tuple(componentes),
    )
