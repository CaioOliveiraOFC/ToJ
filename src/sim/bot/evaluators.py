"""Quanto cada ação VALE agora. Nenhuma fórmula de combate vive aqui.

O adaptador já respondeu "o que esta ação faz" — dano esperado, chance de
acerto, cura, custo de mana, duração, chance de status, e o golpe de cada lado
DEPOIS da ação. Este módulo só faz aritmética de turnos sobre esses fatos.
Reescrever mitigação, acerto ou crítico aqui criaria um segundo simulador.

## A moeda do combate

Turnos. Toda ação é medida por duas parcelas comparáveis:

- **duração**: quantos turnos ela tira (ou acrescenta) ao combate;
- **sobrevivência**: quantos turnos de vida ela me dá.

Uma ação que não causa dano custa um turno de duração — e isso aparece como
parcela negativa, não como exceção no código. É a mesma conta para atacar,
curar, buffar, controlar e usar item.

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


def _turnos_com(state: CombatState, dano_agora: float) -> float:
    """Turnos até o alvo cair se eu causar `dano_agora` agora e o básico depois.

    FRACIONÁRIO, de propósito. Arredondar para turno inteiro criava um degrau:
    uma skill que bate 40% mais que o básico marcava zero, porque o `ceil` só se
    movia quando ela economizava um turno CHEIO. Resultado: a skill perdia para
    o básico na quase totalidade dos turnos e a mana ficava parada — o Mago
    gastou 40 de 1402 de MP antes desta correção. O fracionário mede a vantagem
    real da ação, sem cliff.
    """
    if dano_agora >= state.alvo_hp:
        return 1.0
    resto = state.alvo_hp - dano_agora
    return 1.0 + resto / max(1, state.dano_basico)


def _escassez_de_mana(state: CombatState, custo: int) -> float:
    if custo <= 0:
        return 0.0
    cargas = state.mp // custo
    horizonte = state.horizonte
    if cargas >= horizonte:
        return 0.0
    return 1.0 - cargas / horizonte


def avaliar_combate(opcao: ActionOption, state: CombatState) -> Score:
    """A nota de uma ação de combate. Uma necessidade só: resolver esta luta vivo.

    Não há escada de prioridade aqui — atacar, curar, buffar, controlar, usar
    item e fugir atendem a MESMA necessidade e são comparáveis na mesma escala.
    A máquina de `Need` é exclusiva do mapa.
    """
    m = opcao.mechanics
    # A linha de base é fracionária pelo mesmo motivo que `_turnos_com`: as duas
    # pontas da subtração têm de estar na mesma escala.
    turnos_base = state.alvo_hp / max(1, state.dano_basico)
    componentes: list[tuple[str, float]] = []
    nota = ""

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

    # 1. Duração: o que a ação faz com o tamanho do combate.
    esperado = m.estimated_damage * m.hit_chance
    duracao = turnos_base - _turnos_com(state, esperado)
    componentes.append(("duração", duracao))
    if esperado >= state.alvo_hp > 0:
        nota = "mata agora"

    # 2. Sobrevivência: turnos de vida que a ação me dá.
    sobrevivencia = 0.0
    if m.healing:
        cura_util = min(m.healing, state.hp_max - state.hp)
        sobrevivencia += state.turnos_para_morrer(state.hp + cura_util) - state.turnos_para_morrer()
        if cura_util < m.healing:
            nota = f"cura {m.healing} com só {cura_util} aproveitável"
    if m.incoming_damage_after and m.incoming_damage_after < state.alvo_dano:
        # O adaptador já disse qual fica o golpe dele. Aritmética, não fórmula.
        depois = math.ceil(state.hp / max(1, m.incoming_damage_after))
        janela = min(max(1, m.duration), state.horizonte)
        sobrevivencia += min(depois - state.turnos_para_morrer(), janela)
    if m.status_skips_turn and m.status_chance > 0:
        # Turno roubado é turno em que não tomo dano.
        sobrevivencia += m.status_chance * min(max(1, m.duration), state.horizonte)
    if sobrevivencia:
        componentes.append(("sobrevivência", sobrevivencia))

    # 3. Recurso: só o que a mana ainda pode virar ação.
    recurso = 0.0
    if m.mana_cost:
        recurso = -max(duracao, 0.0) * _escassez_de_mana(state, m.mana_cost)
        componentes.append(("recurso", recurso))
    if m.mana_restored:
        # Repor mana vale o que ela destrava: sai da escassez para dentro dela.
        componentes.append(("mana reposta", min(1.0, m.mana_restored / max(1, state.mp_max))))

    # 4. A corrida perdida. Se DEPOIS desta ação o alvo ainda cai depois de mim,
    #    insistir gasta a vida que resta sem chegar ao fim — e o que está em jogo
    #    é o personagem, não o turno.
    #
    #    A conta é por AÇÃO, não por luta: uma skill que vira a corrida não é
    #    penalizada, porque a comparação usa o tempo de morte do alvo COM ela.
    #    Sem esta parcela, atacar numa luta perdida marcava zero — e zero ganha
    #    de qualquer fuga, que é sempre negativa pelo custo da tentativa.
    if _turnos_com(state, esperado) > state.turnos_para_morrer():
        perdida = -float(state.turnos_para_morrer())
        componentes.append(("corrida perdida", perdida))
        nota = nota or "não mato antes de morrer"

    utility = sum(valor for _nome, valor in componentes)
    return Score(
        opcao.action_id,
        Need.PROGREDIR,
        utility,
        tuple(componentes),
        # O ataque básico é a LINHA DE BASE: a parcela de duração dele é zero por
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
    """
    p = max(0.01, min(1.0, opcao.mechanics.flee_chance))
    deficit = state.turnos_para_matar() - state.turnos_para_morrer()
    componentes = [
        # Perdendo a corrida, o que a fuga preserva é TODA a vida que resta —
        # não a margem pela qual estou perdendo. Medir pelo déficit dava -0,50
        # a uma fuga de luta perdida por um turno, e o bot ficava na luta que
        # sabia estar perdendo.
        ("preservação", (state.turnos_para_morrer() * p) if deficit > 0 else 0.0),
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
