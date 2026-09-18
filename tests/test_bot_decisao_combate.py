"""O bot escolhe uma ação PLAUSÍVEL? — propriedades comportamentais do combate.

FASE A perguntou se o engine executa certo. FASE B, se o adapter representa
certo. Este arquivo pergunta a terceira coisa: **dado tudo que ele enxerga, a
escolha faz sentido para uma pessoa razoável olhando a mesma posição?**

Cada teste monta uma posição controlada em que a decisão é óbvia para um humano,
e cobra a mesma decisão do cérebro. Não se cobra a jogada ÓTIMA — se cobra que a
jogada seja defensável, e que nenhuma fórmula inverta o sinal do que ela mede.

Posição, e não seed: nenhum teste aqui depende de RNG, de classe ou de monstro.
"""

from __future__ import annotations

from pathlib import Path

from src.content.factories.archetypes import all_archetypes
from src.content.factories.monsters import create_monster
from src.shared import effects as fx
from src.sim.bot import decidir_no_combate
from src.sim.bot.decision import ActionOption
from src.sim.bot.evaluators import avaliar_combate
from src.sim.bot.observation import ActionMechanicsView, CombatState, StatusView


def _estado(**kwargs) -> CombatState:
    base = dict(
        turno=1,
        hp=400,
        hp_max=500,
        mp=100,
        mp_max=100,
        dano_basico=50,
        alvo_nivel=5,
        alvo_hp=300,
        alvo_hp_max=300,
        alvo_mp=40,
        alvo_mp_max=40,
        alvo_dano=40,
    )
    base.update(kwargs)
    return CombatState(**base)


def _opcao(action_id: str, family: str, label: str = "", **mecanica) -> ActionOption:
    return ActionOption(
        action_id=action_id,
        family=family,
        label=label or action_id,
        mechanics=ActionMechanicsView(**mecanica),
    )


def _ataque(dano=50, **extra) -> ActionOption:
    campos = dict(
        expected_strike_damage=dano,
        strike_damage_no_crit=int(dano * 0.95),
        strike_damage_on_crit=int(dano * 1.5),
        hit_chance=1.0,
        crit_chance=0.1,
        acts_before_enemy=True,
    )
    campos.update(extra)
    return _opcao("attack", "attack", "ataque básico", **campos)


def _pocao(cura=150, restantes=3) -> ActionOption:
    return _opcao("item:pocao", "heal", "poção", healing=cura, uses_left=restantes, duration=1)


def _status(efeito: str, chance: float, **campos) -> tuple[StatusView, ...]:
    """Um efeito aplicado no alvo. Principal ou `secondary` — o view não distingue."""
    return (StatusView(effect=efeito, chance=chance, **campos),)


def _nota(opcao: ActionOption, state: CombatState) -> float:
    return avaliar_combate(opcao, state).utility


class TestLetalNaoPerdeParaPocao:
    """Inimigo praticamente morto: gastar poção é desperdício visível."""

    def test_o_golpe_que_mata_vence_a_pocao(self):
        state = _estado(alvo_hp=20, hp=450)
        d = decidir_no_combate(state, (_ataque(), _pocao()))
        assert d.action_id == "attack"

    def test_o_golpe_que_mata_nao_recebe_nota_negativa(self):
        """Era o defeito: a linha de base sem piso dava `duração −0,87` ao letal."""
        state = _estado(alvo_hp=20)
        assert _nota(_ataque(), state) >= 0.0

    def test_mata_agora_so_quando_o_golpe_sem_critico_ja_basta(self):
        state = _estado(alvo_hp=20)
        assert avaliar_combate(_ataque(), state).note == "mata agora"
        # O mesmo alvo, mas só o crítico derruba: é chance, não certeza.
        state = _estado(alvo_hp=60)
        nota = avaliar_combate(_ataque(dano=50), state).note
        assert nota.startswith("resolve neste turno com")


