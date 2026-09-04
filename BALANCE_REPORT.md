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

**Nove arquétipos de monstro**, cada um com ameaça e counterplay declarados em
`content/factories/archetypes.py`. Todo arquétipo precisa de pelo menos uma
classe que sofre contra ele.

**Escala relativa.** Dano de skill é percentual do poder base; cura, percentual
do HP máximo; bônus de equipamento, percentual do atributo; chance de acerto usa
a diferença relativa de agilidade, com piso de 20% e teto de 95%.

**Atrito.** Concluir um andar devolve 32% dos recursos. Nada mais cura de graça.

## Resultado

400 runs por classe, política competente, equipamento típico
(`reports/validation_20260904.json`):

| Classe | Andar médio | Chega ao andar 20 | Bot que só ataca |
|---|---:|---:|---:|
| Guerreiro | 13,9 | 12,2% | andar médio 2,3 |
| Mago | 11,6 | 16,0% | andar médio 2,0 |
| Ladino | 13,2 | 1,5% | andar médio 3,4 |

- O bot que só ataca **não termina a masmorra** em nenhuma classe.
- Distância entre a melhor e a pior classe: **2,3 andares**.
- Jogar bem vale de **9,8 a 11,6 andares** de profundidade.
- Duração de combate: trash 3-5 turnos, bruiser 6-11, elite 10-18, chefe 14-29.
- Custo de um encontro: trash 3%, bruiser 13-18%, elite 25-35%, chefe 39% da vida.

## Como reproduzir

```bash
python -m pytest tests/balance -q                     # rápido, 6s
python -m pytest tests/balance -q -m balance_full     # runs completas, 8s
python -m src.sim.runner run --iterations 400 --loadout expected
python -m src.sim.runner matrix --iterations 500 --levels 1,10,20
python -m src.sim.runner compare --against reports/baseline_20260904.json
```
