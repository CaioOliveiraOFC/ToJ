# Tales of the Journey

RPG de masmorra em terminal, em português. Permadeath: o personagem morre e a run
acaba. Cada andar é uma decisão entre descer mais fundo e sair com o que tem.

A masmorra é **infinita** — não há andar final nem condição de vitória. A única
forma de uma run terminar bem é **extrair** o personagem vivo. Toda batalha é
**1x1**: um herói contra um monstro, chefe incluído.

## Rodar

```bash
python -m src.ui.toj_menu
```

Requer Python 3.10+ e `rich`. Não há `src/main.py` nem console script declarado:
o ponto de entrada é o menu. Instalação de desenvolvimento:

```bash
pip install -e ".[dev]"
```

## Testar

```bash
python -m pytest -q                 # suíte funcional
python -m pytest -q -m balance      # invariantes de balanceamento
ruff check . && ruff format --check .
```

Os três rodam na CI como **jobs bloqueantes**, em Python 3.10, 3.11 e 3.12. A CI
usa `-m "balance or balance_full"` no job de balanceamento; `balance_full` está
reservado para medições longas e hoje nenhum teste o declara.

A separação entre as duas suítes é deliberada, e não é "uma bloqueia, a outra
não". A suíte padrão protege comportamento e propriedades estruturais: se ela
quebra, há um defeito. A suíte `-m balance` mede bandas calibradas para o meta
atual: se ela sai da faixa, isso é informação sobre o jogo, e pode ser a resposta
certa a uma mudança de design — mas a banda tem de ser movida de propósito e com
o número registrado, nunca afrouxada para caber.

## Ferramentas de simulação

Rodam sem UI, direto sobre as regras:

```bash
python -m src.sim.runner run --iterations 500        # runs completas
python -m src.sim.runner scout                       # destaques por sistema
python -m src.sim.runner progression --max-floor 500 # nível do herói × encontro
```

Auditorias pontuais ficam em `tools/`: acessibilidade das interações
(`audit_interactions.py`), geometria do andar (`measure_map.py`) e o laço de
serviços, saída e punição (`measure_floor_loop.py`).

## Estrutura

```
src/shared/     tipos, constantes, fórmulas, efeitos e as 16 leis de interação
src/data/       os JSON de conteúdo (itens, monstros, skills, passivas)
src/entities/   estado: Player, Monster
src/mechanics/  combate e matemática
src/content/    catálogos, fábricas, economia, loja, Ferreiro, saída do andar
src/storage/    save/load
src/sim/        simulação headless
src/engine/     orquestração, mapa e laço de jogo
src/ui/         apresentação e input
```

As camadas não se importam livremente, e `tests/test_architecture.py` verifica
isso por AST — a regra está em [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Documentação

- [`GAME_DESIGN.md`](GAME_DESIGN.md) — o design do jogo que existe, a matemática
  do combate e as decisões ainda em aberto.
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — as camadas, a responsabilidade de cada
  módulo e as regras que os testes verificam.
