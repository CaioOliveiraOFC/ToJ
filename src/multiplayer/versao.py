"""A versão que esta instalação DECLARA ser.

Quatro identificadores, escolhidos por gente e mudados de propósito. O que eles
valem não é afirmado aqui: o manifesto da versão
(`src/multiplayer/manifestos/<VERSAO_DO_JOGO>.json`) amarra cada um ao hash do
conteúdo que ele nomeia, e o gate de publicação recusa a instalação cujo código
não bate com o manifesto (`tools/multiplayer_manifesto.py verificar`).

Este arquivo fica FORA dos hashes: ele é a declaração, não o conteúdo medido.

Quando mudar cada um:

- `VERSAO_DO_JOGO`: a cada distribuição. Um manifesto publicado é imutável, então
  qualquer mudança no conteúdo medido depois de uma publicação exige uma versão
  nova.
- `VERSAO_DO_PROTOCOLO`: quando o formato das mensagens muda
  (`src/multiplayer/protocolo.py`).
- `REGRAS_DE_COMBATE`: quando muda qualquer regra de combate (`src/mechanics/`,
  `src/shared/`, `src/entities/`). O gate recusa duas versões com o mesmo
  identificador de regras e regras diferentes.
- `ESQUEMA_DO_GLADIADOR`: quando muda o formato persistido do gladiador ou o
  caminho de reconstrução (`src/storage/`, `src/engine/arena_setup.py`,
  `src/multiplayer/gladiadores.py`). Um esquema novo exige migração registrada
  em `gladiadores.MIGRACOES`.
"""

from __future__ import annotations

VERSAO_DO_JOGO = "0.4.0-arena.2"
VERSAO_DO_PROTOCOLO = 2
REGRAS_DE_COMBATE = "duelo-1"
ESQUEMA_DO_GLADIADOR = 1


def declarados() -> dict[str, object]:
    """Os quatro identificadores, com os nomes de campo do manifesto."""
    return {
        "jogo": VERSAO_DO_JOGO,
        "protocolo": VERSAO_DO_PROTOCOLO,
        "regras": REGRAS_DE_COMBATE,
        "esquema_gladiador": ESQUEMA_DO_GLADIADOR,
    }
