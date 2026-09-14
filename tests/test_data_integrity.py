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

    def test_toda_skill_de_dano_tem_alguma_identidade(self):
        """Uma skill de dano sem NENHUM traço próprio é um ataque básico caro.

        A escolha entre elas vira aritmética fixa — sempre a de maior valor — e
        o deck deixa de precisar ser lido.

        A regra exigia especificamente uma CONDIÇÃO SITUACIONAL de todas elas, e
        isso é forte demais: uma carta também se distingue pelo efeito que
        aplica, pela mira que tem, pelo equipamento que pede ou por onde o golpe
        nasce. Exigir sempre a mesma forma de identidade empurra o catálogo para
        uma forma só, que é o oposto do que esta regra protege.

        O que continua proibido é a carta sem nenhuma delas.
        """
        sem = []
        for s in _skills():
            if s["effect_type"] != "damage":
                continue
            tracos = [
                nome
                for nome, tem in (
                    ("condição", bool(s.get("bonus_condition")) and bool(s.get("bonus_percent"))),
                    ("efeito secundário", bool(s.get("secondary"))),
                    ("mira", bool(s.get("accuracy_modifier"))),
                    ("requisito", bool(s.get("requires"))),
                )
                if tem
            ]
            if not tracos:
                sem.append(s["id"])
        assert not sem, (
            "skills de dano sem condição, efeito, mira nem requisito — "
            f"são ataques básicos mais caros: {sem}"
        )


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
        # Achados na auditoria semântica do catálogo de 150 cartas.
        "nunca erra": "não existe acerto garantido: `accuracy_modifier` soma na "
        "mesma conta e continua preso ao teto global de acerto",
        "sempre acerta": "idem — o teto de acerto vale para toda carta",
        "reflete": "não existe reflexão de dano no motor",
        "devolve o feitiço": "não existe reflexão de magia no motor",
        "não sobra mão": "a carta não impede o ataque do turno seguinte",
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


class TestResistenciaDeItemUsaOVocabulario:
    """Um item não pode declarar resistência a um status que não existe.

    `frost`, `freeze` e `congelado` seriam três placebos silenciosos: o campo
    fica no JSON, o motor soma zero e ninguém percebe. A grafia canônica é a que
    `shared/effects.negative_statuses()` devolve.
    """

    def test_toda_resistencia_declarada_tem_nome_canonico(self):
        from src.shared.effects import negative_statuses

        canonicos = set(negative_statuses())
        invalidas = []
        for arquivo in DADOS:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            for item in dados.get("items", []):
                for nome, valor in (item.get("status_resistances") or {}).items():
                    if nome not in canonicos:
                        invalidas.append(f"{item['id']}: {nome}")
                    if not 0 <= int(valor) <= 100:
                        invalidas.append(f"{item['id']}: {nome}={valor} fora de 0..100")
        assert not invalidas, f"resistências inválidas: {invalidas}"


