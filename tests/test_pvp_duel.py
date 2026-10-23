"""Duelo da Arena: decisões simultâneas, resolução sequencial, o PvE intacto.

Fixtures pequenas e sementes fixas. Nenhum teste aqui mede balanceamento: cada
um prova uma regra do motor com um ou poucos duelos determinísticos.

As referências de iniciativa daqui são uma tabela constante INJETADA, e não as
canônicas da fundação: com ela, dois níveis de diferença bastam para fixar quem
age primeiro entre classes diferentes, e cada teste que depende da ordem confere
a ordem antes de conferir a regra. O duelo pelo caminho normal, com as
referências canônicas, está em `test_pvp_references.py`.
"""

from __future__ import annotations

import copy
import dataclasses
import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.extraction import mark_extracted  # noqa: E402
from src.content.gladiator import GladiatorNotEligibleError, prepare_gladiator  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.skills_loader import get_skill_by_id  # noqa: E402
from src.engine.arena_setup import gladiator_from_snapshot  # noqa: E402
from src.mechanics import battle  # noqa: E402
from src.mechanics import combat as combat_mech  # noqa: E402
from src.mechanics.pvp_duel import (  # noqa: E402
    SIDES,
    Duel,
    DuelAction,
    DuelFinishedError,
    DuelView,
    Gladiator,
    InvalidDuelActionError,
    run_round,
)
from src.mechanics.pvp_initiative import (  # noqa: E402
    InitiativeReference,
    ReferenceTable,
    SeededCoinTieBreak,
)
from src.shared import combat_topics as T  # noqa: E402
from src.shared import effect_core as core  # noqa: E402
from src.shared.constants import MAX_BATTLE_TURNS, MP_REGEN_PERCENT_PER_TURN  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.pvp_controllers import FirstLegalSkillController, ScriptedController  # noqa: E402
from src.storage.save_manager import to_save_data  # noqa: E402

REFS = ReferenceTable(
    {n: InitiativeReference(hp=1000, mp=500, st=50, mg=50, ag=50, df=50) for n in range(1, 41)}
)
ATAQUE = DuelAction.attack()
RENDER = DuelAction.surrender()
# Teto do LAÇO DO TESTE, não do motor: o motor não tem teto nenhum.
LIMITE_DO_TESTE = 400


def skill(skill_id: str):
    return DuelAction.use_skill(skill_id)


def carta_certeira(skill_id: str):
    """A carta do catálogo com chance 100: o controle pega sem depender do RNG."""
    return dataclasses.replace(get_skill_by_id(skill_id), chance=100)


def heroi(classe: str, nivel: int, deck=(), loadout: str = "naked", nome: str | None = None):
    """Um personagem EXTRAÍDO, pronto para a Arena."""
    h = make_hero(classe, nivel, loadout)
    if nome:
        h.nick_name = nome
    if deck:
        h.skills = {
            i: (c if not isinstance(c, str) else get_skill_by_id(c))
            for i, c in enumerate(deck, start=1)
        }
    mark_extracted(h, nivel)
    return h


def duelo(h1, h2, *, seed: int = 1, publish=None) -> Duel:
    return Duel(
        prepare_gladiator(h1),
        prepare_gladiator(h2),
        references=REFS,
        tie_break=SeededCoinTieBreak(),
        rng=random.Random(seed),
        publish=publish,
    )


def jogar(d: Duel, a1: DuelAction, a2: DuelAction):
    return d.play_round({"p1": a1, "p2": a2})


def ate_o_fim(d: Duel, controladores) -> None:
    while not d.finished and d.round_number <= LIMITE_DO_TESTE:
        run_round(d, controladores)
    assert d.finished, f"o duelo não terminou em {LIMITE_DO_TESTE} rodadas"


def snapshot(classe: str, nivel: int, loadout: str = "expected") -> dict:
    h = make_hero(classe, nivel, loadout)
    mark_extracted(h, nivel)
    return to_save_data(h, nivel)


def passo(registro, lado):
    return next(p for p in registro.steps if p.side == lado)


def eventos(d: Duel, nome: str):
    return [e for e in d.events if e.name == nome]


# ---------------------------------------------------------------------------
# 1, 2 — duelos completos entre heróis reais
# ---------------------------------------------------------------------------


