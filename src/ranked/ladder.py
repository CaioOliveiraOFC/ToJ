"""A Ladder: o estado competitivo de cada gladiador e a classificação.

Cada gladiador — NPC da população ou gladiador extraído do jogador — tem um
`Registro`: identidade persistente, rating e incerteza (do sistema escolhido),
vitórias, derrotas, empates, a progressão visível (divisão e PR, ou a elite,
`progressao.py`) e o histórico recente de confrontos. Uma partida atualiza os
DOIS lados, com os valores de antes dela.

Os desfechos de uma partida:

- **vitória/derrota** (KO ou rendição) — 1 e 0 no rating;
- **empate técnico** (impasse ou teto, `impasse.py`) — ½ para cada lado; conta
  como partida disputada (também no posicionamento), não como vitória nem
  derrota;
- **anulada** (interrupção ou erro técnico) — entra no histórico e mais nada:
  não muda rating, PR nem contagem, e não consome partida de posicionamento.

A classificação é pelo rating, entre os gladiadores COMPETITIVOS: todos os NPCs
e os gladiadores do jogador que já cumpriram as 10 partidas de posicionamento.
Quem está posicionando não aparece na classificação nem tem divisão, mas o
rating dele já muda desde a primeira partida.

O histórico guardado por gladiador é o recente (`HISTORICO_MAXIMO`); os totais
de vitórias, derrotas e empates são de sempre. Nada aqui sabe de motor, tela,
relógio ou disco: quem joga e grava é `engine/`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.ranked import progressao, ranks
from src.ranked.progressao import Progresso

POSICIONAMENTO = 10
HISTORICO_MAXIMO = 50
EVENTOS_MAXIMOS = 30

VITORIA = "vitoria"
DERROTA = "derrota"
EMPATE = "empate"
ANULADA = "anulada"


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
    empates: int = 0
    progresso: Progresso = field(default_factory=Progresso)
    # Promoções, rebaixamentos, candidatura e elite, os mais recentes.
    eventos: list[dict] = field(default_factory=list)

    @property
    def partidas(self) -> int:
        """As disputadas: vitórias, derrotas e empates. Anuladas não contam."""
        return self.vitorias + self.derrotas + self.empates

    @property
    def posicionado(self) -> bool:
        return self.npc or self.partidas >= POSICIONAMENTO

    def anotar(self, evento: dict) -> None:
        self.eventos.append(evento)
        del self.eventos[:-EVENTOS_MAXIMOS]


@dataclass(frozen=True)
class Atualizacao:
    """O que uma partida mudou, para a tela de resultado e para o histórico."""

    a: str
    b: str
    vencedor: str | None
    antes: dict
    depois: dict
    probabilidade_de_a: float
    pr: dict
    eventos: dict

    @property
    def empate(self) -> bool:
        return self.vencedor is None

    @property
    def perdedor(self) -> str | None:
        if self.vencedor is None:
            return None
        return self.b if self.vencedor == self.a else self.a

    @property
    def probabilidade_do_vencedor(self) -> float | None:
        if self.vencedor is None:
            return None
        return self.probabilidade_de_a if self.vencedor == self.a else 1 - self.probabilidade_de_a

    def esperado(self, identidade: str) -> float:
        return self.probabilidade_de_a if identidade == self.a else 1 - self.probabilidade_de_a


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
        """O rank que o PERCENTIL de agora daria (a régua matemática, não a exibida)."""
        valor = self.percentil(identidade)
        return None if valor is None else ranks.rank_do_percentil(valor)

    def alvo(self, identidade: str) -> float | None:
        """O percentil de agora na régua das divisões (`progressao.alvo`)."""
        valor = self.percentil(identidade)
        return None if valor is None else progressao.alvo(valor)

    def titulo(self, identidade: str) -> str | None:
        """O título publicado na última atualização da leaderboard (Definitive Master)."""
        return self._registros[identidade].progresso.titulo

    def exibicao(self, identidade: str) -> str | None:
        """O que o gladiador mostra: a elite, a divisão com PR, ou `None` (posicionando)."""
        p = self._registros[identidade].progresso
        if p.elite is not None:
            return p.elite
        if p.divisao is None:
            return None
        return f"{progressao.nome_da_divisao(p.divisao)} — {p.pr}/{progressao.PR_POR_DIVISAO} PR"

    # -- a partida --

    def registrar(self, a: str, b: str, vencedor: str, *, origem: str, extra=None) -> Atualizacao:
        """Vitória de `vencedor`, por KO ou rendição: 1 e 0 no rating."""
        if vencedor not in (a, b) or a == b:
            raise ValueError("resultado incoerente")
        return self._resultado(a, b, 1.0 if vencedor == a else 0.0, origem, extra, None)

    def registrar_empate(
        self, a: str, b: str, *, origem: str, motivo: str, extra=None
    ) -> Atualizacao:
        """Empate técnico (`motivo`: impasse ou teto): ½ para cada lado."""
        if a == b:
            raise ValueError("resultado incoerente")
        return self._resultado(a, b, 0.5, origem, extra, motivo)

    def _resultado(self, a, b, pontos_de_a, origem, extra, motivo) -> Atualizacao:
        ra, rb = self._registros[a], self._registros[b]
        antes = {a: ra.rating, b: rb.rating}
        prob_a = self.sistema.esperado(ra.rating, rb.rating)
        # O alvo é o de antes da partida, como o rating.
        metas = {
            r.identidade: self.alvo(r.identidade)
            for r in (ra, rb)
            if r.progresso.divisao is not None and r.progresso.elite is None
        }
        ra.rating, rb.rating = self.sistema.partida(ra.rating, rb.rating, pontos_de_a)
        self.partidas_jogadas += 1
        variacoes: dict[str, int | None] = {}
        eventos: dict[str, list[dict]] = {}
        for meu, outro, pontos, esperado in (
            (ra, rb, pontos_de_a, prob_a),
            (rb, ra, 1.0 - pontos_de_a, 1.0 - prob_a),
        ):
            if pontos == 0.5:
                meu.empates += 1
            elif pontos == 1.0:
                meu.vitorias += 1
            else:
                meu.derrotas += 1
            delta, mudancas = None, []
            if meu.identidade in metas:
                meta = metas[meu.identidade]
                delta = progressao.variacao(pontos, esperado, meu.progresso.coordenada, meta)
                mudancas = progressao.aplicar(meu.progresso, delta, meta)
            elif (
                not meu.npc
                and meu.progresso.divisao is None
                and meu.progresso.elite is None
                and meu.partidas == POSICIONAMENTO
            ):
                meu.progresso = progressao.posicionar(self.alvo(meu.identidade))
                mudancas = [{"evento": "posicionamento", "para": meu.progresso.divisao}]
            variacoes[meu.identidade] = delta
            eventos[meu.identidade] = mudancas
            for mudanca in mudancas:
                meu.anotar({"n": self.partidas_jogadas, **mudanca})
            resultado = EMPATE if pontos == 0.5 else (VITORIA if pontos == 1.0 else DERROTA)
            meu.historico.append(
                {
                    "n": self.partidas_jogadas,
                    "oponente": outro.identidade,
                    "resultado": resultado,
                    "venceu": None if pontos == 0.5 else pontos == 1.0,
                    "antes": round(self.sistema.exibicao(antes[meu.identidade]), 2),
                    "depois": round(self.sistema.exibicao(meu.rating), 2),
                    "oponente_antes": round(self.sistema.exibicao(antes[outro.identidade]), 2),
                    "origem": origem,
                    **({"motivo": motivo} if motivo else {}),
                    **({"pr": delta} if delta is not None else {}),
                    **(extra or {}),
                }
            )
            del meu.historico[:-HISTORICO_MAXIMO]
        if pontos_de_a == 0.5:
            vencedor = None
        else:
            vencedor = a if pontos_de_a == 1.0 else b
        return Atualizacao(
            a,
            b,
            vencedor,
            {i: self.sistema.exibicao(r) for i, r in antes.items()},
            {i: self.sistema.exibicao(self._registros[i].rating) for i in (a, b)},
            prob_a,
            variacoes,
            eventos,
        )

    def registrar_anulada(self, a: str, b: str, *, origem: str, motivo: str, extra=None) -> None:
        """Uma partida anulada (interrupção, erro técnico): só o histórico guarda.

        Não muda rating, PR nem contagem, e não consome partida de
        posicionamento; fica no histórico para o matchmaking não repetir a
        dupla logo.
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
                    "resultado": ANULADA,
                    "venceu": None,
                    "antes": valor,
                    "depois": valor,
                    "oponente_antes": round(self.sistema.exibicao(outro.rating), 2),
                    "origem": origem,
                    "motivo": motivo,
                    **(extra or {}),
                }
            )
            del meu.historico[:-HISTORICO_MAXIMO]

    def registrar_sem_resultado(self, a: str, b: str, *, origem: str, extra=None) -> None:
        """A partida que bateu o limite técnico da Fase 6: anulada (para os replays dela)."""
        self.registrar_anulada(a, b, origem=origem, motivo="limite", extra=extra)

    def inatividade(self, periodos: float) -> None:
        """A incerteza de todos cresce com o tempo sem jogar (a volta depois de dias fora)."""
        for r in self._registros.values():
            r.rating = self.sistema.inatividade(r.rating, periodos)

    def posicionar_npc(self, identidade: str) -> None:
        """A divisão de um NPC que ainda não tem nenhuma: a do alvo, como no posicionamento."""
        registro = self._registros[identidade]
        if registro.npc and registro.progresso.divisao is None and registro.progresso.elite is None:
            registro.progresso = progressao.posicionar(self.alvo(identidade))

    # -- integridade --

    def problemas(self) -> list[str]:
        """O que impede uma atualização confiável da leaderboard; vazio se está íntegra."""
        erros = []
        for r in self._registros.values():
            valor, incerteza = self.sistema.exibicao(r.rating), self.sistema.incerteza(r.rating)
            if not (math.isfinite(valor) and math.isfinite(incerteza) and incerteza > 0):
                erros.append(f"{r.identidade}: rating inválido")
            if min(r.vitorias, r.derrotas, r.empates) < 0:
                erros.append(f"{r.identidade}: contagem negativa")
            p = r.progresso
            if p.divisao is not None and not (
                0 <= p.divisao <= progressao.ULTIMA and 0 <= p.pr <= progressao.PR_POR_DIVISAO
            ):
                erros.append(f"{r.identidade}: divisão ou PR fora da régua")
            if p.candidato and p.divisao != progressao.ULTIMA:
                erros.append(f"{r.identidade}: candidato fora de Obsidian I")
            if p.elite is not None and p.elite not in progressao.ELITE:
                erros.append(f"{r.identidade}: elite desconhecida")
            if r.posicionado and p.divisao is None and p.elite is None:
                erros.append(f"{r.identidade}: competitivo sem divisão")
        return erros

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
                    "empates": r.empates,
                    "historico": r.historico,
                    "forca_de_referencia": r.forca_de_referencia,
                    "progresso": r.progresso.para_dict(),
                    "eventos": r.eventos,
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
                    empates=int(d.get("empates", 0)),
                    historico=list(d.get("historico") or []),
                    forca_de_referencia=d.get("forca_de_referencia"),
                    progresso=Progresso.de_dict(d.get("progresso")),
                    eventos=list(d.get("eventos") or []),
                )
            )
        return ladder
