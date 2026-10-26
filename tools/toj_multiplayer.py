"""Multiplayer humano × humano no terminal: administração, servidor e cliente.

No computador do servidor (administrador):

    python tools/toj_multiplayer.py conta criar --dados DADOS --usuario ana
    python tools/toj_multiplayer.py gladiador importar --dados DADOS --dono ana --id W23
    python tools/toj_multiplayer.py gladiador listar --dados DADOS
    python tools/toj_multiplayer.py servidor --dados DADOS --host 0.0.0.0 \\
        --certificado certificado.pem --chave chave.pem

Em cada computador de jogador:

    python tools/toj_multiplayer.py cliente --url wss://SERVIDOR:8765 --usuario ana \\
        --autoridade certificado.pem

A senha é sempre pedida sem eco (ou lida de uma variável de ambiente cujo NOME é
passado em `--senha-em`, para scripts); nunca vai na linha de comando nem em log.
O passo a passo está em `MULTIPLAYER.md`.
"""

from __future__ import annotations

import argparse
import asyncio
import getpass
import logging
import os
import sys
import time
from collections.abc import Callable
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from websockets.exceptions import ConnectionClosed  # noqa: E402

from src.mechanics.pvp_duel import DuelAction, DuelView  # noqa: E402
from src.multiplayer import protocolo  # noqa: E402
from src.multiplayer.cliente import ClienteMultiplayer  # noqa: E402
from src.multiplayer.contas import ContaInvalidaError, ContasLocais  # noqa: E402
from src.multiplayer.gladiadores import GladiadorIncompativelError  # noqa: E402
from src.multiplayer.manifesto import (  # noqa: E402
    InstalacaoDivergenteError,
    manifesto_da_instalacao,
)
from src.multiplayer.rede import (  # noqa: E402
    PORTA_PADRAO,
    ConexaoDeRede,
    ConfiguracaoInseguraError,
    ServidorDeRede,
    tls_do_cliente,
    tls_do_servidor,
)
from src.multiplayer.registro import (  # noqa: E402
    PropriedadeError,
    RegistroDeGladiadores,
    importar_da_copa,
)
from src.multiplayer.servidor import ServidorAutoritativo  # noqa: E402

COPA_PADRAO = ROOT / "reports" / "pvp" / "copa_03"
TENTATIVAS_DE_RECONEXAO = 3

Entrada = Callable[[str], str]
Saida = Callable[[str], None]


def _senha(args, pergunta: str = "Senha: ") -> str:
    if getattr(args, "senha_em", None):
        valor = os.environ.get(args.senha_em)
        if not valor:
            raise SystemExit(f"A variável {args.senha_em} está vazia.")
        return valor
    return getpass.getpass(pergunta)


# --- administração -------------------------------------------------------------------


def _conta_criar(args) -> int:
    contas = ContasLocais.na_pasta(args.dados)
    senha = _senha(args)
    if not getattr(args, "senha_em", None) and getpass.getpass("Repita a senha: ") != senha:
        print("As senhas não conferem.")
        return 1
    try:
        conta = contas.criar(args.usuario, senha)
    except ContaInvalidaError as erro:
        print(erro)
        return 1
    print(f"Conta criada: {conta.usuario}")
    return 0


def _gladiador_importar(args) -> int:
    contas = ContasLocais.na_pasta(args.dados)
    dono = contas.conta_do_usuario(args.dono)
    if dono is None:
        print(f"Não existe a conta {args.dono!r}.")
        return 1
    registro = RegistroDeGladiadores.na_pasta(args.dados)
    falhou = False
    for gladiador in args.id:
        try:
            ficha = importar_da_copa(registro, args.copa, gladiador, dono.id)
        except (PropriedadeError, GladiadorIncompativelError) as erro:
            print(f"{gladiador}: recusado — {erro}")
            falhou = True
            continue
        nome = ficha.apelido or ficha.nome
        print(f"{ficha.id}: {nome} ({ficha.classe} {ficha.nivel}) → {dono.usuario}")
    return 1 if falhou else 0


