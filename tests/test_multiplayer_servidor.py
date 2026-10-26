"""Servidor autoritativo, resultados canônicos e replay (contrato multiplayer, §3, §5, §6).

- O cliente só manda ação e comando de sessão; não há campo para impor HP, dano,
  atributo, equipamento, recarga, resultado ou MMR.
- O servidor valida a legalidade e roda o motor canônico: uma partida pelo
  servidor é o MESMO duelo que `Duel.play_round` daria com a mesma semente e as
  mesmas ações — a final publicada da Copa 03, rejogada pela rede, chega aos
  mesmos HP, MP e resultado em todas as 37 rodadas.
- Os snapshots publicados não mudam.
- O replay é determinístico, inclusive em outro processo, e só roda na versão em
  que a partida nasceu.
"""

from __future__ import annotations

import json
import os
import random
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.arena_setup import gladiator_from_snapshot  # noqa: E402
from src.mechanics.pvp_duel import Duel  # noqa: E402
from src.multiplayer import protocolo  # noqa: E402
from src.multiplayer.servidor import (  # noqa: E402
    CONCLUIDA,
    PartidaIncompativelError,
    reproduzir,
)
from src.multiplayer.transporte import RedeLocal  # noqa: E402
from tests._multiplayer_apoio import (  # noqa: E402
    COPA_03,
    ROOT,
    SEMENTE_DA_FINAL,
    SNAPSHOTS,
    Ataca,
    PrimeiraSkill,
    Roteiro,
    acervo,
    acoes_da_final,
    cliente,
    conta_id,
    em_fila,
    entrar,
    registro,
    resultado_da_final,
    rodadas_da_final,
    servidor,
    sha256_do_arquivo,
)


def _duelo_pela_rede(controlador_1, controlador_2, gladiadores=("W23", "W64")):
    srv = servidor(registro(ana=gladiadores[0], bia=gladiadores[1]))
    rede = RedeLocal(srv)
    ana, bia = cliente("ana", controlador_1), cliente("bia", controlador_2)
    em_fila(rede, "c1", ana, gladiadores[0])
    em_fila(rede, "c2", bia, gladiadores[1])
    return srv, rede, ana, bia


def _estado(partida) -> tuple:
    duelo = partida.duelo
    return (
        duelo.round_number,
        duelo.history,
        tuple(sorted(partida.pendentes.items())),
        tuple(duelo.hero(lado).get_hp() for lado in ("p1", "p2")),
        tuple(duelo.hero(lado).get_mp() for lado in ("p1", "p2")),
    )


def _parado_na_rodada_1():
    srv, rede, ana, bia = _duelo_pela_rede(None, None)
    return srv, rede, ana, bia, srv.partida(ana.partida)


# --- o cliente não impõe nada ---------------------------------------------------------


@pytest.mark.parametrize(
    "campo, valor",
    [
        ("hp", 99999),
        ("dano", 5000),
        ("atributos", {"ST": 999}),
        ("equipamento", {"Weapon1": "Lâmina Lendária"}),
        ("recarga", {}),
        ("resultado", "vitoria"),
        ("mmr", 3000),
    ],
)
def test_mensagem_de_acao_com_campo_imposto_e_recusada_inteira(campo, valor):
    srv, rede, ana, _, partida = _parado_na_rodada_1()
    antes = _estado(partida)
    texto = json.dumps(
        {
            "tipo": "acao",
            "partida": partida.id,
            "rodada": 1,
            "acao": {"kind": "attack", "skill_id": None},
            campo: valor,
        }
    )
    rede.enviar("c1", texto)
    assert ana.recusas[-1]["motivo"] == "campos_invalidos"
    assert _estado(partida) == antes


@pytest.mark.parametrize(
    "acao",
    [
        {"kind": "attack", "skill_id": None, "damage": 9999},
        {"kind": "attack", "critico": True},
        {"kind": "heal"},
        {"kind": "potion"},
        {"kind": "flee"},
        {"kind": "attack", "skill_id": "investida"},
    ],
)
def test_acao_fora_do_vocabulario_e_recusada(acao):
    srv, rede, ana, _, partida = _parado_na_rodada_1()
    antes = _estado(partida)
    rede.enviar(
        "c1", json.dumps({"tipo": "acao", "partida": partida.id, "rodada": 1, "acao": acao})
    )
    assert ana.recusas[-1]["motivo"] == "acao_invalida"
    assert _estado(partida) == antes


