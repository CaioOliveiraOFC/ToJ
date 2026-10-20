# Baseline — Run/Progression Balance @ `fb321d4e`

| | |
|---|---|
| **Commit de gameplay medido** | `fb321d4e` — Starter Kit: toda nova jornada começa com exatamente uma peça Lv1 |
| **Tipo** | `Run/Progression Balance` |
| **Estado** | `pendente de calibração` |

É a primeira baseline versionada de **progressão real**: a jornada do nível 1,
com o Starter Kit, jogada pelo BotPadrão até morrer ou extrair. Ela registra a
situação atual. Não é uma meta e não foi usada para tuning.

---

## Duas réguas, dois estados

| | Combat/Class Balance | Run/Progression Balance |
|---|---|---|
| **Baseline** | `bc815fcd` | `fb321d4e` (esta) |
| **Régua** | expected loadout | jornada real com Starter Kit + BotPadrão |
| **Estado** | **FECHADA** | **PENDENTE DE CALIBRAÇÃO** |

A régua de combate mede herói contra herói e herói contra monstro, com o
equipamento esperado para o nível (`src/sim/loadouts.py`). A régua de progressão
mede a run de verdade: nível 1, uma peça de starter e o que a dungeon der depois.

**Um resultado numa régua não invalida automaticamente a outra.** Uma classe que
vai mais fundo aqui não está, só por isso, desbalanceada no combate: o
equipamento e a curva de nível que as duas réguas medem não são os mesmos.

---

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `baseline.jsonl` | As 300 runs, uma por linha. 242.074 bytes, sha256 `d1c0ebb772c98526c23eb3de50e1cab9b081893807b746d4a126525a039d56a3` |
| `run_baseline.py` | Coletor do protocolo abaixo, mais o modo `--conferir` (reexecuta runs do arquivo e compara) |
| `agrega.py` | Confere a integridade da amostra e imprime todas as métricas deste README |

O `baseline.jsonl` é a amostra original, copiada byte a byte. Ela não foi
regenerada. A ordem das linhas é a ordem em que as runs terminaram na coleta
original, e não importa: o agregador ordena por classe e seed antes de qualquer
conta. O campo `segundos` é tempo de parede e não entra em comparação.

Para reproduzir, a partir da raiz do repositório e só com a biblioteca padrão:

```
# métricas e integridade (instantâneo)
python baselines/progression/fb321d4e/agrega.py

# reexecuta as 21 extrações e confere registro a registro + Chave na extração
python baselines/progression/fb321d4e/run_baseline.py \
    --conferir baselines/progression/fb321d4e/baseline.jsonl --runs extracoes

# coleta completa nova (~16 min em 4 núcleos); nunca sobre o arquivo versionado
python baselines/progression/fb321d4e/run_baseline.py --saida /caminho/nova.jsonl
```

Os traces citados abaixo saem do próprio bot, por exemplo
`python -m tools.bot_padrao --seed 24 --classe warrior --max-floor 200`.

---

## Protocolo

- **300 runs**: 100 por classe (`warrior`, `mage`, `rogue`), **seeds 1–100**, a
  mesma faixa nas três classes.
- **BotPadrão** (`tools/bot_padrao.py`) no perfil **conservador**, sem alteração.
- **Starter Kit real**: o bot nasce por `create_player_for_new_run`, o mesmo
  caminho da tela do jogador. Isso dá nível 1, nenhum ouro, uma skill e uma peça
  do Starter Kit sorteada pelo gerador da run. A mesma seed dá o mesmo starter
  nas três classes.
- **Sem expected loadout e sem injeção de equipamento.** Nenhuma regra do jogo
  foi alterada para a medição.
- **Cada run num processo próprio** (`spawn`, um processo por tarefa). Uma run
  não herda estado de outra.
- **Teto técnico de 200 andares. Nenhuma run o atingiu** (o máximo foi 29).

O teto não participa da decisão do bot. `max_andar` é só o limite do laço de
andares em `BotPadrao.jogar`, e nenhum avaliador o lê. Cortar estes dados no
andar 20 dá exatamente o que o bot faria com o teto padrão de 20.

---

## Resultado consolidado

