"""Fluxo do Ferreiro: aprimorar, engastar e encantar (orquestração UI → content).

A UI não tem preço nem regra. Ela lê o número de `content/economy.py`, chama o
serviço em `content/forge.py` e mostra o resultado — e é por isso que o valor na
tela é o mesmo que o simulador paga.

O Ferreiro não impõe teto nenhum: o jogador pode aprimorar a mesma peça a noite
inteira, se tiver ouro. Quem segura é a conta.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from src.content import forge
from src.content.economy import (
    enchant_cost,
    enhancement_cost,
    reenchant_cost,
    socket_cost,
    unsocket_cost,
)
from src.content.enchantments import MAX_ENCHANTMENTS
from src.ui import screens
from src.ui.prompts import safe_get_key

if TYPE_CHECKING:
    from src.entities.heroes import Player


def run_forge_flow(player: "Player", dungeon_level: int) -> None:
    """Menu do Ferreiro: três serviços e a saída."""
    while True:
        screens.render_forge_main(player.coins, len(player.gems))
        escolha = safe_get_key(valid_keys=["1", "2", "3", "0"])
        if escolha == "0" or escolha is None:
            return
        if escolha == "1":
            _aprimorar(player, dungeon_level)
        elif escolha == "2":
            _gemas(player, dungeon_level)
        elif escolha == "3":
            _encantar(player, dungeon_level)


def _escolher(itens: list, render, *args) -> int | None:
    """Menu numérico sobre uma lista. `None` quando o jogador volta."""
    if not itens:
        return None
    render(*args)
    teclas = [str(i) for i in range(1, len(itens) + 1)] + ["0"]
    escolha = safe_get_key(valid_keys=teclas)
    if not escolha or escolha == "0":
        return None
    return int(escolha) - 1


def _aprimorar(player: "Player", dungeon_level: int) -> None:
    while True:
        pecas = forge.enhanceable(player)
        if not pecas:
            screens.render_forge_empty("Nada equipado para aprimorar.")
            return
        custos = [enhancement_cost(p, dungeon_level) for p in pecas]
        indice = _escolher(pecas, screens.render_forge_enhance_menu, pecas, custos, player.coins)
        if indice is None:
            return
        peca, custo = pecas[indice], custos[indice]
        novo = forge.enhance(player, peca, dungeon_level)
        if novo is None:
            screens.render_forge_denied(custo, player.coins)
        else:
            screens.render_forge_enhanced(peca.display_name, custo)


def _gemas(player: "Player", dungeon_level: int) -> None:
    while True:
        pecas = forge.socketable(player)
        if not pecas:
            screens.render_forge_empty("Nenhuma peça equipada tem socket.")
            return
        indice = _escolher(pecas, screens.render_forge_gem_items, pecas, player.gems)
        if indice is None:
            return
        _gemas_da_peca(player, pecas[indice], dungeon_level)


def _gemas_da_peca(player: "Player", peca, dungeon_level: int) -> None:
    """Sockets de UMA peça: engastar no vazio, retirar do ocupado.

    Socket cheio não aceita engaste. A mecânica sabe substituir, mas usar isso
    aqui seria uma troca de graça e um item mudando sem o jogador decidir o que
    sai. Para trocar, retira-se primeiro — e pagam-se as duas pontas.
    """
    while True:
        preco_engastar = socket_cost(dungeon_level)
        preco_retirar = unsocket_cost(dungeon_level)
        screens.render_forge_sockets(peca, player.gems, preco_engastar, preco_retirar, player.coins)
        teclas = [str(i) for i in range(1, peca.socket_count + 1)] + ["0"]
        escolha = safe_get_key(valid_keys=teclas)
        if not escolha or escolha == "0":
            return
        slot = int(escolha) - 1

        if peca.gems[slot] is not None:
            retirada = forge.unsocket(player, peca, slot, dungeon_level)
            if retirada is None:
                screens.render_forge_denied(preco_retirar, player.coins)
            else:
                screens.render_forge_unsocketed(retirada.display_name, preco_retirar)
            continue

        if not player.gems:
            screens.render_forge_empty("A bolsa de gemas está vazia.")
            continue
        escolhida = _escolher(player.gems, screens.render_forge_gem_bag, player.gems)
        if escolhida is None:
            continue
        gema = player.gems[escolhida]
        if forge.socket(player, peca, gema, slot, dungeon_level):
            screens.render_forge_socketed(gema.display_name, peca.display_name, preco_engastar)
        else:
            screens.render_forge_denied(preco_engastar, player.coins)


def _encantar(player: "Player", dungeon_level: int) -> None:
    while True:
        pecas = forge.enhanceable(player)
        if not pecas:
            screens.render_forge_empty("Nada equipado para encantar.")
            return
        indice = _escolher(pecas, screens.render_forge_enchant_items, pecas, dungeon_level)
        if indice is None:
            return
        _encantar_peca(player, pecas[indice], dungeon_level)


def _encantar_peca(player: "Player", peca, dungeon_level: int) -> None:
    """Camadas de UMA peça: acrescentar a próxima, ou trocar uma existente.

    Reencantar é aposta: sai do mesmo sorteio, não garante efeito diferente nem
    valor maior, e o antigo não volta.
    """
    while True:
        camadas = len(peca.enchantments)
        preco_novo = enchant_cost(dungeon_level, camadas) if camadas < MAX_ENCHANTMENTS else None
        precos_troca = [reenchant_cost(dungeon_level, i) for i in range(camadas)]
        screens.render_forge_enchant_layers(peca, preco_novo, precos_troca, player.coins)

        teclas = [str(i) for i in range(1, camadas + 1)] + ["0"]
        if preco_novo is not None:
            teclas.append("a")
        escolha = safe_get_key(valid_keys=teclas + [t.upper() for t in teclas if t.isalpha()])
        if not escolha or escolha == "0":
            return

        if escolha.lower() == "a":
            novo = forge.enchant(player, peca, dungeon_level)
            if novo is None:
                screens.render_forge_denied(preco_novo or 0, player.coins)
            else:
                screens.render_forge_enchanted(novo.display_name, preco_novo or 0)
            continue

        indice = int(escolha) - 1
        novo = forge.reenchant(player, peca, indice, dungeon_level)
        if novo is None:
            screens.render_forge_denied(precos_troca[indice], player.coins)
        else:
            screens.render_forge_enchanted(novo.display_name, precos_troca[indice])
