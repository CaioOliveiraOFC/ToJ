"""Copa Arena de Testes 01: mata-mata de oito gladiadores e a final auditada.

Uso: `python tools/arena_copa_teste.py`

Experimento de DIAGNÓSTICO da matemática do duelo. Não mede balanceamento entre
classes nem forma a população ranked.

Os oito bonecos (3 Guerreiros, 3 Magos, 2 Ladinos) são montados só com o que o
jogo já tem: classe e nível pelo caminho da simulação (`make_hero`), o
equipamento do `expected loadout` daquele nível, cartas que a oferta real pode
dar naquele nível e passivas Comuns na quantidade esperada. O poder é o canônico,
`sim.arena.overall_power`, e a calibração para perto do nível equivalente 10 foi
feita trocando nível e escolhas do catálogo — nunca atributo.

Isolamento: os bonecos vivem só em memória. Recebem a marca de extração porque a
preparação da Arena (`prepare_gladiator`) a exige, mas nunca passam pelo save,
não ocupam slot e não entram em lista de gladiadores.

Cada partida começa de gladiadores recém-preparados (HP e MP cheios, sem recarga
nem efeito), com semente própria derivada da principal e da posição na chave, e a
mesma política simples dos dois lados. Cada partida roda DUAS vezes — sem
instrumentação e auditada — e as duas precisam coincidir em tudo.
"""

from __future__ import annotations

import hashlib
import json
import random
import statistics
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.extraction import mark_extracted, was_extracted  # noqa: E402
from src.content.gladiator import prepare_gladiator  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.level_up import oferece_skill  # noqa: E402
from src.content.passives import get_passive_by_id  # noqa: E402
from src.content.skills_loader import (  # noqa: E402
    get_initial_skills,
    get_offer_pool,
    get_skill_by_id,
)
from src.mechanics.pvp_duel import SIDES, DuelAction, opponent_of  # noqa: E402
from src.mechanics.pvp_initiative import foundation_reference  # noqa: E402
from src.shared.constants import (  # noqa: E402
    BASIC_ATTACK_POWER_MULT,
    DEFENSE_K,
    PERCENTAGE_RANGE_MAX,
    PERCENTAGE_RANGE_MIN,
    PVP_INITIATIVE_LEVEL_STEP,
    XMULT_CAP,
)
from src.sim.arena import overall_power  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.loadouts import expected_passive_count  # noqa: E402
from tools.arena_auditoria import DueloAuditado, disputar  # noqa: E402

SEMENTE_PRINCIPAL = 20261023
# Teto do LAÇO desta ferramenta contra um duelo que não acaba. Não é regra: o
# motor não tem teto, e um duelo que bate aqui é inconclusivo, nunca empate.
LIMITE_TECNICO = 500
FAIXA_DE_PODER = (9.0, 11.0)
LIMIAR_DE_CURA = 0.5
FASES = (("quartas", 4), ("semifinal", 2), ("final", 1))
NOME_DA_FASE = {"quartas": "Quartas", "semifinal": "Semifinal", "final": "Final"}
PASTA_DE_SAIDA = RAIZ / "reports" / "pvp"
ARQUIVO_RESUMO = "copa_teste_01.md"
ARQUIVO_FINAL = "copa_teste_01_final_detalhada.md"
ARQUIVO_TRACE = "copa_teste_01_trace.json"
DESFECHO = {
    "executed": "executada",
    "cancelled_control": "cancelada por controle",
    "cancelled_death": "cancelada por morte",
    "not_reached": "não alcançada (o duelo acabou antes)",
}
CLASSE = {"Warrior": "Guerreiro", "Mage": "Mago", "Rogue": "Ladino"}


class BuildIlegitimaError(ValueError):
    """A build pede algo que o catálogo e as regras de montagem não permitem."""


@dataclass(frozen=True)
class Especificacao:
    id: str
    nome: str
    classe: str
    nivel: int
    deck: tuple[str, ...]
    passivas: tuple[str, ...]
    foco: str


# As passivas entram em ciclo até `nível − 1` cartas, como o `expected loadout`.
ESPECIFICACOES = (
    Especificacao(
        "G1",
        "Muralha",
        "Warrior",
        7,
        ("golpe_poderoso", "couraca_improvisada", "baluarte"),
        ("pele_grossa", "postura_fechada", "coracao_ferro", "sangue_guerreiro"),
        "defesa: duas reduções de dano, Defesa e HP",
    ),
    Especificacao(
        "G2",
        "Carrasco",
        "Warrior",
        7,
        ("golpe_poderoso", "grito_guerra", "cutelada"),
        ("musculos_aco", "odio_baixo", "pulso_certeiro", "olho_aguia"),
        "dano físico: buff de Força, +MULT e crítico",
    ),
    Especificacao(
        "G3",
        "Sentinela",
        "Warrior",
        6,
        ("golpe_poderoso", "investida", "pisada_de_ferro"),
        ("olho_de_cacador", "pele_de_sal", "musculos_aco", "coracao_ferro"),
        "precisão e controle leve: atordoar e lentidão, resistência a status",
    ),
    Especificacao(
        "G4",
        "Piromante",
        "Mage",
        6,
        ("bola_fogo", "missil_magico", "marca_ardente"),
        ("sangue_de_vidente", "odio_baixo", "pulso_certeiro", "olho_aguia"),
        "dano mágico: Magia, +MULT, crítico e veneno",
    ),
    Especificacao(
        "G5",
        "Curandeira",
        "Mage",
        7,
        ("bola_fogo", "drenar_vida", "pele_de_quartzo"),
        ("coracao_ferro", "respiracao_contada", "boca_de_sangue", "reserva_arcana"),
        "sustentação: cura, roubo de vida, regeneração e reserva de MP",
    ),
    Especificacao(
        "G6",
        "Geada",
        "Mage",
        6,
        ("bola_fogo", "lasca_de_gelo", "palavra_de_torpor"),
        ("mente_serena", "pele_de_sal", "sangue_de_vidente", "olho_de_cacador"),
        "controle: lentidão e névoa, com reserva de MP",
    ),
    Especificacao(
        "G7",
        "Navalha",
        "Rogue",
        6,
        ("ataque_furtivo", "respiracao_de_ladrao", "corte_de_tendao"),
        ("olho_aguia", "pulso_certeiro", "passo_de_corca", "passos_leves"),
        "agilidade e crítico",
    ),
    Especificacao(
        "G8",
        "Peçonha",
        "Rogue",
        7,
        ("ataque_furtivo", "faro_de_rua", "envenenar"),
        ("fio_serrilhado", "boca_de_sangue", "passo_de_corca", "coracao_ferro"),
        "atrito: veneno, sangramento e roubo de vida",
    ),
)
DISTRIBUICAO = {"Warrior": 3, "Mage": 3, "Rogue": 2}


# --- formação ------------------------------------------------------------------


def niveis_de_oferta(nivel: int) -> list[int]:
    """Os níveis em que o jogo abre uma escolha de skill, até `nivel`."""
    return [n for n in range(2, nivel + 1) if oferece_skill(n)]


def construir(espec: Especificacao):
    """O boneco: herói da simulação, equipamento esperado, deck e passivas.

    O equipamento é o do `expected loadout` daquele nível, copiado peça por peça
    do catálogo para a mesma posição. Poções não entram: na Arena não se bebe, e
    a preparação as retiraria de qualquer forma.
    """
    heroi = make_hero(espec.classe, espec.nivel, "naked")
    heroi.nick_name = espec.nome
    referencia = make_hero(espec.classe, espec.nivel, "expected")
    catalogo = get_all_items()
    for posicao, peca in referencia.equipment.items():
        if peca is not None:
            copia = catalogo[peca.name].instance()
            heroi.add_item_to_inventory(copia)
            heroi.equip(copia, posicao)
    for indice in range(expected_passive_count(espec.nivel)):
        heroi.add_passive(get_passive_by_id(espec.passivas[indice % len(espec.passivas)]))
    heroi.skills = {i: get_skill_by_id(sid) for i, sid in enumerate(espec.deck, start=1)}
    heroi.rest()
    # Marca de extração EM MEMÓRIA, só para a interface da Arena aceitar o boneco.
    mark_extracted(heroi, espec.nivel)
    validar_build(espec, heroi, referencia)
    return heroi


def validar_build(espec: Especificacao, heroi, referencia) -> None:
    """Recusa a build que o jogo não conseguiria produzir."""
    problemas = []
    iniciais = {s.id for s in get_initial_skills(espec.classe)}
    oferta = {s.id: s for s in get_offer_pool(espec.classe)}
    niveis = niveis_de_oferta(espec.nivel)
    if len(espec.deck) != 1 + len(niveis):
        problemas.append(f"deck com {len(espec.deck)} cartas; o nível dá {1 + len(niveis)}")
    if espec.deck[0] not in iniciais:
        problemas.append(f"{espec.deck[0]} não é a carta inicial de {espec.classe}")
    for nivel_da_oferta, sid in zip(niveis, espec.deck[1:]):
        carta = oferta.get(sid)
        if carta is None:
            problemas.append(f"{sid} não está na oferta de {espec.classe}")
        elif carta.level_required > nivel_da_oferta:
            problemas.append(
                f"{sid} exige nível {carta.level_required} (oferta no {nivel_da_oferta})"
            )
    if len(set(espec.deck)) != len(espec.deck):
        problemas.append("carta repetida no deck")
    for skill in heroi.skills.values():
        if not heroi.can_use_skill(skill):
            problemas.append(f"{skill.id}: requisito de equipamento não atendido")
    if len(heroi.passives) != expected_passive_count(espec.nivel):
        problemas.append(f"{len(heroi.passives)} passivas; o nível dá {espec.nivel - 1}")
    for passiva in heroi.passives:
        if passiva.rarity != "Common":
            problemas.append(f"{passiva.id} não é Comum")
    esperado = {p: (i.name if i else None) for p, i in referencia.equipment.items()}
    montado = {p: (i.name if i else None) for p, i in heroi.equipment.items()}
    if esperado != montado:
        problemas.append("equipamento diferente do expected loadout")
    if any(getattr(item, "is_potion", False) for item in heroi.inventory):
        problemas.append("consumível no inventário")
    if not was_extracted(heroi):
        problemas.append("sem a marca de extração")
    if problemas:
        raise BuildIlegitimaError(f"{espec.nome}: " + "; ".join(problemas))


@dataclass
class Participante:
    espec: Especificacao
    heroi: object
    poder: float | None
    duelos_da_medicao: int = 0

    @property
    def id(self) -> str:
        return self.espec.id

    @property
    def nome(self) -> str:
        return self.espec.nome


def formar_participantes(*, medir: bool = True) -> list[Participante]:
    contagem = Counter(e.classe for e in ESPECIFICACOES)
    if dict(contagem) != DISTRIBUICAO:
        raise BuildIlegitimaError(f"distribuição de classes {dict(contagem)} != {DISTRIBUICAO}")
    participantes = []
    for espec in ESPECIFICACOES:
        heroi = construir(espec)
        if medir:
            leitura = overall_power(heroi, usar_cache=False)
            participantes.append(
                Participante(espec, heroi, leitura.nivel_equivalente, leitura.duelos)
            )
        else:
            participantes.append(Participante(espec, heroi, None))
    return participantes


# --- a chave -----------------------------------------------------------------


def sortear_chave(ids, semente: int = SEMENTE_PRINCIPAL) -> list[str]:
    """A ordem dos oito na chave: pares (0,1), (2,3), (4,5), (6,7) nas quartas."""
    ordem = list(ids)
    random.Random(semente).shuffle(ordem)
    return ordem


