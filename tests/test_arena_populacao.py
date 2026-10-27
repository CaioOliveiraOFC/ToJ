"""A população offline da Arena: integridade, unicidade, elegibilidade e variedade.

O catálogo é o do jogo (`src/data/arena_populacao/`), gerado por
`tools/arena_offline_geracao.py`. Estes testes não geram nada: conferem o que
está publicado, com as regras canônicas de extração e reconstrução, e provam que
qualquer adulteração bloqueia o gladiador em vez de deixá-lo lutar.
"""

from __future__ import annotations

import hashlib
import json
import sys
from collections import Counter
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import tools.arena_copa_03_geracao as ger  # noqa: E402
import tools.arena_offline_geracao as geracao  # noqa: E402
from src.engine import arena_populacao as pop  # noqa: E402
from src.engine.arena_populacao import Populacao, PopulacaoInvalidaError  # noqa: E402
from src.sim.arena import assinatura_de_build  # noqa: E402

COPA_03 = ROOT / "reports" / "pvp" / "copa_03"


@pytest.fixture(scope="module")
def populacao() -> Populacao:
    return Populacao()


def _indice(populacao: Populacao) -> dict:
    return json.loads((populacao.pasta / "indice.json").read_text(encoding="utf-8"))


def _copia(populacao: Populacao, destino: Path, ids: list[str], mexer=None) -> Path:
    """Um catálogo pequeno com os mesmos bytes; `mexer(indice, pasta)` adultera."""
    indice = _indice(populacao)
    indice["gladiadores"] = [g for g in indice["gladiadores"] if g["id"] in ids]
    destino.mkdir(parents=True, exist_ok=True)
    for g in indice["gladiadores"]:
        (destino / g["arquivo"]).write_bytes((populacao.pasta / g["arquivo"]).read_bytes())
    if mexer is not None:
        mexer(indice, destino)
    (destino / "indice.json").write_text(json.dumps(indice, ensure_ascii=False), encoding="utf-8")
    return destino


class TestCatalogo:
    def test_tamanho_e_as_tres_classes(self, populacao):
        assert pop.TAMANHO_MINIMO <= len(populacao) <= pop.TAMANHO_MAXIMO
        por_classe = Counter(o.classe for o in populacao)
        assert set(por_classe) == {"warrior", "mage", "rogue"}
        assert min(por_classe.values()) >= 30, por_classe

    def test_cada_gladiador_confere_e_e_elegivel(self, populacao):
        for oponente in populacao:
            snapshot = populacao.conferir(oponente)
            assert snapshot["extracted_on_floor"] == oponente.andar_de_extracao
            assert snapshot["player_class"].lower() == oponente.classe

    def test_unicidade_de_id_nome_bytes_seed_e_build(self, populacao):
        builds = set()
        for oponente in populacao:
            heroi = pop.reconstruir(populacao.snapshot(oponente))
            builds.add(json.dumps(assinatura_de_build(heroi), sort_keys=True, default=str))
        for chave in ("id", "apelido", "sha256", "arquivo"):
            assert len({getattr(o, chave) for o in populacao}) == len(populacao), chave
        assert len({o.origem["seed"] for o in populacao}) == len(populacao)
        assert len(builds) == len(populacao)

    def test_nenhum_arquivo_fora_do_indice(self, populacao):
        no_disco = {p.name for p in populacao.pasta.iterdir()}
        assert no_disco == {o.arquivo for o in populacao} | {"indice.json"}

    def test_os_ids_seguem_a_classe(self, populacao):
        letra = {"warrior": "W", "mage": "M", "rogue": "R"}
        for oponente in populacao:
            assert oponente.id[0] == letra[oponente.classe]
            assert oponente.arquivo == f"{oponente.id}.json"

    def test_os_64_da_copa_03_entram_com_os_mesmos_bytes(self, populacao):
        copa = json.loads((COPA_03 / "gladiadores.json").read_text(encoding="utf-8"))
        da_copa = {
            o.origem["id_na_copa"]: o for o in populacao if o.origem.get("fonte") == "copa_03"
        }
        assert len(da_copa) == 64
        for g in copa["gladiadores"]:
            oponente = da_copa[g["id"]]
            assert oponente.sha256 == g["sha256"]
            original = (COPA_03 / g["snapshot"]).read_bytes()
            assert hashlib.sha256(original).hexdigest() == g["sha256"]
            assert (populacao.pasta / oponente.arquivo).read_bytes() == original

    def test_a_origem_de_cada_gladiador_e_rastreavel(self, populacao):
        for oponente in populacao:
            origem = oponente.origem
            assert origem["versao"] == ger.VERSAO
            assert origem["fonte"] in {"copa_03", "copa_03_fora_da_faixa", "arena_offline"}
            semente = ger.semente_da_run(
                oponente.perfil, oponente.politica, origem["tentativa"], oponente.classe
            )
            assert origem["seed"] == str(semente), oponente.id

    def test_variedade_de_classe_nivel_estilo_e_forca(self, populacao):
        niveis = [o.nivel for o in populacao]
        assert max(niveis) - min(niveis) >= 20
        assert len(set(niveis)) >= 12
        forcas = [o.op for o in populacao]
        assert max(forcas) - min(forcas) >= 20
        for classe in ("warrior", "mage", "rogue"):
            da_classe = [o for o in populacao if o.classe == classe]
            assert len({o.perfil for o in da_classe}) >= 2, classe
            assert len({o.politica for o in da_classe}) == 3, classe
        # Fora da faixa da Copa 03 (OP 20–30): a população não tem limite de OP.
        assert any(o.op > 30 for o in populacao) and any(o.op < 20 for o in populacao)