class TestDuelosCompletos:
    @pytest.mark.parametrize(
        ("a", "b"), [("Warrior", "Mage"), ("Mage", "Rogue"), ("Rogue", "Warrior")]
    )
    def test_confronto_entre_classes_termina_com_vencedor_por_ko(self, a, b):
        resultados = []
        for _ in range(2):
            d = Duel(
                gladiator_from_snapshot(snapshot(a, 10)),
                gladiator_from_snapshot(snapshot(b, 10)),
                references=REFS,
                tie_break=SeededCoinTieBreak(),
                rng=random.Random(2026),
            )
            ate_o_fim(d, {"p1": FirstLegalSkillController(), "p2": FirstLegalSkillController()})
            r = d.result
            vencedor, perdedor = d.hero(r.winner), d.hero(r.loser)
            assert r.reason == "ko"
            assert vencedor.get_isalive() and vencedor.get_hp() > 0
            assert not perdedor.get_isalive() and perdedor.get_hp() <= 0
            assert r.rounds == len(r.history) == len(d.history)
            assert {r.winner_name, r.loser_name} == {d.hero("p1").nick_name, d.hero("p2").nick_name}
            resultados.append((r.winner, r.rounds, [x.hp_end for x in r.history]))
        # Mesma semente, mesmos gladiadores: o MESMO duelo, rodada a rodada.
        assert resultados[0] == resultados[1]

    def test_mirror_match_do_mesmo_snapshot_sao_duas_instancias(self):
        base = snapshot("Rogue", 10)
        g1, g2 = gladiator_from_snapshot(base), gladiator_from_snapshot(base)
        assert g1.hero is not g2.hero
        d = Duel(g1, g2, references=REFS, tie_break=SeededCoinTieBreak(), rng=random.Random(5))
        ate_o_fim(d, {"p1": FirstLegalSkillController(), "p2": FirstLegalSkillController()})
        # Builds idênticas: score e AG relativa empatam, e quem decide a primeira
        # ordem é a política de desempate injetada.
        assert d.history[0].order.decided_by == "fallback"
        assert d.result.reason == "ko"
        assert d.hero(d.result.loser).get_hp() <= 0 < d.hero(d.result.winner).get_hp()

    def test_o_duelo_recusa_a_mesma_instancia_dos_dois_lados(self):
        g = prepare_gladiator(heroi("Warrior", 10))
        with pytest.raises(ValueError):
            Duel(g, Gladiator(g.hero), references=REFS, tie_break=SeededCoinTieBreak())

    def test_o_duelo_so_recebe_gladiador_preparado(self):
        with pytest.raises(TypeError):
            Duel(
                heroi("Warrior", 10),
                heroi("Mage", 10),
                references=REFS,
                tie_break=SeededCoinTieBreak(),
            )


# ---------------------------------------------------------------------------
# 3 — escolha simultânea sem vazamento
# ---------------------------------------------------------------------------


class TestEscolhaSimultanea:
    def _visao_do_p2(self, acao_do_p1):
        d = duelo(
            heroi("Warrior", 10, deck=("golpe_poderoso",)),
            heroi("Mage", 10, deck=("bola_fogo",)),
            seed=3,
        )
        p2 = ScriptedController([ATAQUE])
        run_round(d, {"p1": ScriptedController([acao_do_p1]), "p2": p2})
        return p2.views[0]

    def test_a_visao_de_um_lado_nao_depende_da_escolha_do_outro(self):
        visoes = {
            self._visao_do_p2(ATAQUE),
            self._visao_do_p2(skill("golpe_poderoso")),
            self._visao_do_p2(RENDER),
        }
        assert len(visoes) == 1

    def test_a_visao_nao_carrega_acao_adversaria_nem_iniciativa(self):
        campos = {f.name for f in dataclasses.fields(DuelView)}
        assert campos == {"round_number", "side", "me", "opponent", "legal_actions", "cooldowns"}

    def test_ambas_as_visoes_sao_montadas_antes_da_primeira_escolha(self):
        d = duelo(heroi("Warrior", 10), heroi("Mage", 10), seed=3)
        ordem: list[str] = []

        class Anota:
            def __init__(self, lado):
                self.lado = lado

            def choose(self, view):
                ordem.append(f"choose:{self.lado}")
                return ATAQUE

        original = d.view

        def view_anotada(lado):
            ordem.append(f"view:{lado}")
            return original(lado)

        d.view = view_anotada
        run_round(d, {"p1": Anota("p1"), "p2": Anota("p2")})
        assert ordem == ["view:p1", "view:p2", "choose:p1", "choose:p2"]

    def test_acao_ilegal_nao_muda_nada(self):
        d = duelo(heroi("Warrior", 10, deck=("golpe_poderoso",)), heroi("Mage", 10), seed=3)
        antes = (d.round_number, d.hero("p1").get_mp(), d.hero("p2").get_hp(), len(d.events))
        with pytest.raises(InvalidDuelActionError):
            jogar(d, skill("golpe_poderoso"), skill("nao_existe"))
        with pytest.raises(InvalidDuelActionError):
            d.play_round({"p1": ATAQUE})
        assert (d.round_number, d.hero("p1").get_mp(), d.hero("p2").get_hp(), len(d.events)) == (
            antes
        )


