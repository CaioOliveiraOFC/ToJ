"""A Ladder: o estado competitivo de cada gladiador e a classificação.

Cada gladiador — NPC da população ou gladiador extraído do jogador — tem um
`Registro`: identidade persistente, rating e incerteza (do sistema escolhido),
vitórias, derrotas, partidas de posicionamento e o histórico recente de
confrontos. Uma partida atualiza os DOIS lados, com os valores de antes dela.

A classificação é pelo rating, entre os gladiadores COMPETITIVOS: todos os NPCs
e os gladiadores do jogador que já cumpriram as 10 partidas de posicionamento.
Quem está posicionando não aparece na classificação nem tem rank, mas o rating
dele já muda desde a primeira partida.

O histórico guardado por gladiador é o recente (`HISTORICO_MAXIMO`); os totais
de vitórias e derrotas são de sempre. Nada aqui sabe de motor, tela ou disco:
quem joga e grava é `engine/`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from src.ranked import ranks

POSICIONAMENTO = 10
HISTORICO_MAXIMO = 50


@dataclass
class Registro:
    identidade: str
    nome: str
    classe: str
    npc: bool
    rating: object
    vitorias: int = 0
    derrotas: int = 0
    historico: list[dict] = field(default_factory=list)
    # A força de referência (OP) do NPC: só a priori fraca, nunca rating.
    forca_de_referencia: float | None = None

    @property
    def partidas(self) -> int:
        return self.vitorias + self.derrotas

    @property
    def posicionado(self) -> bool:
        return self.npc or self.partidas >= POSICIONAMENTO


@dataclass(frozen=True)
class Atualizacao:
    """O que uma partida mudou, para a tela de resultado e para o histórico."""

    vencedor: str
    perdedor: str
    antes: dict
    depois: dict
    probabilidade_do_vencedor: float


class Ladder:
    def __init__(self, sistema, registros: list[Registro] | None = None) -> None:
        self.sistema = sistema
        self._registros: dict[str, Registro] = {}
        self.partidas_jogadas = 0
        for r in registros or ():
            self.adicionar(r)

    # -- registros --

    def adicionar(self, registro: Registro) -> None:
        if registro.identidade in self._registros:
            raise ValueError(f"identidade repetida na Ladder: {registro.identidade}")
        self._registros[registro.identidade] = registro

    def __contains__(self, identidade: str) -> bool:
        return identidade in self._registros

    def __getitem__(self, identidade: str) -> Registro:
        return self._registros[identidade]

    def registros(self) -> list[Registro]:
        return list(self._registros.values())

    def npcs(self) -> list[Registro]:
        return [r for r in self._registros.values() if r.npc]

    # -- leitura --

    def valor(self, identidade: str) -> float:
        return self.sistema.exibicao(self._registros[identidade].rating)

    def incerteza(self, identidade: str) -> float:
        return self.sistema.incerteza(self._registros[identidade].rating)

    def esperado(self, a: str, b: str) -> float:
        return self.sistema.esperado(self._registros[a].rating, self._registros[b].rating)

    def classificacao(self) -> list[Registro]:
        """Os competitivos, do primeiro ao último. Empate de rating desempata pela identidade."""
        competitivos = [r for r in self._registros.values() if r.posicionado]
        return sorted(competitivos, key=lambda r: (-self.sistema.exibicao(r.rating), r.identidade))

    def posicao(self, identidade: str) -> int | None:
        """A posição (1 = primeiro) de um competitivo; `None` para quem posiciona."""
        registro = self._registros[identidade]
        if not registro.posicionado:
            return None
        meu = self.sistema.exibicao(registro.rating)
        acima = sum(
            1
            for r in self._registros.values()
            if r.posicionado
            and r.identidade != identidade
            and (self.sistema.exibicao(r.rating), identidade) > (meu, r.identidade)
        )
        return acima + 1

    def competitivos(self) -> int:
        return sum(r.posicionado for r in self._registros.values())

    def percentil(self, identidade: str) -> float | None:
        posicao = self.posicao(identidade)
        return None if posicao is None else ranks.percentil(posicao, self.competitivos())

    def rank(self, identidade: str) -> str | None:
        valor = self.percentil(identidade)
        return None if valor is None else ranks.rank_do_percentil(valor)

    def titulo(self, identidade: str) -> str | None:
        posicao = self.posicao(identidade)
        return None if posicao is None else ranks.titulo(posicao)

    # -- a partida --

    def registrar(self, a: str, b: str, vencedor: str, *, origem: str, extra=None) -> Atualizacao:
        """Aplica o resultado de uma partida aos dois lados."""
        if vencedor not in (a, b) or a == b:
            raise ValueError("resultado incoerente")
        ra, rb = self._registros[a], self._registros[b]
        antes = {a: ra.rating, b: rb.rating}
        prob = self.sistema.esperado(ra.rating, rb.rating)
        prob_vencedor = prob if vencedor == a else 1.0 - prob
        ra.rating, rb.rating = self.sistema.partida(ra.rating, rb.rating, vencedor == a)
        self.partidas_jogadas += 1
        for meu, outro in ((ra, rb), (rb, ra)):
            venceu = meu.identidade == vencedor
            if venceu:
                meu.vitorias += 1
            else:
                meu.derrotas += 1
            meu.historico.append(
                {
                    "n": self.partidas_jogadas,
                    "oponente": outro.identidade,
                    "venceu": venceu,
                    "antes": round(self.sistema.exibicao(antes[meu.identidade]), 2),
                    "depois": round(self.sistema.exibicao(meu.rating), 2),
                    "oponente_antes": round(self.sistema.exibicao(antes[outro.identidade]), 2),
                    "origem": origem,
                    **(extra or {}),
                }
            )
            del meu.historico[:-HISTORICO_MAXIMO]
        return Atualizacao(
            vencedor,
            b if vencedor == a else a,
            {i: self.sistema.exibicao(r) for i, r in antes.items()},
            {i: self.sistema.exibicao(self._registros[i].rating) for i in (a, b)},
            prob_vencedor,
        )

    def registrar_sem_resultado(self, a: str, b: str, *, origem: str, extra=None) -> None:
        """Um confronto que terminou sem vencedor: entra no histórico, não no rating.

        Não conta como partida (nem de posicionamento) e não mexe em vitórias e
        derrotas; fica no histórico para o matchmaking não repetir a dupla logo.
        """
        if a == b:
            raise ValueError("resultado incoerente")
        self.partidas_jogadas += 1
        for meu, outro in (
            (self._registros[a], self._registros[b]),
            (self._registros[b], self._registros[a]),
        ):
            valor = round(self.sistema.exibicao(meu.rating), 2)
            meu.historico.append(
                {
                    "n": self.partidas_jogadas,
                    "oponente": outro.identidade,
                    "venceu": None,
                    "antes": valor,
                    "depois": valor,
                    "oponente_antes": round(self.sistema.exibicao(outro.rating), 2),
                    "origem": origem,
                    **(extra or {}),
                }
            )
            del meu.historico[:-HISTORICO_MAXIMO]

    def inatividade(self, periodos: float) -> None:
        """A incerteza de todos cresce com o tempo sem jogar (a volta depois de dias fora)."""
        for r in self._registros.values():
            r.rating = self.sistema.inatividade(r.rating, periodos)

    # -- persistência --

    def para_dict(self) -> dict:
        return {
            "partidas_jogadas": self.partidas_jogadas,
            "registros": [
                {
                    "identidade": r.identidade,
                    "nome": r.nome,
                    "classe": r.classe,
                    "npc": r.npc,
                    "rating": self.sistema.serializar(r.rating),
                    "vitorias": r.vitorias,
                    "derrotas": r.derrotas,
                    "historico": r.historico,
                    "forca_de_referencia": r.forca_de_referencia,
                }
                for r in self._registros.values()
            ],
        }

    @classmethod
    def de_dict(cls, sistema, dados: dict) -> Ladder:
        ladder = cls(sistema)
        ladder.partidas_jogadas = int(dados.get("partidas_jogadas", 0))
        for d in dados["registros"]:
            ladder.adicionar(
                Registro(
                    identidade=str(d["identidade"]),
                    nome=str(d["nome"]),
                    classe=str(d["classe"]),
                    npc=bool(d["npc"]),
                    rating=sistema.desserializar(d["rating"]),
                    vitorias=int(d["vitorias"]),
                    derrotas=int(d["derrotas"]),
                    historico=list(d.get("historico") or []),
                    forca_de_referencia=d.get("forca_de_referencia"),
                )
            )
        return ladder
