"""O modo Arena jogável: menu, seleção, preparação, adversário, duelo e volta.

Os gladiadores daqui são FIXTURES de teste: heróis construídos pelo jogo,
marcados como extraídos e gravados num diretório de saves temporário. O jogo de
verdade só lista o que está em save.

O teclado é roteirizado. Quando o roteiro acaba, `Teclado` responde como um
jogador que só ataca: "1" no menu de ação, qualquer tecla nos avisos e "q" nas
listas — o que devolve o fluxo ao menu principal.
"""

from __future__ import annotations

import copy
import io
import json
import random
import sys
from pathlib import Path

import pytest
from rich.console import Console

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content.extraction import mark_extracted  # noqa: E402
from src.content.gladiator import GladiatorNotEligibleError, prepare_gladiator  # noqa: E402
from src.content.items import get_all_items  # noqa: E402
from src.content.passives import get_passive_by_id  # noqa: E402
from src.engine import arena_mode, arena_setup, bootstrap  # noqa: E402
from src.mechanics.pvp_duel import Duel, DuelAction  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.pvp_controllers import FirstLegalSkillController  # noqa: E402
from src.storage import save_manager  # noqa: E402
from src.ui import (  # noqa: E402
    arena_screens,
    combat_event_handlers,
    inventory_flow,
    navigation_menu,
    renderer,
    toj_menu,
)


class Teclado:
    """`safe_get_key` roteirizado, com o jogador que só ataca depois do roteiro."""

    def __init__(self, roteiro=()):
        self.roteiro = list(roteiro)
        self.pedidos: list = []

    def __call__(self, valid_keys=None, allow_escape=True):
        self.pedidos.append(valid_keys)
        if self.roteiro:
            return self.roteiro.pop(0)
        if valid_keys is None:
            return "x"
        if "1" in valid_keys:
            return "1"
        return "q"


@pytest.fixture
def saves(tmp_path, monkeypatch):
    monkeypatch.setattr(save_manager, "SAVE_DIR", str(tmp_path), raising=False)
    monkeypatch.setattr(
        save_manager, "get_slot_file", lambda slot: str(tmp_path / f"slot_{slot}.json")
    )
    return tmp_path


@pytest.fixture
def tela(monkeypatch):
    """A tela vai para um console em memória, sem pausa entre mensagens."""
    console = Console(record=True, width=160, file=io.StringIO())
    monkeypatch.setattr(arena_screens, "console", console)
    monkeypatch.setattr(renderer, "console", console)
    monkeypatch.setattr(combat_event_handlers, "sleep", lambda *_: None)
    monkeypatch.setattr(navigation_menu, "get_key", lambda: "q")
    return console


def _pocao():
    return next(i for i in get_all_items().values() if i.is_potion).instance()


def _arma_solta(classe):
    return next(
        i
        for i in get_all_items().values()
        if getattr(i, "slot", None) == "Weapon"
        and not getattr(i, "hands_required", 0) == 2
        and (not getattr(i, "classes", None) or classe in i.classes)
        and getattr(i, "shop_min_floor", 1) <= 3
    ).instance()


def salvar(slot, classe, nivel, *, extraido=True, nome=None, loadout="expected", extras=()):
    """Grava um personagem no slot. Extraído por padrão."""
    heroi = make_hero(classe, nivel, loadout)
    heroi.nick_name = nome or f"{classe}{slot}"
    heroi.inventory.append(_pocao())
    for item in extras:
        heroi.inventory.append(item)
    if extraido:
        mark_extracted(heroi, nivel)
    assert save_manager.save_game(heroi, nivel, None, slot=slot)["success"]
    return heroi


def ler(slot) -> str:
    return Path(save_manager.get_slot_file(slot)).read_text(encoding="utf-8")


def jogar_arena(monkeypatch, roteiro=(), seed=1):
    teclado = Teclado(roteiro)
    monkeypatch.setattr(arena_mode, "safe_get_key", teclado)
    arena_mode.run_arena(rng=random.Random(seed))
    return teclado


# ---------------------------------------------------------------------------
# 1, 11 — menu de entrada e volta
# ---------------------------------------------------------------------------


