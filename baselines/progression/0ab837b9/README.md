# Auditoria do instrumento — BotPadrão corrigido @ `0ab837b9`

| | |
|---|---|
| **Commit medido ("depois")** | `0ab837b9` — fim do bloco que corrigiu o BotPadrão |
| **"Antes"** | `fb321d4e` — a [primeira baseline real](../fb321d4e/README.md), remedida com o mesmo coletor |
| **Tipo** | auditoria do instrumento, sobre a régua de `Run/Progression Balance` |
| **Estado** | `Run/Progression Balance — pendente de calibração` |

Esta é uma **auditoria do instrumento**, e não uma baseline nova do jogo. Entre o
"antes" e o "depois", o jogo é o mesmo; só o piloto mudou. Ela responde a uma
pergunta: o que, na `fb321d4e`, era política do BotPadrão, e o que sobra para a
dungeon?

A baseline `fb321d4e` não foi sobrescrita e continua sendo o registro do "antes".
Nenhum número desta auditoria virou tuning.

---

## O que mudou entre as duas coletas

Só o BotPadrão, em quatro commits. O detalhe está em
[`FOUNDATION_CHANGELOG.md`](../../../FOUNDATION_CHANGELOG.md#bloco-do-instrumento--botpadrão-corrigido-e-auditado).

| Commit | Correção |
|---|---|
| `9ef74639` | KI-001: a Loja só promete a cura de HP que o orçamento real paga |
| `7c08bdec` | KI-004, parte do bot: poção por necessidade observada |
| `7b9734c3` | KI-003, parte do bot: a descida sem pagar deixa de ser estratégia |
| `0ab837b9` | KI-006: intenção explícita para as 23 famílias de passiva |

Nenhuma regra do jogo mudou: classes, monstros, atributos, dano, HP, Starter
Kit, loot, mapa, preços, economia, Essência, saída, extração e expected loadout
ficaram como estavam.

**Um acoplamento.** As políticas de passiva do `0ab837b9` também são as do
`simulate_run`, a régua do Combat/Class Balance. Por isso o `pytest -m balance`
rodou como portão antes do commit: 118 passed, 0 falhas.

---

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `antes.jsonl` | As 300 runs do `fb321d4e`. 317.619 bytes, sha256 `8a31224f869253e634793ac33b47b0a7b611c484b7c0c416d4b2b256c5b2d859` |
| `depois.jsonl` | As 300 runs do `0ab837b9`. 317.801 bytes, sha256 `053afcb0c324a8cea771a540e7930a79375bbc7d54957199146d1a105301d08a` |
| `run_auditoria.py` | O coletor. Roda contra qualquer árvore do jogo (`--raiz`) |
| `agrega_auditoria.py` | Confere a integridade das duas amostras e imprime todas as tabelas deste README |

O campo `segundos` é tempo de parede e não entra em comparação. O agregador
ordena por classe e seed antes de qualquer conta.

Para reproduzir, a partir da raiz do repositório e só com a biblioteca padrão:

```
# tabelas e integridade (instantâneo)
python baselines/progression/0ab837b9/agrega_auditoria.py

# o "depois": coleta nova sobre a árvore atual; nunca sobre o arquivo versionado
python baselines/progression/0ab837b9/run_auditoria.py --saida /caminho/depois.jsonl

# o "antes": a mesma coleta sobre uma exportação do fb321d4e
mkdir -p /caminho/fb321d4e && git archive fb321d4e | tar -x -C /caminho/fb321d4e
python baselines/progression/0ab837b9/run_auditoria.py --saida /caminho/antes.jsonl \
    --raiz /caminho/fb321d4e
```

---

## Protocolo

O mesmo da `fb321d4e`:

- **300 runs**: 100 por classe (`warrior`, `mage`, `rogue`), seeds 1–100.
- **BotPadrão no perfil conservador.**
- **Starter Kit real**, por `create_player_for_new_run`. A mesma seed dá o mesmo
  starter no "antes" e no "depois", e o agregador recusa agregar se não der.
- **Sem expected loadout** e sem injeção de equipamento.
- **Cada run num processo próprio** (`spawn`, um processo por tarefa).
- **Teto técnico de 200 andares.** Nenhuma run o atingiu: o máximo foi 29 no
  "antes" e 27 no "depois".

O coletor grava os mesmos campos do `run_baseline.py` da `fb321d4e`, mais sondas
**passivas**:

| Campo | O que mede |
|---|---|
| `lojas`, `lojas_inuteis` | visitas à Loja, e as que não mudaram nada: nem ouro, nem HP, nem poção na mochila |
| `lojas_que_curaram` | visitas que compraram recuperação de HP |
| `pocoes_compradas` | poções de cura que entraram na mochila na Loja |
| `pocoes_na_mochila_ao_fim` | poções de cura que sobraram quando a run acabou; numa morte, as que ele não usou |
| `max_streak_nao_pagas` | maior sequência de saídas não pagas da run |
| `familias_passivas` | o `effect_type` de cada passiva escolhida |
| `acoes` | quantas vezes cada verbo de combate foi escolhido |

As sondas embrulham métodos do driver e só leem estado. Nenhuma consulta o RNG.

---

## Resultado — as três classes (n = 300)

| Métrica | antes (`fb321d4e`) | depois (`0ab837b9`) |
|---|---:|---:|
| Mortes / extrações | 279 / 21 | 275 / 25 |
| Andar médio | 5,88 | 6,11 |
| Andar mediana · P25 · P75 · P90 · máx | 4 · 2 · 8 · 12,1 · 29 | 4 · 2 · 8 · 14 · 27 |
| Nível final médio · mediana · P90 · máx | 4,3 · 2 · 8 · 28 | 4,6 · 2 · 9,2 · 29 |
| Morte no andar 1 / até 3 / até 5 | 46 / 140 / 193 | 45 / 137 / 185 |
| Chegou ao 10 / ao 20 | 55 / 18 | 58 / 25 |
| Morte na 1ª luta do andar 1, com HP cheio | 6 | 6 |
| HP de entrada no combate fatal (mediana) | 0,51 | 0,50 |
| Combate fatal por HP de entrada: <35% · 35–55% · ≥55% | 1 · 172 · 106 | 30 · 143 · 102 |
| … dos <35%, sublevel (nível < andar) | 1 | 29 |
| Mortes com combate fatal abaixo de 55% | 173/279 (62%) | 173/275 (63%) |
| Poções bebidas no mapa (total · runs sem nenhuma) | 314 · 228/300 | 129 · 240/300 |
| Itens usados em combate (total) | 64 | 64 |
| Mortes com poção de cura na mochila (poções levadas) | 8 (12) | 10 (17) |
| … dessas, com combate fatal abaixo de 55% | 5 | 0 |
| Extrações com poção de cura na mochila | 11/21 | 24/25 |
| Loja: visitas · que curaram · poções compradas | 627 · 461 · 338 | 703 · 492 · 212 |
| Loja: visitas sem efeito nenhum | 59 (9%) | 41 (6%) |
| Saídas não pagas por run (média) | 1,23 | 0,89 |
| Maior streak de não pagas (média · P90 · máx) | 0,98 · 3 · 18 | 0,74 · 2 · 9 |
| Chegou ao 10 com nível ≤ 5 (extraíram) | 26 (0) | 14 (0) |
| Combates por run (média) | 19,2 | 22,0 |

"Chegou ao andar N" quer dizer que a run entrou no andar N. Percentil por
interpolação linear. O "nível ao entrar no andar 10" é `nivel_por_andar[9]`.

### Por classe

| Métrica | Warrior antes → depois | Mage antes → depois | Rogue antes → depois |
|---|---:|---:|---:|
| Mortes / extrações | 92/8 → 88/12 | 94/6 → 93/7 | 93/7 → 94/6 |
| Andar médio | 7,20 → 7,86 | 5,23 → 5,14 | 5,20 → 5,33 |
| Morte até o andar 5 | 53 → 48 | 70 → 67 | 70 → 70 |
| Chegou ao 10 / ao 20 | 29/8 → 33/12 | 15/4 → 11/7 | 11/6 → 14/6 |
| Combate fatal abaixo de 55% | 66% → 70% | 60% → 67% | 60% → 52% |
| Chegou ao 10 com nível ≤ 5 | 17 → 9 | 7 → 4 | 2 → 1 |
| Saídas não pagas por run | 1,69 → 1,33 | 1,24 → 0,83 | 0,75 → 0,52 |
| Poções bebidas no mapa | 109 → 45 | 105 → 46 | 100 → 38 |
| Combates por run | 24,1 → 30,2 | 15,8 → 16,9 | 17,7 → 18,9 |

Extrações, por andares e níveis:

| | Warrior | Mage | Rogue |
|---|---|---|---|
| antes | 8: andares 19–25, níveis 23–28 | 6: andares 18–23, níveis 21–25 | 7: andares 18–22, níveis 22–24 |
| depois | 12: andares 20–27, níveis 21–29 | 7: andares 20–25, níveis 22–26 | 6: andares 21–24, níveis 23–26 |

### Famílias de passiva escolhidas

O BotPadrão escolhe pela política `survival`. As famílias marcadas com * são as
10 que ficavam sem preferência até a decisão D3.

| Família | antes | depois |
|---|---:|---:|
| max_hp | 225 | 282 |
| life_steal * | 4 | 125 |
| damage_reduction | 116 | 124 |
| defense | 101 | 97 |
| strength | 87 | 80 |
| crit_chance | 100 | 76 |
| agility | 95 | 72 |
| max_mp | 73 | 59 |
| status_resistance * | 2 | 46 |
| precision * | 4 | 44 |
| mana_regen * | 4 | 17 |
| potion_heal_bonus | 21 | 15 |
| magic * | 7 | 14 |
| damage_percent * | 4 | 12 |
| evasion | 12 | 6 |
| crit_damage * | 8 | 5 |
| death_ignore | 4 | 2 |
| stun_chance | 19 | 1 |
| fear_chance * | 13 | 1 |
| bleed_chance * | 7 | 1 |
| essence_bonus | 48 | 0 |
| gold_drop_bonus | 18 | 0 |
| poison_chance * | 8 | 0 |
| **as 10 antes neutras** | **61/980 (6%)** | **265/1079 (25%)** |

### Seed a seed

Mesma classe, mesma seed, mesmo starter.

- **Extrações:** 10 mantidas, 11 perdidas, 15 novas.
- **Mergulhos** (andar 10 com nível ≤ 5): 6 mantidos, 20 saíram, 8 novos.
- **As 29 mortes sublevel com combate fatal abaixo de 35%:**
  - todas também morriam no "antes";
  - andar médio 7,69 → 7,17;
  - 15 morrem mais raso, 3 no mesmo andar e 11 mais fundo.

Mudar uma decisão muda o caminho do RNG da run dali em diante. Por isso o
desfecho de uma seed isolada não é estável entre instrumentos, e a comparação
vale pelo agregado, não pelo par de seeds.

### Casos históricos

São traces de regressão, não critério de sucesso.

| Caso | antes | depois |
|---|---|---|
| Warrior seed 24 | morreu no andar 1, nível 1 | morreu no andar 13, nível 7, 3 saídas não pagas; 4 visitas à Loja, nenhuma sem efeito |
| Mage seed 59 | morreu no andar 23, nível 3, 19 saídas não pagas | morreu no andar 6, nível 3, 2 saídas não pagas |
| Warrior seed 2 | morreu no andar 29, nível 18, 6 saídas não pagas | extraiu no andar 20, nível 23, 0 saídas não pagas |

---

## Leitura — as nove perguntas

**1. O BotPadrão parou de desperdiçar recuperação que não podia pagar? Sim.**
- Por construção: a Loja só promete cura de HP quando o primeiro passo cabe no
  orçamento real, pela mesma regra de compra. Um teste de paridade confere o
  prometido contra a compra real.
- As visitas sem efeito caíram de 59 (9%) para 41 (6%), e as que curaram subiram
  de 461 para 492.
- As 41 que sobram não vêm da promessa de cura de HP, que agora só existe
  quando a compra real a executa. O fato da poção não promete estoque: a Loja
  sorteia a vitrine na visita.

**2. Usa poções e recuperação sem virar conservador demais? Sim, sem sinal de
excesso.**
- Bebe menos no mapa (314 → 129) porque deixou de beber sem necessidade e com a
  cura transbordando.
- Não guarda a cura de que precisava antes de entrar na luta que o mata:
  - mortes com poção na mochila foram de 8 para 10;
  - nenhuma das 10 começou o combate fatal abaixo de 55% de HP;
  - no "antes", 5 das 8 tinham começado.
- A reserva que sobra sai com a run: extrações com poção na mochila foram de
  11/21 para 24/25.
- A faixa de 35–55% do combate fatal caiu (pergunta 3), e as visitas à Loja que
  curaram subiram.
- O uso continua baixo: 80% das runs não bebem no mapa. Com a política corrigida,
  isso fica no KI-004, como aquisição.

**3. A proporção de combates fatais iniciados com HP baixo caiu? No agregado,
não.**
- A faixa de 35–55% caiu de 172 para 143 (−17%).
- Mas surgiu a faixa abaixo de 35%: de 1 para 30, sendo 29 sublevel. São as
  lutas que a regra do KI-003 manda aceitar.
- Abaixo de 55% ficam 62% → 63%, e a mediana do HP de entrada vai de 0,51 para
  0,50.

**4. A espiral de mergulho caiu de forma material? Sim.**
- Mergulhos até o andar 10 no nível 5 ou menos: 26 → 14.
- Saídas não pagas por run: 1,23 → 0,89.
- Maior streak: máximo 18 → 9, P90 3 → 2.
- **Mas nenhum mergulho extrai, antes ou depois.** O que sobra é a espiral sem
  fôlego, em que sair é a recuperação que existe (KI-003).

**5. O bot ainda luta e progride? Sim.**
- Combates por run: 19,2 → 22,0.
- Andar médio: 5,88 → 6,11.
- Chegou ao 10: 55 → 58. Chegou ao 20: 18 → 25.
- Extrações: 21 → 25.
- Mortes até o andar 5: 193 → 185.
- Exceção: o Mage chega ao andar 10 menos vezes (15 → 11), embora chegue mais ao
  20 (4 → 7).

**6. As 23 famílias de passiva participam de decisões intencionais? Sim.**
- Por construção: toda política ordena as 23, e um teste exige isso.
- Na população, as 10 antes neutras foram de 6% para 25% das escolhas. Roubo de
  vida (4 → 125), resistência a status (2 → 46) e Precisão (4 → 44) entram
  onde a `survival` pede.
- Antes, Essência, ouro e atordoamento ficavam no fim da `survival`, mas
  ganhavam de qualquer família sem preferência. Agora perdem para as que a
  intenção pede: 48 / 18 / 19 → 0 / 0 / 1.

**7. Algum comportamento novo claramente patológico apareceu? Nenhum claro. Há
três observações, registradas para o bloco da dungeon:**
- **As 29 mortes sublevel abaixo de 35%.** São o custo de a regra do KI-003
  usar a luta média observada. Todas essas runs já morriam no "antes", e
  nenhuma era extração. A alternativa era o mergulho, que não extrai.
- **O Mage seed 59 morre no andar 6 em vez do 23.** O desfecho é o mesmo, com
  menos andares de descida sem progresso. Era a troca pretendida.
- **O Mage tem mais mortes com combate fatal abaixo de 55%** (60% → 67%) e chega
  menos ao andar 10.

**8. O bot continua determinístico? Sim.**
- As duas amostras foram coletadas duas vezes. Nas 600 runs, todos os campos
  saíram idênticos, fora `segundos` e o campo que a segunda coleta acrescentou.
- O "antes" reproduz a `fb321d4e` registro a registro.
- Os testes de determinismo do bot continuam verdes.

**9. Alguma fronteira de informação foi quebrada? Não.**
- `TargetView` não mudou: casa, passos, extras e chefe, sem identidade do
  monstro.
- Os testes da fronteira não foram alterados.
- Os dois campos novos são fatos da Loja (`ServiceView.cura_hp` e
  `ServiceView.pocao_pagavel`). Eles saem do orçamento do próprio herói e do
  catálogo de preços e desbloqueios. Nenhum vem da vitrine sorteada ou do RNG.

---

## O que sobrou para a dungeon

Estes sintomas sobreviveram ao instrumento corrigido. O registro está em
[`KNOWN_ISSUES.md`](../../../KNOWN_ISSUES.md), e a ordem do bloco em
[`NEXT_PHASE.md`](../../../NEXT_PHASE.md).

- **KI-002: letalidade do early game.** As mesmas 6 mortes na primeira luta do
  andar 1 com HP cheio. 15,0% das runs morrem no andar 1, e 61,7% até o 5.
- **KI-003: a espiral sem fôlego.** 14 mergulhos, nenhum extrai. Inclui as 29
  mortes sublevel abaixo de 35%.
- **KI-004: aquisição de poções.** 80% das runs não bebem nenhuma poção no mapa,
  com a política corrigida.
- **KI-005: calibração global.**

> `Run/Progression Balance — pendente de calibração.`

---

## Determinismo e integridade

- **As duas coletas foram feitas duas vezes**, em processos independentes.
  - A segunda existiu para acrescentar o campo passivo
    `pocoes_na_mochila_ao_fim`.
  - Nas 600 runs, todos os outros campos saíram idênticos aos da primeira, fora
    `segundos`.
  - Os arquivos versionados são os da segunda.
- **O "antes" reproduz a `fb321d4e`.** Nos campos que o `baseline.jsonl` dela
  tem, as 300 runs saíram idênticas, registro a registro, fora `segundos`. Por
  isso a comparação mede só a mudança do instrumento.
- As 600 runs terminaram, e nenhuma ficou presa.

`agrega_auditoria.py` recusa agregar se qualquer item abaixo falhar:
- as duas amostras têm exatamente 300 registros;
- cada amostra tem seeds 1–100 nas três classes, sem duplicata e sem falta;
- nenhuma run ficou no teto;
- toda run tem exatamente um starter de origem `starter`;
- o desfecho é coerente com o fim;
- o "antes" e o "depois" nasceram com o mesmo starter em cada classe e seed.
