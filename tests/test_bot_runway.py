"""A razão de RUNWAY: capacidade restante estimada / progresso já atravessado.

Ela substituiu o modelo de VOTOS — `len(sinais_de_risco) - 1`, quatro textos
booleanos em que dois convenciam e um não, e onde HP 34% e HP 4% eram o mesmo
voto. No lugar entraram números que a própria run mediu.

    custo de uma luta   dano REAL recebido / encontros medidos
    HP útil             vida agora + cura que já está na mão
    lutas que absorvo   HP útil / custo de uma luta  −  lutas até o portal
    andares que aguento lutas que absorvo / lutas por andar observadas
    runway relativo     andares que aguento / andar atual

NÃO é probabilidade de ruína e NÃO é valor esperado. É razão estrutural: as duas
pontas acabam em ANDARES, e a taxa que converte uma na outra vem do histórico da
run, não de constante.

O que estes testes fixam são as MONOTONICIDADES. Elas valem mais que qualquer
número: são o que impede a fórmula de inverter o sinal do que mede, que foi
exatamente o defeito da fuga no combate e o da extração antiga.
"""

from __future__ import annotations

import pytest

from src.sim.bot.evaluators import _runway_relativo
from src.sim.bot.observation import MapState, ProgressionState

CLASSES_NAO_ENTRAM = ("warrior", "mage", "rogue")


def _prog(**kwargs) -> ProgressionState:
    """Uma run que já mediu: cada luta custou 10% da barra, 3 lutas por andar."""
    base = dict(
        nivel=8,
        hp=300,
        hp_max=500,
        mp=60,
        mp_max=100,
        ouro=120,
        taxa_de_saida=60,
        dano_por_luta=0.10,
        combates_observados=12,
        lutas_por_andar=3.0,
        andares_concluidos=4,
    )
    base.update(kwargs)
    return ProgressionState(**base)


def _mapa(**kwargs) -> MapState:
    base = dict(andar=5, posicao=(1, 1), passos_ate_saida=10)
    base.update(kwargs)
    return MapState(**base)


def _runway(mapa_kw=None, **prog_kw) -> float | None:
    return _runway_relativo(_mapa(**(mapa_kw or {})), _prog(**prog_kw))


class TestEvidenciaInsuficiente:
    """Sem medição não se inventa média global. É regra separada e declarada."""

    def test_sem_encontro_medido_nao_ha_runway(self):
        assert _runway(combates_observados=0) is None

    def test_sem_andar_concluido_nao_ha_runway(self):
        assert _runway(andares_concluidos=0) is None

    def test_custo_zero_nao_vira_divisao_por_zero(self):
        assert _runway(dano_por_luta=0.0) is None

    def test_taxa_de_lutas_por_andar_zerada_tambem_e_falta_de_evidencia(self):
        assert _runway(lutas_por_andar=0.0) is None

    def test_com_uma_luta_medida_e_um_andar_concluido_ja_ha_runway(self):
        assert _runway(combates_observados=1, andares_concluidos=1) is not None


class TestMonotonicidades:
    def test_mesmo_historico_menos_hp_runway_menor(self):
        anterior = None
        for hp in (500, 400, 300, 200, 100, 40, 10):
            atual = _runway(hp=hp, hp_max=500)
            if anterior is not None:
                assert atual <= anterior, f"runway subiu ao perder vida (hp={hp})"
            anterior = atual

    def test_mesma_capacidade_andar_maior_runway_relativo_menor(self):
        anterior = None
        for andar in (1, 2, 3, 5, 8, 13, 20):
            atual = _runway(mapa_kw={"andar": andar})
            if anterior is not None:
                assert atual <= anterior, f"runway subiu ao descer mais fundo (andar={andar})"
            anterior = atual

    def test_mais_dano_por_luta_runway_menor(self):
        anterior = None
        for custo in (0.02, 0.05, 0.10, 0.20, 0.35, 0.60):
            atual = _runway(dano_por_luta=custo)
            if anterior is not None:
                assert atual <= anterior, f"runway subiu com luta mais cara (custo={custo})"
            anterior = atual

    def test_pocao_disponivel_nao_diminui_o_runway(self):
        sem = _runway(cura_garantida=0.0)
        for cura in (0.1, 0.25, 0.5):
            assert _runway(cura_garantida=cura) >= sem

    def test_mais_lutas_ate_o_portal_runway_menor(self):
        anterior = None
        for lutas in (0, 1, 2, 3, 5):
            atual = _runway(mapa_kw={"lutas_ate_extracao": lutas})
            if anterior is not None:
                assert atual <= anterior, f"runway subiu com o portal mais perigoso ({lutas})"
            anterior = atual

    def test_rota_inalcancavel_com_o_folego_atual_zera_o_runway(self):
        assert _runway(mapa_kw={"lutas_ate_extracao": 99}) == 0.0

    def test_lutas_por_andar_maiores_reduzem_o_runway(self):
        """Andar que custa mais lutas consome o fôlego mais rápido."""
        anterior = None
        for taxa in (1.0, 2.0, 3.0, 5.0, 8.0):
            atual = _runway(lutas_por_andar=taxa)
            if anterior is not None:
                assert atual <= anterior
            anterior = atual


