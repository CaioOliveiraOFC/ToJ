"""`overall_power`: o poder do personagem medido em NÍVEL DE MONSTRO.

    overall_power = L tal que P(vencer o boneco de nível L) = 0,50

A régua anterior era determinística e via só o ataque básico. Medido, ela errava
de 1,036× a 1,684× conforme o equipamento — e invertia pares reais: um Mago
nível 15 pelado lia SUPEROU contra um nível 12 equipado onde o combate de
verdade diz ABAIXO. Aqui quem converte skill, mana, poção, status, Égide e
iniciativa em poder é o DUELO, não um peso escrito por alguém.

O que estes testes fixam, em ordem de importância:

1. a medição não altera o jogo — nem o personagem, nem o sorteio da run;
2. o número é da BUILD, não do desgaste do momento;
3. consumível, desgaste e recarga NÃO movem o número: eles são run, não build;
4. as monotonicidades, que são o que impede a fórmula de inverter o sinal do que
   mede.

Os testes de (4) são caros — centenas de combates reais — e por isso ficam sob a
marca `balance`, junto com as outras medições sob demanda.
"""

from __future__ import annotations

import ast
import copy
import random
from pathlib import Path

import pytest

from src.content.factories.archetypes import spawn_by_role
from src.content.factories.monsters import calculate_scaled_monster_level
from src.shared.constants import (
    ARENA_EQUIVALENCE_BAND,
    ARENA_LEVEL_BRACKET,
    ARENA_LEVEL_FLOOR,
    ARENA_REFERENCE_ROLE,
)
from src.sim import arena
from src.sim.arena import (
    ABAIXO,
    EQUIVALENTE,
    SUPEROU,
    PoderForaDeEscalaError,
    assinatura_de_build,
    classificar,
    limpar_cache,
    overall_power,
)
from src.sim.harness import make_hero

# Duelos por sondagem nos testes de contrato. O número real é 100; aqui o que
# está sob teste é o COMPORTAMENTO (não mutar, não consumir sorteio, marcar kit
# incompatível), e esse comportamento não depende do tamanho da amostra.
POUCOS_DUELOS = 6


@pytest.fixture(autouse=True)
def _cache_limpo():
    limpar_cache()
    yield
    limpar_cache()


def medir(heroi, **kwargs):
    kwargs.setdefault("duelos", POUCOS_DUELOS)
    return overall_power(heroi, **kwargs)


# --- 1. A medição não altera o jogo ---------------------------------------


def test_a_medicao_devolve_o_gerador_global_ao_estado_anterior():
    """Medir não pode consumir o sorteio que a run ainda vai usar.

    A camada de conteúdo sorteia pelo `random` do módulo: mapa, loot, oferta de
    carta e nível de monstro saem de lá. Uma medição que gastasse esse gerador
    mudaria o jogo que o jogador está jogando — medir o personagem não pode
    alterar a partida dele.
    """
    random.seed(4242)
    antes = random.getstate()
    medir(make_hero("Warrior", 5, "expected"))
    assert random.getstate() == antes


def test_a_medicao_nao_machuca_o_personagem_da_run():
    """`run_battle` machuca quem entra nele. Quem entra é uma cópia."""
    heroi = make_hero("Rogue", 8, "expected")
    antes = (
        heroi.get_hp(),
        heroi.get_mp(),
        heroi.isalive,
        len(heroi.inventory),
        dict(heroi.active_effects),
        dict(heroi.equipment),
    )
    medir(heroi)
    depois = (
        heroi.get_hp(),
        heroi.get_mp(),
        heroi.isalive,
        len(heroi.inventory),
        dict(heroi.active_effects),
        dict(heroi.equipment),
    )
    assert antes == depois


def test_duas_medicoes_do_mesmo_personagem_dao_o_mesmo_numero():
    """A decisão de extrair não pode oscilar por sorteio."""
    heroi = make_hero("Mage", 8, "expected")
    primeira = medir(heroi, usar_cache=False)
    segunda = medir(heroi, usar_cache=False)
    assert primeira == segunda


# --- 2. O número é da BUILD, não do desgaste -------------------------------


