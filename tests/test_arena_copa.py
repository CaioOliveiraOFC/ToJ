"""Copa Arena de Testes: formação, chave, isolamento e fidelidade da auditoria.

A Copa é um experimento de diagnóstico (`tools/arena_copa_teste.py`). O que estes
testes fixam é que ela é honesta:

1. os oito bonecos são builds que o catálogo real permite, e o poder medido é o
   canônico;
2. a chave e as seeds são reproduzíveis, e o vencedor de cada confronto é quem
   avança;
3. nenhum boneco toca save, slot ou a lista de gladiadores, e nada atravessa de
   uma partida para outra;
4. a auditoria observa sem mudar: o duelo auditado é idêntico ao duelo sem
   instrumentação, o gerador não sorteia nada a mais e cada número do trace bate
   com o motor.
"""

from __future__ import annotations

import hashlib
import math
import random
from dataclasses import replace
from pathlib import Path

import pytest

from src.content.gladiator import prepare_gladiator
from src.engine import arena_setup
from src.mechanics import combat, pvp_duel
from src.mechanics.pvp_duel import SIDES
from src.shared import effect_core
from src.sim.arena import limpar_cache, overall_power
from src.storage import save_manager
from tools.arena_auditoria import (
    AuditoriaDivergenteError,
    RngGravado,
    Trace,
    foto,
    interceptar,
)
from tools.arena_copa_teste import (
    DISTRIBUICAO,
    ESPECIFICACOES,
    FAIXA_DE_PODER,
    LIMITE_TECNICO,
    SEMENTE_PRINCIPAL,
    BuildIlegitimaError,
    PoliticaCopa,
    construir,
    disputar_copa,
    escrever_relatorios,
    formar_participantes,
    jogar_partida,
    semente_da_partida,
    sortear_chave,
)


@pytest.fixture(scope="module")
def participantes():
    return formar_participantes(medir=False)


@pytest.fixture(scope="module")
def copa(participantes):
    return disputar_copa(participantes)


@pytest.fixture(scope="module")
def partida_com_skill(participantes):
    """Geada × Peçonha: status, DoT, procs de passiva e golpes de skill."""
    por_nome = {p.nome: p for p in participantes}
    return jogar_partida("teste", 1, por_nome["Geada"], por_nome["Peçonha"])


# --- 1. Formação -----------------------------------------------------------


def test_oito_participantes_distintos_na_distribuicao_pedida(participantes):
    assert len(participantes) == 8
    contagem = {}
    for p in participantes:
        contagem[p.espec.classe] = contagem.get(p.espec.classe, 0) + 1
    assert contagem == DISTRIBUICAO
    assert len({p.id for p in participantes}) == 8
    assert len({p.nome for p in participantes}) == 8
    assert len({(p.espec.deck, p.espec.passivas) for p in participantes}) == 8


def test_build_fora_do_catalogo_e_recusada():
    """Carta acima do nível da oferta não entra: a Copa não inventa build."""
    muralha = ESPECIFICACOES[0]
    # Baluarte exige nível 6 e não pode ser a carta da oferta do nível 3.
    precoce = replace(muralha, deck=("golpe_poderoso", "baluarte", "couraca_improvisada"))
    with pytest.raises(BuildIlegitimaError, match="baluarte exige nível 6"):
        construir(precoce)
    de_outra_classe = replace(muralha, deck=("golpe_poderoso", "couraca_improvisada", "bola_fogo"))
    with pytest.raises(BuildIlegitimaError, match="bola_fogo"):
        construir(de_outra_classe)


@pytest.mark.parametrize("nome", ["Muralha", "Navalha"])
def test_poder_medido_fica_na_faixa(nome):
    """Os dois extremos medidos da Copa, pelo `overall_power` canônico e sem cache."""
    limpar_cache()
    espec = next(e for e in ESPECIFICACOES if e.nome == nome)
    poder = overall_power(construir(espec), usar_cache=False).nivel_equivalente
    assert FAIXA_DE_PODER[0] <= poder <= FAIXA_DE_PODER[1]


# --- 2. Chave e seeds ------------------------------------------------------


def test_chave_e_permutacao_reproduzivel(participantes):
    ids = [p.id for p in participantes]
    chave = sortear_chave(ids)
    assert sorted(chave) == sorted(ids)
    assert chave == sortear_chave(ids)
    assert chave == sortear_chave(ids, SEMENTE_PRINCIPAL)