class TestGeracaoDeterministica:
    def test_os_apelidos_sao_ficticios_e_sorteados_com_semente_fixa(self, populacao):
        apelidos = [g["apelido"] for g in _indice(populacao)["gladiadores"]]
        assert apelidos == geracao.apelidos(len(apelidos))
        assert geracao.apelidos(5) == geracao.apelidos(5)
        copa = json.loads((COPA_03 / "gladiadores.json").read_text(encoding="utf-8"))
        assert not {g["nick"] for g in copa["gladiadores"]} & set(apelidos)

    def test_a_variedade_de_guerreiros_e_a_selecao_publicada(self, populacao):
        candidatos = geracao.extracoes_fora_da_faixa()
        escolhidos = geracao.selecionar_variedade(candidatos)
        assert escolhidos == geracao.selecionar_variedade(list(reversed(candidatos)))
        assert len(escolhidos) == geracao.VARIEDADE
        ops = sorted(r["op"] for r in candidatos)
        assert escolhidos[0]["op"] == ops[0] and escolhidos[-1]["op"] == ops[-1]
        publicados = {
            (o.perfil, o.politica, o.origem["tentativa"])
            for o in populacao
            if o.origem["fonte"] == "copa_03_fora_da_faixa"
        }
        assert publicados == {(r["perfil"], r["politica"], r["tentativa"]) for r in escolhidos}

    def test_a_seed_de_outra_classe_nunca_repete_a_do_guerreiro(self):
        for perfil, politica in ger.GRUPOS:
            guerreiro = ger.semente_da_run(perfil, politica, 1)
            assert guerreiro == ger.semente_da_run(perfil, politica, 1, "warrior")
            for classe in ("mage", "rogue"):
                assert ger.semente_da_run(perfil, politica, 1, classe) != guerreiro


class TestConferencia:
    """Adulterar o catálogo bloqueia; nunca vira gladiador montado pela metade."""

    def _tres(self, populacao):
        return [populacao.oponentes(c)[0].id for c in ("warrior", "mage", "rogue")]

    def test_arquivo_adulterado(self, populacao, tmp_path):
        alvo = self._tres(populacao)[1]

        def mexer(indice, pasta):
            arquivo = pasta / f"{alvo}.json"
            arquivo.write_bytes(arquivo.read_bytes().replace(b'"coins": ', b'"coins": 9', 1))

        pequena = Populacao(_copia(populacao, tmp_path, self._tres(populacao), mexer), (1, 256))
        with pytest.raises(PopulacaoInvalidaError, match="não confere"):
            pequena.gladiador(pequena.get(alvo))
        # Os outros continuam lutando.
        for outro in self._tres(populacao):
            if outro != alvo:
                assert pequena.gladiador(pequena.get(outro)).hero.get_hp() > 0

    def test_snapshot_reescrito_com_sha_novo_mas_sem_extracao(self, populacao, tmp_path):
        alvo = self._tres(populacao)[0]

        def mexer(indice, pasta):
            arquivo = pasta / f"{alvo}.json"
            dados = json.loads(arquivo.read_bytes())
            dados["extracted_on_floor"] = 0
            novo = geracao.publicado(dados)
            arquivo.write_bytes(novo)
            for g in indice["gladiadores"]:
                if g["id"] == alvo:
                    g["sha256"] = hashlib.sha256(novo).hexdigest()

        pequena = Populacao(_copia(populacao, tmp_path, self._tres(populacao), mexer), (1, 256))
        with pytest.raises(PopulacaoInvalidaError, match="extração"):
            pequena.gladiador(pequena.get(alvo))

    def test_classe_trocada_no_indice(self, populacao, tmp_path):
        alvo = self._tres(populacao)[2]

        def mexer(indice, pasta):
            for g in indice["gladiadores"]:
                if g["id"] == alvo:
                    g["classe"] = "mage"

        pequena = Populacao(_copia(populacao, tmp_path, self._tres(populacao), mexer), (1, 256))
        with pytest.raises(PopulacaoInvalidaError, match="classe"):
            pequena.conferir(pequena.get(alvo))

    @pytest.mark.parametrize(
        "mexer, motivo",
        [
            (lambda i, p: i["gladiadores"].append(dict(i["gladiadores"][0])), "repetido"),
            (lambda i, p: i["gladiadores"][0].update(arquivo="../fora.json"), "fora do catálogo"),
            (lambda i, p: i["gladiadores"][0].update(classe="paladin"), "classe desconhecida"),
            (lambda i, p: i["gladiadores"][0].update(perfil="suicida"), "estilo"),
            (lambda i, p: i["gladiadores"][0].pop("sha256"), "ilegível"),
            (lambda i, p: i.update(versao=2), "outra versão"),
        ],
    )
    def test_indice_invalido(self, populacao, tmp_path, mexer, motivo):
        pasta = _copia(populacao, tmp_path, self._tres(populacao), mexer)
        with pytest.raises(PopulacaoInvalidaError, match=motivo):
            Populacao(pasta, (1, 256))

    def test_tamanho_fora_dos_limites(self, populacao, tmp_path):
        pasta = _copia(populacao, tmp_path, self._tres(populacao))
        with pytest.raises(PopulacaoInvalidaError, match="fora de"):
            Populacao(pasta)

    def test_o_gladiador_e_uma_copia_pronta(self, populacao):
        oponente = populacao.oponentes("rogue")[0]
        a, b = populacao.gladiador(oponente), populacao.gladiador(oponente)
        assert a.hero is not b.hero
        assert a.name == oponente.apelido
        assert (a.hero.get_hp(), a.hero.get_mp()) == (a.hero.base_hp, a.hero.base_mp)
        a.hero._hp = 1
        assert populacao.gladiador(oponente).hero.get_hp() == b.hero.base_hp
