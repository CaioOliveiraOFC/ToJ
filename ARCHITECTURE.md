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
├── tests/                          # TESTES AUTOMATIZADOS
│   └── auto_test.py                # AutoTester com BFS para QA automatizado
│
└── src/                            # CÓDIGO FONTE DO JOGO
    ├── __init__.py
    │
    ├── shared/                     # TIPOS COMPARTILHADOS — sem dependências
    │   ├── __init__.py
    │   ├── types.py                # TypedDicts e Dataclasses (CombatResult, EntityStats, DTOs)
    │   ├── constants.py            # Constantes globais do jogo
    │   └── combat_topics.py        # Tópicos de eventos de combate (EventBus)
    │
    ├── data/                       # DADOS ESTÁTICOS (JSON e loaders)
    │   ├── __init__.py
    │   ├── loader.py               # Utilitários para carregar JSON (monsters, items)
    │   ├── items.json              # Definições de itens em JSON
    │   └── monsters.json           # Definições de monstros em JSON
    │
    ├── engine/                     # ORQUESTRADOR CENTRAL
    │   ├── __init__.py
    │   ├── bootstrap.py            # Inicialização do jogo e menu principal
    │   ├── loop.py                 # Loop principal e motor de combate
    │   ├── map.py                  # Lógica de mapa, colisão e movimentação
    │   ├── game_logic.py           # Criação de personagem e geração de monstros
    │   ├── events.py               # Sistema Pub/Sub (EventBus e GameEvents)
    │   └── ui_events.py            # Utilitários para emitir eventos de UI via EventBus
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
    │   └── math_operations.py      # Escalonamento de stats (HP/ST/DF/MG de bosses, curva de XP)
    │
    ├── content/                    # DADOS E FÁBRICAS
    │   ├── __init__.py
    │   ├── items.py                # Classes base: Item, Weapon, Armor, Potion
    │   ├── armor.py                # Definições de armaduras (Helmet, Body, Legs, Shoes)
    │   ├── skills.py               # Definições de habilidades (Skill e variantes por classe)
    │   ├── shop.py                 # Lógica da loja (preços, compra, venda)
    │   └── factories/
    │       ├── __init__.py
    │       ├── monsters.py         # generate_monsters_for_level / create_monster / create_boss_for_level
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
        ├── combat_event_handlers.py # Handlers de eventos de combate (inscrições no EventBus)
        ├── inventory_flow.py       # Fluxo de interação do inventário
        └── shop_flow.py            # Fluxo de interação da loja

Fluxo de Dependências (permitido)
ui/ ←── engine/ ←── mechanics/ ←── entities/
                         ↑               ↑
                     content/        shared/
                         ↑
                      storage/
                         ↑
                       data/

Todas as camadas podem importar de shared/. Nenhuma outra importação cruzada é permitida.

Notas Importantes:
- data/ é uma camada de suporte que fornece loaders para JSON (não tem dependências de lógica)
- engine/ui_events.py é um utilitário para emitir eventos sem violar regras de importação
- content/shop.py contém a lógica de preços e transações (anteriormente chamado economy.py)
- content/skills.py define as habilidades disponíveis para cada classe
- tests/ fica na raiz do projeto para facilitar execução de testes automatizados
