TOJ (Tales of the Journey) — Documento-Fonte do Projeto

> **Nota:** Este documento reflete a **visão ideal e histórica** do projeto. Para o estado atual de implementação e pendências técnicas, consulte **GAME_DESING.md**.

---

1. Visão Geral e Alma do Jogo

TOJ é um RPG de masmorra hardcore em terminal, onde o jogador realiza Forge Runs (PvE) para forjar gladiadores e levá-los à Arena (PvP futuro). A morte na masmorra é permanente — o personagem é perdido para sempre. A progressão é tática, com escolhas de passivas e skills, inspirada em Auto Chess/TFT e Pokémon Ruby.

Sagrada Trindade do Design
Velocidade: Turnos rápidos, decisões ágeis, navegação fluida

Inteligência: Escolhas táticas profundas (skills, passivas, equipamentos)

Caos: Natureza imprevisível — loot, loja, encontros são rolados

Tom e Estilo
Terminal puro, sem GUI

Estética ASCII/Unicode com cores Rich

Atmosfera sombria mas com toques de humor negro

Mercador é um NPC com falas que evoluem com o progresso

Mecânicas caóticas (loja rerrola 100% a cada visita)

2. Estrutura do Projeto

```
ToJ/
├── main.py                          # Ponto de entrada (bootstrap)
├── savegame.json                    # Arquivo de save (gerado automaticamente)
├── pyproject.toml                    # Configuração do projeto (ruff, mypy)
│
├── src/                             # Código fonte
│   ├── __init__.py
│   │
│   ├── shared/                      # Tipos compartilhados e constantes
│   │   ├── __init__.py
│   │   ├── types.py                  # TypedDicts e Dataclasses (CombatResult, EntityStats, DTOs)
│   │   ├── constants.py             # Constantes globais do jogo
│   │   └── combat_topics.py          # Tópicos de eventos de combate (EventBus)
│   │
│   ├── data/                        # Dados JSON e loaders
│   │   ├── __init__.py
│   │   ├── loader.py                # Utilitário para carregar JSONs
│   │   ├── items.json               # Catálogo de ~121 itens
│   │   ├── passives.json            # 27 passivas em 4 raridades
│   │   ├── skills.json              # 41 skills (12 iniciais + 24 novas + 5 de classe)
│   │   └── monsters.json            # Definições de monstros
│   │
│   ├── engine/                      # Orquestração central
│   │   ├── __init__.py
│   │   ├── bootstrap.py             # Inicialização do jogo e menu principal
│   │   ├── loop.py                  # Loop principal e motor de combate
│   │   ├── map.py                   # Lógica de mapa, colisão e movimentação
│   │   ├── game_logic.py            # Criação de personagem e geração de monstros
│   │   ├── events.py                # Sistema Pub/Sub (EventBus)
│   │   └── ui_events.py             # Utilitários para emitir eventos de UI
│   │
│   ├── entities/                    # Estado puro e encapsulamento
│   │   ├── __init__.py
│   │   ├── base.py                  # Classe mãe Entity (HP, MP, take_damage, heal)
│   │   ├── heroes.py                # Warrior, Mage, Rogue (Player)
│   │   └── monsters.py              # Monster e variantes
│   │
│   ├── storage/                     # Persistência
│   │   ├── __init__.py
│   │   └── save_manager.py         # save_game / load_game → savegame.json
│   │
│   ├── mechanics/                   # Regras de negócio
│   │   ├── __init__.py
│   │   ├── combat.py                # Fórmulas de dano, esquiva, crítico
│   │   └── math_operations.py      # Escalonamento de stats, XP, multiplicador
│   │
│   ├── content/                     # Dados e fábricas
│   │   ├── __init__.py
│   │   ├── items.py                 # Classes: Item, Weapon, Armor, Potion
│   │   ├── passives.py              # PassiveCard + loader + gerador de escolhas
│   │   ├── skills_loader.py        # SkillCard + loader
│   │   ├── shop.py                  # Lógica da loja (preços, compra, venda)
│   │   │
│   │   └── factories/               # Fábricas de geração
│   │       ├── __init__.py
│   │       ├── monsters.py         # generate_monsters_for_level / create_boss
│   │       ├── loot.py             # Drop de itens com raridade
│   │       └── dungeons.py         # Geração de masmorras
│   │
│   └── ui/                         # Apresentação (único local com rich/print/input)
│       ├── __init__.py
│       ├── renderer.py             # Console Rich (único local com import rich)
│       ├── screens.py              # Telas de estado (Game Over, Inventário, Combate)
│       ├── prompts.py              # Leitura de teclado (suporta W/S, setas, ENTER, ESC)
│       ├── toj_menu.py             # Menu principal, splash screen, game over
│       ├── utils.py                # clear_screen() multiplataforma
│       ├── combat_event_handlers.py # Handlers de eventos de combate
│       ├── inventory_flow.py       # Fluxo de interação do inventário
│       ├── shop_flow.py            # Fluxo de interação da loja
│       ├── skill_flow.py           # Fluxo de escolha de skills
│       ├── passive_flow.py         # Fluxo de escolha de passivas
│       └── navigation_menu.py      # Menus navegáveis com split view
│
├── tests/                          # Testes automatizados
│   ├── __init__.py
│   └── auto_test.py                # AutoTester BFS para QA
│
└── docs/                           # Documentação adicional
    └── GUIDE_PASSIVES.md            # Guia para criar novas passivas
```

