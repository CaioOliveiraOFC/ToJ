"""A MATRIZ da extração: qualidade da build × fôlego da run.

Duas grandezas que não se somam. `poder_relativo` diz se o gladiador já está
pronto para a Arena; `runway` diz quantos ANDARES ADICIONAIS a run ainda
sustenta. Somá-las pediria um câmbio que ninguém mediu, então a combinação é uma
TABELA:

                      SAUDÁVEL   CURTO      ESGOTADO
    ABAIXO            continua   continua   PRESERVA
    CLOSE_ENOUGH      continua   PRESERVA   PRESERVA
    META_BATIDA       continua   PRESERVA   PRESERVA
    HARD_STOP         PRESERVA   PRESERVA   PRESERVA

`CLOSE_ENOUGH` e `META_BATIDA` têm a mesma linha, e é decisão tomada: com três
estados de runway, quatro bandas não dão quatro linhas distintas sem inventar
comportamento. As duas seguem distintas no trace e na telemetria.

O veredito viaja na `Need`, não na `utility`: `PRESERVAR` quando preserva,
`ENCERRAR` com utility 0,0 quando não. Foi por isso que `PRESERVAR` nasceu —
encaixar um booleano em `SOBREVIVER` ou `RECUPERAR` exigiria uma utility
calibrada contra o teto de OUTRO avaliador, que quebra em silêncio quando ele
mudar.

Estes testes cobrem as nove células, as quatro fronteiras, os dois casos sem
evidência, e as duas travas conceituais de direção — o que poção pode mudar e o
que equipamento pode mudar.
"""

from __future__ import annotations

import pytest

from src.shared.constants import ARENA_EQUIVALENCE_BAND
from src.sim.arena import classificar
from src.sim.bot.decision import ActionOption, Need
from src.sim.bot.evaluators import (
    ABAIXO,
    CLOSE_ENOUGH,
    HARD_STOP,
    META_BATIDA,
    avaliar_mapa,
)
from src.sim.bot.observation import MapState, ProgressionState

EXTRAIR = ActionOption(action_id="extrair", family="extrair", label="extração")

# Um histórico de run que já mediu o suficiente para haver runway.
#
# Com `lutas_por_andar=5` e `dano_por_luta=0,20`, a fórmula vira
# `runway = hp_util / 1,0` — ou seja, `hp_util` É o runway em andares. Isso deixa
# cada célula ser montada por um HP legível, e as fronteiras (0 e 1) caírem em
# pontos exatos em vez de perto deles.
#
# `ANDAR` não entra mais na conta: é justamente a mudança desta rodada. Ele segue
# no `MapState` porque o mapa precisa dele, e os testes o variam para provar que
# NÃO muda nada.
ANDAR = 10
MEDIDO = dict(dano_por_luta=0.20, combates_observados=9, lutas_por_andar=5.0, andares_concluidos=2)
HP_MAX = 1000


def _prog(poder: float, **kwargs) -> ProgressionState:
    base = dict(
        nivel=10,
        hp=450,
        hp_max=HP_MAX,
        mp=90,
        mp_max=100,
        ouro=200,
        taxa_de_saida=50,
        poder_relativo=poder,
    )
    base.update(MEDIDO)
    base.update(kwargs)
    return ProgressionState(**base)


def _mapa(**kwargs) -> MapState:
    base = dict(
        andar=ANDAR, posicao=(1, 1), passos_ate_saida=12, desvio_extracao=2, lutas_ate_extracao=0
    )
    base.update(kwargs)
    return MapState(**base)


def _hp_util_para(runway: float) -> float:
    """O `hp_util` que produz EXATAMENTE este runway, resolvendo a própria fórmula.

    `runway = (hp_util / dano_por_luta - lutas_ate_extracao) / lutas_por_andar`

    Resolver em vez de chutar é o que deixa as fronteiras (runway 0 e 1) serem
    testadas NO ponto, e não perto dele. Note a ausência de `ANDAR`: é a mudança
    desta rodada.
    """
    return runway * MEDIDO["lutas_por_andar"] * MEDIDO["dano_por_luta"]


