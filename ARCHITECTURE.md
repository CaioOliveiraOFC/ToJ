# ARCHITECTURE — Tales of the Journey

## As regras

1. Raiz do código em `src/`, só imports absolutos.
2. `engine/` fala com `ui/` pelo EventBus (`src/engine/events.py`). As exceções
   estão listadas abaixo.
3. Nenhuma importação cruzada entre camadas. Todas podem importar `shared/`; é
   por lá que uma camada de baixo alcança o que está acima.
4. Apresentação só em `ui/`: nem `print()`, nem `rich` fora dela. É o que mantém
   `sim/` headless.
5. **Fórmula é código, valor é dado.** O nome de um monstro, o custo de uma skill
   ou o multiplicador de um arquétipo vão para o JSON. Números de balanceamento
   que não cabem no JSON ficam em `shared/constants.py`, com nome.
6. `safe_get_key()` é o único ponto de entrada de teclado.

`tests/test_architecture.py` verifica 1, 3, 4 e 5. Regra que só existe em
Markdown é regra que ninguém checa.

## Camadas

```
ui/ ←── engine/ ←── mechanics/ ←── entities/
         ↑        ↑               ↑
        sim/   content/         shared/
                  ↑
               storage/
                  ↑
                data/

multiplayer/ ──→ engine/arena_setup ──→ storage/, content/
     └─────────→ mechanics/pvp_duel   (nunca ui/ nem sim/; rede pelo pacote websockets)
```

| camada | responsabilidade | pode importar |
|---|---|---|
| `shared/` | tipos, constantes, fórmulas, tópicos, efeitos | nada |
| `data/` | leitura dos JSON | shared/ |
| `entities/` | estado (Player, Monster) | shared/ |
| `mechanics/` | regras de combate e matemática | entities/, shared/ |
| `content/` | catálogos e fábricas | entities/, mechanics/, shared/, data/ |
| `sim/` | simulação headless: medir balanceamento e a IA dos adversários da Arena | content/, mechanics/, entities/, shared/, data/ |
| `storage/` | save/load | content/, entities/, shared/, data/ |
| `engine/` | orquestração | todas |
| `ui/` | apresentação e input | shared/, content/, entities/, storage/, data/ |
| `multiplayer/` | versão, protocolo e servidor autoritativo da Arena | engine/, content/, mechanics/, entities/, storage/, shared/, data/ — nunca ui/ nem sim/ |

Imports sob `TYPE_CHECKING` não contam: não existem em tempo de execução.

## EventBus

`engine/` publica um tópico; `ui/` registrou um handler para ele. Os tópicos
vivem em `src/shared/combat_topics.py`.

```python
bus = EventBus()
register_ui_handlers(bus)  # ui/ assina
bus.publish(topics.UI_OPEN_SHOP, {...})  # engine/ publica
```

### Exceções à regra 2

`engine/` pode importar direto de `ui/`: as funções `screens.render_*` e
`arena_screens.render_*`, `clear_screen()`, `safe_get_key()`, os dois
`register_*_handlers()` e os fluxos de menu inicial (`toj_menu`), que rodam antes
do laço de jogo existir.

`sim/runner.py` pode usar `print()`: é CLI de desenvolvimento, e importar `ui/`
de dentro de `sim/` quebraria a regra maior de a simulação ser headless.

## Responsabilidade por módulo

Os módulos onde a responsabilidade não é óbvia pelo nome da camada:

