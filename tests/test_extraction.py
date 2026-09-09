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


class TestExtracaoNaoRefazOAndar:
    def test_extrair_salva_o_proximo_andar(self, save_isolado):
        """O andar corrente já foi concluído quando a extração é oferecida.

        Reproduz o que `engine/loop.py` faz ao extrair. Se voltasse a gravar o
        andar concluído, o jogador o refaria e receberia as recompensas de novo.
        """
        heroi = Warrior("Teste")
        heroi.set_level(9)
        andar_concluido = 8

        save_manager.save_game(heroi, andar_concluido + 1, None, slot=1)
        _, andar_ao_voltar, mapa = _recarrega()

        assert andar_ao_voltar == andar_concluido + 1, (
            "voltou para o andar já limpo: as recompensas dele podem ser refeitas"
        )
        assert mapa is None, "o próximo andar tem de ser gerado do zero"

    def test_o_codigo_da_extracao_soma_um(self):
        """Fixa a chamada em `engine/loop.py`, não só a semântica do save."""
        fonte = (RAIZ / "src" / "engine" / "loop.py").read_text(encoding="utf-8")
        assert "save_game(player, dungeon_level + 1, None, slot=slot)" in fonte, (
            "a extração voltou a gravar o andar concluído"
        )


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))
