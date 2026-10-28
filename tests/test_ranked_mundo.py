"""O mundo ranqueado local: persistência, migração, identidade, reservas, retorno,
a leaderboard por ciclos e o agendador.

A Ladder daqui é a da população real com a priori fraca do OP (sem a calibração
publicada), fundada e gravada num diretório temporário. Os confrontos do
agendador são de mentira (`jogar` injetado, determinístico) — exceto um, que
passa pelo motor de verdade. O relógio é sempre injetado.
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
from src.ranked import progressao, sistema  # noqa: E402
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
    mundo = rm.MundoRanqueado(
        ladder, populacao, semente=semente, caminho=str(tmp_path / "ranked.json")
    )
    mundo.fundar()
    return mundo


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

    def test_empate_tecnico_vale_meio_ponto_e_consome_a_vaga(self, populacao, tmp_path):
        """Regressão: há duplas que nunca terminam; o mundo não pode replanejá-las para sempre."""
        mundo = _mundo(populacao, tmp_path)
        mundo.fila = 3

        def empate(populacao, a, b, semente, parar=None, **_):
            return ranked_partidas.Confronto(a, b, semente, None, "impasse", 339, 0.0)

        primeiro_plano = mundo.planejar(1)
        ((a, b, _),) = primeiro_plano
        agente = rm.AgendadorDoMundo(mundo, lote=1, jogar=empate)
        agente.iniciar()
        agente._thread.join(5)
        assert agente.coletar() == 1
        assert (mundo.relogio, mundo.fila) == (1, 2)
        assert mundo.ladder[a].partidas == 1 and mundo.ladder[a].empates == 1
        entrada = mundo.ladder[a].historico[-1]
        assert (entrada["resultado"], entrada["motivo"]) == ("empate", "impasse")
        assert mundo.planejar(1) != primeiro_plano

    def test_erro_tecnico_no_mundo_anula_e_consome_a_vaga(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.fila = 2

        def quebra(populacao, a, b, semente, parar=None, **_):
            raise RuntimeError("motor")

        ((a, b, _), _segundo) = mundo.planejar(2)
        antes = (mundo.ladder.valor(a), mundo.ladder.valor(b))
        agente = rm.AgendadorDoMundo(mundo, lote=2, jogar=quebra)
        agente.iniciar()
        agente._thread.join(5)
        assert agente.coletar() == 2 and mundo.fila == 0
        assert (mundo.ladder.valor(a), mundo.ladder.valor(b)) == antes
        assert mundo.ladder[a].partidas == 0
        entrada = mundo.ladder[a].historico[-1]
        assert entrada["resultado"] == "anulada" and "RuntimeError" in entrada["motivo"]

    def test_parar_devolve_none(self, populacao):
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


class TestResultadoDoJogador:
    def test_os_quatro_desfechos(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        eu = mundo.inscrever("jogador:x", "Eu", "Mage").identidade
        primeiro = mundo.adversario(eu)
        mundo.registrar_do_jogador(eu, primeiro, "anulada", motivo="interrompida")
        # Interrompida: nada conta e o adversário continua reservado.
        assert mundo.ladder[eu].partidas == 0 and mundo.adversario(eu) == primeiro
        assert mundo.fila == 0
        mundo.registrar_do_jogador(eu, primeiro, "anulada", motivo="erro técnico: X")
        assert eu not in mundo.reservas  # o erro técnico libera a reserva
        mundo.registrar_do_jogador(eu, mundo.adversario(eu), "empate", motivo="impasse")
        mundo.registrar_do_jogador(eu, mundo.adversario(eu), "vitoria")
        mundo.registrar_do_jogador(eu, mundo.adversario(eu), False)
        r = mundo.ladder[eu]
        assert (r.vitorias, r.derrotas, r.empates, r.partidas) == (1, 1, 1, 3)
        assert [e["resultado"] for e in r.historico] == [
            "anulada",
            "anulada",
            "empate",
            "vitoria",
            "derrota",
        ]
        with pytest.raises(ValueError):
            mundo.registrar_do_jogador(eu, mundo.adversario(eu), "talvez")


class TestLeaderboardPorCiclos:
    HORA = 3600

    def test_a_primeira_sessao_so_marca_o_ciclo(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        assert mundo.atualizar_leaderboard(10 * self.HORA + 30) is None
        assert mundo.leaderboard.ciclo == 10 and mundo.leaderboard.proxima() == 11 * self.HORA
        assert mundo.atualizar_leaderboard(11 * self.HORA - 1) is None

    def test_cada_ciclo_novo_publica_um_retrato(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.atualizar_leaderboard(10 * self.HORA)
        resumo = mundo.atualizar_leaderboard(11 * self.HORA + 5)
        assert resumo["ciclo"] == 11 and resumo["pulados"] == 0
        assert mundo.leaderboard.publicada_em == 11 * self.HORA + 5
        assert len(mundo.leaderboard.linhas) == len(populacao)
        gravado = json.loads(Path(mundo.caminho).read_text(encoding="utf-8"))
        assert gravado["leaderboard"]["ciclo"] == 11

    def test_dias_fechado_publicam_um_retrato_so(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.atualizar_leaderboard(10 * self.HORA)
        resumo = mundo.atualizar_leaderboard(10 * self.HORA + 3 * DIA)
        assert resumo["pulados"] == 71 and mundo.leaderboard.ciclo == 10 + 72
        assert mundo.atualizar_leaderboard(10 * self.HORA + 3 * DIA + 60) is None

    def test_ciclo_de_24_horas(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.leaderboard.periodo = DIA
        mundo.atualizar_leaderboard(5 * DIA + 7 * self.HORA)
        assert mundo.atualizar_leaderboard(5 * DIA + 23 * self.HORA) is None
        assert mundo.atualizar_leaderboard(6 * DIA + 1)["ciclo"] == 6

    def test_a_candidatura_atravessa_sessoes_e_e_avaliada_no_ciclo(self, populacao, tmp_path):
        mundo = _mundo(populacao, tmp_path)
        mundo.atualizar_leaderboard(10 * self.HORA)
        eu = mundo.inscrever("jogador:x", "Eu", "Mage").identidade
        registro = mundo.ladder[eu]
        registro.vitorias = 12
        registro.rating = mundo.ladder.sistema.novo(3000, 70)  # o primeiro da Ladder
        registro.progresso = progressao.Progresso(divisao=progressao.ULTIMA, pr=100, candidato=True)
        mundo.salvar()
        relido = rm.MundoRanqueado.carregar(populacao, mundo.caminho)
        assert relido.ladder[eu].progresso.candidato
        resumo = relido.atualizar_leaderboard(11 * self.HORA)
        assert relido.ladder[eu].progresso.elite == "Distinguished Master"
        assert relido.ladder[eu].progresso.titulo == "Definitive Master"
        evento = next(e for e in resumo["eventos"] if e["identidade"] == eu)
        assert evento["evento"] == "promocao_a_elite"
        assert rm.MundoRanqueado.carregar(populacao, mundo.caminho).ladder[eu].progresso.elite


class TestMigracaoERecuperacao:
    def _v1(self, tmp_path) -> Path:
        """O estado da Fase 6: a calibração publicada, com um jogador e uma reserva."""
        dados = json.loads(rm.INICIAL.read_text(encoding="utf-8"))
        assert dados["versao"] == 1
        dados["ladder"]["registros"].append(
            {
                "identidade": "jogador:slot1:abc",
                "nome": "Eu",
                "classe": "rogue",
                "npc": False,
                "rating": {"rating": 1700.0, "rd": 110.0, "volatilidade": 0.06},
                "vitorias": 7,
                "derrotas": 4,
                "historico": [
                    {
                        "n": 9,
                        "oponente": "M33",
                        "venceu": None,
                        "antes": 1690.0,
                        "depois": 1690.0,
                        "oponente_antes": 2100.0,
                        "origem": "ranqueada",
                    }
                ],
                "forca_de_referencia": None,
            }
        )
        dados["reservas"] = {"jogador:slot1:abc": "W10"}
        dados["ultima_sessao"] = 1000.0
        caminho = tmp_path / "ranked.json"
        caminho.write_text(json.dumps(dados), encoding="utf-8")
        return caminho

    def test_o_estado_da_fase_6_migra_sem_perder_nada(self, populacao, tmp_path):
        caminho = self._v1(tmp_path)
        original = caminho.read_text(encoding="utf-8")
        antigo = json.loads(original)
        mundo = rm.MundoRanqueado.carregar(populacao, str(caminho))
        # A cópia da v1 fica ao lado, idêntica, e o arquivo vira v2.
        assert (tmp_path / rm.COPIA_DA_V1).read_text(encoding="utf-8") == original
        gravado = json.loads(caminho.read_text(encoding="utf-8"))
        assert gravado["versao"] == rm.VERSAO == 2
        assert mundo.reservas == {"jogador:slot1:abc": "W10"}
        assert mundo.ultima_sessao == 1000.0
        for velho in antigo["ladder"]["registros"]:
            novo = mundo.ladder[velho["identidade"]]
            assert (novo.vitorias, novo.derrotas, novo.empates) == (
                velho["vitorias"],
                velho["derrotas"],
                0,
            )
            assert novo.rating.rating == pytest.approx(velho["rating"]["rating"])
            assert len(novo.historico) == len(velho["historico"])
        eu = mundo.ladder["jogador:slot1:abc"]
        assert eu.historico[0]["resultado"] == "anulada" and eu.historico[0]["motivo"] == "limite"
        assert eu.posicionado and (eu.progresso.divisao is not None or eu.progresso.elite)
        assert not mundo.ladder.problemas()
        assert mundo.leaderboard.linhas and mundo.leaderboard.ciclo is None

    def test_a_copia_da_v1_nao_e_sobrescrita(self, populacao, tmp_path):
        caminho = self._v1(tmp_path)
        (tmp_path / rm.COPIA_DA_V1).write_text("a primeira cópia", encoding="utf-8")
        rm.MundoRanqueado.carregar(populacao, str(caminho))
        assert (tmp_path / rm.COPIA_DA_V1).read_text(encoding="utf-8") == "a primeira cópia"

    def test_o_estado_inicial_publicado_tambem_passa_pela_fundacao(self, populacao, tmp_path):
        mundo = rm.MundoRanqueado.carregar(populacao, str(tmp_path / "novo.json"))
        assert not (tmp_path / rm.COPIA_DA_V1).exists()
        elite = [r for r in mundo.ladder.registros() if r.progresso.elite]
        assert 10 <= len(elite) <= 20 and not mundo.ladder.problemas()
        assert sum(1 for r in mundo.ladder.registros() if r.progresso.titulo) == 5

    def test_uma_gravacao_que_falha_nao_estraga_o_arquivo(self, populacao, tmp_path, monkeypatch):
        mundo = _mundo(populacao, tmp_path)
        mundo.salvar()
        antes = Path(mundo.caminho).read_text(encoding="utf-8")
        mundo.fila = 9

        def falha(*_, **__):
            raise OSError("disco cheio")

        monkeypatch.setattr(rm.os, "replace", falha)
        with pytest.raises(OSError):
            mundo.salvar()
        assert Path(mundo.caminho).read_text(encoding="utf-8") == antes
        assert not [p for p in tmp_path.iterdir() if p.name.startswith(".ranked-")]

    def test_estado_incompleto_e_recusado_sem_sobrescrever(self, populacao, tmp_path):
        caminho = tmp_path / "ranked.json"
        caminho.write_text(json.dumps({"versao": 2, "ladder": {}}), encoding="utf-8")
        with pytest.raises(rm.RankedInvalidaError):
            rm.MundoRanqueado.carregar(populacao, str(caminho))
        assert json.loads(caminho.read_text(encoding="utf-8")) == {"versao": 2, "ladder": {}}
