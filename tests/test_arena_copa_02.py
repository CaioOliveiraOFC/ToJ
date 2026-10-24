"""Copa Arena 02: 64 builds legais, chave de 64, isolamento e fidelidade da auditoria.

O que estes testes fixam:

1. os 64 são distintos, na distribuição pedida de classes e faixas de OP, e cada
   build é uma que o catálogo e as regras de montagem permitem;
2. a calibração gravada é a medição canônica — remedida, dá o mesmo número;
3. a chave tem 63 confrontos, cada fase recebe exatamente os vencedores da
   anterior e sai um campeão; tudo se reproduz pela seed;
4. nenhum boneco toca save, slot ou a lista de gladiadores;
5. a auditoria não muda o duelo e não sorteia nada a mais.
"""

from __future__ import annotations

import hashlib
import json
import statistics
from collections import Counter
from dataclasses import replace
from pathlib import Path

import pytest

from src.engine import arena_setup
from src.mechanics.pvp_duel import SIDES
from src.sim.arena import limpar_cache, overall_power
from src.storage import save_manager
from tools.arena_copa_02 import (
    BUILD_POR_ID,
    BUILDS,
    DISTRIBUICAO,
    FAIXAS,
    FASES,
    IDS,
    MAX_TENTATIVAS,
    NICKS,
    POR_FAIXA,
    SEMENTE_PRINCIPAL,
    disputar_copa,
    faixa_de,
    formar_participantes,
    ler_calibracao,
    montar,
    sortear_nomes,
    todas,
)
from tools.arena_copa_02_relatorios import escrever_tudo
from tools.arena_copa_teste import BuildIlegitimaError, jogar_partida, semente_da_partida


@pytest.fixture(scope="module")
def calibracao():
    return ler_calibracao()


@pytest.fixture(scope="module")
def participantes(calibracao):
    return formar_participantes(calibracao, medir=False)


@pytest.fixture(scope="module")
def copa(participantes):
    return disputar_copa(participantes)


# --- 1. Os 64 --------------------------------------------------------------


def test_sessenta_e_quatro_distintos():
    assert len(BUILDS) == 64
    assert IDS == tuple(f"G{i:02d}" for i in range(1, 65))
    assert len({b.rotulo for b in BUILDS}) == 64
    assert len({b.deck for b in BUILDS}) == 64
    nomes = sortear_nomes()
    todos = {nick for lista in NICKS.values() for nick in lista}
    assert len(todos) == 64
    assert {nick for nick, _ in nomes.values()} == todos


def test_distribuicao_de_classes_e_faixas(calibracao):
    assert dict(Counter(b.classe for b in BUILDS)) == DISTRIBUICAO
    assert Counter(b.faixa for b in BUILDS) == {f: POR_FAIXA for f in range(1, len(FAIXAS) + 1)}
    medidos = calibracao["participantes"]
    assert set(medidos) == set(IDS)
    for gid, registro in medidos.items():
        assert registro["dentro"], gid
        assert faixa_de(registro["op"]) == BUILD_POR_ID[gid].faixa, gid
        assert sum(1 for t in registro["tentativas"] if "op" in t) <= MAX_TENTATIVAS
    media = statistics.mean(r["op"] for r in medidos.values())
    assert 24.0 <= media <= 26.0


def test_todas_as_builds_sao_legais_no_nivel_calibrado(calibracao):
    for gid, build in BUILD_POR_ID.items():
        montar(build, calibracao["participantes"][gid]["nivel"], gid)


@pytest.mark.parametrize(
    "mudanca, erro",
    [
        ({"deck": ("golpe_poderoso", "baluarte", "couraca_improvisada", "bola_fogo")}, "oferta"),
        ({"deck": ("imortal", "golpe_poderoso", "golpe_devastador", "veterania")}, "exigem"),
        ({"trocas": (("Weapon1", "Machado Terrível"),)}, "supera"),
        ({"extras": (("imortalidade", 1),)}, "Lendária"),
        ({"extras": (("escudo_fe", 3),)}, "Rara"),
        ({"deck": ("golpe_poderoso", "baluarte", "couraca_improvisada", "fantasma")}, "fantasma"),
    ],
)
def test_build_fora_das_regras_e_recusada(mudanca, erro):
    base = BUILD_POR_ID["G01"]  # Muralha de maça, Guerreiro
    with pytest.raises(BuildIlegitimaError, match=erro):
        montar(replace(base, **mudanca), 16, "teste")


@pytest.mark.parametrize("gid", ["G23", "G43"])
def test_calibracao_gravada_e_a_medicao_canonica(calibracao, gid):
    """O menor e o maior OP gravados se repetem, número por número."""
    limpar_cache()
    registro = calibracao["participantes"][gid]
    heroi = montar(BUILD_POR_ID[gid], registro["nivel"], gid)
    assert overall_power(heroi, usar_cache=False).nivel_equivalente == registro["op"]


def test_faixa_inviavel_registrada_e_medida():
    """O Colhedor não cabe na faixa 3: o menor nível legal já passa do teto."""
    colhedor = replace(BUILD_POR_ID["G13"], faixa=3)
    with pytest.raises(BuildIlegitimaError):
        montar(colhedor, 17, "teste")
    limpar_cache()
    op = overall_power(montar(colhedor, 18, "teste"), usar_cache=False).nivel_equivalente
    assert op > FAIXAS[2][1]


