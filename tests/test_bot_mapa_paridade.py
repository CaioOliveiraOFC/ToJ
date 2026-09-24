"""Paridade do MAPA: o que o adaptador DECLARA × o que o driver EXECUTA.

Mesmo par de perguntas da FASE A, um andar acima:

    (B) o adapter representa certo o andar  — AQUI
    (C) o evaluator valoriza certo          — `test_bot_decisao_mapa.py`

A auditoria mediu, em 366 alvos alcançáveis de 6 seeds × 3 classes × 6 andares,
12 divergências entre a rota DECLARADA e a rota ANDADA — e em todas elas o
executado lutava MAIS que o declarado. O `-extras` que a policy descontava era
ficção nesses casos. Estes testes são o contrato que impede a volta.
"""

from __future__ import annotations

import random

from src.content.factories.dungeons import RANDOM_EVENT_TYPES
from src.engine.loop import _setup_dungeon_map
from src.sim.bot.observation import EventoView, MapState
from tools import bot_adapter as ad
from tools.bot_padrao import BotPadrao, _pos

SEEDS = (20260918, 20260916, 20260901, 20261001)


def _andar(seed: int, andar: int, classe: str = "warrior") -> BotPadrao:
    """Um andar real, montado pelo mesmo `_setup_dungeon_map` do jogo."""
    random.seed(seed)
    bot = BotPadrao(classe=classe, seed=seed)
    random.seed(seed * 31 + andar)
    bot.andar = andar
    bot.mapa = _setup_dungeon_map(andar, None, andar, bot.hero)
    bot.posicao = _pos(bot.mapa.player_pos)
    bot.saida = _pos(bot.mapa.exit_pos)
    return bot


class TestRotaDeclaradaEARotaAndada:
    def test_os_extras_declarados_sao_os_encontros_do_caminho_real(self):
        """Para todo alvo de todo andar: o declarado é o que o caminho tem."""
        vistos = 0
        for seed in SEEDS:
            for andar in range(1, 7):
                bot = _andar(seed, andar)
                mapa, _prog = ad.estado_do_mapa(bot)
                for alvo in mapa.alvos:
                    rota, caminho = ad.rota_para(bot, alvo.casa, lutar=True)
                    encontros = ad.encontros_do_caminho(bot.mapa, caminho) - {alvo.casa}
                    assert alvo.extras == len(encontros), (seed, andar, alvo.casa)
                    assert alvo.passos == rota.passos
                    vistos += 1
        assert vistos >= 90, "a varredura não alcançou alvos suficientes"

    def test_o_driver_e_o_adaptador_pedem_a_mesma_rota(self):
        """Uma função só resolve a rota dos dois lados — não há segunda cópia."""
        fonte = open("tools/bot_padrao.py", encoding="utf-8").read()
        assert "adapter.rota_para(self, destino" in fonte
        assert "rota_do_campo(self._campo(evitando)" not in fonte

    def test_observar_o_mapa_nao_muda_nada(self):
        """Inércia: ler o andar não toca HP, MP, mapa nem o estado do RNG."""
        bot = _andar(20260918, 3)
        antes = (
            bot.hero.get_hp(),
            bot.hero.get_mp(),
            bot.hero.coins,
            dict(bot.mapa.enemies_pos),
            dict(bot.mapa.features),
            bot.mapa.event_pos,
            random.getstate(),
        )
        for _ in range(5):
            mapa, prog = ad.estado_do_mapa(bot)
            ad.acoes_do_mapa(bot, mapa, prog)
        depois = (
            bot.hero.get_hp(),
            bot.hero.get_mp(),
            bot.hero.coins,
            dict(bot.mapa.enemies_pos),
            dict(bot.mapa.features),
            bot.mapa.event_pos,
            random.getstate(),
        )
        assert antes == depois

    def test_observar_o_mapa_e_deterministico(self):
        bot = _andar(20260916, 4)
        primeiro = ad.estado_do_mapa(bot)[0]
        segundo = ad.estado_do_mapa(bot)[0]
        assert primeiro == segundo


