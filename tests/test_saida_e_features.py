"""A saída cobra, quem não paga perde Essência, e os serviços viraram casas.

Loja, Ferreiro e Extração aconteciam sozinhos no fim do andar: o jogador
recebia os três, todo andar, sem andar até lugar nenhum. Agora são casas do
mapa, com chance e pity. E sair do andar passou a custar — é o que dá preço a
atravessá-lo sem lutar, sem nenhuma regra proibindo evitar combate.

Quem não consegue pagar sobe do mesmo jeito: não há dívida, bloqueio nem
softlock. O preço é a Essência do andar seguinte, e ela tem piso — a punição
encolhe a run, nunca a encerra.
"""

from __future__ import annotations

import math
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.economy import exit_fee  # noqa: E402
from src.content.factories import features  # noqa: E402
from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.factories.features import RULES, roll_features  # noqa: E402
from src.content.floor_exit import (  # noqa: E402
    current_penalty,
    effective_essence,
    use_exit,
)
from src.engine import loop  # noqa: E402
from src.engine.map import FeatureTile, MapOfGame  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402
from src.shared.constants import (  # noqa: E402
    ESSENCE_PENALTY_FLOOR,
    EXTRACTION_MIN_FLOOR,
)


@pytest.fixture
def heroi():
    h = Warrior("Teste")
    h.set_level(10)
    return h


def _mapa() -> MapOfGame:
    m = MapOfGame(height=14, width=28)
    m.generate_map(percent_of_walls=0.05)
    m.place_player()
    m.place_exit()
    return m


class TestServicosNaoSaoMaisGarantidos:
    def test_o_fim_de_andar_nao_abre_mais_loja_ferreiro_nem_extracao(self):
        import inspect

        assert loop.FIM_DE_ANDAR == ("saida", "descanso", "juros")
        fonte = inspect.getsource(loop.start_game)
        depois = fonte[fonte.index('result == "level_complete"') :]
        for garantido in ("UI_OPEN_SHOP", "UI_OPEN_FORGE", "UI_EXTRACTION_PROMPT"):
            assert garantido not in depois, f"{garantido} ainda é automático no fim do andar."

    def test_o_andar_e_quem_sorteia_os_servicos(self):
        import inspect

        assert "roll_features" in inspect.getsource(loop._setup_dungeon_map)

    @pytest.mark.parametrize("feature", ["shop", "forge"])
    def test_a_chance_base_e_a_declarada(self, feature, heroi):
        regra = next(r for r in RULES if r.feature == feature)
        r = random.Random(3)
        caiu = 0
        for _ in range(4000):
            # Streak zerado a cada tentativa: mede a chance BASE, sem pity.
            setattr(heroi, regra.streak_field, 0)
            caiu += feature in roll_features(heroi, 10, r)
        assert abs(caiu / 4000 - regra.base_chance) < 0.03


class TestPity:
    @pytest.mark.parametrize("feature", ["shop", "forge", "extraction"])
    def test_a_chance_sobe_a_cada_andar_sem_aparecer(self, feature):
        regra = next(r for r in RULES if r.feature == feature)
        # Quantas faltas o pity leva para fechar em 100%, pela própria regra.
        faltas_ate_garantir = math.ceil((1.0 - regra.base_chance) / regra.pity_increment)
        chances = [regra.chance(20, n) for n in range(faltas_ate_garantir + 1)]

        assert chances == sorted(chances)
        assert chances[0] == pytest.approx(regra.base_chance)
        assert chances[-1] == 1.0, "O pity precisa chegar a 100% e forçar o encontro."
        assert chances[-2] < 1.0, "Chegar a 100% cedo demais tiraria a chance de o azar existir."

    def test_aparecer_zera_a_seca(self, heroi):
        heroi.shop_miss_streak = 4

        class SempreCai(random.Random):
            def random(self):
                return 0.0

        assert "shop" in roll_features(heroi, 10, SempreCai(0))
        assert heroi.shop_miss_streak == 0

    def test_nao_aparecer_aumenta_a_seca(self, heroi):
        class NuncaCai(random.Random):
            def random(self):
                return 0.999999

        roll_features(heroi, 10, NuncaCai(0))
        assert heroi.shop_miss_streak == 1
        assert heroi.forge_miss_streak == 1
        assert heroi.extraction_miss_streak == 1

    def test_extracao_respeita_o_andar_minimo(self, heroi):
        class SempreCai(random.Random):
            def random(self):
                return 0.0

        for andar in range(1, EXTRACTION_MIN_FLOOR):
            assert "extraction" not in roll_features(heroi, andar, SempreCai(0))
            assert heroi.extraction_miss_streak == 0, "Andar sem extração não é seca."
        assert "extraction" in roll_features(heroi, EXTRACTION_MIN_FLOOR, SempreCai(0))


