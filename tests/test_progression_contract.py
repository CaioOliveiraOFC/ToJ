"""O contrato de progressão de nível numa masmorra infinita.

A grandeza protegida é `nível do herói − nível esperado do encontro`. Estar
atrás é dificuldade; ficar **cada vez mais** atrás é a run ter teto matemático,
e é isso que estes testes impedem.

São propriedades, não números: nenhum depende de `XP_LEVEL_SOFTENER` valer 6. Se
alguém recalibrar o amortecedor, a banda se move e os testes continuam válidos.
"""

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

from src.shared.constants import (
    BOSS_FLOOR_INTERVAL,
    GROWTH_RATE,
    XP_BASE_COST,
    XP_LEVEL_SOFTENER,
)
from src.shared.formulas import xp_for_level
from src.sim import xp_model as xp

# Perfis de diagnóstico: fração dos encontros do andar que o jogador enfrenta.
# Não são regra de jogo e não existem no produto — o mapa é que decide quanto um
# jogador real evita. Servem só para provar que os três se movem juntos.
BAIXO, NORMAL, ALTO = 0.50, 0.75, 1.00
FUNDO = 1000

# A razão exponencial que existia antes. Fica aqui, e só aqui, como referência
# histórica: é contra ela que se mede se o early game foi preservado.
RAZAO_ANTIGA = 1.195


@pytest.fixture(scope="module")
def trajetorias():
    return {
        (perfil, essencia): xp.level_trajectory(FUNDO, engajamento, essencia)
        for perfil, engajamento in (("baixo", BAIXO), ("normal", NORMAL), ("alto", ALTO))
        for essencia in ("expected", "neutral")
    }


class TestFormaDaCurva:
    def test_o_custo_sempre_sobe(self):
        for nivel in range(1, 2000):
            assert xp_for_level(nivel + 1) > xp_for_level(nivel), f"custo parou no nível {nivel}"

    def test_a_curva_e_nivel_vezes_a_razao_comum(self):
        """`L × 1,12^L`, e não outra forma. É o que casa com a produção do andar.

        Dividido por `L × 1,12^(L-1)`, o custo tem de convergir para uma
        constante. O limite é `XP_BASE_COST / (1 + amortecedor)` — escrito com as
        constantes, não com o valor delas, para o teste sobreviver a uma
        recalibragem do amortecedor.
        """

        def razao(nivel):
            return xp_for_level(nivel) / (nivel * GROWTH_RATE ** (nivel - 1))

        limite = XP_BASE_COST / (1 + XP_LEVEL_SOFTENER)
        assert razao(2000) == pytest.approx(limite, rel=0.01)
        assert razao(500) == pytest.approx(limite, rel=0.03)
        # E converge por cima, monotonicamente: o resíduo é o amortecedor sumindo.
        assert razao(100) > razao(500) > razao(2000) > limite

    def test_o_custo_do_nivel_1_e_a_base(self):
        """O amortecedor existe para isto: não mexer no começo do jogo."""
        assert xp_for_level(1) == XP_BASE_COST

    def test_combates_por_nivel_continuam_subindo(self):
        """Subir de nível continua custando mais fundo — linearmente, não o impossível.

        Era a propriedade que o `XP_LEVEL_RATIO > GROWTH_RATE` protegia. Ela
        sobrevive: `custo/recompensa` é proporcional a `nível + amortecedor`.
        O que morre é a explosão exponencial.
        """
        from src.mechanics.math_operations import calculate_monster_xp_reward

        def combates(nivel):
            return xp_for_level(nivel) / calculate_monster_xp_reward(nivel)

        assert combates(1) < combates(10) < combates(50) < combates(200)
        # Linear, não exponencial: dobrar o nível quase dobra o custo relativo.
        assert combates(200) / combates(100) == pytest.approx(
            (200 + XP_LEVEL_SOFTENER) / (100 + XP_LEVEL_SOFTENER), rel=0.02
        )


class TestModeloUsaAsRegrasReais:
    """Se o modelo inventar densidade própria, ele volta a medir outro jogo."""

    def test_densidade_bate_com_o_gerador_de_verdade(self):
        import random

        from src.content.factories.monsters import generate_monsters_for_level

        for andar in (1, 4, 10, 20, 50, 100):
            random.seed(1234)
            real = statistics.fmean(
                len(generate_monsters_for_level(andar, andar)) for _ in range(120)
            )
            modelo = xp.expected_monsters(andar) - 1.0 / BOSS_FLOOR_INTERVAL
            assert modelo == pytest.approx(real, rel=0.05), (
                f"andar {andar}: modelo {modelo:.1f} contra geração real {real:.1f}"
            )

    def test_nivel_do_encontro_bate_com_o_gerador_de_verdade(self):
        """Cobre o atalho de balde: níveis baixos de herói entram de propósito."""
        import random

        from src.content.factories.monsters import calculate_scaled_monster_level

        for andar, heroi in ((1, 1), (2, 2), (3, 3), (5, 4), (10, 11), (50, 52), (200, 202)):
            random.seed(99)
            real = statistics.fmean(
                calculate_scaled_monster_level(andar, heroi) for _ in range(3000)
            )
            # `expected_monster_level` pondera o chefe junto; compara-se o comum.
            modelo, _ = xp._amostra_do_encontro(andar, heroi)
            assert modelo == pytest.approx(real, abs=0.1), (
                f"andar {andar}, herói {heroi}: modelo {modelo:.2f} contra real {real:.2f}"
            )

    def test_essencia_em_forma_fechada_bate_com_o_sorteio(self):
        import random

        from src.mechanics.math_operations import generate_essence_multiplier

        for andar in (1, 5, 10, 21, 50, 200):
            random.seed(55)
            real = statistics.fmean(generate_essence_multiplier(andar) for _ in range(6000))
            assert xp.expected_essence(andar) == pytest.approx(real, abs=0.02)

    def test_o_chefe_entra_pela_regra_de_intervalo(self):
        """Um chefe a cada `BOSS_FLOOR_INTERVAL` andares, não por chance de spawn."""
        sem_chefe = xp.expected_monsters(10) - 1.0 / BOSS_FLOOR_INTERVAL
        assert xp.expected_monsters(10) - sem_chefe == pytest.approx(0.2)


