"""Auditoria de um duelo da Arena: observa o motor sem mudar o que ele faz.

Instrumentação de DIAGNÓSTICO, para ferramentas e testes. Nada aqui é regra de
jogo, e nada aqui roda no jogo. Três peças:

- `RngGravado` é o gerador do duelo visto por dentro: um proxy que DELEGA cada
  chamada a um `random.Random` comum e anota operação, limites, valor e quem
  chamou. Não é subclasse de propósito: uma subclasse que sobrescreve `random()`
  troca o algoritmo de `randrange` do CPython (`_randbelow`), e a mesma semente
  passaria a dar outro duelo. Qualquer método que o proxy não conhece levanta
  erro — um sorteio que a auditoria não vê não pode acontecer calado.
- `interceptar(trace)` troca, durante o bloco, funções canônicas de
  `mechanics/combat.py`, `shared/effect_core.py` e `mechanics/pvp_duel.py` por
  embrulhos que chamam a ORIGINAL exatamente uma vez e anotam entradas, saída e
  o estado em volta. Os golpes que `apply_skill` resolve com `publish=None`
  passam pelos mesmos embrulhos, porque a chamada interna lê o nome no módulo.
- `Trace` guarda os registros, em ordem, como dicionários prontos para JSON.

As parcelas intermediárias (a conta de acerto, o funil de dano, a Égide, a
iniciativa) são recalculadas com as MESMAS funções e constantes do motor, sem
consumir sorteio, e cada recálculo é conferido contra o valor que o motor de
fato devolveu: se divergirem, a auditoria falha em vez de publicar uma conta
que o jogo não fez.
"""

from __future__ import annotations

import contextlib
import dataclasses
import math
import random
import sys
from collections.abc import Callable

from src.mechanics import combat, pvp_duel
from src.mechanics import pvp_initiative as ini
from src.mechanics.pvp_duel import SIDES, Duel, run_round
from src.shared import effect_core as core
from src.shared import effects as fx
from src.shared import interactions as ix
from src.shared.constants import (
    BASE_HIT_CHANCE,
    BASIC_ATTACK_POWER_MULT,
    CLASS_WEIGHTS,
    CRIT_CHANCE_CAP,
    CRIT_CHANCE_DEFAULT,
    CRIT_DAMAGE_BASE,
    DEFENSE_K,
    HIT_AGILITY_SWING,
    HIT_CHANCE_CEIL,
    HIT_CHANCE_FLOOR,
    MAGIC_SHIELD_DAMAGE_PER_MP,
    MP_REGEN_PERCENT_PER_TURN,
    XMULT_CAP,
)


class AuditoriaDivergenteError(AssertionError):
    """O recálculo da auditoria não bateu com o que o motor fez."""


def _confere(condicao: bool, mensagem: str) -> None:
    if not condicao:
        raise AuditoriaDivergenteError(mensagem)


def plano(valor):
    """Converte o que o motor devolve em dado de JSON."""
    if dataclasses.is_dataclass(valor) and not isinstance(valor, type):
        return {k: plano(v) for k, v in dataclasses.asdict(valor).items()}
    if isinstance(valor, dict):
        return {str(k): plano(v) for k, v in valor.items()}
    if isinstance(valor, (list, tuple, set)):
        return [plano(v) for v in valor]
    if isinstance(valor, float):
        return valor if math.isfinite(valor) else str(valor)
    if isinstance(valor, (int, str, bool)) or valor is None:
        return valor
    return str(valor)


def foto(heroi) -> dict:
    """O estado do gladiador neste instante. Só leitura."""
    return {
        "hp": int(heroi.get_hp()),
        "hp_max": int(heroi.base_hp),
        "mp": int(heroi.get_mp()),
        "mp_max": int(heroi.base_mp),
        "st": int(heroi.get_st()),
        "mg": int(heroi.get_mg()),
        "ag": int(heroi.get_ag()),
        "df": int(heroi.get_df()),
        "recargas": {str(k): int(v) for k, v in heroi.skill_cooldowns.items()},
        "buffs": {
            str(nome): {
                "stat": str(dados.get("stat", "")),
                "valor": dados.get("value"),
                "duracao": int(dados.get("duration", 0)),
            }
            for nome, dados in heroi.active_buffs.items()
        },
        "efeitos": [
            {
                "efeito": i.effect,
                "fonte": i.source_id,
                "intensidade": i.intensity,
                "duracao": i.duration,
                "stacks": i.stacks,
            }
            for i in core.instances(heroi)
        ],
        "death_ignore_usado": bool(getattr(heroi, "_death_ignore_used", False)),
        "vivo": bool(heroi.get_isalive()),
    }


MODIFICADORES_DA_FICHA = (
    "crit_chance",
    "crit_damage",
    "damage_percent",
    "damage_reduction",
    "evasion",
    "precision",
    "life_steal",
    "mana_regen",
    "status_resistance",
    "stun_chance",
    "bleed_chance",
    "poison_chance",
    "fear_chance",
    "death_ignore",
    "potion_heal_bonus",
)