# ---------------------------------------------------------------------------
# 4 — iniciativa na ordem da rodada
# ---------------------------------------------------------------------------


class TestIniciativaNaRodada:
    @pytest.mark.parametrize("alto", SIDES)
    def test_maior_score_age_primeiro_em_qualquer_lado(self, alto):
        niveis = {alto: 12, ("p2" if alto == "p1" else "p1"): 10}
        d = duelo(heroi("Warrior", niveis["p1"]), heroi("Warrior", niveis["p2"]), seed=4)
        registro = jogar(d, ATAQUE, ATAQUE)
        leituras = {x.side: x for x in registro.initiative}
        baixo = "p2" if alto == "p1" else "p1"
        assert leituras[alto].score > leituras[baixo].score
        assert (registro.order.first, registro.order.decided_by) == (alto, "score")
        assert [p.side for p in registro.steps] == [alto, baixo]

    def test_recalculada_a_cada_rodada_com_atributos_efetivos(self):
        d = duelo(
            heroi("Rogue", 10, deck=("sombra_rapida",)),
            heroi("Rogue", 10, deck=(carta_certeira("joelho_torto"),)),
            seed=4,
        )
        r1 = jogar(d, skill("sombra_rapida"), ATAQUE)  # p1 ganha +AG (buff)
        r2 = jogar(d, ATAQUE, skill("joelho_torto"))  # p2 põe `slowed` em p1
        r3 = jogar(d, ATAQUE, ATAQUE)
        p1 = [{x.side: x for x in r.initiative}["p1"] for r in (r1, r2, r3)]
        assert p1[1].relative_ag > p1[0].relative_ag
        assert p1[1].score > p1[0].score
        assert p1[2].relative_ag < p1[1].relative_ag
        assert p1[2].score < p1[1].score

    def test_a_ordem_travada_nao_muda_dentro_da_rodada(self):
        """O primeiro lento o segundo; o segundo continua sendo o segundo."""
        d = duelo(
            heroi("Rogue", 12, deck=(carta_certeira("joelho_torto"),)),
            heroi("Rogue", 10),
            seed=4,
        )
        registro = jogar(d, skill("joelho_torto"), ATAQUE)
        assert registro.order.first == "p1"
        assert [p.side for p in registro.steps] == ["p1", "p2"]
        assert all(p.outcome == "executed" for p in registro.steps)

    def test_a_iniciativa_fica_fora_da_visao(self):
        d = duelo(heroi("Warrior", 12), heroi("Warrior", 10))
        texto = repr(d.view("p1")) + repr(d.view("p2"))
        assert "score" not in texto and "initiative" not in texto


# ---------------------------------------------------------------------------
# 6, 7, 8 — ação comprometida e MP reservado
# ---------------------------------------------------------------------------


