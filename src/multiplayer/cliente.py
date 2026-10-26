"""O cliente de referência: identidade, autenticação, comandos de sessão e a ação.

Ele não calcula nada do combate. Recebe a observação, entrega a `DuelView` ao
controlador (humano, bot ou roteiro — o mesmo `DuelController` do modo local) e
manda de volta só a ação escolhida. Tudo o mais que chega é registro.

A senha só passa por `login()` para virar mensagem; o cliente não a guarda. O
token de acesso e a sessão ficam em atributos que não aparecem no `repr`.
"""

from __future__ import annotations

import json

from src.mechanics.pvp_duel import DuelController
from src.multiplayer import protocolo
from src.multiplayer.manifesto import Identidade


class ClienteMultiplayer:
    def __init__(self, identidade: Identidade, controlador: DuelController | None = None) -> None:
        self.identidade = identidade
        self.controlador = controlador
        self.token: str | None = None
        self.sessao: str | None = None
        self.conta: str | None = None
        self.usuario: str | None = None
        self.gladiadores: list[dict] = []
        self.sala: str | None = None
        self.partida: str | None = None
        self.lado: str | None = None
        self.ficha: dict | None = None
        self.adversario: dict | None = None
        self.recebidas: list[dict] = []
        self.recusas: list[dict] = []
        self.fim: dict | None = None

    def __repr__(self) -> str:
        return f"ClienteMultiplayer(usuario={self.usuario!r}, partida={self.partida!r})"

    # --- o que o cliente envia --------------------------------------------------------

    def _versao(self) -> dict:
        return self.identidade.como_dict()

    def login(self, usuario: str, senha: str) -> str:
        return protocolo.codificar("login", identidade=self._versao(), usuario=usuario, senha=senha)

    def ola(self) -> str:
        if self.token is None:
            raise RuntimeError("Sem token: faça o login antes.")
        return protocolo.codificar("ola", identidade=self._versao(), token=self.token)

    def entrar_na_fila(self, gladiador: str) -> str:
        return protocolo.codificar("entrar_na_fila", identidade=self._versao(), gladiador=gladiador)

    def criar_sala(self, gladiador: str) -> str:
        return protocolo.codificar("criar_sala", identidade=self._versao(), gladiador=gladiador)

    def entrar_na_sala(self, sala: str, gladiador: str) -> str:
        return protocolo.codificar(
            "entrar_na_sala", identidade=self._versao(), sala=sala, gladiador=gladiador
        )

    def reconectar(self) -> str:
        if self.sessao is None or self.token is None:
            raise RuntimeError("Sem sessão para reconectar.")
        return protocolo.codificar(
            "reconectar", identidade=self._versao(), sessao=self.sessao, token=self.token
        )

    def acao(self, rodada: int, acao) -> str:
        return protocolo.codificar(
            "acao", partida=self.partida, rodada=rodada, acao=protocolo.acao_para_dict(acao)
        )

    # --- o que o cliente recebe ------------------------------------------------------

    def receber(self, texto: str) -> list[str]:
        """Uma mensagem do servidor. Devolve as respostas (a ação, quando é a vez)."""
        mensagem = json.loads(texto)
        self.recebidas.append(mensagem)
        tipo = mensagem.get("tipo")
        if tipo == "autenticado":
            self.token, self.conta, self.usuario = (
                mensagem["token"],
                mensagem["conta"],
                mensagem["usuario"],
            )
        elif tipo == "bem_vindo":
            self.sessao = mensagem["sessao"]
            self.conta, self.usuario = mensagem["conta"], mensagem["usuario"]
            self.gladiadores = list(mensagem["gladiadores"])
        elif tipo == "recusado":
            self.recusas.append(mensagem)
        elif tipo == "sala_criada":
            self.sala = mensagem["sala"]
        elif tipo == "partida_criada":
            self.partida, self.lado, self.fim = mensagem["partida"], mensagem["lado"], None
            self.ficha, self.adversario, self.sala = mensagem["voce"], mensagem["adversario"], None
        elif tipo == "fim":
            self.fim = mensagem
            self.partida = None
        elif tipo == "observacao" and self.controlador is not None:
            visao = protocolo.visao_de_dict(mensagem["visao"])
            return [self.acao(visao.round_number, self.controlador.choose(visao))]
        return []

    def ultima(self, tipo: str) -> dict | None:
        return next((m for m in reversed(self.recebidas) if m.get("tipo") == tipo), None)
