# Known Issues

Só problemas **abertos**. Histórico resolvido fica em
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md) e nas marcas `[corrigido]`
de [`GAME_DESIGN.md`](GAME_DESIGN.md).

Cada item traz uma classificação, que é a taxonomia da baseline: bug/mecânica,
progressão/dificuldade, comportamento do bot, starter ou inconclusivo. Nenhum
item aqui afirma qual mudança resolve o problema; isso é trabalho de
[`NEXT_PHASE.md`](NEXT_PHASE.md).

A evidência numérica completa está em
[`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md).

---

## KI-001 — decisão de engajamento do BotPadrão

**Classificação:** `BotPadrão / política`. Não é bug do motor.

A decisão de lutar no mapa não considera adequadamente a força do oponente.

- A nota da luta depende do HP do herói e de quantas lutas o alvo custa
  (`src/sim/bot/evaluators.py`), não da força do monstro.
- A escada de necessidades (`src/sim/bot/decision.py`) põe progredir acima de
  investir. Acima do ponto de aposta de HP, curar na Loja perde para qualquer
  luta com nota positiva.
- O bot entra em lutas que o próprio avaliador de combate, no turno 0, já estima
  como perdidas.

**Evidência (baseline `fb321d4e`):**
- 62% das mortes começaram o combate fatal abaixo de 55% de HP.
- Exemplo rastreável: Warrior seed 24, andar 1.

## KI-002 — letalidade do early game

**Classificação:** `Run/Progression Balance`.

Há mortes na primeira luta do andar 1, com HP cheio, contra monstros de nível 1
a 3.

**Evidência (baseline `fb321d4e`):**
- 6 runs morreram na primeira luta do andar 1 com 100% de HP.
- 15,3% das runs morrem no andar 1, e 64,3% até o andar 5.
- Parte dessas mortes se explica pelo KI-001; as 6 mortes com HP cheio, não.

**Ainda não concluído:** qual sistema ou constante é responsável. A suspeita pode
recair sobre a curva do monstro, a população do andar 1, a largada do herói ou a
política do bot, e nada disso está decidido.

## KI-003 — espiral de mergulho

**Classificação:** `progressão + BotPadrão`.

Uma run com pouca vida pode entrar numa espiral:

1. evita o combate;
2. desce;
3. acumula saídas não pagas;
4. ganha pouca Essência;
5. fica abaixo do nível do andar;
6. continua descendo até morrer.

**Evidência (baseline `fb321d4e`):**
- 26 runs chegaram ao andar 10 no nível 5 ou menos.
- Nenhuma delas extraiu.
- O caso extremo é o Mage seed 59: andar 23 no nível 3.

**Não se afirma** que alguma regra individual esteja errada. Cada peça se comporta
como foi escrita:
- contornar monstro é design declarado;
- a saída não paga não bloqueia ninguém;
- o descanso de fim de andar é parcial de propósito.

O problema é a interação entre elas, somada à política do bot.

Relacionado, mas separado: a decisão de design ainda aberta sobre o chefe ser
contornável ([`GAME_DESIGN.md`](GAME_DESIGN.md), D4).

## KI-004 — baixo uso de poções

**Classificação:** `inconclusivo — economia ou política do bot`.

76% das runs da baseline (228/300) não consumiram nenhuma poção.

Não está separado se isso vem de a poção não caber no orçamento, de não aparecer,
ou de o bot não a comprar ou usar. Nenhuma solução é proposta ainda.

## KI-005 — calibração global de progressão pendente

**Classificação:** `Run/Progression Balance`.

> **`Run/Progression Balance — pendente de calibração.`**

A jornada real está implementada e medida (baseline `fb321d4e`), e a calibração
dela está aberta. KI-001 a KI-004 e KI-006 são partes conhecidas desse trabalho,
não a lista inteira.

## KI-006 — o bot não tem intenção sobre 10 das 23 famílias de passiva

**Classificação:** `BotPadrão / política`.

- As políticas de escolha do simulador, inclusive a `survival`, que o BotPadrão
  usa por padrão, ordenam 13 famílias de passiva.
- As outras 10 estão declaradas sem preferência (`PASSIVE_SEM_PREFERENCIA`, em
  `src/sim/pick_policies.py`). Quando a oferta é só dessas, a escolha não tem
  intenção de build.
- Atribuir intenção a essas famílias é decisão de balanceamento, registrada como
  pendente em [`GAME_DESIGN.md`](GAME_DESIGN.md), D3.

Por que importa nesta fase: a build que o bot monta é parte do que a régua de
progressão mede. Não dá para concluir que uma passiva dessas famílias é fraca a
partir do que o bot escolhe.

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
- **A ausência de CI remota na branch de fase.** A CI só roda para `master` e
  para PRs contra ela.
- **Arquivos experimentais fora do repositório.**
- **O que as Etapas 1 a 8 corrigiram.**
