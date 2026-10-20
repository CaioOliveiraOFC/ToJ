"""Livro-razão do orçamento das cartas de dano: de onde sai cada `power`.

`power` não é número de autoria. É o que resolve uma INTENÇÃO — "esta carta vale
`bud`% do ataque básico da referência dela" — contra o personagem de referência
(`SKILL_REFERENCE_STATS` para o herói, `spawn_by_role` no nível de referência
para o monstro). A conta é `skill_forge.resolver_power`, o inverso exato de
`skill_validator.offensive_budget`.

Este arquivo guarda a intenção de TODA carta de dano publicada, e a origem dela:

- `lote`: o `bud` declarado no lote de autoria (`tools/skill_batches/`).
- `lote+preparar`: o lote declarou um `bud` e `skill_forge.preparar` o ajustou
  antes de publicar — o piso de 1,80 ataques básicos ou o desempate de preço.
  O lote guarda a intenção de partida; o valor publicado é este.
- `legado`: carta sem intenção registrada — a migração V1 calibrou o `power`
  para preservar o dano antigo, e nunca houve orçamento. Vale o orçamento que
  ela ENTREGAVA na Etapa 7 da reforma de fundação. Não se reconstrói intenção
  onde ela não existe: o `effect_value` V1 de monstro (`100 + effect_value`)
  foi descartado de propósito.

Por que ele existe: quando a referência muda, o `power` tem de ser rederivado
para que cada carta continue entregando o `bud` dela. Foi o que não aconteceu
quando o monstro ganhou atributos reais — as cartas de lote foram resolvidas
contra a referência inflada e passaram a entregar de 2/3 a 1,8x do que
declaravam. `tests/test_orcamento_de_cartas.py` falha se isso voltar a ocorrer.

Uso:
    python tools/orcamento_de_cartas.py            # confere, não grava
    python tools/orcamento_de_cartas.py --gravar   # rederiva e grava `power`
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(RAIZ / "tools"))

from skill_forge import MONSTERS_JSON, SKILLS_JSON, resolver_power  # noqa: E402

from src.content.skill_validator import _referencia, monster_reference  # noqa: E402

# id -> (bud, origem). `bud` em % do ataque básico da referência, no melhor caso.
ORCAMENTO: dict[str, tuple[int, str]] = {
    # --- herói ---
    "golpe_poderoso": (141, "legado"),
    "investida": (161, "legado"),
    "golpe_devastador": (277, "legado"),
    "bola_fogo": (212, "legado"),
    "missil_magico": (154, "legado"),
    "ataque_furtivo": (179, "legado"),
    "cutelada": (218, "legado"),
    "golpe_duplo": (256, "legado"),
    "esmagar": (318, "legado"),
    "relampago": (241, "legado"),
    "explosao_arcana": (296, "legado"),
    "tempestade": (334, "legado"),
    "apocalipse": (431, "legado"),
    "golpe_sombras": (231, "legado"),
    "assassinato": (288, "legado"),
    "danca_laminas": (298, "legado"),
    "morte_subita": (434, "legado"),
    "quebra_guarda": (185, "lote"),
    "pisada_de_ferro": (180, "lote"),
    "soco_de_placa": (165, "lote"),
    "marca_do_acougueiro": (167, "lote"),
    "investida_de_ariete": (170, "lote"),
    "peso_do_machado": (190, "lote"),
    "ferro_contra_ferro": (215, "lote"),
    "rasgo_de_gancho": (210, "lote"),
    "tremor_de_bigorna": (205, "lote"),
    "mao_dupla": (230, "lote"),
    "colheita_de_ferro": (280, "lote"),
    "carga_do_condenado": (290, "lote"),
    "fortaleza_viva": (420, "lote"),
    "lasca_de_gelo": (220, "lote"),
    "fagulha_teimosa": (165, "lote"),
    "marca_ardente": (169, "lote"),
    "pulso_de_forca": (175, "lote"),
    "lancar_pedra": (176, "lote+preparar"),
    "lente_de_obsidiana": (225, "lote"),
    "maldicao_de_cinzas": (205, "lote"),
    "troca_de_sangue": (240, "lote"),
    "prisma_de_devastacao": (310, "lote"),
    "dividendo_de_mana": (350, "lote"),
    "corte_de_tendao": (195, "lote"),
    "picada_certeira": (159, "lote"),
    "flecha_pela_fresta": (175, "lote"),
    "dose_da_viuva": (166, "lote"),
    "duas_maos_um_tempo": (185, "lote"),
    "lamina_no_escuro": (230, "lote"),
    "marcar_a_presa": (215, "lote"),
    "chuva_de_ferrões": (220, "lote"),
    "hora_do_lobo": (300, "lote"),
    "cobranca_de_juros": (325, "lote"),
    "testamento_do_ladrao": (301, "lote+preparar"),
    "n_mira_calma": (218, "lote"),
    "n_marca_do_cacador": (267, "lote"),
    "n_ultima_carta": (239, "lote"),
    # --- monstro ---
    "mob_mordida_suja": (115, "lote"),  # trash
    "mob_golpe_pesado": (93, "legado"),  # bruiser
    "mob_cabecada": (150, "lote"),  # bruiser
    "mob_impacto": (105, "legado"),  # tank
    "mob_pisao": (140, "lote"),  # tank
    "mob_rajada": (113, "legado"),  # glass_cannon
    "mob_detonacao": (153, "legado"),  # glass_cannon
    "mob_lanca_de_ozonio": (195, "lote"),  # glass_cannon
    "mob_fenda_de_eter": (225, "lote"),  # glass_cannon
    "mob_corte_rapido": (129, "legado"),  # skirmisher
    "mob_finta": (140, "lote"),  # skirmisher
    "mob_bote": (160, "lote"),  # skirmisher
    "mob_agulhada_mental": (130, "lote"),  # controller
    "mob_investida_brutal": (104, "legado"),  # elite
    "mob_golpe_de_arauto": (185, "lote"),  # elite
    "mob_lamina_negra": (175, "lote"),  # elite
    "boss_devastar": (122, "legado"),  # boss
    "boss_juizo": (230, "lote"),  # boss
}


def medir_referencia_do_heroi() -> dict[str, dict[str, int]]:
    """`SKILL_REFERENCE_STATS` medido: cada classe no nível 12 com o loadout
    `expected`, atributos já resolvidos. É o regenerador da tabela — e o teste
    que a compara com isto é o que impede a cópia de envelhecer em silêncio.
    """
    from src.shared.constants import SKILL_REFERENCE_STATS, SKILL_SCALING_STATS
    from src.sim.harness import make_hero

    medida = {}
    for classe in SKILL_REFERENCE_STATS:
        heroi = make_hero(classe, 12, "expected")
        linha = {stat: int(heroi.get_stat(stat)) for stat in SKILL_SCALING_STATS}
        linha["avg"] = int(heroi.get_avg_damage())
        medida[classe] = linha
    return medida


def _cartas_de_dano(dados: dict) -> list[dict]:
    return [s for s in dados if s.get("effect_type") == "damage" and s.get("scaling")]


def power_derivado(carta: dict, referencia: dict) -> float:
    """O `power` que faz a carta publicada entregar o `bud` do livro-razão."""
    bud, _ = ORCAMENTO[carta["id"]]
    return resolver_power(
        bud,
        carta["scaling"],
        carta.get("bonus_percent", 0),
        referencia,
        crit_chance=int(carta.get("crit_chance", 0) or 0),
    )


def divergencias() -> list[tuple[str, float, float]]:
    """(id, power publicado, power derivado) de toda carta fora do orçamento."""
    saida = []
    herois = json.loads(SKILLS_JSON.read_text(encoding="utf-8"))["skills"]
    for s in _cartas_de_dano(herois):
        derivado = power_derivado(s, _referencia(s.get("skill_class", "")))
        if abs(float(s["power"]) - derivado) > 1e-9:
            saida.append((s["id"], float(s["power"]), derivado))
    monstros = json.loads(MONSTERS_JSON.read_text(encoding="utf-8"))["archetypes"]
    for papel, arquetipo in monstros.items():
        referencia = monster_reference(papel)
        for s in _cartas_de_dano(arquetipo.get("skills", [])):
            derivado = power_derivado(s, referencia)
            if abs(float(s["power"]) - derivado) > 1e-9:
                saida.append((s["id"], float(s["power"]), derivado))
    return saida


def gravar() -> int:
    """Rederiva e grava `power` em toda carta de dano. Devolve quantas mudaram."""
    novos = {i: d for i, _, d in divergencias()}
    for caminho, raiz in ((SKILLS_JSON, "skills"), (MONSTERS_JSON, "archetypes")):
        dados = json.loads(caminho.read_text(encoding="utf-8"))
        grupos = [dados[raiz]] if raiz == "skills" else [a["skills"] for a in dados[raiz].values()]
        for grupo in grupos:
            for s in grupo:
                if s["id"] in novos:
                    s["power"] = novos[s["id"]]
        caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return len(novos)


if __name__ == "__main__":
    if "--gravar" in sys.argv:
        print(f"{gravar()} cartas rederivadas")
    else:
        fora = divergencias()
        for carta, publicado, derivado in fora:
            print(f"{carta:24} publicado {publicado:7.3f}  derivado {derivado:7.3f}")
        print(f"{len(fora)} cartas fora do orçamento")
        sys.exit(1 if fora else 0)
