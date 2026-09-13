"""Gemas: a segunda dimensão, e a prova de que ela não se mistura com a primeira.

`+N` multiplica a base da própria peça; a gema soma um percentual do atributo do
personagem. Campos diferentes, curvas diferentes, caminhos diferentes — e é isso
que estes testes travam, porque é o que permite Encantamentos entrarem depois
sem ninguém saber de onde veio cada ponto de poder.
"""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.gems import GEM_TYPES, Gem, create_gem, random_gem  # noqa: E402
from src.content.items import Item  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.shared.formulas import enhancement_multiplier, gem_percent  # noqa: E402


def _item(nome: str, **kw) -> Item:
    kw.setdefault("slot", "Weapon")
    return Item(item_id=nome, name=nome, description="prova", **kw)


class TestGema:
    def test_os_seis_tipos_cobrem_seis_atributos_distintos(self):
        assert len(set(GEM_TYPES.values())) == len(GEM_TYPES) == 6

    def test_nivel_comeca_em_um(self):
        with pytest.raises(ValueError):
            Gem("Rubi", 0)

    def test_tipo_desconhecido_levanta(self):
        with pytest.raises(ValueError):
            Gem("Quartzo", 5)

    def test_gema_nao_recebe_enhancement(self):
        """O nível da gema já é a progressão dela. `+N` é só de equipamento."""
        gema = create_gem("Rubi", 5)
        assert not hasattr(gema, "enhancement_level")
        assert not hasattr(gema, "increase_enhancement")

    def test_curva_cresce_e_a_margem_diminui(self):
        anterior, margem_anterior = gem_percent(1), None
        for n in (5, 10, 25, 50, 100, 500, 1000):
            atual = gem_percent(n)
            assert atual > anterior
            margem = atual - gem_percent(n - 1)
            if margem_anterior is not None:
                assert margem < margem_anterior
            anterior, margem_anterior = atual, margem

    def test_a_curva_da_gema_nao_e_a_do_rank(self):
        """Sistemas independentes: se um dia compartilharem função, isto grita."""
        assert gem_percent(10) != enhancement_multiplier(10)


class TestSockets:
    def test_item_sem_socket_recusa_gema(self):
        peca = _item("Espada", damage_bonus=10)
        with pytest.raises(ValueError):
            peca.socket(create_gem("Rubi", 5))

    def test_encaixar_ocupa_o_primeiro_livre(self):
        peca = _item("Espada", socket_count=2)
        peca.socket(create_gem("Rubi", 5))
        assert peca.free_socket() == 1

    def test_substituir_devolve_a_pedra_antiga(self):
        peca = _item("Espada", socket_count=1)
        antiga = create_gem("Rubi", 5)
        peca.socket(antiga)
        assert peca.socket(create_gem("Rubi", 30), 0) is antiga

    def test_retirar_esvazia_o_socket(self):
        peca = _item("Espada", socket_count=1)
        gema = create_gem("Rubi", 5)
        peca.socket(gema)
        assert peca.unsocket(0) is gema
        assert peca.gems == [None]

    def test_dois_exemplares_nao_dividem_sockets(self):
        """`copy.copy` é raso: sem lista própria, um Rubi entraria nos dois."""
        definicao = _item("Espada", socket_count=1)
        a, b = definicao.instance(), definicao.instance()
        a.socket(create_gem("Rubi", 5))
        assert b.gems == [None]


class TestPosseNaoDuplicaNemPerde:
    def _heroi_com_peca(self, sockets=1):
        h = Warrior("Prova")
        peca = _item("Espada", damage_bonus=10, socket_count=sockets)
        h.equip(peca)
        return h, peca

    def test_encaixar_tira_da_bolsa(self):
        h, peca = self._heroi_com_peca()
        gema = create_gem("Rubi", 5)
        h.gems.append(gema)
        assert h.socket_gem(peca, gema)
        assert h.gems == []
        assert peca.gems == [gema]

    def test_retirar_devolve_a_bolsa(self):
        h, peca = self._heroi_com_peca()
        gema = create_gem("Rubi", 5)
        h.gems.append(gema)
        h.socket_gem(peca, gema)
        assert h.unsocket_gem(peca, 0) is gema
        assert h.gems == [gema]

    def test_substituir_nao_duplica_nem_perde(self):
        h, peca = self._heroi_com_peca()
        antiga, nova = create_gem("Rubi", 5), create_gem("Rubi", 30)
        h.gems += [antiga, nova]
        h.socket_gem(peca, antiga)
        h.socket_gem(peca, nova, 0)
        # Cada pedra existe uma vez, num lugar só.
        for gema in (antiga, nova):
            assert h.gems.count(gema) + peca.gems.count(gema) == 1
        assert peca.gems == [nova]
        assert h.gems == [antiga]

    def test_item_sem_socket_nao_consome_a_gema(self):
        h = Warrior("Prova")
        peca = _item("Espada", damage_bonus=10)
        gema = create_gem("Rubi", 5)
        h.gems.append(gema)
        assert h.socket_gem(peca, gema) is False
        assert h.gems == [gema]


