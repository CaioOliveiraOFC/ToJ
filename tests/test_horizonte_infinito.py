"""O motor continua matematicamente válido em horizontes altos.

Validade ESTRUTURAL, não balanceamento. Um monstro do andar 5000 causar dano
absurdo é esperado; `dano = NaN`, chance de acerto de 340% ou HP máximo negativo
não são. A pergunta aqui é só a segunda.

O instrumento vive em `_sonda_infinita.py`, e ele próprio é testado: há um
plantio deliberado de defeito para provar que a sonda enxerga.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tests._sonda_infinita import Falhas, checkpoint  # noqa: E402

# O sweep completo leva ~1,7s, então roda na suíte padrão. Se um dia pesar,
# ganha marcador próprio — nunca o de `balance`, que é outra pergunta.
ANDARES_DO_SWEEP = 1000

# Checkpoints extremos que o motor sustenta hoje. `5000` é o teto testado;
# acima dele ver `TestLimiteEstrutural`.
CHECKPOINTS = [1, 10, 20, 50, 100, 500, 1000, 5000]

# Onde a curva de atributo estoura o ponto flutuante. `geometric` calcula
# `base * 1.12**(nível-1)`, e o expoente sai do alcance do `double` por volta
# daqui. É limite conhecido, não regressão — e o teste o fixa para que ele não
# caia sem ninguém ver.
PRIMEIRO_ANDAR_INVALIDO = 6159


def _falhas_em(ponto: int, completo: bool = True) -> Falhas:
    f = Falhas()
    checkpoint(f, ponto, completo=completo)
    return f


class TestCheckpoints:
    @pytest.mark.parametrize("ponto", CHECKPOINTS)
    def test_todos_os_invariantes_valem(self, ponto):
        falhas = _falhas_em(ponto)
        assert not falhas, "\n".join(
            f"[{x['sistema']}] andar {x['ponto']} {x['quem']}: "
            f"esperado {x['esperado']}, obtido {x['obtido']}"
            for x in falhas[:10]
        )


class TestSweep:
    def test_mil_andares_seguidos(self):
        """Um por andar, do 1 ao 1000, sem buraco."""
        falhas = Falhas()
        primeira = None
        for andar in range(1, ANDARES_DO_SWEEP + 1):
            antes = len(falhas)
            checkpoint(falhas, andar, completo=(andar % 100 == 0 or andar <= 3))
            if len(falhas) > antes and primeira is None:
                primeira = (andar, falhas[antes])
        assert not falhas, f"primeira quebra no andar {primeira[0]}: {primeira[1]}"


class TestLimiteEstrutural:
    """O teto conhecido da curva de atributo, fixado para não escorregar.

    `geometric` usa exponenciação em ponto flutuante. Não é bug de lógica: é o
    alcance do `double`. Corrigir exigiria trocar a aritmética da fórmula, e
    isso é decisão de design — o teste registra o limite, não o esconde.
    """

    def test_o_ultimo_andar_valido_continua_valido(self):
        assert not _falhas_em(PRIMEIRO_ANDAR_INVALIDO - 1)

    def test_o_limite_nao_desceu(self):
        """Se algo fizer a curva estourar mais cedo, isto acusa."""
        with pytest.raises(OverflowError):
            checkpoint(Falhas(), PRIMEIRO_ANDAR_INVALIDO)


class TestASondaEnxerga:
    """Prova de carga do instrumento. Sonda que não acusa nada é sonda cega."""

    def test_piso_de_atributo_removido_e_detectado(self, monkeypatch):
        from src.shared import effect_core as core

        monkeypatch.setattr(core, "MIN_ATTRIBUTE_RATIO", 0.0)
        assert any(x["sistema"] == "effects/piso" for x in _falhas_em(50, completo=False))

    def test_cap_de_critico_furado_e_detectado(self, monkeypatch):
        from src.mechanics import combat as cmb

        monkeypatch.setattr(cmb, "CRIT_CHANCE_CAP", 500)
        assert any(x["sistema"] == "crit" for x in _falhas_em(50, completo=False))

    def test_chance_de_acerto_invalida_e_detectada(self, monkeypatch):
        from src.mechanics import combat as cmb

        monkeypatch.setattr(cmb, "BASE_HIT_CHANCE", 400)
        monkeypatch.setattr(cmb, "HIT_CHANCE_CEIL", 340)
        assert any(x["sistema"] == "hit_chance" for x in _falhas_em(50, completo=False))

    def test_teto_de_stacks_furado_e_detectado(self, monkeypatch):
        from src.shared import effect_core as core

        original = core.CATALOG["bleed"]
        monkeypatch.setitem(
            core.CATALOG, "bleed", original.__class__(**{**original.__dict__, "max_stacks": 99})
        )
        assert any(x["sistema"] == "effects/bleed" for x in _falhas_em(50, completo=False))
