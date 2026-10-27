"""O mundo ranqueado local: persistência, identidade, reservas, retorno e o agendador.

A Ladder daqui é a da população real com a priori fraca do OP (sem a calibração
publicada), gravada num diretório temporário. Os confrontos do agendador são de
mentira (`jogar` injetado, determinístico) — exceto um, que passa pelo motor de
verdade.
"""

from __future__ import annotations

import json
import sys
import threading
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.engine import ranked_mundo as rm  # noqa: E402
from src.engine import ranked_partidas  # noqa: E402
from src.engine.arena_historico import identidade_do_gladiador  # noqa: E402
from src.engine.arena_populacao import Populacao  # noqa: E402
from src.ranked import sistema  # noqa: E402
from src.ranked.ladder import Ladder, Registro  # noqa: E402

DIA = rm.SEGUNDOS_POR_DIA


@pytest.fixture(scope="module")
def populacao():
    return Populacao()


def _mundo(populacao, tmp_path, semente=7) -> rm.MundoRanqueado:
    sis = sistema.criar()
    ladder = Ladder(
        sis,
        [
            Registro(
                o.id,
                o.apelido,
                o.classe,
                True,
                sistema.inicial(sis, o.op),
                forca_de_referencia=o.op,
            )
            for o in populacao.oponentes()
        ],
    )
    return rm.MundoRanqueado(
        ladder, populacao, semente=semente, caminho=str(tmp_path / "ranked.json")
    )


def _falso(populacao, a, b, semente, parar=None, **_):
    """Um confronto sem motor: vence quem tem o id menor, se a semente for par."""
    vencedor = min(a, b) if semente % 2 == 0 else max(a, b)
    return ranked_partidas.Confronto(a, b, semente, vencedor, "ko", 10, 0.0)


