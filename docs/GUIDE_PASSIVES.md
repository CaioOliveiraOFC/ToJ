# Guia de Criação de Passivas em Massa — TOJ

## Contexto

Este guia serve para gerar dezenas/centenas de novas passivas para o catálogo `src/data/passives.json` do jogo TOJ (Tales of the Journey).

---

## 1. Estrutura do Arquivo

O arquivo `src/data/passives.json` tem esta estrutura:

```json
{
  "description": "...",
  "version": "1.0",
  "rarity_weights": { "Common": 60, "Rare": 28, "Epic": 10, "Legendary": 2 },
  "passives": [
    { ... cada passiva é um objeto ... }
  ]
}
```

Cada passiva dentro do array `"passives"` deve ter **exatamente** estes 7 campos:

| Campo | Tipo | Descrição | Exemplo |
|---|---|---|---|
| `id` | string | Identificador único, snake_case, sem acentos | `"coracao_ferro"` |
| `name` | string | Nome exibido, pode ter acentos | `"Coração de Ferro"` |
| `category` | string | Uma das 3 categorias: `Stats`, `Recursos`, `Combate` | `"Stats"` |
| `rarity` | string | Uma das 4: `Common`, `Rare`, `Epic`, `Legendary` | `"Common"` |
| `description` | string | Texto curto exibido na carta | `"+15 HP máximo"` |
| `effect_type` | string | Identificador do efeito (ver tabela abaixo) | `"max_hp"` |
| `effect_value` | number | Valor numérico (inteiro ou float) | `15` |

---

## 2. Effect Types Válidos

### Stats (alteram atributos base do jogador)
| effect_type | O que faz | Valores típicos por raridade |
|---|---|---|
| `max_hp` | Aumenta HP máximo | Common: 10-30, Rare: 30-60, Epic: 60-120, Legendary: 120-250 |
| `max_mp` | Aumenta MP máximo | Common: 8-20, Rare: 20-40, Epic: 40-80, Legendary: 80-150 |
| `strength` | Aumenta força base | Common: 2-5, Rare: 6-12, Epic: 12-20, Legendary: 20-40 |
| `defense` | Aumenta defesa base | Common: 2-5, Rare: 5-10, Epic: 10-20, Legendary: 20-35 |
| `agility` | Aumenta agilidade base (cap: 95) | Common: 1-3, Rare: 3-6, Epic: 6-12, Legendary: 12-20 |

### Recursos (afetam economia e ganhos)
| effect_type | O que faz | Valores típicos por raridade |
|---|---|---|
| `essence_bonus` | Bônus % no multiplicador de essência | Common: 5-15, Rare: 15-25, Epic: 25-45, Legendary: 45-70 |
| `gold_drop_bonus` | Bônus % em ouro dropado | Common: 5-15, Rare: 15-30, Epic: 30-50, Legendary: 40-60 |
| `potion_heal_bonus` | Bônus % na cura de poções | Common: 5-12, Rare: 12-20, Epic: 20-35, Legendary: 30-50 |

### Combate (afetam mecânicas de luta)
| effect_type | O que faz | Valores típicos por raridade |
|---|---|---|
| `crit_chance` | Chance % de ataque crítico | Common: 3-8, Rare: 8-15, Epic: 15-25, Legendary: 25-40 |
| `dodge_chance` | Chance % de esquiva | Common: 3-6, Rare: 6-12, Epic: 10-18, Legendary: 15-25 |
| `damage_reduction` | % de redução de dano recebido | Common: 2-5, Rare: 5-10, Epic: 10-18, Legendary: 15-25 |
| `stun_chance` | Chance % de atordoar | Common: 3-6, Rare: 6-10, Epic: 10-15, Legendary: 12-20 |
| `death_ignore` | Quantas mortes ignorar (inteiro, não %) | Epic: 1, Legendary: 1-2 |

---

## 3. Regras Críticas

1. **IDs devem ser únicos** — nunca repetir um `id` existente no arquivo
2. **IDs sem acentos** — usar `coracao` em vez de `coração`, `lamina` em vez de `lâmina`
3. **IDs em snake_case** — `nome_da_passiva`, sem camelCase ou kebab-case
4. **Nomes com acentos são ok** — `"Coração de Ferro"` está correto no campo `name`
5. **`effect_value` deve ser número** — `15`, não `"15"`
6. **Categorias fixas** — exatamente `"Stats"`, `"Recursos"` ou `"Combate"`
7. **Raridades fixas** — exatamente `"Common"`, `"Rare"`, `"Epic"` ou `"Legendary"`
8. **Escalabilidade por raridade** — valores de Legendary devem ser significativamente maiores que Common
9. **Descriptions concisas** — máximo ~40 caracteres, formato: `"+X Y"` ou `"descrição curta"`
10. **JSON válido** — aspas duplas em tudo, vírgulas entre objetos, sem trailing comma no último elemento

---

## 4. Template para Gerar em Massa

```json
{
  "id": "nome_unico_snake_case",
  "name": "Nome da Passiva",
  "category": "Stats",
  "rarity": "Common",
  "description": "+15 HP máximo",
  "effect_type": "max_hp",
  "effect_value": 15
}
```

---

## 5. Onde os Dados São Usados

| Arquivo | Uso |
|---|---|
| `src/content/passives.py` | Carrega o JSON, cria `PassiveCard` dataclasses, gera escolhas ponderadas |
| `src/entities/heroes.py` | Aplica stats (`max_hp`, `max_mp`, `strength`, `defense`, `agility`) ao escolher passiva |
| `src/mechanics/combat.py` | Usa `crit_chance` e `dodge_chance` em cálculos de combate |
| `src/storage/save_manager.py` | Salva/carrega apenas os IDs das passivas |

---

## 6. Notas sobre Integração

- **Stats** (`max_hp`, `max_mp`, `strength`, `defense`, `agility`) são aplicados **imediatamente** ao escolher a passiva, sem chamar `rest()`.
- **Combate** (`crit_chance`, `dodge_chance`) é lido pelo `combat.py` via `player.get_passive_bonus()`.
- **Recursos** (`essence_bonus`, `gold_drop_bonus`, `potion_heal_bonus`) e **Combate avançado** (`damage_reduction`, `stun_chance`, `death_ignore`) ainda não têm integração ativa no motor — ficarão para tarefas futuras.
- Novos `effect_type` podem ser adicionados, mas requerem código em `_apply_passive_stats()` (heroes.py) e/ou `combat.py`.

---

## 7. Checklist Pós-Criação

- [ ] Todos os IDs são únicos (sem duplicatas)
- [ ] JSON válido (validar com `python3 -c "import json; json.load(open('src/data/passives.json'))"`)
- [ ] Nenhuma passiva tem `effect_value` como string
- [ ] Distribuição por raridade está balanceada
- [ ] Ruff check passa: `python3 -m ruff check src/content/passives.py`