class TestAcaoComprometida:
    def test_buff_aplicado_antes_do_ataque_adversario_entra_no_golpe(self):
        golpes = []

        def publish(topico, evento):
            if topico == T.COMBAT_PHYSICAL_STRIKE:
                defensor = evento.payload["defender"]
                golpes.append((defensor.nick_name, defensor.get_df(), set(defensor.active_buffs)))

        maga = heroi("Mage", 12, deck=("escudo_magico",), nome="Maga")
        df_sem_escudo = maga.get_df()
        d = duelo(maga, heroi("Warrior", 10), seed=6, publish=publish)
        registro = jogar(d, skill("escudo_magico"), ATAQUE)

        assert registro.order.first == "p1"
        assert [p.outcome for p in registro.steps] == ["executed", "executed"]
        escudo = get_skill_by_id("escudo_magico").name
        assert golpes, "o golpe do Guerreiro não aconteceu"
        nome, df_no_golpe, buffs = golpes[-1]
        assert nome == "Maga"
        assert escudo in buffs
        assert df_no_golpe > df_sem_escudo

    def test_mana_burn_drena_so_o_mp_livre_e_a_skill_reservada_resolve(self):
        drenos = []

        def publish(topico, evento):
            if evento.payload.get("kind") == "mana_burn_tick":
                drenos.append(evento.payload["amount"])

        d = duelo(
            heroi("Mage", 12, deck=("dreno_mana",)),
            heroi("Mage", 10, deck=("bola_fogo",)),
            seed=7,
            publish=publish,
        )
        vitima = d.hero("p2")
        custo = combat_mech.skill_mana_cost(vitima, get_skill_by_id("bola_fogo"))
        # A vítima trava a Bola de Fogo com EXATAMENTE o custo em caixa: depois
        # da reserva, o MP livre é zero. Sem reserva, o dreno a deixaria sem a
        # mana da skill.
        vitima._mp = custo
        hp_atacante = d.hero("p1").get_hp()

        registro = jogar(d, skill("dreno_mana"), skill("bola_fogo"))

        assert registro.order.first == "p1"
        assert core.has_effect(vitima, "mana_burn")
        assert drenos, "o dreno não foi processado na oportunidade da vítima"
        p2 = passo(registro, "p2")
        assert p2.outcome == "executed"
        assert p2.mp_reserved == p2.mp_spent == custo
        assert vitima.get_mp() == 0
        assert d.hero("p1").get_hp() <= hp_atacante

    @pytest.mark.parametrize("folga", [0, 50])
    def test_skill_desconta_o_mp_uma_unica_vez(self, folga):
        d = duelo(
            heroi("Warrior", 12, deck=("golpe_poderoso",)),
            heroi("Warrior", 10, deck=("escudo_protetor",)),
            seed=8,
        )
        guerreiro = d.hero("p1")
        teto = guerreiro.base_mp
        inicio = teto - folga
        guerreiro._mp = inicio
        custo = combat_mech.skill_mana_cost(guerreiro, get_skill_by_id("golpe_poderoso"))
        regen = int(max(1, teto * MP_REGEN_PERCENT_PER_TURN / 100))

        registro = jogar(d, skill("golpe_poderoso"), skill("escudo_protetor"))

        # A mesma conta do PvE: regenera até o teto, depois paga o custo uma vez.
        assert guerreiro.get_mp() == min(inicio + regen, teto) - custo
        p1 = passo(registro, "p1")
        assert p1.mp_reserved == p1.mp_spent == custo
        assert [e.detail for e in eventos(d, "mp_reserved") if e.side == "p1"] == [
            (("amount", custo),)
        ]

    def test_reserva_que_nao_cabe_no_mp_livre_e_recusada_no_lock(self):
        d = duelo(heroi("Warrior", 10, deck=("golpe_poderoso",)), heroi("Mage", 10))
        d.hero("p1")._mp = 0
        assert skill("golpe_poderoso") not in d.legal_actions("p1")
        with pytest.raises(InvalidDuelActionError):
            jogar(d, skill("golpe_poderoso"), ATAQUE)


# ---------------------------------------------------------------------------
# 9 — controle: antes e depois da ação pendente, com a duração declarada
# ---------------------------------------------------------------------------

# Carta de controle e duração declarada no catálogo.
CONTROLES = {
    "stun": ("fortalecimento", 1),
    "frozen": ("raio_congelante", 2),
    "sleep": ("sono_profundo", 3),
}
# Ações do aplicador depois do controle: nenhuma causa dano, então nem o sono
# (que quebra com dano) é interrompido antes do fim.
BUFFS_DO_APLICADOR = ("escudo_magico", "foco_do_estudante", "veias_de_eter")


