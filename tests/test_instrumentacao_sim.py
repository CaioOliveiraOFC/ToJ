"""O instrumento tem de medir o que diz medir.

Estes testes não olham para o jogo: olham para o simulador. Um bot que escolhe
carta por acidente e uma ablação que não desliga o sistema que nomeia produzem
números com aparência de medição, e foi assim que o balanceamento anterior foi
calibrado contra um andar que o jogo não gerava.
"""

from __future__ import annotations

import dataclasses
import random
from types import SimpleNamespace

from src.content.passives import PassiveCard, load_passives
from src.sim.harness import simulate_run
from src.sim.pick_policies import (
    DESCONHECIDA,
    FORA_DA_INTENCAO,
    NEUTRA,
    PASSIVE_PRIORITIES,
    PASSIVE_SEM_PREFERENCIA,
    POLICIES,
    PREFERIDA,
    intent_fit,
)
from src.sim.toggles import Toggles


def _familias_do_catalogo() -> set[str]:
    return {p.effect_type for p in load_passives()}


class TestPoliticaCobreOCatalogo:
    """B1 — nenhuma família de passiva chega ao bot sem tratamento declarado."""

    def test_toda_familia_e_preferida_ou_declarada_indiferente(self):
        # Este é o teste que falha quando alguém acrescenta um `effect_type` novo
        # ao catálogo. A carta nova não pode simplesmente não existir para as
        # políticas: ou entra numa ordem de preferência, ou entra no tier
        # indiferente — e as duas coisas são decisão de alguém, não omissão.
        catalogo = _familias_do_catalogo()
        for nome, ordem in PASSIVE_PRIORITIES.items():
            sem_tratamento = catalogo - set(ordem) - PASSIVE_SEM_PREFERENCIA
            assert not sem_tratamento, (
                f"a política {nome} não sabe o que fazer com {sorted(sem_tratamento)}: "
                "declare a preferência ou acrescente a família a PASSIVE_SEM_PREFERENCIA."
            )

    def test_preferida_e_indiferente_sao_exclusivas_e_existem(self):
        catalogo = _familias_do_catalogo()
        orfas = PASSIVE_SEM_PREFERENCIA - catalogo
        assert not orfas, f"PASSIVE_SEM_PREFERENCIA cita famílias que não existem: {sorted(orfas)}"
        for nome, ordem in PASSIVE_PRIORITIES.items():
            conflito = set(ordem) & PASSIVE_SEM_PREFERENCIA
            assert not conflito, (
                f"{nome} declara preferência por {sorted(conflito)} e ao mesmo tempo "
                "as trata como indiferentes."
            )
            mortas = set(ordem) - catalogo
            assert not mortas, f"{nome} ordena famílias que saíram do catálogo: {sorted(mortas)}"

    def test_no_tier_indiferente_o_desempate_e_raridade_e_nao_valor(self):
        # O defeito original: sem preferência declarada, a escolha caía num
        # `max(effect_value)` que compara grandezas diferentes. +200 de HP e +5%
        # de dano crítico não são o mesmo eixo, e o bot levava o número maior.
        indiferente = sorted(PASSIVE_SEM_PREFERENCIA)[0]
        comum_gorda = PassiveCard(
            id="teste_comum",
            name="Comum de número grande",
            category="Combate",
            rarity="Common",
            description="",
            effect_type=indiferente,
            effect_value=999,
        )
        lendaria_magra = PassiveCard(
            id="teste_lendaria",
            name="Lendária de número pequeno",
            category="Combate",
            rarity="Legendary",
            description="",
            effect_type=indiferente,
            effect_value=1,
        )
        for nome, politica in POLICIES.items():
            if not politica.deliberate:
                continue
            escolha = politica.pick_passive(
                SimpleNamespace(passives=[]),
                [comum_gorda, lendaria_magra],
                random.Random(0),
            )
            assert escolha is lendaria_magra, (
                f"{nome} escolheu pelo effect_value bruto entre famílias sem preferência."
            )


class TestAblacaoIsolaOSistema:
    """B2 — desligar um sistema desliga aquele sistema, e só aquele."""

    def test_sem_essencia_o_xp_nao_e_multiplicado_por_nada(self):
        # Inclui as passivas de `essence_bonus`, que continuavam multiplicando o
        # XP com a Essência desligada: a run "sem essência" rendia mais que a
        # base, e a ablação media o sorteio do andar achando que media o sistema.
        resultado = simulate_run(
            "Warrior", 10, 5, "smart", 1337, "expected", toggles=Toggles().without(essence=False)
        )
        essencia = resultado["telemetry"]["essence"]
        assert essencia["xp_after"] == essencia["xp_base"]

    def test_cada_toggle_de_servico_desliga_somente_o_proprio(self):
        servicos = {"shop", "forge", "extraction"}
        for alvo in servicos:
            resultado = simulate_run(
                "Warrior",
                10,
                8,
                "smart",
                99,
                "expected",
                toggles=Toggles().without(**{alvo: False}),
            )
            surgidos = set(resultado["telemetry"]["features"]["spawned"])
            assert alvo not in surgidos, f"{alvo} desligado e mesmo assim apareceu no andar."

    def test_desligar_um_servico_nao_mexe_no_pity_dos_outros(self):
        # `roll_features` avança os três contadores de seca numa chamada só. Se a
        # ablação pulasse o sorteio em vez de filtrar o resultado, uma run sem
        # loja veria Ferreiro e Extração com outra distribuição — e o número
        # atribuído à loja carregaria junto uma mudança de frequência que
        # ninguém pediu.
        from src.content.factories.features import roll_features

        def andares_com_ferreiro(descartar: str | None) -> list[int]:
            jogador = SimpleNamespace(
                shop_miss_streak=0, forge_miss_streak=0, extraction_miss_streak=0
            )
            rng = random.Random(4242)
            return [
                andar
                for andar in range(1, 31)
                if "forge" in [s for s in roll_features(jogador, andar, rng) if s != descartar]
            ]

        assert andares_com_ferreiro(None) == andares_com_ferreiro("shop")

    def test_o_rotulo_da_ablacao_nomeia_todo_sistema_que_pode_ser_desligado(self):
        # Um sistema desligado e ausente do rótulo é um relatório que mente sobre
        # o próprio cenário.
        booleanos = [
            campo.name
            for campo in dataclasses.fields(Toggles)
            if campo.type is bool or campo.type == "bool"
        ]
        for nome in booleanos:
            rotulo = Toggles().without(**{nome: False}).label()
            assert nome in rotulo, f"desligar {nome} não aparece em label(): {rotulo!r}"


