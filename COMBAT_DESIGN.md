# ⚔️ COMBAT_DESIGN — Tales of the Journey

## Filosofia Central

O sistema de combate do ToJ é um **pipeline determinístico de redução de contexto**.
Nenhum sistema gera dano diretamente — todos injetam operadores matemáticos num contexto
de combate imutável que é colapsado em sequência.

Inspirado na arquitetura do Balatro: matemática simples, profundidade emergente via interações.

---

## 1. Fórmula Universal de Dano

$$DAMAGE_{final} = \Big[\big(BASE\_POWER + \sum FLAT\big) \times \prod MULT \times \prod XMULT_{capped}\Big] \times DEFENSE\_MODIFIER$$

Uma única fórmula para todas as classes, skills e situações.
A identidade vem dos **pesos e modificadores**, não de equações separadas.

---

## 2. Geração do Poder Base

$$BASE\_POWER = (W_{class} \cdot A) + weapon_{power}$$

Onde:
- `A` = vetor de atributos `[ST, MG, AG]`
- `W_class` = vetor de pesos da classe
- `weapon_power` = poder bruto da arma equipada

### Matriz de Pesos por Classe

| Classe  | w_ST | w_MG | w_AG |
|---------|------|------|------|
| Warrior | 1.6  | 0.4  | 0.0  |
| Mage    | 0.3  | 1.9  | 0.0  |
| Rogue   | 0.8  | 0.4  | 1.7  |

> **Nota:** Warrior e Mage não usam AG no poder base.
> AG para essas classes alimenta apenas Speed (ordem de turno) e hit_chance.

---

## 3. Pipeline de Modificadores

Os sistemas do jogo não geram dano — injetam operadores no pipeline.

### 3.1 Modificadores Aditivos (FLAT e MULT)

Bônus lineares. Acumulam-se de forma previsível.

$$\prod MULT = 1 + \sum \Delta mult$$

**Fontes:** skills comuns, buffs de buff, equipamentos passivos, atributos secundários.

### 3.2 Modificadores Multiplicativos (XMULT)

Multiplicadores puros. Reservados para gatilhos de alto impacto.

$$\prod XMULT_{raw} = \prod_{i=1}^{n} xmult_i$$

**Fontes:** cartas de dungeon, passivas de alto risco, condições críticas de estado.

### 3.3 Teto Obrigatório de XMULT

Para evitar explosão numérica por empilhamento de multiplicadores:

$$\prod XMULT_{capped} = \min\!\Big(\prod XMULT_{raw},\ 5.0\Big)$$

> Exemplo sem teto: Full House (3.0) × Execute (2.0) × Glass Soul (1.8) × Crit (1.5) = **16.2×**
> Com teto de 5.0: resultado máximo é **5.0×** — previsível e balanceável.

---

## 4. Resolução de Crítico

O crítico injeta no produtório de XMULT **antes** do teto ser aplicado.

```
Se rand(0, 100) <= crit_chance:
    XMULT_raw *= crit_damage_multiplier
```

**Limites obrigatórios:**

| Parâmetro          | Valor  |
|--------------------|--------|
| crit_chance máximo | 75%    |
| crit_damage padrão | 1.5×   |

---

## 5. Curva de Mitigação de Defesa

Curva hiperbólica de rendimento decrescente. O dano **nunca** chega a zero.

$$DEFENSE\_MODIFIER = \frac{k}{k + defense_{target}}$$

Onde `k = 100` (constante de calibração).

| defense | Mitigação | Dano recebido |
|---------|-----------|---------------|
| 0       | 0%        | 100%          |
| 30      | 23%       | 77%           |
| 100     | 50%       | 50%           |
| 200     | 67%       | 33%           |
| 300     | 75%       | 25%           |
| 500     | 83%       | 17%           |
| 1000    | 91%       | 9%            |

---

## 6. Injeção por Sistema

### Skills
| Skill     | Injeção                                          |
|-----------|--------------------------------------------------|
| Fireball  | `ΔMULT += 0.35`, `Resource_cost += 20 MP`        |
| Execute   | `Se HP_target < 30%: XMULT *= 2.0`              |

### Equipamentos
| Item          | Injeção                                              |
|---------------|------------------------------------------------------|
| Sword         | `FLAT += 25`                                         |
| Ancient Staff | `ΔMULT += 0.20`                                      |
| Cursed Dagger | `crit_chance += 15`, trigger: `hp_drain = 5/turno`   |

### Cartas de Dungeon
| Carta        | Injeção                                                       |
|--------------|---------------------------------------------------------------|
| 7 of Blades  | `ΔMULT += 0.25`                                               |
| Full House   | `XMULT *= 3.0`, `healing_modifier *= 0.5`                     |
| Ace of Death | `damage_incoming *= 1.5`, `crit_chance += 20`                 |

#### Apenas exemplo, cartas não foi introduzida ainda.

### Passivas
| Passiva      | Injeção                                                       |
|--------------|---------------------------------------------------------------|
| Battle Focus | `ΔMULT += 0.05 × stack_combo`                                 |
| Glass Soul   | `XMULT *= 1.8`, `DEFENSE_MODIFIER *= 0.7`                     |

---

## 7. Economia de Recursos (Condição de Contorno)

A jogada só é executada se o custo for viável:

$$Cost_{vector} = \begin{bmatrix} \Delta HP \\ \Delta MP \\ \Delta Essence \\ \Delta Corruption \end{bmatrix}$$

Se qualquer componente do vetor exceder o recurso disponível, a ação é bloqueada pelo sistema — independente do DAMAGE_final calculado.

---

## 8. Constantes de Calibração

| Constante           | Valor | Descrição                            |
|---------------------|-------|--------------------------------------|
| `DEFENSE_K`         | 100   | Curva de mitigação                   |
| `XMULT_CAP`         | 5.0   | Teto de multiplicadores puros        |
| `CRIT_CHANCE_CAP`   | 75    | % máximo de chance crítica           |
| `CRIT_DAMAGE_BASE`  | 1.5   | Multiplicador padrão de crítico      |

> Estas constantes residem em `src/shared/constants.py` e são os únicos valores
> a serem ajustados durante o balanceamento. Nunca hardcode esses valores inline.