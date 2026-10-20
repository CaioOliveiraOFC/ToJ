# Próxima etapa — Calibração da Progressão PvE

Continuação da fase atual. A fundação está fechada e o Combat/Class Balance
também (ver [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md)). O que falta na
fase PvE é a progressão.

## Objetivo

Fechar **`Run/Progression Balance`**: a jornada real, do nível 1 com o Starter
Kit até a morte ou a extração. A referência atual é
[`baselines/progression/fb321d4e/`](baselines/progression/fb321d4e/README.md), e
os problemas conhecidos estão em [`KNOWN_ISSUES.md`](KNOWN_ISSUES.md).

## Ordem inicial de investigação

1. **Comportamento de engajamento do BotPadrão** (KI-001). Vem primeiro porque o
   bot é o instrumento: enquanto ele aceita lutas perdidas, a régua mistura
   política com dificuldade.
2. **Letalidade real do early game** (KI-002).
3. **Espiral de mergulho** (KI-003).
4. **Recuperação, uso de poções e economia** (KI-004).
5. **Nova baseline de progressão**, pelo mesmo protocolo da `fb321d4e`.

Isso **não** significa que cada ponto vai exigir mudança. Primeiro se
diagnostica, depois se decide. "Medido e aceito como está" é um desfecho válido,
desde que registrado.

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
