"""Testes de fumaça do engine.

Existem por causa de um bug concreto: um import esquecido em `engine/loop.py`
deixou a montagem de andar com um `NameError`, e nenhum dos 197 testes pegou —
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
    def test_cada_monstro_do_andar_ganha_a_propria_casa(self, andar):
        """O andar tem vários inimigos; cada um é uma batalha própria."""
        monstros = generate_monsters_for_level(andar, andar)
        game_map = MapOfGame(height=20, width=40)
        game_map.generate_map(percent_of_walls=0.05)
        game_map.place_player()
        game_map.place_exit()
        for monstro in monstros:
            game_map.place_enemy(monstro)

        assert len(game_map.enemies_pos) == len(monstros), (
            "Nenhum monstro pode ser perdido nem dividir casa com outro."
        )
        for ocupante in game_map.enemies_pos.values():
            assert not isinstance(ocupante, list), "Uma casa guarda UM monstro."

    def test_a_casa_recusa_um_grupo(self):
        """A porta por onde o encontro composto voltaria."""
        game_map = MapOfGame(height=12, width=25)
        game_map.generate_map(percent_of_walls=0.05)
        game_map.place_player()
        game_map.place_exit()
        with pytest.raises(ValueError):
            game_map.place_enemy([spawn_by_role("trash", 3), spawn_by_role("bruiser", 3)])

    def test_mapa_guarda_o_monstro_e_devolve_na_colisao(self):
        game_map = MapOfGame(height=12, width=25)
        game_map.generate_map(percent_of_walls=0.05)
        game_map.place_player()
        game_map.place_exit()
        monstro = spawn_by_role("trash", 3)
        game_map.place_enemy(monstro)

        estado = game_map.get_map_state()
        recarregado = MapOfGame(height=12, width=25)
        recarregado.load_map_state(estado)

        assert len(recarregado.enemies_pos) == 1
        [carregado] = recarregado.enemies_pos.values()
        assert carregado.role == monstro.role, "O papel do monstro precisa sobreviver ao save."

    def test_save_da_fase_de_grupos_migra_para_casas_separadas(self):
        """Save antigo com `[A, B, C]` numa casa: ninguém é apagado."""
        game_map = MapOfGame(height=14, width=28)
        game_map.generate_map(percent_of_walls=0.05)
        game_map.place_player()
        game_map.place_exit()
        game_map.place_enemy(spawn_by_role("trash", 3))
        estado = game_map.get_map_state()

        casa = next(iter(estado["enemies_pos"]))
        estado["enemies_pos"][casa] = [
            {"nick_name": "A", "level": 3, "role": "trash"},
            {"nick_name": "B", "level": 3, "role": "bruiser"},
            {"nick_name": "C", "level": 3, "role": "tank"},
        ]

        migrado = MapOfGame(height=14, width=28)
        migrado.load_map_state(estado)

        assert len(migrado.enemies_pos) == 3, "Nenhum monstro do save pode sumir."
        assert {m.nick_name for m in migrado.enemies_pos.values()} == {"A", "B", "C"}
        y, x = map(int, casa.split(","))
        assert migrado.enemies_pos[(y, x)].nick_name == "A", "O primeiro fica onde estava."

        # Determinística: o mesmo save recarregado põe todo mundo nas mesmas casas.
        outro = MapOfGame(height=14, width=28)
        outro.load_map_state(estado)
        assert sorted(outro.enemies_pos) == sorted(migrado.enemies_pos)

    def test_save_novo_nao_grava_array_de_encontro(self):
        game_map = MapOfGame(height=12, width=25)
        game_map.generate_map(percent_of_walls=0.05)
        game_map.place_player()
        game_map.place_exit()
        game_map.place_enemy(spawn_by_role("trash", 3))
        for entrada in game_map.get_map_state()["enemies_pos"].values():
            assert isinstance(entrada, dict), "Uma casa, um monstro, no disco também."


class TestPosCombate:
    """Recompensa do monstro derrotado. A batalha é 1x1."""

    def test_recompensa_recusa_mais_de_um_monstro(self):
        heroi = Warrior("Teste")
        heroi.set_level(5)
        with pytest.raises(ValueError):
            loop.process_post_battle(heroi, [spawn_by_role("trash", 5) for _ in range(3)])

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
            i
            for i in get_all_items().values()
            if getattr(i, "slot", None) == "Weapon"
            and (not getattr(i, "classes", None) or "Warrior" in i.classes)
        )
        # `load_game` chama `equip` com o item já retirado do inventário.
        assert heroi.equip(arma) == arma.name
        assert heroi.equipment["Weapon1"] is arma

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
            i
            for i in get_all_items().values()
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
        assert carregado.equipment["Weapon1"] is not None