@pytest.mark.parametrize("tipo", ["resultado", "definir_mmr", "equipar", "atualizar_hp"])
def test_o_cliente_nao_tem_mensagem_para_impor_estado(tipo):
    srv, rede, ana, _, partida = _parado_na_rodada_1()
    antes = _estado(partida)
    rede.enviar("c1", json.dumps({"tipo": tipo}))
    assert ana.recusas[-1]["motivo"] == "tipo_desconhecido"
    assert _estado(partida) == antes
    assert srv.resultados.todos() == ()


def test_acao_ilegal_e_recusada_sem_mudar_nada():
    srv, rede, ana, bia, partida = _parado_na_rodada_1()
    antes = _estado(partida)
    fora_do_deck = protocolo.codificar(
        "acao",
        partida=partida.id,
        rodada=1,
        acao={"kind": "skill", "skill_id": "carta_que_nao_esta_no_deck"},
    )
    rede.enviar("c1", fora_do_deck)
    assert ana.ultima("acao_recusada")["motivo"] == "acao_ilegal"
    assert _estado(partida) == antes


def test_rodada_errada_e_acao_repetida_sao_recusadas():
    srv, rede, ana, bia, partida = _parado_na_rodada_1()
    ataque = {"kind": "attack", "skill_id": None}
    rede.enviar("c1", protocolo.codificar("acao", partida=partida.id, rodada=2, acao=ataque))
    assert ana.ultima("acao_recusada")["motivo"] == "rodada_errada"
    rede.enviar("c1", protocolo.codificar("acao", partida=partida.id, rodada=1, acao=ataque))
    assert ana.ultima("acao_recebida") is not None
    rede.enviar("c1", protocolo.codificar("acao", partida=partida.id, rodada=1, acao=ataque))
    assert ana.ultima("acao_recusada")["motivo"] == "acao_ja_enviada"
    assert partida.duelo.round_number == 1


def test_quem_nao_joga_a_partida_nao_age_nela():
    srv, rede, ana, bia, partida = _parado_na_rodada_1()
    intruso = cliente("caio")
    entrar(rede, "c9", intruso)
    antes = _estado(partida)
    ataque = {"kind": "attack", "skill_id": None}
    rede.enviar("c9", protocolo.codificar("acao", partida=partida.id, rodada=1, acao=ataque))
    assert intruso.recusas[-1]["motivo"] == "partida_desconhecida"
    assert _estado(partida) == antes


# --- o motor canônico ------------------------------------------------------------------


def test_a_final_publicada_da_copa_03_rejogada_pelo_servidor_da_o_mesmo_resultado():
    acoes = acoes_da_final()
    srv, rede, ana, bia = _duelo_pela_rede(Roteiro(acoes["p1"]), Roteiro(acoes["p2"]))
    publicado = rodadas_da_final()
    registro = srv.exportar(next(iter(srv._partidas)))

    assert len(registro["rodadas"]) == len(publicado) == 37
    for nossa, deles in zip(registro["rodadas"], publicado):
        assert nossa["hp_fim"] == dict(deles["hp_end"])
        assert nossa["mp_fim"] == dict(deles["mp_end"])

    final = resultado_da_final()
    assert ana.fim["estado"] == CONCLUIDA
    assert (ana.fim["vencedor"], ana.fim["motivo"], ana.fim["rodadas"]) == (
        final["winner"],
        final["reason"],
        final["rounds"],
    )
    (desfecho,) = srv.resultados.classificaveis()
    # fer (W64), da bia, vence; o livro guarda as contas, não nomes declarados.
    assert (desfecho.vencedor, desfecho.perdedor) == (conta_id("bia"), conta_id("ana"))


def test_partida_pelo_servidor_e_o_mesmo_duelo_que_o_motor_direto():
    srv, rede, ana, bia = _duelo_pela_rede(PrimeiraSkill(), Ataca())
    partida = srv.partida(next(iter(srv._partidas)))
    assert partida.duelo.finished

    direto = Duel(
        gladiator_from_snapshot(json.loads((SNAPSHOTS / "W23.json").read_text())),
        gladiator_from_snapshot(json.loads((SNAPSHOTS / "W64.json").read_text())),
        rng=random.Random(SEMENTE_DA_FINAL),
    )
    for rodada in partida.rodadas:
        direto.play_round({lado: protocolo.acao_de(a) for lado, a in rodada["acoes"].items()})
    # Rodada a rodada, inclusive iniciativa, ordem, passos e eventos do motor.
    assert direto.history == partida.duelo.history
    assert direto.events == partida.duelo.events
    assert direto.result == partida.duelo.result


def test_a_observacao_e_a_duelview_do_motor_e_nada_alem():
    srv, rede, ana, bia, partida = _parado_na_rodada_1()
    observacao = ana.ultima("observacao")
    assert set(observacao) == {"tipo", "partida", "visao"}
    assert protocolo.visao_de_dict(observacao["visao"]) == partida.duelo.view("p1")