class TestFugaMonotonica:
    """Piorar a posição NUNCA pode tornar insistir artificialmente mais atraente."""

    def _par(self, alvo_dano: int) -> tuple[float, float]:
        state = _estado(alvo_dano=alvo_dano, alvo_hp=600, dano_basico=30, hp=200)
        fuga = _opcao("flee", "flee", "fugir", flee_chance=0.5)
        return _nota(fuga, state), _nota(_ataque(dano=30), state)

    def test_a_vantagem_da_fuga_nunca_cai_quando_o_perigo_cresce(self):
        anterior = None
        for alvo_dano in range(20, 220, 10):
            fuga, ataque = self._par(alvo_dano)
            vantagem = fuga - ataque
            if anterior is not None:
                assert vantagem >= anterior - 1e-9, f"inverteu em alvo_dano={alvo_dano}"
            anterior = vantagem

    def test_luta_perdida_com_perigo_extremo_escolhe_fugir(self):
        state = _estado(alvo_dano=190, alvo_hp=600, dano_basico=30, hp=200)
        fuga = _opcao("flee", "flee", "fugir", flee_chance=0.5)
        d = decidir_no_combate(state, (_ataque(dano=30), fuga))
        assert d.action_id == "flee"

    def test_ganhando_a_corrida_nao_se_foge(self):
        state = _estado(alvo_hp=100, alvo_dano=10, hp=450)
        fuga = _opcao("flee", "flee", "fugir", flee_chance=0.5)
        d = decidir_no_combate(state, (_ataque(), fuga))
        assert d.action_id == "attack"


class TestBuffDefensivo:
    """Guarda Alta que torna a corrida sustentável tem de superar o básico."""

    def test_buff_que_vira_a_corrida_vence_o_ataque(self):
        state = _estado(hp=120, alvo_dano=60, alvo_hp=400, dano_basico=50)
        guarda = _opcao(
            "skill:guarda",
            "damage_reduction",
            "Guarda Alta",
            incoming_damage_after=15,
            duration=4,
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), guarda))
        assert d.action_id == "skill:guarda"

    def test_o_mesmo_buff_numa_luta_ja_ganha_nao_vence(self):
        state = _estado(hp=480, alvo_dano=5, alvo_hp=60, dano_basico=50)
        guarda = _opcao(
            "skill:guarda",
            "damage_reduction",
            "Guarda Alta",
            incoming_damage_after=2,
            duration=4,
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), guarda))
        assert d.action_id == "attack"


class TestBuffOfensivo:
    """Buff de ST/MG só vale se encurtar a luta o bastante para pagar o turno."""

    def test_buff_que_encurta_muito_vence_o_ataque(self):
        state = _estado(alvo_hp=900, dano_basico=50, alvo_dano=20, hp=450)
        furia = _opcao(
            "skill:furia",
            "buff",
            "Fúria",
            buff_stat="st",
            buff_value=60,
            outgoing_damage_after=130,
            duration=6,
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), furia))
        assert d.action_id == "skill:furia"

    def test_buff_que_encurta_pouco_numa_luta_curta_nao_vence(self):
        state = _estado(alvo_hp=120, dano_basico=50, alvo_dano=20, hp=450)
        furia = _opcao(
            "skill:furia",
            "buff",
            "Fúria",
            buff_stat="st",
            buff_value=5,
            outgoing_damage_after=55,
            duration=2,
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), furia))
        assert d.action_id == "attack"


class TestControle:
    """Roubar turno vale pela resposta inimiga que deixa de existir."""

    def test_controle_de_alta_chance_em_turno_critico_vence_o_ataque(self):
        """Dois golpes para matar, um golpe para morrer: o turno roubado decide."""
        state = _estado(hp=50, alvo_dano=60, alvo_hp=150, dano_basico=50)
        atordoar = _opcao(
            "skill:atordoar",
            "status",
            "Atordoar",
            statuses=_status("stun", 0.9, skips_turn=True, duration=3),
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), atordoar))
        assert d.action_id == "skill:atordoar"

    def test_numa_corrida_sem_esperanca_a_fuga_ainda_vence_o_controle(self):
        """Controle que só adia a morte não é solução: fugir continua na mesa."""
        state = _estado(hp=90, alvo_dano=80, alvo_hp=400, dano_basico=50)
        atordoar = _opcao(
            "skill:atordoar",
            "status",
            "Atordoar",
            statuses=_status("stun", 0.9, skips_turn=True, duration=2),
            mana_cost=10,
        )
        fuga = _opcao("flee", "flee", "fugir", flee_chance=0.5)
        d = decidir_no_combate(state, (_ataque(), atordoar, fuga))
        assert d.action_id == "flee"

    def test_controle_irrelevante_em_luta_que_acaba_agora_nao_vence(self):
        state = _estado(hp=450, alvo_dano=5, alvo_hp=20, dano_basico=50)
        atordoar = _opcao(
            "skill:atordoar",
            "status",
            "Atordoar",
            statuses=_status("stun", 0.9, skips_turn=True, duration=2),
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), atordoar))
        assert d.action_id == "attack"