| módulo | responsabilidade |
|---|---|
| `shared/formulas.py` | a matemática fundamental: crescimento, dano, acerto, mitigação |
| `shared/economy.py` | **aritmética** econômica pura. Recebe a renda como número; nunca a calcula, porque isso exigiria conhecer o catálogo |
| `shared/effects.py` | `fx.combat_modifier(entidade, nome)` — o **funil único** que soma buff + passiva + equipamento. Nada multiplica dano fora dele |
| `shared/effect_core.py` | o catálogo global de efeitos: famílias, empilhamento, duração |
| `shared/interactions.py` | as 16 **leis** sobre pares de efeitos. Sem estado, sem ator, sem fonte |
| `content/economy.py` | a **ponte**: conhece o catálogo e o gerador, e é o único lugar que calcula `expected_floor_income`, `reroll_cost`, `exit_fee`, custos do Ferreiro e teto de juros |
| `content/factories/monsters.py` | **fonte única da população do andar** (`routine_monster_count`, `floor_role_plan`). Mapa e simulador leem daqui — é o que garante que os dois meçam o mesmo andar |
| `content/factories/features.py` | sorteio dos serviços do andar com pity (`roll_features`). Muta os contadores de seca do jogador, que pertencem à run |
| `content/floor_exit.py` | a saída: cobra a taxa (`use_exit`), mantém o `unpaid_exit_streak` e converte o roll em Essência efetiva (`effective_essence`). Não existe dívida |
| `content/forge.py` | o Ferreiro: cobra e delega. `+N`, gemas e encantamentos continuam implementados em `content/items.py` |
| `content/starter_kit.py` | a pool do Starter Kit (`data/starter_kit.json`), validada contra o catálogo, e o sorteio categoria → item. Quem entrega o starter na nova jornada é `engine/game_logic.create_player_for_new_run`; `create_player_from_data` segue neutro |
| `engine/map.py` | a grade do andar: casas de monstro, evento, serviço e saída, e a serialização delas no save |
| `engine/map_analysis.py` | medição da geometria do andar (Dijkstra por `(combates, passos)`). Ferramenta de auditoria, não regra de jogo |
| `sim/` | simulação headless. Roda o mesmo `mechanics/battle.py`, lê as mesmas fontes de população e de serviços, e nunca importa `engine/` nem `ui/`. `sim/loadouts.py` é o `expected loadout`, a régua sintética do Combat/Class Balance |
| `mechanics/pvp_duel.py` | o **duelo da Arena**: rodada de decisões simultâneas, reserva de MP, ordem travada, cancelamento por controle ou morte, resultado MD1. É orquestração própria sobre `combat.py`, sem laço interno nem teto de rodadas. `run_battle` continua sendo só o PvE |
| `mechanics/pvp_initiative.py` | a iniciativa do duelo: a fórmula aprovada, a **referência global** por nível (`foundation_reference`: a média das três classes pelo crescimento canônico, sem número próprio) e o desempate pela semente. Os dois são o padrão do duelo e continuam injetáveis para teste |
| `content/gladiator.py` | a preparação do gladiador: só personagem extraído, cópia normalizada, sem consumível |
| `engine/arena_setup.py` | o gladiador a partir do snapshot do save, pelo caminho canônico de reconstrução (`player_from_save_data`); a lista de elegíveis (slots com extração) e a gravação do equipamento confirmado, só no slot do próprio gladiador |
| `engine/arena_mode.py` | a **Arena offline** no terminal (o modo competitivo do ToJ 1.0): seleção do gladiador, preparação, escolha do adversário na população, ficha pública, duelo do jogador contra a IA, resultado, revanche. Só desenha, lê teclas e pergunta; a regra é do motor do duelo. Não importa `multiplayer/` |
| `engine/arena_populacao.py` | a **população offline**: lê o catálogo de `data/arena_populacao/` e confere cada adversário antes da partida (sha256 do índice, reconstrução canônica, extração, classe, ida e volta). Quem gera o catálogo é `tools/arena_offline_geracao.py` |
| `engine/arena_historico.py` | os pontos de extensão do MMR: o `ResultadoDaPartida`, o histórico da sessão, a `Classificacao` (hoje a nula) e a identidade estável do gladiador do jogador. Não calcula rating nem grava em disco |
| `ui/arena_screens.py` | as telas da Arena, desenhadas a partir da `DuelView` do motor: o que a tela mostra é o que o controlador recebe |
| `sim/ia_estrategica.py` | a **IA estratégica** dos adversários da Arena: decide só pela `DuelView`, joga continuações curtas no próprio motor sobre cópias e avalia o fim com as fórmulas canônicas de dano. Não é regra; não muda o motor |
| `sim/pvp_controllers.py` | controladores de referência do duelo (roteiro, primeira skill legal). Provam a interface |
| `multiplayer/versao.py` | a versão que a instalação **declara**: jogo, protocolo, regras de combate, esquema do gladiador. Fica fora dos hashes |
| `multiplayer/manifesto.py` | o **escopo do gameplay** (`ESCOPO`, cinco grupos), os hashes, a `Identidade` e as conferências do gate: código contra manifesto, um identificador para um conteúdo, imutabilidade do publicado. `manifesto_da_instalacao` é o único caminho de produção para a identidade |
| `multiplayer/compatibilidade.py` | a decisão de conexão: identidade **idêntica** ou recusa com "atualização obrigatória". Não existe versão próxima |
| `multiplayer/protocolo.py` | as mensagens em JSON, sem tolerância. Do cliente, só identidade, comandos de sessão e ação (`kind`, `skill_id`); do servidor, a `DuelView`, a rodada pública (sem iniciativa) e o desfecho |
| `multiplayer/gladiadores.py` | o gladiador no servidor: esquema versionado, validação antes e depois da reconstrução canônica, migrações explícitas (`MIGRACOES`) e o `AcervoDeGladiadores` |
| `multiplayer/servidor.py` | o **servidor autoritativo**: login, sessão autenticada, posse conferida, sala direta e fila simples, partida presa à versão, legalidade pelo motor, `Resultados`, drenagem, retomada por replay conferido, anulação e a `Frota` da atualização. Recebe `(conexão, texto)`, devolve envios; não conhece rede |
| `multiplayer/contas.py` | a **identidade**, independente do duelo: a interface `Autenticador`, senha em scrypt, tokens assinados (HMAC-SHA256) com expiração e `ContasLocais`, a implementação mínima de desenvolvimento |
| `multiplayer/registro.py` | a **propriedade**: o registro persistente de gladiadores com dono e origem; só entra por importação de origem confiável (`importar_da_copa`, conferida pelo sha256 publicado); sem transferência nem cópia |
| `multiplayer/rede.py` | o **transporte WebSocket** (WSS fora do loopback): servidor asyncio com fila de saída por conexão, limites de tamanho e de conexões, prazo para autenticar, fechamento por abuso, logger sem o conteúdo dos quadros; cliente síncrono. Só move texto |
| `multiplayer/cliente.py`, `multiplayer/transporte.py` | o cliente de referência (entrega a `DuelView` a um `DuelController` e devolve só a ação) e o transporte em processo (`RedeLocal`), que faz o papel da rede nos testes |
| `tools/toj_multiplayer.py` | o **humano × humano no terminal**: administração (conta, importação de gladiador), servidor e cliente. É ferramenta, por isso pode imprimir; a regra está toda em `src/multiplayer/` |
| `tools/multiplayer_manifesto.py` | o **gate de publicação** (`verificar`, `gerar`), lendo as tags `v<versão>` do git. É o passo que o CI roda |

