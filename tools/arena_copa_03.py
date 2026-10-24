"""Copa Arena 03: mata-mata de 64 Guerreiros extraídos de runs PvE reais.

Uso:
    python tools/arena_copa_03_geracao.py gerar   # as runs, até as 64 vagas
    python tools/arena_copa_03.py                 # finaliza, disputa e escreve tudo

A geração (`tools/arena_copa_03_geracao.py`) deixa em `_trabalho/` cada
tentativa e o snapshot de cada extração qualificada. Aqui:

1. `finalizar` lê o checkpoint, confere que os nove grupos fecharam as quotas,
   dá aos 64 aceitos os IDs `W01`–`W64` (na ordem dos grupos e, dentro de cada
   um, na ordem das tentativas), sorteia os nicknames e grava os entregáveis:
   `snapshots/`, `gladiadores.json` e `runs.jsonl`;
2. `formar_participantes` reconstrói cada gladiador do snapshot pelo caminho da
   Arena (`player_from_save_data` sobre cópia, como `arena_setup`), e a partida
   o prepara com `prepare_gladiator`, que restaura HP/MP e limpa efeitos,
   buffs e recargas. O snapshot nunca é alterado;
3. `disputar_copa` joga as 63 partidas MD1 com a `PoliticaCopa` das Copas 01 e
   02, cada uma duas vezes (com e sem auditoria), como na Copa 02;
4. `diagnostico_rng` repete alguns confrontos com outras seeds, DEPOIS da Copa
   oficial e sem tocar nela.

Semente principal 20261025, a mesma da geração. A chave e os nomes têm seeds
derivadas próprias (`sha256("20261025:chave")`, `sha256("20261025:nomes")`),
independentes das builds, dos perfis e uma da outra. Sem cabeças de chave.

Nicknames: os mesmos 64 da Copa 02, identificadores de exibição tirados de
canais da Twitch. Ninguém participou nem endossou, e nada liga a pessoa à
build, ao perfil ou à posição na chave. O snapshot guarda o nome com que a run
foi criada ("Referencia"); o nickname é posto só na instância reconstruída.
"""

from __future__ import annotations

import hashlib
import json
import math
import random
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.extraction import was_extracted  # noqa: E402
from src.content.gladiator import prepare_gladiator  # noqa: E402
from src.content.skills_loader import get_skill_by_id  # noqa: E402
from tools.arena_auditoria import disputar  # noqa: E402
from tools.arena_copa_02 import FASES, NICKS, faixa_de  # noqa: E402
from tools.arena_copa_03_geracao import (  # noqa: E402
    GRUPOS,
    PASTA,
    SEMENTE_PRINCIPAL,
    TRABALHO,
    gravar_atomico,
    ler_tentativas,
    montar_fila,
    reconstruir,
)
from tools.arena_copa_teste import (  # noqa: E402
    LIMITE_TECNICO,
    Copa,
    Participante,
    PoliticaCopa,
    jogar_partida,
    sortear_chave,
)

COPA = "Copa Arena 03"
PASTA_SNAPSHOTS = PASTA / "snapshots"
ARQUIVO_GLADIADORES = "gladiadores.json"
ARQUIVO_RUNS = "runs.jsonl"
ARQUIVO_DIAGNOSTICO = "diagnostico_rng.json"
ARQUIVO_PILOTO = "runs_piloto.jsonl"
PERFIL_PT = {"conservador": "Conservador", "moderado": "Moderado", "hardcore": "Hardcore"}
# Repetições por confronto no diagnóstico de RNG, metade com os lados trocados.
REPETICOES = 200
CONFRONTOS_DO_DIAGNOSTICO = 10
CONTROLES = {"stun", "sleep", "frozen", "fear"}