def ficha(heroi) -> dict:
    """A build: o que não muda durante o duelo, mais o estado inicial."""
    return {
        "nome": heroi.get_nick_name(),
        "classe": heroi.get_classname(),
        "nivel": int(heroi.get_level()),
        "equipamento": {
            pos: (peca.display_name if peca is not None else None)
            for pos, peca in heroi.equipment.items()
        },
        "arma_percent": heroi.weapon_percent(),
        "skills": [
            {
                "id": s.id,
                "nome": s.name,
                "tipo": s.effect_type,
                "valor": plano(s.effect_value),
                "stat": getattr(s, "effect_stat", ""),
                "custo_mp": int(heroi.skill_mana_cost(s)),
                "recarga": int(getattr(s, "cooldown", 0) or 0),
                "alvo": getattr(s, "target", ""),
                "chance": int(getattr(s, "chance", 0) or 0),
                "duracao": int(getattr(s, "duration", 0) or 0),
                "power": float(getattr(s, "power", 0) or 0),
                "escala": [(t.stat, float(t.weight)) for t in (getattr(s, "scaling", ()) or ())],
                "modificador_de_acerto": int(getattr(s, "accuracy_modifier", 0) or 0),
                "critico_da_carta": int(getattr(s, "crit_chance", 0) or 0),
                "secundario": plano(getattr(s, "secondary", None)),
                "requisito": (s.requires.describe() if getattr(s, "requires", None) else None),
                "usavel": bool(heroi.can_use_skill(s)),
            }
            for s in heroi.skills.values()
        ],
        "passivas": [
            {"id": p.id, "nome": p.name, "efeito": p.effect_type, "valor": p.effect_value}
            for p in heroi.passives
        ],
        "modificadores": {c: float(fx.combat_modifier(heroi, c)) for c in MODIFICADORES_DA_FICHA},
        "egide_percent": int(getattr(heroi, "magic_shield_percent", 0) or 0),
        "estado": foto(heroi),
    }


# --- o registro --------------------------------------------------------------


class Trace:
    """Os registros de um duelo, na ordem em que aconteceram."""

    def __init__(self) -> None:
        self.records: list[dict] = []
        self.round = 0
        self.ator: str | None = None
        self._lados: dict[int, str] = {}
        self._golpes: list[int] = []
        self._acerto_pendente: dict | None = None
        self.contador_golpes = 0
        # As trocas de `interceptar` enquanto ele está ativo (ver `fora_do_duelo`).
        self.trocas: list = []

    def registrar_lados(self, duelo: Duel) -> None:
        for lado in SIDES:
            self._lados[id(duelo.hero(lado))] = lado

    def lado(self, entidade) -> str:
        return self._lados.get(id(entidade), "?")

    def add(self, kind: str, **dados) -> dict:
        registro = {
            "seq": len(self.records) + 1,
            "rodada": self.round,
            "ator": self.ator,
            "golpe": self._golpes[-1] if self._golpes else None,
            "kind": kind,
            **{k: plano(v) for k, v in dados.items()},
        }
        self.records.append(registro)
        return registro

    def de(self, kind: str) -> list[dict]:
        return [r for r in self.records if r["kind"] == kind]

    # --- o RNG ---

    def rng(self, operacao: str, argumentos: list, valor, quadro, chamada: int) -> dict:
        funcao = quadro.f_code.co_name
        local = quadro.f_locals
        arquivo = quadro.f_code.co_filename.rsplit("/src/", 1)[-1]
        base = {
            "operacao": operacao,
            "argumentos": list(argumentos),
            "valor": valor,
            "chamada": chamada,
            "chamador": f"{arquivo}:{quadro.f_lineno} {funcao}",
        }
        if operacao == "randrange":
            inicio, fim = argumentos[0], argumentos[1]
            base["limites"] = (
                f"inteiro uniforme em [{inicio}, {fim - 1}] (randrange({inicio}, {fim}))"
            )
        if funcao == "resolve_physical_attack" and "chance_critica" in local:
            chance = int(local["chance_critica"])
            return self.add(
                "rolagem",
                mecanica="crítico",
                chance=chance,
                teste=f"{valor} <= {chance}",
                teste_verdadeiro=valor <= chance,
                operador="<=",
                aprovado=valor <= chance,
                resultado="CRÍTICO" if valor <= chance else "sem crítico",
                **base,
            )
        if funcao == "resolve_physical_attack":
            # A chance de acerto é calculada DEPOIS do sorteio, no mesmo `if`
            # (`randrange(...) > hit_chance(...)`): quem completa este registro
            # é o embrulho de `hit_chance`, chamado logo em seguida.
            registro = self.add("rolagem", mecanica="acerto", operador=">", **base)
            self._acerto_pendente = registro
            return registro
        if funcao == "try_apply_status":
            chance = float(local["chance"])
            return self.add(
                "rolagem",
                mecanica=f"aplicação de status ({local['status']})",
                status=local["status"],
                alvo=self.lado(local["target"]),
                chance_base=float(local["base_chance"]),
                chance=chance,
                teste=f"{valor} > {chance!r}",
                teste_verdadeiro=valor > chance,
                operador=">",
                aprovado=not (valor > chance),
                resultado="passou na rolagem" if not (valor > chance) else "falhou na rolagem",
                **base,
            )
        if funcao == "first" and isinstance(local.get("self"), ini.SeededCoinTieBreak):
            a, b = local["a"], local["b"]
            return self.add(
                "rolagem",
                mecanica="desempate absoluto de iniciativa (SeededCoinTieBreak)",
                teste=f"{valor!r} < 0.5",
                teste_verdadeiro=valor < 0.5,
                operador="<",
                aprovado=valor < 0.5,
                resultado=f"{a.side if valor < 0.5 else b.side} primeiro",
                **base,
            )
        return self.add("rolagem", mecanica=f"DESCONHECIDA ({funcao})", **base)

    def completar_acerto(self, chance: int, detalhe: dict) -> None:
        pendente = self._acerto_pendente
        if pendente is None:
            self.add("acerto_sem_rolagem", chance=chance, detalhe=detalhe)
            return
        valor = pendente["valor"]
        pendente.update(
            chance=chance,
            teste=f"{valor} > {chance}",
            teste_verdadeiro=valor > chance,
            aprovado=not (valor > chance),
            resultado="ACERTOU" if not (valor > chance) else "ERROU",
            detalhe_chance=plano(detalhe),
        )
        self._acerto_pendente = None

    # --- eventos do motor e do EventBus ---

    def publish(self, topico: str, evento) -> None:
        payload = {}
        for chave, valor in evento.payload.items():
            if hasattr(valor, "get_nick_name"):
                payload[chave] = self.lado(valor)
            elif hasattr(valor, "id") and hasattr(valor, "effect_type"):
                payload[chave] = valor.id
            else:
                payload[chave] = plano(valor)
        self.add("evento_publicado", topico=topico, tipo=evento.type, payload=payload)

    def embrulhar_evento(self, original: Callable) -> Callable:
        def _event(numero, name, side=None, detail=()):
            original(numero, name, side, detail)
            self.add("evento_do_motor", nome=name, lado=side, detalhe=dict(detail))

        return _event


