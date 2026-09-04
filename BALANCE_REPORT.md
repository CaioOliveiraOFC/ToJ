# Balanceamento — rebalanceamento estrutural

Substitui o relatório anterior (PROMPT 14), que ajustava constantes de classe
sobre um modelo que divergia por construção.

## O que estava errado

A auditoria mediu, com o motor de combate real rodando headless, uma taxa de
vitória de **99% a 100% contra o monstro comum em todos os níveis e nas três
classes**. Sete causas, nenhuma delas de "número baixo demais":

| # | Causa | Evidência |
|---|---|---|
| D1 | Herói crescia em percentual composto (`+20%` de HP por nível), monstro em soma fixa (`+20` de HP) | Poder do Mago x21,8 do nível 1 ao 20; HP do monstro x4,8 |
| D2 | `rest()` restaurava tudo depois de cada vitória, a cada nível, ao equipar, ao desequipar e ao fugir | Cinco pontos; atrito zero |
| D3 | Todo combate durava 1 ou 2 turnos | Sem espaço para decisão nem para punir decisão ruim |
| D4 | 32 efeitos declarados no JSON não tinham tratamento no motor | 16 de 41 skills, 10 de 29 passivas, 6 de 11 poções |
| D5 | Um único monstro com 121 nomes; combate sempre 1 contra 1 | `weight` e `min_level` das categorias nunca eram lidos |
| D6 | Ladino ficava com 0% de chance de ser acertado a partir do nível 13 | `85 + AG_atacante - AG_defensor`, sem piso |
| D7 | Skill, cura e equipamento eram somas fixas sobre um poder que crescia | Melhor arma = 3% do poder base no nível 20 |

Baseline completa em `reports/baseline_20260904.json`.

## O modelo

**Uma razão de crescimento só.** `GROWTH_RATE = 1.12` para herói e monstro. A
razão poder-do-herói / HP-do-monstro fica constante ao longo dos 20 níveis, e a
dificuldade passa a ser controlada de propósito.

**Orçamento distribuído.** As três classes têm poder de ataque comparável no
nível 1; a identidade está em como elas gastam o resto.

| Classe | Poder | HP efetivo | Identidade | Fraqueza |
|---|---:|---:|---|---|
| Guerreiro | 89 | 581 | Ganha por atrito | Tank, que também ganha por atrito |
| Mago | 119 | 466 | Vence rápido ou não vence | Controlador, que rouba turno e mana |
| Ladino | 100 | 463 + esquiva | Escolhe quando lutar | Skirmisher, que anula a esquiva |

**Nove arquétipos de monstro**, com orçamento, comportamento, ameaça e
counterplay declarados em `src/data/monsters.json`. Todo arquétipo precisa de
pelo menos uma classe que sofre contra ele.

**Escala relativa.** Dano de skill é percentual do poder base; cura, percentual
do HP máximo; bônus de equipamento, percentual do atributo; chance de acerto usa
a diferença relativa de agilidade, com piso de 20% e teto de 95%.

**Atrito.** Concluir um andar devolve 32% dos recursos. Nada mais cura de graça.

## O que a simulação roda

A run simulada percorre os mesmos sistemas do jogo, e não só o combate:

| Sistema | Onde |
|---|---|
| Escolha de passiva a cada nível | `sim/progression.py: on_level_up` |
| Escolha de skill em nível ímpar a partir do 5 | `sim/progression.py: pick_skill` |
| Drop de item por vitória, com troca se for melhor | `sim/progression.py: collect_loot` |
| Loja entre andares: repõe cura e melhora equipamento | `sim/progression.py: visit_shop` |
| Evento aleatório de andar (Fonte, Altar) | `sim/harness.py: _apply_random_event` |
| Multiplicador de Essência por andar | `sim/progression.py: floor_essence_multiplier` |
| Buff, elixir, poção de mana e controle em combate | `sim/policies.py: smart_policy` |

Isso importa mais do que parece. Uma calibração anterior media um herói que
atravessava vinte andares **com zero passivas** e o equipamento do andar 1,
porque `while level_up(show=False)` nunca iterava — o método devolve lista vazia
quando `show=False`, mesmo tendo subido de nível. Os números daquela calibração
não valiam para o jogo que existe. `test_a_run_entrega_a_progressao_do_jogo`
existe para que isso não volte em silêncio.

## Resultado

250 runs por classe, política competente, equipamento típico
(`reports/validation_20260904.json`):

| Classe | Andar médio | Mediano | Chega ao andar 20 | Passivas ao fim | Bot que só ataca |
|---|---:|---:|---:|---:|---:|
| Guerreiro | 8,1 | 4 | 26,0% | 9,6 | andar médio 1,0 |
| Mago | 5,8 | 2 | 17,6% | 6,9 | andar médio 0,3 |
| Ladino | 8,1 | 4 | 23,6% | 9,8 | andar médio 1,0 |

- O bot que só ataca **não termina a masmorra** em nenhuma classe.
- Distância entre a melhor e a pior classe: **2,3 andares**.
- Jogar bem vale de **5,5 a 7,1 andares** de profundidade.
- Duração de combate: trash 3,4 turnos, bruiser 8-12, elite 12-17, chefe 16-24.

**A distribuição é bimodal**, e isso é um achado, não um detalhe: a maioria das
runs termina nos primeiros andares, e quem passa do andar 5 com passivas
empilhadas tende a chegar ao 20. A run é decidida cedo. Fechar essa lacuna —
fazer os andares finais voltarem a ser uma pergunta — é o próximo trabalho de
balanceamento, e depende de as passivas deixarem de ser puro acúmulo.

## Como reproduzir

```bash
python -m pytest tests/balance -q                     # rápido, 6s
python -m pytest tests/balance -q -m balance_full     # runs completas, 8s
python -m src.sim.runner run --iterations 400 --loadout expected
python -m src.sim.runner matrix --iterations 500 --levels 1,10,20
python -m src.sim.runner compare --against reports/baseline_20260904.json
```
