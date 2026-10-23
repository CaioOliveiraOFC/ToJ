# Próxima etapa — decisão de release da fase PvE

A fundação está fechada, e o Combat/Class Balance também. O instrumento foi
corrigido e auditado (`0ab837b9`). O bloco Dungeon / Run Progression terminou
com uma auditoria de 300 runs (`4d0a9a0a`), e a última correção antes do release,
o custo do primeiro level-up, com outra (`d3105edc`). Ver
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md).

## Onde a fase está

- A referência atual é a auditoria do primeiro level-up,
  [`baselines/progression/d3105edc/`](baselines/progression/d3105edc/README.md).
- O BotPadrão está congelado desde `0ab837b9`. Ele só muda por bug mecânico
  comprovado, e mudá-lo é outra rodada de instrumento, com remedição.
- Os problemas estruturais conhecidos da progressão foram tratados ou
  explicitamente aceitos ([`KNOWN_ISSUES.md`](KNOWN_ISSUES.md)):
  - **KI-004 fechou** na auditoria da dungeon.
  - **KI-002 fechou**: entrar no andar 2 ainda no nível 1 caiu de 178/266 para
    103/268, sem mudar o comportamento profundo. A fração das mortes até o
    andar 5 (64%) fica como característica da dificuldade.
  - **KI-003 fechou como característica**: voltar de 3+ níveis atrás é raro de
    propósito, o alto risco da progressão.
- **KI-005 fechou.** O `-m balance` completo rodou uma vez no `82ff73ea`, como
  gate final: 118 passed, inclusive o spread entre classes ≤ 4,0.

## O que falta para a decisão de release

Só a decisão. O critério abaixo está atendido.

Nenhuma outra rodada da dungeon está planejada.

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

## Critério para release PvE

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

Depois disso, faz-se o merge e o release da fase PvE, e abre-se a branch
`phase/pvp-arena`.