class TestEfeitoDeEquipamentoEConhecido:
    """Um `effect_type` de equipamento é suportado, é backlog, ou é erro.

    A auditoria encontrou 58 itens de equipamento declarando um efeito que nada
    lê. Nenhum deles foi escrito de má-fé: cada um pareceu funcionar quando foi
    adicionado, porque o JSON aceita qualquer palavra e o motor ignora em
    silêncio o que não conhece.

    Esta guarda não exige que o backlog esteja implementado — exigir isso hoje
    forçaria acordar tudo de uma vez, que é exatamente o que estamos evitando.
    Ela exige apenas que todo nome no catálogo seja um nome que ALGUÉM decidiu:
    ou já funciona, ou está numa lista de espera com data. Um nome fora das duas
    é erro de digitação ou conteúdo novo nascendo placebo.
    """

    # Efeitos que o motor consome hoje quando o item está equipado.
    SUPPORTED = frozenset(
        {
            # Camada A: atributos, via `Player.equipment_percent`.
            "max_hp",
            "max_mp",
            "strength",
            "agility",
            "speed",
            "magic_damage",
            "defense",
            # Camada B: modificadores de combate, via `Player.get_equipment_bonus`.
            "evasion",
            "damage_reduction",
            "crit_chance",
            "crit_damage",
            "life_steal",
            "mana_regen",
            "death_ignore",
            # on-hit: o valor é a CHANCE, e a mecânica é do catálogo global.
            "stun",
            "bleed",
            "poison",
            "fear",
        }
    )

    # Backlog consciente. Cada entrada tem um motivo, não é uma amnistia geral.
    KNOWN_BACKLOG = {
        "true_damage": "sem mecânica: 'ignora defesa' ainda não é um conceito do motor",
        "armageddon": "sem mecânica: o nome não corresponde a nada",
    }

    def test_todo_effect_type_de_equipamento_e_suportado_ou_backlog(self):
        conhecidos = self.SUPPORTED | set(self.KNOWN_BACKLOG)
        desconhecidos = []
        for arquivo in DADOS:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            for item in dados.get("items", []):
                if item.get("consumable"):
                    continue
                efeito = item.get("effect_type")
                if efeito and efeito not in conhecidos:
                    desconhecidos.append(f"{item['id']}: {efeito}")
        assert not desconhecidos, (
            "effect_type de equipamento fora de SUPPORTED ∪ KNOWN_BACKLOG — "
            "conteúdo novo nascendo placebo, ou erro de grafia:\n" + "\n".join(desconhecidos)
        )

    def test_supported_bate_com_o_que_o_motor_realmente_le(self):
        """A lista não pode virar promessa: ela espelha o código, ou não vale."""
        from src.entities.heroes import Player

        atributos = {nome for fontes in Player.EQUIP_STAT_SOURCES.values() for nome in fontes}
        assert self.SUPPORTED == (
            atributos | set(Player.EQUIP_COMBAT_EFFECTS) | set(Player.EQUIP_ONHIT_EFFECTS)
        )

    def test_backlog_e_supported_nao_se_sobrepoem(self):
        """Um efeito ligado não pode continuar listado como pendente."""
        assert not (self.SUPPORTED & set(self.KNOWN_BACKLOG))

    def test_o_backlog_nao_guarda_efeito_que_ninguem_declara(self):
        """Backlog sem item é lista de desejos. Some quando o último item sai."""
        declarados = set()
        for arquivo in DADOS:
            dados = json.loads(arquivo.read_text(encoding="utf-8"))
            for item in dados.get("items", []):
                if not item.get("consumable") and item.get("effect_type"):
                    declarados.add(item["effect_type"])
        orfaos = sorted(set(self.KNOWN_BACKLOG) - declarados)
        assert not orfaos, f"backlog sem nenhum item que o declare: {orfaos}"


class TestCatalogoDeSkills:
    """O portão que separa o JSON do jogo.

    O catálogo vai ser escrito por IA, e IA devaneia. O validador roda ANTES de
    a carta chegar ao motor — estaticamente, sem simular combate — e é aqui que
    ele é acionado sobre o catálogo real: sem esta chamada ele seria um módulo
    correto que ninguém executa, que é a definição de placebo neste projeto.
    """

    def test_toda_carta_do_catalogo_passa_no_validador(self):
        from src.content.skill_validator import assert_catalogo_valido
        from src.content.skills_loader import load_skills

        assert_catalogo_valido(load_skills())

    def test_o_validador_reprova_de_verdade(self):
        """Prova de carga: sem ela, um validador quebrado aprovaria tudo em silêncio."""
        import dataclasses

        import pytest

        from src.content.skill_validator import assert_catalogo_valido, validate
        from src.content.skills_loader import ScalingTerm, get_skill_by_id

        carta = get_skill_by_id("golpe_poderoso")
        absurda = dataclasses.replace(
            carta,
            id="absurda",
            power=carta.power * 20,
            scaling=(ScalingTerm("st", 1.0),),
        )
        veredito = validate(absurda)
        assert not veredito.ok
        assert "offensive budget" in " ".join(veredito.erros)
        with pytest.raises(ValueError):
            assert_catalogo_valido([absurda])

    def test_toda_carta_de_monstro_passa_no_mesmo_validador(self):
        """Monstro obedece às MESMAS leis, medido contra o arquétipo dele.

        A régua muda porque tem de mudar — o Tanque tem Defesa alta e Agilidade
        baixa, e medi-lo contra o Guerreiro diria que a carta dele é fraca por
        um detalhe de planilha. A LEI é a mesma: escala válida, no máximo dois
        atributos somando 1.0, MP e recarga, acerto na faixa, efeito do catálogo
        global, orçamento não absurdo.
        """
        from src.content.skill_validator import validate_monster_catalog

        vereditos = validate_monster_catalog()
        assert vereditos, "nenhuma carta de monstro validada: o teste não estaria medindo nada"
        reprovadas = [str(v) for v in vereditos if not v.ok]
        assert not reprovadas, "\n".join(reprovadas)

    def test_o_validador_reprova_carta_de_monstro_invalida(self):
        """Prova de carga do lado do monstro."""
        import dataclasses

        from src.content.factories.archetypes import get_archetype
        from src.content.skill_validator import monster_reference, validate
        from src.content.skills_loader import ScalingTerm

        ref = monster_reference("boss")
        carta = next(s for s in get_archetype("boss").skills if s.effect_type == "damage")
        for rotulo, quebrada in (
            (
                "três atributos",
                dataclasses.replace(
                    carta,
                    scaling=(
                        ScalingTerm("st", 0.4),
                        ScalingTerm("mg", 0.3),
                        ScalingTerm("df", 0.3),
                    ),
                ),
            ),
            ("pesos errados", dataclasses.replace(carta, scaling=(ScalingTerm("st", 0.5),))),
            ("sem recarga", dataclasses.replace(carta, cooldown=0)),
            ("sem mana", dataclasses.replace(carta, mana_cost=0, mana_cost_percent=0)),
            ("dano absurdo", dataclasses.replace(carta, power=carta.power * 30)),
        ):
            assert not validate(quebrada, reference=ref).ok, f"{rotulo} passou no validador"


