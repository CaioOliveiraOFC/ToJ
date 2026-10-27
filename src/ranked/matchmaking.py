"""Matchmaking da Ranked: o adversário é escolhido pelo jogo, nunca pelo jogador.

As 10 partidas de posicionamento têm três etapas:

- **Descoberta (1–4):** o alvo é a estimativa atual, e o adversário sai de uma
  faixa LARGA em volta dela (±1 desvio da população), sorteada: o jogo vê o
  gladiador contra níveis diferentes enquanto a incerteza ainda é grande.
- **Nivelamento (5–7):** faixa de ±0,5 desvio, entre os mais próximos do alvo.
- **Validação (8–10):** faixa de ±0,25 desvio, o mais próximo possível — as
  últimas partidas conferem o posicionamento.

Depois, a ranqueada normal usa ±0,35 desvio.

O rating muda desde a primeira partida, e é ele que move o alvo: vencer alguém
forte sobe mais do que vencer alguém fraco. A SEQUÊNCIA empurra o alvo um pouco
além disso, mas só conta resultado contra adversário do mesmo nível ou acima
(vitória) ou do mesmo nível ou abaixo (derrota): três vitórias sobre gladiadores
muito mais fracos não endurecem o próximo adversário.

Quem enfrentou o gladiador nas últimas `RECENTES` partidas fica de fora enquanto
houver alternativa. Tudo depende só do estado da Ladder e do gerador recebido.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from src.ranked.ladder import Ladder

DESCOBERTA = "descoberta"
NIVELAMENTO = "nivelamento"
VALIDACAO = "validacao"
RANQUEADA = "ranqueada"

JANELA = {DESCOBERTA: 1.0, NIVELAMENTO: 0.5, VALIDACAO: 0.25, RANQUEADA: 0.35}
MAIS_PROXIMOS = {DESCOBERTA: 1, NIVELAMENTO: 4, VALIDACAO: 2, RANQUEADA: 5}
RECENTES = 3
EMPURRAO_POR_RESULTADO = 0.15
SEQUENCIA_MAXIMA = 3


def fase(partidas_jogadas: int) -> str:
    """A etapa da PRÓXIMA partida, pelo número de partidas já jogadas."""
    if partidas_jogadas < 4:
        return DESCOBERTA
    if partidas_jogadas < 7:
        return NIVELAMENTO
    if partidas_jogadas < 10:
        return VALIDACAO
    return RANQUEADA


@dataclass(frozen=True)
class Escolha:
    oponente: str
    fase: str
    alvo: float
    desvio: float


def desvio_da_populacao(ladder: Ladder, candidatos: list[str]) -> float:
    valores = [ladder.valor(c) for c in candidatos]
    media = sum(valores) / len(valores)
    return math.sqrt(sum((v - media) ** 2 for v in valores) / len(valores)) or 1.0


def empurrao_da_sequencia(ladder: Ladder, identidade: str, desvio: float) -> float:
    """Quanto a sequência atual empurra o alvo, contando só resultados que dizem algo.

    Vitória conta se o derrotado não estava muito abaixo (mais de meio desvio);
    derrota conta se o vencedor não estava muito acima. A sequência para no
    primeiro resultado do outro tipo.
    """
    historico = ladder[identidade].historico
    if not historico:
        return 0.0
    sinal = 1 if historico[-1]["venceu"] else -1
    conta = 0
    for entrada in reversed(historico):
        if entrada["venceu"] != (sinal > 0):
            break
        diferenca = entrada["oponente_antes"] - entrada["antes"]
        if (sinal > 0 and diferenca >= -0.5 * desvio) or (sinal < 0 and diferenca <= 0.5 * desvio):
            conta += 1
    return sinal * min(SEQUENCIA_MAXIMA, conta) * EMPURRAO_POR_RESULTADO * desvio


def escolher_oponente(ladder: Ladder, identidade: str, rng, *, excluir=()) -> Escolha:
    """O próximo adversário NPC de `identidade`. Determinístico pelo `rng`."""
    proibidos = {identidade, *excluir}
    candidatos = [r.identidade for r in ladder.npcs() if r.identidade not in proibidos]
    if not candidatos:
        raise ValueError("nenhum adversário disponível")
    etapa = fase(ladder[identidade].partidas)
    desvio = desvio_da_populacao(ladder, candidatos)
    alvo = ladder.valor(identidade) + empurrao_da_sequencia(ladder, identidade, desvio)
    if etapa == DESCOBERTA:
        alvo += rng.uniform(-1.0, 1.0) * JANELA[DESCOBERTA] * desvio
    recentes = {e["oponente"] for e in ladder[identidade].historico[-RECENTES:]}
    janela = JANELA[etapa] * desvio
    escolhidos: list[str] = []
    for _ in range(8):
        escolhidos = [
            c for c in candidatos if c not in recentes and abs(ladder.valor(c) - alvo) <= janela
        ]
        if escolhidos:
            break
        janela *= 2
    if not escolhidos:
        # Só sobraram recentes: repetir é melhor do que não jogar.
        escolhidos = candidatos
    escolhidos.sort(key=lambda c: (abs(ladder.valor(c) - alvo), c))
    oponente = rng.choice(escolhidos[: MAIS_PROXIMOS[etapa]])
    return Escolha(oponente, etapa, alvo, desvio)


def parear_npcs(ladder: Ladder, rng, quantidade: int) -> list[tuple[str, str]]:
    """Duplas NPC × NPC de nível parecido, sem gladiador repetido no lote."""
    livres = sorted(r.identidade for r in ladder.npcs())
    rng.shuffle(livres)
    pares: list[tuple[str, str]] = []
    ocupados: set[str] = set()
    for identidade in livres:
        if len(pares) >= quantidade:
            break
        if identidade in ocupados:
            continue
        try:
            escolha = escolher_oponente(ladder, identidade, rng, excluir=ocupados)
        except ValueError:
            break
        pares.append((identidade, escolha.oponente))
        ocupados |= {identidade, escolha.oponente}
    return pares


def rodada_suica(
    ladder: Ladder, rng, vizinhos: int = 3, recentes: int = RECENTES
) -> list[tuple[str, str]]:
    """Uma rodada em que cada NPC joga uma vez, contra um dos vizinhos de rating.

    Para calibração: a lista é percorrida do mais forte ao mais fraco, e cada um
    enfrenta, entre os `vizinhos` livres mais próximos, um que ele não enfrentou
    nas últimas `recentes` partidas.
    """
    ordem = sorted(ladder.npcs(), key=lambda r: (-ladder.valor(r.identidade), r.identidade))
    livres = [r.identidade for r in ordem]
    pares: list[tuple[str, str]] = []
    while len(livres) >= 2:
        atual = livres.pop(0)
        vistos = {e["oponente"] for e in ladder[atual].historico[-recentes:]}
        opcoes = [c for c in livres if c not in vistos][:vizinhos] or livres[:1]
        oponente = rng.choice(opcoes)
        livres.remove(oponente)
        pares.append((atual, oponente))
    return pares