class TestControle:
    def _duelo(self, controle: str, aplicador_primeiro: bool):
        carta_id, duracao = CONTROLES[controle]
        assert get_skill_by_id(carta_id).duration == duracao
        assert get_skill_by_id(carta_id).effect_value == controle
        aplicador = heroi(
            "Mage",
            12 if aplicador_primeiro else 10,
            deck=(carta_certeira(carta_id), *BUFFS_DO_APLICADOR),
        )
        vitima = heroi("Warrior", 10 if aplicador_primeiro else 12)
        d = duelo(aplicador, vitima, seed=9)
        roteiro = [skill(carta_id), *(skill(b) for b in BUFFS_DO_APLICADOR)]
        registros = [jogar(d, acao, ATAQUE) for acao in roteiro]
        esperado_primeiro = "p1" if aplicador_primeiro else "p2"
        assert all(r.order.first == esperado_primeiro for r in registros)
        return [passo(r, "p2").outcome for r in registros], duracao

    @pytest.mark.parametrize("controle", sorted(CONTROLES))
    def test_aplicado_antes_da_acao_pendente_cancela_ela(self, controle):
        desfechos, duracao = self._duelo(controle, aplicador_primeiro=True)
        # A oportunidade desta rodada é a primeira das `duracao` perdidas.
        assert desfechos[:duracao] == ["cancelled_control"] * duracao
        assert desfechos[duracao] == "executed"
        assert desfechos.count("cancelled_control") == duracao

    @pytest.mark.parametrize("controle", sorted(CONTROLES))
    def test_aplicado_depois_que_a_vitima_agiu_pega_a_proxima(self, controle):
        desfechos, duracao = self._duelo(controle, aplicador_primeiro=False)
        assert desfechos[0] == "executed"
        assert desfechos[1 : 1 + duracao] == ["cancelled_control"] * duracao
        assert desfechos.count("cancelled_control") == duracao

    def test_acao_cancelada_por_controle_devolve_a_reserva(self):
        d = duelo(
            heroi("Mage", 12, deck=(carta_certeira("fortalecimento"),)),
            heroi("Warrior", 10, deck=("golpe_poderoso",)),
            seed=9,
        )
        guerreiro = d.hero("p2")
        mp_antes = guerreiro.get_mp()
        registro = jogar(d, skill("fortalecimento"), skill("golpe_poderoso"))
        assert passo(registro, "p2").outcome == "cancelled_control"
        assert guerreiro.get_mp() == mp_antes  # cheio antes, cheio depois
        assert guerreiro.skill_cooldowns == {}
        assert [e.side for e in eventos(d, "mp_refunded")] == ["p2"]

    def test_efeito_aplicado_pelo_primeiro_nao_interrompe_a_acao_pendente(self):
        d = duelo(
            heroi("Mage", 12, deck=(carta_certeira("dreno_mana"),)),
            heroi("Warrior", 10, deck=("golpe_poderoso",)),
            seed=9,
        )
        registro = jogar(d, skill("dreno_mana"), skill("golpe_poderoso"))
        assert core.has_effect(d.hero("p2"), "mana_burn")
        assert passo(registro, "p2").outcome == "executed"

    @pytest.mark.parametrize(
        "efeito",
        ["fear", "poison", "bleed", "mana_burn", "slowed", "weakened", "hexed", "vulnerable"],
    )
    def test_efeito_comum_ativo_nao_cancela_a_acao(self, efeito):
        d = duelo(heroi("Warrior", 12), heroi("Warrior", 10, deck=("golpe_poderoso",)), seed=9)
        core.apply_effect(d.hero("p2"), efeito, source_id="teste")
        registro = jogar(d, ATAQUE, skill("golpe_poderoso"))
        assert passo(registro, "p2").outcome == "executed"

    def test_buff_defensivo_nao_cancela_a_acao(self):
        d = duelo(
            heroi("Warrior", 12, deck=("escudo_protetor", "couraca_improvisada")),
            heroi("Warrior", 10),
            seed=9,
        )
        jogar(d, skill("escudo_protetor"), ATAQUE)
        registro = jogar(d, skill("couraca_improvisada"), ATAQUE)
        assert [p.outcome for p in registro.steps] == ["executed", "executed"]


# ---------------------------------------------------------------------------
# 10, 11 — morte, rendição e desfechos externos
# ---------------------------------------------------------------------------


