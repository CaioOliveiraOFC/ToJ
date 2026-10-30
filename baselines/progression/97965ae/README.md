# B0 — o PvE antes da recuperação da fundação @ `97965ae`

| | |
|---|---|
| **Commit medido** | `97965ae` — a ponta da `master` (`v0.3-pve`) e o ponto de partida da `phase/game-core` |
| **Referência** | `d3105edc` — a [auditoria do primeiro level-up](../d3105edc/README.md), retrato atual da progressão |
| **Tipo** | reprodução de baseline: mesmo protocolo, mesmo coletor, nenhuma mudança de gameplay |
| **Etapa** | Etapa 0 da recuperação da fundação PvE ([relatório](../../../reports/etapa0_fundacao_pve/README.md)) |

A B0 é o registro do PvE antes de qualquer correção mecânica da `phase/game-core`.
Ela não mede nada novo: prova que o jogo e o instrumento de hoje ainda produzem,
run a run, a régua publicada. É contra ela que as etapas seguintes vão se medir.

---

## Protocolo

O mesmo da `d3105edc`, sem nenhuma alteração:

- 300 runs: seeds 1–100 × warrior, mage e rogue;
- BotPadrão no perfil `conservador`, congelado desde `0ab837b9`;
- nova jornada real com Starter Kit;
- teto técnico de 200 andares;
- um processo por run (`spawn`), para que nada vaze de uma run para a seguinte.

O coletor é o `run_auditoria.py` da `d3105edc`, rodado sem cópia e sem edição:

```
python baselines/progression/d3105edc/run_auditoria.py --saida b0.jsonl --workers 4
```

Entre `d3105edc` e `97965ae`, nada muda em `src/`, `tools/bot_padrao.py` nem
`tools/arena_alvo.py` (`git diff --stat`). Os cinco commits do intervalo só
acrescentam os arquivos da própria baseline `d3105edc`. Por isso a régua aqui é
a mais dura possível: igualdade campo a campo, e não semelhança estatística.

---

## Resultado

**300 de 300 runs idênticas à `d3105edc`**, em todos os campos do coletor menos
`segundos`, que é tempo de relógio:

```
python tools/cobertura_pve.py conferir baselines/progression/97965ae/b0.jsonl \
    baselines/progression/d3105edc/depois.jsonl
runs medidas 300, de referência 300, não medidas 0, divergentes 0
```

O agregador histórico dá diferença zero em todas as linhas, com a `d3105edc`
como "antes" e a B0 como "depois":

```
python baselines/progression/d3105edc/agrega_auditoria.py \
    baselines/progression/d3105edc/depois.jsonl baselines/progression/97965ae/b0.jsonl
```

O agregador rotula as colunas como "antes (4d0a9a0a)" e "depois", porque o rótulo
está fixo no script. Nesta chamada, "antes" é a `d3105edc` e "depois" é a B0.

| Métrica | Todas (n=300) | Warrior | Mage | Rogue |
|---|---:|---:|---:|---:|
| mortes / extrações | 227 / 73 | 74 / 26 | 68 / 32 | 85 / 15 |
| andar médio | 9,18 | 10,25 | 10,10 | 7,19 |
| andar mediana · P25 · P75 · P90 · máx | 6 · 3 · 16,2 · 22 · 28 | 8 · 4,8 · 19,2 · 22 · 25 | 6 · 4 · 20 · 22,1 · 28 | 4 · 2 · 9 · 21 · 27 |
| morte no andar 1 / até 3 / até 5 | 32 / 85 / 145 | 10 / 19 / 34 | 7 / 24 / 49 | 15 / 42 / 62 |
| chegou ao 10 / ao 20 | 94 / 67 | 37 / 25 | 36 / 26 | 21 / 16 |

As demais linhas estão na saída completa do agregador e são todas iguais às da
[`d3105edc`](../d3105edc/README.md#resultado--as-três-classes-n--300):

- nível por andar e atraso;
- poções e Loja;
- Essência e ouro;
- saídas pagas.

---

## O que a B0 não diz

- **Ela não diz que o PvE está correto.** Ela diz que o PvE de hoje é o mesmo
  que a `d3105edc` mediu. As lacunas que a Etapa 0 encontrou estão DENTRO
  destes números, e é isso que faz deles a linha de partida. Entre elas:
  - o Altar sem efeito;
  - os buffs de vida e de mana sem leitor;
  - o BotPadrão sem exercitar parte dos sistemas.
- **Ela não serve, sozinha, para comparar uma mudança que mexa no RNG.** O
  experimento de pareamento da Etapa 0 mede quanto um sorteio a mais desloca
  as runs seguintes (ver o relatório).

---

## Arquivos

| Arquivo | Conteúdo |
|---|---|
| `b0.jsonl` | As 300 runs da B0. 396.396 bytes, sha256 `c92e85f7611f8c9485da96ee586f4c64f762a60735a12ce29e98815da1c0d01d`. Difere de `../d3105edc/depois.jsonl` só no campo `segundos` |