class TestDanoAoLongoDoTempo:
    """DoT vale pelos tiques que a luta ainda comporta — temporalidade preservada."""

    def _veneno(self) -> ActionOption:
        return _opcao(
            "skill:veneno",
            "status",
            "Veneno",
            statuses=_status("poison", 1.0, duration=5, dot_damage_per_turn=30, dot_duration=5),
            mana_cost=10,
        )

    def test_luta_que_acaba_antes_do_primeiro_tique_nao_ganha_valor(self):
        curta = _estado(alvo_hp=40, dano_basico=50, alvo_dano=10, hp=450)
        assert _nota(self._veneno(), curta) < _nota(_ataque(), curta)

    def test_luta_longa_captura_os_tiques(self):
        curta = _estado(alvo_hp=40, dano_basico=50, alvo_dano=10, hp=450)
        longa = _estado(alvo_hp=800, dano_basico=50, alvo_dano=10, hp=450)
        assert _nota(self._veneno(), longa) > _nota(self._veneno(), curta)

    def test_o_dot_nunca_alonga_a_luta(self):
        longa = _estado(alvo_hp=800, dano_basico=50, alvo_dano=10, hp=450)
        componentes = dict(avaliar_combate(self._veneno(), longa).components)
        assert componentes["duração"] >= -1.0


class TestConsumivelFinito:
    """Escassez é custo de oportunidade, nunca proibição."""

    def test_a_ultima_pocao_que_evita_a_morte_pode_ser_usada(self):
        state = _estado(hp=50, hp_max=500, alvo_dano=45, alvo_hp=600, dano_basico=40)
        d = decidir_no_combate(state, (_ataque(dano=40), _pocao(cura=300, restantes=1)))
        assert d.action_id == "item:pocao"

    def test_a_ultima_pocao_com_hp_quase_cheio_perde(self):
        state = _estado(hp=480, hp_max=500, alvo_dano=20, alvo_hp=300)
        d = decidir_no_combate(state, (_ataque(), _pocao(cura=300, restantes=1)))
        assert d.action_id == "attack"

    def test_estoque_maior_cobra_menos_escassez(self):
        state = _estado(hp=50, hp_max=500, alvo_dano=45, alvo_hp=600, dano_basico=40)
        assert _nota(_pocao(cura=300, restantes=5), state) > _nota(
            _pocao(cura=300, restantes=1), state
        )


class TestManaNaoPuneQuemResolve:
    def test_skill_cara_que_resolve_melhor_nao_e_punida(self):
        state = _estado(alvo_hp=600, dano_basico=50, mp=100, mp_max=100, alvo_dano=20, hp=450)
        bomba = _opcao(
            "skill:bomba",
            "damage",
            "Bomba",
            expected_strike_damage=220,
            strike_damage_no_crit=210,
            strike_damage_on_crit=330,
            hit_chance=1.0,
            crit_chance=0.1,
            mana_cost=40,
        )
        d = decidir_no_combate(state, (_ataque(), bomba))
        assert d.action_id == "skill:bomba"

    def test_com_a_barra_no_fim_e_luta_longa_a_escassez_aparece(self):
        cheia = _estado(alvo_hp=600, dano_basico=50, mp=100, mp_max=100, alvo_dano=20, hp=450)
        vazia = _estado(alvo_hp=600, dano_basico=50, mp=40, mp_max=100, alvo_dano=20, hp=450)
        bomba = _opcao(
            "skill:bomba",
            "damage",
            "Bomba",
            expected_strike_damage=220,
            strike_damage_no_crit=210,
            strike_damage_on_crit=330,
            hit_chance=1.0,
            mana_cost=40,
        )
        assert _nota(bomba, vazia) < _nota(bomba, cheia)

    def test_recarga_desconta_mas_nunca_inverte_o_sinal_do_ganho(self):
        state = _estado(alvo_hp=600, dano_basico=50, alvo_dano=20, hp=450)
        sem = _opcao(
            "skill:a",
            "damage",
            "sem recarga",
            expected_strike_damage=200,
            strike_damage_no_crit=190,
            strike_damage_on_crit=300,
            hit_chance=1.0,
        )
        com = _opcao(
            "skill:b",
            "damage",
            "com recarga",
            expected_strike_damage=200,
            strike_damage_no_crit=190,
            strike_damage_on_crit=300,
            hit_chance=1.0,
            cooldown=3,
        )
        assert 0 < _nota(com, state) < _nota(sem, state)