class RngGravado:
    """O gerador do duelo, observado. Delega tudo a um `random.Random(seed)`."""

    def __init__(self, seed: int, trace: Trace) -> None:
        self._gerador = random.Random(seed)
        self._trace = trace
        self.chamadas = 0

    def randrange(self, *argumentos):
        valor = self._gerador.randrange(*argumentos)
        self.chamadas += 1
        self._trace.rng("randrange", list(argumentos), valor, sys._getframe(1), self.chamadas)
        return valor

    def random(self):
        valor = self._gerador.random()
        self.chamadas += 1
        self._trace.rng("random", [], valor, sys._getframe(1), self.chamadas)
        return valor

    def getstate(self):
        return self._gerador.getstate()

    def __getattr__(self, nome):
        raise AttributeError(
            f"RngGravado não conhece {nome!r}: o motor chamou o gerador por um caminho "
            "que a auditoria não observa."
        )


# --- os embrulhos --------------------------------------------------------------


def _detalhe_iniciativa(side, heroi, oponente, referencias, leitura) -> dict:
    nivel, nivel_op = int(heroi.get_level()), int(oponente.get_level())
    vetor = ini.build_vector(heroi)
    ref = referencias.at_level(nivel)
    parcelas = []
    for s in ini.INITIATIVE_STATS:
        razao = max(0.0, vetor[s]) / getattr(ref, s)
        parcelas.append(
            {
                "stat": s,
                "valor": vetor[s],
                "ref": getattr(ref, s),
                "razao": razao,
                "raiz": math.sqrt(razao),
            }
        )
    soma = math.fsum(p["raiz"] for p in parcelas)
    build = soma / len(parcelas)
    delta = nivel - nivel_op
    modificador = ini.level_modifier(nivel, nivel_op)
    score = build * modificador
    _confere(build == leitura.build, f"build de iniciativa {build!r} != {leitura.build!r}")
    _confere(score == leitura.score, f"score {score!r} != {leitura.score!r}")
    return {
        "lado": side,
        "nivel": nivel,
        "nivel_oponente": nivel_op,
        "parcelas": parcelas,
        "soma_raizes": soma,
        "build": build,
        "delta_nivel": delta,
        "delta_x_step": delta * ini.PVP_INITIATIVE_LEVEL_STEP,
        "teto_do_modificador": ini.PVP_INITIATIVE_LEVEL_CAP,
        "modificador": modificador,
        "score": score,
        "ag": vetor["ag"],
        "ref_ag": ref.ag,
        "ag_relativa": leitura.relative_ag,
    }


def _detalhe_acerto(atacante, defensor, modificador_acao) -> dict:
    att_ag = max(0, atacante.get_ag())
    def_ag = max(0, defensor.get_ag())
    total = att_ag + def_ag
    swing = 0.0 if total <= 0 else HIT_AGILITY_SWING * (att_ag - def_ag) / total
    evasao = fx.combat_modifier(defensor, "evasion")
    saldo = core.accuracy_shift(atacante)
    precisao = fx.combat_modifier(atacante, "precision")
    ocultacao = core.concealment_penalty(defensor)
    bruto = BASE_HIT_CHANCE + swing - evasao + saldo + precisao + int(modificador_acao) - ocultacao
    return {
        "base": BASE_HIT_CHANCE,
        "ag_atacante": att_ag,
        "ag_defensor": def_ag,
        "swing": swing,
        "swing_formula": f"{HIT_AGILITY_SWING} × ({att_ag} − {def_ag}) / {total}",
        "evasao_defensor": evasao,
        "medo_precisao_temporarios": saldo,
        "precisao_permanente": precisao,
        "modificador_da_acao": int(modificador_acao),
        "ocultacao_defensor": ocultacao,
        "bruto": bruto,
        "piso": HIT_CHANCE_FLOOR,
        "teto": HIT_CHANCE_CEIL,
        "final": int(max(HIT_CHANCE_FLOOR, min(HIT_CHANCE_CEIL, bruto))),
    }


