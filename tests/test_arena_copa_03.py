"""Copa Arena 03: 64 Guerreiros extraídos de runs PvE reais, e o mata-mata deles.

O que estes testes fixam:

1. a variante experimental: nove grupos com as quotas pedidas, a agenda de risco
   ordenada e limitada, a matriz de extração que só acrescenta preservação, e a
   escalada mudando decisões em estados que uma run real alcança;
2. a variante não toca no BotPadrão oficial: com a linha canônica ela reproduz o
   trace dele, e as constantes voltam ao valor canônico mesmo com erro;
3. a geração real: uma tentativa sai do `BotPadrao` desde a criação canônica, as
   seeds são estáveis e únicas, a fila aceita na ordem das tentativas e o
   checkpoint retoma sem repetir run;
4. os 64 entregues: snapshots íntegros e reconstruíveis com a mesma build, OP
   entre 20 e 30, distribuição por grupo, nicknames e `runs.jsonl` coerentes;
5. a Copa: 63 confrontos, cada fase com os vencedores da anterior, seeds,
   reprodução, isolamento de saves e a fidelidade da auditoria.
"""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest

import tools.bot_padrao as bp
from src.content.extraction import was_extracted
from src.engine import arena_setup
from src.mechanics.pvp_duel import SIDES
from src.sim.arena import limpar_cache, overall_power
from src.sim.bot import evaluators
from src.storage import save_manager
from tools import arena_copa_03_geracao as ger
from tools.arena_copa_02 import FASES, NICKS
from tools.arena_copa_03 import (
    ARQUIVO_PILOTO,
    ARQUIVO_PLANO,
    ARQUIVO_RUNS_PREENCHIMENTO,
    PASTA,
    diagnostico_rng,
    disputar_copa,
    formar_participantes,
    ler_gladiadores,
    semente_derivada,
    todas,
)
from tools.arena_copa_teste import jogar_partida, semente_da_partida

ENTREGUES = (PASTA / "gladiadores.json").exists()
entregues = pytest.mark.skipif(not ENTREGUES, reason="a geração da Copa 03 não foi finalizada")


# --- 1. A variante experimental -------------------------------------------------


def test_nove_grupos_com_as_quotas_pedidas():
    assert sum(ger.QUOTAS.values()) == 64
    assert len(ger.QUOTAS) == 9
    por_perfil = Counter()
    por_politica = Counter()
    for (perfil, politica), quota in ger.QUOTAS.items():
        por_perfil[perfil] += quota
        por_politica[politica] += quota
    assert por_perfil == {"conservador": 22, "moderado": 21, "hardcore": 21}
    assert por_politica == {"survival": 22, "offense": 21, "economy": 21}
    assert ger.QUOTAS[("conservador", "survival")] == 8


def test_agenda_ordenada_progressiva_e_limitada():
    assert ger.linha_base("conservador") == ger.LINHA_CANONICA
    for andar in range(1, 201):
        c, m, h = (ger.linha_de_aposta(p, andar) for p in ger.PERFIS)
        assert c > m > h, andar
        for perfil in ger.PERFIS:
            linha = ger.linha_de_aposta(perfil, andar)
            assert ger.PISO[perfil] <= linha <= ger.linha_base(perfil)
            if andar > 1:
                assert linha <= ger.linha_de_aposta(perfil, andar - 1)
    for perfil in ger.PERFIS:
        assert ger.linha_de_aposta(perfil, 200) == ger.PISO[perfil]
        assert ger.linha_de_aposta(perfil, 6) < ger.linha_de_aposta(perfil, 5)


def test_matriz_de_extracao_so_acrescenta_e_segue_o_risco():
    canonica = ger.MATRIZ_CANONICA
    preservadas = {}
    for perfil in ger.PERFIS:
        matriz = ger.matriz_de_extracao(perfil)
        assert set(matriz) == set(canonica)
        assert all(matriz[k] for k, v in canonica.items() if v)
        preservadas[perfil] = {k for k, v in matriz.items() if v}
    assert ger.matriz_de_extracao("hardcore") is canonica
    assert preservadas["conservador"] > preservadas["moderado"] > preservadas["hardcore"]


def test_a_escalada_muda_decisoes_alcancaveis():
    bot = ger.BotExperimental(12, "hardcore", "offense", max_andar=6)
    bot.jogar()
    assert bot.decisoes > 0 and bot.ilegais == 0
    assert sum(bot.divergencias.values()) > 0
    assert any(par.endswith("→lutar") for par in bot.divergencias)
    assert bot.orcamentos_divergentes > 0


