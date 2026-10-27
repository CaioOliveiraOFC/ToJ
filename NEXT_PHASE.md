# Próxima etapa — Fase 6: MMR Offline

A fase PvE está fechada e publicada em `v0.3-pve` (`97965ae7`). O histórico dela
está em [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md), e a fundação
continua congelada.

**Decisão definitiva: o ToJ 1.0 é 100% offline, em Python.**

## O que já existe na `phase/pvp-arena`

| fase | entrega |
|---|---|
| 1 e 1.1 | o **motor headless do duelo**: preparação do gladiador a partir da extração, rodada de decisões simultâneas com lock, iniciativa (referências globais e desempate pela semente), MP reservado, controle, morte, rendição e resultado MD1 |
| 2 | o **modo local jogável** no terminal, opção 3 do menu principal |
| 3 e 4 | o **multiplayer humano × humano** em rede: manifesto e gate de compatibilidade, servidor autoritativo, WebSocket com TLS, contas, gladiadores com dono, salas diretas e cliente de terminal ([`MULTIPLAYER.md`](MULTIPLAYER.md)). **Preservado no repositório e fora do fluxo do 1.0** |
| 5 | a **Arena offline**: o gladiador extraído do jogador contra a população offline, controlada pela IA estratégica da Copa Arena 03 v2, com revanche, histórico da sessão e os pontos de extensão do MMR |

As regras estão em [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#arena).

## Fase 6 — MMR Offline

O que a Fase 5 deixou pronto para ela (`src/engine/arena_historico.py`):

- `ResultadoDaPartida`, com a identidade estável dos dois lados, quem venceu, o
  motivo do motor (`ko` ou `surrender`), as rodadas, a força de referência do
  oponente e a versão do catálogo;
- o protocolo `Historico` (hoje `HistoricoDaSessao`, em memória) e o protocolo
  `Classificacao` (hoje `SemClassificacao`, sem fórmula), já chamados pela
  Arena a cada partida terminada;
- a identidade do gladiador do jogador (`identidade_do_gladiador`), que não
  muda quando ele grava equipamento e muda quando o slot recebe outra run.

O que a Fase 6 decide e implementa:

1. **A fórmula do rating** por gladiador do jogador, e se os gladiadores da
   população também têm rating (ou ficam fixos como régua).
2. **O rating inicial.** Se a força de referência (o OP da geração) entra, e
   como. O OP é medido contra o benchmark do PvE; não é rating.
3. **Como a rendição conta**, e se partida muito curta conta igual.
4. **A persistência local** do histórico e dos ratings: onde fica, o formato, a
   versão, o que acontece quando o slot recebe outra run e quando o catálogo da
   população muda de versão. Ela muda o formato persistido do jogo: passa pelo
   contrato de save.
5. **O que o jogador vê:** rating na lista de gladiadores, na ficha e no fim da
   partida; sugestão de adversário pela diferença de rating, se fizer sentido.
6. **Testes determinísticos** da fórmula, da persistência e da migração.

## Decisões pendentes

- **O gate do multiplayer no CI.** O job `compatibilidade` continua bloqueante,
  e toda mudança em `src/data/` (inclusive o catálogo da população) exige
  regenerar o manifesto `0.4.0-arena.2`, que ainda não foi publicado. Manter
  assim, tirar o job do bloqueio enquanto o multiplayer está fora do 1.0, ou
  separar o catálogo offline do escopo medido é decisão do usuário.
- **Rendição simultânea.** Hoje perde quem está à frente da ordem travada. Na
  Arena offline não acontece (a IA nunca se rende); volta a importar se o
  multiplayer voltar.
- **Crescer a população.** O catálogo aceita até 256 gladiadores. Gerar mais
  (por exemplo, para equilibrar classes ou níveis) é rodar
  `tools/arena_offline_geracao.py` com quotas novas, e muda o sha256 do catálogo.

## Regra de trabalho

- **O PvE está congelado.** A Arena reutiliza as mecânicas, e não as muda. Uma
  mudança que tocaria o PvE é decisão explícita, registrada em
  [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md), com o `-m balance` verde.
- **Não inventar regra de gameplay** para um caso que o contrato não cobre. Ele
  vira ponto de extensão e pendência registrada.
- **Nada de rede no 1.0.** A Arena não importa `src/multiplayer/` nem
  `websockets` (`tests/test_arena_ia_offline.py` confere).
- **Mudança em arquivo medido passa pelo manifesto** enquanto o gate existir:
  rode `python tools/multiplayer_manifesto.py gerar`.
- **Testes determinísticos, fixtures pequenas e sementes fixas** provam regra.
  Nenhuma simulação com mais de ~20 runs sem uma pergunta nova que realmente
  exija estatística.
- Respeitar [`ARCHITECTURE.md`](ARCHITECTURE.md): o motor do duelo fica em
  `mechanics/`, sem teclado, rede, relógio nem UI; a IA fica em `sim/`; a Arena
  em `engine/` só desenha, lê teclas e pergunta.
