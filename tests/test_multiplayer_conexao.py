"""Versão obrigatória entre cliente e servidor (contrato multiplayer, §2).

A conexão competitiva só é autorizada quando a identidade do cliente é IGUAL à do
servidor. Não existe compatibilidade com versão próxima, anterior ou posterior.
A verificação se repete na entrada da fila, na criação da partida e na
reconexão, e a recusa diz que a atualização do jogo é obrigatória.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multiplayer import compatibilidade as compat  # noqa: E402
from src.multiplayer.manifesto import Identidade  # noqa: E402
from src.multiplayer.transporte import RedeLocal  # noqa: E402
from tests._multiplayer_apoio import (  # noqa: E402
    Ataca,
    acervo,
    cliente,
    em_fila,
    identidade_oficial,
    outra_identidade,
    servidor,
)


def _cumprimentar(identidade: Identidade | dict):
    """Um `ola` cru no servidor; devolve o servidor e a resposta decodificada."""
    srv = servidor()
    corpo = identidade.como_dict() if isinstance(identidade, Identidade) else identidade
    texto = json.dumps({"tipo": "ola", "identidade": corpo, "jogador": "ana"})
    envios = srv.receber("c1", texto)
    assert len(envios) == 1 and envios[0].conexao == "c1"
    return srv, json.loads(envios[0].texto)


def _sem_sessao(srv) -> bool:
    return not srv._sessoes and not srv._por_conexao


# --- a conexão ----------------------------------------------------------------------


def test_cliente_e_servidor_identicos_conexao_autorizada():
    srv, resposta = _cumprimentar(identidade_oficial())
    assert resposta["tipo"] == "bem_vindo"
    assert resposta["versao"] == srv.identidade.jogo
    assert len(srv._sessoes) == 1


def test_cliente_desatualizado_conexao_recusada():
    srv, resposta = _cumprimentar(outra_identidade(jogo="0.3.9-arena.9"))
    assert resposta["tipo"] == "recusado"
    assert resposta["motivo"] == compat.VERSAO_DO_JOGO
    assert resposta["atualizacao_obrigatoria"] is True
    assert resposta["versao_exigida"] == srv.identidade.jogo
    assert "Atualização do jogo obrigatória" in resposta["mensagem"]
    assert _sem_sessao(srv)


def test_cliente_com_versao_superior_conexao_recusada():
    srv, resposta = _cumprimentar(outra_identidade(jogo="9.0.0-arena.1"))
    assert resposta["tipo"] == "recusado"
    assert resposta["motivo"] == compat.VERSAO_DO_JOGO
    assert resposta["atualizacao_obrigatoria"] is True
    assert _sem_sessao(srv)


@pytest.mark.parametrize("grupo", ["regras", "catalogos", "persistencia", "protocolo", "servidor"])
def test_mesmo_numero_de_versao_com_hash_incompativel_conexao_recusada(grupo):
    oficial = identidade_oficial()
    adulterada = outra_identidade(grupos={grupo: "0" * 64})
    assert adulterada.jogo == oficial.jogo
    srv, resposta = _cumprimentar(adulterada)
    assert resposta["tipo"] == "recusado"
    assert resposta["motivo"] == compat.CONTEUDO
    assert grupo in resposta["mensagem"]
    assert _sem_sessao(srv)


def test_hash_do_conteudo_sozinho_tambem_recusa():
    # Grupos certos, conteúdo total errado: a identidade não é a mesma.
    srv, resposta = _cumprimentar(outra_identidade(conteudo="0" * 64))
    assert resposta["motivo"] == compat.CONTEUDO
    assert _sem_sessao(srv)


@pytest.mark.parametrize(
    "mudanca, motivo",
    [
        ({"protocolo": 2}, compat.PROTOCOLO),
        ({"regras": "duelo-0"}, compat.REGRAS),
        ({"esquema_gladiador": 2}, compat.ESQUEMA),
    ],
)
def test_cada_identificador_divergente_recusa(mudanca, motivo):
    srv, resposta = _cumprimentar(outra_identidade(**mudanca))
    assert resposta["motivo"] == motivo
    assert resposta["atualizacao_obrigatoria"] is True
    assert _sem_sessao(srv)


@pytest.mark.parametrize(
    "estrago",
    [
        lambda d: d.pop("conteudo"),
        lambda d: d.update(extra=1),
        lambda d: d.update(protocolo="1"),
        lambda d: d.update(protocolo=True),
        lambda d: d["grupos"].pop("regras"),
    ],
    ids=["sem_conteudo", "campo_extra", "protocolo_texto", "protocolo_bool", "sem_grupo"],
)
def test_identidade_malformada_recusa(estrago):
    corpo = identidade_oficial().como_dict()
    estrago(corpo)
    srv, resposta = _cumprimentar(corpo)
    assert resposta["tipo"] == "recusado"
    assert resposta["motivo"] == compat.IDENTIDADE_INVALIDA
    assert _sem_sessao(srv)


def test_a_decisao_nao_aceita_nada_alem_da_igualdade():
    oficial = identidade_oficial()
    assert compat.decidir(oficial, oficial).aceita
    assert compat.decidir(oficial, oficial.como_dict()).aceita
    for diferente in (
        outra_identidade(jogo=oficial.jogo + ".1"),
        outra_identidade(grupos={"catalogos": "1" * 64}),
    ):
        assert not compat.decidir(oficial, diferente).aceita


# --- a fila -----------------------------------------------------------------------


def test_entrada_na_fila_confere_a_versao_de_novo():
    srv = servidor()
    rede = RedeLocal(srv)
    ana = cliente("ana")
    rede.conectar("c1", ana)
    rede.enviar("c1", ana.ola())
    assert ana.token is not None

    # O cliente trocou de binário no meio da sessão: a fila confere de novo.
    ana.identidade = outra_identidade(jogo="0.3.9-arena.9")
    rede.enviar("c1", ana.entrar_na_fila("W23"))
    assert ana.recusas[-1]["motivo"] == compat.VERSAO_DO_JOGO
    assert srv.na_fila() == ()


def test_fila_recusa_gladiador_que_o_servidor_nao_conhece():
    srv = servidor()
    rede = RedeLocal(srv)
    ana = cliente("ana")
    em_fila(rede, "c1", ana, "W99")
    assert ana.recusas[-1]["motivo"] == "gladiador_incompativel"
    assert srv.na_fila() == ()


def test_fila_exige_sessao():
    srv = servidor()
    rede = RedeLocal(srv)
    ana = cliente("ana")
    rede.conectar("c1", ana)
    rede.enviar("c1", ana.entrar_na_fila("W23"))
    assert ana.recusas[-1]["motivo"] == "sem_sessao"


# --- a criação da partida -------------------------------------------------------------


def test_criacao_da_partida_confere_a_versao_dos_dois_lados():
    srv = servidor()
    rede = RedeLocal(srv)
    ana, bia = cliente("ana", Ataca()), cliente("bia", Ataca())
    em_fila(rede, "c1", ana, "W23")
    assert srv.na_fila() == ("ana",)

    # A sessão de ana passou a registrar outra versão entre a fila e o
    # pareamento: a partida não nasce, e bia volta para a fila.
    srv._sessoes[ana.token].identidade = outra_identidade(jogo="0.3.9-arena.9")
    em_fila(rede, "c2", bia, "W64")
    assert ana.recusas[-1]["motivo"] == compat.VERSAO_DO_JOGO
    assert srv.partidas_em_andamento() == ()
    assert srv.na_fila() == ("bia",)
    assert bia.partida is None


def test_criacao_da_partida_revalida_o_gladiador():
    acervo_ = acervo("W23", "W64")
    srv = servidor(acervo_)
    rede = RedeLocal(srv)
    ana, bia = cliente("ana", Ataca()), cliente("bia", Ataca())
    em_fila(rede, "c1", ana, "W23")
    # O registro de W23 deixou de ser válido nesta versão (item fora do catálogo).
    acervo_._registros["W23"]["snapshot"]["inventory"].append({"name": "Item que Saiu"})
    em_fila(rede, "c2", bia, "W64")
    assert ana.recusas[-1]["motivo"] == "gladiador_incompativel"
    assert any("Item que Saiu" in p for p in ana.recusas[-1]["problemas"])
    assert srv.partidas_em_andamento() == ()
    assert srv.na_fila() == ("bia",)


# --- a reconexão --------------------------------------------------------------------


def _partida_em_andamento():
    """Uma partida parada na rodada 1, com os dois clientes sem controlador."""
    srv = servidor()
    rede = RedeLocal(srv)
    ana, bia = cliente("ana"), cliente("bia")
    em_fila(rede, "c1", ana, "W23")
    em_fila(rede, "c2", bia, "W64")
    assert ana.partida is not None
    return srv, rede, ana, bia


def test_reconexao_com_versao_incompativel_e_recusada():
    srv, rede, ana, _ = _partida_em_andamento()
    partida = srv.partida(ana.partida)
    rodada, historia = partida.duelo.round_number, partida.duelo.history

    rede.desconectar("c1")
    ana.identidade = outra_identidade(jogo="0.3.9-arena.9")
    rede.conectar("c3", ana)
    rede.enviar("c3", ana.reconectar())

    assert ana.recusas[-1]["motivo"] == compat.VERSAO_DO_JOGO
    assert ana.recusas[-1]["atualizacao_obrigatoria"] is True
    assert srv._sessoes[ana.token].conexao is None
    assert "c3" not in srv._por_conexao
    # A partida não andou nem mudou.
    assert partida.duelo.round_number == rodada
    assert partida.duelo.history == historia


def test_reconexao_com_hash_divergente_e_recusada():
    srv, rede, ana, _ = _partida_em_andamento()
    rede.desconectar("c1")
    ana.identidade = outra_identidade(grupos={"regras": "0" * 64})
    rede.conectar("c3", ana)
    rede.enviar("c3", ana.reconectar())
    assert ana.recusas[-1]["motivo"] == compat.CONTEUDO
    assert srv._sessoes[ana.token].conexao is None


def test_reconexao_com_a_mesma_versao_volta_para_a_partida():
    srv, rede, ana, _ = _partida_em_andamento()
    rede.desconectar("c1")
    observacoes = len([m for m in ana.recebidas if m["tipo"] == "observacao"])
    rede.conectar("c3", ana)
    rede.enviar("c3", ana.reconectar())
    assert ana.ultima("bem_vindo")["token"] == ana.token
    assert len([m for m in ana.recebidas if m["tipo"] == "observacao"]) == observacoes + 1
    assert srv._sessoes[ana.token].conexao == "c3"


def test_reconexao_com_token_desconhecido_e_recusada():
    srv = servidor()
    rede = RedeLocal(srv)
    ana = cliente("ana")
    ana.token = "token-inventado"
    rede.conectar("c1", ana)
    rede.enviar("c1", ana.reconectar())
    assert ana.recusas[-1]["motivo"] == "sessao_desconhecida"