class TestNenhumaSkillOficialUsaOAtalhoLegado:
    """O fallback existe para save antigo e mod — não para o conteúdo do jogo.

    `skill_damage_base` aceita uma carta sem `scaling`/`power` e cai no poder de
    ataque genérico. Isso é rede de segurança para um save de outra versão, e
    tem de continuar existindo. Mas se uma carta OFICIAL cair ali, ela deixou de
    ter identidade: duas cartas diferentes passam a bater igual, e ninguém
    percebe, porque o motor não reclama — só devolve um número plausível.
    """

    def _oficiais_de_dano(self):
        from src.content.factories.archetypes import all_archetypes
        from src.content.skills_loader import load_skills

        cartas = [("hero", s) for s in load_skills()]
        for role, arquetipo in sorted(all_archetypes().items()):
            cartas += [(role, s) for s in arquetipo.skills]
        return [(origem, s) for origem, s in cartas if s.effect_type == "damage"]

    def test_toda_carta_oficial_de_dano_tem_gramatica_v2(self):
        faltando = [
            f"{origem}/{s.id}"
            for origem, s in self._oficiais_de_dano()
            if not s.scaling or not s.power
        ]
        assert not faltando, (
            "cartas oficiais de dano sem `scaling`/`power` caem no atalho de "
            f"conteúdo legado e batem todas igual: {faltando}"
        )

    def test_o_atalho_continua_existindo_para_conteudo_de_fora(self):
        """Prova de carga: a rede de segurança não pode ter sido removida junto."""
        from types import SimpleNamespace

        from src.entities.heroes import Warrior
        from src.mechanics.combat import skill_damage_base

        heroi = Warrior("Teste")
        antiga = SimpleNamespace(name="De um save velho", effect_type="damage", effect_value=140)
        assert skill_damage_base(heroi, antiga) == heroi.get_avg_damage()


