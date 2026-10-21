# Auditoria da dungeon — Run Progression @ `4d0a9a0a`

| | |
|---|---|
| **Commit medido ("depois")** | `4d0a9a0a` — fim do bloco Dungeon / Run Progression |
| **"Antes"** | `0ab837b9` — a [auditoria do instrumento](../0ab837b9/README.md), remedida com o coletor deste diretório |
| **Tipo** | auditoria da dungeon, sobre a régua de `Run/Progression Balance` |
| **Estado** | `Run/Progression Balance — pendente de calibração` (ver [`KNOWN_ISSUES.md`](../../../KNOWN_ISSUES.md)) |

Esta é a única medição populacional do bloco Dungeon / Run Progression. Entre o
"antes" e o "depois", o BotPadrão é o mesmo: ele ficou congelado desde
`0ab837b9`. Só o jogo mudou. A auditoria `0ab837b9` não foi sobrescrita e
continua sendo o "antes".

---

## O que mudou entre as duas coletas

Só a dungeon, em três commits. O detalhe está em
[`FOUNDATION_CHANGELOG.md`](../../../FOUNDATION_CHANGELOG.md#bloco-da-dungeon--run-progression).

| Commit | KI | Mudança |
|---|---|---|
| `dfa1ebcc` | KI-002 | O glass cannon entra com os papéis avançados: só a partir do andar 4 |
| `0d0c91bc` | KI-003 | O teto de nível do monstro relativo ao herói afrouxa um nível por nível, em vez de sumir no nível 4 |
| `4d0a9a0a` | KI-004 | A Poção de Cura Pequena é linha fixa da vitrine da Loja |

Não mudaram:
- o BotPadrão, sua política e a fronteira de informação;
- as classes, as fórmulas de dano, o expected loadout e os budgets de skill;
- o Starter Kit, os preços, o loot, a Essência, a taxa de saída e a extração.

**Combat/Class.** `monsters.json`, o gerador de monstros e a Loja são
compartilhados com o `simulate_run`. Três bandas do `-m balance` mediam
dificuldade global da dungeon sob expected loadout e se moveram:
`MAX_SMART_REACH_20`, `MIN_TOTAL_ATTRITION` e `MAX_CLASS_MEAN_FLOOR`. Por decisão
do usuário, foram remedidas no fim do bloco, com valor antigo, valor novo e
protocolo registrados em `tests/balance/thresholds.py`. A paridade não se moveu:
o spread entre classes ficou em 2,04 andares, contra o limite de 4,0.

---

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `antes.jsonl` | As 300 runs do `0ab837b9`. 376.607 bytes, sha256 `3fd344152bb39c290888d3f918782da753d4d3b21c07a5267a17310166c139a3` |
| `depois.jsonl` | As 300 runs do `4d0a9a0a`. 387.553 bytes, sha256 `c449dbf357f958a88b76c54d023e71d747e1c3ace2fde4c658a162217c17ff24` |
| `run_auditoria.py` | O coletor. Roda contra qualquer árvore do jogo (`--raiz`) |
| `agrega_auditoria.py` | Confere a integridade das duas amostras e imprime todas as tabelas deste README |

Para reproduzir, a partir da raiz do repositório e só com a biblioteca padrão:

```
# tabelas e integridade (instantâneo)
python baselines/progression/4d0a9a0a/agrega_auditoria.py

# o "depois": coleta nova sobre a árvore atual; nunca sobre o arquivo versionado
python baselines/progression/4d0a9a0a/run_auditoria.py --saida /caminho/depois.jsonl

# o "antes": a mesma coleta sobre uma exportação do 0ab837b9
mkdir -p /caminho/0ab837b9 && git archive 0ab837b9 | tar -x -C /caminho/0ab837b9
python baselines/progression/4d0a9a0a/run_auditoria.py --saida /caminho/antes.jsonl \
    --raiz /caminho/0ab837b9
```

---

## Protocolo

O mesmo das réguas `fb321d4e` e `0ab837b9`:
- 300 runs: 100 por classe, seeds 1–100;
- BotPadrão no perfil conservador;
- Starter Kit real;
- sem expected loadout;
- teto técnico de 200 andares, que nenhuma run atingiu (máximo 27 no "antes", 26 no "depois");
- um processo por run.

O coletor grava os campos da auditoria do instrumento, mais sondas **passivas**:

| Campo | O que mede |
|---|---|
| `pocoes_do_loot` | poções de cura que caíram de monstro |
| `pocoes_da_fonte` | poções de cura que a Fonte devolveu |
| `essencia_efetiva`, `essencia_sorteada` | a Essência de cada andar, com e sem a penalidade |
| `taxa_por_andar` | a taxa da saída de cada andar |

As sondas embrulham funções do jogo e do driver, chamam o original uma vez e só
contam. Nenhuma consulta o RNG por conta própria.

---

## Resultado — as três classes (n = 300)

| Métrica | antes (`0ab837b9`) | depois (`4d0a9a0a`) |
|---|---:|---:|
| Mortes / extrações | 275 / 25 | 248 / 52 |
| Andar médio | 6,11 | 7,74 |
| Andar mediana · P25 · P75 · P90 · máx | 4 · 2 · 8 · 14 · 27 | 5 · 3 · 10 · 21 · 26 |
| Nível final médio · mediana · P90 · máx | 4,6 · 2 · 9,2 · 29 | 6,6 · 3 · 23 · 28 |
| Morte no andar 1 / até 3 / até 5 | 45 / 137 / 185 | 34 / 93 / 165 |
| … das mortes, fração até o andar 5 | 67% | 67% |
| Chegou ao 10 / ao 20 | 58 / 25 | 77 / 46 |
| Morte na 1ª luta do andar 1, com HP cheio | 6 | 4 |
| Nível 1 ao entrar no andar 2 | 182/255 | 178/266 |
| HP de entrada no combate fatal (mediana) | 0,50 | 0,47 |
| Combate fatal por HP de entrada: <35% · 35–55% · ≥55% | 30 · 143 · 102 | 25 · 146 · 77 |
| … dos <35%, sublevel | 29 | 25 |
| Mortes com combate fatal abaixo de 55% | 173/275 (63%) | 171/248 (69%) |
| Mortes sublevel (nível < andar) | 187 | 178 |
| Atraso ao entrar no andar 5 · 10 · 15 (média) | 1,65 · 2,38 · 0,07 | 1,38 · 1,00 · −0,44 |
| Maior atraso da run (mediana · P90 · máx) | 1 · 4 · 11 | 1 · 4 · 11 |
| Caíram 3+ atrás · voltaram a ≤ 1 | 87 · 0 | 79 · 3 |
| Caíram 2+ atrás · voltaram a ≤ 1 | 128 · 11 | 139 · 19 |
| Chegou ao 10 com nível ≤ 5 (extraíram) | 14 (0) | 7 (0) |
| Saídas não pagas por run (média) | 0,89 | 0,84 |
| Maior streak de não pagas (média · P90 · máx) | 0,74 · 2 · 9 | 0,74 · 2 · 7 |
| Essência efetiva média por andar | 1,24 | 1,29 |
| Andares na Essência do piso (0,5) | 51 | 21 |
| Ouro ganho por run (média · por andar) | 3.300 · 540 | 6.007 · 776 |
| Poções obtidas: compradas · loot · Fonte | 212 · 21 · 57 | 862 · 40 · 57 |
| Poções bebidas no mapa (total · runs sem nenhuma) | 129 · 240/300 | 523 · 159/300 |
| Itens usados em combate | 64 | 235 |
| Runs que nunca tiveram poção | 207 | 133 |
| Runs sem acesso a cura (nenhuma poção, nenhuma cura paga) | 100 | 75 |
| Mortes com poção na mochila (… com fatal < 55%) | 10 (0) | 7 (0) |
| Loja: visitas · que curaram · sem efeito | 703 · 492 · 41 | 961 · 632 · 39 |
| Combates por run (média) | 22,0 | 33,1 |

O atraso é andar menos nível, ao entrar no andar. As médias nos andares 10 e 15
são de quem chegou lá, então têm viés de sobrevivência. "Voltou a ≤ 1" quer dizer
que, depois de cair, a run entrou em algum andar no máximo 1 nível atrás dele.

### Por classe

| Métrica | Warrior | Mage | Rogue |
|---|---:|---:|---:|
| Mortes / extrações | 88/12 → 79/21 | 93/7 → 81/19 | 94/6 → 88/12 |
| Andar médio | 7,86 → 9,26 | 5,14 → 7,79 | 5,33 → 6,18 |
| Morte até o andar 5 | 48 → 43 | 67 → 55 | 70 → 67 |
| Chegou ao 10 / ao 20 | 33/12 → 34/21 | 11/7 → 25/17 | 14/6 → 18/8 |
| 1ª luta do andar 1 com HP cheio | 0 → 1 | 3 → 1 | 3 → 2 |
| Caíram 3+ atrás · voltaram | 37·0 → 29·1 | 27·0 → 25·0 | 23·0 → 25·2 |
| Chegou ao 10 com nível ≤ 5 | 9 → 3 | 4 → 3 | 1 → 1 |
| Poções bebidas no mapa | 45 → 245 | 46 → 158 | 38 → 120 |
| Runs que nunca tiveram poção | 66 → 33 | 73 → 51 | 68 → 49 |
| Andares na Essência do piso | 32 → 6 | 16 → 12 | 3 → 3 |
| Ouro por andar | 635 → 813 | 464 → 817 | 474 → 669 |

Extrações:

| | Warrior | Mage | Rogue |
|---|---|---|---|
| antes | 12: andares 20–27, níveis 21–29 | 7: andares 20–25, níveis 22–26 | 6: andares 21–24, níveis 23–26 |
| depois | 21: andares 20–25, níveis 21–27 | 19: andares 19–25, níveis 21–27 | 12: andares 19–26, níveis 21–28 |

### As seis runs da primeira luta (fixtures do KI-002)

| Run | antes | depois |
|---|---|---|
| Mage seed 16 | morreu na 1ª luta do andar 1 | ainda morre nela: Bandido Nv.2 (bruiser) |
| Mage seed 62 | morreu na 1ª luta do andar 1 | morreu no andar 6 |
| Mage seed 93 | morreu na 1ª luta do andar 1 | morreu no andar 4 |
| Rogue seed 4 | morreu na 1ª luta do andar 1 | ainda morre nela: Orc Nv.1 (bruiser) |
| Rogue seed 16 | morreu na 1ª luta do andar 1 | morreu no andar 4 |
| Rogue seed 98 | morreu na 1ª luta do andar 1 | morreu no andar 3 |

As 4 mortes de primeira luta do "depois":
- Mage 16, Bandido Nv.2 (bruiser);
- Rogue 4, Orc Nv.1 (bruiser);
- Warrior 92, Lobo Faminto Nv.2 (bruiser);
- Rogue 54, Assassino das Sombras Nv.2 (skirmisher).

Nenhuma é papel avançado. Contra um herói de nível 1 com HP cheio (200 a 300
seeds por duelo), esses duelos matam cerca de 2% a 4%. O skirmisher Nv.2 contra o
Rogue mata 16%, e essa é a fraqueza declarada da classe.

### Seed a seed

- **Extrações:** 14 mantidas, 11 perdidas, 38 novas.
- **Mergulhos:** 1 mantido, 13 saíram, 6 novos.

Mudar o jogo muda o caminho do RNG da run. A comparação vale pelo agregado.

### Casos históricos

| Caso | antes | depois |
|---|---|---|
| Warrior seed 24 | morreu no andar 13, nível 7 | extraiu no andar 20, nível 22 |
| Mage seed 59 | morreu no andar 6, nível 3 | morreu no andar 2, nível 2 |
| Warrior seed 2 | extraiu no andar 20, nível 23 | extraiu no andar 23, nível 25 |

---

## Leitura — o critério do bloco

**1. O early game ainda mata, mas não concentra quase toda a run? Em parte.**
- Ainda mata: 11% morrem no andar 1 e 55% até o andar 5.
- Mata menos runs: as mortes até o andar 5 caíram de 185 para 165, e até o
  andar 3 de 137 para 93.
- **Mas a forma não mudou: 67% das mortes acontecem até o andar 5, antes e
  depois.**
- E 178 de 266 runs ainda entram no andar 2 no nível 1.

**2. As 6 mortes de primeira luta com HP cheio diminuíram ou têm justificativa
clara? Sim.**
- Das 6 fixtures, 4 deixam de morrer na primeira luta.
- No total, 6 → 4, e as 4 de agora são duelos comuns, não papel avançado, que
  raramente matam.

**3. Cair alguns níveis atrás deixou de ser espiral praticamente irreversível?
Pouco.**
- Agora há volta: 3 de 79 runs voltaram de 3 ou mais níveis atrás (antes, 0 de
  87), e 19 de 139 voltaram de 2 ou mais (antes, 11 de 128).
- Os mergulhos caíram de 14 para 7, mas nenhum extrai.
- O degrau do nível 4 sumiu.
- Recuperar continua raro.

**4. Poções e recuperação aparecem e cabem na economia? Sim.**
- Poções compradas: 212 → 862.
- Bebidas no mapa: 129 → 523.
- Runs que nunca tiveram uma: 207 → 133.
- Das 75 runs sem nenhum acesso a cura, 53 morrem nos andares 1-2, e as 75
  somadas visitaram 11 Lojas: elas morrem antes de achar uma.

**5. O bot continua progredindo e assumindo risco? Sim.**
- Combates por run: 22,0 → 33,1.
- Mortes com combate fatal abaixo de 55% de HP: 63% → 69%.

**6. A cauda não explodiu artificialmente? Não explodiu.**
- O máximo foi de 27 para 26.
- O P90 foi de 14 para 21, e chegar ao 20 de 25 para 46 runs.
- As extrações dobraram (8% → 17%), e todas continuam entre os andares 19 e 26,
  onde a política de extração do bot corta.

**7. Alguma classe ganhou vantagem estrutural absurda? Não.**
- O Mage foi quem mais ganhou (andar médio 5,14 → 7,79), e o Rogue quem menos
  ganhou (5,33 → 6,18).
- A distância entre a melhor e a pior classe na jornada real foi de 2,7 para
  3,1 andares.
- Registrado como observação, sem tuning de classe.

**8. O Combat/Class ficou intacto? Sim, nas bandas de classe.**
- Spread de 2,04 contra o limite de 4,0, e TTK, skill gap, sorte e arquétipos
  verdes.
- As três bandas de dificuldade global foram remedidas, como decidido.

**9. Determinismo? Sim.**
- 16 runs do "depois" foram reexecutadas em processos novos e saíram
  idênticas.
- O "antes" reproduz a auditoria `0ab837b9` registro a registro.

---

## O que fica aberto

O estado de cada KI está em [`KNOWN_ISSUES.md`](../../../KNOWN_ISSUES.md).

- **KI-002 continua aberto, mais estreito.** A condenação sorteada saiu. Ficou a
  forma da curva: 2/3 das mortes até o andar 5, e a armadilha do nível 1.
- **KI-003 continua aberto.** Agora existe volta, mas ela é rara, e os
  mergulhos não extraem.
- **KI-004 fecha.** A cura apareceu e cabe na economia.
- **KI-005 continua aberto**, enquanto KI-002 e KI-003 estiverem.

---

## Determinismo e integridade

- **O "antes" reproduz a `0ab837b9`.** Nos 29 campos que o `depois.jsonl` dela
  tem, as 300 runs saíram idênticas, registro a registro, fora `segundos`. Por
  isso a comparação mede só a mudança da dungeon.
- **O "depois" é determinístico.** 16 runs foram reexecutadas em processos novos
  e comparadas campo a campo com o arquivo, fora `segundos`, sem nenhuma
  divergência:
  - as 6 fixtures da primeira luta;
  - os 3 casos históricos;
  - as duas novas mortes de primeira luta (Warrior 92, Rogue 54);
  - as 6 primeiras extrações do arquivo (Warrior seeds 2, 4, 6, 8, 9 e 12; a
    seed 2 também é caso histórico).
  - No total, 7 das 16 são extrações.
- As 600 runs terminaram, e nenhuma ficou presa.

`agrega_auditoria.py` recusa agregar se qualquer item abaixo falhar:
- as duas amostras têm 300 registros, seeds 1–100 nas três classes, sem
  duplicata;
- nenhuma run ficou no teto;
- toda run tem exatamente um starter de origem `starter`;
- o desfecho é coerente com o fim;
- o "antes" e o "depois" nasceram com o mesmo starter em cada classe e seed.