def _decidir(poder: float, runway_alvo: float, andar: int = ANDAR):
    """Monta o estado que produz este runway e pede a decisão.

    `hp_util = hp_frac + cura_garantida`, e `hp_frac` não passa de 1. Então o que
    excede uma barra entra por `cura_garantida` — que é exatamente como o jogo
    chega a mais de um andar de fôlego: barra cheia MAIS poção na mochila.
    """
    hp_util = _hp_util_para(runway_alvo)
    frac = min(1.0, hp_util)
    cura = max(0.0, hp_util - 1.0)
    prog = _prog(poder, hp=int(round(frac * HP_MAX)), hp_max=HP_MAX, cura_garantida=cura)
    return avaliar_mapa(EXTRAIR, _mapa(andar=andar), prog)


def _preserva(score) -> bool:
    return score.need is Need.PRESERVAR and score.utility > 0


# --- As nove células -------------------------------------------------------


@pytest.mark.parametrize(
    ("poder", "runway", "espera_preservar", "rotulo"),
    [
        (0.80, 1.5, False, "ABAIXO + saudável: ainda constrói"),
        (0.80, 0.5, False, "ABAIXO + curto: aceita risco para melhorar"),
        (0.80, 0.0, True, "ABAIXO + esgotado: salva o que sobrou"),
        (0.97, 1.5, False, "CLOSE_ENOUGH + saudável: aceitável, mas vale melhorar"),
        (0.97, 0.5, True, "CLOSE_ENOUGH + curto: o fôlego apertou"),
        (0.97, 0.0, True, "CLOSE_ENOUGH + esgotado: preservar"),
        (1.02, 1.5, False, "META_BATIDA + saudável: só continua com fôlego saudável"),
        (1.02, 0.5, True, "META_BATIDA + curto: alvo atingido e fôlego curto"),
        (1.02, 0.0, True, "META_BATIDA + esgotado: preservar"),
        (1.10, 1.5, True, "HARD_STOP + saudável: limite de ganância"),
        (1.10, 0.5, True, "HARD_STOP + curto: preservar"),
        (1.10, 0.0, True, "HARD_STOP + esgotado: preservar"),
    ],
)
def test_as_doze_celulas(poder, runway, espera_preservar, rotulo):
    score = _decidir(poder, runway)
    assert _preserva(score) is espera_preservar, f"{rotulo}: {score.note}"


# --- As fronteiras ---------------------------------------------------------


@pytest.mark.parametrize(
    ("poder", "banda"),
    [
        (1 - ARENA_EQUIVALENCE_BAND - 0.001, ABAIXO),
        (1 - ARENA_EQUIVALENCE_BAND, CLOSE_ENOUGH),
        (0.999, CLOSE_ENOUGH),
        (1.0, META_BATIDA),
        (1 + ARENA_EQUIVALENCE_BAND, META_BATIDA),
        (1 + ARENA_EQUIVALENCE_BAND + 0.001, HARD_STOP),
    ],
)
def test_as_fronteiras_dos_quatro_marcos(poder, banda):
    """0,95 abre CLOSE_ENOUGH; 1,00 abre META_BATIDA; 1,05 ainda é META_BATIDA.

    O topo é `>` e não `>=`, igual a `sim.arena.classificar` — trocar isso
    quebraria a paridade entre as duas implementações da banda.
    """
    assert banda in _decidir(poder, 0.5).note


def test_a_fronteira_de_0_95_muda_a_decisao_com_runway_curto():
    """A célula (·, curto) é onde a banda decide: ABAIXO continua, CLOSE_ENOUGH sai."""
    assert not _preserva(_decidir(1 - ARENA_EQUIVALENCE_BAND - 0.001, 0.5))
    assert _preserva(_decidir(1 - ARENA_EQUIVALENCE_BAND, 0.5))


def test_a_fronteira_de_1_05_muda_a_decisao_com_runway_saudavel():
    """A célula (·, saudável) é onde HARD_STOP se separa de META_BATIDA."""
    assert not _preserva(_decidir(1 + ARENA_EQUIVALENCE_BAND, 1.5))
    assert _preserva(_decidir(1 + ARENA_EQUIVALENCE_BAND + 0.001, 1.5))


def test_o_1_00_nao_muda_a_decisao_hoje_mas_muda_a_banda():
    """CLOSE_ENOUGH e META_BATIDA compartilham a linha, e isso é deliberado.

    O que as separa é o NOME no trace e na telemetria, não a consequência: com
    três estados de runway não há como dar quatro linhas distintas a quatro
    bandas sem inventar comportamento. Este teste fixa as duas coisas — a
    igualdade de decisão e a diferença de rótulo — para que nem a fusão nem a
    invenção passem sem alguém decidir.
    """
    for runway in (1.5, 0.5, 0.0):
        assert _preserva(_decidir(0.99, runway)) is _preserva(_decidir(1.01, runway))
    assert CLOSE_ENOUGH in _decidir(0.99, 0.5).note
    assert META_BATIDA in _decidir(1.01, 0.5).note


