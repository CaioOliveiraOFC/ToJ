"""Catálogo de skills: carga, skills iniciais e geração de escolhas.

Este arquivo já existiu com quatro testes que só chamavam `print()`. Eles
passavam desde que nada levantasse exceção — quatro testes verdes que não
verificavam nada, e um `__main__` que imprimia "todos os testes passaram" sem
ter checado uma linha. Cada `print` daqui virou a asserção do que ele mostrava.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.content.skills_loader import (  # noqa: E402
    generate_skill_choices,
    get_initial_skills,
    get_skills_for_class,
    load_skills,
)
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.shared.constants import INITIAL_SKILL_LEVELS  # noqa: E402

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


def test_catalogo_carrega_sem_id_repetido():
    skills = load_skills()
    assert skills, "nenhuma skill carregada"
    ids = [s.id for s in skills]
    assert len(ids) == len(set(ids)), "id de skill repetido no JSON"


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_toda_classe_tem_skills_iniciais(classe):
    iniciais = get_initial_skills(classe)
    assert iniciais, f"{classe} não tem skill inicial"
    assert all(s.is_initial for s in iniciais)
    assert all(s.skill_class == classe for s in iniciais)
    assert len(iniciais) == INITIAL_SKILL_LEVELS, (
        f"{classe} tem {len(iniciais)} iniciais e o herói aprende uma por nível "
        f"até o {INITIAL_SKILL_LEVELS}: alguém ficaria com slot vazio ou skill sobrando."
    )


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_escolhas_sao_unicas_e_da_classe(classe):
    escolhas = generate_skill_choices(classe, player_level=11, player_skill_ids=[], count=3)
    assert len(escolhas) == 3
    assert len({s.id for s in escolhas}) == 3, "a mesma carta foi oferecida duas vezes"
    for skill in escolhas:
        assert skill.skill_class == classe
        assert not skill.is_initial, "skill inicial não deve aparecer no menu de escolha"
        assert skill.level_required <= 11, "carta acima do nível do herói foi oferecida"


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_o_menu_so_enche_a_partir_do_nivel_9(classe):
    """O catálogo não sustenta um menu de três cartas quando ele começa.

    `SKILL_CHOICE_MIN_LEVEL` é 5, e no nível 5 existem só duas cartas
    candidatas nas três classes: a primeira escolha do jogo mostra duas opções
    num menu de três. No nível 7 são exatamente três — escolher entre todas as
    cartas que existem não é escolher. Só a partir do 9 há mais candidatas que
    vagas.

    Isto é lacuna de conteúdo, não defeito de código: `generate_skill_choices`
    devolve o que existe. O teste fixa o número para que subir o catálogo
    apareça aqui em vez de passar despercebido.
    """
    candidatas = {
        nivel: len(
            [
                s
                for s in get_skills_for_class(classe)
                if not s.is_initial and s.level_required <= nivel
            ]
        )
        for nivel in (5, 7, 9)
    }
    assert candidatas == {5: 2, 7: 3, 9: 4}, (
        f"{classe}: o catálogo mudou ({candidatas}). Se aumentou, o menu do "
        "nível 5 finalmente oferece escolha — atualize este número."
    )
    assert len(generate_skill_choices(classe, 5, [], count=3)) == candidatas[5]


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_escolha_nunca_repete_o_que_o_heroi_ja_tem(classe):
    disponiveis = [
        s for s in get_skills_for_class(classe) if not s.is_initial and s.level_required <= 20
    ]
    conhecidas = [s.id for s in disponiveis[:2]]
    escolhas = generate_skill_choices(classe, 20, conhecidas, count=3)
    assert not ({s.id for s in escolhas} & set(conhecidas))


@pytest.mark.parametrize("classe,cls", sorted(CLASSES.items()))
def test_subir_de_nivel_entrega_a_proxima_skill_inicial(classe, cls):
    heroi = cls("Teste")
    antes = dict(heroi.skills)
    heroi.level = heroi.level + 1
    mensagens = heroi.learn_new_skills(show=True)

    assert len(heroi.skills) == len(antes) + 1, "subir de nível não entregou skill nova"
    assert mensagens, "o herói aprendeu uma skill e não avisou ninguém"
    nova = set(heroi.skills.values()) - set(antes.values())
    assert len(nova) == 1
    assert next(iter(nova)).is_initial


# --- Regras de design da tabela de preços --------------------------------
#
# O primeiro scout registrou "escolher skill vale -0,2 andar", "10 skills
# recusadas por toda intenção" e "3 escolhidas e nunca usadas", e por três
# rodadas isso ficou anotado como conteúdo fraco. Não era. A tabela de preços
# não era monótona: `golpe_devastador` (nível 10, 50%, 30 MP, recarga 3) perdia
# em TODOS os eixos para `golpe_poderoso` (nível 1, 60%, 15 MP, recarga 1).
# Eram 13 pares nessa situação. Metade do catálogo era matematicamente pior que
# o que o jogador já tinha na mão, e nenhum bot ia escolher pior de propósito.
#
# As três regras abaixo são o que impede isso de voltar. Elas valem sobre os
# dados, não sobre o motor — é uma regra de conteúdo, e é onde o defeito estava.

SKILLS_DE_DANO = [s for s in load_skills() if s.effect_type == "damage"]
CLASSES_COM_DANO = sorted({s.skill_class for s in SKILLS_DE_DANO})
assert SKILLS_DE_DANO, "nenhuma skill de dano carregada: os testes abaixo não rodariam."


def _eficiencia(skill) -> float:
    return int(skill.effect_value) / max(1, int(skill.mana_cost))


@pytest.mark.parametrize("classe", CLASSES_COM_DANO)
def test_nenhuma_skill_de_dano_e_dominada(classe):
    """Nenhuma skill pode custar mais e entregar menos que outra da classe.

    "Custar mais" é o conjunto: mais mana, mais recarga e mais nível exigido.
    Uma carta dominada nesses três eixos não é uma escolha difícil — é uma
    escolha errada, e oferecê-la ao jogador gasta um slot do menu.

    Os dois lados da comparação mudaram de campo e a regra teve de acompanhar,
    senão ela passa a medir outra coisa:

    - o custo é `mana_cost_percent`, não `mana_cost`. O absoluto ficou como
      valor de conteúdo não migrado, e comparar dois números em unidades
      diferentes deixaria a dominação passar despercebida;
    - o poder é um INTERVALO. Com condição situacional, a mesma carta entrega
      `effect_value` quando a situação não ajuda e `+ bonus_percent` quando
      ajuda. Dominar exige entregar mais nas duas pontas: uma carta que perde no
      piso e ganha no teto não é pior, é outra aposta — e é exatamente a decisão
      que a condição existe para criar.
    """
    da_classe = [s for s in SKILLS_DE_DANO if s.skill_class == classe]

    def piso(s) -> int:
        return int(s.effect_value)

    def teto(s) -> int:
        return int(s.effect_value) + int(getattr(s, "bonus_percent", 0) or 0)

    def custo(s) -> float:
        return float(getattr(s, "mana_cost_percent", 0) or 0) or float(s.mana_cost)

    for a in da_classe:
        for b in da_classe:
            if a is b:
                continue
            pior_ou_igual = (
                piso(a) <= piso(b)
                and teto(a) <= teto(b)
                and custo(a) >= custo(b)
                and int(a.cooldown) >= int(b.cooldown)
                and int(a.level_required) >= int(b.level_required)
            )
            estritamente_pior = (
                piso(a) < piso(b)
                or teto(a) < teto(b)
                or custo(a) > custo(b)
                or int(a.cooldown) > int(b.cooldown)
            )
            assert not (pior_ou_igual and estritamente_pior), (
                f"{a.id} (nv {a.level_required}, {piso(a)}-{teto(a)}%, "
                f"{custo(a):.2f} de mana, recarga {a.cooldown}) é dominada por "
                f"{b.id} (nv {b.level_required}, {piso(b)}-{teto(b)}%, "
                f"{custo(b):.2f} de mana, recarga {b.cooldown})"
            )


@pytest.mark.parametrize("classe", CLASSES_COM_DANO)
def test_a_skill_aprendida_bate_a_inicial(classe):
    """Subir de nível tem de entregar mais poder que o kit de partida.

    Sem esta regra, o kit inicial é o kit final: era o caso das doze skills
    aprendidas do jogo, todas com dano abaixo da melhor skill de nível 1 da
    própria classe.
    """
    da_classe = [s for s in SKILLS_DE_DANO if s.skill_class == classe]
    iniciais = [s for s in da_classe if int(s.level_required) <= 1]
    aprendidas = [s for s in da_classe if int(s.level_required) > 1]
    if not iniciais or not aprendidas:
        pytest.skip(f"{classe} não tem os dois grupos")

    teto = max(int(s.effect_value) for s in iniciais)
    for s in aprendidas:
        assert int(s.effect_value) > teto, (
            f"{s.id} é aprendida no nível {s.level_required} e entrega "
            f"{s.effect_value}%, abaixo dos {teto}% que a classe já tem no nível 1"
        )


@pytest.mark.parametrize("classe", CLASSES_COM_DANO)
def test_o_dano_cresce_com_o_nivel_exigido(classe):
    """Duas skills da mesma classe: a de nível maior entrega mais.

    É a promessa que o menu de escolha faz ao jogador. Quebrá-la transforma a
    escolha num teste de memória sobre quais cartas são armadilha.
    """
    da_classe = sorted(
        (s for s in SKILLS_DE_DANO if s.skill_class == classe),
        key=lambda s: int(s.level_required),
    )
    for anterior, seguinte in zip(da_classe, da_classe[1:]):
        if int(anterior.level_required) == int(seguinte.level_required):
            continue
        assert int(seguinte.effect_value) > int(anterior.effect_value), (
            f"{seguinte.id} (nv {seguinte.level_required}) entrega "
            f"{seguinte.effect_value}%, não mais que {anterior.id} "
            f"(nv {anterior.level_required}, {anterior.effect_value}%)"
        )


def test_a_recarga_longa_e_paga_em_eficiencia():
    """Recarga longa tem de render mais por mana, senão é só a mesma coisa mais rara.

    Não é uma ordenação estrita: o kit de nível 1 é barato de propósito, para
    ter função de preenchimento entre recargas. A regra é sobre as aprendidas.
    """
    aprendidas = [s for s in SKILLS_DE_DANO if int(s.level_required) > 1]
    curtas = [_eficiencia(s) for s in aprendidas if int(s.cooldown) <= 2]
    longas = [_eficiencia(s) for s in aprendidas if int(s.cooldown) >= 4]
    if not curtas or not longas:
        pytest.skip("catálogo sem os dois grupos")
    assert min(longas) > max(curtas), (
        "a skill de recarga longa não rende mais dano por mana que a de recarga curta: "
        "trocar frequência por pico fica sem contrapartida"
    )