# --- 2. O BotPadrão oficial fica intacto ----------------------------------------


@pytest.mark.parametrize("semente", [12, 13])
def test_com_a_linha_canonica_a_variante_e_o_botpadrao(semente):
    # Cada bot joga logo depois de nascer: o construtor do BotPadrão semeia o
    # `random` global, como numa run de verdade (um processo por run).
    trace_oficial = bp.BotPadrao("warrior", semente, 5, bp.PERFIS["conservador"]).jogar()
    variante = ger.BotExperimental(semente, "conservador", "survival", max_andar=5)
    assert variante.jogar() == trace_oficial
    assert sum(variante.divergencias.values()) == 0


def test_constantes_voltam_ao_canonico_mesmo_com_erro(monkeypatch):
    def explode(self, andar):
        assert evaluators.HP_DE_APOSTA == ger.linha_de_aposta("moderado", andar)
        assert evaluators._MATRIZ == ger.matriz_de_extracao("moderado")
        raise RuntimeError("falha simulada")

    monkeypatch.setattr(bp.BotPadrao, "_jogar_andar", explode)
    bot = ger.BotExperimental(5, "moderado", "economy", max_andar=3)
    with pytest.raises(RuntimeError):
        bot.jogar()
    assert evaluators.HP_DE_APOSTA == ger.LINHA_CANONICA
    assert bp.HP_CRITICO == ger.LINHA_CANONICA
    assert evaluators._MATRIZ is ger.MATRIZ_CANONICA


# --- 3. A geração real ----------------------------------------------------------


def test_uma_tentativa_real_pelo_botpadrao():
    registro = ger.executar("moderado", "offense", 2)
    assert registro["seed"] == ger.semente_da_run("moderado", "offense", 2)
    assert registro["versao"] == "v2" and registro["teto"] == ger.TETO
    assert registro["desfecho"] == "morreu" and registro["qualificada"] is False
    assert registro["nivel_por_andar"][0] == 1
    assert registro["ilegais"] == 0 and registro["linha_restaurada"]
    de_novo = ger.executar("moderado", "offense", 2)
    assert de_novo | {"tempo_s": registro["tempo_s"]} == registro


def test_seeds_estaveis_unicas_e_de_namespace_proprio():
    sementes = {
        ger.semente_da_run(perfil, politica, k)
        for perfil, politica in ger.GRUPOS
        for k in range(1, 401)
    }
    assert len(sementes) == 9 * 400
    v1 = hashlib.sha256(f"{ger.SEMENTE_PRINCIPAL}:hardcore:survival:3".encode()).digest()
    assert ger.semente_da_run("hardcore", "survival", 3) != int.from_bytes(v1[:8], "big")


def test_faixa_de_op_inclusiva():
    assert ger.na_faixa(20.0) and ger.na_faixa(30.0) and ger.na_faixa(25.3)
    assert not ger.na_faixa(19.99) and not ger.na_faixa(30.01)


def _registro(perfil, politica, k, qualificada):
    return {
        "perfil": perfil,
        "politica": politica,
        "tentativa": k,
        "seed": ger.semente_da_run(perfil, politica, k),
        "desfecho": "extraiu" if qualificada else "morreu",
        "qualificada": qualificada,
        "op": 25.0 if qualificada else None,
    }


def test_a_fila_aceita_na_ordem_das_tentativas_sem_lacuna():
    grupo = ger.Grupo("hardcore", "survival", 2, {}, set())
    grupo.concluidas[1] = _registro("hardcore", "survival", 1, True)
    grupo.concluidas[3] = _registro("hardcore", "survival", 3, True)
    assert grupo.aceitas() == [1] and not grupo.completo
    assert grupo.proxima() == 2
    grupo.concluidas[2] = _registro("hardcore", "survival", 2, False)
    assert grupo.aceitas() == [1, 3] and grupo.completo


def test_a_fila_distribui_proporcionalmente_as_vagas():
    fila = ger.montar_fila([])
    contagem = Counter()
    for _ in range(64):
        grupo = ger.escolher_grupo(fila)
        grupo.em_voo.add(grupo.proxima())
        contagem[grupo.chave] += 1
    assert contagem == Counter(ger.QUOTAS)


def test_o_checkpoint_recusa_duplicata():
    r = _registro("moderado", "economy", 1, False)
    with pytest.raises(RuntimeError, match="repetida"):
        ger.montar_fila([r, dict(r)])


