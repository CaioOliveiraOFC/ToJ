"""A IA estratégica da Arena (Copa 03 v2) e a reprodução da Copa 03 com ela.

O que estes testes fixam:

1. as estimativas canônicas da IA batem com o motor: golpe, cura, cópia de
   combate e o gerador alinhado das simulações;
2. decisões, em estados montados de gladiadores reais da Copa 03:
   - golpe letal quando compensa;
   - cura quando sobreviver vale mais, e corrida quando a corrida é dela;
   - nada de cura com HP cheio, nem de buff já ativo ou com o alvo a um golpe;
   - status preparando a skill condicional, e a condicional depois;
   - nada de controle puro em alvo já controlado;
   - impasse entre builds de sustento quebrado;
3. o que a IA não pode saber: a visão igual dá decisão igual, o herói do
   adversário não é lido, a escolha do outro na mesma rodada não chega, e
   nenhuma ação ilegal sai;
4. a auditoria não vê as simulações, e a decisão é determinística;
5. a Copa 03 v2: a mesma chave e as mesmas seeds da publicada, a reprodução da
   original conferida, os confrontos controlados e as métricas de condução.
"""

from __future__ import annotations

import copy
import dataclasses
import json
import random

import pytest

from src.content.gladiator import Gladiator, prepare_gladiator
from src.mechanics import combat
from src.mechanics.pvp_duel import Duel, DuelAction, run_round
from src.shared import effect_core as core
from src.shared import effects as fx
from tools import arena_copa_03_ia as v2
from tools import arena_copa_03_ia_relatorios as r
from tools.arena_auditoria import disputar
from tools.arena_copa_02 import FASES
from tools.arena_copa_03 import PASTA, formar_participantes, semente_derivada
from tools.arena_copa_teste import PoliticaCopa, jogar_partida, semente_da_partida
from tools.arena_ia_estrategica import (
    DERROTA,
    VITORIA,
    GeradorAlinhado,
    IAEstrategica,
    Leitura,
    copia_de_combate,
    cura_esperada,
    golpe_esperado,
    para_simulacao,
    sinal_da_iniciativa,
    utilizavel,
)
from tools.arena_metricas_combate import metricas_da_partida

ENTREGUES = (PASTA / "gladiadores.json").exists()
pytestmark = pytest.mark.skipif(not ENTREGUES, reason="os 64 da Copa 03 não estão publicados")


@pytest.fixture(scope="module")
def ps():
    return {p.id: p for p in formar_participantes(PASTA)}


def _duelo(ps, eu, ele, *, hp_eu=None, hp_ele=None, efeitos_dele=(), buffs=None) -> Duel:
    a, b = prepare_gladiator(ps[eu].heroi), prepare_gladiator(ps[ele].heroi)
    duelo = Duel(a, b, rng=random.Random(1))
    if hp_eu is not None:
        duelo.hero("p1")._hp = int(hp_eu)
    if hp_ele is not None:
        duelo.hero("p2")._hp = int(hp_ele)
    for efeito, duracao in efeitos_dele:
        core.apply_effect(duelo.hero("p2"), efeito, source_id="teste", duration=duracao)
    duelo.hero("p1").active_buffs.update(buffs or {})
    return duelo


def _decidir(duelo: Duel, lado: str = "p1"):
    ia = IAEstrategica(duelo.hero(lado))
    acao = ia.choose(duelo.view(lado))
    return ia, acao


def _modelo_do_outro(ps, eu, ele):
    """O adversário como a IA o vê na primeira rodada, e a cópia do próprio herói."""
    duelo = _duelo(ps, eu, ele)
    ia, _ = _decidir(duelo)
    proprio = para_simulacao(duelo.hero("p1"))
    return proprio, ia._modelo.materializar(duelo.view("p1"), eu=proprio)


def _avaliacao(ia, rotulo: str) -> dict:
    return next(a for a in ia.last_decision["avaliacoes"] if a["acao"] == rotulo)


# --- 1. As estimativas batem com o motor ------------------------------------------


class _GeradorFixo:
    """Devolve, em ordem, os números pedidos: força acerto, erro e crítico."""

    def __init__(self, valores) -> None:
        self._valores = list(valores)

    def randrange(self, *_):
        return self._valores.pop(0)

    def random(self):
        return 0.0


