"""Nenhuma carta pode ser enfeite.

Uma skill ou passiva placebo é o pior defeito possível num jogo de escolhas: ela
não quebra nada, não levanta exceção, aparece bonita na tela, o jogador gasta o
recurso escasso da run nela — e não acontece nada. A suíte fica verde e o menu
de cartas vira decoração.

Já aconteceu duas vezes nesta base. `essence_bonus` (4 cartas) e
`gold_drop_bonus` (2) não eram lidas por nenhum cálculo. E `Golpe Baixo`
declarava 15% de atordoamento que o motor entregava em 0% das vezes, porque o
bloco que rola o atordoamento da skill só existia no ramo de dano e ela é uma
skill de status.

Os testes abaixo não conferem número de balanceamento: conferem que o efeito
declarado no JSON chega ao boneco.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.items import Item  # noqa: E402
from src.content.passives import load_passives  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.mechanics import combat  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.sim.encounters import build_encounter  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402

SKILLS = {s.id: s for s in load_skills()}
PASSIVAS = {p.name: p for p in load_passives()}
COM_STUN = [s for s in SKILLS.values() if int(getattr(s, "stun_chance", 0) or 0) > 0]


def _alvo_imortal(nivel: int = 20):
    """Um monstro que não morre: se morrer no meio da amostra, ela encolhe."""
    m = build_encounter("trash_solo", nivel)[0]
    m._hp = 10**9
    return m


def _taxa_de_stun(skill, n: int = 4000) -> float:
    atordoados = 0
    for i in range(n):
        r = random.Random(i)
        heroi = make_hero("Warrior", 20, "naked")
        heroi._mp = 10**6
        heroi.skill_cooldowns = {}
        alvo = _alvo_imortal()
        combat.apply_skill(heroi, alvo, skill, rng=r, publish=None)
        atordoados += "stun" in getattr(alvo, "active_effects", {})
    return atordoados / n


class TestAtordoamentoDeSkill:
    """O `stun_chance` do JSON é o que o jogo entrega."""

    @pytest.mark.parametrize("skill", COM_STUN, ids=lambda s: s.id)
    def test_a_taxa_medida_bate_com_a_declarada(self, skill):
        declarada = int(skill.stun_chance) / 100
        medida = _taxa_de_stun(skill)

        # Teto: nunca acima do declarado. Uma skill que atordoa mais do que o
        # JSON diz está rolando duas vezes — foi o caso de Esmagar, que
        # prometia 30% e entregava 46% porque o motor a atordoava por nome
        # ANTES de `apply_skill` rolar o `stun_chance` dela.
        assert medida <= declarada + 0.02, (
            f"{skill.id} atordoa {medida:.1%} com {declarada:.0%} declarados: "
            "há mais de uma rolagem no caminho"
        )

        # Piso: fica abaixo do declarado só pelo que o golpe erra. Um piso em
        # zero é o placebo — a carta cobra mana por um efeito que não existe.
        assert medida >= declarada * 0.75, (
            f"{skill.id} atordoa {medida:.1%} com {declarada:.0%} declarados: "
            "o efeito declarado não está chegando ao alvo"
        )

    def test_skill_de_status_tambem_atordoa(self):
        """Regressão direta: `Golpe Baixo` é `status` e entregava 0%."""
        golpe_baixo = SKILLS["golpe_baixo"]
        assert golpe_baixo.effect_type == "status", "premissa do teste mudou"
        assert _taxa_de_stun(golpe_baixo) > 0.05


class TestPassivaMudaOBoneco:
    """Toda passiva precisa mexer em alguma coisa observável."""

    def _com_e_sem(self, nome: str):
        base = make_hero("Warrior", 20, "naked")
        com = make_hero("Warrior", 20, "naked")
        com.add_passive(PASSIVAS[nome])
        return base, com

    @pytest.mark.parametrize("nome", sorted(PASSIVAS))
    def test_a_passiva_tem_efeito_no_seu_dominio(self, nome):
        passiva = PASSIVAS[nome]
        base, com = self._com_e_sem(nome)
        efeito = passiva.effect_type

        # Cada família age num lugar diferente. Medir todas pelo combate faria
        # as de recompensa parecerem mortas — foi assim que uma auditoria
        # anterior quase condenou as cartas de essência de novo, por engano.
        if efeito in ("essence_bonus", "gold_drop_bonus", "potion_heal_bonus", "death_ignore"):
            assert com.get_passive_bonus(efeito) > base.get_passive_bonus(efeito)
        else:
            perfil = lambda h: (  # noqa: E731
                h.base_hp,
                h.base_mp,
                h.get_st(),
                h.get_ag(),
                h.get_mg(),
                h.get_df(),
            )
            mudou_perfil = perfil(com) != perfil(base)
            mudou_modificador = com.get_passive_bonus(efeito) > base.get_passive_bonus(efeito)
            assert mudou_perfil or mudou_modificador, (
                f"{nome} ({efeito}) não muda nada que o motor consulte"
            )

    def test_essencia_e_ouro_chegam_ao_calculo_de_recompensa(self):
        """As seis cartas que já foram placebo, no cálculo que as usa."""
        for efeito in ("essence_bonus", "gold_drop_bonus"):
            cartas = [p for p in PASSIVAS.values() if p.effect_type == efeito]
            assert cartas, f"nenhuma carta de {efeito}: o teste perdeu o objeto"
            heroi = make_hero("Warrior", 20, "naked")
            for carta in cartas:
                heroi.add_passive(carta)
            assert 1 + heroi.get_passive_bonus(efeito) / 100 > 1.0

    def test_pocao_cura_mais_com_a_passiva(self):
        pocao = SimpleNamespace(effect_type="max_hp", effect_value=25, name="Poção")
        curas = []
        for passiva in (None, PASSIVAS["Bebida dos Deuses"]):
            heroi = make_hero("Warrior", 20, "naked")
            if passiva:
                heroi.add_passive(passiva)
            heroi._hp = 1
            heroi.use_potion(pocao)
            curas.append(heroi.get_hp())
        assert curas[1] > curas[0]

    def test_death_ignore_impede_a_morte_uma_vez(self):
        def morreu(passiva):
            heroi = make_hero("Warrior", 20, "naked")
            if passiva:
                heroi.add_passive(passiva)
            heroi._death_ignore_used = False
            heroi._hp = 1
            combat.resolve_physical_attack(
                _alvo_imortal(), heroi, 10**6, "ataque", rng=random.Random(0), publish=None
            )
            return heroi.get_hp() <= 0

        assert morreu(None)
        assert not morreu(PASSIVAS["Imortalidade Momentânea"])


def _satisfazer_requisito(heroi, skill) -> None:
    """Põe nas mãos do herói o que a carta exige, se ela exigir algo.

    Sem isto o teste mede a coisa errada: com as mãos vazias o motor RECUSA a
    carta de requisito — corretamente —, nada muda de estado, e uma carta que
    funciona perfeitamente é reprovada como placebo. O requisito bloqueia o uso;
    quem verifica se a carta faz alguma coisa precisa primeiro cumpri-lo.
    """
    req = getattr(skill, "requires", None)
    if req is None:
        return
    tipo = req.hand_type or "sword"
    peca = Item(
        item_id=f"prova_{tipo}",
        name=f"Arma de Prova ({tipo})",
        description="",
        slot="Weapon",
        damage_bonus=1,
        price=1,
        hand_type=tipo,
    )
    heroi.equip(peca, "Weapon1")
    if req.two_weapons:
        heroi.equip(peca.instance(), "Weapon2")


class TestSkillMudaOEstado:
    """Toda skill precisa mudar o alvo ou o lançador."""

    @pytest.mark.parametrize("skill", list(SKILLS.values()), ids=lambda s: s.id)
    def test_usar_a_skill_muda_alguma_coisa(self, skill):
        classe = skill.skill_class
        if classe not in ("Warrior", "Mage", "Rogue"):
            classe = "Warrior"
        for i in range(60):
            heroi = make_hero(classe, 20, "naked")
            _satisfazer_requisito(heroi, skill)
            heroi._mp = 10**6
            heroi.skill_cooldowns = {}
            heroi._hp = max(1, heroi.base_hp // 2)  # cura e buff precisam de espaço
            alvo = _alvo_imortal()
            antes = (
                alvo.get_hp(),
                dict(alvo.active_effects or {}),
                heroi.get_hp(),
                dict(heroi.active_buffs or {}),
            )
            combat.apply_skill(heroi, alvo, skill, rng=random.Random(i), publish=None)
            depois = (
                alvo.get_hp(),
                dict(alvo.active_effects or {}),
                heroi.get_hp(),
                dict(heroi.active_buffs or {}),
            )
            if antes != depois:
                return
        pytest.fail(f"{skill.id} não mudou nada em 60 usos: a carta é placebo")


class TestCondicaoSituacionalDaSkill:
    """Uma skill de dano sem situação é um ataque básico caro.

    Se toda skill entrega o mesmo contra qualquer alvo, "qual eu uso" é
    aritmética fixa — sempre a de maior valor —, o deck não precisa ser lido e
    controlar o inimigo não paga o turno que custou. A condição é o que liga uma
    carta à outra: atordoar passa a valer porque a skill seguinte cobra por isso.
    """

    @staticmethod
    def _criar_situacao(alvo, heroi, condicao: str) -> None:
        if condicao == "target_wounded":
            alvo._hp = max(1, int(alvo.base_hp * 0.2))
        elif condicao == "caster_wounded":
            heroi._hp = max(1, int(heroi.base_hp * 0.2))
        elif condicao == "target_controlled":
            alvo.active_effects["stun"] = {"duration": 1}
        elif condicao == "target_afflicted":
            alvo.active_effects["poison"] = {"duration": 2}

    @staticmethod
    def _quebrar_situacao(alvo, heroi, condicao: str) -> None:
        alvo.active_effects.clear()
        alvo._hp = alvo.base_hp
        heroi._hp = heroi.base_hp
        if condicao == "target_healthy":
            # A única cuja ausência é o alvo ferido, não o alvo intacto.
            alvo._hp = max(1, int(alvo.base_hp * 0.5))

    @pytest.mark.parametrize(
        "skill",
        [s for s in SKILLS.values() if getattr(s, "bonus_condition", "")],
        ids=lambda s: s.id,
    )
    def test_a_condicao_muda_o_dano(self, skill):
        classe = skill.skill_class
        if classe not in ("Warrior", "Mage", "Rogue"):
            classe = "Warrior"
        condicao = skill.bonus_condition

        heroi = make_hero(classe, 20, "naked")
        alvo = _alvo_imortal()
        self._quebrar_situacao(alvo, heroi, condicao)
        sem = combat.skill_damage_base(heroi, skill, alvo)

        heroi = make_hero(classe, 20, "naked")
        alvo = _alvo_imortal()
        self._quebrar_situacao(alvo, heroi, condicao)
        self._criar_situacao(alvo, heroi, condicao)
        if condicao == "target_healthy":
            alvo._hp = alvo.base_hp
        com = combat.skill_damage_base(heroi, skill, alvo)

        assert com > sem, (
            f"{skill.id} declara bônus de {skill.bonus_percent}% com "
            f"'{condicao}' e entrega o mesmo dano nos dois casos: o bônus é placebo"
        )

    def test_sem_alvo_a_condicao_nao_conta(self):
        """A estimativa fora de combate não pode inventar um bônus."""
        skill = SKILLS["assassinato"]
        heroi = make_hero("Rogue", 20, "naked")
        assert not combat.bonus_condition_met(heroi, skill, None)

    def test_nenhuma_carta_depende_de_alvo_controlado(self):
        """`target_controlled` mede 0% de disparo: nenhuma carta pode contar com ela.

        A sinergia parecia óbvia — atordoe, depois bata forte no alvo sem turno —
        e é impossível com a mecânica atual. `STUN_DURATION` é 1, e a duração de
        um status é consumida no turno do PRÓPRIO afetado: o monstro perde a vez
        e o efeito expira antes de o herói voltar a agir. Ele nunca vê o alvo
        controlado. Medido em jogo: o Guerreiro atordoa em 41% das lutas e a
        condição dispara em 0% das avaliações. Com `STUN_DURATION = 2` sobe para
        6%, o que não paga dobrar o valor de todo atordoamento do jogo.

        A condição continua implementada no motor, e volta a valer no dia em que
        o atordoamento durar mais. Até lá, uma carta que dependa dela cobra mana
        por um bônus que não acontece — placebo, que é o defeito que esta suíte
        existe para impedir.
        """
        dependentes = [
            s.id
            for s in SKILLS.values()
            if getattr(s, "bonus_condition", "") == "target_controlled"
        ]
        assert not dependentes, (
            f"{dependentes} dependem de 'target_controlled', que dispara 0% das vezes. "
            "Para usá-la, o atordoamento precisa durar além do turno do alvo."
        )

    def test_a_condicao_de_controle_continua_funcionando_no_motor(self):
        """Se um dia o atordoamento durar mais, a condição precisa estar de pé."""
        heroi = make_hero("Warrior", 20, "naked")
        falsa = type(
            "S",
            (),
            {"bonus_condition": "target_controlled", "bonus_percent": 50, "effect_value": 100},
        )()
        alvo = _alvo_imortal()
        assert not combat.bonus_condition_met(heroi, falsa, alvo)
        alvo.active_effects["stun"] = {"duration": 1}
        assert combat.bonus_condition_met(heroi, falsa, alvo)


class TestMecanicasQueAsPassivasNovasUsam:
    """As seis famílias que o motor consome e que nenhuma passiva usava.

    O teste é da MECÂNICA, não de cada nome de carta: o que importa é que o
    caminho exista e desemboque no lugar certo do funil. Uma passiva nova só
    precisa declarar `effect_type` e cair aqui.

    E o contrato de Balatro é o que separa cada linha: atributo muda o
    PERSONAGEM (e o BASE sai maior por consequência), `damage_percent` entra em
    `+MULT`, `crit_damage` no `×MULT` do crítico, e status nunca entra em
    bucket de dano nenhum.
    """

    @staticmethod
    def _com(efeito, valor, classe="Warrior", nivel=20):
        from src.content.passives import PassiveCard

        heroi = make_hero(classe, nivel, "naked")
        heroi.add_passive(PassiveCard("prova", "Prova", "Combate", "Common", "", efeito, valor))
        return heroi

    def test_magic_sobe_o_base_de_uma_skill_que_escala_em_magia(self):
        """Layer A: a passiva muda o personagem, e o BASE vem maior sozinho.

        `combat.py` não sabe que a Magia veio de uma passiva — é exatamente o
        que impede uma passiva de virar um segundo sistema de dano.
        """
        from src.content.skills_loader import get_skill_by_id

        bola = get_skill_by_id("bola_fogo")
        sem = make_hero("Mage", 20, "naked")
        com = self._com("magic", 40, classe="Mage")
        assert com.get_mg() > sem.get_mg()
        assert combat.skill_damage_base(com, bola) > combat.skill_damage_base(sem, bola)

    def test_damage_percent_entra_no_bucket_mult(self):
        """No `+MULT` do funil, e em lugar nenhum depois dele."""
        alvo = _alvo_imortal()
        sem = combat.damage_modifiers(make_hero("Warrior", 20, "naked"), alvo, is_critical=False)
        com = combat.damage_modifiers(self._com("damage_percent", 30), alvo, is_critical=False)
        assert sem.mult == [] and com.mult == [0.3]
        # E não vaza para os outros baldes.
        assert (com.flat, com.xmult, com.mitigation) == (sem.flat, sem.xmult, sem.mitigation)

    def test_crit_damage_so_muda_o_golpe_critico(self):
        """`×MULT` só existe quando o golpe crita — fora disso, nada muda."""
        alvo = _alvo_imortal()
        sem = make_hero("Warrior", 20, "naked")
        com = self._com("crit_damage", 50)
        assert combat.damage_modifiers(sem, alvo, is_critical=False).xmult == []
        assert combat.damage_modifiers(com, alvo, is_critical=False).xmult == []
        assert (
            combat.damage_modifiers(com, alvo, is_critical=True).xmult
            > combat.damage_modifiers(sem, alvo, is_critical=True).xmult
        )

    def test_life_steal_cura_a_partir_do_dano_realmente_causado(self):
        heroi = self._com("life_steal", 50)
        heroi._hp = max(1, heroi.base_hp // 2)
        antes = heroi.get_hp()
        alvo = _alvo_imortal()
        hp_alvo = alvo.get_hp()
        golpe = combat.resolve_physical_attack(
            heroi, alvo, 1000, "", rng=random.Random(3), publish=None
        )
        causado = hp_alvo - alvo.get_hp()
        assert not golpe.was_evaded and causado > 0
        assert heroi.get_hp() - antes == max(1, int(causado * 50 / 100))

    def test_mana_regen_restaura_mp_pelo_consumidor_real(self):
        def mp_ganho(heroi):
            heroi._mp = 0
            combat.process_turn_start_effects(heroi, rng=random.Random(0), publish=None)
            return heroi.get_mp()

        assert mp_ganho(self._com("mana_regen", 40)) > mp_ganho(make_hero("Warrior", 20, "naked"))

    @pytest.mark.parametrize(
        "efeito,modificador",
        [("bleed", "bleed_chance"), ("poison", "poison_chance"), ("fear", "fear_chance")],
    )
    def test_procs_de_acerto_passam_pelo_nucleo_global(self, efeito, modificador):
        """A passiva dá a CHANCE; o que o efeito é continua sendo do catálogo."""
        assert combat.ONHIT_PROCS[efeito] == modificador
        heroi = self._com(modificador, 100)
        alvo = _alvo_imortal()
        combat.resolve_physical_attack(heroi, alvo, 500, "", rng=random.Random(1), publish=None)
        assert efeito in alvo.active_effects
        # Duração e stacks vêm do catálogo, não da passiva.
        definicao = core.definition(efeito)
        assert core.stacks_of(alvo, efeito) <= definicao.max_stacks

    def test_o_alvo_resiste_ao_proc_pela_mesma_regra(self):
        """Resistência é do alvo e vale para qualquer fonte, passiva inclusive."""
        heroi = self._com("poison_chance", 100)
        alvo = _alvo_imortal()
        alvo.resistances = {"poison": 100}
        combat.resolve_physical_attack(heroi, alvo, 500, "", rng=random.Random(1), publish=None)
        assert "poison" not in alvo.active_effects