@contextlib.contextmanager
def interceptar(trace: Trace):
    """Troca as funções canônicas por embrulhos durante o bloco. Restaura no fim.

    As trocas ficam em `trace.trocas`, para que `ControladorAuditado` possa
    desfazê-las enquanto o controlador pensa: o que um controlador simula por
    conta própria não é o duelo, e não entra no trace.
    """
    trocadas: list[tuple[object, str, object, object]] = []
    trace.trocas = trocadas

    def troca(modulo, nome, fabrica):
        original = getattr(modulo, nome)
        embrulho = fabrica(original)
        trocadas.append((modulo, nome, original, embrulho))
        setattr(modulo, nome, embrulho)

    # Originais puras usadas nos recálculos: capturadas ANTES da troca, para
    # que um recálculo nunca passe por um embrulho e duplique um registro.
    crit_multiplier = combat.crit_multiplier
    additive_multiplier = combat.additive_multiplier
    apply_xmult_cap = combat._apply_xmult_cap
    defense_modifier = combat._defense_modifier
    bonus_condition_met = combat.bonus_condition_met
    skill_mana_cost = combat.skill_mana_cost

    def e_read_initiative(original):
        def read_initiative(side, hero, opponent, references):
            leitura = original(side, hero, opponent, references)
            detalhe = _detalhe_iniciativa(side, hero, opponent, references, leitura)
            trace.add("iniciativa", **detalhe)
            return leitura

        return read_initiative

    def e_order(original):
        def order_by_initiative(a, b, tie_break, rng):
            ordem = original(a, b, tie_break, rng)
            trace.add(
                "ordem",
                score={a.side: a.score, b.side: b.score},
                scores_iguais=a.score == b.score,
                ag_relativa={a.side: a.relative_ag, b.side: b.relative_ag},
                ag_relativa_igual=a.relative_ag == b.relative_ag,
                decidido_por=ordem.decided_by,
                primeiro=ordem.first,
                segundo=ordem.second,
            )
            return ordem

        return order_by_initiative

    def e_turn_start(original):
        def process_turn_start_effects(entity, *, rng=None, publish=None):
            trace.ator = trace.lado(entity)
            antes = foto(entity)
            mp_max = int(getattr(entity, "base_mp", entity.get_mp()))
            mod_regen = fx.combat_modifier(entity, "mana_regen")
            base_regen = max(1, mp_max * MP_REGEN_PERCENT_PER_TURN / 100)
            regen = int(mod_regen + base_regen)
            trace.add(
                "inicio_oportunidade",
                antes=antes,
                regeneracao={
                    "mp_max": mp_max,
                    "percentual": MP_REGEN_PERCENT_PER_TURN,
                    "base": base_regen,
                    "base_formula": f"max(1, {mp_max} × {MP_REGEN_PERCENT_PER_TURN} / 100)",
                    "modificador_mana_regen": mod_regen,
                    "total_int": regen,
                    "total_formula": f"int({mod_regen:g} + {base_regen!r})",
                    "teto": mp_max,
                    "mp_antes": antes["mp"],
                    "mp_depois_da_regeneracao": min(mp_max, antes["mp"] + regen),
                },
            )
            perdeu = original(entity, rng=rng, publish=publish)
            trace.add("fim_inicio_oportunidade", perde_a_oportunidade=perdeu, depois=foto(entity))
            return perdeu

        return process_turn_start_effects

    def e_tick(original):
        def tick_effects(entity, *, drain_scale=None):
            relatorio = original(entity, drain_scale=drain_scale)
            trace.add("tick_de_efeitos", relatorio=relatorio)
            return relatorio

        return tick_effects

    def e_apply_skill(original):
        def apply_skill(caster, target, skill, *, rng=None, publish=None):
            receptor = caster if getattr(skill, "target", "self") == "self" else target
            antes = {"caster": foto(caster), "alvo": foto(target)}
            info = {
                "skill": skill.id,
                "nome": skill.name,
                "tipo": skill.effect_type,
                "valor": skill.effect_value,
                "stat": getattr(skill, "effect_stat", ""),
                "alvo_declarado": getattr(skill, "target", ""),
                "receptor": trace.lado(receptor),
                "custo_mp": skill_mana_cost(caster, skill),
                "recarga_declarada": int(getattr(skill, "cooldown", 0) or 0),
                "recarga_antes": caster.skill_cooldowns.get(skill.id, 0),
                "requisito": (
                    skill.requires.describe() if getattr(skill, "requires", None) else None
                ),
                "requisito_atendido": bool(caster.can_use_skill(skill)),
                "mp_disponivel": caster.get_mp(),
                "chance_declarada": int(getattr(skill, "chance", 0) or 0),
                "duracao_declarada": int(getattr(skill, "duration", 0) or 0),
            }
            if skill.effect_type == "heal":
                max_hp = int(getattr(caster, "base_hp", caster.get_hp()))
                cura = max(1, int(max_hp * int(skill.effect_value) / 100))
                bonus = fx.combat_modifier(caster, "potion_heal_bonus")
                info["cura_calculo"] = {
                    "hp_max": max_hp,
                    "percentual": int(skill.effect_value),
                    "base": cura,
                    "base_formula": f"max(1, int({max_hp} × {int(skill.effect_value)} / 100))",
                    "potion_heal_bonus": bonus,
                    "total": cura + int(cura * bonus / 100),
                }
            if skill.effect_type == "buff":
                stat = str(getattr(skill, "effect_stat", "") or "")
                info["buff_calculo"] = {
                    "stat": stat,
                    "declarado": int(skill.effect_value),
                    "valor": fx.buff_value(receptor, stat, int(skill.effect_value)),
                    "regra": (
                        f"percentual de base_{stat}: max(1, int(base × "
                        f"{int(skill.effect_value)}/100))"
                        if stat in fx.ATTRIBUTE_STATS
                        else "valor literal (modificador já percentual)"
                    ),
                }
            trace.add("skill_inicio", **info, antes=antes)
            resultado = original(caster, target, skill, rng=rng, publish=publish)
            depois = {"caster": foto(caster), "alvo": foto(target)}
            trace.add(
                "skill_fim",
                skill=skill.id,
                resultado=resultado,
                mp_debitado=antes["caster"]["mp"] - depois["caster"]["mp"],
                recarga_depois=caster.skill_cooldowns.get(skill.id, 0),
                buff_gravado=receptor.active_buffs.get(str(skill.name)),
                depois=depois,
            )
            return resultado

        return apply_skill

    def e_resolve(original):
        def resolve_physical_attack(
            attacker,
            defender,
            base_damage,
            *,
            rng=None,
            publish=None,
            accuracy_modifier=0,
            skill=None,
        ):
            trace.contador_golpes += 1
            trace._golpes.append(trace.contador_golpes)
            try:
                antes = {"atacante": foto(attacker), "defensor": foto(defender)}
                trace.add(
                    "golpe_inicio",
                    atacante=trace.lado(attacker),
                    defensor=trace.lado(defender),
                    base=base_damage,
                    skill=getattr(skill, "id", None),
                    modificador_da_acao=accuracy_modifier,
                    publish_ligado=publish is not None,
                    antes=antes,
                )
                resultado = original(
                    attacker,
                    defender,
                    base_damage,
                    rng=rng,
                    publish=publish,
                    accuracy_modifier=accuracy_modifier,
                    skill=skill,
                )
                depois = {"atacante": foto(attacker), "defensor": foto(defender)}
                roubo = fx.combat_modifier(attacker, "life_steal")
                cura_roubo = None
                if not resultado.was_evaded and roubo > 0:
                    cura_roubo = {
                        "percentual": roubo,
                        "formula": f"max(1, int({resultado.damage} × {roubo:g} / 100))",
                        "calculada": max(1, int(resultado.damage * roubo / 100)),
                        "aplicada": depois["atacante"]["hp"] - antes["atacante"]["hp"],
                    }
                trace.add(
                    "golpe_fim",
                    atacante=trace.lado(attacker),
                    defensor=trace.lado(defender),
                    resultado=resultado,
                    hp_defensor=(antes["defensor"]["hp"], depois["defensor"]["hp"]),
                    hp_aplicado=antes["defensor"]["hp"] - depois["defensor"]["hp"],
                    mp_defensor=(antes["defensor"]["mp"], depois["defensor"]["mp"]),
                    roubo_de_vida=cura_roubo,
                    death_ignore_disparou=(
                        not antes["defensor"]["death_ignore_usado"]
                        and depois["defensor"]["death_ignore_usado"]
                    ),
                    defensor_morreu=bool(resultado.did_defender_die),
                    depois=depois,
                )
                return resultado
            finally:
                trace._golpes.pop()

        return resolve_physical_attack

    def e_hit(original):
        def hit_chance(attacker, defender, accuracy_modifier=0):
            chance = original(attacker, defender, accuracy_modifier)
            detalhe = _detalhe_acerto(attacker, defender, accuracy_modifier)
            _confere(detalhe["final"] == chance, f"acerto recalculado {detalhe} != {chance}")
            trace.completar_acerto(chance, detalhe)
            return chance

        return hit_chance

    def e_crit(original):
        def crit_chance(attacker, skill=None):
            chance = original(attacker, skill)
            da_carta = int(getattr(skill, "crit_chance", 0) or 0)
            fontes = int(fx.combat_modifier(attacker, "crit_chance"))
            bruto = CRIT_CHANCE_DEFAULT + da_carta + fontes
            final = max(0, min(bruto, CRIT_CHANCE_CAP))
            _confere(final == chance, f"crítico recalculado {final} != {chance}")
            trace.add(
                "chance_de_critico",
                padrao=CRIT_CHANCE_DEFAULT,
                da_carta=da_carta,
                fontes_do_atacante=fontes,
                bruto=bruto,
                teto=CRIT_CHANCE_CAP,
                final=chance,
            )
            return chance

        return crit_chance

    def e_mods(original):
        def damage_modifiers(attacker, defender, *, is_critical, skill=None):
            mods = original(attacker, defender, is_critical=is_critical, skill=skill)
            xmult = []
            if is_critical:
                extra = fx.combat_modifier(attacker, "crit_damage")
                xmult.append(
                    {
                        "fonte": "crítico",
                        "fator": crit_multiplier(attacker),
                        "formula": f"{CRIT_DAMAGE_BASE} + {extra:g}/100",
                    }
                )
            leis = ix.strike_interactions(attacker, defender, is_critical=is_critical)
            for lei, fator in zip(leis, ix.strike_xmult(leis)):
                xmult.append({"fonte": f"lei {ix.label(lei)}", "fator": fator})
            mult = []
            percentual = fx.combat_modifier(attacker, combat.MULT_MODIFIER)
            if percentual:
                mult.append(
                    {
                        "fonte": "damage_percent (passiva, equipamento ou buff)",
                        "parcela": percentual / 100,
                    }
                )
            condicao = str(getattr(skill, "bonus_condition", "") or "") if skill is not None else ""
            condicao_ok = bool(skill is not None and bonus_condition_met(attacker, skill, defender))
            if condicao_ok and int(getattr(skill, "bonus_percent", 0) or 0):
                mult.append(
                    {
                        "fonte": f"condição da carta ({condicao})",
                        "parcela": int(skill.bonus_percent) / 100,
                    }
                )
            mitigacao = [
                {
                    "fonte": "saída do atacante (outgoing_damage_multiplier)",
                    "fator": fx.outgoing_damage_multiplier(attacker),
                },
                {
                    "fonte": "entrada do defensor (incoming_damage_multiplier)",
                    "fator": fx.incoming_damage_multiplier(defender),
                    "damage_reduction": fx.combat_modifier(defender, "damage_reduction"),
                    "formula": "max(0.1, 1 − min(80, damage_reduction) / 100)",
                },
            ]
            _confere([m["parcela"] for m in mult] == list(mods.mult), "+MULT divergente")
            _confere([x["fator"] for x in xmult] == list(mods.xmult), "×MULT divergente")
            _confere(
                [m["fator"] for m in mitigacao] == list(mods.mitigation), "mitigação divergente"
            )
            trace.add(
                "modificadores",
                critico=is_critical,
                mult=mult,
                xmult=xmult,
                mitigacao=mitigacao,
                condicao_da_carta=condicao or None,
                condicao_satisfeita=condicao_ok if condicao else None,
            )
            return mods

        return damage_modifiers

    def e_calc(original):
        def _calculate_damage(
            base_power, mult_mods=None, xmult_mods=None, defense_target=0, mitigation=None
        ):
            dano = original(base_power, mult_mods, xmult_mods, defense_target, mitigation)
            mult_total = additive_multiplier(mult_mods)
            xmult_bruto = 1.0
            for v in xmult_mods or ():
                xmult_bruto *= v
            xmult = apply_xmult_cap(xmult_bruto)
            defesa = defense_modifier(defense_target)
            bruto = base_power * mult_total * xmult * defesa
            atual = max(1, int(bruto))
            passos = [{"etapa": "max(1, int(bruto))", "valor": atual}]
            for redutor in mitigation or ():
                atual = int(atual * redutor)
                passos.append({"etapa": f"int(anterior × {redutor!r})", "valor": atual})
            final = max(1, atual)
            _confere(final == dano, f"funil recalculado {final} != {dano}")
            trace.add(
                "funil",
                base=base_power,
                mult_total=mult_total,
                mult_formula=f"1 + Σ{list(mult_mods or [])}",
                xmult_bruto=xmult_bruto,
                xmult_teto=XMULT_CAP,
                xmult_aplicado=xmult,
                defesa_alvo=defense_target,
                fator_defesa=defesa,
                fator_defesa_formula=f"{DEFENSE_K} / ({DEFENSE_K} + {max(0, defense_target)})",
                bruto=bruto,
                bruto_formula=f"{base_power!r} × {mult_total!r} × {xmult!r} × {defesa!r}",
                passos=passos,
                final=dano,
            )
            return dano

        return _calculate_damage

    def e_basic(original):
        def basic_attack_power(attacker):
            poder = original(attacker)
            pesos = CLASS_WEIGHTS[attacker.get_classname()]
            termos = [(k, float(attacker.get_stat(k)), float(pesos[k])) for k in ("st", "mg", "ag")]
            soma = sum(v * p for _, v, p in termos)
            arma = attacker.weapon_percent()
            media = max(1, int(soma * (1 + arma / 100)))
            _confere(media == attacker.get_avg_damage(), "dano médio divergente")
            calculado = max(1, int(media * BASIC_ATTACK_POWER_MULT))
            _confere(calculado == poder, f"poder básico {calculado} != {poder}")
            trace.add(
                "base_ataque_basico",
                termos=[{"stat": k, "valor": v, "peso": p, "produto": v * p} for k, v, p in termos],
                soma_ponderada=soma,
                arma_percent=arma,
                media=media,
                media_formula=f"max(1, int({soma!r} × (1 + {arma:g}/100)))",
                multiplicador_basico=BASIC_ATTACK_POWER_MULT,
                poder=poder,
                poder_formula=f"max(1, int({media} × {BASIC_ATTACK_POWER_MULT}))",
            )
            return poder

        return basic_attack_power

    def e_skill_base(original):
        def skill_damage_base(caster, skill, target=None):
            poder = original(caster, skill, target)
            escala = getattr(skill, "scaling", ())
            if escala and getattr(skill, "power", 0):
                termos = [(t.stat, float(caster.get_stat(t.stat)), float(t.weight)) for t in escala]
                soma = sum(v * p for _, v, p in termos)
                arma = caster.weapon_percent()
                com_arma = soma * (1 + arma / 100)
                total = com_arma * float(skill.power)
                calculado = max(1, int(total))
                _confere(calculado == poder, f"BASE da skill {calculado} != {poder}")
                trace.add(
                    "base_skill",
                    skill=skill.id,
                    termos=[
                        {"stat": k, "valor": v, "peso": p, "produto": v * p} for k, v, p in termos
                    ],
                    soma_ponderada=soma,
                    arma_percent=arma,
                    com_arma=com_arma,
                    power=float(skill.power),
                    total=total,
                    poder=poder,
                    poder_formula=(
                        f"max(1, int({soma!r} × (1 + {arma:g}/100) × {float(skill.power)!r}))"
                    ),
                )
            else:
                trace.add("base_skill", skill=skill.id, sem_escala=True, poder=poder)
            return poder

        return skill_damage_base

    def e_egide(original):
        def _absorve_com_egide(defender, damage, publish):
            fracao = int(getattr(defender, "magic_shield_percent", 0) or 0)
            mana = int(defender.get_mp())
            detalhe = {
                "defensor": trace.lado(defender),
                "fracao": fracao,
                "mp_livre": mana,
                "dano_entrada": damage,
            }
            if fracao <= 0 or damage <= 1 or mana <= 0:
                esperado, custo = damage, 0
                detalhe["inaplicavel"] = True
            else:
                desejado = int(damage * fracao / 100)
                possivel = min(desejado, int(mana * MAGIC_SHIELD_DAMAGE_PER_MP))
                if possivel <= 0:
                    esperado, custo = damage, 0
                else:
                    custo = max(1, int(possivel / MAGIC_SHIELD_DAMAGE_PER_MP))
                    esperado = max(1, damage - possivel)
                detalhe.update(
                    desejado=desejado,
                    desejado_formula=f"int({damage} × {fracao} / 100)",
                    possivel=possivel,
                    possivel_formula=f"min({desejado}, int({mana} × {MAGIC_SHIELD_DAMAGE_PER_MP}))",
                    custo_mp=custo,
                    custo_formula=f"max(1, int({possivel} / {MAGIC_SHIELD_DAMAGE_PER_MP}))",
                )
            passa = original(defender, damage, publish)
            _confere(passa == esperado, f"Égide recalculada {esperado} != {passa}")
            _confere(mana - defender.get_mp() == custo, "custo da Égide divergente")
            trace.add("egide", **detalhe, dano_saida=passa)
            return passa

        return _absorve_com_egide

    def e_status(original):
        def try_apply_status(
            target,
            status,
            base_chance,
            duration,
            r,
            publish=None,
            *,
            applied_kind=None,
            source_id="",
        ):
            origem = sys._getframe(1).f_code.co_name
            resistencia = fx.status_resistance(target, status)
            efetiva = fx.effective_status_chance(base_chance, resistencia)
            duracao_lei, leis = ix.duration_before_apply(target, status, duration)
            antes = [dict(i) for i in core.instances(target) if i.effect == status]
            inicio = len(trace.records)
            pegou = original(
                target,
                status,
                base_chance,
                duration,
                r,
                publish,
                applied_kind=applied_kind,
                source_id=source_id,
            )
            depois = [dict(i) for i in core.instances(target) if i.effect == status]
            rolagens = [r for r in trace.records[inicio:] if r["kind"] == "rolagem"]
            _confere(len(rolagens) == (1 if efetiva > 0 else 0), "rolagens de status divergentes")
            trace.add(
                "status",
                origem=origem,
                alvo=trace.lado(target),
                status=status,
                fonte=source_id,
                chance_base=base_chance,
                resistencia_do_alvo=resistencia,
                chance_efetiva=efetiva,
                chance_formula=f"{base_chance:g} × (1 − {resistencia:g}/100)",
                rolou=efetiva > 0,
                rolagem_seq=rolagens[0]["seq"] if rolagens else None,
                rolagem_valor=rolagens[0]["valor"] if rolagens else None,
                rolagem_aprovada=rolagens[0]["aprovado"] if rolagens else None,
                atacante=trace.ator,
                duracao_pedida=duration,
                duracao_apos_leis=duracao_lei,
                leis_de_duracao=[ix.label(lei) for lei in leis],
                pegou=pegou,
                instancia_antes=antes,
                instancia_depois=depois,
            )
            return pegou

        return try_apply_status

    def e_interacoes(original):
        # As leis anunciadas com `publish=None` (golpe interno de `apply_skill`)
        # não chegam ao EventBus; o registro aqui não depende dele.
        def _anunciar_interacoes(attacker, defender, disparadas, publish):
            if disparadas:
                trace.add(
                    "interacoes",
                    ator_da_lei=trace.lado(attacker),
                    alvo_da_lei=trace.lado(defender),
                    leis=[{"id": lei, "nome": ix.label(lei)} for lei in disparadas],
                    origem=sys._getframe(1).f_code.co_name,
                )
            original(attacker, defender, disparadas, publish)

        return _anunciar_interacoes

    troca(pvp_duel, "read_initiative", e_read_initiative)
    troca(pvp_duel, "order_by_initiative", e_order)
    troca(combat, "process_turn_start_effects", e_turn_start)
    troca(core, "tick_effects", e_tick)
    troca(combat, "apply_skill", e_apply_skill)
    troca(combat, "resolve_physical_attack", e_resolve)
    troca(combat, "hit_chance", e_hit)
    troca(combat, "crit_chance", e_crit)
    troca(combat, "damage_modifiers", e_mods)
    troca(combat, "_calculate_damage", e_calc)
    troca(combat, "basic_attack_power", e_basic)
    troca(combat, "skill_damage_base", e_skill_base)
    troca(combat, "_absorve_com_egide", e_egide)
    troca(combat, "try_apply_status", e_status)
    troca(combat, "_anunciar_interacoes", e_interacoes)
    try:
        yield trace
    finally:
        for modulo, nome, original, _ in reversed(trocadas):
            setattr(modulo, nome, original)
        trace.trocas = []