class TestMenu:
    def test_a_arena_esta_no_menu_principal(self, saves, monkeypatch):
        monkeypatch.setattr(toj_menu, "clear_screen", lambda: None)
        monkeypatch.setattr(toj_menu, "console", Console(file=io.StringIO()))
        monkeypatch.setattr(toj_menu, "safe_get_key", lambda **_: "3")
        assert toj_menu.main_menu() == "arena"

    def test_o_jogo_abre_a_arena_e_volta_ao_menu(self, monkeypatch):
        respostas = iter(["arena", "quit"])
        chamadas: list = []
        monkeypatch.setattr(bootstrap, "call_main_menu", lambda: next(respostas))
        monkeypatch.setattr(bootstrap, "run_arena", lambda: chamadas.append("arena"))
        bootstrap.run_main_loop()
        assert chamadas == ["arena"]

    def test_q_na_lista_volta_sem_duelo(self, saves, tela, monkeypatch):
        salvar(1, "Warrior", 10)
        salvar(2, "Mage", 10)
        duelos: list = []
        monkeypatch.setattr(arena_mode, "duel", lambda *a, **k: duelos.append(a))
        jogar_arena(monkeypatch, ["q"])
        assert duelos == []

    def test_depois_do_resultado_volta_para_a_lista_e_dali_ao_menu(self, saves, tela, monkeypatch):
        salvar(1, "Warrior", 10)
        salvar(2, "Mage", 10)
        listas: list = []
        original = arena_screens.render_gladiator_list
        monkeypatch.setattr(
            arena_screens,
            "render_gladiator_list",
            lambda titulo, entradas, cursor: (
                listas.append(titulo),
                original(titulo, entradas, cursor),
            ),
        )
        teclado = jogar_arena(monkeypatch, ["enter", "enter", "enter", "enter"])
        texto = tela.export_text()
        assert "VITÓRIA" in texto or "DERROTA" in texto
        # Depois do duelo a lista volta, e o "q" do jogador sai da Arena.
        assert listas[-1] == "ESCOLHA SEU GLADIADOR" and listas.count("ESCOLHA SEU GLADIADOR") == 2
        assert teclado.roteiro == []


# ---------------------------------------------------------------------------
# 2, 3 — quem pode lutar, e contra quem
# ---------------------------------------------------------------------------


class TestElegibilidade:
    def test_so_personagens_extraidos_sao_listados(self, saves):
        salvar(1, "Warrior", 10)
        salvar(2, "Rogue", 8, extraido=False)
        salvar(3, "Mage", 10)
        assert [e.slot for e in arena_setup.list_gladiators()] == [1, 3]

    def test_personagem_nao_extraido_nao_entra_por_nenhum_caminho(self, saves):
        salvar(2, "Rogue", 8, extraido=False)
        with pytest.raises(GladiatorNotEligibleError):
            arena_setup.load_character(2)
        with pytest.raises(GladiatorNotEligibleError):
            arena_setup.gladiator_from_slot(2)
        heroi = make_hero("Rogue", 8, "naked")
        heroi.nick_name = "Rogue2"
        with pytest.raises(GladiatorNotEligibleError):
            arena_setup.store_loadout(2, heroi)

    def test_com_menos_de_dois_gladiadores_explica_e_volta(self, saves, tela, monkeypatch):
        salvar(1, "Warrior", 10)
        salvar(2, "Rogue", 8, extraido=False)
        duelos: list = []
        monkeypatch.setattr(arena_mode, "duel", lambda *a, **k: duelos.append(a))
        jogar_arena(monkeypatch)
        texto = tela.export_text()
        assert "Extração" in texto and "1 gladiador" in texto
        assert duelos == []

    def test_o_adversario_e_outro_gladiador_valido(self, saves, tela, monkeypatch):
        salvar(1, "Warrior", 10)
        salvar(2, "Rogue", 8, extraido=False)
        salvar(3, "Mage", 10)
        salvar(4, "Rogue", 10)
        listas: list = []
        original = arena_screens.render_gladiator_list
        monkeypatch.setattr(
            arena_screens,
            "render_gladiator_list",
            lambda titulo, entradas, cursor: (
                listas.append((titulo, [e.slot for e in entradas])),
                original(titulo, entradas, cursor),
            ),
        )
        lutas: list = []
        monkeypatch.setattr(
            arena_mode,
            "duel",
            lambda personagem, adversario, **k: lutas.append((personagem, adversario)),
        )
        monkeypatch.setattr(arena_mode, "_mostrar_resultado", lambda duelo: None)
        jogar_arena(monkeypatch, ["s", "enter", "enter", "enter", "enter"])
        # A lista é redesenhada a cada passo do cursor: o que importa é a
        # sequência de telas DISTINTAS.
        telas = [t for i, t in enumerate(listas) if i == 0 or t != listas[i - 1]]
        assert telas[0] == ("ESCOLHA SEU GLADIADOR", [1, 3, 4])
        assert telas[1] == ("ESCOLHA O ADVERSÁRIO", [1, 4])
        personagem, adversario = lutas[0]
        assert personagem.get_nick_name() == "Mage3"
        assert adversario.name == "Warrior1"
        assert adversario.hero is not personagem