3. Regras de Arquitetura (Invioláveis)
entities/ não importa de content/: Inversão de dependência — entidades não conhecem dados

Nada de print() fora de ui/: Toda saída passa pelo renderer Rich

Sem imports cruzados: Estrutura hierárquica clara

Dados em JSON, código limpo, sem hardcoded: Tudo data-driven

safe_get_key() é o único ponto de entrada de teclado: Consistência multiplataforma

4. Sistema de Classes de Heróis

> **Versus:** Esta seção documenta a **visão original de design**. O código evoluiu desde então.

4.1 Warrior
Foco: Força (ST) e Defesa (DF)

- **Documentado (visão original):** `(ST * 1.5 + AG * 0.3) / DAMAGE_FORMULA_DIVISOR`
- **Implementado (atualmente):** `(ST * 2 + MG) // 4`

- **Documentado:** Equipamento inicial: Weapon Common + Body Common
- **Implementado:** ❌ NÃO IMPLEMENTADO — personagem começa sem equipamentos

4.2 Mage
Foco: Magia (MG) e Mana (MP)

- **Documentado (visão original):** `(MG * 1.8 + AG * 0.2) / DAMAGE_FORMULA_DIVISOR`
- **Implementado (atualmente):** `(ST + MG * 2) // 5`

- **Documentado:** Equipamento inicial: Weapon Common + Body Common
- **Implementado:** ❌ NÃO IMPLEMENTADO

4.3 Rogue
Foco: Agilidade (AG) e Evasão

- **Documentado (visão original):** `(AG * 1.2 + ST * 0.6) / DAMAGE_FORMULA_DIVISOR`
- **Implementado (atualmente):** `(ST * 1.2 + AG * 1.8) // 3`

- **Documentado:** Equipamento inicial: Weapon Common + Body Common
- **Implementado:** ❌ NÃO IMPLEMENTADO

- **Documentado:** Mecânica especial: Esquiva acumulativa (cap em 65%)
- **Implementado:** ✅ Implementado

- **Documentado:** Ajuste de balanceamento: Ataque Furtivo — mana 10→30, effect_value 80→65
- **Implementado:** ✅ Implementado

4.4 Stats Base por Classe

| Classe  | HP  | MP | ST | MG | AG | DF |
|---------|-----|----|----|----|----|-----|
| Warrior | 120 | 30 | 12 | 4  | 6  | 10  |
| Mage    | 80  | 80 | 4  | 14 | 7  | 5   |
| Rogue   | 90  | 40 | 8  | 5  | 14 | 6   |

