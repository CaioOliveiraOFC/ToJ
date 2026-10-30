# KI-015 — validação da sonda de status na B0

A passada instrumentada da B0 refeita com a sonda de status corrigida
(`tools/cobertura_pve.py`, `sonda_de_status`). Fica num subdiretório próprio: os
arquivos da B0 em `../` não mudam.

## Protocolo

O da B0, sem alteração: o coletor histórico da `d3105edc`, seeds 1–100 × 3
classes, BotPadrão conservador, teto 200, um processo por run.

```
python tools/cobertura_pve.py rodar --saida cobertura.jsonl --workers 4
python tools/cobertura_pve.py conferir cobertura.jsonl baselines/progression/97965ae/b0.jsonl
python tools/cobertura_pve_matriz.py cobertura.jsonl matriz_cobertura.json > matriz_cobertura.md
```

## Resultado

**Não interferência.** As 300 runs saem idênticas à B0 e à `d3105edc`:

```
runs medidas 300, de referência 300, não medidas 0, divergentes 0
```

**A matriz só muda onde devia.** Comparada linha a linha com
[`../matriz_cobertura.md`](../matriz_cobertura.md), depois de remover a seção
nova e normalizar o título renomeado, a matriz fica idêntica, com duas
exceções intencionais:

| sistema | runs com efeito na B0 (evento publicado) | com a sonda nova (porta única) |
|---|---:|---:|
| Status aplicados pelo herói | 127 | 166 |
| Status aplicados pelos monstros | 225 | 232 |

- A tabela antiga, "eventos publicados", sai igual à da B0. Ela continua na
  matriz para a diferença ficar visível.
- No JSON, a única mudança fora dessas duas linhas é a chave nova
  `status_porta_unica`.

**Os status que a sonda antiga não via** (n = 300):

| status | alvo | tentativas | aplicados | esperado (Σ chance) | antes (evento) |
|---|---|---:|---:|---:|---:|
| `frozen` | herói | 113 | 66 | 63,9 | 0 |
| `sleep` | herói | 128 | 69 | 64,5 | 0 |
| `invisible` | monstro | 202 | 202 | 202,0 | 0 |
| `mana_burn` | herói | 103 | 68 | 62,1 | 25 |
| `clouded` | herói | 43 | 25 | 25,3 | 25 |

Agora as leis que dependem desses status têm a contrapartida medida:
- `quebra_gelida` (3 disparos) e `frozen` (66 aplicações);
- `sleep_damage` (55) e `sleep` (69);
- `emboscada` (79) e `invisible` (202);
- `colapso_mental` (49), `mana_burn` (68) e `clouded` (25).

**Calibração.** Em todo status, o aplicado fica perto do esperado pela soma
das chances efetivas, por exemplo `stun` no monstro com 888 contra 857,8 e
`bleed` no herói com 993 contra 1.008. É uma checagem estatística, não um
invariante, e ela confirma que a chance calculada pela sonda é a mesma que o
combate rolou.

**Por origem:**
- skill principal: 1.315 tentativas e 887 aplicações;
- secundário: 14.029 e 5.254;
- proc de acerto: 30.696 e 1.862.

Imunidade e recusa do núcleo: zero em 300 runs.

## Um achado que a sonda nova revela

O `support` não lançou nenhuma carta de status em 300 runs: só buff (186) e
cura (179). Então `frailty`, que vem do secundário de `mob_maldicao` e de
`mob_praga_lenta`, nunca foi tentado no herói, e a lei `toxicidade` (veneno em
alvo frágil) fica em zero por isso. A lei é alcançável pelo conteúdo, e o zero
vem da IA do monstro, não da sonda.

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `cobertura.jsonl.gz` | A passada com a sonda nova. `gzip -9 -n`: 385.420 bytes, sha256 `920f67fa788bbb53245c20577a6228c2e1631675bd03e306f4428460abe6c6e6`; descomprimido, 3.706.755 bytes, sha256 `0fbca3e05b182976cbeaebe556c683ccdea1f973d2dc71caa0802b6cb388f0f7` |
| `matriz_cobertura.md` | A matriz com a seção "Status — porta única (KI-015)" |
| `matriz_cobertura.json` | A mesma matriz, com a chave `status_porta_unica` |
