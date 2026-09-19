"""A Chave de Extração, e a extração que finalmente encerra a run.

Antes desta regra a auditoria mediu três coisas no runtime:

- `_handle_feature` devolvia `"extracted"` e o laço principal NÃO tinha ramo
  para ele: o herói continuava de pé sobre o `E`, no mesmo andar;
- `take_feature` nunca era chamado para a Extração, então a casa ficava e o
  checkpoint era repetível;
- extrair não cobrava nada.

Somadas, faziam de ir até o `E` a jogada estritamente dominante sempre que ele
aparecesse — não havia decisão, só a sorte de o `E` nascer. A Chave devolve o
preço, e o ramo no laço devolve o desfecho.

Estes testes usam o RNG e as funções REAIS. Nada é mockado além da UI bloqueante
e da gravação em disco.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content import extraction  # noqa: E402
from src.content.factories.monsters import create_monster  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.engine import loop as L  # noqa: E402
from src.engine.encounter import process_post_battle  # noqa: E402
from src.engine.game_logic import create_player_from_data  # noqa: E402
from src.engine.map import FeatureTile  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.shared.constants import (  # noqa: E402
    EXTRACTION_KEY_DROP_CHANCE,
    EXTRACTION_KEY_MAX,
)
from src.storage import save_manager  # noqa: E402

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


def _heroi(classe="warrior", nivel=5):
    h = create_player_from_data(classe, "Chave")
    h.set_level(nivel)
    return h


@pytest.fixture()
def porta_da_extracao(monkeypatch):
    """A casa `E` num andar, com a UI e o disco fora do caminho.

    Devolve `abrir(hero, escolha)`: executa `_handle_feature` de verdade e
    informa o que o engine devolveu, o que foi salvo e se a casa continua lá.
    """
    gravados: list = []
    monkeypatch.setattr(L, "save_game", lambda *a, **k: gravados.append(a))
    monkeypatch.setattr(L.screens, "render_extraction_success", lambda *a, **k: None)
    monkeypatch.setattr(L.screens, "render_extraction_no_key", lambda *a, **k: None)

    def abrir(hero, escolha="extract", andar=6):
        random.seed(20260918)
        mapa = L._setup_dungeon_map(andar, None, andar, hero)
        casa = (2, 2)
        mapa.features[casa] = "extraction"
        monkeypatch.setattr(
            L,
            "_get_game_publish",
            lambda: lambda topic, payload: payload.get("result", {}).update({"choice": escolha}),
        )
        resultado = L._handle_feature(hero, mapa, andar, FeatureTile("extraction", casa), 1)
        return {
            "resultado": resultado,
            "casa_continua": casa in mapa.features,
            "salvou_no_andar": gravados[-1][1] if gravados else None,
            "gravou": len(gravados),
        }

    return abrir


# --- 1, 2: o drop ------------------------------------------------------------


class TestDropDaChave:
    """A chave cai de monstro derrotado, pelo RNG real, e nunca empilha."""

    def test_monstro_morto_pode_dropar_chave(self):
        caiu = 0
        for semente in range(400):
            hero = _heroi()
            random.seed(semente)
            process_post_battle(hero, create_monster("Alvo", 5, "bruiser"), 1.0, 5)
            if extraction.has_key(hero):
                caiu += 1
        assert caiu > 0, "nenhuma chave caiu em 400 vitórias — o drop não está ligado"
        assert caiu < 400, "a chave caiu em TODAS as vitórias — não é mais uma chance"
        # Sem balancear: só a confirmação de que a ordem de grandeza é a da regra.
        medida = caiu / 400
        assert 0.5 * EXTRACTION_KEY_DROP_CHANCE < medida < 2 * EXTRACTION_KEY_DROP_CHANCE

    def test_a_chave_cai_pela_funcao_canonica_e_nao_por_outra_porta(self):
        hero = _heroi()
        assert extraction.award_key(hero, rng=random.Random(0) if False else _sempre()) is True
        assert extraction.keys_of(hero) == 1

    def test_nunca_mais_de_uma_chave(self):
        """Cem vitórias seguidas, com o RNG forçado a dar chave sempre."""
        hero = _heroi()
        for _ in range(100):
            extraction.award_key(hero, rng=_sempre())
            assert extraction.keys_of(hero) <= EXTRACTION_KEY_MAX
        assert extraction.keys_of(hero) == 1

    def test_quem_ja_tem_a_chave_nao_consulta_o_rng(self):
        """Não é descartar o resultado: é não rolar. Uma rolagem a mais
        deslocaria todo o sorteio seguinte da run."""
        hero = _heroi()
        extraction.award_key(hero, rng=_sempre())
        espiao = _contador()
        assert extraction.award_key(hero, rng=espiao) is False
        assert espiao.chamadas == 0

    def test_o_campo_nasce_zerado(self):
        for classe in ("warrior", "mage", "rogue"):
            assert extraction.keys_of(_heroi(classe)) == 0


# --- 3: a morte --------------------------------------------------------------


class TestMorrerPerdeAChave:
    def test_o_save_do_personagem_morto_e_apagado_com_a_chave_dentro(self, tmp_path, monkeypatch):
        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
        hero = _heroi()
        extraction.award_key(hero, rng=_sempre())
        save_manager.save_game(hero, 6, None, slot=1)
        recarregado, _andar, _mapa = save_manager.load_game(get_all_items(), CLASSES, slot=1)
        assert extraction.has_key(recarregado), "a chave tem de sobreviver ao save"
        # É isto que a morte faz, e é a mesma chamada de `loop.py`.
        save_manager.delete_save(1)
        vazio, _a, _m = save_manager.load_game(get_all_items(), CLASSES, slot=1)
        assert vazio is None, "morrer apaga o personagem — e a chave vai junto"

    def test_derrotado_no_combate_nao_ganha_chave(self):
        """`process_post_battle` só rola a chave para quem VENCEU."""
        for semente in range(120):
            hero = _heroi()
            hero.set_isalive(False)
            random.seed(semente)
            process_post_battle(hero, create_monster("Alvo", 5, "bruiser"), 1.0, 5)
            assert not extraction.has_key(hero)


# --- 4, 5, 6, 7, 8, 9: a casa `E` -------------------------------------------


class TestPortaDaExtracao:
    def test_sem_chave_nao_extrai(self, porta_da_extracao):
        hero = _heroi()
        assert not extraction.has_key(hero)
        r = porta_da_extracao(hero, "extract")
        assert r["resultado"] is None, "extraiu sem chave"
        assert r["gravou"] == 0, "gravou save sem chave"

    def test_sem_chave_a_casa_permanece_no_mapa(self, porta_da_extracao):
        r = porta_da_extracao(_heroi(), "extract")
        assert r["casa_continua"]

    def test_com_chave_extrai(self, porta_da_extracao):
        hero = _heroi()
        extraction.award_key(hero, rng=_sempre())
        r = porta_da_extracao(hero, "extract")
        assert r["resultado"] == "extracted"
        # FIM DE RUN, não ponto de retomada: grava o andar em que ela acabou.
        assert r["salvou_no_andar"] == 6
        assert extraction.was_extracted(hero)
        assert extraction.extracted_floor(hero) == 6

    def test_extrair_consome_a_chave(self, porta_da_extracao):
        hero = _heroi()
        extraction.award_key(hero, rng=_sempre())
        porta_da_extracao(hero, "extract")
        assert extraction.keys_of(hero) == 0

    def test_recusar_mantem_a_casa_e_a_chave(self, porta_da_extracao):
        hero = _heroi()
        extraction.award_key(hero, rng=_sempre())
        r = porta_da_extracao(hero, "continue")
        assert r["resultado"] is None
        assert r["casa_continua"], "recusar tem de deixar o `E` disponível no andar"
        assert extraction.has_key(hero), "recusar não pode cobrar a chave"

    def test_a_casa_nunca_e_consumida_em_nenhum_dos_desfechos(self, porta_da_extracao):
        """É por isso que o `E` continua valendo até o herói mudar de andar."""
        com_chave = _heroi()
        extraction.award_key(com_chave, rng=_sempre())
        assert porta_da_extracao(com_chave, "extract")["casa_continua"]
        assert porta_da_extracao(_heroi(), "continue")["casa_continua"]


class TestExtrairEncerraARun:
    """O ramo que faltava no laço principal."""

    def test_o_laco_principal_trata_extracted(self):
        import inspect
        import re

        ramos = re.findall(r'result == "(\w+)"', inspect.getsource(L.start_game))
        assert "extracted" in ramos, "o laço voltou a ignorar o desfecho da extração"

    def test_extracted_encerra_e_nao_cai_no_vazio(self):
        """O ramo devolve — não segue para o andar seguinte nem continua o laço."""
        import inspect

        fonte = inspect.getsource(L.start_game)
        trecho = fonte[fonte.index('elif result == "extracted":') :]
        corpo = trecho[: trecho.index("elif result ==", 1)]
        assert "return" in corpo
        assert "dungeon_level += 1" not in corpo


# --- 10: o bot não consulta RNG futuro --------------------------------------


class TestOBotNaoConsultaRngFuturo:
    def test_observar_o_mapa_com_e_sem_chave_nao_toca_o_rng(self):
        from tools import bot_adapter as ad
        from tools.bot_padrao import BotPadrao, _pos

        random.seed(20260918)
        bot = BotPadrao(classe="warrior", seed=20260918)
        random.seed(20260918 * 31 + 6)
        bot.andar = 6
        bot.mapa = L._setup_dungeon_map(6, None, 6, bot.hero)
        bot.posicao = _pos(bot.mapa.player_pos)
        bot.saida = _pos(bot.mapa.exit_pos)
        _rota, caminho = ad.rota_para(bot, bot.saida, lutar=False)
        bot.mapa.features[caminho[len(caminho) // 2]] = "extraction"

        for tem_chave in (False, True):
            if tem_chave:
                extraction.award_key(bot.hero, rng=_sempre())
            estado = random.getstate()
            for _ in range(3):
                mapa, prog = ad.estado_do_mapa(bot)
                ad.acoes_do_mapa(bot, mapa, prog)
            assert random.getstate() == estado, "observar o mapa consumiu RNG"
            assert prog.tem_chave is tem_chave

    def test_sem_chave_extrair_nao_e_candidata(self):
        from tools import bot_adapter as ad
        from tools.bot_padrao import BotPadrao, _pos

        random.seed(20260918)
        bot = BotPadrao(classe="warrior", seed=20260918)
        random.seed(20260918 * 31 + 6)
        bot.andar = 6
        bot.mapa = L._setup_dungeon_map(6, None, 6, bot.hero)
        bot.posicao = _pos(bot.mapa.player_pos)
        bot.saida = _pos(bot.mapa.exit_pos)
        # Casa ALCANÇÁVEL: uma do caminho real até a saída.
        _rota, caminho = ad.rota_para(bot, bot.saida, lutar=False)
        bot.mapa.features[caminho[len(caminho) // 2]] = "extraction"

        mapa, prog = ad.estado_do_mapa(bot)
        assert mapa.desvio_extracao is not None, "a casa plantada precisa ser alcançável"
        assert "extrair" not in {o.action_id for o in ad.acoes_do_mapa(bot, mapa, prog)[0]}

        extraction.award_key(bot.hero, rng=_sempre())
        mapa, prog = ad.estado_do_mapa(bot)
        assert "extrair" in {o.action_id for o in ad.acoes_do_mapa(bot, mapa, prog)[0]}

    def test_a_chave_nao_e_comprada_vendida_nem_dada_por_servico(self):
        """A única porta é `award_key`, e ela só é chamada no pós-combate."""
        import subprocess

        saida = subprocess.run(
            ["grep", "-rn", "award_key\\|extraction_keys", "--include=*.py", "src/", "tools/"],
            capture_output=True,
            text=True,
            cwd=str(RAIZ),
        ).stdout
        permitidos = (
            "src/content/extraction.py",
            "src/engine/encounter.py",
            "src/entities/heroes.py",
            "src/storage/save_manager.py",
        )
        for linha in saida.strip().splitlines():
            arquivo = linha.split(":")[0]
            assert arquivo in permitidos, f"chave tocada fora da porta única: {linha}"


# --- utilitários de RNG controlado ------------------------------------------


class _Sempre:
    """Um RNG que sempre faz o drop cair. Não é mock do jogo: é rolagem forçada."""

    def random(self) -> float:
        return 0.0


class _Contador:
    """Conta consultas ao RNG. Prova que quem já tem a chave não rola."""

    def __init__(self) -> None:
        self.chamadas = 0

    def random(self) -> float:
        self.chamadas += 1
        return 1.0


def _sempre() -> _Sempre:
    return _Sempre()


def _contador() -> _Contador:
    return _Contador()
