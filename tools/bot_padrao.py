"""BOT_PADRÃO: o jogador automatizado do ToJ.

As quatro políticas da auditoria anterior eram caricaturas úteis — limpar tudo,
correr, economizar, explorar. Nenhuma delas é um jogador. Esta é a tentativa de
escrever um: alguém que quer sobreviver, ficar mais forte, continuar descendo, e
que não gasta recurso nem encara inimigo sem motivo.

O que ela NÃO é: um jogador perfeito. Ela não conhece o RNG futuro, não sabe o
que o monstro vai dropar, e não sabe o resultado de uma batalha antes de lutar.
Decide com o que a tela mostra.

PARIDADE. Tudo que é REGRA vem do jogo:

    criação do personagem   engine.game_logic.create_player_from_data
    andar                   engine.loop._setup_dungeon_map
    combate                 mechanics.battle.run_battle
    pós-combate             engine.loop.process_post_battle
    loot / equipar          sim.progression.equip_if_better
    level-up                sim.progression.on_level_up
    loja                    sim.progression.visit_shop
    ferreiro                sim.progression.visit_forge
    eventos                 content.factories.dungeons
    saída / Essência        content.floor_exit
    juros                   content.economy.pay_interest

O que é DECISÃO — para onde ir, quando lutar, quando entrar na loja — mora aqui,
e é isso que o trace existe para você revisar.

    python -m tools.reference_run --seed 20260916 --classe warrior
"""

from __future__ import annotations

import argparse
import random
from collections import Counter
from dataclasses import dataclass

from src.content import level_up
from src.content.economy import exit_fee, pay_interest
from src.content.factories import features as feat
from src.content.factories.dungeons import (
    altar_hp_cost,
    apply_altar_blessing,
    apply_fountain_heal,
)
from src.content.floor_exit import effective_essence, unpaid_streak, use_exit
from src.content.shop import Shop
from src.engine.encounter import resolve_encounter
from src.engine.game_logic import create_player_from_data
from src.engine.loop import _setup_dungeon_map
from src.engine.map import EventTile, FeatureTile
from src.engine.map_analysis import campo_de_custo, rota_do_campo
from src.mechanics.battle import Action
from src.shared import combat_topics as T
from src.shared.constants import FLOOR_CLEAR_RESTORE_PERCENT
from src.sim import progression
from src.sim.pick_policies import DEFAULT_PICK_POLICY, get_pick_policy
from src.sim.policies import (
    _estimate_basic_damage,
    _estimated_turns,
    get_policy,
)
from src.sim.toggles import Toggles

# --------------------------------------------------------------------------
# Os limiares da política. Poucos, nomeados, e todos explicáveis em uma frase.
# --------------------------------------------------------------------------

# Abaixo disto o personagem está em perigo: nada de procurar briga.
HP_CRITICO = 0.35

# Não existem mais duas caças. Havia "obrigatória" (preciso de ouro para a saída)
# e "opcional" (quero XP), e a segunda exigia 80% de HP — o que na prática
# significava UMA luta por andar, porque uma luta custa quase metade da barra.
# Pior: a obrigatória estava atrás de `coins < taxa`, então pagar a saída
# DESLIGAVA a principal fonte de combate do bot. Ter ouro virava motivo para
# abandonar o mapa.
#
# Agora existe uma decisão só: ENGAJAR. Acima do piso ele luta; abaixo, procura
# recuperação e volta. Ouro nunca é condição — no máximo é um motivo a mais.
#
# O piso fica 0,20 da barra acima do crítico: margem para a policy de combate
# (que cura em 35% e foge em 12%) ainda ter turno de reagir.
HP_PARA_ENGAJAR = 0.55
# MP é munição, mas o ataque básico não custa mana: a barra aqui é baixa de
# propósito. Exigir 60% era recusar luta que o herói ganharia no braço.
MP_PARA_ENGAJAR = 0.15

# Quantas poções ele quer ter em mãos para sustentar o próximo andar. Não é uma
# quota de combate: é estoque de cura, e existe porque beber no mapa passou a ser
# o que devolve o andar depois de uma luta cara.
POCOES_PARA_SUSTENTAR = 2

# Abaixo disto a recuperação paga da Loja vale o desvio.
HP_SAUDAVEL = 0.65
# Quantos passos a mais ele aceita andar por um serviço.
DESVIO_ACEITAVEL = 10
# Quanto de ouro além da taxa de saída ele quer ter antes de ir às compras.
FOLGA_PARA_COMPRAR = 1.5
# Altar cobra vida. Só vale com folga real.
HP_PARA_ALTAR = 0.75

# --- Prioridade global de decisão ------------------------------------------
# O bot avaliava cada serviço isoladamente, e por isso gastava no Ferreiro logo
# antes de precisar do ouro para curar na Loja. A correção não é "no andar 7 não
# entre no Ferreiro": é uma ESCADA, e nenhuma necessidade mais baixa é atendida
# enquanto houver uma mais alta pendente e alcançável.
#
# `CONTINUIDADE` (preciso de ouro) e `COMBATE_OPCIONAL` (quero XP) eram dois
# degraus para o MESMO ato, e tê-los separados era o que permitia "já paguei a
# saída, logo não preciso lutar". Viraram um só: PROGREDIR. Lutar não é o que
# sobra quando não há mais nada urgente — é o objetivo do andar.
#
# `EVITAR_DESPROPORCIONAL` saiu da escada. Ele media desproporção pelo nível dos
# monstros no mapa, que o jogador não vê, e — pior — freava o combate justamente
# quando o herói estava atrasado, que é quando lutar é o único jeito de recuperar
# o atraso. A desproporção agora é julgada na FICHA, depois da colisão.
SOBREVIVENCIA = 1
RECUPERACAO = 2
PROGREDIR = 3
INVESTIMENTO = 4
ENCERRAR = 5

NOME_DA_NECESSIDADE = {
    SOBREVIVENCIA: "sobrevivência",
    RECUPERACAO: "recuperação",
    PROGREDIR: "progredir",
    INVESTIMENTO: "investimento",
    ENCERRAR: "encerrar o andar",
}


