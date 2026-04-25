# 🗡️ Tales of the Journey

**Tales of the Journey** é um RPG (Role-Playing Game) em formato de texto executado diretamente no terminal. Desenvolvido em Python, o jogo utiliza a biblioteca `rich` para entregar uma estética visual premium e imersiva com painéis dinâmicos, tabelas interativas e textos coloridos, contrastando com aventuras em texto tradicionais.

---

## 🌟 Características Principais

*   **Classes Distintas**: Escolha entre **Warrior** (Guerreiro focado em HP e Força), **Mage** (Mago especializado em magia e habilidades em área) e **Rogue** (Ladino com alta agilidade e chances de crítico).
*   **Masmorras Procedurais**: Explore labirintos gerados dinamicamente. Os mapas aumentam em tamanho e complexidade conforme você avança pelos níveis da masmorra.
*   **Sistema de Combate Complexo**: Batalhas baseadas em turnos (`interactions.py`) contendo sistema de ataque, fuga, magias com custo de MP, poções, efeitos de status (veneno, congelamento) e buffs temporários.
*   **Inventário e Loja**: Sistema dinâmico de coleta de loot, gerenciamento de equipamentos (armas, capacetes, armaduras de corpo, calças e botas) e a possibilidade de interagir com o Mercador (`shop.py`) para comprar e vender itens com economia baseada em ouro e nível da masmorra.
*   **Auto-Teste Embutido**: Possui um bot com sistema de navegação por busca em largura (BFS) que pode jogar o jogo automaticamente para realização de testes de estabilidade.

---

## 🏗️ Arquitetura do Projeto

Abaixo segue o mapa estrutural e arquitetural de todo o código-fonte, dividido por domínios:

### 🎮 Motor e Loop Principal
*   `game.py`: Ponto de entrada. Gerencia o loop principal, instanciação do mapa e a orquestração do jogo entre a masmorra, menu de inventário e instâncias de combate.
*   `toj_source/game_logic.py`: Regras gerais do jogo, criação de personagem inicial e funções lógicas atreladas à geração de monstros.
*   `toj_source/save_manager.py`: Controlador de persistência. Salva e carrega o estado atual do mapa, o progresso e o inventário do jogador em arquivos locais (`savegame.json`).
*   `toj_source/auto_test.py`: Ferramenta para Quality Assurance contendo uma inteligência artificial embutida capaz de navegar os mapas perfeitamente e avaliar possíveis *crashes* sistêmicos.

### 🧙‍♂️ Entidades e RPG
*   `toj_source/classes.py`: Definição Orientada a Objetos das classes do jogador (`Warrior`, `Mage`, `Rogue`) herdando da classe base `Player`. Também inclui as lógicas de balanceamento do inimigo base `Monster`.
*   `toj_source/math_operations.py`: Módulo auxiliar estritamente matemático para escalonamento (scaling) linear da força e vida dos inimigos e requisitos de XP de forma progressiva.
*   `toj_source/skills.py` & `spell.py`: Bibliotecas de habilidades com seus respectivos dicionários de requisitos de nível, custo de mana e cálculo de dano/cura.

### ⚔️ Interações e Ambiente
*   `toj_source/interactions.py`: O coração do fluxo de gameplay que processa toda a lógica do combate. Gerencia turnos de ataque normal, conjuração de habilidades, efeitos de *status* no turno de cada entidade, além do menu da loja do mercador.
*   `toj_source/map.py`: Classe modular responsável por instanciar a grade bi-dimensional (`grid`), espalhar obstáculos (paredes), alocar o jogador, monstros e a escada de saída usando a biblioteca `random`.

### 🎒 Economia e Itens
*   `toj_source/items.py`: Classes bases de instâncias coletáveis do jogo (Item, Arma, Poção).
*   `toj_source/armor.py`: Sub-classes definindo proteções específicas divididas por *slots* (Corpo, Cabeça, Pernas e Pés).
*   `toj_source/shop.py`: O sistema comercial do jogo controlando preços de custo e venda baseados na inflação natural por nível da masmorra, instanciando novas lojas.

### 🎨 Interface (UX)
*   `toj_source/toj_menu.py`: Módulo responsável pelos menus e design principal. Telas Splash animadas (com efeito *typewriter*), tela de Game Over e as estatísticas finais da jornada.
*   `toj_source/utils.py`: Funções utilitárias como leitura segura do teclado (raw input control) e a função multi-plataforma para limpar o terminal.

> **Aviso:** O minigame ("O Desafio do Oráculo" - `guesser.py`) foi descontinuado e removido do código por motivos de otimização de fluxo e consistência com as novas mecânicas base.

---

## ⚙️ Pré-requisitos e Execução

O jogo requer as seguintes bibliotecas em seu ambiente Python 3:
*   `rich` (Estilização avançada no terminal)
*   `pyfiglet` (Arte ASCII para os letreiros)

**Instalação das dependências:**
```bash
pip install rich pyfiglet
```

**Como jogar:**
```bash
python game.py
```
