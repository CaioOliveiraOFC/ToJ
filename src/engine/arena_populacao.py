"""A população offline da Arena: os adversários do jogador no ToJ 1.0.

Cada adversário é a EXTRAÇÃO de uma run PvE real, guardada como o snapshot
canônico do save em `src/data/arena_populacao/`. Quem gera, valida e grava o
catálogo é `tools/arena_offline_geracao.py`; aqui o jogo só o lê, e confere de
novo antes de cada partida:

- o sha256 do arquivo tem de ser o do índice;
- o snapshot tem de reconstruir pelo caminho da Arena (`arena_setup`) como um
  gladiador extraído, vivo, da classe do índice, com a Chave gasta, e voltar
  idêntico pela serialização canônica (`validar_snapshot`).

Um adversário que não passa não entra em partida nenhuma: o erro é
`PopulacaoInvalidaError`, e nunca um gladiador montado pela metade.

O apelido é o do catálogo. O OP do índice é só a referência inicial de força,
medida na geração; não é rating.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass, field
from pathlib import Path

from src.content.extraction import extracted_floor, keys_of, was_extracted
from src.content.gladiator import GladiatorNotEligibleError, prepare_gladiator
from src.data import loader
from src.engine import arena_setup
from src.engine.game_logic import CLASS_MAP
from src.mechanics.pvp_duel import Gladiator
from src.storage.save_manager import to_save_data

PASTA = Path(loader.__file__).resolve().parent / "arena_populacao"
VERSAO_DO_CATALOGO = 1
TAMANHO_MINIMO = 128
TAMANHO_MAXIMO = 256

# Os rótulos do estilo de cada gladiador: o jeito como a run PvE dele foi
# jogada. Na Arena todos lutam com a mesma IA; o estilo explica a build.
PERFIS = {"conservador": "conservador", "moderado": "moderado", "hardcore": "arriscado"}
POLITICAS = {"survival": "sobrevivência", "offense": "ataque", "economy": "economia"}


class PopulacaoInvalidaError(RuntimeError):
    """O catálogo ou um snapshot dele não confere: nada é montado."""


@dataclass(frozen=True)
class Oponente:
    """Um gladiador da população, como o índice o descreve."""

    id: str
    apelido: str
    classe: str
    nivel: int
    op: float
    perfil: str
    politica: str
    andar_de_extracao: int
    sha256: str
    arquivo: str
    origem: dict = field(default_factory=dict, compare=False, hash=False)

    @property
    def nome_da_classe(self) -> str:
        return CLASS_MAP[self.classe][1]

    @property
    def estilo(self) -> str:
        return f"{PERFIS[self.perfil]} · {POLITICAS[self.politica]}"

    @property
    def identidade(self) -> str:
        """Identidade estável para histórico e rating: o id e o conteúdo."""
        return f"populacao:{self.id}:{self.sha256[:16]}"


def _sem_telemetria_de_carga(dados: dict) -> dict:
    """O snapshot normalizado, sem `ledger.items_equipped`.

    A recarga canônica reequipa cada peça por `Player.equip`, que soma 1 a esse
    contador do livro-caixa. É telemetria, não build.
    """
    copia = json.loads(json.dumps(dados))
    copia.get("ledger", {}).pop("items_equipped", None)
    return copia


def reconstruir(snapshot: dict):
    """O personagem do snapshot pelo caminho da Arena, ainda não preparado."""
    return arena_setup.character_from_snapshot(snapshot)


def validar_snapshot(snapshot: dict, classe: str) -> list[str]:
    """O que impede o snapshot de ser um gladiador da população. Vazio = elegível."""
    try:
        heroi = reconstruir(snapshot)
    except (GladiatorNotEligibleError, KeyError, TypeError, ValueError) as erro:
        return [f"não reconstrói: {erro}"]
    falhas = []
    if heroi.get_classname().lower() != classe:
        falhas.append(f"classe {heroi.get_classname()}, o índice diz {classe}")
    if not was_extracted(heroi):
        falhas.append("sem marca de extração")
    elif extracted_floor(heroi) != snapshot.get("dungeon_level"):
        falhas.append("a marca de extração é de outro andar")
    if not heroi.get_isalive() or heroi.get_hp() <= 0:
        falhas.append("sem vida")
    if keys_of(heroi) != 0:
        falhas.append("a Chave de Extração não foi gasta")
    ida_e_volta = to_save_data(heroi, snapshot.get("dungeon_level", 0))
    if _sem_telemetria_de_carga(ida_e_volta) != _sem_telemetria_de_carga(snapshot):
        falhas.append("o snapshot não se reproduz pela ida e volta canônica")
    return falhas


def _oponente(registro: dict) -> Oponente:
    try:
        oponente = Oponente(
            id=str(registro["id"]),
            apelido=str(registro["apelido"]),
            classe=str(registro["classe"]),
            nivel=int(registro["nivel"]),
            op=float(registro["op"]),
            perfil=str(registro["perfil"]),
            politica=str(registro["politica"]),
            andar_de_extracao=int(registro["andar_de_extracao"]),
            sha256=str(registro["sha256"]),
            arquivo=str(registro["arquivo"]),
            origem=dict(registro.get("origem") or {}),
        )
    except (KeyError, TypeError, ValueError) as erro:
        raise PopulacaoInvalidaError(f"entrada ilegível no índice: {erro}") from erro
    if oponente.classe not in CLASS_MAP:
        raise PopulacaoInvalidaError(f"{oponente.id}: classe desconhecida {oponente.classe!r}")
    if oponente.perfil not in PERFIS or oponente.politica not in POLITICAS:
        raise PopulacaoInvalidaError(f"{oponente.id}: estilo desconhecido")
    if Path(oponente.arquivo).name != oponente.arquivo or not oponente.arquivo.endswith(".json"):
        raise PopulacaoInvalidaError(f"{oponente.id}: arquivo fora do catálogo")
    return oponente


class Populacao:
    """O catálogo lido do disco. Imutável durante o jogo."""

    def __init__(
        self,
        pasta: Path = PASTA,
        limites: tuple[int, int] = (TAMANHO_MINIMO, TAMANHO_MAXIMO),
    ) -> None:
        self.pasta = Path(pasta)
        try:
            indice = json.loads((self.pasta / "indice.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as erro:
            raise PopulacaoInvalidaError(f"índice da população ilegível: {erro}") from erro
        if not isinstance(indice, dict) or indice.get("versao") != VERSAO_DO_CATALOGO:
            raise PopulacaoInvalidaError("índice da população de outra versão")
        oponentes = [_oponente(r) for r in indice.get("gladiadores") or ()]
        for campo in ("id", "apelido", "sha256", "arquivo"):
            valores = [getattr(o, campo) for o in oponentes]
            if len(set(valores)) != len(valores):
                raise PopulacaoInvalidaError(f"{campo} repetido no índice da população")
        minimo, maximo = limites
        if not minimo <= len(oponentes) <= maximo:
            raise PopulacaoInvalidaError(
                f"a população tem {len(oponentes)} gladiadores, fora de {minimo}–{maximo}"
            )
        self._oponentes = tuple(oponentes)
        self._por_id = {o.id: o for o in oponentes}

    def __len__(self) -> int:
        return len(self._oponentes)

    def __iter__(self):
        return iter(self._oponentes)

    def get(self, oponente_id: str) -> Oponente:
        return self._por_id[oponente_id]

    def oponentes(self, classe: str | None = None) -> list[Oponente]:
        """Os oponentes, do mais fraco ao mais forte pela referência de OP."""
        escolhidos = [o for o in self._oponentes if classe is None or o.classe == classe]
        return sorted(escolhidos, key=lambda o: (o.op, o.id))

    def snapshot(self, oponente: Oponente) -> dict:
        """O snapshot do oponente, conferido pelo sha256 do índice."""
        try:
            dados = (self.pasta / oponente.arquivo).read_bytes()
        except OSError as erro:
            raise PopulacaoInvalidaError(f"{oponente.id}: arquivo ausente") from erro
        if hashlib.sha256(dados).hexdigest() != oponente.sha256:
            raise PopulacaoInvalidaError(f"{oponente.id}: o arquivo não confere com o índice")
        try:
            return json.loads(dados)
        except json.JSONDecodeError as erro:
            raise PopulacaoInvalidaError(f"{oponente.id}: snapshot ilegível") from erro

    def conferir(self, oponente: Oponente) -> dict:
        """O snapshot do oponente, se ele for elegível; senão, o erro."""
        snapshot = self.snapshot(oponente)
        falhas = validar_snapshot(snapshot, oponente.classe)
        heroi = reconstruir(snapshot) if not falhas else None
        if heroi is not None and heroi.get_level() != oponente.nivel:
            falhas.append(f"nível {heroi.get_level()}, o índice diz {oponente.nivel}")
        if falhas:
            raise PopulacaoInvalidaError(f"{oponente.id}: " + "; ".join(falhas))
        return snapshot

    def gladiador(self, oponente: Oponente) -> Gladiator:
        """O oponente pronto para o duelo: cópia, HP e MP cheios, com o apelido."""
        heroi = reconstruir(copy.deepcopy(self.conferir(oponente)))
        heroi.nick_name = oponente.apelido
        return prepare_gladiator(heroi)