class TestTetoDeHpNaoFabricaSobrevivencia:
    """Ganhar teto sem ganhar vida não pode melhorar a sobrevivência.

    É o defeito clássico de medir vida em absoluto: subir de nível aumenta
    `base_hp`, e o herói pareceria mais seguro sem ter curado um ponto.
    """

    def test_subir_o_teto_sem_curar_nao_aumenta_o_runway(self):
        antes = _runway(hp=250, hp_max=500)
        depois = _runway(hp=250, hp_max=800)
        assert depois <= antes

    def test_a_mesma_fracao_de_vida_da_o_mesmo_runway_em_qualquer_teto(self):
        """O custo por luta também é fração, então a conta é adimensional."""
        assert _runway(hp=250, hp_max=500) == pytest.approx(_runway(hp=400, hp_max=800))

    def test_curar_de_verdade_aumenta_o_runway(self):
        assert _runway(hp=400, hp_max=500) > _runway(hp=250, hp_max=500)


class TestAMesmaFormulaParaTodaClasse:
    """Nenhum `if classe`. O que muda entre heróis é o histórico, não a regra."""

    def test_o_evaluator_nao_conhece_nome_de_classe(self):
        """Pela AST, e não por `grep`: o que importa é o CÓDIGO, não a prosa.

        Uma busca em texto acusaria o próprio comentário que explica por que não
        existe `if mage` — e um teste que proíbe falar do defeito é um teste que
        empurra a explicação para fora do código.
        """
        import ast
        from pathlib import Path

        arvore = ast.parse(Path("src/sim/bot/evaluators.py").read_text(encoding="utf-8"))
        docstrings = {
            no.body[0].value
            for no in ast.walk(arvore)
            if isinstance(no, ast.Module | ast.FunctionDef | ast.ClassDef)
            and no.body
            and isinstance(no.body[0], ast.Expr)
            and isinstance(no.body[0].value, ast.Constant)
        }
        literais = [
            no.value.lower()
            for no in ast.walk(arvore)
            if isinstance(no, ast.Constant) and isinstance(no.value, str) and no not in docstrings
        ]
        for classe in CLASSES_NAO_ENTRAM:
            assert classe not in literais, f"nome de classe no cérebro: {classe}"

    def test_mesmo_estado_mesmo_runway_seja_quem_for(self):
        """A `ProgressionState` não carrega classe — e é isso que garante a regra."""
        campos = set(ProgressionState.__dataclass_fields__)
        assert not any("class" in c or "classe" in c for c in campos)

    def test_historicos_diferentes_produzem_runways_diferentes(self):
        """A diferença entre heróis entra pelos NÚMEROS que cada run mediu."""
        frageis = _runway(dano_por_luta=0.30)
        resistente = _runway(dano_por_luta=0.08)
        assert resistente > frageis


class TestOQueOModeloNaoE:
    def test_o_runway_pode_passar_de_um(self):
        """Não é probabilidade: não está preso a [0, 1]."""
        assert _runway(hp=500, hp_max=500, dano_por_luta=0.02, mapa_kw={"andar": 1}) > 1.0

    def test_o_runway_nunca_e_negativo(self):
        assert _runway(hp=1, hp_max=500, dano_por_luta=0.9) >= 0.0
