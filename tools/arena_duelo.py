"""Demonstração de UM duelo da Arena, determinístico, com o registro por rodada.

Uso: `python tools/arena_duelo.py [semente]`

É uma partida, não uma medição: não diz nada sobre balanceamento entre classes.
Os dois gladiadores passam pelo caminho real da Arena — personagem extraído,
snapshot de save (`to_save_data`), reconstrução e preparação
(`gladiator_from_snapshot`) — e os dois lados são controlados pela política de
referência mais simples (`FirstLegalSkillController`).

O duelo é criado pelo caminho normal: referências canônicas de iniciativa e
desempate pela semente, sem nada injetado. A ferramenta mostra a iniciativa
porque é ferramenta de desenvolvimento; a UI normal não a mostra.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.extraction import mark_extracted  # noqa: E402
from src.content.skills_loader import get_skill_by_id  # noqa: E402
from src.engine.arena_setup import gladiator_from_snapshot  # noqa: E402
from src.mechanics.pvp_duel import SIDES, Duel, run_round  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.pvp_controllers import FirstLegalSkillController  # noqa: E402
from src.storage.save_manager import to_save_data  # noqa: E402

NIVEL = 10
SEMENTE_PADRAO = 2026
GLADIADORES = (
    ("Warrior", "Brakka", ("golpe_poderoso", "investida", "escudo_protetor", "grito_guerra")),
    ("Mage", "Ilsa", ("bola_fogo", "missil_magico", "drenar_vida", "escudo_magico")),
)
# Teto do LAÇO desta ferramenta, contra um duelo que não acaba. O motor não tem
# teto: quem conduz o duelo decide quando parar.
LIMITE_DA_DEMO = 1000


def snapshot_extraido(classe: str, nome: str, deck) -> dict:
    """Um personagem do nível pedido, com o equipamento esperado, extraído e salvo."""
    heroi = make_hero(classe, NIVEL, "expected")
    heroi.nick_name = nome
    heroi.skills = {i: get_skill_by_id(sid) for i, sid in enumerate(deck, start=1)}
    mark_extracted(heroi, NIVEL)
    return to_save_data(heroi, NIVEL)


def _acao(passo, duelo: Duel) -> str:
    acao = passo.action
    if acao.kind == "skill":
        nome = next(s.name for s in duelo.hero(passo.side).skills.values() if s.id == acao.skill_id)
    else:
        nome = {"attack": "Ataque básico", "surrender": "Rendição"}[acao.kind]
    if passo.outcome != "executed":
        return f"{nome} — {passo.outcome}"
    extra = f", MP -{passo.mp_spent}" if passo.mp_spent else ""
    return f"{nome} — dano {passo.damage_to_opponent}{extra}"


def main(semente: int) -> None:
    duelo = Duel(
        *(gladiator_from_snapshot(snapshot_extraido(*g)) for g in GLADIADORES),
        rng=random.Random(semente),
    )
    nomes = {lado: duelo.hero(lado).nick_name for lado in SIDES}
    print(f"Arena — {nomes['p1']} (p1) x {nomes['p2']} (p2), nível {NIVEL}, semente {semente}")
    for lado in SIDES:
        h = duelo.hero(lado)
        print(
            f"  {lado} {h.get_classname():7} HP {h.get_hp()}/{h.base_hp}  MP {h.get_mp()}/"
            f"{h.base_mp}  deck {h.active_skill_ids()}"
        )

    controladores = {lado: FirstLegalSkillController() for lado in SIDES}
    while not duelo.finished and duelo.round_number <= LIMITE_DA_DEMO:
        r = run_round(duelo, controladores)
        score = {x.side: x.score for x in r.initiative}
        cabecalho = (
            f"R{r.number:02d} {r.order.first}→{r.order.second} "
            f"(score {score['p1']:.4f} x {score['p2']:.4f}, {r.order.decided_by})"
        )
        passos = " | ".join(f"{p.side}: {_acao(p, duelo)}" for p in r.steps)
        hp = "  ".join(f"{lado} HP {v}" for lado, v in r.hp_end)
        print(f"{cabecalho}\n     {passos}\n     {hp}")

    resultado = duelo.result
    if resultado is None:
        print(f"Sem resultado em {LIMITE_DA_DEMO} rodadas (teto da demonstração).")
        return
    print(
        f"Vencedor: {resultado.winner_name} ({resultado.winner}) — {resultado.reason}, "
        f"{resultado.rounds} rodadas"
    )


if __name__ == "__main__":
    main(int(sys.argv[1]) if len(sys.argv) > 1 else SEMENTE_PADRAO)
