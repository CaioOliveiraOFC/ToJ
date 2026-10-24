"""Copa Arena 02: mata-mata de 64 gladiadores com OP entre 20 e 30 e a final auditada.

Uso:
    python tools/arena_copa_02.py calibrar   # mede e grava `calibracao.json`
    python tools/arena_copa_02.py            # disputa a Copa e escreve os relatórios

Experimento de DIAGNÓSTICO do duelo PvP sob uma política fixa. Não mede
balanceamento entre classes: uma Copa MD1 é uma amostra, não uma estatística.

Reaproveita a Copa 01 (`tools/arena_copa_teste.py`) — política, partida dupla com
e sem auditoria, estatística por partida e transcrição da final — e a
instrumentação (`tools/arena_auditoria.py`). O motor e o `overall_power` são os
canônicos; nada aqui calcula poder ou dano por conta própria.

Regras de montagem (o que conta como build LEGAL nesta Copa):

- classe e nível pelo caminho da simulação (`make_hero`);
- deck de até 4 cartas da oferta da classe (classe + Neutral). A inicial entra de
  graça; cada outra carta precisa de uma oferta própria (níveis 3, 6, 9, ...) de
  nível maior ou igual ao `level_required` dela. Trocar a inicial gasta uma
  oferta. Requisito de equipamento tem de estar atendido;
- `nível − 1` passivas, uma por nível. Raridade não tem trava no jogo, só peso;
  aqui vale um teto de plausibilidade: nenhuma Lendária, no máximo uma Épica e
  no máximo duas cópias de cada Rara;
- equipamento: o `expected loadout` daquele nível, peça por peça. Uma troca só é
  aceita se a peça nova pode cair de loot (`droppable` — o loot não tem trava de
  andar), serve à classe e à posição, e não supera em dano+defesa a melhor peça
  da mesma categoria que o `expected loadout` daquele nível já tem;
- fora: consumíveis, cartas de economia e a carta `fantasma` (status `invisible`
  com alvo próprio: `apply_skill` aplica status sempre no adversário, então ela
  esconderia o rival — peculiaridade do motor registrada no relatório).

Isolamento: os bonecos vivem só em memória, com a marca de extração que a
preparação da Arena exige. Nenhum save, slot ou coleção de gladiadores é tocado.

Nicknames: identificadores de exibição tirados de canais da Twitch, atribuídos
aos IDs `G01`–`G64` por sorteio com semente própria. Nada liga classe, build,
força ou posição na chave à pessoa real, e ninguém participou nem endossou.
"""

from __future__ import annotations

import hashlib
import json
import random
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from src.content.extraction import mark_extracted, was_extracted  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.passives import get_passive_by_id  # noqa: E402
from src.content.skills_loader import (  # noqa: E402
    get_initial_skills,
    get_offer_pool,
    get_skill_by_id,
)
from src.shared.constants import MAX_ACTIVE_SKILLS  # noqa: E402
from src.sim.arena import overall_power  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.loadouts import expected_passive_count  # noqa: E402
from tools.arena_copa_teste import (  # noqa: E402
    BuildIlegitimaError,
    Copa,
    Participante,
    jogar_partida,
    niveis_de_oferta,
    sortear_chave,
)

SEMENTE_PRINCIPAL = 20261024
COPA = "Copa Arena 02"
# Faixas de OP: a primeira fechada nos dois lados, as outras abertas à esquerda.
FAIXAS = ((20.0, 22.5), (22.5, 25.0), (25.0, 27.5), (27.5, 30.0))
POR_FAIXA = 16
DISTRIBUICAO = {"Warrior": 22, "Mage": 21, "Rogue": 21}
MAX_TENTATIVAS = 4
# Quanto o OP anda por nível nas sondagens desta calibração (12–21, as três
# classes): o passo da busca, não uma fórmula de poder.
OP_POR_NIVEL = 1.2
NIVEL_INICIAL = {
    ("Warrior", 1): 16,
    ("Warrior", 2): 18,
    ("Warrior", 3): 20,
    ("Warrior", 4): 22,
    ("Mage", 1): 16,
    ("Mage", 2): 18,
    ("Mage", 3): 20,
    ("Mage", 4): 23,
    ("Rogue", 1): 15,
    ("Rogue", 2): 17,
    ("Rogue", 3): 19,
    ("Rogue", 4): 21,
}
FASES = (
    ("fase64", 32, "Fase de 64"),
    ("fase32", 16, "Fase de 32"),
    ("oitavas", 8, "Oitavas"),
    ("quartas", 4, "Quartas"),
    ("semifinal", 2, "Semifinal"),
    ("final", 1, "Final"),
)
NOME_DA_FASE = {fase: nome for fase, _, nome in FASES}
PASTA_DE_SAIDA = RAIZ / "reports" / "pvp" / "copa_02"
ARQUIVO_CALIBRACAO = "calibracao.json"
CARTAS_PROIBIDAS = {"fantasma"}
RARAS_POR_PASSIVA = 2