def semente_derivada(rotulo: str) -> int:
    digest = hashlib.sha256(f"{SEMENTE_PRINCIPAL}:{rotulo}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


@dataclass(frozen=True)
class Especificacao03:
    """A ficha de um participante, com os nomes que os relatórios das Copas leem."""

    id: str
    nome: str
    grupo: str
    rotulo: str
    classe: str
    nivel: int
    faixa: int | None
    deck: tuple[str, ...]
    passivas: tuple[str, ...]
    foco: str
    perfil: str
    politica: str
    tentativa: int
    seed: int
    andar: int
    snapshot: str
    trocas: tuple = ()
    tentativas: tuple = field(default=(), compare=False)


# --- leitura da build --------------------------------------------------------


def arquetipos(build: dict) -> list[str]:
    """Canais da build, lidos DEPOIS da geração, só para o relatório.

    Uma build pode ter vários. As regras são declaradas e não escolhem ninguém:

    - crítico: 3+ passivas de crítico (`crit_chance`, `crit_damage`);
    - defesa: metade ou mais das passivas em vida, defesa, redução, esquiva ou
      resistência, ou uma carta de redução de dano no deck;
    - controle: carta de status de controle (atordoar, sono, congelar, medo) ou
      passiva de chance de atordoar/medo;
    - sustento: carta de cura, ou 2+ passivas de roubo de vida, bônus de poção
      ou ignorar a morte.
    """
    familias = Counter(build.get("familias", {}))
    total = sum(familias.values()) or 1
    cartas = [get_skill_by_id(sid) for sid in build.get("deck", ())]
    saida = []
    if familias["crit_chance"] + familias["crit_damage"] >= 3:
        saida.append("crítico")
    defesa = sum(
        familias[f]
        for f in ("max_hp", "defense", "damage_reduction", "evasion", "status_resistance")
    )
    if defesa * 2 >= total or any(c.effect_type == "damage_reduction" for c in cartas):
        saida.append("defesa")
    if any(c.effect_type == "status" and c.effect_stat in CONTROLES for c in cartas) or (
        familias["stun_chance"] + familias["fear_chance"]
    ):
        saida.append("controle")
    if any(c.effect_type == "heal" for c in cartas) or (
        familias["life_steal"] + familias["potion_heal_bonus"] + familias["death_ignore"] >= 2
    ):
        saida.append("sustento")
    return saida


# --- finalização da geração ---------------------------------------------------


def situacao(registro: dict, aceitas: set[int], ultima_aceita: int) -> str:
    """O destino de uma tentativa, para `runs.jsonl`."""
    if registro["tentativa"] in aceitas:
        return "aceita"
    if registro.get("qualificada"):
        return "qualificada_sem_vaga"
    if registro["desfecho"] == "extraiu":
        if registro.get("op") is None:
            return "rejeitada_snapshot"
        return "rejeitada_op"
    return registro["desfecho"]


def sortear_nomes(ids: list[str]) -> dict[str, str]:
    nicks = [nick for lista in NICKS.values() for nick in lista]
    random.Random(semente_derivada("nomes")).shuffle(nicks)
    return dict(zip(ids, nicks))


def _sha(texto: str) -> str:
    return hashlib.sha256(texto.encode()).hexdigest()


def finalizar(trabalho: Path = TRABALHO, pasta: Path = PASTA) -> dict:
    """Grava `snapshots/`, `gladiadores.json` e `runs.jsonl` a partir do checkpoint."""
    registros = ler_tentativas(trabalho)
    fila = montar_fila(registros)
    abertos = [f"{g.perfil}/{g.politica}" for g in fila.values() if not g.completo]
    if abertos:
        raise RuntimeError(f"a geração não fechou as quotas: {', '.join(abertos)}")

    aceitos = [(fila[g], k) for g in GRUPOS for k in fila[g].aceitas()]
    ids = [f"W{i:02d}" for i in range(1, len(aceitos) + 1)]
    nomes = sortear_nomes(ids)
    gladiadores = []
    for gid, (grupo, k) in zip(ids, aceitos):
        registro = grupo.concluidas[k]
        texto = (trabalho / "candidatos" / registro["candidato"]).read_text(encoding="utf-8")
        snapshot = json.loads(texto)
        heroi = reconstruir(snapshot)
        if heroi is None or not was_extracted(heroi) or heroi.get_classname() != "Warrior":
            raise RuntimeError(f"{gid}: o snapshot não reconstrói um Guerreiro extraído")
        destino = pasta / "snapshots" / f"{gid}.json"
        conteudo = json.dumps(snapshot, ensure_ascii=False, indent=1, sort_keys=True) + "\n"
        if destino.exists() and destino.read_text(encoding="utf-8") != conteudo:
            raise RuntimeError(f"{destino} já existe com outro conteúdo: snapshot é imutável")
        if not destino.exists():
            gravar_atomico(destino, conteudo)
        build = registro["build"]
        gladiadores.append(
            {
                "id": gid,
                "nick": nomes[gid],
                "classe": "Warrior",
                "perfil": grupo.perfil,
                "politica": grupo.politica,
                "tentativa": k,
                "seed": str(registro["seed"]),
                "andar_de_extracao": registro["andar"],
                "nivel": registro["nivel"],
                "op": registro["op"],
                "duelos_da_medicao": registro["duelos_op"],
                "snapshot": f"snapshots/{gid}.json",
                "sha256": _sha(conteudo),
                "deck": build["deck"],
                "passivas": build["passivas"],
                "familias": build["familias"],
                "raridades": build["raridades"],
                "equipamento": build["equipamento"],
                "arquetipos": arquetipos(build),
            }
        )
    gravar_atomico(
        pasta / ARQUIVO_GLADIADORES,
        json.dumps(
            {
                "copa": COPA,
                "semente_principal": SEMENTE_PRINCIPAL,
                "aviso": (
                    "Nicknames são identificadores fictícios de simulação, sem participação ou "
                    "endosso das pessoas reais; foram sorteados independentemente das builds, "
                    "dos perfis e da chave."
                ),
                "gladiadores": gladiadores,
            },
            ensure_ascii=False,
            indent=1,
        )
        + "\n",
    )

    linhas = []
    for g in GRUPOS:
        grupo = fila[g]
        aceitas = set(grupo.aceitas())
        ultima = max(aceitas)
        for k in sorted(grupo.concluidas):
            r = dict(grupo.concluidas[k])
            r["situacao"] = situacao(r, aceitas, ultima)
            r["apos_a_quota"] = k > ultima
            r["seed"] = str(r["seed"])
            r.pop("candidato", None)
            linhas.append(json.dumps(r, ensure_ascii=False, sort_keys=True))
    gravar_atomico(pasta / ARQUIVO_RUNS, "\n".join(linhas) + "\n")

    # O piloto v1 (só a linha de aposta, matriz de extração canônica) não entra na
    # Copa, mas é a evidência que levou à v2: fica publicado à parte.
    piloto = ler_tentativas(trabalho / "piloto_v1")
    if piloto:
        linhas_piloto = []
        for r in sorted(
            piloto, key=lambda r: (GRUPOS.index((r["perfil"], r["politica"])), r["tentativa"])
        ):
            r = dict(r, versao="v1", situacao="piloto", seed=str(r["seed"]))
            r.pop("candidato", None)
            linhas_piloto.append(json.dumps(r, ensure_ascii=False, sort_keys=True))
        gravar_atomico(pasta / ARQUIVO_PILOTO, "\n".join(linhas_piloto) + "\n")
    return {"gladiadores": gladiadores, "tentativas": len(linhas), "piloto": len(piloto)}


def ler_gladiadores(pasta: Path = PASTA) -> list[dict]:
    return json.loads((pasta / ARQUIVO_GLADIADORES).read_text(encoding="utf-8"))["gladiadores"]


def formar_participantes(pasta: Path = PASTA) -> list[Participante]:
    """Os 64, reconstruídos dos snapshots. O OP é o medido na geração."""
    participantes = []
    for g in ler_gladiadores(pasta):
        texto = (pasta / g["snapshot"]).read_text(encoding="utf-8")
        if _sha(texto) != g["sha256"]:
            raise RuntimeError(f"{g['id']}: o snapshot mudou desde a geração")
        heroi = reconstruir(json.loads(texto))
        heroi.nick_name = g["nick"]
        espec = Especificacao03(
            id=g["id"],
            nome=g["nick"],
            grupo=f"{g['perfil']}/{g['politica']}",
            rotulo=f"{PERFIL_PT[g['perfil']]} · {g['politica']}",
            classe="Warrior",
            nivel=g["nivel"],
            faixa=faixa_de(g["op"]),
            deck=tuple(g["deck"]),
            passivas=tuple(g["passivas"]),
            foco=" + ".join(g["arquetipos"]) or "sem canal dominante",
            perfil=g["perfil"],
            politica=g["politica"],
            tentativa=g["tentativa"],
            seed=int(g["seed"]),
            andar=g["andar_de_extracao"],
            snapshot=g["snapshot"],
        )
        participantes.append(Participante(espec, heroi, g["op"], g["duelos_da_medicao"]))
    return participantes


# --- a Copa ------------------------------------------------------------------


def disputar_copa(participantes: list[Participante]) -> Copa:
    por_id = {p.id: p for p in participantes}
    chave = sortear_chave([p.id for p in participantes], semente_derivada("chave"))
    vivos = [por_id[i] for i in chave]
    copa = Copa(participantes, chave, {})
    for fase, quantas, nome in FASES:
        partidas = [
            jogar_partida(
                fase,
                i + 1,
                vivos[2 * i],
                vivos[2 * i + 1],
                semente_principal=SEMENTE_PRINCIPAL,
                nome_da_fase=nome,
            )
            for i in range(quantas)
        ]
        copa.fases[fase] = partidas
        if any(p.inconclusiva for p in partidas):
            copa.interrompida = f"{nome}: confronto inconclusivo no limite técnico; a chave parou."
            return copa
        vivos = [p.vencedor for p in partidas]
    return copa


def todas(copa: Copa) -> list:
    return [p for fase, _, _ in FASES for p in copa.fases.get(fase, ())]


# --- diagnóstico do RNG do duelo ----------------------------------------------


def _wilson(vitorias: int, n: int) -> tuple[float, float]:
    """Intervalo de 95% (Wilson) para a taxa de vitória."""
    if n == 0:
        return 0.0, 0.0
    z = 1.96
    p = vitorias / n
    centro = (p + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return max(0.0, centro - meia), min(1.0, centro + meia)


def escolher_confrontos(copa: Copa, quantos: int = CONFRONTOS_DO_DIAGNOSTICO) -> list:
    """A final, as zebras (maior ΔOP primeiro) e os mais parelhos em OP."""
    partidas = todas(copa)
    escolhidas = [p for p in partidas if p.fase == "final"]
    zebras = sorted(
        (p for p in partidas if p.vencedor.poder < p.perdedor.poder),
        key=lambda p: p.vencedor.poder - p.perdedor.poder,
    )
    parelhas = sorted(
        (p for p in partidas if p.vencedor.poder >= p.perdedor.poder),
        key=lambda p: (abs(p.vencedor.poder - p.perdedor.poder), p.fase, p.indice),
    )
    for p in zebras[: quantos // 2] + parelhas:
        if len(escolhidas) >= quantos:
            break
        if p not in escolhidas:
            escolhidas.append(p)
    return escolhidas


def diagnostico_rng(copa: Copa, repeticoes: int = REPETICOES) -> list[dict]:
    """Os mesmos dois gladiadores e o mesmo controlador, sob outras seeds.

    Metade das repetições troca os lados, para que a ordem p1/p2 não pese. Nada
    aqui altera a Copa oficial: são duelos novos, sem auditoria, com seeds
    `sha256("20261025:rng:fase:indice:r")`.
    """
    saida = []
    for partida in escolher_confrontos(copa):
        oficial = partida.vencedor
        outro = partida.perdedor
        vitorias = inconclusivos = 0
        rodadas = []
        for r in range(repeticoes):
            semente = semente_derivada(f"rng:{partida.fase}:{partida.indice}:{r}")
            a, b = (oficial, outro) if r % 2 == 0 else (outro, oficial)
            duelo = disputar(
                prepare_gladiator(a.heroi),
                prepare_gladiator(b.heroi),
                semente,
                PoliticaCopa,
                auditar=False,
                limite=LIMITE_TECNICO,
            )
            if duelo.inconclusivo:
                inconclusivos += 1
                continue
            vencedor = a if duelo.duelo.result.winner == "p1" else b
            vitorias += vencedor is oficial
            rodadas.append(len(duelo.duelo.history))
        validos = repeticoes - inconclusivos
        baixo, alto = _wilson(vitorias, validos)
        saida.append(
            {
                "chave": f"{partida.fase}-{partida.indice}",
                "titulo": partida.titulo,
                "vencedor_oficial": oficial.id,
                "perdedor_oficial": outro.id,
                "op": [oficial.poder, outro.poder],
                "zebra_oficial": oficial.poder < outro.poder,
                "repeticoes": repeticoes,
                "inconclusivos": inconclusivos,
                "vitorias_do_vencedor_oficial": vitorias,
                "taxa": vitorias / validos if validos else 0.0,
                "ic95": [baixo, alto],
                "rodadas_media": sum(rodadas) / len(rodadas) if rodadas else 0.0,
            }
        )
    return saida


def main(argv: list[str]) -> int:
    from tools.arena_copa_03_relatorios import escrever_tudo

    if argv[:1] != ["sem-finalizar"]:
        resumo = finalizar()
        print(f"finalizado: {len(resumo['gladiadores'])} gladiadores, {resumo['tentativas']} runs")
    participantes = formar_participantes()
    copa = disputar_copa(participantes)
    diagnostico = diagnostico_rng(copa)
    gravar_atomico(
        PASTA / ARQUIVO_DIAGNOSTICO, json.dumps(diagnostico, ensure_ascii=False, indent=1) + "\n"
    )
    for caminho in escrever_tudo(copa, diagnostico):
        print(f"escrito: {caminho.relative_to(RAIZ)}")
    campeao = copa.campeao
    print(f"Campeão: {campeao.nome} ({campeao.id})" if campeao else copa.interrompida)
    falhas = [p for p in todas(copa) if not all(ok for _, ok in p.fidelidade + p.coerencia)]
    return 1 if falhas or copa.interrompida else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
