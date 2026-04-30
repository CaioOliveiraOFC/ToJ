# ⚔️ Tales of the Journey (ToJ)

**Tales of the Journey** é um RPG de terminal desenvolvido em Python que utiliza a biblioteca `rich`. Mais do que um jogo, este projeto serve como um **laboratório avançado de Engenharia de Software**, focado em padrões arquiteturais rigorosos para facilitar um futuro porting para **Rust com Ratatui**.

---

## 🏗️ Filosofia Arquitetural

O ToJ foi desenhado seguindo princípios de alta coesão e baixo acoplamento:

- **Arquitetura Orientada a Eventos (Pub/Sub):** Utiliza um `EventBus` centralizado em `src/engine/events.py` para comunicação entre o motor de jogo e a interface.
- **Separação MVC / Hexagonal:** A lógica de combate (`mechanics/`) e o estado das entidades (`entities/`) são agnósticos em relação à interface.
- **Data-Driven Design:** As definições de itens, monstros e balanceamento residem em `src/data/` (JSON), permitindo ajustes sem alteração de código.
- **Clean Entry Point:** O `main.py` atua estritamente como *Bootstrap*, configurando as dependências e iniciando o loop.

---

## 🚀 Roadmap de Engenharia (Sprints)

- ✅ **[SPRINT 0] Saneamento e Contratos** — `main.py` limpo; `shared/constants.py` e `shared/types.py` criados; `pyproject.toml` com ruff/mypy configurados. **Débitos:** `print()` direto ainda presente em `entities/`, `engine/game_logic.py`, `engine/map.py` e `storage/`; `main.py` ainda excede 30 linhas; import lazy em `map.py#load_map_state`.
- ✅ **[SPRINT 1] O Sistema Nervoso** — `EventBus` implementado; combate publica eventos; UI reage via handlers inscritos. **Débito:** `ui/screens.py#render_post_battle` contém lógica de negócio (XP, loot) e importa ilegalmente de `mechanics/` e `content/`.
- ✅ **[SPRINT 2] Motor de Conteúdo** — Dados de monstros e itens migrados para `src/data/monsters.json` e `src/data/items.json`; fábricas refatoradas para JSON; `src/data/loader.py` como utilitário central.
- 📅 **[SPRINT 3] Game Feel (UX Visual)** — Pausas dramáticas e feedback visual dinâmico baseado em porcentagem de vida.
- 📅 **[SPRINT 4] Expansão de Features** — Status Effects (Veneno, Atordoamento, Sangramento) e fundação do modo Arena.

> Consulte `SPRINTS.md` para o detalhamento completo de tarefas de cada sprint.

---

## 📂 Organização do Código (`src/`)

```text
├── engine/     # Orquestração: EventBus, GameLoop e lógica de Mapas.
├── entities/   # Estado Puro: Definição de Heróis e Monstros (Classes Base).
├── mechanics/  # Regras de Negócio: Fórmulas de combate e matemática pura.
├── content/    # Fábricas: Geradores de instâncias, itens e equipamentos.
├── data/       # Dados JSON: monsters.json, items.json, loader.py.
├── ui/         # Apresentação: Renderização com Rich e captura de inputs.
├── shared/     # Contratos: Tipos (DTOs), constantes e tópicos de eventos.
└── storage/    # Persistência: Serialização de Savegames em JSON.
```

> Consulte `ARCHITECTURE.md` para o mapa estrutural completo com todos os arquivos.

---

## 🛠️ Tecnologias

- **Linguagem:** Python 3.12+
- **Interface:** [Rich](https://github.com/Textualize/rich) (Tabelas, Painéis, Cores)
- **Design Patterns:** Observer (Pub/Sub), Factory, Singleton (EventBus), DTOs.

---

## ⚙️ Instalação e Execução

```bash
pip install rich pyfiglet
python main.py
```

---

## 📐 Notas de Arquitetura para Co-pilotos de IA

- **Regra de Ouro:** NUNCA importe `rich` ou use `print()` dentro de `src/engine/`, `src/mechanics/`, `src/entities/` ou `src/storage/`. Toda saída visual deve passar pelo `EventBus` ou por `src/ui/`.
- **Tipagem:** Utilize as dataclasses de `src/shared/types.py` para transportar dados entre camadas.
- **Eventos:** Os tópicos do EventBus estão em `src/shared/combat_topics.py`. A UI subscreve via `src/ui/combat_event_handlers.py`.
- **Regras de import completas:** Consulte `.windsurfrules`.