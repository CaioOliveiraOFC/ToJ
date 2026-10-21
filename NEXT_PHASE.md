# Próxima etapa — decisão de release da fase PvE

A fundação está fechada, e o Combat/Class Balance também. O instrumento foi
corrigido e auditado (`0ab837b9`), e o bloco Dungeon / Run Progression terminou
com uma auditoria de 300 runs (`4d0a9a0a`). Ver
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md).

## Onde a fase está

- A referência atual é a auditoria da dungeon,
  [`baselines/progression/4d0a9a0a/`](baselines/progression/4d0a9a0a/README.md).
- O BotPadrão está congelado desde `0ab837b9`. Ele só muda por bug mecânico
  comprovado, e mudá-lo é outra rodada de instrumento, com remedição.
- `Run/Progression Balance` continua **pendente de calibração**
  ([`KNOWN_ISSUES.md`](KNOWN_ISSUES.md)).
  - **KI-004 fechou.**
  - **KI-002 está aberto**, mais estreito: a condenação sorteada saiu, mas 2/3 das
    mortes ainda acontecem até o andar 5, e 2/3 das runs entram no andar 2 no
    nível 1.
  - **KI-003 está aberto**, mais estreito: agora existe volta para quem caiu para
    trás, mas ela é rara, e nenhum mergulho extrai.
  - **KI-005** fecha quando KI-002 e KI-003 forem tratados ou explicitamente
    aceitos.

## O que decidir

O critério de release abaixo pede que os problemas estruturais conhecidos tenham
sido "tratados ou explicitamente aceitos". Para KI-002 e KI-003, as saídas são:

1. **Aceitar como característica do jogo**, registrando a decisão. Exemplos: a
   largada concentra as mortes de propósito; voltar de muito atrás é raro de
   propósito. Aí KI-005 fecha e a fase vai para o release.
2. **Outra rodada da dungeon**, só sobre o que sobrou. Os candidatos já
   levantados, sem decisão:
   - o começo da curva de XP contra a população do andar 1;
   - a largada real contra o expected loadout;
   - quanto de volta o jogo deve oferecer a quem caiu para trás.

Nenhuma das duas está decidida.

## Regra de trabalho

**Se já se sabe que o sistema está errado e a direção da correção é clara, não é
preciso experimento populacional para pedir permissão para corrigir.** Decisão
do usuário no bloco da dungeon.

- Corrigir em sequência, com commits pequenos por mudança lógica, testes
  específicos curtos e fixtures entre os commits.
- Uma única medição populacional grande no fim do bloco, pelo protocolo da
  régua.
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