def test_o_desgaste_do_momento_nao_muda_o_poder():
    """HP baixo agora não é build pior.

    O desgaste é o que a razão de runway mede. Deixá-lo entrar aqui contaria o
    mesmo atrito duas vezes na decisão de extrair.
    """
    inteiro = make_hero("Warrior", 8, "expected")
    ferido = copy.deepcopy(inteiro)
    ferido.take_damage(int(ferido.base_hp * 0.7))
    assert ferido.get_hp() < inteiro.get_hp()
    assert medir(ferido, usar_cache=False) == medir(inteiro, usar_cache=False)


def test_a_curva_de_orcamento_do_monstro_e_continua():
    """O nível fracionário é legítimo: a régua não precisa interpolar.

    `geometric` é contínua, então o boneco de nível 16,5 fica ENTRE o de 16 e o
    de 17 em cada atributo. Sem isso a bisseção teria de inventar uma
    interpolação entre inteiros — a última escolha arbitrária que sobrava.
    """
    baixo = spawn_by_role(ARENA_REFERENCE_ROLE, 16)
    meio = spawn_by_role(ARENA_REFERENCE_ROLE, 16.5)
    alto = spawn_by_role(ARENA_REFERENCE_ROLE, 17)
    for ler in (lambda m: m.base_hp, lambda m: m.get_st(), lambda m: m.get_df()):
        assert ler(baixo) <= ler(meio) <= ler(alto)
        assert ler(baixo) < ler(alto)


def test_o_nivel_fracionario_nao_escapa_para_a_run():
    """O `float` vive dentro da medição; o mapa continua spawnando inteiros.

    A régua pode pedir um boneco de nível 16,5 porque ela não o entrega a
    ninguém. O caminho da RUN é outro e continua inteiro — `Monster.level` sai
    em texto na ficha do confronto, e um "Nv.16,5" no mapa seria a medição
    vazando para dentro do jogo.
    """
    leitura = medir(make_hero("Warrior", 5, "expected"))
    assert isinstance(leitura.nivel_equivalente, float)

    for andar in range(1, 21):
        assert isinstance(calculate_scaled_monster_level(andar, andar), int)

    # E nenhuma camada de jogo conhece a régua: quem mede importa o motor, o
    # motor nunca importa quem mede.
    for arquivo in (*Path("src/engine").rglob("*.py"), *Path("src/content").rglob("*.py")):
        texto = arquivo.read_text(encoding="utf-8")
        assert "sim.arena" not in texto, arquivo


def test_quem_perde_para_o_menor_monstro_para_no_piso():
    """Abaixo do menor monstro do jogo não há curva de orçamento para ler."""
    fraquissimo = make_hero("Mage", 1, "naked")
    fraquissimo.base_hp = 1
    fraquissimo.rest()
    leitura = medir(fraquissimo, usar_cache=False)
    assert leitura.nivel_equivalente == ARENA_LEVEL_FLOOR
    assert leitura.sondagens == 1  # uma sondagem basta para saber que perde


# --- A banda aprovada ------------------------------------------------------


@pytest.mark.parametrize(
    ("relativo", "esperado"),
    [
        (0.90, ABAIXO),
        (1 - ARENA_EQUIVALENCE_BAND - 0.001, ABAIXO),
        (1 - ARENA_EQUIVALENCE_BAND, EQUIVALENTE),
        (1.00, EQUIVALENTE),
        (1 + ARENA_EQUIVALENCE_BAND, EQUIVALENTE),
        (1 + ARENA_EQUIVALENCE_BAND + 0.001, SUPEROU),
        (1.20, SUPEROU),
    ],
)
def test_a_classificacao_usa_a_banda_aprovada(relativo, esperado):
    assert classificar(relativo) == esperado


# --- O cache ---------------------------------------------------------------


def test_o_cache_responde_pela_assinatura_da_build():
    heroi = make_hero("Warrior", 8, "expected")
    primeira = medir(heroi)
    assert medir(heroi) is primeira


