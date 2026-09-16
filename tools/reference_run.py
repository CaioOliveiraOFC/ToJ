"""SMART_REAL: uma run de referência, jogada passo a passo e revisável.

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

from src.content.economy import exit_fee, pay_interest
from src.content.factories import features as feat
from src.content.factories.dungeons import (
    altar_hp_cost,
    apply_altar_blessing,
    apply_fountain_heal,
)
from src.content.floor_exit import effective_essence, use_exit
from src.content.shop import Shop
from src.engine.game_logic import create_player_from_data
from src.engine.loop import _setup_dungeon_map, process_post_battle
from src.engine.map_analysis import campo_de_custo, rota_do_campo
from src.mechanics.battle import run_battle
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
# Acima disto ele se considera saudável para encarar um duelo a mais.
HP_SAUDAVEL = 0.65
# Quantos passos a mais ele aceita andar por um serviço.
DESVIO_ACEITAVEL = 10
# Quanto de ouro além da taxa de saída ele quer ter antes de ir às compras.
FOLGA_PARA_COMPRAR = 1.5
# Altar cobra vida. Só vale com folga real.
HP_PARA_ALTAR = 0.75


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


class RegistroDeOfertas:
    """Captura as ofertas REAIS do level-up, pelo hook que o jogo já chama.

    `progression.on_level_up` gera as três cartas por conta própria e avisa o
    objeto de telemetria por `record_offer`. Gerar uma "amostra" aqui só para
    imprimir mostraria três cartas que NÃO foram as oferecidas — um trace que
    inventa a opção é pior que um trace sem opção nenhuma.

    Aceita qualquer outro atributo porque `_pagar_reroll` escreve contadores de
    reroll no mesmo objeto, e esta classe não quer conhecer a lista deles.
    """

    def __init__(self) -> None:
        object.__setattr__(self, "ofertas", [])
        object.__setattr__(self, "_contadores", {})

    def record_offer(self, kind: str, offered: list, chosen) -> None:
        self.ofertas.append((kind, list(offered), chosen))

    def __getattr__(self, nome):
        return self._contadores.get(nome, 0)

    def __setattr__(self, nome, valor):
        if nome in ("ofertas", "_contadores"):
            object.__setattr__(self, nome, valor)
        else:
            self._contadores[nome] = valor


class RunDeReferencia:
    """Uma run, jogada decisão a decisão."""

    def __init__(self, classe: str, seed: int, max_andar: int = 20) -> None:
        random.seed(seed)
        self.rng = random.Random(seed)
        self.seed = seed
        self.max_andar = max_andar
        # O CAMINHO REAL de criação de personagem. Sem loadout, sem presente:
        # nível 1, sem ouro, sem inventário, sem equipamento, uma skill.
        self.hero = create_player_from_data(classe, "Referencia")
        self.decide = get_policy("smart")
        self.picker = get_pick_policy(DEFAULT_PICK_POLICY)
        self.toggles = Toggles()
        self.trace = Trace()
        self.fim = ""
        self.andar = 0

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

    def _monstro_mais_perto(self):
        visto = self._campo(por_combate=False)[0]
        candidatos = [(visto[c][0], c) for c in self.mapa.enemies_pos if c in visto]
        return min(candidatos)[1] if candidatos else None

    # -- ações ------------------------------------------------------------

    def _ir_ate(self, destino, evitando: bool = True) -> bool:
        """Anda até a casa, resolvendo o que estiver no caminho. False se morreu."""
        if destino == self.posicao:
            monstro = self.mapa.enemies_pos.get(destino)
            return self._duelo(monstro, destino) if monstro is not None else True
        rota, caminho = rota_do_campo(self._campo(evitando), destino, evitando)
        if not rota.alcancavel:
            return True
        for casa in caminho[1:]:
            self.passos += 1
            self.posicao = casa
            monstro = self.mapa.enemies_pos.get(casa)
            if monstro is not None and not self._duelo(monstro, casa):
                return False
        return True

    def _duelo(self, monstro, casa) -> bool:
        """Um combate e todo o pós-combate, pelas funções do jogo."""
        hero = self.hero
        self.mapa.enemies_pos.pop(casa, None)
        self.mapa.grid[casa[0]][casa[1]] = "D"

        hp_antes, mp_antes = hero.get_hp(), hero.get_mp()
        nome = monstro.get_nick_name()
        resultado = run_battle(
            hero, [monstro], lambda h, m, t: self.decide(h, m, t), rng=self.rng, publish=None
        )
        self.combates += 1

        # FUGA NÃO PAGA. `engine/loop.run_fight` devolve ANTES do pós-combate
        # quando o herói foge, e `process_post_battle` decide "venceu" por
        # `player.get_isalive()` — quem fugiu está vivo. Sem esta guarda, fugir
        # rendia XP, ouro e loot cheios.
        if resultado.fled:
            self.trace.diz(f"  Combate: {nome} -> FUGIU | HP {hp_antes}->{hero.get_hp()}")
            return hero.get_isalive() and hero.get_hp() > 0

        # PÓS-COMBATE REAL: `engine.loop.process_post_battle`, a mesma função da
        # Forge Run. Ela dá XP, ouro, loot, gema e sobe o nível.
        xp, venceu, drop, _msgs, moedas, niveis = process_post_battle(
            hero, [monstro], self.essencia, self.andar
        )
        self.trace.diz(
            f"  Combate: {nome} -> {'vitória' if venceu else 'DERROTA'} | "
            f"HP {hp_antes}->{hero.get_hp()} MP {mp_antes}->{hero.get_mp()} | "
            f"+{xp} XP +{moedas} ouro"
        )
        if drop is not None:
            trocou = progression.equip_if_better(hero, drop)
            self.trace.diz(
                f"  Drop: {drop.name} ({getattr(drop, 'rarity', '?')}) — "
                + ("EQUIPOU, é melhor que o que estava no slot" if trocou else "guardou na mochila")
            )
        if niveis:
            self._subir_de_nivel(niveis)
        if not hero.get_isalive() or hero.get_hp() <= 0:
            return False
        return True

    def _subir_de_nivel(self, niveis: int) -> None:
        """As escolhas do level-up, com as opções e a escolha no trace."""
        hero = self.hero
        self.trace.diz(f"  LEVEL UP -> nível {hero.get_level()} ({niveis} nível(is))")
        registro = RegistroDeOfertas()
        progression.on_level_up(
            hero,
            niveis,
            self.rng,
            self.toggles,
            registro,
            self.picker,
            dungeon_level=self.andar,
        )
        for tipo, oferecidas, escolhida in registro.ofertas:
            rotulo = "Passivas" if tipo == "passive" else "Skills"
            self.trace.diz(
                f"  {rotulo} oferecidas: "
                + ", ".join(
                    f"{c.name} [{getattr(c, 'rarity', '?')}/{getattr(c, 'effect_type', '?')}]"
                    for c in oferecidas
                )
            )
            if escolhida is None:
                self.trace.diz("  Escolha: recusou — nenhuma melhora o que já tem")
            else:
                self.trace.diz(
                    f"  Escolha: {escolhida.name} "
                    f"[{getattr(escolhida, 'effect_type', '?')}] — primeira da ordem de "
                    f"preferência da política '{self.picker.name}' presente na oferta"
                )

    # -- serviços ---------------------------------------------------------

    def _usar_loja(self, casa) -> None:
        hero = self.hero
        ouro_antes, hp_antes = hero.coins, hero.get_hp()
        taxa = exit_fee(self.andar)
        self.mapa.take_feature(casa)
        progression.visit_shop(hero, Shop(), self.andar, self.rng, self.toggles, None)
        self.trace.diz(
            f"  Loja: ouro {ouro_antes} -> {hero.coins} | HP {hp_antes} -> {hero.get_hp()}"
        )
        # A política de compra existente NÃO reserva ouro para a saída. Não vou
        # forkar a regra para ensiná-la; vou MEDIR quando isso custa a taxa.
        if ouro_antes >= taxa > hero.coins:
            self.trace.diz(
                f"  !! A compra consumiu a reserva: entrou com {ouro_antes} podendo pagar a "
                f"saída ({taxa}), saiu com {hero.coins}."
            )
            self.reserva_gasta += 1

    def _usar_ferreiro(self, casa) -> None:
        hero = self.hero
        ouro_antes = hero.coins
        self.mapa.take_feature(casa)
        progression.visit_forge(hero, self.andar, self.toggles, None)
        self.trace.diz(f"  Ferreiro: ouro {ouro_antes} -> {hero.coins}")

    def _usar_evento(self, casa) -> bool:
        hero = self.hero
        tipo = self.mapa.event_type
        self.mapa.take_event()
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
            ouro_antes = hero.coins
            progression.visit_shop(hero, Shop(), self.andar, self.rng, self.toggles, None)
            self.trace.diz(f"  Evento Mercador: ouro {ouro_antes} -> {hero.coins}")
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
        monstro = self._monstro_mais_perto()

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

        # 2. Não consigo pagar a saída. Preciso de capital.
        if hero.coins < taxa and monstro is not None and hp >= HP_SAUDAVEL:
            return (
                "lutar",
                monstro,
                f"Tenho {hero.coins} de ouro e a saída custa {taxa}. Estou "
                f"com {hp:.0%} de HP: vale enfrentar o monstro mais perto para pagar.",
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

        # 4. Progressão: estou atrás da masmorra?
        if monstro is not None and hp >= HP_SAUDAVEL and hero.get_level() <= self.andar:
            passos = self._alcance(monstro)
            return (
                "lutar",
                monstro,
                f"Nível {hero.get_level()} no andar {self.andar}: estou "
                f"atrás da curva. Com {hp:.0%} de HP e MP em {mp:.0%}, vale caçar o monstro a "
                f"{passos[0] if passos else '?'} passos.",
            )

        # 5. Sair. O motivo tem de ser o REAL: "já tenho o que precisava" com
        #    ouro abaixo da taxa é mentira, e um trace que mente não serve para
        #    revisar decisão nenhuma.
        if monstro is not None and hero.coins < taxa:
            return (
                "saida",
                self.saida,
                f"Faltam {taxa - hero.coins} de ouro para a saída, mas estou com {hp:.0%} de HP "
                f"— abaixo dos {HP_SAUDAVEL:.0%} que considero seguro para caçar. Prefiro subir "
                "sem pagar a morrer tentando pagar.",
            )
        if monstro is not None:
            return (
                "saida",
                self.saida,
                f"Nível {hero.get_level()} no andar {self.andar}, {hero.coins} de ouro e a saída "
                f"custa {taxa}: já dá. Sobram monstros, mas lutar por lutar só gasta HP.",
            )
        return ("saida", self.saida, "Andar resolvido. Sigo para a saída.")

    def _tem_o_que_preservar(self) -> bool:
        return self.hero.get_level() >= 5 or len(self.hero.passives) >= 3

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

        rolada = progression.floor_essence_multiplier(andar)
        self.essencia = effective_essence(hero, rolada)

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
            acao, alvo, motivo = self._decidir()
            self.trace.decisao(motivo)

            if acao == "saida":
                if not self._ir_ate(self.saida, evitando=True):
                    return "morreu"
                break
            if acao == "extrair":
                if not self._ir_ate(alvo, evitando=True):
                    return "morreu"
                return "extraiu"
            if acao == "lutar":
                if not self._ir_ate(alvo, evitando=False):
                    return "morreu"
                continue
            if not self._ir_ate(alvo, evitando=True):
                return "morreu"
            if acao == "loja":
                self._usar_loja(alvo)
            elif acao == "ferreiro":
                self._usar_ferreiro(alvo)
            elif acao == "evento":
                if not self._usar_evento(alvo):
                    return "morreu"

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
        self.trace.secao("RUN DE REFERÊNCIA — SMART_REAL")
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
    parser = argparse.ArgumentParser(description="Uma run de referência do ToJ, com trace.")
    parser.add_argument("--seed", type=int, default=20260916)
    parser.add_argument("--classe", default="warrior", choices=("warrior", "mage", "rogue"))
    parser.add_argument("--max-floor", type=int, default=20)
    args = parser.parse_args()
    print(RunDeReferencia(args.classe, args.seed, args.max_floor).jogar())


if __name__ == "__main__":
    main()
