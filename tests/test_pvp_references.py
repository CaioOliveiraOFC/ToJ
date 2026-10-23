"""As referências globais de iniciativa, derivadas da fundação do jogo.

    REF_s(nível) = média, sobre Warrior, Mage e Rogue, de geometric(CLASS_BASE[s], nível)

Nenhum número aqui é escolhido pelo teste: tudo é conferido contra as constantes
de classe, a função de crescimento e os heróis que o próprio jogo constrói. E o
duelo, criado sem nada injetado, usa essas referências e o desempate pela
semente da partida.
"""

from __future__ import annotations

import dataclasses
import inspect
import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.extraction import mark_extracted  # noqa: E402
from src.content.gladiator import prepare_gladiator  # noqa: E402
from src.content.passives import get_passive_by_id  # noqa: E402
from src.content.skills_loader import get_skill_by_id  # noqa: E402
from src.engine.arena_setup import gladiator_from_snapshot  # noqa: E402
from src.engine.game_logic import CLASS_MAP  # noqa: E402
from src.mechanics import combat as combat_mech  # noqa: E402
from src.mechanics.pvp_duel import SIDES, Duel, DuelAction, run_round  # noqa: E402
from src.mechanics.pvp_initiative import (  # noqa: E402
    FOUNDATION_REFERENCES,
    INITIATIVE_STATS,
    REFERENCE_CLASSES,
    InitiativeReference,
    SeededCoinTieBreak,
    build_initiative,
    build_vector,
    foundation_reference,
    level_modifier,
    read_initiative,
)
from src.shared import constants as k  # noqa: E402
from src.shared.formulas import geometric  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.pvp_controllers import FirstLegalSkillController  # noqa: E402
from src.storage.save_manager import to_save_data  # noqa: E402

CLASSES = ("Warrior", "Mage", "Rogue")
NIVEIS = (1, 2, 5, 10, 20, 35, 60)
ALTOS = (100, 250, 500, 1000, 5000)
ATAQUE = DuelAction.attack()


def _heroi(classe, nivel, deck=(), loadout="naked"):
    h = make_hero(classe, nivel, loadout)
    if deck:
        h.skills = {
            i: (c if not isinstance(c, str) else get_skill_by_id(c))
            for i, c in enumerate(deck, start=1)
        }
    mark_extracted(h, nivel)
    return h


def _certeira(skill_id):
    return dataclasses.replace(get_skill_by_id(skill_id), chance=100)


def _valores(ref: InitiativeReference) -> dict[str, float]:
    return {s: getattr(ref, s) for s in INITIATIVE_STATS}


# ---------------------------------------------------------------------------
# 1 — uma referência por nível, comum às três classes
# ---------------------------------------------------------------------------


class TestUmaReferenciaGlobal:
    def test_o_provedor_so_pergunta_o_nivel(self):
        assert list(inspect.signature(FOUNDATION_REFERENCES.at_level).parameters) == ["level"]

    def test_as_classes_da_referencia_sao_as_da_criacao_de_personagem(self):
        assert set(REFERENCE_CLASSES) == {classe for classe, _ in CLASS_MAP.values()}

    @pytest.mark.parametrize("nivel", (1, 10, 35))
    def test_as_tres_classes_sao_normalizadas_pela_mesma_referencia(self, nivel):
        ref = foundation_reference(nivel)
        adversario = make_hero("Warrior", nivel, "naked")
        for classe in CLASSES:
            heroi = make_hero(classe, nivel, "expected")
            leitura = read_initiative("p1", heroi, adversario, FOUNDATION_REFERENCES)
            assert leitura.build == build_initiative(heroi, ref)
            assert leitura.relative_ag == heroi.get_ag() / ref.ag


# ---------------------------------------------------------------------------
# 2, 3 — derivada dos atributos-base e do crescimento canônico
# ---------------------------------------------------------------------------


