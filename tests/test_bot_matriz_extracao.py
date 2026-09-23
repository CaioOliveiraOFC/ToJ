"""A MATRIZ da extração: qualidade da build × fôlego da run.

Duas grandezas que não se somam. `poder_relativo` diz se o gladiador já está
pronto para a Arena; `runway` diz se a run ainda tem estrada. Somá-las pediria um
câmbio que ninguém mediu, então a combinação é uma TABELA:

                    SAUDÁVEL   CURTO      ESGOTADO
    ABAIXO          continua   continua   PRESERVA
    EQUIVALENTE     continua   PRESERVA   PRESERVA
    SUPEROU         PRESERVA   PRESERVA   PRESERVA

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
from src.sim.bot.evaluators import ABAIXO, EQUIVALENTE, SUPEROU, avaliar_mapa
from src.sim.bot.observation import MapState, ProgressionState

EXTRAIR = ActionOption(action_id="extrair", family="extrair", label="extração")

# Um histórico de run que já mediu o suficiente para haver runway.
#
# Os números são escolhidos para que a faixa útil de runway (0 a ~1,7) caiba em
# `hp_frac` entre 0 e 1 — ou seja, em estados que o jogo consegue produzir. Com
# `andar=3`, `lutas_por_andar=2` e `dano_por_luta=0,10`, a fórmula vira
# `runway = hp_util / 0,6`, e testar a fronteira deixa de exigir uma barra de
# vida de 450%.
ANDAR = 3
MEDIDO = dict(dano_por_luta=0.10, combates_observados=9, lutas_por_andar=2.0, andares_concluidos=2)
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

    `runway = (hp_util / dano_por_luta - lutas_ate_extracao) / lutas_por_andar / andar`

    Resolver em vez de chutar é o que deixa as fronteiras (runway 0 e 1) serem
    testadas NO ponto, e não perto dele.
    """
    return runway * ANDAR * MEDIDO["lutas_por_andar"] * MEDIDO["dano_por_luta"]


def _decidir(poder: float, runway_alvo: float):
    hp = int(round(_hp_util_para(runway_alvo) * HP_MAX))
    assert 0 <= hp <= HP_MAX, f"runway {runway_alvo} não cabe numa barra de vida"
    return avaliar_mapa(EXTRAIR, _mapa(), _prog(poder, hp=hp, hp_max=HP_MAX))


def _preserva(score) -> bool:
    return score.need is Need.PRESERVAR and score.utility > 0


# --- As nove células -------------------------------------------------------


@pytest.mark.parametrize(
    ("poder", "runway", "espera_preservar", "rotulo"),
    [
        (0.80, 1.5, False, "ABAIXO + saudável: ainda constrói"),
        (0.80, 0.5, False, "ABAIXO + curto: aceita risco para melhorar"),
        (0.80, 0.0, True, "ABAIXO + esgotado: salva o que sobrou"),
        (1.00, 1.5, False, "EQUIVALENTE + saudável: dá para melhorar"),
        (1.00, 0.5, True, "EQUIVALENTE + curto: preservar passa a fazer sentido"),
        (1.00, 0.0, True, "EQUIVALENTE + esgotado: preservar"),
        (1.10, 1.5, True, "SUPEROU + saudável: objetivo cumprido"),
        (1.10, 0.5, True, "SUPEROU + curto: preservar"),
        (1.10, 0.0, True, "SUPEROU + esgotado: preservar"),
    ],
)
def test_as_nove_celulas(poder, runway, espera_preservar, rotulo):
    score = _decidir(poder, runway)
    assert _preserva(score) is espera_preservar, f"{rotulo}: {score.note}"


# --- As fronteiras ---------------------------------------------------------


@pytest.mark.parametrize(
    ("poder", "banda"),
    [
        (1 - ARENA_EQUIVALENCE_BAND - 0.001, ABAIXO),
        (1 - ARENA_EQUIVALENCE_BAND, EQUIVALENTE),
        (1 + ARENA_EQUIVALENCE_BAND, EQUIVALENTE),
        (1 + ARENA_EQUIVALENCE_BAND + 0.001, SUPEROU),
    ],
)
def test_a_fronteira_da_banda_e_a_aprovada(poder, banda):
    """0,95 e 1,05 pertencem a EQUIVALENTE; os vizinhos, não."""
    assert banda in _decidir(poder, 0.5).note


def test_a_fronteira_de_0_95_muda_a_decisao_com_runway_curto():
    """A célula (·, curto) é onde a banda decide: ABAIXO continua, EQUIVALENTE sai."""
    assert not _preserva(_decidir(1 - ARENA_EQUIVALENCE_BAND - 0.001, 0.5))
    assert _preserva(_decidir(1 - ARENA_EQUIVALENCE_BAND, 0.5))


