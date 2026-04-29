# ⚔️ Tales of the Journey (ToJ)
 
**Tales of the Journey** é um RPG de terminal desenvolvido em Python que utiliza a biblioteca `rich`. Mais do que um jogo, este projeto serve como um **laboratório avançado de Engenharia de Software**, focado em padrões arquiteturais rigorosos para facilitar um futuro porting para **Rust com Ratatui**.
 
---
 
## 🏗️ Filosofia Arquitetural
 
O ToJ foi desenhado seguindo princípios de alta coesão e baixo acoplamento:
 
- **Arquitetura Orientada a Eventos (Pub/Sub):** Utiliza um `EventBus` centralizado em `src/engine/events.py` para comunicação assíncrona entre o motor de jogo e a interface.
- **Separação MVC / Hexagonal:** A lógica de combate (`mechanics/`) e o estado das entidades (`entities/`) são agnósticos em relação à interface.
- **Data-Driven Design:** As definições de itens, monstros e balanceamento estão sendo migradas para arquivos JSON, permitindo ajustes sem alteração de código.
- **Clean Entry Point:** O `main.py` atua estritamente como *Bootstrap*, configurando as dependências e iniciando o loop.
---
 
## 🚀 Roadmap de Engenharia (Sprints)
 
- ✅ **[SPRINT 0] Desmembramento do Monólito**: Limpeza do `main.py`. A UI foi movida para `src/ui/screens.py` e a lógica para `src/engine/loop.py`.
- ⏳ **[SPRINT 1] O Sistema Nervoso (Em andamento):** Implementação do `EventBus`. O combate publicará eventos e a UI reagirá a eles via handlers.
- 📅 **[SPRINT 2] Motor de Conteúdo:** Migração de dados *hardcoded* para `src/data/`. Refatoração das fábricas de monstros e loot para JSON.
- 📅 **[SPRINT 3] Game Feel (UX Visual):** Pausas dramáticas e feedback visual dinâmico baseado em porcentagem de vida.
- 📅 **[SPRINT 4] Expansão de Features:** Status Effects (Veneno, Atordoamento, Sangramento) e fundação do modo Arena.
> Consulte `SPRINTS.md` para o detalhamento completo de tarefas de cada sprint.
 
---
 
## 📂 Organização do Código (`src/`)
 
```text
├── engine/     # Orquestração: EventBus, GameLoop e lógica de Mapas.
├── entities/   # Estado Puro: Definição de Heróis e Monstros (Classes Base).
├── mechanics/  # Regras de Negócio: Fórmulas de combate e matemática pura.
├── content/    # Fábricas: Geradores de instâncias, itens e equipamentos.
├── ui/         # Apresentação: Renderização com Rich e captura de inputs.
├── shared/     # Contratos: Tipos (DTOs) e constantes de eventos.
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
 
- **Regra de Ouro:** NUNCA importe `rich` ou use `print()` dentro de `src/engine/` ou `src/mechanics/`. Toda saída visual deve passar pelo `EventBus` ou por `src/ui/`.
- **Tipagem:** Utilize as dataclasses de `src/shared/types.py` para transportar dados entre camadas.
- **Regras de import completas:** Consulte `.cursorrules`.