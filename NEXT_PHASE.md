# Próxima etapa — recuperação da fundação PvE (`phase/game-core`)

A fase PvE chegou à decisão de release com a progressão calibrada (`d3105edc`,
gate final no `82ff73ea`). Depois disso, uma auditoria da fundação PvE achou
mecânicas declaradas que não fazem nada e sistemas que o BotPadrão nunca
exercita. A recuperação acontece na `phase/game-core`, criada da `master` em
`97965ae` (`v0.3-pve`). Ver
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md#recuperação-da-fundação-pve--etapa-0-phasegame-core).

## Onde a fase está

- **Etapa 0, fechada:**
  - a B0 (`97965ae`), 300 de 300 runs idênticas à `d3105edc`;
  - a cobertura por sistema do BotPadrão;
  - os efeitos sem função, em `xfail` estrito;
  - a CI em fatias.

  Integrada em `04f50ea`; o fechamento, pelo PR #7 (`0552259`). O relatório
  está em [`reports/etapa0_fundacao_pve/`](reports/etapa0_fundacao_pve/README.md).
- **KI-015 (sonda de status).** Corrigido no PR #8, validado sobre a base com
  o PR #7 (CI 9/9). Aguarda autorização para integrar.
- **Etapa 1, aprovada e não iniciada.** O
  [plano](reports/etapa1_plano/README.md) (revisão 4) define a ordem:
  1. KI-009, o Amuleto de Argila;
  2. KI-008, buffs de HP/MP, pelo M1;
  3. o Mercador por ofertas no BotPadrão, que é mudança de instrumento;
  4. a variante experimental da régua (F2), sem substituir a original;
  5. o KI-007, quando a decisão D1 sair.
- **Nenhuma linha de gameplay mudou** desde `97965ae`. Os problemas abertos
  estão em [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md), do KI-007 ao KI-016.
- **O BotPadrão está congelado desde `0ab837b9`.** A próxima mudança nele é a
  do Mercador (D4), com baseline nova.

## Próximo passo

1. Autorização para integrar o PR #8.
2. KI-009 na `fix/ki009-amuleto-argila`:
   - a correção;
   - testes de contrato sobre o catálogo;
   - impacto medido pela exposição à peça durante a jornada;
   - PR sem merge automático.

## Regra de trabalho

**Se já se sabe que o sistema está errado e a direção da correção é clara, não é
preciso experimento populacional para pedir permissão para corrigir.** Decisão
do usuário no bloco da dungeon.

- Corrigir em sequência, com commits pequenos por mudança lógica, testes
  específicos curtos e fixtures entre os commits.
- Uma única medição populacional grande no fim do bloco, pelo protocolo da
  régua.
- Nenhuma simulação com mais de ~20 runs sem uma pergunta nova que realmente
  exija estatística. Decisão do usuário no primeiro level-up.
- Classificar cada achado antes de mexer: bug/mecânica, progressão/dificuldade,
  comportamento do bot, starter ou inconclusivo.
- Medir pela régua certa:
  - progressão pela auditoria de progressão;
  - classe pelo `-m balance`.
- Uma mudança no BotPadrão é uma mudança de instrumento: a medição de antes e a
  de depois não se comparam sem remedir.
- Das bandas do `-m balance`, só as três de dificuldade global da dungeon se
  movem com a dungeon, e com remedição registrada. As demais continuam
  congeladas ([`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#combatclass-balance)).
- Respeitar [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md). Um contrato só
  muda por decisão explícita, registrada lá.
- **Integração só com autorização explícita do usuário.** Uma branch e um PR
  por correção, e a CI verde verificada no GitHub antes de pedir o merge.
- **Nenhum threshold muda sem avaliação dos resultados** (D5 do plano). Um
  movimento de banda é relatado como achado, com os números.
- **As duas réguas continuam separadas** (D6). O `-m balance` não é calibrado
  pelo BotPadrão, e a régua original não é substituída.
- **Fora de alcance:** a `master`, a `phase/pvp-arena`, os 186 gladiadores e a
  calibração da Ranked.

## Critério para release PvE

O critério registrado antes da recuperação. A decisão de release continua
pendente, e os itens reabertos pela Etapa 0 estão em
[`KNOWN_ISSUES.md`](KNOWN_ISSUES.md).

Qualitativo. As bandas numéricas da progressão ainda não foram decididas, e
este documento não as inventa.

- O Combat/Class Balance continua verde.
- O Starter Kit continua estável.
- Os problemas estruturais conhecidos da progressão foram tratados ou
  explicitamente aceitos.
- O comportamento do BotPadrão é confiável o bastante para servir de regressão.
- A progressão real foi medida de novo.
- A baseline final da fase PvE está registrada.
- A documentação está sincronizada.
- Suíte padrão, `ruff` e `-m balance` estão verdes.

Depois disso, faz-se o merge e o release da fase PvE. A branch
`phase/pvp-arena` já existe e não é tocada pela recuperação.