def _gladiador_listar(args) -> int:
    contas = ContasLocais.na_pasta(args.dados)
    registro = RegistroDeGladiadores.na_pasta(args.dados)
    for gladiador in registro.ids():
        ficha = registro.ficha(gladiador)
        dono = contas.conta(registro.dono_de(gladiador))
        print(
            f"{ficha.id:6} {ficha.apelido or ficha.nome:24} {ficha.classe:8} "
            f"nível {ficha.nivel:3}  "
            f"dono: {dono.usuario if dono else '?'}"
        )
    return 0


# --- servidor ------------------------------------------------------------------------


def _servidor(args) -> int:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(message)s")
    try:
        servidor = ServidorAutoritativo.da_instalacao(
            RegistroDeGladiadores.na_pasta(args.dados), ContasLocais.na_pasta(args.dados)
        )
    except InstalacaoDivergenteError as erro:
        print("Esta instalação não confere com o manifesto da versão; o servidor não sobe:")
        print("\n".join(f"  - {p}" for p in erro.problemas))
        return 1
    tls = tls_do_servidor(args.certificado, args.chave) if args.certificado else None
    try:
        rede = ServidorDeRede(
            servidor, args.host, args.porta, tls=tls, permitir_sem_tls=args.sem_tls
        )
    except ConfiguracaoInseguraError as erro:
        print(erro)
        return 1
    print(f"ToJ {servidor.identidade.jogo} — servidor em {rede.url} (Ctrl+C encerra)")
    try:
        asyncio.run(rede.servir_para_sempre())
    except KeyboardInterrupt:
        pass
    return 0


# --- cliente -------------------------------------------------------------------------


_DESFECHOS = {
    "executed": "",
    "cancelled_control": " (cancelada: controle)",
    "cancelled_death": " (cancelada: morte)",
    "not_reached": " (não chegou a vez)",
}


