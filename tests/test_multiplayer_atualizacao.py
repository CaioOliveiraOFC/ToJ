"""Atualização do servidor durante partidas (contrato multiplayer, §4).

- A partida fica presa à versão em que nasceu.
- Na atualização, a versão antiga para de aceitar sessão, fila e partida
  novas, e as partidas em andamento terminam numa instância compatível — a
  mesma instância drenando, ou outra da MESMA versão, por replay conferido.
- Sem instância compatível, a partida termina anulada: sem vitória, sem derrota,
  fora da classificação. Nunca continua com regras divergentes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multiplayer import compatibilidade as compat  # noqa: E402
from src.multiplayer import protocolo  # noqa: E402
from src.multiplayer.servidor import (  # noqa: E402
    ANULADA,
    CONCLUIDA,
    DESLIGADO,
    DRENANDO,
    TRANSFERIDA,
    Frota,
    PartidaIncompativelError,
    Resultados,
)
from src.multiplayer.transporte import RedeLocal  # noqa: E402
from tests._multiplayer_apoio import (  # noqa: E402
    PrimeiraSkill,
    acervo,
    cliente,
    em_fila,
    manifesto_de_outra_versao,
    servidor,
)


def _em_partida(srv, rede):
    ana, bia = cliente("ana"), cliente("bia")
    em_fila(rede, "c1", ana, "W23")
    em_fila(rede, "c2", bia, "W64")
    return ana, bia, srv.partida(ana.partida)


def _rodar(rede, partida, rodadas):
    ataque = {"kind": "attack", "skill_id": None}
    for _ in range(rodadas):
        numero = partida.duelo.round_number
        for conexao in ("c1", "c2"):
            rede.enviar(
                conexao, protocolo.codificar("acao", partida=partida.id, rodada=numero, acao=ataque)
            )


# --- drenagem --------------------------------------------------------------------


def test_publicar_versao_nova_drena_a_antiga_e_recusa_o_que_e_novo():
    resultados = Resultados()
    antiga = servidor(resultados=resultados, nome="a")
    nova = servidor(manifesto=manifesto_de_outra_versao(), resultados=resultados, nome="b")
    frota = Frota(antiga)
    rede = RedeLocal(antiga)

    na_fila = cliente("na_fila")
    em_fila(rede, "c1", na_fila, "W23")
    assert antiga.na_fila() == ("na_fila",)

    rede.entregar(frota.publicar(nova))
    assert antiga.estado == DRENANDO
    assert frota.atual() is nova
    # Quem esperava na fila é avisado de que precisa atualizar.
    assert na_fila.recusas[-1]["motivo"] == compat.SERVIDOR_EM_ATUALIZACAO
    assert antiga.na_fila() == ()

    # Nada novo começa na versão antiga: nem sessão, nem fila.
    atrasado = cliente("atrasado")
    rede.conectar("c2", atrasado)
    rede.enviar("c2", atrasado.ola())
    assert atrasado.recusas[-1]["motivo"] == compat.SERVIDOR_EM_ATUALIZACAO
    rede.enviar("c1", na_fila.entrar_na_fila("W23"))
    assert na_fila.recusas[-1]["motivo"] == compat.SERVIDOR_EM_ATUALIZACAO
    assert antiga.partidas_em_andamento() == ()

    # A versão nova recusa o cliente antigo e aceita o atualizado.
    rede.conectar("c3", cliente("velho"), nova)
    velho = rede._clientes["c3"]
    rede.enviar("c3", velho.ola())
    assert velho.recusas[-1]["motivo"] == compat.VERSAO_DO_JOGO
    atualizado = cliente("atualizado", identidade=nova.identidade)
    rede.conectar("c4", atualizado, nova)
    rede.enviar("c4", atualizado.ola())
    assert atualizado.ultima("bem_vindo") is not None


def test_partida_em_andamento_termina_na_versao_em_que_nasceu():
    resultados = Resultados()
    antiga = servidor(resultados=resultados)
    frota = Frota(antiga)
    rede = RedeLocal(antiga)
    ana, bia, partida = _em_partida(antiga, rede)
    _rodar(rede, partida, 3)

    rede.entregar(frota.publicar(servidor(manifesto=manifesto_de_outra_versao(), nome="b")))
    assert antiga.estado == DRENANDO

    # O duelo segue na instância antiga, que drena, até o fim.
    while not partida.duelo.finished:
        _rodar(rede, partida, 1)
    assert partida.impressao == antiga.impressao
    assert ana.fim["estado"] == CONCLUIDA
    (desfecho,) = resultados.classificaveis()
    assert desfecho.impressao == antiga.impressao

    # Drenada e sem partida, a instância antiga sai do ar.
    assert frota.recolher() == [antiga]
    assert antiga.estado == DESLIGADO


def test_reconexao_durante_a_drenagem_volta_so_para_terminar_a_partida():
    antiga = servidor()
    frota = Frota(antiga)
    rede = RedeLocal(antiga)
    ana, bia, partida = _em_partida(antiga, rede)
    rede.entregar(frota.publicar(servidor(manifesto=manifesto_de_outra_versao(), nome="b")))

    rede.desconectar("c1")
    rede.conectar("c1", ana)
    rede.enviar("c1", ana.reconectar())
    assert ana.ultima("bem_vindo") is not None
    assert ana.ultima("observacao")["partida"] == partida.id


# --- continuidade em instância compatível ----------------------------------------------


def _referencia():
    """O mesmo duelo sem interrupção: o resultado que a continuidade tem de dar."""
    srv = servidor(nome="ref")
    rede = RedeLocal(srv)
    ana, bia, partida = _em_partida(srv, rede)
    while not partida.duelo.finished:
        _rodar(rede, partida, 1)
    return partida.duelo


def test_desligar_transfere_a_partida_para_instancia_da_mesma_versao():
    resultados = Resultados()
    a1 = servidor(resultados=resultados, nome="a1")
    a2 = servidor(resultados=resultados, nome="a2")
    assert a1.impressao == a2.impressao
    frota = Frota(a1, a2)
    rede = RedeLocal(a1)
    ana, bia, partida = _em_partida(a1, rede)
    _rodar(rede, partida, 5)

    rede.entregar(frota.desligar(a1))
    assert a1.estado == DESLIGADO
    assert ana.fim["estado"] == TRANSFERIDA and bia.fim["estado"] == TRANSFERIDA
    assert resultados.todos() == ()

    # Os dois voltam, com o token, na instância compatível.
    for conexao, cli in (("c1", ana), ("c2", bia)):
        rede.desconectar(conexao)
        rede.conectar(conexao, cli, a2)
        rede.enviar(conexao, cli.reconectar())
        assert cli.ultima("bem_vindo") is not None
    continuada = a2.partida(partida.id)
    assert continuada.duelo.round_number == 6
    while not continuada.duelo.finished:
        _rodar(rede, continuada, 1)

    referencia = _referencia()
    assert continuada.duelo.history == referencia.history
    assert continuada.duelo.result == referencia.result
    (desfecho,) = resultados.classificaveis()
    assert desfecho.estado == CONCLUIDA and desfecho.partida == partida.id


# --- encerramento seguro -----------------------------------------------------------------


def test_sem_instancia_compativel_a_partida_e_anulada_sem_vitoria_derrota_ou_mmr():
    resultados = Resultados()
    antiga = servidor(resultados=resultados, nome="a")
    nova = servidor(manifesto=manifesto_de_outra_versao(), resultados=resultados, nome="b")
    frota = Frota(antiga)
    rede = RedeLocal(antiga)
    ana, bia, partida = _em_partida(antiga, rede)
    _rodar(rede, partida, 4)

    rede.entregar(frota.publicar(nova))
    rede.entregar(frota.desligar(antiga))

    assert antiga.estado == DESLIGADO
    assert nova.partida(partida.id) is None  # nunca muda de versão
    for cli in (ana, bia):
        assert cli.fim["estado"] == ANULADA
        assert cli.fim["vencedor"] is None
    (desfecho,) = resultados.todos()
    assert desfecho.estado == ANULADA
    assert (desfecho.vencedor, desfecho.perdedor) == (None, None)
    assert resultados.classificaveis() == ()
    for jogador in ("ana", "bia"):
        assert resultados.vitorias(jogador) == 0
        assert resultados.derrotas(jogador) == 0

    # A instância desligada não aceita mais nada.
    rede.enviar("c1", ana.reconectar())
    assert ana.recusas[-1]["motivo"] == "servidor_desligado"


def test_versao_nova_recusa_retomar_partida_da_antiga():
    antiga = servidor(nome="a")
    nova = servidor(manifesto=manifesto_de_outra_versao(), nome="b")
    rede = RedeLocal(antiga)
    ana, bia, partida = _em_partida(antiga, rede)
    _rodar(rede, partida, 2)
    with pytest.raises(PartidaIncompativelError, match="outra versão"):
        nova.retomar(antiga.exportar(partida.id))
    assert nova.partidas_em_andamento() == ()


def test_retomar_recusa_replay_divergente_e_gladiador_diferente():
    a1 = servidor(nome="a1")
    rede = RedeLocal(a1)
    ana, bia, partida = _em_partida(a1, rede)
    _rodar(rede, partida, 3)
    registro = a1.exportar(partida.id)

    adulterado = {**registro, "rodadas": [dict(r) for r in registro["rodadas"]]}
    adulterado["rodadas"][1] = {**adulterado["rodadas"][1], "mp_fim": {"p1": 0, "p2": 0}}
    a2 = servidor(nome="a2")
    with pytest.raises(PartidaIncompativelError, match="rodada 2"):
        a2.retomar(adulterado)
    assert a2.partidas_em_andamento() == ()

    # Mesmo id de gladiador, outro registro: não é o gladiador da partida.
    outro_acervo = acervo("W23", "W01")
    outro_acervo._registros["W64"] = outro_acervo._registros.pop("W01")
    a3 = servidor(outro_acervo, nome="a3")
    with pytest.raises(PartidaIncompativelError, match="não é o registro da partida"):
        a3.retomar(registro)


def test_desligar_com_partida_sem_passar_pela_frota_e_proibido():
    srv = servidor()
    rede = RedeLocal(srv)
    _em_partida(srv, rede)
    with pytest.raises(RuntimeError, match="transfira ou anule"):
        srv.desligar()


def test_partida_transferida_nao_aceita_mais_acao_na_instancia_antiga():
    a1, a2 = servidor(nome="a1"), servidor(nome="a2")
    frota = Frota(a1, a2)
    rede = RedeLocal(a1)
    ana, bia, partida = _em_partida(a1, rede)
    registro = a1.exportar(partida.id)
    a2.retomar(registro)
    a1.transferir(partida.id)
    assert partida.estado == TRANSFERIDA
    assert a1.partidas_em_andamento() == ()
    assert frota.recolher() == []  # a1 não está drenando; nada a recolher


def test_controladores_terminam_a_partida_depois_da_transferencia():
    resultados = Resultados()
    a1, a2 = servidor(resultados=resultados, nome="a1"), servidor(resultados=resultados, nome="a2")
    frota = Frota(a1, a2)
    rede = RedeLocal(a1)
    ana, bia = cliente("ana", PrimeiraSkill()), cliente("bia", None)
    em_fila(rede, "c1", ana, "W23")
    em_fila(rede, "c2", bia, "W64")
    partida = a1.partida(ana.partida)
    rede.entregar(frota.desligar(a1))

    bia.controlador = PrimeiraSkill()
    for conexao, cli in (("c1", ana), ("c2", bia)):
        rede.conectar(conexao, cli, a2)
        rede.enviar(conexao, cli.reconectar())
    assert a2.partida(partida.id).duelo.finished
    assert ana.fim["estado"] == CONCLUIDA
    assert resultados.desfecho(partida.id).estado == CONCLUIDA