class Observador:
    """Escuta o barramento de combate e conta. Não decide, não altera, não sorteia.

    `run_battle` e `combat.py` já publicam tudo que interessa — golpe, crítico,
    esquiva, Égide, tick de veneno. O parâmetro `publish` existe desde sempre e o
    bot passava `None`. Passar um ouvinte é observação pura: `_emit` só chama o
    callback, sem tocar no RNG nem no fluxo.

    O que NÃO dá para observar daqui: o dano MITIGADO pela curva de defesa. O
    pipeline publica o dano final, não o de antes da mitigação. Inventar esse
    número seria pior que não ter.
    """

    def __init__(self, heroi_nome: str) -> None:
        self.heroi = heroi_nome
        self.dado_total = 0
        self.dado_max = 0
        self.dado_min: int | None = None
        self.recebido_total = 0
        self.recebido_max = 0
        self.recebido_min: int | None = None
        self.ultimo_recebido = 0
        self.crit_dados = 0
        self.crit_recebidos = 0
        self.erros_meus = 0
        self.erros_deles = 0
        self.absorvido_egide = 0
        self.mp_egide = 0
        self.dot_sofrido: Counter = Counter()
        self.golpe_fatal: dict | None = None
        # Reiniciado a cada encontro para medir a luta que mata.
        self.recebido_no_encontro = 0
        self.maior_no_encontro = 0

    def novo_encontro(self) -> None:
        self.recebido_no_encontro = 0
        self.maior_no_encontro = 0

    def __call__(self, topic: str, evento) -> None:
        payload = getattr(evento, "payload", {}) or {}
        if topic == T.COMBAT_PHYSICAL_STRIKE:
            self._golpe(payload.get("attacker"), payload.get("defender"), payload.get("strike"))
        elif topic == T.COMBAT_SKILL_OUTCOME:
            resultado = payload.get("result")
            golpe = getattr(resultado, "strike", None)
            if golpe is not None:
                self._golpe(payload.get("caster"), payload.get("target"), golpe)
        elif topic == T.COMBAT_TURN_EFFECT:
            self._efeito(payload)

    def _nome(self, entidade) -> str:
        obter = getattr(entidade, "get_nick_name", None)
        return obter() if callable(obter) else str(entidade)

    def _golpe(self, atacante, defensor, golpe) -> None:
        if golpe is None:
            return
        dano = int(getattr(golpe, "damage", 0) or 0)
        errou = bool(getattr(golpe, "was_evaded", False))
        critico = bool(getattr(golpe, "was_critical", False))
        meu = self._nome(atacante) == self.heroi

        if errou:
            # MISS não é "dano zero": contá-lo como golpe faria o mínimo ser
            # sempre 0 e apagaria o piso real de dano.
            if meu:
                self.erros_meus += 1
            else:
                self.erros_deles += 1
            return
        if dano <= 0:
            return

        if meu:
            self.dado_total += dano
            self.dado_max = max(self.dado_max, dano)
            self.dado_min = dano if self.dado_min is None else min(self.dado_min, dano)
            self.crit_dados += int(critico)
        elif self._nome(defensor) == self.heroi:
            self.recebido_total += dano
            self.recebido_max = max(self.recebido_max, dano)
            self.recebido_min = dano if self.recebido_min is None else min(self.recebido_min, dano)
            self.crit_recebidos += int(critico)
            self.ultimo_recebido = dano
            self.recebido_no_encontro += dano
            self.maior_no_encontro = max(self.maior_no_encontro, dano)
            self.golpe_fatal = {
                "de": self._nome(atacante),
                "dano": dano,
                "critico": critico,
                "tipo": "golpe",
            }

    def _efeito(self, payload) -> None:
        if self._nome(payload.get("entity")) != self.heroi:
            return
        kind = str(payload.get("kind", ""))
        if kind == "magic_shield":
            self.absorvido_egide += int(payload.get("absorbed", 0) or 0)
            self.mp_egide += int(payload.get("mp", 0) or 0)
            return
        if kind.endswith("_tick") and "damage" in payload:
            dano = int(payload.get("damage", 0) or 0)
            if dano <= 0:
                return
            efeito = kind[: -len("_tick")]
            self.dot_sofrido[efeito] += dano
            self.recebido_total += dano
            self.recebido_no_encontro += dano
            self.ultimo_recebido = dano
            self.golpe_fatal = {
                "de": efeito,
                "dano": dano,
                "critico": False,
                "tipo": "tick",
            }


@dataclass(frozen=True)
class Perfil:
    """Quanto este jogador procura combate NO MAPA. Só isso.

    Nenhum perfil toca em `smart_policy`: dentro do duelo os três usam skill,
    cura, fuga, buff e controle exatamente igual. A variável do experimento é o
    APETITE, e ela mora aqui para que se possa apontar o que mudou.
    """

    nome: str
    # Estado mínimo para colidir com o próximo monstro.
    hp_engajar: float
    mp_engajar: float


# O perfil não tem mais um campo "só luta quando está atrasado". Aquele portão
# existia para conter a caça opcional, e o que ele produzia era o inverso da
# intenção: o herói adiantado parava de lutar e voltava a ficar atrasado.
CONSERVADOR = Perfil("conservador", HP_PARA_ENGAJAR, MP_PARA_ENGAJAR)
MODERADO = Perfil("moderado", 0.45, 0.10)
HARDCORE = Perfil("hardcore", 0.38, 0.05)
PERFIS = {p.nome: p for p in (CONSERVADOR, MODERADO, HARDCORE)}

# --- Desproporção, julgada na FICHA -----------------------------------------
# Não existe mais um `GAP_ACEITAVEL` aplicado ao mapa: o jogador olha o mapa e vê
# `&`, não "Nv7". A ficha do inimigo (nível, HP, ST, DF) só aparece em
# `render_fight_intro`, DEPOIS da colisão — e ali a saída é `flee`, que é 50% por
# turno.
#
# A régua: quantos turnos eu levo para matá-lo, contra quantos ele leva para me
# matar. Em 1,0 a regra é "não entro numa corrida de dano que eu perco". Medido
# na seed 20260918, as lutas ganhas ficaram em 0,20–0,83 e a que matou o Warrior
# no andar 5 estava em 1,33 — o limiar separa as duas populações.
#
# Não é 2,0. Com 2,0 o bot aceitava lutas em que morre ao dobro da velocidade com
# que mata, contando com skill e cura para virar. Isso não é ler a ficha: é
# apostar o personagem e chamar de leitura.
RAZAO_MAXIMA_PARA_LUTAR = 1.0

# --- Extração ---------------------------------------------------------------
# A Extração deixou de ser tratada só como botão de pânico. Sempre que existir
# uma casa alcançável ela é AVALIADA, e o trace registra o veredito — inclusive
# quando o veredito é continuar.
HP_DE_RISCO = 0.50
STREAK_DE_RISCO = 3
# Quantos sinais de risco simultâneos convencem a sair.
SINAIS_PARA_EXTRAIR = 2


# Passo -> tecla. Não é regra de jogo espelhada: é a tradução entre "a rota diz
# para ir ao norte" e a letra que `move_player` espera. Quem decide o que
# acontece ao pisar continua sendo `move_player`.
DIRECAO = {(-1, 0): "w", (1, 0): "s", (0, -1): "a", (0, 1): "d"}


def _pos(d: dict) -> tuple[int, int]:
    return (d["y"], d["x"])


def _frac_hp(hero) -> float:
    return hero.get_hp() / max(1, hero.base_hp)


def _frac_mp(hero) -> float:
    return hero.get_mp() / max(1, hero.base_mp)


def _pocoes(hero) -> list:
    return [
        i
        for i in hero.inventory
        if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
    ]


class Trace:
    """O diário da run. É o produto desta rodada, não um efeito colateral."""

    def __init__(self) -> None:
        self.linhas: list[str] = []

    def secao(self, texto: str) -> None:
        self.linhas.append("")
        self.linhas.append(texto)
        self.linhas.append("-" * len(texto))

    def diz(self, texto: str) -> None:
        self.linhas.append(texto)

    def decisao(self, texto: str) -> None:
        self.linhas.append(f'  DECISÃO: "{texto}"')

    def __str__(self) -> str:
        return "\n".join(self.linhas)