def test_seed_da_partida_e_estavel_e_unica_por_posicao():
    sementes = {
        (fase, i): semente_da_partida(fase, i)
        for fase, n in (("quartas", 4), ("semifinal", 2), ("final", 1))
        for i in range(1, n + 1)
    }
    assert len(set(sementes.values())) == 7
    esperada = int.from_bytes(hashlib.sha256(b"20261023:final:1").digest()[:8], "big")
    assert sementes[("final", 1)] == esperada


def test_vencedor_avanca(copa):
    quartas, semis, final = (copa.fases[f] for f in ("quartas", "semifinal", "final"))
    assert copa.interrompida is None
    assert [p.lados[s] for p in semis for s in SIDES] == [p.vencedor for p in quartas]
    assert [final[0].lados[s] for s in SIDES] == [p.vencedor for p in semis]
    assert copa.campeao is final[0].vencedor
    for partida in quartas + semis + final:
        assert partida.vencedor in partida.lados.values()
        assert partida.vencedor is not partida.perdedor
        assert not partida.inconclusiva
        assert len(partida.auditado.duelo.history) < LIMITE_TECNICO


def test_mesma_partida_mesmo_resultado(participantes):
    a = jogar_partida("final", 1, participantes[0], participantes[1])
    b = jogar_partida("final", 1, participantes[0], participantes[1])
    assert a.auditado.duelo.history == b.auditado.duelo.history
    assert a.auditado.trace.records == b.auditado.trace.records


# --- 3. Isolamento ---------------------------------------------------------


def test_cada_partida_comeca_de_recursos_cheios_e_estado_limpo(copa):
    for fase in copa.fases.values():
        for partida in fase:
            inicio = partida.auditado.trace.de("rodada_inicio")[0]["estado"]
            for lado in SIDES:
                f = inicio[lado]
                assert f["hp"] == f["hp_max"] and f["mp"] == f["mp_max"]
                assert f["recargas"] == {} and f["buffs"] == {} and f["efeitos"] == []
                assert f["death_ignore_usado"] is False


def test_o_boneco_original_nunca_luta(participantes, copa):
    for p in participantes:
        estado = foto(p.heroi)
        assert estado == foto(prepare_gladiator(p.heroi).hero)
        assert estado["hp"] == estado["hp_max"] and estado["mp"] == estado["mp_max"]


def _impressao(pasta: Path) -> dict:
    if not pasta.exists():
        return {}
    return {
        str(arq.relative_to(pasta)): hashlib.sha256(arq.read_bytes()).hexdigest()
        for arq in sorted(pasta.rglob("*"))
        if arq.is_file()
    }


def test_nenhum_save_slot_ou_gladiador_e_tocado(monkeypatch, tmp_path):
    reais = Path(save_manager.__file__).resolve().parents[2] / "saves"
    antes = _impressao(reais)
    saves = tmp_path / "saves"
    saves.mkdir()
    monkeypatch.setattr(save_manager, "SAVE_DIR", str(saves))

    copa = disputar_copa(formar_participantes(medir=False))
    escrever_relatorios(copa, tmp_path / "relatorios")

    assert list(saves.iterdir()) == []
    assert arena_setup.list_gladiators() == []
    assert _impressao(reais) == antes


# --- 4. Auditoria ----------------------------------------------------------


def test_auditoria_nao_muda_o_duelo(copa, partida_com_skill):
    for fase in copa.fases.values():
        for partida in fase:
            assert all(ok for _, ok in partida.fidelidade), partida.fidelidade
            assert all(ok for _, ok in partida.coerencia), partida.coerencia
    assert all(ok for _, ok in partida_com_skill.fidelidade)
    assert all(ok for _, ok in partida_com_skill.coerencia)


def test_proxy_do_gerador_nao_altera_a_sequencia():
    trace = Trace()
    gravado = RngGravado(1234, trace)
    puro = random.Random(1234)
    for _ in range(50):
        assert gravado.randrange(1, 101) == puro.randrange(1, 101)
        assert gravado.random() == puro.random()
    assert gravado.chamadas == 100
    assert gravado.getstate() == puro.getstate()
    with pytest.raises(AttributeError):
        gravado.choice([1, 2])