class TestEstadoConsumido:
    """O benefício da interação já está no dano; o preço tem de aparecer."""

    def test_consumir_gelo_baixa_a_nota_do_mesmo_golpe(self):
        state = _estado(alvo_hp=600, dano_basico=50, alvo_dano=40)
        limpo = _ataque()
        gastando = _ataque(forfeited_control_turns=2)
        assert _nota(gastando, state) < _nota(limpo, state)

    def test_acordar_quem_dorme_aparece_como_parcela_nomeada(self):
        state = _estado(alvo_hp=600, dano_basico=50)
        componentes = dict(avaliar_combate(_ataque(forfeited_control_turns=2), state).components)
        assert componentes["estado gasto"] < 0

    def test_o_custo_do_estado_e_proporcional_a_chance_de_perde_lo(self):
        """O preço é ESPERADO: cobrar a duração cheia seria cobrar por um
        consumo que o motor só executa no crítico que acerta."""
        state = _estado(alvo_hp=600, dano_basico=50, alvo_dano=40, hp=120)
        provavel = _ataque(forfeited_control_turns=3 * 0.8 * 0.25)
        certo = _ataque(forfeited_control_turns=3.0)
        assert _nota(provavel, state) > _nota(certo, state)

    def test_perder_a_ocultacao_conta_como_golpe_que_passa_a_doer_mais(self):
        state = _estado(alvo_hp=600, dano_basico=50, alvo_dano=40, hp=200)
        oculto = _ataque()
        revelando = _ataque(incoming_damage_after=70, duration=2)
        assert _nota(revelando, state) < _nota(oculto, state)


class TestLegalidade:
    def test_a_decisao_aponta_para_uma_das_opcoes_recebidas(self):
        state = _estado()
        opcoes = (_ataque(), _pocao(), _opcao("flee", "flee", "fugir", flee_chance=0.5))
        d = decidir_no_combate(state, opcoes)
        assert d.action_id in {o.action_id for o in opcoes}

    def test_com_uma_opcao_so_a_decisao_e_ela(self):
        state = _estado()
        d = decidir_no_combate(state, (_pocao(),))
        assert d.action_id == "item:pocao"


class TestFronteiraDeInformacao:
    """Nenhum canal escondido do monstro está ativo.

    O que a ficha do confronto mostra é Nível, HP, MP, Força, Agilidade, Magia e
    Defesa. Tudo que o `CombatState` carrega do alvo reduz a isso mais regra
    pública — mas isso é verdade por conteúdo, não por construção. Este teste é o
    alarme: se um arquétipo ganhar passiva escondida ou resistência a status, o
    bot passaria a decidir com informação que o jogador não tem.
    """

    def test_nenhum_arquetipo_tem_modificador_de_combate_escondido(self):
        for papel in all_archetypes():
            for nivel in (1, 10, 20):
                monstro = create_monster("Alvo", nivel, papel)
                for tipo in ("crit_chance", "crit_damage", "damage_percent", "precision"):
                    assert fx.combat_modifier(monstro, tipo) == 0.0, (papel, nivel, tipo)

    def test_nenhum_arquetipo_tem_resistencia_a_status(self):
        efeitos = ("stun", "frozen", "sleep", "poison", "bleed", "weakened", "mana_burn")
        for papel in all_archetypes():
            monstro = create_monster("Alvo", 10, papel)
            for efeito in efeitos:
                assert fx.status_resistance(monstro, efeito) == 0.0, (papel, efeito)

    def test_o_estado_de_combate_nao_carrega_campo_novo_do_alvo_sem_revisao(self):
        """A ficha mostra sete linhas. Campo novo em `alvo_*` passa por aqui."""
        campos = {c for c in CombatState.__dataclass_fields__ if c.startswith("alvo_")}
        assert campos == {
            "alvo_nivel",
            "alvo_hp",
            "alvo_hp_max",
            "alvo_mp",
            "alvo_mp_max",
            "alvo_dano",
            "alvo_efeitos",
        }


