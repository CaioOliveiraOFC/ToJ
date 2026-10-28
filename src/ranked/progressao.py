"""A progressão visível da Ranked: 45 divisões de 100 PR, de Iron V a Obsidian I.

Três coisas diferentes, e só uma delas é a verdade:

- **MMR** (o rating do Glicko-2, com incerteza) — a estimativa competitiva. É
  ele que escolhe adversário e ordena a classificação.
- **Percentil** — a posição na população competitiva. Os limites dos ranks são
  de percentil (`ranks.LIMITES`).
- **PR** — a barra de 0 a 100 dentro da divisão. É a progressão que o jogador
  VÊ, e anda atrás do MMR: nunca é um segundo MMR.

## O alvo

O percentil vira uma coordenada contínua, o ALVO, na mesma régua das divisões:
cada rank vale 500 (5 divisões × 100 PR), e dentro do rank a coordenada é
linear no percentil. Iron V 0 PR é 0; Obsidian I 100 PR é 4.500; a elite
continua a régua (Master de 4.500 a 5.000, e assim por diante). A coordenada
VISÍVEL é `100 × divisão + PR`.

## A variação de PR

    ΔPR = K · (S − E) · m

- `S` é o resultado (1 vitória, ½ empate, 0 derrota) e `E` a chance que o
  Glicko-2 dava antes da partida. Vencer quem era favorito rende mais; perder
  para quem era azarão custa mais. Na média, `S − E` é zero: jogar muito, sem
  melhorar, não sobe ninguém.
- `m` puxa a coordenada visível para o alvo: com `g = (alvo − visível)/100`
  (em divisões), o ganho é multiplicado por `e^{βg}` e a perda por `e^{−βg}`,
  os dois presos em [1/M, M]. Quem está ABAIXO do que o MMR diz sobe mais rápido
  e cai mais devagar; quem está ACIMA, o contrário. No alvo, `m = 1`.

## Promoção, rebaixamento e o escudo

- 100 PR ou mais promove para a divisão seguinte, e o excedente vai junto (a
  coordenada é contínua). Uma partida move no máximo uma divisão.
- Abaixo de 0 PR rebaixa para a divisão anterior, com o que faltou descontado
  de 100 — mas no máximo `PR_APOS_REBAIXAMENTO` (75): voltar à divisão de cima
  exige mais de uma vitória, e a fronteira não vira pisca-pisca.
- Depois de uma promoção, as `ESCUDO` partidas seguintes não rebaixam (o PR
  para em 0) — mas só enquanto o alvo não estiver mais de uma divisão abaixo:
  o escudo segura a oscilação na fronteira, não esconde um gladiador que está
  no lugar errado.
- Iron V não desce de 0. Em Obsidian I, o PR para em 100: aí o gladiador vira
  **Candidato a Master**, e a promoção à elite só acontece na atualização da
  leaderboard (`leaderboard.py`). A candidatura se perde ao cair de Obsidian I.

## O posicionamento

Durante as 10 partidas de posicionamento não há PR (o MMR já anda). Na 10ª, a
coordenada visível nasce NO alvo (divisão e PR), com o escudo de uma promoção,
e no máximo Obsidian I com 0 PR: a barra de Obsidian I, que leva à
candidatura, sempre se conquista jogando. A mesma regra vale para os NPCs na
fundação e para quem sai da elite.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.ranked import ranks

ROMANOS = ("V", "IV", "III", "II", "I")
DIVISOES_POR_RANK = len(ROMANOS)
RANKS_COM_DIVISOES = ranks.RANKS[:9]
ELITE = ranks.RANKS[9:]
DIVISOES = len(RANKS_COM_DIVISOES) * DIVISOES_POR_RANK
PR_POR_DIVISAO = 100
POR_RANK = DIVISOES_POR_RANK * PR_POR_DIVISAO
TOPO = DIVISOES * PR_POR_DIVISAO
ULTIMA = DIVISOES - 1

# Parâmetros da fórmula (proposta da Fase 6.1, ver `reports/ranked/fase61/`).
K = 40.0
BETA = 0.20
MULTIPLICADOR_MAXIMO = 3.0
VARIACAO_MAXIMA = 60
ESCUDO = 3
PR_APOS_REBAIXAMENTO = 75


@dataclass
class Progresso:
    """O que o gladiador mostra. `divisao` é `None` enquanto posiciona."""

    divisao: int | None = None
    pr: int = 0
    escudo: int = 0
    candidato: bool = False
    # A elite e o título vêm da leaderboard publicada (`leaderboard.py`).
    elite: str | None = None
    risco: bool = False
    titulo: str | None = None

    @property
    def coordenada(self) -> int | None:
        if self.divisao is None:
            return None
        return self.divisao * PR_POR_DIVISAO + self.pr

    def para_dict(self) -> dict:
        return {
            "divisao": self.divisao,
            "pr": self.pr,
            "escudo": self.escudo,
            "candidato": self.candidato,
            "elite": self.elite,
            "risco": self.risco,
            "titulo": self.titulo,
        }

    @classmethod
    def de_dict(cls, d: dict | None) -> Progresso:
        d = d or {}
        divisao = d.get("divisao")
        return cls(
            divisao=None if divisao is None else int(divisao),
            pr=int(d.get("pr", 0)),
            escudo=int(d.get("escudo", 0)),
            candidato=bool(d.get("candidato", False)),
            elite=d.get("elite"),
            risco=bool(d.get("risco", False)),
            titulo=d.get("titulo"),
        )


def nome_da_divisao(divisao: int) -> str:
    if not 0 <= divisao <= ULTIMA:
        raise ValueError(f"divisão {divisao} fora de 0–{ULTIMA}")
    rank, dentro = divmod(divisao, DIVISOES_POR_RANK)
    return f"{RANKS_COM_DIVISOES[rank]} {ROMANOS[dentro]}"


def rank_da_divisao(divisao: int) -> str:
    return RANKS_COM_DIVISOES[divisao // DIVISOES_POR_RANK]


def alvo(percentil: float, limites: tuple[float, ...] = ranks.LIMITES) -> float:
    """O percentil na régua das divisões: linear dentro de cada rank."""
    teto = (*limites[1:], 100.0)
    for i, (minimo, maximo) in enumerate(zip(limites, teto)):
        if percentil < maximo or i == len(limites) - 1:
            largura = maximo - minimo
            fracao = 1.0 if largura <= 0 else (percentil - minimo) / largura
            return POR_RANK * (i + max(0.0, min(1.0, fracao)))
    raise AssertionError("inalcançável")


def multiplicador(ganho: bool, distancia_em_divisoes: float) -> float:
    expoente = BETA * distancia_em_divisoes * (1 if ganho else -1)
    return max(1.0 / MULTIPLICADOR_MAXIMO, min(MULTIPLICADOR_MAXIMO, math.exp(expoente)))


def variacao(pontos: float, esperado: float, coordenada: float, meta: float) -> int:
    """ΔPR de uma partida: resultado contra a expectativa, puxado para o alvo."""
    surpresa = pontos - esperado
    if surpresa == 0:
        return 0
    bruto = K * surpresa * multiplicador(surpresa > 0, (meta - coordenada) / PR_POR_DIVISAO)
    valor = int(round(bruto))
    if valor == 0 and pontos != 0.5:
        valor = 1 if surpresa > 0 else -1
    return max(-VARIACAO_MAXIMA, min(VARIACAO_MAXIMA, valor))


def posicionar(meta: float) -> Progresso:
    """A coordenada inicial: o alvo, no máximo Obsidian I com 0 PR, com escudo."""
    coordenada = max(0, min(ULTIMA * PR_POR_DIVISAO, int(meta)))
    divisao, pr = divmod(coordenada, PR_POR_DIVISAO)
    return Progresso(divisao=divisao, pr=pr, escudo=ESCUDO)


def aplicar(progresso: Progresso, delta: int, meta: float) -> list[dict]:
    """Aplica ΔPR e devolve os eventos (promoção, rebaixamento, candidatura)."""
    if progresso.elite is not None or progresso.divisao is None:
        return []
    eventos: list[dict] = []
    antes = progresso.divisao
    escudo = progresso.escudo
    progresso.escudo = max(0, escudo - 1)
    pr = progresso.pr + delta
    if pr >= PR_POR_DIVISAO and progresso.divisao < ULTIMA:
        pr -= PR_POR_DIVISAO
        progresso.divisao += 1
        progresso.escudo = ESCUDO
        pr = min(pr, PR_POR_DIVISAO - 1)
        eventos.append({"evento": "promocao", "de": antes, "para": progresso.divisao})
    if progresso.divisao == ULTIMA and pr >= PR_POR_DIVISAO:
        pr = PR_POR_DIVISAO
        if not progresso.candidato:
            progresso.candidato = True
            eventos.append({"evento": "candidatura"})
    if pr < 0:
        piso = progresso.divisao * PR_POR_DIVISAO
        protegido = escudo > 0 and meta >= piso - PR_POR_DIVISAO
        if progresso.divisao == 0 or protegido:
            if protegido and progresso.divisao > 0:
                eventos.append({"evento": "escudo", "divisao": progresso.divisao})
            pr = 0
        else:
            progresso.divisao -= 1
            pr = max(0, min(PR_APOS_REBAIXAMENTO, pr + PR_POR_DIVISAO))
            progresso.escudo = 0
            eventos.append({"evento": "rebaixamento", "de": antes, "para": progresso.divisao})
    progresso.pr = pr
    if progresso.candidato and progresso.divisao < ULTIMA:
        progresso.candidato = False
        eventos.append({"evento": "candidatura_perdida"})
    return eventos