# ---------------------------------------------------------------------------
# 4, 5 — preparação: a mochila é do gladiador, e o save muda só se ele quiser
# ---------------------------------------------------------------------------


class TestPreparacao:
    def test_o_inventario_e_o_do_proprio_gladiador(self, saves):
        arma = _arma_solta("Warrior")
        salvar(1, "Warrior", 10, extras=[arma])
        salvar(2, "Mage", 10)
        meu = arena_setup.load_character(1)
        dados = save_manager.load_save_data(1)
        assert [i.name for i in meu.inventory] == [r["name"] for r in dados["inventory"]]
        outro = save_manager.load_save_data(2)
        so_do_outro = (
            {r["name"] for r in outro["equipment"].values() if r}
            - {r["name"] for r in dados["equipment"].values() if r}
            - {r["name"] for r in dados["inventory"]}
        )
        assert not so_do_outro & {i.name for i in meu.inventory}

    def test_consumivel_continua_na_mochila_e_nao_se_usa(self, monkeypatch):
        heroi = make_hero("Warrior", 10, "naked")
        pocao = _pocao()
        heroi.inventory.append(pocao)
        heroi._hp = heroi.base_hp // 2
        teclas = iter(["u", "u", "q"])
        monkeypatch.setattr(navigation_menu, "get_key", lambda: next(teclas))
        monkeypatch.setattr(renderer, "console", Console(file=io.StringIO()))
        inventory_flow.run_arena_loadout_flow(heroi)
        assert pocao in heroi.inventory
        assert heroi.get_hp() == heroi.base_hp // 2

    def test_equipar_usa_as_regras_de_sempre(self, monkeypatch):
        heroi = make_hero("Warrior", 10, "naked")
        arma = _arma_solta("Warrior")
        heroi.inventory.append(arma)
        teclas = iter(["e", "q"])
        monkeypatch.setattr(navigation_menu, "get_key", lambda: next(teclas))
        monkeypatch.setattr(renderer, "console", Console(file=io.StringIO()))
        inventory_flow.run_arena_loadout_flow(heroi)
        assert arma in heroi.equipment.values()

    def test_restricao_de_classe_continua_valendo(self, monkeypatch):
        heroi = make_hero("Warrior", 10, "naked")
        cajado = get_all_items()["Cajado de Aprendiz"].instance()
        assert cajado.classes == ["Mage"]
        heroi.inventory.append(cajado)
        teclas = iter(["e", "q"])
        monkeypatch.setattr(navigation_menu, "get_key", lambda: next(teclas))
        monkeypatch.setattr(renderer, "console", Console(file=io.StringIO()))
        inventory_flow.run_arena_loadout_flow(heroi)
        assert cajado not in heroi.equipment.values()
        assert cajado in heroi.inventory

    def _trocar_e_confirmar(self, monkeypatch, resposta):
        arma = _arma_solta("Warrior")
        salvar(1, "Warrior", 10, extras=[arma])
        salvar(2, "Mage", 10)
        antes = ler(1)
        # A arma solta é o único equipável da mochila, e a mochila lista
        # equipável antes de consumível: ela está sob o cursor. Equipar na
        # posição 1 (as duas mãos já estão ocupadas pelo loadout), sair.
        teclas = iter(["e", "1", "q"])
        monkeypatch.setattr(navigation_menu, "get_key", lambda: next(teclas, "q"))
        lutas: list = []
        monkeypatch.setattr(arena_mode, "duel", lambda p, a, **k: lutas.append(p))
        monkeypatch.setattr(arena_mode, "_mostrar_resultado", lambda duelo: None)
        jogar_arena(monkeypatch, ["enter", "e", "enter", resposta, "x", "enter", "enter"])
        return antes, lutas

    def test_sem_gravar_o_save_fica_intacto(self, saves, tela, monkeypatch):
        antes, lutas = self._trocar_e_confirmar(monkeypatch, "n")
        assert ler(1) == antes
        assert lutas, "a configuração confirmada não chegou ao duelo"

    def test_gravar_muda_so_o_equipamento(self, saves, tela, monkeypatch):
        antes, lutas = self._trocar_e_confirmar(monkeypatch, "s")
        velho, novo = json.loads(antes), json.loads(ler(1))
        assert velho["equipment"] != novo["equipment"]
        for campo in velho:
            if campo not in save_manager.CAMPOS_DE_EQUIPAMENTO:
                assert novo[campo] == velho[campo], campo
        # Nada some: o que saiu de um lugar foi para o outro, e a poção ficou.
        nomes = lambda d: sorted(  # noqa: E731
            [r["name"] for r in d["equipment"].values() if r] + [r["name"] for r in d["inventory"]]
        )
        assert nomes(novo) == nomes(velho)
        recarregado = arena_setup.load_character(1)
        assert {i.name for i in recarregado.equipment.values() if i} == {
            i.name for i in lutas[0].equipment.values() if i
        }

    def test_equipamento_nao_passa_para_outro_gladiador(self, saves):
        salvar(1, "Warrior", 10)
        salvar(2, "Warrior", 10)
        do_um = arena_setup.load_character(1)
        antes = ler(2)
        with pytest.raises(GladiatorNotEligibleError):
            arena_setup.store_loadout(2, do_um)
        assert ler(2) == antes


