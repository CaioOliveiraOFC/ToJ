# Known Issues

Só problemas **abertos**. Histórico resolvido fica em
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md) e nas marcas `[corrigido]`
de [`GAME_DESIGN.md`](GAME_DESIGN.md).

Cada item traz uma classificação, que é a taxonomia da baseline: bug/mecânica,
progressão/dificuldade, comportamento do bot, starter ou inconclusivo. Nenhum
item aqui afirma qual mudança resolve o problema; isso é trabalho de
[`NEXT_PHASE.md`](NEXT_PHASE.md).

A evidência numérica está em dois lugares:

- [`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md):
  a primeira baseline real, medida com o instrumento antigo;
- [`baselines/progression/0ab837b9/README.md`](baselines/progression/0ab837b9/README.md):
  a auditoria do instrumento corrigido, que é o retrato atual.

> **KI-001 e KI-006 foram fechados** pela auditoria do instrumento. A resolução
> está em [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md#bloco-do-instrumento--botpadrão-corrigido-e-auditado).
> A numeração não é reaproveitada.

---

## KI-002 — letalidade do early game

**Classificação:** `Run/Progression Balance`.

Há mortes na primeira luta do andar 1, com HP cheio, contra monstros de nível 1
a 3.

**Evidência:**
- Baseline `fb321d4e`:
  - 6 runs morreram na primeira luta do andar 1 com 100% de HP;
  - 15,3% das runs morreram no andar 1, e 64,3% até o andar 5.
- Auditoria do instrumento `0ab837b9`:
  - as **mesmas 6 runs** (Mage seeds 16, 62 e 93; Rogue seeds 4, 16 e 98)
    morrem na mesma primeira luta, com HP cheio;
  - 15,0% morrem no andar 1 (46 → 45), e 61,7% até o andar 5 (193 → 185).

Com o instrumento corrigido, a letalidade do começo quase não se moveu. Ela não
era, no essencial, política do bot.

**Ainda não concluído:** qual sistema ou constante é responsável. A suspeita pode
recair sobre a curva do monstro, a população do andar 1 ou a largada do herói, e
nada disso está decidido.

## KI-003 — espiral de mergulho

**Classificação:** `Run/Progression Balance`. A parte do BotPadrão foi corrigida
em `7b9734c3`.

Uma run com pouca vida pode entrar numa espiral:

1. evita o combate;
2. desce;
3. acumula saídas não pagas;
4. ganha pouca Essência;
5. fica abaixo do nível do andar;
6. continua descendo até morrer.

**O que o bot deixou de fazer.** Ele não trata mais a descida sem pagar como
estratégia quando está abaixo do nível do andar, a saída não seria paga, há luta
no mapa e o fôlego observado paga pelo menos uma luta média. Nesse estado, ele
luta. Fora dele, a regra de antes continua: sem fôlego, sem evidência ou com a
saída pagável, sair abaixo do ponto de aposta continua sendo recuperação, e a
sobrevivência continua acima.

**O que sobreviveu (auditoria `0ab837b9` contra `fb321d4e`):**
- Runs que chegam ao andar 10 no nível 5 ou menos: 26 → **14**, e **nenhuma
  extrai**, antes ou depois. Das 14, 6 já mergulhavam antes e 8 são novas.
- Elas ainda somam em média 6,9 saídas não pagas por run.
- Saídas não pagas por run caíram de 1,23 para 0,89. A maior sequência caiu de
  18 para 9.
- O Mage seed 59 não mergulha mais: morre no andar 6, nível 3, com 2 saídas não
  pagas, contra o andar 23 e 19 saídas não pagas antes.

O que resta é a espiral que o bot não tem como evitar: sem fôlego para uma luta
média, a saída é a recuperação que existe. A interação continua sendo a do
diagnóstico original:
- o descanso de fim de andar é parcial de propósito;
- a saída não paga reduz a Essência;
- cada andar sublevel é mais difícil que o anterior.

**Efeito colateral, a ser lido no bloco da dungeon.** Mortes cujo combate fatal
começou abaixo de 35% de HP subiram de 1 para 30. 29 delas são sublevel, e são
as lutas que a nova regra manda aceitar. As 29 runs também morriam no
`fb321d4e`; nenhuma era extração. 15 morrem mais raso, 3 no mesmo andar e 11
mais fundo. A regra usa a luta média observada, e a luta que as mata custa mais
que a média.

**Não se afirma** que alguma regra individual esteja errada. Cada peça se comporta
como foi escrita:
- contornar monstro é design declarado;
- a saída não paga não bloqueia ninguém;
- o descanso de fim de andar é parcial de propósito.

Relacionado, mas separado: a decisão de design ainda aberta sobre o chefe ser
contornável ([`GAME_DESIGN.md`](GAME_DESIGN.md), D4).

## KI-004 — baixo uso de poções

**Classificação:** `economia / aquisição`. A parte do BotPadrão foi corrigida em
`9ef74639` e `7c08bdec`.

**O que o bot deixou de fazer:**
- beber uma poção só porque a tem, com HP alto ou com a cura quase toda
  transbordando;
- prometer a si mesmo uma cura ou uma poção que o orçamento real da Loja não
  paga.

Agora a poção do mapa atende uma necessidade observada: emergência abaixo do
ponto de aposta, ou uma próxima luta média que derrubaria o herói abaixo dele.

**O que sobreviveu (auditoria `0ab837b9` contra `fb321d4e`):**
- Runs sem nenhuma poção bebida no mapa: 228 → **240 de 300 (80%)**.
- Poções bebidas no mapa: 314 → 129. Pela regra nova, nenhuma é bebida quando
  mais da metade da cura transbordaria.
- Poções compradas na Loja: 338 → 212. A regra de compra (`visit_shop`) não
  mudou: ela repõe a mochila até 3, então quem bebe menos compra menos.
- Itens usados dentro do combate: 64 → 64.
- Mortes com poção de cura na mochila: 8 → 10. Nenhuma das 10 começou o
  combate fatal abaixo de 55% de HP; no `fb321d4e`, 5 das 8 tinham começado.

O uso continua baixo com a política corrigida. Ainda não se sabe se a poção
chega ao herói quando ele precisa: drop, estoque, preço contra o orçamento e
desbloqueio da Loja são economia, não política do bot. Nenhuma solução é
proposta ainda.

## KI-005 — calibração global de progressão pendente

**Classificação:** `Run/Progression Balance`.

> **`Run/Progression Balance — pendente de calibração.`**

A jornada real está implementada e medida com o instrumento corrigido (auditoria
`0ab837b9`), e a calibração dela está aberta. KI-002 a KI-004 são as partes
conhecidas que sobreviveram à auditoria, não a lista inteira.

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
