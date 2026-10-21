# Known Issues

Só problemas **abertos**. Histórico resolvido fica em
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md) e nas marcas `[corrigido]`
de [`GAME_DESIGN.md`](GAME_DESIGN.md).

Cada item traz uma classificação, que é a taxonomia da baseline: bug/mecânica,
progressão/dificuldade, comportamento do bot, starter ou inconclusivo. Nenhum
item aqui afirma qual mudança resolve o problema; isso é trabalho de
[`NEXT_PHASE.md`](NEXT_PHASE.md).

A evidência numérica está em três lugares:

- [`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md):
  a primeira baseline real, medida com o instrumento antigo;
- [`baselines/progression/0ab837b9/README.md`](baselines/progression/0ab837b9/README.md):
  a auditoria do instrumento corrigido;
- [`baselines/progression/4d0a9a0a/README.md`](baselines/progression/4d0a9a0a/README.md):
  a auditoria da dungeon, que é o retrato atual.

> **Fechados:** KI-001 e KI-006 pela auditoria do instrumento
> ([changelog](FOUNDATION_CHANGELOG.md#bloco-do-instrumento--botpadrão-corrigido-e-auditado)),
> e KI-004 pela auditoria da dungeon
> ([changelog](FOUNDATION_CHANGELOG.md#bloco-da-dungeon--run-progression)).
> A numeração não é reaproveitada.

---

## KI-002 — a largada concentra as mortes

**Classificação:** `Run/Progression Balance`. A parte da condenação sorteada foi
corrigida em `dfa1ebcc`.

**O que saiu.** Um encontro comum sorteado no começo não é mais condenação antes
de qualquer decisão. O glass cannon, que matava quase metade das runs dos
andares 1-3, entra com os papéis avançados a partir do andar 4.
- Mortes na primeira luta do andar 1 com HP cheio: 6 → 4.
- As 4 que sobram são duelos comuns (bruiser, skirmisher) que, repetidos com
  outras seeds, matam de 2% a 16%.
- Das 6 runs históricas, 4 deixaram de morrer nessa luta.

**O que sobreviveu (auditoria `4d0a9a0a` contra `0ab837b9`):**
- A largada mata menos runs: andar 1 45 → 34, até o 3 137 → 93, até o 5
  185 → 165.
- **Mas a forma não mudou:** 67% das mortes acontecem até o andar 5, antes e
  depois. 55% das runs morrem até ali.
- **A armadilha do nível 1:** 178 de 266 runs entram no andar 2 ainda no nível 1.
  - O nível 2 custa 140 de XP.
  - O andar 1 tem 3 monstros, que pagam cerca de 54 cada com a Essência média.
  - Subir no andar 1 exige limpá-lo inteiro no nível 1, sem cura.

**Ainda não concluído:** o que responde por essa forma. Os candidatos são o
começo da curva de XP, a largada real contra o expected loadout (uma peça contra
um kit) e o atrito dos papéis que ficaram nos andares 1-3. Nada disso está
decidido.

## KI-003 — espiral de mergulho, parte de progressão

**Classificação:** `Run/Progression Balance`.
- A parte do BotPadrão foi corrigida em `7b9734c3`.
- O degrau do teto de nível do monstro foi corrigido em `0d0c91bc`.

**O que saiu.** O teto de nível do monstro relativo ao herói não some mais no
nível 4. A folga cresce um nível por nível, e quem estava atrasado e subia de
nível não é mais premiado com monstros 5 a 10 níveis acima.

**O que sobreviveu (auditoria `4d0a9a0a` contra `0ab837b9`):**
- Voltar de 3 ou mais níveis atrás para no máximo 1: 0 de 87 → 3 de 79.
- De 2 ou mais: 11 de 128 → 19 de 139.
- Agora existe volta, mas ela é rara.
- Runs que chegam ao andar 10 no nível 5 ou menos: 14 → 7, e **nenhuma extrai**.
- Maior atraso da run: P90 de 4 e máximo de 11, sem mudança.
- Andares com a Essência no piso de 0,5: 51 → 21.

Cair para trás continua caro, e é de propósito: o monstro continua acima do
herói, contornar e a saída não paga custam o que custavam. O que fica aberto é
quanto de volta o jogo deve oferecer. Hoje ela existe e é rara.

Relacionado, mas separado: a decisão de design ainda aberta sobre o chefe ser
contornável ([`GAME_DESIGN.md`](GAME_DESIGN.md), D4).

## KI-005 — calibração global de progressão pendente

**Classificação:** `Run/Progression Balance`.

> **`Run/Progression Balance — pendente de calibração.`**

A jornada real foi medida depois do bloco da dungeon (auditoria `4d0a9a0a`):
- 17% das runs extraem (eram 8%);
- o andar médio é 7,7;
- a cauda vai até o andar 26.

A calibração continua aberta enquanto KI-002 e KI-003 estiverem. Eles são as
partes conhecidas, não a lista inteira.

**As bandas de dificuldade global do `-m balance`** — `MAX_SMART_REACH_20`,
`MIN_TOTAL_ATTRITION` e `MAX_CLASS_MEAN_FLOOR`, medidas sob expected loadout —
foram remedidas no fim do bloco, por decisão do usuário, porque a dungeon mudou
de propósito. A paridade entre classes ficou congelada e verde.

---

## Abertos, mas fora do escopo da progressão PvE

Registrados onde vivem, e listados aqui só para não se perderem:

- **Custo × recarga das skills.** As cartas de recarga longa rendem menos dano
  por ponto de mana que as de recarga curta.
  - Está registrado como `xfail` estrito em `tests/test_skills.py`.
  - É um defeito de preço de carta, anterior à reforma.
- **O smoke "jogando sozinho" de `tools/audit_interactions.py`** faz spawn sem
  semente, então duas rodadas podem diferir. A seção dirigida já é determinística.
- **As decisões de design pendentes** D2, D4 e D6, em
  [`GAME_DESIGN.md`](GAME_DESIGN.md). São escolhas ainda não ratificadas, e não
  defeitos.

## O que NÃO é known issue

- **A diferença entre starters.** Nenhum efeito foi detectado com a amostra
  atual.
- **O Warrior ir mais fundo na baseline real.** Isolado, isso não é problema, e
  não reabre o Combat/Class Balance.
- **A incerteza sobre qual monstro está num `&`.** É design: o mapa não revela o
  monstro antes da colisão, nem ao jogador nem ao bot.
- **A ausência de CI remota na branch de fase.** A CI só roda para `master` e
  para PRs contra ela.
- **Arquivos experimentais fora do repositório.**
- **O que as Etapas 1 a 8 corrigiram.**
