"""A régua de informação do BOT_PADRÃO, provada na ESTRUTURA.

O cérebro não pode receber objeto de jogo. Não é disciplina: é o que impede a
regressão que já aconteceu uma vez, quando a seleção de alvo passou a ler
`get_nick_name()` e `.level` de uma casa que o jogador vê como `&`.
"""

from __future__ import annotations

import ast
from dataclasses import MISSING
from pathlib import Path

import pytest

from src.sim.bot.observation import CombatState, MapState, ProgressionState, TargetView

CEREBRO = Path("src/sim/bot")
PROIBIDOS = ("src.engine", "src.entities", "src.content", "src.mechanics")


def _arquivos() -> list[Path]:
    arquivos = sorted(CEREBRO.glob("*.py"))
    assert arquivos, f"{CEREBRO} não casou com nenhum arquivo — a regra ficaria verde sem verificar"
    return arquivos


class TestOCerebroNaoVeOJogo:
    def test_nao_importa_engine_entities_content_nem_mechanics(self):
        for caminho in _arquivos():
            arvore = ast.parse(caminho.read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                modulos = []
                if isinstance(no, ast.Import):
                    modulos = [a.name for a in no.names]
                elif isinstance(no, ast.ImportFrom) and no.module:
                    modulos = [no.module]
                for modulo in modulos:
                    for proibido in PROIBIDOS:
                        assert not modulo.startswith(proibido), (
                            f"{caminho}:{no.lineno} importa {modulo} — o cérebro passaria a "
                            "receber objeto de jogo"
                        )

    def test_nenhum_parametro_se_chama_hero_ou_monstro(self):
        """Nome de parâmetro é o sintoma mais barato de a fronteira ter furado."""
        suspeitos = {"hero", "heroi", "herói", "monster", "monstro", "player", "jogador"}
        for caminho in _arquivos():
            arvore = ast.parse(caminho.read_text(encoding="utf-8"))
            for no in ast.walk(arvore):
                if not isinstance(no, ast.FunctionDef):
                    continue
                for arg in no.args.args + no.args.kwonlyargs:
                    assert arg.arg not in suspeitos, (
                        f"{caminho}:{no.lineno} {no.name}({arg.arg}) — parece receber o objeto real"
                    )

    def test_nenhum_campo_de_dataclass_e_do_tipo_any(self):
        """`Any` deixaria um `Hero` atravessar por dentro de uma view."""
        for caminho in _arquivos():
            texto = caminho.read_text(encoding="utf-8")
            arvore = ast.parse(texto)
            for no in ast.walk(arvore):
                if isinstance(no, ast.AnnAssign) and isinstance(no.annotation, ast.Name):
                    assert no.annotation.id != "Any", f"{caminho}:{no.lineno} tem campo `Any`"


class TestOQueOMapaMostra:
    def test_o_alvo_no_mapa_nao_identifica_o_monstro(self):
        """`draw_map` desenha `&` e `B`. Nome e nível não estão lá."""
        campos = set(TargetView.__dataclass_fields__)
        assert campos == {"casa", "passos", "extras", "chefe"}, (
            f"TargetView carrega informação que o mapa não mostra: {sorted(campos)}"
        )

    def test_o_estado_do_mapa_nao_tem_atributo_de_monstro(self):
        proibidos = {"nivel", "nome", "hp", "st", "df", "ag", "mg"}
        assert not (set(MapState.__dataclass_fields__) & proibidos)

    def test_progressao_nao_carrega_limiar_de_perfil(self):
        """`Perfil.hp_engajar` não pode voltar como gate por dentro do estado."""
        campos = set(ProgressionState.__dataclass_fields__)
        assert not {"hp_para_engajar", "mp_para_engajar", "hp_engajar", "mp_engajar"} & campos


class TestAFichaSoDepoisDaColisao:
    def test_o_estado_de_combate_precisa_dos_dados_revelados(self):
        """Não existe `CombatState` sem a ficha: os campos são obrigatórios.

        E ele NÃO depende de a UI ter sido chamada — em headless
        `render_fight_intro` nunca roda. Quem revela é a colisão.
        """
        with pytest.raises(TypeError):
            CombatState()  # type: ignore[call-arg]
        # Os atributos revelados pela ficha são campos SEM default: não existe
        # um `CombatState` meio montado, "antes de saber contra o que encostei".
        for revelado in ("alvo_nivel", "alvo_hp", "alvo_dano"):
            campo = CombatState.__dataclass_fields__[revelado]
            assert campo.default is MISSING, f"{revelado} tem default — daria estado sem ficha"

    def test_o_estado_de_combate_nao_carrega_acoes_legais(self):
        """Uma fonte só: estado é estado, ação legal é `tuple[ActionOption]`."""
        campos = set(CombatState.__dataclass_fields__)
        assert not {"acoes", "opcoes", "actions", "options"} & campos
