"""O manifesto da versão e o gate de publicação (contrato multiplayer, §1, §2, §6, §7).

- O manifesto da versão declarada confere com o código desta árvore.
- O escopo medido cobre tudo o que o servidor carrega para jogar uma partida.
- Mudança em regra, catálogo, persistência ou protocolo sem manifesto novo:
  publicação bloqueada, e a instalação divergente não sobe servidor.
- Um identificador nomeia um só conteúdo; manifesto publicado não muda.
- O CI bloqueia build e distribuição quando o gate falha.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.multiplayer import manifesto as mf  # noqa: E402
from src.multiplayer import versao  # noqa: E402
from src.multiplayer.servidor import ServidorAutoritativo  # noqa: E402
from tests._multiplayer_apoio import ROOT, acervo  # noqa: E402
from tools import multiplayer_manifesto as ferramenta  # noqa: E402

WORKFLOWS = ROOT / ".github" / "workflows"


def _copia(destino: Path) -> Path:
    """Uma cópia da árvore medida (o `src/`), para estragar sem tocar no repositório."""
    shutil.copytree(ROOT / "src", destino / "src", ignore=shutil.ignore_patterns("__pycache__"))
    return destino


def _acrescenta(caminho: Path, texto: str = "\n") -> None:
    caminho.write_bytes(caminho.read_bytes() + texto.encode())


def _declara(raiz: Path, **valores) -> None:
    """Reescreve constantes de `versao.py` na cópia."""
    arquivo = raiz / "src" / "multiplayer" / "versao.py"
    texto = arquivo.read_text(encoding="utf-8")
    for nome, valor in valores.items():
        antigo = f"{nome} = {json.dumps(getattr(versao, nome))}"
        assert antigo in texto
        texto = texto.replace(antigo, f"{nome} = {json.dumps(valor)}")
    arquivo.write_text(texto, encoding="utf-8")


# --- o manifesto desta árvore ---------------------------------------------------------


def test_a_instalacao_confere_com_o_manifesto_da_versao_declarada():
    identidade = mf.manifesto_da_instalacao().identidade.como_dict()
    assert {campo: identidade[campo] for campo in versao.declarados()} == versao.declarados()
    assert ferramenta.verificar(ROOT, usar_git=False) == []


def test_o_gate_tambem_passa_com_git():
    if shutil.which("git") is None:
        pytest.skip("git ausente")
    assert ferramenta.verificar(ROOT) == []


def test_o_manifesto_cobre_os_grupos_e_so_o_escopo():
    manifesto = mf.manifesto_da_instalacao()
    arquivos = dict(manifesto.arquivos)
    grupos = {mf.grupo_de(a) for a in arquivos}
    assert grupos == set(mf.ESCOPO)
    assert "src/multiplayer/versao.py" not in arquivos
    assert not any(a.startswith("src/multiplayer/manifestos/") for a in arquivos)
    assert not any(a.startswith(("src/ui/", "src/sim/")) for a in arquivos)
    assert {"src/data/skills.json", "src/data/items.json", "src/mechanics/combat.py"} <= set(
        arquivos
    )
    assert mf.grupo_de("src/mechanics/pvp_duel.py") == "regras"
    assert mf.grupo_de("src/data/passives.json") == "catalogos"
    assert mf.grupo_de("src/multiplayer/gladiadores.py") == "persistencia"
    assert mf.grupo_de("src/multiplayer/protocolo.py") == "protocolo"
    assert mf.grupo_de("src/multiplayer/servidor.py") == "servidor"


def test_o_escopo_cobre_tudo_o_que_o_servidor_carrega_para_jogar():
    """Num processo limpo: sobe o servidor, joga uma partida pela rede e lista os módulos."""
    programa = """
import json, sys
sys.path.insert(0, sys.argv[1])
from src.mechanics.pvp_duel import DuelAction
from src.multiplayer.gladiadores import AcervoDeGladiadores
from src.multiplayer.servidor import ServidorAutoritativo
from src.multiplayer.cliente import ClienteMultiplayer
from src.multiplayer.transporte import RedeLocal

class Ataca:
    def choose(self, view):
        return DuelAction.attack()

pasta = sys.argv[1] + "/reports/pvp/copa_03/snapshots/"
acervo = AcervoDeGladiadores.de_snapshots(
    {g: json.load(open(pasta + g + ".json")) for g in ("W23", "W64")}
)
srv = ServidorAutoritativo.da_instalacao(acervo)
rede = RedeLocal(srv)
for conexao, nome, gladiador in (("c1", "ana", "W23"), ("c2", "bia", "W64")):
    cli = ClienteMultiplayer(srv.identidade, nome, Ataca())
    rede.conectar(conexao, cli)
    rede.enviar(conexao, cli.ola())
    rede.enviar(conexao, cli.entrar_na_fila(gladiador))