def _com_estado(poder: float, hp: int, cura: float = 0.0):
    prog = _prog(poder, hp=hp, hp_max=HP_MAX, cura_garantida=cura)
    return avaliar_mapa(EXTRAIR, _mapa(), prog)


def test_runway_exatamente_1_ainda_esta_na_zona_curta():
    """`runway > 1` é SAUDÁVEL, então o empate exato ainda preserva.

    Com estes parâmetros a barra cheia dá runway exatamente 1,00; o primeiro
    ponto acima vem de cura na mochila, que é o caminho real para passar de um
    andar de fôlego.
    """
    assert "runway 1.00 andar(es) (curto)" in _com_estado(1.02, HP_MAX).note
    assert _preserva(_com_estado(1.02, HP_MAX))
    assert not _preserva(_com_estado(1.02, HP_MAX, cura=0.01))


def test_runway_exatamente_0_e_esgotado():
    """`runway > 0` é CURTO; zero é ESGOTADO, e aí até ABAIXO preserva."""
    assert _preserva(_com_estado(0.80, 0))
    assert "esgotado" in _com_estado(0.80, 0).note
    assert not _preserva(_com_estado(0.80, 1))
    assert "curto" in _com_estado(0.80, 1).note


# --- Sem evidência ---------------------------------------------------------


def _sem_runway(poder: float):
    prog = ProgressionState(
        nivel=3,
        hp=450,
        hp_max=HP_MAX,
        mp=90,
        mp_max=100,
        ouro=200,
        taxa_de_saida=50,
        poder_relativo=poder,
        combates_observados=0,
        andares_concluidos=0,
    )
    return avaliar_mapa(EXTRAIR, _mapa(), prog)


@pytest.mark.parametrize(
    ("poder", "espera_preservar"),
    [(0.80, False), (0.97, False), (1.02, False), (1.10, True)],
)
def test_sem_evidencia_de_runway_so_o_hard_stop_preserva(poder, espera_preservar):
    """Sem luta medida não se inventa média. Quem passou do limite não constrói mais."""
    score = _sem_runway(poder)
    assert _preserva(score) is espera_preservar
    assert "sem evidência" in score.note


def test_poder_nao_medido_nao_vira_abaixo():
    """Ausência de medição não é build fraca, e a matriz não se aplica sem banda."""
    prog = _prog(0.0)
    score = avaliar_mapa(EXTRAIR, _mapa(), prog)
    assert not _preserva(score)
    assert score.need is Need.ENCERRAR
    assert "não foi medido" in score.note
    assert ABAIXO not in score.note


# --- A escada de necessidades ----------------------------------------------


def test_preservar_vence_progredir_e_perde_para_sobreviver():
    """A ordem pedida: emergência > preservar > recuperar > progredir."""
    assert Need.SOBREVIVER < Need.PRESERVAR < Need.RECUPERAR < Need.PROGREDIR


def test_quem_nao_preserva_fica_em_encerrar_com_utility_zero():
    """Continua no trace, mas `escolher` só deixa vencer quem tem utility > 0."""
    score = _decidir(0.80, 1.5)
    assert score.need is Need.ENCERRAR
    assert score.utility == 0.0
    assert score.note


def test_as_quatro_bandas_do_cerebro_mapeiam_nas_tres_da_arena():
    """Duas implementações, uma constante. A paridade é o que impede a divergência.

    O cérebro não pode importar `sim.arena` — ela importa `content` e
    `mechanics`, e este pacote é fechado para os dois. Ele tem QUATRO bandas
    porque aqui elas descrevem comportamento; a régua tem três porque lá elas
    descrevem equivalência. O mapeamento é fechado, e é ele que se verifica:

        ABAIXO                        -> ABAIXO
        CLOSE_ENOUGH, META_BATIDA     -> EQUIVALENTE
        HARD_STOP                     -> SUPEROU
    """
    mapeamento = {
        ABAIXO: "ABAIXO",
        CLOSE_ENOUGH: "EQUIVALENTE",
        META_BATIDA: "EQUIVALENTE",
        HARD_STOP: "SUPEROU",
    }
    for centesimos in range(50, 151):
        poder = centesimos / 100
        nota = _decidir(poder, 0.5).note
        minha = next(b for b in mapeamento if b in nota)
        assert mapeamento[minha] == classificar(poder), f"poder {poder}: {nota}"


