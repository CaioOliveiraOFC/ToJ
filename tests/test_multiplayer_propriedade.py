"""Propriedade dos gladiadores e sessão autenticada no servidor (Fase 4, §3).

- Um gladiador só entra no servidor por importação de origem confiável, com
  extração real; snapshot alterado, repetido (cópia para outra conta) ou fora do
  publicado é recusado. Não existe transferência.
- A conta da sessão é a do token; o cliente não tem como declarar outra.
- Gladiador de outra conta não entra na fila, na sala nem na partida.
- Uma conta não controla os dois lados da mesma partida.
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multiplayer import contas as c  # noqa: E402
from src.multiplayer.gladiadores import GladiadorIncompativelError  # noqa: E402
from src.multiplayer.registro import (  # noqa: E402
    PropriedadeError,
    RegistroDeGladiadores,
    importar_da_copa,
)
from src.multiplayer.transporte import RedeLocal  # noqa: E402
from tests._multiplayer_apoio import (  # noqa: E402
    COPA_03,
    SENHAS,
    SNAPSHOTS,
    cliente,
    conta_id,
    contas,
    em_fila,
    entrar,
    identidade_oficial,
    registro,
    servidor,
    sha256_do_arquivo,
    snapshot,
)

# --- o registro --------------------------------------------------------------------


def test_importacao_confiavel_guarda_dono_e_origem():
    gladiadores = registro(ana=("W23", "W01"), bia="W64")
    assert gladiadores.dono_de("W23") == conta_id("ana")
    assert [f.id for f in gladiadores.de(conta_id("ana"))] == ["W01", "W23"]
    assert [f.id for f in gladiadores.de(conta_id("bia"))] == ["W64"]
    origem = gladiadores.origem("W23")
    assert origem["tipo"] == "copa_publicada"
    assert origem["sha256"] == sha256_do_arquivo(SNAPSHOTS / "W23.json")


def test_mesmo_personagem_nao_e_registrado_duas_vezes():
    gladiadores = registro(ana="W23")
    with pytest.raises(PropriedadeError, match="já está registrado"):
        importar_da_copa(gladiadores, COPA_03, "W23", conta_id("bia"))
    # Mesmo conteúdo sob outro id: é cópia do personagem para outra conta.
    with pytest.raises(PropriedadeError, match="cópia nem transferência"):
        gladiadores.importar("W23b", snapshot("W23"), conta_id("bia"), {"tipo": "teste"})
    assert gladiadores.dono_de("W23") == conta_id("ana")


def test_nao_existe_transferencia_entre_contas():
    gladiadores = registro()
    publicos = [nome for nome in dir(gladiadores) if not nome.startswith("_")]
    assert not any(
        palavra in nome for nome in publicos for palavra in ("transfer", "dono_para", "doar")
    )


def test_snapshot_fora_do_publicado_e_recusado(tmp_path):
    copa = tmp_path / "copa"
    shutil.copytree(COPA_03 / "snapshots", copa / "snapshots")
    shutil.copy(COPA_03 / "gladiadores.json", copa / "gladiadores.json")
    alterado = json.loads((copa / "snapshots" / "W23.json").read_text())
    alterado["level"] = 99
    (copa / "snapshots" / "W23.json").write_text(json.dumps(alterado))
    with pytest.raises(PropriedadeError, match="não é o publicado"):
        importar_da_copa(RegistroDeGladiadores(), copa, "W23", conta_id("ana"))
    with pytest.raises(PropriedadeError, match="não está no índice"):
        importar_da_copa(RegistroDeGladiadores(), copa, "W99", conta_id("ana"))


def test_personagem_sem_extracao_nao_entra_no_registro():
    dados = snapshot("W23")
    dados["extracted_on_floor"] = 0
    with pytest.raises(GladiadorIncompativelError, match="Extração"):
        RegistroDeGladiadores().importar("X1", dados, conta_id("ana"), {"tipo": "teste"})


def test_registro_persiste_e_detecta_alteracao_por_fora(tmp_path):
    arquivo = tmp_path / "gladiadores.json"
    gladiadores = RegistroDeGladiadores(arquivo)
    importar_da_copa(gladiadores, COPA_03, "W23", conta_id("ana"))
    reaberto = RegistroDeGladiadores(arquivo)
    assert reaberto.dono_de("W23") == conta_id("ana")
    reaberto.preparar("W23")

    dados = json.loads(arquivo.read_text())
    dados["gladiadores"]["W23"]["registro"]["snapshot"]["level"] = 99
    arquivo.write_text(json.dumps(dados))
    with pytest.raises(GladiadorIncompativelError, match="alterado fora do servidor"):
        RegistroDeGladiadores(arquivo).preparar("W23")


def test_snapshots_publicados_ficam_intactos_depois_da_importacao():
    antes = {p.name: sha256_do_arquivo(p) for p in SNAPSHOTS.glob("*.json")}
    registro(ana=("W23", "W01", "W02"), bia=("W64", "W03"))
    depois = {p.name: sha256_do_arquivo(p) for p in SNAPSHOTS.glob("*.json")}
    assert antes == depois


# --- a sessão autenticada ------------------------------------------------------------


def _ola_cru(srv, conexao: str, **campos) -> dict:
    corpo = {"tipo": "ola", "identidade": identidade_oficial().como_dict(), **campos}
    (envio,) = srv.receber(conexao, json.dumps(corpo))
    return json.loads(envio.texto)


def test_o_cliente_nao_tem_campo_para_declarar_conta_ou_dono():
    srv = servidor()
    token = contas().entrar("bia", SENHAS["bia"]).token
    for extra in ({"conta": conta_id("ana")}, {"usuario": "ana"}, {"jogador": "ana"}):
        resposta = _ola_cru(srv, "c1", token=token, **extra)
        assert resposta["motivo"] == "campos_invalidos"
    resposta = _ola_cru(srv, "c1", token=token)
    assert resposta["tipo"] == "bem_vindo"
    assert (resposta["usuario"], resposta["conta"]) == ("bia", conta_id("bia"))
    assert [g["id"] for g in resposta["gladiadores"]] == ["W64"]


@pytest.mark.parametrize("estrago", ["adulterado", "outra_chave", "lixo"])
def test_ola_com_token_invalido_e_recusado(estrago):
    srv = servidor()
    token = contas().entrar("ana", SENHAS["ana"]).token
    if estrago == "adulterado":
        token = token[:-3] + ("AAA" if not token.endswith("AAA") else "BBB")
    elif estrago == "outra_chave":
        token, _ = c.TokensAssinados(bytes(reversed(range(32)))).emitir(conta_id("ana"))
    else:
        token = "v1.isto.nao"
    resposta = _ola_cru(srv, "c1", token=token)
    assert resposta["motivo"] == "token_invalido"
    assert srv.sessao_da_conexao("c1") is None


def test_ola_com_token_expirado_e_recusado():
    relogio = [1_000_000.0]
    vencidas = c.ContasLocais(None, c.TokensAssinados(bytes(range(32)), 60, lambda: relogio[0]))
    vencidas.criar("ana", SENHAS["ana"])
    token = vencidas.entrar("ana", SENHAS["ana"]).token
    relogio[0] += 61
    srv = servidor()
    srv.autenticador = vencidas
    resposta = _ola_cru(srv, "c1", token=token)
    assert resposta["motivo"] == "token_invalido"
    assert "expirado" in resposta["mensagem"]


def test_token_que_expira_durante_a_sessao_nao_compromete_nada_novo():
    agora = [0.0]
    srv = servidor(relogio=lambda: agora[0])
    rede = RedeLocal(srv)
    ana = cliente("ana")
    entrar(rede, "c1", ana)
    agora[0] = srv.sessao_da_conexao("c1").expira_em
    rede.enviar("c1", ana.criar_sala("W23"))
    assert ana.recusas[-1]["motivo"] == "token_expirado"
    assert srv.salas_abertas() == ()


def test_login_errado_e_limitado_por_conexao():
    srv = servidor()
    rede = RedeLocal(srv)
    ana = cliente("ana")
    rede.conectar("c1", ana)
    for _ in range(5):
        rede.enviar("c1", ana.login("ana", "senha-errada"))
        assert ana.recusas[-1]["motivo"] == "credenciais_invalidas"
    rede.enviar("c1", ana.login("ana", SENHAS["ana"]))
    assert ana.recusas[-1]["motivo"] == "tentativas_esgotadas"
    assert ana.token is None


def test_reconectar_com_token_de_outra_conta_e_recusado():
    srv = servidor()
    rede = RedeLocal(srv)
    ana, bia = cliente("ana"), cliente("bia")
    em_fila(rede, "c1", ana, "W23")
    em_fila(rede, "c2", bia, "W64")
    rede.desconectar("c1")
    # bia tenta assumir a sessão de ana com o próprio token.
    bia_intrusa = cliente("bia")
    bia_intrusa.sessao, bia_intrusa.token = ana.sessao, bia.token
    rede.conectar("c3", bia_intrusa)
    rede.enviar("c3", bia_intrusa.reconectar())
    assert bia_intrusa.recusas[-1]["motivo"] == "sessao_desconhecida"
    assert srv._sessoes[ana.sessao].conexao is None


# --- a posse ---------------------------------------------------------------------------


@pytest.mark.parametrize("comando", ["entrar_na_fila", "criar_sala"])
def test_gladiador_de_outra_conta_e_recusado(comando):
    srv = servidor()
    rede = RedeLocal(srv)
    ana = cliente("ana")
    entrar(rede, "c1", ana)
    rede.enviar("c1", getattr(ana, comando)("W64"))  # o W64 é da bia
    assert ana.recusas[-1]["motivo"] == "gladiador_alheio"
    assert srv.na_fila() == () and srv.salas_abertas() == ()


def test_entrar_na_sala_com_gladiador_alheio_e_recusado():
    srv = servidor(registro(ana="W23", bia="W64", caio="W01"))
    rede = RedeLocal(srv)
    ana, caio = cliente("ana"), cliente("caio")
    entrar(rede, "c1", ana)
    rede.enviar("c1", ana.criar_sala("W23"))
    entrar(rede, "c2", caio)
    rede.enviar("c2", caio.entrar_na_sala(ana.sala, "W64"))
    assert caio.recusas[-1]["motivo"] == "gladiador_alheio"
    assert srv.partidas_em_andamento() == ()
    assert srv.salas_abertas() == ("ana",)


def test_dono_trocado_entre_a_fila_e_a_partida_e_conferido_na_criacao():
    gladiadores = registro()
    srv = servidor(gladiadores)
    rede = RedeLocal(srv)
    ana, bia = cliente("ana"), cliente("bia")
    em_fila(rede, "c1", ana, "W23")
    gladiadores._itens["W23"]["dono"] = conta_id("caio")
    em_fila(rede, "c2", bia, "W64")
    assert ana.recusas[-1]["motivo"] == "gladiador_alheio"
    assert srv.partidas_em_andamento() == ()


# --- uma conta, um lado ------------------------------------------------------------------


def test_a_mesma_conta_nao_abre_duas_sessoes_ao_mesmo_tempo():
    srv = servidor()
    rede = RedeLocal(srv)
    primeira, segunda = cliente("ana"), cliente("ana")
    entrar(rede, "c1", primeira)
    entrar(rede, "c2", segunda)
    assert segunda.recusas[-1]["motivo"] == "conta_ja_conectada"
    assert srv.sessao_da_conexao("c2") is None


def test_a_mesma_conta_nao_entra_na_propria_sala():
    srv = servidor(registro(ana=("W23", "W01")))
    rede = RedeLocal(srv)
    ana = cliente("ana")
    entrar(rede, "c1", ana)
    rede.enviar("c1", ana.criar_sala("W23"))
    sala = ana.sala
    # Mesma sessão: ela já está numa sala.
    rede.enviar("c1", ana.entrar_na_sala(sala, "W01"))
    assert ana.recusas[-1]["motivo"] == "ja_ocupado"
    # Outra sessão da mesma conta (a primeira caiu): a sala dela fecha junto.
    rede.desconectar("c1")
    outra = cliente("ana")
    entrar(rede, "c2", outra)
    rede.enviar("c2", outra.entrar_na_sala(sala, "W01"))
    assert outra.recusas[-1]["motivo"] == "sala_desconhecida"
    assert srv.partidas_em_andamento() == ()


def test_a_criacao_da_partida_recusa_a_mesma_conta_dos_dois_lados():
    """Defesa em profundidade: mesmo que duas sessões da mesma conta cheguem à fila."""
    srv = servidor(registro(ana=("W23", "W01")))
    rede = RedeLocal(srv)
    primeira, segunda = cliente("ana"), cliente("ana")
    em_fila(rede, "c1", primeira, "W23")
    sessao = srv._sessoes[primeira.sessao]
    sessao.conta, sessao.usuario = "outra-conta-qualquer", "x"  # entra como outra
    entrar(rede, "c2", segunda)
    sessao.conta, sessao.usuario = conta_id("ana"), "ana"  # e volta a ser ana
    rede.enviar("c2", segunda.entrar_na_fila("W01"))
    assert segunda.recusas[-1]["motivo"] == "mesma_conta"
    assert srv.partidas_em_andamento() == ()
    assert srv.na_fila() == ("ana",)