# ---------------------------------------------------------------------------
# 6 — a build do adversário, completa, antes do duelo
# ---------------------------------------------------------------------------


class TestBuildAdversaria:
    def test_a_ficha_mostra_nome_classe_nivel_equipamento_skills_e_passivas(self, tela):
        heroi = make_hero("Rogue", 12, "expected")
        heroi.nick_name = "Sombra"
        heroi.add_passive(get_passive_by_id("passos_leves"))
        arena_screens.render_build_sheet(prepare_gladiator_safe(heroi), "Adversário")
        texto = tela.export_text()
        for parte in ("Sombra", "Rogue", "Nível 12"):
            assert parte in texto
        for item in heroi.equipment.values():
            if item is not None:
                assert item.display_name in texto
        for skill in heroi.skills.values():
            assert skill.name in texto
        assert get_passive_by_id("passos_leves").name in texto

    def test_a_ficha_do_adversario_aparece_antes_de_confirmar(self, saves, tela, monkeypatch):
        salvar(1, "Warrior", 10)
        salvar(2, "Mage", 10, nome="Ilsa")
        fichas: list = []
        original = arena_screens.render_build_sheet
        monkeypatch.setattr(
            arena_screens,
            "render_build_sheet",
            lambda heroi, titulo: (
                fichas.append((titulo, heroi.get_nick_name())),
                original(heroi, titulo),
            ),
        )
        monkeypatch.setattr(arena_mode, "duel", lambda *a, **k: None)
        monkeypatch.setattr(arena_mode, "_mostrar_resultado", lambda duelo: None)
        jogar_arena(monkeypatch, ["enter", "enter", "enter", "q"])
        assert ("Adversário", "Ilsa") in fichas


def prepare_gladiator_safe(heroi):
    """A ficha é a do gladiador pronto: o herói de teste marcado e preparado."""
    marcado = copy.deepcopy(heroi)
    mark_extracted(marcado, 1)
    return prepare_gladiator(marcado).hero


# ---------------------------------------------------------------------------
# 7, 8, 9 — o duelo: ação manual, controlador automático e a rodada na tela
# ---------------------------------------------------------------------------


def _gladiadores(nivel_meu=10, nivel_outro=10, classe_minha="Warrior", classe_outra="Mage"):
    meu = make_hero(classe_minha, nivel_meu, "expected")
    meu.nick_name = "Eu"
    mark_extracted(meu, nivel_meu)
    outro = make_hero(classe_outra, nivel_outro, "expected")
    outro.nick_name = "Ele"
    mark_extracted(outro, nivel_outro)
    return meu, prepare_gladiator(outro)