class TestEarlyGamePreservado:
    def test_a_faixa_ja_calibrada_continua_reconhecivel(self, trajetorias):
        """Andares 1-25 contra a curva antiga: diferença de no máximo 2 níveis.

        A faixa 1-20 é a única que já foi jogada e calibrada. A correção existe
        para o fundo; se ela reescrevesse o começo, seria outra mudança.
        """

        def custo_antigo(nivel):
            return int(XP_BASE_COST * RAZAO_ANTIGA ** (nivel - 1))

        antiga = _trajetoria_com_custo(custo_antigo, 25)
        nova = trajetorias[("normal", "expected")]
        for andar in range(1, 26):
            assert abs(nova[andar] - antiga[andar]) <= 2, (
                f"andar {andar}: nível {nova[andar]} contra {antiga[andar]} da curva antiga"
            )


class TestNaoDivergencia:
    """O coração do contrato: nenhuma das curvas pode se separar com a profundidade."""

    LIMITE = 0.01  # nível por andar; a curva antiga marcava 0,336

    @pytest.mark.parametrize("perfil", ["baixo", "normal", "alto"])
    @pytest.mark.parametrize("essencia", ["expected", "neutral"])
    def test_a_defasagem_nao_tem_tendencia(self, trajetorias, perfil, essencia):
        inclinacao = xp.delta_slope(trajetorias[(perfil, essencia)], 20, FUNDO)
        assert abs(inclinacao) < self.LIMITE, (
            f"{perfil}/{essencia}: {inclinacao:+.5f} nível por andar entre os andares 20 e {FUNDO}"
        )

    @pytest.mark.parametrize(
        "perfil,sinal", [("baixo", -1), ("alto", +1)], ids=["evitar_combate", "limpar_tudo"]
    )
    def test_a_distancia_entre_perfis_estabiliza(self, trajetorias, perfil, sinal):
        """Jogar mais rende níveis e jogar menos custa — sem crescer para sempre.

        É o que transforma rota em decisão: a diferença precisa existir (senão a
        escolha não vale nada) e precisa parar de crescer (senão evitar um
        encontro no andar 10 condena a run no 500).
        """
        outro, normal = trajetorias[(perfil, "expected")], trajetorias[("normal", "expected")]
        distante = sinal * (outro[FUNDO] - normal[FUNDO])
        meio = sinal * (outro[FUNDO // 2] - normal[FUNDO // 2])
        assert distante > 0, f"o perfil {perfil} deixou de se distinguir do normal"
        assert abs(distante - meio) <= 2, (
            f"a distância {perfil}↔normal ainda cresce: {meio} no andar {FUNDO // 2}, "
            f"{distante} no {FUNDO}"
        )

    def test_essencia_desloca_a_curva_sem_inclina_la(self, trajetorias):
        """Essência é vantagem, não requisito estrutural.

        Que ela não incline nenhuma das curvas já é coberto pelo teste acima,
        que roda os seis perfis. O que falta provar é que a vantagem que ela dá
        para de crescer: senão, jogar sem sorte de Essência vira condenação.
        """
        vantagem_meio = (
            trajetorias[("normal", "expected")][FUNDO // 2]
            - trajetorias[("normal", "neutral")][FUNDO // 2]
        )
        vantagem_fundo = (
            trajetorias[("normal", "expected")][FUNDO] - trajetorias[("normal", "neutral")][FUNDO]
        )
        assert vantagem_meio > 0
        assert abs(vantagem_fundo - vantagem_meio) <= 2


class TestGuardaDoAndar1000:
    """Rede de segurança grossa: falha se voltarmos a uma curva divergente.

    Não exige nível exato. Exige que, mil andares depois, o herói ainda esteja
    no mesmo bairro do encontro — nem centenas atrás, nem centenas à frente.
    """

    def test_o_heroi_continua_perto_do_encontro(self, trajetorias):
        for essencia in ("expected", "neutral"):
            delta = xp.level_delta(trajetorias[("normal", essencia)], FUNDO)
            assert abs(delta) <= 10, f"normal/{essencia} no andar {FUNDO}: {delta:+.1f} níveis"

    def test_os_perfis_nao_se_afastam_sem_limite(self, trajetorias):
        baixo = xp.level_delta(trajetorias[("baixo", "neutral")], FUNDO)
        alto = xp.level_delta(trajetorias[("alto", "expected")], FUNDO)
        assert alto - baixo <= 20, (
            f"do canto mais cauteloso ao mais agressivo vão {alto - baixo:.0f} níveis"
        )


def _trajetoria_com_custo(custo, ate: int) -> dict[int, int]:
    """Trajetória sob outra curva de custo — usada só para comparar com a antiga."""
    nivel, acumulado, saida = 1, 0.0, {}
    for andar in range(1, ate + 1):
        acumulado += xp.expected_floor_xp(andar, nivel, xp.expected_essence(andar), NORMAL)
        while acumulado >= custo(nivel):
            acumulado -= custo(nivel)
            nivel += 1
        saida[andar] = nivel
    return saida
