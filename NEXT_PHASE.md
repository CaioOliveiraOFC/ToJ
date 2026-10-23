# Próxima etapa — Arena PvP depois do modo local

A fase PvE está fechada e publicada em `v0.3-pve` (`97965ae7`). O histórico dela
está em [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md), e a fundação
continua congelada.

A Fase 1 do PvP, na branch `phase/pvp-arena`, entregou o **motor headless do
duelo**: preparação do gladiador a partir da extração, rodada de decisões
simultâneas com lock, iniciativa, MP reservado, controle, morte, rendição e
resultado MD1.

A Fase 1.1 fechou a parte técnica da iniciativa:

- as **referências globais** saem da fundação, como a média das três classes
  pelo crescimento canônico;
- o **desempate pela semente** é o contrato definitivo;
- o duelo usa os dois por padrão.

A Fase 2 entregou o **modo local jogável** no terminal: a opção 3 do menu
principal, a escolha do gladiador extraído e do adversário, a preparação do
equipamento, a ficha do adversário, o duelo contra o controlador automático e o
resultado, sem tocar no save.

As regras e o que ainda é futuro estão em
[`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#arena).

## Decisão pendente

- **Rendição simultânea.** Hoje perde quem está à frente da ordem travada, de
  forma provisória. Não bloqueia o modo local, porque o controlador automático
  nunca se rende.

## O que vem depois do modo local

Nenhum destes itens foi iniciado.

- O relógio de decisão (45 s), a desconexão (60 s, com pausa) e a ligação deles
  ao `forfeit` do motor.
- Fila com prioridade humana por 30 s e bots depois.
- MMR individual por gladiador.
- O controlador remoto (rede) e o bot de PvP, ambos pela interface
  `DuelController`.
- A população artificial, formada só por heróis extraídos de runs PvE reais.

## Regra de trabalho

- **O PvE está congelado.** O PvP reutiliza as mecânicas, e não as muda. Uma
  mudança que tocaria o PvE é decisão explícita, registrada em
  [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md), com o `-m balance` verde.
- **Não inventar regra de gameplay** para um caso que o contrato não cobre. Ele
  vira ponto de extensão e pendência registrada.
- **Testes determinísticos, fixtures pequenas e sementes fixas** provam regra.
  Nenhuma simulação com mais de ~20 runs sem uma pergunta nova que realmente
  exija estatística.
- Respeitar [`ARCHITECTURE.md`](ARCHITECTURE.md): o motor do duelo fica em
  `mechanics/`, sem teclado, rede, relógio nem UI.
