"""Evento é casa do mapa, e o mapa sabe dizer o que obriga.

O evento acontecia sozinho ao pisar na saída: o jogador não escolhia, recebia.
Agora é uma casa — quem quiser o Altar anda até ele, e quem preferir a saída
passa direto. E como andar passou a ser decisão, o andar precisa saber responder
quanto dele é obrigatório.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.engine import loop  # noqa: E402
from src.engine.map import EventTile, MapOfGame  # noqa: E402
from src.engine.map_analysis import analisar  # noqa: E402
from src.shared.constants import RANDOM_EVENT_CHANCE  # noqa: E402


def _mapa(altura=14, largura=28) -> MapOfGame:
    m = MapOfGame(height=altura, width=largura)
    m.generate_map(percent_of_walls=0.05)
    m.place_player()
    m.place_exit()
    return m


class TestEventoSaiuDoFimDeAndar:
    def test_a_ordem_de_fim_de_andar_nao_tem_mais_evento(self):
        assert "evento" not in loop.FIM_DE_ANDAR
        assert loop.FIM_DE_ANDAR == ("descanso", "loja", "ferreiro", "juros", "extracao")

    def test_chegar_na_saida_nao_dispara_evento(self):
        """Medido no código: o ramo de `level_complete` não sorteia mais nada."""
        import inspect

        fonte = inspect.getsource(loop.start_game)
        depois = fonte[fonte.index('result == "level_complete"') :]
        assert "roll_random_event" not in depois

    def test_o_andar_e_quem_sorteia_o_evento(self):
        import inspect

        assert "roll_random_event" in inspect.getsource(loop._setup_dungeon_map)


class TestEventoNoMapa:
    def test_a_chance_continua_sendo_a_declarada(self):
        from src.content.factories.dungeons import roll_random_event

        r = random.Random(7)
        caiu = sum(1 for _ in range(20_000) if roll_random_event(r) is not None)
        assert abs(caiu / 20_000 - RANDOM_EVENT_CHANCE) < 0.02

    def test_no_maximo_um_evento_por_andar(self):
        m = _mapa()
        m.place_event("altar")
        primeiro = m.event_pos
        m.place_event("fountain")
        assert m.event_pos != primeiro or m.event_type == "fountain"
        # Uma casa e um tipo: não existe lista de eventos.
        assert isinstance(m.event_pos, tuple)
        assert isinstance(m.event_type, str)

    def test_nao_sobrepoe_jogador_saida_nem_inimigo(self):
        for semente in range(60):
            random.seed(semente)
            m = _mapa()
            for _ in range(8):
                m.place_enemy(spawn_by_role("trash", 1))
            m.place_event("merchant")
            if m.event_pos is None:
                continue
            assert m.event_pos != (m.player_pos["y"], m.player_pos["x"])
            assert m.event_pos != (m.exit_pos["y"], m.exit_pos["x"])
            assert m.event_pos not in m.enemies_pos

    def test_aparece_no_desenho_como_interrogacao(self):
        m = _mapa()
        m.place_event("altar")
        assert any("?" in linha for linha in m.draw_map())


class TestPisarConsomeOEvento:
    def _com_evento_ao_lado(self):
        """Põe o evento numa casa vizinha do jogador e devolve a direção."""
        for semente in range(200):
            random.seed(semente)
            m = _mapa()
            py, px = m.player_pos["y"], m.player_pos["x"]
            for direcao, (dy, dx) in (("w", (-1, 0)), ("s", (1, 0)), ("a", (0, -1)), ("d", (0, 1))):
                ny, nx = py + dy, px + dx
                if m.grid[ny][nx] == "." and (ny, nx) != (m.exit_pos["y"], m.exit_pos["x"]):
                    m.event_pos, m.event_type = (ny, nx), "fountain"
                    return m, direcao
        pytest.skip("Nenhum mapa com casa livre ao lado do jogador.")

    def test_pisar_devolve_o_evento(self):
        m, direcao = self._com_evento_ao_lado()
        resultado = m.move_player(direcao)
        assert isinstance(resultado, EventTile)
        assert resultado.event_type == "fountain"

    def test_a_casa_fica_vazia_mesmo_sem_aceitar(self):
        """Recusar o Altar gasta a visita: não existe farm de entra-e-sai."""
        m, direcao = self._com_evento_ao_lado()
        m.move_player(direcao)
        assert m.event_pos is None and m.event_type is None
        # Voltar e pisar de novo não devolve nada.
        oposto = {"w": "s", "s": "w", "a": "d", "d": "a"}[direcao]
        m.move_player(oposto)
        assert not isinstance(m.move_player(direcao), EventTile)


class TestSaveLoadDoEvento:
    def test_evento_nao_visitado_volta_onde_estava(self):
        m = _mapa()
        m.place_enemy(spawn_by_role("trash", 1))
        m.place_event("altar")
        estado = m.get_map_state()

        recarregado = MapOfGame(height=m.height, width=m.width)
        recarregado.load_map_state(estado)
        assert recarregado.event_pos == m.event_pos
        assert recarregado.event_type == "altar"

    def test_evento_consumido_nao_volta(self):
        m = _mapa()
        m.place_event("merchant")
        m.take_event()
        recarregado = MapOfGame(height=m.height, width=m.width)
        recarregado.load_map_state(m.get_map_state())
        assert recarregado.event_pos is None and recarregado.event_type is None

    def test_save_antigo_sem_a_chave_carrega_como_andar_sem_evento(self):
        m = _mapa()
        estado = m.get_map_state()
        del estado["event"]
        recarregado = MapOfGame(height=m.height, width=m.width)
        recarregado.load_map_state(estado)
        assert recarregado.event_pos is None


class TestGeometriaDoAndar:
    def test_encontra_a_saida(self):
        m = _mapa()
        g = analisar(m)
        assert g.curta.alcancavel
        manhattan = abs(m.player_pos["y"] - m.exit_pos["y"]) + abs(
            m.player_pos["x"] - m.exit_pos["x"]
        )
        assert g.curta.passos >= manhattan, "Caminho mais curto que a distância reta."

    def test_conta_os_inimigos_obrigatorios(self):
        """Mapa lotado: não há como atravessar sem lutar."""
        m = _mapa()
        inicio = (m.player_pos["y"], m.player_pos["x"])
        fim = (m.exit_pos["y"], m.exit_pos["x"])
        m.enemies_pos = {
            (y, x): spawn_by_role("trash", 1)
            for y, linha in enumerate(m.grid)
            for x, c in enumerate(linha)
            if c == "." and (y, x) not in (inicio, fim)
        }
        g = analisar(m)
        assert g.segura.combates > 0
        assert g.evitaveis < g.monstros

    def test_conta_os_inimigos_evitaveis(self):
        """Mapa aberto com poucos monstros: dá para contornar todo mundo."""
        m = _mapa()
        for _ in range(5):
            m.place_enemy(spawn_by_role("trash", 1))
        g = analisar(m)
        assert g.monstros == 5
        assert 0.0 <= g.fracao_evitavel <= 1.0
        assert g.evitaveis == g.monstros - g.segura.combates

    def test_a_rota_segura_nunca_luta_mais_que_a_curta(self):
        for semente in range(40):
            random.seed(semente)
            m = _mapa()
            for _ in range(10):
                m.place_enemy(spawn_by_role("trash", 1))
            g = analisar(m)
            assert g.segura.combates <= g.curta.combates
            assert g.segura.passos >= g.curta.passos

    def test_mede_o_desvio_do_evento(self):
        m = _mapa()
        m.place_event("altar")
        g = analisar(m)
        assert g.tem_evento
        assert g.desvio_do_evento >= 0


class TestSimuladorSeparaGerarDeVisitar:
    def test_a_telemetria_conta_as_duas_coisas(self):
        from src.sim.harness import simulate_run

        r = simulate_run("Warrior", max_floor=20, iterations=30, policy="smart", seed=7)
        ev = r["telemetry"]["events"]
        assert ev["spawned"] > 0
        assert ev["visited"] + ev["skipped"] == ev["spawned"]
