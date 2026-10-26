"""O gladiador no multiplayer: esquema versionado, validação estrita e migração.

O snapshot do gladiador é o dicionário de save (`storage.save_manager.to_save_data`),
guardado num registro com a versão do esquema:

    {"esquema": 1, "snapshot": {...o save do personagem extraído...}}

O caminho de reconstrução é o canônico (`engine.arena_setup`, sobre
`player_from_save_data`). Esse caminho é TOLERANTE de propósito — para o jogador
local, um item que saiu do catálogo some da mochila e o save continua abrindo.
No multiplayer a tolerância seria execução silenciosa com dados divergentes, então
este módulo confere antes e depois:

- **antes**: o snapshot tem exatamente os campos do esquema, com os tipos
  certos, de um personagem extraído, e todo item, carta e passiva existe no
  catálogo desta versão;
- **depois**: o personagem reconstruído, serializado de volta pelo mesmo
  `to_save_data`, devolve classe, nome, nível, equipamento, mochila, gemas,
  passivas e deck IDÊNTICOS. Qualquer coisa que o carregador tenha descartado
  ou mudado aparece aqui.

Falhou uma conferência, o gladiador não entra em partida. Esquema mais novo que
o desta versão é recusado; esquema mais velho só entra por uma migração
registrada em `MIGRACOES`, explícita e testada. Nenhum snapshot recebido é
alterado: tudo trabalha em cópias.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections.abc import Callable, Iterable, Mapping

from src.content.gladiator import GladiatorNotEligibleError, prepare_gladiator
from src.content.items import get_all_items
from src.content.passives import get_passive_by_id
from src.content.skills_loader import get_skill_by_id
from src.engine.arena_setup import character_from_snapshot
from src.mechanics.pvp_duel import Gladiator
from src.multiplayer.versao import ESQUEMA_DO_GLADIADOR
from src.storage.save_manager import to_save_data

ESQUEMA_ATUAL = ESQUEMA_DO_GLADIADOR

# O esquema 1: os campos de `to_save_data`, nem um a mais nem um a menos. Um
# campo novo no save é mudança de formato — esquema novo e migração —, e
# `tests/test_multiplayer_gladiadores.py` falha até isso ser feito.
_NADA = type(None)
CAMPOS_DO_SNAPSHOT: dict[str, tuple[type, ...]] = {
    "active_buffs": (dict,),
    "active_effects": (dict,),
    "coins": (int,),
    "dungeon_level": (int,),
    "equipment": (dict,),
    "extracted_on_floor": (int,),
    "extraction_keys": (int,),
    "extraction_miss_streak": (int,),
    "forge_miss_streak": (int,),
    "gems": (list,),
    "hp": (int,),
    "initial_skills_learned": (int,),
    "inventory": (list,),
    "last_interest_floor": (int,),
    "ledger": (dict,),
    "level": (int,),
    "map_state": (dict, _NADA),
    "mp": (int,),
    "passives": (list,),
    "player_class": (str,),
    "player_name": (str,),
    "seen_skill_ids": (list,),
    "shop_miss_streak": (int,),
    "skill_cooldowns": (dict,),
    "skills": (dict,),
    "unpaid_exit_streak": (int,),
    "xp": (int,),
}

# O que tem de sobreviver intacto à reconstrução canônica. O `ledger` fica de
# fora: é contabilidade da run, e `equip` o incrementa ao reequipar na carga.
CAMPOS_DO_CICLO = (
    "player_class",
    "player_name",
    "level",
    "equipment",
    "inventory",
    "gems",
    "passives",
    "skills",
    "extracted_on_floor",
)

Migracao = Callable[[dict], dict]

# Migrações do registro, de N para N+1. Vazio: o esquema 1 é o primeiro. Uma
# entrada nova vem com o teste que leva um registro real do esquema antigo até
# o novo e o põe para lutar.
MIGRACOES: dict[int, Migracao] = {}


class GladiadorIncompativelError(ValueError):
    """O gladiador não pode entrar em partida nesta versão."""

    def __init__(self, problemas: Iterable[str]) -> None:
        self.problemas = tuple(problemas)
        super().__init__("; ".join(self.problemas) or "gladiador incompatível")


def _tipo_certo(valor, tipos: tuple[type, ...]) -> bool:
    # `bool` é `int` em Python, e `true` no lugar de um número é dado errado.
    if isinstance(valor, bool):
        return bool in tipos
    return isinstance(valor, tipos)


def _json(dados) -> object:
    """O valor como o JSON o vê: chaves texto, tuplas como listas."""
    return json.loads(json.dumps(dados, sort_keys=True))


def impressao_do_registro(registro: Mapping) -> str:
    """sha256 do registro guardado: a partida guarda esta etiqueta de cada lado."""
    texto = json.dumps(registro, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(texto.encode()).hexdigest()


# --- as conferências ---------------------------------------------------------------


def _nome_do_item(registro) -> str | None:
    if isinstance(registro, str):
        return registro
    if isinstance(registro, dict) and isinstance(registro.get("name"), str):
        return registro["name"]
    return None


def problemas_estruturais(snapshot) -> list[str]:
    """Campos, tipos, extração e referências ao catálogo. Não reconstrói nada."""
    if not isinstance(snapshot, dict):
        return ["O snapshot precisa ser um objeto."]
    problemas = []
    faltam = sorted(set(CAMPOS_DO_SNAPSHOT) - set(snapshot))
    sobram = sorted(set(snapshot) - set(CAMPOS_DO_SNAPSHOT))
    if faltam:
        problemas.append(f"Campos ausentes no snapshot: {faltam}.")
    if sobram:
        problemas.append(
            f"Campos que o esquema {ESQUEMA_ATUAL} não conhece: {sobram} "
            "(formato mais novo, exige versão e migração)."
        )
    for campo, tipos in CAMPOS_DO_SNAPSHOT.items():
        if campo in snapshot and not _tipo_certo(snapshot[campo], tipos):
            problemas.append(f"`{campo}` com tipo {type(snapshot[campo]).__name__}.")
    if problemas:
        return problemas

    if snapshot["level"] < 1:
        problemas.append(f"Nível {snapshot['level']} inválido.")
    if snapshot["extracted_on_floor"] <= 0:
        problemas.append("O personagem não encerrou a run pela Extração.")

    catalogo = get_all_items()
    registros = list(snapshot["inventory"]) + [r for r in snapshot["equipment"].values() if r]
    for registro in registros:
        nome = _nome_do_item(registro)
        if nome is None:
            problemas.append(f"Item sem nome: {registro!r}.")
        elif nome not in catalogo:
            problemas.append(f"Item {nome!r} não existe no catálogo desta versão.")
    for pid in snapshot["passives"]:
        if not isinstance(pid, str) or get_passive_by_id(pid) is None:
            problemas.append(f"Passiva {pid!r} não existe no catálogo desta versão.")
    for chave, sid in snapshot["skills"].items():
        if not isinstance(sid, str) or get_skill_by_id(sid) is None:
            problemas.append(f"Carta {sid!r} (slot {chave}) não existe no catálogo desta versão.")
    return problemas


def _reconstruir(snapshot: dict):
    """O personagem pelo caminho canônico, ou a razão por que não reconstrói."""
    try:
        return character_from_snapshot(snapshot), None
    except GladiatorNotEligibleError as erro:
        return None, str(erro)
    except (KeyError, TypeError, ValueError) as erro:
        return None, f"A reconstrução canônica falhou: {type(erro).__name__}: {erro}"


def problemas_do_ciclo(snapshot: dict, heroi) -> list[str]:
    """O personagem reconstruído devolve, pelo mesmo `to_save_data`, o snapshot?"""
    volta = _json(to_save_data(heroi, snapshot["dungeon_level"], snapshot["map_state"]))
    original = _json(snapshot)
    return [
        f"`{campo}` não sobrevive à reconstrução canônica: o carregador descartaria ou "
        "mudaria dados."
        for campo in CAMPOS_DO_CICLO
        if volta[campo] != original[campo]
    ]


def problemas_do_snapshot(snapshot) -> list[str]:
    """Tudo o que impede este snapshot de virar gladiador. Vazio = válido."""
    problemas = problemas_estruturais(snapshot)
    if problemas:
        return problemas
    heroi, erro = _reconstruir(snapshot)
    if erro:
        return [erro]
    return problemas_do_ciclo(snapshot, heroi)


# --- o registro e a migração --------------------------------------------------------


def registro_de_snapshot(snapshot: dict) -> dict:
    """O registro do esquema atual para um snapshot de save. Valida antes de aceitar."""
    problemas = problemas_do_snapshot(snapshot)
    if problemas:
        raise GladiadorIncompativelError(problemas)
    return {"esquema": ESQUEMA_ATUAL, "snapshot": copy.deepcopy(snapshot)}


def migrar(
    registro,
    migracoes: Mapping[int, Migracao] | None = None,
    atual: int = ESQUEMA_ATUAL,
) -> dict:
    """O registro levado ao esquema atual, passo a passo. Nunca altera `registro`."""
    migracoes = MIGRACOES if migracoes is None else migracoes
    if not isinstance(registro, dict):
        raise GladiadorIncompativelError(["O registro do gladiador precisa ser um objeto."])
    esquema = registro.get("esquema")
    if type(esquema) is not int or esquema < 1:
        raise GladiadorIncompativelError([f"Esquema do registro ilegível: {esquema!r}."])
    if esquema > atual:
        raise GladiadorIncompativelError(
            [f"Registro do esquema {esquema}, mais novo que o desta versão ({atual})."]
        )
    dados = copy.deepcopy(registro)
    while dados["esquema"] < atual:
        de = dados["esquema"]
        passo = migracoes.get(de)
        if passo is None:
            raise GladiadorIncompativelError(
                [f"Não há migração registrada do esquema {de} para {de + 1}."]
            )
        dados = passo(copy.deepcopy(dados))
        if not isinstance(dados, dict) or dados.get("esquema") != de + 1:
            raise GladiadorIncompativelError(
                [f"A migração do esquema {de} não produziu o esquema {de + 1}."]
            )
    return dados


def gladiador_de_registro(registro, migracoes: Mapping[int, Migracao] | None = None) -> Gladiator:
    """O gladiador pronto para o duelo, ou `GladiadorIncompativelError`. Não altera `registro`."""
    atual = migrar(registro, migracoes)
    if set(atual) != {"esquema", "snapshot"}:
        raise GladiadorIncompativelError([f"Campos do registro: {sorted(atual)}."])
    snapshot = atual["snapshot"]
    problemas = problemas_estruturais(snapshot)
    if problemas:
        raise GladiadorIncompativelError(problemas)
    heroi, erro = _reconstruir(snapshot)
    if erro:
        raise GladiadorIncompativelError([erro])
    problemas = problemas_do_ciclo(snapshot, heroi)
    if problemas:
        raise GladiadorIncompativelError(problemas)
    return prepare_gladiator(heroi)


class AcervoDeGladiadores:
    """Os gladiadores que o servidor conhece, pelo id. O cliente só nomeia o id.

    O registro fica no servidor: o cliente nunca envia ficha, atributo ou
    equipamento. Cada `preparar` valida de novo — um registro que deixou de ser
    compatível (catálogo novo, esquema novo) é recusado na hora, e não depois.
    """

    def __init__(self, registros: Mapping[str, dict] | None = None) -> None:
        # Cópia própria, em JSON: nada que o chamador faça depois chega aqui.
        self._registros = {str(g): _json(r) for g, r in (registros or {}).items()}

    @classmethod
    def de_snapshots(cls, snapshots: Mapping[str, dict]) -> AcervoDeGladiadores:
        return cls({gid: registro_de_snapshot(s) for gid, s in snapshots.items()})

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._registros))

    def impressao(self, gladiador_id: str) -> str:
        return impressao_do_registro(self._registros[gladiador_id])

    def preparar(self, gladiador_id: str) -> tuple[Gladiator, str]:
        """O gladiador validado e a impressão do registro de onde ele veio."""
        registro = self._registros.get(gladiador_id)
        if registro is None:
            raise GladiadorIncompativelError(
                [f"O gladiador {gladiador_id!r} não existe neste servidor."]
            )
        return gladiador_de_registro(registro), impressao_do_registro(registro)
