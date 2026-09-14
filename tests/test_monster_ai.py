"""Comportamento dos arquétipos de monstro e peso do ataque básico.

Duas coisas são testadas aqui, e elas são a mesma coisa vista de dois lados.

A primeira é o **valor do recurso**: enquanto o ataque básico entregava o poder
inteiro de graça e sem recarga, a skill mediana do jogo valia 1,65 ataque
gratuito. A linha ótima era não gastar nada, e não existe adaptação num combate
em que a melhor jogada é sempre a mesma. O teste fixa a razão mínima entre uma
skill de dano e um ataque básico — é uma regra de design, não um detalhe de
implementação, e é ela que impede o número de voltar a escorregar.

A segunda é a **intenção do monstro**. Um arquétipo só existe se o
comportamento dele mudar o combate. Os testes abaixo verificam que as quatro
jogadas decisivas acontecem quando devem e que furam a rolagem de
`skill_use_chance`: uma execução que depende de moeda não é uma execução.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.factories.archetypes import (  # noqa: E402
    all_archetypes,
    get_archetype,
    spawn_by_role,
)
from src.content.skills_loader import load_skills  # noqa: E402
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.mechanics import combat as combat_mech  # noqa: E402
from src.mechanics.monster_ai import _pick_skill, decide_monster_action  # noqa: E402
from src.shared.constants import BASIC_ATTACK_POWER_MULT  # noqa: E402

# Uma skill de dano precisa valer pelo menos isto em ataques básicos. Abaixo
# disso, gastar mana e recarga é matematicamente pior que não gastar nada.
#
# Começou em 1,4 — o que a skill mais barata entregava enquanto a tabela de
# preços tinha 13 pares dominados. Com a tabela arrumada, a pior razão do
# catálogo é 1,78 (Golpe Poderoso, a skill mais barata do Guerreiro no nível 1).
# O piso fica em 1,7 para deixar folga de arredondamento sem voltar a aceitar
# uma skill que não paga o próprio custo.
MIN_SKILL_TO_BASIC_RATIO = 1.7

# As três classes, para medir cada carta com quem de fato a usa.
CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


def _ferir(entidade, fracao: float) -> None:
    """Deixa a entidade com `fracao` da vida máxima."""
    alvo = max(1, int(entidade.base_hp * fracao))
    entidade.take_damage(entidade.get_hp() - alvo)


class TestPesoDoAtaqueBasico:
    def test_o_basico_e_uma_fracao_do_poder(self):
        heroi = Warrior("Teste")
        assert combat_mech.basic_attack_power(heroi) == int(
            heroi.get_avg_damage() * BASIC_ATTACK_POWER_MULT
        )
        assert combat_mech.basic_attack_power(heroi) < heroi.get_avg_damage()

    def test_os_dois_lados_usam_a_mesma_conta(self):
        """Nerfar só o herói seria balanceamento; nerfar só o monstro, presente."""
        monstro = spawn_by_role("bruiser", 5)
        assert combat_mech.basic_attack_power(monstro) == int(
            monstro.get_avg_damage() * BASIC_ATTACK_POWER_MULT
        )

    @pytest.mark.parametrize(
        "carta",
        [s for s in load_skills() if s.effect_type == "damage"],
        ids=lambda c: c.id,
    )
    def test_toda_skill_de_dano_vale_mais_que_bater(self, carta):
        """A regra que faz o recurso ser uma decisão, e não um imposto.

        A carta REAL, e não um boneco com `effect_value`. O boneco parou de
        medir o que este teste protege quando a skill passou a nascer dos
        atributos: sem `scaling` nem `power` ele caía no atalho de conteúdo não
        migrado, todas as 17 cartas mediam 1,11 — o inverso do multiplicador do
        ataque básico — e o teste virava uma checagem de constante.

        A carta é medida contra um herói DA CLASSE DELA, no nível em que ela
        aparece: `bola_fogo` escala com Magia e um Guerreiro a mediria fraca por
        um motivo que não é da carta. Neutral vale para os três, e o pior dos
        três é o que conta.
        """
        classes = [carta.skill_class] if carta.skill_class in CLASSES else sorted(CLASSES)
        for nome in classes:
            heroi = CLASSES[nome](f"Teste{nome}")
            heroi.set_level(max(1, carta.level_required))
            razao = combat_mech.skill_damage_base(heroi, carta) / combat_mech.basic_attack_power(
                heroi
            )
            assert razao >= MIN_SKILL_TO_BASIC_RATIO, (
                f"{carta.name} vale {razao:.2f} ataque básico para o {nome}: "
                "gastar mana e recarga é pior que não gastar nada"
            )

    def test_a_medicao_da_razao_usa_a_carta_e_nao_um_boneco(self):
        """Prova de carga: uma carta sem gramática V2 seria reprovada.

        É o defeito que o teste acima tinha. Ele fica registrado aqui para que
        voltar a medir um boneco seja uma falha, e não um verde silencioso.
        """
        heroi = Warrior("Teste")
        boneco = SimpleNamespace(effect_value=140, name="Boneco")
        razao = combat_mech.skill_damage_base(heroi, boneco) / combat_mech.basic_attack_power(heroi)
        assert razao < MIN_SKILL_TO_BASIC_RATIO

    def test_a_estimativa_do_bot_bate_com_o_motor(self):
        """Fórmula duplicada diverge no primeiro rebalanceamento."""
        from src.sim.policies import _estimate_basic_damage

        heroi = Warrior("Teste")
        alvo = spawn_by_role("trash", 3)
        mitigacao = 100 / (100 + alvo.get_df())
        esperado = max(1, int(combat_mech.basic_attack_power(heroi) * mitigacao))
        assert _estimate_basic_damage(heroi, alvo) == esperado


class TestJogadasDecisivas:
    """As quatro jogadas que furam `skill_use_chance`."""

    def test_execucao_com_o_heroi_quase_morto(self):
        monstro = spawn_by_role("glass_cannon", 8)
        heroi = Warrior("Teste")
        _ferir(heroi, 0.10)
        escolha, decisiva = _pick_skill(monstro, heroi, monstro.skills, random.Random(1))
        assert decisiva is True
        assert escolha.name == "Detonação Arcana", "a execução tem de buscar o maior dano"

    def test_a_execucao_vem_antes_da_cura(self):
        """Ordem das intenções: fechar a conta ganha de se curar.

        Nenhum arquétipo do jogo tem cura E dano ao mesmo tempo, então o
        suporte recebe aqui uma skill de dano emprestada do bruiser — o que se
        testa é a ordem dos ramos, não o catálogo.
        """
        monstro = spawn_by_role("support", 8)
        dano = next(s for s in spawn_by_role("bruiser", 8).skills if s.effect_type == "damage")
        monstro.skills.append(dano)

        heroi = Warrior("Teste")
        _ferir(heroi, 0.10)
        _ferir(monstro, 0.30)  # ferido o bastante para o ramo de cura disparar

        escolha, decisiva = _pick_skill(monstro, heroi, monstro.skills, random.Random(1))
        assert decisiva is True
        assert escolha.effect_type == "damage", "curou com o herói a um golpe da morte"

    def test_o_suporte_sem_dano_continua_curando(self):
        """O ramo de execução exige ter com que executar."""
        monstro = spawn_by_role("support", 8)
        assert not [s for s in monstro.skills if s.effect_type == "damage"]
        heroi = Warrior("Teste")
        _ferir(heroi, 0.10)
        _ferir(monstro, 0.30)
        escolha, _ = _pick_skill(monstro, heroi, monstro.skills, random.Random(1))
        assert escolha.effect_type == "heal"

    def test_o_suporte_ferido_se_cura(self):
        monstro = spawn_by_role("support", 8)
        heroi = Warrior("Teste")
        _ferir(monstro, 0.30)
        escolha, decisiva = _pick_skill(monstro, heroi, monstro.skills, random.Random(1))
        assert decisiva is True
        assert escolha.effect_type == "heal"

    def test_o_tank_no_desespero_se_fecha(self):
        monstro = spawn_by_role("tank", 8)
        heroi = Warrior("Teste")
        _ferir(monstro, 0.15)
        escolha, decisiva = _pick_skill(monstro, heroi, monstro.skills, random.Random(1))
        assert decisiva is True
        assert escolha.effect_type in ("damage_reduction", "buff")

    def test_o_bruiser_no_desespero_da_o_porrada0(self):
        """Quem não tem defesa gasta o maior dano antes de cair."""
        monstro = spawn_by_role("bruiser", 8)
        heroi = Warrior("Teste")
        _ferir(monstro, 0.15)
        escolha, decisiva = _pick_skill(monstro, heroi, monstro.skills, random.Random(1))
        assert decisiva is True
        assert escolha.effect_type == "damage"

    def test_o_tank_abre_se_fechando(self):
        monstro = spawn_by_role("tank", 8)
        escolha, decisiva = _pick_skill(monstro, Warrior("Teste"), monstro.skills, random.Random(1))
        assert decisiva is True
        assert escolha.effect_type in ("damage_reduction", "buff")

    def test_o_bruiser_nao_tem_abertura(self):
        """Abertura é identidade de quem vive de defesa, não de todo mundo."""
        monstro = spawn_by_role("bruiser", 8)
        _, decisiva = _pick_skill(monstro, Warrior("Teste"), monstro.skills, random.Random(1))
        assert decisiva is False

    def test_a_jogada_decisiva_ignora_a_moeda(self):
        """`skill_use_chance = 0` e ainda assim a execução acontece."""
        monstro = spawn_by_role("glass_cannon", 8)
        monstro.skill_use_chance = 0
        heroi = Warrior("Teste")
        _ferir(heroi, 0.10)
        mp_antes = monstro.get_mp()
        decide_monster_action(monstro, heroi, rng=random.Random(3), publish=None)
        assert monstro.get_mp() < mp_antes, "a execução caiu na moeda e virou tapa"


class TestTurnoDesperdicado:
    def test_nao_relanca_reducao_de_dano_ja_ativa(self):
        monstro = spawn_by_role("tank", 8)
        # A chave é o NOME DA SKILL, igual ao buff — é assim que a IA sabe que
        # a carta dela já está no ar.
        carapaca = next(s for s in monstro.skills if s.id == "mob_carapaca")
        monstro.active_buffs[carapaca.name] = {
            "stat": "damage_reduction",
            "value": 35,
            "duration": 3,
        }
        from src.mechanics.monster_ai import _usable_skills

        ids = {s.id for s in _usable_skills(monstro)}
        assert "mob_carapaca" not in ids

    def test_nao_relanca_buff_ja_ativo(self):
        monstro = spawn_by_role("bruiser", 8)
        monstro.active_buffs["Fúria"] = {"stat": "st", "value": 20, "duration": 3}
        from src.mechanics.monster_ai import _usable_skills

        ids = {s.id for s in _usable_skills(monstro)}
        assert "mob_furia" not in ids

    def test_o_kit_do_trash_continua_simples(self):
        """O trash ganhou repertório, e o contraste que ele protege é outro.

        Ele tinha zero skills, e o teste anterior travava isso. O contraste que
        importa nunca foi "não tem nada": é que o bicho de andar raso não rouba
        o turno do jogador. Perder a vez para um monstro descartável é a pior
        sensação que um combate pode dar, porque não há decisão a tomar contra
        ela — só esperar. Controle é do Controlador, e é para isso que ele existe.
        """
        from src.shared.effects import TURN_SKIPPING_STATUSES

        arquetipo = get_archetype("trash")
        assert arquetipo.skills, "o trash perdeu o kit inteiro"
        assert len(arquetipo.skills) <= 4, "o trash deixou de ser simples"
        for carta in arquetipo.skills:
            aplica = {str(carta.effect_value)}
            if carta.secondary:
                aplica.add(carta.secondary.effect)
            roubados = aplica & set(TURN_SKIPPING_STATUSES)
            assert not roubados, (
                f"{carta.id} deixa o trash roubar o turno do jogador ({roubados}); "
                "isso é papel do Controlador"
            )


class TestCatalogoDeArquetipos:
    def test_todo_arquetipo_com_moeda_tem_skill(self):
        """`skill_use_chance` sem skill é uma promessa que o combate não cumpre."""
        for papel, a in all_archetypes().items():
            if a.skill_use_chance:
                assert a.skills, f"{papel} sorteia uso de skill e não tem nenhuma"

    def test_todo_arquetipo_menos_o_trash_tem_ao_menos_duas_intencoes(self):
        """Uma skill só faz o papel depender da moeda cair na hora certa."""
        for papel, a in all_archetypes().items():
            if papel == "trash":
                continue
            assert len(a.skills) >= 2, f"{papel} tem {len(a.skills)} skill(s)"

    def test_todo_monstro_tem_mana_para_a_skill_mais_cara(self):
        for papel, a in all_archetypes().items():
            if not a.skills:
                continue
            monstro = spawn_by_role(papel, 1)
            mais_cara = max(int(s.mana_cost) for s in a.skills)
            assert monstro.get_mp() >= mais_cara, (
                f"{papel} nasce no nível 1 sem mana para a própria skill"
            )

    def test_papeis_defensivos_tem_com_que_se_fechar(self):
        from src.mechanics.monster_ai import DEFENSIVE_EFFECTS, DEFENSIVE_ROLES

        for papel in DEFENSIVE_ROLES:
            tipos = {s.effect_type for s in all_archetypes()[papel].skills}
            assert tipos & set(DEFENSIVE_EFFECTS), f"{papel} é defensivo e não se fecha"


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__, "-q"]))


class TestMonstroEscolheControlePorValor:
    """O monstro precisa comparar status, não pegar o primeiro do JSON.

    `_valor` lê `effect_value` numérico, e todo status tem nome no lugar do
    número (`"stun"`, `"fear"`, `"mana_burn"`). Devolvia 0 para todos, então
    `max(..., key=_valor)` retornava o primeiro elemento: a comparação existia na
    forma e não na prática.

    O `controller` era o caso grave — as três skills dele são status, e
    `monsters.json` declara `threat: "Nega turnos e recurso."`. Ele lançava
    sempre `Torpor` e nunca `Queima de Mana`, então negava turno e jamais
    recurso. O `counterplay` que o próprio JSON declara para ele ("não depender
    de MP") é exatamente a fraqueza da Égide do Mago, que ficava sem ser exercida.
    """

    @staticmethod
    def _controller():
        from src.content.factories.monsters import create_monster

        return create_monster("ctrl", 12, "controller")

    def test_status_deixa_de_empatar_em_zero(self):
        from src.mechanics.monster_ai import _valor_de_status

        monstro = self._controller()
        valores = {s.name: _valor_de_status(s) for s in monstro.skills}
        assert len(set(valores.values())) > 1, (
            f"todas as skills de status valem o mesmo ({valores}) — a escolha "
            "volta a ser a ordem do arquivo"
        )

    def test_a_escolha_segue_o_valor_e_nao_a_ordem_do_arquivo(self):
        from src.mechanics.monster_ai import _maior, _valor_de_status

        monstro = self._controller()
        # Só as cartas de status: é este o ramo de `_maior` que a regra protege,
        # e o Controlador passou a ter também uma carta de dano. Misturar os dois
        # tipos mediria outro caminho do código.
        skills = [s for s in monstro.skills if s.effect_type == "status"]
        assert len(skills) > 1, "o Controlador precisa de mais de um status para haver escolha"
        escolhida = _maior(skills, monstro)
        melhor = max(skills, key=_valor_de_status)
        assert escolhida is melhor
        assert escolhida is not skills[0] or _valor_de_status(skills[0]) == _valor_de_status(melhor)

    def test_roubar_turno_pesa_mais_que_enfraquecer(self):
        """A métrica é a mesma do herói: família × duração × chance."""
        from src.shared.effects import control_weight

        assert control_weight("stun") > control_weight("weakened")
        assert control_weight("poison") > control_weight("fear")


class TestMonstroNaoRelancaStatusAtivo:
    """Relançar um status que já está no alvo é turno e MP jogados fora.

    A regra já existia para `buff` e `damage_reduction` (`TestTurnoDesperdicado`),
    e `status` tinha ficado de fora do código e do teste — o mesmo padrão do
    `stun_chance` que faltava no ramo de status do motor.

    O status vive no ALVO, não em quem lança, então `_ja_esta_no_ar` precisava
    receber o alvo; antes ela só olhava o próprio monstro e era estruturalmente
    incapaz de ver isso.
    """

    @staticmethod
    def _controller():
        from src.content.factories.monsters import create_monster

        return create_monster("ctrl", 12, "controller")

    def test_status_ja_ativo_no_alvo_sai_das_usaveis(self):
        from src.mechanics.monster_ai import _usable_skills

        monstro = self._controller()
        heroi = Warrior("alvo")
        torpor = next(s for s in monstro.skills if str(s.effect_value) == "stun")

        assert torpor in _usable_skills(monstro, heroi)
        heroi.active_effects["stun"] = {"duration": 1}
        assert torpor not in _usable_skills(monstro, heroi), (
            "o monstro relança o atordoamento num herói já atordoado"
        )

    def test_as_outras_continuam_disponiveis(self):
        """Bloquear o repetido não pode calar o monstro."""
        from src.mechanics.monster_ai import _usable_skills

        monstro = self._controller()
        heroi = Warrior("alvo")
        heroi.active_effects["stun"] = {"duration": 1}
        assert _usable_skills(monstro, heroi), (
            "o monstro ficou sem jogada nenhuma por causa de um status ativo"
        )