**Tudo o que decide uma partida multiplayer está no manifesto.** O escopo
(`multiplayer/manifesto.ESCOPO`) não é uma lista de boa-fé: um teste sobe o
servidor num processo limpo, joga uma partida e reprova se algum módulo de `src/`
carregado estiver fora dele. Código novo que o servidor passe a usar entra no
escopo, ou o teste fica vermelho.

**Fonte única é regra, não estilo.** Renda do andar, população do andar, custo de
reroll, preços do Ferreiro e penalidade de Essência vivem cada um em exatamente
uma função. Copiar a fórmula para o simulador ou para a UI é o defeito que já
produziu um simulador medindo um andar que o jogo não gera.

## Onde está a verdade

| assunto | fonte |
|---|---|
| matemática fundamental | `src/shared/formulas.py` |
| valores de balanceamento | `src/shared/constants.py` e `src/data/*.json` |
| arquitetura | este arquivo |
| design do jogo | `GAME_DESIGN.md` |
| decisões que não mudam de passagem | `GAMEPLAY_CONTRACTS.md` |
| comportamento | a suíte padrão, `python -m pytest -q` |
| balanceamento de combate e classe | `python -m pytest -q -m balance` e `src/sim/` |
| medições de referência | `BASELINES.md`, que aponta para cada uma (ex.: `baselines/progression/`) |
| problemas abertos | `KNOWN_ISSUES.md` |
| versão multiplayer | `src/multiplayer/versao.py` e o manifesto em `src/multiplayer/manifestos/` |
| compatibilidade multiplayer | `python tools/multiplayer_manifesto.py verificar` e `tests/test_multiplayer_*.py` |
| como jogar em rede | `MULTIPLAYER.md` |

Nada além disso deve tentar ser uma segunda fonte de verdade.
