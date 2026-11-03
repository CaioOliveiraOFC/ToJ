# Known Issues

Só problemas **abertos**. Histórico resolvido fica em
[`FOUNDATION_CHANGELOG.md`](FOUNDATION_CHANGELOG.md) e nas marcas `[corrigido]`
de [`GAME_DESIGN.md`](GAME_DESIGN.md).

Cada item traz uma classificação, que é a taxonomia da baseline: bug/mecânica,
progressão/dificuldade, comportamento do bot, starter ou inconclusivo. Nenhum
item aqui afirma qual mudança resolve o problema; isso é trabalho de
[`NEXT_PHASE.md`](NEXT_PHASE.md).

A evidência numérica está nas auditorias de progressão, em ordem:

- [`baselines/progression/fb321d4e/README.md`](baselines/progression/fb321d4e/README.md):
  a primeira baseline real, medida com o instrumento antigo;
- [`baselines/progression/0ab837b9/README.md`](baselines/progression/0ab837b9/README.md):
  a auditoria do instrumento corrigido;
- [`baselines/progression/4d0a9a0a/README.md`](baselines/progression/4d0a9a0a/README.md):
  a auditoria da dungeon;
- [`baselines/progression/d3105edc/README.md`](baselines/progression/d3105edc/README.md):
  a auditoria do primeiro level-up, que é o retrato atual.

