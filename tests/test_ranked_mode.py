"""A Arena Ranqueada jogável: hub, gladiador, matchmaking, partida, rating, classificação.

O gladiador do jogador é uma fixture gravada num diretório de saves temporário,
como em `test_arena_mode.py`. O mundo ranqueado é o da população real com a
priori fraca do OP, gravado no mesmo diretório; o agendador do mundo fica
desligado (ele tem testes próprios em `test_ranked_mundo.py`).

O teclado é roteirizado e, quando o roteiro acaba, responde como um jogador que
só ataca e volta: "1" na ação, qualquer tecla nos avisos, "q" no resto.
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest
from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.extraction import mark_extracted  # noqa: E402
from src.engine import arena_mode, bootstrap, ranked_mode  # noqa: E402
from src.engine import ranked_mundo as rm  # noqa: E402
from src.engine.arena_populacao import Populacao  # noqa: E402
from src.ranked import sistema  # noqa: E402
from src.ranked.ladder import POSICIONAMENTO, Ladder, Registro  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.ia_estrategica import Configuracao, IAEstrategica  # noqa: E402
from src.storage import save_manager  # noqa: E402
from src.ui import (  # noqa: E402
    arena_screens,
    combat_event_handlers,
    navigation_menu,
    ranked_screens,
    renderer,
)

IA_RAPIDA = Configuracao(rollouts=2, rollouts_criticos=3)


class Teclado:
    def __init__(self, roteiro=()):
        self.roteiro = list(roteiro)

    def __call__(self, valid_keys=None, allow_escape=True):
        if self.roteiro:
            return self.roteiro.pop(0)
        if valid_keys is None:
            return "x"
        return "1" if "1" in valid_keys else "q"


@pytest.fixture(scope="module")
def populacao():
    return Populacao()


@pytest.fixture
def saves(tmp_path, monkeypatch):
    monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
    monkeypatch.setattr(
        save_manager, "get_slot_file", lambda slot: str(tmp_path / f"slot_{slot}.json")
    )
    return tmp_path


@pytest.fixture
def tela(monkeypatch):
    console = Console(record=True, width=170, file=io.StringIO())
    for modulo in (arena_screens, ranked_screens, renderer):
        monkeypatch.setattr(modulo, "console", console)
    monkeypatch.setattr(combat_event_handlers, "sleep", lambda *_: None)
    monkeypatch.setattr(navigation_menu, "get_key", lambda: "q")
    return console


@pytest.fixture
def mundo(populacao, saves):
    sis = sistema.criar()
    ladder = Ladder(
        sis,
        [
            Registro(
                o.id,
                o.apelido,
                o.classe,
                True,
                sistema.inicial(sis, o.op),
                forca_de_referencia=o.op,
            )
            for o in populacao.oponentes()
        ],
    )
    return rm.MundoRanqueado(ladder, populacao, semente=11, caminho=str(saves / "ranked.json"))


def salvar(slot, classe, nivel, nome=None):
    heroi = make_hero(classe, nivel, "expected")
    heroi.nick_name = nome or f"{classe}{slot}"
    mark_extracted(heroi, nivel)
    assert save_manager.save_game(heroi, nivel, None, slot=slot)["success"]


def jogar(monkeypatch, mundo, roteiro=(), agora=1000.0):
    teclado = Teclado(roteiro)
    monkeypatch.setattr(arena_mode, "safe_get_key", teclado)
    monkeypatch.setattr(ranked_mode, "safe_get_key", teclado)
    ranked_mode.run_ranqueada(
        populacao=mundo.populacao,
        mundo=mundo,
        controlador=lambda heroi: IAEstrategica(heroi, IA_RAPIDA),
        agora=agora,
        mundo_em_segundo_plano=False,
    )
    return teclado


def _o_jogador(mundo):
    return next(r for r in mundo.ladder.registros() if not r.npc)


class TestHub:
    def test_o_menu_principal_abre_o_hub(self, monkeypatch):
        respostas = iter(["arena", "quit"])
        chamadas: list = []
        monkeypatch.setattr(bootstrap, "call_main_menu", lambda: next(respostas))
        monkeypatch.setattr(bootstrap, "run_arena_hub", lambda: chamadas.append("hub"))
        bootstrap.run_main_loop()
        assert chamadas == ["hub"]

    def test_o_hub_preserva_o_duelo_livre_e_abre_a_ranqueada(self, tela, monkeypatch, mundo):
        chamadas: list = []
        monkeypatch.setattr(arena_mode, "run_arena", lambda: chamadas.append("livre"))
        monkeypatch.setattr(ranked_mode, "run_ranqueada", lambda **k: chamadas.append("ranked"))
        monkeypatch.setattr(ranked_mode, "safe_get_key", Teclado(["1", "2", "3", "q", "q"]))
        ranked_mode.run_arena_hub(populacao=mundo.populacao, mundo=mundo)
        assert chamadas == ["livre", "ranked"]
        assert "CLASSIFICAÇÃO" in tela.export_text()


class TestPartidaRanqueada:
    def test_uma_partida_completa_muda_o_rating_e_nao_toca_o_save(
        self, saves, tela, monkeypatch, mundo
    ):
        salvar(1, "Warrior", 20)
        antes = Path(save_manager.get_slot_file(1)).read_text(encoding="utf-8")
        jogar(monkeypatch, mundo, ["enter", "enter", "enter", "enter"])
        eu = _o_jogador(mundo)
        assert eu.partidas == 1 and eu.historico[0]["origem"] == "ranqueada"
        assert eu.historico[0]["antes"] != eu.historico[0]["depois"]
        oponente = eu.historico[0]["oponente"]
        assert mundo.ladder[oponente].partidas == 1
        assert Path(save_manager.get_slot_file(1)).read_text(encoding="utf-8") == antes
        gravado = json.loads((saves / "ranked.json").read_text(encoding="utf-8"))
        assert any(r["identidade"] == eu.identidade for r in gravado["ladder"]["registros"])
        texto = tela.export_text()
        assert "Adversário encontrado" in texto and "Rating" in texto
        assert "Posicionamento: 1 de 10" in texto

    def test_voltar_na_ficha_mantem_o_adversario_reservado(self, saves, tela, monkeypatch, mundo):
        salvar(1, "Mage", 15)
        encontrados: list = []
        original = ranked_screens.render_opponent_found
        monkeypatch.setattr(
            ranked_screens,
            "render_opponent_found",
            lambda info: (encontrados.append(info["nome"]), original(info)),
        )
        # Painel → buscar → voltar; buscar de novo → voltar; sair.
        jogar(monkeypatch, mundo, ["enter", "enter", "enter", "q", "enter", "q"])
        assert len(encontrados) == 2 and encontrados[0] == encontrados[1]
        assert _o_jogador(mundo).partidas == 0

    def test_dez_partidas_revelam_o_rank(self, saves, tela, monkeypatch, mundo):
        salvar(1, "Rogue", 25)
        resultados = iter([True, True, False, True, False, True, True, False, True, True])

        def duelo_rapido(personagem, adversario, **_):
            venceu = next(resultados)
            return SimpleNamespace(result=SimpleNamespace(winner="p1" if venceu else "p2"))

        monkeypatch.setattr(arena_mode, "duel", duelo_rapido)
        roteiro = ["enter", "enter"] + ["enter", "enter", "x"] * POSICIONAMENTO + ["c", "q"]
        fases: list = []
        original = ranked_screens.render_opponent_found
        monkeypatch.setattr(
            ranked_screens,
            "render_opponent_found",
            lambda info: (fases.append(info["fase"]), original(info)),
        )
        jogar(monkeypatch, mundo, roteiro)
        eu = _o_jogador(mundo)
        assert (eu.vitorias, eu.derrotas) == (7, 3) and eu.posicionado
        assert fases == ["descoberta"] * 4 + ["nivelamento"] * 3 + ["validacao"] * 3
        assert mundo.ladder.rank(eu.identidade) is not None
        texto = tela.export_text()
        assert "Posicionamento concluído" in texto
        assert "(você)" in texto  # a classificação destaca o gladiador
        # A fila do mundo cresceu com as partidas do jogador.
        assert mundo.fila == min(rm.FILA_MAXIMA, POSICIONAMENTO * rm.PARTIDAS_DO_MUNDO_POR_PARTIDA)

    def test_cada_gladiador_tem_o_proprio_mmr(self, saves, tela, monkeypatch, mundo):
        salvar(1, "Warrior", 20)
        salvar(2, "Mage", 20)
        monkeypatch.setattr(
            arena_mode,
            "duel",
            lambda *a, **k: SimpleNamespace(result=SimpleNamespace(winner="p1")),
        )
        # Slot 1: uma partida. Slot 2: duas.
        roteiro = ["enter", "enter", "enter", "enter", "x", "q"]
        roteiro += ["s", "enter", "enter", "enter", "enter", "x", "enter", "enter", "x", "q"]
        jogar(monkeypatch, mundo, roteiro)
        jogadores = sorted(
            (r for r in mundo.ladder.registros() if not r.npc), key=lambda r: r.partidas
        )
        assert [r.partidas for r in jogadores] == [1, 2]
        assert jogadores[0].identidade != jogadores[1].identidade


class TestTelas:
    def test_status_do_posicionamento_e_do_rank(self, mundo):
        eu = mundo.inscrever("jogador:x", "Eu", "Warrior").identidade
        status = ranked_mode.status(mundo, eu)
        assert status["posicionado"] is False and status["fase"] == "descoberta"
        assert status["rank"] is None and status["partidas"] == 0
        for k in range(POSICIONAMENTO):
            mundo.registrar_do_jogador(eu, mundo.adversario(eu), k % 2 == 0)
        status = ranked_mode.status(mundo, eu)
        assert status["posicionado"] and status["rank"] and status["posicao"]
        assert len(status["recentes"]) == ranked_mode.RECENTES_NO_PAINEL

    def test_a_classificacao_tem_todos_os_competitivos_e_os_cinco_definitivos(self, mundo):
        linhas = ranked_mode.linhas_da_classificacao(mundo)
        assert len(linhas) == len(mundo.populacao)
        assert [linha["titulo"] for linha in linhas[:6]] == ["Definitive Master"] * 5 + [None]
        assert linhas[0]["percentil"] == 100.0 and linhas[-1]["percentil"] == 0.0
        assert linhas[-1]["rank"] == "Iron" and linhas[0]["rank"] == "Distinguished Master"
