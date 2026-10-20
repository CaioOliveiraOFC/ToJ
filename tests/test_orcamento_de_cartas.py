"""Toda carta de dano entrega o orçamento declarado — contra a referência ATUAL.

`power` é derivado: resolve o `bud` (intenção, em % do ataque da referência)
contra o personagem de referência. Quando o monstro ganhou atributos reais, as
cartas de lote continuaram com o `power` resolvido contra a referência inflada
de antes e passaram a entregar de 2/3 a 1,8x do que declaravam — sem nenhum
teste perceber, porque nada comparava o `power` publicado com a intenção.

Estes testes comparam. Mudou a referência (do herói ou do arquétipo) sem
rederivar, falha aqui; o conserto é `python tools/orcamento_de_cartas.py --gravar`.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

import orcamento_de_cartas as orc  # noqa: E402

from src.content.factories.archetypes import all_archetypes  # noqa: E402
from src.content.skill_validator import monster_reference, offensive_budget  # noqa: E402
from src.content.skills_loader import load_skills  # noqa: E402
from src.shared.constants import SKILL_REFERENCE_STATS  # noqa: E402


def _ids_de_dano() -> set[str]:
    herois = {s.id for s in load_skills() if s.effect_type == "damage" and s.scaling}
    monstros = {
        s.id
        for a in all_archetypes().values()
        for s in a.skills
        if s.effect_type == "damage" and s.scaling
    }
    return herois | monstros


def test_toda_carta_de_dano_tem_orcamento_e_nenhum_orcamento_sobra():
    ids = _ids_de_dano()
    assert ids - set(orc.ORCAMENTO) == set(), "carta de dano sem orçamento declarado"
    assert set(orc.ORCAMENTO) - ids == set(), "orçamento de carta que não existe mais"


def test_toda_origem_e_conhecida():
    assert {origem for _, origem in orc.ORCAMENTO.values()} <= {
        "lote",
        "lote+preparar",
        "legado",
    }


def test_o_power_publicado_e_o_derivado_do_orcamento():
    fora = orc.divergencias()
    assert fora == [], f"cartas fora do orçamento (rode --gravar): {fora[:5]}"


def test_o_validador_mede_o_orcamento_declarado():
    """Ida e volta: a forge resolve `power` pelo `bud`; o validador o mede de volta.

    `offensive_budget` trunca para inteiro, e `power` tem três casas — então o
    medido é o `bud` ou um abaixo, nunca outro número.
    """
    herois = {s.id: s for s in load_skills()}
    for papel, arquetipo in all_archetypes().items():
        ref = monster_reference(papel)
        for s in arquetipo.skills:
            if s.id in orc.ORCAMENTO:
                bud = orc.ORCAMENTO[s.id][0]
                assert offensive_budget(s, reference=ref) in (bud - 1, bud), s.id
    for carta_id, (bud, _) in orc.ORCAMENTO.items():
        if carta_id in herois:
            assert offensive_budget(herois[carta_id]) in (bud - 1, bud), carta_id


def test_o_critico_proprio_da_carta_entra_no_orcamento():
    """`crit_chance` na carta é dano esperado, e o orçamento tem de contá-lo.

    O Ataque Furtivo declara 25% de crítico próprio. Fora do orçamento, ele
    aparecia "no bud" entregando em média 12,5% acima dele. A conta é a do
    motor: `1 + chance x (multiplicador - 1)`, com `CRIT_DAMAGE_BASE` vigente.
    """
    from dataclasses import replace

    from src.shared.constants import CRIT_DAMAGE_BASE

    com_critico = [s for s in load_skills() if s.crit_chance]
    assert com_critico, "premissa: alguma carta declara crítico próprio"
    for carta in com_critico:
        sem = replace(carta, crit_chance=0)
        razao = offensive_budget(carta) / max(1, offensive_budget(sem))
        esperado = 1 + carta.crit_chance / 100 * (CRIT_DAMAGE_BASE - 1)
        assert abs(razao - esperado) < 0.01, (carta.id, razao, esperado)
        assert carta.id in orc.ORCAMENTO, carta.id


def test_a_referencia_do_heroi_e_a_medida():
    """A tabela é cópia de uma medição; a cópia não pode envelhecer sozinha."""
    assert SKILL_REFERENCE_STATS == orc.medir_referencia_do_heroi()


def test_o_livro_razao_nao_mexe_em_nada_alem_de_power():
    """`--gravar` reescreve o JSON inteiro; o formato tem de sair idêntico."""
    for caminho in (orc.SKILLS_JSON, orc.MONSTERS_JSON):
        bruto = caminho.read_text(encoding="utf-8")
        assert json.dumps(json.loads(bruto), ensure_ascii=False, indent=2) + "\n" == bruto