def _falso_executar(chamadas):
    def executar(perfil, politica, k):
        chamadas.append((perfil, politica, k))
        r = _registro(perfil, politica, k, k % 3 == 0)
        if r["qualificada"]:
            r["_snapshot"] = {"player_class": "Warrior", "tentativa": k}
        return r

    return executar


def test_o_checkpoint_retoma_sem_repetir_runs(monkeypatch, tmp_path):
    quotas = {g: 2 for g in ger.GRUPOS[:3]}
    monkeypatch.setattr(ger, "QUOTAS", quotas)
    monkeypatch.setattr(ger, "GRUPOS", tuple(quotas))
    monkeypatch.setattr(ger, "executar", _falso_executar([]))
    inteira = tmp_path / "inteira"
    estado = ger.gerar(2, inteira, executor=ThreadPoolExecutor(2))
    assert all(g["completo"] for g in estado["grupos"].values())

    # O corte: as 5 primeiras linhas inteiras e meia linha da sexta.
    cortada = tmp_path / "cortada"
    (cortada / "candidatos").mkdir(parents=True)
    linhas = (inteira / "tentativas.jsonl").read_text().splitlines()
    (cortada / "tentativas.jsonl").write_text("\n".join(linhas[:5]) + "\n" + linhas[5][:20])
    assert len(ger.ler_tentativas(cortada)) == 5
    # A meia linha não é tentativa concluída: some antes de o log voltar a crescer.
    (cortada / "tentativas.jsonl").write_text("\n".join(linhas[:5]) + "\n")
    for nome in (inteira / "candidatos").iterdir():
        (cortada / "candidatos" / nome.name).write_text(nome.read_text())

    retomada = []
    monkeypatch.setattr(ger, "executar", _falso_executar(retomada))
    ger.gerar(2, cortada, executor=ThreadPoolExecutor(2))
    feitas = {(r["perfil"], r["politica"], r["tentativa"]) for r in map(json.loads, linhas[:5])}
    assert retomada and not feitas & set(retomada)
    final = ger.montar_fila(ger.ler_tentativas(cortada))
    assert {g: final[g].aceitas() for g in quotas} == {g: [3, 6] for g in quotas}


def _checkpoint_sintetico(qualificadas_do_hardcore: int) -> list[dict]:
    """Conservador e moderado com as quotas fechadas; o hardcore incompleto."""
    registros = []
    for perfil, politica in ger.GRUPOS:
        if perfil == "hardcore":
            for k in range(1, 8):
                registros.append(_registro(perfil, politica, k, k <= qualificadas_do_hardcore))
        else:
            for k in range(1, ger.QUOTAS[(perfil, politica)] + 2):
                registros.append(_registro(perfil, politica, k, True))
    return registros


def test_o_plano_de_preenchimento_e_deterministico_e_equilibrado():
    fila = ger.montar_fila(_checkpoint_sintetico(qualificadas_do_hardcore=3))
    plano = ger.plano_de_preenchimento(fila)
    assert plano == ger.plano_de_preenchimento(ger.montar_fila(_checkpoint_sintetico(3)))
    original = plano["selecao_original"]
    assert len(original) == 22 + 21 + 9
    vagas = plano["preenchimento"]
    assert len(original) + len(vagas) == ger.VAGAS
    # As qualificadas que sobraram no checkpoint (uma por grupo de C/M) vêm primeiro.
    assert [v["origem"] for v in vagas[:6]] == ["preenchimento_checkpoint"] * 6
    novas = [v for v in vagas if v["origem"] == "preenchimento_novo"]
    assert {v["perfil"] for v in vagas} <= set(ger.PERFIS_DO_PREENCHIMENTO)
    por_perfil = Counter(v["perfil"] for v in novas)
    assert abs(por_perfil["conservador"] - por_perfil["moderado"]) <= 1
    politicas = Counter(s["politica"] for s in original + vagas)
    assert max(politicas.values()) - min(politicas.values()) <= 1
    chaves = [(s["perfil"], s["politica"], s.get("tentativa")) for s in original]
    assert len(set(chaves)) == len(chaves)