class TestFimDoDuelo:
    def test_golpe_letal_cancela_a_acao_pendente_do_morto(self):
        # Vítima sem Égide: a mana dela só pode mudar pela própria skill.
        d = duelo(heroi("Warrior", 12), heroi("Warrior", 10, deck=("golpe_poderoso",)), seed=10)
        d.hero("p2")._hp = 1
        mp_antes = d.hero("p2").get_mp()
        registro = jogar(d, ATAQUE, skill("golpe_poderoso"))
        assert registro.order.first == "p1"
        assert passo(registro, "p1").outcome == "executed"
        assert passo(registro, "p2").outcome == "cancelled_death"
        assert d.result.winner == "p1" and d.result.reason == "ko"
        assert d.hero("p2").get_mp() == mp_antes  # a reserva voltou; a skill não saiu
        assert not [e for e in eventos(d, "action_executed") if e.side == "p2"]

    def test_morte_no_comeco_da_propria_oportunidade_encerra_antes_do_outro(self):
        d = duelo(heroi("Warrior", 12), heroi("Warrior", 10), seed=10)
        primeiro = d.hero("p1")
        primeiro._hp = 1
        core.apply_effect(primeiro, "poison", source_id="teste")
        hp_do_outro = d.hero("p2").get_hp()
        registro = jogar(d, ATAQUE, ATAQUE)
        assert registro.order.first == "p1"
        assert [p.outcome for p in registro.steps] == ["cancelled_death", "not_reached"]
        assert d.result.winner == "p2" and d.result.reason == "ko"
        assert d.hero("p2").get_hp() == hp_do_outro

    def test_nada_acontece_depois_do_fim(self):
        d = duelo(heroi("Warrior", 12), heroi("Mage", 10), seed=10)
        d.hero("p2")._hp = 1
        jogar(d, ATAQUE, ATAQUE)
        assert d.finished
        with pytest.raises(DuelFinishedError):
            jogar(d, ATAQUE, ATAQUE)
        with pytest.raises(DuelFinishedError):
            d.forfeit("p1", "timeout")

    def test_rendicao_e_derrota_imediata_sem_golpe_nenhum(self):
        d = duelo(heroi("Warrior", 12), heroi("Mage", 10), seed=11)
        hp = {lado: d.hero(lado).get_hp() for lado in SIDES}
        registro = jogar(d, RENDER, ATAQUE)
        assert (d.result.winner, d.result.loser, d.result.reason) == ("p2", "p1", "surrender")
        assert [p.outcome for p in registro.steps] == ["not_reached", "not_reached"]
        assert {lado: d.hero(lado).get_hp() for lado in SIDES} == hp
        assert not eventos(d, "action_executed")

    def test_quem_esta_atordoado_ainda_pode_se_render(self):
        d = duelo(heroi("Warrior", 12), heroi("Mage", 10), seed=11)
        core.apply_effect(d.hero("p2"), "stun", source_id="teste")
        jogar(d, ATAQUE, RENDER)
        assert (d.result.winner, d.result.reason) == ("p1", "surrender")

    def test_rendicao_simultanea_resolve_pela_ordem_travada(self):
        d = duelo(heroi("Warrior", 12), heroi("Warrior", 10), seed=11)
        registro = jogar(d, RENDER, RENDER)
        assert registro.order.first == "p1"
        assert (d.result.loser, d.result.reason) == ("p1", "surrender")
        assert eventos(d, "surrender")[0].detail == (("simultaneous", True),)

    @pytest.mark.parametrize("motivo", ["timeout", "disconnect"])
    def test_desfecho_externo_e_derrota_de_quem_o_sofreu(self, motivo):
        d = duelo(heroi("Warrior", 10), heroi("Mage", 10))
        jogar(d, ATAQUE, ATAQUE)
        resultado = d.forfeit("p2", motivo)
        assert (resultado.winner, resultado.loser, resultado.reason) == ("p1", "p2", motivo)
        assert resultado.rounds == 1

    def test_desfecho_externo_desconhecido_e_recusado(self):
        d = duelo(heroi("Warrior", 10), heroi("Mage", 10))
        with pytest.raises(ValueError):
            d.forfeit("p1", "surrender")
        with pytest.raises(ValueError):
            d.forfeit("p1", "draw")
        assert not d.finished


# ---------------------------------------------------------------------------
# 12 — recarga, cura e regeneração pelo motor de sempre
# ---------------------------------------------------------------------------


