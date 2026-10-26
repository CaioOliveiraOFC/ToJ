"""Como cada lado conduziu o combate: o turno, o MP e o que ficou na mesa.

Métricas de DIAGNÓSTICO de uma partida auditada (`arena_copa_teste.Partida`),
lidas do trace (`escolha`: visão, ações legais, ação, recargas no lock) e do
histórico do duelo (`StepRecord`: desfecho, MP gasto, dano). Servem igual para
qualquer controlador — é o que permite pôr a `PoliticaCopa` e a IA estratégica
lado a lado com a mesma régua.

Um ataque básico tem sempre um MOTIVO, lido da visão e da ficha do próprio
lado, na mesma ordem de `Duel._skill_problem`:

- `mp`: nenhuma carta legal, e ao menos uma esbarrava só no MP livre — o limite
  da economia de MP;
- `recarga`: nenhuma carta legal, e as que existem estavam em recarga;
- `requisito`: nenhuma carta legal, só por equipamento;
- `preferencia`: havia carta legal e o controlador escolheu o básico. Na
  `PoliticaCopa` isso é "nenhuma regra dela pedia carta"; na IA, "a avaliação
  preferiu o básico".
"""

from __future__ import annotations

from collections import Counter

from src.mechanics.pvp_duel import SIDES
from src.shared import effect_core as core
from src.shared.constants import MP_REGEN_PERCENT_PER_TURN
from tools.arena_ia_estrategica import cura_esperada, utilizavel

MOTIVOS = ("mp", "recarga", "requisito", "preferencia")
ROTULO_DO_MOTIVO = {
    "mp": "MP insuficiente",
    "recarga": "recarga",
    "requisito": "requisito de equipamento",
    "preferencia": "havia skill legal (escolha do controlador)",
}
CONTROLE = frozenset(core.effects_of_family(core.FAMILY_CONTROL))


def _motivo_do_basico(escolha: dict, deck: dict, heroi) -> str:
    legais = {a["skill_id"] for a in escolha["acoes_legais"] if a["kind"] == "skill"}
    if legais:
        return "preferencia"
    recargas = escolha.get("recargas_no_lock", {})
    motivos = set()
    for sid, carta in deck.items():
        if not utilizavel(heroi, carta):
            motivos.add("requisito")
        elif int(recargas.get(sid, 0)) > 0:
            motivos.add("recarga")
        else:
            motivos.add("mp")
    for motivo in ("mp", "recarga", "requisito"):
        if motivo in motivos:
            return motivo
    return "requisito"


def _sequencias(flags: list[bool]) -> list[tuple[int, int]]:
    """(início, comprimento) de cada sequência de `True`."""
    saida, inicio = [], None
    for i, f in enumerate(flags + [False]):
        if f and inicio is None:
            inicio = i
        elif not f and inicio is not None:
            saida.append((inicio, i - inicio))
            inicio = None
    return saida


def _executou(passo) -> bool:
    return passo is not None and passo.outcome == "executed"


