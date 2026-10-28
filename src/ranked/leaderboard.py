"""A leaderboard publicada: atualizações periódicas, a candidatura a Master e a elite.

O MMR muda a cada partida; a leaderboard PUBLICADA, não. Ela é um retrato da
classificação tirado no começo de cada ciclo (`PERIODO`, 1 hora por padrão,
configurável — 24 horas também é um ciclo válido). É no retrato, e só nele,
que a elite muda:

1. **Integridade.** O retrato só sai de uma Ladder íntegra
   (`Ladder.problemas`); senão a atualização fica adiada, e o ciclo continua
   pendente.
2. **A elite que já existe.** Quem está em Master, International Master ou
   Distinguished Master fica se o percentil continua no mínimo de Master. Abaixo
   dele, mas a menos de `FAIXA_DE_RISCO` pontos, o gladiador entra EM RISCO; se
   ainda estiver abaixo no retrato seguinte, ou se cair além da faixa, é
   rebaixado para a divisão do alvo (como num posicionamento, no máximo
   Obsidian I com 0 PR). Ninguém precisa jogar entre um retrato e outro.
3. **As candidaturas.** O Candidato a Master (Obsidian I com 100 PR, e que não
   caiu de Obsidian I desde então) é promovido se, no retrato, (a) continua
   candidato e posicionado, (b) o percentil alcança o mínimo de Master e (c) a
   classificação dele é confiável: RD até `RD_MAXIMO_PARA_PROMOVER`. Senão,
   continua candidato e é avaliado de novo no próximo retrato — sem promoção
   automática por ter acumulado PR.
4. **O nível na elite** é o rank que o percentil dá no retrato (no mínimo
   Master), e os cinco membros da elite mais bem colocados recebem a distinção
   **Definitive Masters**.

A atualização é offline e não precisa de processo rodando: quem chama passa o
relógio (`agora`), e um retorno depois de muitos ciclos perdidos publica UM
retrato só (`MundoRanqueado.atualizar_leaderboard`), reproduzível pelo estado
gravado.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from src.ranked import progressao, ranks
from src.ranked.ladder import Ladder

PERIODO = 3600
RD_MAXIMO_PARA_PROMOVER = 150.0
FAIXA_DE_RISCO = 3.0
EVENTOS_MAXIMOS = 200
MINIMO_DA_ELITE = ranks.LIMITES[ranks.RANKS.index(progressao.ELITE[0])]


def ciclo(agora: float, periodo: int = PERIODO, origem: float = 0.0) -> int:
    """O número do ciclo que contém `agora`; os ciclos começam em `origem + k·periodo`."""
    return math.floor((agora - origem) / periodo)


def inicio(numero: int, periodo: int = PERIODO, origem: float = 0.0) -> float:
    return origem + numero * periodo


@dataclass
class Leaderboard:
    periodo: int = PERIODO
    origem: float = 0.0
    # O último ciclo publicado; `None` antes da primeira sessão (a fundação vale).
    ciclo: int | None = None
    publicada_em: float | None = None
    linhas: list[dict] = field(default_factory=list)
    anteriores: dict[str, int] = field(default_factory=dict)
    eventos: list[dict] = field(default_factory=list)
    adiada: list[str] = field(default_factory=list)

    def proxima(self) -> float | None:
        """Quando sai o próximo retrato (o começo do ciclo seguinte)."""
        if self.ciclo is None:
            return None
        return inicio(self.ciclo + 1, self.periodo, self.origem)

    def pendente(self, agora: float) -> bool:
        return self.ciclo is not None and ciclo(agora, self.periodo, self.origem) > self.ciclo

    def linha(self, identidade: str) -> dict | None:
        return next((x for x in self.linhas if x["identidade"] == identidade), None)

    def variacao(self, identidade: str) -> int | None:
        """Posições ganhas desde o retrato anterior (positivo = subiu)."""
        atual = self.linha(identidade)
        if atual is None or identidade not in self.anteriores:
            return None
        return self.anteriores[identidade] - atual["posicao"]

    def para_dict(self) -> dict:
        return {
            "periodo": self.periodo,
            "origem": self.origem,
            "ciclo": self.ciclo,
            "publicada_em": self.publicada_em,
            "linhas": self.linhas,
            "anteriores": self.anteriores,
            "eventos": self.eventos,
            "adiada": self.adiada,
        }

    @classmethod
    def de_dict(cls, d: dict | None) -> Leaderboard:
        d = d or {}
        return cls(
            periodo=int(d.get("periodo", PERIODO)),
            origem=float(d.get("origem", 0.0)),
            ciclo=d.get("ciclo"),
            publicada_em=d.get("publicada_em"),
            linhas=list(d.get("linhas") or []),
            anteriores={str(k): int(v) for k, v in (d.get("anteriores") or {}).items()},
            eventos=list(d.get("eventos") or []),
            adiada=list(d.get("adiada") or []),
        )


def _nivel(percentil: float) -> str:
    return ranks.rank_do_percentil(max(percentil, MINIMO_DA_ELITE))


def publicar(
    ladder: Ladder,
    leaderboard: Leaderboard,
    agora: float | None,
    *,
    numero: int | None,
    fundacao: bool = False,
) -> dict:
    """Tira o retrato do ciclo `numero` e aplica a candidatura e a elite.

    Na FUNDAÇÃO (o estado inicial publicado, ou a migração de um estado antigo)
    não há candidatura ainda: todo competitivo no percentil de elite entra nela,
    e os outros recebem a divisão do alvo. Devolve o resumo, com os eventos.
    """
    problemas = ladder.problemas() if not fundacao else []
    if problemas:
        leaderboard.adiada = problemas[:10]
        return {"ciclo": numero, "adiada": leaderboard.adiada, "eventos": []}
    ordem = ladder.classificacao()
    total = len(ordem)
    percentis = {r.identidade: ranks.percentil(i, total) for i, r in enumerate(ordem, start=1)}
    eventos: list[dict] = []

    def evento(registro, nome: str, **detalhe) -> None:
        dados = {"evento": nome, "ciclo": numero, **detalhe}
        eventos.append({"identidade": registro.identidade, "nome": registro.nome, **dados})
        registro.anotar(dados)

    for r in ordem:
        p = r.progresso
        pct = percentis[r.identidade]
        if fundacao:
            if pct >= MINIMO_DA_ELITE:
                r.progresso = progressao.Progresso(elite=_nivel(pct))
            elif p.elite is None and p.divisao is None:
                r.progresso = progressao.posicionar(progressao.alvo(pct))
            continue
        if p.elite is not None:
            if pct >= MINIMO_DA_ELITE:
                if p.risco:
                    evento(r, "fora_de_risco", percentil=round(pct, 1))
                p.risco = False
            elif pct >= MINIMO_DA_ELITE - FAIXA_DE_RISCO and not p.risco:
                p.risco = True
                evento(r, "em_risco", percentil=round(pct, 1))
            else:
                r.progresso = progressao.posicionar(progressao.alvo(pct))
                evento(
                    r,
                    "rebaixamento_da_elite",
                    de=p.elite,
                    para=r.progresso.divisao,
                    percentil=round(pct, 1),
                )
            continue
        if p.divisao is None:
            # Um NPC novo no catálogo, ainda sem divisão.
            r.progresso = progressao.posicionar(progressao.alvo(pct))
            continue
        if p.candidato:
            motivos = []
            if pct < MINIMO_DA_ELITE:
                motivos.append(f"percentil {pct:.1f} abaixo de {MINIMO_DA_ELITE:g}")
            if ladder.incerteza(r.identidade) > RD_MAXIMO_PARA_PROMOVER:
                motivos.append(
                    f"incerteza {ladder.incerteza(r.identidade):.0f} acima de "
                    f"{RD_MAXIMO_PARA_PROMOVER:g}"
                )
            if motivos:
                evento(r, "candidatura_mantida", percentil=round(pct, 1), motivos=motivos)
            else:
                r.progresso = progressao.Progresso(elite=_nivel(pct))
                evento(r, "promocao_a_elite", para=r.progresso.elite, percentil=round(pct, 1))
    # O nível na elite e os Definitive Masters, pelo retrato.
    vagas = ranks.DEFINITIVE_MASTERS
    for r in ordem:
        p = r.progresso
        if p.elite is None:
            p.titulo = None
            continue
        nivel = _nivel(percentis[r.identidade])
        if nivel != p.elite and not fundacao:
            subiu = ranks.RANKS.index(nivel) > ranks.RANKS.index(p.elite)
            evento(r, "elite_sobe" if subiu else "elite_desce", de=p.elite, para=nivel)
        p.elite = nivel
        p.titulo = ranks.TITULO_DEFINITIVO if vagas > 0 else None
        vagas -= 1
    leaderboard.anteriores = {x["identidade"]: x["posicao"] for x in leaderboard.linhas}
    leaderboard.linhas = [
        {
            "identidade": r.identidade,
            "nome": r.nome,
            "classe": r.classe,
            "jogador": not r.npc,
            "posicao": i,
            "percentil": round(percentis[r.identidade], 2),
            "rating": round(ladder.valor(r.identidade), 2),
            "rd": round(ladder.incerteza(r.identidade), 2),
            "exibicao": ladder.exibicao(r.identidade),
            "elite": r.progresso.elite,
            "divisao": r.progresso.divisao,
            "pr": r.progresso.pr,
            "candidato": r.progresso.candidato,
            "titulo": r.progresso.titulo,
            "vitorias": r.vitorias,
            "derrotas": r.derrotas,
            "empates": r.empates,
        }
        for i, r in enumerate(ordem, start=1)
    ]
    leaderboard.ciclo = numero
    leaderboard.publicada_em = agora
    leaderboard.adiada = []
    leaderboard.eventos.extend(eventos)
    del leaderboard.eventos[:-EVENTOS_MAXIMOS]
    return {"ciclo": numero, "adiada": [], "eventos": eventos}