class TestDesvioContaEncontroUmaVez:
    """Um monstro que caia na ida E na volta é UM combate, não dois."""

    def _bot_com_desvio(self):
        bot = _andar(20260918, 3)
        return bot

    def test_o_desvio_nunca_conta_mais_encontros_do_que_o_andar_tem(self):
        for seed in SEEDS:
            for andar in range(1, 7):
                bot = _andar(seed, andar)
                total = len(bot.mapa.enemies_pos)
                for casa in list(bot.mapa.features) + (
                    [bot.mapa.event_pos] if bot.mapa.event_pos else []
                ):
                    desvio = bot._desvio(casa)
                    if desvio is None:
                        continue
                    assert 0 <= desvio[1] <= total, (seed, andar, casa)

    def test_o_custo_do_desvio_e_o_conjunto_ida_uniao_volta_menos_direto(self):
        """A conta inteira, refeita aqui do zero e comparada com a do driver."""
        from src.engine.map_analysis import campo_de_custo, rota_do_campo

        conferidos = 0
        for seed in SEEDS:
            for andar in range(1, 7):
                bot = _andar(seed, andar)
                _r, direto = ad.rota_para(bot, bot.saida, lutar=False)
                for casa in bot.mapa.features:
                    desvio = bot._desvio(casa)
                    if desvio is None:
                        continue
                    _r, ida = ad.rota_para(bot, casa, lutar=False)
                    volta_rota, volta = rota_do_campo(
                        campo_de_custo(bot.mapa, casa, por_combate=True), bot.saida, True
                    )
                    if not volta_rota.alcancavel:
                        continue
                    esperado = (
                        ad.encontros_do_caminho(bot.mapa, ida)
                        | ad.encontros_do_caminho(bot.mapa, volta)
                    ) - ad.encontros_do_caminho(bot.mapa, direto)
                    assert desvio[1] == len(esperado), (seed, andar, casa)
                    conferidos += 1
        assert conferidos >= 10, "a varredura não alcançou serviços suficientes"

    def test_monstro_nas_duas_pernas_conta_uma_vez(self):
        """Andar montado à mão: o MESMO monstro na ida e na volta é um combate.

        Somar `ida.combates + volta.combates` devolveria 2 — e depois do primeiro
        combate aquele monstro não existe mais.
        """
        bot = _andar(20260918, 2)
        mapa = bot.mapa
        # Corredor limpo: só o monstro do gargalo fica no andar.
        mapa.enemies_pos.clear()
        mapa.features.clear()
        mapa.event_pos, mapa.event_type = None, None
        _r, ida = ad.rota_para(bot, bot.saida, lutar=False)
        assert len(ida) >= 4, "o andar precisa de um caminho com casas intermediárias"
        gargalo = ida[len(ida) // 2]
        servico = ida[max(1, len(ida) // 2 - 1)]
        mapa.enemies_pos[gargalo] = object()
        mapa.features[servico] = "forge"
        desvio = bot._desvio(servico)
        assert desvio is not None
        # O gargalo pode estar na ida, na volta ou nas duas; nunca conta 2.
        assert desvio[1] <= 1

    def test_a_conta_e_de_conjunto_e_nao_de_soma(self):
        """O código não pode voltar a somar contadores de rota."""
        fonte = open("tools/bot_padrao.py", encoding="utf-8").read()
        assert "encontros(self.mapa, caminho_ida) | encontros(self.mapa, caminho_volta)" in fonte
        assert "ida.combates + volta.combates" not in fonte


class TestFronteiraDeInformacaoDoAndar:
    """O mapa desenha `?`. O tipo só existe depois de pisar."""

    def test_o_estado_do_mapa_nao_carrega_o_tipo_do_evento(self):
        campos = MapState.__dataclass_fields__
        assert "tem_evento" in campos
        assert campos["tem_evento"].type in ("bool", bool)
        assert campos["evento"].type in ("EventoView | None",)

    def test_a_view_do_evento_so_carrega_regra_publica(self):
        campos = set(EventoView.__dataclass_fields__)
        assert campos == {
            "desvio",
            "lutas_no_desvio",
            "cura_da_fonte",
            "custo_do_altar",
            "altar_mataria",
            "desfechos",
        }

    def test_dois_andares_iguais_com_eventos_diferentes_produzem_o_mesmo_estado(self):
        """A propriedade central: o sorteio escondido não muda o que o bot vê."""
        estados = []
        for tipo in RANDOM_EVENT_TYPES:
            bot = _andar(20260918, 3)
            if bot.mapa.event_pos is None:
                bot.mapa.place_event(tipo)
            else:
                bot.mapa.event_type = tipo
            estados.append(ad.estado_do_mapa(bot)[0])
        assert len({repr(e) for e in estados}) == 1, "o tipo do evento vazou para o MapState"

    def test_a_opcao_do_evento_tem_uma_familia_so(self):
        """`family=mapa.evento` fazia o tipo virar a família, e o evaluator
        entrava direto no ramo da Fonte ou do Altar."""
        for tipo in RANDOM_EVENT_TYPES:
            bot = _andar(20260918, 3)
            if bot.mapa.event_pos is None:
                bot.mapa.place_event(tipo)
            else:
                bot.mapa.event_type = tipo
            mapa, prog = ad.estado_do_mapa(bot)
            if not mapa.tem_evento:
                continue
            familias = {o.family for o in ad.acoes_do_mapa(bot, mapa, prog)[0]}
            assert "evento" in familias
            assert not familias & set(RANDOM_EVENT_TYPES)

    def test_nenhuma_opcao_alcancavel_e_escondida_por_limiar_de_desvio(self):
        """`DESVIO_ACEITAVEL` apagava 7 de 45 serviços medidos da mesa."""
        for seed in SEEDS:
            for andar in range(1, 7):
                bot = _andar(seed, andar)
                mapa, prog = ad.estado_do_mapa(bot)
                ids = {o.action_id for o in ad.acoes_do_mapa(bot, mapa, prog)[0]}
                for servico in mapa.servicos:
                    if servico.tipo == "extraction":
                        continue
                    assert servico.tipo in ids, (seed, andar, servico)
                if mapa.tem_evento:
                    assert "evento" in ids
