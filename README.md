# Tales of the Journey

RPG de masmorra em terminal, em português. Permadeath: o personagem morre e a run
acaba. Cada andar é uma decisão entre descer mais fundo e sair com o que tem.

## Rodar

```bash
python -m src.main
```

Requer Python 3.11+ e `rich`. Instalação de desenvolvimento:

```bash
pip install -e ".[dev]"
```

## Testar

```bash
python -m pytest -q                 # suíte funcional — precisa ficar verde
python -m pytest -q -m balance      # medição de balanceamento — informa, não bloqueia
ruff check . && ruff format --check .
```

A separação é deliberada. A suíte padrão protege comportamento e propriedades
estruturais; se ela quebra, há um defeito. A suíte `-m balance` mede bandas
calibradas para o meta atual; se ela sai da faixa, isso é informação sobre o
jogo, e pode ser a resposta certa a uma mudança de design.

## Ferramentas de simulação

Rodam sem UI, direto sobre as regras:

```bash
python -m src.sim.runner run --iterations 500        # runs completas
python -m src.sim.runner scout                       # destaques por sistema
python -m src.sim.runner progression --max-floor 500 # nível do herói × encontro
```

## Documentação

- [`GAME_DESIGN.md`](GAME_DESIGN.md) — o design do jogo que existe, e a matemática
  do combate.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — as camadas e as regras que os testes
  verificam.
