"""A Égide de Mana: a mitigação passiva do Mago, paga em mana.

Não confundir com a skill `Barreira Arcana`, que é um buff de defesa que o
jogador escolhe lançar. As duas são do Mago e as duas reduzem dano.

Cada classe precisa de uma forma de não morrer. O Guerreiro absorve com HP e
defesa, o Ladino evita com agilidade, e o Mago não tinha nenhuma: no nível 4,
760 de HP efetivo contra 749 do Ladino, mas com agilidade 11 contra 38 — a mesma
vida sem a esquiva que a compensa — e apenas +5% de dano sobre o Guerreiro para
pagar por 20% menos vida que ele.

O resultado era que ele morria no andar 4, contra `trash_pair`, `bruiser_solo` e
`skirmisher_solo`, os encontros mais banais do jogo, enquanto Guerreiro e Ladino
chegavam ao 7 e ao 6. A reserva de mana era a compensação escrita no design, e
ela só rendia em luta longa: ele morria antes de a reserva valer alguma coisa.

Estas regras protegem as duas pontas: a barreira precisa funcionar, e precisa
continuar custando.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.mechanics import combat  # noqa: E402
from src.shared.constants import (  # noqa: E402
    MAGIC_SHIELD_ABSORB_PERCENT,
    MAGIC_SHIELD_DAMAGE_PER_MP,
)
from src.sim.harness import make_hero  # noqa: E402


class TestAEgideFunciona:
    def test_o_mago_recebe_menos_dano_que_sem_barreira(self):
        golpe = 400
        com = make_hero("Mage", 10, "naked")
        com._hp = com.base_hp
        sem = make_hero("Mage", 10, "naked")
        sem._hp = sem.base_hp
        sem.magic_shield_percent = 0

        for heroi in (com, sem):
            combat.resolve_physical_attack(
                Warrior("atacante"), heroi, golpe, "", rng=random.Random(0), publish=None
            )
        assert com.get_hp() > sem.get_hp()

    def test_so_o_mago_tem_egide(self):
        """Se todo mundo tivesse, não seria a resposta de ninguém em particular."""
        assert Mage.magic_shield_percent == MAGIC_SHIELD_ABSORB_PERCENT
        assert not getattr(Warrior, "magic_shield_percent", 0)
        assert not getattr(Rogue, "magic_shield_percent", 0)

    def test_absorve_no_maximo_a_fracao_declarada(self):
        """Sem teto, a Égide anularia o golpe inteiro e o Mago viraria o tanque."""
        heroi = make_hero("Mage", 20, "naked")
        golpe = 1000
        passou = combat._absorve_com_egide(heroi, golpe, None)
        absorvido = golpe - passou
        assert absorvido <= golpe * MAGIC_SHIELD_ABSORB_PERCENT / 100 + 1


class TestAEgideCustaMana:
    """Sem custo, isto é redução de dano grátis com outro nome."""

    def test_absorver_consome_mp(self):
        heroi = make_hero("Mage", 10, "naked")
        antes = heroi.get_mp()
        combat._absorve_com_egide(heroi, 400, None)
        assert heroi.get_mp() < antes

    def test_o_preco_segue_a_taxa_declarada(self):
        heroi = make_hero("Mage", 20, "naked")
        antes = heroi.get_mp()
        golpe = 600
        passou = combat._absorve_com_egide(heroi, golpe, None)
        absorvido = golpe - passou
        gasto = antes - heroi.get_mp()
        assert gasto == pytest.approx(absorvido / MAGIC_SHIELD_DAMAGE_PER_MP, abs=1.5)

    def test_mago_sem_mana_fica_sem_egide(self):
        """É a fraqueza que a barreira cria: quem queima a mana dele o desarma.

        Sem esta regra, o Mago teria a mitigação de graça quando ela mais
        importa, e o controlador — que o design marca como o contra dele —
        deixaria de ser uma ameaça.
        """
        heroi = make_hero("Mage", 10, "naked")
        heroi._mp = 0
        golpe = 400
        assert combat._absorve_com_egide(heroi, golpe, None) == golpe

    def test_mana_curta_absorve_so_o_que_paga(self):
        heroi = make_hero("Mage", 20, "naked")
        heroi._mp = 3
        golpe = 1000
        passou = combat._absorve_com_egide(heroi, golpe, None)
        absorvido = golpe - passou
        assert absorvido <= 3 * MAGIC_SHIELD_DAMAGE_PER_MP
        assert heroi.get_mp() >= 0

    def test_a_egide_nunca_zera_o_golpe(self):
        heroi = make_hero("Mage", 20, "naked")
        assert combat._absorve_com_egide(heroi, 10, None) >= 1