class TestContribuicao:
    def test_duas_gemas_na_mesma_peca_contribuem(self):
        h = Warrior("Prova")
        h.level = 8
        st, hp = h.base_st, h.base_hp
        peca = _item("Espada", socket_count=2)
        h.equip(peca)
        peca.socket(create_gem("Rubi", 5))
        peca.socket(create_gem("Ônix", 10))
        assert h.base_st > st and h.base_hp > hp
        assert h.equipment_percent("st") == pytest.approx(gem_percent(5))
        assert h.equipment_percent("hp") == pytest.approx(gem_percent(10))

    def test_duas_maos_e_dois_aneis_somam_sem_regra_por_slot(self):
        h = Rogue("Prova")
        h.level = 8
        for posicao, nivel in (("Weapon1", 5), ("Weapon2", 8), ("Ring1", 3), ("Ring2", 4)):
            peca = _item(posicao, slot=h.category_of(posicao), socket_count=1)
            h.equip(peca, posicao)
            peca.socket(create_gem("Rubi", nivel))
        esperado = sum(gem_percent(n) for n in (5, 8, 3, 4))
        assert h.equipment_percent("st") == pytest.approx(esperado)

    def test_retirar_a_gema_devolve_o_atributo(self):
        h = Mage("Prova")
        h.level = 8
        antes = h.base_mg
        peca = _item("Cajado", socket_count=1)
        h.equip(peca)
        peca.socket(create_gem("Safira", 20))
        assert h.base_mg > antes
        h.unsocket_gem(peca, 0)
        assert h.base_mg == antes


class TestRankEGemaNaoSeMisturam:
    def test_cada_um_mexe_no_seu_campo(self):
        """`+N` sobe o dano da peça; a gema sobe a Força. Nenhum toca no outro."""
        h = Warrior("Prova")
        h.level = 8
        peca = _item("Espada", damage_bonus=10, socket_count=1)
        h.equip(peca)

        peca.increase_enhancement(10)
        dano_com_rank, st_com_rank = peca.damage_bonus, h.base_st
        assert dano_com_rank > 10, "o rank não subiu o dano da peça"

        peca.socket(create_gem("Rubi", 5))
        assert peca.damage_bonus == dano_com_rank, "a gema mexeu no dano da peça"
        assert h.base_st > st_com_rank, "a gema não subiu a Força"

    def test_o_rank_nao_escala_a_gema(self):
        peca = _item("Espada", damage_bonus=10, socket_count=1)
        peca.socket(create_gem("Rubi", 5))
        antes = peca.gem_percent("st")
        peca.increase_enhancement(500)
        assert peca.gem_percent("st") == antes


class TestDrop:
    def test_gera_gema_valida_dentro_do_andar(self):
        r = random.Random(7)
        for andar in (1, 5, 30):
            gema = random_gem(andar, r)
            assert gema.gem_type in GEM_TYPES
            assert 1 <= gema.level <= max(1, andar)


class TestSave:
    @pytest.fixture
    def save_isolado(self, tmp_path, monkeypatch):
        from src.storage import save_manager

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
        monkeypatch.setattr(
            save_manager, "get_slot_file", lambda s: str(tmp_path / f"slot_{s}.json")
        )
        return save_manager

    class _Registro:
        def __init__(self, pecas):
            self._pecas = pecas

        def get(self, nome):
            return self._pecas.get(nome)

    FABRICAS = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}

    def test_rank_e_gemas_voltam_exatamente(self, save_isolado):
        registro = self._Registro(
            {"Espada de Ferro": _item("Espada de Ferro", damage_bonus=6, socket_count=2)}
        )
        h = Rogue("Joalheiro")
        peca = registro.get("Espada de Ferro").instance()
        peca.increase_enhancement(17)
        peca.socket(create_gem("Rubi", 8))
        h.equip(peca, position="Weapon1")
        h.gems.append(create_gem("Safira", 3))
        save_isolado.save_game(h, 3, None, slot=1)

        carregado, _, _ = save_isolado.load_game(registro, self.FABRICAS, slot=1)
        arma = carregado.equipment["Weapon1"]
        assert arma.display_name == "Espada de Ferro +17"
        assert arma.gems[0].gem_type == "Rubi" and arma.gems[0].level == 8
        assert arma.gems[1] is None
        assert [(g.gem_type, g.level) for g in carregado.gems] == [("Safira", 3)]

    def test_save_antigo_sem_gemas_carrega(self, save_isolado):
        registro = self._Registro({"Espada de Ferro": _item("Espada de Ferro", damage_bonus=6)})
        h = Warrior("Antigo")
        h.equip(registro.get("Espada de Ferro").instance())
        save_isolado.save_game(h, 3, None, slot=1)

        caminho = Path(save_isolado.get_slot_file(1))
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        dados["equipment"] = {"Weapon": "Espada de Ferro"}
        dados.pop("gems", None)
        caminho.write_text(json.dumps(dados), encoding="utf-8")

        carregado, _, _ = save_isolado.load_game(registro, self.FABRICAS, slot=1)
        assert carregado.equipment["Weapon1"].gems == []
        assert carregado.gems == []