class TestRequisitoDeSkillTemPecaQueOCumpra:
    """Um requisito que nenhum item satisfaz é uma carta morta no deck.

    O requisito bloqueia o USO. Se nenhuma peça do jogo declara o `hand_type`
    pedido, a carta nunca fica jogável — ela ocupa um dos quatro slots para
    sempre, e a tela ainda diz ao jogador para ir atrás de uma arma que não
    existe. É o defeito de placebo na sua forma mais cruel: não é que o efeito
    não aconteça, é que o jogador passa a run inteira tentando fazê-lo acontecer.

    Foi um problema real: nenhum item declarava `hand_type` até este catálogo,
    e as 42 armas precisaram ser etiquetadas para que os requisitos existissem.
    """

    def _tipos_de_mao_no_jogo(self) -> set[str]:
        dados = json.loads((RAIZ / "src" / "data" / "items.json").read_text(encoding="utf-8"))
        return {
            i["hand_type"] for i in dados["items"] if i.get("hand_type") and not i.get("consumable")
        }

    def test_todo_hand_type_exigido_existe_em_alguma_arma(self):
        from src.content.skills_loader import load_skills

        disponiveis = self._tipos_de_mao_no_jogo()
        assert disponiveis, "nenhuma arma declara hand_type: todo requisito seria carta morta"
        orfas = [
            f"{s.id} exige {s.requires.hand_type!r}"
            for s in load_skills()
            if s.requires and s.requires.hand_type and s.requires.hand_type not in disponiveis
        ]
        assert not orfas, "requisitos que nenhuma peça do jogo cumpre: " + "; ".join(orfas)

    def test_cada_classe_alcanca_os_tipos_que_as_cartas_dela_exigem(self):
        """Exigir do Mago uma arma que o Mago não pode equipar é o mesmo defeito."""
        from src.content.skills_loader import NEUTRAL, load_skills

        dados = json.loads((RAIZ / "src" / "data" / "items.json").read_text(encoding="utf-8"))
        por_classe: dict[str, set[str]] = {"Warrior": set(), "Mage": set(), "Rogue": set()}
        for item in dados["items"]:
            tipo = item.get("hand_type")
            if not tipo or item.get("consumable"):
                continue
            for classe in item.get("classes") or list(por_classe):
                por_classe.setdefault(classe, set()).add(tipo)

        impossiveis = []
        for skill in load_skills():
            req = skill.requires
            if not req or not req.hand_type:
                continue
            alvos = list(por_classe) if skill.skill_class == NEUTRAL else [skill.skill_class]
            for classe in alvos:
                if req.hand_type not in por_classe.get(classe, set()):
                    impossiveis.append(f"{skill.id} exige {req.hand_type} e {classe} não equipa")
        assert not impossiveis, "; ".join(impossiveis)


class TestCatalogoNaoTemCartaRepetida:
    """Duas cartas que oferecem a MESMA decisão são uma carta com dois nomes.

    A assinatura de uma carta é o que ela decide: de quem é, o que faz, de qual
    atributo nasce, o que aplica, o que exige e quando rende mais. Número não
    entra — "a mesma carta com o valor maior" é justamente o caso que esta regra
    recusa. O catálogo já teve três buffs de Agilidade do Ladino que só diferiam
    em 30, 45 e 50, e nove grupos assim no total; todos foram redesenhados.

    Sem este teste, o próximo lote de conteúdo os traz de volta sem ninguém ver.
    """

    def test_nenhuma_carta_de_heroi_repete_outra(self):
        from src.content.skill_validator import find_clones
        from src.content.skills_loader import load_skills

        repetidas = find_clones(load_skills())
        assert not repetidas, f"cartas que oferecem a mesma decisão: {repetidas}"

    def test_nenhuma_carta_de_monstro_repete_outra_do_mesmo_arquetipo(self):
        from src.content.factories.archetypes import all_archetypes
        from src.content.skill_validator import find_clones

        cartas = [
            (papel, carta)
            for papel, arquetipo in sorted(all_archetypes().items())
            for carta in arquetipo.skills
        ]
        repetidas = find_clones(cartas)
        assert not repetidas, f"cartas que oferecem a mesma decisão: {repetidas}"

    def test_a_deteccao_enxerga_uma_copia(self):
        """Prova de carga: um auditor cego aprovaria o catálogo inteiro."""
        import dataclasses

        from src.content.skill_validator import find_clones
        from src.content.skills_loader import get_skill_by_id

        original = get_skill_by_id("grito_guerra")
        copia = dataclasses.replace(original, id="copia", name="Cópia", effect_value=999)
        assert find_clones([original, copia]) == [["grito_guerra", "copia"]]


class TestMitigacaoDizQuantoReduz:
    """A carta de mitigação é escolhida pelo número, e o número tem de estar lá.

    Nove cartas diziam apenas o que a personagem fazia ("amarra o escudo no
    braço") e nunca quanto isso valia. Entre duas delas, a escolha era às cegas.
    """

    def test_toda_carta_de_reducao_cita_o_proprio_valor(self):
        erradas = [
            f"{s['id']} (reduz {s['effect_value']}%): {s['description']!r}"
            for s in _skills()
            if s["effect_type"] == "damage_reduction"
            and str(s["effect_value"]) not in s.get("description", "")
        ]
        assert not erradas, "mitigação que não diz quanto reduz: " + "; ".join(erradas)
