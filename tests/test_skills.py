"""Catálogo de skills: carga, aquisição e as regras de preço da tabela.

Este arquivo já existiu com quatro testes que só chamavam `print()`. Eles
passavam desde que nada levantasse exceção — quatro testes verdes que não
verificavam nada, e um `__main__` que imprimia "todos os testes passaram" sem
ter checado uma linha. Cada `print` daqui virou a asserção do que ele mostrava.

Com a V2 as regras de preço mudaram de UNIDADE. `effect_value` era o dano da
carta e agora é sempre zero: a carta diz de quais atributos o golpe nasce, e o
número sai do personagem. Toda comparação de poder aqui passou a usar
`offensive_budget`, que é o dano da carta em % do ataque básico de um
personagem de REFERÊNCIA da classe dela — a única medida comparável entre um
Guerreiro de Força 191 e um Ladino de Agilidade 92.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.content.skill_validator import offensive_budget  # noqa: E402
from src.content.skills_loader import (  # noqa: E402
    NEUTRAL,
    generate_skill_choices,
    get_initial_skills,
    get_offer_pool,
    get_skills_for_class,
    load_skills,
)
from src.entities.heroes import Mage, Rogue, Warrior  # noqa: E402
from src.shared.constants import (  # noqa: E402
    MAX_ACTIVE_SKILLS,
    SKILL_OFFER_LEVEL_INTERVAL,
    SKILL_OFFER_SIZE,
)

CLASSES = {"Warrior": Warrior, "Mage": Mage, "Rogue": Rogue}


def test_catalogo_carrega_sem_id_repetido():
    skills = load_skills()
    assert skills, "nenhuma skill carregada"
    ids = [s.id for s in skills]
    assert len(ids) == len(set(ids)), "id de skill repetido no JSON"


# --- aquisição -------------------------------------------------------------


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_cada_classe_tem_exatamente_uma_assinatura(classe):
    """Uma inicial, e uma só: o nível 1 entrega a identidade da classe.

    Eram quatro, entregues uma por nível até o quarto. O jogador chegava ao
    nível 4 com o deck cheio sem ter escolhido nada — o kit inicial era o deck
    inteiro, e a primeira decisão do jogo acontecia depois de ele já estar
    montado.
    """
    iniciais = get_initial_skills(classe)
    assert len(iniciais) == 1, f"{classe} tem {len(iniciais)} iniciais; a assinatura é uma só"
    assert iniciais[0].is_initial
    assert iniciais[0].skill_class == classe


@pytest.mark.parametrize("classe,cls", sorted(CLASSES.items()))
def test_o_heroi_nasce_com_a_assinatura_e_nada_mais(classe, cls):
    heroi = cls("Teste")
    assert len(heroi.skills) == 1
    assert heroi.skills[1].id == get_initial_skills(classe)[0].id
    assert heroi.seen_skill_ids == {heroi.skills[1].id}


@pytest.mark.parametrize("cls", sorted(CLASSES.values(), key=lambda c: c.get_classname()))
def test_subir_de_nivel_nao_entrega_carta_de_graca(cls):
    """Depois do nível 1 nada entra no deck sozinho: tudo é escolha.

    O teste anterior exigia o contrário — que subir de nível entregasse a
    próxima inicial. Era o sistema antigo, e é justamente o que a V2 remove.
    """
    heroi = cls("Teste")
    antes = dict(heroi.skills)
    heroi.level += 1
    assert heroi.learn_new_skills(show=True) == []
    assert heroi.skills == antes


@pytest.mark.parametrize("cls", sorted(CLASSES.values(), key=lambda c: c.get_classname()))
def test_a_oferta_acontece_de_tres_em_tres_niveis(cls):
    heroi = cls("Teste")
    ofertam = []
    for nivel in range(1, 13):
        heroi.level = nivel
        if heroi.is_skill_offer_level():
            ofertam.append(nivel)
    assert ofertam == list(range(SKILL_OFFER_LEVEL_INTERVAL, 13, SKILL_OFFER_LEVEL_INTERVAL))
    assert 1 not in ofertam, "o nível 1 entrega a assinatura, não uma escolha"


@pytest.mark.parametrize("classe,cls", sorted(CLASSES.items()))
def test_a_oferta_nunca_traz_carta_de_outra_classe(classe, cls):
    heroi = cls("Teste")
    heroi.set_level(12)
    escolhas = generate_skill_choices(classe, 12, heroi.active_skill_ids())
    assert len(escolhas) == SKILL_OFFER_SIZE
    ids = {s.id for s in escolhas}
    assert len(ids) == SKILL_OFFER_SIZE, "a mesma carta foi oferecida duas vezes"
    for skill in escolhas:
        assert skill.skill_class in (classe, NEUTRAL), "carta de outra classe foi oferecida"
        assert skill.level_required <= 12, "carta acima do nível do herói foi oferecida"
        assert skill.id not in heroi.active_skill_ids(), "carta que ele já tem ocupou um espaço"


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_o_inedito_vem_antes_do_repetido(classe):
    """Sem esta ordem, o jogador via a mesma carta três vezes antes de conhecer
    metade do catálogo, e a escolha virava sorteio."""
    candidatas = [s for s in get_offer_pool(classe) if not s.is_initial and s.level_required <= 20]
    vistas = {s.id for s in candidatas[:-2]}
    escolhas = generate_skill_choices(classe, 20, [], seen_ids=vistas)
    ineditas = {s.id for s in candidatas if s.id not in vistas}
    # As duas inéditas têm de aparecer antes de qualquer repescagem.
    assert ineditas <= {s.id for s in escolhas}


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_a_repescagem_existe_quando_o_inedito_acaba(classe):
    """Com tudo já visto, a oferta continua cheia em vez de vir vazia."""
    todas = {s.id for s in get_offer_pool(classe)}
    escolhas = generate_skill_choices(classe, 20, [], seen_ids=todas)
    assert len(escolhas) == SKILL_OFFER_SIZE


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_escolha_nunca_repete_o_que_o_heroi_ja_tem(classe):
    disponiveis = [
        s for s in get_skills_for_class(classe) if not s.is_initial and s.level_required <= 20
    ]
    conhecidas = [s.id for s in disponiveis[:2]]
    escolhas = generate_skill_choices(classe, 20, conhecidas, count=3)
    assert not ({s.id for s in escolhas} & set(conhecidas))


@pytest.mark.parametrize("classe,cls", sorted(CLASSES.items()))
def test_o_deck_para_em_quatro(classe, cls):
    heroi = cls("Teste")
    heroi.set_level(20)
    for skill in get_offer_pool(classe):
        heroi.learn_skill(skill)
    assert len(heroi.skills) == MAX_ACTIVE_SKILLS
    assert not heroi.has_free_skill_slot()
    assert sorted(heroi.skills) == list(range(1, MAX_ACTIVE_SKILLS + 1))


@pytest.mark.parametrize("classe,cls", sorted(CLASSES.items()))
def test_com_o_deck_cheio_a_carta_so_entra_por_substituicao(classe, cls):
    heroi = cls("Teste")
    heroi.set_level(20)
    candidatas = [s for s in get_offer_pool(classe) if s.id not in heroi.active_skill_ids()]
    for skill in candidatas[:3]:
        heroi.learn_skill(skill)
    extra = candidatas[3]
    heroi.learn_skill(extra)
    assert extra.id not in heroi.active_skill_ids(), "a quinta carta entrou sozinha"
    assert extra.id in heroi.seen_skill_ids, "a carta recusada não foi registrada como vista"
    heroi.add_skill_with_replacement(extra, 2)
    assert heroi.skills[2].id == extra.id


@pytest.mark.parametrize("classe", sorted(CLASSES))
def test_o_menu_do_nivel_3_ainda_nao_oferece_escolha_de_verdade(classe):
    """Lacuna de CONTEÚDO, registrada em número para não passar despercebida.

    Na primeira oferta (nível 3) existem exatamente três candidatas nas três
    classes: o menu mostra todas as cartas que existem, o que não é escolher.
    Só a partir do nível 6 há mais candidatas que vagas.

    `generate_skill_choices` devolve o que existe — o código está certo. O
    número fica fixado aqui para que subir o catálogo apareça como uma falha
    deste teste, e não como um silêncio.
    """

    def quantas(nivel):
        pool = get_offer_pool(classe)
        return len([s for s in pool if not s.is_initial and s.level_required <= nivel])

    candidatas = {nivel: quantas(nivel) for nivel in (3, 6, 9)}
    assert candidatas == {3: 3, 6: 5, 9: 7}, (
        f"{classe}: o catálogo mudou ({candidatas}). Se aumentou, o menu do "
        "nível 3 finalmente oferece escolha — atualize este número."
    )


def test_o_pool_neutral_esta_vazio_hoje():
    """A gramática Neutral existe e o conteúdo dela ainda não.

    `get_offer_pool` já junta as cartas da classe com as Neutral, e o validador
    já as segura num teto ofensivo menor. Só que nenhuma carta declara
    `skill_class: "Neutral"`, então o caminho inteiro é, hoje, um caminho que
    não passa por lugar nenhum.

    Este teste existe para que isso seja um fato registrado, e não um recurso
    que todo mundo acha que funciona. Quando a primeira Neutral entrar no JSON,
    ele falha e pede para ser trocado por um teste do comportamento real.
    """
    neutras = [s for s in load_skills() if s.skill_class == NEUTRAL]
    assert not neutras, (
        f"{len(neutras)} carta(s) Neutral entraram no catálogo. O pool deixou de "
        "ser vazio: troque este teste por um que verifique que as três classes a recebem."
    )


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


def _custo(skill) -> float:
    """O que a carta cobra, em % da mana máxima de quem lança."""
    return float(getattr(skill, "mana_cost_percent", 0) or 0) or float(skill.mana_cost)


def _eficiencia(skill) -> float:
    """Dano por ponto percentual de mana. As duas pontas na mesma unidade.

    Era `effect_value / mana_cost`: um percentual de bônus sobre o poder base
    dividido por uma mana ABSOLUTA que não escala. Duas unidades diferentes, e
    o resultado não era dano por mana — era um número sem significado que por
    acaso ordenava do jeito esperado.
    """
    return offensive_budget(skill) / max(0.01, _custo(skill))


@pytest.mark.parametrize("classe", CLASSES_COM_DANO)
def test_nenhuma_skill_de_dano_e_dominada(classe):
    """Nenhuma skill pode custar mais e entregar menos que outra da classe.

    "Custar mais" é o conjunto: mais mana, mais recarga e mais nível exigido.
    Uma carta dominada nesses três eixos não é uma escolha difícil — é uma
    escolha errada, e oferecê-la ao jogador gasta um slot do menu.

    O poder é um INTERVALO, e continua sendo depois da V2: com condição
    situacional, a mesma carta entrega o piso quando a situação não ajuda e o
    teto quando ajuda. Dominar exige entregar mais nas duas pontas — uma carta
    que perde no piso e ganha no teto não é pior, é outra aposta, e é
    exatamente a decisão que a condição existe para criar.
    """
    da_classe = [s for s in SKILLS_DE_DANO if s.skill_class == classe]

    for a in da_classe:
        for b in da_classe:
            if a is b:
                continue
            piso_a = offensive_budget(a, com_bonus=False)
            piso_b = offensive_budget(b, com_bonus=False)
            teto_a, teto_b = offensive_budget(a), offensive_budget(b)
            pior_ou_igual = (
                piso_a <= piso_b
                and teto_a <= teto_b
                and _custo(a) >= _custo(b)
                and int(a.cooldown) >= int(b.cooldown)
                and int(a.level_required) >= int(b.level_required)
            )
            estritamente_pior = (
                piso_a < piso_b
                or teto_a < teto_b
                or _custo(a) > _custo(b)
                or int(a.cooldown) > int(b.cooldown)
            )
            assert not (pior_ou_igual and estritamente_pior), (
                f"{a.id} (nv {a.level_required}, {piso_a}-{teto_a}%, "
                f"{_custo(a):.2f} de mana, recarga {a.cooldown}) é dominada por "
                f"{b.id} (nv {b.level_required}, {piso_b}-{teto_b}%, "
                f"{_custo(b):.2f} de mana, recarga {b.cooldown})"
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

    teto = max(offensive_budget(s) for s in iniciais)
    for s in aprendidas:
        assert offensive_budget(s) > teto, (
            f"{s.id} é aprendida no nível {s.level_required} e entrega "
            f"{offensive_budget(s)}%, abaixo dos {teto}% que a classe já tem no nível 1"
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
        assert offensive_budget(seguinte) > offensive_budget(anterior), (
            f"{seguinte.id} (nv {seguinte.level_required}) entrega "
            f"{offensive_budget(seguinte)}%, não mais que {anterior.id} "
            f"(nv {anterior.level_required}, {offensive_budget(anterior)}%)"
        )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "DEFEITO DE BALANCEAMENTO MEDIDO, não corrigido nesta rodada. As cartas de "
        "recarga longa rendem ~21 de dano por ponto percentual de mana contra ~29 "
        "das de recarga curta: trocar frequência por pico custa mais caro por ponto "
        "de dano, e não menos. O teste antigo dizia o contrário porque dividia "
        "`effect_value` (percentual de bônus) por `mana_cost` (mana absoluta, que "
        "não escala) — unidades diferentes. Medida na mesma unidade sobre os DADOS "
        "PRÉ-MIGRAÇÃO a razão já estava invertida (0,13-0,16 contra 0,23-0,24): a "
        "migração V2 não criou o problema, só tornou visível. Corrigir exige mexer "
        "em preço de carta, que é balanceamento, e esta rodada é estrutural."
    ),
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
