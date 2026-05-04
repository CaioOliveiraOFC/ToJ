# ⚔️ Tales of the Journey (ToJ)

RPG de masmorra terminal-based hardcore com exploração procedural e combate tático por turnos. O jogo conta com sistema de extração — o jogador pode sair da masmorra a qualquer momento para salvar seu progresso. No futuro, a extração será expandida com mais opções e recompensas.

---

## 🎮 Sobre o Jogo

- Filosofia: *"Você não está farmando. Você está jogando xadrez com a morte."*
- Referências: Pokémon Ruby (progressão), Auto Chess/TFT (builds), Hades (ritmo), Minecraft Hardcore (permadeath)
- Dois pilares: **Forge Run** (criação de gladiadores, permadeath) e **Arena** (PvP futuro)

## ✨ Funcionalidades Atuais

- RPG de masmorra terminal-based hardcore com exploração procedural e combate tático por turnos com extração; no futuro vai ter extração
- 3 classes: Guerreiro, Mago, Ladino (stats e habilidades únicas)
- Masmorras procedurais infinitas com multiplicador de Essência variável (0.5x a 3.0x)
- Combate tático por turnos com iniciativa dinâmica, crítico, esquiva e itens/habilidades
- 100+ cartas passivas permanentes em 4 raridades (Comum → Lendário)
- 4 habilidades ativas por classe com custo de MP e cooldowns
- Sistema de loja, drops de itens (armas, armaduras, poções)
- Save/Load via JSON
- Arquitetura orientada a eventos (EventBus) para fácil manutenção

## 🚀 Instalação e Execução

```bash
pip install rich pyfiglet
python main.py
```

## 🎯 Como Jogar

- Explore a masmorra, derrote monstros para ganhar Essência (XP) e ouro
- Suba de nível para ganhar stats, pontos de atributo e escolher passivas
- Gerencie inventário e habilidades em combate
- Decida quando extrair seu personagem: morte na Forge Run apaga o personagem para sempre

## 🏗️ Arquitetura

Camadas unidirecionais: `ui/` → `engine/` → `mechanics/` → `entities/` (todas importam de `shared/`)

- EventBus (Pub/Sub) para comunicação desacoplada
- Data-Driven: Itens, monstros, habilidades e passivas em JSON
- Lógica de negócio pura em `mechanics/`, apresentação exclusiva em `ui/`

## 📂 Estrutura do Projeto

```
ToJ/
├── main.py                  # Bootstrap
├── src/
│   ├── shared/              # Tipos, constantes, tópicos de eventos
│   ├── data/                # JSONs e loaders
│   ├── engine/              # EventBus, loop principal, mapa
│   ├── entities/            # Heróis e Monstros
│   ├── mechanics/           # Fórmulas de combate
│   ├── content/             # Fábricas (monstros, loot, itens)
│   ├── ui/                  # Rich, telas, inputs
│   └── storage/             # Save/Load
└── tests/                   # Testes
```

## 🛠️ Tecnologias

- Python 3.12+, Rich, pyfiglet
- Padrões: Observer, Factory, Singleton, DTOs
- Qualidade: Ruff, mypy

## 📖 Documentação

- `ARCHITECTURE.md` — Mapa completo do código
- `GAME_DESING.md` — Design do jogo
- `docs/GUIDE_PASSIVES.md` — Guia de passivas
- `TASK.md` — Rastreador de tarefas (TASK-003 em progresso: correções de bugs na UI)

## 🗺️ Roadmap

- ✅ Sistema de Passivas (Concluído)
- ✅ Skills Reimaginadas (Pronta)
- 🔲 Loja, Itens e Inventário (Em construção)
- 🔲 Teste Automatizado com Bot BFS (Pendente)
- 🔲 10 slots de personagens + permadeath (TASK-004)
- 🔲 Eventos aleatórios na masmorra (TASK-005)
- 🔲 Cooldowns + redução de dano + stun (TASK-006)
- 🔲 Saída da masmorra (extração) (TASK-007)
- 🔲 Arena PvP

## 📊 Métricas de Sucesso

1. Jogador novo entende o jogo sem tutoriais externos
2. Arquitetura não violada (sem `print()` fora de `ui/`, sem imports cruzados)
3. Sessões longas sem crashes