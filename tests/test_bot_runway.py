"""O RUNWAY: quantos ANDARES ADICIONAIS a run ainda sustenta.

Ele substituiu o modelo de VOTOS — `len(sinais_de_risco) - 1`, quatro textos
booleanos em que dois convenciam e um não, e onde HP 34% e HP 4% eram o mesmo
voto. No lugar entraram números que a própria run mediu.

    custo de uma luta   dano REAL recebido / encontros medidos
    HP útil             vida agora + cura que já está na mão
    lutas que absorvo   HP útil / custo de uma luta  −  lutas até o portal
    runway              lutas que absorvo / lutas por andar observadas

E depois deixou de ser uma RAZÃO. Havia uma divisão por `andar` no fim, e ela
respondia "quanto isso representa em relação a tudo que já percorri" — pergunta
diferente da que a extração faz. Medido em 900 runs, essa escala comprimia o eixo
até ele não decidir nada: 461 de 461 oportunidades em CURTO, zero em SAUDÁVEL,
zero em ESGOTADO. E o valor CAÍA com a profundidade enquanto a capacidade
absoluta CRESCIA. Hoje o número é andares, e é comparável entre profundidades.

NÃO é probabilidade de ruína e NÃO é valor esperado: é capacidade estimada, na
unidade do progresso, com a taxa de conversão vinda do histórico da run.

O que estes testes fixam são as MONOTONICIDADES. Elas valem mais que qualquer
número: são o que impede a fórmula de inverter o sinal do que mede, que foi
exatamente o defeito da fuga no combate e o da extração antiga.
"""

from __future__ import annotations

import pytest

from src.sim.bot.evaluators import _runway_em_andares
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
    return _runway_em_andares(_mapa(**(mapa_kw or {})), _prog(**prog_kw))


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

    def test_a_profundidade_sozinha_nao_move_o_runway(self):
        """O TESTE CENTRAL da nova unidade, e o motivo de ela existir.

        Antes havia `/ andar` no fim da conta, e por isso o mesmo estado mecânico
        lia runway menor só por estar mais fundo — a métrica caía enquanto a
        capacidade real crescia. Agora dois heróis com o mesmo fôlego restante
        leem o MESMO runway, estejam no andar 1 ou no 20.

        Se alguém reintroduzir a divisão, é aqui que aparece.
        """
        valores = {andar: _runway(mapa_kw={"andar": andar}) for andar in (1, 2, 3, 5, 8, 13, 20)}
        assert len(set(valores.values())) == 1, f"a profundidade mexeu no runway: {valores}"

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
        assert _runway(hp=500, hp_max=500, dano_por_luta=0.02) > 1.0

    def test_o_runway_nunca_e_negativo(self):
        assert _runway(hp=1, hp_max=500, dano_por_luta=0.9) >= 0.0


class TestAUnidadeEAndares:
    """A conta antiga é reproduzida AQUI, à mão, para a mudança ser auditável.

    O nome e a implementação antigos desapareceram do código de produção — manter
    um `_runway_relativo` vivo só para o teste comparar seria preservar a fórmula
    que a rodada existe para remover, e ela envelheceria em silêncio ao lado da
    nova. Então a referência é escrita explicitamente, nos termos da própria
    definição antiga: `andares_restantes / andar`.
    """

    def _referencia_antiga(self, andar: int, **prog_kw) -> float:
        """`andares_restantes / andar` — a razão que existia antes desta rodada."""
        prog = _prog(**prog_kw)
        mapa = _mapa(andar=andar)
        hp_util = prog.hp_frac + prog.cura_garantida
        lutas = hp_util / prog.dano_por_luta - mapa.lutas_ate_extracao
        andares = lutas / prog.lutas_por_andar
        return andares / max(1, andar)

    @pytest.mark.parametrize("andar", [1, 3, 7, 12, 20])
    def test_o_novo_runway_e_o_antigo_multiplicado_pelo_andar(self, andar):
        """(A) A ponte entre as duas unidades, em cinco profundidades."""
        novo = _runway(mapa_kw={"andar": andar})
        antigo = self._referencia_antiga(andar)
        assert novo == pytest.approx(antigo * max(1, andar))

    def test_capacidade_de_um_andar_e_meio_le_um_e_meio(self):
        """(B) A unidade é direta: 1,5 significa um andar e meio adicional.

        `hp_util / dano_por_luta / lutas_por_andar` = 0,9 / 0,20 / 3 = 1,5.
        """
        assert _runway(
            hp=450, hp_max=500, dano_por_luta=0.20, lutas_por_andar=3.0, mapa_kw={"andar": 10}
        ) == pytest.approx(1.5)

    def test_capacidade_de_sete_decimos_le_sete_decimos(self):
        """(C) 0,42 / 0,20 / 3 = 0,7."""
        assert _runway(
            hp=210, hp_max=500, dano_por_luta=0.20, lutas_por_andar=3.0, mapa_kw={"andar": 10}
        ) == pytest.approx(0.7)

    def test_folego_que_nao_paga_a_rota_ate_o_portal_le_zero(self):
        """(D) Se as lutas do desvio consomem tudo, não sobra andar nenhum."""
        assert (
            _runway(hp=200, hp_max=500, dano_por_luta=0.20, mapa_kw={"lutas_ate_extracao": 2})
            == 0.0
        )
