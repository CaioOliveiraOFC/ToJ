"""A Arena offline jogável: menu, seleção, preparação, adversário, duelo e volta.

Os gladiadores DO JOGADOR daqui são FIXTURES de teste: heróis construídos pelo
jogo, marcados como extraídos e gravados num diretório de saves temporário. O
jogo de verdade só lista o que está em save. Os ADVERSÁRIOS são da população
offline de verdade (`src/data/arena_populacao/`): um catálogo pequeno com um
gladiador de cada classe, copiado do catálogo do jogo com os mesmos bytes.

O teclado é roteirizado. Quando o roteiro acaba, `Teclado` responde como um
jogador que só ataca: "1" no menu de ação, qualquer tecla nos avisos e "q" nas
listas e no fim da partida — o que devolve o fluxo ao menu principal.

O adversário é a IA estratégica com um orçamento menor de continuações
(`IA_RAPIDA`): a mesma decisão por simulação, em menos tempo de teste.
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
from src.engine import arena_mode, arena_populacao, arena_setup, bootstrap  # noqa: E402
from src.engine.arena_historico import HistoricoDaSessao, identidade_do_gladiador  # noqa: E402
from src.mechanics.pvp_duel import Duel, DuelAction  # noqa: E402
from src.sim.harness import make_hero  # noqa: E402
from src.sim.ia_estrategica import Configuracao, IAEstrategica  # noqa: E402
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


IA_RAPIDA = Configuracao(rollouts=2, rollouts_criticos=3)


def ia_rapida(heroi):
    return IAEstrategica(heroi, IA_RAPIDA)


def catalogo_pequeno(destino: Path, ids=None) -> arena_populacao.Populacao:
    """Um catálogo de teste com os mesmos bytes do catálogo do jogo.

    Sem `ids`, o gladiador de menor força de cada classe.
    """
    jogo = arena_populacao.Populacao()
    if ids is None:
        ids = [jogo.oponentes(classe)[0].id for classe in ("warrior", "mage", "rogue")]
    indice = json.loads((jogo.pasta / "indice.json").read_text(encoding="utf-8"))
    escolhidos = [g for g in indice["gladiadores"] if g["id"] in ids]
    destino.mkdir(parents=True, exist_ok=True)
    for g in escolhidos:
        (destino / g["arquivo"]).write_bytes((jogo.pasta / g["arquivo"]).read_bytes())
    (destino / "indice.json").write_text(
        json.dumps({**indice, "gladiadores": escolhidos}, ensure_ascii=False), encoding="utf-8"
    )
    return arena_populacao.Populacao(destino, limites=(1, 256))


@pytest.fixture
def populacao(tmp_path):
    return catalogo_pequeno(tmp_path / "populacao")


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


def jogar_arena(monkeypatch, populacao, roteiro=(), seed=1, **kwargs):
    teclado = Teclado(roteiro)
    monkeypatch.setattr(arena_mode, "safe_get_key", teclado)
    kwargs.setdefault("controlador", ia_rapida)
    kwargs.setdefault("historico", HistoricoDaSessao())
    arena_mode.run_arena(rng=random.Random(seed), populacao=populacao, **kwargs)
    return teclado


def sem_duelo(monkeypatch, lutas: list) -> None:
    """Troca o duelo por um registro de quem chegou a ele, e volta à lista."""
    monkeypatch.setattr(
        arena_mode,
        "duel",
        lambda personagem, adversario, **k: lutas.append((personagem, adversario)),
    )
    monkeypatch.setattr(arena_mode, "resultado_da_partida", lambda *a: None)
    monkeypatch.setattr(arena_mode, "_mostrar_resultado", lambda *a: "voltar")


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
        monkeypatch.setattr(bootstrap, "run_arena_hub", lambda: chamadas.append("arena"))
        bootstrap.run_main_loop()
        assert chamadas == ["arena"]

    def test_q_na_lista_volta_sem_duelo(self, saves, tela, populacao, monkeypatch):
        salvar(1, "Warrior", 10)
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        jogar_arena(monkeypatch, populacao, ["q"])
        assert lutas == []

    def test_depois_do_resultado_volta_para_a_lista_e_dali_ao_menu(
        self, saves, tela, populacao, monkeypatch
    ):
        salvar(1, "Warrior", 10)
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
        teclado = jogar_arena(monkeypatch, populacao, ["enter", "enter", "enter", "enter"])
        texto = tela.export_text()
        assert "VITÓRIA" in texto or "DERROTA" in texto
        # Depois do duelo, o "q" do fim da partida volta à lista, e o "q" da
        # lista sai da Arena.
        assert listas == ["ESCOLHA SEU GLADIADOR", "ESCOLHA SEU GLADIADOR"]
        assert teclado.roteiro == []

    def test_populacao_adulterada_bloqueia_a_arena(self, saves, tela, tmp_path, monkeypatch):
        salvar(1, "Warrior", 10)
        pasta = tmp_path / "adulterada"
        catalogo_pequeno(pasta)
        indice = json.loads((pasta / "indice.json").read_text(encoding="utf-8"))
        indice["versao"] = 999
        (pasta / "indice.json").write_text(json.dumps(indice), encoding="utf-8")
        monkeypatch.setattr(
            arena_mode, "Populacao", lambda: arena_populacao.Populacao(pasta, limites=(1, 256))
        )
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        teclado = Teclado()
        monkeypatch.setattr(arena_mode, "safe_get_key", teclado)
        arena_mode.run_arena(rng=random.Random(1), historico=HistoricoDaSessao())
        assert "conferência de integridade" in tela.export_text()
        assert lutas == []


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

    def test_sem_gladiador_extraido_explica_e_volta(self, saves, tela, populacao, monkeypatch):
        salvar(2, "Rogue", 8, extraido=False)
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        jogar_arena(monkeypatch, populacao)
        texto = tela.export_text()
        assert "Extração" in texto and "0 gladiador" in texto
        assert lutas == []

    def test_um_gladiador_extraido_basta(self, saves, tela, populacao, monkeypatch):
        salvar(1, "Warrior", 10)
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        jogar_arena(monkeypatch, populacao, ["enter", "enter", "enter", "enter"])
        assert len(lutas) == 1

    def test_o_adversario_vem_da_populacao_offline(self, saves, tela, populacao, monkeypatch):
        salvar(1, "Warrior", 10)
        salvar(3, "Mage", 10)
        listas: list = []
        original = arena_screens.render_opponent_list
        monkeypatch.setattr(
            arena_screens,
            "render_opponent_list",
            lambda oponentes, *a: (
                listas.append([o.id for o in oponentes]),
                original(oponentes, *a),
            ),
        )
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        jogar_arena(monkeypatch, populacao, ["s", "enter", "enter", "s", "enter", "enter"])
        ordem = [o.id for o in populacao.oponentes()]
        assert listas[0] == ordem
        personagem, adversario = lutas[0]
        assert personagem.get_nick_name() == "Mage3"
        segundo = populacao.get(ordem[1])
        assert adversario.name == segundo.apelido
        assert adversario.hero.get_classname().lower() == segundo.classe
        assert adversario.hero.base_hp == adversario.hero.get_hp()

    def test_filtro_de_classe_e_paginas(self, saves, tela, tmp_path, monkeypatch):
        jogo = arena_populacao.Populacao()
        ids = [o.id for o in jogo.oponentes("rogue")[:20]] + [jogo.oponentes("mage")[0].id]
        populacao = catalogo_pequeno(tmp_path / "grande", ids)
        salvar(1, "Warrior", 10)
        vistas: list = []
        original = arena_screens.render_opponent_list
        monkeypatch.setattr(
            arena_screens,
            "render_opponent_list",
            lambda oponentes, cursor, filtro, pagina, paginas, total: (
                vistas.append(
                    (filtro, pagina, paginas, total, oponentes[cursor].id if oponentes else None)
                ),
                original(oponentes, cursor, filtro, pagina, paginas, total),
            ),
        )
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        # Todas → Warrior (vazio) → Mage → Rogue; página seguinte; escolher.
        jogar_arena(
            monkeypatch, populacao, ["enter", "enter", "f", "f", "f", "d", "enter", "enter"]
        )
        assert [v[0] for v in vistas[:4]] == ["todas", "Warrior", "Mage", "Rogue"]
        assert vistas[1][3] == 0 and vistas[2][3] == 1 and vistas[3][3] == 20
        rogues = [o.id for o in populacao.oponentes("rogue")]
        assert vistas[4][1:4] == (2, 2, 20) and vistas[4][4] == rogues[arena_mode.POR_PAGINA]
        assert lutas[0][1].name == populacao.get(rogues[arena_mode.POR_PAGINA]).apelido

    def test_oponente_com_arquivo_adulterado_nao_luta(self, saves, tela, tmp_path, monkeypatch):
        populacao = catalogo_pequeno(tmp_path / "pop")
        primeiro = populacao.oponentes()[0]
        alvo = populacao.pasta / primeiro.arquivo
        alvo.write_bytes(alvo.read_bytes().replace(b'"level": ', b'"level": 1', 1))
        salvar(1, "Warrior", 10)
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        jogar_arena(monkeypatch, populacao, ["enter", "enter", "enter", "x", "q"])
        assert lutas == []
        assert "não pode lutar" in tela.export_text()


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

    def _trocar_e_confirmar(self, monkeypatch, populacao, resposta):
        arma = _arma_solta("Warrior")
        salvar(1, "Warrior", 10, extras=[arma])
        antes = ler(1)
        # A arma solta é o único equipável da mochila, e a mochila lista
        # equipável antes de consumível: ela está sob o cursor. Equipar na
        # posição 1 (as duas mãos já estão ocupadas pelo loadout), sair.
        teclas = iter(["e", "1", "q"])
        monkeypatch.setattr(navigation_menu, "get_key", lambda: next(teclas, "q"))
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        jogar_arena(
            monkeypatch, populacao, ["enter", "e", "enter", resposta, "x", "enter", "enter"]
        )
        return antes, [personagem for personagem, _ in lutas]

    def test_sem_gravar_o_save_fica_intacto(self, saves, tela, populacao, monkeypatch):
        antes, lutas = self._trocar_e_confirmar(monkeypatch, populacao, "n")
        assert ler(1) == antes
        assert lutas, "a configuração confirmada não chegou ao duelo"

    def test_gravar_muda_so_o_equipamento(self, saves, tela, populacao, monkeypatch):
        antes, lutas = self._trocar_e_confirmar(monkeypatch, populacao, "s")
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
        # Gravar equipamento não muda quem o gladiador é para o histórico.
        assert identidade_do_gladiador(velho, 1) == identidade_do_gladiador(novo, 1)

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

    def test_a_ficha_do_adversario_aparece_antes_de_confirmar(
        self, saves, tela, populacao, monkeypatch
    ):
        salvar(1, "Warrior", 10)
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
        lutas: list = []
        sem_duelo(monkeypatch, lutas)
        # A ficha aparece, e "q" nela volta à lista sem lutar.
        jogar_arena(monkeypatch, populacao, ["enter", "enter", "enter", "q", "q"])
        primeiro = populacao.oponentes()[0]
        assert ("Adversário", primeiro.apelido) in fichas
        assert lutas == []
        texto = tela.export_text()
        assert primeiro.id in texto and "controlado pela IA" in texto


def prepare_gladiator_safe(heroi):
    """A ficha é a do gladiador pronto: o herói de teste marcado e preparado."""
    marcado = copy.deepcopy(heroi)
    mark_extracted(marcado, 1)
    return prepare_gladiator(marcado).hero


# ---------------------------------------------------------------------------
# 7, 8, 9 — o duelo: ação manual, IA e a rodada na tela
# ---------------------------------------------------------------------------


def _gladiadores(populacao, nivel_meu=10, classe_minha="Warrior", classe_outra="mage"):
    meu = make_hero(classe_minha, nivel_meu, "expected")
    meu.nick_name = "Eu"
    mark_extracted(meu, nivel_meu)
    return meu, populacao.gladiador(populacao.oponentes(classe_outra)[0])


class TestDuelo:
    def test_a_skill_escolhida_pelo_jogador_chega_ao_motor(self, tela, populacao, monkeypatch):
        meu, outro = _gladiadores(populacao)
        duelo = Duel(prepare_gladiator(meu), outro, rng=random.Random(3))
        humano = arena_mode.HumanDuelController(duelo.hero("p1"))
        tecla, skill = next(iter(sorted(duelo.hero("p1").skills.items())))
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado(["2", str(tecla)]))
        acao = humano.choose(duelo.view("p1"))
        assert acao == DuelAction.use_skill(skill.id)
        registro = duelo.play_round({"p1": acao, "p2": DuelAction.attack()})
        assert dict(registro.actions)["p1"] == acao
        assert next(p for p in registro.steps if p.side == "p1").outcome == "executed"

    def test_skill_indisponivel_nao_e_escolhivel(self, tela, populacao, monkeypatch):
        meu, outro = _gladiadores(populacao)
        duelo = Duel(prepare_gladiator(meu), outro, rng=random.Random(3))
        duelo.hero("p1")._mp = 0
        humano = arena_mode.HumanDuelController(duelo.hero("p1"))
        tecla = next(iter(sorted(duelo.hero("p1").skills)))
        assert humano.skill_rows(duelo.view("p1"))[0][3] == "MP insuficiente"
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado(["2", str(tecla), "x", "0", "1"]))
        assert humano.choose(duelo.view("p1")) == DuelAction.attack()

    def test_o_adversario_padrao_e_a_ia_e_so_trava_acao_legal(self, tela, populacao, monkeypatch):
        acoes: list = []

        class Conferida(IAEstrategica):
            def __init__(self, heroi):
                super().__init__(heroi, IA_RAPIDA)

            def choose(self, view):
                acao = super().choose(view)
                assert acao in view.legal_actions and acao.kind != "surrender"
                acoes.append(acao)
                return acao

        monkeypatch.setattr(arena_mode, "IAEstrategica", Conferida)
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado())
        meu, outro = _gladiadores(populacao)
        duelo = arena_mode.duel(meu, outro, rng=random.Random(5))
        assert duelo.finished and len(acoes) == duelo.result.rounds

    def test_a_rodada_aparece_na_ordem_resolvida_pelo_motor(self, tela, populacao, monkeypatch):
        resumos: list = []
        original = arena_screens.render_round_summary
        monkeypatch.setattr(
            arena_screens,
            "render_round_summary",
            lambda texto: (resumos.append(list(texto)), original(texto)),
        )
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado())
        meu, outro = _gladiadores(populacao)
        duelo = arena_mode.duel(meu, outro, rng=random.Random(5), controlador=ia_rapida)
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

    def test_a_tela_mostra_hp_mp_e_efeitos_do_adversario(self, tela, populacao, monkeypatch):
        quadros: list = []
        monkeypatch.setattr(
            arena_screens, "render_duel_frame", lambda view, log: quadros.append(view.opponent)
        )
        monkeypatch.setattr(arena_mode, "safe_get_key", Teclado())
        meu, outro = _gladiadores(populacao)
        duelo = arena_mode.duel(meu, outro, rng=random.Random(5), controlador=ia_rapida)
        assert len(quadros) == duelo.result.rounds or duelo.result.reason == "surrender"
        primeiro = quadros[0]
        assert (primeiro.hp, primeiro.hp_max) == (outro.hero.base_hp, outro.hero.base_hp)
        assert primeiro.mp_max == outro.hero.base_mp
        assert primeiro.name == outro.name


# ---------------------------------------------------------------------------
# 10, 12 — vitória, derrota, rendição, revanche, e o save intocado
# ---------------------------------------------------------------------------


class TestFimEPersistencia:
    def _partida(self, saves, tela, populacao, monkeypatch, meu, roteiro=(), alvo="mage"):
        salvar(1, *meu)
        antes = ler(1)
        resultados: list = []
        original = arena_screens.render_duel_result
        monkeypatch.setattr(
            arena_screens,
            "render_duel_result",
            lambda *a: (resultados.append(a), original(*a)),
        )
        # O alvo é o primeiro da lista ordenada por força; ele é escolhido
        # descendo o cursor até ele.
        ordem = [o.id for o in populacao.oponentes()]
        descer = ["s"] * ordem.index(populacao.oponentes(alvo)[0].id)
        historico = HistoricoDaSessao()
        jogar_arena(
            monkeypatch,
            populacao,
            ["enter", "enter", *descer, "enter", "enter", *roteiro],
            seed=11,
            historico=historico,
        )
        return resultados, antes, historico

    def test_vitoria(self, saves, tela, populacao, monkeypatch):
        resultados, _, historico = self._partida(
            saves, tela, populacao, monkeypatch, ("Warrior", 40)
        )
        ganhou, vencedor, perdedor, motivo, _ = resultados[0]
        assert ganhou and (vencedor, motivo) == ("Warrior1", "nocaute")
        assert historico.partidas()[0].venceu

    def test_derrota(self, saves, tela, populacao, monkeypatch):
        resultados, _, historico = self._partida(
            saves, tela, populacao, monkeypatch, ("Mage", 2), alvo="rogue"
        )
        ganhou, vencedor, perdedor, motivo, _ = resultados[0]
        assert not ganhou and perdedor == "Mage1" and motivo == "nocaute"
        assert historico.placar(historico.partidas()[0].jogador.identidade) == (0, 1)

    def test_rendicao(self, saves, tela, populacao, monkeypatch):
        resultados, _, historico = self._partida(
            saves, tela, populacao, monkeypatch, ("Warrior", 20), roteiro=["3", "s"]
        )
        ganhou, vencedor, perdedor, motivo, rodadas = resultados[0]
        assert not ganhou and (perdedor, motivo, rodadas) == ("Warrior1", "rendição", 1)
        assert historico.partidas()[0].motivo == "surrender"

    def test_revanche_e_outro_adversario(self, saves, tela, populacao, monkeypatch):
        # Rendição, revanche (mesmo oponente), rendição, outro adversário (o
        # primeiro da lista que não é o Mage do alvo), rendição, voltar. O "x"
        # é a tecla do resumo da rodada.
        alvo = populacao.oponentes("mage")[0].id
        outro = next(i for i, o in enumerate(populacao.oponentes()) if o.id != alvo)
        roteiro = [
            *("3", "s", "x", "r", "3", "s", "x", "a"),
            *["s"] * outro,
            *("enter", "enter", "3", "s", "x", "q"),
        ]
        _, _, historico = self._partida(
            saves, tela, populacao, monkeypatch, ("Warrior", 20), roteiro=roteiro
        )
        partidas = historico.partidas()
        assert len(partidas) == 3
        assert partidas[0].oponente == partidas[1].oponente != partidas[2].oponente
        assert historico.placar(partidas[0].jogador.identidade) == (0, 3)
        assert "Nesta sessão: 0 vitória(s), 3 derrota(s)" in tela.export_text()

    def test_o_save_sai_da_partida_como_entrou(self, saves, tela, populacao, monkeypatch):
        _, antes, _ = self._partida(saves, tela, populacao, monkeypatch, ("Mage", 2))
        # Perdeu, e continua existindo: mesmo arquivo, byte a byte — sem HP
        # perdido, sem XP, sem ouro, sem troféu de morte.
        assert ler(1) == antes
        assert [e.slot for e in arena_setup.list_gladiators()] == [1]
        assert not (saves / save_manager.TROPHY_FILE).exists()

    def test_o_catalogo_sai_da_partida_como_entrou(self, saves, tela, populacao, monkeypatch):
        bytes_antes = {o.id: (populacao.pasta / o.arquivo).read_bytes() for o in populacao}
        self._partida(saves, tela, populacao, monkeypatch, ("Warrior", 20))
        assert {o.id: (populacao.pasta / o.arquivo).read_bytes() for o in populacao} == bytes_antes


# ---------------------------------------------------------------------------
# Histórico e classificação: os pontos de extensão do MMR
# ---------------------------------------------------------------------------


class TestPontosDeExtensaoDoMMR:
    def test_cada_partida_vira_um_resultado_e_passa_pela_classificacao(
        self, saves, tela, populacao, monkeypatch
    ):
        salvar(1, "Warrior", 20)
        vistos: list = []

        class Espia:
            def atualizar(self, resultado):
                vistos.append(resultado)

            def rating(self, identidade):
                return None

        historico = HistoricoDaSessao()
        jogar_arena(
            monkeypatch,
            populacao,
            ["enter", "enter", "enter", "enter", "3", "s"],
            historico=historico,
            classificacao=Espia(),
        )
        assert vistos == historico.partidas() and len(vistos) == 1
        resultado = vistos[0]
        oponente = populacao.oponentes()[0]
        assert resultado.oponente.identidade == oponente.identidade
        assert resultado.oponente.forca_de_referencia == oponente.op
        assert resultado.jogador.forca_de_referencia is None
        assert resultado.jogador.identidade == identidade_do_gladiador(
            save_manager.load_save_data(1), 1
        )
        assert resultado.versao_do_catalogo == arena_populacao.VERSAO_DO_CATALOGO

    def test_a_classificacao_padrao_nao_tem_formula(self):
        from src.engine.arena_historico import SemClassificacao

        assert SemClassificacao().rating("qualquer") is None

    def test_identidade_muda_com_outra_run_no_mesmo_slot(self, saves):
        salvar(1, "Warrior", 10)
        primeira = identidade_do_gladiador(save_manager.load_save_data(1), 1)
        salvar(1, "Warrior", 11)
        assert identidade_do_gladiador(save_manager.load_save_data(1), 1) != primeira
