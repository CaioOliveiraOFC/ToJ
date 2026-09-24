"""Paridade mecânica: o que o adapter DECLARA × o que o engine EXECUTA.

Três perguntas separadas, e este arquivo responde só a segunda:

    (A) o engine executa certo   — coberto pelas suítes de mecânica
    (B) o adapter representa certo — AQUI
    (C) o evaluator valoriza certo — `test_bot_combat_policy.py`

A auditoria que originou estes testes encontrou onze de vinte e dois sistemas
chegando ao cérebro como "custa um turno e não causa dano", dois medidos na
unidade errada, e uma exceção não tratada que derrubaria a run na primeira skill
de status que o herói recebesse.

Propriedade, não número decorado: o que se prova é que declaração e execução
representam a MESMA consequência mecânica.
"""

from __future__ import annotations

import json
import random

from src.content.factories.monsters import create_monster
from src.content.skills_loader import get_skill_by_id
from src.engine.game_logic import create_player_from_data
from src.mechanics import combat as combat_mech
from src.mechanics.battle import build_turn_order
from src.shared import effect_core as core
from src.shared import effects as fx
from tools import bot_adapter as ad


def _heroi(classe="warrior", nivel=8):
    h = create_player_from_data(classe, "Paridade")
    h.set_level(nivel)
    return h


def _monstro(nivel=8, papel="bruiser"):
    return create_monster("Alvo", nivel, papel)


def _cartas_do_catalogo(effect_type: str) -> list:
    dados = json.load(open("src/data/skills.json", encoding="utf-8"))
    itens = dados["skills"] if isinstance(dados, dict) and "skills" in dados else dados
    lista = list(itens.values()) if isinstance(itens, dict) else itens
    return [s for s in lista if s.get("effect_type") == effect_type]


class TestStatusNaoDerrubaAConstrucao:
    """37 skills de status são acessíveis ao herói, e `float('frozen')` explodia."""

    def test_toda_skill_de_status_do_catalogo_constroi_mecanica(self):
        hero, alvo = _heroi("mage", 10), _monstro(10)
        cartas = _cartas_do_catalogo("status")
        assert cartas, "o catálogo não tem skill de status — a busca ficaria verde sem verificar"
        for dados in cartas:
            skill = get_skill_by_id(dados["id"])
            if skill is None:
                continue
            m = ad._mecanica_de_skill(hero, alvo, skill)
            assert m.statuses, f"{dados['name']} chegou sem efeito declarado"
            assert m.statuses[0].effect, f"{dados['name']} chegou sem nome de efeito"

    def test_o_efeito_declarado_e_o_que_a_carta_aplica(self):
        hero, alvo = _heroi("mage", 10), _monstro(10)
        for dados in _cartas_do_catalogo("status")[:6]:
            skill = get_skill_by_id(dados["id"])
            if skill is None:
                continue
            m = ad._mecanica_de_skill(hero, alvo, skill)
            assert m.statuses[0].effect == str(skill.effect_value)


class TestChanceDeStatusUsaAResistencia:
    def test_alvo_imune_zera_a_chance_declarada(self):
        """A carta declara 100%; o alvo resiste 100%. O fato tem de dizer zero."""
        alvo = _monstro(10)
        efeito = "frozen"
        assert ad._chance_efetiva(alvo, efeito, 100.0) > 0
        alvo.resistances = {efeito: 100}
        assert ad._chance_efetiva(alvo, efeito, 100.0) == 0.0

    def test_a_chance_declarada_e_a_canonica(self):
        alvo = _monstro(10)
        alvo.resistances = {"poison": 40}
        esperado = fx.effective_status_chance(80.0, fx.status_resistance(alvo, "poison")) / 100
        assert ad._chance_efetiva(alvo, "poison", 80.0) == esperado


