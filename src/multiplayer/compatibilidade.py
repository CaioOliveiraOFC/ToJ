"""A decisão de compatibilidade: igual, ou recusado.

Não existe "versão próxima". Cliente e servidor jogam juntos quando as duas
identidades são idênticas — versão do jogo, protocolo, regras de combate,
esquema do gladiador e todos os hashes —, e em qualquer outro caso o cliente é
recusado com a mensagem de que a atualização é obrigatória. Isso vale para
cliente mais velho, mais novo, ou com o mesmo número e outro conteúdo.

A ordem das conferências só escolhe o motivo da recusa, para a mensagem dizer o
que está diferente; qualquer diferença recusa.
"""

from __future__ import annotations

from dataclasses import dataclass

from src.multiplayer.manifesto import Identidade, IdentidadeInvalidaError

# Os motivos de recusa, estáveis: o cliente pode traduzir por eles.
IDENTIDADE_INVALIDA = "identidade_invalida"
VERSAO_DO_JOGO = "versao_do_jogo"
PROTOCOLO = "protocolo"
REGRAS = "regras"
ESQUEMA = "esquema_gladiador"
CONTEUDO = "conteudo"
SERVIDOR_EM_ATUALIZACAO = "servidor_em_atualizacao"

MOTIVOS_DE_VERSAO = (IDENTIDADE_INVALIDA, VERSAO_DO_JOGO, PROTOCOLO, REGRAS, ESQUEMA, CONTEUDO)


@dataclass(frozen=True)
class Decisao:
    aceita: bool
    motivo: str | None = None
    mensagem: str = ""
    versao_exigida: str | None = None

    @property
    def atualizacao_obrigatoria(self) -> bool:
        return not self.aceita


def _recusa(motivo: str, detalhe: str, servidor: Identidade) -> Decisao:
    return Decisao(
        aceita=False,
        motivo=motivo,
        mensagem=(
            f"Atualização do jogo obrigatória: o servidor exige a versão {servidor.jogo}. {detalhe}"
        ),
        versao_exigida=servidor.jogo,
    )


def decidir(servidor: Identidade, cliente) -> Decisao:
    """A conexão competitiva é autorizada só quando as identidades são idênticas.

    `cliente` pode chegar como `Identidade` ou como o objeto cru da mensagem; a
    forma é conferida aqui, sem tolerância.
    """
    if not isinstance(cliente, Identidade):
        try:
            cliente = Identidade.de_dict(cliente)
        except IdentidadeInvalidaError as erro:
            return _recusa(IDENTIDADE_INVALIDA, f"Identidade de versão ilegível: {erro}", servidor)
    if cliente == servidor:
        return Decisao(aceita=True)
    if cliente.jogo != servidor.jogo:
        return _recusa(VERSAO_DO_JOGO, f"Este cliente é a versão {cliente.jogo}.", servidor)
    if cliente.protocolo != servidor.protocolo:
        return _recusa(
            PROTOCOLO,
            f"Protocolo do cliente {cliente.protocolo}, do servidor {servidor.protocolo}.",
            servidor,
        )
    if cliente.regras != servidor.regras:
        return _recusa(
            REGRAS,
            f"Regras de combate do cliente {cliente.regras!r}, do servidor {servidor.regras!r}.",
            servidor,
        )
    if cliente.esquema_gladiador != servidor.esquema_gladiador:
        return _recusa(
            ESQUEMA,
            f"Esquema de gladiador do cliente {cliente.esquema_gladiador}, "
            f"do servidor {servidor.esquema_gladiador}.",
            servidor,
        )
    divergentes = sorted(
        g for g, h in dict(cliente.grupos).items() if dict(servidor.grupos).get(g) != h
    )
    return _recusa(
        CONTEUDO,
        "O número da versão é o mesmo, mas o conteúdo não: "
        f"{', '.join(divergentes) or 'conteúdo'} diferem da distribuição oficial.",
        servidor,
    )


def recusa_por_atualizacao(servidor: Identidade) -> Decisao:
    """O servidor está retirando esta versão: nada novo começa nela."""
    return Decisao(
        aceita=False,
        motivo=SERVIDOR_EM_ATUALIZACAO,
        mensagem=(
            f"A versão {servidor.jogo} está sendo retirada do servidor. "
            "Atualize o jogo para entrar na fila."
        ),
        versao_exigida=None,
    )