class TestDerivacao:
    def test_nivel_1_e_a_media_das_bases_das_tres_classes(self):
        ref = foundation_reference(1)
        bases = {
            "hp": (k.WARRIOR_BASE_HP, k.MAGE_BASE_HP, k.ROGUE_BASE_HP),
            "mp": (k.WARRIOR_BASE_MP, k.MAGE_BASE_MP, k.ROGUE_BASE_MP),
            "st": (k.WARRIOR_BASE_ST, k.MAGE_BASE_ST, k.ROGUE_BASE_ST),
            "mg": (k.WARRIOR_BASE_MG, k.MAGE_BASE_MG, k.ROGUE_BASE_MG),
            "ag": (k.WARRIOR_BASE_AG, k.MAGE_BASE_AG, k.ROGUE_BASE_AG),
            "df": (k.WARRIOR_BASE_DF, k.MAGE_BASE_DF, k.ROGUE_BASE_DF),
        }
        assert _valores(ref) == {s: math.fsum(v) / 3 for s, v in bases.items()}

    @pytest.mark.parametrize("nivel", NIVEIS + ALTOS)
    def test_cada_nivel_e_a_media_do_crescimento_canonico(self, nivel):
        esperado = {
            s: math.fsum(geometric(c.CLASS_BASE[s], nivel) for c in REFERENCE_CLASSES) / 3
            for s in INITIATIVE_STATS
        }
        assert _valores(foundation_reference(nivel)) == esperado

    @pytest.mark.parametrize("nivel", NIVEIS)
    def test_corresponde_aos_herois_nus_construidos_pelo_jogo(self, nivel):
        """A média dos três heróis que o jogo constrói, sem equipamento: exata."""
        vetores = [build_vector(make_hero(c, nivel, "naked")) for c in CLASSES]
        media = {s: math.fsum(v[s] for v in vetores) / 3 for s in INITIATIVE_STATS}
        assert _valores(foundation_reference(nivel)) == media

    @pytest.mark.parametrize("nivel", NIVEIS + ALTOS)
    def test_e_neutra_entre_as_classes(self, nivel):
        """Em cada atributo, a média das razões classe/REF das três classes é 1."""
        ref = foundation_reference(nivel)
        for s in INITIATIVE_STATS:
            razoes = [
                geometric(c.CLASS_BASE[s], nivel) / getattr(ref, s) for c in REFERENCE_CLASSES
            ]
            assert math.fsum(razoes) / 3 == pytest.approx(1.0, rel=1e-12)


# ---------------------------------------------------------------------------
# 4 — válida em qualquer nível, inclusive alto, sem teto próprio
# ---------------------------------------------------------------------------


class TestCurvaEmTodoNivel:
    @pytest.mark.parametrize("nivel", ALTOS)
    def test_positiva_e_finita_em_nivel_alto(self, nivel):
        ref = foundation_reference(nivel)
        assert all(math.isfinite(v) and v > 0 for v in _valores(ref).values())

    @pytest.mark.parametrize("nivel", (50, 100, 500, 1000))
    def test_cresce_na_razao_do_jogo(self, nivel):
        antes, depois = foundation_reference(nivel), foundation_reference(nivel + 1)
        for s in INITIATIVE_STATS:
            assert getattr(depois, s) / getattr(antes, s) == pytest.approx(k.GROWTH_RATE, rel=1e-3)

    @pytest.mark.parametrize("classe", CLASSES)
    def test_a_build_nua_de_cada_classe_le_o_mesmo_em_todo_nivel(self, classe):
        """A referência não favorece nível: só o modificador de nível o faz."""
        leituras = [
            build_initiative(make_hero(classe, nivel, "naked"), foundation_reference(nivel))
            for nivel in (*NIVEIS, 100)
        ]
        assert max(leituras) - min(leituras) < 0.005

    @pytest.mark.parametrize("ruim", (0, -3, 2.5, "10"))
    def test_nivel_invalido_e_recusado(self, ruim):
        with pytest.raises(ValueError):
            foundation_reference(ruim)


# ---------------------------------------------------------------------------
# 5 — a build muda o score; a referência não muda
# ---------------------------------------------------------------------------


class TestABuildNaoMexeNaReferencia:
    def test_equipamento_buff_e_passiva_mudam_o_score_e_nao_a_referencia(self):
        nivel = 10
        antes = _valores(foundation_reference(nivel))
        oponente = make_hero("Mage", nivel, "naked")

        def score(heroi):
            return read_initiative("p1", heroi, oponente, FOUNDATION_REFERENCES).score

        nu = make_hero("Warrior", nivel, "naked")
        base = score(nu)
        assert score(make_hero("Warrior", nivel, "expected")) > base

        com_buff = make_hero("Warrior", nivel, "naked")
        com_buff.active_buffs["Grito"] = {"stat": "st", "value": 30, "duration": 3}
        assert score(com_buff) > base

        com_passiva = make_hero("Warrior", nivel, "naked")
        com_passiva.add_passive(get_passive_by_id("passos_leves"))
        assert score(com_passiva) > base

        assert _valores(foundation_reference(nivel)) == antes
        foundation_reference.cache_clear()
        assert _valores(foundation_reference(nivel)) == antes


# ---------------------------------------------------------------------------
# 6, 7, 8 — comparação crua e desempate pela semente
# ---------------------------------------------------------------------------