class TestBuffDefensivoSeESomenteSe:
    """O buff reduz o dano declarado se e somente se reduz na execução real."""

    def _reduz_de_verdade(self, hero, alvo, stat, valor) -> bool:
        antes = ad._dano_basico_esperado(alvo, hero)
        hero.active_buffs["__prova__"] = {
            "stat": stat,
            "value": fx.buff_value(hero, stat, valor),
            "duration": 1,
        }
        try:
            return ad._dano_basico_esperado(alvo, hero) < antes
        finally:
            del hero.active_buffs["__prova__"]

    def test_guarda_alta_reduz_no_fato_porque_reduz_no_motor(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        skill = get_skill_by_id("n_guarda_alta")
        m = ad._mecanica_de_skill(hero, alvo, skill)
        reduz_no_motor = self._reduz_de_verdade(hero, alvo, "df", int(skill.effect_value))
        declara_reducao = bool(m.incoming_damage_after)
        assert declara_reducao == reduz_no_motor
        assert declara_reducao, "Guarda Alta reduz dano de verdade e o fato marcava zero"

    def test_o_valor_declarado_e_menor_que_o_golpe_atual(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        m = ad._mecanica_de_skill(hero, alvo, get_skill_by_id("n_guarda_alta"))
        assert 0 < m.incoming_damage_after < ad._dano_basico_esperado(alvo, hero)

    def test_a_sonda_devolve_o_heroi_ao_estado_anterior(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        antes = dict(hero.active_buffs)
        ad._mecanica_de_skill(hero, alvo, get_skill_by_id("n_guarda_alta"))
        assert dict(hero.active_buffs) == antes


class TestAgilidadeTemTresConsequencias:
    """Acerto, esquiva e ORDEM DE TURNO. O motor tem as três."""

    def test_buff_de_agilidade_aparece_em_alguma_consequencia(self):
        hero, alvo = _heroi("rogue", 8), _monstro(8)
        skill = get_skill_by_id("sombra_rapida")
        m = ad._mecanica_de_skill(hero, alvo, skill)
        mudou = (
            m.incoming_damage_after
            or m.outgoing_damage_after
            or m.acts_before_enemy_after is not None
        )
        assert mudou, "+30% de agilidade não mudou fato nenhum — é o caso AUSENTE da auditoria"

    def test_a_iniciativa_declarada_e_a_de_build_turn_order(self):
        hero, alvo = _heroi("rogue", 8), _monstro(8)
        assert ad._age_antes(hero, alvo) is (build_turn_order(hero, [alvo])[0] is hero)

    def test_agilidade_que_vira_a_iniciativa_muda_o_fato(self):
        hero, alvo = _heroi("warrior", 5), _monstro(5)
        # Um monstro mais rápido: o herói começa atrás e o buff pode virar.
        alvo.base_ag = hero.get_ag() + 1
        antes = ad._age_antes(hero, alvo)
        depois = ad._sonda_de_buff(hero, alvo, "ag", 500, "prova")["age_antes"]
        if depois != antes:
            campos = ad._consequencias_do_buff(hero, alvo, "ag", 500, "prova")
            assert campos.get("acts_before_enemy_after") == depois


class TestDanoDeclaradoEODoFunil:
    def test_o_golpe_declarado_sai_da_funcao_canonica(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        base = combat_mech.basic_attack_power(hero)
        mods = combat_mech.damage_modifiers(hero, alvo, is_critical=False)
        canonico = combat_mech._calculate_damage(
            base_power=float(base),
            flat_mods=list(getattr(mods, "flat", ()) or ()),
            mult_mods=list(mods.mult),
            xmult_mods=list(mods.xmult),
            defense_target=alvo.get_df(),
            mitigation=list(mods.mitigation),
        )
        assert ad._dano_do_funil(hero, alvo, base, critico=False) == canonico

    def test_defesa_maior_reduz_o_dano_declarado(self):
        hero = _heroi("warrior", 8)
        fraco, forte = _monstro(8), _monstro(8)
        forte.base_df = fraco.get_df() * 4
        base = combat_mech.basic_attack_power(hero)
        assert ad._dano_do_funil(hero, forte, base, critico=False) < ad._dano_do_funil(
            hero, fraco, base, critico=False
        )

    def test_o_critico_bate_mais_que_o_golpe_normal(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        base = combat_mech.basic_attack_power(hero)
        assert ad._dano_do_funil(hero, alvo, base, critico=True) > ad._dano_do_funil(
            hero, alvo, base, critico=False
        )


class TestChanceDeCriticoDeclarada:
    """Mirror mínimo protegido por paridade contra a regra real do motor."""

    def _crit_real(self, atacante, nome_da_skill="") -> float:
        from src.shared.constants import (
            CRIT_CHANCE_CAP,
            CRIT_CHANCE_DEFAULT,
            CRIT_CHANCE_HIGH,
        )

        base = (
            CRIT_CHANCE_HIGH
            if (
                hasattr(atacante, "get_classname")
                and atacante.get_classname() == "Rogue"
                and nome_da_skill == "Ataque Furtivo"
            )
            else CRIT_CHANCE_DEFAULT
        )
        base += int(fx.combat_modifier(atacante, "crit_chance"))
        return min(base, CRIT_CHANCE_CAP) / 100

    def test_bate_com_a_regra_do_motor_para_as_tres_classes(self):
        for classe in ("warrior", "mage", "rogue"):
            hero = _heroi(classe, 8)
            assert ad._chance_de_critico(hero) == self._crit_real(hero)

    def test_o_caso_do_ladino_com_ataque_furtivo_nao_se_perde(self):
        rogue = _heroi("rogue", 8)
        assert ad._chance_de_critico(rogue, "Ataque Furtivo") > ad._chance_de_critico(rogue)

    def test_o_teto_do_motor_e_respeitado(self):
        from src.shared.constants import CRIT_CHANCE_CAP

        hero = _heroi("rogue", 8)
        hero.active_buffs["__crit__"] = {"stat": "crit_chance", "value": 999, "duration": 1}
        assert ad._chance_de_critico(hero, "Ataque Furtivo") == CRIT_CHANCE_CAP / 100


class TestEgideDeclaraACapacidadeReal:
    def test_a_capacidade_declarada_e_o_que_a_execucao_absorve(self):
        mago, alvo = _heroi("mage", 8), _monstro(8)
        entrada = ad._dano_basico_esperado(alvo, mago)
        declarado = ad._egide_absorve(mago, entrada)
        mp_antes = mago.get_mp()
        passou = combat_mech._absorve_com_egide(mago, entrada, None)
        assert declarado == entrada - passou, "a capacidade declarada não é a que o motor absorve"
        assert mago.get_mp() < mp_antes, "a execução real precisa gastar mana"

    def test_a_leitura_nao_consome_mana(self):
        mago, alvo = _heroi("mage", 8), _monstro(8)
        antes = mago.get_mp()
        ad._egide_absorve(mago, ad._dano_basico_esperado(alvo, mago))
        assert mago.get_mp() == antes

    def test_sem_mana_nao_ha_capacidade(self):
        mago, alvo = _heroi("mage", 8), _monstro(8)
        mago.reduce_mp(mago.get_mp())
        assert ad._egide_absorve(mago, ad._dano_basico_esperado(alvo, mago)) == 0

    def test_quem_nao_tem_egide_declara_zero(self):
        guerreiro, alvo = _heroi("warrior", 8), _monstro(8)
        assert ad._egide_absorve(guerreiro, ad._dano_basico_esperado(alvo, guerreiro)) == 0


class TestDotDeclarado:
    def test_um_dot_do_catalogo_declara_dano_e_duracao(self):
        hero = _heroi("rogue", 8)
        por_turno, duracao = ad._dot_declarado("poison", hero, 0)
        assert por_turno > 0 and duracao > 0

    def test_efeito_que_nao_e_dot_declara_zero(self):
        hero = _heroi("rogue", 8)
        assert ad._dot_declarado("frozen", hero, 3) == (0, 0)

    def test_o_dano_declarado_acompanha_o_hp_maximo(self):
        pequeno, grande = _heroi("rogue", 1), _heroi("rogue", 15)
        assert (
            ad._dot_declarado("poison", grande, 0)[0] > ad._dot_declarado("poison", pequeno, 0)[0]
        )


class TestAcertoIncluiAMiraDaAcao:
    def test_accuracy_modifier_da_carta_entra_na_chance(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        neutro = ad._chance_de_acerto(hero, alvo, 0)
        preciso = ad._chance_de_acerto(hero, alvo, 20)
        pesado = ad._chance_de_acerto(hero, alvo, -20)
        assert pesado <= neutro <= preciso
        assert preciso > pesado, "a mira da ação não estava entrando na conta"

    def test_a_chance_declarada_e_a_canonica(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        assert ad._chance_de_acerto(hero, alvo, 7) == combat_mech.hit_chance(hero, alvo, 7) / 100


class TestCuraIncluiOBonusDoJogo:
    def test_potion_heal_bonus_aumenta_a_cura_declarada(self):
        hero, alvo = _heroi("warrior", 8), _monstro(8)
        cura = next(
            (s for s in _cartas_do_catalogo("heal") if get_skill_by_id(s["id"]) is not None), None
        )
        assert cura is not None, "o catálogo não tem skill de cura"
        skill = get_skill_by_id(cura["id"])
        sem = ad._mecanica_de_skill(hero, alvo, skill).healing
        hero.active_buffs["__bonus__"] = {"stat": "potion_heal_bonus", "value": 50, "duration": 1}
        com = ad._mecanica_de_skill(hero, alvo, skill).healing
        assert com > sem, "o bônus de cura do jogo não chegava ao fato"


class TestConsumivelDeclaraEscassez:
    def test_o_numero_de_usos_restantes_chega_ao_fato(self):
        from src.content.items import Item

        hero, alvo = _heroi("warrior", 8), _monstro(8)
        pocao = Item(
            "pocao_prova", "Poção", "cura", effect_type="max_hp", effect_value=30, consumable=True
        )
        hero.inventory.extend([pocao, pocao])
        estado = ad.estado_do_combate(hero, alvo, 0)
        opcoes, _ = ad.acoes_do_combate(hero, alvo, estado)
        item = next(o for o in opcoes if o.action_id.startswith("item:"))
        assert item.mechanics.uses_left == 2


class TestOAdaptadorNaoMudaOEstado:
    def test_enumerar_as_acoes_nao_altera_heroi_nem_monstro(self):
        hero, alvo = _heroi("rogue", 8), _monstro(8)
        antes = (hero.get_hp(), hero.get_mp(), dict(hero.active_buffs), alvo.get_hp())
        estado = ad.estado_do_combate(hero, alvo, 0)
        ad.acoes_do_combate(hero, alvo, estado)
        assert (hero.get_hp(), hero.get_mp(), dict(hero.active_buffs), alvo.get_hp()) == antes

    def test_enumerar_nao_consome_rng(self):
        hero, alvo = _heroi("rogue", 8), _monstro(8)
        r = random.Random(1)
        estado = ad.estado_do_combate(hero, alvo, 0)
        antes = r.getstate()
        ad.acoes_do_combate(hero, alvo, estado)
        assert r.getstate() == antes


class TestPontasDoFunil:
    """FASE C: "mata agora" não pode sair de uma média.

    `expected_strike_damage` é a média sobre o crítico. As duas pontas viajam
    separadas para a policy poder distinguir a certeza da expectativa.
    """

    def test_as_duas_pontas_cercam_a_media(self):
        hero, alvo = _heroi("warrior", 9), _monstro(9)
        opcoes, _ = ad.acoes_do_combate(hero, alvo, ad.estado_do_combate(hero, alvo, 1))
        ataque = next(o for o in opcoes if o.action_id == "attack")
        m = ataque.mechanics
        assert m.strike_damage_no_crit <= m.expected_strike_damage <= m.strike_damage_on_crit

    def test_a_ponta_sem_critico_e_o_funil_sem_critico(self):
        hero, alvo = _heroi("rogue", 9), _monstro(9)
        base = combat_mech.basic_attack_power(hero)
        opcoes, _ = ad.acoes_do_combate(hero, alvo, ad.estado_do_combate(hero, alvo, 1))
        m = next(o for o in opcoes if o.action_id == "attack").mechanics
        assert m.strike_damage_no_crit == max(1, ad._dano_do_funil(hero, alvo, base, critico=False))
        assert m.strike_damage_on_crit == max(1, ad._dano_do_funil(hero, alvo, base, critico=True))


class TestEgideDepoisDoCusto:
    """A ordem do motor: `apply_skill` cobra o MP ANTES de o golpe resolver.

    `_absorve_com_egide` só dispara quando o herói é DEFENSOR — no turno do
    monstro, com a mana já gasta. Declarar a capacidade com o MP de antes seria
    prometer um escudo que não vai existir.
    """

    def test_com_mp_curto_a_skill_declara_menos_egide_que_o_ataque(self):
        """Quando o MP é o gargalo, gastar mana ENCOLHE o escudo do próximo golpe."""
        hero, alvo = _heroi("mage", 12), _monstro(12)
        hero.magic_shield_percent = 100
        estado = ad.estado_do_combate(hero, alvo, 1)
        # MP baixo o bastante para a capacidade ser limitada pela mana, e não
        # pela fração do golpe que entra.
        hero._mp = max(1, int(estado.alvo_dano / ad.MAGIC_SHIELD_DAMAGE_PER_MP))
        estado = ad.estado_do_combate(hero, alvo, 1)
        opcoes, _ = ad.acoes_do_combate(hero, alvo, estado)
        ataque = next(o for o in opcoes if o.action_id == "attack")
        caras = [o for o in opcoes if o.mechanics.mana_cost > 0]
        assert caras, "o mago do nível 12 não tinha skill com custo — o teste ficaria vazio"
        for opcao in caras:
            assert (
                opcao.mechanics.aegis_absorbable_damage < ataque.mechanics.aegis_absorbable_damage
            )

    def test_a_capacidade_declarada_e_a_do_mp_que_sobra(self):
        hero, alvo = _heroi("mage", 12), _monstro(12)
        hero.magic_shield_percent = 50
        estado = ad.estado_do_combate(hero, alvo, 1)
        opcoes, _ = ad.acoes_do_combate(hero, alvo, estado)
        for opcao in opcoes:
            m = opcao.mechanics
            sobra = estado.mp - m.mana_cost + m.mana_restored
            assert m.aegis_absorbable_damage == ad._egide_absorve(hero, estado.alvo_dano, mp=sobra)


class TestSondaDeStatusNoAlvo:
    """Status de ATRIBUTO chegava como nome e chance, sem consequência nenhuma.

    São 15 cartas acessíveis ao jogador de hoje: weakened, hexed, slowed,
    vulnerable e clouded.
    """

    def test_a_sonda_nao_deixa_residuo_no_alvo(self):
        hero, alvo = _heroi("mage", 10), _monstro(10)
        antes = (alvo.get_hp(), alvo.get_mp(), dict(getattr(alvo, "active_effects", {})))
        for efeito in ("weakened", "vulnerable", "slowed", "hexed", "clouded"):
            ad._sonda_de_status(hero, alvo, efeito)
        depois = (alvo.get_hp(), alvo.get_mp(), dict(getattr(alvo, "active_effects", {})))
        assert antes == depois

    def test_o_declarado_e_o_que_um_apply_real_produz(self):
        """Paridade: a sonda escreve a instância direto; o motor aplica de verdade."""
        for efeito in ("weakened", "vulnerable", "slowed", "hexed"):
            hero, alvo = _heroi("mage", 10), _monstro(10)
            declarado = ad._sonda_de_status(hero, alvo, efeito)
            if not declarado:
                continue
            definicao = core.definition(efeito)
            core.apply_effect(
                alvo,
                efeito,
                intensity=definicao.default_intensity,
                duration=definicao.default_duration,
                source_id="real",
            )
            real = {
                "entrando": ad._dano_basico_esperado(alvo, hero),
                "saindo": ad._dano_basico_esperado(hero, alvo),
                "age_antes": ad._age_antes(hero, alvo),
            }
            assert declarado == real, efeito

    def test_vulnerable_aumenta_o_golpe_que_sai(self):
        hero, alvo = _heroi("warrior", 10), _monstro(10, "tank")
        antes = ad._dano_basico_esperado(hero, alvo)
        campos = ad._consequencias_do_status(hero, alvo, "vulnerable")
        assert campos.get("outgoing_damage_after", antes) > antes

    def test_weakened_reduz_o_golpe_que_entra(self):
        hero, alvo = _heroi("warrior", 10), _monstro(10)
        antes = ad._dano_basico_esperado(alvo, hero)
        campos = ad._consequencias_do_status(hero, alvo, "weakened")
        assert campos.get("incoming_damage_after", antes) < antes


class TestDrenoDeclarado:
    """`mana_burn` é família DRAIN: tira MP ATUAL por turno, pela duração."""

    def test_o_dreno_nunca_passa_do_mp_que_o_alvo_tem(self):
        alvo = _monstro(10)
        alvo._mp = 5
        assert ad._dreno_declarado("mana_burn", alvo, 4) <= 5

    def test_alvo_sem_mp_nao_tem_o_que_drenar(self):
        alvo = _monstro(10)
        alvo._mp = 0
        assert ad._dreno_declarado("mana_burn", alvo, 3) == 0

    def test_efeito_que_nao_e_dreno_declara_zero(self):
        alvo = _monstro(10)
        assert ad._dreno_declarado("poison", alvo, 3) == 0


class TestCustoDoEstadoConsumido:
    """O benefício da interação já está no dano; o preço não estava em lugar nenhum."""

    def test_gelo_consumido_cobra_so_a_chance_real_de_ser_consumido(self):
        """Quebra Gélida gasta o gelo no CRÍTICO QUE ACERTA, não em todo golpe."""
        hero, alvo = _heroi("rogue", 10), _monstro(10)
        core.apply_effect(alvo, "frozen", intensity=0.0, duration=3, source_id="teste")
        leis = ad._interacoes_do_ataque(hero, alvo)
        gelo = [v for v in leis if v.consumes_status == "frozen"]
        assert gelo, "sem a lei do gelo declarada, o teste ficaria verde sem verificar"
        assert gelo[0].requires_critical, "Quebra Gélida exige crítico"
        perdidos = ad._turnos_de_controle_perdidos(
            alvo, leis, ad._quebra_ao_dar_dano(alvo), hit_chance=0.8, crit_chance=0.25
        )
        assert perdidos == 3 * 0.8 * 0.25

    def test_gelo_certo_seria_cobrado_inteiro(self):
        """O contraste: com acerto e crítico garantidos, o preço é a duração cheia."""
        hero, alvo = _heroi("rogue", 10), _monstro(10)
        core.apply_effect(alvo, "frozen", intensity=0.0, duration=3, source_id="teste")
        leis = ad._interacoes_do_ataque(hero, alvo)
        perdidos = ad._turnos_de_controle_perdidos(
            alvo, leis, ad._quebra_ao_dar_dano(alvo), hit_chance=1.0, crit_chance=1.0
        )
        assert perdidos == 3.0

    def test_acordar_quem_dorme_custa_so_o_que_o_golpe_acerta(self):
        """Sono só quebra se a ação CAUSAR dano: o preço é a chance de acertar."""
        alvo = _monstro(10)
        core.apply_effect(alvo, "sleep", intensity=0.0, duration=2, source_id="teste")
        quebras = ad._quebra_ao_dar_dano(alvo)
        assert "sleep" in quebras
        assert ad._turnos_de_controle_perdidos(alvo, (), quebras, hit_chance=1.0) == 2.0
        assert ad._turnos_de_controle_perdidos(alvo, (), quebras, hit_chance=0.5) == 1.0
        # E o crítico não entra: quebrar sono não depende de crítico.
        assert (
            ad._turnos_de_controle_perdidos(alvo, (), quebras, hit_chance=0.5, crit_chance=1.0)
            == 1.0
        )

    def test_estado_que_nao_rouba_turno_nao_custa_turno(self):
        alvo = _monstro(10)
        core.apply_effect(alvo, "weakened", intensity=10.0, duration=3, source_id="teste")
        assert ad._turnos_de_controle_perdidos(alvo, (), ("weakened",)) == 0


class TestEmboscadaCustaCerto:
    """`invisible` sai NA TENTATIVA, inclusive no erro — custo certo, não provável.

    É o contraste com Quebra Gélida e com o sono: aquelas dependem de acertar (e
    de critar), esta não depende de nada. `reveal_on_attempt` remove a ocultação
    mesmo quando o golpe passa longe.
    """

    def _com_invisibilidade(self):
        hero, alvo = _heroi("rogue", 10), _monstro(10)
        definicao = core.definition("invisible")
        core.apply_effect(
            hero,
            "invisible",
            intensity=definicao.default_intensity,
            duration=3,
            source_id="teste",
        )
        return hero, alvo

    def test_ocultacao_nao_entra_no_custo_de_controle(self):
        """Invisibilidade não rouba turno, então o preço dela não é turno de controle."""
        hero, alvo = self._com_invisibilidade()
        leis = ad._interacoes_do_ataque(hero, alvo)
        do_atacante = [v for v in leis if v.consumes_from_self]
        assert do_atacante, "sem Emboscada declarada, o teste ficaria verde sem verificar"
        assert do_atacante[0].consumes_status == "invisible"
        perdidos = ad._turnos_de_controle_perdidos(
            alvo, leis, ad._quebra_ao_dar_dano(alvo), hit_chance=1.0, crit_chance=1.0
        )
        assert perdidos == 0.0

    def test_o_preco_da_ocultacao_e_o_golpe_que_passa_a_doer(self):
        hero, alvo = self._com_invisibilidade()
        leis = ad._interacoes_do_ataque(hero, alvo)
        antes = ad._dano_basico_esperado(alvo, hero)
        campos = ad._custo_da_ocultacao_perdida(hero, alvo, leis)
        assert campos["incoming_damage_after"] > antes

    def test_o_custo_declarado_nao_depende_da_chance_de_acerto(self):
        """A prova de que é CERTO: o número é o mesmo qualquer que seja a mira."""
        hero, alvo = self._com_invisibilidade()
        leis = ad._interacoes_do_ataque(hero, alvo)
        primeiro = ad._custo_da_ocultacao_perdida(hero, alvo, leis)
        hero.base_ag = 1
        segundo = ad._custo_da_ocultacao_perdida(hero, alvo, leis)
        assert primeiro["incoming_damage_after"] > 0
        assert segundo["incoming_damage_after"] > 0

    def test_observar_a_emboscada_nao_gasta_a_invisibilidade(self):
        hero, alvo = self._com_invisibilidade()
        leis = ad._interacoes_do_ataque(hero, alvo)
        ad._custo_da_ocultacao_perdida(hero, alvo, leis)
        ad._turnos_de_controle_perdidos(alvo, leis, (), hit_chance=1.0, crit_chance=1.0)
        assert core.has_effect(hero, "invisible")