class TestTaxaDeSaida:
    def test_a_saida_cobra_quem_pode_pagar(self, heroi):
        heroi.earn_coins(10_000, "combat")
        antes, taxa = heroi.coins, exit_fee(10)
        r = use_exit(heroi, 10)
        assert r.was_paid
        assert heroi.coins == antes - taxa
        assert heroi.ledger["gold_spent_on_exit_fee"] == taxa
        assert heroi.ledger["paid_exits"] == 1

    def test_sem_ouro_nao_cobra_parcialmente(self, heroi):
        """Cobrar o que tem seria dívida disfarçada: sem ouro E com punição."""
        taxa = exit_fee(10)
        heroi.earn_coins(taxa - 50, "combat")
        moedas = heroi.coins

        r = use_exit(heroi, 10)
        assert not r.was_paid
        assert r.paid == 0
        assert heroi.coins == moedas, "Saída não paga não pode tirar ouro nenhum."
        assert heroi.ledger.get("gold_spent_on_exit_fee", 0) == 0

    def test_sem_ouro_o_jogador_sobe_do_mesmo_jeito(self, heroi):
        """Não há bloqueio, não há softlock: a run continua."""
        for _ in range(10):
            r = use_exit(heroi, 10)
            assert not r.was_paid
        assert heroi.unpaid_exit_streak == 10, "A sequência não tem teto."

    def test_a_sequencia_sobe_de_um_em_um(self, heroi):
        for esperado in (1, 2, 3):
            assert use_exit(heroi, 10).streak == esperado
            assert heroi.unpaid_exit_streak == esperado

    def test_nao_existe_divida(self, heroi):
        """O design de dívida foi removido: nada é cobrado depois."""
        for _ in range(3):
            use_exit(heroi, 10)
        heroi.earn_coins(10_000, "combat")
        assert heroi.coins == 10_000, "Renda futura não pode ser confiscada."
        assert not hasattr(heroi, "exit_debt_amount")
        assert not hasattr(heroi, "exit_debt_streak")


class TestPenalidadeDeEssencia:
    def test_a_penalidade_e_a_sequencia_vezes_dois_decimos(self, heroi):
        for streak in range(6):
            heroi.unpaid_exit_streak = streak
            assert current_penalty(heroi) == pytest.approx(streak * 0.20)

    def test_a_sequencia_declarada(self, heroi):
        """1,5x sorteado, descontando 0,2x por saída não paga."""
        efetivos = []
        for streak in range(7):
            heroi.unpaid_exit_streak = streak
            efetivos.append(round(effective_essence(heroi, 1.5), 2))
        assert efetivos == [1.5, 1.3, 1.1, 0.9, 0.7, 0.5, 0.5]

    def test_a_essencia_nunca_fica_abaixo_do_piso(self, heroi):
        for rolled in (0.5, 0.7, 1.0, 2.2):
            for streak in range(0, 30):
                heroi.unpaid_exit_streak = streak
                assert effective_essence(heroi, rolled) >= ESSENCE_PENALTY_FLOOR

    def test_o_piso_vale_mesmo_com_roll_ja_baixo(self, heroi):
        heroi.unpaid_exit_streak = 1
        assert effective_essence(heroi, 0.7) == pytest.approx(0.5)
        heroi.unpaid_exit_streak = 9
        assert effective_essence(heroi, 0.5) == pytest.approx(0.5)

    def test_pagar_uma_saida_zera_a_punicao_na_hora(self, heroi):
        for _ in range(4):
            use_exit(heroi, 10)
        assert current_penalty(heroi) == pytest.approx(0.8)
        assert effective_essence(heroi, 1.5) == pytest.approx(0.7)

        heroi.earn_coins(10_000, "combat")
        assert use_exit(heroi, 10).was_paid
        assert heroi.unpaid_exit_streak == 0
        assert current_penalty(heroi) == 0
        assert effective_essence(heroi, 1.5) == pytest.approx(1.5), (
            "No andar seguinte a Essência volta ao roll normal."
        )

    def test_a_extracao_nao_depende_da_punicao(self, heroi):
        """Extrair é a saída de emergência: ignora ouro e sequência."""
        import inspect

        from src.content import floor_exit

        heroi.unpaid_exit_streak = 9
        fonte = inspect.getsource(floor_exit)
        assert "extract" not in fonte.lower(), (
            "A regra da saída não pode conhecer Extração — são portas diferentes."
        )
        # E o fluxo da Extração também não consulta a punição em lugar nenhum.
        assert "unpaid_exit_streak" not in inspect.getsource(loop._handle_feature)


