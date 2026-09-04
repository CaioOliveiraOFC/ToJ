# ⚔️ Tales of the Journey (ToJ)

RPG de masmorra terminal-based hardcore com exploração procedural e combate tático por turnos. O jogo conta com sistema de extração — o jogador pode sair da masmorra entre andares para salvar seu progresso, além de eventos aleatórios e combate com cooldowns.

---

## 🎮 Sobre o Jogo

- Filosofia: *"Você não está farmando. Você está jogando xadrez com a morte."*
- Referências: Pokémon Ruby (progressão), Auto Chess/TFT (builds), Hades (ritmo), Minecraft Hardcore (permadeath)
- Dois pilares: **Forge Run** (criação de gladiadores, permadeath) e **Arena** (PvP futuro)

## ✨ Funcionalidades Atuais

- RPG de masmorra terminal-based hardcore com exploração procedural e combate tático por turnos com extração entre andares
- 3 classes com identidade própria: Guerreiro (atrito), Mago (explosão), Ladino (esquiva) — poder comparável, fraquezas diferentes
- 9 arquétipos de monstro (trash, bruiser, tank, glass cannon, skirmisher, controlador, suporte, elite, chefe), cada um com um counterplay
- Encontros compostos com escolha de alvo a partir do andar 4
- Recursos importam: vencer custa vida e mana, e concluir o andar devolve só parte
- 29 cartas passivas permanentes em 4 raridades (Comum → Lendário)
- 41 skills com custo de MP, cooldown e efeitos que funcionam de fato
- 14 consumíveis, loja, drops e eventos aleatórios (Mercador, Altar, Fonte)
- Save/Load via JSON com 10 slots + permadeath e Troféu de Fracasso
- Arquitetura orientada a eventos (EventBus) e simulação headless para balanceamento

## 🚀 Instalação e Execução

```bash
pip install -r requirements.txt
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

## ⚖️ Balanceamento

O balanceamento é medido, não estimado. `src/sim/` roda o motor de combate real
sem UI e simula milhares de combates por segundo; `tests/balance/` transforma os
alvos em invariantes que quebram quando alguém os desfaz.

```bash
python -m pytest tests/balance -q                  # invariantes rápidas (6s)
python -m pytest tests/balance -q -m balance_full  # runs de 20 andares (8s)
python -m src.sim.runner run --iterations 400      # curva de dificuldade
python -m src.sim.runner matrix --iterations 500   # matriz classe x encontro
```

A simulação roda os mesmos sistemas do jogo — passivas, escolha de skill, drops,
loja, eventos e Essência — e não só o combate.

Estado atual (250 runs por classe, jogador competente): Guerreiro chega em média
ao andar 8,1 e termina a masmorra em 26% das runs; Mago 5,8 e 18%; Ladino 8,1 e
24%. Um bot que só aperta "atacar" nunca termina, e para no andar 1.
Detalhes em `BALANCE_REPORT.md`.

## 🛠️ Tecnologias

- Python 3.12+, Rich, pyfiglet
- Padrões: Observer, Factory, Singleton, DTOs
- Qualidade: Ruff, mypy

## 📖 Documentação

- `ARCHITECTURE.md` — Mapa completo do código
- `GAME_DESING.md` — Design do jogo
- `docs/GUIDE_PASSIVES.md` — Guia de passivas
- `BALANCE_REPORT.md` — Modelo de balanceamento e números medidos
- `TASK.md` — Rastreador de tarefas

## 🗺️ Roadmap

- ✅ Sistema de Passivas (Concluído — 29 passivas)
- ✅ Skills Reimaginadas (Concluída — 41 skills com cooldown)
- ✅ Loja, Itens e Inventário (Concluído — single-item equip corrigido)
- ✅ Teste Automatizado com Bot BFS (AutoTester — tests/auto_test.py, mock de saves)
- ✅ 10 slots de personagens + permadeath + Troféu de Fracasso (TASK-004)
- ✅ Eventos aleatórios na masmorra (TASK-005 — 25% Mercador/Altar/Fonte)
- ✅ Cooldowns + redução de dano + stun (TASK-006 — cooldown por skill, status temporários)
- ✅ Saída da masmorra (extração) entre andares (TASK-007 — preserva save pós-loja)
- ✅ Rebalanceamento estrutural (orçamento único, arquétipos, atrito, encontros compostos)
- 🔲 Arena PvP (único pendente — tiers, matchmaking, ranking por Elo)

## 📊 Métricas de Sucesso

1. Jogador novo entende o jogo sem tutoriais externos
2. Arquitetura não violada (sem `print()` fora de `ui/`, sem imports cruzados)
3. Sessões longas sem crashes