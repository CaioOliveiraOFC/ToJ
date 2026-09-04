# ARCHITECTURE — Tales of the Journey

## Regras Fundamentais

1. Raiz do código-fonte: `src/`. Use apenas imports absolutos (ex: `from src.shared.types import ...`).
2. Comunicação entre `engine/` e `ui/` é feita **exclusivamente via EventBus** (`src/engine/events.py`).
   - Exceções documentadas: `screens.render_*`, `clear_screen`, `safe_get_key` (funções de renderização e input blocking)
3. `entities/` não importa de `content/`: Inversão de dependência — entidades não conhecem dados.
4. Nada de `print()` fora de `ui/`: Toda saída passa pelo renderer Rich.
5. Dados em JSON, código limpo, sem hardcoded: Tudo data-driven.
   - A fronteira: **fórmula é código, valor é dado**. Um multiplicador de arquétipo, o nome de um monstro ou o custo de uma skill mudam sem que a regra mude — vão para o JSON. Números que governam balanceamento e não cabem no JSON ficam em `shared/constants.py`, com nome.
6. `safe_get_key()` é o único ponto de entrada de teclado: Consistência multiplataforma.

> As seis regras acima são verificadas por `tests/test_architecture.py`. Regra que
> só existe em Markdown é regra que ninguém checa.

---

## Estrutura do Projeto

```
ToJ/
├── main.py                         # Entry point: bootstrap e orquestração do menu
├── README.md
├── ARCHITECTURE.md                 # Este arquivo
├── BALANCE_REPORT.md               # Modelo de balanceamento e números medidos
├── requirements.txt                # Dependências de execução
├── pyproject.toml                  # Configuração do projeto (ruff, mypy, pytest)
│
├── tests/                          # TESTES AUTOMATIZADOS
│   ├── __init__.py
│   ├── auto_test.py                # AutoTester BFS para QA (mock de saves)
│   ├── test_architecture.py        # As seis regras desta página, verificadas
│   ├── test_combat.py              # Testes de dano, XMULT cap, defesa, crítico
│   ├── test_math_operations.py     # Testes de XP, moedas, multiplicador
│   ├── test_new_systems.py         # Testes de cooldown, damage_reduction, stun
│   └── balance/                    # Invariantes de balanceamento (simulação)
│
├── docs/                           # Documentação adicional
│   └── GUIDE_PASSIVES.md           # Guia para criar novas passivas
│
└── src/                            # CÓDIGO FONTE DO JOGO
    ├── __init__.py
    │
    ├── shared/                     # TIPOS COMPARTILHADOS — sem dependências
    │   ├── __init__.py
    │   ├── types.py                # TypedDicts e Dataclasses (CombatResult, EntityStats, DTOs)
    │   ├── constants.py            # Constantes globais do jogo
    │   ├── formulas.py             # Curvas de crescimento e de XP (fonte única)
    │   ├── effects.py              # Tabela de buffs, status e modificadores de combate
    │   ├── registries.py           # Injeção de dependência entre camadas
    │   └── combat_topics.py        # Tópicos de eventos do EventBus (combat.*, ui.*, system.*)
    │
    ├── data/                       # DADOS ESTÁTICOS (JSON e loaders)
    │   ├── __init__.py
    │   ├── loader.py               # Utilitários para carregar JSON
    │   ├── items.json              # 159 itens (armas, armaduras, 14 consumíveis)
    │   ├── passives.json           # 29 passivas em 4 raridades
    │   ├── skills.json             # 41 skills das três classes
    │   └── monsters.json           # Arquétipos, orçamento por papel e densidade do andar
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
    │   ├── heroes.py               # Warrior, Mage, Rogue (Player)
    │   └── monsters.py             # Monster e variantes
    │
    ├── storage/                    # PERSISTÊNCIA
    │   ├── __init__.py
    │   └── save_manager.py         # save_game / load_game → saves/slot_N.json (10 slots)
    │
    ├── mechanics/                  # REGRAS DE NEGÓCIO
    │   ├── __init__.py
    │   ├── combat.py               # Fórmulas de dano, acerto, crítico, status
    │   ├── battle.py               # Laço de batalha puro (jogo e simulação usam este)
    │   ├── monster_ai.py           # Decisão de turno do monstro
    │   └── math_operations.py      # Recompensas e multiplicador de essência

    ├── sim/                        # SIMULAÇÃO HEADLESS (balanceamento)
    │   ├── __init__.py
    │   ├── harness.py              # simulate() e simulate_run()
    │   ├── policies.py             # Políticas do bot (greedy, smart, random)
    │   ├── encounters.py           # Catálogo de encontros nomeados
    │   ├── loadouts.py             # Equipamento típico por nível
    │   ├── metrics.py              # Agregação e intervalo de confiança
    │   └── runner.py               # CLI de desenvolvimento
    │
    ├── content/                    # DADOS E FÁBRICAS
    │   ├── __init__.py
    │   ├── items.py                # Classes: Item, Weapon, Armor, Potion
    │   ├── passives.py             # PassiveCard + loader + gerador de escolhas
    │   ├── skills_loader.py        # SkillCard + loader
    │   ├── shop.py                 # Lógica da loja (preços, compra, venda)
    │   └── factories/
    │       ├── __init__.py
    │       ├── archetypes.py       # Papéis de monstro carregados do JSON
    │       ├── monsters.py         # generate_monsters_for_level / create_boss
    │       ├── loot.py             # Drop de itens com raridade
    │       └── dungeons.py         # Geração de masmorras
    │
    └── ui/                         # APRESENTAÇÃO — único local com rich / print / input
        ├── __init__.py
        ├── renderer.py             # Console Rich (único local com import rich)
        ├── screens.py              # Telas de estado (Game Over, Inventário, Combate, Eventos, Extração)
        ├── prompts.py              # Leitura de teclado (suporta W/S, setas, ENTER, ESC/Q)
        ├── toj_menu.py             # Menu principal, splash screen, game over
        ├── utils.py                # clear_screen() multiplataforma
        ├── combat_event_handlers.py # Handlers de eventos de combate (EventBus)
        ├── ui_event_handlers.py    # Handlers de eventos de UI (EventBus)
        ├── inventory_flow.py       # Fluxo de interação do inventário (single-item corrigido)
        ├── shop_flow.py            # Fluxo de interação da loja
        ├── skill_flow.py           # Fluxo de escolha de skills
        ├── passive_flow.py         # Fluxo de escolha de passivas
        ├── extraction_flow.py      # Fluxo de decisão de extração entre andares
        ├── random_event_flow.py    # Fluxos de Mercador/Altar/Fonte (TASK-005)
        ├── navigation_menu.py      # Menus navegáveis com split view (3-4 painéis)
        └── combat_event_handlers.py # Handlers de eventos de combate
```

