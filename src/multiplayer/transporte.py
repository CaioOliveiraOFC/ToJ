"""O transporte local: entrega texto entre clientes e servidores, no mesmo processo.

É a camada de rede em sua forma mínima — só move `(conexão, texto)` — e é o que
os testes e o modo local usam. Um transporte de rede de verdade (socket,
websocket) faz exatamente o mesmo papel e não toca em regra: o servidor recebe
texto, devolve `Envio`s, e nada mais atravessa.
"""

from __future__ import annotations

from collections import deque
from collections.abc import Iterable

from src.multiplayer.cliente import ClienteMultiplayer
from src.multiplayer.servidor import Envio, ServidorAutoritativo


class RedeLocal:
    """Cada conexão liga um cliente a uma instância do servidor."""

    def __init__(self, servidor: ServidorAutoritativo | None = None) -> None:
        self.padrao = servidor
        self._clientes: dict[str, ClienteMultiplayer] = {}
        self._servidor_da: dict[str, ServidorAutoritativo] = {}

    def conectar(
        self,
        conexao: str,
        cliente: ClienteMultiplayer,
        servidor: ServidorAutoritativo | None = None,
    ) -> None:
        destino = servidor if servidor is not None else self.padrao
        if destino is None:
            raise ValueError("Conexão sem servidor.")
        self._clientes[conexao] = cliente
        self._servidor_da[conexao] = destino

    def desconectar(self, conexao: str) -> None:
        self._clientes.pop(conexao, None)
        servidor = self._servidor_da.pop(conexao, None)
        if servidor is not None:
            servidor.desconectar(conexao)

    def enviar(self, conexao: str, texto: str) -> None:
        """Manda um texto do cliente e entrega tudo o que decorrer, até a rede assentar."""
        self._processar(deque([(conexao, texto)]))

    def entregar(self, envios: Iterable[Envio]) -> None:
        """Entrega o que um servidor gerou fora de uma requisição (atualização, anulação)."""
        pendentes: deque[tuple[str, str]] = deque()
        for envio in envios:
            pendentes.extend(self._entregar(envio))
        self._processar(pendentes)

    def _processar(self, pendentes: deque[tuple[str, str]]) -> None:
        while pendentes:
            origem, texto = pendentes.popleft()
            servidor = self._servidor_da.get(origem)
            if servidor is None:
                continue
            for envio in servidor.receber(origem, texto):
                pendentes.extend(self._entregar(envio))

    def _entregar(self, envio: Envio) -> list[tuple[str, str]]:
        cliente = self._clientes.get(envio.conexao)
        if cliente is None:
            return []
        return [(envio.conexao, resposta) for resposta in cliente.receber(envio.texto)]
