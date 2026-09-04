"""Testes de fumaça do engine.

Existem por causa de um bug concreto: um import esquecido em `engine/loop.py`
deixou `_build_encounters` com um `NameError`, e nenhum dos 197 testes pegou —
porque nenhum deles executava o loop do jogo. O erro só apareceu ao rodar o
AutoTester à mão.

Estes testes não medem balanceamento nem regra de negócio. Eles verificam que
cada módulo importa e que os caminhos principais do engine executam de ponta a
ponta, que é a classe de defeito que estava passando batido.
"""

from __future__ import annotations

import importlib
import pkgutil
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import src  # noqa: E402
from src.content.factories.archetypes import spawn_by_role  # noqa: E402
from src.content.factories.monsters import (  # noqa: E402
    create_boss_for_level,
    generate_monsters_for_level,
)
from src.engine import loop  # noqa: E402
from src.engine.map import MapOfGame  # noqa: E402
from src.entities.heroes import Warrior  # noqa: E402


def all_modules() -> list[str]:
    """Todo módulo sob `src/`, para o teste de import."""
    return [
        name
        for _, name, _ in pkgutil.walk_packages(src.__path__, prefix="src.")
        if not name.rsplit(".", 1)[-1].startswith("_")
    ]


@pytest.mark.parametrize("modulo", all_modules())
def test_todo_modulo_importa(modulo):
    """Um import quebrado em módulo sem teste é invisível até alguém jogar."""
    importlib.import_module(modulo)


class TestGeracaoDeAndar:
    """Os caminhos do engine que só o jogo real percorria."""

    @pytest.mark.parametrize("andar", [1, 3, 4, 5, 9, 10, 15, 20])
    def test_monta_encontros_do_andar(self, andar):
        monstros = generate_monsters_for_level(andar, andar)
        grupos = loop._build_encounters(monstros, andar)

        assert grupos, f"Andar {andar} não gerou encontro nenhum."
        assert sum(len(g) for g in grupos) == len(monstros), (
            "Agrupar não pode perder nem duplicar monstro."
        )
        for grupo in grupos:
            marcos = [m for m in grupo if getattr(m, "is_boss", False)]
            if marcos:
                assert len(grupo) == 1, "Elite e chefe entram sozinhos no encontro."

    def test_grupos_crescem_com_a_profundidade(self):
        raso = max(len(g) for g in loop._build_encounters(generate_monsters_for_level(1, 1), 1))
        fundo = max(len(g) for g in loop._build_encounters(generate_monsters_for_level(20, 20), 20))
        assert raso == 1, "Os primeiros andares ensinam com inimigos isolados."
        assert fundo > raso

    def test_mapa_guarda_encontro_e_devolve_na_colisao(self):
        game_map = MapOfGame(height=12, width=25)
        game_map.generate_map(percent_of_walls=0.05)
        game_map.place_player()
        game_map.place_exit()
        grupo = [spawn_by_role("trash", 3), spawn_by_role("bruiser", 3)]
        game_map.place_enemy(grupo)

        estado = game_map.get_map_state()
        recarregado = MapOfGame(height=12, width=25)
        recarregado.load_map_state(estado)

        assert len(recarregado.enemies_pos) == 1
        [carregado] = recarregado.enemies_pos.values()
        assert len(carregado) == len(grupo)
        assert [m.role for m in carregado] == [m.role for m in grupo], (
            "O papel do monstro precisa sobreviver ao save."
        )


class TestPosCombate:
    """Recompensa por encontro, não por monstro."""

    def test_encontro_maior_paga_mais(self):
        def xp_de(quantidade):
            heroi = Warrior("Teste")
            heroi.set_level(5)
            monstros = [spawn_by_role("trash", 5) for _ in range(quantidade)]
            xp, venceu, _, _, moedas, _ = loop.process_post_battle(heroi, monstros)
            assert venceu
            return xp, moedas

        xp_um, moedas_um = xp_de(1)
        xp_tres, moedas_tres = xp_de(3)
        assert xp_tres > xp_um
        assert moedas_tres > moedas_um

    def test_chefe_paga_mais_que_monstro_comum(self):
        heroi = Warrior("Teste")
        heroi.set_level(8)
        xp_comum, *_ = loop.process_post_battle(heroi, [spawn_by_role("trash", 8)])

        heroi = Warrior("Teste")
        heroi.set_level(8)
        xp_chefe, *_ = loop.process_post_battle(heroi, [create_boss_for_level(8)])

        assert xp_chefe > xp_comum

    def test_derrota_nao_zera_a_recompensa_mas_reduz(self):
        vencedor = Warrior("Teste")
        vencedor.set_level(5)
        xp_vitoria, *_ = loop.process_post_battle(vencedor, [spawn_by_role("bruiser", 5)])

        derrotado = Warrior("Teste")
        derrotado.set_level(5)
        derrotado.set_isalive(False)
        xp_derrota, venceu, *_ = loop.process_post_battle(derrotado, [spawn_by_role("bruiser", 5)])

        assert not venceu
        assert 0 < xp_derrota < xp_vitoria

    def test_vitoria_nao_cura_o_heroi(self):
        # `rest()` depois de cada vitória era o que zerava o atrito da run.
        heroi = Warrior("Teste")
        heroi.set_level(5)
        heroi.take_damage(heroi.base_hp // 2)
        ferido = heroi.get_hp()
        loop.process_post_battle(heroi, [spawn_by_role("trash", 5)])
        assert heroi.get_hp() <= ferido or heroi.get_level() > 5


class TestSaveComEquipamento:
    """O bug que impedia carregar qualquer save com item equipado."""

    def test_equipar_item_fora_do_inventario_nao_levanta_erro(self):
        from src.content.items import get_all_items

        heroi = Warrior("Teste")
        arma = next(
            i for i in get_all_items().values()
            if getattr(i, "slot", None) == "Weapon"
            and (not getattr(i, "classes", None) or "Warrior" in i.classes)
        )
        # `load_game` chama `equip` com o item já retirado do inventário.
        assert heroi.equip(arma) == arma.name
        assert heroi.equipment["Weapon"] is arma

    def test_round_trip_de_save_com_equipamento(self, tmp_path, monkeypatch):
        from src.content.items import ALL_ITEMS, get_all_items
        from src.entities.heroes import Mage, Rogue
        from src.storage import save_manager

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
        monkeypatch.setattr(
            save_manager, "get_slot_file", lambda slot: str(tmp_path / f"slot_{slot}.json")
        )

        heroi = Warrior("Equipado")
        heroi.set_level(6)
        arma = next(
            i for i in get_all_items().values()
            if getattr(i, "slot", None) == "Weapon"
            and (not getattr(i, "classes", None) or "Warrior" in i.classes)
        )
        heroi.add_item_to_inventory(arma)
        heroi.equip(arma)

        assert save_manager.save_game(heroi, 3, None, slot=1)["success"]
        carregado, andar, _ = save_manager.load_game(
            item_registry=ALL_ITEMS,
            player_factory={"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue},
            slot=1,
        )

        assert carregado is not None, "Save com equipamento não carregou."
        assert carregado.get_level() == 6
        assert andar == 3
        assert carregado.equipment["Weapon"] is not None