---

## Fluxo de Dependências (permitido)

```
ui/ ←── engine/ ←── mechanics/ ←── entities/
         ↑        ↑               ↑
        sim/   content/         shared/
                  ↑
               storage/
                  ↑
                data/
```

**Regra:** Todas as camadas podem importar de `shared/`. Nenhuma outra importação cruzada é permitida.

**Consequência prática:** quando `entities/` precisa de uma fórmula (`shared/formulas.py`),
de uma tabela de efeitos (`shared/effects.py`) ou de um catálogo de `content/`
(`shared/registries.py`), a saída é sempre `shared/` — nunca um import para cima.

**Imports sob `TYPE_CHECKING`** não contam como dependência de camada: não existem
em tempo de execução e servem só para anotar tipos.

---

## EventBus — Comunicação engine ↔ ui

### Tópicos de Eventos

**Eventos de Combate:**
- `combat.physical_strike` — Ataque físico executado
- `combat.skill_outcome` — Resultado de skill (dano, heal, status)
- `combat.skill_cast` — Skill foi usada
- `combat.turn_effect` — Efeito por turno (poison, frozen, stun, damage_reduction, etc.)
- `combat.flee_result` — Resultado de fuga

**Eventos de UI:**
- `ui.open_inventory` — Abrir inventário
- `ui.open_shop` — Abrir loja (sempre antes da extração)
- `ui.open_passives` — Abrir seleção de passivas
- `ui.random_event` — Evento aleatório de masmorra (Mercador/Altar/Fonte, 25%)
- `ui.extraction_prompt` — Decisão Extrair vs Continuar entre andares
- `ui.game_over` — Tela de game over
- `ui.save_success` — Salvamento bem-sucedido

