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
| 6.1 | a **progressão competitiva**: 45 divisões de 100 PR (Iron V a Obsidian I) puxadas para o MMR, escudo e rebaixamento com folga, Candidato a Master promovido só na atualização periódica da leaderboard (1 h, configurável), risco e rebaixamento da elite, empate técnico por impasse, custo progressivo de repetição no matchmaking, `ranked.json` versão 2 com migração da 1 |

As regras estão em [`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#arena-ranqueada-fase-6-experimental)
e na seção da [Fase 6.1](GAMEPLAY_CONTRACTS.md#arena-ranqueada-progressão-competitiva-fase-61-experimental);
os números, em [`reports/ranked/relatorio.md`](reports/ranked/relatorio.md) e
[`reports/ranked/fase61/relatorio.md`](reports/ranked/fase61/relatorio.md).

## Antes de expandir para 5.000

Resolvido na 6.1, e medido com os 186:

- **Partida sem fim** → empate técnico por impasse (150 rodadas sem desgaste
  novo, teto de 1.000), para NPC × NPC e para o jogador.
- **Repetição de adversário** → custo progressivo; a repetição nas últimas 10
  some fora do topo, e no topo cai de 56% para 16% (modelo). Nas carreiras reais
  da 6.1 (120 partidas por faixa), fica entre 0% e 1,7% nas faixas baixa, média,
  alta e na fronteira, e em **32,5% na elite**, com chance média de 0,65: com
  186 gladiadores o topo tem poucos rivais, e o modelo subestimou isso. Com 5.000
  a mesma regra vale sem mudança.
- **Rank piscando na fronteira** → a divisão visível anda pelo PR, com escudo e
  rebaixamento pousando em 75: na carreira W26 da Fase 6, de 71 trocas de rank
  por percentil para 5 trocas de rank visível.

O que a população de 186 não consegue responder, e precisa estar decidido ou
medido antes de gerar milhares de gladiadores:

1. **Aprovar os parâmetros** da tabela da Fase 6.1 (K, β, escudo, pouso do
   rebaixamento, ciclo, faixa de risco, RD para promover, janela do impasse,
   custo de repetição). Todos estão num lugar só, com o experimento que os
   sustenta.
2. **Os limites percentuais.** Com 5.000, o Master (percentil ≥ 92) tem ~400
   gladiadores e cada divisão do meio tem dezenas — rever as faixas com a
   população calibrada maior, e ver se o alvo linear dentro do rank continua
   bom.
3. **O custo da calibração.** Um confronto real custa ~3 s de CPU (os de
   sustain, até ~60 s antes do empate técnico). Calibrar 5.000 com ~15 partidas
   cada são ~37.500 partidas, ~10 h de CPU em 4 núcleos. A geração dos
   gladiadores também custa (~0,6 min de relógio por extração aceita). Planejar
   lotes e checkpoint.
4. **O tamanho do estado local.** `saves/ranked.json` guarda os registros com
   histórico recente e, desde a 6.1, o retrato publicado e as posições do
   anterior: com 5.000, ~10–12 MB, gravados a cada partida. Medir e, se
   preciso, gravar só o que mudou (ou o retrato à parte).
5. **O ritmo do mundo orgânico e a divisão dos NPCs.** O NPC só mexe no PR
   quando joga; com 5.000 e 2 confrontos por partida do jogador, um NPC joga
   raramente e a divisão dele envelhece. Definir a meta (partidas por NPC por
   semana de jogo) e decidir se o retrato reaproxima a divisão de quem não joga.
6. **A volatilidade do Glicko-2.** Com uma partida por período ela não tem
   efeito (τ é indiferente). Decidir se o mundo passa a ter períodos com várias
   partidas, ou se fica assim (Glicko-2 funcionando como Glicko-1).
7. **Um teste manual longo** na branch: posicionar alguns gladiadores de verdade
   e jogar algumas horas, para validar a sensação do PR, da candidatura e da
   espera pela atualização.

## Decisões pendentes

- **Os parâmetros propostos da Fase 6.1** (acima, item 1).
- **Empate técnico contra o jogador humano.** O impasse real termina perto da
  rodada 300–420: 30 a 40 minutos de um humano. Aceitar, oferecer um empate
  por acordo, ou encurtar a janela só para o jogador (a regra hoje é a mesma
  para NPC e jogador).
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
