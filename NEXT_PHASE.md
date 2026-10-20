# Próxima etapa — Dungeon / Run Progression

Continuação da fase atual. A fundação está fechada, o Combat/Class Balance
também, e o instrumento de medição foi corrigido e auditado (ver
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md)). O que falta na fase PvE é
a progressão da dungeon.

## Objetivo

Fechar **`Run/Progression Balance`**: a jornada real, do nível 1 com o Starter
Kit até a morte ou a extração.

- A referência atual é a auditoria do instrumento corrigido,
  [`baselines/progression/0ab837b9/`](baselines/progression/0ab837b9/README.md).
- A `fb321d4e` fica como o "antes" do instrumento.
- Os problemas conhecidos estão em [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md).

## O que este bloco trata

**Só os sintomas que sobreviveram à auditoria do instrumento.** O que era
política do BotPadrão já foi separado e corrigido no bloco anterior: engajamento
e recuperação (KI-001), a parte do bot da espiral (KI-003) e do uso de poções
(KI-004), e a intenção das passivas (KI-006). Aqui, o bot é a régua, e não o
objeto.

Ordem inicial de investigação:

1. **Letalidade real do early game** (KI-002).
   - As mesmas 6 runs morrem na primeira luta do andar 1, com HP cheio.
   - 15,0% das runs morrem no andar 1, e 61,7% até o andar 5.
2. **A espiral de mergulho que sobrou** (KI-003).
   - 14 runs chegam ao andar 10 no nível 5 ou menos, e nenhuma extrai.
   - Entram aqui as 29 mortes sublevel cujo combate fatal começou abaixo de 35%
     de HP.
3. **Economia de recuperação e poções** (KI-004).
   - 80% das runs não bebem nenhuma poção no mapa, com a política já corrigida.
4. **Calibração global** (KI-005) e **nova baseline de progressão**, pelo mesmo
   protocolo.

Isso **não** significa que cada ponto vai exigir mudança. Primeiro se
diagnostica, depois se decide. "Medido e aceito como está" é um desfecho válido,
desde que registrado.

**O instrumento fica congelado durante o bloco.** Se o BotPadrão precisar mudar
de novo, isso é outra rodada de instrumento, com remedição antes de qualquer
conclusão sobre a dungeon.

## Regra de trabalho

Cada problema segue o mesmo ciclo:

```
hipótese → mudança isolada → testes → medição → decisão
```

- Uma variável por vez, em mudança isolada. Não se alteram vários sistemas para
  perseguir uma média.
- Medir pela régua certa:
  - progressão pela baseline de progressão;
  - classe pelo `-m balance`.
- Classificar cada achado antes de mexer: bug/mecânica, progressão/dificuldade,
  comportamento do bot, starter ou inconclusivo.
- Uma mudança no BotPadrão é uma mudança de instrumento: a medição de antes e a
  de depois não se comparam sem remedir.
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