def metricas_do_lado(escolhas: list[dict], historico, lado: str, heroi) -> dict:
    """As métricas de condução de `lado` num duelo.

    `escolhas` são os registros `escolha` do lado (o formato do trace auditado,
    ou o de `RegistroDeEscolhas`); `historico`, o `Duel.history`; `heroi`, a
    ficha do participante: deck, custos e requisitos.
    """
    deck = {s.id: s for s in heroi.skills.values()}
    escolhas = [e for e in escolhas if e["lado"] == lado]
    passos = {r.number: next(s for s in r.steps if s.side == lado) for r in historico}
    # O dano que o outro me causou ANTES da minha vez, em cada rodada: a cura que
    # sai depois dele encontra mais HP faltando do que a visão do lock mostrava.
    antes_de_mim = {
        r.number: sum(
            s.damage_to_opponent for s in r.steps if s.side != lado and s.outcome == "executed"
        )
        if r.order.first != lado
        else 0
        for r in historico
    }
    basicos = [e["acao"]["kind"] == "attack" for e in escolhas]
    motivos = [
        _motivo_do_basico(e, deck, heroi) if b else None
        for e, b in zip(escolhas, basicos, strict=True)
    ]
    seqs = _sequencias(basicos)
    maior = max(seqs, key=lambda s: s[1], default=(0, 0))
    composicao = Counter(m for m in motivos[maior[0] : maior[0] + maior[1]] if m)
    # Rodada sem skill: escolheu o básico, ou a carta não chegou a sair (controle).
    sem_skill = [
        not (e["acao"]["kind"] == "skill" and _executou(passos.get(e["rodada"]))) for e in escolhas
    ]

    por_tipo: Counter = Counter()
    mp_em_dano = dano_de_skill = dano_basico = basicos_executados = 0
    cura_excedente = cura_lancada = 0
    controle_redundante = status_redundante = buff_redundante = 0
    teto_sem_gastar = regen_no_teto = 0
    for e in escolhas:
        passo = passos.get(e["rodada"])
        visao = e["visao"]
        me, outro = visao["me"], visao["opponent"]
        legais = [a for a in e["acoes_legais"] if a["kind"] == "skill"]
        if e["acao"]["kind"] == "attack":
            if me["mp"] >= me["mp_max"] and legais:
                teto_sem_gastar += 1
                regen_no_teto += max(1, int(me["mp_max"] * MP_REGEN_PERCENT_PER_TURN / 100))
            if passo is not None and passo.outcome == "executed":
                basicos_executados += 1
                dano_basico += passo.damage_to_opponent
            continue
        if e["acao"]["kind"] != "skill":
            continue
        carta = deck[e["acao"]["skill_id"]]
        por_tipo[carta.effect_type] += 1
        if carta.effect_type == "status":
            efeito = str(carta.effect_value)
            definicao = core.definition(efeito)
            if efeito in CONTROLE and any(x in CONTROLE for x in outro["effects"]):
                controle_redundante += 1
            elif (
                efeito in outro["effects"]
                and definicao is not None
                and definicao.stack_rule != core.STACK_COUNT
            ):
                status_redundante += 1
        # Relançar com duração 1 é lançar de novo: o buff sai no começo da minha
        # vez, antes de agir. Redundante é relançar com ele ainda valendo depois.
        duracao = e.get("duracoes_buffs", {}).get(carta.name, 2 if carta.name in me["buffs"] else 0)
        if carta.effect_type in ("buff", "damage_reduction") and duracao >= 2:
            buff_redundante += 1
        if passo is None or passo.outcome != "executed":
            continue
        if carta.effect_type == "damage":
            mp_em_dano += passo.mp_spent
            dano_de_skill += passo.damage_to_opponent
        if carta.effect_type == "heal":
            cura = cura_esperada(heroi, carta)
            cura_lancada += cura
            faltava = me["hp_max"] - me["hp"] + antes_de_mim.get(e["rodada"], 0)
            cura_excedente += max(0, cura - faltava)

    executados = [s for s in passos.values() if s.outcome == "executed"]
    mp_gasto = sum(s.mp_spent for s in executados)
    mp_inicial = escolhas[0]["visao"]["me"]["mp"] if escolhas else 0
    ultimo = historico[-1] if historico else None
    mp_final = dict(ultimo.mp_end)[lado] if ultimo else mp_inicial
    skills = sum(por_tipo.values())
    return {
        "rodadas": len(escolhas),
        "basicos": sum(basicos),
        "skills": skills,
        "skills_por_tipo": dict(por_tipo),
        "basicos_por_motivo": dict(Counter(m for m in motivos if m)),
        "max_basicos_seguidos": maior[1],
        "motivo_da_maior_sequencia": dict(composicao),
        "sequencias_5_ou_mais": sum(1 for _, n in seqs if n >= 5),
        "rodadas_sem_skill": sum(sem_skill),
        "max_rodadas_sem_skill": max((n for _, n in _sequencias(sem_skill)), default=0),
        "perdidas_por_controle": sum(
            1 for s in passos.values() if s.outcome == "cancelled_control"
        ),
        "mp_inicial": mp_inicial,
        "mp_gasto": mp_gasto,
        "mp_final": mp_final,
        # Conservação: final = inicial + regenerado − gasto (dreno e Égide à parte).
        "mp_regenerado": mp_final - mp_inicial + mp_gasto,
        "mp_em_dano": mp_em_dano,
        "dano_de_skill": dano_de_skill,
        "dano_basico": dano_basico,
        "basicos_executados": basicos_executados,
        "rodadas_no_teto_sem_gastar": teto_sem_gastar,
        "regen_perdida_no_teto": regen_no_teto,
        "cura_lancada": cura_lancada,
        "cura_excedente": cura_excedente,
        "controle_redundante": controle_redundante,
        "status_redundante": status_redundante,
        "buff_redundante": buff_redundante,
    }


def metricas_da_partida(partida, herois: dict) -> dict:
    """As métricas dos dois lados de uma partida auditada. `herois`: id -> herói."""
    trace = partida.auditado.trace
    duracoes = {
        (r["rodada"], lado): {n: b["duracao"] for n, b in r["estado"][lado]["buffs"].items()}
        for r in trace.de("rodada_inicio")
        for lado in SIDES
    }
    escolhas = [
        dict(e, duracoes_buffs=duracoes.get((e["rodada"], e["lado"]), {}))
        for e in trace.de("escolha")
    ]
    historico = partida.auditado.duelo.history
    return {
        lado: metricas_do_lado(escolhas, historico, lado, herois[partida.lados[lado].id])
        for lado in SIDES
    }


class RegistroDeEscolhas:
    """Envolve um controlador e anota cada escolha no formato do trace auditado.

    Para os duelos sem auditoria: só os campos que `metricas_do_lado` lê. Não
    muda nada do que o controlador faz.
    """

    def __init__(self, interno, lado: str, registros: list, heroi=None) -> None:
        self.interno = interno
        self._lado = lado
        self._registros = registros
        self._heroi = heroi

    def choose(self, view):
        acao = self.interno.choose(view)
        self._registros.append(
            {
                "lado": self._lado,
                "rodada": view.round_number,
                "visao": {
                    "me": _lutador(view.me),
                    "opponent": _lutador(view.opponent),
                },
                "acoes_legais": [
                    {"kind": a.kind, "skill_id": a.skill_id} for a in view.legal_actions
                ],
                "acao": {"kind": acao.kind, "skill_id": acao.skill_id},
                "recargas_no_lock": dict(view.cooldowns),
                "duracoes_buffs": {
                    str(n): int(d.get("duration", 0))
                    for n, d in getattr(self._heroi, "active_buffs", {}).items()
                },
            }
        )
        return acao


def _lutador(f) -> dict:
    return {
        "hp": f.hp,
        "hp_max": f.hp_max,
        "mp": f.mp,
        "mp_max": f.mp_max,
        "effects": list(f.effects),
        "buffs": list(f.buffs),
    }


def somar(lista: list[dict]) -> dict:
    """Soma as métricas de vários lados; máximos ficam como máximo."""
    total: dict = {"lados": len(lista)}
    for m in lista:
        for k, v in m.items():
            if k.startswith("max_"):
                total[k] = max(total.get(k, 0), v)
            elif isinstance(v, dict):
                alvo = total.setdefault(k, Counter())
                alvo.update(v)
            else:
                total[k] = total.get(k, 0) + v
    for k, v in list(total.items()):
        if isinstance(v, Counter):
            total[k] = dict(v)
    return total