def test_o_preenchimento_retoma_e_confere_o_plano(monkeypatch, tmp_path):
    with open(tmp_path / "tentativas.jsonl", "w") as f:
        for r in _checkpoint_sintetico(qualificadas_do_hardcore=2):
            f.write(json.dumps(r) + "\n")
    chamadas = []
    monkeypatch.setattr(ger, "executar", _falso_executar(chamadas))
    plano = ger.preencher(2, tmp_path, executor=ThreadPoolExecutor(2))
    assert all(g.completo for g in ger.fila_do_preenchimento(plano, tmp_path).values())
    primeiras = plano["primeira_tentativa"]
    assert all(k >= primeiras[f"{p}-{pol}"] for p, pol, k in chamadas)
    feitas = len(ger.ler_tentativas(tmp_path, ger.LOG_DO_PREENCHIMENTO))
    # Retomar com o preenchimento completo não roda nada e confere o plano.
    chamadas.clear()
    assert ger.preencher(2, tmp_path, executor=ThreadPoolExecutor(2)) == plano
    assert chamadas == []
    assert len(ger.ler_tentativas(tmp_path, ger.LOG_DO_PREENCHIMENTO)) == feitas
    # Um checkpoint original que mudou depois do plano é recusado.
    with open(tmp_path / "tentativas.jsonl", "a") as f:
        f.write(json.dumps(_registro("hardcore", "survival", 8, True)) + "\n")
    with pytest.raises(RuntimeError, match="mudou"):
        ger.preencher(2, tmp_path, executor=ThreadPoolExecutor(2))


# --- 4. Os 64 entregues ---------------------------------------------------------


@pytest.fixture(scope="module")
def gladiadores():
    return ler_gladiadores()


@entregues
def test_os_64_snapshots_sao_integros(gladiadores):
    assert [g["id"] for g in gladiadores] == [f"W{i:02d}" for i in range(1, 65)]
    chaves = [(g["perfil"], g["politica"], g["tentativa"]) for g in gladiadores]
    assert len(set(chaves)) == 64
    plano = json.loads((PASTA / ARQUIVO_PLANO).read_text(encoding="utf-8"))
    originais = [g for g in gladiadores if g["origem"] == "original"]
    assert [(g["perfil"], g["politica"], g["tentativa"]) for g in originais] == [
        (s["perfil"], s["politica"], s["tentativa"]) for s in plano["selecao_original"]
    ]
    preenchidos = [g for g in gladiadores if g["origem"].startswith("preenchimento")]
    assert len(originais) + len(preenchidos) == 64
    assert {g["perfil"] for g in preenchidos} <= set(ger.PERFIS_DO_PREENCHIMENTO)
    assert [(g["perfil"], g["politica"]) for g in preenchidos] == [
        (v["perfil"], v["politica"]) for v in plano["preenchimento"]
    ]
    todos = {nick for lista in NICKS.values() for nick in lista}
    assert {g["nick"] for g in gladiadores} == todos
    arquivos = sorted((PASTA / "snapshots").glob("*.json"))
    assert [a.stem for a in arquivos] == [g["id"] for g in gladiadores]
    for g in gladiadores:
        texto = (PASTA / g["snapshot"]).read_text(encoding="utf-8")
        assert hashlib.sha256(texto.encode()).hexdigest() == g["sha256"], g["id"]
        snapshot = json.loads(texto)
        heroi = ger.reconstruir(snapshot)
        assert heroi.get_classname() == "Warrior" and was_extracted(heroi), g["id"]
        assert snapshot["extracted_on_floor"] == g["andar_de_extracao"]
        assert snapshot["extraction_keys"] == 0 and heroi.get_level() == g["nivel"]
        assert ger.na_faixa(g["op"]), g["id"]


@entregues
@pytest.mark.parametrize("indice", [0, 63])
def test_a_reconstrucao_mantem_a_build(gladiadores, indice):
    g = gladiadores[indice]
    snapshot = json.loads((PASTA / g["snapshot"]).read_text(encoding="utf-8"))
    heroi = ger.reconstruir(snapshot)
    assert ger._conferir_reconstrucao(heroi, snapshot) == []
    build = ger._build(heroi)
    assert build["deck"] == g["deck"] and build["passivas"] == g["passivas"]
    assert build["equipamento"] == g["equipamento"]


@entregues
def test_o_op_gravado_e_a_medicao_canonica(gladiadores):
    limpar_cache()
    g = min(gladiadores, key=lambda g: g["op"])
    snapshot = json.loads((PASTA / g["snapshot"]).read_text(encoding="utf-8"))
    assert overall_power(ger.reconstruir(snapshot), usar_cache=False).nivel_equivalente == g["op"]