**Eventos de Sistema:**
- `system.log_message` — Mensagem de log
- `system.save_success` — Salvamento concluído
- `system.save_error` — Erro ao salvar

### Handler Pattern

```python
# UI registra handlers
from src.ui.combat_event_handlers import register_combat_ui_handlers
from src.ui.ui_event_handlers import register_ui_handlers

bus = EventBus()
cleanup_combat = register_combat_ui_handlers(bus)
cleanup_ui = register_ui_handlers(bus)

# Engine publica eventos
bus.publish("ui.open_inventory", {"player": player})

# Cleanup no final
cleanup_combat()
cleanup_ui()
```

---

## Exceções Documentadas

As seguintes funções de UI podem ser importadas diretamente por `engine/` por serem funções de renderização ou utilitários de terminal:

1. `screens.render_*` — Funções de renderização síncrona (não são fluxos bloqueantes)
2. `clear_screen()` — Utilitário de terminal
3. `safe_get_key()` — Input blocking (não tem alternativa via EventBus)
4. `register_combat_ui_handlers()` — Setup de handlers de combate
5. `register_ui_handlers()` — Setup de handlers de UI
6. `toj_menu.main_menu`, `toj_menu.character_creation_flow` — Fluxos de menu principal (executam antes do loop do jogo)
7. `sim/runner.py` usa `print()` — é uma CLI de desenvolvimento, não saída de jogo. Importar `ui/` de dentro de `sim/` quebraria a regra maior de a simulação ser headless.

---

## Camadas e Responsabilidades

| Camada | Responsabilidade | Depende de |
|--------|-----------------|------------|
| `shared/` | Tipos, constantes, tópicos de eventos | nada |
| `data/` | Loaders de JSON | nada |
| `entities/` | Estado puro (Player, Monster) | shared/ |
| `mechanics/` | Regras de negócio (combate, matemática) | entities/, shared/ |
| `content/` | Dados (itens, skills, passivas) + fábricas | entities/, mechanics/, shared/, data/ |
| `sim/` | Simulação headless para balanceamento | content/, mechanics/, entities/, shared/, data/ |
| `storage/` | Persistência (save/load) | content/, entities/, shared/ |
| `engine/` | Orquestração central | content/, mechanics/, entities/, storage/, ui/ (via EventBus) |
| `ui/` | Apresentação e input | shared/, content/ |

---

## Padrões de Código

- **Imports:** Sempre absolutos (`from src.x.y import ...`)
- **Type hints:** Use `TYPE_CHECKING` para evitar imports circulares
- **Eventos:** Publique eventos para comunicação engine → ui, não chame funções diretamente
- **Dados:** Tudo em JSON, sem hardcoded
- **UI:** Use Rich para renderização, screens.py para funções de renderização

---

## Notas Importantes

- `data/` é uma camada de suporte que fornece loaders para JSON (não tem dependências de lógica)
- `mechanics/battle.py` é o laço de batalha compartilhado: `engine/loop.py` passa um callback que lê o teclado, `sim/harness.py` passa uma política. Um simulador que reimplementa o combate mede um jogo que não existe
- `shared/formulas.py` é a fonte única das curvas de crescimento; herói e monstro usam a mesma razão de propósito
- Balanceamento é medido, não estimado: `python -m pytest tests/balance -q`
- `engine/ui_events.py` é um utilitário para emitir eventos sem violar regras de importação
- `content/shop.py` contém a lógica de preços e transações
- `content/skills_loader.py` carrega skills do JSON
- `ui/navigation_menu.py` fornece menus navegáveis com split view (3-4 painéis)
- Navegação usa **W/S** (não setas), **ENTER** para selecionar, **Q** para sair (não ESC)
- Inventário mostra comparação contextual: "Ao equipar: ATK +5 (atual: +3)"

---

## Glossário de Arquitetura

| Termo | Definição |
|-------|-----------|
| EventBus | Sistema Pub/Sub para comunicação entre engine e ui |
| Handler | Função que responde a um evento do EventBus |
| Topic | Nome do canal de evento (ex: "combat.physical_strike") |
| publish() | Enviar evento para todos os handlers inscritos |
| subscribe() | Inscrever handler em um tópico |
| TYPE_CHECKING | Import para type hints apenas (não em runtime) |
| Split View | Layout de múltiplos painéis lado a lado |