> **Nota:** Stats base estão corretos no código atual.
5. Sistema de Passivas
5.1 Estrutura
Arquivo: passives.json

20+ passivas em 4 raridades (Common, Rare, Epic, Legendary)

Classe: PassiveCard (dataclass)

Escolha a cada level up (3 opções aleatórias)

5.2 Tipos de Efeito
max_hp: Aumenta HP máximo

max_mp: Aumenta MP máximo

strength: Aumenta Força

magic: Aumenta Magia

agility: Aumenta Agilidade

defense: Aumenta Defesa

speed: Aumenta Velocidade

crit_chance: Aumenta chance de crítico

life_steal: Roubo de vida

damage_reduction: Redução de dano

5.3 Aplicação de HP/MP com Proporção
Quando uma passiva aumenta max_hp ou max_mp, o valor atual é ajustado proporcionalmente:

```python
hp_ratio = self._hp / old_base_hp
self._hp = min(int(self.base_hp * hp_ratio), self.base_hp)
```
6. Sistema de Skills

> **Versus:** Esta seção documenta a **visão original de design**.

6.1 Estrutura
Arquivo: skills.json

41 skills (12 iniciais + 24 novas + 5 de classe)

Classe: SkillCard (dataclass)

- **Documentado:** 4 skills iniciais por classe
- **Implementado (atualmente):** ❌ BUG — código adiciona apenas 1 skill inicial (`initial_skills[0]`)

Escolhas a partir do nível 5 (níveis ímpares)

UI de substituição (trocar uma skill existente)

6.2 Mecânica de Combate
Scaling de skills: +8% por nível de skill

Tipos de dano: físico, mágico, veneno (escala com AG), sangramento

Efeitos: stun, bleed, poison, fear, etc.

6.3 Balanceamento
DEFENSE_REDUCTION_DIVISOR: 4

SKILL_LEVEL_SCALING: 0.08

- **Documentado:** Skills causam mais dano que ataque normal
- **Implementado:** ✅ Implementado

- **Documentado:** Classes têm identidades distintas
- **Implementado:** ✅ Implementado (fórmulas diferentes por classe)

7. Sistema de Itens
7.1 Estrutura
Arquivo: items.json (~121 itens)

Classe: Item com propriedades is_potion e is_usable

8 slots: Weapon, Helmet, Body, Legs, Shoes, Hands, Amulet, Ring

7.2 Raridades
Raridade	Peso	Disponível na Loja
Common	60%	Sempre
Rare	28%	A partir do andar 5
Epic	10%	Apenas andar 10+
Legendary	2%	Nunca na loja
7.3 Efeitos de Itens
Efeitos usáveis (consumíveis): max_hp, max_mp, agility, strength, defense, speed, evasion, crit_chance, crit_damage, life_steal, mana_regen

Efeitos secundários (passivos ao equipar): bleed, poison, stun, magic_damage, magic_resist, damage_reduction, fire_resist, fear, true_damage, armageddon, death_ignore

7.4 Propriedades do Item
python
class Item:
    id: str
    name: str
    description: str
    rarity: str          # Common, Rare, Epic, Legendary
    slot: str            # Weapon, Helmet, Body, Legs, Shoes, Hands, Amulet, Ring
    damage_bonus: int
    defense_bonus: int
    effect_type: str | None
    effect_value: int
    classes: list[str] | None  # None = todas as classes
    sold_in_shop: bool
    droppable: bool
    price: int
    shop_min_floor: int
    shop_max_floor: int | None

    @property
    def is_potion(self) -> bool:
        """Legacy: verifica effect_type em max_hp, max_mp, agility, strength, defense"""

    @property
    def is_usable(self) -> bool:
        """Verifica se o item pode ser usado (tem efeito consumível)"""
8. Sistema de Loja
8.1 Comportamento Caótico
A cada visita, o mercador rerrola 100% do estoque

Itens são embaralhados aleatoriamente da pool disponível para o andar

