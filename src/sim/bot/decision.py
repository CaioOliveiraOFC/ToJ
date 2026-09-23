"""A decisão, e a única representação dela.

A MESMA `Decision` que o driver executa é a que alimenta o trace. Não existe
"função A decide, função B descobre depois por que A decidiu" — era daí que vinha
um trace que dizia "já tenho ouro para a saída" em 48 saídas nas quais o portão
fechado tinha sido o HP.

A `Decision` aponta para um `action_id`. Ela não carrega `Hero`, `Monster`,
`Skill` nem `Item`, e não tem campo `Any`: um `Mapping[str, Any]` deixaria um
objeto de jogo atravessar a fronteira por dentro da decisão. Quem resolve
`action_id` -> objeto real -> `battle.Action` é o adaptador.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum

from src.sim.bot.observation import ActionMechanicsView, TargetView


class Need(IntEnum):
    """A necessidade que uma ação atende. Menor é mais urgente.

    Existe porque ouro, sobrevivência, extração e turnos NÃO são conversíveis
    entre si, e inventar um fator para somá-los seria a constante mágica que esta
    refatoração existe para eliminar.

    A necessidade ORDENA necessidades incompatíveis; a `utility` compara
    alternativas dentro de uma necessidade comparável. Ela nunca impede uma ação
    de ser enumerada, avaliada ou registrada — só de ganhar a comparação.

    A `need` de uma ação é atribuída pelo avaliador A PARTIR DO ESTADO, e não é
    rótulo fixo: a Loja atende RECUPERAR quando o HP está baixo e a cura paga
    cabe, e INVESTIR quando não está.
    """

    SOBREVIVER = 1
    # PRESERVAR nasceu porque a decisão de extrair é BOOLEANA e não cabia em
    # nenhum tier existente sem uma constante calibrada contra outro avaliador.
    # A matriz de extração diz apenas "preserve" ou "continue"; encaixá-la em
    # `SOBREVIVER` exigiria utility acima do teto da Loja (2,0) e faria extrair
    # vencer beber poção com vida crítica, e em `RECUPERAR` exigiria passar do
    # teto da saída (`HP_DE_APOSTA - hp_frac`). Os dois números quebrariam em
    # silêncio quando aqueles avaliadores mudassem.
    #
    # Sozinha no tier, a utility da extração não é comparada com nada: qualquer
    # valor positivo dá o mesmo comportamento, e por isso ela deixa de ser um
    # câmbio entre grandezas. Emergência de vida continua acima; recuperação e
    # progressão passam a ficar abaixo — que é exatamente a ordem pedida.
    PRESERVAR = 2
    RECUPERAR = 3
    PROGREDIR = 4
    INVESTIR = 5
    ENCERRAR = 6


@dataclass(frozen=True, slots=True)
class ActionOption:
    """Uma ação JÁ declarada legal pelo adaptador.

    O cérebro não enumera legalidade: MP, recarga, requisito de equipamento,
    existência do item e alcançabilidade da casa são regra do jogo, e regra do
    jogo vive do outro lado da fronteira. A policy só avalia o que recebe — e,
    por construção, não consegue escolher algo que não recebeu.
    """

    action_id: str
    # Qual avaliador atende esta ação.
    family: str
    # Para o trace ler como humano. Não entra em decisão.
    label: str = ""
    mechanics: ActionMechanicsView = ActionMechanicsView()
    target: TargetView | None = None


@dataclass(frozen=True, slots=True)
class Score:
    """A nota de UMA candidata, com as parcelas visíveis.

    `components` é o que torna a decisão auditável: um valor absurdo aparece na
    parcela que o produziu, em vez de se esconder dentro de um número só.
    """

    action_id: str
    need: Need
    utility: float
    components: tuple[tuple[str, float], ...] = ()
    # Desempate DENTRO da mesma utility. Não é somado a ela: serve para ordenar
    # coisas cujo custo tem unidade diferente (passos contra lutas no caminho)
    # sem inventar uma conversão entre as duas.
    tiebreak: float = 0.0
    note: str = ""

    def explicar(self) -> str:
        partes = ", ".join(f"{nome} {valor:+.2f}" for nome, valor in self.components)
        texto = f"{self.action_id} [{self.need.name}] {self.utility:+.2f}"
        if partes:
            texto += f" ({partes})"
        if self.note:
            texto += f" — {self.note}"
        return texto


@dataclass(frozen=True, slots=True)
class Decision:
    """O que fazer, por quê, e o que mais estava na mesa."""

    action_id: str
    reason: str
    scores: tuple[Score, ...] = ()

    def explicar_candidatas(self) -> str:
        return " | ".join(s.explicar() for s in self.scores)


def escolher(scores: tuple[Score, ...], motivo_de: dict[str, str]) -> Decision:
    """A escolha, lexicográfica: `min(need)`, depois `max(utility)`.

    Duas regras que valem a pena estar escritas:

    1. Só ganha quem tem `utility > 0`. Sem isso, uma ação de necessidade urgente
       e valor nulo venceria uma ação útil de necessidade menos urgente — beber
       poção com a vida cheia ganharia de lutar. Filtrar por valor não é gate:
       a ação continua enumerada, avaliada e no trace; ela só perde.
    2. Se NADA rende, vence a de maior utilidade ainda assim. O andar sempre tem
       saída, então sempre existe uma resposta; um empate vazio seria a
       ferramenta pendurando.

    O desempate final é `action_id`, para que a decisão seja determinística e a
    mesma seed produza a mesma run.
    """
    if not scores:
        raise ValueError("escolher() recebeu zero candidatas — o adaptador não enumerou nada")

    def chave(s: Score) -> tuple:
        return (s.need, -s.utility, -s.tiebreak, s.action_id)

    uteis = [s for s in scores if s.utility > 0]
    vencedora = min(uteis or list(scores), key=chave)
    return Decision(
        action_id=vencedora.action_id,
        reason=motivo_de.get(vencedora.action_id, vencedora.note or vencedora.action_id),
        scores=tuple(sorted(scores, key=chave)),
    )