# --- As travas conceituais: a DIREÇÃO importa ------------------------------


def test_pocao_so_pode_mudar_extrair_para_continuar():
    """Poção é fôlego, não poder — e fôlego move a linha para a ESQUERDA.

    `cura_garantida` entra em `hp_util`, que aumenta `runway`. Runway maior anda
    ESGOTADO → CURTO → SAUDÁVEL, e nessa direção a matriz só troca PRESERVA por
    continua. Poção nunca pode CAUSAR uma extração.
    """
    hp = int(round(_hp_util_para(0.5) * HP_MAX))
    sem = _prog(1.02, hp=hp, hp_max=HP_MAX)
    # A poção entra por `cura_garantida`, que soma em `hp_util` — o suficiente
    # para o runway cruzar 1 e a linha andar de CURTO para SAUDÁVEL.
    com = _prog(1.02, hp=hp, hp_max=HP_MAX, cura_garantida=_hp_util_para(1.2) - hp / HP_MAX)

    assert _preserva(avaliar_mapa(EXTRAIR, _mapa(), sem))
    assert not _preserva(avaliar_mapa(EXTRAIR, _mapa(), com))


def test_equipamento_so_pode_mudar_continuar_para_extrair():
    """Equipamento é poder, não fôlego — e poder sobe a COLUNA.

    Build melhor anda ABAIXO → CLOSE_ENOUGH → META_BATIDA → HARD_STOP, e nessa
    direção a matriz só
    troca continua por PRESERVA. Equipar melhor nunca pode CANCELAR uma extração.
    """
    hp = int(round(_hp_util_para(0.5) * HP_MAX))
    fraco = _prog(0.80, hp=hp, hp_max=HP_MAX)
    forte = _prog(0.97, hp=hp, hp_max=HP_MAX)

    assert not _preserva(avaliar_mapa(EXTRAIR, _mapa(), fraco))
    assert _preserva(avaliar_mapa(EXTRAIR, _mapa(), forte))


def test_a_matriz_e_monotona_nas_duas_direcoes():
    """Nenhuma célula contradiz as duas travas acima.

    Mais poder nunca cancela uma preservação; mais fôlego nunca causa uma.
    """
    poderes = (0.80, 0.97, 1.02, 1.10)
    runways = (0.0, 0.5, 1.5)
    tabela = {(p, r): _preserva(_decidir(p, r)) for p in poderes for r in runways}
    for i in range(len(poderes) - 1):
        for r in runways:
            assert tabela[(poderes[i], r)] <= tabela[(poderes[i + 1], r)]
    for p in poderes:
        for j in range(len(runways) - 1):
            assert tabela[(p, runways[j])] >= tabela[(p, runways[j + 1])]


def test_a_profundidade_sozinha_nao_muda_a_decisao():
    """(F) O TESTE CENTRAL da rodada, agora no nível da DECISÃO.

    Antes o runway era dividido por `mapa.andar`, então o mesmo estado mecânico
    lia fôlego menor só por estar mais fundo — e a matriz mudava de célula por
    profundidade, não por capacidade. Medido nas 900 runs: 461 de 461
    oportunidades caíam em CURTO, e nenhuma em SAUDÁVEL, porque tudo era dividido
    por um andar cada vez maior.

    Aqui o estado é o mesmo e só o andar varia. Banda, estado do runway e veredito
    têm de ser idênticos em toda a profundidade. `_runway_em_andares` tem o mesmo
    teste na unidade; este cobre a ponta que decide.
    """
    for poder, runway in ((0.80, 1.5), (0.97, 0.5), (1.02, 1.5), (1.10, 0.5)):
        vistos = {}
        for andar in (3, 7, 12, 20):
            score = _decidir(poder, runway, andar=andar)
            estado = score.note.split("(")[2].split(")")[0]
            vistos[andar] = (_preserva(score), estado)
        assert len(set(vistos.values())) == 1, f"poder {poder}, runway {runway}: {vistos}"
