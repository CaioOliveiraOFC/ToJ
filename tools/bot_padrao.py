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
from src.shared.constants import FLOOR_CLEAR_RESTORE_PERCENT
from src.sim import progression
from src.sim.pick_policies import DEFAULT_PICK_POLICY, get_pick_policy
from src.sim.policies import get_policy
from src.sim.toggles import Toggles

# --------------------------------------------------------------------------
# Os limiares da política. Poucos, nomeados, e todos explicáveis em uma frase.
# --------------------------------------------------------------------------

# Abaixo disto o personagem está em perigo: nada de procurar briga.
HP_CRITICO = 0.35

# CAÇA OBRIGATÓRIA e CAÇA OPCIONAL são decisões diferentes e não podem dividir
# o mesmo limiar. Obrigatória é "preciso de ouro para a saída": aceita risco
# moderado, porque não lutar também cobra. Opcional é "quero XP": só acontece
# com o personagem claramente confortável, porque recusá-la não custa nada agora.
#
# Nenhuma das duas olha só para HP. MP é munição: um herói cheio de vida e sem
# mana entra no duelo com o ataque básico, que é a forma mais cara de brigar.
HP_PARA_CACA_OBRIGATORIA = 0.50
MP_PARA_CACA_OBRIGATORIA = 0.25
# Os limiares do perfil CONSERVADOR, que é o BOT_PADRÃO de sempre. Continuam
# aqui como nomes para os testes existentes; o perfil é quem os entrega.
HP_PARA_CACA_OPCIONAL = 0.80
MP_PARA_CACA_OPCIONAL = 0.60

# Abaixo disto ele prefere a Loja (recuperação paga) a seguir explorando.
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
SOBREVIVENCIA = 1
EVITAR_DESPROPORCIONAL = 2
RECUPERACAO = 3
CONTINUIDADE = 4
INVESTIMENTO = 5
COMBATE_OPCIONAL = 6

NOME_DA_NECESSIDADE = {
    SOBREVIVENCIA: "sobrevivência",
    EVITAR_DESPROPORCIONAL: "evitar combate desproporcional",
    RECUPERACAO: "recuperação",
    CONTINUIDADE: "continuidade da run",
    INVESTIMENTO: "investimento",
    COMBATE_OPCIONAL: "combate opcional",
}


@dataclass(frozen=True)
class Perfil:
    """Quanto este jogador procura combate NO MAPA. Só isso.

    Nenhum perfil toca em `smart_policy`: dentro do duelo os três usam skill,
    cura, fuga, buff e controle exatamente igual. A variável do experimento é o
    APETITE, e ela mora aqui para que se possa apontar o que mudou.
    """

    nome: str
    # Estado mínimo para aceitar uma luta que só dá XP.
    hp_opcional: float
    mp_opcional: float
    # Só caça opcional quando está atrás da curva de nível?
    #
    # Não existe um campo "continua depois de poder pagar a saída": quem decide
    # isso JÁ é este portão. A caça opcional é avaliada antes do "já dá, saio",
    # então um perfil que passa nos limiares continua lutando por conta própria.
    # Um campo a mais seria configuração morta.
    so_quando_atrasado: bool


CONSERVADOR = Perfil("conservador", 0.80, 0.60, True)
MODERADO = Perfil("moderado", 0.65, 0.40, False)
HARDCORE = Perfil("hardcore", 0.50, 0.25, False)
PERFIS = {p.nome: p for p in (CONSERVADOR, MODERADO, HARDCORE)}