def test_a_fronteira_de_1_05_muda_a_decisao_com_runway_saudavel():
    """A célula (·, saudável) é onde SUPEROU se separa de EQUIVALENTE."""
    assert not _preserva(_decidir(1 + ARENA_EQUIVALENCE_BAND, 1.5))
    assert _preserva(_decidir(1 + ARENA_EQUIVALENCE_BAND + 0.001, 1.5))


def _com_hp(poder: float, hp: int):
    return avaliar_mapa(EXTRAIR, _mapa(), _prog(poder, hp=hp, hp_max=HP_MAX))


def test_runway_exatamente_1_ainda_esta_na_zona_curta():
    """`runway > 1` é SAUDÁVEL, então o empate exato ainda preserva.

    A fronteira é escrita em HP, e não em épsilon de runway, porque HP é inteiro:
    `runway 1,0001` arredonda para o mesmo HP de `runway 1,0` e não testaria
    fronteira nenhuma. Com estes parâmetros, HP 600 dá runway exatamente 1,00 e
    601 é o primeiro ponto acima.
    """
    assert _com_hp(1.00, 600).note.count("runway 1.00 (curto)") == 1
    assert _preserva(_com_hp(1.00, 600))
    assert not _preserva(_com_hp(1.00, 601))


def test_runway_exatamente_0_e_esgotado():
    """`runway > 0` é CURTO; zero é ESGOTADO, e aí até ABAIXO preserva."""
    assert _preserva(_com_hp(0.80, 0))
    assert "esgotado" in _com_hp(0.80, 0).note
    assert not _preserva(_com_hp(0.80, 1))
    assert "curto" in _com_hp(0.80, 1).note


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
    [(0.80, False), (1.00, False), (1.10, True)],
)
def test_sem_evidencia_de_runway_so_quem_superou_preserva(poder, espera_preservar):
    """Sem luta medida não se inventa média. Quem já superou não constrói mais."""
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


def test_a_classificacao_do_cerebro_bate_com_a_da_arena():
    """Duas implementações, uma constante. A paridade é o que impede a divergência.

    O cérebro não pode importar `sim.arena` — ela importa `content` e
    `mechanics`, e este pacote é fechado para os dois.
    """
    for centesimos in range(50, 151):
        poder = centesimos / 100
        assert classificar(poder) in _decidir(poder, 0.5).note


# --- As travas conceituais: a DIREÇÃO importa ------------------------------


def test_pocao_so_pode_mudar_extrair_para_continuar():
    """Poção é fôlego, não poder — e fôlego move a linha para a ESQUERDA.

    `cura_garantida` entra em `hp_util`, que aumenta `runway`. Runway maior anda
    ESGOTADO → CURTO → SAUDÁVEL, e nessa direção a matriz só troca PRESERVA por
    continua. Poção nunca pode CAUSAR uma extração.
    """
    hp = int(round(_hp_util_para(0.5) * HP_MAX))
    sem = _prog(1.00, hp=hp, hp_max=HP_MAX)
    # A poção entra por `cura_garantida`, que soma em `hp_util` — o suficiente
    # para o runway cruzar 1 e a linha andar de CURTO para SAUDÁVEL.
    com = _prog(1.00, hp=hp, hp_max=HP_MAX, cura_garantida=_hp_util_para(1.2) - hp / HP_MAX)

    assert _preserva(avaliar_mapa(EXTRAIR, _mapa(), sem))
    assert not _preserva(avaliar_mapa(EXTRAIR, _mapa(), com))


def test_equipamento_so_pode_mudar_continuar_para_extrair():
    """Equipamento é poder, não fôlego — e poder sobe a COLUNA.

    Build melhor anda ABAIXO → EQUIVALENTE → SUPEROU, e nessa direção a matriz só
    troca continua por PRESERVA. Equipar melhor nunca pode CANCELAR uma extração.
    """
    hp = int(round(_hp_util_para(0.5) * HP_MAX))
    fraco = _prog(0.80, hp=hp, hp_max=HP_MAX)
    forte = _prog(1.10, hp=hp, hp_max=HP_MAX)

    assert not _preserva(avaliar_mapa(EXTRAIR, _mapa(), fraco))
    assert _preserva(avaliar_mapa(EXTRAIR, _mapa(), forte))


def test_a_matriz_e_monotona_nas_duas_direcoes():
    """Nenhuma célula contradiz as duas travas acima.

    Mais poder nunca cancela uma preservação; mais fôlego nunca causa uma.
    """
    poderes = (0.80, 1.00, 1.10)
    runways = (0.0, 0.5, 1.5)
    tabela = {(p, r): _preserva(_decidir(p, r)) for p in poderes for r in runways}
    for i in range(len(poderes) - 1):
        for r in runways:
            assert tabela[(poderes[i], r)] <= tabela[(poderes[i + 1], r)]
    for p in poderes:
        for j in range(len(runways) - 1):
            assert tabela[(p, runways[j])] >= tabela[(p, runways[j + 1])]