@contextlib.contextmanager
def fora_do_duelo(trace: Trace):
    """As funções canônicas originais durante o bloco; os embrulhos de volta no fim.

    É o que um controlador enxerga enquanto escolhe. A `PoliticaCopa` não chama
    nada do motor; a IA estratégica simula rodadas inteiras em cópias, e cada
    golpe simulado entraria no trace do duelo verdadeiro como se tivesse
    acontecido.
    """
    trocadas = list(getattr(trace, "trocas", ()))
    for modulo, nome, original, _ in reversed(trocadas):
        setattr(modulo, nome, original)
    try:
        yield
    finally:
        for modulo, nome, _, embrulho in trocadas:
            setattr(modulo, nome, embrulho)


class ControladorAuditado:
    """Envolve o controlador de um lado e anota a visão, as opções e a escolha."""

    def __init__(self, interno, lado: str, heroi, trace: Trace) -> None:
        self._interno = interno
        self._lado = lado
        self._heroi = heroi
        self._trace = trace

    def choose(self, view):
        with fora_do_duelo(self._trace):
            acao = self._interno.choose(view)
        skill = None
        if acao.kind == "skill":
            skill = next((s for s in self._heroi.skills.values() if s.id == acao.skill_id), None)
        self._trace.add(
            "escolha",
            lado=self._lado,
            visao=view,
            acoes_legais=list(view.legal_actions),
            acao=acao,
            justificativa=getattr(self._interno, "last_reason", ""),
            legal=acao in view.legal_actions,
            custo_mp=(combat.skill_mana_cost(self._heroi, skill) if skill is not None else 0),
            recargas_no_lock=dict(view.cooldowns),
        )
        return acao