@pytest.mark.parametrize(
    "mudanca",
    [
        pytest.param("nivel", id="subir de nível"),
        pytest.param("deck", id="perder a carta"),
        pytest.param("equipamento", id="desequipar"),
    ],
)
def test_a_assinatura_muda_quando_a_build_muda(mudanca):
    """Uma assinatura que não enxerga a mudança devolve poder velho.

    Gastar a última poção NÃO está nesta lista, e a ausência é o desenho: a
    partir da V2 consumível não é build, e a invariância tem teste próprio.
    """
    antes = make_hero("Warrior", 8, "expected")
    depois = copy.deepcopy(antes)
    if mudanca == "nivel":
        depois.set_level(9)
    elif mudanca == "deck":
        depois.skills.clear()
    else:
        for posicao, peca in list(depois.equipment.items()):
            if peca is not None:
                depois.unequip(posicao)
                break
    assert assinatura_de_build(antes) != assinatura_de_build(depois)


# --- A fronteira -----------------------------------------------------------


def test_a_regua_nao_depende_do_cerebro_do_bot():
    """`overall_power` é propriedade do personagem, não nota da policy do bot.

    O piloto de medição é `smart_policy`, que é congelado e mora fora de
    `sim/bot/`. Se a régua importasse o cérebro do bot, melhorar o bot passaria
    a "aumentar" o poder de todo personagem — e a comparação com a Arena viraria
    uma avaliação da própria inteligência que a consulta.
    """
    arvore = ast.parse(Path("src/sim/arena.py").read_text(encoding="utf-8"))
    importados = {
        no.module
        for no in ast.walk(arvore)
        if isinstance(no, ast.ImportFrom) and no.module is not None
    }
    assert not any(modulo.startswith("src.sim.bot") for modulo in importados)
    assert "src.sim.policies" in importados


# --- 4. As monotonicidades (medição sob demanda) ---------------------------


@pytest.mark.balance
def test_mais_equipamento_nunca_vale_menos_poder():
    for classe in ("Warrior", "Mage", "Rogue"):
        pelado, tipico, topo = (
            overall_power(make_hero(classe, 12, carga)).nivel_equivalente
            for carga in ("naked", "expected", "best")
        )
        assert pelado < tipico < topo, (classe, pelado, tipico, topo)


@pytest.mark.balance
def test_mais_nivel_nunca_vale_menos_poder():
    for classe in ("Warrior", "Mage", "Rogue"):
        serie = [
            overall_power(make_hero(classe, nivel, "expected")).nivel_equivalente
            for nivel in (5, 8, 12, 15, 20)
        ]
        assert serie == sorted(serie), (classe, serie)


@pytest.mark.balance
def test_o_numero_se_repete_entre_blocos_de_seed_independentes():
    """O ruído tem de ser menor que a banda, ou o veredito é sorteio."""
    for classe, nivel in (("Warrior", 12), ("Mage", 15)):
        heroi = make_hero(classe, nivel, "expected")
        valores = [
            overall_power(heroi, semente=semente, usar_cache=False).nivel_equivalente
            for semente in (777, 20777, 40777, 60777, 80777)
        ]
        media = sum(valores) / len(valores)
        assert (max(valores) - min(valores)) / media < 0.02, (classe, valores)


# --- O teto que não é teto -------------------------------------------------


# Multiplicador do campeão de teste. Medido com `POUCOS_DUELOS`: com 400× o
# resultado fica em 60,6–62,9 — margem de 1% sobre o bracket, que é ruído de
# amostra e não prova nada. Com 4.000× fica em 70,7–72,8: 18% acima, folga
# suficiente para o teste falhar só quando a expansão realmente quebrar.
#
# A escala é logarítmica nos atributos porque o orçamento de monstro é
# geométrico — 10× de força não vale 10× de nível, vale cerca de +20.
FORCA_FORA_DE_ESCALA = 4_000


def campeao_fora_de_escala(fator: int = FORCA_FORA_DE_ESCALA):
    """Um personagem forte o bastante para passar do bracket inicial.

    Artificial de propósito: o que está sob teste é o MECANISMO DE BUSCA, não um
    build que a progressão produza. Os atributos entram pelos setters do próprio
    herói, então tudo abaixo continua saindo das funções canônicas.
    """
    heroi = make_hero("Warrior", 20, "best")
    heroi.base_hp = heroi.base_hp * fator
    heroi.base_st = heroi.base_st * fator
    heroi.base_df = heroi.base_df * fator
    heroi.rest()
    return heroi


