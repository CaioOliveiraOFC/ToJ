"""Integridade dos dados de conteúdo.

Seis skills chegaram ao repositório com o nome duplamente codificado — os bytes
UTF-8 de "Lançar Adaga" lidos como latin-1 e regravados, virando
"LanÃ§ar Adaga". O jogo carrega o JSON corretamente, então nada quebra: o
defeito só aparece na tela do jogador e no relatório do scout, onde a carta
passa a ter dois nomes possíveis conforme quem a imprime.

Nenhum teste pegava isso porque nenhum teste olhava o texto. Este olha.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

DADOS = sorted((RAIZ / "src" / "data").glob("*.json"))
# Sem isto, mover `src/data/` transformaria os testes abaixo em zero casos
# parametrizados — nada a executar, nada a falhar, suíte verde.
assert DADOS, "nenhum JSON encontrado em src/data/: os testes abaixo não rodariam."

# Assinatura de UTF-8 lido como latin-1: um 'Ã' ou 'Â' seguido de um byte de
# continuação. Em português correto, 'Ã' só ocorre em maiúsculas isoladas
# ("ÃGUA" não existe), então a sequência é sempre erro de codificação.
MOJIBAKE = re.compile(r"[ÃÂ][\x80-\xbf\xa0-\xff\xad]")

CAMPOS_DE_TEXTO = ("name", "description")


def _todos_os_registros(valor):
    """Percorre a estrutura carregada e devolve cada dicionário encontrado."""
    if isinstance(valor, dict):
        yield valor
        for filho in valor.values():
            yield from _todos_os_registros(filho)
    elif isinstance(valor, list):
        for filho in valor:
            yield from _todos_os_registros(filho)


@pytest.mark.parametrize("arquivo", DADOS, ids=lambda p: p.name)
def test_arquivo_nao_tem_texto_mal_codificado(arquivo: Path):
    conteudo = arquivo.read_text(encoding="utf-8")
    achados = sorted({m.group(0) for m in MOJIBAKE.finditer(conteudo)})
    assert not achados, (
        f"{arquivo.name} tem texto duplamente codificado ({achados}). "
        "Corrija com texto.encode('latin-1').decode('utf-8')."
    )


@pytest.mark.parametrize("arquivo", DADOS, ids=lambda p: p.name)
def test_todo_registro_tem_nome_legivel(arquivo: Path):
    dados = json.loads(arquivo.read_text(encoding="utf-8"))
    for registro in _todos_os_registros(dados):
        for campo in CAMPOS_DE_TEXTO:
            texto = registro.get(campo)
            if not isinstance(texto, str):
                continue
            assert texto.strip(), f"{arquivo.name}: {campo} vazio em {registro.get('id')}"
            assert not MOJIBAKE.search(texto), (
                f"{arquivo.name}: {campo} de {registro.get('id')!r} = {texto!r}"
            )


class TestCondicoesDeBonusExistemNoMotor:
    """Uma condição com grafia errada é um bônus que nunca acontece.

    É o defeito mais caro que esta base já teve, em três variantes: buff que o
    motor não reconhecia pelo nome, passiva de essência que ninguém lia, e
    `stun_chance` num ramo que não o consultava. Nenhuma levantou exceção; todas
    saíram como carta bonita na tela que não fazia nada. Esta regra fecha a porta
    na origem, no dado, antes de o motor ver a carta.
    """

    def test_toda_condicao_declarada_e_conhecida(self):
        from src.shared.effects import BONUS_CONDITIONS

        desconhecidas = [
            (s["id"], s["bonus_condition"])
            for s in _skills()
            if s.get("bonus_condition") and s["bonus_condition"] not in BONUS_CONDITIONS
        ]
        assert not desconhecidas, (
            "condições que o motor não sabe avaliar (o bônus nunca dispara): "
            f"{desconhecidas}. Conhecidas: {BONUS_CONDITIONS}"
        )

    def test_condicao_e_bonus_andam_juntos(self):
        """Um sem o outro é sempre erro: ou bônus de zero, ou bônus sem gatilho."""
        quebradas = [
            s["id"]
            for s in _skills()
            if bool(s.get("bonus_condition")) != bool(s.get("bonus_percent"))
        ]
        assert not quebradas, f"condição sem bônus, ou bônus sem condição: {quebradas}"

    def test_toda_skill_de_dano_tem_uma_situacao(self):
        """Sem condição, uma skill de dano é um ataque básico caro.

        A escolha entre elas vira aritmética fixa — sempre a de maior valor — e
        o deck deixa de precisar ser lido.
        """
        sem = [
            s["id"]
            for s in _skills()
            if s["effect_type"] == "damage" and not s.get("bonus_condition")
        ]
        assert not sem, f"skills de dano sem condição situacional: {sem}"


def _skills() -> list[dict]:
    caminho = RAIZ / "src" / "data" / "skills.json"
    return json.loads(caminho.read_text(encoding="utf-8"))["skills"]


class TestDescricaoDizOQueACartaFaz:
    """A descrição é a única coisa que o jogador lê antes de gastar o recurso.

    Ela é renderizada literalmente (`src/ui/screens.py`), então uma descrição
    desatualizada não é um detalhe de texto: é o jogo declarando um efeito e
    entregando outro. Três casos reais que estas regras fecham:

    - `fortalecimento` prometia "+15 Força" e dava +48 — o rebalanceamento mudou
      `effect_value` de 17 skills e as descrições ficaram para trás;
    - `imortal` prometia "Ignora morte 1 vez" e é um buff de redução de dano —
      `death_ignore` existe, mas como passiva, não nesta carta;
    - `morte_subita` prometia "insta-kill (50%)", mecânica que o motor nunca teve.
      O `chance: 50` que sustentava a promessa nem era lido: `skill.chance` só
      vale no ramo de status.
    """

    # Palavras que descrevem mecânica: se aparecem, a carta precisa ter o campo.
    PROMESSAS = {
        "insta-kill": "não existe execução instantânea no motor",
        "ignora morte": "`death_ignore` é passiva, não efeito de skill",
    }

    def test_nenhuma_descricao_promete_mecanica_inexistente(self):
        quebradas = []
        for skill in _skills():
            texto = skill.get("description", "").lower()
            for termo, motivo in self.PROMESSAS.items():
                if termo in texto:
                    quebradas.append(f"{skill['id']}: '{termo}' — {motivo}")
        assert not quebradas, "descrições prometendo o que o jogo não faz: " + "; ".join(quebradas)

    def test_a_descricao_de_buff_cita_o_percentual_certo(self):
        """O buff é percentual do atributo, então número fixo mente em todo nível.

        `buff_value` converte `effect_value` em percentual do atributo base, e o
        atributo cresce com o nível: "+15 Força" só seria verdade num nível.
        """
        erradas = []
        for skill in _skills():
            if skill["effect_type"] != "buff":
                continue
            valor = int(skill["effect_value"])
            if str(valor) not in skill.get("description", ""):
                erradas.append(f"{skill['id']} (vale {valor}): {skill['description']!r}")
        assert not erradas, "descrições de buff que não citam o próprio valor: " + "; ".join(
            erradas
        )

    def test_a_descricao_de_dano_avisa_a_condicao(self):
        """A condição é o que decide a jogada — omiti-la esconde a decisão.

        Sem ela o jogador não tem como saber que Assassinato cobra mais de um
        alvo ferido, e a carta volta a ser 'aperte quando acender'.
        """
        sem_aviso = [
            s["id"]
            for s in _skills()
            if s["effect_type"] == "damage"
            and s.get("bonus_condition")
            and str(s.get("bonus_percent", 0)) not in s.get("description", "")
        ]
        assert not sem_aviso, (
            f"skills com bônus condicional que a descrição não menciona: {sem_aviso}"
        )

    def test_chance_so_existe_onde_o_motor_a_le(self):
        """`skill.chance` só é consultado no ramo de status (`combat.py`).

        Fora dele o campo é dado morto — e foi um dado morto que sustentou a
        promessa de insta-kill de `morte_subita` por toda a vida do arquivo.
        """
        mortas = [
            s["id"] for s in _skills() if s["effect_type"] != "status" and int(s["chance"]) != 100
        ]
        assert not mortas, (
            f"`chance` != 100 em skills que não são de status, onde o motor a ignora: {mortas}"
        )


class TestDadosVemDoJSON:
    """Regra 5: dados em JSON, sem hardcoded.

    A fronteira: fórmula é código, valor é dado. Um multiplicador de arquétipo,
    o nome de um monstro ou o custo de uma skill são valores — mudam sem que a
    regra mude, e por isso vivem no JSON.
    """

    def test_arquetipos_vem_do_json(self):
        from src.content.factories.archetypes import all_archetypes

        dados = json.loads((RAIZ / "src" / "data" / "monsters.json").read_text(encoding="utf-8"))
        assert set(all_archetypes()) == set(dados["archetypes"]), (
            "Os arquétipos carregados divergem do JSON — há papel definido em Python."
        )

    def test_todo_arquetipo_declara_orcamento_e_papel_no_json(self):
        dados = json.loads((RAIZ / "src" / "data" / "monsters.json").read_text(encoding="utf-8"))
        for role, payload in dados["archetypes"].items():
            assert set(payload["budget"]) == {"hp", "attack", "defense", "agility"}, role
            assert payload["threat"] and payload["counterplay"], (
                f"{role} não declara ameaça e counterplay no JSON."
            )

    def test_geracao_de_andar_vem_do_json(self):
        dados = json.loads((RAIZ / "src" / "data" / "monsters.json").read_text(encoding="utf-8"))
        geracao = dados["generation"]
        for chave in (
            "base_count",
            "min_monsters",
            "scaling_per_3_levels",
            "advanced_role_min_floor",
            "advanced_roles",
            "elite_spawn_chance",
            "level_variation",
        ):
            assert chave in geracao, f"generation.{chave} ausente do JSON."

    @pytest.mark.parametrize(
        "arquivo", ["items.json", "skills.json", "passives.json", "monsters.json"]
    )
    def test_json_de_conteudo_e_valido_e_versionado(self, arquivo):
        dados = json.loads((RAIZ / "src" / "data" / arquivo).read_text(encoding="utf-8"))
        assert dados.get("version"), f"{arquivo} sem campo version."
        assert dados.get("description"), f"{arquivo} sem descrição."
