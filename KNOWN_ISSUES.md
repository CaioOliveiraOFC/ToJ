# Known Issues

Só problemas **abertos**. Histórico resolvido fica em
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md) e nas marcas `[corrigido]`
de [`GAME_DESIGN.md`](GAME_DESIGN.md).

Cada item traz uma classificação, que é a taxonomia da baseline: bug/mecânica,
progressão/dificuldade, comportamento do bot, starter ou inconclusivo. Nenhum
item aqui afirma qual mudança resolve o problema; isso é trabalho de
[`NEXT_PHASE.md`](NEXT_PHASE.md).

A evidência numérica está nas auditorias de progressão, em ordem:

- [`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md):
  a primeira baseline real, medida com o instrumento antigo;
- [`baselines/progression/0ab837b9/README.md`](baselines/progression/0ab837b9/README.md):
  a auditoria do instrumento corrigido;
- [`baselines/progression/4d0a9a0a/README.md`](baselines/progression/4d0a9a0a/README.md):
  a auditoria da dungeon;
- [`baselines/progression/d3105edc/README.md`](baselines/progression/d3105edc/README.md):
  a auditoria do primeiro level-up, que é o retrato atual.

> **Fechados.** A resolução de cada um está no changelog. A numeração não é
> reaproveitada.
> - KI-001 e KI-006, pela auditoria do instrumento
>   ([changelog](FOUNDATION_CHANGELOG.md#bloco-do-instrumento--botpadrão-corrigido-e-auditado)).
> - KI-004, pela auditoria da dungeon
>   ([changelog](FOUNDATION_CHANGELOG.md#bloco-da-dungeon--run-progression)).
> - KI-002 e KI-003, pela auditoria do primeiro level-up
>   ([changelog](FOUNDATION_CHANGELOG.md#o-primeiro-level-up)). O KI-003 foi
>   aceito como característica de alto risco.

---

## KI-005 — calibração global de progressão: falta uma verificação

**Classificação:** `Run/Progression Balance`.

A jornada real foi medida depois da última correção (auditoria `d3105edc`).
- Extraem 24% das runs.
- O andar médio é 9,2.
- A cauda vai até o andar 28.
- Os problemas conhecidos foram tratados ou aceitos.

As três bandas de dificuldade global do `-m balance` foram remedidas com os
valores que o próprio `-m balance` do `d3105edc` observou.

**Falta só uma verificação.** O `-m balance` não foi rodado de novo depois da
remedição.
- Os 4 testes das três bandas são determinísticos e passam por construção.
- A asserção de **spread entre classes** (≤ 4,0, a paridade) ainda não foi
  avaliada no `d3105edc`, porque fica no mesmo teste da banda que falhou antes
  dela.
- Uma rodada do `-m balance` fecha a questão. Se o spread passar, KI-005 fecha.

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
- **A largada concentrar as mortes.** Cerca de dois terços das mortes acontecem
  até o andar 5 (64% na auditoria `d3105edc`). É característica da dificuldade,
  por decisão do usuário. A condenação sorteada e a armadilha do nível 1, que
  eram defeito, foram corrigidas (KI-002).
- **Voltar de muito atrás ser raro.** Cair vários níveis atrás do andar é de alto
  risco por design: o monstro continua acima do herói, a volta existe mas é rara,
  e não há catch-up garantido (KI-003).
- **A ausência de CI remota na branch de fase.** A CI só roda para `master` e
  para PRs contra ela.
- **Arquivos experimentais fora do repositório.**
- **O que as Etapas 1 a 8 corrigiram.**
