"""Os contratos da fundação SKILLS V2.

Uma frase resume o que este arquivo protege: **a skill define COMO o personagem
transforma os atributos dele numa ação; o poder vem do personagem.** Tudo o que
está aqui é uma consequência dessa frase, e cada teste existe porque quebrá-la
criaria um segundo sistema de dano ao lado do funil de combate.

A divisão de trabalho, para não se perder:

    carta      -> de quais atributos o golpe nasce (`scaling`) e o peso da ação
                  (`power`); a mira dela (`accuracy_modifier`); o preço (MP,
                  recarga); no máximo UM efeito secundário, do catálogo global
    personagem -> os números: nível, equipamento, gemas, `+N`, efeitos ativos
    motor      -> crítico, encantamento, defesa, mitigação — o funil de sempre

Os testes de aquisição, do pool e da tabela de preços vivem em
`test_skills.py`. Aqui estão as regras do MOTOR.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.content.factories.archetypes import all_archetypes, spawn_by_role  # noqa: E402
from src.content.items import Item, get_all_items  # noqa: E402
from src.content.skill_validator import (  # noqa: E402
    offensive_budget,
    validate,
)
from src.content.skills_loader import (  # noqa: E402
    Requirement,
    ScalingTerm,
    SecondaryEffect,
    SkillCard,
    get_skill_by_id,
    load_skills,
)
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.mechanics import combat as cmb  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.shared.constants import (  # noqa: E402
    HIT_CHANCE_CEIL,
    HIT_CHANCE_FLOOR,
    MAX_SCALING_STATS,
    SKILL_ACCURACY_RANGE,
    SKILL_SCALING_STATS,
)
from src.storage import save_manager  # noqa: E402

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}
DANO = [s for s in load_skills() if s.effect_type == "damage"]
assert DANO, "nenhuma skill de dano carregada: metade deste arquivo não rodaria."


def heroi(classe="Warrior", nivel=10):
    h = CLASSES[classe](f"H{nivel}")
    h.set_level(nivel)
    return h


def carta(**campos):
    """Uma carta V2 mínima, para isolar UMA regra por vez."""
    padrao = dict(
        id="proto",
        name="Protótipo",
        skill_class="Warrior",
        level_required=1,
        mana_cost=10,
        effect_type="damage",
        effect_value=0,
        description="",
        target="enemy",
        duration=0,
        chance=100,
        rarity="Common",
        is_initial=False,
        cooldown=1,
        scaling=(ScalingTerm("st", 1.0),),
        power=1.0,
    )
    padrao.update(campos)
    return SimpleNamespace(**padrao)


# --- 1. o BASE vem do personagem -------------------------------------------


class TestOPoderVemDoPersonagem:
    def test_a_carta_nao_carrega_numero_de_dano(self):
        """`effect_value` não influencia mais o dano de uma skill de dano.

        É o teste que separa a V2 da V1. Enquanto o campo valesse alguma coisa,
        existiriam DOIS jeitos de uma carta ficar mais forte, e só um deles
        passaria pela régua do validador.
        """
        h = heroi()
        base = cmb.skill_damage_base(h, carta(effect_value=0))
        assert cmb.skill_damage_base(h, carta(effect_value=9999)) == base

    def test_dobrar_o_atributo_dobra_o_base(self):
        h = heroi()
        antes = cmb.skill_damage_base(h, carta())
        core.apply_effect(h, "empowered", source_id="teste", intensity=100)
        assert cmb.skill_damage_base(h, carta()) == pytest.approx(2 * antes, rel=0.02)

    def test_o_equipamento_chega_sozinho_ao_base(self):
        """Sem uma linha de equipamento em `combat.py`: a entidade resolve."""
        h = heroi()
        antes = cmb.skill_damage_base(h, carta())
        arma = Item(
            item_id="espada_teste",
            name="Espada de Teste",
            description="",
            slot="Weapon",
            damage_bonus=50,
            price=1,
        )
        h.equip(arma, "Weapon1")
        assert cmb.skill_damage_base(h, carta()) == pytest.approx(1.5 * antes, rel=0.02)

    @pytest.mark.parametrize("skill", DANO, ids=lambda s: s.id)
    def test_toda_carta_de_dano_do_catalogo_escala_com_alguem(self, skill):
        assert skill.scaling, f"{skill.id} não declara de qual atributo o golpe nasce"
        assert skill.power > 0, f"{skill.id} não declara o peso da ação"

    @pytest.mark.parametrize("skill", DANO, ids=lambda s: s.id)
    def test_nenhuma_carta_de_dano_guarda_effect_value(self, skill):
        """Campo morto com valor dentro é armadilha: alguém vai confiar nele."""
        assert not skill.effect_value, (
            f"{skill.id} ainda traz effect_value={skill.effect_value}; "
            "o dano da V2 sai de `scaling` × `power`"
        )


# --- 2. a gramática da escala ----------------------------------------------


class TestAGramaticaDaEscala:
    @pytest.mark.parametrize("skill", load_skills(), ids=lambda s: s.id)
    def test_no_maximo_dois_atributos_somando_um(self, skill):
        assert len(skill.scaling) <= MAX_SCALING_STATS
        if skill.scaling:
            assert sum(t.weight for t in skill.scaling) == pytest.approx(1.0, abs=0.001)
            assert all(t.stat in SKILL_SCALING_STATS for t in skill.scaling)

    def test_tres_atributos_sao_recusados(self):
        v = validate(
            carta(scaling=(ScalingTerm("st", 0.4), ScalingTerm("ag", 0.3), ScalingTerm("mg", 0.3)))
        )
        assert not v.ok and "máximo é 2" in " ".join(v.erros)

    def test_pesos_que_nao_somam_um_sao_recusados(self):
        v = validate(carta(scaling=(ScalingTerm("st", 0.5), ScalingTerm("ag", 0.4))))
        assert not v.ok and "somam" in " ".join(v.erros)

    def test_atributo_inventado_e_recusado(self):
        v = validate(carta(scaling=(ScalingTerm("luck", 1.0),)))
        assert not v.ok and "luck" in " ".join(v.erros)


# --- 3. crítico e acerto são globais ---------------------------------------


class TestCriticoEAcertoSaoDoMotor:
    def test_a_skill_usa_a_mesma_rolagem_de_critico_do_basico(self):
        """Nenhuma carta declara crítico próprio; ele é do funil."""
        for skill in load_skills():
            assert not hasattr(skill, "crit_chance")
            assert not hasattr(skill, "crit_damage")

    def test_o_modificador_de_acerto_da_carta_entra_na_conta_do_motor(self):
        h, m = heroi(), heroi("Rogue", 10)
        neutro = cmb.hit_chance(h, m)
        assert cmb.hit_chance(h, m, -15) == max(HIT_CHANCE_FLOOR, neutro - 15)
        assert cmb.hit_chance(h, m, 15) == min(HIT_CHANCE_CEIL, neutro + 15)

    def test_a_carta_de_mira_ruim_erra_onde_a_carta_neutra_acerta(self):
        """Ponta a ponta: `apply_skill` -> `resolve_physical_attack` -> `hit_chance`.

        O teste acima prova que `hit_chance` sabe somar o modificador. Este
        prova que ele CHEGA lá vindo da carta — sem ele, o campo poderia ficar
        no JSON sem ninguém o ler, que é o defeito mais caro desta base.
        """
        h, m = heroi(), heroi("Rogue", 10)
        m._hp = 10**7
        limite = cmb.hit_chance(h, m)
        # Uma rolagem exatamente no limite acerta; com -20 de mira, erra.
        preciso = cmb.apply_skill(h, m, carta(accuracy_modifier=0), rng=_Rng(limite, 100))
        h.skill_cooldowns.clear()
        m._hp = 10**7
        torto = cmb.apply_skill(h, m, carta(accuracy_modifier=-20), rng=_Rng(limite, 100))
        assert not preciso.strike.was_evaded
        assert torto.strike.was_evaded

    def test_o_ataque_basico_e_a_regua_e_passa_zero(self):
        h, m = heroi(), heroi("Rogue", 10)
        assert cmb.hit_chance(h, m, 0) == cmb.hit_chance(h, m)

    def test_precisao_e_medo_se_cancelam_na_mesma_conta(self):
        """Uma conta só de acerto. Duas rolagens seriam dois sistemas."""
        h = heroi()
        core.apply_effect(h, "precision", source_id="a", intensity=20)
        assert core.accuracy_shift(h) == 20
        core.apply_effect(h, "fear", source_id="b", intensity=20)
        assert core.accuracy_shift(h) == 0

    @pytest.mark.parametrize("skill", load_skills(), ids=lambda s: s.id)
    def test_o_modificador_declarado_cabe_na_faixa(self, skill):
        lo, hi = SKILL_ACCURACY_RANGE
        assert lo <= skill.accuracy_modifier <= hi

    def test_acerto_fora_da_faixa_e_recusado(self):
        v = validate(carta(accuracy_modifier=90))
        assert not v.ok and "accuracy_modifier" in " ".join(v.erros)


# --- 4. preço: toda skill ativa custa --------------------------------------


class TestTodaSkillAtivaCusta:
    @pytest.mark.parametrize("skill", load_skills(), ids=lambda s: s.id)
    def test_mp_e_recarga_sao_obrigatorios(self, skill):
        assert skill.mana_cost_percent > 0 or skill.mana_cost > 0
        assert skill.cooldown > 0

    def test_skill_sem_custo_e_recusada(self):
        assert not validate(carta(mana_cost=0, mana_cost_percent=0)).ok
        assert not validate(carta(cooldown=0)).ok


# --- 5. um efeito principal, no máximo um secundário -----------------------


class TestEfeitos:
    @pytest.mark.parametrize("skill", load_skills(), ids=lambda s: s.id)
    def test_o_secundario_vem_do_catalogo_global(self, skill):
        if skill.secondary is not None:
            assert core.definition(skill.secondary.effect) is not None, (
                f"{skill.id} inventa o efeito {skill.secondary.effect!r}; "
                "a carta escolhe chance e duração, o catálogo diz o que o efeito é"
            )

    def test_secundario_inventado_e_recusado(self):
        v = validate(carta(secondary=SecondaryEffect(effect="explodir", chance=50)))
        assert not v.ok and "explodir" in " ".join(v.erros)

    def test_o_secundario_so_pega_quando_o_golpe_conecta(self):
        """Um golpe esquivado não envenena ninguém."""
        h, m = heroi(), heroi("Mage", 3)
        m._hp = 10**7
        sk = carta(secondary=SecondaryEffect(effect="poison", chance=100, duration=3))
        # Rolagem de acerto acima de qualquer chance: erra.
        cmb.apply_skill(h, m, sk, rng=_Rng(100, 100, 100))
        assert "poison" not in m.active_effects

    def test_o_secundario_pega_quando_o_golpe_conecta(self):
        h, m = heroi(), heroi("Mage", 3)
        m._hp = 10**7
        sk = carta(secondary=SecondaryEffect(effect="poison", chance=100, duration=3))
        cmb.apply_skill(h, m, sk, rng=_Rng(1, 100, 1))
        assert "poison" in m.active_effects

    def test_duas_cartas_diferentes_empilham_e_a_mesma_refresca(self):
        """A fonte do efeito é a CARTA.

        Sem `source_id` por carta, dois debuffs distintos colidiam na mesma
        chave e o segundo apagava o primeiro em silêncio — encontrado pelo teste
        de simetria entre herói e monstro, não por este caminho.
        """
        h, m = heroi(), heroi("Mage", 3)
        a = carta(id="a", effect_type="status", effect_value="weakened", duration=3, chance=100)
        b = carta(id="b", effect_type="status", effect_value="weakened", duration=3, chance=100)
        cmb.apply_skill(h, m, a, rng=_Rng(1))
        uma = core.stacks_of(m, "weakened")
        cmb.apply_skill(h, m, b, rng=_Rng(1))
        assert core.stacks_of(m, "weakened") > uma, "a segunda carta apagou a primeira"
        duas = core.stacks_of(m, "weakened")
        cmb.apply_skill(h, m, a, rng=_Rng(1))
        assert core.stacks_of(m, "weakened") == duas, "a mesma carta empilhou consigo mesma"


# --- 6. requisito de equipamento bloqueia o USO, não a posse ---------------


class TestRequisitoDeEquipamento:
    def _carta_de_escudo(self):
        return carta(id="bloqueio", requires=Requirement(hand_type="shield"))

    def _escudo(self):
        return Item(
            item_id="escudo_teste",
            name="Escudo de Teste",
            description="",
            slot="Weapon",
            defense_bonus=5,
            price=1,
            hand_type="shield",
        )

    def test_aprender_nao_depende_do_equipamento(self):
        """Pegar a carta e ir atrás do escudo é pivotar; o contrário é só reagir."""
        h = heroi()
        h.learn_skill(self._carta_de_escudo())
        assert "bloqueio" in h.active_skill_ids()

    def test_sem_o_equipamento_a_carta_nao_pode_ser_usada(self):
        h = heroi()
        assert not h.can_use_skill(self._carta_de_escudo())

    def test_com_o_equipamento_a_mesma_carta_libera(self):
        h = heroi()
        h.equip(self._escudo(), "Weapon2")
        assert h.can_use_skill(self._carta_de_escudo())

    def test_o_motor_recusa_sem_cobrar_o_turno(self):
        """Recusa sem MP gasto e sem recarga: tentativa impossível não custa."""
        h, m = heroi(), heroi("Mage", 3)
        mp = h.get_mp()
        out = cmb.apply_skill(h, m, self._carta_de_escudo(), rng=random.Random(1))
        assert out.mp_spent == 0
        assert h.get_mp() == mp
        assert not h.skill_cooldowns

    def test_a_carta_continua_visivel_no_deck(self):
        """Não substituir, não esconder: o requisito é um objetivo, não um erro."""
        h = heroi()
        h.learn_skill(self._carta_de_escudo())
        assert "bloqueio" in h.active_skill_ids()
        assert not h.can_use_skill(h.skills[2])

    def test_o_bot_nao_escolhe_uma_carta_que_nao_pode_lancar(self):
        from src.sim.policies import _usable_skills

        h = heroi()
        h.skills[2] = self._carta_de_escudo()
        assert "bloqueio" not in [s.id for s in _usable_skills(h, ("damage",))]
        h.equip(self._escudo(), "Weapon2")
        assert "bloqueio" in [s.id for s in _usable_skills(h, ("damage",))]


# --- 7. o orçamento é medido, e mede o catálogo real -----------------------


class TestOrcamento:
    @pytest.mark.parametrize("skill", load_skills(), ids=lambda s: s.id)
    def test_toda_carta_do_catalogo_passa(self, skill):
        v = validate(skill)
        assert v.ok, str(v)

    def test_o_teto_e_derivado_do_catalogo_e_nao_o_reprova(self):
        """Um teto que reprovasse conteúdo existente seria balancear por validador."""
        maiores = sorted((validate(s).orcamento for s in load_skills()), reverse=True)
        assert maiores[0] <= validate(load_skills()[0]).teto

    def test_a_classe_e_a_unidade_da_medida(self):
        """Ladino e Guerreiro comparáveis: 200% quer dizer o mesmo nos dois.

        `power` sozinho não serviria — a Agilidade do Ladino vale 92 onde a
        Força do Guerreiro vale 191, e a mesma pancada pede quase o dobro de
        `power` nele.
        """
        guerreiro = get_skill_by_id("golpe_poderoso")
        ladino = get_skill_by_id("ataque_furtivo")
        assert ladino.power > guerreiro.power
        assert abs(offensive_budget(ladino) - offensive_budget(guerreiro)) < 60

    def test_classe_inventada_e_recusada(self):
        assert not validate(carta(skill_class="Bardo")).ok


# --- 8. save / load --------------------------------------------------------


class TestSaveLoad:
    def _ida_e_volta(self, tmp_path, monkeypatch, player):
        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
        save_manager.save_game(player, dungeon_level=3, slot=1)
        carregado, _, _ = save_manager.load_game(
            get_all_items(), {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}, slot=1
        )
        return carregado

    def test_deck_vistas_e_recargas_sobrevivem(self, tmp_path, monkeypatch):
        h = heroi()
        for skill in [s for s in load_skills() if s.skill_class == "Warrior"][:3]:
            h.learn_skill(skill)
        h.seen_skill_ids.add("carta_recusada")
        h.skill_cooldowns["golpe_poderoso"] = 2

        depois = self._ida_e_volta(tmp_path, monkeypatch, h)
        assert depois is not None
        assert depois.active_skill_ids() == h.active_skill_ids()
        assert h.seen_skill_ids <= depois.seen_skill_ids
        assert depois.skill_cooldowns == {"golpe_poderoso": 2}

    def test_save_antigo_com_mais_de_quatro_skills_migra_sem_apagar(self, tmp_path, monkeypatch):
        """As 4 primeiras ficam no deck; o excedente vira 'já visto', não sumiço."""
        import json
        import os

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
        antigas = [s.id for s in load_skills() if s.skill_class == "Warrior"][:6]
        assert len(antigas) == 6
        os.makedirs(tmp_path, exist_ok=True)
        with open(save_manager.get_slot_file(2), "w") as f:
            json.dump(
                {
                    "player_class": "Warrior",
                    "player_name": "Velho",
                    "level": 12,
                    "xp": 0,
                    "coins": 0,
                    "inventory": [],
                    "equipment": {},
                    "skills": {str(i + 1): sid for i, sid in enumerate(antigas)},
                    "dungeon_level": 4,
                },
                f,
            )
        carregado, andar, _ = save_manager.load_game(get_all_items(), {"Warrior": Warrior}, slot=2)
        assert carregado is not None, "save antigo deixou de carregar"
        assert andar == 4
        assert carregado.active_skill_ids() == antigas[:4]
        assert set(antigas) <= carregado.seen_skill_ids, "o excedente sumiu em silêncio"

    def test_a_migracao_e_deterministica(self, tmp_path, monkeypatch):
        """Ordem de slot, não ordem do dicionário: o mesmo arquivo, o mesmo deck."""
        import json

        monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path))
        antigas = [s.id for s in load_skills() if s.skill_class == "Warrior"][:6]
        embaralhado = {str(i + 1): sid for i, sid in enumerate(antigas)}
        decks = []
        for ordem in (list(embaralhado.items()), list(reversed(list(embaralhado.items())))):
            with open(save_manager.get_slot_file(3), "w") as f:
                json.dump(
                    {
                        "player_class": "Warrior",
                        "player_name": "Velho",
                        "level": 12,
                        "xp": 0,
                        "coins": 0,
                        "inventory": [],
                        "equipment": {},
                        "skills": dict(ordem),
                        "dungeon_level": 4,
                    },
                    f,
                )
            carregado, _, _ = save_manager.load_game(get_all_items(), {"Warrior": Warrior}, slot=3)
            decks.append(carregado.active_skill_ids())
        assert decks[0] == decks[1] == antigas[:4]


# --- 9. o simulador e o jogo oferecem a mesma coisa ------------------------


def test_o_simulador_usa_a_cadencia_do_jogo():
    """Duas cadências divergentes fariam o bot medir outra progressão de deck."""
    import inspect

    from src.engine import loop
    from src.sim import progression

    for modulo in (loop, progression):
        fonte = inspect.getsource(modulo)
        assert "SKILL_OFFER_LEVEL_INTERVAL" in fonte, (
            f"{modulo.__name__} tem uma cadência de oferta própria"
        )


def test_o_teto_de_deck_e_um_so():
    """O simulador não pode ter o próprio 4.

    `is` entre dois inteiros pequenos passaria por interning mesmo com dois
    literais separados, então a prova é sobre a FONTE: o módulo importa o teto
    do jogo em vez de reescrevê-lo.
    """
    import inspect

    from src.shared.constants import MAX_ACTIVE_SKILLS
    from src.sim import pick_policies

    assert pick_policies.MAX_EQUIPPED_SKILLS == MAX_ACTIVE_SKILLS
    fonte = inspect.getsource(pick_policies)
    assert "MAX_EQUIPPED_SKILLS = MAX_ACTIVE_SKILLS" in fonte


# --- 10. monstro fala a mesma língua ---------------------------------------


CARTAS_DE_MONSTRO = [
    (papel, carta)
    for papel, arquetipo in sorted(all_archetypes().items())
    for carta in arquetipo.skills
]
MONSTRO_DE_DANO = [(p, c) for p, c in CARTAS_DE_MONSTRO if c.effect_type == "damage"]
assert MONSTRO_DE_DANO, "nenhuma carta de dano de monstro: esta seção não estaria medindo nada."


class TestMonstroUsaAMesmaGramatica:
    """Não existe `MonsterSkill`. Existe `SkillCard`, e o monstro usa a mesma.

    O que muda entre herói e monstro é a ORIGEM da carta e os atributos de quem
    a lança. A linguagem e o resolvedor são um só — é o que impede o dano do
    monstro de virar um segundo sistema que ninguém compara com o do jogador.
    """

    @pytest.mark.parametrize("papel,carta", CARTAS_DE_MONSTRO, ids=lambda x: getattr(x, "id", x))
    def test_a_carta_de_monstro_e_a_carta_do_heroi(self, papel, carta):
        assert isinstance(carta, SkillCard)

    @pytest.mark.parametrize("papel,carta", MONSTRO_DE_DANO, ids=lambda x: getattr(x, "id", x))
    def test_escala_valida_e_custo_declarado(self, papel, carta):
        assert carta.scaling, f"{carta.id} não diz de qual atributo o golpe nasce"
        assert len(carta.scaling) <= MAX_SCALING_STATS
        assert sum(t.weight for t in carta.scaling) == pytest.approx(1.0, abs=0.001)
        assert all(t.stat in SKILL_SCALING_STATS for t in carta.scaling)
        assert carta.power > 0
        assert carta.mana_cost > 0 or carta.mana_cost_percent > 0
        assert carta.cooldown > 0
        lo, hi = SKILL_ACCURACY_RANGE
        assert lo <= carta.accuracy_modifier <= hi

    @pytest.mark.parametrize("papel,carta", MONSTRO_DE_DANO, ids=lambda x: getattr(x, "id", x))
    def test_o_dano_sai_dos_atributos_do_proprio_monstro(self, papel, carta):
        """Dobrar a Força do monstro dobra o golpe — como no herói."""
        m = spawn_by_role(papel, 12)
        antes = cmb.skill_damage_base(m, carta)
        assert antes == pytest.approx(
            sum(m.get_stat(t.stat) * t.weight for t in carta.scaling) * carta.power, rel=0.02
        )
        # Sobe os atributos DESTA carta — não um genérico: `mob_rajada` escala
        # com Magia, e empurrar Força nela não provaria nada.
        for termo in carta.scaling:
            setattr(m, f"base_{termo.stat}", int(getattr(m, f"base_{termo.stat}") * 2))
        depois = cmb.skill_damage_base(m, carta)
        assert depois > antes, "o atributo do monstro não chega ao BASE da carta dele"

    @pytest.mark.parametrize("papel,carta", CARTAS_DE_MONSTRO, ids=lambda x: getattr(x, "id", x))
    def test_status_e_secundario_vem_do_catalogo_global(self, papel, carta):
        """Poison é Poison. Nenhuma carta redefine um efeito, de nenhum lado."""
        if carta.effect_type == "status":
            assert core.definition(str(carta.effect_value)) is not None, (
                f"{carta.id} inventa o status {carta.effect_value!r}"
            )
        if carta.secondary is not None:
            assert core.definition(carta.secondary.effect) is not None

    def test_o_monstro_passa_pelo_mesmo_funil_de_dano(self):
        """Mesma função, mesmo acerto, mesmo crítico, mesma defesa, mesma mitigação.

        A prova é por REPRODUÇÃO: o dano que o monstro causa é reconstruído aqui
        com o BASE da carta dele e o mesmo pipeline público que o herói usa. Se
        `combat.py` ganhasse um caminho separado para monstro, os dois números
        deixariam de bater.
        """
        m = spawn_by_role("glass_cannon", 12)
        alvo = heroi("Warrior", 12)
        alvo._hp = 10**7
        carta_mob = next(c for c in m.skills if c.effect_type == "damage")

        base = cmb.skill_damage_base(m, carta_mob, alvo)
        baldes = cmb.damage_modifiers(m, alvo, is_critical=False)
        esperado = cmb._calculate_damage(
            base,
            baldes.flat,
            baldes.mult,
            baldes.xmult,
            alvo.get_df(),
            baldes.mitigation,
        )

        antes = alvo.get_hp()
        resultado = cmb.apply_skill(m, alvo, carta_mob, rng=_Rng(1, 100))
        assert not resultado.strike.was_evaded
        assert antes - alvo.get_hp() == esperado

    def test_a_mira_da_carta_do_monstro_tambem_vale(self):
        """`accuracy_modifier` não é enfeite de herói: é a mesma conta dos dois."""
        m = spawn_by_role("skirmisher", 12)
        alvo = heroi("Warrior", 12)
        rapido = next(c for c in m.skills if c.id == "mob_corte_rapido")
        assert rapido.accuracy_modifier != 0
        neutro = cmb.hit_chance(m, alvo)
        com_carta = cmb.hit_chance(m, alvo, rapido.accuracy_modifier)
        assert com_carta == max(
            HIT_CHANCE_FLOOR, min(HIT_CHANCE_CEIL, neutro + rapido.accuracy_modifier)
        )

    def test_combat_nao_tem_caminho_separado_para_monstro(self):
        """Nenhum `if monster:` dentro do resolvedor. A origem difere, a regra não."""
        import inspect

        fonte = inspect.getsource(cmb)
        for proibido in ("is_boss", "Monster", "isinstance(caster", "isinstance(attacker"):
            assert proibido not in fonte, f"`combat.py` distingue monstro por {proibido!r}"


# --- utilitário ------------------------------------------------------------


class _Rng:
    """RNG de roteiro: devolve os valores na ordem em que foram pedidos."""

    def __init__(self, *valores):
        self._v = list(valores) or [1]
        self._i = 0

    def randrange(self, a, b):
        v = self._v[min(self._i, len(self._v) - 1)]
        self._i += 1
        return v

    def randint(self, a, b):
        return a

    def random(self):
        return 0.0

    def choice(self, seq):
        return seq[0]