def test_todo_sorteio_do_duelo_e_capturado(partida_com_skill):
    trace = partida_com_skill.auditado.trace
    rolagens = trace.de("rolagem")
    assert len(rolagens) == partida_com_skill.auditado.rng.chamadas
    assert [r["chamada"] for r in rolagens] == list(range(1, len(rolagens) + 1))
    mecanicas = {r["mecanica"].split(" (")[0] for r in rolagens}
    assert {"acerto", "crítico", "aplicação de status"} <= mecanicas
    assert partida_com_skill.puro.rng.getstate() == partida_com_skill.auditado.rng.getstate()


def test_golpe_interno_de_skill_sem_publish_e_observado(partida_com_skill):
    """`apply_skill` resolve o golpe com `publish=None`; a auditoria vê assim mesmo."""
    internos = [
        g for g in partida_com_skill.auditado.trace.de("golpe_inicio") if g["skill"] is not None
    ]
    assert internos
    assert all(g["publish_ligado"] is False for g in internos)


def test_interceptacao_e_desfeita_mesmo_com_erro():
    originais = (
        combat.resolve_physical_attack,
        combat.apply_skill,
        combat.try_apply_status,
        effect_core.tick_effects,
        pvp_duel.read_initiative,
    )
    with pytest.raises(RuntimeError), interceptar(Trace()):
        assert combat.resolve_physical_attack is not originais[0]
        raise RuntimeError("falha no meio")
    assert (
        combat.resolve_physical_attack,
        combat.apply_skill,
        combat.try_apply_status,
        effect_core.tick_effects,
        pvp_duel.read_initiative,
    ) == originais


def test_recalculo_divergente_derruba_a_auditoria(monkeypatch, participantes):
    """Se o motor devolver outro número, a auditoria falha em vez de publicar."""
    original = combat._calculate_damage
    monkeypatch.setattr(combat, "_calculate_damage", lambda *a, **k: original(*a, **k) + 1)
    with pytest.raises(AuditoriaDivergenteError):
        jogar_partida("teste", 2, participantes[1], participantes[6])


def test_numeros_do_trace_batem_com_o_motor(partida_com_skill):
    trace = partida_com_skill.auditado.trace
    por_golpe = {}
    for r in trace.records:
        if r["golpe"] is not None:
            por_golpe.setdefault(r["golpe"], {})[r["kind"]] = r
    conectados = 0
    for golpe in por_golpe.values():
        fim = golpe["golpe_fim"]
        if fim["resultado"]["was_evaded"]:
            continue
        conectados += 1
        mods, funil = golpe["modificadores"], golpe["funil"]
        dano = combat._calculate_damage(
            funil["base"],
            [m["parcela"] for m in mods["mult"]],
            [x["fator"] for x in mods["xmult"]],
            funil["defesa_alvo"],
            [m["fator"] for m in mods["mitigacao"]],
        )
        assert dano == funil["final"]
        egide = golpe.get("egide")
        assert fim["resultado"]["damage"] == (egide["dano_saida"] if egide else funil["final"])
    assert conectados

    leituras = trace.de("iniciativa")
    for x in leituras:
        raizes = [math.sqrt(p["valor"] / p["ref"]) for p in x["parcelas"]]
        assert math.fsum(raizes) / 6 == x["build"]
        assert x["build"] * x["modificador"] == x["score"]
    for ordem in trace.de("ordem"):
        a, b = ordem["score"]["p1"], ordem["score"]["p2"]
        if a != b:
            assert ordem["primeiro"] == ("p1" if a > b else "p2")


def test_politica_le_so_a_visao(participantes):
    """A mesma visão dá sempre a mesma ação, sem consultar o herói ao vivo."""
    heroi = prepare_gladiator(participantes[0].heroi).hero
    duelo = pvp_duel.Duel(
        prepare_gladiator(participantes[0].heroi),
        prepare_gladiator(participantes[1].heroi),
        rng=random.Random(1),
    )
    visao = duelo.view("p1")
    politica = PoliticaCopa(heroi)
    primeira = politica.choose(visao)
    heroi._hp = 1  # o herói da política não é lido: só a visão
    assert politica.choose(visao) == primeira
    assert primeira in visao.legal_actions
    assert politica.last_reason