# --- 2. A chave ------------------------------------------------------------


def test_sessenta_e_tres_confrontos_e_um_campeao(copa):
    assert copa.interrompida is None
    for fase, quantas, _ in FASES:
        assert len(copa.fases[fase]) == quantas
    assert len(todas(copa)) == 63
    perdedores = [p.perdedor.id for p in todas(copa)]
    assert len(perdedores) == len(set(perdedores)) == 63
    assert set(IDS) - set(perdedores) == {copa.campeao.id}


def test_cada_fase_recebe_os_vencedores_da_anterior(copa):
    estreia = [p.lados[s].id for p in copa.fases["fase64"] for s in SIDES]
    assert estreia == list(copa.chave)
    assert sorted(estreia) == sorted(IDS)
    fases = [f for f, _, _ in FASES]
    for anterior, atual in zip(fases, fases[1:]):
        esperados = [p.vencedor.id for p in copa.fases[anterior]]
        recebidos = [p.lados[s].id for p in copa.fases[atual] for s in SIDES]
        assert recebidos == esperados


def test_seeds_derivadas_da_principal(copa):
    for partida in todas(copa):
        assert partida.semente == semente_da_partida(
            partida.fase, partida.indice, SEMENTE_PRINCIPAL
        )
    digest = hashlib.sha256(f"{SEMENTE_PRINCIPAL}:final:1".encode()).digest()
    assert copa.fases["final"][0].semente == int.from_bytes(digest[:8], "big")
    assert len({p.semente for p in todas(copa)}) == 63


def test_reproducao_pela_seed(copa, participantes):
    final = copa.fases["final"][0]
    de_novo = jogar_partida(
        "final",
        1,
        final.lados["p1"],
        final.lados["p2"],
        semente_principal=SEMENTE_PRINCIPAL,
        nome_da_fase="Final",
    )
    assert de_novo.auditado.duelo.history == final.auditado.duelo.history
    assert de_novo.auditado.trace.records == final.auditado.trace.records
    outra = disputar_copa(participantes)
    assert list(outra.chave) == list(copa.chave)
    assert outra.campeao.id == copa.campeao.id


# --- 3. Isolamento ---------------------------------------------------------


def _impressao(pasta: Path) -> dict:
    if not pasta.exists():
        return {}
    return {
        str(arq.relative_to(pasta)): hashlib.sha256(arq.read_bytes()).hexdigest()
        for arq in sorted(pasta.rglob("*"))
        if arq.is_file()
    }


def test_nenhum_save_slot_ou_gladiador_e_tocado(monkeypatch, tmp_path, copa):
    reais = Path(save_manager.__file__).resolve().parents[2] / "saves"
    antes = _impressao(reais)
    saves = tmp_path / "saves"
    saves.mkdir()
    monkeypatch.setattr(save_manager, "SAVE_DIR", str(saves))

    escritos = escrever_tudo(copa, tmp_path / "copa_02", pdf=False)

    assert list(saves.iterdir()) == []
    assert arena_setup.list_gladiators() == []
    assert _impressao(reais) == antes
    nomes = {p.name for p in escritos if p.exists()}
    assert {"relatorio.md", "final_detalhada.md", "final_trace.json", "dashboard.html"} <= nomes


def test_cada_partida_comeca_de_recursos_cheios(copa):
    for partida in todas(copa):
        inicio = partida.auditado.trace.de("rodada_inicio")[0]["estado"]
        for lado in SIDES:
            estado = inicio[lado]
            assert estado["hp"] == estado["hp_max"] and estado["mp"] == estado["mp_max"]
            assert estado["recargas"] == {} and estado["efeitos"] == []
            assert estado["buffs"] == {}


# --- 4. Auditoria ----------------------------------------------------------


def test_auditoria_da_final_fiel_ao_motor(copa):
    final = copa.fases["final"][0]
    assert all(ok for _, ok in final.fidelidade), final.fidelidade
    assert all(ok for _, ok in final.coerencia), final.coerencia
    assert final.puro.duelo.result == final.auditado.duelo.result


def test_nenhuma_chamada_extra_ao_gerador(copa):
    for partida in todas(copa):
        rolagens = partida.auditado.trace.de("rolagem")
        assert len(rolagens) == partida.auditado.rng.chamadas
        assert partida.puro.rng.getstate() == partida.auditado.rng.getstate()
        assert all(ok for _, ok in partida.fidelidade), partida.titulo


def test_dashboard_sem_marcador_e_com_os_dados(tmp_path, copa):
    escrever_tudo(copa, tmp_path, pdf=False)
    pagina = (tmp_path / "dashboard.html").read_text(encoding="utf-8")
    assert "@@" not in pagina
    marca = '<script id="dados" type="application/json">'
    inicio = pagina.index(marca) + len(marca)
    dados = json.loads(pagina[inicio : pagina.index("</script>", inicio)])
    assert len(dados["participantes"]) == 64 and len(dados["partidas"]) == 63
    assert pagina.count('class="jogo"') == 63
    assert dados["campeao"] == copa.campeao.id