class TerminalDeDuelo:
    """O que o jogador vê e escolhe. Entrada e saída injetáveis (o teste roda o fluxo todo)."""

    def __init__(self, entrada: Entrada = input, saida: Saida = print) -> None:
        self.entrada = entrada
        self.saida = saida
        self.cartas: dict[str, dict] = {}
        self.nomes: dict[str, str] = {}

    def escolher_numero(self, titulo: str, opcoes: list[str]) -> int:
        self.saida(titulo)
        for numero, opcao in enumerate(opcoes, start=1):
            self.saida(f"  [{numero}] {opcao}")
        while True:
            resposta = self.entrada("> ").strip()
            if resposta.isdigit() and 1 <= int(resposta) <= len(opcoes):
                return int(resposta) - 1
            self.saida("Escolha um dos números.")

    def ficha(self, titulo: str, ficha: dict) -> None:
        a = ficha["atributos"]
        nome = ficha.get("apelido") or ficha["nome"]
        cabecalho = f"{nome} — {ficha['classe']} nível {ficha['nivel']}"
        self.saida(f"--- {titulo}: {cabecalho}")
        self.saida(
            f"    HP {a['hp']}  MP {a['mp']}  ST {a['st']}  "
            f"MG {a['mg']}  AG {a['ag']}  DF {a['df']}"
        )
        pecas = [f"{p}: {n}" for p, n in ficha["equipamento"].items() if n]
        self.saida("    Equipamento: " + ("; ".join(pecas) or "nenhum"))
        cartas = [f"{s['nome']} ({s['mp']} MP, recarga {s['recarga']})" for s in ficha["skills"]]
        self.saida("    Skills: " + ("; ".join(cartas) or "nenhuma"))
        self.saida(
            "    Passivas: " + ("; ".join(p["nome"] for p in ficha["passivas"]) or "nenhuma")
        )

    def confronto(self, voce: dict, adversario: dict) -> None:
        for ficha in (voce, adversario):
            for carta in ficha["skills"]:
                self.cartas[carta["id"]] = carta
        self.nomes = {
            "Você": voce.get("apelido") or voce["nome"],
            "Adversário": adversario.get("apelido") or adversario["nome"],
        }
        self.ficha("Você", voce)
        self.ficha(f"Adversário ({adversario['usuario']})", adversario)

    def nome_da_acao(self, acao: DuelAction) -> str:
        if acao.kind == "attack":
            return "Ataque básico"
        if acao.kind == "surrender":
            return "Render-se"
        carta = self.cartas.get(acao.skill_id, {})
        return f"{carta.get('nome', acao.skill_id)} ({carta.get('mp', '?')} MP)"

    def estado(self, visao: DuelView) -> None:
        def linha(quem: str, lutador) -> str:
            marcas = ", ".join(lutador.effects + lutador.buffs)
            texto = (
                f"    {quem}: {self.nomes.get(quem, lutador.name)}  "
                f"HP {max(0, lutador.hp)}/{lutador.hp_max}  "
                f"MP {lutador.mp}/{lutador.mp_max}"
            )
            return texto + (f"  [{marcas}]" if marcas else "")

        self.saida(f"=== Rodada {visao.round_number}")
        self.saida(linha("Você", visao.me))
        self.saida(linha("Adversário", visao.opponent))
        esperando = [
            f"{self.cartas.get(carta, {}).get('nome', carta)} ({n})"
            for carta, n in visao.cooldowns
            if n > 0
        ]
        if esperando:
            self.saida("    Em recarga: " + ", ".join(esperando))

    def escolher_acao(self, visao: DuelView) -> DuelAction:
        acoes = list(visao.legal_actions)
        while True:
            indice = self.escolher_numero(
                "Sua ação (o adversário não vê antes do lock):",
                [self.nome_da_acao(a) for a in acoes],
            )
            acao = acoes[indice]
            if acao.kind != "surrender":
                return acao
            confirma = self.entrada("Render-se encerra o duelo com derrota. Confirmar? [s/N] ")
            if confirma.strip().lower() == "s":
                return acao

    def rodada(self, rodada: dict, lado: str) -> None:
        ordem = " → ".join("você" if s == lado else "adversário" for s in rodada["ordem"])
        self.saida(f"--- Rodada {rodada['numero']} resolvida (ordem: {ordem})")
        for passo in rodada["passos"]:
            quem = "Você" if passo["lado"] == lado else "Adversário"
            acao = protocolo.acao_de(rodada["acoes"][passo["lado"]])
            dano = f", {passo['dano']} de dano" if passo["dano"] else ""
            desfecho = _DESFECHOS.get(passo["desfecho"], "")
            self.saida(f"    {quem}: {self.nome_da_acao(acao)}{desfecho}{dano}")
        outro = "p2" if lado == "p1" else "p1"
        hp = {s: max(0, valor) for s, valor in rodada["hp_fim"].items()}
        self.saida(f"    HP: você {hp[lado]}, adversário {hp[outro]}")

    def fim(self, fim: dict, lado: str) -> None:
        if fim["estado"] == "anulada":
            self.saida(f"=== Partida anulada ({fim['motivo']}): sem vitória nem derrota.")
        elif fim["estado"] == "transferida":
            self.saida("=== A partida mudou de instância: reconectando.")
        else:
            veredito = "VITÓRIA" if fim["vencedor"] == lado else "DERROTA"
            self.saida(f"=== {veredito} — {fim['motivo']} em {fim['rodadas']} rodadas.")


