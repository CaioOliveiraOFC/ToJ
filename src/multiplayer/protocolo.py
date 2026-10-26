"""As mensagens entre cliente e servidor, em JSON, sem tolerância.

A rede só transporta texto. Este módulo define o que esse texto pode dizer — e,
principalmente, o que ele NÃO pode: do cliente só saem a identidade de versão,
os comandos de sessão (entrar, fila, reconectar) e a AÇÃO do duelo (tipo e id da
carta). Não existe campo para HP, dano, atributo, equipamento, recarga,
resultado ou MMR; uma mensagem com campo a mais é recusada inteira.

Do servidor saem a observação (a mesma `DuelView` que o controlador local
recebe), o registro público da rodada (sem a iniciativa, que é auditoria) e o
desfecho.
"""

from __future__ import annotations

import json

from src.mechanics.pvp_duel import DUEL_ACTION_KINDS, DuelAction, DuelView, FighterView, RoundRecord

TAMANHO_MAXIMO = 64 * 1024

# tipo → {campo: tipos aceitos}. Exatamente estes campos, além de `tipo`.
MENSAGENS_DO_CLIENTE: dict[str, dict[str, tuple[type, ...]]] = {
    "ola": {"identidade": (dict,), "jogador": (str,)},
    "entrar_na_fila": {"identidade": (dict,), "gladiador": (str,)},
    "sair_da_fila": {},
    "acao": {"partida": (str,), "rodada": (int,), "acao": (dict,)},
    "reconectar": {"identidade": (dict,), "token": (str,)},
}

MENSAGENS_DO_SERVIDOR = (
    "bem_vindo",
    "recusado",
    "na_fila",
    "partida_criada",
    "observacao",
    "acao_recebida",
    "acao_recusada",
    "rodada",
    "fim",
)


class ProtocoloInvalidoError(ValueError):
    """A mensagem não é uma mensagem válida do protocolo. Nada é feito com ela."""

    def __init__(self, motivo: str, mensagem: str) -> None:
        self.motivo = motivo
        super().__init__(mensagem)


def codificar(tipo: str, /, **campos) -> str:
    """Uma mensagem em texto canônico (chaves ordenadas)."""
    return json.dumps({"tipo": tipo, **campos}, sort_keys=True, ensure_ascii=False)


def _tipo_certo(valor, tipos: tuple[type, ...]) -> bool:
    if isinstance(valor, bool):
        return bool in tipos
    return isinstance(valor, tipos)


def decodificar_do_cliente(texto) -> dict:
    """A mensagem do cliente, conferida campo a campo. Recusa o que não é do protocolo."""
    if not isinstance(texto, str):
        raise ProtocoloInvalidoError("mensagem_invalida", "A mensagem precisa ser texto.")
    if len(texto.encode()) > TAMANHO_MAXIMO:
        raise ProtocoloInvalidoError("mensagem_invalida", "Mensagem acima do tamanho máximo.")
    try:
        dados = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ProtocoloInvalidoError("mensagem_invalida", f"JSON ilegível: {erro}") from erro
    if not isinstance(dados, dict) or not isinstance(dados.get("tipo"), str):
        raise ProtocoloInvalidoError("mensagem_invalida", "A mensagem precisa de `tipo`.")
    esquema = MENSAGENS_DO_CLIENTE.get(dados["tipo"])
    if esquema is None:
        raise ProtocoloInvalidoError(
            "tipo_desconhecido", f"O cliente não envia mensagens do tipo {dados['tipo']!r}."
        )
    campos = set(dados) - {"tipo"}
    if campos != set(esquema):
        raise ProtocoloInvalidoError(
            "campos_invalidos",
            f"`{dados['tipo']}` leva exatamente {sorted(esquema)}; chegou {sorted(campos)}.",
        )
    for campo, tipos in esquema.items():
        if not _tipo_certo(dados[campo], tipos):
            raise ProtocoloInvalidoError("campos_invalidos", f"`{campo}` com tipo errado.")
    if dados["tipo"] == "acao":
        acao_de(dados["acao"])
    return dados


def acao_de(dados) -> DuelAction:
    """A ação do duelo a partir do objeto da mensagem. Só `kind` e `skill_id`."""
    if not isinstance(dados, dict) or set(dados) - {"kind", "skill_id"} or "kind" not in dados:
        raise ProtocoloInvalidoError("acao_invalida", "A ação leva só `kind` e `skill_id`.")
    tipo = dados["kind"]
    if tipo not in DUEL_ACTION_KINDS:
        raise ProtocoloInvalidoError("acao_invalida", f"Ação desconhecida: {tipo!r}.")
    carta = dados.get("skill_id")
    if tipo == "skill":
        if not isinstance(carta, str) or not carta:
            raise ProtocoloInvalidoError("acao_invalida", "Skill sem `skill_id`.")
        return DuelAction.use_skill(carta)
    if carta is not None:
        raise ProtocoloInvalidoError("acao_invalida", f"`{tipo}` não leva `skill_id`.")
    return DuelAction(tipo)


def acao_para_dict(acao: DuelAction) -> dict:
    return {"kind": acao.kind, "skill_id": acao.skill_id}


def _lutador(view: FighterView) -> dict:
    return {
        "name": view.name,
        "class_name": view.class_name,
        "level": view.level,
        "hp": view.hp,
        "hp_max": view.hp_max,
        "mp": view.mp,
        "mp_max": view.mp_max,
        "effects": list(view.effects),
        "buffs": list(view.buffs),
    }


def visao_para_dict(view: DuelView) -> dict:
    """A `DuelView` inteira, e nada além dela."""
    return {
        "round_number": view.round_number,
        "side": view.side,
        "me": _lutador(view.me),
        "opponent": _lutador(view.opponent),
        "legal_actions": [acao_para_dict(a) for a in view.legal_actions],
        "cooldowns": [[carta, espera] for carta, espera in view.cooldowns],
    }


def visao_de_dict(dados: dict) -> DuelView:
    """A visão de volta, do lado do cliente, para entregar ao controlador."""

    def lutador(d: dict) -> FighterView:
        return FighterView(
            name=d["name"],
            class_name=d["class_name"],
            level=d["level"],
            hp=d["hp"],
            hp_max=d["hp_max"],
            mp=d["mp"],
            mp_max=d["mp_max"],
            effects=tuple(d["effects"]),
            buffs=tuple(d["buffs"]),
        )

    return DuelView(
        round_number=dados["round_number"],
        side=dados["side"],
        me=lutador(dados["me"]),
        opponent=lutador(dados["opponent"]),
        legal_actions=tuple(acao_de(a) for a in dados["legal_actions"]),
        cooldowns=tuple((c, e) for c, e in dados["cooldowns"]),
    )


def rodada_publica(registro: RoundRecord) -> dict:
    """O que os dois lados veem da rodada resolvida. A iniciativa fica de fora."""
    return {
        "numero": registro.number,
        "acoes": {lado: acao_para_dict(acao) for lado, acao in registro.actions},
        "ordem": [registro.order.first, registro.order.second],
        "passos": [
            {
                "lado": passo.side,
                "desfecho": passo.outcome,
                "mp_gasto": passo.mp_spent,
                "dano": passo.damage_to_opponent,
            }
            for passo in registro.steps
        ],
        "hp_fim": dict(registro.hp_end),
        "mp_fim": dict(registro.mp_end),
    }
