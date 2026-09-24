"""As quatro políticas da auditoria precisam medir coisas diferentes.

Uma política que diz evitar combate e luta do mesmo jeito não é um bot ruim: é
um instrumento que responde a pergunta errada. Estes testes provam o
comportamento, não a qualidade da jogada.
"""

from __future__ import annotations

import random

import pytest

from src.content.factories.monsters import create_monster
from src.engine.map import MapOfGame
from tools import audit_new_loop as audit


def _mapa_aberto(altura: int = 9, largura: int = 13) -> MapOfGame:
    """Uma sala retangular sem paredes internas, com jogador num canto e saída noutro."""
    game_map = MapOfGame(height=altura, width=largura)
    game_map.grid = [
        ["#" if (y in (0, altura - 1) or x in (0, largura - 1)) else "." for x in range(largura)]
        for y in range(altura)
    ]
    game_map.player_pos = {"y": 1, "x": 1}
    game_map.exit_pos = {"y": altura - 2, "x": largura - 2}
    game_map.grid[altura - 2][largura - 2] = "X"
    return game_map


def _estado(game_map, hero=None, andar: int = 1):
    from src.sim.harness import make_hero
    from src.sim.policies import get_policy
    from src.sim.toggles import Toggles

    if hero is None:
        hero = make_hero("Warrior", 20, "expected")
        hero.learn_new_skills(show=False)
    return audit.Estado(
        hero=hero,
        game_map=game_map,
        acc=audit.Acumulador(),
        rng=random.Random(7),
        decide=get_policy("smart"),
        toggles=Toggles(),
        andar=andar,
        essencia=1.0,
        posicao=(game_map.player_pos["y"], game_map.player_pos["x"]),
    )


class TestPoliticasSeComportamDiferente:
    def test_rush_nao_luta_quando_existe_rota_livre(self):
        # Monstros longe da linha reta entre jogador e saída: existe caminho de
        # zero combates, e o Rush precisa achá-lo.
        game_map = _mapa_aberto()
        for casa in ((1, 6), (2, 6), (3, 6)):
            game_map.enemies_pos[casa] = create_monster("Alvo", 1, "trash")
        estado = _estado(game_map)

        assert audit._politica_rush(estado) is True
        assert estado.acc.combates == 0, "o Rush lutou tendo rota livre disponível"
        assert estado.posicao == (game_map.exit_pos["y"], game_map.exit_pos["x"])

    def test_rush_luta_quando_o_corredor_obriga(self):
        # Parede inteira com uma única fresta, e um monstro na fresta. Aqui o
        # Rush TEM de lutar: "evita combate" não é "atravessa parede".
        game_map = _mapa_aberto()
        for y in range(1, game_map.height - 1):
            game_map.grid[y][6] = "#"
        game_map.grid[4][6] = "."
        game_map.enemies_pos[(4, 6)] = create_monster("Portao", 1, "trash")
        estado = _estado(game_map)

        assert audit._politica_rush(estado) is True
        assert estado.acc.combates == 1

    def test_full_clear_procura_os_monstros(self):
        game_map = _mapa_aberto()
        for casa in ((1, 6), (2, 9), (5, 3)):
            game_map.enemies_pos[casa] = create_monster("Alvo", 1, "trash")
        estado = _estado(game_map)

        assert audit._politica_full_clear(estado) is True
        assert estado.acc.combates == 3, "o Full Clear deixou monstro alcançável para trás"
        assert not game_map.enemies_pos

    def test_economica_nao_limpa_o_andar_por_acidente(self):
        # Com ouro de sobra para a taxa, a Econômica não tem motivo para lutar.
        game_map = _mapa_aberto()
        for casa in ((1, 6), (2, 9), (5, 3)):
            game_map.enemies_pos[casa] = create_monster("Alvo", 1, "trash")
        estado = _estado(game_map)
        estado.hero.earn_coins(100_000)

        assert audit._politica_economica(estado) is True
        assert estado.acc.combates == 0, "a Econômica lutou sem motivo econômico"
        assert len(game_map.enemies_pos) == 3

    def test_economica_luta_quando_nao_pode_pagar_a_saida(self):
        game_map = _mapa_aberto()
        for casa in ((1, 6), (2, 9), (5, 3)):
            game_map.enemies_pos[casa] = create_monster("Alvo", 1, "trash")
        estado = _estado(game_map)
        estado.hero.coins = 0

        assert audit._politica_economica(estado) is True
        assert estado.acc.combates >= 1, "a Econômica não buscou capital sem poder pagar a saída"

    def test_exploradora_vai_atras_das_features(self):
        game_map = _mapa_aberto()
        game_map.features[(1, 9)] = audit.feat.SHOP
        game_map.features[(5, 4)] = audit.feat.FORGE
        estado = _estado(game_map)

        assert audit._politica_exploradora(estado) is True
        assert estado.acc.visitado[audit.feat.SHOP] == 1
        assert estado.acc.visitado[audit.feat.FORGE] == 1

    def test_rush_ignora_as_features(self):
        game_map = _mapa_aberto()
        game_map.features[(1, 9)] = audit.feat.SHOP
        game_map.features[(5, 4)] = audit.feat.FORGE
        estado = _estado(game_map)

        assert audit._politica_rush(estado) is True
        assert sum(estado.acc.visitado.values()) == 0

    def test_extracao_nunca_e_consumida_nesta_auditoria(self):
        # `never_extract`: a casa continua no mapa, como no jogo.
        game_map = _mapa_aberto()
        game_map.features[(1, 9)] = audit.feat.EXTRACTION
        estado = _estado(game_map)

        assert audit._politica_exploradora(estado) is True
        assert game_map.features.get((1, 9)) == audit.feat.EXTRACTION


class TestUsaAsRegrasReais:
    def test_a_auditoria_nao_tem_formula_propria(self):
        # Preço, recompensa, taxa e Essência têm de ser os objetos do jogo, e não
        # cópias. Se alguém reimplementar qualquer um deles aqui, este teste cai.
        from src.content import economy as economia_do_jogo
        from src.content import floor_exit
        from src.sim import harness

        assert audit.exit_fee is economia_do_jogo.exit_fee
        assert audit.pay_interest is economia_do_jogo.pay_interest
        assert audit.use_exit is floor_exit.use_exit
        assert audit.effective_essence is floor_exit.effective_essence
        assert audit._award is harness._award

    def test_o_andar_vem_do_gerador_do_jogo(self):
        from src.engine import loop

        assert audit._setup_dungeon_map is loop._setup_dungeon_map


class TestDeterminismo:
    @pytest.mark.parametrize("politica", audit.POLITICAS)
    def test_a_mesma_seed_reproduz_a_mesma_run(self, politica):
        primeira = audit.rodar_uma("Warrior", politica, 4242, max_andar=6)
        segunda = audit.rodar_uma("Warrior", politica, 4242, max_andar=6)
        for campo in ("andar_alcancado", "nivel_final", "ouro_final"):
            assert getattr(primeira["acc"], campo) == getattr(segunda["acc"], campo)
        assert primeira["acc"].combates == segunda["acc"].combates
        assert primeira["acc"].passos == segunda["acc"].passos

    def test_seeds_diferentes_produzem_runs_diferentes(self):
        uma = audit.rodar_uma("Warrior", "full_clear", 1, max_andar=6)
        outra = audit.rodar_uma("Warrior", "full_clear", 2, max_andar=6)
        assert (uma["acc"].combates, uma["acc"].passos) != (
            outra["acc"].combates,
            outra["acc"].passos,
        )