| Métrica | Warrior | Mage | Rogue |
|---|---:|---:|---:|
| Mortes / extrações | 92 / 8 | 94 / 6 | 93 / 7 |
| Andar médio [IC95] | 7,20 [6,0–8,5] | 5,23 [4,3–6,3] | 5,20 [4,3–6,2] |
| Mediana | 5 | 4 | 3 |
| P25 | 2 | 2 | 2 |
| P75 | 10 | 6 | 7 |
| P90 | 16,1 | 11,1 | 10,1 |
| Máximo | 29 | 23 | 22 |
| Nível final médio | 5,0 | 3,6 | 4,2 |
| Nível final mediano | 3 | 2 | 2 |
| Nível final P90 | 9 | 6 | 8 |
| Nível final máximo | 28 | 25 | 24 |
| Morte no andar 1 | 14 | 17 | 15 |
| Morte até andar 3 | 38 | 49 | 53 |
| Morte até andar 5 | 53 | 70 | 70 |
| Chegou ao andar 10 | 29 | 15 | 11 |
| Chegou ao andar 20 | 8 | 4 | 6 |

Extrações:

- Warrior: andares 19–25, níveis 23–28
- Mage: andares 18–23, níveis 21–25
- Rogue: andares 18–22, níveis 22–24

"Chegou ao andar N" quer dizer que a run entrou no andar N. Percentil por
interpolação linear. IC95 por bootstrap da média, com semente fixa (ver
`agrega.py`).

---

## Principais achados

Registrados como observação. Nenhum deles virou tuning nesta rodada.

### Early game

As mortes estão fortemente concentradas no começo:

- 46/300 runs (**15,3%**) morrem no andar 1;
- 193/300 runs (**64,3%**) morrem até o andar 5.

Há dois fenômenos:

1. **O comportamento do BotPadrão permite entrar em combate em condição ruim.**
   173 das 279 mortes (62%) começaram o combate fatal abaixo de 55% de HP. A
   mediana do HP de entrada foi 0,51.
2. **Algumas primeiras lutas são letais mesmo com HP cheio.** 6 runs (3 Mage,
   3 Rogue) morreram na primeira luta do andar 1, com 100% de HP. Os monstros
   foram Assassino das Sombras Nv.2 (três vezes), Necromante Nv.3, Aparição
   Nv.2 e Orc Nv.1.

### Decisão de combate do bot

A avaliação de lutar no mapa não considera suficientemente o oponente. A nota da
luta é `(HP − 0,35) / lutas` (`src/sim/bot/evaluators.py`). Ela depende do HP do
herói e de quantas lutas o alvo custa, e não da força do monstro.

A escada de necessidades (`src/sim/bot/decision.py`) põe PROGREDIR acima de
INVESTIR. Acima de 35% de HP, curar na Loja conta como INVESTIR e perde para
qualquer luta com nota positiva.

Exemplo, Warrior seed 24, andar 1, com 36% de HP:

- a Loja valia +1,64 (INVESTIR) e a luta valia +0,01 (PROGREDIR), e a luta venceu;
- no turno 0, o avaliador de combate do próprio bot estimou "mato em ~9, morro em ~3";
- o bot tentou fugir e morreu para um Homem-Lagarto Nv.2.

Não é bug do motor: o motor executa o que a política escolheu.

Classificação: `comportamento do bot`.

### Espiral de mergulho

26 runs chegaram ao andar 10 com nível 5 ou menos:

- Warrior: 17
- Mage: 7
- Rogue: 2

**Nenhuma dessas runs extraiu.** Todas morreram entre os andares 10 e 23.

Mecanismo observado:

1. o herói entra no andar com pouca vida;
2. evita combate e busca a saída;
3. o descanso de fim de andar devolve só 25% do HP (`FLOOR_CLEAR_RESTORE_PERCENT`);
4. a saída fica sem pagar, e a sequência de saídas não pagas reduz a Essência
   efetiva; sobra pouco ouro e pouca Essência, e o herói sobe poucos níveis;
5. o próximo andar é mais difícil.

O caso extremo é o Mage seed 59. Ele chegou ao andar 23 no nível 3, depois de 18
saídas não pagas seguidas (19 no total), passando ao largo dos monstros. Cada regra se comporta
como foi escrita.

Classificação: `progressão/dificuldade + comportamento do bot`.

### Warrior

O Warrior avança mais na dungeon real. Comparando seed a seed, com o mesmo
starter:

- desce mais que o Mage em 56 seeds, contra 29 (teste do sinal p = 0,0045);
- desce mais que o Rogue em 51 seeds, contra 34 (p = 0,08).

Mas **não há evidência de snowball de combate** como na hipótese anterior. Das
runs que chegam ao andar 10 com nível 8 ou mais, extraem:

- Warrior: 8/11
- Mage: 6/8
- Rogue: 6/7

A vantagem do Warrior parece estar em sobreviver melhor ao early game: 38 mortes
até o andar 3, contra 49 do Mage e 53 do Rogue. Ela também aparece nos
mergulhos, que são 17 das 29 chegadas do Warrior ao andar 10, e todos morrem.

A Etapa 8 (Combat/Class Balance) **não é reaberta** por causa disso.

### Starter Kit

Nenhum efeito grosseiro foi detectado. O teste é Kruskal-Wallis por permutação,
com a seed como unidade (n = 100):

- categoria × andar médio: p = 0,18
- categoria × morte até andar 3: p = 0,15
- item × andar médio: p = 0,21

A análise item a item tem amostras pequenas, de 1 a 11 seeds por item, e é
inconclusiva. Separar o efeito do starter do efeito da seed exigiria injetar o
item, o que fica fora deste protocolo. O starter não é recalibrado nesta rodada.

### Extração

A cauda das três classes é cortada pela política de extração do bot, entre os
andares 18 e 25 aproximadamente.

O Warrior seed 2 chegou ao andar 29 porque nunca cumpriu o critério de extração.
Ele tinha Chave e portal alcançável em 7 andares (7, 12, 13, 15, 19, 25 e 26).
Mas o poder da build contra o alvo da Arena ficou sempre na banda ABAIXO, com
máximo de 0,81, e o fôlego não estava esgotado em nenhum desses andares. Nessa
combinação, a matriz de extração (`src/sim/bot/evaluators.py`) manda continuar.
O nível dele estagnou em 18 a partir do andar 23, e ele morreu para um Kobold
Nv.29. Não foi bug.

### Poções

228/300 runs (**76%**) não beberam nenhuma poção.

Classificação: `inconclusivo — economia ou comportamento do bot`. Ainda não há
conclusão de balance.

---

## Classificação final

| Achado | Classificação |
|---|---|
| Lutar no mapa ignora suficientemente o oponente | comportamento do bot |
| Primeira luta letal mesmo com HP cheio | progressão/dificuldade |
| Espiral de mergulho | progressão/dificuldade + comportamento do bot |
| Warrior avança mais cedo | progressão/dificuldade |
| Cauda limitada pela extração | comportamento do bot / design |
| 76% das runs sem poção | inconclusivo |
| Starter | nenhum efeito detectável com esta amostra |
| Bug mecânico | nenhum encontrado |

> `Run/Progression Balance — pendente de calibração.`

---

## Determinismo e integridade

Na coleta:

- 6 runs (seeds 1–2 nas três classes) foram repetidas em processos
  independentes e produziram resultado idêntico;
- o log de erros ficou vazio;
- as 300 runs terminaram e nenhuma ficou presa; a mais longa levou 175 s.

Na persistência:

- `agrega.py` confere que a amostra tem:
  - exatamente 300 registros;
  - 100 por classe;
  - seeds 1–100 em cada classe;
  - nenhuma duplicata e nenhuma falta;
  - nenhuma run no teto;
  - exatamente um starter de origem `starter` por run;
  - o mesmo starter por seed nas três classes;
  - desfecho coerente com o fim.

  Se qualquer item falhar, ele recusa agregar.
- `run_baseline.py --conferir` reexecutou as 21 extrações e as runs citadas como
  exemplo (Warrior seeds 2 e 24, Mage seed 59). Todas saíram idênticas ao arquivo,
  fora `segundos`.
- Toda extração tinha uma Chave de Extração no momento de extrair. A chave é lida
  por sonda passiva em `finish_run`, porque não faz parte do registro.

---

## Relação com a baseline anterior

`reports/BASELINE_PRE_BALANCE.md` é outra medição. Ela foi feita no commit
`88190c5f`, antes do Balanceamento Global, com 3.000 runs, `max_andar` 20 e sem
Starter Kit. Os números das duas não são comparáveis um a um.
