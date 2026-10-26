"""O registro de gladiadores do servidor: o snapshot validado e o seu DONO.

A propriedade é do servidor. O cliente nunca envia ficha, snapshot ou dono: ele
nomeia o id de um gladiador, e o servidor confere aqui se aquele gladiador
pertence à conta autenticada da sessão.

Como um gladiador entra:

- só por `importar`, chamado pelo administrador do servidor, nunca por mensagem
  de rede;
- o snapshot passa pela validação estrita de `gladiadores.registro_de_snapshot`
  — extração real, esquema exato, catálogo desta versão, reconstrução canônica
  sem perda;
- a origem é registrada. Hoje a única origem confiável é o snapshot PUBLICADO de
  uma Copa (`importar_da_copa`), conferido pelo sha256 do índice
  `gladiadores.json` da Copa. Ainda não existe caminho para o servidor receber e
  confiar numa extração nova feita num computador de jogador.

O que não existe, de propósito: transferência entre contas, troca de dono, e o
mesmo personagem registrado duas vezes (cópia para outra conta). O arquivo do
registro guarda a impressão de cada registro; alterado por fora, o gladiador é
recusado na preparação.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from src.mechanics.pvp_duel import Gladiator
from src.multiplayer.contas import gravar_privado
from src.multiplayer.gladiadores import (
    GladiadorIncompativelError,
    gladiador_de_registro,
    impressao_do_registro,
    registro_de_snapshot,
)

ARQUIVO_DO_REGISTRO = "gladiadores.json"
ID_VALIDO = re.compile(r"^[A-Za-z0-9_-]{1,32}$")


class PropriedadeError(ValueError):
    """Registro recusado: id repetido, personagem já registrado ou origem não confere."""


@dataclass(frozen=True)
class FichaResumida:
    """O que o próprio dono vê na lista dos seus gladiadores.

    `nome` é o do personagem no snapshot; `apelido`, quando a origem tem um (o
    `nick` publicado pela Copa), só identifica o gladiador na lista. O duelo usa
    o personagem como ele é.
    """

    id: str
    nome: str
    classe: str
    nivel: int
    apelido: str | None = None

    def como_dict(self) -> dict:
        return {
            "id": self.id,
            "nome": self.nome,
            "apelido": self.apelido,
            "classe": self.classe,
            "nivel": self.nivel,
        }


class RegistroDeGladiadores:
    """Gladiadores, donos e origens, num arquivo JSON (`None` = só em memória)."""

    def __init__(self, arquivo: Path | None = None) -> None:
        self._arquivo = arquivo
        self._itens: dict[str, dict] = {}
        if arquivo is not None and arquivo.exists():
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            if dados.get("formato") != 1:
                raise ValueError(f"{arquivo.name}: formato desconhecido.")
            self._itens = dict(dados["gladiadores"])

    @classmethod
    def na_pasta(cls, pasta: Path) -> RegistroDeGladiadores:
        return cls(pasta / ARQUIVO_DO_REGISTRO)

    def __repr__(self) -> str:
        return f"RegistroDeGladiadores({len(self._itens)} gladiadores)"

    def _gravar(self) -> None:
        if self._arquivo is not None:
            texto = json.dumps({"formato": 1, "gladiadores": self._itens}, indent=2, sort_keys=True)
            gravar_privado(self._arquivo, texto + "\n")

    # --- entrada --------------------------------------------------------------------

    def importar(self, gladiador_id: str, snapshot: dict, dono: str, origem: dict) -> FichaResumida:
        """Registra um gladiador para `dono` (id de conta). Só o administrador chama."""
        if not ID_VALIDO.match(str(gladiador_id)):
            raise PropriedadeError(f"Id de gladiador inválido: {gladiador_id!r}.")
        if gladiador_id in self._itens:
            raise PropriedadeError(f"O gladiador {gladiador_id} já está registrado.")
        if not isinstance(dono, str) or not dono:
            raise PropriedadeError("Gladiador sem dono.")
        registro = registro_de_snapshot(snapshot)  # GladiadorIncompativelError
        impressao = impressao_do_registro(registro)
        repetido = next((g for g, i in self._itens.items() if i["impressao"] == impressao), None)
        if repetido is not None:
            raise PropriedadeError(
                f"Este personagem já está registrado como {repetido}: não há cópia nem "
                "transferência entre contas."
            )
        self._itens[gladiador_id] = {
            "dono": dono,
            "registro": registro,
            "impressao": impressao,
            "origem": dict(origem),
        }
        self._gravar()
        return self.ficha(gladiador_id)

    # --- leitura --------------------------------------------------------------------

    def ids(self) -> tuple[str, ...]:
        return tuple(sorted(self._itens))

    def dono_de(self, gladiador_id: str) -> str | None:
        item = self._itens.get(gladiador_id)
        return None if item is None else item["dono"]

    def origem(self, gladiador_id: str) -> dict:
        return dict(self._itens[gladiador_id]["origem"])

    def ficha(self, gladiador_id: str) -> FichaResumida:
        item = self._itens[gladiador_id]
        snapshot = item["registro"]["snapshot"]
        return FichaResumida(
            gladiador_id,
            str(snapshot["player_name"]),
            str(snapshot["player_class"]),
            int(snapshot["level"]),
            item["origem"].get("apelido"),
        )

    def de(self, conta_id: str) -> tuple[FichaResumida, ...]:
        return tuple(self.ficha(g) for g in self.ids() if self._itens[g]["dono"] == conta_id)

    def impressao(self, gladiador_id: str) -> str:
        return self._itens[gladiador_id]["impressao"]

    def preparar(self, gladiador_id: str) -> tuple[Gladiator, str]:
        """O gladiador validado e a impressão do registro. Mesma interface do acervo."""
        item = self._itens.get(gladiador_id)
        if item is None:
            raise GladiadorIncompativelError(
                [f"O gladiador {gladiador_id!r} não existe neste servidor."]
            )
        if impressao_do_registro(item["registro"]) != item["impressao"]:
            raise GladiadorIncompativelError(
                [f"O registro do gladiador {gladiador_id} foi alterado fora do servidor."]
            )
        return gladiador_de_registro(item["registro"]), item["impressao"]


def importar_da_copa(
    registro: RegistroDeGladiadores, pasta_da_copa: Path, gladiador_id: str, dono: str
) -> FichaResumida:
    """Origem confiável: o snapshot publicado de uma Copa, conferido pelo sha256 do índice."""
    indice = json.loads((pasta_da_copa / "gladiadores.json").read_text(encoding="utf-8"))
    entrada = next((g for g in indice["gladiadores"] if g["id"] == gladiador_id), None)
    if entrada is None:
        raise PropriedadeError(f"{gladiador_id} não está no índice de {pasta_da_copa.name}.")
    arquivo = (pasta_da_copa / entrada["snapshot"]).resolve()
    if pasta_da_copa.resolve() not in arquivo.parents:
        raise PropriedadeError("O índice aponta para fora da pasta da Copa.")
    bruto = arquivo.read_bytes()
    sha = hashlib.sha256(bruto).hexdigest()
    if sha != entrada["sha256"]:
        raise PropriedadeError(f"O snapshot de {gladiador_id} não é o publicado (sha256 difere).")
    return registro.importar(
        gladiador_id,
        json.loads(bruto),
        dono,
        origem={
            "tipo": "copa_publicada",
            "copa": str(indice.get("copa", pasta_da_copa.name)),
            "arquivo": entrada["snapshot"],
            "sha256": sha,
            "apelido": entrada.get("nick"),
        },
    )