@pytest.mark.balance
def test_o_bracket_inicial_nao_e_teto_do_resultado():
    """A dungeon é infinita; o número não pode saturar em 60.

    Com teto fixo, dois campeões diferentes liam o mesmo valor e
    `relative_power` entre eles dava 1,000 sem que nenhum tivesse sido medido —
    a saturação que a régua existe para não ter.
    """
    leitura = overall_power(campeao_fora_de_escala(), duelos=POUCOS_DUELOS)
    assert leitura.nivel_equivalente > ARENA_LEVEL_BRACKET


@pytest.mark.balance
def test_dois_campeoes_acima_do_bracket_continuam_distinguiveis():
    """O que a saturação quebrava: comparar quem passou do teto."""
    um = overall_power(campeao_fora_de_escala(), duelos=POUCOS_DUELOS).nivel_equivalente
    outro = overall_power(
        campeao_fora_de_escala(FORCA_FORA_DE_ESCALA * 8), duelos=POUCOS_DUELOS
    ).nivel_equivalente
    assert um > ARENA_LEVEL_BRACKET
    assert outro > um


def test_a_trava_tecnica_falha_em_vez_de_virar_resultado(monkeypatch):
    """O limite de segurança não pode ser devolvido calado.

    Devolvê-lo seria trocar um número medido por um número escolhido — e
    reintroduzir, no limite técnico, a mesma saturação que o bracket fixo tinha.
    """
    monkeypatch.setattr(arena, "ARENA_LEVEL_HARD_LIMIT", 4.0)
    monkeypatch.setattr(arena, "ARENA_LEVEL_BRACKET", 2.0)
    with pytest.raises(PoderForaDeEscalaError) as erro:
        overall_power(campeao_fora_de_escala(), duelos=1, usar_cache=False)
    assert "não foi medido" in str(erro.value)


def test_a_expansao_nao_cobra_sondagem_de_quem_esta_na_escala():
    """Quem cabe no bracket inicial não paga pela busca dos que não cabem."""
    normal = make_hero("Warrior", 8, "expected")
    leitura = overall_power(normal, duelos=POUCOS_DUELOS, usar_cache=False)
    assert ARENA_LEVEL_FLOOR < leitura.nivel_equivalente < ARENA_LEVEL_BRACKET
    # Piso, topo do bracket e a bisseção até a tolerância relativa. Uma expansão
    # a mais apareceria aqui como sondagem extra.
    assert leitura.sondagens <= 16


# --- A FRONTEIRA: recurso da run não é build ------------------------------
#
# Consumível, desgaste, buff e recarga são estado da RUN. Quem os mede é a razão
# de runway. Se entrarem aqui, o mesmo gladiador lê poderes diferentes conforme a
# mochila e o momento — e a comparação com a Arena passa a premiar estoque.


def _consumivel():
    from src.content.items import get_all_items

    for definicao in get_all_items().values():
        if getattr(definicao, "consumable", False):
            return definicao.instance()
    raise AssertionError("catálogo sem consumível")


def _item_guardado():
    """Uma peça equipável que fica NA MOCHILA, sem ser equipada."""
    from src.content.items import get_all_items

    for definicao in get_all_items().values():
        if getattr(definicao, "slot", None) == "Helmet":
            return definicao.instance()
    raise AssertionError("catálogo sem elmo")


def _arma(predicado):
    from src.content.items import get_all_items

    for definicao in get_all_items().values():
        if getattr(definicao, "slot", None) == "Weapon" and predicado(definicao):
            return definicao.instance()
    raise AssertionError("catálogo sem arma para este caso")


def _mede(heroi):
    return overall_power(heroi, duelos=POUCOS_DUELOS, usar_cache=False).nivel_equivalente