class TestPersistencia:
    def test_ida_e_volta_pelo_arquivo(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.inscrever("jogador:slot1:abc", "Eu", "Warrior")
        mundo.registrar_do_jogador("jogador:slot1:abc", "W01", True)
        relido = rm.MundoRanqueado.carregar(populacao, mundo.caminho)
        assert relido.para_dict() == mundo.para_dict()
        assert relido.ladder["jogador:slot1:abc"].vitorias == 1

    def test_arquivo_ilegivel_nao_e_sobrescrito(self, populacao, tmp_path):
        caminho = tmp_path / "ranked.json"
        caminho.write_text("{ quebrado", encoding="utf-8")
        with pytest.raises(rm.RankedInvalidaError):
            rm.MundoRanqueado.carregar(populacao, str(caminho))
        caminho.write_text(json.dumps({"versao": 99}), encoding="utf-8")
        with pytest.raises(rm.RankedInvalidaError):
            rm.MundoRanqueado.carregar(populacao, str(caminho))
        assert json.loads(caminho.read_text(encoding="utf-8")) == {"versao": 99}

    def test_gladiador_novo_no_catalogo_entra_sem_apagar_ninguem(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.ladder.registrar("W01", "W02", "W01", origem="mundo")
        dados = mundo.para_dict()
        dados["ladder"]["registros"] = [
            r for r in dados["ladder"]["registros"] if r["identidade"] != "R45"
        ]
        Path(mundo.caminho).write_text(json.dumps(dados), encoding="utf-8")
        relido = rm.MundoRanqueado.carregar(populacao, mundo.caminho)
        assert "R45" in relido.ladder and relido.ladder["R45"].partidas == 0
        assert relido.ladder["W01"].vitorias == 1 and relido.ladder["W01"].historico


class TestIdentidade:
    def test_run_nova_no_slot_nao_herda_a_classificacao(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        velho = {"player_name": "Ana", "player_class": "Mage", "level": 20, "xp": 10}
        novo = dict(velho, level=3, xp=1)
        a, b = identidade_do_gladiador(velho, 1), identidade_do_gladiador(novo, 1)
        assert a != b
        mundo.inscrever(a, "Ana", "Mage")
        for k in range(3):
            mundo.registrar_do_jogador(a, f"W0{k + 1}", True)
        registro = mundo.inscrever(b, "Ana", "Mage")
        assert registro.partidas == 0 and not registro.historico
        assert mundo.ladder.valor(b) == sistema.criar().novo().rating

    def test_equipamento_nao_muda_a_identidade(self):
        save = {"player_name": "Ana", "level": 20, "equipment": {"Weapon1": None}, "inventory": []}
        trocado = dict(save, equipment={"Weapon1": {"name": "Espada"}}, inventory=[{"name": "x"}])
        assert identidade_do_gladiador(save, 2) == identidade_do_gladiador(trocado, 2)


class TestMatchmakingNoMundo:
    def test_o_adversario_fica_reservado_ate_a_partida(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        eu = mundo.inscrever("jogador:x", "Eu", "Rogue").identidade
        primeiro = mundo.adversario(eu)
        assert mundo.adversario(eu) == primeiro
        assert rm.MundoRanqueado.carregar(populacao, mundo.caminho).adversario(eu) == primeiro
        mundo.registrar_do_jogador(eu, primeiro, False)
        assert eu not in mundo.reservas

    def test_o_adversario_e_deterministico(self, populacao, tmp_path):
        um = _mundo(populacao, tmp_path / "a")
        dois = _mundo(populacao, tmp_path / "b")
        for mundo in (um, dois):
            mundo.inscrever("jogador:x", "Eu", "Rogue")
        assert um.adversario("jogador:x") == dois.adversario("jogador:x")


class TestRetorno:
    def test_a_primeira_sessao_so_marca_o_relogio(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        assert mundo.ao_retornar(1000.0) == {"dias": 0.0, "fila_nova": 0}
        assert mundo.ultima_sessao == 1000.0 and mundo.fila == 0

    def test_dias_fora_aumentam_a_incerteza_e_a_fila_e_limitada(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.ao_retornar(0.0)
        antes = mundo.ladder.incerteza("W10")
        volta = mundo.ao_retornar(3 * DIA)
        assert volta["dias"] == 3 and volta["fila_nova"] == rm.FILA_AO_RETORNAR
        assert mundo.ladder.incerteza("W10") >= antes
        # Um ano fora: a inatividade e a fila têm teto.
        volta = mundo.ao_retornar(3 * DIA + 365 * DIA)
        assert volta["dias"] == rm.DIAS_MAXIMOS
        assert mundo.fila <= rm.FILA_MAXIMA

    def test_uma_hora_fora_poe_poucos_confrontos(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.ao_retornar(0.0)
        assert mundo.ao_retornar(3600.0)["fila_nova"] == rm.PARTIDAS_DO_MUNDO_POR_HORA


class TestMundoOrganico:
    def test_o_plano_e_deterministico_limitado_e_poupa_os_reservados(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        eu = mundo.inscrever("jogador:x", "Eu", "Rogue").identidade
        reservado = mundo.adversario(eu)
        mundo.fila = 5
        plano = mundo.planejar(10)
        assert len(plano) == 5 and plano == mundo.planejar(10)
        nomes = [i for a, b, _ in plano for i in (a, b)]
        assert reservado not in nomes and eu not in nomes and len(set(nomes)) == 10
        mundo.fila = 0
        assert mundo.planejar(10) == []

    def test_o_agendador_aplica_na_ordem_e_esvazia_a_fila(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.fila = 4
        plano = mundo.planejar(4)
        agente = rm.AgendadorDoMundo(mundo, lote=4, jogar=_falso)
        agente.iniciar()
        agente._thread.join(5)
        assert agente.coletar() == 4
        assert mundo.fila == 0 and mundo.relogio == 4
        for a, b, semente in plano:
            entrada = mundo.ladder[a].historico[-1]
            assert entrada["oponente"] == b and entrada["origem"] == "mundo"
            assert entrada["venceu"] == (_falso(populacao, a, b, semente).vencedor == a)
        gravado = json.loads(Path(mundo.caminho).read_text(encoding="utf-8"))
        assert gravado["relogio"] == 4

    def test_parar_interrompe_sem_aplicar_partida_pela_metade(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.fila = 3
        liberar = threading.Event()

        def lento(populacao, a, b, semente, parar=None, **_):
            liberar.wait(5)
            return None if parar.is_set() else _falso(populacao, a, b, semente)

        agente = rm.AgendadorDoMundo(mundo, lote=3, jogar=lento)
        agente.iniciar()
        agente._parar.set()
        liberar.set()
        assert agente.parar() == 0
        assert mundo.fila == 3 and mundo.relogio == 0

    def test_confronto_sem_vencedor_consome_a_vaga_e_nao_trava_o_mundo(self, populacao, tmp_path):
        """Regressão: há duplas que nunca terminam; o mundo não pode replanejá-las para sempre."""
        mundo = _mundo(populacao, tmp_path)
        mundo.fila = 3

        def empate(populacao, a, b, semente, parar=None, **_):
            return ranked_partidas.Confronto(a, b, semente, None, "limite", 500, 0.0)

        primeiro_plano = mundo.planejar(1)
        ((a, b, _),) = primeiro_plano
        antes = (mundo.ladder.valor(a), mundo.ladder.valor(b))
        agente = rm.AgendadorDoMundo(mundo, lote=1, jogar=empate)
        agente.iniciar()
        agente._thread.join(5)
        assert agente.coletar() == 1
        assert (mundo.relogio, mundo.fila) == (1, 2)
        assert (mundo.ladder.valor(a), mundo.ladder.valor(b)) == antes
        assert mundo.ladder[a].partidas == 0
        assert mundo.ladder[a].historico[-1]["venceu"] is None
        assert mundo.planejar(1) != primeiro_plano

    def test_o_limite_tecnico_devolve_confronto_sem_vencedor(self, populacao, monkeypatch):
        monkeypatch.setattr(ranked_partidas, "LIMITE_TECNICO", 1)
        confronto = ranked_partidas.jogar(populacao, "W30", "W31", 4)
        assert confronto is not None and confronto.vencedor is None
        assert confronto.motivo == "limite" and confronto.perdedor is None
        parar = threading.Event()
        parar.set()
        assert ranked_partidas.jogar(populacao, "W30", "W31", 4, parar=parar) is None

    def test_um_confronto_do_mundo_pelo_motor_de_verdade(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.fila = 1
        ((a, b, semente),) = mundo.planejar(1)
        confronto = ranked_partidas.jogar(populacao, a, b, semente)
        assert confronto is not None and confronto.vencedor in (a, b)
        de_novo = ranked_partidas.jogar(populacao, a, b, semente)
        assert (de_novo.vencedor, de_novo.rodadas, de_novo.motivo) == (
            confronto.vencedor,
            confronto.rodadas,
            confronto.motivo,
        )
        mundo.aplicar_do_mundo(confronto)
        assert mundo.ladder[confronto.vencedor].vitorias == 1