assert srv.resultados.classificaveis(), "a partida não terminou"
print(json.dumps(sorted(
    (nome, getattr(m, "__file__", None)) for nome, m in sys.modules.items()
)))
"""
    feito = subprocess.run(
        [sys.executable, "-c", programa, str(ROOT)],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=True,
    )
    carregados = json.loads(feito.stdout)
    nomes = {nome for nome, _ in carregados}
    assert not any(n == "src.ui" or n.startswith(("src.ui.", "src.sim.")) for n in nomes)
    assert "rich" not in nomes and "pyfiglet" not in nomes

    fora = []
    for nome, arquivo in carregados:
        if not nome.startswith("src") or arquivo is None:
            continue
        relativo = Path(arquivo).resolve().relative_to(ROOT).as_posix()
        if relativo != "src/multiplayer/versao.py" and mf.grupo_de(relativo) is None:
            fora.append(relativo)
    assert not fora, f"O servidor carrega código fora do manifesto: {fora}"


# --- mudança sem manifesto: publicação bloqueada ----------------------------------------


@pytest.mark.parametrize(
    "arquivo",
    [
        "src/data/skills.json",
        "src/data/items.json",
        "src/mechanics/combat.py",
        "src/mechanics/pvp_duel.py",
        "src/content/passives.py",
        "src/storage/save_manager.py",
        "src/multiplayer/protocolo.py",
    ],
)
def test_mudanca_em_regra_ou_catalogo_sem_atualizar_o_manifesto_bloqueia(tmp_path, arquivo):
    raiz = _copia(tmp_path)
    assert ferramenta.verificar(raiz, usar_git=False) == []
    _acrescenta(raiz / arquivo, "\n" if arquivo.endswith(".json") else "\n# mudança\n")

    problemas = ferramenta.verificar(raiz, usar_git=False)
    assert any(arquivo in p and "sem atualizar o manifesto" in p for p in problemas), problemas
    # O código de saída é o que reprova o passo do CI.
    assert ferramenta.main(["verificar", "--raiz", str(raiz), "--sem-git"]) == 1
    # E a instalação divergente não sobe servidor.
    with pytest.raises(mf.InstalacaoDivergenteError, match=arquivo):
        ServidorAutoritativo.da_instalacao(
            acervo(), raiz=raiz, pasta=raiz / "src/multiplayer/manifestos"
        )


def test_arquivo_novo_ou_removido_no_escopo_bloqueia(tmp_path):
    raiz = _copia(tmp_path)
    (raiz / "src/mechanics/regra_nova.py").write_text("X = 1\n", encoding="utf-8")
    (raiz / "src/data/arena_benchmark_v1.json").unlink()
    problemas = ferramenta.verificar(raiz, usar_git=False)
    assert any("regra_nova.py" in p and "arquivo novo" in p for p in problemas)
    assert any("arena_benchmark_v1.json" in p and "não existe" in p for p in problemas)


def test_o_executavel_do_gate_sai_com_erro(tmp_path):
    """O passo do CI chama o script; o código de saída dele é o bloqueio."""
    raiz = _copia(tmp_path)
    comando = [sys.executable, str(ROOT / "tools/multiplayer_manifesto.py"), "verificar"]
    comando += ["--raiz", str(raiz), "--sem-git"]
    assert subprocess.run(comando, capture_output=True, cwd=ROOT).returncode == 0
    _acrescenta(raiz / "src/shared/formulas.py", "\n# mudança\n")
    feito = subprocess.run(comando, capture_output=True, text=True, cwd=ROOT)
    assert feito.returncode == 1
    assert "BLOQUEADA" in feito.stdout and "src/shared/formulas.py" in feito.stdout


def test_o_que_nao_e_gameplay_nao_bloqueia(tmp_path):
    raiz = _copia(tmp_path)
    _acrescenta(raiz / "src/ui/renderer.py", "\n# só apresentação\n")
    _acrescenta(raiz / "src/sim/runner.py", "\n# ferramenta de medição\n")
    _acrescenta(raiz / "src/multiplayer/versao.py", "\n# comentário na declaração\n")
    assert ferramenta.verificar(raiz, usar_git=False) == []


def test_fim_de_linha_do_checkout_nao_muda_a_versao(tmp_path):
    raiz = _copia(tmp_path)
    alvo = raiz / "src/mechanics/combat.py"
    alvo.write_bytes(alvo.read_bytes().replace(b"\n", b"\r\n"))
    assert ferramenta.verificar(raiz, usar_git=False) == []


def test_declaracao_diferente_do_manifesto_bloqueia(tmp_path):
    raiz = _copia(tmp_path)
    _declara(raiz, REGRAS_DE_COMBATE="duelo-9")
    problemas = ferramenta.verificar(raiz, usar_git=False)
    assert any("`regras`" in p for p in problemas)


def test_tag_de_publicacao_precisa_ser_a_versao_declarada():
    certa = f"v{versao.VERSAO_DO_JOGO}"
    assert ferramenta.verificar(ROOT, tag=certa, usar_git=False) == []
    problemas = ferramenta.verificar(ROOT, tag="v9.9.9", usar_git=False)
    assert any("v9.9.9" in p for p in problemas)


# --- um identificador, um conteúdo --------------------------------------------------------


def test_regras_novas_exigem_identificador_de_regras_novo(tmp_path):
    raiz = _copia(tmp_path)
    _acrescenta(raiz / "src/mechanics/combat.py", "\n# regra mudou\n")
    _declara(raiz, VERSAO_DO_JOGO="0.4.0-arena.99")

    caminho, problemas = ferramenta.gerar(raiz, usar_git=False)
    assert caminho is None
    assert any("`regras`" in p and "duelo-1" in p for p in problemas), problemas

    _declara(raiz, REGRAS_DE_COMBATE="duelo-99")
    caminho, problemas = ferramenta.gerar(raiz, usar_git=False)
    assert problemas == [] and caminho.name == "0.4.0-arena.99.json"
    assert ferramenta.verificar(raiz, usar_git=False) == []


def test_catalogo_novo_com_versao_nova_mantem_o_identificador_de_regras(tmp_path):
    raiz = _copia(tmp_path)
    _acrescenta(raiz / "src/data/items.json")
    _declara(raiz, VERSAO_DO_JOGO="0.4.0-arena.99")
    caminho, problemas = ferramenta.gerar(raiz, usar_git=False)
    assert problemas == []
    antigo = mf.carregar(versao.VERSAO_DO_JOGO, raiz / "src/multiplayer/manifestos")
    novo = mf.carregar("0.4.0-arena.99", raiz / "src/multiplayer/manifestos")
    assert novo.identidade.regras == antigo.identidade.regras
    assert dict(novo.identidade.grupos)["regras"] == dict(antigo.identidade.grupos)["regras"]
    assert dict(novo.identidade.grupos)["catalogos"] != dict(antigo.identidade.grupos)["catalogos"]


def test_esquema_e_protocolo_tambem_nomeiam_um_so_conteudo(tmp_path):
    raiz = _copia(tmp_path)
    _acrescenta(raiz / "src/storage/save_manager.py", "\n# formato mudou\n")
    _acrescenta(raiz / "src/multiplayer/protocolo.py", "\n# mensagem mudou\n")
    _declara(raiz, VERSAO_DO_JOGO="0.4.0-arena.99")
    _, problemas = ferramenta.gerar(raiz, usar_git=False)
    assert any("`esquema_gladiador`" in p for p in problemas)
    assert any("`protocolo`" in p for p in problemas)


# --- manifesto publicado é imutável --------------------------------------------------------


def _git(raiz: Path, *argumentos: str) -> None:
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=teste",
            "-c",
            "user.email=teste@example.invalid",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "tag.gpgsign=false",
            *argumentos,
        ],
        cwd=raiz,
        check=True,
        capture_output=True,
    )


@pytest.fixture
def publicada(tmp_path):
    """Uma cópia da árvore com a versão atual publicada (tag `v<versão>`)."""
    if shutil.which("git") is None:
        pytest.skip("git ausente")
    raiz = _copia(tmp_path)
    _git(raiz, "init", "-q")
    _git(raiz, "add", "-A")
    _git(raiz, "commit", "-q", "-m", "publicação")
    _git(raiz, "tag", f"v{versao.VERSAO_DO_JOGO}")
    return raiz


def test_publicada_e_coerente_passa_no_gate(publicada):
    assert ferramenta.verificar(publicada) == []


def test_versao_publicada_nao_pode_ser_regerada_com_outro_conteudo(publicada):
    _acrescenta(publicada / "src/mechanics/combat.py", "\n# regra mudou depois\n")
    caminho, problemas = ferramenta.gerar(publicada)
    assert caminho is None
    assert any("já foi publicada" in p for p in problemas)
    assert any("mudou depois" in p for p in ferramenta.verificar(publicada))


def test_manifesto_publicado_alterado_ou_apagado_bloqueia(publicada):
    pasta = publicada / "src/multiplayer/manifestos"
    arquivo = pasta / f"{versao.VERSAO_DO_JOGO}.json"

    # Mudar o código e refazer o manifesto "por fora" do gate.
    _acrescenta(publicada / "src/mechanics/combat.py", "\n# regra mudou depois\n")
    caminho, problemas = ferramenta.gerar(publicada, usar_git=False)
    assert problemas == []
    assert any("foi alterado" in p for p in ferramenta.verificar(publicada))

    arquivo.unlink()
    problemas = ferramenta.verificar(publicada)
    assert any("foi apagado" in p for p in problemas)
    assert any("Não existe manifesto" in p for p in problemas)


def test_conferir_imutabilidade():
    assert mf.conferir_imutabilidade({"1": "a"}, {"1": "a", "2": "b"}) == []
    assert mf.conferir_imutabilidade({"1": "a"}, {"1": "b"}) != []
    assert mf.conferir_imutabilidade({"1": "a"}, {}) != []


# --- leitura sem tolerância -----------------------------------------------------------------


def test_manifesto_ilegivel_ou_inconsistente_e_recusado():
    dados = json.loads(mf.caminho_do_manifesto(versao.VERSAO_DO_JOGO).read_text())
    extra = {**dados, "compatibilidade": "relaxada"}
    with pytest.raises(mf.ManifestoInvalidoError):
        mf.Manifesto.de_dict(extra)
    torto = {**dados, "arquivos": {**dados["arquivos"], "src/mechanics/combat.py": "0" * 64}}
    with pytest.raises(mf.ManifestoInvalidoError, match="grupo"):
        mf.Manifesto.de_dict(torto)
    with pytest.raises(mf.ManifestoInvalidoError):
        mf.Manifesto.de_dict({**dados, "formato": 2})


def test_o_texto_do_manifesto_e_deterministico():
    a = mf.construir()
    b = mf.construir()
    assert a.texto() == b.texto()
    assert mf.ler(a.texto()) == a


# --- o CI ------------------------------------------------------------------------------------


def _jobs(workflow: str) -> dict[str, str]:
    """Os blocos de cada job de um workflow, como texto (sem depender de YAML)."""
    linhas = (WORKFLOWS / workflow).read_text(encoding="utf-8").splitlines()
    inicio = linhas.index("jobs:")
    jobs: dict[str, list[str]] = {}
    atual = None
    for linha in linhas[inicio + 1 :]:
        if linha.startswith("  ") and not linha.startswith("   ") and linha.rstrip().endswith(":"):
            atual = linha.strip()[:-1]
            jobs[atual] = []
        elif atual is not None:
            jobs[atual].append(linha)
    return {nome: "\n".join(corpo) for nome, corpo in jobs.items()}


def test_o_ci_tem_o_gate_de_compatibilidade_bloqueante():
    jobs = _jobs("ci.yml")
    gate = jobs["compatibilidade"]
    assert "python tools/multiplayer_manifesto.py verificar" in gate
    assert "pytest -q tests/test_multiplayer_*.py" in gate
    assert "fetch-depth: 0" in gate
    assert "continue-on-error" not in (WORKFLOWS / "ci.yml").read_text()
    # A suíte padrão também roda os testes de compatibilidade (não são `balance`).
    assert "python -m pytest -q" in jobs["testes"]


def test_o_ci_roda_no_push_da_branch_de_trabalho_sem_enfraquecer_master():
    texto = (WORKFLOWS / "ci.yml").read_text(encoding="utf-8")
    assert "    branches: [master, phase/pvp-arena]" in texto  # push
    assert "  pull_request:\n    branches: [master]" in texto
    jobs = _jobs("ci.yml")
    assert set(jobs) == {"testes", "balanceamento", "compatibilidade", "lint"}
    # Testes, lint e compatibilidade rodam em todo evento, sem condição.
    for nome in ("testes", "compatibilidade", "lint"):
        assert "\n    if:" not in jobs[nome], nome
    # O balanceamento continua em `master` e em todo PR para ela.
    assert (
        "if: github.event_name == 'pull_request' || github.ref == 'refs/heads/master'"
        in jobs["balanceamento"]
    )
    assert 'pytest -q -m "balance or balance_full"' in jobs["balanceamento"]


def test_a_publicacao_so_empacota_depois_do_gate():
    texto = (WORKFLOWS / "publicacao.yml").read_text(encoding="utf-8")
    assert 'tags: ["v*"]' in texto
    assert "continue-on-error" not in texto
    jobs = _jobs("publicacao.yml")
    assert 'verificar --tag "${GITHUB_REF_NAME}"' in jobs["compatibilidade"]
    assert "python -m pytest -q" in jobs["compatibilidade"]
    assert "needs: compatibilidade" in jobs["distribuicao"]
    assert set(jobs) == {"compatibilidade", "distribuicao"}
