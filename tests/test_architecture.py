"""As regras de ARCHITECTURE.md, verificadas automaticamente.

Uma regra de arquitetura que só existe em Markdown é uma regra que ninguém
checa. Este módulo lê o código-fonte e falha quando alguma das seis regras
fundamentais é quebrada — inclusive por engano, que é como elas costumam ser
quebradas.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(ROOT))

# Regra 3 e o diagrama de dependências: o que cada camada pode importar, além de
# si mesma. Toda camada pode importar `shared/`.
ALLOWED_IMPORTS: dict[str, set[str]] = {
    "shared": set(),
    "data": {"shared"},
    "entities": {"shared"},
    "mechanics": {"entities", "shared"},
    "content": {"entities", "mechanics", "shared", "data"},
    "storage": {"content", "entities", "shared", "data"},
    # `sim/` mede balanceamento chamando as regras direto. Nunca importa `ui/`
    # nem `engine/`: é isso que a mantém rápida e headless.
    "sim": {"content", "entities", "mechanics", "shared", "data"},
    "engine": {"content", "mechanics", "entities", "storage", "shared", "ui", "data", "sim"},
    "ui": {"shared", "content", "entities", "storage", "data"},
}

# Regra 4: `print()` é da camada de apresentação. `sim/runner.py` é a única
# exceção — é uma ferramenta de linha de comando para desenvolvimento, não saída
# de jogo, e importar `ui/` de dentro de `sim/` quebraria a regra maior de a
# simulação ser headless.
PRINT_EXCEPTIONS = {"src/sim/runner.py"}


def python_files() -> list[Path]:
    return arquivos_de(SRC, recursivo=True)


def arquivos_de(pasta: Path, recursivo: bool = False) -> list[Path]:
    """Os `.py` de uma pasta, garantindo que a busca achou alguma coisa.

    Um teste que percorre o resultado de um `glob` passa quando o `glob` não
    casa com nada — e é assim que uma pasta renomeada transforma a regra de
    arquitetura em teste verde que não verifica nada. Já aconteceu nesta base:
    uma auditoria por padrão de texto deu certo porque o padrão não encontrava
    arquivo nenhum.
    """
    encontrados = sorted(pasta.rglob("*.py") if recursivo else pasta.glob("*.py"))
    assert encontrados, (
        f"{pasta.relative_to(ROOT)} não tem nenhum .py: a regra abaixo não seria "
        "verificada, e o teste passaria sem olhar uma linha."
    )
    return encontrados


def layer_of(path: Path) -> str | None:
    parts = path.relative_to(SRC).parts
    return parts[0] if len(parts) > 1 else None


def runtime_imports(tree: ast.AST) -> list[tuple[str, int]]:
    """Imports que existem em tempo de execução.

    Blocos `if TYPE_CHECKING:` ficam de fora: eles não criam dependência real
    entre camadas, e ARCHITECTURE.md recomenda usá-los justamente para anotar
    tipos sem acoplar módulos.
    """
    type_checking_lines: set[int] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.If):
            test = node.test
            is_type_checking = (
                isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"
            ) or (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING")
            if is_type_checking:
                for child in ast.walk(node):
                    if hasattr(child, "lineno"):
                        type_checking_lines.add(child.lineno)

    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module and node.lineno not in type_checking_lines:
            found.append((node.module, node.lineno))
        elif isinstance(node, ast.Import) and node.lineno not in type_checking_lines:
            for alias in node.names:
                found.append((alias.name, node.lineno))
    return found


class TestRegra1ImportsAbsolutos:
    """Regra 1: apenas imports absolutos a partir de `src`."""

    def test_nenhum_import_relativo(self):
        relativos = []
        for path in python_files():
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.level:
                    relativos.append(f"{path.relative_to(ROOT)}:{node.lineno}")
        assert not relativos, f"Imports relativos: {relativos}"


class TestRegra3Camadas:
    """Regra 3 e o diagrama de dependências: nenhuma importação cruzada.

    A violação mais fácil de cometer é a inversão de dependência — `entities/`
    importando de `content/` ou de `mechanics/` para alcançar uma fórmula ou um
    catálogo. A saída correta é `shared/`, que todas as camadas podem importar.
    """

    def test_dependencias_respeitam_o_diagrama(self):
        violacoes = []
        for path in python_files():
            layer = layer_of(path)
            if layer not in ALLOWED_IMPORTS:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for module, lineno in runtime_imports(tree):
                if not module.startswith("src."):
                    continue
                target = module.split(".")[1]
                if target != layer and target not in ALLOWED_IMPORTS[layer]:
                    violacoes.append(
                        f"{path.relative_to(ROOT)}:{lineno} — {layer} importa {target}"
                    )
        assert not violacoes, "Violações do diagrama de dependências:\n" + "\n".join(violacoes)

    def test_entities_nao_conhece_dados(self):
        # A regra 3 escrita por extenso, porque é a que mais se quebra sem querer.
        for path in arquivos_de(SRC / "entities"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for module, lineno in runtime_imports(tree):
                assert not module.startswith("src.content"), (
                    f"{path.relative_to(ROOT)}:{lineno} importa de content/. "
                    "Use o registro em shared/registries.py."
                )

    def test_simulacao_e_headless(self):
        # Se `sim/` importar `ui/` ou `engine/`, ela deixa de ser rápida e passa
        # a medir a UI em vez das regras.
        for path in arquivos_de(SRC / "sim"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for module, lineno in runtime_imports(tree):
                assert not module.startswith(("src.ui", "src.engine")), (
                    f"{path.relative_to(ROOT)}:{lineno} acopla a simulação à apresentação."
                )


class TestRegra4SaidaPelaUI:
    """Regra 4: nada de `print()` fora de `ui/`."""

    def test_print_apenas_na_ui_ou_na_cli_de_simulacao(self):
        violacoes = []
        for path in python_files():
            relativo = str(path.relative_to(ROOT))
            if relativo.startswith("src/ui/") or relativo in PRINT_EXCEPTIONS:
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if (
                    isinstance(node, ast.Call)
                    and isinstance(node.func, ast.Name)
                    and node.func.id == "print"
                ):
                    violacoes.append(f"{relativo}:{node.lineno}")
        assert not violacoes, f"print() fora de ui/: {violacoes}"

    def test_rich_apenas_na_ui(self):
        violacoes = []
        for path in python_files():
            if str(path.relative_to(ROOT)).startswith("src/ui/"):
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for module, lineno in runtime_imports(tree):
                if module.split(".")[0] in ("rich", "pyfiglet"):
                    violacoes.append(f"{path.relative_to(ROOT)}:{lineno} importa {module}")
        assert not violacoes, f"Renderização fora de ui/: {violacoes}"


class TestRegra5DadosEmJSON:
    """Regra 5: dados em JSON, sem hardcoded.

    A fronteira: fórmula é código, valor é dado. Um multiplicador de arquétipo,
    o nome de um monstro ou o custo de uma skill são valores — mudam sem que a
    regra mude, e por isso vivem no JSON.
    """

    def test_arquetipos_vem_do_json(self):
        from src.content.factories.archetypes import all_archetypes

        dados = json.loads((SRC / "data" / "monsters.json").read_text(encoding="utf-8"))
        assert set(all_archetypes()) == set(dados["archetypes"]), (
            "Os arquétipos carregados divergem do JSON — há papel definido em Python."
        )

    def test_todo_arquetipo_declara_orcamento_e_papel_no_json(self):
        dados = json.loads((SRC / "data" / "monsters.json").read_text(encoding="utf-8"))
        for role, payload in dados["archetypes"].items():
            assert set(payload["budget"]) == {"hp", "attack", "defense", "agility"}, role
            assert payload["threat"] and payload["counterplay"], (
                f"{role} não declara ameaça e counterplay no JSON."
            )

    def test_geracao_de_andar_vem_do_json(self):
        dados = json.loads((SRC / "data" / "monsters.json").read_text(encoding="utf-8"))
        geracao = dados["generation"]
        for chave in (
            "base_count", "min_monsters", "scaling_per_3_levels",
            "advanced_role_min_floor", "advanced_roles", "elite_spawn_chance",
            "level_variation",
        ):
            assert chave in geracao, f"generation.{chave} ausente do JSON."

    @pytest.mark.parametrize("arquivo", ["items.json", "skills.json", "passives.json", "monsters.json"])
    def test_json_de_conteudo_e_valido_e_versionado(self, arquivo):
        dados = json.loads((SRC / "data" / arquivo).read_text(encoding="utf-8"))
        assert dados.get("version"), f"{arquivo} sem campo version."
        assert dados.get("description"), f"{arquivo} sem descrição."


class TestConstantesNomeadas:
    """Números que governam regra vivem em `shared/constants.py`, com nome.

    O objetivo não é banir todo literal — `+ 1`, `/ 100` e índices são ruído
    inevitável. É garantir que nenhum número de balanceamento fique escondido no
    meio de uma função, onde ninguém acha para ajustar.
    """

    # Literais que não carregam significado de balanceamento.
    IGNORADOS = {0, 1, 2, 10, 100, -1}

    def test_modulos_de_regra_nao_escondem_numeros_de_balanceamento(self):
        suspeitos = []
        for modulo in ("mechanics/combat.py", "mechanics/battle.py", "mechanics/monster_ai.py",
                       "entities/heroes.py", "entities/monsters.py"):
            path = SRC / modulo
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
                    if node.value in self.IGNORADOS or isinstance(node.value, bool):
                        continue
                    suspeitos.append(f"{modulo}:{node.lineno} — {node.value}")
        assert not suspeitos, (
            "Números de balanceamento fora de shared/constants.py:\n" + "\n".join(suspeitos)
        )

    def test_constantes_de_balanceamento_existem_e_sao_coerentes(self):
        from src.shared import constants as k

        assert k.GROWTH_RATE > 1.0
        assert k.XP_LEVEL_RATIO > k.GROWTH_RATE, (
            "O custo de nível precisa crescer mais rápido que os atributos, "
            "senão o herói nunca fica atrás do andar."
        )
        assert 0 < k.HIT_CHANCE_FLOOR < k.HIT_CHANCE_CEIL <= 100
        assert 0 < k.FLOOR_CLEAR_RESTORE_PERCENT < 100


class TestDocumentacao:
    """ARCHITECTURE.md precisa descrever o código que existe."""

    def test_arquitetura_menciona_todos_os_pacotes(self):
        texto = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        pacotes = {p.name for p in SRC.iterdir() if p.is_dir() and not p.name.startswith("__")}
        ausentes = [p for p in sorted(pacotes) if f"{p}/" not in texto]
        assert not ausentes, f"Pacotes ausentes de ARCHITECTURE.md: {ausentes}"

    def test_arquitetura_nao_cita_arquivos_inexistentes(self):
        texto = (ROOT / "ARCHITECTURE.md").read_text(encoding="utf-8")
        for citado in ("SPRINTS.md", "savegame.json"):
            assert citado not in texto, (
                f"ARCHITECTURE.md cita {citado}, que não existe no repositório."
            )