@pytest.mark.parametrize(("eu", "ele", "carta"), [("W01", "W02", None), ("W01", "W02", "cutelada")])
def test_golpe_esperado_e_o_golpe_do_motor(ps, eu, ele, carta):
    for rolagens, campo in (([1, 100], "normal"), ([1, 1], "forte")):
        a = prepare_gladiator(ps[eu].heroi).hero
        b = prepare_gladiator(ps[ele].heroi).hero
        skill = next((s for s in a.skills.values() if s.id == carta), None)
        previsto = golpe_esperado(a, b, skill)
        base = combat.skill_damage_base(a, skill, b) if skill else combat.basic_attack_power(a)
        hp = b.get_hp()
        combat.resolve_physical_attack(
            a, b, base, rng=_GeradorFixo(rolagens + [100] * 8), skill=skill
        )
        assert hp - b.get_hp() == getattr(previsto, campo)


@pytest.mark.parametrize("gid", ["W05", "W08", "W23", "W64"])
def test_cura_esperada_e_a_cura_do_motor(ps, gid):
    heroi = prepare_gladiator(ps[gid].heroi).hero
    cura = next(s for s in heroi.skills.values() if s.effect_type == "heal")
    heroi._hp = 1
    heroi.skill_cooldowns.clear()
    resultado = combat.apply_skill(heroi, heroi, cura, rng=random.Random(1))
    assert resultado.heal_amount == cura_esperada(heroi, cura)


def test_a_copia_de_combate_joga_igual_ao_deepcopy(ps):
    a = prepare_gladiator(ps["W42"].heroi).hero
    b = prepare_gladiator(ps["W08"].heroi).hero
    core.apply_effect(b, "bleed", source_id="t", duration=2)
    a.active_buffs["teste"] = {"stat": "st", "value": 50, "duration": 2}
    raiz_a, raiz_b = para_simulacao(a), para_simulacao(b)
    resultados = []
    for copiar in (copia_de_combate, copy.deepcopy):
        x, y = copiar(raiz_a), copiar(raiz_b)
        duelo = Duel(Gladiator(x), Gladiator(y), rng=random.Random(7))
        controles = {"p1": PoliticaCopa(x), "p2": PoliticaCopa(y)}
        for _ in range(12):
            if not duelo.finished:
                run_round(duelo, controles)
        resultados.append([(r.actions, r.steps, r.hp_end, r.mp_end) for r in duelo.history])
    assert resultados[0] == resultados[1]
    # E a raiz não foi tocada pelas cópias.
    assert raiz_a.active_buffs["teste"]["duration"] == 2
    assert [i.duration for i in core.instances(raiz_b)] == [2]


def test_o_gerador_alinhado_separa_por_origem():
    lados = {}
    primeiro, segundo = GeradorAlinhado(42, lados), GeradorAlinhado(42, lados)

    def resolve_physical_attack(r, attacker):
        return r.randrange(1, 101)

    def try_apply_status(r, target):
        return r.randrange(1, 101)

    # Um sorteio de status no meio não desloca o do golpe: cada origem tem fluxo.
    golpe = resolve_physical_attack(primeiro, None)
    try_apply_status(segundo, None)
    assert resolve_physical_attack(segundo, None) == golpe
    with pytest.raises(AttributeError):
        primeiro.choice([1, 2])


def test_perder_e_sempre_o_pior_valor():
    longa = Leitura(0.0, 10_000.0)
    for impasse in (0.0, 0.5, 1.0):
        assert DERROTA.utilidade(impasse) <= longa.utilidade(impasse)
        assert VITORIA.utilidade(impasse) == 1.0
        assert Leitura(0.9, 3.0).utilidade(impasse) > Leitura(0.9, 12.0).utilidade(impasse)


# --- 2. Decisões ------------------------------------------------------------------