O jogador sabe que a loja é um "dado rolado"

8.2 Progressão do Catálogo
Andar	Itens na Loja	Raridades Disponíveis
1-3	8-10 itens	Common + 1-2 Rare
4-6	12-15 itens	Common + Rare
7-9	15-18 itens	Common + Rare + 1-2 Epic
10-14	18-22 itens	Common + Rare + Epic
15+	22-25 itens	Common + Rare + Epic
Legendary nunca aparece na loja (sold_in_shop: false)

Preço escala: base_price * (1 + dungeon_level * 0.05)

Refresh automático a cada andar completado

8.3 Comportamento de Compra
Item comprado some imediatamente da lista

A lista não é rerrolada até a próxima visita (próximo andar)

Itens restantes permanecem os mesmos

9. Sistema de Inventário
9.1 Layout de 3-4 Painéis
text
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ INVENTÁRIO   │ DETALHES     │ STATUS       │ EFEITOS*     │
│══════════════│══════════════│══════════════│══════════════│
│              │              │              │              │
│> [1] Lança   │ Nome: Lança  │ Warrior      │ Força +10    │
│  [2] Cajado   │ Dano: +5     │ HP: 173/173  │  3 turnos    │
│              │              │ MP: 30/30    │              │
│              │ Ao equipar:  │ ATK: 51      │ Velocidade+5 │
│              │ ATK +5, DEF+1│ DEF: 30      │  2 turnos    │
│              │              │ AGI: 5       │              │
│              │ [E] equipar  │ Ouro: 128    │              │
└──────────────┴──────────────┴──────────────┴──────────────┘
* Painel de efeitos é condicional (só aparece se houver buffs ativos)
9.2 Funcionalidades
Ordenação tática: Equipáveis primeiro (por slot), usáveis depois, resto por último

Comparação contextual: "Ao equipar: ATK +5 (atual: +3)" — mostra ganho/perda líquida

Indicadores visuais:

← será trocado — slot ocupado que será substituído

← upgrade! — slot vazio com item compatível disponível

⛝ classe restrita — item não usável pela classe

Teclas rápidas:

E = Equipar/Desequipar imediatamente

U = Usar item imediatamente

ENTER = Submenu (apenas para itens ambíguos: equipáveis E usáveis)

ESC = Sair

Confirmação para itens raros: Epic+ pede confirmação antes de usar

Scroll inteligente: Ao remover item, cursor mantém posição relativa

Feedback visual: Mensagens temporárias no rodapé sem sair dos painéis

Inventário vazio: Mostra mensagem sem expulsar o jogador

10. Sistema de Navegação (UI)
10.1 Menu Navegável
Navegação: W (cima) e S (baixo)

Seleção: ENTER

Cancelar: ESC

Máximo de 10 itens por página (com paginação quando >10)

10.2 Leitura de Teclado (prompts.py)
Multiplataforma (Windows: msvcrt, Unix: termios/tty)

Detecta: caracteres normais, arrow keys, W/S, ENTER, ESC, BACKSPACE

Funções: get_key(), safe_get_key(), wait_enter_to_continue()

10.3 Escape de Markup
Função escape_markup() para evitar quebras de formatação Rich

Caracteres [ e ] em nomes de itens são escapados

11. Sistema de Combate

> **Versus:** Esta seção documenta a **visão original de design** (continuação).

11.1 Constantes
```python
DEFENSE_REDUCTION_DIVISOR = 4
SKILL_LEVEL_SCALING = 0.08
DAMAGE_FORMULA_DIVISOR = 2
```

> **Nota:** `DAMAGE_FORMULA_DIVISOR` não é mais usado — as fórmulas foram refatoradas para operações inteiras diretas (ver seção 4).

11.2 Fórmulas de Dano por Classe (original)

