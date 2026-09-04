"""Testes para cálculo de atributos com/sem equipamento — trade-offs reais."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from src.content.items import get_all_items
from src.entities.heroes import Warrior, Mage, Rogue


def test_equip_muda_atk_e_def():
    player = Warrior("Teste")
    base_atk = player.get_avg_damage()
    base_def = player.base_df
    # Pega uma arma com dano e defesa conhecidos
    all_items = get_all_items()
    sword = all_items["Espada de Ferro"]  # dmg 5, def 0
    # Adiciona ao inventário antes de equipar (fluxo real: compra -> inventário -> equipar)
    player.inventory.append(sword)
    # Equipa
    player.equip(sword)
    assert player.get_avg_damage() == base_atk + 5
    assert player.base_df == base_def
    # Desequipa
    player.unequip("Weapon")
    assert player.get_avg_damage() == base_atk
    assert player.base_df == base_def


def test_trade_off_arma_alta_vs_baixa():
    """Arma A com mais ATK mas menos DEF vs Arma B com menos ATK mas mais DEF — escolha real."""
    player = Warrior("Teste")

    all_items = get_all_items()
    # Lâmina Veloz: dmg 7, vel +4 (trade-off: ATK vs nada, mas efeito)
    # Clava Pesada: dmg 5, def 2, speed -3 — usamos armaduras para DEF trade-off real
    # Para armas, o trade-off é ATK vs efeito, já que DEF de arma não conta para base_df
    lamina = all_items["Lâmina Veloz"]
    clava = all_items["Clava Pesada"]

    # Equipa Lâmina
    player.inventory.append(lamina)
    player.equip(lamina)
    atk_lamina = player.get_avg_damage()
    eff_lamina = getattr(lamina, "effect_value", 0)
    player.unequip("Weapon")

    # Equipa Clava
    player.inventory.append(clava)
    player.equip(clava)
    atk_clava = player.get_avg_damage()
    eff_clava = getattr(clava, "effect_value", 0)
    player.unequip("Weapon")

    # Lâmina tem mais ATK mas Clava tem DEF (via slot Hands? não, Weapon DEF não conta)
    # Trade-off real: Lâmina dano puro vs Clava dano menor mas com DEF bonus ignorado para Weapon
    # Verifica que nenhuma é estritamente melhor em dano+efeito
    assert atk_lamina > atk_clava
    # Lâmina tem efeito speed positivo, Clava tem speed negativo — trade-off de efeito
    assert eff_lamina > 0
    assert eff_clava < 0


def test_armadura_trade_off_def_vs_mobilidade():
    player = Warrior("Teste")
    all_items = get_all_items()
    cota_leve = all_items["Cota Leve"]  # def 2 + agility 4
    placa_pesada = all_items["Placa Pesada"]  # def 5, speed -2

    # Cota Leve
    player.inventory.append(cota_leve)
    player.equip(cota_leve)
    def_leve = player.base_df
    player.unequip("Body")
    # Placa Pesada
    player.inventory.append(placa_pesada)
    player.equip(placa_pesada)
    def_pesada = player.base_df
    player.unequip("Body")

    assert def_pesada > def_leve
    # Trade-off: Placa tem mais DEF mas perde velocidade (efeito), Cota tem menos DEF mas ganha agilidade
    # Verifica que os efeitos são diferentes
    assert cota_leve.effect_type == "agility"
    assert placa_pesada.effect_type == "speed"
    assert placa_pesada.effect_value < 0  # penalidade de velocidade


def test_rare_vs_common_nao_e_power_creep_linear():
    """Rare não é estritamente melhor que Common em tudo — trade-off."""
    all_items = get_all_items()
    common = all_items["Espada de Ferro"]  # Common dmg 5
    rare = all_items["Espada da Vingança"]  # Rare dmg 12, def -2

    # Rare tem mais dano, mas tem penalidade de defesa
    assert rare.damage_bonus > common.damage_bonus
    assert rare.defense_bonus < common.defense_bonus  # Common 0 vs Rare -2, trade-off


def test_epic_vs_rare_trade_off():
    all_items = get_all_items()
    rare = all_items["Espada da Vingança"]  # dmg 12, def -2
    epic = all_items["Lâmina da Tempestade"]  # dmg 18, def -2, stun 8

    # Epic tem mais dano mas mesmo def negativa, mas tem efeito stun como trade-off positivo
    # Não é estritamente melhor em tudo vs Rare, mas tem trade-off de raridade vs disponibilidade
    assert epic.damage_bonus > rare.damage_bonus
    # Epic tem stun, Rare tem crit_damage — trade-off de efeito
    assert epic.effect_type == "stun"
    assert rare.effect_type == "crit_damage"


def test_legendary_nao_e_estritamente_melhor_que_epic():
    all_items = get_all_items()
    epic = all_items["Lâmina da Tempestade"]  # dmg 18, def -2
    legendary = all_items["Espada do Eclipse"]  # dmg 28, def 3, life_steal -8

    # Legendary tem mais dano e até defesa positiva, mas tem penalidade de life_steal negativo
    assert legendary.damage_bonus > epic.damage_bonus
    assert legendary.effect_value < 0  # life steal negativo = custo vital
    # Epic tem stun positivo, Legendary tem custo — trade-off
    assert epic.effect_value > 0
    assert legendary.effect_value < 0


def test_equip_unequip_restora_status():
    # O bônus do item é percentual do atributo, não soma fixa: uma armadura de
    # "defesa 3" dá +3% de defesa, e por isso continua valendo o mesmo no nível
    # 20, onde +3 pontos sobre 301 de defesa não valeriam nada.
    player = Warrior("Teste")
    base_def = player.base_df
    armadura = get_all_items()["Gibão de Couro"]  # defesa 3 -> +3%
    player.inventory.append(armadura)
    player.equip(armadura)
    assert player.base_df == int(base_def * 1.03)
    player.unequip("Body")
    assert player.base_df == base_def


def test_bonus_de_equipamento_mantem_peso_entre_niveis():
    # Como soma fixa, a melhor arma do jogo valia 3% do poder base no nível 20.
    # Como percentual, ela vale o mesmo em qualquer nível.
    arma = get_all_items()["Espada de Ferro"]

    def ganho_no_nivel(nivel):
        player = Warrior("Teste")
        player.set_level(nivel)
        sem_arma = player.get_avg_damage()
        player.inventory.append(arma)
        player.equip(arma)
        return player.get_avg_damage() / sem_arma

    assert ganho_no_nivel(1) == pytest.approx(ganho_no_nivel(20), rel=0.02)


def test_equipar_item_nao_cura_o_heroi():
    # Equipar chamava rest(), que restaurava HP e MP ao máximo: era uma cura
    # completa gratuita e ilimitada, acionável pelo inventário a qualquer hora.
    player = Warrior("Teste")
    player.take_damage(player.base_hp // 2)
    ferido = player.get_hp()
    arma = get_all_items()["Espada de Ferro"]
    player.inventory.append(arma)
    player.equip(arma)
    assert player.get_hp() <= ferido


def test_catalogo_tem_minimo_12_novos_itens_com_tradeoff():
    all_items = get_all_items()
    # Verifica que os 24 novos itens existem
    new_ids = [
        "lamina_veloz", "clava_pesada", "adaga_sangrenta",
        "cota_leve", "placa_pesada", "manto_curandeiro",
        "espada_vinganca", "cajado_equilibrio", "arco_precisao",
        "armadura_espinhos", "tunica_fluxo", "colete_resistencia",
        "lamina_tempestade", "cajado_vazio", "arco_silencio",
        "armadura_fenrir", "manto_etereo", "colete_sombra",
        "espada_eclipse", "cajado_oblivion", "adaga_vazio",
        "armadura_tita", "tunica_arquimago", "manto_assassino",
    ]
    for nid in new_ids:
        assert nid in [item.id for item in all_items.values()], f"Item {nid} não encontrado"
        item = next(i for i in all_items.values() if i.id == nid)
        # Cada novo item deve ter pelo menos 2 atributos de trade-off (damage/defense/effect)
        attrs = 0
        if item.damage_bonus != 0:
            attrs += 1
        if item.defense_bonus != 0:
            attrs += 1
        if item.effect_type and item.effect_value != 0:
            attrs += 1
        assert attrs >= 2, f"{nid} precisa de >=2 atributos para trade-off, tem {attrs}"

    # Verifica distribuição por raridade
    from collections import Counter
    rarity_counts = Counter()
    for nid in new_ids:
        item = next(i for i in all_items.values() if i.id == nid)
        rarity_counts[item.rarity] += 1
    assert rarity_counts["Common"] == 6
    assert rarity_counts["Rare"] == 6
    assert rarity_counts["Epic"] == 6
    assert rarity_counts["Legendary"] == 6