class SessaoDeTerminal:
    """O fluxo do jogador: login, gladiador, sala, duelo, resultado — pela rede."""

    def __init__(self, url: str, usuario: str, senha: str, terminal: TerminalDeDuelo, **rede):
        self.url = url
        self.usuario = usuario
        self._senha = senha
        self.terminal = terminal
        self._rede = rede
        self.cliente = ClienteMultiplayer(manifesto_da_instalacao().identidade)
        self.conexao: ConexaoDeRede | None = None
        self.visao: DuelView | None = None

    def __repr__(self) -> str:
        return f"SessaoDeTerminal(usuario={self.usuario!r})"

    def _esperar(self, *tipos: str) -> dict:
        while True:
            self.cliente.receber(self.conexao.receber())
            mensagem = self.cliente.recebidas[-1]
            if mensagem["tipo"] in tipos or mensagem["tipo"] == "recusado":
                return mensagem

    def _recusado(self, mensagem: dict) -> bool:
        if mensagem["tipo"] != "recusado":
            return False
        self.terminal.saida(f"Recusado ({mensagem['motivo']}): {mensagem['mensagem']}")
        for problema in mensagem.get("problemas", []):
            self.terminal.saida(f"  - {problema}")
        return True

    def entrar(self) -> bool:
        self.conexao = ConexaoDeRede(self.url, **self._rede)
        self.conexao.enviar(self.cliente.login(self.usuario, self._senha))
        resposta = self._esperar("autenticado")
        self._senha = ""  # a senha não fica na memória do cliente além do login
        if self._recusado(resposta):
            return False
        self.conexao.enviar(self.cliente.ola())
        boas_vindas = self._esperar("bem_vindo")
        if self._recusado(boas_vindas):
            return False
        self.terminal.saida(
            f"Conectado como {self.cliente.usuario} (versão {boas_vindas['versao']})."
        )
        return True

    def preparar_partida(self) -> bool:
        gladiadores = self.cliente.gladiadores
        if not gladiadores:
            self.terminal.saida("Sua conta não tem gladiadores registrados neste servidor.")
            return False
        indice = self.terminal.escolher_numero(
            "Seu gladiador:",
            [
                f"{g['apelido'] or g['nome']} — {g['classe']} nível {g['nivel']} ({g['id']})"
                for g in gladiadores
            ],
        )
        escolhido = gladiadores[indice]["id"]
        modo = self.terminal.escolher_numero(
            "Partida direta:", ["Criar uma sala", "Entrar na sala de alguém"]
        )
        if modo == 0:
            self.conexao.enviar(self.cliente.criar_sala(escolhido))
            mensagem = self._esperar("sala_criada")
            if self._recusado(mensagem):
                return False
            self.terminal.saida(
                f"Sala {mensagem['sala']} — passe este código ao adversário e aguarde."
            )
        else:
            codigo = self.terminal.entrada("Código da sala: ").strip()
            self.conexao.enviar(self.cliente.entrar_na_sala(codigo, escolhido))
        mensagem = self._esperar("partida_criada")
        if self._recusado(mensagem):
            return False
        self.terminal.confronto(mensagem["voce"], mensagem["adversario"])
        return True

    def _agir(self) -> None:
        acao = self.terminal.escolher_acao(self.visao)
        self.conexao.enviar(self.cliente.acao(self.visao.round_number, acao))
        self.terminal.saida("Ação enviada. Aguardando o adversário...")

    def _reconectar(self) -> bool:
        for tentativa in range(1, TENTATIVAS_DE_RECONEXAO + 1):
            self.terminal.saida(
                f"Conexão perdida; reconectando ({tentativa}/{TENTATIVAS_DE_RECONEXAO})..."
            )
            time.sleep(min(2.0 * tentativa, 5.0))
            try:
                self.conexao = ConexaoDeRede(self.url, **self._rede)
                self.conexao.enviar(self.cliente.reconectar())
                return not self._recusado(self._esperar("bem_vindo"))
            except (OSError, ConnectionClosed, TimeoutError):
                continue
        return False

    def duelar(self) -> dict | None:
        while True:
            try:
                self.cliente.receber(self.conexao.receber())
            except ConnectionClosed:
                if not self._reconectar():
                    return None
                continue
            mensagem = self.cliente.recebidas[-1]
            tipo = mensagem["tipo"]
            if tipo == "observacao":
                self.visao = protocolo.visao_de_dict(mensagem["visao"])
                self.terminal.estado(self.visao)
                self._agir()
            elif tipo == "acao_recusada":
                self.terminal.saida(f"Ação recusada: {mensagem['mensagem']}")
                if mensagem["motivo"] == "acao_ilegal" and self.visao is not None:
                    self._agir()
            elif tipo == "rodada":
                self.terminal.rodada(mensagem["rodada"], self.cliente.lado)
            elif tipo == "fim":
                self.terminal.fim(mensagem, self.cliente.lado)
                if mensagem["estado"] != "transferida":
                    return mensagem
            elif tipo == "recusado":
                self._recusado(mensagem)

    def fechar(self) -> None:
        if self.conexao is not None:
            self.conexao.fechar()