| Classe  | Documentado (visão original) | Implementado (atualmente) |
|---------|------------------------------|---------------------------|
| Warrior | `(ST * 1.5 + AG * 0.3) / 2` | `(ST * 2 + MG) // 4` |
| Mage    | `(MG * 1.8 + AG * 0.2) / 2` | `(ST + MG * 2) // 5` |
| Rogue   | `(AG * 1.2 + ST * 0.6) / 2` | `(ST * 1.2 + AG * 1.8) // 3` |

11.3 Veneno
Escala com AG do personagem

Duração e dano por turno baseados no effect_value da skill

- **Documentado:** ✅ Implementado
- **Implementado:** Sistema de veneno com duração e dano por turno funciona corretamente

11.4 Esquiva (Rogue)
Acumulativa durante a batalha

Cap em 65%

Reseta ao fim do combate

- **Documentado:** ✅ Implementado
- **Implementado:** Implementado com acumulação e cap de 65%

12. Estado Atual e Pendências
12.1 Implementado
✅ Sistema de passivas com escolha a cada level up

✅ Sistema de skills com JSON (41 skills)

✅ Balanceamento de combate (4 etapas)

✅ Itens data-driven (121 itens)

✅ Loja com progressão por andar e reroll 100%

✅ Inventário com 3 painéis (lista + detalhes + status)

✅ Menu navegável com W/S/ENTER/ESC

✅ Teclas rápidas E/U no inventário

✅ Comparação contextual ao equipar

✅ Ajuste do Rogue (Ataque Furtivo, cap de esquiva)

✅ Correção de HP/MP com proporção em passivas

12.2 Pendências Técnicas (do roadmap)
🟡 Scroll inteligente ao remover item

🟡 Mensagem de feedback pós-ação sem sair dos painéis

🟡 Equipamento inicial por classe (Weapon Common + Body Common)

🟡 4 habilidades iniciais (corrigir bug - atualmente adiciona apenas 1)

🟡 Sistema de cooldown de habilidades

12.3 Futuro
🟢 TASK-003: 10 slots de heróis + permadeath + Troféu de Fracasso

🟢 Arena (PvP)

🟢 Status effects complexos (taunt, mana_burn, sleep, etc.)

🟢 Mais itens e variedade de builds

13. Glossário
Termo	Definição
Forge Run	Sessão PvE na masmorra para evoluir gladiadores
Arena	Modo PvP futuro onde gladiadores competem
Sagrada Trindade	Velocidade, Inteligência, Caos — pilares do design
Reroll	Embaralhamento completo do estoque da loja
Split View	Layout de múltiplos painéis lado a lado
Cap de Esquiva	Limite máximo de 65% para esquiva do Rogue
Proporção de HP/MP	Ao aumentar HP/MP máximo, o atual mantém a mesma %
Item Ambíguo	Item que é equipável E usável (ex: amuletos com efeito)
Teclas Rápidas	E para equipar, U para usar, sem abrir submenu
Comparação Contextual	Mostra ganho/perda ao equipar vs slot vazio ou ocupado
14. Regras de Ouro do Desenvolvimento
Data-driven sempre: Novos itens, skills, passivas vão em JSON

UI separada da lógica: ui/ renderiza, engine/ processa, entities/ modela

Terminal first: Toda interação funciona em terminal 80x24 mínimo

Caos controlado: Aleatoriedade com limites (progressão, raridades)

Feedback imediato: Toda ação tem resposta visual instantânea

Permadeath real: Morte na masmorra = personagem perdido

Respeito ao jogador: Ações rápidas para o frequente, profundidade para o raro

15. Notas para o LLM
O projeto está em Python 3.12+

Usa rich para renderização de terminal

Todos os dados de conteúdo estão em JSON na pasta src/data/

A UI é construída com painéis Rich e navegação por teclado

O jogo é hardcore — morte é permanente

A loja é caótica — 100% de reroll a cada visita

O inventário usa 3-4 painéis com comparação contextual

As teclas de navegação são W/S (não setas)

Itens ambíguos (equipáveis E usáveis) precisam de tratamento especial

Efeitos ativos são mostrados condicionalmente no 4º painel