def test_a_poção_nao_move_o_poder():
    """(A) 0 contra 5 consumíveis, mesma build permanente."""
    sem = make_hero("Warrior", 10, "expected")
    sem.inventory = [i for i in sem.inventory if not i.is_potion]
    com = copy.deepcopy(sem)
    for _ in range(5):
        com.add_item_to_inventory(_consumivel())

    assert assinatura_de_build(sem) == assinatura_de_build(com)
    assert _mede(sem) == _mede(com)


def test_item_guardado_na_mochila_nao_move_o_poder():
    """(B) Item não equipado não toca o duelo."""
    antes = make_hero("Rogue", 10, "expected")
    depois = copy.deepcopy(antes)
    depois.add_item_to_inventory(_item_guardado())

    assert assinatura_de_build(antes) == assinatura_de_build(depois)
    assert _mede(antes) == _mede(depois)


def test_equipar_peca_melhor_move_o_poder():
    """(C) Equipamento é build, e build muda o número."""
    pelado = make_hero("Warrior", 10, "naked")
    armado = make_hero("Warrior", 10, "best")
    assert assinatura_de_build(pelado) != assinatura_de_build(armado)
    assert _mede(armado) > _mede(pelado)


def test_skill_a_mais_muda_a_identidade():
    """(D) Deck é build."""
    from src.content.skills_loader import get_skills_for_class

    antes = make_hero("Mage", 10, "expected")
    depois = copy.deepcopy(antes)
    for carta in get_skills_for_class("Mage"):
        if carta.id not in depois.active_skill_ids() and depois.has_free_skill_slot():
            depois.learn_skill(carta)
            break
    assert len(depois.skills) > len(antes.skills)
    assert assinatura_de_build(antes) != assinatura_de_build(depois)


def test_passiva_a_mais_muda_a_identidade():
    """(E) Passiva é build."""
    from src.content.passives import load_passives

    antes = make_hero("Warrior", 10, "expected")
    depois = copy.deepcopy(antes)
    depois.add_passive_load(load_passives()[0])
    assert assinatura_de_build(antes) != assinatura_de_build(depois)


