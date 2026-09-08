"""Interruptores de sistema para ablação.

Medir "quanto este sistema importa" exige desligá-lo e comparar. Sem um lugar
único para os interruptores, cada experimento vira um `if` espalhado pelo
código de simulação, e o experimento seguinte não consegue repetir o anterior.

Todo campo é `True` por padrão: a run normal roda o jogo inteiro. Uma ablação é
sempre uma cópia com um campo desligado, o que torna óbvio, na leitura do
resultado, o que exatamente foi removido.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace


@dataclass(frozen=True)
class Toggles:
    """Quais sistemas a run simulada executa."""

    passives: bool = True
    skill_choice: bool = True
    loot: bool = True
    shop: bool = True
    events: bool = True
    essence: bool = True
    # Cartas removidas do sorteio. Usado para medir uma skill ou passiva
    # específica, em vez do sistema inteiro.
    banned_skills: frozenset[str] = field(default_factory=frozenset)
    banned_passives: frozenset[str] = field(default_factory=frozenset)

    def without(self, **kwargs) -> "Toggles":
        """Cópia com os campos indicados alterados."""
        return replace(self, **kwargs)

    def label(self) -> str:
        """Nome curto do que foi desligado, para aparecer no relatório."""
        desligados = [
            nome for nome in ("passives", "skill_choice", "loot", "shop", "events", "essence")
            if not getattr(self, nome)
        ]
        if self.banned_skills:
            desligados.append("sem_skill:" + ",".join(sorted(self.banned_skills)))
        if self.banned_passives:
            desligados.append("sem_passiva:" + ",".join(sorted(self.banned_passives)))
        return "+".join(desligados) if desligados else "completo"


ALL_ON = Toggles()

# Os sistemas que a ablação de primeiro corte desliga, um por vez.
ABLATION_SYSTEMS = ("passives", "skill_choice", "loot", "shop", "events", "essence")
