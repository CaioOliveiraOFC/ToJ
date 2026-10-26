# Próxima etapa — Arena PvP depois do humano × humano em rede

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

A Fase 3 entregou o **contrato de compatibilidade multiplayer**:

- o manifesto imutável de cada versão;
- o handshake que só aceita a versão idêntica;
- o servidor autoritativo sobre o motor canônico;
- partidas presas à versão, com drenagem, transferência ou anulação na
  atualização;
- o gate de publicação no CI.

A Fase 4 entregou o **humano × humano em rede**: transporte WebSocket com TLS,
contas autenticadas por token assinado, gladiadores com dono (importação de
origem confiável), salas diretas e o cliente de terminal. O passo a passo está em
[`MULTIPLAYER.md`](MULTIPLAYER.md).

As regras e o que ainda é futuro estão em
[`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#arena).

## Decisão pendente

- **Rendição simultânea.** Hoje perde quem está à frente da ordem travada, de
  forma provisória. No humano × humano isso já pode acontecer: os dois se rendem
  na mesma rodada.

## O que vem depois

Nenhum destes itens foi iniciado.

- **Extração confiável.** Registrar no servidor um gladiador extraído num
  computador de jogador. Hoje só entram snapshots de origem confiável (as Copas
  publicadas), porque o servidor não tem como confiar numa run local. Exige
  decidir entre PvE autoritativo e extração assinada.
- **O relógio competitivo.** Decisão em 45 s e reconexão em 60 s (com pausa),
  ligados ao `forfeit` do motor. Até ele existir, a partida espera.
- Fila com prioridade humana por 30 s e bots depois.
- MMR individual por gladiador, lendo `Resultados.classificaveis()`, e a
  persistência dos resultados.
- O bot de PvP pela interface `DuelController`.
- A população artificial, formada só por heróis extraídos de runs PvE reais.
- **Identidade de produção.** Provedor externo pelo `Autenticador`, troca de
  senha e revogação de token.

## Regra de trabalho

- **O PvE está congelado.** O PvP reutiliza as mecânicas, e não as muda. Uma
  mudança que tocaria o PvE é decisão explícita, registrada em
  [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md), com o `-m balance` verde.
- **Não inventar regra de gameplay** para um caso que o contrato não cobre. Ele
  vira ponto de extensão e pendência registrada.
- **Mudança de gameplay passa pelo manifesto.** Todo arquivo do escopo medido
  muda o hash: rode `python tools/multiplayer_manifesto.py gerar`; depois de
  publicada, a versão exige número novo.
- **Testes determinísticos, fixtures pequenas e sementes fixas** provam regra.
  Nenhuma simulação com mais de ~20 runs sem uma pergunta nova que realmente
  exija estatística.
- Respeitar [`ARCHITECTURE.md`](ARCHITECTURE.md): o motor do duelo fica em
  `mechanics/`, sem teclado, rede, relógio nem UI; a rede fica em
  `multiplayer/rede.py` e só move texto.