class TestDuelo:
    def test_a_skill_escolhida_pelo_jogador_chega_ao_motor(self, tela, monkeypatch):
        meu, outro = _gladiadores()
        duelo = Duel(prepare_gladiator(meu), outro, rng=random.Random(3))
        humano = arena_mode.HumanDuelController(duelo.hero("p1"))
        tecla, skill = next(iter(sorted(duelo.hero("p1").skills.items())))
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado(["2", str(tecla)]))
        acao = humano.choose(duelo.view("p1"))
        assert acao == DuelAction.use_skill(skill.id)
        registro = duelo.play_round({"p1": acao, "p2": DuelAction.attack()})
        assert dict(registro.actions)["p1"] == acao
        assert next(p for p in registro.steps if p.side == "p1").outcome == "executed"

    def test_skill_indisponivel_nao_e_escolhivel(self, tela, monkeypatch):
        meu, outro = _gladiadores()
        duelo = Duel(prepare_gladiator(meu), outro, rng=random.Random(3))
        duelo.hero("p1")._mp = 0
        humano = arena_mode.HumanDuelController(duelo.hero("p1"))
        tecla = next(iter(sorted(duelo.hero("p1").skills)))
        assert humano.skill_rows(duelo.view("p1"))[0][3] == "MP insuficiente"
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado(["2", str(tecla), "x", "0", "1"]))
        assert humano.choose(duelo.view("p1")) == DuelAction.attack()

    def test_o_controlador_automatico_so_trava_acao_legal(self, tela, monkeypatch):
        acoes: list = []

        class Conferido(FirstLegalSkillController):
            def choose(self, view):
                acao = super().choose(view)
                assert acao in view.legal_actions
                acoes.append(acao)
                return acao

        monkeypatch.setattr(arena_mode, "FirstLegalSkillController", Conferido)
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado())
        meu, outro = _gladiadores()
        duelo = arena_mode.duel(meu, outro, rng=random.Random(5))
        assert duelo.finished and len(acoes) == duelo.result.rounds

    def test_a_rodada_aparece_na_ordem_resolvida_pelo_motor(self, tela, monkeypatch):
        resumos: list = []
        original = arena_screens.render_round_summary
        monkeypatch.setattr(
            arena_screens,
            "render_round_summary",
            lambda texto: (resumos.append(list(texto)), original(texto)),
        )
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado())
        meu, outro = _gladiadores()
        duelo = arena_mode.duel(meu, outro, rng=random.Random(5))
        assert len(resumos) == len(duelo.history)
        nomes = {lado: duelo.hero(lado).get_nick_name() for lado in ("p1", "p2")}
        for linhas, registro in zip(resumos, duelo.history):
            assert linhas == arena_mode.round_lines(registro, duelo)
            assert nomes[registro.order.first] in linhas[0]
            ordem_na_tela = [linha.split(":")[0] for linha in linhas[1:-1]]
            assert ordem_na_tela == [nomes[p.side] for p in registro.steps]
        texto = tela.export_text()
        assert "Rodada resolvida" in texto
        assert "score" not in texto.lower() and "iniciativa" not in texto.lower()


# ---------------------------------------------------------------------------
# 10, 12 — vitória, derrota, rendição, e o save intocado
# ---------------------------------------------------------------------------


class TestFimEPersistencia:
    def _duelo_completo(self, saves, tela, monkeypatch, meu, outro, roteiro=()):
        salvar(1, *meu)
        salvar(2, *outro)
        antes = {s: ler(s) for s in (1, 2)}
        resultados: list = []
        original = arena_screens.render_duel_result
        monkeypatch.setattr(
            arena_screens,
            "render_duel_result",
            lambda *a: (resultados.append(a), original(*a)),
        )
        jogar_arena(monkeypatch, ["enter", "enter", "enter", "enter", *roteiro], seed=11)
        assert len(resultados) == 1
        return resultados[0], antes

    def test_vitoria(self, saves, tela, monkeypatch):
        (ganhou, vencedor, perdedor, motivo, _), _ = self._duelo_completo(
            saves, tela, monkeypatch, ("Warrior", 20), ("Mage", 4)
        )
        assert ganhou and (vencedor, perdedor, motivo) == ("Warrior1", "Mage2", "nocaute")

    def test_derrota(self, saves, tela, monkeypatch):
        (ganhou, vencedor, perdedor, motivo, _), _ = self._duelo_completo(
            saves, tela, monkeypatch, ("Mage", 4), ("Warrior", 20)
        )
        assert not ganhou and (vencedor, perdedor, motivo) == ("Warrior2", "Mage1", "nocaute")

    def test_rendicao(self, saves, tela, monkeypatch):
        (ganhou, vencedor, perdedor, motivo, rodadas), _ = self._duelo_completo(
            saves, tela, monkeypatch, ("Warrior", 20), ("Mage", 4), roteiro=["3", "s"]
        )
        assert not ganhou
        assert (vencedor, perdedor, motivo, rodadas) == ("Mage2", "Warrior1", "rendição", 1)

    def test_os_dois_saves_saem_do_duelo_como_entraram(self, saves, tela, monkeypatch):
        _, antes = self._duelo_completo(saves, tela, monkeypatch, ("Mage", 4), ("Warrior", 20))
        # Perdeu, e continua existindo: mesmo arquivo, byte a byte — sem HP
        # perdido, sem XP, sem ouro, sem troféu de morte.
        assert {s: ler(s) for s in (1, 2)} == antes
        assert [e.slot for e in arena_setup.list_gladiators()] == [1, 2]
        assert not (saves / save_manager.TROPHY_FILE).exists()