class TestMecanicasExistentes:
    @pytest.mark.parametrize("carta", ["golpe_poderoso", "escudo_protetor"])
    def test_recarga_bloqueia_exatamente_as_oportunidades_declaradas(self, carta):
        recarga = get_skill_by_id(carta).cooldown
        d = duelo(heroi("Warrior", 12, deck=(carta,)), heroi("Warrior", 10), seed=12)
        jogar(d, skill(carta), ATAQUE)
        bloqueadas = 0
        while skill(carta) not in d.legal_actions("p1"):
            with pytest.raises(InvalidDuelActionError):
                jogar(d, skill(carta), ATAQUE)
            jogar(d, ATAQUE, ATAQUE)
            bloqueadas += 1
            assert bloqueadas <= recarga
        assert bloqueadas == recarga
        assert passo(jogar(d, skill(carta), ATAQUE), "p1").outcome == "executed"

    def test_cura_da_skill(self):
        d = duelo(
            heroi("Mage", 10, deck=("drenar_vida",)),
            heroi("Warrior", 10, deck=("escudo_protetor",)),
            seed=12,
        )
        maga = d.hero("p1")
        maga._hp = maga.base_hp // 2
        antes = maga.get_hp()
        cura = max(1, int(maga.base_hp * get_skill_by_id("drenar_vida").effect_value / 100))
        jogar(d, skill("drenar_vida"), skill("escudo_protetor"))
        assert maga.get_hp() == min(maga.base_hp, antes + cura)

    def test_regeneracao_de_mp_por_oportunidade(self):
        d = duelo(
            heroi("Warrior", 10),
            heroi("Warrior", 10, deck=("escudo_protetor",)),
            seed=12,
        )
        guerreiro = d.hero("p1")
        guerreiro._mp = 0
        regen = int(max(1, guerreiro.base_mp * MP_REGEN_PERCENT_PER_TURN / 100))
        jogar(d, ATAQUE, skill("escudo_protetor"))
        assert guerreiro.get_mp() == regen
        jogar(d, ATAQUE, ATAQUE)
        assert guerreiro.get_mp() == 2 * regen


# ---------------------------------------------------------------------------
# 13, 14, 15 — consumíveis, preparação e o personagem salvo intacto
# ---------------------------------------------------------------------------


def _pocao():
    return next(i for i in get_all_items().values() if i.is_potion)


class TestConsumiveisProibidos:
    def test_a_preparacao_tira_todo_consumivel(self):
        h = heroi("Warrior", 10)
        h.inventory.append(copy.deepcopy(_pocao()))
        g = prepare_gladiator(h)
        assert not [i for i in g.hero.inventory if i.is_potion]
        assert [i for i in h.inventory if i.is_potion]

    def test_nao_existe_acao_de_item_nem_de_fuga(self):
        d = duelo(heroi("Warrior", 10), heroi("Mage", 10))
        assert {a.kind for a in d.legal_actions("p1")} <= {"attack", "skill", "surrender"}
        pocao = _pocao()
        for proibida in (
            battle.Action(kind="item", item=pocao),
            battle.Action(kind="flee"),
            battle.Action(kind="attack"),
            DuelAction("item"),  # type: ignore[arg-type]
            DuelAction("flee"),  # type: ignore[arg-type]
        ):
            with pytest.raises(InvalidDuelActionError):
                jogar(d, proibida, ATAQUE)
        assert d.round_number == 1


class TestPreparacao:
    def _ferido_da_dungeon(self):
        h = heroi("Mage", 10, deck=("bola_fogo",))
        h._hp = 3
        h._mp = 1
        core.apply_effect(h, "poison", source_id="monstro")
        core.apply_effect(h, "vitality", source_id="altar")
        h.active_buffs["Altar"] = {"stat": "mg", "value": 9, "duration": 4}
        h.skill_cooldowns["bola_fogo"] = 2
        h._death_ignore_used = True
        return h

    def test_restaura_recursos_e_remove_o_que_era_da_run(self):
        original = self._ferido_da_dungeon()
        g = prepare_gladiator(original)
        h = g.hero
        assert h is not original
        assert not h.active_effects and not h.active_buffs and not h.skill_cooldowns
        assert h.get_hp() == h.base_hp and h.get_mp() == h.base_mp
        assert h._death_ignore_used is False and h.get_isalive()
        # O permanente fica.
        assert (h.get_classname(), h.get_level()) == (original.get_classname(), original.level)
        assert h.active_skill_ids() == original.active_skill_ids()

    def test_nao_toca_o_personagem_de_origem(self):
        original = self._ferido_da_dungeon()
        antes = (
            original.get_hp(),
            original.get_mp(),
            copy.deepcopy(original.active_effects),
            copy.deepcopy(original.active_buffs),
            dict(original.skill_cooldowns),
        )
        prepare_gladiator(original)
        assert (
            original.get_hp(),
            original.get_mp(),
            original.active_effects,
            original.active_buffs,
            original.skill_cooldowns,
        ) == antes

    def test_so_entra_quem_foi_extraido(self):
        vivo_na_dungeon = make_hero("Warrior", 10, "naked")
        with pytest.raises(GladiatorNotEligibleError):
            prepare_gladiator(vivo_na_dungeon)
        dados = to_save_data(vivo_na_dungeon, 10)
        with pytest.raises(GladiatorNotEligibleError):
            gladiator_from_snapshot(dados)

    def test_death_ignore_vale_uma_vez_por_duelo(self):
        h = heroi("Warrior", 10)
        h._death_ignore_used = True
        d = duelo(h, heroi("Warrior", 10))
        assert d.hero("p1")._death_ignore_used is False


