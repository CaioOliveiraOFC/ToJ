"""Regressões da extração: o save tem de preservar o custo da run.

Extrair era a jogada ótima do jogo, e por dois motivos que nada tinham a ver
com design. O save não gravava HP nem MP, então recarregar reconstruía o herói
no nível salvo com os recursos no máximo; e a extração gravava o andar que
acabara de ser concluído, então voltar refazia esse andar e pagava as
recompensas outra vez.

Juntos, davam cura total gratuita e um moedor infinito de XP e ouro. Uma
estratégia degenerada não é só mais um defeito: ela anula todas as outras
decisões do jogo, porque nenhuma escolha de recurso importa se dá para resetar.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content import extraction  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.storage import save_manager  # noqa: E402

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


@pytest.fixture()
def save_isolado(tmp_path, monkeypatch):
    """Aponta o save para um diretório temporário: o teste nunca toca o do jogador."""
    monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
    return tmp_path


def _recarrega(slot: int = 1):
    jogador, andar, mapa = save_manager.load_game(get_all_items(), CLASSES, slot=slot)
    assert jogador is not None, "o save gravado não voltou"
    return jogador, andar, mapa


class TestRecursosSobrevivemAoSave:
    def test_hp_ferido_continua_ferido(self, save_isolado):
        heroi = Warrior("Teste")
        heroi.set_level(6)
        ferido = int(heroi.base_hp * 0.30)
        heroi.take_damage(heroi.get_hp() - ferido)

        save_manager.save_game(heroi, 7, None, slot=1)
        voltou, _, _ = _recarrega()

        assert voltou.get_hp() == ferido, "recarregar curou o herói de graça"
        assert voltou.get_hp() < voltou.base_hp

    def test_mp_gasto_continua_gasto(self, save_isolado):
        heroi = Mage("Teste")
        heroi.set_level(6)
        heroi.reduce_mp(int(heroi.base_mp * 0.8))
        restante = heroi.get_mp()

        save_manager.save_game(heroi, 7, None, slot=1)
        voltou, _, _ = _recarrega()

        assert voltou.get_mp() == restante, "recarregar devolveu mana de graça"

    def test_o_teto_e_respeitado_apos_as_passivas(self, save_isolado):
        """Passiva de vida altera `base_hp`; o HP salvo não pode ultrapassar o novo teto."""
        from src.content.passives import load_passives

        heroi = Warrior("Teste")
        heroi.set_level(6)
        grandes = [p for p in load_passives() if p.effect_type == "max_hp"]
        heroi.add_passive(max(grandes, key=lambda p: int(p.effect_value)))

        save_manager.save_game(heroi, 7, None, slot=1)
        voltou, _, _ = _recarrega()

        assert voltou.get_hp() <= voltou.base_hp
        assert voltou.get_hp() == heroi.get_hp()

    def test_save_antigo_sem_hp_ainda_carrega(self, save_isolado):
        """Compatibilidade: save gravado antes desta correção não pode quebrar."""
        import json

        heroi = Rogue("Teste")
        heroi.set_level(4)
        save_manager.save_game(heroi, 5, None, slot=1)

        caminho = save_manager.get_slot_file(1)
        dados = json.loads(Path(caminho).read_text())
        del dados["hp"]
        del dados["mp"]
        Path(caminho).write_text(json.dumps(dados))

        voltou, andar, _ = _recarrega()
        assert voltou is not None
        assert andar == 5


class TestExtrairEncerraARunEmVezDeAdiantarOAndar:
    """A extração grava FIM DE RUN, não ponto de retomada.

    Esta classe guardava outra coisa: que a extração gravasse `andar + 1`. O `+1`
    existia para tapar um buraco real — a extração gravava o andar recém-concluído,
    e voltar ao save refazia esse andar e pagava as recompensas de novo.

    O loop hoje é de mão única — dungeon → extração → personagem preservado →
    camada pós-dungeon —, e a marca de run extraída fecha o mesmo buraco por
    cima e mais fundo: quem extraiu NÃO REENTRA na dungeon em andar nenhum,
    então não há andar a refazer nem recompensa a repetir. Gravar `+1` seria
    prometer uma retomada que não existe.
    """

    def test_a_marca_de_extracao_sobrevive_ao_save(self, save_isolado):
        heroi = Warrior("Teste")
        heroi.set_level(9)
        extraction.mark_extracted(heroi, 8)
        save_manager.save_game(heroi, 8, None, slot=1)

        recarregado, andar, mapa = _recarrega()
        assert extraction.was_extracted(recarregado), "o save perdeu o fim da run"
        assert extraction.extracted_floor(recarregado) == 8
        assert andar == 8, "o registro é o andar em que a run ACABOU"
        assert mapa is None

    def test_save_de_run_viva_nao_vem_marcado(self, save_isolado):
        heroi = Warrior("Teste")
        heroi.set_level(4)
        save_manager.save_game(heroi, 5, None, slot=1)
        recarregado, andar, _mapa = _recarrega()
        assert not extraction.was_extracted(recarregado)
        assert andar == 5, "uma run viva continua retomando onde parou"

    def test_save_antigo_sem_o_campo_carrega_como_run_viva(self, save_isolado):
        """Compatibilidade: o campo não existia, e a ausência dele é 'não extraída'."""
        import json

        heroi = Warrior("Teste")
        heroi.set_level(6)
        save_manager.save_game(heroi, 7, None, slot=1)
        caminho = save_manager.get_slot_file(1)
        dados = json.loads(Path(caminho).read_text(encoding="utf-8"))
        del dados["extracted_on_floor"]
        Path(caminho).write_text(json.dumps(dados), encoding="utf-8")

        recarregado, andar, _mapa = _recarrega()
        assert recarregado is not None, "o save antigo tem de continuar legível"
        assert not extraction.was_extracted(recarregado)
        assert andar == 7

    def test_o_codigo_da_extracao_grava_o_andar_do_fim(self):
        """Fixa a chamada em `engine/loop.py`, não só a semântica do save."""
        fonte = (RAIZ / "src" / "engine" / "loop.py").read_text(encoding="utf-8")
        assert "finish_run(" in fonte, "a extração deixou de ser atômica"
        assert "save_game(player, dungeon_level, None, slot=slot)" in fonte
        assert "save_game(player, dungeon_level + 1, None, slot=slot)" not in fonte, (
            "a extração voltou a gravar um ponto de retomada"
        )

    def test_a_listagem_de_slots_distingue_run_extraida(self, save_isolado):
        heroi = Warrior("Teste")
        heroi.set_level(9)
        extraction.mark_extracted(heroi, 8)
        save_manager.save_game(heroi, 8, None, slot=1)
        slot = next(s for s in save_manager.list_slots() if s["slot"] == 1)
        assert slot["extracted"] is True


class TestCarregarExtraidoNaoVoltaParaADungeon:
    """A garantia estrutural: o personagem preservado não reentra na masmorra."""

    def _carregar(self, monkeypatch, marcado: bool):
        from src.engine import bootstrap

        chamadas: list = []
        avisos: list = []
        monkeypatch.setattr(bootstrap, "start_game", lambda *a, **k: chamadas.append(a))
        monkeypatch.setattr(bootstrap.screens, "render_game_saved", lambda m="": avisos.append(m))

        heroi = Warrior("Teste")
        heroi.set_level(9)
        if marcado:
            extraction.mark_extracted(heroi, 8)
        save_manager.save_game(heroi, 8, None, slot=1)

        jogador, andar, mapa = save_manager.load_game(get_all_items(), CLASSES, slot=1)
        # O MESMO trecho do `bootstrap`, sem o menu interativo em volta.
        if jogador and bootstrap.was_extracted(jogador):
            bootstrap.screens.render_game_saved("extraída")
        elif jogador:
            bootstrap.start_game(jogador, andar, mapa, slot=1)
        return chamadas, avisos

    def test_extraido_nao_inicia_a_dungeon(self, save_isolado, monkeypatch):
        chamadas, avisos = self._carregar(monkeypatch, marcado=True)
        assert chamadas == [], "um personagem extraído foi devolvido à dungeon"
        assert avisos, "nem entrou na dungeon nem avisou: o jogador ficaria sem resposta"

    def test_run_viva_continua_carregando_normalmente(self, save_isolado, monkeypatch):
        chamadas, _avisos = self._carregar(monkeypatch, marcado=False)
        assert len(chamadas) == 1, "a run viva parou de retomar"
        assert chamadas[0][1] == 8

    def test_o_bootstrap_checa_a_marca_antes_de_iniciar(self):
        fonte = (RAIZ / "src" / "engine" / "bootstrap.py").read_text(encoding="utf-8")
        assert "was_extracted(player)" in fonte


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