def jogar(url: str, usuario: str, senha: str, terminal: TerminalDeDuelo, **rede) -> dict | None:
    """O fluxo completo de um jogador. Devolve o `fim`, ou `None` se não chegou a jogar."""
    sessao = SessaoDeTerminal(url, usuario, senha, terminal, **rede)
    try:
        if not sessao.entrar() or not sessao.preparar_partida():
            return None
        return sessao.duelar()
    finally:
        sessao.fechar()


def _cliente(args) -> int:
    try:
        manifesto_da_instalacao()
    except InstalacaoDivergenteError as erro:
        print("Esta instalação não confere com o manifesto da versão; atualize o jogo:")
        print("\n".join(f"  - {p}" for p in erro.problemas))
        return 1
    rede = {"permitir_sem_tls": args.sem_tls}
    if args.url.startswith("wss://"):
        rede["tls"] = tls_do_cliente(args.autoridade)
    try:
        fim = jogar(args.url, args.usuario, _senha(args), TerminalDeDuelo(), **rede)
    except ConfiguracaoInseguraError as erro:
        print(erro)
        return 1
    except KeyboardInterrupt:
        print("\nSaindo. A partida em andamento continua no servidor esperando a reconexão.")
        return 1
    return 0 if fim is not None else 1


# --- linha de comando ----------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)

    def com_dados(p):
        p.add_argument("--dados", type=Path, required=True, help="pasta de dados do servidor")
        return p

    conta = sub.add_parser("conta").add_subparsers(dest="acao", required=True)
    criar = com_dados(conta.add_parser("criar"))
    criar.add_argument("--usuario", required=True)
    criar.add_argument("--senha-em", help="NOME da variável de ambiente com a senha")
    criar.set_defaults(funcao=_conta_criar)

    gladiador = sub.add_parser("gladiador").add_subparsers(dest="acao", required=True)
    importar = com_dados(gladiador.add_parser("importar"))
    importar.add_argument("--dono", required=True, help="usuário dono")
    importar.add_argument("--id", action="append", required=True, help="id no índice da Copa")
    importar.add_argument("--copa", type=Path, default=COPA_PADRAO)
    importar.set_defaults(funcao=_gladiador_importar)
    listar = com_dados(gladiador.add_parser("listar"))
    listar.set_defaults(funcao=_gladiador_listar)

    servidor = com_dados(sub.add_parser("servidor"))
    servidor.add_argument("--host", default="127.0.0.1")
    servidor.add_argument("--porta", type=int, default=PORTA_PADRAO)
    servidor.add_argument("--certificado")
    servidor.add_argument("--chave")
    servidor.add_argument("--sem-tls", action="store_true", help="só desenvolvimento")
    servidor.set_defaults(funcao=_servidor)

    cliente = sub.add_parser("cliente")
    cliente.add_argument("--url", required=True, help="wss://host:porta")
    cliente.add_argument("--usuario", required=True)
    cliente.add_argument("--autoridade", help="certificado da CA do servidor (autoassinado)")
    cliente.add_argument("--sem-tls", action="store_true", help="só desenvolvimento")
    cliente.add_argument("--senha-em", help="NOME da variável de ambiente com a senha")
    cliente.set_defaults(funcao=_cliente)

    args = parser.parse_args(argv)
    if getattr(args, "certificado", None) and not getattr(args, "chave", None):
        parser.error("--certificado exige --chave")
    return args.funcao(args)


if __name__ == "__main__":
    sys.exit(main())