# Quantos níveis acima de mim um duelo ainda é proporcional. Acima disto o
# monstro não é "difícil": é outro patamar, e HP cheio não compensa.
GAP_ACEITAVEL = 2

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
        self.decide = get_policy("smart")
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
        """Os monstros alcançáveis, com o que o JOGADOR consegue ver de cada um.

        Nível está no nome da casa, distância e combates extras saem do mapa.
        Nada de resultado futuro, RNG ou loot: só o que está na tela.
        """
        campo = self._campo(por_combate=True)
        nivel_heroi = self.hero.get_level()
        alvos = []
        for casa, monstro in self.mapa.enemies_pos.items():
            rota, _ = rota_do_campo(campo, casa, True)
            if not rota.alcancavel:
                continue
            nivel = int(getattr(monstro, "level", nivel_heroi))
            alvos.append(
                {
                    "casa": casa,
                    "nome": monstro.get_nick_name(),
                    "nivel": nivel,
                    "gap": nivel - nivel_heroi,
                    "passos": rota.passos,
                    # A rota até ele pode obrigar a lutar com OUTROS pelo
                    # caminho. Um alvo fácil atrás de dois difíceis não é fácil.
                    "extras": max(0, rota.combates - 1),
                }
            )
        return alvos

    def _razoavel(self, alvo: dict) -> bool:
        """Um duelo que não é desproporcional ao personagem."""
        return alvo["gap"] <= GAP_ACEITAVEL

    def _melhor_alvo(self, alvos: list[dict]) -> dict | None:
        """O alvo razoável mais barato: menor defasagem, menos lutas extras, mais perto.

        Nunca "o mais perto". Era assim que um Bandido Nv.9 a 3 passos ganhava de
        um Rato Nv.5 a 7 passos — e matava a run.
        """
        razoaveis = [a for a in alvos if self._razoavel(a)]
        if not razoaveis:
            return None
        return min(razoaveis, key=lambda a: (a["gap"], a["extras"], a["passos"]))

    def _descrever_alvos(self, alvos: list[dict], escolhido: dict | None) -> None:
        """Põe no trace o que estava disponível e o que foi recusado."""
        if not alvos:
            return
        partes = []
        for a in sorted(alvos, key=lambda x: (x["gap"], x["passos"])):
            marca = (
                "ESCOLHIDO"
                if escolhido is not None and a["casa"] == escolhido["casa"]
                else ("recusado (desproporcional)" if not self._razoavel(a) else "descartado")
            )
            partes.append(
                f"{a['nome']} (Nv{a['nivel']}, {a['gap']:+d} de mim, {a['passos']} passos"
                + (f", +{a['extras']} luta(s) no caminho" if a["extras"] else "")
                + f") — {marca}"
            )
        self.trace.diz("  Alvos visíveis: " + " | ".join(partes))

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

        # OBSERVAÇÃO, não decisão: o wrapper conta o que a política devolveu e
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
        )
        self.combates += 1
        self.combates_na_run += 1
        if self.por_andar:
            self.por_andar[-1]["combates"] += 1

        if resultado.fled:
            self.trace.diz(f"  Combate: {nome} -> FUGIU | HP {hp_antes}->{hero.get_hp()}")
        vivo = hero.get_isalive() and hero.get_hp() > 0
        if not vivo:
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
        """
        hero = self.hero
        taxa = exit_fee(self.andar)
        if _frac_hp(hero) < HP_SAUDAVEL:
            return hero.coins, taxa, True
        return max(0, hero.coins - taxa), taxa, False

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

        # 1. Perigo. Em ordem: quem cura primeiro.
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
            if loja is not None and hero.coins > 0 and self._desvio(loja) is not None:
                return (
                    "loja",
                    loja,
                    f"HP em {hp:.0%} e tenho {hero.coins} de ouro. Vou à Loja "
                    "pagar recuperação antes de arriscar o resto do andar.",
                )
            if extracao is not None and self._tem_o_que_preservar():
                if self._alcance(extracao) is not None:
                    return (
                        "extrair",
                        extracao,
                        f"HP em {hp:.0%}, sem cura por perto, e já tenho "
                        f"nível {hero.get_level()} e {len(hero.passives)} passivas para "
                        "preservar. Extrair vale mais que insistir.",
                    )
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

        # 3. CAÇA POR NECESSIDADE. Não é "preciso pagar, logo preciso lutar" —
        #    é "estou sem ouro; vale assumir UMA luta para conseguir pagar?".
        #    Se todos os alvos forem desproporcionais, aceitar a saída não paga é
        #    decisão válida: perder Essência é melhor que perder o personagem.
        if hero.coins < taxa and hp >= HP_PARA_CACA_OBRIGATORIA and mp >= MP_PARA_CACA_OBRIGATORIA:
            if alvo is not None:
                self._descrever_alvos(alvos, alvo)
                return (
                    "lutar",
                    alvo["casa"],
                    f"Faltam {taxa - hero.coins} de ouro para a saída de {taxa}. O melhor alvo é "
                    f"{alvo['nome']} (Nv{alvo['nivel']}, {alvo['gap']:+d} de mim) a "
                    f"{alvo['passos']} passos, e estou com {hp:.0%} de HP e {mp:.0%} de MP. "
                    "Vale a luta.",
                )
            if alvos:
                self._descrever_alvos(alvos, None)
                menor = min(a["gap"] for a in alvos)
                return (
                    "saida",
                    self.saida,
                    f"Faltam {taxa - hero.coins} de ouro, mas o melhor alvo disponível está "
                    f"{menor:+d} níveis de mim. Aceito a saída não paga em vez de arriscar a "
                    "run — Essência se recupera, personagem não.",
                )

        # 3. Serviços, quando o desvio é pequeno e o bolso permite.
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
                    # Sem isto ele era um ralo: na primeira versão desta run,
                    # três visitas levaram 90->31, 148->39 e 183->21, e nas três
                    # o herói chegou ao X sem poder pagar a taxa.
                    if hp < HP_SAUDAVEL or hero.coins >= taxa * FOLGA_PARA_COMPRAR:
                        return (
                            "evento",
                            evento,
                            f"Mercador a {desvio} passos, com {hero.coins} de ouro contra uma "
                            f"saída de {taxa}: dá para gastar sem ficar sem a taxa.",
                        )

        # 5. CAÇA OPCIONAL: só XP. Recusá-la não custa nada agora, então só
        #    acontece com o personagem claramente confortável — em vida E em
        #    munição. Foi exatamente esta decisão, tomada a 67% de HP, que matou
        #    a run anterior no andar 6.
        if (
            alvo is not None
            and hp >= self.perfil.hp_opcional
            and mp >= self.perfil.mp_opcional
            and (not self.perfil.so_quando_atrasado or hero.get_level() <= self.andar)
        ):
            self._descrever_alvos(alvos, alvo)
            return (
                "lutar",
                alvo["casa"],
                f"Nível {hero.get_level()} no andar {self.andar}: estou atrás da curva. Caça "
                f"OPCIONAL, e estou confortável — {hp:.0%} de HP e {mp:.0%} de MP. Escolho "
                f"{alvo['nome']} (Nv{alvo['nivel']}, {alvo['gap']:+d} de mim) a "
                f"{alvo['passos']} passos.",
            )

        # 5. Sair. O motivo tem de ser o REAL: "já tenho o que precisava" com
        #    ouro abaixo da taxa é mentira, e um trace que mente não serve para
        #    revisar decisão nenhuma.
        if alvos and hero.coins < taxa:
            return (
                "saida",
                self.saida,
                f"Faltam {taxa - hero.coins} de ouro para a saída, mas estou com {hp:.0%} de HP "
                f"e {mp:.0%} de MP — abaixo do mínimo ({HP_PARA_CACA_OBRIGATORIA:.0%} / "
                f"{MP_PARA_CACA_OBRIGATORIA:.0%}) até para caça obrigatória. Prefiro subir sem "
                "pagar a morrer tentando pagar.",
            )
        if alvos:
            return (
                "saida",
                self.saida,
                f"Nível {hero.get_level()} no andar {self.andar}, {hero.coins} de ouro e a saída "
                f"custa {taxa}: já dá. Sobram monstros, mas lutar por lutar só gasta HP.",
            )
        return ("saida", self.saida, "Andar resolvido. Sigo para a saída.")

    def _tem_o_que_preservar(self) -> bool:
        """Há progresso que valha a pena tirar vivo daqui?"""
        hero = self.hero
        return (
            hero.get_level() >= 3
            or len(hero.passives) >= 2
            or sum(1 for i in hero.equipment.values() if i) >= 2
        )

    def _sinais_de_risco(self) -> tuple[list[str], str]:
        """(sinais normais, sinal grave). O grave vale por dois.

        Grave é um só, e é estrutural: os combates que este andar oferece são
        desproporcionais ao personagem. Quando isso acontece, não existe jogada
        que recupere o atraso — nem lutar nem fugir —, e é o momento em que um
        jogador olha a casa de Extração com outros olhos.
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
        if mp < MP_PARA_CACA_OBRIGATORIA:
            sinais.append(f"MP em {mp:.0%}")

        grave = ""
        alvos = self._alvos_visiveis()
        if alvos and self._melhor_alvo(alvos) is None:
            pior = min(a["gap"] for a in alvos)
            grave = (
                f"nenhum dos {len(alvos)} combates acessíveis é proporcional — o mais fácil "
                f"está {pior:+d} níveis de mim"
            )
        return sinais, grave

    def _avaliar_extracao(self, casa) -> tuple[bool, str]:
        """A Extração é SEMPRE avaliada quando alcançável, e o veredito vai ao trace.

        Limitá-la a HP crítico era tratá-la como botão de pânico: quando o
        gatilho disparava já era tarde. Aqui ela é uma pergunta feita com o andar
        ainda inteiro — e a resposta pode continuar sendo "sigo descendo".
        """
        hero = self.hero
        preserva = self._tem_o_que_preservar()
        sinais, grave = self._sinais_de_risco()
        resumo = (
            f"nível {hero.get_level()}, {len(hero.passives)} passivas, "
            f"{sum(1 for i in hero.equipment.values() if i)} peças"
        )
        if not preserva:
            return False, (
                f"Extração avaliada: ainda não acumulei nada que valha preservar ({resumo}). "
                "Continuo descendo."
            )
        if grave:
            return True, (
                f"Extração avaliada: SINAL GRAVE — {grave}. Com {resumo} acumulados, insistir "
                "num andar que não me oferece luta possível é entregar a run."
            )
        if not sinais:
            return False, (
                f"Extração avaliada: tenho {resumo} para preservar, mas nenhum sinal de risco "
                "— HP, MP, nível e saídas em dia. Continuo descendo."
            )
        if len(sinais) < SINAIS_PARA_EXTRAIR:
            return False, (
                f"Extração avaliada: {sinais[0]}, mas é um sinal só, sem nada grave, e tenho "
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
        _sinais, grave = self._sinais_de_risco()
        if grave and self._tem_o_que_preservar():
            return EVITAR_DESPROPORCIONAL, grave
        if hp < HP_SAUDAVEL or mp < MP_PARA_CACA_OBRIGATORIA:
            return RECUPERACAO, f"HP em {hp:.0%}, MP em {mp:.0%}"
        if hero.coins < taxa:
            return CONTINUIDADE, f"{hero.coins} de ouro contra uma saída de {taxa}"
        if hero.coins >= taxa * FOLGA_PARA_COMPRAR and self._tem_peca_para_investir():
            return INVESTIMENTO, f"{hero.coins} de ouro, com a saída de {taxa} já garantida"
        return COMBATE_OPCIONAL, "nada urgente"

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

        rolada = progression.floor_essence_multiplier(andar)
        self.essencia = effective_essence(hero, rolada)
        registro = {
            "andar": andar,
            "nivel": hero.get_level(),
            "oferecidos": len(self.mapa.enemies_pos),
            "combates": 0,
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

        # Uma decisão por vez. O teto de voltas é generoso e existe só para a
        # ferramenta não pendurar: cada volta consome um monstro ou um serviço.
        for _ in range(len(self.mapa.enemies_pos) + 8):
            necessidade, porque = self._necessidade_atual()
            acao, alvo, motivo = self._decidir()
            self.trace.diz(f"  [prioridade: {NOME_DA_NECESSIDADE[necessidade]} — {porque}]")
            self.trace.decisao(motivo)

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
        self.trace.diz(
            f"  Fim do andar: {self.combates} combate(s), {self.passos} passos. "
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