class BotPadrao:
    """Um jogador automatizado. Observa, escolhe UMA ação, e o jogo executa."""

    def __init__(
        self, classe: str, seed: int, max_andar: int = 20, perfil: Perfil = CONSERVADOR
    ) -> None:
        random.seed(seed)
        self.rng = random.Random(seed)
        self.seed = seed
        self.max_andar = max_andar
        self.perfil = perfil
        # O CAMINHO REAL de criação de personagem. Sem loadout, sem presente:
        # nível 1, sem ouro, sem inventário, sem equipamento, uma skill.
        self.hero = create_player_from_data(classe, "Referencia")
        # A política de combate do bot é a do simulador MAIS a leitura da ficha.
        # A composição acontece aqui, e não dentro do duelo, porque assim trocar
        # `self.decide` troca a política INTEIRA — que é o que um teste quer
        # dizer quando fixa a decisão para isolar o núcleo do encontro.
        self.decide = self._com_leitura_de_ficha(get_policy("smart"))
        self.picker = get_pick_policy(DEFAULT_PICK_POLICY)
        self.toggles = Toggles()
        self.trace = Trace()
        self.fim = ""
        self.andar = 0
        # Quantas vezes cada verbo de combate foi escolhido na run inteira.
        self.acoes: Counter = Counter()
        self.mp_gasto = 0
        # Denominador honesto para "usou pouca mana": o MP que ele TINHA ao
        # entrar em cada luta, somado. Comparar com `base_mp` ignoraria que ele
        # entra na segunda luta já gastando o que sobrou da primeira.
        self.mp_disponivel = 0
        # `self.combates` é zerado a cada andar para a linha "Fim do andar".
        # Este acumula a run inteira.
        self.combates_na_run = 0
        # O combate que encerrou a run, com o que era visível ANTES dele.
        self.fatal: dict | None = None
        # Por andar: quantos monstros o andar TINHA (contados uma vez, na
        # entrada) e quantos duelos aconteceram. Contar na entrada evita somar o
        # mesmo monstro toda vez que o bot reavalia os alvos.
        self.por_andar: list[dict] = []
        # Serviços efetivamente USADOS (não só pisados).
        self.servicos: Counter = Counter()
        # Fugas decididas na FICHA, no turno 1 — separadas das que a política de
        # combate toma no meio da luta, que já estão em `acoes["flee"]`.
        self.fugas_na_run = 0
        self.pocoes_bebidas = 0
        # A ficha do encontro corrente já foi ao trace? Reler não muda decisão;
        # só evita repetir a mesma linha a cada turno de uma fuga insistente.
        self._ficha_lida = False
        # Por que ele parou de lutar no andar corrente. Vai ao registro do andar.
        self.parada = ""
        # Ouvinte do barramento de combate. Só conta; `_emit` não consulta o
        # RNG nem o retorno do callback, então plugar isto não muda uma decisão.
        self.observador = Observador(self.hero.get_nick_name())

    # -- observação -------------------------------------------------------

    def _campo(self, por_combate: bool):
        return campo_de_custo(self.mapa, self.posicao, por_combate=por_combate)

    def _alcance(self, casa, por_combate: bool = True):
        """(passos, combates) até a casa, ou None se não dá para chegar."""
        rota, _ = rota_do_campo(self._campo(por_combate), casa, por_combate)
        return (rota.passos, rota.combates) if rota.alcancavel else None

    def _desvio(self, casa) -> int | None:
        """Passos a mais para passar pela casa antes da saída."""
        ida = self._alcance(casa)
        direto = self._alcance(self.saida)
        if ida is None or direto is None:
            return None
        volta, _ = rota_do_campo(
            campo_de_custo(self.mapa, casa, por_combate=True), self.saida, True
        )
        if not volta.alcancavel:
            return None
        return max(0, ida[0] + volta.passos - direto[0])

    def _casa_de(self, tipo: str):
        if tipo == "event":
            return self.mapa.event_pos
        for casa, nome in self.mapa.features.items():
            if nome == tipo:
                return casa
        return None

    def _alvos_visiveis(self) -> list[dict]:
        """Os monstros alcançáveis, com o que o MAPA mostra de cada um.

        O jogador olha o mapa e vê `&`, ou `B` se for chefe (`MapOfGame.draw_map`).
        Nome e nível NÃO estão ali: a ficha do inimigo — nível, HP, MP, ST, AG,
        MG, DF — só aparece em `render_fight_intro`, depois da colisão, e com
        `allow_escape=False`. A versão anterior lia `get_nick_name()` e `.level`
        daqui e escolhia alvo por defasagem de nível: informação que nenhum
        jogador tem antes de encostar no monstro.

        O que sobra é honesto e suficiente: onde ele está, quantos passos custa,
        quantas OUTRAS lutas a rota obriga, e se é chefe.
        """
        campo = self._campo(por_combate=True)
        alvos = []
        for casa, monstro in self.mapa.enemies_pos.items():
            rota, _ = rota_do_campo(campo, casa, True)
            if not rota.alcancavel:
                continue
            alvos.append(
                {
                    "casa": casa,
                    "passos": rota.passos,
                    # A rota até ele pode obrigar a lutar com OUTROS pelo
                    # caminho. Um alvo perto atrás de dois monstros não é perto.
                    "extras": max(0, rota.combates - 1),
                    "chefe": bool(getattr(monstro, "is_boss", False)),
                }
            )
        return alvos

    def _melhor_alvo(self, alvos: list[dict]) -> dict | None:
        """O alvo mais barato de alcançar: menos lutas pelo caminho, depois mais perto.

        `extras` vem antes de `passos` de propósito: um monstro a 3 passos com
        dois outros na frente custa três lutas, e um a 9 passos com o caminho
        livre custa uma.

        Chefe (`B`) não entra. É a única distinção de perigo que o mapa oferece
        ao jogador, e ignorá-la seria jogar pior que um humano, não melhor.
        """
        candidatos = [a for a in alvos if not a["chefe"]]
        if not candidatos:
            return None
        return min(candidatos, key=lambda a: (a["extras"], a["passos"]))

    def _descrever_alvos(self, alvos: list[dict], escolhido: dict | None) -> None:
        """Põe no trace o que o mapa mostrava e o que foi escolhido.

        Sem nome e sem nível: o trace registra a decisão com a informação que a
        decisão teve. O nome do monstro aparece na linha do combate, que é
        quando o jogador também o descobre.
        """
        if not alvos:
            return
        partes = []
        for a in sorted(alvos, key=lambda x: (x["extras"], x["passos"])):
            marca = (
                "ESCOLHIDO"
                if escolhido is not None and a["casa"] == escolhido["casa"]
                else ("chefe — não é alvo opcional" if a["chefe"] else "descartado")
            )
            partes.append(
                f"{'B' if a['chefe'] else '&'} a {a['passos']} passos"
                + (f", +{a['extras']} luta(s) no caminho" if a["extras"] else "")
                + f" — {marca}"
            )
        self.trace.diz("  Alvos visíveis no mapa: " + " | ".join(partes))

    # -- ações ------------------------------------------------------------

    def _ir_ate(self, destino, evitando: bool = True) -> bool:
        """Anda até a casa, UM PASSO POR VEZ, pelo movimento real do jogo.

        Cada passo é `MapOfGame.move_player`, a mesma função que o teclado
        aciona: é ela que decide o que acontece ao pisar numa casa. Antes esta
        função só olhava para `enemies_pos`, e o herói atravessava Loja,
        Ferreiro, Evento e Extração como se fossem chão quando o objetivo era
        outro — intangível às casas que o jogo faz o jogador encarar.

        A policy ainda decide o que FAZER com a casa (abrir a loja ou passar
        reto), mas não decide mais se a casa existe. Devolve False só quando a
        run acabou.
        """
        if destino == self.posicao:
            monstro = self.mapa.enemies_pos.get(destino)
            return self._duelo(monstro, destino) if monstro is not None else True

        rota, caminho = rota_do_campo(self._campo(evitando), destino, evitando)
        if not rota.alcancavel:
            return True

        for casa in caminho[1:]:
            anterior = self.posicao
            direcao = DIRECAO.get((casa[0] - anterior[0], casa[1] - anterior[1]))
            if direcao is None:
                return True
            resultado = self.mapa.move_player(direcao)
            self.posicao = _pos(self.mapa.player_pos)
            if self.posicao == anterior and resultado is None:
                # Parede ou borda: a rota e o mapa discordam. Parar é melhor que
                # girar no lugar.
                return True
            self.passos += 1
            if not self._resolver_casa(resultado, casa):
                return False
            if resultado == "level_complete":
                self.posicao = self.saida
                return True
        return True

    def _resolver_casa(self, resultado, casa) -> bool:
        """O que a casa em que ele pisou produz. False se a run acabou."""
        if resultado is None or resultado == "level_complete":
            return True
        if isinstance(resultado, EventTile):
            # `move_player` JÁ consumiu o evento — e é a regra: recusar o Altar,
            # ignorar a Fonte ou sair do Mercador sem comprar gastam a visita do
            # mesmo jeito. O que a policy ainda decide é se ACEITA o efeito.
            return self._resolver_evento(resultado.event_type)
        if isinstance(resultado, FeatureTile):
            return self._resolver_feature(resultado.feature, resultado.position)
        return self._duelo(resultado, casa)

    def _resolver_feature(self, tipo: str, casa) -> bool:
        """Pisou num serviço. A casa NÃO foi consumida: quem gasta é abrir."""
        hero = self.hero
        taxa = exit_fee(self.andar)
        hp = _frac_hp(hero)

        if tipo == feat.EXTRACTION:
            extrair, veredito = self._avaliar_extracao(casa)
            if veredito == self._ultimo_veredito_extracao:
                self.trace.diz("  Pisou na Extração — o veredito acima é o desta casa.")
            else:
                self.trace.diz(f"  Pisou na Extração. {veredito}")
                self._ultimo_veredito_extracao = veredito
            if extrair:
                self.extraiu = True
                return False
            return True

        if tipo == feat.SHOP:
            if hp < HP_SAUDAVEL or hero.coins >= taxa * FOLGA_PARA_COMPRAR:
                self.trace.diz("  Pisou na Loja e vale entrar.")
                self.mapa.take_feature(casa)
                self.servicos["loja"] += 1
                self._comprar_com_orcamento("Loja")
            else:
                self.trace.diz(
                    f"  Pisou na Loja e passou reto: {hero.coins} de ouro contra uma saída de "
                    f"{taxa}, e {hp:.0%} de HP. Nada aqui que valha a reserva."
                )
            return True

        if tipo == feat.FORGE:
            necessidade, porque = self._necessidade_atual()
            if necessidade < INVESTIMENTO:
                self.trace.diz(
                    f"  Pisou no Ferreiro e passou reto: o que importa agora é "
                    f"{NOME_DA_NECESSIDADE[necessidade]} ({porque}). Aprimorar equipamento é "
                    "investimento, e investimento espera."
                )
                return True
            if not self._tem_peca_para_investir():
                self.trace.diz("  Pisou no Ferreiro e passou reto: não tenho peça equipada.")
                return True
            self.trace.diz(
                f"  Pisou no Ferreiro e vale entrar: {hero.coins} de ouro, saída de {taxa} "
                "garantida, e nada mais urgente pendente."
            )
            self.mapa.take_feature(casa)
            self.servicos["ferreiro"] += 1
            self._usar_ferreiro(casa)
            return True
        return True

    def _com_leitura_de_ficha(self, politica):
        """A política tática do simulador, precedida da leitura da ficha.

        Fica ANTES de `smart_policy` pela mesma razão que o jogador lê
        `render_compare_opponents` antes de escolher a tecla: a tela de confronto
        vem primeiro, e o que ela diz pode ser "não lute isto".

        Reavalia a cada turno, não só no primeiro: fugir é 50% por turno
        (`FLEE_RANGE_MAX = 2`), e uma tentativa só seria aceitar a primeira
        moeda e ficar na luta que já se decidiu não querer.
        """

        def decidir(heroi, monstros, turno):
            alvo = monstros[0] if isinstance(monstros, list) else monstros
            fuga = self._ler_a_ficha(heroi, alvo)
            if fuga is not None:
                if turno == 0:
                    self.fugas_na_run += 1
                    if self.por_andar:
                        self.por_andar[-1]["fugas"] += 1
                return fuga
            return politica(heroi, monstros, turno)

        return decidir

    def _ler_a_ficha(self, heroi, monstro):
        """A tela de confronto, e o que fazer com ela. Devolve `flee` ou None.

        É aqui que a desproporção é julgada, e não no mapa. `render_fight_intro`
        mostra nível, HP, MP, ST, AG, MG e DF dos dois lados — e mostra DEPOIS
        da colisão, com `allow_escape=False`. O jogador não escolhe não lutar:
        escolhe fugir, a 50% por turno.

        A conta reusa `_estimate_basic_damage` e `_estimated_turns` de
        `sim/policies`, que leem exatamente os campos da tela. Quantos turnos
        para matá-lo, quantos para ele me matar. Se ele me mata muito mais
        rápido, a aposta da fuga é melhor que a da luta.

        Uma imprecisão registrada em vez de escondida: o humano vê a ficha antes
        de qualquer turno; o bot vê no primeiro turno DELE, que pode vir depois
        de um golpe do monstro se a agilidade dele for maior.
        """
        meu_dano = _estimate_basic_damage(heroi, monstro)
        dano_dele = _estimate_basic_damage(monstro, heroi)
        turnos_para_matar = _estimated_turns(monstro, meu_dano)
        turnos_para_morrer = _estimated_turns(heroi, dano_dele)
        if turnos_para_matar <= turnos_para_morrer * RAZAO_MAXIMA_PARA_LUTAR:
            return None
        if self._ficha_lida:
            return Action(kind="flee")
        self._ficha_lida = True
        self.trace.diz(
            f"  Ficha do inimigo: {monstro.get_nick_name()} Nv{getattr(monstro, 'level', '?')} "
            f"| HP {monstro.get_hp()} ST {monstro.get_st()} DF {monstro.get_df()}. "
            f"Mato em ~{turnos_para_matar} turnos, morro em ~{turnos_para_morrer}. "
            "Perco a corrida de dano — tento fugir."
        )
        return Action(kind="flee")

    def _duelo(self, monstro, casa) -> bool:
        """Um encontro, pelo MESMO core que a tela do jogador usa.

        O bot não monta mais a sequência (batalha, guarda de fuga, pós-combate,
        ofertas): ele pede o encontro e responde quando o core pergunta. Montar
        por fora era ter dois roteiros, e foi assim que fugir chegou a pagar
        recompensa cheia.
        """
        hero = self.hero
        # `move_player` tira o monstro da casa AO COLIDIR, antes de saber o
        # resultado — fugir também consome o encontro no jogo.
        self.mapa.enemies_pos.pop(casa, None)
        self.mapa.grid[casa[0]][casa[1]] = "D"

        hp_antes, mp_antes = hero.get_hp(), hero.get_mp()
        self.observador.novo_encontro()
        self._ficha_lida = False
        nome = monstro.get_nick_name()
        nivel_alvo = int(getattr(monstro, "level", hero.get_level()))
        self.mp_disponivel += mp_antes
        # Gravado ANTES de saber o resultado: se esta luta for a última, é isto
        # que o jogador tinha na tela ao aceitá-la.
        candidato = {
            "monstro": nome,
            "nivel": nivel_alvo,
            "gap": nivel_alvo - hero.get_level(),
            "hp_antes": hp_antes,
            "hp_frac": hp_antes / max(1, hero.base_hp),
            "mp_antes": mp_antes,
            "mp_frac": mp_antes / max(1, hero.base_mp),
            "andar": self.andar,
        }

        def _apos_o_combate(resultado) -> None:
            """O que o bot faz com o resultado — ANTES das escolhas de nível.

            É o mesmo gancho que a tela do jogador usa para desenhar os
            resultados. Sem ele, o level-up aparecia no trace antes do combate
            que o causou: a ordem do core é batalha -> pós-combate ->
            apresentação -> ofertas.
            """
            self.trace.diz(
                f"  Combate: {nome} -> {'vitória' if resultado.hero_won else 'DERROTA'} | "
                f"HP {hp_antes}->{hero.get_hp()} MP {mp_antes}->{hero.get_mp()} | "
                f"+{resultado.xp_gained} XP +{resultado.coins_gained} ouro"
            )
            self.mp_gasto += max(0, mp_antes - hero.get_mp())
            drop = resultado.dropped_item
            if drop is None:
                return
            trocou = progression.equip_if_better(hero, drop)
            self.trace.diz(
                f"  Drop: {drop.name} ({getattr(drop, 'rarity', '?')}) — "
                + ("EQUIPOU, é melhor que o que estava no slot" if trocou else "guardou na mochila")
            )

        # OBSERVAÇÃO, não decisão: conta o verbo que a política devolveu e
        # devolve exatamente isso. Sem ele não dá para responder "o Mago usa
        # mana ou fica no ataque básico?" — e a resposta não pode ser um palpite.
        def _observar(h, m, turno):
            acao = self.decide(h, m, turno)
            self.acoes[getattr(acao, "kind", "?")] += 1
            return acao

        resultado = resolve_encounter(
            hero,
            [monstro],
            combat_decision=_observar,
            level_up_provider=self._escolher_do_nivel,
            rng=self.rng,
            essence_multiplier=self.essencia,
            dungeon_level=self.andar,
            on_results=_apos_o_combate,
            publish=self.observador,
        )
        self.combates += 1
        self.combates_na_run += 1
        if self.por_andar:
            self.por_andar[-1]["combates"] += 1

        if resultado.fled:
            self.trace.diz(f"  Combate: {nome} -> FUGIU | HP {hp_antes}->{hero.get_hp()}")
        vivo = hero.get_isalive() and hero.get_hp() > 0
        if not vivo:
            candidato["turnos"] = int(getattr(resultado.outcome, "turns", 0) or 0)
            candidato["dano_no_encontro"] = self.observador.recebido_no_encontro
            candidato["maior_no_encontro"] = self.observador.maior_no_encontro
            candidato["golpe_final"] = self.observador.golpe_fatal
            self.fatal = candidato
        return vivo

    def _escolher_do_nivel(self, jogador, oferta) -> None:
        """A resposta do bot quando o core pergunta o que levar deste nível.

        A oferta VEIO do core — as mesmas três cartas que a tela mostraria. Aqui
        só se escolhe, e a aplicação passa por `content.level_up`, que é a mesma
        função da tela.
        """
        self.trace.diz(f"  LEVEL UP -> nível {jogador.get_level()}")
        self.trace.diz(
            "  Passivas oferecidas: "
            + ", ".join(f"{c.name} [{c.rarity}/{c.effect_type}]" for c in oferta.passives)
        )
        escolhida = self.picker.pick_passive(jogador, oferta.passives, self.rng)
        if escolhida is not None:
            level_up.aplicar_passiva(jogador, escolhida)
            self.trace.diz(
                f"  Escolha: {escolhida.name} [{escolhida.effect_type}] — primeira da ordem "
                f"de preferência da política '{self.picker.name}' presente na oferta"
            )

        if not oferta.tem_skill:
            return
        self.trace.diz(
            "  Skills oferecidas: "
            + ", ".join(
                f"{c.name} [{getattr(c, 'rarity', '?')}/{getattr(c, 'effect_type', '?')}]"
                for c in oferta.skills
            )
        )
        nova, slot = self.picker.pick_skill(jogador, oferta.skills, self.rng)
        if nova is None:
            self.trace.diz("  Escolha: recusou — nenhuma melhora o que já tem")
            return
        level_up.aplicar_skill(jogador, nova, slot)
        self.trace.diz(
            f"  Escolha: {nova.name} — primeira da ordem de preferência da política "
            f"'{self.picker.name}' presente na oferta"
        )

    # -- serviços ---------------------------------------------------------

    def _orcamento(self) -> tuple[int, int, bool]:
        """Quanto o jogador está disposto a gastar: (orçamento, reserva, quebrou).

        `ouro disponível = ouro atual - reserva desejada`, e a reserva desejada é
        a taxa de saída deste andar. A EXCEÇÃO é sobrevivência: com o HP baixo,
        recuperar vale mais que subir de graça, e aí a reserva é conscientemente
        quebrada — mas o trace tem de dizer isso em voz alta.

        A exceção disparava em `HP_SAUDAVEL` (65%). Com o bot jogando o andar em
        vez de correr para a saída, estar abaixo de 65% virou o estado NORMAL, e
        a exceção passou a valer sempre: ele gastava 91 de 108 em recuperação,
        saía sem pagar, perdia Essência e nunca sobrava ouro para poção — que é
        justamente a cura que sustentaria o andar seguinte.
        Agora a reserva só é quebrada em emergência de verdade.
        """
        hero = self.hero
        taxa = exit_fee(self.andar)
        if _frac_hp(hero) < HP_CRITICO:
            return hero.coins, taxa, True
        return max(0, hero.coins - taxa), taxa, False

    def _beber_pocao(self) -> bool:
        """Abre o inventário no mapa e bebe. Mesma porta que o jogador usa.

        `navigation_menu.py:975` chama exatamente `player.use_potion(item)` fora
        de combate — é uma ação de jogador que existe desde sempre e que o bot
        nunca tomou. Em 60 partidas ele usou poção 22 vezes, todas DENTRO do
        combate, e terminou runs com cura na mochila.

        Este é o degrau que sustenta jogar o andar: depois de uma luta cara,
        beber devolve o piso de engajamento sem custar ouro nem passos.
        """
        hero = self.hero
        curas = [
            i
            for i in hero.inventory
            if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
        ]
        if not curas:
            return False
        melhor = max(curas, key=lambda i: int(getattr(i, "effect_value", 0) or 0))
        antes = hero.get_hp()
        # `use_potion` já tira o item da mochila (heroes.py:750). Remover de novo
        # aqui seria consumir duas poções para curar uma vez.
        hero.use_potion(melhor)
        self.pocoes_bebidas += 1
        if self.por_andar:
            self.por_andar[-1]["pocoes_bebidas"] += 1
        self.trace.diz(
            f"  Bebeu {melhor.name} no mapa: HP {antes} -> {hero.get_hp()} "
            f"({self._pocoes()} restante(s) na mochila)."
        )
        return True

    def _comprar_com_orcamento(self, rotulo: str) -> None:
        """Abre a loja levando SÓ o orçamento, e devolve a reserva depois.

        A política de compra de `progression.visit_shop` é boa — vende o
        dominado, repara a vida, repõe cura e só então melhora equipamento — mas
        não conhece a taxa de saída e gasta até o fim. Ensinar a reserva a ela
        seria forkar a regra.

        Então quem decide o limite é o JOGADOR, no único lugar em que isso é
        decisão e não regra: o quanto ele leva na carteira. A loja gasta o que vê.
        O que ficou reservado volta depois, e o que ela conseguiu VENDENDO fica,
        porque vender é receita e não orçamento.
        """
        hero = self.hero
        orcamento, reserva, quebrou = self._orcamento()
        ouro_antes, hp_antes = hero.coins, hero.get_hp()
        guardado = ouro_antes - orcamento

        if quebrou:
            self.trace.diz(
                f"  Vou sacrificar a saída paga para recuperar HP: levo os {ouro_antes} "
                f"inteiros, e a saída custa {reserva}."
            )
            self.reserva_gasta += 1
        else:
            self.trace.diz(
                f"  Orçamento de compra: {orcamento} "
                f"(ouro {ouro_antes} − reserva de saída {reserva}). O resto fica guardado."
            )

        hero.coins = orcamento
        try:
            progression.visit_shop(hero, Shop(), self.andar, self.rng, self.toggles, None)
        finally:
            hero.coins += guardado

        self.trace.diz(
            f"  {rotulo}: ouro {ouro_antes} -> {hero.coins} | HP {hp_antes} -> {hero.get_hp()}"
        )

    def _usar_ferreiro(self, casa) -> None:
        hero = self.hero
        ouro_antes = hero.coins
        progression.visit_forge(hero, self.andar, self.toggles, None)
        self.trace.diz(f"  Ferreiro: ouro {ouro_antes} -> {hero.coins}")

    def _resolver_evento(self, tipo: str | None) -> bool:
        """O evento em que ele pisou. A casa já foi gasta por `move_player`.

        A policy ainda escolhe ACEITAR ou não: o Altar cobra vida, e pagá-lo com
        pouco HP é como um jogador morre. Recusar não devolve a casa — é a regra
        do jogo, e é por isso que atravessar um evento por acaso tem preço.
        """
        hero = self.hero
        if tipo == "altar" and _frac_hp(hero) < HP_PARA_ALTAR:
            self.trace.diz(
                f"  Evento Altar: RECUSADO. Ele cobra vida e estou com "
                f"{_frac_hp(hero):.0%} — a casa some do mesmo jeito, mas pagar aqui me mata."
            )
            return True
        self.servicos[f"evento:{tipo}"] += 1
        if tipo == "fountain":
            curou = apply_fountain_heal(hero)
            self.trace.diz(f"  Evento Fonte: curou {int(curou)} (HP {hero.get_hp()})")
        elif tipo == "altar":
            custo = altar_hp_cost(hero)
            hero.take_damage(custo)
            apply_altar_blessing(hero)
            self.trace.diz(f"  Evento Altar: pagou {int(custo)} de HP (HP {hero.get_hp()})")
            if hero.get_hp() <= 0:
                hero.set_isalive(False)
                return False
        elif tipo == "merchant":
            # O Mercador ABRE A MESMA LOJA, então respeita o mesmo orçamento.
            self._comprar_com_orcamento("Evento Mercador")
        return True

    # -- a decisão --------------------------------------------------------

    def _decidir(self):
        """O próximo objetivo, e a frase que o justifica.

        Uma decisão por vez, reavaliada depois de cada combate, drop, nível,
        compra ou evento — porque o estado mudou e a decisão pode mudar.
        """
        hero = self.hero
        hp, mp = _frac_hp(hero), _frac_mp(hero)
        taxa = exit_fee(self.andar)
        loja, ferreiro, evento = (self._casa_de(t) for t in (feat.SHOP, feat.FORGE, "event"))
        extracao = self._casa_de(feat.EXTRACTION)
        alvos = self._alvos_visiveis()
        alvo = self._melhor_alvo(alvos)

        # 1. Perigo. Em ordem: quem cura primeiro e mais barato.
        if hp < HP_CRITICO:
            if evento is not None and self.mapa.event_type == "fountain":
                desvio = self._desvio(evento)
                if desvio is not None:
                    return (
                        "evento",
                        evento,
                        f"HP em {hp:.0%}. Há uma Fonte a {desvio} passos de "
                        "desvio — curar antes de qualquer outra coisa.",
                    )
            if self._pocoes() > 0:
                return (
                    "pocao",
                    None,
                    f"HP em {hp:.0%} e {self._pocoes()} poção(ões) na mochila. Bebo AGORA — "
                    "morrer com cura guardada é o pior desfecho possível.",
                )
            if loja is not None and hero.coins > 0 and self._desvio(loja) is not None:
                return (
                    "loja",
                    loja,
                    f"HP em {hp:.0%} e tenho {hero.coins} de ouro. Vou à Loja "
                    "pagar recuperação antes de arriscar o resto do andar.",
                )
            if extracao is not None and self._tem_o_que_preservar():
                if self._alcance(extracao) is not None:
                    self.parada = f"HP em {hp:.0%} sem cura alcançável"
                    return (
                        "extrair",
                        extracao,
                        f"HP em {hp:.0%}, sem cura por perto, e já tenho "
                        f"nível {hero.get_level()} e {len(hero.passives)} passivas para "
                        "preservar. Extrair vale mais que insistir.",
                    )
            self.parada = f"HP em {hp:.0%}, abaixo do crítico, e nada que cure no andar"
            return (
                "saida",
                self.saida,
                f"HP em {hp:.0%} e nada que cure por perto. Encerro o "
                "andar pela rota de menos combate — o descanso do fim de andar é a cura.",
            )

        # 2. Extração: avaliada SEMPRE que houver casa alcançável, e não só em
        #    emergência. O veredito entra no trace mesmo quando é "continuo".
        if extracao is not None and self._alcance(extracao) is not None:
            extrair, veredito = self._avaliar_extracao(extracao)
            if extrair:
                self._ultimo_veredito_extracao = veredito
                return ("extrair", extracao, veredito)
            if veredito != self._ultimo_veredito_extracao:
                self.trace.diz(f"  {veredito}")
                self._ultimo_veredito_extracao = veredito

        # 2b. Beber é barato: não custa passo nem ouro, e poção parada na mochila
        #     não cura ninguém. NÃO é pré-condição para lutar — acima do piso ele
        #     luta sem cura garantida, como pedido. É só deixar de morrer com
        #     cura guardada, que foi como a primeira versão desta policy perdeu o
        #     Warrior no andar 5 com uma poção na bolsa.
        if hp < HP_SAUDAVEL and self._pocoes() > 0 and alvo is not None:
            return (
                "pocao",
                None,
                f"HP em {hp:.0%} e ainda há monstro no andar. Bebo uma das "
                f"{self._pocoes()} poções antes de encostar no próximo — beber é de graça em "
                "passos e em ouro.",
            )

        # 3. RECUPERAÇÃO. Abaixo do piso de engajamento ele NÃO desiste do andar:
        #    procura como voltar a poder lutar. Era aqui que a versão anterior
        #    encerrava — 48 das 101 saídas prematuras saíram deste estado, e o
        #    trace ainda dizia que o motivo era o ouro da saída.
        if hp < self.perfil.hp_engajar:
            cura = self._caminho_de_cura(loja, evento, taxa, hp)
            if cura is not None:
                return cura

        # 4. PROGREDIR. O andar é para ser jogado. Não existe mais "já tenho
        #    ouro para a saída, então não preciso lutar": ouro é consequência do
        #    combate, não substituto dele. Se há alvo alcançável e o estado
        #    permite encostar nele, ele encosta.
        if alvo is not None:
            impedimento = self._por_que_nao_engajar(hp, mp)
            if impedimento is None:
                self._descrever_alvos(alvos, alvo)
                extra = (
                    f" Faltam {taxa - hero.coins} de ouro para a saída, o que torna esta luta "
                    "também necessária."
                    if hero.coins < taxa
                    else ""
                )
                return (
                    "lutar",
                    alvo["casa"],
                    f"Nv{hero.get_level()} no andar {self.andar}, {hp:.0%} de HP e {mp:.0%} de "
                    f"MP: dá para lutar. Vou ao & a {alvo['passos']} passos"
                    + (f" (+{alvo['extras']} luta(s) no caminho)" if alvo["extras"] else "")
                    + f".{extra}",
                )

        # 5. INVESTIMENTO. Serviços vêm DEPOIS do combate: gastar antes é gastar
        #    com o ouro e os drops que a luta ainda não deu.
        if loja is not None:
            desvio = self._desvio(loja)
            if desvio is not None and desvio <= DESVIO_ACEITAVEL:
                if hp < HP_SAUDAVEL:
                    return (
                        "loja",
                        loja,
                        f"Loja a {desvio} passos e estou com {hp:.0%} de HP. Vou pela "
                        f"recuperação paga, com {hero.coins} de ouro — mesmo que sobre pouco "
                        f"para a saída de {taxa}.",
                    )
                if self._quer_repor_cura() and hero.coins >= taxa:
                    return (
                        "loja",
                        loja,
                        f"Loja a {desvio} passos. Estou com {self._pocoes()} poção(ões) e a "
                        f"saída de {taxa} já está coberta pelos {hero.coins} de ouro: repor "
                        "cura é o que sustenta continuar lutando nos próximos andares.",
                    )
                if hero.coins >= taxa * FOLGA_PARA_COMPRAR:
                    return (
                        "loja",
                        loja,
                        f"Loja a {desvio} passos de desvio, com {hero.coins} de ouro contra uma "
                        f"saída de {taxa}. Sobra folga para comprar sem perder a reserva.",
                    )
        if ferreiro is not None:
            desvio = self._desvio(ferreiro)
            if desvio is not None and desvio <= DESVIO_ACEITAVEL:
                if hero.coins >= taxa * FOLGA_PARA_COMPRAR and self._tem_peca_para_investir():
                    return (
                        "ferreiro",
                        ferreiro,
                        f"Ferreiro a {desvio} passos, {hero.coins} de "
                        "ouro acima da reserva, e tenho peça equipada onde investir.",
                    )
        if evento is not None:
            desvio = self._desvio(evento)
            tipo = self.mapa.event_type
            if desvio is not None and desvio <= DESVIO_ACEITAVEL:
                if tipo == "fountain" and hp < 0.95:
                    return (
                        "evento",
                        evento,
                        f"Fonte a {desvio} passos e estou com {hp:.0%}. Cura de graça.",
                    )
                if tipo == "altar" and hp >= HP_PARA_ALTAR:
                    return (
                        "evento",
                        evento,
                        f"Altar a {desvio} passos. Com {hp:.0%} de HP dá para pagar o preço dele.",
                    )
                if tipo == "merchant":
                    # O Mercador ABRE A MESMA LOJA, então vale a mesma reserva.
                    if hp < HP_SAUDAVEL or hero.coins >= taxa * FOLGA_PARA_COMPRAR:
                        return (
                            "evento",
                            evento,
                            f"Mercador a {desvio} passos, com {hero.coins} de ouro contra uma "
                            f"saída de {taxa}: dá para gastar sem ficar sem a taxa.",
                        )

        # 6. ENCERRAR — e o motivo tem de ser o REAL.
        #
        #    A versão anterior imprimia "{ouro} de ouro e a saída custa {taxa}:
        #    já dá" mesmo quando o portão que fechou tinha sido o HP. Um trace
        #    que mente sobre a própria causa não serve para revisar decisão
        #    nenhuma, e foi por isso que a auditoria das 60 runs leu errado o
        #    comportamento do bot durante semanas.
        if alvos:
            impedimento = self._por_que_nao_engajar(hp, mp) or (
                "sobraram só alvos que o mapa marca como chefe"
                if alvo is None
                else "nada me impede, mas não há alvo alcançável"
            )
            self._descrever_alvos(alvos, None)
            self.parada = impedimento
            return (
                "saida",
                self.saida,
                f"Encerro o andar com {len(alvos)} monstro(s) ainda no mapa. Motivo real: "
                f"{impedimento}.",
            )
        self.parada = "andar limpo"
        return ("saida", self.saida, "Andar resolvido: não sobrou monstro alcançável.")

    # -- engajar ----------------------------------------------------------

    def _por_que_nao_engajar(self, hp: float, mp: float) -> str | None:
        """None quando dá para encostar no próximo monstro; senão, o que impede.

        Uma condição só, com nome, para que a linha de saída possa citá-la. Note
        o que NÃO está aqui: ouro. Ter a taxa da saída paga nunca foi motivo para
        parar de jogar o andar — era só o lugar onde a policy antiga desligava.
        """
        if hp < self.perfil.hp_engajar:
            return (
                f"HP em {hp:.0%}, abaixo do piso de {self.perfil.hp_engajar:.0%}, e não há "
                "caminho de recuperação neste andar"
            )
        if mp < self.perfil.mp_engajar:
            return f"MP em {mp:.0%}, abaixo do piso de {self.perfil.mp_engajar:.0%}"
        return None

    def _pocoes(self) -> int:
        return sum(
            1
            for i in self.hero.inventory
            if getattr(i, "consumable", False) and getattr(i, "effect_type", None) == "max_hp"
        )

    def _quer_repor_cura(self) -> bool:
        """Está sem estoque de cura para sustentar os próximos andares?

        Compra saudável é a que não fura a reserva da saída — quem garante isso é
        `_orcamento`. Aqui só se pergunta se vale a visita.
        """
        return self._pocoes() < POCOES_PARA_SUSTENTAR

    def _caminho_de_cura(self, loja, evento, taxa: int, hp: float):
        """Como voltar ao piso de engajamento, na ordem do mais barato.

        A poção não está aqui porque o degrau 2b já bebeu, e mais cedo — assim
        que o HP cai abaixo de saudável e ainda há monstro no andar. O que sobra
        são os caminhos que custam passos ou ouro.
        """
        hero = self.hero
        # A poção não aparece aqui: o degrau 2b já bebe antes, e mais cedo.
        if evento is not None and self.mapa.event_type == "fountain":
            desvio = self._desvio(evento)
            if desvio is not None and desvio <= DESVIO_ACEITAVEL:
                return (
                    "evento",
                    evento,
                    f"HP em {hp:.0%} e uma Fonte a {desvio} passos. Cura de graça antes de "
                    "voltar ao mapa.",
                )
        if loja is not None and hero.coins > taxa:
            desvio = self._desvio(loja)
            if desvio is not None and desvio <= DESVIO_ACEITAVEL:
                return (
                    "loja",
                    loja,
                    f"HP em {hp:.0%} e {hero.coins} de ouro contra uma saída de {taxa}: a "
                    "recuperação paga cabe sem furar a reserva, e me devolve o andar.",
                )
        return None

    def _tem_o_que_preservar(self) -> bool:
        """Há progresso que valha a pena tirar vivo daqui?"""
        hero = self.hero
        return (
            hero.get_level() >= 3
            or len(hero.passives) >= 2
            or sum(1 for i in hero.equipment.values() if i) >= 2
        )

    def _sinais_de_risco(self) -> list[str]:
        """Os sinais que pesam na decisão de ENCERRAR A RUN pela Extração.

        Nenhum deles freia combate. Em particular `nível < andar − 1`: ele é
        alerta estrutural e contexto de risco, nunca gate de engajamento. Usá-lo
        como gate fechava o ciclo errado — o herói atrasado parava de lutar, e
        lutar era a única coisa que recuperava o atraso. O andar 5 do warrior
        20260918 (Nv3, 4 combates, 396 XP, quase dois níveis) é exatamente o
        catch-up que um gate desses proibiria.

        O antigo sinal GRAVE morreu junto com o `gap` no mapa: ele dizia
        "nenhum combate acessível é proporcional" lendo o nível dos monstros, que
        o jogador não vê. A proporção agora se julga na ficha, dentro do duelo.
        """
        hero = self.hero
        sinais = []
        hp, mp = _frac_hp(hero), _frac_mp(hero)
        if hp < HP_DE_RISCO:
            sinais.append(f"HP em {hp:.0%}")
        if hero.get_level() < self.andar - 1:
            sinais.append(f"nível {hero.get_level()} contra andar {self.andar}")
        streak = unpaid_streak(hero)
        if streak >= STREAK_DE_RISCO:
            sinais.append(f"{streak} saídas não pagas seguidas")
        if mp < MP_PARA_ENGAJAR:
            sinais.append(f"MP em {mp:.0%}")
        return sinais

    def _avaliar_extracao(self, casa) -> tuple[bool, str]:
        """A Extração é SEMPRE avaliada quando alcançável, e o veredito vai ao trace.

        Limitá-la a HP crítico era tratá-la como botão de pânico: quando o
        gatilho disparava já era tarde. Aqui ela é uma pergunta feita com o andar
        ainda inteiro — e a resposta pode continuar sendo "sigo descendo".
        """
        hero = self.hero
        preserva = self._tem_o_que_preservar()
        sinais = self._sinais_de_risco()
        resumo = (
            f"nível {hero.get_level()}, {len(hero.passives)} passivas, "
            f"{sum(1 for i in hero.equipment.values() if i)} peças"
        )
        if not preserva:
            return False, (
                f"Extração avaliada: ainda não acumulei nada que valha preservar ({resumo}). "
                "Continuo descendo."
            )
        if not sinais:
            return False, (
                f"Extração avaliada: tenho {resumo} para preservar, mas nenhum sinal de risco "
                "— HP, MP, nível e saídas em dia. Continuo descendo."
            )
        if len(sinais) < SINAIS_PARA_EXTRAIR:
            return False, (
                f"Extração avaliada: {sinais[0]}, mas é um sinal só e tenho "
                f"{resumo}. Ainda dá para seguir."
            )
        return True, (
            f"Extração avaliada: {' e '.join(sinais)}. Com {resumo} acumulados, "
            "sair vivo vale mais que o próximo andar."
        )

    def _necessidade_atual(self) -> tuple[int, str]:
        """A necessidade mais alta que está pendente AGORA.

        É o que substitui a avaliação isolada de cada serviço. Uma casa só é
        aberta quando ela atende a necessidade corrente — ou uma igualmente
        urgente. O Ferreiro atende INVESTIMENTO; se a necessidade for
        RECUPERAÇÃO, ele espera, sem que ninguém precise escrever "andar 7".
        """
        hero = self.hero
        hp, mp = _frac_hp(hero), _frac_mp(hero)
        taxa = exit_fee(self.andar)

        if hp < HP_CRITICO:
            return SOBREVIVENCIA, f"HP em {hp:.0%}"
        if hp < self.perfil.hp_engajar:
            return RECUPERACAO, f"HP em {hp:.0%}, abaixo do piso de engajamento"
        if self._alvos_visiveis() and self._por_que_nao_engajar(hp, mp) is None:
            # Havia aqui dois degraus, CONTINUIDADE ("preciso de ouro para a
            # saída") e COMBATE_OPCIONAL ("se sobrar, luto"), e o primeiro
            # desligava quando o ouro chegava. Os dois eram o mesmo ato, e
            # separá-los era o que fazia pagar a saída parecer o fim do andar.
            return PROGREDIR, f"há monstro alcançável, {hp:.0%} de HP e {mp:.0%} de MP"
        if hero.coins >= taxa * FOLGA_PARA_COMPRAR and self._tem_peca_para_investir():
            return INVESTIMENTO, f"{hero.coins} de ouro, com a saída de {taxa} já garantida"
        return ENCERRAR, self._por_que_nao_engajar(hp, mp) or "não há mais alvo alcançável"

    def _tem_peca_para_investir(self) -> bool:
        return any(i is not None for i in self.hero.equipment.values())

    # -- o andar ----------------------------------------------------------

    def _jogar_andar(self, andar: int) -> str:
        """Um andar inteiro. Devolve '', 'morreu' ou 'extraiu'."""
        hero = self.hero
        self.andar = andar
        self.mapa = _setup_dungeon_map(andar, None, andar, hero)
        self.posicao = _pos(self.mapa.player_pos)
        self.saida = _pos(self.mapa.exit_pos)
        self.passos = 0
        self.combates = 0
        self._ultimo_veredito_extracao = ""
        self.extraiu = False
        self.parada = ""

        rolada = progression.floor_essence_multiplier(andar)
        self.essencia = effective_essence(hero, rolada)
        registro = {
            "andar": andar,
            "nivel": hero.get_level(),
            "oferecidos": len(self.mapa.enemies_pos),
            "combates": 0,
            "fugas": 0,
            "pocoes_bebidas": 0,
            "hp_entrada": _frac_hp(hero),
            "mp_entrada": _frac_mp(hero),
            "essencia_sorteada": rolada,
            "essencia_efetiva": self.essencia,
            # A passiva de Essência é lida em `process_post_battle`; guardada
            # aqui para o relatório não ter de reproduzir a conta do core.
            "bonus_passiva": hero.get_passive_bonus("essence_bonus"),
            "streak_antes": unpaid_streak(hero),
            "xp_antes": hero.xp_points,
            "ouro_antes": hero.coins,
            "saida_paga": None,
            "taxa": exit_fee(andar),
            "juros": 0,
        }
        self.por_andar.append(registro)

        self.trace.secao(f"ANDAR {andar}")
        self.trace.diz(
            f"  Estado: HP {hero.get_hp()}/{hero.base_hp}  MP {hero.get_mp()}/{hero.base_mp}  "
            f"Nv{hero.get_level()}  Ouro {hero.coins}  "
            f"Passivas {len(hero.passives)}  Skills {len(hero.skills)}"
        )
        servicos = sorted(self.mapa.features.values())
        self.trace.diz(
            f"  Mapa: {len(self.mapa.enemies_pos)} monstros | "
            f"serviços: {', '.join(servicos) if servicos else 'nenhum'} | "
            f"evento: {self.mapa.event_type or 'nenhum'} | "
            f"saída a {self._alcance(self.saida)[0] if self._alcance(self.saida) else '?'} passos"
        )
        self.trace.diz(
            f"  Essência do andar: sorteada {rolada:.2f}x -> efetiva {self.essencia:.2f}x  "
            f"| taxa de saída: {exit_fee(andar)}"
        )

        # Uma decisão por vez. O teto de voltas subiu porque o bot agora JOGA o
        # andar: cada monstro pode custar uma volta para lutar e outra para se
        # recuperar antes da próxima, e os serviços ainda entram por cima.
        for _ in range(len(self.mapa.enemies_pos) * 2 + 12):
            necessidade, porque = self._necessidade_atual()
            acao, alvo, motivo = self._decidir()
            self.trace.diz(f"  [prioridade: {NOME_DA_NECESSIDADE[necessidade]} — {porque}]")
            self.trace.decisao(motivo)

            # Beber não é ir a lugar nenhum: é o menu de inventário, no mapa.
            if acao == "pocao":
                if not self._beber_pocao():
                    # Não deveria acontecer: `_decidir` só pede poção quando há
                    # uma. Se acontecer, encerrar é melhor que girar no laço.
                    self.parada = "pediu poção e não tinha"
                    break
                continue

            # O destino é escolha da policy; o que acontece em cada casa do
            # caminho é `move_player`. Por isso o laço não "usa" mais o serviço:
            # ele anda até lá, e a casa se resolve ao ser pisada.
            vivo = self._ir_ate(alvo, evitando=(acao != "lutar"))
            if self.extraiu:
                return "extraiu"
            if not vivo:
                return "morreu"
            if acao == "saida":
                break

        # FIM DO ANDAR, na ordem do jogo: saída -> descanso -> juros.
        saida = use_exit(hero, andar)
        hp_antes = hero.get_hp()
        hero.recover(FLOOR_CLEAR_RESTORE_PERCENT)
        juros = pay_interest(hero, andar)
        registro["saida_paga"] = saida.was_paid
        registro["streak_depois"] = saida.streak
        registro["juros"] = juros
        registro["xp_depois"] = hero.xp_points
        registro["ouro_depois"] = hero.coins
        registro["restantes"] = len(self.mapa.enemies_pos)
        registro["nivel_depois"] = hero.get_level()
        registro["motivo_da_parada"] = self.parada or "saiu sem avaliar alvos"
        registro["hp_saida"] = hp_antes / max(1, hero.base_hp)
        registro["mp_saida"] = _frac_mp(hero)
        self.trace.diz(
            f"  Fim do andar: {self.combates} combate(s) de "
            f"{registro['oferecidos']} monstro(s) oferecidos, {registro['fugas']} fuga(s), "
            f"{registro['pocoes_bebidas']} poção(ões) bebida(s), {self.passos} passos. "
            f"Parou porque: {registro['motivo_da_parada']}. "
            f"Saída {'PAGA' if saida.was_paid else 'NÃO PAGA'} ({saida.fee}), "
            f"streak {saida.streak}. Descanso HP {hp_antes}->{hero.get_hp()}. "
            f"Juros +{juros}. Ouro {hero.coins}."
        )
        return ""

    def jogar(self) -> str:
        hero = self.hero
        self.trace.secao("BOT_PADRÃO — uma run")
        self.trace.diz(f"  Seed {self.seed} | classe {hero.get_classname()}")
        self.trace.diz(
            f"  Estado inicial (criação real): nível {hero.get_level()}, "
            f"HP {hero.get_hp()}/{hero.base_hp}, MP {hero.get_mp()}/{hero.base_mp}, "
            f"ouro {hero.coins}, inventário {len(hero.inventory)}, "
            f"equipamento {sum(1 for i in hero.equipment.values() if i)} peças, "
            f"skill '{list(hero.skills.values())[0].name}', {len(hero.passives)} passivas"
        )
        self.reserva_gasta = 0

        for andar in range(1, self.max_andar + 1):
            desfecho = self._jogar_andar(andar)
            if desfecho == "morreu":
                self.fim = f"MORREU no andar {andar}"
                break
            if desfecho == "extraiu":
                self.fim = f"EXTRAIU no andar {andar}"
                break
        else:
            self.fim = f"CHEGOU AO ANDAR {self.max_andar} vivo"

        self.trace.secao("ESTADO FINAL")
        self.trace.diz(f"  {self.fim}")
        self.trace.diz(
            f"  Nível {hero.get_level()} | HP {hero.get_hp()}/{hero.base_hp} | "
            f"Ouro {hero.coins} | Passivas {len(hero.passives)} | Skills {len(hero.skills)} | "
            f"Equipado {sum(1 for i in hero.equipment.values() if i)} peças | "
            f"Mochila {len(hero.inventory)}"
        )
        self.trace.diz(
            "  Combate: "
            + ", ".join(f"{verbo} {n}x" for verbo, n in sorted(self.acoes.items()))
            + f" | MP gasto {self.mp_gasto} de {self.mp_disponivel} disponíveis"
        )
        if self.fatal is not None:
            f = self.fatal
            self.trace.diz(
                f"  Combate fatal: {f['monstro']} (Nv{f['nivel']}, {f['gap']:+d} de mim) no "
                f"andar {f['andar']}, com HP {f['hp_antes']} ({f['hp_frac']:.0%}) e "
                f"MP em {f['mp_frac']:.0%}"
            )
        led = hero.ledger
        self.trace.diz(
            f"  Livro-caixa: ganhou {led.get('gold_earned', 0)}, "
            f"gastou {led.get('gold_spent', 0)}, "
            f"pico {led.get('max_gold_held', 0)}, saídas pagas {led.get('paid_exits', 0)}, "
            f"não pagas {led.get('unpaid_exits', 0)}"
        )
        if self.reserva_gasta:
            self.trace.diz(
                f"  ATENÇÃO: em {self.reserva_gasta} visita(s) a compra "
                "consumiu a reserva da saída."
            )
        return str(self.trace)


def main() -> None:
    parser = argparse.ArgumentParser(description="O bot padrão do ToJ jogando uma run, com trace.")
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--classe", default="warrior", choices=("warrior", "mage", "rogue"))
    parser.add_argument("--max-floor", type=int, default=20)
    parser.add_argument("--perfil", default="conservador", choices=sorted(PERFIS))
    args = parser.parse_args()
    print(BotPadrao(args.classe, args.seed, args.max_floor, PERFIS[args.perfil]).jogar())


if __name__ == "__main__":
    main()
