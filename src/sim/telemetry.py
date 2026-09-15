"""Telemetria por sistema durante uma run simulada.

Saber que uma classe chega ao andar 8 não diz qual sistema a levou até lá. Sem
atribuição, "esta skill é forte demais" e "esta passiva é inútil" continuam
sendo palpite, e a única forma de responder é desligar coisas uma a uma — o que
custa minutos.

Este coletor registra, durante a run que já está rodando, o que cada sistema
efetivamente entregou: dano por skill e por mana, quantas vezes cada passiva foi
oferecida e escolhida, de onde veio o equipamento, quanto o ouro comprou, quanto
a Essência multiplicou e o que os eventos aleatórios fizeram.

É atribuição, não causalidade: um número alto aqui aponta o suspeito. Quem
condena é a ablação em `sim/scout.py`, que desliga o sistema e mede o delta.

Definições econômicas
---------------------
Duas leituras da economia já saíram confusas por falta destas definições — "55%
utilizado" e "54% parado" foram publicados lado a lado com denominadores
diferentes, como se somassem 100%. Não somam: o primeiro é razão de FLUXO, o
segundo é ESTOQUE sobre fluxo. As três categorias são distintas e não se
misturam:

    gold_from_primary_income = combate
        Riqueza NOVA. É o único ouro que o jogo cria do nada.

    total_liquid_gold_inflow = combate + juros + venda
        Ouro líquido que entrou nas mãos do jogador. Venda entra aqui e NÃO em
        `primary_income`: vender é converter item em ouro, não criar riqueza —
        o item sai do inventário na mesma transação. Separar as duas é o que
        permite distinguir "o jogador gasta pouco" de "os juros estão
        imprimindo dinheiro demais".

    gold_spent = equipamento + consumível + recuperação
        Ouro MOVIMENTADO: o que virou decisão.

    gold_utilization_rate = gold_spent / total_liquid_gold_inflow
        Razão de fluxo. O denominador é o inflow líquido, sempre.

    carrying_balance = saldo ao fim do andar
        ESTOQUE. Média por andar observado, nunca percentual de fluxo.

    interest_payments = pagamentos de juros MAIORES QUE ZERO
        Andar concluído com saldo zero não conta. Contá-lo mediria "quantos
        andares foram concluídos", que já se sabe por `floors_observed`, e
        esconderia o que a métrica existe para mostrar: em quantos andares o
        jogador tinha de fato capital rendendo.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field

# Faixas de cinco andares, geradas sem teto: a masmorra é infinita, e um limite
# superior aqui repetiria o erro do `shop_max_floor`, que fazia a loja sumir no
# andar 16 porque alguém escreveu 15 quando o jogo acabava no 20.
BAND_SIZE = 5


def band_index(floor: int) -> int:
    return (max(1, int(floor)) - 1) // BAND_SIZE


def band_label(index: int) -> str:
    return f"{index * BAND_SIZE + 1}-{(index + 1) * BAND_SIZE}"


@dataclass
class BandTotals:
    """A economia de uma faixa de profundidade.

    `floors_observed` e `runs_observed` não são enfeite. A faixa 21-25 só contém
    quem sobreviveu até lá — os melhores equipados, os que gastaram bem —, e ler
    a média dela ao lado da faixa 1-5, onde está a população inteira, compara
    dois grupos diferentes como se fossem o mesmo. Nenhuma média daqui deve ser
    lida sem o tamanho da amostra ao lado.
    """

    floors_observed: int = 0
    runs_observed: int = 0
    gold_from_combat: int = 0
    gold_from_interest: int = 0
    gold_from_sales: int = 0
    gold_spent_on_gear: int = 0
    gold_spent_on_consumables: int = 0
    gold_spent_on_recovery: int = 0
    gold_spent_on_shop_reroll: int = 0
    gold_spent_on_skill_reroll: int = 0
    gold_spent_on_passive_reroll: int = 0
    rerolls: int = 0
    # Reroll: comprar outra amostra do RNG. Separado por CONTEXTO porque as três
    # ofertas competem pelo mesmo ouro e a pergunta do balanceamento é em qual
    # delas o jogador queima o capital.
    gold_spent_on_shop_reroll: int = 0
    gold_spent_on_skill_reroll: int = 0
    gold_spent_on_passive_reroll: int = 0
    rerolls: int = 0
    purchases: int = 0
    items_sold: int = 0
    interest_payments: int = 0
    # Soma dos saldos ao fim de cada andar da faixa; a média sai na serialização.
    carrying_balance_sum: int = 0

    @property
    def gold_spent_on_rerolls(self) -> int:
        return (
            self.gold_spent_on_shop_reroll
            + self.gold_spent_on_skill_reroll
            + self.gold_spent_on_passive_reroll
        )

    @property
    def gold_spent_total(self) -> int:
        return (
            self.gold_spent_on_gear
            + self.gold_spent_on_consumables
            + self.gold_spent_on_recovery
            + self.gold_spent_on_rerolls
        )

    @property
    def total_liquid_gold_inflow(self) -> int:
        return self.gold_from_combat + self.gold_from_interest + self.gold_from_sales

    @property
    def gold_utilization_rate(self) -> float:
        entrada = self.total_liquid_gold_inflow
        return (self.gold_spent_total / entrada) if entrada else 0.0

    @property
    def carrying_balance(self) -> float:
        """ESTOQUE: saldo médio ao fim de um andar desta faixa."""
        return (self.carrying_balance_sum / self.floors_observed) if self.floors_observed else 0.0

    def to_dict(self) -> dict:
        return {
            "floors_observed": self.floors_observed,
            "runs_observed": self.runs_observed,
            "gold_from_combat": self.gold_from_combat,
            "gold_from_interest": self.gold_from_interest,
            "gold_from_sales": self.gold_from_sales,
            "total_liquid_gold_inflow": self.total_liquid_gold_inflow,
            "gold_spent_total": self.gold_spent_total,
            "gold_spent_on_gear": self.gold_spent_on_gear,
            "gold_spent_on_consumables": self.gold_spent_on_consumables,
            "gold_spent_on_recovery": self.gold_spent_on_recovery,
            "gold_spent_on_rerolls": self.gold_spent_on_rerolls,
            "gold_spent_on_shop_reroll": self.gold_spent_on_shop_reroll,
            "gold_spent_on_skill_reroll": self.gold_spent_on_skill_reroll,
            "gold_spent_on_passive_reroll": self.gold_spent_on_passive_reroll,
            "rerolls": self.rerolls,
            "purchases": self.purchases,
            "items_sold": self.items_sold,
            "interest_payments": self.interest_payments,
            "carrying_balance": round(self.carrying_balance, 1),
            "gold_utilization_rate": round(self.gold_utilization_rate, 4),
        }


@dataclass
class RunTelemetry:
    """Acumulador de contribuição por sistema, ao longo de muitas runs."""

    runs: int = 0

    # --- Skills ---
    skill_uses: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_damage: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_mp: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_offered: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    skill_picked: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    basic_damage: int = 0

    # --- Passivas ---
    passive_offered: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    passive_picked: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # --- Equipamento e economia ---
    items_from_loot: int = 0
    items_equipped_from_loot: int = 0
    items_bought: int = 0
    items_equipped_from_shop: int = 0
    gold_from_combat: int = 0
    gold_spent_on_gear: int = 0
    gold_spent_on_consumables: int = 0
    gold_spent_on_recovery: int = 0
    gold_spent_on_shop_reroll: int = 0
    gold_spent_on_skill_reroll: int = 0
    gold_spent_on_passive_reroll: int = 0
    rerolls: int = 0
    gold_from_sales: int = 0
    gold_from_interest: int = 0
    gold_unspent: int = 0
    # Permadeath: ouro não gasto no fim da run é ouro que nunca comprou nada.
    # Separar o que sobrou vivo do que morreu junto é o que distingue "o jogador
    # está guardando para uma compra" de "a economia não tinha o que oferecer".
    gold_lost_on_death: int = 0
    max_gold_held: int = 0
    interest_payments: int = 0
    recovery_purchases: int = 0
    items_sold: int = 0
    equipped_by_slot: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    final_power_naked: list[float] = field(default_factory=list)
    final_power_equipped: list[float] = field(default_factory=list)

    # --- Consumíveis ---
    consumables_used: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # --- Essência ---
    essence_rolls: list[float] = field(default_factory=list)
    xp_base: int = 0
    xp_after_essence: int = 0

    # --- Eventos aleatórios ---
    event_counts: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    fountain_healed: int = 0
    altar_hp_paid: int = 0
    altar_deaths: int = 0
    event_declined: dict[str, int] = field(default_factory=lambda: defaultdict(int))

    # --- Economia por faixa de profundidade ---
    by_band: dict[int, BandTotals] = field(default_factory=lambda: defaultdict(BandTotals))

    # --- Combate ---
    battles: int = 0
    turns: int = 0
    # Runs que terminaram com o herói morto. Separar vitória de derrota é o que
    # permite perguntar "o que ele estava fazendo quando morreu" — a pergunta
    # mais útil num jogo de permadeath.
    defeats: int = 0

    @property
    def purchases(self) -> int:
        """Quantas transações de compra a run fez, de qualquer tipo.

        Derivada, não contada à parte: um contador próprio ficaria em zero no dia
        em que alguém acrescentasse um jeito novo de gastar e esquecesse de
        incrementá-lo — e um zero em telemetria não parece defeito, parece dado.
        """
        return self.items_bought + self.recovery_purchases

    @property
    def gold_spent_on_rerolls(self) -> int:
        return (
            self.gold_spent_on_shop_reroll
            + self.gold_spent_on_skill_reroll
            + self.gold_spent_on_passive_reroll
        )

    @property
    def gold_spent(self) -> int:
        """Todo ouro que saiu do jogador, por destino."""
        return (
            self.gold_spent_on_gear
            + self.gold_spent_on_consumables
            + self.gold_spent_on_recovery
            + self.gold_spent_on_rerolls
        )

    @property
    def gold_from_primary_income(self) -> int:
        """Riqueza nova: só recompensa de combate. Nem juros, nem venda."""
        return self.gold_from_combat

    @property
    def total_liquid_gold_inflow(self) -> int:
        """Todo ouro líquido que entrou nas mãos do jogador. Ver o cabeçalho."""
        return self.gold_from_combat + self.gold_from_interest + self.gold_from_sales

    @property
    def gold_utilization_rate(self) -> float:
        """Fatia do inflow líquido que virou decisão, em vez de saldo parado.

        É a métrica-chave desta fase: se ela é baixa, o ouro não está comprando
        opção nenhuma — ou porque não há o que comprar, ou porque o preço está
        desconectado da renda. Não tem meta ainda; existe para ser observada.
        """
        entrada = self.total_liquid_gold_inflow
        return (self.gold_spent / entrada) if entrada else 0.0

    def start_run(self) -> None:
        """Zera o retrato do livro-caixa: uma run nova começa com herói novo."""
        self._ledger_anterior = {}
        self._bandas_desta_run = set()

    def record_floor(self, floor: int, ledger: dict, coins: int) -> None:
        """Credita à faixa deste andar o que o livro-caixa do herói mudou nele.

        Por diferença do livro, e não por contadores próprios: o livro já é
        escrito em `earn_coins`/`spend_coins`, por onde TODO o ouro do jogo
        passa, e já vem separado por origem e destino. A atribuição sai correta
        por construção, e uma fonte de ouro nova entra na telemetria por faixa
        sem ninguém precisar lembrar de incrementar coisa nenhuma aqui.
        """
        anterior = getattr(self, "_ledger_anterior", {})

        def delta(chave: str) -> int:
            return int(ledger.get(chave, 0)) - int(anterior.get(chave, 0))

        indice = band_index(floor)
        faixa = self.by_band[indice]
        faixa.floors_observed += 1
        faixa.gold_from_combat += delta("gold_from_combat")
        faixa.gold_from_interest += delta("gold_from_interest")
        faixa.gold_from_sales += delta("gold_from_sale")
        faixa.gold_spent_on_gear += delta("gold_spent_on_gear")
        faixa.gold_spent_on_consumables += delta("gold_spent_on_consumable")
        faixa.gold_spent_on_recovery += delta("gold_spent_on_recovery")
        faixa.gold_spent_on_shop_reroll += delta("gold_spent_on_shop_reroll")
        faixa.gold_spent_on_skill_reroll += delta("gold_spent_on_skill_reroll")
        faixa.gold_spent_on_passive_reroll += delta("gold_spent_on_passive_reroll")
        faixa.purchases += delta("purchases")
        faixa.items_sold += delta("items_sold")
        faixa.interest_payments += delta("interest_payments")
        faixa.carrying_balance_sum += int(coins)

        bandas = getattr(self, "_bandas_desta_run", set())
        if indice not in bandas:
            bandas.add(indice)
            faixa.runs_observed += 1
        self._bandas_desta_run = bandas

        self._ledger_anterior = dict(ledger)

    def record_battle(self, outcome) -> None:
        """Soma o que uma batalha entregou, por skill e por consumível."""
        self.battles += 1
        self.turns += outcome.turns
        self.basic_damage += outcome.basic_damage
        for skill_id, count in outcome.skill_uses.items():
            self.skill_uses[skill_id] += count
        for skill_id, dano in outcome.skill_damage.items():
            self.skill_damage[skill_id] += dano
        for skill_id, mana in outcome.skill_mp.items():
            self.skill_mp[skill_id] += mana
        for efeito, count in outcome.items_by_effect.items():
            self.consumables_used[efeito] += count

    def record_offer(self, kind: str, offered: list, chosen) -> None:
        """Registra uma escolha oferecida ao jogador e o que ele levou.

        A taxa de escolha quando oferecida separa a carta que ninguém quer da
        carta que raramente aparece — duas causas muito diferentes para o mesmo
        sintoma de "quase nunca vista".
        """
        alvo_oferta = self.skill_offered if kind == "skill" else self.passive_offered
        alvo_escolha = self.skill_picked if kind == "skill" else self.passive_picked
        for carta in offered:
            alvo_oferta[carta.id] += 1
        if chosen is not None:
            alvo_escolha[chosen.id] += 1

    def to_dict(self) -> dict:
        """Serializa para JSON, convertendo os defaultdict em dict comum."""
        return {
            "runs": self.runs,
            "battles": self.battles,
            "turns": self.turns,
            "defeats": self.defeats,
            "skills": {
                "uses": dict(self.skill_uses),
                "damage": dict(self.skill_damage),
                "mp": dict(self.skill_mp),
                "offered": dict(self.skill_offered),
                "picked": dict(self.skill_picked),
                "basic_damage": self.basic_damage,
            },
            "passives": {
                "offered": dict(self.passive_offered),
                "picked": dict(self.passive_picked),
            },
            "equipment": {
                "items_from_loot": self.items_from_loot,
                "items_equipped_from_loot": self.items_equipped_from_loot,
                "items_bought": self.items_bought,
                "items_equipped_from_shop": self.items_equipped_from_shop,
                "equipped_by_slot": dict(self.equipped_by_slot),
                "power_naked_sum": sum(self.final_power_naked),
                "power_equipped_sum": sum(self.final_power_equipped),
                "power_samples": len(self.final_power_naked),
            },
            "economy": {
                # Nomes explícitos: `gold_earned` significava "só combate" aqui
                # e "tudo" no livro-caixa do herói. Dois denominadores com o
                # mesmo nome é como saiu a leitura de "55% utilizado, 54%
                # parado" — números que nunca deveriam ter sido lidos juntos.
                "gold_from_combat": self.gold_from_combat,
                "gold_from_primary_income": self.gold_from_primary_income,
                "total_liquid_gold_inflow": self.total_liquid_gold_inflow,
                "gold_spent": self.gold_spent,
                "gold_spent_on_gear": self.gold_spent_on_gear,
                "gold_spent_on_rerolls": self.gold_spent_on_rerolls,
                "gold_spent_on_shop_reroll": self.gold_spent_on_shop_reroll,
                "gold_spent_on_skill_reroll": self.gold_spent_on_skill_reroll,
                "gold_spent_on_passive_reroll": self.gold_spent_on_passive_reroll,
                "rerolls": self.rerolls,
                "gold_spent_on_consumables": self.gold_spent_on_consumables,
                "gold_spent_on_recovery": self.gold_spent_on_recovery,
                "gold_from_sales": self.gold_from_sales,
                "gold_from_interest": self.gold_from_interest,
                "gold_unspent": self.gold_unspent,
                "gold_lost_on_death": self.gold_lost_on_death,
                "max_gold_held": self.max_gold_held,
                "purchases": self.purchases,
                "interest_payments": self.interest_payments,
                "recovery_purchases": self.recovery_purchases,
                "items_dropped": self.items_from_loot,
                "items_equipped": self.items_equipped_from_loot + self.items_equipped_from_shop,
                "items_sold": self.items_sold,
                "gold_utilization_rate": self.gold_utilization_rate,
            },
            "economy_by_band": {
                band_label(indice): faixa.to_dict()
                for indice, faixa in sorted(self.by_band.items())
            },
            "consumables": dict(self.consumables_used),
            # Somas e contagens, nunca médias: o agregador soma bloco a bloco,
            # e somar três médias produz um número sem significado — foi assim
            # que a Essência apareceu com média 4,02 num intervalo de 0,5 a 3,0.
            "essence": {
                "rolls": len(self.essence_rolls),
                "sum": sum(self.essence_rolls),
                "xp_base": self.xp_base,
                "xp_after": self.xp_after_essence,
            },
            "events": {
                "counts": dict(self.event_counts),
                "declined": dict(self.event_declined),
                "fountain_healed": self.fountain_healed,
                "altar_hp_paid": self.altar_hp_paid,
                "altar_deaths": self.altar_deaths,
            },
        }
