ToJ/
├── main.py                        # Entry point (Bootstrap: carrega dependências e inicia)
├── README.md
├── ARCHITECTURE.md                # Mapa do projeto
├── .cursorrules                   # Regras de arquitetura e restrições de import
└── src/                           # CÓDIGO FONTE DO JOGO
    ├── __init__.py
    │
    ├── shared/                    # TIPOS E DADOS COMPARTILHADOS (Sem dependências)
    │   ├── __init__.py
    │   └── types.py               # TypedDicts, Dataclasses (CombatResult, EntityStats)
    │
    ├── engine/                    # ORQUESTRADOR CENTRAL
    │   ├── __init__.py
    │   ├── loop.py                # O loop principal infinito (While True)
    │   ├── world.py               # Lógica de mapa, colisão e movimentação
    │   └── events.py              # Sistema de Pub/Sub (EventBus e GameEvents)
    │
    ├── entities/                  # ESTADO PURO E ENCAPSULAMENTO
    │   ├── __init__.py
    │   ├── base.py                # Classe mãe (Entity com HP, MP, take_damage)
    │   ├── heroes.py              # Classes filhas (Warrior, Mage, Rogue)
    │   └── monsters.py            # Classes filhas (Inimigos instanciados)
    │
    ├── storage/                   # PERSISTÊNCIA DE DADOS
    │   ├── __init__.py
    │   └── save_game.py           # Leitura/Escrita do savegame.json
    │
    ├── mechanics/                 # REGRAS DE NEGÓCIO E MATEMÁTICA
    │   ├── __init__.py
    │   ├── combat.py              # Fórmulas de dano, esquiva e crítico
    │   └── progression.py         # Curva de XP e level up
    │
    ├── content/                   # DADOS E FÁBRICAS (Data-Driven)
    │   ├── __init__.py
    │   ├── equipment.py           # Definição de armas, armaduras, poções
    │   ├── economy.py             # Preços, lógica da loja e inflação
    │   └── factories/             # Namespace de geradores
    │       ├── __init__.py
    │       ├── monsters.py        # Gera instâncias de inimigos com stats escalados
    │       ├── loot.py            # Dropa itens com rolagens de raridade
    │       └── dungeons.py        # Gera masmorras e modificadores
    │
    └── ui/                        # APRESENTAÇÃO E INTERAÇÃO (Terminal)
        ├── __init__.py
        ├── renderer.py            # Único local que importa o `rich` (Tabelas, Painéis)
        ├── screens.py             # Telas de estado (Game Over, Inventário, Combate)
        └── prompts.py             # Único local com `input()` e captura de teclado