def test_usa_o_golpe_letal_quando_compensa(ps):
    eu, outro = _modelo_do_outro(ps, "W01", "W02")
    basico = golpe_esperado(eu, outro)
    letal = min(
        golpe_esperado(eu, outro, s).normal for s in eu.skills.values() if s.effect_type == "damage"
    )
    assert basico.forte < letal
    # Nem o crítico do básico derruba; qualquer acerto das skills de dano derruba.
    ia, acao = _decidir(_duelo(ps, "W01", "W02", hp_ele=(basico.forte + letal) // 2))
    assert acao.kind == "skill" and ia._deck[acao.skill_id].effect_type == "damage"
    assert _avaliacao(ia, ia.last_decision["acao"])["chance_letal"] >= 0.8
    assert _avaliacao(ia, "ataque básico")["chance_letal"] == 0


@pytest.mark.parametrize(("eu", "ele"), [("W44", "W61"), ("W23", "W09"), ("W05", "W09")])
def test_cura_quando_sobreviver_vale_mais(ps, eu, ele):
    proprio, outro = _modelo_do_outro(ps, eu, ele)
    assert sinal_da_iniciativa(proprio, outro) == 1
    golpe = golpe_esperado(outro, proprio)
    duelo = _duelo(ps, eu, ele, hp_eu=golpe.normal * 0.7)
    duelo.hero("p2")._hp = int(duelo.hero("p2").base_hp * 0.6)
    ia, acao = _decidir(duelo)
    # Ajo antes dele, o próximo golpe me derruba, e a corrida não é minha: curar.
    assert ia._deck[acao.skill_id].effect_type == "heal"
    melhor_outra = max(
        a["utilidade"]
        for a in ia.last_decision["avaliacoes"]
        if a["acao"] != ia.last_decision["acao"]
    )
    assert _avaliacao(ia, ia.last_decision["acao"])["utilidade"] > melhor_outra + 0.05


@pytest.mark.parametrize(("eu", "ele"), [("W44", "W61"), ("W23", "W09"), ("W05", "W09")])
def test_corre_em_vez_de_curar_quando_o_golpe_dela_chega_antes(ps, eu, ele):
    proprio, outro = _modelo_do_outro(ps, eu, ele)
    golpe = golpe_esperado(outro, proprio)
    # O golpe medido com o alvo já baixo: bônus de "alvo saudável" não vale ali.
    outro._hp = int(outro.base_hp * 0.1)
    melhor = max(
        golpe_esperado(proprio, outro, s).normal
        for s in proprio.skills.values()
        if s.effect_type == "damage" and utilizavel(proprio, s)
    )
    duelo = _duelo(ps, eu, ele, hp_eu=golpe.normal * 0.7, hp_ele=melhor * 0.9)
    ia, acao = _decidir(duelo)
    # O mesmo HP baixo, mas agora ela age primeiro e o golpe dela derruba: não é
    # regra "HP baixo cura".
    assert acao.kind == "attack" or ia._deck[acao.skill_id].effect_type == "damage"
    assert _avaliacao(ia, ia.last_decision["acao"])["chance_letal"] > 0


@pytest.mark.parametrize(
    ("eu", "ele"), [("W44", "W61"), ("W23", "W09"), ("W05", "W09"), ("W08", "W19")]
)
def test_nao_cura_com_hp_cheio_agindo_primeiro(ps, eu, ele):
    proprio, outro = _modelo_do_outro(ps, eu, ele)
    assert sinal_da_iniciativa(proprio, outro) == 1
    ia, acao = _decidir(_duelo(ps, eu, ele))
    assert acao.kind != "skill" or ia._deck[acao.skill_id].effect_type != "heal"


def test_nao_relanca_buff_ativo(ps):
    heroi = prepare_gladiator(ps["W01"].heroi).hero
    valor = fx.buff_value(heroi, "st", 35)
    buffs = {"Grito de Guerra": {"stat": "st", "value": valor, "duration": 3}}
    ia, acao = _decidir(_duelo(ps, "W01", "W02", buffs=buffs))
    assert acao.skill_id != "grito_guerra"


def test_nao_lanca_buff_com_o_alvo_a_um_golpe(ps):
    eu, outro = _modelo_do_outro(ps, "W04", "W02")
    ia, acao = _decidir(_duelo(ps, "W04", "W02", hp_ele=golpe_esperado(eu, outro).normal * 0.8))
    assert acao.kind == "attack" or ia._deck[acao.skill_id].effect_type == "damage"


def test_prepara_o_status_e_depois_bate_com_a_condicional(ps):
    # Encarar deixa o alvo vulnerável (defesa −20%) e "afetado": o Golpe Duplo
    # ganha +55% contra alvo afetado.
    limpo, acao = _decidir(_duelo(ps, "W12", "W57"))
    assert acao.skill_id == "n_encarar"
    afetado, acao = _decidir(_duelo(ps, "W12", "W57", efeitos_dele=[("vulnerable", 3)]))
    # Com o alvo já afetado, não reaplica: bate. E a condicional passou a valer mais.
    assert acao.skill_id != "n_encarar" and afetado._deck[acao.skill_id].effect_type == "damage"
    antes = _avaliacao(limpo, "Golpe Duplo")["p"]
    depois = _avaliacao(afetado, "Golpe Duplo")["p"]
    assert depois > antes + 0.05


def test_nao_gasta_controle_puro_em_alvo_ja_controlado(ps):
    # O Gancho e Corda de verdade traz um secundário (vulnerável) que vale a
    # pena mesmo com o alvo atordoado; aqui ele é só controle.
    duelo = _duelo(ps, "W42", "W61", efeitos_dele=[("stun", 1)])
    heroi = duelo.hero("p1")
    heroi.skills = {
        k: dataclasses.replace(s, secondary=None) if s.id == "n_gancho_e_corda" else s
        for k, s in heroi.skills.items()
    }
    proprio, outro = para_simulacao(heroi), prepare_gladiator(ps["W61"].heroi).hero
    assert sinal_da_iniciativa(proprio, outro) == 1
    ia, acao = _decidir(duelo)
    assert acao.skill_id != "n_gancho_e_corda"


def test_quebra_o_impasse_entre_builds_de_sustento(ps):
    # Espelho de W05: a cura por MP rende quatro vezes o dano por MP, e com a
    # política de cura dos dois lados a luta não sai do lugar.
    a, b = prepare_gladiator(ps["W05"].heroi), prepare_gladiator(ps["W05"].heroi)
    b.hero.nick_name += "'"
    ias = []

    def fabrica(heroi):
        ias.append(IAEstrategica(heroi))
        return ias[-1]

    resultado = disputar(a, b, 6539252711803490829, fabrica, auditar=False, limite=300)
    assert resultado.duelo.finished and resultado.duelo.result.rounds < 300
    impasses = [d["modelo"]["impasse"] for d in ias[0].decisoes]
    assert impasses[0] == 0 and max(impasses) >= 0.5


def test_o_impasse_cresce_com_a_luta_parada_e_zera_com_progresso(ps):
    duelo = _duelo(ps, "W05", "W09")
    ia = IAEstrategica(duelo.hero("p1"))
    vista = duelo.view("p1")
    medidas = [
        ia._medir_impasse(dataclasses.replace(vista, round_number=r)) for r in (1, 21, 31, 41)
    ]
    assert medidas == [0.0, 0.0, 0.5, 1.0]
    ferido = dataclasses.replace(
        vista,
        round_number=42,
        opponent=dataclasses.replace(vista.opponent, hp=vista.opponent.hp_max // 2),
    )
    assert ia._medir_impasse(ferido) == 0.0
    # E numa luta longa a urgência vem da própria rodada, mesmo com progresso.
    assert ia._medir_impasse(dataclasses.replace(ferido, round_number=120)) == 1.0


# --- 3. O que a IA não pode saber ---------------------------------------------------


def test_visao_igual_da_decisao_igual_com_adversario_oculto_diferente(ps):
    normal = _duelo(ps, "W01", "W02")
    mexido = _duelo(ps, "W01", "W02")
    outro = mexido.hero("p2")
    # Atributos, deck e passivas que a tela não mostra.
    outro._add_bonus("st", 400)
    outro._add_bonus("df", -200)
    outro.skills = {1: next(iter(ps["W42"].heroi.skills.values()))}
    outro.passives = []
    assert normal.view("p1") == mexido.view("p1")
    a, _ = _decidir(normal)
    b, _ = _decidir(mexido)
    assert a.last_decision == b.last_decision


class _Espiao:
    """Um herói que anota cada atributo que alguém lê dele."""

    def __init__(self, alvo) -> None:
        object.__setattr__(self, "_alvo", alvo)
        object.__setattr__(self, "lidos", [])

    def __getattr__(self, nome):
        object.__getattribute__(self, "lidos").append(nome)
        return getattr(object.__getattribute__(self, "_alvo"), nome)

    def __setattr__(self, nome, valor):
        setattr(object.__getattribute__(self, "_alvo"), nome, valor)


def test_a_escolha_nao_le_o_heroi_do_adversario(ps):
    espiao = _Espiao(prepare_gladiator(ps["W02"].heroi).hero)
    duelo = Duel(prepare_gladiator(ps["W01"].heroi), Gladiator(espiao), rng=random.Random(1))
    ia = IAEstrategica(duelo.hero("p1"))
    for _ in range(4):
        vista = duelo.view("p1")
        espiao.lidos.clear()
        acao = ia.choose(vista)
        assert espiao.lidos == []
        duelo.play_round({"p1": acao, "p2": DuelAction.attack()})


def test_a_escolha_do_outro_na_mesma_rodada_nao_chega(ps):
    primeiras = []
    for acao_dele in (DuelAction.attack(), DuelAction.use_skill("investida")):
        duelo = _duelo(ps, "W01", "W02")
        ia = IAEstrategica(duelo.hero("p2"))

        class Fixo:
            def choose(self, view, acao=acao_dele):
                return acao

        run_round(duelo, {"p1": Fixo(), "p2": ia})
        primeiras.append(ia.decisoes[0])
    assert primeiras[0] == primeiras[1]


def test_nunca_escolhe_acao_ilegal_nem_rendicao(ps):
    sorteio = random.Random(5)
    ids = sorted(ps)
    for _ in range(10):
        eu, ele = sorteio.sample(ids, 2)
        duelo = _duelo(ps, eu, ele)
        a, b = duelo.hero("p1"), duelo.hero("p2")
        a._hp = max(1, int(a.base_hp * sorteio.random()))
        b._hp = max(1, int(b.base_hp * sorteio.random()))
        a._mp = int(a.base_mp * sorteio.random())
        for skill in a.skills.values():
            a.skill_cooldowns[skill.id] = sorteio.choice([0, 0, 1, 2, 3])
        if sorteio.random() < 0.5:
            core.apply_effect(b, sorteio.choice(["stun", "bleed", "slowed", "fear"]), source_id="t")
        vista = duelo.view("p1")
        acao = IAEstrategica(a).choose(vista)
        assert acao in vista.legal_actions and acao.kind != "surrender"


# --- 4. Auditoria e determinismo ------------------------------------------------------


@pytest.fixture(scope="module")
def partida_ia(ps):
    return jogar_partida("fase64", 1, ps["W03"], ps["W40"], controlador=IAEstrategica)


def test_a_auditoria_continua_fiel_e_nao_ve_a_simulacao(partida_ia):
    assert all(ok for _, ok in partida_ia.fidelidade + partida_ia.coerencia)
    escolhas = partida_ia.auditado.trace.de("escolha")
    assert len(escolhas) == 2 * partida_ia.auditado.duelo.result.rounds
    assert all(e["legal"] for e in escolhas)
    executados = sum(
        1
        for r in partida_ia.auditado.duelo.history
        for s in r.steps
        if s.outcome == "executed" and (s.action.kind == "attack" or s.action.skill_id)
    )
    # Cada golpe do trace é de uma ação de verdade; os simulados não aparecem.
    assert len(partida_ia.auditado.trace.de("golpe_fim")) <= executados


def test_a_mesma_visao_da_a_mesma_decisao(ps):
    decisoes = [_decidir(_duelo(ps, "W34", "W02"))[0].last_decision for _ in range(2)]
    assert decisoes[0] == decisoes[1]


# --- 5. A Copa 03 v2 ---------------------------------------------------------------------


@pytest.fixture(scope="module")
def publicados():
    return v2.dados_publicados()


def test_a_v2_usa_a_chave_e_as_seeds_publicadas(ps, publicados):
    participantes = list(ps.values())
    chave = v2.sortear_chave([p.id for p in participantes], semente_derivada("chave"))
    assert chave == publicados["chave"]
    fase, quantas, nome = FASES[0]
    tarefas = v2.tarefas_da_fase(fase, quantas, nome, [ps[i] for i in chave], "ia")
    jogos = {j["chave"]: j for j in publicados["partidas"]}
    for f, i, a, b, _, controlador in tarefas:
        jogo = jogos[f"{f}-{i}"]
        assert (a, b, controlador) == (jogo["p1"], jogo["p2"], "ia")
        assert str(semente_da_partida(f, i, v2.SEMENTE_PRINCIPAL)) == jogo["seed"]


def test_a_copa_original_e_reproduzida_bit_a_bit(ps, publicados):
    copa, _ = v2.disputar_copa(list(ps.values()), "politica_copa", processos=2)
    verificacoes = v2.conferir_reproducao(copa, publicados)
    assert all(ok for _, ok in verificacoes), verificacoes


def test_os_confrontos_controlados_alternam_lado_seed_e_controlador(ps):
    tarefas = v2.tarefas_controladas(list(ps.values()))
    espelhos = [t for t in tarefas if t[0] == "espelho"]
    cruzados = [t for t in tarefas if t[0] == "cruzado"]
    assert len(espelhos) == 64 * 2 * v2.SEEDS_POR_LADO
    assert len(cruzados) == 32 * 2 * 2 * v2.SEEDS_POR_LADO
    assert len({t[-1] for t in tarefas}) == len(tarefas)
    assert all(t[1] == t[2] for t in espelhos)
    pares = {(t[1], t[2]) for t in cruzados}
    for a, b in pares:
        vistos = {(t[3], t[4]) for t in cruzados if (t[1], t[2]) == (a, b)}
        assert vistos == {("A", "p1"), ("A", "p2"), ("B", "p1"), ("B", "p2")}


def test_um_confronto_controlado_registra_metricas_dos_dois_lados(ps):
    tarefa = v2.tarefas_controladas(list(ps.values()))[0]
    r = v2._duelo_controlado(tarefa)
    assert r["vencedor"] in ("p1", "p2") and r["decisoes"] == r["rodadas"]
    for lado in ("p1", "p2"):
        m = r["metricas"][lado]
        assert m["basicos"] + m["skills"] == m["rodadas"] == r["rodadas"]


def test_as_metricas_de_conducao_fecham_as_contas(ps, partida_ia):
    herois = {pid: p.heroi for pid, p in ps.items()}
    rodadas = partida_ia.auditado.duelo.result.rounds
    for m in metricas_da_partida(partida_ia, herois).values():
        assert m["rodadas"] == rodadas
        assert m["basicos"] + m["skills"] == rodadas
        assert sum(m["basicos_por_motivo"].values()) == m["basicos"]
        assert sum(m["motivo_da_maior_sequencia"].values()) == m["max_basicos_seguidos"]
        assert m["mp_regenerado"] >= 0 and m["mp_gasto"] <= m["mp_inicial"] + m["mp_regenerado"]
        assert 0 <= m["cura_excedente"] <= m["cura_lancada"]


# --- 6. Os entregáveis publicados ---------------------------------------------------------

PUBLICADA = (v2.PASTA_IA / "final_trace.json").exists()
publicada = pytest.mark.skipif(not PUBLICADA, reason="a Copa 03 v2 não foi publicada")


@publicada
def test_os_entregaveis_da_v2_estao_completos_e_coerentes():
    pasta = v2.PASTA_IA
    for nome in (
        "relatorio.md",
        "decisoes.md",
        "final_detalhada.md",
        "final_trace.json",
        "dashboard.html",
        "relatorio_visual.pdf",
        "confrontos.json",
    ):
        assert (pasta / nome).exists(), nome
    trace = json.loads((pasta / "final_trace.json").read_text(encoding="utf-8"))
    assert trace["copa"] == v2.COPA_IA and trace["fase"] == "final"
    assert all(x["ok"] for x in trace["fidelidade"] + trace["coerencia"])
    assert trace["decisoes_ia"]["p1"] and trace["decisoes_ia"]["p2"]
    assert "@@" not in (pasta / "dashboard.html").read_text(encoding="utf-8")
    relatorio = (pasta / "relatorio.md").read_text(encoding="utf-8")
    for secao in ("## A comparação obrigatória", "## Três lutas em detalhe", "## Limitações"):
        assert secao in relatorio
    assert relatorio.count("### ") >= 3
    confrontos = json.loads((pasta / "confrontos.json").read_text(encoding="utf-8"))
    assert len(confrontos["confrontos"]) == 64 * 2 * 2 + 32 * 2 * 2 * 2


@publicada
def test_a_v2_publicada_e_dos_mesmos_64(ps):
    trace = json.loads((v2.PASTA_IA / "final_trace.json").read_text(encoding="utf-8"))
    for lado in ("p1", "p2"):
        info = trace["lados"][lado]
        assert info["id"] in ps and info["nome"] == ps[info["id"]].nome
        assert info["overall_power"] == ps[info["id"]].poder


def test_o_basico_com_carta_na_mao_tem_motivo():
    decisao = {
        "avaliacoes": [
            {"acao": "ataque básico", "utilidade": 0.501},
            {"acao": "Investida", "utilidade": 0.5005},
        ]
    }
    assert r._por_que_basico(decisao, [], set()) == "empate"
    decisao["avaliacoes"][1]["utilidade"] = 0.45
    assert r._por_que_basico(decisao, [{"acao": "Tomar Fôlego"}], {"Tomar Fôlego"}) == "cura"
    assert r._por_que_basico(decisao, [], {"Tomar Fôlego"}) == "preferencia"