class TestNeutraNaoEOffIntent:
    """Sem preferência definida não é o mesmo que contra a intenção.

    Enquanto os dois estados eram um só, a ausência de classificação virava
    veredito: o bot pagava reroll para fugir de uma oferta neutra e o scout
    contava essa recusa como prova de carta fraca. A carta era fraca porque
    ninguém tinha classificado a família dela — circular.
    """

    def _carta(self, effect_type: str, rarity: str = "Common") -> PassiveCard:
        return PassiveCard(
            id=f"teste_{effect_type}",
            name=f"Carta de {effect_type}",
            category="Combate",
            rarity=rarity,
            description="",
            effect_type=effect_type,
            effect_value=10,
        )

    def test_familia_classificada_fora_da_intencao_continua_off_intent(self):
        # A regra, provada sobre uma política construída aqui. Com o catálogo de
        # hoje as três políticas ordenam o MESMO conjunto de 13 famílias, em
        # ordens diferentes, então FORA_DA_INTENCAO está vazio na prática e não
        # existe oferta real que dispare a recusa. Testar a regra com dado
        # sintético é o que mantém a garantia viva para o dia em que uma política
        # deixar de ordenar algo que outra ordena.
        ordenada_por_alguem = sorted(PASSIVE_PRIORITIES["survival"])[0]
        politica = POLICIES["survival"]

        assert intent_fit("survival", ordenada_por_alguem) == PREFERIDA

        magra = dataclasses.replace(
            politica,
            name="magra",
        )
        PASSIVE_PRIORITIES["magra"] = tuple(
            f for f in PASSIVE_PRIORITIES["survival"] if f != ordenada_por_alguem
        )
        try:
            assert intent_fit("magra", ordenada_por_alguem) == FORA_DA_INTENCAO
            oferta = [self._carta(ordenada_por_alguem)]
            assert magra.passive_off_intent(oferta) is True
        finally:
            del PASSIVE_PRIORITIES["magra"]

    def test_familia_neutra_nao_e_off_intent(self):
        neutra = sorted(PASSIVE_SEM_PREFERENCIA)[0]
        oferta = [self._carta(neutra) for _ in range(3)]
        for nome, politica in POLICIES.items():
            if not politica.deliberate:
                continue
            assert intent_fit(nome, neutra) == NEUTRA
            assert politica.passive_off_intent(oferta) is False, (
                f"{nome} tratou uma oferta sem classificação como oferta ruim: "
                "a ausência de decisão virou veredito."
            )

    def test_nenhuma_familia_do_catalogo_fica_em_estado_implicito(self):
        # DESCONHECIDA é erro de dados, não um quarto comportamento: uma família
        # entrou no catálogo sem ninguém decidir nada sobre ela.
        for familia in _familias_do_catalogo():
            for nome, politica in POLICIES.items():
                if not politica.deliberate:
                    continue
                estado = intent_fit(nome, familia)
                assert estado != DESCONHECIDA, (
                    f"{familia} não está classificada nem declarada neutra para {nome}."
                )
                assert estado in (PREFERIDA, NEUTRA, FORA_DA_INTENCAO)

    def test_o_scout_nao_chama_carta_neutra_de_fraca(self):
        # O caminho completo: taxa de escolha baixa numa família neutra não pode
        # sair do relatório com o veredito de carta morta.
        from src.content.passives import load_passives
        from src.sim.scout import _analyse_cards

        neutras = [p for p in load_passives() if p.effect_type in PASSIVE_SEM_PREFERENCIA]
        assert neutras, "o tier neutro ficou vazio; este teste perdeu o objeto"
        alvo = neutras[0]
        taxas = {nome: {alvo.id: 0.0} for nome in ("survival", "offense", "economy")}

        achados = _analyse_cards(taxas, "passivas")
        assuntos = {a.subject for a in achados}
        assert "recusadas por toda intenção" not in assuntos, (
            f"{alvo.name} tem a família sem classificação e mesmo assim foi declarada fraca."
        )
        assert "sem classificação de intenção" in assuntos
