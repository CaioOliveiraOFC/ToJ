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
        nivel: len([
            s for s in get_skills_for_class(classe)
            if not s.is_initial and s.level_required <= nivel
        ])
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
