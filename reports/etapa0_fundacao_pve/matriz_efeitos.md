# Matriz de cobertura de efeitos declarados

Gerada a partir de `tests/test_cobertura_de_efeitos.py` na Etapa 0, sobre o jogo de `97965ae` (nenhum arquivo de `src/` mudou). Para cada par (fonte, efeito) que o conteúdo declara, o estado e as sondas da assinatura que mudam quando o efeito é aplicado (valor inflado, mesmas seeds).

Estados: **funcional** (alguma sonda muda) e **PENDÊNCIA** (inerte e ao alcance do jogador, em `PENDENCIAS`, `xfail` estrito), do tipo **bug** (a mecânica existe e o caminho está quebrado) ou **design** (o motor não tem a mecânica e falta decidir o que ela é). Nenhum efeito é tratado como inerte de propósito.

| fonte | efeito | estado | consumidores que mudam |
|---|---|---|---|
| passiva | `agility` | funcional | funil, golpes_dados, golpes_recebidos, lutas, perfil |
| passiva | `bleed_chance` | funcional | golpes_dados, lutas |
| passiva | `crit_chance` | funcional | golpes_dados, lutas |
| passiva | `crit_damage` | funcional | funil |
| passiva | `damage_percent` | funcional | funil, golpes_dados, lutas |
| passiva | `damage_reduction` | funcional | golpes_recebidos, lutas |
| passiva | `death_ignore` | funcional | golpe_letal, lutas |
| passiva | `defense` | funcional | golpes_recebidos, lutas, perfil |
| passiva | `essence_bonus` | funcional | recompensa |
| passiva | `evasion` | funcional | funil, golpe_letal, golpes_recebidos, lutas |
| passiva | `fear_chance` | funcional | golpes_dados, lutas |
| passiva | `gold_drop_bonus` | funcional | recompensa |
| passiva | `life_steal` | funcional | golpes_dados, lutas |
| passiva | `magic` | funcional | lutas, perfil |
| passiva | `mana_regen` | funcional | inicio_de_turno |
| passiva | `max_hp` | funcional | inicio_de_turno, lutas, perfil, pocao |
| passiva | `max_mp` | funcional | inicio_de_turno, perfil |
| passiva | `poison_chance` | funcional | golpes_dados, lutas |
| passiva | `potion_heal_bonus` | funcional | pocao |
| passiva | `precision` | funcional | funil, golpes_dados, lutas |
| passiva | `status_resistance` | funcional | lutas, resistencia |
| passiva | `strength` | funcional | lutas, perfil |
| passiva | `stun_chance` | funcional | golpes_dados, lutas |
| equipamento | `agility` | funcional | funil, golpes_dados, golpes_recebidos, lutas, perfil |
| equipamento | `armageddon` | PENDÊNCIA design N4 | — |
| equipamento | `bleed` | funcional | golpes_dados, lutas |
| equipamento | `crit_chance` | funcional | golpes_dados, lutas |
| equipamento | `crit_damage` | funcional | funil |
| equipamento | `damage_reduction` | funcional | golpes_recebidos, lutas |
| equipamento | `death_ignore` | funcional | golpe_letal, lutas |
| equipamento | `defense` | PENDÊNCIA bug N11 | — |
| equipamento | `evasion` | funcional | funil, golpe_letal, golpes_recebidos, lutas |
| equipamento | `fear` | funcional | golpes_dados, lutas |
| equipamento | `life_steal` | funcional | golpes_dados, lutas |
| equipamento | `magic_damage` | funcional | lutas, perfil |
| equipamento | `mana_regen` | funcional | inicio_de_turno |
| equipamento | `max_hp` | funcional | lutas, perfil, pocao |
| equipamento | `max_mp` | funcional | inicio_de_turno, perfil |
| equipamento | `poison` | funcional | golpes_dados, lutas |
| equipamento | `speed` | funcional | funil, golpes_dados, golpes_recebidos, lutas, perfil |
| equipamento | `strength` | funcional | lutas, perfil |
| equipamento | `stun` | funcional | golpes_dados, lutas |
| equipamento | `true_damage` | PENDÊNCIA design N4 | — |
| consumivel | `agility` | funcional | funil, golpes_dados, golpes_recebidos, lutas, perfil |
| consumivel | `crit_chance` | funcional | golpes_dados, lutas |
| consumivel | `damage_reduction` | funcional | golpes_recebidos, lutas |
| consumivel | `defense` | funcional | golpes_recebidos, lutas, perfil |
| consumivel | `evasion` | funcional | funil, golpe_letal, golpes_recebidos, lutas |
| consumivel | `life_steal` | funcional | golpes_dados, lutas |
| consumivel | `mana_regen` | funcional | inicio_de_turno |
| consumivel | `max_hp` | funcional | inicio_de_turno, lutas, perfil |
| consumivel | `max_mp` | funcional | perfil |
| consumivel | `strength` | funcional | lutas, perfil |
| encanto | `bleed_chance` | funcional | golpes_dados, lutas |
| encanto | `crit_chance` | funcional | golpes_dados, lutas |
| encanto | `crit_damage` | funcional | funil |
| encanto | `damage_percent` | funcional | funil, golpes_dados, lutas |
| encanto | `damage_reduction` | funcional | golpes_recebidos, lutas |
| encanto | `evasion` | funcional | funil, golpe_letal, golpes_recebidos, lutas |
| encanto | `fear_chance` | funcional | golpes_dados, lutas |
| encanto | `life_steal` | funcional | golpes_dados, lutas |
| encanto | `mana_regen` | funcional | inicio_de_turno |
| encanto | `poison_chance` | funcional | golpes_dados, lutas |
| encanto | `stun_chance` | funcional | golpes_dados, lutas |
| gema | `Ametista` | funcional | inicio_de_turno, perfil |
| gema | `Esmeralda` | funcional | funil, golpes_recebidos, lutas, perfil |
| gema | `Rubi` | funcional | lutas, perfil |
| gema | `Safira` | funcional | lutas, perfil |
| gema | `Topázio` | funcional | golpes_recebidos, lutas, perfil |
| gema | `Ônix` | funcional | lutas, perfil, pocao |
| skill-heroi | `buff:ag` | funcional | funil, golpes_dados, lutas, perfil |
| skill-heroi | `buff:crit_chance` | funcional | golpes_dados, lutas |
| skill-heroi | `buff:crit_damage` | funcional | funil |
| skill-heroi | `buff:damage_reduction` | funcional | golpes_recebidos |
| skill-heroi | `buff:df` | funcional | golpes_recebidos, lutas, perfil |
| skill-heroi | `buff:evasion` | funcional | funil, golpes_recebidos, lutas |
| skill-heroi | `buff:hp` | PENDÊNCIA bug N10 | — |
| skill-heroi | `buff:life_steal` | funcional | golpes_dados, lutas |
| skill-heroi | `buff:mana_regen` | funcional | inicio_de_turno |
| skill-heroi | `buff:mg` | funcional | lutas, perfil |
| skill-heroi | `buff:mp` | PENDÊNCIA bug N10 | — |
| skill-heroi | `buff:st` | funcional | lutas, perfil |
| skill-heroi | `damage_reduction` | funcional | golpes_recebidos, lutas |
| skill-monstro | `buff:crit_chance` | funcional | golpes_dados, lutas |
| skill-monstro | `buff:df` | funcional | golpes_recebidos, lutas, perfil |
| skill-monstro | `buff:hp` | PENDÊNCIA bug N10 | — |
| skill-monstro | `buff:mg` | funcional | lutas, perfil |
| skill-monstro | `buff:st` | funcional | lutas, perfil |
| skill-monstro | `damage_reduction` | funcional | golpes_recebidos, lutas |
| passiva-monstro | `controller:crit_chance` | funcional | golpes_dados, lutas |
| evento | `altar` | PENDÊNCIA bug PVE-01 | — |
| evento | `fonte` | funcional | inicio_de_turno, lutas, perfil |

## Totais por fonte

| fonte | estado | pares |
|---|---|---:|
| consumivel | funcional | 10 |
| encanto | funcional | 11 |
| equipamento | PENDÊNCIA bug | 1 |
| equipamento | funcional | 17 |
| equipamento | PENDÊNCIA design | 2 |
| evento | PENDÊNCIA bug | 1 |
| evento | funcional | 1 |
| gema | funcional | 6 |
| passiva | funcional | 23 |
| passiva-monstro | funcional | 1 |
| skill-heroi | PENDÊNCIA bug | 2 |
| skill-heroi | funcional | 11 |
| skill-monstro | PENDÊNCIA bug | 1 |
| skill-monstro | funcional | 5 |