@dataclasses.dataclass
class DueloAuditado:
    duelo: Duel
    trace: Trace | None
    rng: object
    inconclusivo: bool
    # O estado dos dois lados ao fim de cada rodada, lido entre rodadas pelos
    # getters públicos — a mesma leitura nos dois caminhos, para compará-los.
    fotos: list = dataclasses.field(default_factory=list)


def _fotografar(duelo: Duel) -> dict:
    return {lado: foto(duelo.hero(lado)) for lado in SIDES}


def disputar(
    g1, g2, seed: int, fabrica_de_controlador, *, auditar: bool, limite: int
) -> DueloAuditado:
    """Um duelo completo, com ou sem a auditoria. O limite é técnico, não regra.

    Sem auditoria: `random.Random(seed)`, nenhum embrulho e `publish=None` — o
    duelo exatamente como o motor o joga. Com auditoria: o mesmo duelo visto
    por dentro.
    """
    if not auditar:
        rng = random.Random(seed)
        duelo = Duel(g1, g2, rng=rng)
        controles = {lado: fabrica_de_controlador(duelo.hero(lado)) for lado in SIDES}
        fotos = []
        while not duelo.finished and duelo.round_number <= limite:
            run_round(duelo, controles)
            fotos.append(_fotografar(duelo))
        return DueloAuditado(duelo, None, rng, not duelo.finished, fotos)

    trace = Trace()
    rng = RngGravado(seed, trace)
    duelo = Duel(g1, g2, rng=rng, publish=trace.publish)
    trace.registrar_lados(duelo)
    duelo._event = trace.embrulhar_evento(duelo._event)
    controles = {
        lado: ControladorAuditado(
            fabrica_de_controlador(duelo.hero(lado)), lado, duelo.hero(lado), trace
        )
        for lado in SIDES
    }
    trace.add("fichas", p1=ficha(duelo.hero("p1")), p2=ficha(duelo.hero("p2")), seed=seed)
    corte_original = duelo._clamp_free_mp

    def _clamp_free_mp(heroi, reservado):
        antes = int(heroi.get_mp())
        corte_original(heroi, reservado)
        trace.add(
            "corte_de_mp_livre",
            reservado=reservado,
            teto_livre=max(0, int(heroi.base_mp) - reservado),
            mp_antes=antes,
            mp_depois=int(heroi.get_mp()),
        )

    duelo._clamp_free_mp = _clamp_free_mp
    fotos = []
    with interceptar(trace):
        while not duelo.finished and duelo.round_number <= limite:
            trace.round = duelo.round_number
            trace.ator = None
            trace.add("rodada_inicio", estado=_fotografar(duelo))
            registro = run_round(duelo, controles)
            trace.ator = None
            fotos.append(_fotografar(duelo))
            trace.add("rodada_fim", registro=registro, estado=fotos[-1])
    trace.round = duelo.round_number
    trace.add(
        "resultado",
        resultado=(
            None
            if duelo.result is None
            else {
                campo: getattr(duelo.result, campo)
                for campo in ("winner", "loser", "winner_name", "loser_name", "reason", "rounds")
            }
        ),
        inconclusivo=not duelo.finished,
        limite_tecnico=limite,
        chamadas_ao_rng=rng.chamadas,
    )
    return DueloAuditado(duelo, trace, rng, not duelo.finished, fotos)
