"""A Chave de Extração: a porta única de tudo que envolve a chave.

Antes desta regra, extrair era grátis, repetível e nem encerrava a run — o laço
principal não tratava o desfecho `"extracted"`, a casa `E` nunca era consumida, e
ir até ela era estritamente dominante sempre que aparecesse. O jogo não tinha
decisão de extração: tinha a sorte de o `E` nascer.

A chave devolve a decisão ao jogador, e ela é o oposto de um serviço: cai de
monstro derrotado e só de lá. Não se compra, não se vende, nenhuma casa a
oferece. Quem quer a saída de emergência precisa ter lutado por ela — e, como
morrer apaga o personagem inteiro, a chave morre junto.

Ponto único, como `content/forge.award_gem` é o ponto único da gema: jogo e
simulador chamam estas funções, e é por isso que a chance medida na simulação é
a chance que o jogador vive.
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.shared.constants import EXTRACTION_KEY_DROP_CHANCE, EXTRACTION_KEY_MAX

if TYPE_CHECKING:
    from src.entities.heroes import Player

# O campo mora no jogador, e não no mapa: a chave atravessa andares, e o mapa do
# andar 7 não tem como saber o que caiu no 4.
CAMPO = "extraction_keys"


def keys_of(player) -> int:
    """Quantas chaves o personagem carrega. Zero ou uma — nunca mais que isso."""
    return max(0, min(EXTRACTION_KEY_MAX, int(getattr(player, CAMPO, 0) or 0)))


def has_key(player) -> bool:
    return keys_of(player) > 0


def award_key(player: "Player", rng=None) -> bool:
    """Rola a chave desta vitória e, se cair, guarda. Devolve se caiu.

    Rolagem SEPARADA da do item e da da gema, como `award_gem`: a mesma vitória
    pode largar os três, e nenhum tira a vez do outro.

    Quem já tem a chave NÃO ROLA. Não é só descartar o resultado depois — é não
    consultar o RNG, porque uma rolagem consumida muda todo o sorteio seguinte da
    run. Quem está com a chave no bolso vive a mesma sequência de quem nunca a
    teve.
    """
    if has_key(player):
        return False
    r = rng if rng is not None else random
    if r.random() >= EXTRACTION_KEY_DROP_CHANCE:
        return False
    setattr(player, CAMPO, keys_of(player) + 1)
    livro = getattr(player, "ledger", None)
    if isinstance(livro, dict):
        livro["extraction_keys_found"] = livro.get("extraction_keys_found", 0) + 1
    return True


def consume_key(player: "Player") -> bool:
    """Gasta a chave. Devolve se havia uma para gastar.

    Quem chama já decidiu extrair. Esta função não pergunta nada sobre a casa,
    sobre o andar nem sobre o estado do herói: ela cobra o preço.
    """
    if not has_key(player):
        return False
    setattr(player, CAMPO, keys_of(player) - 1)
    livro = getattr(player, "ledger", None)
    if isinstance(livro, dict):
        livro["extraction_keys_spent"] = livro.get("extraction_keys_spent", 0) + 1
    return True