def _ler_jsonl(nome: str) -> list[dict]:
    return [json.loads(x) for x in (PASTA / nome).read_text(encoding="utf-8").splitlines() if x]


@entregues
def test_runs_jsonl_coerente_com_os_aceitos(gladiadores):
    runs = _ler_jsonl("runs.jsonl")
    novas = _ler_jsonl(ARQUIVO_RUNS_PREENCHIMENTO)
    plano = json.loads((PASTA / ARQUIVO_PLANO).read_text(encoding="utf-8"))
    todas_as_runs = runs + novas
    assert len({r["seed"] for r in todas_as_runs}) == len(todas_as_runs)
    assert all(r["versao"] == "v2" for r in todas_as_runs)
    assert sum(r.get("ilegais", 0) for r in todas_as_runs) == 0
    assert all(r.get("linha_restaurada", True) for r in todas_as_runs)
    assert {r["fase"] for r in runs} == {"geracao"} and {r["fase"] for r in novas} == {
        "preenchimento"
    }
    assert plano["tentativas_da_geracao_original"] == len(runs)
    selecionadas = {
        (r["perfil"], r["politica"], r["tentativa"]) for r in todas_as_runs if "selecionada" in r
    }
    assert selecionadas == {(g["perfil"], g["politica"], g["tentativa"]) for g in gladiadores}
    for perfil, politica in ger.GRUPOS:
        chave = f"{perfil}-{politica}"
        do_grupo = sorted(
            r["tentativa"] for r in runs if (r["perfil"], r["politica"]) == (perfil, politica)
        )
        lacunas = plano["interrompidas"].get(chave, [])
        assert sorted(do_grupo + lacunas) == list(range(1, max(do_grupo) + 1))
        if chave in plano["primeira_tentativa"]:
            depois = sorted(
                r["tentativa"] for r in novas if (r["perfil"], r["politica"]) == (perfil, politica)
            )
            assert not depois or depois[0] == plano["primeira_tentativa"][chave]
    for r in todas_as_runs:
        if "selecionada" in r:
            assert r["qualificada"] and ger.na_faixa(r["op"])
    piloto = (PASTA / ARQUIVO_PILOTO).read_text().splitlines()
    assert piloto and all(json.loads(linha)["versao"] == "v1" for linha in piloto)


# --- 5. A Copa ------------------------------------------------------------------


@pytest.fixture(scope="module")
def copa():
    return disputar_copa(formar_participantes())


@entregues
def test_sessenta_e_tres_confrontos_e_um_campeao(copa):
    assert copa.interrompida is None
    for fase, quantas, _ in FASES:
        assert len(copa.fases[fase]) == quantas
    perdedores = [p.perdedor.id for p in todas(copa)]
    assert len(perdedores) == len(set(perdedores)) == 63
    assert {p.id for p in copa.participantes} - set(perdedores) == {copa.campeao.id}


@entregues
def test_cada_fase_recebe_os_vencedores_da_anterior(copa):
    estreia = [p.lados[s].id for p in copa.fases["fase64"] for s in SIDES]
    assert estreia == list(copa.chave)
    fases = [f for f, _, _ in FASES]
    for anterior, atual in zip(fases, fases[1:]):
        esperados = [p.vencedor.id for p in copa.fases[anterior]]
        assert [p.lados[s].id for p in copa.fases[atual] for s in SIDES] == esperados


@entregues
def test_seeds_e_reproducao(copa):
    for partida in todas(copa):
        assert partida.semente == semente_da_partida(
            partida.fase, partida.indice, ger.SEMENTE_PRINCIPAL
        )
    assert len({p.semente for p in todas(copa)}) == 63
    assert semente_derivada("chave") != semente_derivada("nomes")
    final = copa.fases["final"][0]
    de_novo = jogar_partida(
        "final",
        1,
        final.lados["p1"],
        final.lados["p2"],
        semente_principal=ger.SEMENTE_PRINCIPAL,
        nome_da_fase="Final",
    )
    assert de_novo.auditado.trace.records == final.auditado.trace.records


@entregues
def test_cada_partida_comeca_de_recursos_cheios(copa):
    for partida in todas(copa):
        estado = partida.auditado.trace.de("rodada_inicio")[0]["estado"]
        for lado in SIDES:
            assert estado[lado]["hp"] == estado[lado]["hp_max"]
            assert estado[lado]["mp"] == estado[lado]["mp_max"]
            assert estado[lado]["recargas"] == {} and estado[lado]["efeitos"] == []