def test_a_rodada_publica_nao_revela_a_iniciativa():
    srv, rede, ana, bia = _duelo_pela_rede(Ataca(), Ataca())
    rodada = ana.ultima("rodada")["rodada"]
    assert "initiative" not in rodada and "iniciativa" not in rodada
    assert set(rodada) == {"numero", "acoes", "ordem", "passos", "hp_fim", "mp_fim"}


# --- os snapshots canônicos --------------------------------------------------------------


def test_os_snapshots_publicados_nao_mudam():
    publicados = {
        g["id"]: g["sha256"]
        for g in json.loads((COPA_03 / "gladiadores.json").read_text())["gladiadores"]
    }
    antes = {gid: sha256_do_arquivo(SNAPSHOTS / f"{gid}.json") for gid in publicados}
    assert antes == publicados

    acoes = acoes_da_final()
    _duelo_pela_rede(Roteiro(acoes["p1"]), Roteiro(acoes["p2"]))
    _duelo_pela_rede(PrimeiraSkill(), PrimeiraSkill(), ("W01", "W02"))
    acervo(*publicados).ids()

    depois = {gid: sha256_do_arquivo(SNAPSHOTS / f"{gid}.json") for gid in publicados}
    assert depois == publicados


def test_o_acervo_nao_compartilha_estado_com_quem_o_criou():
    from tests._multiplayer_apoio import snapshot

    original = snapshot("W23")
    gladiadores = acervo("W23")
    impressao = gladiadores.impressao("W23")
    original["level"] = 99
    original["passives"].clear()
    assert gladiadores.impressao("W23") == impressao
    g1, _ = gladiadores.preparar("W23")
    g2, _ = gladiadores.preparar("W23")
    assert g1.hero is not g2.hero


# --- o replay -------------------------------------------------------------------------


def _partida_concluida():
    srv, rede, ana, bia = _duelo_pela_rede(PrimeiraSkill(), PrimeiraSkill())
    partida_id = next(iter(srv._partidas))
    return srv, srv.exportar(partida_id)


def test_replay_reproduz_a_partida_na_versao_contratada():
    srv, registro = _partida_concluida()
    duelo = reproduzir(registro, acervo(), srv.impressao)
    assert duelo.result == srv.partida(registro["partida"]).duelo.result
    assert duelo.history == srv.partida(registro["partida"]).duelo.history


def test_replay_de_outra_versao_e_recusado():
    srv, registro = _partida_concluida()
    with pytest.raises(PartidaIncompativelError, match="outra versão"):
        reproduzir(registro, acervo(), "0" * 64)


def test_replay_com_estado_adulterado_e_recusado():
    srv, registro = _partida_concluida()
    registro["rodadas"][3]["hp_fim"]["p1"] += 1
    with pytest.raises(PartidaIncompativelError, match="rodada 4"):
        reproduzir(registro, acervo(), srv.impressao)


def test_replay_com_resultado_adulterado_e_recusado():
    srv, registro = _partida_concluida()
    registro["resultado"]["vencedor"] = "p1" if registro["resultado"]["vencedor"] == "p2" else "p2"
    with pytest.raises(PartidaIncompativelError, match="resultado"):
        reproduzir(registro, acervo(), srv.impressao)


def test_replay_e_deterministico_em_outro_processo():
    """O mesmo registro, rejogado em processos com hash aleatório diferente."""
    srv, registro = _partida_concluida()
    programa = (
        "import json, sys\n"
        "sys.path.insert(0, sys.argv[1])\n"
        "from tests._multiplayer_apoio import acervo\n"
        "from src.multiplayer.servidor import reproduzir\n"
        "registro = json.loads(sys.stdin.read())\n"
        "duelo = reproduzir(registro, acervo(), registro['impressao'])\n"
        "print(json.dumps([duelo.result.winner, duelo.result.rounds,"
        " [list(r.hp_end) for r in duelo.history]]))\n"
    )
    esperado = srv.partida(registro["partida"]).duelo
    for semente_de_hash in ("1", "987654"):
        feito = subprocess.run(
            [sys.executable, "-c", programa, str(ROOT)],
            input=json.dumps(registro),
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONHASHSEED": semente_de_hash},
            cwd=ROOT,
            check=True,
        )
        vencedor, rodadas, hp = json.loads(feito.stdout)
        assert (vencedor, rodadas) == (esperado.result.winner, esperado.result.rounds)
        assert hp == [[list(par) for par in r.hp_end] for r in esperado.history]
