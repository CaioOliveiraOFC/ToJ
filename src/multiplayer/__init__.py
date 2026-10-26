"""A camada multiplayer: versão, protocolo e servidor autoritativo da Arena.

Não tem regra de combate. O duelo é o de `src/mechanics/pvp_duel.py`, o
gladiador nasce pelo caminho canônico de `src/engine/arena_setup.py`, e esta
camada só faz três coisas:

- exige que cliente e servidor sejam a MESMA versão (`manifesto`, `compatibilidade`);
- transporta ações, observações e resultados (`protocolo`), sem conhecer a rede;
- conduz partidas no servidor, que valida o gladiador e a ação e roda o motor
  (`servidor`, `gladiadores`).

O contrato está em `GAMEPLAY_CONTRACTS.md`, seção "Multiplayer".
"""
