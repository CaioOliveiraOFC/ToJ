"""O bot precisa ser capaz de escolher uma carta que não seja de dano.

Um medidor que só aceita skills de dano não mede um jogo com skills de utilidade:
mede um jogo sem elas, e depois declara mortas as cartas que ele mesmo recusou.
Foi o que aconteceu — o scout classificou nove cartas de status, buff e cura
como "recusadas por toda intenção", que é o seu veredito de carta fraca, quando
a política de escolha nunca tinha conseguido colocá-las no deck.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from src.content.skills_loader import load_skills  # noqa: E402
from src.sim import policies  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.pick_policies import (  # noqa: E402
    MAX_EQUIPPED_SKILLS,
    POLICIES,
    SKILL_PRIORITIES,
)

pytestmark = pytest.mark.balance

SKILLS = {s.id: s for s in load_skills()}


def _deck_de_dano(heroi) -> None:
    """Enche o deck com as skills de dano de maior valor, como o bot fazia."""
    dano = sorted(
        (s for s in SKILLS.values() if s.effect_type == "damage"),
        key=lambda s: -float(s.effect_value),
    )
    heroi.skills = dict(enumerate(dano[:MAX_EQUIPPED_SKILLS], start=1))


class TestTrocaDeSkillNaoMisturaUnidades:
    def test_survival_aceita_cura_no_lugar_de_dano(self):
        """`survival` declara cura como prioridade 1. Precisa conseguir levá-la.

        `effect_value` de uma cura é percentual de HP; o de uma skill de dano é
        percentual de dano. Comparar os dois com `<=` barrava toda cura: a maior
        vale 55, e a pior skill de dano vale 60.
        """
        heroi = make_hero("Mage", 20, "naked")
        _deck_de_dano(heroi)
        cura = SKILLS["cura_menor"]
        assert SKILL_PRIORITIES["survival"][0] == "heal", "premissa do teste mudou"

        nova, slot = POLICIES["survival"].pick_skill(heroi, [cura], random.Random(0))
        assert nova is cura and slot is not None, (
            "a política que prioriza cura não consegue equipar uma cura"
        )

    @pytest.mark.parametrize("tipo", ["heal", "buff", "status"])
    def test_alguma_politica_aceita_cada_tipo(self, tipo):
        """Nenhum tipo de carta pode ser impossível para todas as intenções."""
        candidatas = [s for s in SKILLS.values() if s.effect_type == tipo]
        assert candidatas, f"nenhuma skill de {tipo}: o teste perdeu o objeto"

        aceita = False
        for nome in SKILL_PRIORITIES:
            for carta in candidatas:
                heroi = make_hero("Warrior", 20, "naked")
                _deck_de_dano(heroi)
                nova, _ = POLICIES[nome].pick_skill(heroi, [carta], random.Random(0))
                aceita |= nova is carta
        assert aceita, (
            f"nenhuma das {len(SKILL_PRIORITIES)} intenções consegue equipar uma skill "
            f"de {tipo} — o scout vai chamar essas cartas de fracas sem nunca as ter testado"
        )

    def test_o_grupo_de_controle_troca_ao_acaso(self):
        """`random` é a referência do valor de escolher: não pode filtrar por dano.

        Enquanto ele herdava o filtro por `effect_value`, o "acaso" carregava a
        mesma preferência por dano das políticas deliberadas, e a diferença entre
        os dois media menos do que dizia medir.
        """
        heroi = make_hero("Warrior", 20, "naked")
        _deck_de_dano(heroi)
        status = SKILLS["provocacao"]
        trocou = any(
            POLICIES["random"].pick_skill(heroi, [status], random.Random(seed))[0] is status
            for seed in range(20)
        )
        assert trocou, "a política de controle nunca aceita uma carta que não seja de dano"

    def test_troca_por_carta_melhor_do_mesmo_tipo(self):
        """Dentro do mesmo tipo o valor ainda manda — a correção não pode apagar isso."""
        heroi = make_hero("Warrior", 20, "naked")
        fraca, forte = SKILLS["golpe_poderoso"], SKILLS["esmagar"]
        heroi.skills = {1: fraca}
        for _ in range(MAX_EQUIPPED_SKILLS - 1):
            heroi.skills[max(heroi.skills) + 1] = fraca

        nova, slot = POLICIES["offense"].pick_skill(heroi, [forte], random.Random(0))
        assert nova is forte and slot is not None

        nova, _ = POLICIES["offense"].pick_skill(heroi, [fraca], random.Random(0))
        assert nova is None, "trocar uma carta pela igual desperdiça a escolha"


class TestBotUsaAMelhorOpcaoNaoAPrimeira:
    """`lista[0]` é ordem de inserção do deck, não preferência."""

    def test_cura_escolhe_a_que_cura_mais(self):
        curas = [SKILLS["cura_menor"], SKILLS["drenar_vida"]]
        melhor = max(curas, key=lambda s: float(s.effect_value))
        assert policies._melhor(curas, policies._valor_de_cura) is melhor
        assert policies._melhor(list(reversed(curas)), policies._valor_de_cura) is melhor, (
            "a escolha muda com a ordem da lista: está pegando o primeiro, não o melhor"
        )

    def test_buff_desconta_a_duracao(self):
        """+30 por 2 turnos entrega menos que +20 por 5."""
        curto = type("S", (), {"effect_value": 30, "duration": 2})()
        longo = type("S", (), {"effect_value": 20, "duration": 5})()
        assert policies._valor_de_buff(longo) > policies._valor_de_buff(curto)

    def test_controle_que_rouba_turno_vale_mais(self):
        congelar = SKILLS["raio_congelante"]  # frozen: rouba o turno
        enfraquecer = SKILLS["provocacao"]  # weakened: só reduz dano
        assert policies._valor_de_controle(congelar) > policies._valor_de_controle(enfraquecer)


class TestODeckMontadoEJogavel:
    """A ordem da intenção é estrita demais para ser a única regra.

    `SKILL_PRIORITIES["survival"]` lista `damage` por último. Obedecida ao pé da
    letra, ela montava um deck de quatro buffs — com a mesma carta repetida — e
    o herói passava a depender do ataque básico para matar tudo. Medido: a
    política escolhia 10% de dano, 45% de status e 41% de buff, e a profundidade
    média caía de 9,2 para 6,1 andares. Não era build: era bot quebrado.
    """

    @staticmethod
    def _monta_deck(politica: str, classe: str = "Warrior", rodadas: int = 8):
        from src.content.skills_loader import load_skills

        ofertas = [s for s in load_skills() if s.skill_class == classe]
        heroi = make_hero(classe, 20, "naked")
        heroi.skills = {}
        rng = random.Random(0)
        for _ in range(rodadas):
            nova, slot = POLICIES[politica].pick_skill(heroi, rng.sample(ofertas, 3), rng)
            if nova is not None and slot is not None:
                heroi.skills[slot] = nova
        return list(heroi.skills.values())

    @pytest.mark.parametrize("politica", sorted(SKILL_PRIORITIES))
    def test_o_deck_tem_como_matar(self, politica):
        from src.sim.pick_policies import MIN_DAMAGE_SKILLS

        deck = self._monta_deck(politica)
        com_dano = sum(1 for s in deck if s.effect_type == "damage")
        assert com_dano >= MIN_DAMAGE_SKILLS, (
            f"{politica} montou um deck com {com_dano} skill(s) de dano: {[s.name for s in deck]}"
        )

    @pytest.mark.parametrize("politica", sorted(SKILL_PRIORITIES))
    def test_o_deck_nao_repete_carta(self, politica):
        deck = self._monta_deck(politica)
        ids = [s.id for s in deck]
        assert len(ids) == len(set(ids)), (
            f"{politica} levou carta repetida: {[s.name for s in deck]} — "
            "o segundo exemplar não acrescenta nada"
        )

    def test_a_intencao_ainda_manda_depois_do_minimo(self):
        """A garantia de dano não pode transformar toda política em 'só dano'."""
        deck = self._monta_deck("survival")
        assert any(s.effect_type != "damage" for s in deck), (
            "survival deveria levar utilidade depois de garantir o dano mínimo"
        )


class TestODeckCobreMaisDeUmTipo:
    """Quatro cartas do tipo favorito não é build, é a ordem da intenção obedecida.

    `survival` lista `status` atrás de cura e buff. O Mago começa com uma de
    cada, então o deck enchia antes de sobrar espaço para controle — e ele
    terminava a run sem nunca poder congelar ninguém, apesar de o documento de
    design chamá-lo de Controlador.

    Não era preferência: medido, o deck com a carta que ele nunca escolhia caía
    de 14% para 6% de mortes contra o chefe do andar 5, e de 28% para 22% contra
    o inimigo de dano alto do andar 6. A carta era boa; a regra de montagem é que
    não a alcançava.
    """

    @staticmethod
    def _monta_deck(politica: str, classe: str, rodadas: int = 10):
        from src.content.skills_loader import load_skills

        ofertas = [s for s in load_skills() if s.skill_class == classe]
        heroi = make_hero(classe, 20, "naked")
        heroi.skills = {}
        rng = random.Random(0)
        for _ in range(rodadas):
            nova, slot = POLICIES[politica].pick_skill(heroi, rng.sample(ofertas, 3), rng)
            if nova is not None and slot is not None:
                heroi.skills[slot] = nova
        return list(heroi.skills.values())

    @pytest.mark.parametrize("classe", ["Warrior", "Mage", "Rogue"])
    @pytest.mark.parametrize("politica", sorted(SKILL_PRIORITIES))
    def test_o_deck_tem_mais_de_um_tipo(self, politica, classe):
        deck = self._monta_deck(politica, classe)
        tipos = {s.effect_type for s in deck}
        assert len(tipos) >= 2, (
            f"{politica}/{classe} montou um deck de um tipo só ({tipos}): {[s.name for s in deck]}"
        )

    def test_o_mago_alcanca_o_proprio_controle(self):
        """O arquétipo declarado precisa ser alcançável pela regra de montagem."""
        from src.shared.effects import TURN_SKIPPING_STATUSES

        alcancou = False
        for politica in SKILL_PRIORITIES:
            deck = self._monta_deck(politica, "Mage")
            alcancou |= any(
                str(getattr(s, "effect_value", "")) in TURN_SKIPPING_STATUSES for s in deck
            )
        assert alcancou, (
            "nenhuma intenção monta um Mago com controle que rouba turno — "
            "o 'Controlador' do design não controla nada"
        )