def test_desgaste_buff_e_recarga_nao_movem_o_poder():
    """(F) A mesma build, em estados de run diferentes, é a mesma build.

    `rest()` sozinho não bastava: ele não limpa `skill_cooldowns`, e
    `policies._usable_skills` consulta recarga. Sem a normalização, o poder
    dependia do instante da run em que a medição caiu.
    """
    limpa = make_hero("Rogue", 10, "expected")
    suja = copy.deepcopy(limpa)
    suja.take_damage(int(suja.base_hp * 0.6))
    suja.reduce_mp(suja.get_mp() // 2)
    suja.active_buffs["Teste"] = {"stat": "st", "value": 999, "duration": 3}
    suja.active_effects["poison"] = {"duration": 2, "value": 5}
    for carta in suja.skills.values():
        suja.skill_cooldowns[carta.id] = 9

    assert assinatura_de_build(limpa) == assinatura_de_build(suja)
    assert _mede(limpa) == _mede(suja)


def test_recarga_sozinha_nao_move_o_poder():
    """(G) Isola a recarga das outras sujeiras do estado."""
    pronta = make_hero("Mage", 10, "expected")
    recarregando = copy.deepcopy(pronta)
    for carta in recarregando.skills.values():
        recarregando.skill_cooldowns[carta.id] = 5

    assert assinatura_de_build(pronta) == assinatura_de_build(recarregando)
    assert _mede(pronta) == _mede(recarregando)


# --- As colisões de cache -------------------------------------------------


def _com_arma(classe, arma, segunda=None):
    heroi = make_hero(classe, 10, "naked")
    heroi.add_item_to_inventory(arma)
    heroi.equip(arma, "Weapon1")
    if segunda is not None:
        heroi.add_item_to_inventory(segunda)
        heroi.equip(segunda, "Weapon2")
    return heroi


def test_armas_de_dano_diferente_nao_dividem_cache():
    """(I) `get_avg_damage` passa por `weapon_percent`, e `get_st` não carrega isso."""
    armas = sorted(
        (
            d.instance()
            for d in __import__("src.content.items", fromlist=["x"]).get_all_items().values()
            if getattr(d, "slot", None) == "Weapon" and getattr(d, "damage_bonus", 0)
        ),
        key=lambda i: i.damage_bonus,
    )
    fraca, forte = armas[0], armas[-1]
    assert fraca.damage_bonus != forte.damage_bonus
    assert assinatura_de_build(_com_arma("Warrior", fraca)) != assinatura_de_build(
        _com_arma("Warrior", forte)
    )


def test_maos_diferentes_nao_dividem_cache():
    """(H) `can_use_skill` lê `hand_type`, e ele decide se a carta sai."""
    tipos = {}
    from src.content.items import get_all_items

    for definicao in get_all_items().values():
        tipo = getattr(definicao, "hand_type", None)
        if getattr(definicao, "slot", None) == "Weapon" and tipo:
            tipos.setdefault(tipo, definicao)
    if len(tipos) < 2:
        pytest.skip("catálogo com um só hand_type de arma")
    (_, uma), (_, outra) = list(tipos.items())[:2]
    assert assinatura_de_build(_com_arma("Warrior", uma.instance())) != assinatura_de_build(
        _com_arma("Warrior", outra.instance())
    )


def test_uma_arma_e_duas_armas_nao_dividem_cache():
    """(J) `req.two_weapons` conta peças empunhadas.

    Sem a OCUPAÇÃO na assinatura, a mão vazia assinaria `("", 1)` — igual a uma
    arma de uma mão sem `hand_type` —, e as duas builds colidiriam.
    """
    from src.content.items import get_all_items

    de_uma_mao = [
        d
        for d in get_all_items().values()
        if getattr(d, "slot", None) == "Weapon"
        and int(getattr(d, "hands_required", 1) or 1) == 1
        and (not d.classes or "Warrior" in d.classes)
    ]
    if len(de_uma_mao) < 2:
        pytest.skip("catálogo sem duas armas de uma mão")
    uma = _com_arma("Warrior", de_uma_mao[0].instance())
    duas = _com_arma("Warrior", de_uma_mao[0].instance(), de_uma_mao[1].instance())
    if duas.equipment.get("Weapon2") is None:
        pytest.skip("este personagem não empunha duas armas")
    assert assinatura_de_build(uma) != assinatura_de_build(duas)


def test_a_ordem_do_deck_nao_divide_cache():
    """(K) `policies._melhor` é `max`, e `max` devolve o PRIMEIRO máximo.

    A lista vem de `hero.skills.values()`, que é a ordem dos slots — o docstring
    de `_melhor` declara que a ordem do deck é o desempate. As mesmas cartas em
    ordens diferentes jogam diferente.
    """
    from src.content.skills_loader import get_skills_for_class

    heroi = make_hero("Rogue", 10, "expected")
    for carta in get_skills_for_class("Rogue"):
        if heroi.has_free_skill_slot() and carta.id not in heroi.active_skill_ids():
            heroi.learn_skill(carta)
    if len(heroi.skills) < 2:
        pytest.skip("deck pequeno demais para trocar a ordem")

    trocado = copy.deepcopy(heroi)
    chaves = sorted(trocado.skills)
    a, b = chaves[0], chaves[1]
    trocado.skills[a], trocado.skills[b] = trocado.skills[b], trocado.skills[a]

    assert set(heroi.active_skill_ids()) == set(trocado.active_skill_ids())
    assert assinatura_de_build(heroi) != assinatura_de_build(trocado)


def test_o_clone_medido_nao_tem_consumivel_e_o_original_mantem_os_dele():
    """A normalização é do CLONE. O personagem da run não perde a poção dele."""
    from src.sim.arena import _normalizado

    heroi = make_hero("Warrior", 10, "expected")
    for _ in range(3):
        heroi.add_item_to_inventory(_consumivel())
    quantos_antes = sum(1 for i in heroi.inventory if i.is_potion)
    assert quantos_antes > 0

    clone = _normalizado(heroi)
    assert not [i for i in clone.inventory if i.is_potion]
    assert not clone.skill_cooldowns
    assert clone.get_hp() == clone.base_hp
    assert sum(1 for i in heroi.inventory if i.is_potion) == quantos_antes
