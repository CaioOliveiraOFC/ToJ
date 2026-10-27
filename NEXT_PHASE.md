# Próxima etapa — expandir a Ranked para 5.000 gladiadores

A fase PvE está fechada e publicada em `v0.3-pve` (`97965ae7`). O histórico dela
está em [`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md), e a fundação
continua congelada.

**Decisão definitiva: o ToJ 1.0 é 100% offline, em Python.**

## O que já existe na `phase/pvp-arena`

| fase | entrega |
|---|---|
| 1 e 1.1 | o **motor headless do duelo**: preparação do gladiador, decisões simultâneas com lock, iniciativa, MP reservado, controle, morte, rendição e resultado MD1 |
| 2 | o **modo local jogável** no terminal |
| 3 e 4 | o **multiplayer humano × humano** em rede ([`MULTIPLAYER.md`](MULTIPLAYER.md)). **Preservado no repositório e fora do fluxo do 1.0** |
| 5 | a **Arena offline**: 186 gladiadores extraídos de runs PvE reais, a IA estratégica, o Duelo Livre |
| 6 | a **Arena Ranqueada experimental**: Glicko-2 escolhido contra TrueSkill em confrontos reais, os 186 calibrados em 1.632 partidas, 10 partidas de posicionamento, 12 ranks por percentil e os Definitive Masters, mundo NPC × NPC, persistência local e jogadores artificiais |

As regras estão em [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#arena-ranqueada-fase-6-experimental),
e os números em [`reports/ranked/relatorio.md`](reports/ranked/relatorio.md).

## Antes de expandir para 5.000

O que a população de 186 não consegue responder, e precisa estar decidido ou
medido antes de gerar milhares de gladiadores:

1. **Repetição de adversário.** Com 186, a faixa de nível de cada gladiador tem
   poucos NPCs: nos jogadores artificiais, 15–25% das partidas repetem um
   oponente das últimas 10, e no topo é pior. A exclusão das últimas 3 partidas
   não basta. Com 5.000 o problema diminui, mas a regra (exclusão maior, ou um
   custo por repetição no matchmaking) deve ser decidida medindo.
2. **Os limites percentuais.** A proposta atual foi feita sobre 186; com 5.000
   as faixas do topo terão dezenas de gladiadores, e as do meio podem ficar mais
   estreitas que a incerteza. Reavaliar com a população calibrada maior.
3. **O custo da calibração.** Um confronto real custa ~3 s de CPU. Calibrar
   5.000 com ~15 partidas cada são ~37.500 partidas, ~10 h de CPU em 4 núcleos.
   A geração dos gladiadores também custa (~0,6 min de relógio por extração
   aceita). Planejar lotes e checkpoint.
4. **O tamanho do estado local.** `saves/ranked.json` guarda todos os
   registros com histórico recente; com 5.000, ~10 MB. Medir o tempo de gravar
   a cada partida e, se preciso, gravar só o que mudou.
5. **O ritmo do mundo orgânico.** 2 confrontos NPC × NPC por partida do jogador
   e 4 por hora fora mexem em pouca coisa numa população de 5.000. Definir a
   meta (quantas partidas por NPC por semana de jogo) antes de escolher o ritmo.
6. **Rank piscando na fronteira.** No meio da Ladder, um gladiador que mora
   perto de um limite troca de rank a cada poucas partidas (70 trocas em 390
   partidas num jogador artificial). Decidir se entra histerese de rank (mudar
   só ao passar o limite com folga, por exemplo meio RD) e medir de novo.
7. **A volatilidade do Glicko-2.** Com uma partida por período ela não tem
   efeito (τ é indiferente). Decidir se o mundo passa a ter períodos com várias
   partidas, ou se fica assim (Glicko-2 funcionando como Glicko-1).
8. **Um teste manual longo** na branch: posicionar alguns gladiadores de verdade
   e jogar algumas horas, para validar a sensação do matchmaking e dos ranks.

## Decisões pendentes

- **Partida sem fim (a mais urgente).** Há duplas que nunca terminam (as duas
  builds se curam mais rápido do que se ferem); no topo é frequente — 13 de 100
  partidas de um jogador artificial no International Master, todas contra Magos
  de topo. Entre NPCs, a partida vira "sem resultado" em 500 rodadas; contra o
  jogador, hoje só a rendição encerra. Falta a regra de design: empate, limite
  com desempate, ou outra.

- **O gate do multiplayer no CI.** O job `compatibilidade` continua bloqueante:
  toda mudança em `src/data/` (o catálogo e o estado inicial da Ranked)
  regenera o manifesto `0.4.0-arena.2`, ainda não publicado. Manter, tirar do
  bloqueio enquanto o multiplayer está fora do 1.0, ou separar o que é offline
  do escopo medido.
- **Rendição na Ranqueada** conta como derrota comum. Confirmar.
- **`websockets`** continua como dependência obrigatória (o multiplayer e o CI
  o usam); movê-lo para um extra opcional fica para o empacotamento do 1.0.

## Regra de trabalho

- **O PvE está congelado.** A Arena reutiliza as mecânicas, e não as muda.
- **O motor PvP e a IA estratégica não mudam para favorecer classificação.**
- **Não inventar regra de gameplay** para um caso que o contrato não cobre. Ele
  vira ponto de extensão e pendência registrada.
- **Nada de rede no 1.0.** A Arena não importa `src/multiplayer/` nem
  `websockets` (`tests/test_arena_ia_offline.py` confere).
- **Mudança em arquivo medido passa pelo manifesto** enquanto o gate existir:
  rode `python tools/multiplayer_manifesto.py gerar`.
- **Experimento reprodutível:** todo confronto tem seed, todo resultado fica em
  `reports/`, e a Ladder publicada é exatamente a reaplicação deles
  (`tests/test_ranked_experimentos.py`).
- **Medir o custo antes de ampliar**, e simulação grande só com pergunta que a
  pequena não respondeu.