@entregues
def test_auditoria_fiel_e_sem_sorteio_extra(copa):
    for partida in todas(copa):
        assert all(ok for _, ok in partida.fidelidade), partida.titulo
        assert all(ok for _, ok in partida.coerencia), partida.titulo
        assert len(partida.auditado.trace.de("rolagem")) == partida.auditado.rng.chamadas
        assert partida.puro.rng.getstate() == partida.auditado.rng.getstate()


@entregues
def test_o_diagnostico_de_rng_nao_mexe_na_copa(copa):
    final = copa.fases["final"][0]
    antes = (final.vencedor.id, final.auditado.duelo.history)
    vida = {p.id: p.heroi.get_hp() for p in copa.participantes}
    diagnostico = diagnostico_rng(copa, repeticoes=4)
    assert diagnostico[0]["chave"] == "final-1"
    assert (final.vencedor.id, final.auditado.duelo.history) == antes
    assert {p.id: p.heroi.get_hp() for p in copa.participantes} == vida


def _impressao(pasta: Path) -> dict:
    if not pasta.exists():
        return {}
    return {
        str(arq.relative_to(pasta)): hashlib.sha256(arq.read_bytes()).hexdigest()
        for arq in sorted(pasta.rglob("*"))
        if arq.is_file()
    }


@entregues
def test_nenhum_save_slot_ou_gladiador_e_tocado(monkeypatch, tmp_path, copa):
    from tools.arena_copa_03_relatorios import escrever_tudo

    reais = Path(save_manager.__file__).resolve().parents[2] / "saves"
    antes = _impressao(reais)
    saves = tmp_path / "saves"
    saves.mkdir()
    monkeypatch.setattr(save_manager, "SAVE_DIR", str(saves))
    pasta = tmp_path / "copa_03"
    pasta.mkdir()
    for nome in ("gladiadores.json", "runs.jsonl", ARQUIVO_PILOTO):
        (pasta / nome).write_bytes((PASTA / nome).read_bytes())
    escritos = escrever_tudo(copa, diagnostico_rng(copa, repeticoes=2), pasta, pdf=False)
    assert list(saves.iterdir()) == []
    assert arena_setup.list_gladiators() == []
    assert _impressao(reais) == antes
    nomes = {p.name for p in escritos}
    assert {"geracao.md", "relatorio.md", "final_detalhada.md", "dashboard.html"} <= nomes
    pagina = (pasta / "dashboard.html").read_text(encoding="utf-8")
    assert "@@" not in pagina and pagina.count('class="jogo"') == 63


# --- 6. Todos contra todos --------------------------------------------------------


def test_bradley_terry_ordena_e_centra():
    from tools.arena_copa_03_round_robin import bradley_terry

    ids = ["A", "B", "C"]
    vitorias = {
        ("A", "B"): 8,
        ("B", "A"): 2,
        ("B", "C"): 8,
        ("C", "B"): 2,
        ("A", "C"): 9,
        ("C", "A"): 1,
    }
    forca = bradley_terry(ids, vitorias)
    assert forca["A"] > forca["B"] > forca["C"]
    assert abs(sum(forca.values())) < 1e-9


@entregues
def test_o_rodizio_conserva_os_duelos_e_se_reproduz():
    from tools.arena_copa_03_round_robin import jogar_rodizio

    tres = formar_participantes()[:3]
    resultado = jogar_rodizio(tres, seeds=2)
    assert set(resultado) == {("W01", "W02"), ("W01", "W03"), ("W02", "W03")}
    assert all(r["a"] + r["b"] + r["inconclusivos"] == 2 for r in resultado.values())
    assert jogar_rodizio(tres, seeds=2) == resultado


@pytest.mark.skipif(
    not (PASTA / "round_robin.json").exists(), reason="o todos-contra-todos não foi publicado"
)
def test_o_todos_contra_todos_publicado_e_coerente():
    dados = json.loads((PASTA / "round_robin.json").read_text(encoding="utf-8"))
    assert len(dados["matriz"]) == 64 * 63 // 2
    assert all(
        r["a"] + r["b"] + r["inconclusivos"] == dados["seeds"] for r in dados["matriz"].values()
    )
    assert len({r["id"] for r in dados["ranking"]}) == 64
    forcas = [r["forca"] for r in dados["ranking"]]
    assert forcas == sorted(forcas, reverse=True)
