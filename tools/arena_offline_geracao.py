"""População offline da Arena: as extrações reais e o catálogo do jogo.

Uso:
    python tools/arena_offline_geracao.py gerar --classe mage [--trabalhadores 3]
    python tools/arena_offline_geracao.py guerreiros [--trabalhadores 3]
    python tools/arena_offline_geracao.py status
    python tools/arena_offline_geracao.py catalogar

A Arena offline do ToJ 1.0 põe o gladiador do jogador contra uma população fixa
controlada pela IA estratégica. Todo gladiador dessa população saiu de uma run
PvE real até a Extração, pelo mesmo caminho da Copa Arena 03
(`tools/arena_copa_03_geracao.py`): criação canônica da jornada, BotExperimental
com perfil × política, Extração pelo jogo, snapshot pela serialização canônica do
save e reconstrução pelo caminho da Arena. Nada aqui inventa atributo, item,
passiva ou carta.

## As três origens

1. **Os 64 Guerreiros da Copa 03**, como estão: os mesmos bytes, conferidos pelo
   sha256 do índice da Copa.
2. **Guerreiros fora da faixa da Copa.** A Copa 03 só aceitava OP entre 20 e 30,
   e recusou 384 extrações legítimas por isso (`situacao: rejeitada_op` em
   `runs.jsonl` e `runs_preenchimento.jsonl`). A população não tem limite de OP.
   Os snapshots delas não foram guardados, mas a run é determinística pela
   seed: `guerreiros` escolhe `VARIEDADE` delas espaçadas pela ordem do OP (a
   menor e a maior entram sempre) e as executa de novo. Uma re-execução só é
   aceita se seed, andar, nível e OP saírem iguais aos do log da Copa.
3. **Mage e Rogue**, que não existiam: runs novas da mesma variante, com a
   classe na chave da seed (`semente_da_run`), `QUOTA` extrações por grupo
   perfil × política, qualquer OP, e no máximo `LIMITE[classe]` tentativas por
   grupo. O limite existe porque há perfil que quase nunca extrai (o piloto de
   18 runs: Mage 0/9, Rogue 1/9); grupo que bate o limite fica incompleto e o
   registro diz isso.

## O catálogo

`catalogar` junta as três origens, confere cada snapshot pelas regras da
população (`src/engine/arena_populacao.validar_snapshot`: classe, marca de
extração, vida, Chave gasta, reconstrução idêntica pela ida e volta), exige
unicidade de bytes, de seed e de build, e grava `src/data/arena_populacao/`: um
arquivo por gladiador e o `indice.json` com o sha256 de cada um. O apelido é
fictício e sorteado com semente fixa; o nome do jogador de origem não entra.

Tudo o que é transitório fica em `reports/pvp/arena_offline/_trabalho/` (fora do
git). O resumo das tentativas, uma linha por run, vai para
`reports/pvp/arena_offline/tentativas.jsonl`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import multiprocessing as mp
import os
import random
import sys
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import tools.arena_copa_03_geracao as ger  # noqa: E402

PASTA = RAIZ / "reports" / "pvp" / "arena_offline"
TRABALHO = PASTA / "_trabalho"
COPA_03 = RAIZ / "reports" / "pvp" / "copa_03"
CATALOGO = RAIZ / "src" / "data" / "arena_populacao"

CLASSES_NOVAS = ("mage", "rogue")
QUOTA = 5
QUOTAS = {grupo: QUOTA for grupo in ger.GRUPOS}
LIMITE = {"mage": 80, "rogue": 60}
VARIEDADE = 32
LOG_DOS_GUERREIROS = "guerreiros.jsonl"
SEMENTE_DOS_NOMES = f"{ger.SEMENTE_PRINCIPAL}:arena_offline:nomes"
LETRA = {"warrior": "W", "mage": "M", "rogue": "R"}

# Apelidos fictícios: nome × alcunha, sorteados sem repetição.
NOMES = (
    "Aldo", "Bruma", "Caeli", "Dorin", "Esra", "Faro", "Gael", "Hesta", "Iago", "Jora",
    "Kael", "Lira", "Maren", "Nilo", "Oriel", "Pira", "Quila", "Rana", "Sauro", "Tália",
    "Ulme", "Vesna", "Wren", "Xisto", "Yara", "Zeno", "Brisa", "Cirro", "Dália", "Ébano",
    "Fírio", "Galena",
)  # fmt: skip
ALCUNHAS = (
    "da Brasa", "do Vau", "da Névoa", "do Penhasco", "da Areia", "do Trovão", "da Lança",
    "do Corvo", "da Aurora", "do Abismo", "da Forja", "do Espinho", "da Maré", "do Eclipse",
    "da Serra", "do Cardo", "da Cinza", "do Lume", "da Geada", "do Ermo", "da Torre",
    "do Rochedo", "da Fenda", "do Granito", "da Raposa", "do Lobo", "da Vigília", "do Sal",
    "da Pedra", "do Junco",
)  # fmt: skip


def _jsonl(arquivo: Path) -> list[dict]:
    if not arquivo.exists():
        return []
    return [
        json.loads(linha) for linha in arquivo.read_text(encoding="utf-8").splitlines() if linha
    ]


def _sha(dados: bytes) -> str:
    return hashlib.sha256(dados).hexdigest()


def publicado(snapshot: dict) -> bytes:
    """O snapshot no formato publicado da Copa 03: chaves ordenadas, indentação 1."""
    return (json.dumps(snapshot, ensure_ascii=False, indent=1, sort_keys=True) + "\n").encode()


# --- Mage e Rogue ----------------------------------------------------------------


def gerar_classe(classe: str, trabalhadores: int = 3) -> dict:
    """Runs novas da classe até `QUOTA` por grupo ou `LIMITE` tentativas por grupo."""
    if classe not in CLASSES_NOVAS:
        raise ValueError(f"classe sem geração própria: {classe}")
    return ger.gerar(
        trabalhadores,
        TRABALHO / classe,
        quotas=QUOTAS,
        classe=classe,
        faixa=None,
        limite=LIMITE[classe],
    )


def aceitos_da_classe(classe: str) -> list[dict]:
    """As extrações aceitas da classe, na ordem dos grupos e das tentativas."""
    fila = ger.montar_fila(ger.ler_tentativas(TRABALHO / classe), QUOTAS)
    return [g.concluidas[k] for g in fila.values() for k in g.aceitas()]


# --- os Guerreiros fora da faixa da Copa 03 -----------------------------------------


def _copa_03() -> dict:
    return json.loads((COPA_03 / "gladiadores.json").read_text(encoding="utf-8"))


def extracoes_fora_da_faixa() -> list[dict]:
    """As extrações legítimas que a Copa 03 recusou só pelo OP."""
    registros = _jsonl(COPA_03 / "runs.jsonl") + _jsonl(COPA_03 / "runs_preenchimento.jsonl")
    escolhidos = {(g["perfil"], g["politica"], g["tentativa"]) for g in _copa_03()["gladiadores"]}
    return [
        r
        for r in registros
        if r.get("situacao") == "rejeitada_op"
        and r.get("versao") == ger.VERSAO
        and (r["perfil"], r["politica"], r["tentativa"]) not in escolhidos
    ]


def selecionar_variedade(candidatos: list[dict], n: int = VARIEDADE) -> list[dict]:
    """`n` extrações espaçadas pela ordem do OP, com a menor e a maior."""
    ordem = sorted(candidatos, key=lambda r: (r["op"], r["perfil"], r["politica"], r["tentativa"]))
    if len(ordem) <= n:
        return ordem
    return [ordem[round(i * (len(ordem) - 1) / (n - 1))] for i in range(n)]


def _reexecutar(original: dict) -> dict:
    """A run da Copa outra vez, pela mesma seed, e a conferência contra o log."""
    registro = ger.executar(
        original["perfil"], original["politica"], original["tentativa"], faixa=None
    )
    divergencias = [
        campo
        for campo, igual in (
            ("seed", str(registro.get("seed")) == str(original["seed"])),
            ("andar", registro.get("andar") == original["andar"]),
            ("nivel", registro.get("nivel") == original["nivel"]),
            ("op", registro.get("op") == original["op"]),
        )
        if not igual
    ]
    registro["conferida"] = not divergencias and "_snapshot" in registro
    registro["divergencias_da_copa"] = divergencias
    return registro


def gerar_guerreiros(trabalhadores: int = 3) -> list[dict]:
    """Re-executa a variedade de Guerreiros, com checkpoint por run concluída."""
    pasta = TRABALHO / "warrior"
    (pasta / "candidatos").mkdir(parents=True, exist_ok=True)
    log = pasta / LOG_DOS_GUERREIROS
    feitos = {(r["perfil"], r["politica"], r["tentativa"]) for r in _jsonl(log)}
    pendentes = [
        r
        for r in selecionar_variedade(extracoes_fora_da_faixa())
        if (r["perfil"], r["politica"], r["tentativa"]) not in feitos
    ]
    ger._log(f"Guerreiros: {len(feitos)} feitos, {len(pendentes)} pendentes", pasta)
    contexto = mp.get_context("spawn")
    with ProcessPoolExecutor(trabalhadores, mp_context=contexto, max_tasks_per_child=1) as pool:
        futuros = {pool.submit(_reexecutar, r): r for r in pendentes}
        with open(log, "a", encoding="utf-8") as saida:
            while futuros:
                prontos, _ = wait(futuros, return_when=FIRST_COMPLETED)
                for futuro in prontos:
                    original = futuros.pop(futuro)
                    registro = futuro.result()
                    snapshot = registro.pop("_snapshot", None)
                    if snapshot is not None and registro["conferida"]:
                        nome = ger.nome_do_candidato(
                            original["perfil"], original["politica"], original["tentativa"]
                        )
                        ger.gravar_atomico(
                            pasta / "candidatos" / nome,
                            json.dumps(snapshot, ensure_ascii=False, indent=1),
                        )
                        registro["candidato"] = nome
                    saida.write(json.dumps(registro, ensure_ascii=False) + "\n")
                    saida.flush()
                    os.fsync(saida.fileno())
                    ger._log(
                        f"W {original['perfil']}/{original['politica']} #{original['tentativa']}: "
                        f"OP {registro.get('op')} conferida={registro['conferida']}",
                        pasta,
                    )
    return _jsonl(log)


# --- status ------------------------------------------------------------------------


def status() -> str:
    linhas = []
    for classe in CLASSES_NOVAS:
        registros = ger.ler_tentativas(TRABALHO / classe)
        fila = ger.montar_fila(registros, QUOTAS)
        aceitos = sum(len(g.aceitas()) for g in fila.values())
        extraiu = sum(r["desfecho"] == "extraiu" for r in registros)
        linhas.append(
            f"{classe}: {len(registros)} tentativas, {extraiu} extrações, "
            f"{aceitos}/{sum(QUOTAS.values())} aceitas"
        )
        for g in fila.values():
            linhas.append(
                f"  {g.perfil}/{g.politica}: {len(g.aceitas())}/{g.quota} "
                f"em {len(g.concluidas)} tentativas"
            )
    guerreiros = _jsonl(TRABALHO / "warrior" / LOG_DOS_GUERREIROS)
    linhas.append(
        f"warrior (variedade): {sum(r['conferida'] for r in guerreiros)}/{VARIEDADE} conferidas"
    )
    return "\n".join(linhas)


# --- o catálogo ------------------------------------------------------------------


def apelidos(quantidade: int) -> list[str]:
    combinacoes = [f"{nome} {alcunha}" for nome in NOMES for alcunha in ALCUNHAS]
    random.Random(SEMENTE_DOS_NOMES).shuffle(combinacoes)
    if quantidade > len(combinacoes):
        raise ValueError("apelidos insuficientes")
    return combinacoes[:quantidade]


def _resumo(registro: dict) -> dict:
    campos = ("perfil", "politica", "tentativa", "seed", "desfecho", "andar", "nivel", "op")
    return {campo: registro.get(campo) for campo in campos} | {
        "motivo": registro.get("motivo"),
        "tempo_s": registro.get("tempo_s"),
    }


def _entradas() -> list[tuple[dict, bytes]]:
    """(metadados, bytes do snapshot) de cada gladiador, antes dos ids."""
    entradas = []
    for g in _copa_03()["gladiadores"]:
        dados = (COPA_03 / g["snapshot"]).read_bytes()
        if _sha(dados) != g["sha256"] or publicado(json.loads(dados)) != dados:
            raise RuntimeError(f"Copa 03 {g['id']}: o snapshot não confere com o índice")
        meta = {
            "classe": "warrior",
            "perfil": g["perfil"],
            "politica": g["politica"],
            "nivel": g["nivel"],
            "op": g["op"],
            "andar_de_extracao": g["andar_de_extracao"],
            "origem": {
                "fonte": "copa_03",
                "id_na_copa": g["id"],
                "versao": ger.VERSAO,
                "tentativa": g["tentativa"],
                "seed": str(g["seed"]),
            },
        }
        entradas.append((meta, dados))

    variedade = sorted(
        (r for r in _jsonl(TRABALHO / "warrior" / LOG_DOS_GUERREIROS) if r.get("conferida")),
        key=lambda r: (r["op"], r["perfil"], r["politica"], r["tentativa"]),
    )
    novas = [(classe, r) for classe in CLASSES_NOVAS for r in aceitos_da_classe(classe)]
    for classe, r in [("warrior", r) for r in variedade] + novas:
        candidato = TRABALHO / classe / "candidatos" / r["candidato"]
        dados = publicado(json.loads(candidato.read_text(encoding="utf-8")))
        meta = {
            "classe": classe,
            "perfil": r["perfil"],
            "politica": r["politica"],
            "nivel": r["nivel"],
            "op": r["op"],
            "andar_de_extracao": r["andar"],
            "origem": {
                "fonte": "copa_03_fora_da_faixa" if classe == "warrior" else "arena_offline",
                "versao": ger.VERSAO,
                "tentativa": r["tentativa"],
                "seed": str(r["seed"]),
            },
        }
        entradas.append((meta, dados))
    return entradas


def catalogar() -> dict:
    """Valida as três origens e grava `src/data/arena_populacao/`."""
    from src.engine import arena_populacao as pop
    from src.sim.arena import assinatura_de_build

    entradas = _entradas()
    nomes = apelidos(len(entradas))
    contagem = dict.fromkeys(LETRA, 0)
    indice, arquivos = [], {}
    vistos: dict[str, set] = {"sha256": set(), "seed": set(), "build": set()}
    for (meta, dados), apelido in zip(entradas, nomes):
        snapshot = json.loads(dados)
        falhas = pop.validar_snapshot(snapshot, meta["classe"])
        if falhas:
            raise RuntimeError(f"{meta['origem']}: {'; '.join(falhas)}")
        heroi = pop.reconstruir(snapshot)
        if (heroi.get_level(), snapshot["extracted_on_floor"]) != (
            meta["nivel"],
            meta["andar_de_extracao"],
        ):
            raise RuntimeError(f"{meta['origem']}: nível ou andar diferente do registro")
        chaves = {
            "sha256": _sha(dados),
            "seed": meta["origem"]["seed"],
            "build": json.dumps(assinatura_de_build(heroi), sort_keys=True, default=str),
        }
        for campo, valor in chaves.items():
            if valor in vistos[campo]:
                raise RuntimeError(f"{meta['origem']}: {campo} repetido na população")
            vistos[campo].add(valor)
        contagem[meta["classe"]] += 1
        gid = f"{LETRA[meta['classe']]}{contagem[meta['classe']]:02d}"
        arquivos[f"{gid}.json"] = dados
        indice.append(
            {
                "id": gid,
                "apelido": apelido,
                **meta,
                "sha256": chaves["sha256"],
                "arquivo": f"{gid}.json",
            }
        )

    if not pop.TAMANHO_MINIMO <= len(indice) <= pop.TAMANHO_MAXIMO:
        raise RuntimeError(f"população com {len(indice)} gladiadores")
    CATALOGO.mkdir(parents=True, exist_ok=True)
    for antigo in CATALOGO.glob("*.json"):
        if antigo.name != "indice.json" and antigo.name not in arquivos:
            antigo.unlink()
    for nome, dados in arquivos.items():
        if not (CATALOGO / nome).exists() or (CATALOGO / nome).read_bytes() != dados:
            ger.gravar_atomico(CATALOGO / nome, dados.decode("utf-8"))
    conteudo = {
        "versao": pop.VERSAO_DO_CATALOGO,
        "aviso": (
            "Gerado por tools/arena_offline_geracao.py catalogar. Cada gladiador é a "
            "extração de uma run PvE real; não edite à mão."
        ),
        "gladiadores": indice,
    }
    ger.gravar_atomico(
        CATALOGO / "indice.json", json.dumps(conteudo, ensure_ascii=False, indent=1) + "\n"
    )
    _gravar_tentativas()
    return conteudo


def _gravar_tentativas() -> None:
    """O resumo de toda tentativa da população, uma linha por run."""
    linhas = []
    for classe in CLASSES_NOVAS:
        for r in ger.ler_tentativas(TRABALHO / classe):
            linhas.append({"classe": classe, **_resumo(r)})
    for r in _jsonl(TRABALHO / "warrior" / LOG_DOS_GUERREIROS):
        linhas.append(
            {"classe": "warrior", **_resumo(r), "reexecucao_conferida": r.get("conferida")}
        )
    PASTA.mkdir(parents=True, exist_ok=True)
    ger.gravar_atomico(
        PASTA / "tentativas.jsonl",
        "".join(json.dumps(linha, ensure_ascii=False) + "\n" for linha in linhas),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    gerar = sub.add_parser("gerar")
    gerar.add_argument("--classe", choices=CLASSES_NOVAS, required=True)
    gerar.add_argument("--trabalhadores", type=int, default=3)
    guerreiros = sub.add_parser("guerreiros")
    guerreiros.add_argument("--trabalhadores", type=int, default=3)
    sub.add_parser("status")
    sub.add_parser("catalogar")
    args = parser.parse_args()
    if args.comando == "gerar":
        gerar_classe(args.classe, args.trabalhadores)
    elif args.comando == "guerreiros":
        gerar_guerreiros(args.trabalhadores)
    elif args.comando == "catalogar":
        conteudo = catalogar()
        print(f"{len(conteudo['gladiadores'])} gladiadores em {CATALOGO.relative_to(RAIZ)}")
    print(status())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