class TestPersonagemSalvoIntacto:
    def test_snapshot_e_inventario_original_sobrevivem_ao_duelo(self):
        h = make_hero("Warrior", 10, "expected")
        h.inventory.append(copy.deepcopy(_pocao()))
        h._hp = h.base_hp // 3
        core.apply_effect(h, "bleed", source_id="monstro")
        h.active_buffs["Altar"] = {"stat": "st", "value": 5, "duration": 2}
        mark_extracted(h, 10)
        dados = to_save_data(h, 10)
        # Estado legado que a reconstrução migra: sem a cópia, ela o tiraria do
        # snapshot de quem chamou.
        dados["active_effects"]["damage_reduction"] = {"value": 10, "duration": 2}
        intocado = copy.deepcopy(dados)

        d = Duel(
            gladiator_from_snapshot(dados),
            gladiator_from_snapshot(snapshot("Mage", 10)),
            references=REFS,
            tie_break=SeededCoinTieBreak(),
            rng=random.Random(15),
        )
        ate_o_fim(d, {"p1": FirstLegalSkillController(), "p2": FirstLegalSkillController()})

        assert dados == intocado
        assert any(registro and registro.get("name") for registro in dados["inventory"])

    def test_o_personagem_em_memoria_sai_do_duelo_como_entrou(self):
        h = heroi("Rogue", 10, loadout="expected")
        h.inventory.append(copy.deepcopy(_pocao()))
        retrato = (
            h.get_hp(),
            h.get_mp(),
            list(h.inventory),
            dict(h.equipment),
            h.active_skill_ids(),
            [p.id for p in h.passives],
            h.get_st(),
            h.get_df(),
        )
        g = prepare_gladiator(h)
        d = Duel(
            g,
            prepare_gladiator(heroi("Warrior", 10, loadout="expected")),
            references=REFS,
            tie_break=SeededCoinTieBreak(),
            rng=random.Random(15),
        )
        ate_o_fim(d, {"p1": FirstLegalSkillController(), "p2": FirstLegalSkillController()})
        assert (
            h.get_hp(),
            h.get_mp(),
            list(h.inventory),
            dict(h.equipment),
            h.active_skill_ids(),
            [p.id for p in h.passives],
            h.get_st(),
            h.get_df(),
        ) == retrato
        # E a instância do duelo não mudou o que é permanente.
        assert g.hero.active_skill_ids() == h.active_skill_ids()
        assert [p.id for p in g.hero.passives] == [p.id for p in h.passives]
        assert list(g.hero.equipment) == list(h.equipment)


# ---------------------------------------------------------------------------
# 16 — sem teto de rodadas
# ---------------------------------------------------------------------------


class TestSemTetoDeRodadas:
    def test_o_duelo_passa_do_teto_do_pve_sem_ser_encerrado(self):
        d = duelo(heroi("Warrior", 10), heroi("Warrior", 10), seed=16)
        for lado in SIDES:
            d.hero(lado)._hp = 10**9  # ninguém cai: só o laço conta as rodadas
        alvo = MAX_BATTLE_TURNS + 25
        while d.round_number <= alvo:
            jogar(d, ATAQUE, ATAQUE)
        assert not d.finished
        assert len(d.history) == alvo
        jogar(d, RENDER, ATAQUE)
        assert d.result.reason == "surrender" and d.result.rounds == alvo + 1
