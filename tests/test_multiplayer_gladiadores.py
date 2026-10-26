"""Gladiadores e persistência no multiplayer (contrato multiplayer, §5).

- O snapshot é reconstruído pelo caminho canônico de saves, e o multiplayer
  nunca o altera.
- O esquema é explícito: os campos de `to_save_data`, nem um a mais nem um a
  menos. Campo novo no save é formato novo — esquema e migração.
- Gladiador incompatível não entra em partida: item, carta ou passiva fora do
  catálogo, campo desconhecido, tipo errado, personagem sem extração, e qualquer
  coisa que a reconstrução canônica descartaria em silêncio.
- Migração é explícita: esquema mais novo é recusado, e o mais velho só entra
  por um passo registrado.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.engine.arena_setup import character_from_snapshot  # noqa: E402
from src.mechanics.pvp_duel import Gladiator  # noqa: E402
from src.multiplayer import gladiadores as g  # noqa: E402
from src.storage.save_manager import to_save_data  # noqa: E402
from tests._multiplayer_apoio import COPA_03, SNAPSHOTS, snapshot  # noqa: E402


def _problemas(mudar) -> list[str]:
    dados = snapshot("W01")
    mudar(dados)
    return g.problemas_do_snapshot(dados)


def test_o_esquema_e_exatamente_o_formato_de_save():
    """Se o save aprender um campo novo, este teste falha até o esquema mudar."""
    heroi = character_from_snapshot(snapshot("W01"))
    assert set(to_save_data(heroi, 21, None)) == set(g.CAMPOS_DO_SNAPSHOT)


def test_os_64_gladiadores_publicados_sao_validos_e_ficam_intactos():
    indice = json.loads((COPA_03 / "gladiadores.json").read_text())["gladiadores"]
    assert len(indice) == 64
    for entrada in indice:
        arquivo = SNAPSHOTS / f"{entrada['id']}.json"
        texto = arquivo.read_text(encoding="utf-8")
        dados = json.loads(texto)
        assert g.problemas_do_snapshot(dados) == [], entrada["id"]
        assert isinstance(g.gladiador_de_registro(g.registro_de_snapshot(dados)), Gladiator)
        assert json.loads(arquivo.read_text(encoding="utf-8")) == json.loads(texto)
        assert dados == json.loads(texto)


@pytest.mark.parametrize(
    "mudar, trecho",
    [
        (lambda d: d["inventory"].append({"name": "Item Retirado do Jogo"}), "Item Retirado"),
        (lambda d: d["equipment"].update(Helmet={"name": "Elmo Fantasma"}), "Elmo Fantasma"),
        (lambda d: d["passives"].append("passiva_inexistente"), "passiva_inexistente"),
        (lambda d: d["skills"].update({"2": "carta_inexistente"}), "carta_inexistente"),
        (lambda d: d.update(campo_do_futuro=1), "campo_do_futuro"),
        (lambda d: d.pop("ledger"), "ledger"),
        (lambda d: d.update(level=True), "level"),
        (lambda d: d.update(level="23"), "level"),
        (lambda d: d.update(level=0), "Nível 0"),
        (lambda d: d.update(extracted_on_floor=0), "Extração"),
        (lambda d: d.update(player_class="Bardo"), "Bardo"),
    ],
    ids=[
        "item_na_mochila",
        "item_equipado",
        "passiva",
        "carta",
        "campo_desconhecido",
        "campo_ausente",
        "bool_no_lugar_de_int",
        "texto_no_lugar_de_int",
        "nivel_invalido",
        "sem_extracao",
        "classe_desconhecida",
    ],
)
def test_gladiador_incompativel_e_recusado(mudar, trecho):
    problemas = _problemas(mudar)
    assert problemas
    assert any(trecho in p for p in problemas), problemas


def test_o_que_a_reconstrucao_descartaria_em_silencio_e_recusado():
    """Quinta carta no deck: o carregador canônico a tiraria sem avisar."""
    dados = snapshot("W01")
    dados["skills"]["5"] = dados["skills"]["1"]
    assert g.problemas_estruturais(dados) == []  # a carta existe no catálogo
    problemas = g.problemas_do_snapshot(dados)
    assert any("`skills` não sobrevive" in p for p in problemas)


def test_validar_nao_altera_o_snapshot():
    dados = snapshot("W23")
    copia = copy.deepcopy(dados)
    g.problemas_do_snapshot(dados)
    registro = g.registro_de_snapshot(dados)
    g.gladiador_de_registro(registro)
    assert dados == copia
    assert registro["snapshot"] == copia
    assert registro["snapshot"] is not dados


# --- esquema e migração ----------------------------------------------------------


def _registro():
    return g.registro_de_snapshot(snapshot("W01"))


def test_esquema_mais_novo_e_recusado():
    registro = _registro()
    registro["esquema"] = g.ESQUEMA_ATUAL + 1
    with pytest.raises(g.GladiadorIncompativelError, match="mais novo"):
        g.gladiador_de_registro(registro)


@pytest.mark.parametrize("esquema", [0, -1, "1", None, True])
def test_esquema_ilegivel_e_recusado(esquema):
    registro = _registro()
    registro["esquema"] = esquema
    with pytest.raises(g.GladiadorIncompativelError):
        g.migrar(registro)


def test_registro_com_campo_extra_e_recusado():
    registro = _registro()
    registro["atributos"] = {"ST": 999}
    with pytest.raises(g.GladiadorIncompativelError, match="Campos do registro"):
        g.gladiador_de_registro(registro)


def test_esquema_antigo_sem_migracao_registrada_e_recusado():
    registro = _registro()
    with pytest.raises(g.GladiadorIncompativelError, match="Não há migração"):
        g.migrar(registro, migracoes={}, atual=g.ESQUEMA_ATUAL + 1)


def test_migracao_registrada_leva_o_registro_ao_esquema_atual_sem_alterar_o_original():
    registro = _registro()
    original = copy.deepcopy(registro)

    def renomeia(dados: dict) -> dict:
        dados["esquema"] = 2
        dados["snapshot"]["nome_do_passo"] = "migrado"
        return dados

    migrado = g.migrar(registro, migracoes={1: renomeia}, atual=2)
    assert migrado["esquema"] == 2
    assert migrado["snapshot"]["nome_do_passo"] == "migrado"
    assert registro == original


def test_migracao_que_nao_avanca_o_esquema_e_recusada():
    with pytest.raises(g.GladiadorIncompativelError, match="não produziu"):
        g.migrar(_registro(), migracoes={1: lambda d: d}, atual=2)


def test_nao_ha_migracao_pendente_no_esquema_atual():
    """Todo esquema anterior ao atual tem o seu passo registrado."""
    assert set(g.MIGRACOES) == set(range(1, g.ESQUEMA_ATUAL))


# --- o acervo ----------------------------------------------------------------------


def test_acervo_recusa_id_desconhecido_e_revalida_a_cada_preparo():
    acervo = g.AcervoDeGladiadores.de_snapshots({"W01": snapshot("W01")})
    with pytest.raises(g.GladiadorIncompativelError, match="não existe"):
        acervo.preparar("W99")
    gladiador, impressao = acervo.preparar("W01")
    assert impressao == g.impressao_do_registro(acervo._registros["W01"])
    acervo._registros["W01"]["snapshot"]["passives"].append("passiva_inexistente")
    with pytest.raises(g.GladiadorIncompativelError, match="passiva_inexistente"):
        acervo.preparar("W01")


def test_acervo_nao_aceita_snapshot_invalido_na_entrada():
    dados = snapshot("W01")
    dados["extracted_on_floor"] = 0
    with pytest.raises(g.GladiadorIncompativelError, match="Extração"):
        g.AcervoDeGladiadores.de_snapshots({"W01": dados})