class TestStatusDeAtributo:
    """15 cartas do catálogo atual chegavam como um turno gasto à toa."""

    def test_vulnerable_que_encurta_a_luta_vence_o_basico(self):
        state = _estado(alvo_hp=900, dano_basico=50, alvo_dano=20, hp=450)
        vulneravel = _opcao(
            "skill:vulneravel",
            "status",
            "Expor Fraqueza",
            statuses=_status("vulnerable", 1.0, duration=6, outgoing_damage_after=130),
            mana_cost=10,
        )
        d = decidir_no_combate(state, (_ataque(), vulneravel))
        assert d.action_id == "skill:vulneravel"

    def test_weakened_aparece_como_mitigacao(self):
        state = _estado(hp=120, alvo_dano=60, alvo_hp=600, dano_basico=50)
        fraco = _opcao(
            "skill:fraco",
            "status",
            "Enfraquecer",
            statuses=_status("weakened", 1.0, duration=4, incoming_damage_after=25),
            mana_cost=10,
        )
        componentes = dict(avaliar_combate(fraco, state).components)
        assert componentes["mitigação"] > 0

    def test_a_chance_do_status_desconta_a_consequencia(self):
        state = _estado(hp=120, alvo_dano=60, alvo_hp=600, dano_basico=50)

        def fraco(chance):
            return _opcao(
                "skill:fraco",
                "status",
                "Enfraquecer",
                statuses=_status("weakened", chance, duration=4, incoming_damage_after=25),
                mana_cost=10,
            )

        assert _nota(fraco(0.3), state) < _nota(fraco(1.0), state)


class TestDrenoDeRecurso:
    """`mana_burn` deixa de ser uma ação cujo efeito relevante vale zero."""

    def _dreno(self, drenado: int) -> ActionOption:
        return _opcao(
            "skill:dreno",
            "status",
            "Queima de Mana",
            statuses=_status("mana_burn", 1.0, duration=2, target_mp_drained=drenado),
            mana_cost=10,
        )

    def test_alvo_com_mp_cheio_vale_mais_que_alvo_seco(self):
        cheio = _estado(alvo_mp=40, alvo_mp_max=40, alvo_hp=600, dano_basico=50)
        seco = _estado(alvo_mp=0, alvo_mp_max=40, alvo_hp=600, dano_basico=50)
        assert _nota(self._dreno(40), cheio) > _nota(self._dreno(0), seco)

    def test_nunca_vale_mais_que_negar_todas_as_respostas_do_horizonte(self):
        state = _estado(alvo_mp=40, alvo_mp_max=40, alvo_hp=600, dano_basico=50, alvo_dano=40)
        componentes = dict(avaliar_combate(self._dreno(999), state).components)
        assert componentes["recurso negado"] <= state.turnos_para_morrer()


class TestGuardaDaInteracao:
    """`damage_xmult` é INFORMATIVO: o dano declarado já o contém."""

    def test_o_evaluator_nunca_multiplica_pelo_xmult_da_interacao(self):
        fonte = Path("src/sim/bot/evaluators.py").read_text(encoding="utf-8")
        assert "damage_xmult" not in fonte

    def test_a_nota_nao_muda_por_a_interacao_estar_declarada(self):
        from src.sim.bot.observation import InteractionView

        state = _estado(alvo_hp=600, dano_basico=50)
        lei = InteractionView(
            interaction_id="emboscada", label="Emboscada", kind="strike", damage_xmult=1.2
        )
        assert _nota(_ataque(interactions=(lei,)), state) == _nota(_ataque(), state)