NICKS = {
    "A": (
        "alanzoka", "Gaules", "Tenz", "casimito", "Coringa", "YoDa", "TheBurntPeanut",
        "Baiano", "Bagi", "Felps", "calango", "brino", "lubatv", "gabepeixe", "DavyJones",
        "G0ularte",
    ),
    "B": (
        "NOBRU", "PaulinhoLOKObr", "JonVlogs", "LuquEt4", "Bisteconee", "blackoutz", "jukes",
        "loud_thurzin", "tioorochitwitch", "bakzera", "gafallen", "babi", "SkipNhO", "mount",
        "Forever", "XANDAOOGOD",
    ),
    "C": (
        "Smzinho", "jovirone", "PlayHard", "Patriota", "aspaszin", "suetam1v4", "brtt",
        "Dilera", "dona", "hastad", "yeTz", "MeikodRJ", "RazaH", "furq", "frttt", "boltz",
    ),
    "D": (
        "Tealzlol", "aXtLOL", "yayahuz", "Neskwga", "Hayashii", "xandfps", "tteuw", "fer",
        "RNakano", "belrodrigues", "liminhag0d", "sofiaespanha", "k13tv", "coldzin", "sacy",
        "fnxLNTC",
    ),
}  # fmt: skip


@dataclass(frozen=True)
class Build:
    """Uma construção, sem nível: o nível sai da calibração."""

    rotulo: str
    classe: str
    faixa: int
    deck: tuple[str, ...]
    comuns: tuple[str, ...]
    extras: tuple[tuple[str, int], ...] = ()
    trocas: tuple[tuple[str, str], ...] = ()
    foco: str = ""


def _b(rotulo, classe, faixa, deck, comuns, extras=(), trocas=(), foco=""):
    return Build(
        rotulo, classe, faixa, tuple(deck), tuple(comuns), tuple(extras), tuple(trocas), foco
    )


MACA = (("Weapon1", "Clava Pesada"),)
MACHADO = (("Weapon1", "Machado de Batalha"),)
ADAGA = (("Weapon2", "Adaga do Assassino"),)

