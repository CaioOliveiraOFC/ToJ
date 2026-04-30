🗺️ ARCHITECTURE — Tales of the Journey
Regras Fundamentais

Raiz do código-fonte: src/. Use apenas imports absolutos (ex: from src.shared.types import ...).
Consulte .cursorrules para as restrições completas de import entre camadas.
Comunicação entre engine/ e ui/ é feita exclusivamente via EventBus (src/engine/events.py).

ToJ/
├── main.py                         # Entry point: bootstrap e orquestração do menu
├── README.md
├── ARCHITECTURE.md                 # Este arquivo
├── SPRINTS.md                      # Roadmap de desenvolvimento
├── .cursorrules                    # Contrato de arquitetura (regras de import)
├── .env                            # Variáveis de ambiente (NÃO commitar)
├── savegame.json                   # Estado persistido da última sessão
│
└── src/                            # CÓDIGO FONTE DO JOGO
    ├── __init__.py
    │
    ├── shared/                     # TIPOS COMPARTILHADOS — sem dependências
    │   ├── __init__.py
    │   └── types.py                # TypedDicts e Dataclasses (CombatResult, EntityStats, DTOs)
    │
    ├── engine/                     # ORQUESTRADOR CENTRAL
    │   ├── __init__.py
    │   ├── loop.py                 # Loop principal e motor de combate
    │   ├── map.py                  # Lógica de mapa, colisão e movimentação
    │   ├── game_logic.py           # Criação de personagem e geração de monstros
    │   └── events.py               # Sistema Pub/Sub (EventBus e GameEvents)
    │
    ├── entities/                   # ESTADO PURO E ENCAPSULAMENTO
    │   ├── __init__.py
    │   ├── base.py                 # Classe mãe Entity (HP, MP, take_damage, heal)
    │   ├── heroes.py               # Warrior, Mage, Rogue
    │   └── monsters.py             # Monster e variantes
    │
    ├── storage/                    # PERSISTÊNCIA
    │   ├── __init__.py
    │   └── save_manager.py         # save_game / load_game / check_save_file → savegame.json
    │
    ├── mechanics/                  # REGRAS DE NEGÓCIO
    │   ├── __init__.py
    │   ├── combat.py               # Fórmulas de dano, esquiva e crítico
    │   ├── math_operations.py      # Escalonamento de stats (HP/ST/DF/MG de bosses, curva de XP)
    │   └── progression.py         # Level up e progressão de atributos
    │
    ├── content/                    # DADOS E FÁBRICAS
    │   ├── __init__.py
    │   ├── items.py                # Classes base: Item, Weapon, Armor, Potion
    │   ├── equipment.py            # Definições de armas e armaduras
    │   ├── economy.py              # Preços e lógica da loja
    │   └── factories/
    │       ├── __init__.py
    │       ├── monsters.py         # generate_monsters_for_level / create_monster
    │       ├── loot.py             # Drop de itens com rolagem de raridade
    │       └── dungeons.py         # Geração de masmorras e modificadores
    │
    └── ui/                         # APRESENTAÇÃO — único local com rich / print / input
        ├── __init__.py
        ├── renderer.py             # Único local que importa rich (Tabelas, Painéis)
        ├── screens.py              # Telas de estado (Game Over, Inventário, Combate)
        ├── prompts.py              # Único local com input() e captura de teclado
        ├── toj_menu.py             # Menu principal, splash screen, game over screen
        ├── utils.py                # clear_screen() multiplataforma
        └── auto_test.py            # AutoTester com BFS para QA automatizado

Fluxo de Dependências (permitido)
ui/ ←── engine/ ←── mechanics/ ←── entities/
                         ↑               ↑
                     content/        shared/
                         ↑
                      storage/
Todas as camadas podem importar de shared/. Nenhuma outra importação cruzada é permitida.