> **Fechados.** A resolução de cada um está no changelog. A numeração não é
> reaproveitada.
> - KI-001 e KI-006, pela auditoria do instrumento
>   ([changelog](FOUNDATION_CHANGELOG.md#bloco-do-instrumento--botpadrão-corrigido-e-auditado)).
> - KI-004, pela auditoria da dungeon
>   ([changelog](FOUNDATION_CHANGELOG.md#bloco-da-dungeon--run-progression)).
> - KI-002 e KI-003, pela auditoria do primeiro level-up
>   ([changelog](FOUNDATION_CHANGELOG.md#o-primeiro-level-up)). O KI-003 foi
>   aceito como característica de alto risco.
> - KI-005, pelo gate final do `-m balance` no `82ff73ea`: 118 passed, inclusive
>   o spread entre classes ([changelog](FOUNDATION_CHANGELOG.md#o-gate-final)).
>
> **Reabertos pela Etapa 0 da recuperação da fundação PvE (`phase/game-core`).**
> A progressão continua sem item aberto. O que voltou a abrir são mecânicas
> declaradas sem efeito e a cobertura do BotPadrão, abaixo. A medição está em
> [`reports/etapa0_fundacao_pve/README.md`](reports/etapa0_fundacao_pve/README.md).

---

## Abertos — fundação PvE

Os identificadores entre parênteses são os do diagnóstico da fundação PvE
(PVE-xx, BOT-xx, Nx), para rastrear cada item até a matriz de origem.

### KI-007 — A Bênção do Altar não faz nada (PVE-01)

**Classificação:** bug/mecânica.

- `apply_altar_blessing` grava `{"value": 15, "duration": 5}` sem `stat`.
- `buff_stat` recorre a `LEGACY_BUFF_STATS`, que não conhece "Benção do Altar".
  O buff não soma em atributo nem em modificador nenhum.
- O jogador paga 30% do HP máximo, e a tela promete "+15 dano por 5 turnos".
- A régua do `-m balance` (`src/sim/harness.py`) também aceita o Altar, então
  as bandas foram medidas pagando esse custo sem retorno.
- **Evidência:** `tests/test_cobertura_de_efeitos.py`, caso `evento:altar`, em
  `xfail` estrito.

### KI-008 — Buffs de vida e mana máxima não fazem nada (N10)

**Classificação:** bug/mecânica.

- Seis skills de herói declaram buff de `hp` ou `mp`:
  - `cura_menor`, `respiracao_de_forja` e `n_folego_de_marcha` (`hp`);
  - `reserva_profunda`, `bolso_do_alfaiate` e `n_amuleto_rachado` (`mp`).
- Duas de monstro declaram buff de `hp`: `mob_raizes_fundas` e
  `mob_folego_emprestado`.
- Todas gravam `{"stat": "hp"|"mp"}` em `active_buffs`, e nada no combate lê
  esse buff:
  - no herói, o teto (`_scaled`) só lê o `resource_percent` do núcleo;
  - no monstro, só `get_stat("hp")` soma o buff, e o combate usa `base_hp`.
- O `test_placebo` não pegava o defeito: para ele basta o `active_buffs` mudar.
- **Evidência:** `tests/test_cobertura_de_efeitos.py`, casos
  `skill-heroi:buff:hp`, `skill-heroi:buff:mp` e `skill-monstro:buff:hp`, em
  `xfail` estrito.

### KI-009 — O efeito `defense` de equipamento não é lido (N11)

**Classificação:** bug/mecânica.

- `equipment_percent("df")` soma o `defense_bonus` da peça, e o `elif` seguinte
  nunca chega ao `effect_type: defense`.
- O `elif` entrou em `8fb2f0e` para não somar as duas vias, e o efeito ficou
  órfão.
- Só o Amuleto de Argila é afetado: `defense_bonus` 1, efeito `defense` 3. A
  tela mostra "defense +3", e ele entrega o `defense_bonus` 1.
- **Evidência:** `tests/test_cobertura_de_efeitos.py`, caso
  `equipamento:defense`, em `xfail` estrito.

### KI-010 — Vender uma peça engastada destrói as gemas (N3)

**Classificação:** bug/mecânica (integração entre Loja e Ferreiro).

- `Shop.sell_item` tira a peça do inventário e paga o preço. As gemas nos
  sockets somem junto, sem aviso, tanto para o jogador quanto para o bot.
- O preço de venda também ignora o `+N` e os encantamentos da peça.

### KI-011 — O BotPadrão não exercita boa parte dos sistemas (BOT-01, BOT-03, N1, N2, N6)

**Classificação:** comportamento do bot.

Medido na passada instrumentada da B0 (300 runs,
[`matriz_cobertura.md`](baselines/progression/97965ae/matriz_cobertura.md)):

- **Skills.** Escolhe dano quase sempre. Buff foi escolhido 10 vezes em 17.408
  turnos disponíveis; cura, 40 em 18.086; status, 16 em 9.973.
- **Equipamento.**
  - Troca a peça na posição errada em 76 runs, 72 delas com perda líquida, e
    em 69 das 73 builds extraídas (BOT-01).
  - Arma de duas mãos é comparada só com a `Weapon1` (N2).
- **Recursos nunca usados.** Poção de mana, recuperação paga de MP, retirar
  gema, reencantar e reroll de oferta. Elixires, 2 usos em 68 runs com
  oportunidade.
- **Eventos.**
  - O Mercador é tratado como uma segunda Loja (N1).
  - O Altar é aceito em 56 runs, sem efeito (KI-007).
- **Avaliador de combate.** Ignora `mana_restored` (BOT-03) e o desgaste entre
  lutas: HP e MP poupados não contam para a luta seguinte (N6).

Consequência para a régua: uma correção de mecânica que o bot não usa não
aparece na progressão medida.

### KI-012 — O RNG compartilhado limita a comparação entre versões (N5)

**Classificação:** inconclusivo (instrumento de medição).

- A reprodução é exata: mesma seed e mesmo código dão a mesma run.
- O pareamento entre versões não é. Um único sorteio a mais no andar 2, que
  não muda regra nenhuma, muda o desfecho:
  - no gerador global: de 15 a 21 de 60 runs;
  - no gerador da run: 37 de 60.
- Num braço sem mudança de regra, a média subiu +3,0 andares (erro padrão 1,1)
  em 60 pares.
- Com 100 seeds por classe, o efeito mínimo detectável no andar final é de
  ~2 a 3 andares por classe.
- **Evidência:** [`reports/etapa0_fundacao_pve/README.md`](reports/etapa0_fundacao_pve/README.md#4-rng-compartilhado-e-pareamento-entre-versões)
  e `baselines/progression/97965ae/rng/`. A separação das fontes de RNG não foi
  feita: primeiro mede-se o ganho.

---

### KI-013 — Duas armas lendárias declaram efeitos que o motor não tem (N4)

**Classificação:** pendência de design e implementação, não resolvida.

- A Espada do Universo (`true_damage` 20) e o Cajado da Galáxia
  (`armageddon` 50) estão no jogo:
  - são lendárias e `droppable`;
  - a tela mostra o efeito ao jogador.
- Não existe mecânica de dano verdadeiro nem de armageddon. Hoje o jogador recebe
  só o `damage_bonus` da peça.
- Não há decisão aprovada de que fiquem inertes. Falta definir:
  - o que cada efeito é;
  - ou se as peças saem do drop até a mecânica existir.
- **Evidência:** `tests/test_cobertura_de_efeitos.py`, casos
  `equipamento:true_damage` e `equipamento:armageddon`, em `xfail` estrito do
  tipo `design`.

### KI-014 — Os sete efeitos positivos dos pares opostos não têm fonte (PVE-02)

**Classificação:** pendência de design e conteúdo, não resolvida.

- Os efeitos são `empowered`, `arcane_surge`, `quickened`, `fortified`,
  `vitality`, `focused` e `precision`.
- O núcleo os implementa, mas nenhuma carta, item, passiva ou monstro os
  aplica. Por isso as sete leis de par nunca disparam: zero em 300 runs na
  passada instrumentada.
- A passiva `precision` é modificador de acerto, não o efeito do catálogo.
- Não há decisão registrada de que isso seja intencional. Os testes de
  `TestFontesDoCatalogo` travam os dois conjuntos para que qualquer mudança neles
  seja notada, e não para validá-los.

### KI-015 — A sonda de cobertura subconta os status aplicados por skills primárias

**Classificação:** limitação de instrumentação. Não é defeito do jogo.

- A tabela de status de `tools/cobertura_pve.py` conta o evento
  `<status>_applied`.
- `combat.try_apply_status` só publica esse evento quando quem chama passa
  `applied_kind`, e o ramo principal das skills de status não passa. Os
  secundários, os procs de acerto e o atordoamento passam.
- Na passada instrumentada da B0, `frozen`, `sleep` e `invisible` aparecem com
  zero aplicações. Mesmo assim, `quebra_gelida` (que exige alvo congelado),
  `sleep_damage` e `emboscada` (que exige atacante invisível) disparam 3, 55 e
  79 vezes.
- O contador de leis lê outro evento e é confiável. A contagem de status não
  serve para avaliar o uso de skills de status. A correção da medição está
  proposta no
  [relatório da Etapa 0](reports/etapa0_fundacao_pve/README.md#limite-conhecido-da-instrumentação-e-proposta-de-correção)
  e precisa vir antes das melhorias da IA de combate.

---

## Abertos, mas fora do escopo da progressão PvE

Registrados onde vivem, e listados aqui só para não se perderem:

- **Custo × recarga das skills.** As cartas de recarga longa rendem menos dano
  por ponto de mana que as de recarga curta.
  - Está registrado como `xfail` estrito em `tests/test_skills.py`.
  - É um defeito de preço de carta, anterior à reforma.
- **O smoke "jogando sozinho" de `tools/audit_interactions.py`** faz spawn sem
  semente, então duas rodadas podem diferir. A seção dirigida já é determinística.
- **O gate de balanceamento da CI na `master` nunca terminou.** No push da
  `v0.3-pve` (`97965ae`), o job único estourou os 25 minutos e saiu como falha
  sem rodar inteiro.
  - Na `phase/game-core` ele roda em quatro fatias, sem mudar threshold.
  - A `master` fica como está até a próxima integração.
- **As decisões de design pendentes** D2, D4 e D6, em
  [`GAME_DESIGN.md`](GAME_DESIGN.md). São escolhas ainda não ratificadas, e não
  defeitos.

## O que NÃO é known issue

- **A diferença entre starters.** Nenhum efeito foi detectado com a amostra
  atual.
- **O Warrior ir mais fundo na baseline real.** Isolado, isso não é problema, e
  não reabre o Combat/Class Balance.
- **A incerteza sobre qual monstro está num `&`.** É design: o mapa não revela o
  monstro antes da colisão, nem ao jogador nem ao bot.
- **A largada concentrar as mortes.** Cerca de dois terços das mortes acontecem
  até o andar 5 (64% na auditoria `d3105edc`). É característica da dificuldade,
  por decisão do usuário. A condenação sorteada e a armadilha do nível 1, que
  eram defeito, foram corrigidas (KI-002).
- **Voltar de muito atrás ser raro.** Cair vários níveis atrás do andar é de alto
  risco por design: o monstro continua acima do herói, a volta existe mas é rara,
  e não há catch-up garantido (KI-003).
- **A ausência de CI remota nas branches de correção.** A CI roda para `master`
  e para `phase/game-core`, e para os PRs contra elas. As branches `fix/*` e
  `feature/*` são validadas pelo PR, e não pelo push.
- **Arquivos experimentais fora do repositório.**
- **O que as Etapas 1 a 8 corrigiram.**