BUILDS = (
    # --- Guerreiros ----------------------------------------------------------
    _b("Muralha de maça", "Warrior", 1,
       ("golpe_poderoso", "baluarte", "couraca_improvisada", "tremor_de_bigorna"),
       ("pele_grossa", "postura_fechada", "coracao_ferro", "sangue_guerreiro"),
       (("escudo_fe", 2),), MACA, "defesa: reduções de dano com maça"),
    _b("Açougueiro", "Warrior", 1,
       ("golpe_poderoso", "marca_do_acougueiro", "peso_do_machado", "rasgo_de_gancho"),
       ("musculos_aco", "fio_serrilhado", "odio_baixo"),
       (("agulha_no_osso", 2),), MACHADO, "sangramento com machado"),
    _b("Duelista", "Warrior", 1,
       ("golpe_poderoso", "quebra_guarda", "fio_no_rebite", "golpe_devastador"),
       ("olho_aguia", "pulso_certeiro", "musculos_aco"),
       (("lamina_afiada", 2),), (), "crítico de espada"),
    _b("Berserker", "Warrior", 1,
       ("golpe_poderoso", "grito_guerra", "cutelada", "golpe_duplo"),
       ("musculos_aco", "odio_baixo", "coracao_ferro"),
       (("furia_berserker", 2),), (), "Força bruta e fragilidade"),
    _b("Carcereiro", "Warrior", 1,
       ("investida", "berro_de_ferro", "fortalecimento", "ferro_contra_ferro"),
       ("olho_de_cacador", "pele_de_sal", "coracao_ferro", "pele_grossa"),
       (("cabeca_dura", 2),), (), "controle: atordoar, medo e enfraquecer"),
    _b("Escudeiro de forja", "Warrior", 1,
       ("golpe_poderoso", "n_guarda_cruzada", "n_disciplina_de_forja", "mao_dupla"),
       ("sangue_guerreiro", "pele_grossa", "odio_baixo"),
       (("casco_calejado", 2),), (), "duas armas: guarda e sangramento"),
    _b("Regenerador", "Warrior", 2,
       ("golpe_poderoso", "tomar_folego", "n_curativo_de_campo", "investida"),
       ("boca_de_sangue", "coracao_ferro", "musculos_aco"),
       (("sede_silenciosa", 2), ("essencia_fluida", 1)), (), "sustentação: cura e roubo de vida"),
    _b("Ariete", "Warrior", 2,
       ("investida_de_ariete", "pisada_de_ferro", "golpe_poderoso", "postura_de_muro"),
       ("olho_de_cacador", "pele_grossa", "musculos_aco"),
       (("instinto_frio", 2),), (), "atordoar com espada e defesa"),
    _b("Muralha pesada", "Warrior", 2,
       ("golpe_poderoso", "baluarte", "n_couro_batido", "n_pacto_de_ferro"),
       ("coracao_ferro", "sangue_guerreiro", "postura_fechada"),
       (("pele_adamantio", 1),), MACA, "tanque de maça com redução dupla"),
    _b("Lenhador", "Warrior", 2,
       ("golpe_poderoso", "sede_de_batalha", "peso_do_machado", "cutelada"),
       ("musculos_aco", "boca_de_sangue", "odio_baixo"),
       (("odio_antigo", 2),), MACHADO, "machado com roubo de vida"),
    _b("Rompe-guarda", "Warrior", 2,
       ("soco_de_placa", "quebra_guarda", "provocacao", "golpe_devastador"),
       ("olho_de_cacador", "musculos_aco", "pele_de_sal"),
       (("furia_berserker", 1), ("instinto_frio", 1)), (), "enfraquecer e expor"),
    _b("Fúria", "Warrior", 3,
       ("furia", "grito_guerra", "golpe_poderoso", "esmagar"),
       ("musculos_aco", "passos_leves", "odio_baixo"),
       (("toque_dragao", 1), ("furia_berserker", 2)), (), "buffs de Agilidade e Força"),
    _b("Colhedor", "Warrior", 4,
       ("golpe_poderoso", "colheita_de_ferro", "juramento_da_muralha", "mao_dupla"),
       ("fio_serrilhado", "sangue_guerreiro", "odio_baixo"),
       (("agulha_no_osso", 2),), (), "duas armas: sangramento pesado"),
    _b("Veterano", "Warrior", 3,
       ("veterania", "fio_no_rebite", "golpe_poderoso", "golpe_devastador"),
       ("olho_aguia", "pulso_certeiro", "passos_leves"),
       (("lamina_afiada", 2), ("sede_sangue", 1)), (), "evasão e crítico de espada"),
    _b("Bigorna", "Warrior", 3,
       ("tremor_de_bigorna", "n_mao_que_nao_treme", "golpe_poderoso", "baluarte"),
       ("pele_grossa", "coracao_ferro", "olho_aguia"),
       (("cabeca_dura", 2), ("punho_atordoante", 1)), MACA, "maça: atordoamento e crítico"),
    _b("Sentinela de ferro", "Warrior", 3,
       ("golpe_poderoso", "respiracao_de_forja", "n_folego_de_marcha", "quebra_ossos"),
       ("sangue_guerreiro", "coracao_ferro", "pele_de_sal"),
       (("essencia_fluida", 2), ("bencao_divina", 1)), (), "vida máxima e lentidão"),
    _b("Machado pesado", "Warrior", 3,
       ("resistencia_heroica", "rasgo_de_gancho", "marca_do_acougueiro", "golpe_poderoso"),
       ("musculos_aco", "pele_grossa", "fio_serrilhado"),
       (("casco_calejado", 2),), (("Weapon2", "Machado de Guerra"),),
       "machado: defesa e sangramento"),
    _b("Fortaleza", "Warrior", 4,
       ("fortaleza_viva", "golpe_poderoso", "juramento_da_muralha", "n_guarda_cruzada"),
       ("sangue_guerreiro", "pele_grossa", "postura_fechada"),
       (("escudo_fe", 2), ("alma_eterna", 1)), (), "carta lendária e guarda dupla"),
    _b("Imortal", "Warrior", 4,
       ("imortal", "golpe_poderoso", "golpe_devastador", "veterania"),
       ("coracao_ferro", "olho_aguia", "musculos_aco"),
       (("lamina_afiada", 2), ("pele_adamantio", 1)), (), "redução extrema com espada"),
    _b("Condenado", "Warrior", 4,
       ("carga_do_condenado", "silencio_do_veterano", "esmagar", "golpe_devastador"),
       ("olho_de_cacador", "musculos_aco", "pele_de_sal"),
       (("voz_no_escuro", 2), ("presenca_errada", 1)), (), "medo e vulnerabilidade"),
    _b("Postura impecável", "Warrior", 3,
       ("n_postura_impecavel", "grito_guerra", "cutelada", "golpe_poderoso"),
       ("musculos_aco", "odio_baixo", "pulso_certeiro"),
       (("furia_berserker", 2), ("odio_antigo", 2)), (), "acúmulo de Força"),
    _b("Pacto de ferro", "Warrior", 4,
       ("n_pacto_de_ferro", "tomar_folego", "tremor_de_bigorna", "golpe_poderoso"),
       ("coracao_ferro", "boca_de_sangue", "pele_grossa"),
       (("sede_silenciosa", 2), ("voracidade", 1)), MACA, "maça: redução, cura e roubo de vida"),
    # --- Magos ---------------------------------------------------------------
    _b("Piromante", "Mage", 1,
       ("bola_fogo", "marca_ardente", "relampago", "maldicao_de_cinzas"),
       ("sangue_de_vidente", "odio_baixo", "olho_aguia"),
       (("heranca_do_abismo", 2),), (), "fogo e veneno"),
    _b("Geomante", "Mage", 1,
       ("bola_fogo", "pulso_de_forca", "lancar_pedra", "lente_de_obsidiana"),
       ("sangue_de_vidente", "reserva_arcana", "olho_de_cacador"),
       (("poco_fundo", 2),), (), "cajado: lentidão, atordoar e vulnerável"),
    _b("Criomante", "Mage", 1,
       ("lasca_de_gelo", "raio_congelante", "palavra_de_torpor", "bola_fogo"),
       ("mente_serena", "pele_de_sal", "sangue_de_vidente"),
       (("ritmo_profano", 1),), (), "gelo: congelar e lentidão"),
    _b("Curandeira", "Mage", 1,
       ("bola_fogo", "drenar_vida", "pele_de_quartzo", "sanguessuga_arcana"),
       ("coracao_ferro", "respiracao_contada", "boca_de_sangue"),
       (("sede_silenciosa", 2),), (), "cura e roubo de vida"),
    _b("Sonhador", "Mage", 1,
       ("sono_profundo", "bola_fogo", "explosao_arcana", "dissonancia"),
       ("sangue_de_vidente", "reserva_arcana", "coracao_ferro"),
       (("ritmo_profano", 2),), (), "sono e maldição"),
    _b("Arcanista crítico", "Mage", 2,
       ("missil_magico", "mao_firme", "foco_do_estudante", "relampago"),
       ("olho_aguia", "pulso_certeiro", "sangue_de_vidente"),
       (("lamina_afiada", 2),), (), "crítico arcano"),
    _b("Égide rúnica", "Mage", 2,
       ("egide_de_runas", "escudo_magico", "bola_fogo", "palavra_de_pavor"),
       ("coracao_ferro", "mente_serena", "pele_grossa"),
       (("escudo_fe", 2), ("casco_calejado", 1)), (), "tanque arcano"),
    _b("Tempestuoso", "Mage", 2,
       ("tempestade", "bola_fogo", "relampago", "foco_do_estudante"),
       ("sangue_de_vidente", "odio_baixo", "olho_aguia"),
       (("heranca_do_abismo", 2),), (), "raio e atordoamento"),
    _b("Prisma", "Mage", 2,
       ("prisma_de_devastacao", "lente_de_obsidiana", "bola_fogo", "clarividencia"),
       ("sangue_de_vidente", "olho_de_cacador", "passos_leves"),
       (("heranca_do_abismo", 1), ("instinto_frio", 2)), (), "vulnerável e dano de cajado"),
    _b("Grilhões", "Mage", 2,
       ("grilhoes_de_gelo", "lasca_de_gelo", "cerco_de_espelhos", "bola_fogo"),
       ("mente_serena", "sangue_de_vidente", "pele_de_sal"),
       (("poco_fundo", 2),), (), "controle pesado: congelar e medo"),
    _b("Dreno", "Mage", 2,
       ("dreno_mana", "troca_de_sangue", "bola_fogo", "drenar_vida"),
       ("respiracao_contada", "reserva_arcana", "boca_de_sangue"),
       (("ritmo_profano", 2),), (), "queima de mana e drenos"),
    _b("Ressurgente", "Mage", 3,
       ("ressurgir", "bola_fogo", "egide_de_runas", "cura_menor"),
       ("coracao_ferro", "respiracao_contada", "mente_serena"),
       (("essencia_fluida", 2), ("bencao_divina", 1)), (), "cura grande e vida máxima"),
    _b("Hora parada", "Mage", 3,
       ("hora_parada", "bola_fogo", "marca_ardente", "explosao_arcana"),
       ("sangue_de_vidente", "reserva_arcana", "odio_baixo"),
       (("heranca_do_abismo", 2), ("oraculo_partido", 1)), (), "sono e explosão"),
    _b("Pacto do vazio", "Mage", 3,
       ("pacto_do_vazio", "missil_magico", "mao_firme", "relampago"),
       ("olho_aguia", "pulso_certeiro", "sangue_de_vidente"),
       (("lamina_afiada", 2), ("lamina_do_juizo", 1)), (), "dano crítico"),
    _b("Escudo e fogo", "Mage", 3,
       ("escudo_magico", "pele_de_quartzo", "n_couro_batido", "bola_fogo"),
       ("coracao_ferro", "pele_grossa", "sangue_de_vidente"),
       (("escudo_fe", 2), ("pele_adamantio", 1)), (), "defesa em camadas"),
    _b("Coveiro arcano", "Mage", 3,
       ("maldicao_de_cinzas", "n_paciencia_do_coveiro", "marca_ardente", "bola_fogo"),
       ("sangue_de_vidente", "odio_baixo", "pele_de_sal"),
       (("unha_suja", 2), ("sangue_toxico", 1)), (), "veneno e fragilidade"),
    _b("Apocalipse", "Mage", 4,
       ("apocalipse", "bola_fogo", "foco_do_estudante", "relampago"),
       ("sangue_de_vidente", "odio_baixo", "olho_aguia"),
       (("heranca_do_abismo", 2), ("oraculo_partido", 1)), (), "carta lendária de dano"),
    _b("Dividendo", "Mage", 4,
       ("dividendo_de_mana", "dreno_mana", "bola_fogo", "reserva_profunda"),
       ("reserva_arcana", "mente_serena", "respiracao_contada"),
       (("poco_fundo", 2), ("ritmo_profano", 2)), (), "mana: queimar a do rival"),
    _b("Mestre do gelo", "Mage", 4,
       ("grilhoes_de_gelo", "raio_congelante", "lasca_de_gelo", "tempestade"),
       ("mente_serena", "sangue_de_vidente", "olho_de_cacador"),
       (("instinto_frio", 2), ("poco_fundo", 1)), (), "congelar e quebrar"),
    _b("Sanguessuga", "Mage", 4,
       ("sanguessuga_arcana", "drenar_vida", "ressurgir", "bola_fogo"),
       ("boca_de_sangue", "coracao_ferro", "respiracao_contada"),
       (("sede_silenciosa", 2), ("voracidade", 1)), (), "roubo de vida e cura"),
    _b("Prisma do arauto", "Mage", 4,
       ("prisma_de_devastacao", "n_hora_do_arauto", "lente_de_obsidiana", "bola_fogo"),
       ("sangue_de_vidente", "olho_aguia", "pulso_certeiro"),
       (("lamina_afiada", 2), ("oraculo_partido", 1)), (), "vulnerabilidade e dano"),
    # --- Ladinos -------------------------------------------------------------
    _b("Assassino de adaga", "Rogue", 1,
       ("ataque_furtivo", "picada_certeira", "lamina_no_escuro", "leitura_de_guarda"),
       ("olho_aguia", "pulso_certeiro", "passo_de_corca"),
       (("lamina_afiada", 2),), ADAGA, "adaga e crítico"),
    _b("Arqueiro", "Rogue", 1,
       ("ataque_furtivo", "flecha_pela_fresta", "olho_do_falcão", "chuva_de_ferrões"),
       ("olho_de_cacador", "olho_aguia", "passos_leves"),
       (("instinto_frio", 2),), (("Weapon1", "Arco Composto"),), "arco: sangramento e crítico"),
    _b("Envenenador", "Rogue", 1,
       ("envenenar", "dose_da_viuva", "ataque_furtivo", "golpe_sombras"),
       ("boca_de_sangue", "passo_de_corca", "coracao_ferro"),
       (("unha_suja", 2),), ADAGA, "veneno"),
    _b("Esquivo", "Rogue", 1,
       ("evasao", "sombra_rapida", "corte_de_tendao", "golpe_sombras"),
       ("passo_de_corca", "passos_leves", "olho_aguia"),
       (("reflexos_rapidos", 2),), (), "evasão e Agilidade"),
    _b("Trapaceiro", "Rogue", 1,
       ("golpe_baixo", "pó_nos_olhos", "ataque_furtivo", "marcar_a_presa"),
       ("olho_de_cacador", "passo_de_corca", "pele_de_sal"),
       (("cabeca_dura", 1), ("voz_no_escuro", 2)), (), "controle sujo"),
    _b("Sangrador", "Rogue", 2,
       ("joelho_torto", "passo_felino", "corte_de_tendao", "marcar_a_presa"),
       ("fio_serrilhado", "passo_de_corca", "coracao_ferro"),
       (("agulha_no_osso", 2),), (), "sangramento acumulado"),
    _b("Duas lâminas", "Rogue", 2,
       ("ataque_furtivo", "duas_maos_um_tempo", "mao_leve", "assassinato"),
       ("musculos_aco", "olho_aguia", "passo_de_corca"),
       (("lamina_afiada", 2),), (), "duas armas e crítico"),
    _b("Caçador", "Rogue", 2,
       ("n_marca_do_cacador", "n_olho_treinado", "flecha_pela_fresta", "ataque_furtivo"),
       ("olho_de_cacador", "olho_aguia", "passos_leves"),
       (("instinto_frio", 1), ("lamina_afiada", 1)), (("Weapon1", "Arco Longbow"),),
       "arco neutro de alto poder"),
    _b("Ladrão de mana", "Rogue", 2,
       ("bolso_furado", "ataque_furtivo", "cortina_fumaca", "golpe_sombras"),
       ("passo_de_corca", "boca_de_sangue", "pele_de_sal"),
       (("voz_no_escuro", 1), ("sede_silenciosa", 2)), (), "queima de mana e névoa"),
    _b("Couro endurecido", "Rogue", 2,
       ("couro_endurecido", "capa_rasgada", "ataque_furtivo", "assassinato"),
       ("coracao_ferro", "pele_grossa", "passo_de_corca"),
       (("casco_calejado", 2), ("escudo_fe", 1)), (), "Ladino defensivo"),
    _b("Lobo", "Rogue", 3,
       ("hora_do_lobo", "lamina_no_escuro", "ataque_furtivo", "sangria_lenta"),
       ("fio_serrilhado", "olho_aguia", "boca_de_sangue"),
       (("agulha_no_osso", 2), ("sede_sangue", 1)), ADAGA, "adaga: sangramento e roubo de vida"),
    _b("Dançarino", "Rogue", 3,
       ("danca_laminas", "sombra_rapida", "ataque_furtivo", "golpe_sombras"),
       ("passo_de_corca", "passos_leves", "musculos_aco"),
       (("reflexos_rapidos", 2), ("vulto", 1)), (), "dança de lâminas e Agilidade"),
    _b("Silêncio", "Rogue", 3,
       ("silencio_de_seda", "nó_corredio", "ataque_furtivo", "golpe_sombras"),
       ("olho_de_cacador", "passo_de_corca", "pele_de_sal"),
       (("cabeca_dura", 2),), (), "sono e atordoamento"),
    _b("Testamento", "Rogue", 3,
       ("testamento_do_ladrao", "duas_maos_um_tempo", "envenenar", "ataque_furtivo"),
       ("boca_de_sangue", "passo_de_corca", "coracao_ferro"),
       (("unha_suja", 2), ("sangue_toxico", 1)), (), "duas armas e veneno"),
    _b("Gancho", "Rogue", 3,
       ("n_gancho_e_corda", "marcar_a_presa", "corte_de_tendao", "ataque_furtivo"),
       ("olho_de_cacador", "musculos_aco", "passo_de_corca"),
       (("instinto_frio", 2),), (), "atordoar e expor"),
    _b("Morte súbita", "Rogue", 4,
       ("morte_subita", "ataque_furtivo", "assassinato", "respiracao_de_ladrao"),
       ("olho_aguia", "pulso_certeiro", "passo_de_corca"),
       (("lamina_afiada", 2), ("sede_sangue", 1)), (), "carta lendária e crítico"),
    _b("Cobrador", "Rogue", 4,
       ("cobranca_de_juros", "joelho_torto", "passo_felino", "ataque_furtivo"),
       ("fio_serrilhado", "passo_de_corca", "coracao_ferro"),
       (("agulha_no_osso", 2),), (), "sangramento máximo"),
    _b("Evasão perfeita", "Rogue", 4,
       ("evasao_perfeita", "n_leitura_de_terreno", "ataque_furtivo", "lamina_no_escuro"),
       ("passos_leves", "passo_de_corca", "olho_aguia"),
       (("reflexos_rapidos", 2), ("vulto", 1)), (), "evasão máxima com adaga"),
    _b("Chuva de ferrões", "Rogue", 4,
       ("chuva_de_ferrões", "olho_do_falcão", "n_marca_do_cacador", "flecha_pela_fresta"),
       ("olho_de_cacador", "olho_aguia", "pulso_certeiro"),
       (("instinto_frio", 2), ("lamina_do_juizo", 1)), (), "arco: crítico e sangramento"),
    _b("Arauto", "Rogue", 4,
       ("n_hora_do_arauto", "pó_nos_olhos", "ataque_furtivo", "assassinato"),
       ("olho_de_cacador", "musculos_aco", "pele_de_sal"),
       (("voz_no_escuro", 2), ("presenca_errada", 1)), (), "medo"),
    _b("Sombra mortal", "Rogue", 4,
       ("golpe_sombras", "assassinato", "ataque_furtivo", "mao_leve"),
       ("musculos_aco", "olho_aguia", "passo_de_corca"),
       (("furia_berserker", 2), ("toque_dragao", 1)), (), "Força do Ladino e crítico"),
)  # fmt: skip
IDS = tuple(f"G{i:02d}" for i in range(1, len(BUILDS) + 1))
# Faixas que a calibração mostrou inviáveis: (build, faixa pedida, faixa final, motivo).
# A troca mantém 16 por faixa; a medição de cada uma está em `calibracao.json`.
REALOCACOES = (
    (
        "Colhedor",
        3,
        4,
        "O nível legal mais baixo é 18 (Colheita de Ferro pede oferta no 15, Juramento da "
        "Muralha e Mão Dupla pedem ofertas no 12 ou acima), e ali a build já mede OP 27,56, "
        "acima do teto da faixa 3 (27,5).",
    ),
    (
        "Postura impecável",
        4,
        3,
        "Movida para a faixa 3 para manter 16 por faixa; nenhuma carta dela trava o nível.",
    ),
)
BUILD_POR_ID = dict(zip(IDS, BUILDS))


