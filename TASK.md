# TASK.md — TOJ
> Substitua o conteúdo deste arquivo a cada nova sessão. Um arquivo, uma sessão, um objetivo.

---

## Sessão Atual
**ID:** TASK-001
**Data:** 02/05/2026
**Status:** ✅ Concluída

---

## Objetivo

Implementar o **Multiplicador de Essência por Andar** — o primeiro elemento do novo Game Design que diferencia o TOJ de um RPG genérico. Ao entrar em cada novo andar, um multiplicador aleatório é gerado e exibido no HUD. Toda a Essência (XP) recebida naquele andar é afetada por ele.

---

## Contexto do Game Design

Do `GAME_DESIGN.md`:

> "O Multiplicador de Essência é re-gerado a cada novo andar da masmorra. O valor é exibido claramente para o jogador (ex: 'Andar 5 — Multiplicador 2.1x'). O multiplicador varia de 0.5x a 3.0x, com valores intermediários tendendo à normalidade."

O multiplicador deve ser visível no HUD do mapa e influenciar diretamente o XP concedido em `process_post_battle()`.

---

## Arquivos que serão tocados

| Arquivo | O que muda |
|---|---|
| `src/shared/constants.py` | Adicionar constantes: `ESSENCE_MULT_MIN`, `ESSENCE_MULT_MAX`, `ESSENCE_MULT_NORMAL_MEAN`, `ESSENCE_MULT_NORMAL_STD` |
| `src/engine/loop.py` | Gerar multiplicador ao iniciar cada andar; passar para `process_post_battle()`; passar para `render_dungeon_status()` |
| `src/mechanics/math_operations.py` | Nova função `generate_essence_multiplier() -> float` com distribuição gaussiana truncada |
| `src/ui/screens.py` | Atualizar `render_dungeon_status()` para exibir o multiplicador com cor baseada no valor |

**Arquivos que NÃO devem ser tocados:**
- `src/entities/` (nenhuma mudança de estado de entidade)
- `src/storage/save_manager.py` (o multiplicador é volátil, não persiste no save)
- `src/ui/renderer.py`
- Qualquer arquivo de `content/`

---

## Especificação Técnica

### 1. Constantes (`src/shared/constants.py`)

```python
# Multiplicador de Essência por Andar
ESSENCE_MULT_MIN = 0.5
ESSENCE_MULT_MAX = 3.0
ESSENCE_MULT_NORMAL_MEAN = 1.2   # Centro da curva gaussiana
ESSENCE_MULT_NORMAL_STD = 0.5    # Desvio padrão (controla variação)
```

### 2. Gerador (`src/mechanics/math_operations.py`)

```python
def generate_essence_multiplier() -> float:
    """Gera multiplicador de Essência para o andar usando distribuição gaussiana truncada.
    
    Returns:
        Multiplicador entre ESSENCE_MULT_MIN e ESSENCE_MULT_MAX, arredondado para 1 casa.
        Valores intermediários são mais prováveis que extremos.
    """
```

Usar `random.gauss(mean, std)` com clamp entre MIN e MAX. Arredondar para 1 casa decimal.

### 3. Loop de jogo (`src/engine/loop.py`)

- `start_game()`: gerar `essence_multiplier = generate_essence_multiplier()` no início de cada andar (quando um novo mapa é criado)
- Passar o multiplicador para `process_post_battle()` como parâmetro
- Passar o multiplicador para `render_dungeon_status()` como parâmetro

Assinatura atualizada de `process_post_battle()`:
```python
def process_post_battle(
    player: "Player",
    monster: "Monster",
    essence_multiplier: float = 1.0,
) -> tuple[int, bool, object | None, list[str]]:
```

O cálculo de XP passa a ser:
```python
xp_gained = int(xp_base_reward * essence_multiplier)
```

### 4. HUD do mapa (`src/ui/screens.py`)

`render_dungeon_status()` deve exibir o multiplicador com cor:
- `< 0.8x` → vermelho (escassez)
- `0.8x – 1.5x` → amarelo/branco (normal)
- `> 1.5x` → verde (fartura)

Exemplo de output:
```
Masmorra Nível 3 | Multiplicador: [2.1x] | HP: 80/104 | MP: 30/30
```

---

## Critérios de Aceite

- [x] Um novo multiplicador é gerado a cada vez que o jogador desce para um novo andar (não ao carregar o save)
- [x] O multiplicador é exibido no HUD do mapa com a cor correta para o valor
- [x] O XP recebido ao derrotar monstros reflete o multiplicador
- [x] Valores extremos (0.5x e 3.0x) são raros mas possíveis (distribuição gaussiana)
- [x] O multiplicador não é salvo no `savegame.json` (volta a 1.0x ao carregar)
- [x] `ruff check src/` passa sem erros novos (apenas warnings pré-existentes)
- [ ] O auto-test (modo BOT) conclui um run sem crash (testar manualmente)

---

## O Que NÃO Fazer Nesta Sessão

- ❌ Não criar o sistema de cartas de passivas (é TASK-002)
- ❌ Não modificar o sistema de slots de personagem/permadeath (é TASK-003)
- ❌ Não adicionar cooldowns ao combate (é TASK-005)
- ❌ Não criar eventos aleatórios de andar (é TASK-004)
- ❌ Não tocar em `save_manager.py`
- ❌ Não alterar a lógica de spawn de monstros
- ❌ Não introduzir nenhuma dependência nova (sem novos pacotes pip)

---

## Decisões Abertas (responder ANTES de implementar)

1. **O multiplicador persiste se o jogador salvar e recarregar no mesmo andar?**
   → Sugestão: NÃO. Multiplicador é gerado ao entrar no andar, não ao carregar o save. Se recarregar, assume 1.0x. Simples.

2. **O multiplicador afeta apenas XP ou também gold drop?**
   → Sugestão: apenas XP/Essência por enquanto. Gold é separado (será modificado pelo sistema de passivas futuro).

3. **O multiplicador deve aparecer na tela de pós-batalha?**
   → Sugestão: SIM. Exibir "XP ganho: 84 (×2.1)" na `render_post_battle()`.

**Confirme ou ajuste as decisões acima antes de o Windsurf começar.**

---

## Entrega Esperada

Ao finalizar, o Windsurf deve:
1. Listar todos os arquivos modificados
2. Mostrar o diff das assinaturas de função que mudaram
3. Confirmar que `ruff check src/` passou
4. **Aguardar aprovação antes de qualquer passo adicional**

---

## Backlog de Sessões Futuras

| ID | Objetivo | Depende de |
|---|---|---|
| TASK-002 | Sistema de cartas de passivas ao subir de nível | TASK-001 |
| TASK-003 | 10 slots de personagem + permadeath + Troféu de Fracasso | TASK-001 |
| TASK-005 | Cooldowns de habilidades no combate | TASK-002 |
| TASK-006 | Opção "Sair da Masmorra" entre andares | TASK-003 |