class TestFeaturesNoMapa:
    def test_nao_sobrepoem_nada(self):
        for semente in range(40):
            random.seed(semente)
            m = _mapa()
            for _ in range(6):
                m.place_enemy(spawn_by_role("trash", 1))
            m.place_event("altar")
            for f in ("shop", "forge", "extraction"):
                m.place_feature(f)
            ocupadas = [
                (m.player_pos["y"], m.player_pos["x"]),
                (m.exit_pos["y"], m.exit_pos["x"]),
                *m.enemies_pos,
            ]
            if m.event_pos:
                ocupadas.append(m.event_pos)
            for pos in m.features:
                assert pos not in ocupadas
            assert len(set(m.features)) == len(m.features)

    def test_pisar_devolve_o_servico_sem_consumi_lo(self):
        """Quem consome é o fluxo: a Extração recusada continua no mapa."""
        for semente in range(200):
            random.seed(semente)
            m = _mapa()
            py, px = m.player_pos["y"], m.player_pos["x"]
            for direcao, (dy, dx) in (("w", (-1, 0)), ("s", (1, 0)), ("a", (0, -1)), ("d", (0, 1))):
                ny, nx = py + dy, px + dx
                if m.grid[ny][nx] == "." and (ny, nx) != (m.exit_pos["y"], m.exit_pos["x"]):
                    m.features[(ny, nx)] = "extraction"
                    resultado = m.move_player(direcao)
                    assert isinstance(resultado, FeatureTile)
                    assert resultado.feature == "extraction"
                    assert (ny, nx) in m.features, "Pisar não pode consumir sozinho."
                    assert m.take_feature((ny, nx)) == "extraction"
                    assert (ny, nx) not in m.features
                    return
        pytest.skip("Nenhum mapa com casa livre ao lado do jogador.")

    def test_aparecem_no_desenho_com_os_caracteres_declarados(self):
        m = _mapa()
        for f in ("shop", "forge", "extraction"):
            m.place_feature(f)
        desenho = "".join(m.draw_map())
        for char in ("$", "F", "E"):
            assert char in desenho


class TestSaveLoad:
    def test_o_mapa_preserva_as_features(self):
        m = _mapa()
        for f in ("shop", "forge", "extraction"):
            m.place_feature(f)
        m.place_event("fountain")
        recarregado = MapOfGame(height=m.height, width=m.width)
        recarregado.load_map_state(m.get_map_state())
        assert recarregado.features == m.features
        assert recarregado.event_pos == m.event_pos

    def test_feature_consumida_nao_volta(self):
        m = _mapa()
        pos = m.place_feature("shop")
        m.take_feature(pos)
        recarregado = MapOfGame(height=m.height, width=m.width)
        recarregado.load_map_state(m.get_map_state())
        assert pos not in recarregado.features

    def test_o_jogador_preserva_a_punicao_e_o_pity(self, tmp_path, monkeypatch):
        from src.content.items import get_all_items
        from src.entities.heroes import Mage, Rogue
        from src.storage import save_manager

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
        monkeypatch.setattr(
            save_manager, "get_slot_file", lambda s: str(tmp_path / f"slot_{s}.json")
        )
        heroi = Warrior("Fujão")
        heroi.unpaid_exit_streak = 2
        heroi.shop_miss_streak = 3
        heroi.forge_miss_streak = 1
        heroi.extraction_miss_streak = 4

        save_manager.save_game(heroi, 7, None, slot=1)

        class _Registro:
            def get(self, nome):
                return get_all_items()[nome]

        carregado, _, _ = save_manager.load_game(
            _Registro(), {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}, slot=1
        )
        assert carregado.unpaid_exit_streak == 2
        assert carregado.shop_miss_streak == 3
        assert carregado.forge_miss_streak == 1
        assert carregado.extraction_miss_streak == 4


class TestSimuladorUsaAsMesmasRegras:
    def test_o_simulador_chama_as_funcoes_do_jogo(self):
        import inspect

        from src.sim import harness

        fonte = inspect.getsource(harness.simulate_run)
        assert "roll_features(" in fonte, "O sim precisa do MESMO sorteio de serviços."
        assert "use_exit(" in fonte, "O sim precisa da MESMA regra de saída."

    def test_a_telemetria_registra_saida_e_servicos(self):
        from src.sim.harness import simulate_run

        r = simulate_run("Warrior", max_floor=20, iterations=30, policy="smart", seed=7)
        saida, feats = r["telemetry"]["exit"], r["telemetry"]["features"]
        assert saida["fee_paid"] > 0
        assert saida["paid"] + saida["unpaid"] > 0
        assert feats["spawned"].get("shop", 0) > 0
        assert feats["spawned"].get("forge", 0) > 0

    def test_a_run_covarde_paga_em_essencia_e_nao_trava(self):
        """Evitar tudo continua possível — e vai ficando caro."""
        sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
        from measure_floor_loop import run_covarde

        d = run_covarde(andares=12, capital_inicial=0)
        assert d["andares"] == 12, "A run covarde não pode travar: ela continua."
        assert d["streak"] == 12, "Sem renda, toda saída fica sem pagar."
        assert d["essencia_efetiva"] < d["essencia_sorteada"]
        assert d["essencia_efetiva_min"] >= ESSENCE_PENALTY_FLOOR

        com_capital = run_covarde(andares=12, capital_inicial=100_000)
        assert com_capital["streak"] == 0, "Com capital, dá para pagar todas."
        assert com_capital["essencia_efetiva"] == pytest.approx(com_capital["essencia_sorteada"]), (
            "Sem punição, a efetiva é o próprio roll."
        )


def _features_modulo_existe():
    assert features.SHOP and features.FORGE and features.EXTRACTION