# --- nomes ---------------------------------------------------------------------


def _semente_derivada(rotulo: str) -> int:
    digest = hashlib.sha256(f"{SEMENTE_PRINCIPAL}:{rotulo}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def sortear_nomes() -> dict[str, tuple[str, str]]:
    """`id -> (nick, grupo)`, por sorteio próprio: nada liga a pessoa à build."""
    nicks = [(nick, grupo) for grupo, lista in NICKS.items() for nick in lista]
    random.Random(_semente_derivada("nomes")).shuffle(nicks)
    return dict(zip(IDS, nicks))


# --- montagem e legalidade -------------------------------------------------------


def passivas_de(build: Build, nivel: int) -> tuple[str, ...]:
    """As `nível − 1` passivas: as Raras e a Épica declaradas, e as Comuns em ciclo."""
    lista = [pid for pid, copias in build.extras for _ in range(copias)]
    resto = expected_passive_count(nivel) - len(lista)
    if resto < 0:
        raise BuildIlegitimaError(f"{build.rotulo}: passivas demais para o nível {nivel}")
    lista += [build.comuns[i % len(build.comuns)] for i in range(resto)]
    return tuple(lista)


def _pontos(item) -> float:
    return float(getattr(item, "damage_bonus", 0) or 0) + float(
        getattr(item, "defense_bonus", 0) or 0
    )


def montar(build: Build, nivel: int, nome: str):
    """O boneco no nível pedido. Levanta `BuildIlegitimaError` se o jogo não o produziria."""
    heroi = make_hero(build.classe, nivel, "naked")
    heroi.nick_name = nome
    referencia = make_hero(build.classe, nivel, "expected")
    catalogo = get_all_items()
    for posicao, peca in referencia.equipment.items():
        if peca is not None:
            copia = catalogo[peca.name].instance()
            heroi.add_item_to_inventory(copia)
            heroi.equip(copia, posicao)
    for posicao, nome_do_item in build.trocas:
        if nome_do_item not in catalogo:
            raise BuildIlegitimaError(f"{build.rotulo}: {nome_do_item} não está no catálogo")
        peca = catalogo[nome_do_item].instance()
        heroi.add_item_to_inventory(peca)
        heroi.equip(peca, posicao)
        if heroi.equipment.get(posicao) is not peca:
            raise BuildIlegitimaError(f"{build.rotulo}: {nome_do_item} não vai em {posicao}")
    heroi.inventory.clear()
    for pid in passivas_de(build, nivel):
        carta = get_passive_by_id(pid)
        if carta is None:
            raise BuildIlegitimaError(f"{build.rotulo}: passiva {pid} não existe")
        heroi.add_passive(carta)
    cartas = []
    for sid in build.deck:
        carta = get_skill_by_id(sid)
        if carta is None:
            raise BuildIlegitimaError(f"{build.rotulo}: carta {sid} não existe")
        cartas.append(carta)
    heroi.skills = {i: carta for i, carta in enumerate(cartas, start=1)}
    heroi.rest()
    # Marca de extração EM MEMÓRIA, só para a interface da Arena aceitar o boneco.
    mark_extracted(heroi, nivel)
    validar(build, nivel, heroi, referencia)
    return heroi


def validar(build: Build, nivel: int, heroi, referencia) -> None:
    problemas = []
    classe = build.classe
    pool = {s.id: s for s in get_offer_pool(classe)}
    iniciais = {s.id for s in get_initial_skills(classe)}
    ofertas = niveis_de_oferta(nivel)
    deck = build.deck
    if len(deck) != min(MAX_ACTIVE_SKILLS, 1 + len(ofertas)):
        problemas.append(f"deck com {len(deck)} cartas no nível {nivel}")
    if len(set(deck)) != len(deck):
        problemas.append("carta repetida no deck")
    proibidas = CARTAS_PROIBIDAS & set(deck)
    if proibidas:
        problemas.append(f"carta fora desta Copa: {sorted(proibidas)}")
    de_oferta = [sid for sid in deck if sid not in iniciais]
    fora = [sid for sid in de_oferta if sid not in pool]
    if fora:
        problemas.append(f"fora da oferta de {classe}: {fora}")
    exigido = sorted(pool[sid].level_required for sid in de_oferta if sid in pool)
    disponivel = ofertas[-len(exigido) :] if exigido else []
    if len(exigido) > len(ofertas) or any(r > o for r, o in zip(exigido, disponivel)):
        problemas.append(f"cartas exigem {exigido}; ofertas do nível {nivel}: {ofertas}")
    for carta in heroi.skills.values():
        if not heroi.can_use_skill(carta):
            problemas.append(f"{carta.id}: requisito de equipamento não atendido")
    passivas = list(heroi.passives)
    if len(passivas) != expected_passive_count(nivel):
        problemas.append(f"{len(passivas)} passivas; o nível dá {nivel - 1}")
    por_raridade = Counter(p.rarity for p in passivas)
    if por_raridade["Legendary"]:
        problemas.append("passiva Lendária")
    if por_raridade["Epic"] > 1:
        problemas.append("mais de uma passiva Épica")
    raras = Counter(p.id for p in passivas if p.rarity == "Rare")
    if raras and max(raras.values()) > RARAS_POR_PASSIVA:
        problemas.append(f"mais de {RARAS_POR_PASSIVA} cópias de uma Rara: {dict(raras)}")
    teto: dict[str, float] = {}
    for posicao, peca in referencia.equipment.items():
        if peca is not None:
            categoria = heroi.category_of(posicao)
            teto[categoria] = max(teto.get(categoria, 0.0), _pontos(peca))
    for posicao, nome_do_item in build.trocas:
        peca = heroi.equipment.get(posicao)
        if peca is None:
            continue
        if not getattr(peca, "droppable", False) or getattr(peca, "starter_only", False):
            problemas.append(f"{nome_do_item} não cai de loot")
        categoria = heroi.category_of(posicao)
        if _pontos(peca) > teto.get(categoria, 0.0):
            problemas.append(
                f"{nome_do_item} ({_pontos(peca):g}) supera o expected loadout do nível "
                f"{nivel} em {categoria} ({teto.get(categoria, 0.0):g})"
            )
    nomes = [p.name for p in heroi.equipment.values() if p is not None]
    if len(nomes) != len(set(nomes)):
        problemas.append("a mesma peça em duas posições")
    for peca in heroi.equipment.values():
        classes = getattr(peca, "classes", None) if peca is not None else None
        if classes is not None and classe not in classes:
            problemas.append(f"{peca.name} não serve a {classe}")
    if heroi.inventory:
        problemas.append("inventário não vazio")
    if not was_extracted(heroi):
        problemas.append("sem a marca de extração")
    if problemas:
        raise BuildIlegitimaError(f"{build.rotulo} nível {nivel}: " + "; ".join(problemas))


# --- calibração ------------------------------------------------------------------


def faixa_de(op: float) -> int | None:
    for indice, (baixo, alto) in enumerate(FAIXAS, start=1):
        if (baixo <= op if indice == 1 else baixo < op) and op <= alto:
            return indice
    return None


def calibrar_build(build: Build, medir=None) -> dict:
    """Até `MAX_TENTATIVAS` medições, pelo `overall_power` canônico.

    Começa num palpite por classe e faixa e anda pelo passo médio medido nas
    sondagens. Só o nível muda; nenhum atributo é ajustado. Um nível em que a
    build não é legal (carta sem oferta, arma do requisito ausente) fica no
    registro e não conta como tentativa.
    """
    medir = medir or (lambda h: overall_power(h, usar_cache=False).nivel_equivalente)
    baixo, alto = FAIXAS[build.faixa - 1]
    centro = (baixo + alto) / 2
    nivel = NIVEL_INICIAL[(build.classe, build.faixa)]
    tentativas: list[dict] = []
    medidos: dict[int, float] = {}
    while len(medidos) < MAX_TENTATIVAS and len(tentativas) < 2 * MAX_TENTATIVAS:
        if nivel in medidos or nivel < 1:
            break
        try:
            heroi = montar(build, nivel, build.rotulo)
        except BuildIlegitimaError as erro:
            tentativas.append({"nivel": nivel, "erro": str(erro)})
            # Subindo, o nível seguinte destrava mais ofertas; descendo, volta um
            # passo em direção ao último nível medido.
            nivel += 1
            continue
        op = medir(heroi)
        tentativas.append({"nivel": nivel, "op": op})
        medidos[nivel] = op
        if faixa_de(op) == build.faixa:
            return {"nivel": nivel, "op": op, "dentro": True, "tentativas": tentativas}
        passo = round((centro - op) / OP_POR_NIVEL) or (1 if op < baixo else -1)
        passo = max(-3, min(3, passo))
        direcao = 1 if passo > 0 else -1
        proximo = nivel + passo
        while proximo in medidos:
            proximo += direcao
        nivel = proximo
    validos = [t for t in tentativas if "op" in t]
    if not validos:
        return {"nivel": None, "op": None, "dentro": False, "tentativas": tentativas}
    melhor = min(validos, key=lambda t: abs(t["op"] - centro))
    return {"nivel": melhor["nivel"], "op": melhor["op"], "dentro": False, "tentativas": tentativas}


def calibrar_todos(caminho: Path | None = None) -> dict:
    resultado = {
        "copa": COPA,
        "semente_principal": SEMENTE_PRINCIPAL,
        "max_tentativas": MAX_TENTATIVAS,
        "faixas": [list(f) for f in FAIXAS],
        "realocacoes": [
            {"build": b, "faixa_pedida": de, "faixa_final": para, "motivo": m}
            for b, de, para, m in REALOCACOES
        ],
        "participantes": {},
    }
    for gid, build in zip(IDS, BUILDS):
        registro = calibrar_build(build)
        registro.update({"rotulo": build.rotulo, "classe": build.classe, "faixa": build.faixa})
        resultado["participantes"][gid] = registro
        estado = "ok" if registro["dentro"] else "FORA DA FAIXA"
        print(
            f"{gid} {build.rotulo:22} {build.classe:7} faixa {build.faixa} -> nível "
            f"{registro['nivel']} OP {registro['op']} ({len(registro['tentativas'])} tent.) "
            f"{estado}",
            flush=True,
        )
    if caminho is not None:
        caminho.parent.mkdir(parents=True, exist_ok=True)
        caminho.write_text(json.dumps(resultado, ensure_ascii=False, indent=1) + "\n", "utf-8")
    return resultado


def ler_calibracao(pasta: Path = PASTA_DE_SAIDA) -> dict:
    return json.loads((pasta / ARQUIVO_CALIBRACAO).read_text("utf-8"))


# --- participantes e chave -------------------------------------------------------


@dataclass(frozen=True)
class Especificacao02:
    """A ficha de um participante, com os nomes que os relatórios da Copa 01 leem."""

    id: str
    nome: str
    grupo: str
    rotulo: str
    classe: str
    nivel: int
    faixa: int
    deck: tuple[str, ...]
    passivas: tuple[str, ...]
    trocas: tuple[tuple[str, str], ...]
    foco: str
    tentativas: tuple = field(default=(), compare=False)


def formar_participantes(calibracao: dict, *, medir: bool = True) -> list[Participante]:
    """Os 64, no nível calibrado. Com `medir`, o OP é medido de novo, pelo canônico."""
    nomes = sortear_nomes()
    participantes = []
    for gid, build in zip(IDS, BUILDS):
        registro = calibracao["participantes"][gid]
        nivel = registro["nivel"]
        nick, grupo = nomes[gid]
        heroi = montar(build, nivel, nick)
        espec = Especificacao02(
            gid,
            nick,
            grupo,
            build.rotulo,
            build.classe,
            nivel,
            build.faixa,
            build.deck,
            passivas_de(build, nivel),
            build.trocas,
            build.foco,
            tuple(registro["tentativas"]),
        )
        if medir:
            leitura = overall_power(heroi, usar_cache=False)
            participantes.append(
                Participante(espec, heroi, leitura.nivel_equivalente, leitura.duelos)
            )
        else:
            participantes.append(Participante(espec, heroi, registro["op"]))
    return participantes


def disputar_copa(participantes: list[Participante]) -> Copa:
    por_id = {p.id: p for p in participantes}
    chave = sortear_chave([p.id for p in participantes], SEMENTE_PRINCIPAL)
    vivos = [por_id[i] for i in chave]
    copa = Copa(participantes, chave, {})
    for fase, quantas, nome in FASES:
        partidas = [
            jogar_partida(
                fase,
                i + 1,
                vivos[2 * i],
                vivos[2 * i + 1],
                semente_principal=SEMENTE_PRINCIPAL,
                nome_da_fase=nome,
            )
            for i in range(quantas)
        ]
        copa.fases[fase] = partidas
        if any(p.inconclusiva for p in partidas):
            copa.interrompida = f"{nome}: confronto inconclusivo no limite técnico; a chave parou."
            return copa
        vivos = [p.vencedor for p in partidas]
    return copa


def todas(copa: Copa) -> list:
    return [p for fase, _, _ in FASES for p in copa.fases.get(fase, ())]


def main(argv: list[str]) -> int:
    if argv[:1] == ["calibrar"]:
        resultado = calibrar_todos(PASTA_DE_SAIDA / ARQUIVO_CALIBRACAO)
        fora = [g for g, r in resultado["participantes"].items() if not r["dentro"]]
        print(f"fora da faixa: {fora or 'nenhum'}")
        return 1 if fora else 0
    from tools.arena_copa_02_relatorios import escrever_tudo

    participantes = formar_participantes(ler_calibracao())
    copa = disputar_copa(participantes)
    for caminho in escrever_tudo(copa):
        print(f"escrito: {caminho.relative_to(RAIZ)}")
    campeao = copa.campeao
    print(f"Campeão: {campeao.nome} ({campeao.id})" if campeao else copa.interrompida)
    falhas = [p for p in todas(copa) if not all(ok for _, ok in p.fidelidade + p.coerencia)]
    return 1 if falhas or copa.interrompida else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
