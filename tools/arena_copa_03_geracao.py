"""Copa Arena 03, geração: 64 Guerreiros extraídos de runs PvE reais.

Uso:
    python tools/arena_copa_03_geracao.py gerar [--trabalhadores 4]
    python tools/arena_copa_03_geracao.py status

Cada tentativa é uma run do BotPadrão desde a criação canônica de uma nova
jornada (`create_player_for_new_run`, nível 1, Starter Kit sorteado pela seed).
O RNG da run decide mapa, monstros, loot, ofertas, lojas e o momento em que a
Extração acontece. Nada aqui concede item, escolhe carta, mexe em atributo ou
encerra a run: quem joga é o bot, e quem aplica a regra é o jogo.

## A variante experimental: perfil × política

O BotPadrão oficial não muda. A variante vive em `BotExperimental`, uma subclasse
que só faz três coisas:

1. troca a política de escolha (`picker`) por `survival`, `offense` ou
   `economy`, o mesmo atributo que o driver já consulta a cada level-up;
2. aplica, a cada andar, a LINHA DE APOSTA da agenda de risco do perfil;
3. registra telemetria, inclusive a decisão que o cérebro canônico tomaria no
   mesmo estado (a decisão-sombra).

### Por que a linha de aposta, e não `Perfil.hp_engajar`

`Perfil.hp_engajar` e `Perfil.mp_engajar` não são lidos por nenhuma decisão:
o docstring de `ProgressionState` diz que eles ficaram no driver "por
compatibilidade de CLI e de teste", e `tests/test_bot_observation.py` proíbe que
voltem ao estado. Rodar os três perfis oficiais dá três runs idênticas. Baixar
esses números não aumentaria risco nenhum.

O que decide de fato, no mapa, é um limiar só:

- `src/sim/bot/evaluators.HP_DE_APOSTA` (0,35), "o ÚNICO limiar de HP do
  cérebro". Ele mede a capacidade de cada luta (`hp − aposta`), decide quando a
  cura vira SOBREVIVER ou RECUPERAR e quando a saída do andar vira descanso;
- `tools/bot_padrao.HP_CRITICO` (0,35), a mesma linha do lado do driver: abaixo
  dela a Loja pode gastar a reserva da saída em recuperação.

Os dois são constantes de módulo lidas no momento da chamada. A variante os
SOBRESCREVE EM TEMPO DE EXECUÇÃO, só dentro da run experimental, e os devolve ao
valor canônico no fim (`try/finally`). Nenhum arquivo de `src/` ou de
`tools/bot_padrao.py` muda, e o BotPadrão oficial continua idêntico. Não é um
ponto de configuração que o projeto já declarava: é a menor intervenção que muda
risco de verdade sem duplicar regra nem avaliador, e está documentada como tal.

O que NÃO tem alavanca externa (além da extração, abaixo), e por isso fica
canônico nos três perfis:

- MP: o cérebro do mapa não tem limiar de mana; a mana só pesa dentro do duelo,
  pela escassez de `avaliar_combate`;
- desvio voluntário: `DESVIO_ACEITAVEL` não filtra mais nada (o adaptador
  enumera todo serviço alcançável);
- o combate: fuga, cura, buff e controle dentro do duelo são os de sempre.

### A agenda

A linha de base de cada perfil sai dos próprios números do perfil oficial. O
driver documenta que o piso de engajamento fica 0,20 acima da linha crítica
(`HP_PARA_ENGAJAR − HP_CRITICO`), então a linha de cada perfil é
`hp_engajar − 0,20`: conservador 0,35 (o canônico), moderado 0,25, hardcore
0,18. Com a profundidade a linha desce `PASSO` a cada `FAIXA` andares, até um
piso explícito. A ordem conservador > moderado > hardcore vale em todo andar, e
um teste a confere de 1 a 200.

A agenda não força luta nem desliga proteção: abaixo da linha o cérebro continua
mandando curar, recuperar ou sair, e dentro do duelo a fuga é a canônica. O que
muda é ONDE fica a linha. A decisão-sombra mostra quantas escolhas isso mudou
de fato, por faixa de andares.

### A extração (v2)

Continuar ou extrair é a matriz de `_avaliar_extracao`: a banda da build contra
o benchmark da Arena (OP 29,17) × o fôlego observado da run. Ela não tem
parâmetro. A v1 deixou essa matriz canônica nos três perfis e rodou como piloto:
das 58 extrações, 57 saíram com OP acima de 30, porque entre 0,95 e 1,05 do
benchmark a matriz só preserva com o fôlego curto, e o Guerreiro chega ali quase
sempre saudável. A partir da v2, escolhida pelo usuário, a decisão de extrair
entra no perfil, pela mesma via da linha de aposta (`evaluators._MATRIZ`
sobrescrita em tempo de execução e restaurada no fim):

- conservador: preserva a build com qualquer fôlego a partir de CLOSE_ENOUGH
  (0,95 do benchmark);
- moderado: a partir de META_BATIDA (1,00);
- hardcore: a matriz canônica, a mais gananciosa.

A matriz do perfil só ACRESCENTA preservação; onde a canônica já preserva, ela
continua preservando. A ordem de risco é a mesma da linha: o conservador sai
mais cedo, o hardcore aposta mais.

## Geração

Nove grupos (perfil × política), com as quotas de `QUOTAS`. Cada tentativa tem a
seed `sha256("20261025:v2:perfil:politica:k")`. A fila manda a próxima
tentativa para o grupo com menos tentativas despachadas por vaga restante. Não
há limite de tentativas, de mortes nem de seeds.

Uma extração é ACEITA quando o personagem é Warrior, a run terminou pela
Extração, ele está vivo, o snapshot canônico (`to_save_data`) reconstrói pelo
caminho da Arena com a mesma build, o OP do reconstruído está entre 20 e 30 e o
grupo ainda tem vaga. A ordem é a do NÚMERO DA TENTATIVA dentro do grupo, e não a
ordem em que os processos terminam: o grupo aceita as primeiras qualificadas da
sequência dele, sem lacuna. Assim o resultado não depende de quantos processos
rodaram nem de quem terminou antes. Tentativas em voo quando a quota fecha são
executadas e registradas como excedentes.

## Preenchimento

Depois de 1315 tentativas (conservador 22/22, moderado 21/21, hardcore 10/21),
o usuário tirou a obrigatoriedade das quotas: a seleção original fica como
está, e as vagas restantes vão para NOVAS runs v2 de conservador e moderado
(`preencher`). O plano é determinístico e gravado em `preenchimento.json`:
primeiro qualificadas que tenham sobrado no checkpoint, depois vaga a vaga a
política com menos gladiadores nos 64 e, dentro dela, o perfil com menos vagas
novas. Cada grupo continua a própria numeração depois da última tentativa da
geração original, com as mesmas seeds v2. As runs do preenchimento vão para
`preenchimento.jsonl`, com fila própria; o log da geração original não muda.
Retomar confere o plano gravado contra o checkpoint e não repete run.

## Checkpoint

Tudo o que é transitório fica em `reports/pvp/copa_03/_trabalho/` (fora do git):

- `tentativas.jsonl`: uma linha por tentativa concluída, gravada e sincronizada
  em disco no momento em que termina. Uma linha final incompleta é descartada;
- `candidatos/`: o snapshot de cada extração qualificada, gravado atomicamente
  ANTES da linha que o referencia;
- `fila.json`: estado da fila, regravado atomicamente;
- `erros.log` e `progresso.log`.

Ao reiniciar, a fila é reconstruída de `tentativas.jsonl`: nenhuma tentativa
concluída roda de novo e nenhum aceito é medido de novo. As que estavam em voo
no corte não estão no arquivo e rodam outra vez, com a mesma seed, e dão o mesmo
resultado.

Nenhum slot de save é usado: a Extração do bot passa por `finish_run` com
gravação em memória, e o snapshot sai da serialização canônica do save.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import multiprocessing as mp
import os
import sys
import tempfile
import time
import traceback
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait
from dataclasses import dataclass
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

import tools.bot_padrao as bp  # noqa: E402
from src.content.extraction import extracted_floor, keys_of, was_extracted  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.engine.game_logic import CLASS_MAP  # noqa: E402
from src.sim.arena import assinatura_de_build, overall_power  # noqa: E402
from src.sim.bot import decidir_no_mapa, evaluators  # noqa: E402
from src.sim.bot.decision import Need  # noqa: E402
from src.sim.pick_policies import get_pick_policy  # noqa: E402
from src.storage.save_manager import player_from_save_data, to_save_data  # noqa: E402
from tools import bot_adapter as adapter  # noqa: E402

SEMENTE_PRINCIPAL = 20261025
CLASSE = "warrior"
# Horizonte técnico, o mesmo das auditorias de progressão. Não é contrato de
# extração: a maior run de Guerreiro registrada parou no andar 28.
TETO = 200
FAIXA_DE_OP = (20.0, 30.0)
PERFIS = ("conservador", "moderado", "hardcore")
POLITICAS = ("survival", "offense", "economy")
QUOTAS = {
    ("conservador", "survival"): 8,
    ("conservador", "offense"): 7,
    ("conservador", "economy"): 7,
    ("moderado", "survival"): 7,
    ("moderado", "offense"): 7,
    ("moderado", "economy"): 7,
    ("hardcore", "survival"): 7,
    ("hardcore", "offense"): 7,
    ("hardcore", "economy"): 7,
}
GRUPOS = tuple(QUOTAS)

PASTA = RAIZ / "reports" / "pvp" / "copa_03"
TRABALHO = PASTA / "_trabalho"

# --- a agenda de risco -------------------------------------------------------

# O valor canônico das duas linhas. Lido do código, e não repetido: se o cérebro
# mudar de linha, a agenda e o teste de restauração mudam junto.
LINHA_CANONICA = evaluators.HP_DE_APOSTA
assert bp.HP_CRITICO == LINHA_CANONICA, "o driver e o cérebro deixaram de usar a mesma linha"
# Distância do piso de engajamento à linha crítica, declarada pelo driver.
FOLGA_DE_ENGAJAMENTO = bp.HP_PARA_ENGAJAR - bp.HP_CRITICO
FAIXA = 5
PASSO = 0.02
PISO = {"conservador": 0.27, "moderado": 0.19, "hardcore": 0.12}


def linha_base(perfil: str) -> float:
    """`hp_engajar − 0,20`: a linha que o número do perfil oficial supunha."""
    return round(bp.PERFIS[perfil].hp_engajar - FOLGA_DE_ENGAJAMENTO, 4)


def faixa_do_andar(andar: int) -> int:
    return (max(1, andar) - 1) // FAIXA


def rotulo_da_faixa(indice: int) -> str:
    return f"{indice * FAIXA + 1}-{(indice + 1) * FAIXA}"


def linha_de_aposta(perfil: str, andar: int) -> float:
    """A linha do perfil neste andar: desce `PASSO` por faixa, até o piso."""
    return round(max(PISO[perfil], linha_base(perfil) - PASSO * faixa_do_andar(andar)), 4)


def agenda(perfil: str, ate: int = 30) -> dict[str, float]:
    """A agenda por faixa de andares, para o registro de cada run."""
    return {
        rotulo_da_faixa(f): linha_de_aposta(perfil, f * FAIXA + 1)
        for f in range(faixa_do_andar(ate) + 1)
    }


# --- a extração na agenda (v2) -------------------------------------------------

# A versão da variante. A v1 (só a linha de aposta) rodou como piloto e ficou
# registrada: das 58 extrações dela, 57 saíram acima de OP 30, porque a matriz
# canônica só preserva entre 0,95 e 1,05 do benchmark com o fôlego curto. A v2
# põe "continuar ou extrair" no perfil, e as seeds dela têm namespace próprio:
# nenhuma seed da v1 é reaproveitada para produzir outra build.
VERSAO = "v2"
MATRIZ_CANONICA = evaluators._MATRIZ
_BANDAS = (evaluators.ABAIXO, evaluators.CLOSE_ENOUGH, evaluators.META_BATIDA, evaluators.HARD_STOP)
# A partir de que banda da build (contra o benchmark da Arena) o perfil preserva
# com QUALQUER fôlego. Abaixo dela, e no hardcore inteiro, vale a matriz canônica,
# que é a mais gananciosa: só preserva cedo com o fôlego curto.
PRESERVA_DESDE = {"conservador": evaluators.CLOSE_ENOUGH, "moderado": evaluators.META_BATIDA}


def matriz_de_extracao(perfil: str) -> dict:
    """A matriz de `_avaliar_extracao` para o perfil. Só acrescenta `True`."""
    desde = PRESERVA_DESDE.get(perfil)
    if desde is None:
        return MATRIZ_CANONICA
    corte = _BANDAS.index(desde)
    return {
        (banda, estado): preserva or _BANDAS.index(banda) >= corte
        for (banda, estado), preserva in MATRIZ_CANONICA.items()
    }


def _aplicar(linha: float, matriz: dict) -> None:
    evaluators.HP_DE_APOSTA = linha
    bp.HP_CRITICO = linha
    evaluators._MATRIZ = matriz


def semente_da_run(perfil: str, politica: str, tentativa: int, classe: str = CLASSE) -> int:
    """A seed da tentativa. Warrior mantém a fórmula da Copa 03; as outras classes
    levam o nome da classe na chave, para nunca repetir uma seed de Guerreiro."""
    rotulo = f"{perfil}" if classe == CLASSE else f"{classe}:{perfil}"
    digest = hashlib.sha256(
        f"{SEMENTE_PRINCIPAL}:{VERSAO}:{rotulo}:{politica}:{tentativa}".encode()
    ).digest()
    return int.from_bytes(digest[:8], "big")


def _familia(action_id: str) -> str:
    return action_id.split(":")[0]


class BotExperimental(bp.BotPadrao):
    """BotPadrão com política de escolha e agenda de risco do grupo."""

    def __init__(
        self, seed: int, perfil: str, politica: str, max_andar: int = TETO, classe: str = CLASSE
    ) -> None:
        super().__init__(classe, seed, max_andar, bp.PERFIS[perfil])
        self.perfil_nome = perfil
        self.picker = get_pick_policy(politica)
        self.linha = LINHA_CANONICA
        self.matriz = matriz_de_extracao(perfil)
        self.decisoes = 0
        self.ilegais = 0
        self.divergencias: Counter = Counter()
        self.divergencias_por_faixa: Counter = Counter()
        self.decisoes_por_faixa: Counter = Counter()
        self.exemplos: list[dict] = []
        self.orcamentos = 0
        self.orcamentos_divergentes = 0
        self.extracoes: dict[int, dict] = {}

    def jogar(self) -> str:
        try:
            return super().jogar()
        finally:
            _aplicar(LINHA_CANONICA, MATRIZ_CANONICA)

    def _jogar_andar(self, andar: int) -> str:
        self.linha = linha_de_aposta(self.perfil_nome, andar)
        _aplicar(self.linha, self.matriz)
        desfecho = super()._jogar_andar(andar)
        if self.por_andar:
            self.por_andar[-1]["linha_de_aposta"] = self.linha
        return desfecho

    def _decidir_no_mapa(self):
        # As mesmas três chamadas do driver, mais a sombra canônica.
        mapa, prog = adapter.estado_do_mapa(self)
        opcoes, destinos = adapter.acoes_do_mapa(self, mapa, prog)
        decisao = decidir_no_mapa(mapa, prog, opcoes)
        self.decisoes += 1
        if decisao.action_id not in {o.action_id for o in opcoes}:
            self.ilegais += 1
        faixa = rotulo_da_faixa(faixa_do_andar(self.andar))
        self.decisoes_por_faixa[faixa] += 1
        if self.linha != LINHA_CANONICA or self.matriz is not MATRIZ_CANONICA:
            _aplicar(LINHA_CANONICA, MATRIZ_CANONICA)
            try:
                sombra = decidir_no_mapa(mapa, prog, opcoes)
            finally:
                _aplicar(self.linha, self.matriz)
            if _familia(sombra.action_id) != _familia(decisao.action_id):
                par = f"{_familia(sombra.action_id)}→{_familia(decisao.action_id)}"
                self.divergencias[par] += 1
                self.divergencias_por_faixa[faixa] += 1
                if len(self.exemplos) < 3:
                    self.exemplos.append(
                        {
                            "andar": self.andar,
                            "hp": round(prog.hp_frac, 3),
                            "linha": self.linha,
                            "canonica": sombra.action_id,
                            "experimental": decisao.action_id,
                        }
                    )
        self._registrar_extracao(mapa, prog, decisao)
        return decisao, destinos.get(decisao.action_id)

    def _registrar_extracao(self, mapa, prog, decisao) -> None:
        score = next((s for s in decisao.scores if s.action_id == "extrair"), None)
        if score is None:
            return
        preserva = score.need is Need.PRESERVAR
        registro = self.extracoes.setdefault(
            self.andar,
            {
                "andar": self.andar,
                "nivel": prog.nivel,
                "poder_relativo": round(prog.poder_relativo, 4),
                "banda": (
                    evaluators._banda_da_build(prog.poder_relativo)
                    if prog.poder_relativo > 0
                    else None
                ),
                "avaliacoes": 0,
                "preservar": False,
            },
        )
        registro["avaliacoes"] += 1
        if preserva and not registro["preservar"]:
            runway = evaluators._runway_em_andares(mapa, prog)
            registro.update(
                preservar=True,
                nivel=prog.nivel,
                poder_relativo=round(prog.poder_relativo, 4),
                banda=evaluators._banda_da_build(prog.poder_relativo),
                runway=None if runway is None else round(runway, 3),
                hp=round(prog.hp_frac, 3),
            )

    def _orcamento(self):
        resposta = super()._orcamento()
        self.orcamentos += 1
        hp = bp._frac_hp(self.hero)
        if (hp < LINHA_CANONICA) != (hp < self.linha):
            self.orcamentos_divergentes += 1
        return resposta


# --- a tentativa -------------------------------------------------------------


def na_faixa(op: float) -> bool:
    """OP entre 20 e 30, inclusive nas duas pontas."""
    return FAIXA_DE_OP[0] <= op <= FAIXA_DE_OP[1]


_FABRICA = {nome: classe for classe, nome in CLASS_MAP.values()}


def reconstruir(snapshot: dict):
    """O personagem do snapshot, pelo caminho da Arena (`arena_setup`)."""
    heroi, _, _ = player_from_save_data(copy.deepcopy(snapshot), get_all_items(), _FABRICA)
    return heroi


def _build(heroi) -> dict:
    return {
        "deck": [heroi.skills[k].id for k in sorted(heroi.skills)],
        "passivas": [p.id for p in heroi.passives],
        "familias": dict(Counter(p.effect_type for p in heroi.passives)),
        "raridades": dict(Counter(p.rarity for p in heroi.passives)),
        "equipamento": {
            posicao: {
                "nome": item.name,
                "raridade": getattr(item, "rarity", None),
                "mais": int(getattr(item, "enhancement_level", 0) or 0),
                "gemas": sum(1 for g in getattr(item, "gems", ()) or () if g is not None),
                "encantos": sum(
                    1 for e in getattr(item, "enchantments", ()) or () if e is not None
                ),
                "origem": getattr(item, "origin", None),
            }
            for posicao, item in heroi.equipment.items()
            if item is not None
        },
    }


def _conferir_reconstrucao(vivo, snapshot: dict) -> list[str]:
    """O que diverge entre o herói da run e o reconstruído. Vazio = idêntico."""
    reconstruido = reconstruir(snapshot)
    falhas = []
    if reconstruido is None:
        return ["snapshot ilegível"]
    if reconstruido.get_classname() != vivo.get_classname():
        falhas.append(f"classe {reconstruido.get_classname()}")
    if not was_extracted(reconstruido):
        falhas.append("sem marca de extração")
    if assinatura_de_build(vivo) != assinatura_de_build(reconstruido):
        falhas.append("assinatura de build")
    if _build(vivo) != _build(reconstruido):
        falhas.append("deck, passivas ou equipamento")
    if (vivo.base_hp, vivo.base_mp, vivo.get_level()) != (
        reconstruido.base_hp,
        reconstruido.base_mp,
        reconstruido.get_level(),
    ):
        falhas.append("HP/MP máximos ou nível")
    if _sem_telemetria_de_carga(to_save_data(reconstruido, snapshot["dungeon_level"])) != (
        _sem_telemetria_de_carga(snapshot)
    ):
        falhas.append("o snapshot não se reproduz pela ida e volta")
    return falhas


def _sem_telemetria_de_carga(dados: dict) -> dict:
    """O snapshot sem `ledger.items_equipped`.

    A recarga canônica reequipa cada peça por `Player.equip`, que soma 1 a esse
    contador do livro-caixa. É telemetria, não build: o resto do livro-caixa e
    todos os outros campos têm de voltar idênticos.
    """
    copia = copy.deepcopy(dados)
    copia.get("ledger", {}).pop("items_equipped", None)
    return copia


def executar(
    perfil: str,
    politica: str,
    tentativa: int,
    classe: str = CLASSE,
    faixa: tuple[float, float] | None = FAIXA_DE_OP,
) -> dict:
    """Uma run inteira, e o veredito de elegibilidade. Roda num processo próprio.

    `classe` e `faixa` são os da Copa 03 por padrão (Guerreiro, OP 20–30). A
    população offline da Arena usa as três classes e `faixa=None`: qualquer OP.
    """
    semente = semente_da_run(perfil, politica, tentativa, classe)
    inicio = time.time()
    registro: dict = {
        "perfil": perfil,
        "politica": politica,
        "tentativa": tentativa,
        "seed": semente,
        "teto": TETO,
        "versao": VERSAO,
        "agenda": agenda(perfil),
        "extrai_desde": PRESERVA_DESDE.get(perfil, "canônica"),
    }
    try:
        bot = BotExperimental(semente, perfil, politica, classe=classe)
        bot.jogar()
    except Exception:  # noqa: BLE001 — o erro vira registro, nunca some
        registro.update(
            desfecho="erro",
            motivo="exceção na run",
            erro=traceback.format_exc(limit=8),
            tempo_s=round(time.time() - inicio, 1),
        )
        return registro

    heroi = bot.hero
    vivo = heroi.get_isalive() and heroi.get_hp() > 0
    if bot.extraiu:
        desfecho = "extraiu"
    elif not vivo:
        desfecho = "morreu"
    else:
        desfecho = "teto"
    registro.update(
        desfecho=desfecho,
        fim=bot.fim,
        andar=bot.andar,
        nivel=heroi.get_level(),
        nivel_por_andar=[r["nivel"] for r in bot.por_andar],
        combates=bot.combates_na_run,
        fugas_na_ficha=bot.fugas_na_run,
        acoes=dict(bot.acoes),
        pocoes_bebidas=bot.pocoes_bebidas,
        servicos=dict(bot.servicos),
        reserva_gasta=bot.reserva_gasta,
        saidas_pagas=int(heroi.ledger.get("paid_exits", 0)),
        saidas_nao_pagas=int(heroi.ledger.get("unpaid_exits", 0)),
        ouro_ganho=int(heroi.ledger.get("gold_earned", 0)),
        decisoes=bot.decisoes,
        ilegais=bot.ilegais,
        divergencias={
            "total": sum(bot.divergencias.values()),
            "pares": dict(bot.divergencias),
            "por_faixa": dict(bot.divergencias_por_faixa),
            "decisoes_por_faixa": dict(bot.decisoes_por_faixa),
            "exemplos": bot.exemplos,
            "orcamentos": bot.orcamentos,
            "orcamentos_divergentes": bot.orcamentos_divergentes,
        },
        extracao=sorted(bot.extracoes.values(), key=lambda r: r["andar"]),
        fatal=bot.fatal,
        linha_restaurada=evaluators.HP_DE_APOSTA == LINHA_CANONICA
        and bp.HP_CRITICO == LINHA_CANONICA
        and evaluators._MATRIZ is MATRIZ_CANONICA,
    )

    if desfecho != "extraiu":
        registro.update(
            qualificada=False,
            motivo={"morreu": "morreu", "teto": "chegou ao teto vivo sem extrair"}[desfecho],
            tempo_s=round(time.time() - inicio, 1),
        )
        return registro

    snapshot = json.loads(json.dumps(to_save_data(heroi, bot.andar)))
    falhas = []
    if heroi.get_classname().lower() != classe:
        falhas.append(f"não é {classe}")
    if not vivo:
        falhas.append("extraiu sem vida")
    if not was_extracted(heroi) or extracted_floor(heroi) != bot.andar:
        falhas.append("marca de extração ausente ou de outro andar")
    if keys_of(heroi) != 0:
        falhas.append("a Chave não foi gasta")
    falhas += _conferir_reconstrucao(heroi, snapshot)
    registro["build"] = _build(heroi)
    if falhas:
        registro.update(
            qualificada=False,
            motivo="snapshot inválido: " + "; ".join(falhas),
            tempo_s=round(time.time() - inicio, 1),
        )
        return registro

    leitura = overall_power(reconstruir(snapshot), usar_cache=False)
    op = leitura.nivel_equivalente
    dentro = faixa is None or faixa[0] <= op <= faixa[1]
    registro.update(
        op=op,
        duelos_op=leitura.duelos,
        qualificada=dentro,
        motivo="qualificada" if dentro else f"OP {op:.2f} fora de {faixa[0]:g}–{faixa[1]:g}",
        tempo_s=round(time.time() - inicio, 1),
    )
    if dentro:
        registro["_snapshot"] = snapshot
    return registro


# --- persistência ------------------------------------------------------------


def chave_do_grupo(grupo: tuple[str, str]) -> str:
    return f"{grupo[0]}-{grupo[1]}"


def nome_do_candidato(perfil: str, politica: str, tentativa: int) -> str:
    return f"{perfil}-{politica}-{tentativa:05d}.json"


def gravar_atomico(destino: Path, conteudo: str) -> None:
    destino.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(dir=destino.parent, prefix=".tmp-", suffix=destino.suffix)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(conteudo)
            f.flush()
            os.fsync(f.fileno())
        # `mkstemp` cria com 0600; o arquivo publicado é lido por qualquer um.
        os.chmod(temporario, 0o644)
        os.replace(temporario, destino)
    except BaseException:
        Path(temporario).unlink(missing_ok=True)
        raise


def ler_tentativas(trabalho: Path = TRABALHO, nome: str = "tentativas.jsonl") -> list[dict]:
    """As tentativas concluídas. Uma linha final incompleta (corte) é ignorada."""
    arquivo = trabalho / nome
    if not arquivo.exists():
        return []
    registros = []
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        if not linha.strip():
            continue
        try:
            registros.append(json.loads(linha))
        except json.JSONDecodeError:
            break
    return registros


@dataclass
class Grupo:
    perfil: str
    politica: str
    quota: int
    concluidas: dict
    em_voo: set
    # A primeira tentativa desta fila. O preenchimento continua a numeração de
    # cada grupo depois da última tentativa da geração original.
    primeira: int = 1

    @property
    def chave(self) -> tuple[str, str]:
        return (self.perfil, self.politica)

    def aceitas(self) -> list[int]:
        """As primeiras qualificadas da sequência, sem lacuna, até a quota."""
        aceitas = []
        k = self.primeira
        while k in self.concluidas and len(aceitas) < self.quota:
            if self.concluidas[k].get("qualificada"):
                aceitas.append(k)
            k += 1
        return aceitas

    @property
    def completo(self) -> bool:
        return len(self.aceitas()) >= self.quota

    def proxima(self) -> int:
        """A menor tentativa ainda não concluída nem em voo."""
        k = self.primeira
        while k in self.concluidas or k in self.em_voo:
            k += 1
        return k


def montar_fila(
    registros: list[dict], quotas: dict | None = None, primeiras: dict | None = None
) -> dict[tuple[str, str], Grupo]:
    quotas = QUOTAS if quotas is None else quotas
    primeiras = primeiras or {}
    fila = {g: Grupo(g[0], g[1], q, {}, set(), primeiras.get(g, 1)) for g, q in quotas.items()}
    sementes = set()
    for r in registros:
        grupo = fila[(r["perfil"], r["politica"])]
        if r["tentativa"] in grupo.concluidas:
            raise RuntimeError(f"tentativa repetida no checkpoint: {r['perfil']}/{r['politica']}")
        if r["seed"] in sementes:
            raise RuntimeError(f"seed repetida no checkpoint: {r['seed']}")
        sementes.add(r["seed"])
        grupo.concluidas[r["tentativa"]] = r
    return fila


def estado_da_fila(fila: dict) -> dict:
    return {
        "semente_principal": SEMENTE_PRINCIPAL,
        "teto": TETO,
        "grupos": {
            chave_do_grupo(g.chave): {
                "quota": g.quota,
                "aceitas": g.aceitas(),
                "concluidas": len(g.concluidas),
                "em_voo": sorted(g.em_voo),
                "proxima_tentativa": g.proxima(),
                "completo": g.completo,
            }
            for g in fila.values()
        },
    }


def escolher_grupo(fila: dict, limite: int | None = None) -> Grupo | None:
    """O grupo incompleto com menos tentativas despachadas por vaga restante.

    Proporcional às vagas: um grupo com sete vagas recebe sete vezes mais
    tentativas que um com uma. "Mais vagas por tentativa em voo" desempatava
    pela ordem dos grupos, e como a morte cedo devolve o processo em segundos,
    os grupos do conservador eram despachados de novo antes de os outros
    receberem a primeira tentativa.

    `limite` fecha o grupo que já despachou essa quantidade de tentativas, cheio
    ou não. A Copa 03 não tem limite; a população offline tem, porque há classe
    e perfil que quase nunca extraem.
    """
    abertos = [
        g
        for g in fila.values()
        if not g.completo and (limite is None or len(g.concluidas) + len(g.em_voo) < limite)
    ]
    if not abertos:
        return None

    def prioridade(g: Grupo) -> tuple:
        vagas = g.quota - len(g.aceitas())
        return ((len(g.concluidas) + len(g.em_voo)) / vagas, list(fila).index(g.chave))

    return min(abertos, key=prioridade)


def linha_de_progresso(fila: dict) -> str:
    todos = [r for g in fila.values() for r in g.concluidas.values()]
    aceitos = [g.concluidas[k] for g in fila.values() for k in g.aceitas()]
    por_perfil = {
        p: (
            sum(len(g.aceitas()) for g in fila.values() if g.perfil == p),
            sum(g.quota for g in fila.values() if g.perfil == p),
        )
        for p in PERFIS
    }
    media = sum(r["op"] for r in aceitos) / len(aceitos) if aceitos else 0.0
    return (
        f"Tentativas: {len(todos)} | "
        f"Extrações: {sum(r['desfecho'] == 'extraiu' for r in todos)} | "
        f"Aceitos: {len(aceitos)}/{sum(g.quota for g in fila.values())} | "
        + " | ".join(f"{p[0].upper()}: {a}/{q}" for p, (a, q) in por_perfil.items())
        + f" | OP médio: {media:.1f}".replace(".", ",")
    )


def diagnostico(fila: dict) -> str:
    partes = []
    for g in fila.values():
        rs = list(g.concluidas.values())
        if not rs:
            continue
        ext = sum(r["desfecho"] == "extraiu" for r in rs)
        qual = sum(bool(r.get("qualificada")) for r in rs)
        acima = sum(r.get("op") is not None and r["op"] > FAIXA_DE_OP[1] for r in rs)
        partes.append(
            f"{g.perfil[0].upper()}/{g.politica[:3]} {len(g.aceitas())}/{g.quota} "
            f"(n={len(rs)} ext={ext} qual={qual} op>30={acima})"
        )
    return "  " + "; ".join(partes)


def _log(texto: str, trabalho: Path) -> None:
    print(texto, flush=True)
    with open(trabalho / "progresso.log", "a", encoding="utf-8") as f:
        f.write(texto + "\n")


def gerar(
    trabalhadores: int = 4,
    trabalho: Path = TRABALHO,
    *,
    executor=None,
    quotas: dict | None = None,
    primeiras: dict | None = None,
    nome: str = "tentativas.jsonl",
    estado: str = "fila.json",
    classe: str = CLASSE,
    faixa: tuple[float, float] | None = FAIXA_DE_OP,
    limite: int | None = None,
) -> dict:
    """Roda tentativas até os grupos completarem as quotas (ou o `limite`).

    Sem argumentos, é a geração original: nove grupos, `QUOTAS`, o log
    `tentativas.jsonl`. O preenchimento chama a mesma máquina com as quotas, a
    numeração e o log dele.
    """
    trabalho.mkdir(parents=True, exist_ok=True)
    (trabalho / "candidatos").mkdir(exist_ok=True)
    fila = montar_fila(ler_tentativas(trabalho, nome), quotas, primeiras)
    gravar_atomico(trabalho / estado, json.dumps(estado_da_fila(fila), indent=1))
    _log(f"Retomada: {linha_de_progresso(fila)}", trabalho)
    feitos_na_sessao = 0
    erros_recentes: list[bool] = []
    # Só a população offline passa classe e faixa: a Copa 03 chama `executar`
    # exatamente como antes.
    extra = {} if (classe, faixa) == (CLASSE, FAIXA_DE_OP) else {"classe": classe, "faixa": faixa}
    contexto = mp.get_context("spawn")
    with executor or ProcessPoolExecutor(
        max_workers=trabalhadores, mp_context=contexto, max_tasks_per_child=1
    ) as pool:
        futuros = {}

        def despachar() -> None:
            while len(futuros) < trabalhadores:
                grupo = escolher_grupo(fila, limite)
                if grupo is None:
                    return
                k = grupo.proxima()
                grupo.em_voo.add(k)
                futuros[pool.submit(executar, grupo.perfil, grupo.politica, k, **extra)] = (
                    grupo,
                    k,
                )

        despachar()
        with open(trabalho / nome, "a", encoding="utf-8") as log:
            while futuros:
                prontos, _ = wait(futuros, return_when=FIRST_COMPLETED)
                for futuro in prontos:
                    grupo, k = futuros.pop(futuro)
                    grupo.em_voo.discard(k)
                    completo_antes = grupo.completo
                    try:
                        registro = futuro.result()
                    except Exception:  # noqa: BLE001 — processo morto, por exemplo
                        registro = {
                            "perfil": grupo.perfil,
                            "politica": grupo.politica,
                            "tentativa": k,
                            "seed": semente_da_run(grupo.perfil, grupo.politica, k, classe),
                            "teto": TETO,
                            "desfecho": "erro",
                            "motivo": "o processo da run falhou",
                            "erro": traceback.format_exc(limit=8),
                        }
                    snapshot = registro.pop("_snapshot", None)
                    if snapshot is not None:
                        nome = nome_do_candidato(grupo.perfil, grupo.politica, k)
                        gravar_atomico(
                            trabalho / "candidatos" / nome,
                            json.dumps(snapshot, ensure_ascii=False, indent=1),
                        )
                        registro["candidato"] = nome
                    log.write(json.dumps(registro, ensure_ascii=False) + "\n")
                    log.flush()
                    os.fsync(log.fileno())
                    grupo.concluidas[k] = registro
                    feitos_na_sessao += 1
                    erro = registro["desfecho"] == "erro"
                    erros_recentes = (erros_recentes + [erro])[-50:]
                    if erro:
                        with open(trabalho / "erros.log", "a", encoding="utf-8") as f:
                            f.write(f"{chave_do_grupo(grupo.chave)} #{k}\n{registro['erro']}\n")
                        _log(f"ERRO em {chave_do_grupo(grupo.chave)} #{k}", trabalho)
                    if grupo.completo and not completo_antes:
                        _log(
                            f"Quota fechada: {chave_do_grupo(grupo.chave)} | "
                            f"{linha_de_progresso(fila)}",
                            trabalho,
                        )
                    if feitos_na_sessao % 25 == 0:
                        _log(linha_de_progresso(fila), trabalho)
                    if feitos_na_sessao % 100 == 0:
                        _log(diagnostico(fila), trabalho)
                    gravar_atomico(trabalho / estado, json.dumps(estado_da_fila(fila), indent=1))
                if sum(erros_recentes) >= 5 and sum(erros_recentes) * 5 >= len(erros_recentes):
                    _log("PARADA: erros técnicos sistemáticos; ver erros.log", trabalho)
                    for f in futuros:
                        f.cancel()
                    break
                despachar()
    _log(f"Fim: {linha_de_progresso(fila)}", trabalho)
    _log(diagnostico(fila), trabalho)
    return estado_da_fila(fila)


# --- o preenchimento ----------------------------------------------------------

# Decisão do usuário depois de 1315 tentativas: as quotas 22/21/21 deixam de ser
# obrigatórias. A seleção original fica como está; as vagas que o hardcore não
# fechou vão para NOVAS runs v2 de conservador e moderado. O log da geração
# original não é tocado: o preenchimento tem log, fila e plano próprios.
VAGAS = 64
PERFIS_DO_PREENCHIMENTO = ("conservador", "moderado")
LOG_DO_PREENCHIMENTO = "preenchimento.jsonl"
FILA_DO_PREENCHIMENTO = "fila_preenchimento.json"
PLANO_DO_PREENCHIMENTO = "preenchimento.json"


def selecao_original(fila: dict) -> list[dict]:
    """Os aceitos da geração original e as extrações qualificadas que sobraram.

    Grupo completo: as aceitas da quota. Grupo incompleto (o hardcore): todas as
    qualificadas do checkpoint, inclusive alguma que tenha ficado depois de uma
    tentativa interrompida — essas entram como `hardcore_adicional`.
    """
    selecao = []
    for chave in GRUPOS:
        grupo = fila[chave]
        aceitas = grupo.aceitas()
        for k in aceitas:
            selecao.append(
                {"perfil": chave[0], "politica": chave[1], "tentativa": k, "origem": "original"}
            )
        if not grupo.completo:
            for k in sorted(grupo.concluidas):
                if grupo.concluidas[k].get("qualificada") and k not in aceitas:
                    selecao.append(
                        {
                            "perfil": chave[0],
                            "politica": chave[1],
                            "tentativa": k,
                            "origem": "hardcore_adicional",
                        }
                    )
    return selecao


def candidatos_do_checkpoint(fila: dict, selecao: list[dict]) -> list[dict]:
    """Extrações qualificadas de conservador e moderado que ficaram sem vaga."""
    usadas = {(s["perfil"], s["politica"], s["tentativa"]) for s in selecao}
    saida = []
    for chave in GRUPOS:
        if chave[0] not in PERFIS_DO_PREENCHIMENTO:
            continue
        for k in sorted(fila[chave].concluidas):
            r = fila[chave].concluidas[k]
            if r.get("qualificada") and (*chave, k) not in usadas:
                saida.append(
                    {
                        "perfil": chave[0],
                        "politica": chave[1],
                        "tentativa": k,
                        "origem": "preenchimento_checkpoint",
                    }
                )
    return saida


def plano_de_preenchimento(fila: dict) -> dict:
    """As vagas que faltam, em ordem, e de onde cada uma vem. Determinístico.

    Primeiro as qualificadas que sobraram no checkpoint. Depois, vaga a vaga: a
    política com menos gladiadores na população inteira (empate: survival,
    offense, economy) e, dentro dela, o perfil com menos vagas novas nessa
    política (empate: o com menos vagas novas no total; depois conservador).
    Isso dá perto de 50/50 entre conservador e moderado e equilibra as três
    políticas nos 64.
    """
    selecao = selecao_original(fila)
    candidatos = candidatos_do_checkpoint(fila, selecao)
    faltam = VAGAS - len(selecao)
    vagas = candidatos[:faltam]
    politicas = Counter(s["politica"] for s in selecao + vagas)
    while len(vagas) < faltam:
        politica = min(POLITICAS, key=lambda p: (politicas[p], POLITICAS.index(p)))
        novas = [v for v in vagas if v["origem"] == "preenchimento_novo"]
        na_politica = Counter(v["perfil"] for v in novas if v["politica"] == politica)
        no_total = Counter(v["perfil"] for v in novas)
        perfil = min(
            PERFIS_DO_PREENCHIMENTO,
            key=lambda p: (na_politica[p], no_total[p], PERFIS_DO_PREENCHIMENTO.index(p)),
        )
        vagas.append({"perfil": perfil, "politica": politica, "origem": "preenchimento_novo"})
        politicas[politica] += 1
    interrompidas = {
        chave_do_grupo(chave): [k for k in range(1, max(g.concluidas) + 1) if k not in g.concluidas]
        for chave, g in fila.items()
        if g.concluidas
    }
    return {
        "vagas": VAGAS,
        "tentativas_da_geracao_original": sum(len(g.concluidas) for g in fila.values()),
        "selecao_original": selecao,
        "preenchimento": vagas,
        "primeira_tentativa": {
            chave_do_grupo(chave): max(fila[chave].concluidas, default=0) + 1
            for chave in GRUPOS
            if chave[0] in PERFIS_DO_PREENCHIMENTO
        },
        "interrompidas": {k: v for k, v in interrompidas.items() if v},
    }


def _quotas_do_plano(plano: dict) -> tuple[dict, dict]:
    novas = Counter(
        (v["perfil"], v["politica"])
        for v in plano["preenchimento"]
        if v["origem"] == "preenchimento_novo"
    )
    quotas = {chave: novas[chave] for chave in GRUPOS if novas[chave]}
    primeiras = {chave: plano["primeira_tentativa"][chave_do_grupo(chave)] for chave in quotas}
    return quotas, primeiras


def ler_plano(trabalho: Path = TRABALHO) -> dict | None:
    arquivo = trabalho / PLANO_DO_PREENCHIMENTO
    return json.loads(arquivo.read_text(encoding="utf-8")) if arquivo.exists() else None


def fila_do_preenchimento(plano: dict, trabalho: Path = TRABALHO) -> dict:
    quotas, primeiras = _quotas_do_plano(plano)
    return montar_fila(ler_tentativas(trabalho, LOG_DO_PREENCHIMENTO), quotas, primeiras)


def preencher(trabalhadores: int = 4, trabalho: Path = TRABALHO, *, executor=None) -> dict:
    """Grava (ou confere) o plano e roda as runs novas que ele pede."""
    plano = plano_de_preenchimento(montar_fila(ler_tentativas(trabalho)))
    plano = json.loads(json.dumps(plano))
    gravado = ler_plano(trabalho)
    if gravado is None:
        gravar_atomico(trabalho / PLANO_DO_PREENCHIMENTO, json.dumps(plano, indent=1))
    elif gravado != plano:
        raise RuntimeError("o checkpoint da geração original mudou depois do plano")
    quotas, primeiras = _quotas_do_plano(plano)
    if quotas:
        gerar(
            trabalhadores,
            trabalho,
            executor=executor,
            quotas=quotas,
            primeiras=primeiras,
            nome=LOG_DO_PREENCHIMENTO,
            estado=FILA_DO_PREENCHIMENTO,
        )
    return plano


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    g = sub.add_parser("gerar")
    g.add_argument("--trabalhadores", type=int, default=os.cpu_count() or 2)
    p = sub.add_parser("preencher")
    p.add_argument("--trabalhadores", type=int, default=os.cpu_count() or 2)
    sub.add_parser("status")
    args = parser.parse_args()
    if args.comando == "gerar":
        estado = gerar(args.trabalhadores)
        return 0 if all(g["completo"] for g in estado["grupos"].values()) else 1
    if args.comando == "preencher":
        plano = preencher(args.trabalhadores)
        return 0 if all(g.completo for g in fila_do_preenchimento(plano).values()) else 1
    fila = montar_fila(ler_tentativas())
    print(linha_de_progresso(fila))
    print(diagnostico(fila))
    plano = ler_plano()
    if plano:
        fila = fila_do_preenchimento(plano)
        print("Preenchimento: " + linha_de_progresso(fila))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