class TestComparacaoEDesempate:
    def test_o_score_canonico_e_a_formula_sem_arredondamento(self):
        heroi = make_hero("Rogue", 12, "expected")
        oponente = make_hero("Warrior", 10, "naked")
        ref = foundation_reference(12)
        vetor = build_vector(heroi)
        build = math.fsum(math.sqrt(vetor[s] / getattr(ref, s)) for s in INITIATIVE_STATS) / 6
        leitura = read_initiative("p1", heroi, oponente, FOUNDATION_REFERENCES)
        assert leitura.build == build
        assert leitura.score == build * level_modifier(12, 10)

    def _primeiro_no_espelho(self, semente):
        base = make_hero("Rogue", 10, "expected")
        mark_extracted(base, 10)
        g1, g2 = prepare_gladiator(base), prepare_gladiator(base)
        d = Duel(g1, g2, rng=random.Random(semente))
        registro = d.play_round({"p1": ATAQUE, "p2": ATAQUE})
        assert registro.order.decided_by == "fallback"
        return registro.order.first

    def test_desempate_pela_semente_e_reproduzivel(self):
        primeira = [self._primeiro_no_espelho(s) for s in range(8)]
        segunda = [self._primeiro_no_espelho(s) for s in range(8)]
        assert primeira == segunda
        # Sem prioridade fixa por lado: a moeda escolhe os dois.
        assert set(primeira) == set(SIDES)

    def test_o_padrao_do_duelo_e_a_moeda_pela_semente(self):
        semente = 3
        esperado = SeededCoinTieBreak().first(
            read_initiative(
                "p1", make_hero("Rogue", 10), make_hero("Rogue", 10), FOUNDATION_REFERENCES
            ),
            read_initiative(
                "p2", make_hero("Rogue", 10), make_hero("Rogue", 10), FOUNDATION_REFERENCES
            ),
            random.Random(semente),
        )
        assert self._primeiro_no_espelho(semente) == esperado

    def test_o_sorteio_so_acontece_no_empate_exato(self):
        class Espia:
            def __init__(self):
                self.chamadas = 0

            def first(self, a, b, rng):
                self.chamadas += 1
                return a.side

        def chamadas(ajuste_de_ag: int) -> tuple[int, str]:
            base = make_hero("Rogue", 10, "expected")
            mark_extracted(base, 10)
            g1, g2 = prepare_gladiator(base), prepare_gladiator(base)
            if ajuste_de_ag:
                g2.hero.active_buffs["Passo"] = {"stat": "ag", "value": ajuste_de_ag, "duration": 9}
            espia = Espia()
            d = Duel(g1, g2, tie_break=espia, rng=random.Random(1))
            registro = d.play_round({"p1": ATAQUE, "p2": ATAQUE})
            return espia.chamadas, registro.order.decided_by

        assert chamadas(0) == (1, "fallback")
        # Um ponto de AG a mais: o score já difere, e a moeda nem é consultada.
        assert chamadas(1) == (0, "score")


# ---------------------------------------------------------------------------
# 9, 10 — o duelo pelo caminho normal, com o comportamento de antes
# ---------------------------------------------------------------------------


def _snapshot(classe, nivel=10):
    h = make_hero(classe, nivel, "expected")
    mark_extracted(h, nivel)
    return to_save_data(h, nivel)


class TestDueloPeloCaminhoNormal:
    @pytest.mark.parametrize(("a", "b"), [("Warrior", "Mage"), ("Rogue", "Warrior")])
    def test_duelo_sem_tabela_injetada_usa_a_referencia_canonica(self, a, b):
        g1, g2 = gladiator_from_snapshot(_snapshot(a)), gladiator_from_snapshot(_snapshot(b))
        ag_inicial = {lado: g.hero.get_ag() for lado, g in zip(SIDES, (g1, g2))}
        d = Duel(g1, g2, rng=random.Random(9))
        controladores = {lado: FirstLegalSkillController() for lado in SIDES}
        while not d.finished and d.round_number <= 400:
            run_round(d, controladores)
        assert d.finished and d.result.reason == "ko"
        primeira = {x.side: x for x in d.history[0].initiative}
        ref = foundation_reference(10)
        assert all(primeira[lado].relative_ag == ag_inicial[lado] / ref.ag for lado in SIDES)

    def test_controle_antes_da_acao_pendente_cancela_e_devolve_a_reserva(self):
        d = Duel(
            prepare_gladiator(_heroi("Warrior", 12, deck=(_certeira("fortalecimento"),))),
            prepare_gladiator(_heroi("Warrior", 10, deck=("golpe_poderoso",))),
            rng=random.Random(9),
        )
        vitima = d.hero("p2")
        mp_antes = vitima.get_mp()
        registro = d.play_round(
            {
                "p1": DuelAction.use_skill("fortalecimento"),
                "p2": DuelAction.use_skill("golpe_poderoso"),
            }
        )
        assert registro.order.first == "p1"
        assert [p.outcome for p in registro.steps] == ["executed", "cancelled_control"]
        assert vitima.get_mp() == mp_antes
        assert "golpe_poderoso" not in vitima.skill_cooldowns

    def test_mana_burn_so_alcanca_o_mp_livre(self):
        d = Duel(
            prepare_gladiator(_heroi("Mage", 12, deck=("dreno_mana",))),
            prepare_gladiator(_heroi("Mage", 10, deck=("bola_fogo",))),
            rng=random.Random(7),
        )
        vitima = d.hero("p2")
        custo = combat_mech.skill_mana_cost(vitima, get_skill_by_id("bola_fogo"))
        vitima._mp = custo
        registro = d.play_round(
            {"p1": DuelAction.use_skill("dreno_mana"), "p2": DuelAction.use_skill("bola_fogo")}
        )
        assert registro.order.first == "p1"
        passo = next(p for p in registro.steps if p.side == "p2")
        assert passo.outcome == "executed"
        assert passo.mp_reserved == passo.mp_spent == custo
        assert vitima.get_mp() == 0