def semente_da_partida(fase: str, indice: int, semente: int = SEMENTE_PRINCIPAL) -> int:
    """Derivada só da semente principal e da posição na chave. Estável entre execuções."""
    digest = hashlib.sha256(f"{semente}:{fase}:{indice}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


# --- a política --------------------------------------------------------------


class PoliticaCopa:
    """A política dos dois lados: simples, determinística e igual para todos.

    Lê só a `DuelView` e o próprio deck (tipo e efeito de cada carta). Nunca o
    herói ao vivo, o adversário, nem o duelo. Prioridade:

    1. cura, se o HP visível está em até metade do máximo;
    2. buff ou redução de dano que ainda não está ativo (pelo nome);
    3. status que o adversário ainda não carrega;
    4. a primeira skill de dano legal, na ordem do deck;
    5. ataque básico. Nunca se rende.
    """

    def __init__(self, heroi) -> None:
        self._deck = tuple(heroi.skills[k] for k in sorted(heroi.skills))
        self.last_reason = ""

    def choose(self, view):
        legais = {a.skill_id for a in view.legal_actions if a.kind == "skill"}
        cartas = [s for s in self._deck if s.id in legais]
        fracao = view.me.hp / view.me.hp_max if view.me.hp_max else 1.0
        if fracao <= LIMIAR_DE_CURA:
            for carta in cartas:
                if carta.effect_type == "heal":
                    self.last_reason = (
                        f"HP {view.me.hp}/{view.me.hp_max} ({fracao:.1%}) ≤ {LIMIAR_DE_CURA:.0%} "
                        f"e há cura legal: {carta.name}"
                    )
                    return DuelAction.use_skill(carta.id)
        for carta in cartas:
            if (
                carta.effect_type in ("buff", "damage_reduction")
                and str(carta.name) not in view.me.buffs
            ):
                self.last_reason = (
                    f"{carta.name} é legal e não está ativo (buffs visíveis: {list(view.me.buffs)})"
                )
                return DuelAction.use_skill(carta.id)
        for carta in cartas:
            if (
                carta.effect_type == "status"
                and str(carta.effect_value) not in view.opponent.effects
            ):
                self.last_reason = (
                    f"{carta.name} aplica {carta.effect_value}, que o adversário não carrega "
                    f"(efeitos visíveis: {list(view.opponent.effects)})"
                )
                return DuelAction.use_skill(carta.id)
        for carta in cartas:
            if carta.effect_type == "damage":
                self.last_reason = f"primeira skill de dano legal do deck: {carta.name}"
                return DuelAction.use_skill(carta.id)
        ilegais = [s.name for s in self._deck if s.id not in legais]
        self.last_reason = f"nenhuma skill útil e legal (fora: {ilegais}); ataque básico"
        return DuelAction.attack()


# --- as partidas -------------------------------------------------------------


@dataclass
class Partida:
    fase: str
    indice: int
    semente: int
    lados: dict
    puro: DueloAuditado
    auditado: DueloAuditado
    fidelidade: list
    coerencia: list
    # Nome da fase para exibição; sem ele, o da Copa 01 (`NOME_DA_FASE`).
    nome_da_fase: str | None = None

    @property
    def inconclusiva(self) -> bool:
        return self.auditado.inconclusivo or self.puro.inconclusivo

    @property
    def vencedor(self) -> Participante | None:
        resultado = self.auditado.duelo.result
        return None if resultado is None else self.lados[resultado.winner]

    @property
    def perdedor(self) -> Participante | None:
        resultado = self.auditado.duelo.result
        return None if resultado is None else self.lados[resultado.loser]

    @property
    def titulo(self) -> str:
        fase = self.nome_da_fase or NOME_DA_FASE[self.fase]
        rotulo = fase if self.fase == "final" else f"{fase} {self.indice}"
        return f"{rotulo} — {self.lados['p1'].nome} × {self.lados['p2'].nome}"


def jogar_partida(
    fase: str,
    indice: int,
    p1: Participante,
    p2: Participante,
    *,
    semente_principal: int = SEMENTE_PRINCIPAL,
    nome_da_fase: str | None = None,
) -> Partida:
    semente = semente_da_partida(fase, indice, semente_principal)

    def duelo(auditar: bool) -> DueloAuditado:
        # Preparação nova a cada duelo: nada atravessa de uma partida para outra.
        return disputar(
            prepare_gladiator(p1.heroi),
            prepare_gladiator(p2.heroi),
            semente,
            PoliticaCopa,
            auditar=auditar,
            limite=LIMITE_TECNICO,
        )

    puro = duelo(False)
    auditado = duelo(True)
    return Partida(
        fase,
        indice,
        semente,
        {"p1": p1, "p2": p2},
        puro,
        auditado,
        verificar_fidelidade(puro, auditado),
        conferir_trace(auditado),
        nome_da_fase,
    )


def verificar_fidelidade(puro: DueloAuditado, auditado: DueloAuditado) -> list[tuple[str, bool]]:
    """O mesmo duelo com e sem auditoria. Qualquer diferença é defeito da auditoria."""
    a, b = puro.duelo, auditado.duelo
    return [
        ("ações escolhidas", [r.actions for r in a.history] == [r.actions for r in b.history]),
        ("ordem de cada rodada", [r.order for r in a.history] == [r.order for r in b.history]),
        (
            "leituras de iniciativa (floats exatos)",
            [r.initiative for r in a.history] == [r.initiative for r in b.history],
        ),
        (
            "passos: desfecho, MP reservado, MP gasto e dano",
            [r.steps for r in a.history] == [r.steps for r in b.history],
        ),
        (
            "HP e MP ao fim de cada rodada",
            [(r.hp_end, r.mp_end) for r in a.history] == [(r.hp_end, r.mp_end) for r in b.history],
        ),
        (
            "estado completo ao fim de cada rodada (efeitos, buffs, recargas)",
            puro.fotos == auditado.fotos,
        ),
        ("eventos do motor", a.events == b.events),
        ("vencedor, motivo e número de rodadas", a.result == b.result),
        ("conclusividade", puro.inconclusivo == auditado.inconclusivo),
        (
            "posição final do gerador (nenhum sorteio extra)",
            puro.rng.getstate() == auditado.rng.getstate(),
        ),
    ]


def conferir_trace(auditado: DueloAuditado) -> list[tuple[str, bool]]:
    """O trace contra o que o próprio motor registrou."""
    trace = auditado.trace
    rolagens = trace.de("rolagem")
    golpes = trace.de("golpe_fim")
    skills_fim = trace.de("skill_fim")
    dano_ok = mp_ok = True
    for registro in auditado.duelo.history:
        for passo in registro.steps:
            if passo.outcome != "executed":
                continue
            dano = sum(
                g["hp_aplicado"]
                for g in golpes
                if g["rodada"] == registro.number and g["atacante"] == passo.side
            )
            dano_ok &= dano == passo.damage_to_opponent
            debitos = [
                s["mp_debitado"]
                for s in skills_fim
                if s["rodada"] == registro.number and s["ator"] == passo.side
            ]
            mp_ok &= (
                (debitos == [passo.mp_spent])
                if passo.action.kind == "skill"
                else passo.mp_spent == 0
            )
    executados = sum(1 for r in auditado.duelo.history for p in r.steps if p.outcome == "executed")
    return [
        (
            "toda chamada ao gerador foi classificada",
            all("DESCONHECIDA" not in r["mecanica"] for r in rolagens),
        ),
        ("rolagens registradas = chamadas ao gerador", len(rolagens) == auditado.rng.chamadas),
        (
            "toda rolagem de acerto recebeu a chance do motor",
            all("chance" in r for r in rolagens if r["mecanica"] == "acerto"),
        ),
        ("toda rolagem pertence ao intervalo do motor", all(_dentro(r) for r in rolagens)),
        ("dano de cada passo = soma do HP retirado pelos golpes registrados", dano_ok),
        ("MP gasto de cada passo = débito registrado da skill", mp_ok),
        (
            "ações executadas = eventos `action_executed`",
            executados == sum(1 for e in auditado.duelo.events if e.name == "action_executed"),
        ),
    ]


def _dentro(rolagem: dict) -> bool:
    if rolagem["operacao"] == "randrange":
        return rolagem["argumentos"] == [PERCENTAGE_RANGE_MIN, PERCENTAGE_RANGE_MAX] and (
            PERCENTAGE_RANGE_MIN <= rolagem["valor"] < PERCENTAGE_RANGE_MAX
        )
    return 0.0 <= rolagem["valor"] < 1.0


@dataclass
class Copa:
    participantes: list
    chave: list
    fases: dict
    interrompida: str | None = None

    @property
    def campeao(self) -> Participante | None:
        final = self.fases.get("final")
        return final[0].vencedor if final else None


def disputar_copa(participantes: list[Participante]) -> Copa:
    por_id = {p.id: p for p in participantes}
    chave = sortear_chave([p.id for p in participantes])
    vivos = [por_id[i] for i in chave]
    copa = Copa(participantes, chave, {})
    for fase, quantas in FASES:
        partidas = [
            jogar_partida(fase, i + 1, vivos[2 * i], vivos[2 * i + 1]) for i in range(quantas)
        ]
        copa.fases[fase] = partidas
        if any(p.inconclusiva for p in partidas):
            copa.interrompida = (
                f"{NOME_DA_FASE[fase]}: confronto inconclusivo no limite técnico de "
                f"{LIMITE_TECNICO} rodadas; sem vencedor, a chave não avança."
            )
            return copa
        vivos = [p.vencedor for p in partidas]
    return copa


# --- estatística -------------------------------------------------------------


def _vazio() -> dict:
    return {
        "dano_golpes": 0,
        "dano_dot": 0,
        "hp_retirado": 0,
        "cura_skill": 0,
        "roubo_de_vida": 0,
        "mp_gasto": 0,
        "skills": 0,
        "basicos": 0,
        "acertos": 0,
        "erros": 0,
        "criticos": 0,
        "dano_critico": 0,
        "status_aplicados": [],
        "status_falharam_na_rolagem": [],
        "status_anulados": [],
        "status_recusados_pelo_nucleo": [],
        "perdidas_controle": 0,
        "egide_absorvido": 0,
        "egide_mp": 0,
        "buffs": [],
        "leis": [],
        "skills_usadas": Counter(),
        "primeiro": 0,
    }


def estatisticas(partida: Partida) -> dict[str, dict]:
    """Totais por lado, contados do histórico do motor e do trace da partida."""
    st = {lado: _vazio() for lado in SIDES}
    trace = partida.auditado.trace
    for registro in partida.auditado.duelo.history:
        st[registro.order.first]["primeiro"] += 1
        for passo in registro.steps:
            alvo = st[passo.side]
            if passo.outcome == "executed":
                alvo["mp_gasto"] += passo.mp_spent
                if passo.action.kind == "skill":
                    alvo["skills"] += 1
                    alvo["skills_usadas"][passo.action.skill_id] += 1
                else:
                    alvo["basicos"] += 1
            elif passo.outcome == "cancelled_control":
                alvo["perdidas_controle"] += 1
    for g in trace.de("golpe_fim"):
        lado = st[g["atacante"]]
        if g["resultado"]["was_evaded"]:
            lado["erros"] += 1
            continue
        lado["acertos"] += 1
        lado["dano_golpes"] += g["resultado"]["damage"]
        lado["hp_retirado"] += g["hp_aplicado"]
        if g["resultado"]["was_critical"]:
            lado["criticos"] += 1
            lado["dano_critico"] += g["resultado"]["damage"]
        if g["roubo_de_vida"]:
            lado["roubo_de_vida"] += g["roubo_de_vida"]["aplicada"]
    for t in trace.de("tick_de_efeitos"):
        dot = sum(t["relatorio"]["dot"].values())
        st[opponent_of(t["ator"])]["dano_dot"] += dot
        st[opponent_of(t["ator"])]["hp_retirado"] += dot
    for s in trace.de("skill_fim"):
        if s["resultado"]["kind"] == "heal":
            st[s["ator"]]["cura_skill"] += s["depois"]["caster"]["hp"] - _hp_antes_da_skill(
                trace, s
            )
        if s["resultado"]["kind"] == "buff":
            st[s["ator"]]["buffs"].append(s["resultado"]["buff_name"])
    for e in trace.de("egide"):
        if not e.get("inaplicavel"):
            st[e["defensor"]]["egide_absorvido"] += e["dano_entrada"] - e["dano_saida"]
            st[e["defensor"]]["egide_mp"] += e["custo_mp"]
    for s in trace.de("status"):
        quem = st[s["atacante"]] if s["atacante"] in st else None
        if quem is None:
            continue
        rotulo = f"{s['status']} (rodada {s['rodada']})"
        if s["pegou"]:
            quem["status_aplicados"].append(rotulo)
        elif not s["rolou"]:
            quem["status_anulados"].append(rotulo)
        elif s["rolagem_aprovada"]:
            quem["status_recusados_pelo_nucleo"].append(rotulo)
        else:
            quem["status_falharam_na_rolagem"].append(rotulo)
    for i in trace.de("interacoes"):
        lado = i["ator_da_lei"] if i["ator_da_lei"] in st else None
        if lado:
            st[lado]["leis"].extend(f"{lei['nome']} (rodada {i['rodada']})" for lei in i["leis"])
    return st


def _hp_antes_da_skill(trace, skill_fim: dict) -> int:
    inicio = next(
        r
        for r in reversed(trace.records[: skill_fim["seq"] - 1])
        if r["kind"] == "skill_inicio" and r["ator"] == skill_fim["ator"]
    )
    return inicio["antes"]["caster"]["hp"]


def dano_total(e: dict) -> int:
    return e["dano_golpes"] + e["dano_dot"]


def cura_total(e: dict) -> int:
    return e["cura_skill"] + e["roubo_de_vida"]


# --- relatórios: utilidades ----------------------------------------------------


def _nome_da_carta(sid: str) -> str:
    carta = get_skill_by_id(sid)
    return carta.name if carta else sid


def nome_da_acao(acao) -> str:
    kind = acao["kind"] if isinstance(acao, dict) else acao.kind
    skill_id = acao["skill_id"] if isinstance(acao, dict) else acao.skill_id
    if kind == "skill":
        return _nome_da_carta(skill_id)
    return {"attack": "Ataque básico", "surrender": "Rendição"}[kind]


def _r(valor) -> str:
    """Um número com toda a precisão que o motor usou."""
    if isinstance(valor, float):
        return repr(valor)
    return str(valor)


def _op(participante: Participante) -> str:
    return "não medido" if participante.poder is None else f"{participante.poder:.2f}"


def _pct(valor: float) -> str:
    return f"{valor:.1%}"


def _equipamento(heroi) -> str:
    pecas = [f"{p}: {i.display_name}" for p, i in heroi.equipment.items() if i is not None]
    return "; ".join(pecas) or "—"


def _passivas(heroi) -> str:
    contagem = Counter(p.name for p in heroi.passives)
    return ", ".join(f"{nome} ×{n}" if n > 1 else nome for nome, n in contagem.items())


def _deck(heroi) -> str:
    return ", ".join(heroi.skills[k].name for k in sorted(heroi.skills))


def tabela_de_participantes(participantes: list[Participante]) -> list[str]:
    linhas = [
        "| ID | Nome | Classe | Nível | Overall Power | HP máx | MP máx | ST | MG | AG | DF "
        "| Equipamento | Skills | Passivas | Característica |",
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for p in participantes:
        h = prepare_gladiator(p.heroi).hero
        poder = _op(p)
        linhas.append(
            f"| {p.id} | {p.nome} | {CLASSE[p.espec.classe]} | {p.espec.nivel} | {poder} "
            f"| {h.base_hp} | {h.base_mp} | {h.get_st()} | {h.get_mg()} | {h.get_ag()} "
            f"| {h.get_df()} | {_equipamento(h)} | {_deck(h)} | {_passivas(h)} | {p.espec.foco} |"
        )
    poderes = [p.poder for p in participantes if p.poder is not None]
    if poderes:
        linhas += [
            "",
            f"Overall Power — média **{statistics.mean(poderes):.2f}**, mínimo "
            f"**{min(poderes):.2f}**, máximo **{max(poderes):.2f}**; faixa pedida "
            f"[{FAIXA_DE_PODER[0]:.0f}, {FAIXA_DE_PODER[1]:.0f}]: "
            + (
                "todos dentro."
                if all(FAIXA_DE_PODER[0] <= x <= FAIXA_DE_PODER[1] for x in poderes)
                else "há participante fora — ver tabela."
            ),
        ]
    return linhas


def _chave_texto(copa: Copa, ate: str | None) -> list[str]:
    """A chave como estava depois da fase `ate` (`None`: antes da primeira partida)."""
    por_id = {p.id: p for p in copa.participantes}
    fases = [f for f, _ in FASES]
    concluidas = set() if ate is None else set(fases[: fases.index(ate) + 1])

    def desfecho(fase: str, partida: Partida) -> str:
        if fase not in concluidas:
            return ""
        return f"  →  {partida.vencedor.nome}" if partida.vencedor else "  →  inconclusiva"

    linhas = ["```"]
    for i in range(4):
        a, b = copa.chave[2 * i], copa.chave[2 * i + 1]
        partida = copa.fases["quartas"][i] if "quartas" in copa.fases else None
        fim = desfecho("quartas", partida) if partida else ""
        linhas.append(f"Q{i + 1}: {por_id[a].nome} ({a}) × {por_id[b].nome} ({b}){fim}")
    for fase, prefixo, anterior, quantas in (("semifinal", "S", "Q", 2), ("final", "F", "S", 1)):
        for i in range(quantas):
            rotulo = f"{prefixo}{i + 1 if quantas > 1 else ''}"
            if fases[fases.index(fase) - 1] in concluidas and fase in copa.fases:
                partida = copa.fases[fase][i]
                linhas.append(
                    f"{rotulo}: {partida.lados['p1'].nome} × {partida.lados['p2'].nome}"
                    + desfecho(fase, partida)
                )
            else:
                linhas.append(
                    f"{rotulo}: vencedor {anterior}{2 * i + 1} × vencedor {anterior}{2 * i + 2}"
                )
    if "final" in concluidas and copa.campeao:
        linhas.append(f"Campeão: {copa.campeao.nome}")
    linhas.append("```")
    return linhas


# --- relatório: resumo da Copa ---------------------------------------------


def _bloco_da_partida(partida: Partida) -> list[str]:
    st = estatisticas(partida)
    duelo = partida.auditado.duelo
    resultado = duelo.result
    linhas = [f"### {partida.titulo}", ""]
    linhas += [
        "| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for lado in SIDES:
        p = partida.lados[lado]
        linhas.append(
            f"| {lado} | {p.id} | {p.nome} | {CLASSE[p.espec.classe]} | {p.espec.nivel} "
            f"| {_op(p)} | {_deck(p.heroi)} | {p.espec.foco} |"
        )
    linhas.append("")
    linhas.append(f"- Seed da partida: `{partida.semente}`")
    linhas.append(f"- Rodadas: **{len(duelo.history)}**")
    if resultado is None:
        linhas.append(
            f"- **Inconclusiva**: o limite técnico de {LIMITE_TECNICO} rodadas foi atingido."
        )
    else:
        vencedor = duelo.hero(resultado.winner)
        linhas.append(
            f"- Vencedor: **{resultado.winner_name}** ({resultado.winner}), motivo "
            f"`{resultado.reason}` "
            f"(o adversário chegou a 0 de HP) — HP restante {vencedor.get_hp()}/{vencedor.base_hp} "
            f"({_pct(vencedor.get_hp() / vencedor.base_hp)})"
        )
    linhas.append(
        "- Fidelidade (com × sem auditoria): "
        + (
            "**idêntico** em todas as verificações"
            if all(ok for _, ok in partida.fidelidade)
            else "**DIVERGENTE**"
        )
        + "; coerência do trace com o motor: "
        + ("**ok**" if all(ok for _, ok in partida.coerencia) else "**FALHOU**")
    )
    linhas += ["", _tabela_de_totais(partida, st), ""]
    efeitos = []
    for lado in SIDES:
        e = st[lado]
        nome = partida.lados[lado].nome
        if e["status_aplicados"]:
            efeitos.append(f"{nome} aplicou: {', '.join(e['status_aplicados'])}")
        falhos = (
            e["status_falharam_na_rolagem"]
            + e["status_anulados"]
            + e["status_recusados_pelo_nucleo"]
        )
        if falhos:
            efeitos.append(f"{nome} tentou sem sucesso: {', '.join(falhos)}")
        if e["buffs"]:
            efeitos.append(
                f"{nome} ativou: {', '.join(f'{b} ×{n}' for b, n in Counter(e['buffs']).items())}"
            )
        if e["leis"]:
            efeitos.append(f"Leis disparadas por {nome}: {', '.join(e['leis'])}")
        if e["egide_absorvido"]:
            efeitos.append(
                f"Égide de {nome}: absorveu {e['egide_absorvido']} de dano por {e['egide_mp']} MP"
            )
    linhas.append("Efeitos relevantes:")
    linhas += [f"- {x}" for x in efeitos] or ["- nenhum status, buff, lei ou Égide"]
    linhas += ["", "Rodada a rodada:", ""]
    linhas += [
        f"| Rodada | Ordem (critério) | {partida.lados['p1'].nome} (p1) | "
        f"{partida.lados['p2'].nome} (p2) "
        "| HP fim p1 / p2 | MP fim p1 / p2 |",
        "|---|---|---|---|---|---|",
    ]
    for registro in duelo.history:
        passos = {p.side: p for p in registro.steps}
        hp = dict(registro.hp_end)
        mp = dict(registro.mp_end)
        linhas.append(
            f"| {registro.number} | {registro.order.first} → {registro.order.second} "
            f"({registro.order.decided_by}) | {_passo(passos['p1'])} | {_passo(passos['p2'])} "
            f"| {hp['p1']} / {hp['p2']} | {mp['p1']} / {mp['p2']} |"
        )
    return linhas + [""]


def _passo(passo) -> str:
    texto = f"{nome_da_acao(passo.action)} — {DESFECHO[passo.outcome]}"
    if passo.outcome == "executed":
        texto += f", dano {passo.damage_to_opponent}"
        if passo.mp_spent:
            texto += f", MP −{passo.mp_spent}"
    return texto


def _tabela_de_totais(partida: Partida, st: dict) -> str:
    linhas = [
        f"| Total | {partida.lados['p1'].nome} | {partida.lados['p2'].nome} |",
        "|---|---|---|",
    ]
    campos = (
        (
            "Dano causado (golpes + DoT)",
            lambda e: f"{dano_total(e)} ({e['dano_golpes']} + {e['dano_dot']})",
        ),
        (
            "Cura (skill + roubo de vida)",
            lambda e: f"{cura_total(e)} ({e['cura_skill']} + {e['roubo_de_vida']})",
        ),
        ("MP gasto em ações", lambda e: str(e["mp_gasto"])),
        ("Skills / ataques básicos", lambda e: f"{e['skills']} / {e['basicos']}"),
        ("Acertos / erros", lambda e: f"{e['acertos']} / {e['erros']}"),
        ("Críticos (dano)", lambda e: f"{e['criticos']} ({e['dano_critico']})"),
        ("Agiu primeiro (rodadas)", lambda e: str(e["primeiro"])),
        ("Ações perdidas por controle", lambda e: str(e["perdidas_controle"])),
    )
    for rotulo, f in campos:
        linhas.append(f"| {rotulo} | {f(st['p1'])} | {f(st['p2'])} |")
    return "\n".join(linhas)


def _estatisticas_do_campeao(copa: Copa) -> list[str]:
    campeao = copa.campeao
    if campeao is None:
        return ["Sem campeão: a Copa foi interrompida."]
    soma = _vazio()
    recebido = 0
    linhas_partidas = []
    for fase, _ in FASES:
        for partida in copa.fases.get(fase, ()):
            lado = next((s for s in SIDES if partida.lados[s] is campeao), None)
            if lado is None:
                continue
            st = estatisticas(partida)
            e = st[lado]
            recebido += dano_total(st[opponent_of(lado)])
            for k in soma:
                if isinstance(soma[k], (int, float)):
                    soma[k] += e[k]
                elif isinstance(soma[k], list):
                    soma[k] += e[k]
                else:
                    soma[k].update(e[k])
            heroi = partida.auditado.duelo.hero(lado)
            linhas_partidas.append(
                f"| {NOME_DA_FASE[fase]} | {partida.lados[opponent_of(lado)].nome} "
                f"| {len(partida.auditado.duelo.history)} | {dano_total(e)} "
                f"| {dano_total(st[opponent_of(lado)])} | {cura_total(e)} | {e['mp_gasto']} "
                f"| {heroi.get_hp()}/{heroi.base_hp} |"
            )
    tentados = soma["acertos"] + soma["erros"]
    return [
        f"**{campeao.nome}** ({campeao.id}, {CLASSE[campeao.espec.classe]} nível "
        f"{campeao.espec.nivel}, "
        f"OP {_op(campeao)}).",
        "",
        "| Fase | Adversário | Rodadas | Dano causado | Dano recebido | Cura | MP gasto | HP final "
        "|",
        "|---|---|---|---|---|---|---|---|",
        *linhas_partidas,
        "",
        f"- Dano causado: {dano_total(soma)} (golpes {soma['dano_golpes']}, DoT "
        f"{soma['dano_dot']}); "
        f"recebido: {recebido}.",
        f"- Cura: {cura_total(soma)} (skill {soma['cura_skill']}, roubo de vida "
        f"{soma['roubo_de_vida']}).",
        f"- MP gasto: {soma['mp_gasto']}; skills {soma['skills']}, ataques básicos "
        f"{soma['basicos']}.",
        f"- Golpes: {soma['acertos']} acertos e {soma['erros']} erros "
        f"({_pct(soma['acertos'] / tentados) if tentados else '—'} de acerto); "
        f"{soma['criticos']} críticos.",
        "- Skills usadas: "
        + ", ".join(f"{_nome_da_carta(k)} ×{n}" for k, n in soma["skills_usadas"].most_common()),
        f"- Status aplicados: {len(soma['status_aplicados'])}; "
        f"ações perdidas por controle: {soma['perdidas_controle']}.",
    ]


def relatorio_resumo(copa: Copa) -> str:
    linhas = [
        "# Copa Arena de Testes 01",
        "",
        "Minicampeonato técnico da Arena PvP, gerado por `tools/arena_copa_teste.py`. "
        "Experimento de auditoria da matemática do duelo — não é medição de balanceamento "
        "nem população ranked.",
        "",
        "- Oito bonecos descartáveis, montados em memória a partir do catálogo real e "
        "marcados como extraídos só para a interface da Arena. Nenhum save, slot ou "
        "coleção de gladiadores foi tocado.",
        f"- Seed principal: `{SEMENTE_PRINCIPAL}`. Chave: `random.Random(seed).shuffle` dos IDs. "
        "Seed de cada partida: os 8 primeiros bytes (big-endian) de "
        '`sha256(f"{seed}:{fase}:{índice}")`.',
        "- Cada partida começa de uma preparação nova (`prepare_gladiator`): HP e MP cheios, "
        "sem recarga, sem efeito, sem consumível; nada atravessa de uma partida para outra.",
        "- Política dos dois lados (`PoliticaCopa`): cura se HP ≤ 50%; senão buff ou redução "
        "ainda não ativos; senão status que o adversário não carrega; senão a primeira skill "
        "de dano legal; senão ataque básico. Lê só a `DuelView` e o próprio deck.",
        f"- Limite técnico do laço: {LIMITE_TECNICO} rodadas (inconclusivo, nunca empate). "
        + ("Nenhuma partida chegou perto." if copa.interrompida is None else copa.interrompida),
        "- Cada partida rodou duas vezes, sem instrumentação e auditada, com a mesma seed; "
        "as duas coincidem em todas as verificações listadas no fim.",
        "",
        "## Participantes",
        "",
        "Atributos efetivos lidos do gladiador preparado. Overall Power: "
        "`src/sim/arena.py::overall_power(personagem).nivel_equivalente`, medido sem cache.",
        "",
        *tabela_de_participantes(copa.participantes),
        "",
        "## Chave sorteada",
        "",
        *_chave_texto(copa, None),
        "",
    ]
    for fase, _ in FASES:
        if fase not in copa.fases:
            continue
        if fase == "final":
            linhas += ["## Final", ""]
            partida = copa.fases["final"][0]
            linhas += _bloco_da_partida(partida)
            linhas += [
                f"A transcrição completa, com todos os cálculos e sorteios, está em "
                f"[`{ARQUIVO_FINAL}`]({ARQUIVO_FINAL}); o trace estruturado, em "
                f"[`{ARQUIVO_TRACE}`]({ARQUIVO_TRACE}).",
                "",
            ]
        else:
            linhas += [f"## {NOME_DA_FASE[fase]}", ""]
            for partida in copa.fases[fase]:
                linhas += _bloco_da_partida(partida)
        linhas += [f"Chave após {NOME_DA_FASE[fase].lower()}:", "", *_chave_texto(copa, fase), ""]
    linhas += ["## Estatísticas do campeão", "", *_estatisticas_do_campeao(copa), ""]
    linhas += ["## Estatísticas do torneio", "", *_estatisticas_do_torneio(copa), ""]
    linhas += ["## Verificações", "", *_verificacoes(copa), ""]
    return "\n".join(linhas)


def _todas(copa: Copa) -> list[Partida]:
    return [p for fase, _ in FASES for p in copa.fases.get(fase, ())]


def _estatisticas_do_torneio(copa: Copa) -> list[str]:
    partidas = _todas(copa)
    rodadas = [len(p.auditado.duelo.history) for p in partidas]
    criterios = Counter(r.order.decided_by for p in partidas for r in p.auditado.duelo.history)
    vitorias = Counter(CLASSE[p.vencedor.espec.classe] for p in partidas if p.vencedor)
    primeiro_venceu = sum(
        1
        for p in partidas
        if p.vencedor
        and Counter(r.order.first for r in p.auditado.duelo.history).most_common(1)[0][0]
        == p.auditado.duelo.result.winner
    )
    rolagens = Counter(
        r["mecanica"].split(" (")[0] for p in partidas for r in p.auditado.trace.de("rolagem")
    )
    golpes = [g for p in partidas for g in p.auditado.trace.de("golpe_fim")]
    conectados = [g for g in golpes if not g["resultado"]["was_evaded"]]
    return [
        f"- Partidas: {len(partidas)}; rodadas por partida: {rodadas} "
        f"(média {statistics.mean(rodadas):.1f}, total {sum(rodadas)}).",
        f"- Vitórias por classe: {dict(vitorias)}.",
        f"- Critério que decidiu a ordem, por rodada: {dict(criterios)}.",
        f"- Em {primeiro_venceu} de {len(partidas)} partidas venceu quem agiu primeiro na maior "
        "parte das rodadas.",
        f"- Golpes: {len(golpes)}, conectados {len(conectados)} "
        f"({_pct(len(conectados) / len(golpes)) if golpes else '—'}), críticos "
        f"{sum(1 for g in conectados if g['resultado']['was_critical'])}.",
        f"- Chamadas ao gerador, por mecânica: {dict(rolagens)}.",
    ]


def _verificacoes(copa: Copa) -> list[str]:
    linhas = [
        "| Partida | Seed | Rodadas | Fidelidade com × sem auditoria | Coerência trace × motor | "
        "Sorteios |",
        "|---|---|---|---|---|---|",
    ]
    for p in _todas(copa):
        fid = sum(ok for _, ok in p.fidelidade)
        coe = sum(ok for _, ok in p.coerencia)
        linhas.append(
            f"| {p.titulo} | `{p.semente}` | {len(p.auditado.duelo.history)} "
            f"| {fid}/{len(p.fidelidade)} | {coe}/{len(p.coerencia)} | {p.auditado.rng.chamadas} |"
        )
    linhas += ["", "Verificações de fidelidade (iguais em todas as partidas):", ""]
    linhas += [f"- {nome}" for nome, _ in _todas(copa)[0].fidelidade]
    linhas += ["", "Verificações de coerência do trace:", ""]
    linhas += [f"- {nome}" for nome, _ in _todas(copa)[0].coerencia]
    return linhas


# --- relatório: a final, transcrita --------------------------------------------


def _ficha_md(ficha: dict, lado: str) -> list[str]:
    e = ficha["estado"]
    linhas = [
        f"### {lado} — {ficha['nome']} ({CLASSE.get(ficha['classe'], ficha['classe'])}, nível "
        f"{ficha['nivel']})",
        "",
        f"- HP {e['hp']}/{e['hp_max']}, MP {e['mp']}/{e['mp_max']}; ST {e['st']}, MG {e['mg']}, "
        f"AG {e['ag']}, DF {e['df']}",
        f"- Arma: +{_r(ficha['arma_percent'])}% de dano; Égide de Mana: {ficha['egide_percent']}%",
        "- Equipamento: "
        + "; ".join(f"{p}: {n}" for p, n in ficha["equipamento"].items() if n is not None),
        "- Passivas: "
        + ", ".join(f"{p['nome']} ({p['efeito']} {p['valor']})" for p in ficha["passivas"]),
        "- Modificadores de combate (funil `fx.combat_modifier`): "
        + ", ".join(f"{k} {_r(v)}" for k, v in ficha["modificadores"].items() if v),
        "",
        "| Skill | Tipo | Valor | Custo MP | Recarga | Power × escala | Acerto | Crítico da carta "
        "| Secundário | Bônus | Requisito |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for s in ficha["skills"]:
        escala = " + ".join(f"{p}×{st}" for st, p in s["escala"]) or "—"
        sec = s["secundario"]
        sec_txt = f"{sec['effect']} {sec['chance']}% por {sec['duration']}" if sec else "—"
        carta = get_skill_by_id(s["id"])
        bonus = (
            f"{carta.bonus_condition} +{carta.bonus_percent}%"
            if getattr(carta, "bonus_condition", "")
            else "—"
        )
        valor = f"{s['valor']} {s['stat']}".strip()
        if s["tipo"] == "status":
            valor = f"{s['valor']} {s['chance']}% por {s['duracao']}"
        elif s["tipo"] in ("buff", "damage_reduction"):
            valor = f"{valor} por {s['duracao']}"
        linhas.append(
            f"| {s['nome']} (`{s['id']}`) | {s['tipo']} | {valor} | {s['custo_mp']} | "
            f"{s['recarga']} "
            f"| {_r(s['power'])} × ({escala}) | {s['modificador_de_acerto']:+d} | "
            f"{s['critico_da_carta']} "
            f"| {sec_txt} | {bonus} | {s['requisito'] or '—'} |"
        )
    return linhas + [""]


def _estado_md(estado: dict, nomes: dict) -> list[str]:
    linhas = [
        "| | " + " | ".join(f"{nomes[lado]} ({lado})" for lado in SIDES) + " |",
        "|---|---|---|",
    ]

    def efeitos(f):
        return (
            "; ".join(
                f"{i['efeito']} (dur {i['duracao']}, stacks {i['stacks']}, int "
                f"{_r(i['intensidade'])}, fonte {i['fonte']})"
                for i in f["efeitos"]
            )
            or "—"
        )

    def buffs(f):
        return (
            "; ".join(
                f"{n} ({b['stat']} {_r(b['valor'])}, dur {b['duracao']})"
                for n, b in f["buffs"].items()
            )
            or "—"
        )

    def recargas(f):
        return ", ".join(f"{_nome_da_carta(k)} {v}" for k, v in f["recargas"].items()) or "—"

    campos = (
        ("HP", lambda f: f"{f['hp']}/{f['hp_max']}"),
        ("MP", lambda f: f"{f['mp']}/{f['mp_max']}"),
        ("ST / MG / AG / DF", lambda f: f"{f['st']} / {f['mg']} / {f['ag']} / {f['df']}"),
        ("Recargas (contador interno)", recargas),
        ("Buffs", buffs),
        ("Efeitos", efeitos),
        ("death_ignore gasto / vivo", lambda f: f"{f['death_ignore_usado']} / {f['vivo']}"),
    )
    for rotulo, f in campos:
        linhas.append(f"| {rotulo} | {f(estado['p1'])} | {f(estado['p2'])} |")
    return linhas


def _diferencas(antes: dict, depois: dict) -> list[str]:
    mud = []
    for k in ("hp", "mp", "st", "mg", "ag", "df", "hp_max", "mp_max"):
        if antes[k] != depois[k]:
            mud.append(f"{k} {antes[k]} → {depois[k]}")
    for sid in sorted(set(antes["recargas"]) | set(depois["recargas"])):
        a, d = antes["recargas"].get(sid), depois["recargas"].get(sid)
        if a != d:
            mud.append(
                f"recarga {_nome_da_carta(sid)} {a if a is not None else '—'} → "
                f"{d if d is not None else 'livre'}"
            )
    for nome in sorted(set(antes["buffs"]) | set(depois["buffs"])):
        a, d = antes["buffs"].get(nome), depois["buffs"].get(nome)
        if a != d:
            if a is None:
                mud.append(f"buff {nome} entra ({d['stat']} {_r(d['valor'])}, dur {d['duracao']})")
            elif d is None:
                mud.append(f"buff {nome} expira")
            else:
                mud.append(f"buff {nome} dur {a['duracao']} → {d['duracao']}")
    chave = lambda i: (i["efeito"], i["fonte"])  # noqa: E731
    ea = {chave(i): i for i in antes["efeitos"]}
    ed = {chave(i): i for i in depois["efeitos"]}
    for k in sorted(set(ea) | set(ed)):
        a, d = ea.get(k), ed.get(k)
        if a != d:
            if a is None:
                mud.append(
                    f"efeito {k[0]} entra (dur {d['duracao']}, stacks {d['stacks']}, int "
                    f"{_r(d['intensidade'])})"
                )
            elif d is None:
                mud.append(f"efeito {k[0]} sai")
            else:
                mud.append(
                    f"efeito {k[0]}: dur {a['duracao']} → {d['duracao']}, stacks {a['stacks']} → "
                    f"{d['stacks']}"
                )
    if antes["death_ignore_usado"] != depois["death_ignore_usado"]:
        mud.append("death_ignore gasto")
    if antes["vivo"] != depois["vivo"]:
        mud.append("morreu" if not depois["vivo"] else "voltou à vida")
    return mud


def _rolagem_md(r: dict) -> str:
    if r["operacao"] == "randrange":
        a, b = r["argumentos"]
        sorteio = f"`randrange({a}, {b})` — inteiro uniforme em [{a}, {b - 1}]"
    else:
        sorteio = "`random()` — real uniforme em [0, 1)"
    chance = f"chance {_r(r['chance'])}" if "chance" in r else "limiar 0.5 (moeda)"
    verdade = "verdadeiro" if r["teste_verdadeiro"] else "falso"
    return (
        f"sorteio nº {r['chamada']} [{r['mecanica']}]: {sorteio} → **{_r(r['valor'])}**; "
        f"{chance}; teste `{r['teste']}` (operador `{r['operador']}`) é {verdade} ⇒ "
        f"**{r['resultado']}** — chamado em `{r['chamador']}`"
    )


class _Transcricao:
    """Escreve a final a partir do trace, na ordem em que as coisas aconteceram."""

    def __init__(self, partida: Partida) -> None:
        self.partida = partida
        self.trace = partida.auditado.trace
        self.nomes = {lado: partida.lados[lado].nome for lado in SIDES}
        self.linhas: list[str] = []
        self._consumidos: set[int] = set()
        # As leis que `try_apply_status` anuncia saem de dentro da chamada, antes
        # do registro do status; aparecem logo depois do bloco dele.
        self._leis_do_status: list[dict] = []

    def w(self, *linhas: str) -> None:
        self.linhas.extend(linhas)

    def nome(self, lado: str | None) -> str:
        return f"{self.nomes[lado]} ({lado})" if lado in self.nomes else str(lado)

    def escrever(self) -> list[str]:
        registros = self.trace.records
        por_rodada: dict[int, list[dict]] = {}
        for r in registros:
            if r["kind"] in ("fichas", "resultado"):
                continue
            por_rodada.setdefault(r["rodada"], []).append(r)
        for numero in sorted(por_rodada):
            self.rodada(numero, por_rodada[numero])
        return self.linhas

    def rodada(self, numero: int, registros: list[dict]) -> None:
        self.w(f"## Rodada {numero}", "")
        escolhas = [r for r in registros if r["kind"] == "escolha"]
        iniciativa = [r for r in registros if r["kind"] == "iniciativa"]
        ordem = next((r for r in registros if r["kind"] == "ordem"), None)
        dano_rodada, cura_rodada = _dano_e_cura(registros)
        for r in registros:
            if r["seq"] in self._consumidos:
                continue
            k = r["kind"]
            if k == "rodada_inicio":
                self.w(
                    f"### {numero}.0 Estado no início da rodada",
                    "",
                    *_estado_md(r["estado"], self.nomes),
                    "",
                )
                self.w(f"### {numero}.1 Escolha simultânea", "")
                self.w(
                    "As duas visões foram montadas antes da primeira escolha (`run_round`); "
                    "nenhum controlador recebe a ação, o herói ou o controlador do outro.",
                    "",
                )
                for e in escolhas:
                    self.escolha(e)
            elif k == "evento_do_motor":
                self.evento(r, iniciativa, ordem, numero)
            elif k == "inicio_oportunidade":
                self.inicio_oportunidade(r, registros)
            elif k == "skill_inicio":
                self.skill_inicio(r)
            elif k in ("base_ataque_basico", "base_skill"):
                pass  # entra no bloco do golpe
            elif k == "golpe_inicio":
                self.golpe(r, registros)
            elif k == "status":
                self.status(r)
            elif k == "interacoes":
                self.interacoes(r)
            elif k == "skill_fim":
                self.skill_fim(r, registros)
            elif k == "rodada_fim":
                self.rodada_fim(r, dano_rodada, cura_rodada)
            elif k == "rolagem" and r["mecanica"].startswith(("desempate", "aplicação de status")):
                pass  # entra no bloco da iniciativa ou no do status, que vem logo depois
            elif k == "rolagem":
                self.w(f"- {_rolagem_md(r)}")
        self.w("")

    # --- escolha e lock ---

    def escolha(self, e: dict) -> None:
        v = e["visao"]
        me, op = v["me"], v["opponent"]
        legais = ", ".join(nome_da_acao(a) for a in e["acoes_legais"])
        recargas = ", ".join(f"{_nome_da_carta(s)} {n}" for s, n in e["recargas_no_lock"].items())
        self.w(
            f"**{self.nome(e['lado'])}**",
            "",
            f"- Estado recebido (`DuelView`, rodada {v['round_number']}): eu HP "
            f"{me['hp']}/{me['hp_max']}, "
            f"MP {me['mp']}/{me['mp_max']}, efeitos {me['effects'] or '—'}, buffs "
            f"{me['buffs'] or '—'}; "
            f"adversário {op['name']} HP {op['hp']}/{op['hp_max']}, MP {op['mp']}/{op['mp_max']}, "
            f"efeitos {op['effects'] or '—'}, buffs {op['buffs'] or '—'}.",
            f"- Recargas vistas no lock (oportunidades que ainda faltam): {recargas or '—'}",
            f"- Ações legais: {legais}",
            f"- Escolha: **{nome_da_acao(e['acao'])}** — justificativa da política: "
            f"{e['justificativa']}",
            f"- Validação: {'legal' if e['legal'] else 'ILEGAL'} na lista da visão; aceita por "
            "`Duel._validate` (uma ação ilegal levanta erro antes de qualquer mudança).",
            f"- Custo de MP: {e['custo_mp']}",
            "",
        )

    def evento(self, r: dict, iniciativa, ordem, numero) -> None:
        d = r["detalhe"]
        nome = r["nome"]
        if nome == "mp_reserved":
            self.w(
                f"- Lock: {self.nome(r['lado'])} reserva **{d['amount']} MP** (sai do caixa livre "
                "agora)."
            )
        elif nome == "actions_locked":
            self.w(
                "- Ações travadas: "
                + "; ".join(f"{self.nome(lado)} = {nome_da_acao(a)}" for lado, a in d.items()),
                "",
            )
            self.iniciativa(iniciativa, ordem, numero)
        elif nome == "order_locked":
            self.w(
                f"- **Ordem travada**: {' → '.join(self.nome(lado) for lado in d['order'])} "
                f"(critério `{d['by']}`).",
                "",
            )
        elif nome == "action_cancelled":
            causa = {"control": "controle", "death": "morte"}[d["cause"]]
            self.w(f"- Ação de {self.nome(r['lado'])} **cancelada por {causa}**.")
        elif nome == "mp_refunded":
            self.w(
                f"- Devolução: {self.nome(r['lado'])} recebe de volta {d['amount']} MP reservados."
            )
        elif nome == "action_executed":
            self.w(
                f"- Motor (`action_executed`): {self.nome(r['lado'])} executou "
                f"{nome_da_acao(d['action'])}; "
                f"MP gasto {d['mp_spent']}, dano ao adversário {d['damage']}.",
                "",
            )
        elif nome == "duel_finished":
            self.w(f"- **Fim do duelo**: vence {self.nome(r['lado'])}, motivo `{d['reason']}`.", "")
        elif nome == "surrender":
            self.w(f"- Rendição de {self.nome(r['lado'])}.")
        else:
            self.w(f"- Evento do motor `{nome}`: {d}")

    def iniciativa(self, leituras: list[dict], ordem: dict | None, numero: int) -> None:
        self.w(f"### {numero}.2 Initiative Score", "")
        for x in leituras:
            self.w(
                f"**{self.nome(x['lado'])}** — nível próprio {x['nivel']}, adversário "
                f"{x['nivel_oponente']}; "
                f"referências globais `foundation_reference({x['nivel']})`.",
                "",
                "| Atributo | Efetivo | REF | Efetivo / REF | √ |",
                "|---|---|---|---|---|",
            )
            for p in x["parcelas"]:
                self.w(
                    f"| {p['stat']} | {_r(p['valor'])} | {_r(p['ref'])} | {_r(p['razao'])} | "
                    f"{_r(p['raiz'])} |"
                )
            self.w(
                "",
                f"- Soma das seis raízes (`math.fsum`): {_r(x['soma_raizes'])}",
                f"- ÷ 6 = build {_r(x['build'])}",
                f"- Δnível = {x['delta_nivel']}; Δ × {_r(PVP_INITIATIVE_LEVEL_STEP)} = "
                f"{_r(x['delta_x_step'])}, limitado a "
                f"±{_r(x['teto_do_modificador'])} → modificador {_r(x['modificador'])}",
                f"- **Score = {_r(x['build'])} × {_r(x['modificador'])} = {_r(x['score'])}**",
                f"- AG relativa (desempate): {_r(x['ag'])} / {_r(x['ref_ag'])} = "
                f"{_r(x['ag_relativa'])}",
                "",
            )
        if ordem is None:
            return
        a, b = ordem["score"]["p1"], ordem["score"]["p2"]
        sinal = ">" if a > b else ("<" if a < b else "=")
        self.w(
            f"- Comparação: score p1 {_r(a)} {sinal} score p2 {_r(b)} (floats crus, sem "
            "arredondamento)."
        )
        if ordem["scores_iguais"]:
            ag1, ag2 = ordem["ag_relativa"]["p1"], ordem["ag_relativa"]["p2"]
            self.w(f"- Empate de score: AG relativa p1 {_r(ag1)} vs p2 {_r(ag2)}.")
        else:
            self.w("- AG relativa: não consultada (o score decidiu).")
        moeda = [
            r
            for r in self.trace.records
            if r["kind"] == "rolagem"
            and r["rodada"] == numero
            and r["mecanica"].startswith("desempate")
        ]
        if moeda:
            self.w(f"- {_rolagem_md(moeda[0])}")
        else:
            self.w("- Desempate absoluto: não ocorreu; nenhuma rolagem de moeda.")
        self.w(
            f"- Ordem: {self.nome(ordem['primeiro'])} → {self.nome(ordem['segundo'])} "
            f"(`{ordem['decidido_por']}`).",
            "",
        )

    # --- oportunidade ---

    def inicio_oportunidade(self, r: dict, registros: list[dict]) -> None:
        lado = r["ator"]
        self.w(
            f"### Oportunidade de {self.nome(lado)}",
            "",
            "Início da oportunidade (`process_turn_start_effects`):",
            "",
        )
        g = r["regeneracao"]
        fim = next(
            x for x in registros if x["kind"] == "fim_inicio_oportunidade" and x["seq"] > r["seq"]
        )
        tick = next(
            (
                x
                for x in registros
                if x["kind"] == "tick_de_efeitos" and r["seq"] < x["seq"] < fim["seq"]
            ),
            None,
        )
        corte = next(
            (x for x in registros if x["kind"] == "corte_de_mp_livre" and x["seq"] > fim["seq"]),
            None,
        )
        antes, depois = r["antes"], fim["depois"]
        rec = [
            f"{_nome_da_carta(s)} {v} → {depois['recargas'].get(s, 'livre')}"
            for s, v in antes["recargas"].items()
        ]
        self.w(
            f"- Recargas (−1 cada, some ao chegar a 0): {'; '.join(rec) or 'nenhuma'}",
            f"- Regeneração de MP: {g['base_formula']} = {_r(g['base'])}; + mana_regen "
            f"{_r(g['modificador_mana_regen'])} → {g['total_formula']} = **{g['total_int']}**; "
            f"MP livre {g['mp_antes']} → "
            f"min({g['teto']}, {g['mp_antes']} + {g['total_int']}) = "
            f"{g['mp_depois_da_regeneracao']}",
        )
        if tick is not None:
            rel = tick["relatorio"]
            self.w(
                f"- Efeitos do núcleo (`tick_effects`): DoT {rel['dot'] or '—'}, dreno "
                f"{rel['drain'] or '—'}, "
                f"expirados {rel['expired'] or '—'}, leis {rel['laws'] or '—'}, pula a vez: "
                f"{rel['skip_turn']}"
            )
            self._consumidos.add(tick["seq"])
        mud = _diferencas(antes, depois)
        self.w(f"- Mudanças de estado no início: {'; '.join(mud) or 'nenhuma'}")
        if corte is not None:
            self.w(
                f"- Corte do MP livre (`Duel._clamp_free_mp`): reservado {corte['reservado']}, "
                "teto livre "
                f"{corte['teto_livre']} → MP {corte['mp_antes']} → {corte['mp_depois']}"
            )
            self._consumidos.add(corte["seq"])
        self.w(
            "- Perde a oportunidade por controle: "
            f"{'**sim**' if fim['perde_a_oportunidade'] else 'não'}",
            "",
        )
        self._consumidos.add(fim["seq"])

    def skill_inicio(self, r: dict) -> None:
        reserva = next(
            (
                x["detalhe"]["amount"]
                for x in self.trace.records
                if x["kind"] == "evento_do_motor"
                and x["nome"] == "mp_reserved"
                and x["rodada"] == r["rodada"]
                and x["lado"] == r["ator"]
            ),
            0,
        )
        self.w(
            f"**Skill {r['nome']}** (`{r['skill']}`) de {self.nome(r['ator'])}",
            "",
            f"- Tipo `{r['tipo']}`, valor {r['valor']} {r['stat']}; alvo declarado "
            f"`{r['alvo_declarado']}` "
            f"→ recebe {self.nome(r['receptor'])}",
            f"- Requisito de equipamento: {r['requisito'] or 'nenhum'} → atendido: "
            f"{r['requisito_atendido']}",
            f"- Custo {r['custo_mp']} MP; reserva feita no lock {reserva}; MP disponível na "
            "cobrança "
            f"(livre + reserva liberada) {r['mp_disponivel']}",
            f"- Recarga antes do uso: {r['recarga_antes']}; declarada {r['recarga_declarada']} "
            f"(o motor grava declarada + 1)",
        )
        if "cura_calculo" in r:
            c = r["cura_calculo"]
            self.w(
                f"- Cura: {c['base_formula']} = {c['base']}; potion_heal_bonus "
                f"{_r(c['potion_heal_bonus'])}% "
                f"→ total {c['total']}"
            )
        if "buff_calculo" in r:
            b = r["buff_calculo"]
            self.w(
                f"- Buff: {b['stat']} declarado {b['declarado']} → valor gravado {b['valor']} "
                f"({b['regra']})"
            )
        if r["tipo"] == "status":
            self.w(
                f"- Status: chance base {r['chance_declarada']}%, duração declarada "
                f"{r['duracao_declarada']}"
            )
        self.w("")

    def skill_fim(self, r: dict, registros: list[dict]) -> None:
        inicio = next(
            x
            for x in reversed([y for y in registros if y["seq"] < r["seq"]])
            if x["kind"] == "skill_inicio" and x["ator"] == r["ator"]
        )
        res = r["resultado"]
        caster = _diferencas(inicio["antes"]["caster"], r["depois"]["caster"])
        alvo = _diferencas(inicio["antes"]["alvo"], r["depois"]["alvo"])
        self.w(
            f"- Resultado da skill: `{res['kind']}`; MP debitado {r['mp_debitado']}; recarga "
            "depois "
            f"{r['recarga_depois']}"
            + (f"; cura {res['heal_amount']}" if res["kind"] == "heal" else "")
            + (
                f"; status {res['status_effect']} "
                f"{'pegou' if res['status_success'] else 'não pegou'}"
                if res["kind"] == "status"
                else ""
            )
            + (f"; buff gravado {r['buff_gravado']}" if r["buff_gravado"] else ""),
            f"- Mudanças em quem lançou: {'; '.join(caster) or 'nenhuma'}",
            f"- Mudanças no adversário: {'; '.join(alvo) or 'nenhuma'}",
            "",
        )

    def status(self, s: dict) -> None:
        self.w(
            f"**Status `{s['status']}`** sobre {self.nome(s['alvo'])} (via `{s['origem']}`, fonte "
            f"`{s['fonte']}`)",
            "",
            f"- Chance base {_r(s['chance_base'])}%; resistência do alvo "
            f"{_r(s['resistencia_do_alvo'])}% → "
            f"efetiva {s['chance_formula']} = {_r(s['chance_efetiva'])}%",
        )
        if not s["rolou"]:
            self.w(
                "- Chance efetiva ≤ 0: o motor não rola (nenhum sorteio consumido) e o status é "
                "anulado."
            )
        else:
            rol = next(x for x in self.trace.records if x["seq"] == s["rolagem_seq"])
            self.w(f"- {_rolagem_md(rol)}")
            self._consumidos.add(rol["seq"])
            if s["rolagem_aprovada"]:
                leis = ", ".join(s["leis_de_duracao"]) or "nenhuma"
                self.w(
                    f"- Duração pedida {s['duracao_pedida']} → após leis ({leis}) "
                    f"{s['duracao_apos_leis']}; "
                    f"o núcleo decide empilhar/renovar: {'aplicou' if s['pegou'] else 'recusou'}"
                )
        antes = s["instancia_antes"]
        depois = s["instancia_depois"]
        campos = ("duration", "stacks", "intensity", "source_id")
        antes = [{k: i[k] for k in campos} for i in antes]
        depois = [{k: i[k] for k in campos} for i in depois]
        self.w(
            f"- Instâncias de `{s['status']}` no alvo antes: {antes or '—'}; "
            f"depois: {depois or '—'}",
            "",
        )
        for lei in self._leis_do_status:
            self._lei(lei)
        self._leis_do_status.clear()

    def interacoes(self, r: dict) -> None:
        if r["origem"] == "try_apply_status":
            self._leis_do_status.append(r)
            return
        self._lei(r)

    def _lei(self, r: dict) -> None:
        leis = ", ".join(f"{lei['nome']} (`{lei['id']}`)" for lei in r["leis"])
        self.w(f"- Lei(s) de interação anunciada(s) por `{r['origem']}`: {leis}", "")

    def golpe(self, inicio: dict, registros: list[dict]) -> None:
        gid = inicio["golpe"]
        do_golpe = [r for r in registros if r["golpe"] == gid]
        for r in do_golpe:
            self._consumidos.add(r["seq"])
        fim = next(r for r in do_golpe if r["kind"] == "golpe_fim")
        base = next(
            r
            for r in reversed([x for x in registros if x["seq"] < inicio["seq"]])
            if r["kind"] in ("base_ataque_basico", "base_skill")
        )
        acerto = next(r for r in do_golpe if r["kind"] == "rolagem" and r["mecanica"] == "acerto")
        crit_chance = next((r for r in do_golpe if r["kind"] == "chance_de_critico"), None)
        crit_rol = next(
            (r for r in do_golpe if r["kind"] == "rolagem" and r["mecanica"] == "crítico"), None
        )
        mods = next((r for r in do_golpe if r["kind"] == "modificadores"), None)
        funil = next((r for r in do_golpe if r["kind"] == "funil"), None)
        egide = next((r for r in do_golpe if r["kind"] == "egide"), None)
        res = fim["resultado"]
        acao = f"skill `{inicio['skill']}`" if inicio["skill"] else "ataque básico"
        self.w(
            f"**Golpe #{gid}** — {self.nome(inicio['atacante'])} → "
            f"{self.nome(inicio['defensor'])}, {acao}",
            "",
        )
        d = acerto["detalhe_chance"]
        if base["kind"] == "base_ataque_basico":
            pesos = ", ".join(f"{t['stat']} {_r(t['peso'])}" for t in base["termos"])
            poder = (
                f"Σ = {_r(base['soma_ponderada'])}; dano médio {base['media_formula']} = "
                f"{base['media']}; "
                f"BASE do básico = {base['poder_formula']} = **{base['poder']}**"
            )
            arma = (
                f"+{_r(base['arma_percent'])}% → fator {_r(1 + base['arma_percent'] / 100)} "
                "(dentro do dano médio)"
            )
        elif base.get("sem_escala"):
            pesos, poder, arma = "—", f"carta sem escala: BASE = {base['poder']}", "—"
        else:
            pesos = ", ".join(f"{t['stat']} {_r(t['peso'])}" for t in base["termos"])
            poder = (
                f"Σ = {_r(base['soma_ponderada'])}; × arma = {_r(base['com_arma'])}; × power "
                f"{_r(base['power'])} "
                f"= {_r(base['total'])}; {base['poder_formula']} = **{base['poder']}**"
            )
            arma = f"+{_r(base['arma_percent'])}% → fator {_r(1 + base['arma_percent'] / 100)}"
        atributos = ", ".join(f"{t['stat']} {_r(t['valor'])}" for t in base.get("termos", ()))
        basico = base["kind"] == "base_ataque_basico"
        itens = [
            f"Atributos ofensivos efetivos: {atributos or '—'}",
            f"Pesos ({'classe, `CLASS_WEIGHTS`' if basico else 'da carta'}): {pesos}",
            f"Poder básico da ação: {poder}"
            + (
                f" (multiplicador do básico {_r(BASIC_ATTACK_POWER_MULT)})"
                if base["kind"] == "base_ataque_basico"
                else ""
            ),
            f"Bônus de arma: {arma}",
        ]
        if mods is None:
            itens.append(
                "Modificadores condicionais: não calculados — o golpe errou antes do funil."
            )
        elif mods["condicao_da_carta"]:
            itens.append(
                f"Modificadores condicionais: condição `{mods['condicao_da_carta']}` "
                f"{'satisfeita' if mods['condicao_satisfeita'] else 'não satisfeita'} contra este "
                "alvo"
            )
        else:
            itens.append("Modificadores condicionais: inaplicável (a ação não declara condição)")
        itens.append(
            f"Chance de acerto: {d['base']} + swing {_r(d['swing'])} ({d['swing_formula']}) − "
            "evasão "
            f"{_r(d['evasao_defensor'])} + medo/precisão temporários "
            f"{d['medo_precisao_temporarios']} + precisão "
            f"{_r(d['precisao_permanente'])} + modificador da ação {d['modificador_da_acao']} − "
            "ocultação "
            f"{d['ocultacao_defensor']} = {_r(d['bruto'])} → clamp [{d['piso']}, {d['teto']}] e "
            f"int → **{acerto['chance']}**"
        )
        itens.append(f"Rolagem de acerto: {_rolagem_md(acerto)}")
        if res["was_evaded"]:
            itens += [
                f"{x}: inaplicável — o golpe errou e o motor parou aqui."
                for x in (
                    "Chance de crítico",
                    "Rolagem de crítico",
                    "Multiplicador de crítico",
                    "+MULT",
                    "×MULT",
                    "Produto bruto e XMULT_CAP",
                    "Defesa efetiva do alvo",
                    "Fator de defesa",
                    "Mitigação",
                    "Valores intermediários",
                    "Truncamentos",
                    "Dano final do funil",
                    "Égide de Mana",
                    "MP da Égide",
                )
            ]
            itens.append(
                f"Dano aplicado ao HP: 0 (HP do alvo {fim['hp_defensor'][0]} → "
                f"{fim['hp_defensor'][1]})"
            )
            itens.append("Roubo de vida: inaplicável (sem dano).")
            itens.append("Morte / death_ignore: não verificado — sem dano.")
        else:
            itens.append(
                f"Chance de crítico: padrão {crit_chance['padrao']} + carta "
                f"{crit_chance['da_carta']} + fontes do "
                f"atacante {crit_chance['fontes_do_atacante']} = {crit_chance['bruto']}, teto "
                f"{crit_chance['teto']} "
                f"→ **{crit_chance['final']}**"
            )
            itens.append(f"Rolagem de crítico: {_rolagem_md(crit_rol)}")
            critico = next((x for x in mods["xmult"] if x["fonte"] == "crítico"), None)
            itens.append(
                f"Multiplicador de crítico: {critico['formula']} = {_r(critico['fator'])}"
                if critico
                else "Multiplicador de crítico: não aplicado (sem crítico)"
            )
            itens.append(
                "+MULT: "
                + (
                    "; ".join(f"{m['fonte']} {_r(m['parcela'])}" for m in mods["mult"])
                    or "nenhuma parcela"
                )
                + f" → 1 + Σ = {_r(funil['mult_total'])}"
            )
            itens.append(
                "×MULT: "
                + (
                    "; ".join(f"{x['fonte']} ×{_r(x['fator'])}" for x in mods["xmult"])
                    or "nenhuma parcela (×1.0)"
                )
            )
            itens.append(
                f"Produto ×MULT bruto {_r(funil['xmult_bruto'])}; `XMULT_CAP` {_r(XMULT_CAP)} → "
                "aplicado "
                f"{_r(funil['xmult_aplicado'])}"
            )
            itens.append(f"Defesa efetiva do alvo: {funil['defesa_alvo']}")
            itens.append(
                f"Fator de defesa: {DEFENSE_K} / ({DEFENSE_K} + {funil['defesa_alvo']}) = "
                f"{_r(funil['fator_defesa'])}"
            )
            itens.append(
                "Mitigação: "
                + "; ".join(
                    f"{m['fonte']} = {_r(m['fator'])}"
                    + (
                        f" (damage_reduction {_r(m['damage_reduction'])}, {m['formula']})"
                        if "formula" in m
                        else ""
                    )
                    for m in mods["mitigacao"]
                )
            )
            itens.append(
                f"Valores intermediários: bruto = {funil['bruto_formula']} = {_r(funil['bruto'])}; "
                + " → ".join(f"{p['etapa']} = {p['valor']}" for p in funil["passos"])
            )
            itens.append(
                "Truncamentos executados: `max(1, int(bruto))` uma vez; depois `int(anterior × "
                "fator)` para "
                f"cada um dos {len(funil['passos']) - 1} fatores de mitigação; por fim `max(1, ·)`"
            )
            itens.append(f"Dano final do funil: **{funil['final']}**")
            if egide is None or egide.get("inaplicavel"):
                motivo = (
                    "o alvo não tem Égide"
                    if (egide is None or not egide["fracao"])
                    else "sem MP livre ou dano ≤ 1"
                )
                itens.append(f"Égide de Mana: inaplicável ({motivo}); passa {funil['final']}")
                itens.append("MP da Égide: 0")
            else:
                itens.append(
                    f"Égide de Mana: desejado {egide['desejado_formula']} = {egide['desejado']}; "
                    "possível "
                    f"{egide['possivel_formula']} = {egide['possivel']}; passa max(1, "
                    f"{egide['dano_entrada']} − "
                    f"{egide['possivel']}) = {egide['dano_saida']}"
                )
                itens.append(f"MP da Égide: {egide['custo_formula']} = {egide['custo_mp']}")
            itens.append(
                f"Dano aplicado ao HP: `take_damage({res['damage']})`; HP do alvo "
                f"{fim['hp_defensor'][0]} → "
                f"{fim['hp_defensor'][1]} (retirado {fim['hp_aplicado']})"
            )
            roubo = fim["roubo_de_vida"]
            itens.append(
                f"Roubo de vida: {roubo['percentual']}% → {roubo['formula']} = "
                f"{roubo['calculada']}; HP do "
                f"atacante +{roubo['aplicada']} (teto do HP máximo)"
                if roubo
                else "Roubo de vida: 0% no atacante — inaplicável"
            )
            morte = "o alvo morreu" if fim["defensor_morreu"] else "o alvo segue vivo"
            if fim["death_ignore_disparou"]:
                morte = (
                    "golpe letal anulado por `death_ignore`: HP fixado em 1, uma vez por combate"
                )
            itens.append(f"Morte e death_ignore: HP final {fim['hp_defensor'][1]} → {morte}")
        self.w(*[f"{i}. {texto}" for i, texto in enumerate(itens, start=1)], "")
        for r in do_golpe:
            if r["kind"] == "status":
                self.status(r)
            elif r["kind"] == "interacoes":
                self.interacoes(r)

    def rodada_fim(self, r: dict, dano: dict, cura: dict) -> None:
        reg = r["registro"]
        numero = reg["number"]
        self.w(
            f"### {numero}.9 Estado ao final da rodada",
            "",
            *_estado_md(r["estado"], self.nomes),
            "",
        )
        self.w(
            "MP reservado ao fim da rodada: 0 dos dois lados (toda reserva foi cobrada ou "
            "devolvida).",
            "",
        )
        for passo in reg["steps"]:
            lado = passo["side"]
            self.w(
                f"- {self.nome(lado)}: {nome_da_acao(passo['action'])} — "
                f"{DESFECHO[passo['outcome']]}"
                f"; dano causado na rodada {dano[lado]} (golpes e DoT), recebido "
                f"{dano[opponent_of(lado)]}"
                f"; cura {cura[lado]}"
            )
        self.w("")


def _dano_e_cura(registros: list[dict]) -> tuple[dict, dict]:
    """Dano causado e cura de cada lado numa rodada, a partir do trace."""
    dano = {lado: 0 for lado in SIDES}
    cura = {lado: 0 for lado in SIDES}
    for r in registros:
        if r["kind"] == "golpe_fim" and not r["resultado"]["was_evaded"]:
            dano[r["atacante"]] += r["resultado"]["damage"]
            if r["roubo_de_vida"]:
                cura[r["atacante"]] += r["roubo_de_vida"]["aplicada"]
        elif r["kind"] == "tick_de_efeitos":
            dano[opponent_of(r["ator"])] += sum(r["relatorio"]["dot"].values())
        elif r["kind"] == "skill_fim" and r["resultado"]["kind"] == "heal":
            inicio = next(
                x
                for x in reversed([y for y in registros if y["seq"] < r["seq"]])
                if x["kind"] == "skill_inicio" and x["ator"] == r["ator"]
            )
            cura[r["ator"]] += r["depois"]["caster"]["hp"] - inicio["antes"]["caster"]["hp"]
    return dano, cura


def _conclusao_final(partida: Partida) -> list[str]:
    st = estatisticas(partida)
    duelo = partida.auditado.duelo
    res = duelo.result
    linhas = ["## Conclusão da final (fatos registrados)", ""]
    if res is None:
        return linhas + [f"Inconclusiva: limite técnico de {LIMITE_TECNICO} rodadas atingido.", ""]
    linhas += [
        f"- Campeão: **{res.winner_name}** ({res.winner}); vice: **{res.loser_name}** "
        f"({res.loser}).",
        f"- Rodadas: {res.rounds}. Motivo exato: `{res.reason}` — o HP de {res.loser_name} chegou "
        "a 0 "
        f"durante a rodada {res.rounds}.",
        "",
        "| | " + " | ".join(f"{partida.lados[lado].nome} ({lado})" for lado in SIDES) + " |",
        "|---|---|---|",
    ]
    campos = (
        (
            "Dano causado (golpes + DoT)",
            lambda e: f"{dano_total(e)} ({e['dano_golpes']} + {e['dano_dot']})",
        ),
        ("HP retirado do adversário", lambda e: str(e["hp_retirado"])),
        (
            "Cura (skill + roubo)",
            lambda e: f"{cura_total(e)} ({e['cura_skill']} + {e['roubo_de_vida']})",
        ),
        ("MP consumido em ações", lambda e: str(e["mp_gasto"])),
        ("MP consumido pela Égide", lambda e: str(e["egide_mp"])),
        (
            "Skills usadas",
            lambda e: (
                f"{e['skills']}: "
                + (
                    ", ".join(f"{_nome_da_carta(k)} ×{n}" for k, n in e["skills_usadas"].items())
                    or "—"
                )
            ),
        ),
        ("Ataques básicos", lambda e: str(e["basicos"])),
        ("Acertos / erros", lambda e: f"{e['acertos']} / {e['erros']}"),
        ("Críticos (dano)", lambda e: f"{e['criticos']} ({e['dano_critico']})"),
        ("Status aplicados", lambda e: ", ".join(e["status_aplicados"]) or "—"),
        (
            "Status que falharam na rolagem",
            lambda e: ", ".join(e["status_falharam_na_rolagem"]) or "—",
        ),
        (
            "Status anulados por resistência / recusados",
            lambda e: ", ".join(e["status_anulados"] + e["status_recusados_pelo_nucleo"]) or "—",
        ),
        ("Ações perdidas por controle", lambda e: str(e["perdidas_controle"])),
        ("Rodadas agindo primeiro", lambda e: str(e["primeiro"])),
    )
    for rotulo, f in campos:
        linhas.append(f"| {rotulo} | {f(st['p1'])} | {f(st['p2'])} |")
    hp = {lado: duelo.hero(lado) for lado in SIDES}
    linhas.append(
        "| HP / MP restantes | "
        + " | ".join(
            f"{hp[lado].get_hp()}/{hp[lado].base_hp} · {hp[lado].get_mp()}/{hp[lado].base_mp}"
            for lado in SIDES
        )
        + " |"
    )
    if any(hp[lado].get_hp() < 0 for lado in SIDES):
        linhas += [
            "",
            "HP negativo é o valor cru do motor: `take_damage` não corta em zero, e a sobra mostra "
            "quanto o último golpe passou do necessário.",
        ]
    return linhas + [""]


def _diagnostico_final(partida: Partida) -> list[str]:
    """Interpretação. Cada frase cita os números do trace de que parte."""
    st = estatisticas(partida)
    trace = partida.auditado.trace
    duelo = partida.auditado.duelo
    res = duelo.result
    if res is None:
        return []
    v, p = res.winner, res.loser
    nomes = {lado: partida.lados[lado].nome for lado in SIDES}
    golpes = trace.de("golpe_fim")
    funis = trace.de("funil")
    acertos = {
        lado: [r for r in trace.de("rolagem") if r["mecanica"] == "acerto" and r["ator"] == lado]
        for lado in SIDES
    }

    def media(xs):
        return statistics.mean(xs) if xs else 0.0

    dano_por_golpe = {
        lado: media(
            [
                g["resultado"]["damage"]
                for g in golpes
                if g["atacante"] == lado and not g["resultado"]["was_evaded"]
            ]
        )
        for lado in SIDES
    }
    chance_media = {lado: media([r["chance"] for r in acertos[lado]]) for lado in SIDES}
    defesa = {
        lado: media([f["fator_defesa"] for f in funis if f["ator"] == lado]) for lado in SIDES
    }
    mitig = {
        lado: media(
            [
                next(m["fator"] for m in mo["mitigacao"] if m["fonte"].startswith("entrada"))
                for mo in trace.de("modificadores")
                if mo["ator"] == lado
            ]
        )
        for lado in SIDES
    }
    ultima = duelo.history[-1]
    linhas = [
        "## Diagnóstico (interpretação — separado dos fatos acima)",
        "",
        "As frases abaixo são leitura dos números registrados, não registros do motor. Onde há "
        "estimativa, ela está marcada como tal.",
        "",
    ]
    for lado in SIDES:
        e = st[lado]
        tentados = e["acertos"] + e["erros"]
        linhas.append(
            f"- **{nomes[lado]}**: {tentados} golpes tentados com chance média de acerto "
            f"{chance_media[lado]:.1f}%, "
            f"{e['acertos']} conectaram ({_pct(e['acertos'] / tentados) if tentados else '—'}); "
            "dano médio por "
            f"golpe conectado {dano_por_golpe[lado]:.1f}. O fator de defesa médio que os golpes "
            "dele enfrentaram "
            f"foi {defesa[lado]:.4f} e a mitigação de entrada do alvo, {mitig[lado]:.4f}."
        )
    linhas.append(
        f"- Iniciativa: {nomes[v]} agiu primeiro em {st[v]['primeiro']} de {len(duelo.history)} "
        "rodadas; "
        f"{nomes[p]}, em {st[p]['primeiro']}. Na rodada final, a ordem foi "
        f"{nomes[ultima.order.first]} → {nomes[ultima.order.second]} (`{ultima.order.decided_by}`)."
    )
    linhas += _leitura_da_iniciativa(partida, nomes)
    passo_perdedor = next(s for s in ultima.steps if s.side == p)
    if passo_perdedor.outcome in ("not_reached", "cancelled_death"):
        acao = passo_perdedor.action
        carta = get_skill_by_id(acao.skill_id) if acao.kind == "skill" else None
        natureza = (f"skill de tipo `{carta.effect_type}`" if carta else "ataque básico") + (
            ", que não causa dano" if carta and carta.effect_type != "damage" else ""
        )
        linhas.append(
            f"- Na última rodada, {nomes[p]} havia travado {nome_da_acao(acao)} ({natureza}); a "
            "ação "
            f"ficou {DESFECHO[passo_perdedor.outcome]}, porque {nomes[v]} agiu antes e o golpe "
            "dele "
            "encerrou o duelo."
        )
    hp_v = duelo.hero(v).get_hp()
    if dano_por_golpe[p]:
        linhas.append(
            f"- Margem (estimativa, não registro): {nomes[v]} terminou com {hp_v} de HP; o dano "
            "médio "
            f"por golpe conectado de {nomes[p]} foi {dano_por_golpe[p]:.1f}, ou seja, ~"
            f"{hp_v / dano_por_golpe[p]:.1f} golpe(s) conectado(s) de distância."
        )
    for lado in SIDES:
        e = st[lado]
        if cura_total(e) or e["egide_absorvido"]:
            linhas.append(
                f"- Sustentação de {nomes[lado]}: cura {cura_total(e)} e Égide "
                f"{e['egide_absorvido']} contra "
                f"{dano_total(st[opponent_of(lado)])} de dano recebido."
            )
        if e["criticos"]:
            linhas.append(
                f"- Críticos de {nomes[lado]}: {e['criticos']}, somando {e['dano_critico']} de "
                f"{e['dano_golpes']} de dano de golpe "
                f"({_pct(e['dano_critico'] / e['dano_golpes'])})."
            )
        if e["perdidas_controle"]:
            linhas.append(
                f"- {nomes[lado]} perdeu {e['perdidas_controle']} ação(ões) por controle."
            )
    linhas.append(
        f"- Economia de ação: {nomes[v]} usou {st[v]['skills']} skills e {st[v]['basicos']} "
        "ataques básicos; "
        f"{nomes[p]}, {st[p]['skills']} e {st[p]['basicos']}."
    )
    return linhas + [""]


def _leitura_da_iniciativa(partida: Partida, nomes: dict) -> list[str]:
    """O score de cada rodada e o que mudou nos atributos efetivos desde a primeira.

    A iniciativa é relida a cada rodada sobre o estado atual, então buff e status
    que mexem em atributo ou teto de recurso mexem também na ordem.
    """
    por_rodada: dict[int, dict] = {}
    for x in partida.auditado.trace.de("iniciativa"):
        por_rodada.setdefault(x["rodada"], {})[x["lado"]] = x
    ordem = {r.number: r.order for r in partida.auditado.duelo.history}
    estado_no_lock = {r["rodada"]: r["estado"] for r in partida.auditado.trace.de("rodada_inicio")}
    primeira = por_rodada[min(por_rodada)]
    linhas = ["- Score de iniciativa por rodada (p1 / p2 → quem agiu primeiro):"]
    anterior = None
    for numero in sorted(por_rodada):
        leitura = por_rodada[numero]
        mudancas = []
        for lado in SIDES:
            alteradas = [
                f"{agora['stat']} {inicio['valor']:g}→{agora['valor']:g}"
                for agora, inicio in zip(leitura[lado]["parcelas"], primeira[lado]["parcelas"])
                if agora["valor"] != inicio["valor"]
            ]
            if alteradas:
                mudancas.append(f"{nomes[lado]}: {', '.join(alteradas)}")
        primeiro = ordem[numero].first
        virou = anterior is not None and primeiro != anterior
        # Buff com 1 de duração no lock: entra na leitura desta rodada, mas o
        # início da oportunidade do dono o expira antes da ação.
        ultimo_turno = [
            f"{nome} de {nomes[lado]}"
            for lado in SIDES
            for nome, buff in estado_no_lock[numero][lado]["buffs"].items()
            if buff["duracao"] == 1
        ]
        linhas.append(
            f"  - Rodada {numero}: {leitura['p1']['score']:.6f} / {leitura['p2']['score']:.6f} → "
            f"{nomes[primeiro]}"
            + (" **(a ordem virou)**" if virou else "")
            + (
                f"; atributos efetivos diferentes da rodada 1 — {'; '.join(mudancas)}"
                if mudancas
                else ""
            )
            + (
                f"; com duração 1 no lock (conta nesta leitura e expira no início da "
                f"oportunidade do dono, antes da ação): {', '.join(ultimo_turno)}"
                if ultimo_turno
                else ""
            )
        )
        anterior = primeiro
    linhas.append(
        "  - Leitura: o vetor da iniciativa usa ST/MG/AG/DF efetivos e os TETOS de HP e MP, "
        "então um buff de atributo do próprio lado e um status do adversário que reduz atributo "
        "ou teto entram na ordem da rodada seguinte; quando expiram, saem dela."
    )
    return linhas


def relatorio_final(partida: Partida, *, copa: str = "Copa Arena de Testes 01") -> str:
    trace = partida.auditado.trace
    fichas = trace.de("fichas")[0]
    resultado = trace.de("resultado")[0]
    rolagens = trace.de("rolagem")
    nomes = {lado: partida.lados[lado].nome for lado in SIDES}
    nivel_ref = sorted({partida.lados[lado].espec.nivel for lado in SIDES})
    linhas = [
        f"# {copa} — Final detalhada: {nomes['p1']} × {nomes['p2']}",
        "",
        "Transcrição da final a partir do trace da auditoria (`tools/arena_auditoria.py`), na "
        "ordem em "
        "que o motor executou. Cada número abaixo foi capturado no momento da execução, pela "
        "chamada "
        "real da função canônica; os recálculos que explicam um número são feitos com as mesmas "
        "funções e constantes e conferidos contra o valor devolvido pelo motor — se divergissem, a "
        "auditoria pararia com erro.",
        "",
        "## Convenções",
        "",
        f"- Gerador da partida: `random.Random({partida.semente})`, observado por um proxy que "
        "delega "
        "cada chamada e anota operação, limites, valor e chamador. O proxy não sorteia nada por "
        "conta própria.",
        f"- Rolagens percentuais do motor: `randrange({PERCENTAGE_RANGE_MIN}, "
        f"{PERCENTAGE_RANGE_MAX})`, "
        "inteiro uniforme em [1, 100]. Não é D20. O desempate de iniciativa usa `random() < 0.5`.",
        "- Acerto: o golpe ERRA quando `rolagem > chance`. Crítico: CRITA quando `rolagem <= "
        "chance`. "
        "Status: NÃO pega quando `rolagem > chance efetiva`.",
        "- Floats aparecem com `repr`: a precisão total que o motor usou. Nada é arredondado antes "
        "de "
        "uma comparação.",
        "- Referências de iniciativa: `foundation_reference(nível)` — a média das três classes "
        "pelo "
        f"crescimento canônico. Níveis desta final: {nivel_ref}.",
        "- Golpes de skill são resolvidos por `apply_skill` com `publish=None`; a auditoria os vê "
        "porque intercepta a função no módulo, não o EventBus.",
        f"- Limite técnico do laço: {LIMITE_TECNICO} rodadas (não atingido).",
        "",
        "## Referências globais usadas",
        "",
        "| Nível | REF_hp | REF_mp | REF_st | REF_mg | REF_ag | REF_df |",
        "|---|---|---|---|---|---|---|",
    ]
    for n in nivel_ref:
        ref = foundation_reference(n)
        linhas.append(
            f"| {n} | "
            + " | ".join(_r(getattr(ref, s)) for s in ("hp", "mp", "st", "mg", "ag", "df"))
            + " |"
        )
    linhas += ["", "## Fichas completas antes do duelo", ""]
    linhas += _ficha_md(fichas["p1"], "p1")
    linhas += _ficha_md(fichas["p2"], "p2")
    linhas += _Transcricao(partida).escrever()
    linhas += _conclusao_final(partida)
    linhas += [
        "## Todas as chamadas ao gerador",
        "",
        f"{len(rolagens)} chamadas, igual ao contador do proxy ({resultado['chamadas_ao_rng']}).",
        "",
        "| Nº | Rodada | Ator | Mecânica | Operação | Limites | Valor | Chance | Teste | Resultado "
        "|",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for r in rolagens:
        limites = (
            f"[{r['argumentos'][0]}, {r['argumentos'][1] - 1}]"
            if r["operacao"] == "randrange"
            else "[0, 1)"
        )
        chance = _r(r["chance"]) if "chance" in r else "0.5 (moeda)"
        veredito = (
            "—"
            if r["mecanica"].startswith("desempate")
            else ("aprovado" if r["aprovado"] else "recusado")
        )
        linhas.append(
            f"| {r['chamada']} | {r['rodada']} | {r['ator'] or '—'} | {r['mecanica']} "
            f"| `{r['operacao']}` | {limites} | {_r(r['valor'])} | {chance} "
            f"| `{r['teste']}` → {'V' if r['teste_verdadeiro'] else 'F'} "
            f"| {veredito}: {r['resultado']} |"
        )
    linhas += ["", "## Verificação de fidelidade", ""]
    linhas.append(
        f"A final rodou duas vezes com `random.Random({partida.semente})`, os mesmos gladiadores "
        "(preparação nova a cada vez) e a mesma política: sem nenhuma instrumentação e auditada."
    )
    linhas.append("")
    linhas += [f"- {'✔' if ok else '✘'} {nome}" for nome, ok in partida.fidelidade]
    linhas += ["", "Coerência do trace com o que o motor registrou:", ""]
    linhas += [f"- {'✔' if ok else '✘'} {nome}" for nome, ok in partida.coerencia]
    linhas += [
        "",
        "Limitação conhecida: as parcelas intermediárias (swing de acerto, termos do BASE, buckets "
        "do "
        "funil, Égide, regeneração) são recalculadas no instante da chamada com as funções do "
        "motor e "
        "conferidas contra o valor devolvido; a regeneração de MP é descrita pela mesma fórmula de "
        "`process_turn_start_effects`, e o valor resultante aparece no estado logo depois.",
        "",
    ]
    linhas += _diagnostico_final(partida)
    return "\n".join(linhas)


def trace_json(
    partida: Partida,
    *,
    copa: str = "Copa Arena de Testes 01",
    semente_principal: int = SEMENTE_PRINCIPAL,
) -> dict:
    return {
        "copa": copa,
        "partida": partida.titulo,
        "fase": partida.fase,
        "seed_principal": semente_principal,
        "seed_da_partida": partida.semente,
        "lados": {
            lado: {
                "id": partida.lados[lado].id,
                "nome": partida.lados[lado].nome,
                "overall_power": partida.lados[lado].poder,
            }
            for lado in SIDES
        },
        "limite_tecnico": LIMITE_TECNICO,
        "fidelidade": [{"verificacao": n, "ok": ok} for n, ok in partida.fidelidade],
        "coerencia": [{"verificacao": n, "ok": ok} for n, ok in partida.coerencia],
        "chamadas_ao_rng": partida.auditado.rng.chamadas,
        "registros": partida.auditado.trace.records,
    }


def escrever_relatorios(copa: Copa, pasta: Path = PASTA_DE_SAIDA) -> list[Path]:
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = [pasta / ARQUIVO_RESUMO]
    caminhos[0].write_text(relatorio_resumo(copa) + "\n", encoding="utf-8")
    if "final" in copa.fases:
        final = copa.fases["final"][0]
        caminhos.append(pasta / ARQUIVO_FINAL)
        caminhos[-1].write_text(relatorio_final(final) + "\n", encoding="utf-8")
        caminhos.append(pasta / ARQUIVO_TRACE)
        caminhos[-1].write_text(
            json.dumps(trace_json(final), ensure_ascii=False, indent=1) + "\n", encoding="utf-8"
        )
    return caminhos


def main() -> int:
    participantes = formar_participantes()
    print("\n".join(tabela_de_participantes(participantes)))
    print()
    copa = disputar_copa(participantes)
    for caminho in escrever_relatorios(copa):
        print(f"escrito: {caminho.relative_to(RAIZ)}")
    for partida in _todas(copa):
        r = partida.auditado.duelo.result
        print(
            f"{partida.titulo}: "
            + (f"vence {r.winner_name} em {r.rounds} rodadas" if r else "INCONCLUSIVA")
            + f"; fidelidade {'ok' if all(ok for _, ok in partida.fidelidade) else 'DIVERGENTE'}"
        )
    if copa.campeao:
        print(f"Campeão: {copa.campeao.nome}")
    falhas = [p for p in _todas(copa) if not all(ok for _, ok in p.fidelidade + p.coerencia)]
    return 1 if falhas or copa.interrompida else 0


if __name__ == "__main__":
    raise SystemExit(main())
