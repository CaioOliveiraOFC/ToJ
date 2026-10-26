"""O cliente de referência: identidade, comandos de sessão e a ação do controlador.

Ele não calcula nada do combate. Recebe a observação, entrega a `DuelView` ao
controlador (humano, bot ou roteiro — o mesmo `DuelController` do modo local) e
manda de volta só a ação escolhida. Tudo o mais que chega é registro.
"""

from __future__ import annotations

import json

from src.mechanics.pvp_duel import DuelController
from src.multiplayer import protocolo
from src.multiplayer.manifesto import Identidade


class ClienteMultiplayer:
    def __init__(
        self,
        identidade: Identidade,
        jogador: str,
        controlador: DuelController | None = None,
    ) -> None:
        self.identidade = identidade
        self.jogador = jogador
        self.controlador = controlador
        self.token: str | None = None
        self.partida: str | None = None
        self.lado: str | None = None
        self.recebidas: list[dict] = []
        self.recusas: list[dict] = []
        self.fim: dict | None = None

    # --- o que o cliente envia --------------------------------------------------------

    def ola(self) -> str:
        return protocolo.codificar(
            "ola", identidade=self.identidade.como_dict(), jogador=self.jogador
        )

    def entrar_na_fila(self, gladiador: str) -> str:
        return protocolo.codificar(
            "entrar_na_fila", identidade=self.identidade.como_dict(), gladiador=gladiador
        )

    def reconectar(self) -> str:
        if self.token is None:
            raise RuntimeError("Sem sessão para reconectar.")
        return protocolo.codificar(
            "reconectar", identidade=self.identidade.como_dict(), token=self.token
        )

    # --- o que o cliente recebe ------------------------------------------------------

    def receber(self, texto: str) -> list[str]:
        """Uma mensagem do servidor. Devolve as respostas (a ação, quando é a vez)."""
        mensagem = json.loads(texto)
        self.recebidas.append(mensagem)
        tipo = mensagem.get("tipo")
        if tipo == "bem_vindo":
            self.token = mensagem["token"]
        elif tipo == "recusado":
            self.recusas.append(mensagem)
        elif tipo == "partida_criada":
            self.partida, self.lado, self.fim = mensagem["partida"], mensagem["lado"], None
        elif tipo == "fim":
            self.fim = mensagem
            self.partida = None
        elif tipo == "observacao" and self.controlador is not None:
            visao = protocolo.visao_de_dict(mensagem["visao"])
            acao = self.controlador.choose(visao)
            return [
                protocolo.codificar(
                    "acao",
                    partida=mensagem["partida"],
                    rodada=visao.round_number,
                    acao=protocolo.acao_para_dict(acao),
                )
            ]
        return []

    def ultima(self, tipo: str) -> dict | None:
        return next((m for m in reversed(self.recebidas) if m.get("tipo") == tipo), None)
