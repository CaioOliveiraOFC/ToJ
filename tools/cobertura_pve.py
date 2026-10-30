"""Cobertura dos sistemas PvE numa run do BotPadrão: disponível, usado e efeito.

Portado das sondas da auditoria de cobertura PvE (`reports/auditoria_pve/`, na
branch `phase/pvp-arena`, commit `5b99109`), sem merge: aqui elas embrulham o
BotPadrão canônico, e não o gerador da Copa, e rodam sobre o protocolo histórico
de progressão (`baselines/progression/d3105edc/run_auditoria.py`).

Nada em `src/` ou em `tools/bot_padrao.py` muda. Cada sonda envolve uma função
real, chama a original e só OBSERVA: não sorteia, não altera argumento nem
retorno. A prova é o determinismo: o registro de cada run sai com os MESMOS
campos do coletor histórico, e `conferir` os compara com a baseline publicada.

Duas fontes de ruído ficam de fora da contagem, de propósito:

- os duelos de benchmark que medem o OP (o bot os roda DENTRO da decisão de
  extração, pelo mesmo motor de combate);
- qualquer coisa depois do fim da run.

Uso, a partir da raiz do repositório:

    python tools/cobertura_pve.py rodar --saida cobertura.jsonl [--workers 4]
    python tools/cobertura_pve.py conferir cobertura.jsonl \
        baselines/progression/d3105edc/depois.jsonl
"""

from __future__ import annotations

import collections
import json
import multiprocessing as mp
import os
import pathlib
import sys

RAIZ = str(pathlib.Path(__file__).resolve().parents[1])
sys.path.insert(0, RAIZ)
os.chdir(RAIZ)

C: dict | None = None  # o coletor da run em curso


def _novo() -> dict:
    return {
        "n": collections.Counter(),
        "listas": collections.defaultdict(list),
        "ctx": [],
        "monstro": None,
        "pares_no_encontro": set(),
        "bot": None,
    }


def n(chave: str, v: int = 1) -> None:
    # Só a run conta: a medição de OP depois da extração roda duelos de
    # benchmark pelo mesmo motor, e eles não são jornada.
    if C is not None and not C.get("encerrada"):
        C["n"][chave] += v


def lista(chave: str, item) -> None:
    if C is not None and not C.get("encerrada"):
        C["listas"][chave].append(item)


def ctx() -> str:
    return C["ctx"][-1] if C and C["ctx"] else ""


class _Ctx:
    def __init__(self, nome):
        self.nome = nome

    def __enter__(self):
        if C is not None:
            C["ctx"].append(self.nome)

    def __exit__(self, *a):
        if C is not None and C["ctx"]:
            C["ctx"].pop()


# Quem chamou `try_apply_status` diz de onde o status veio. São os quatro
# chamadores de `src/mechanics/combat.py`; qualquer outro aparece pelo nome, e
# não some numa categoria genérica.
ORIGENS_DE_STATUS = {
    "apply_skill": "skill_principal",
    "_aplicar_secundario": "skill_secundario",
    "_try_apply_stun": "atordoamento",
    "_aplicar_procs_on_hit": "proc_de_acerto",
}

# Os desfechos de uma tentativa, na ordem em que `try_apply_status` decide:
DESFECHOS_DE_STATUS = (
    "sem_alvo",  # o alvo não carrega efeitos
    "chance_zero",  # a chance base já era zero
    "imune",  # a resistência levou a chance efetiva a zero; não rola
    "falhou_rolagem",  # rolou e não pegou
    "recusado_nucleo",  # pegou na rolagem e o núcleo não aplicou
    "aplicado",
)


def sonda_de_status(registrar, lado_do_alvo):
    """Mede cada tentativa de status na porta única do combate (KI-015).

    A sonda anterior contava o evento `<status>_applied`. Esse evento só é
    publicado quando quem chama passa `applied_kind`, e o ramo principal das
    skills de status não passa, então `frozen`, `sleep` e `invisible` apareciam
    com zero aplicações enquanto as leis que dependem deles disparavam.

    Aqui a contagem é por CHAMADA. Antes de chamar a original, a sonda calcula a
    chance efetiva com as mesmas funções puras que o combate usa
    (`status_resistance` e `effective_status_chance`); dentro da chamada,
    observa se `effect_core.apply_effect` foi alcançado e o que devolveu. Nada
    disso sorteia nem altera argumento ou retorno: o combate segue idêntico.

    `lado_do_alvo(alvo)` devolve "heroi", "monstro" ou `None` (não conta).
    `registrar(chave, valor)` soma. Devolve a função que desinstala.
    """
    from src.mechanics import combat as cmb
    from src.shared import effect_core as core
    from src.shared import effects as fx

    orig_tentar = cmb.try_apply_status
    orig_aplicar = core.apply_effect
    em_curso: list[dict] = []

    def aplicar(entity, effect_id, *a, **k):
        instancia = orig_aplicar(entity, effect_id, *a, **k)
        if em_curso:
            em_curso[-1]["nucleo"] = instancia is not None
        return instancia

    def tentar(target, status, base_chance, duration, r, publish=None, **k):
        lado = lado_do_alvo(target)
        if lado is None:
            return orig_tentar(target, status, base_chance, duration, r, publish, **k)
        chamador = sys._getframe(1).f_code.co_name
        origem = ORIGENS_DE_STATUS.get(chamador, f"outro_{chamador}")
        tem_efeitos = hasattr(target, "active_effects")
        resistencia = fx.status_resistance(target, status) if tem_efeitos else 0.0
        chance = fx.effective_status_chance(base_chance, resistencia) if tem_efeitos else 0.0
        moldura = {"nucleo": None}
        em_curso.append(moldura)
        try:
            pegou = orig_tentar(target, status, base_chance, duration, r, publish, **k)
        finally:
            em_curso.pop()
        if not tem_efeitos:
            desfecho = "sem_alvo"
        elif chance <= 0:
            desfecho = "imune" if base_chance > 0 else "chance_zero"
        elif moldura["nucleo"] is None:
            desfecho = "falhou_rolagem"
        elif not moldura["nucleo"]:
            desfecho = "recusado_nucleo"
        else:
            desfecho = "aplicado"
        sufixo = f"{status}:{origem}:em_{lado}"
        registrar(f"status.tentativa:{sufixo}", 1)
        registrar(f"status.{desfecho}:{sufixo}", 1)
        if chance > 0:
            # A chance que rolou, em centésimos de ponto percentual: a soma
            # dividida por 10.000 é o número ESPERADO de aplicações, a régua
            # contra a qual o aplicado se compara.
            registrar(f"status.chance_centesimos:{sufixo}", int(round(chance * 100)))
            if 0 < resistencia < 100:
                registrar(f"status.resistencia_parcial:{sufixo}", 1)
        return pegou

    cmb.try_apply_status = tentar
    core.apply_effect = aplicar

    def desinstalar():
        cmb.try_apply_status = orig_tentar
        core.apply_effect = orig_aplicar

    return desinstalar


def instalar() -> None:
    """Instala as sondas. Chamado uma vez por processo trabalhador."""
    import tools.bot_padrao as bp
    from src.content import extraction, forge
    from src.content import shop as shop_mod
    from src.engine import encounter as enc
    from src.entities.heroes import Player
    from src.mechanics import monster_ai as mai
    from src.shared import combat_topics as T
    from src.shared import constants as K
    from src.shared import effect_core as core
    from src.sim import progression as prog

    itens = {}
    try:
        from src.content.items import get_all_items

        for it in get_all_items().values():
            itens[str(getattr(it, "id", it.name))] = it
    except Exception:  # noqa: BLE001
        pass

    def lado(entidade) -> str:
        if C is None or C["bot"] is None:
            return "?"
        return "heroi" if entidade is C["bot"].hero else "monstro"

    def raridade(item) -> str:
        return str(getattr(item, "rarity", "?"))

    def peso(item) -> float:
        return prog._peso_do_item(item) if item is not None else 0.0

    # --- o bot e o andar ------------------------------------------------
    orig_init = bp.BotPadrao.__init__

    def init(self, *a, **k):
        orig_init(self, *a, **k)
        if C is not None:
            C["bot"] = self
            for pos, item in self.hero.equipment.items():
                if item is not None and getattr(item, "origin", None) == "starter":
                    C["starter"] = {
                        "nome": item.name,
                        "slot": str(getattr(item, "slot", pos)),
                        "pos": pos,
                    }

    bp.BotPadrao.__init__ = init

    orig_jogar = bp.BotPadrao.jogar

    def jogar(self):
        try:
            return orig_jogar(self)
        finally:
            if C is not None:
                C["encerrada"] = True

    bp.BotPadrao.jogar = jogar

    orig_setup = bp._setup_dungeon_map

    def setup(andar, *a, **k):
        mapa = orig_setup(andar, *a, **k)
        if C is not None:
            feats = collections.Counter(mapa.features.values())
            chefes = sum(1 for m in mapa.enemies_pos.values() if getattr(m, "is_boss", False))
            papeis = collections.Counter(
                str(getattr(m, "role", "?")) for m in mapa.enemies_pos.values()
            )
            C["andar_atual"] = {
                "andar": andar,
                "monstros": len(mapa.enemies_pos),
                "chefes": chefes,
                "papeis": dict(papeis),
                "loja": feats.get("shop", 0),
                "ferreiro": feats.get("forge", 0),
                "extracao": feats.get("extraction", 0),
                "evento": mapa.event_type,
                "chave_no_inicio": None,
            }
            bot = C["bot"]
            if bot is not None:
                C["andar_atual"]["chave_no_inicio"] = bool(extraction.has_key(bot.hero))
        return mapa

    bp._setup_dungeon_map = setup

    orig_andar = bp.BotPadrao._jogar_andar

    def jogar_andar(self, andar):
        desfecho = orig_andar(self, andar)
        if C is not None and C.get("andar_atual"):
            reg = dict(C["andar_atual"])
            mapa = self.mapa
            restantes = collections.Counter(mapa.features.values())
            reg["loja_usada"] = reg["loja"] - restantes.get("shop", 0)
            reg["ferreiro_usado"] = reg["ferreiro"] - restantes.get("forge", 0)
            reg["evento_consumido"] = reg["evento"] is not None and mapa.event_type is None
            reg["chefes_restantes"] = sum(
                1 for m in mapa.enemies_pos.values() if getattr(m, "is_boss", False)
            )
            reg["chave_no_fim"] = bool(extraction.has_key(self.hero))
            reg["desfecho"] = desfecho
            pa = self.por_andar[-1] if self.por_andar else {}
            reg["essencia_sorteada"] = pa.get("essencia_sorteada")
            reg["essencia_efetiva"] = pa.get("essencia_efetiva")
            reg["saida_paga"] = pa.get("saida_paga")
            reg["juros"] = pa.get("juros")
            lista("andares", reg)
        return desfecho

    bp.BotPadrao._jogar_andar = jogar_andar

    # --- o encontro --------------------------------------------------------
    orig_res = bp.resolve_encounter

    def resolver(hero, monstros, **k):
        m = monstros[0]
        if C is not None:
            C["monstro"] = m
            C["pares_no_encontro"] = set()
            C["fuga_decidida"] = False
            if "Benção do Altar" in getattr(hero, "active_buffs", {}):
                n("altar.buff_ativo_ao_entrar_em_combate")
        papel = str(getattr(m, "role", "?"))
        chefe = bool(getattr(m, "is_boss", False))
        r = orig_res(hero, monstros, **k)
        n(f"encontro.papel:{papel}")
        if chefe:
            n("encontro.chefe")
            if r.hero_won:
                n("encontro.chefe_derrotado")
        if r.fled:
            n("fuga.sucesso")
            n(f"fuga.sucesso_papel:{papel}")
        elif C is not None and C.get("fuga_decidida"):
            n("fuga.falhou_e_seguiu")
        if r.hero_won:
            n("loot.vitorias")
            n(f"encontro.vitoria_papel:{papel}")
        if r.levels_gained:
            n("nivel.ganhos", r.levels_gained)
        if C is not None:
            for par in C["pares_no_encontro"]:
                n(f"lei_core:{par}")
            C["monstro"] = None
        return r

    bp.resolve_encounter = resolver

    # --- o barramento de combate (só a batalha real publica aqui) ------------
    orig_obs = bp.Observador.__call__

    def observar(self, topic, evento):
        orig_obs(self, topic, evento)
        if C is None:
            return
        payload = getattr(evento, "payload", {}) or {}
        if topic == T.COMBAT_TURN_EFFECT:
            kind = str(payload.get("kind", ""))
            quem = lado(payload.get("entity"))
            if kind == "interaction":
                ator = lado(payload.get("actor"))
                n(f"lei:{payload.get('interaction')}:{ator}")
            elif kind.endswith("_applied"):
                n(f"status_aplicado:{kind[:-8]}:em_{quem}")
            elif kind == "status_resisted":
                n(f"status_resistido:{payload.get('status')}:em_{quem}")
            elif kind == "magic_shield":
                n("egide.absorveu")
        elif topic == T.COMBAT_SKILL_OUTCOME:
            caster = payload.get("caster")
            res = payload.get("result")
            if lado(caster) == "heroi":
                n(f"skill_heroi_resultado:{getattr(res, 'kind', '?')}")
                if getattr(res, "status_effect", None):
                    ok = "sucesso" if getattr(res, "status_success", False) else "falhou"
                    n(f"skill_heroi_status:{res.status_effect}:{ok}")
            else:
                papel = str(getattr(caster, "role", "?"))
                n(f"skill_monstro:{papel}:{getattr(res, 'kind', '?')}")
            # O status PRINCIPAL de uma carta de status não publica :
            # ele só aparece aqui, no resultado da skill. Dos dois lados.
            if getattr(res, "status_effect", None):
                ok = "sucesso" if getattr(res, "status_success", False) else "falhou"
                alvo = lado(payload.get("target"))
                n(f"status_principal:{res.status_effect}:{ok}:em_{alvo}")
        elif topic == T.COMBAT_PHYSICAL_STRIKE:
            golpe = payload.get("strike")
            if golpe is not None and getattr(golpe, "was_critical", False):
                n(f"critico:{lado(payload.get('attacker'))}")
        # Leis CORE: co-presença do par oposto na mesma entidade, na luta real.
        for ent in (C["bot"].hero if C["bot"] else None, C["monstro"]):
            if ent is None:
                continue
            ids = {i.effect for i in core.instances(ent)}
            for a in ids:
                b = core.OPPOSING_PAIRS.get(a)
                if b and b in ids:
                    C["pares_no_encontro"].add(f"{min(a, b)}+{max(a, b)}:{lado(ent)}")

    bp.Observador.__call__ = observar

    orig_break = core.break_on_damage

    def quebrar(entity):
        saiu = orig_break(entity)
        if saiu and C is not None and C["monstro"] is not None:
            n(f"lei_core:sleep_damage:{lado(entity)}")
        return saiu

    core.break_on_damage = quebrar

    # --- status: a porta única (KI-015) ----------------------------------------
    def lado_no_encontro(alvo):
        # Só a batalha real conta. Fora do encontro, o que roda pelo mesmo motor
        # são os duelos de benchmark do OP, e eles não são jornada.
        if C is None or C.get("encerrada") or C["monstro"] is None or C["bot"] is None:
            return None
        if alvo is C["bot"].hero:
            return "heroi"
        if alvo is C["monstro"]:
            return "monstro"
        return None

    sonda_de_status(n, lado_no_encontro)

    # --- a IA do monstro -----------------------------------------------------
    orig_pick = mai._pick_skill

    def pick(monster, hero, usable, rng):
        escolha, decisiva = orig_pick(monster, hero, usable, rng)
        if C is None or C["monstro"] is not monster:
            return escolha, decisiva  # duelo de benchmark, não jornada
        papel = str(getattr(monster, "role", "?"))
        proprio = mai._hp_ratio(monster)
        alvo = mai._hp_ratio(hero)
        turnos = int(getattr(monster, "turns_taken", 0))
        heals = [s for s in usable if s.effect_type == "heal"]
        defens = [s for s in usable if s.effect_type in mai.DEFENSIVE_EFFECTS]
        damages = [s for s in usable if s.effect_type == "damage"]
        if alvo < K.MONSTER_EXECUTE_HP_RATIO:
            n(f"ia.execucao.oportunidade:{papel}")
            if damages:
                n(f"ia.execucao.usou:{papel}")
                return escolha, decisiva
        if proprio < K.MONSTER_HEAL_HP_RATIO:
            n(f"ia.sobrevivencia.oportunidade:{papel}")
            if heals:
                n(f"ia.sobrevivencia.usou:{papel}")
                return escolha, decisiva
        if proprio < K.MONSTER_DESPERATE_HP_RATIO:
            n(f"ia.desespero.oportunidade:{papel}")
            if escolha is not None and decisiva:
                n(f"ia.desespero.usou:{papel}")
                return escolha, decisiva
        if turnos < K.MONSTER_OPENER_TURNS and papel in mai.OPENER_ROLES:
            n(f"ia.abertura.oportunidade:{papel}")
            if defens:
                n(f"ia.abertura.usou:{papel}")
                return escolha, decisiva
        n(f"ia.rotina:{papel}")
        return escolha, decisiva

    mai._pick_skill = pick

    orig_decide_m = mai.decide_monster_action

    def decide_m(monster, hero, **k):
        if C is None or C["monstro"] is not monster:
            return orig_decide_m(monster, hero, **k)
        papel = str(getattr(monster, "role", "?"))
        n(f"ia.turnos:{papel}")
        if not mai._usable_skills(monster, hero):
            n(f"ia.sem_skill_usavel:{papel}")
        return orig_decide_m(monster, hero, **k)

    mai.decide_monster_action = decide_m
    import src.mechanics.battle as battle_mod

    battle_mod.decide_monster_action = decide_m

    # --- a medição de OP que o bot faz DURANTE a run (decisão de extração) ---
    import tools.bot_adapter as adapter

    orig_cmp = adapter.comparar_com_benchmark

    def comparar(hero, **k):
        n("op.medicoes_na_run")
        r = orig_cmp(hero, **k)
        lista(
            "op_na_run",
            {
                "andar": getattr(C["bot"], "andar", None) if C and C["bot"] else None,
                "relativo": round(float(r.relativo), 4),
            },
        )
        return r

    adapter.comparar_com_benchmark = comparar

    # --- a decisão de combate do herói ---------------------------------------
    orig_dc = bp.decidir_no_combate

    def decidir_c(estado, opcoes):
        d = orig_dc(estado, opcoes)
        aid = d.action_id
        fam = aid.split(":")[0]
        n(f"heroi.acao:{fam}")
        com_lei = [o for o in opcoes if getattr(o.mechanics, "interactions", ())]
        if com_lei:
            n("heroi.turno_com_lei_disponivel")
            if any(o.action_id == aid for o in com_lei):
                n("heroi.escolheu_acao_com_lei")
        for o in opcoes:
            if o.action_id.startswith("skill:") and C is not None:
                C["listas"]["skills_disponiveis"].append(o.action_id[6:])
            if o.action_id.startswith("item:"):
                it = itens.get(o.action_id[5:])
                n(f"item_disponivel_turno:{getattr(it, 'effect_type', '?')}")
        if aid.startswith("skill:"):
            n(f"skill_heroi_escolhida:{aid[6:]}")
        if aid.startswith("item:"):
            it = itens.get(aid[5:])
            n(f"item_usado_combate:{getattr(it, 'effect_type', '?')}")
        if aid == "flee" and C is not None:
            C["fuga_decidida"] = True
            n("fuga.decidida")
        return d

    bp.decidir_no_combate = decidir_c

    # --- nível ----------------------------------------------------------------
    orig_nivel = bp.BotPadrao._escolher_do_nivel

    def escolher(self, jogador, oferta):
        antes_p = len(jogador.passives)
        antes_s = {getattr(s, "id", s.name) for s in jogador.skills.values()}
        deck_cheio = len(jogador.skills) >= K.MAX_ACTIVE_SKILLS
        n("nivel.ofertas_passiva")
        for c in oferta.passives:
            n(f"passiva.oferecida_raridade:{c.rarity}")
        r = orig_nivel(self, jogador, oferta)
        if len(jogador.passives) > antes_p:
            nova = jogador.passives[-1]
            n("passiva.escolhida")
            n(f"passiva.familia:{getattr(nova, 'effect_type', '?')}")
            n(f"passiva.raridade:{getattr(nova, 'rarity', '?')}")
        if oferta.tem_skill:
            n("skill.ofertas")
            depois = {getattr(s, "id", s.name) for s in jogador.skills.values()}
            novas = depois - antes_s
            if novas:
                n("skill.aprendida")
                if deck_cheio:
                    n("skill.substituiu")
                for sid in novas:
                    lista("skills_aprendidas", sid)
            else:
                n("skill.recusou")
        return r

    bp.BotPadrao._escolher_do_nivel = escolher

    # --- eventos --------------------------------------------------------------
    orig_ev = bp.BotPadrao._resolver_evento

    def evento(self, tipo):
        hp0 = self.hero.get_hp()
        ouro0 = self.hero.coins
        n(f"evento.pisou:{tipo}")
        with _Ctx("mercador" if tipo == "merchant" else f"evento:{tipo}"):
            r = orig_ev(self, tipo)
        if tipo == "fountain" and self.hero.get_hp() > hp0:
            n("evento.fonte_curou")
        if tipo == "altar":
            if "Benção do Altar" in self.hero.active_buffs:
                n("evento.altar_aceito")
                n("evento.altar_hp_pago", hp0 - self.hero.get_hp())
            else:
                n("evento.altar_recusado")
        if tipo == "merchant" and self.hero.coins != ouro0:
            n("evento.mercador_gastou")
        return r

    bp.BotPadrao._resolver_evento = evento

    orig_compra = bp.BotPadrao._comprar_com_orcamento

    def comprar(self, rotulo):
        with _Ctx("mercador" if "Mercador" in rotulo else "loja"):
            return orig_compra(self, rotulo)

    bp.BotPadrao._comprar_com_orcamento = comprar

    # --- loja -----------------------------------------------------------------
    orig_visit = shop_mod.Shop.visit

    def visit(self, dungeon_level, classe):
        v = orig_visit(self, dungeon_level, classe)
        n(f"{ctx() or 'loja'}.vitrines")
        return v

    shop_mod.Shop.visit = visit

    orig_reroll = shop_mod.ShopVisit.reroll

    def reroll(self, player):
        ok = orig_reroll(self, player)
        if ok:
            n(f"{ctx() or 'loja'}.reroll_pago")
        return ok

    shop_mod.ShopVisit.reroll = reroll

    orig_tem = prog._tem_o_que_comprar

    def tem(hero, ofertas):
        r = orig_tem(hero, ofertas)
        if not r:
            n(f"{ctx() or 'loja'}.vitrine_sem_nada_util")
        return r

    prog._tem_o_que_comprar = tem

    orig_buy = shop_mod.Shop.buy_item

    def buy(self, player, item, dungeon_level):
        ok = orig_buy(self, player, item, dungeon_level)
        if ok:
            c = ctx() or "loja"
            if getattr(item, "consumable", False):
                n(f"{c}.comprou_consumivel:{item.effect_type}")
            else:
                n(f"{c}.comprou_equipamento")
                n(f"{c}.comprou_raridade:{raridade(item)}")
        return ok

    shop_mod.Shop.buy_item = buy

    orig_sell = shop_mod.Shop.sell_item

    def sell(self, player, item, dungeon_level):
        ok = orig_sell(self, player, item, dungeon_level)
        if ok:
            n("venda.itens")
        return ok

    shop_mod.Shop.sell_item = sell

    orig_rec = prog.buy_recovery

    def rec(hero, dungeon_level, recurso):
        r = orig_rec(hero, dungeon_level, recurso)
        if r:
            n(f"recuperacao.comprou:{recurso}")
        return r

    prog.buy_recovery = rec

    orig_vend = prog._vender_dominados

    def vend(hero, shop, dungeon_level):
        with _Ctx("reavaliar_mochila"):
            return orig_vend(hero, shop, dungeon_level)

    prog._vender_dominados = vend

    # --- ferreiro ---------------------------------------------------------------
    orig_vf = prog.visit_forge

    def vf(hero, dungeon_level, toggles=None, telemetry=None):
        n("ferreiro.visitas")
        vazios = sum(sum(1 for g in it.gems if g is None) for it in forge.socketable(hero))
        if hero.gems and vazios:
            n("ferreiro.oportunidade_engastar")
        if hero.gems and not vazios:
            n("ferreiro.gemas_sem_socket_vazio")
        ouro = hero.coins
        orc = int(ouro * prog.BOT_FORGE_BUDGET_RATIO)
        pecas = forge.enhanceable(hero)
        if pecas:
            minimo = min(prog.enhancement_cost(p, dungeon_level) for p in pecas)
            if minimo <= orc:
                n("ferreiro.oportunidade_aprimorar")
            if minimo <= ouro:
                n("ferreiro.oportunidade_aprimorar_sem_teto_do_bot")
        with _Ctx("ferreiro"):
            return orig_vf(hero, dungeon_level, toggles, telemetry)

    prog.visit_forge = vf

    def embrulhar(nome):
        orig = getattr(forge, nome)

        def w(player, item, *a, **k):
            r = orig(player, item, *a, **k)
            if r is not None and r is not False:
                n(f"ferreiro.{nome}")
                n(f"ferreiro.{nome}_slot:{getattr(item, 'slot', '?')}")
            return r

        setattr(forge, nome, w)

    for nome in ("enhance", "socket", "unsocket", "enchant", "reenchant"):
        embrulhar(nome)

    # --- loot e equipar -----------------------------------------------------------
    orig_loot = enc.get_loot

    def loot(*a, **k):
        it = orig_loot(*a, **k)
        if it is not None:
            if getattr(it, "consumable", False):
                n(f"loot.drop_consumivel:{it.effect_type}")
            else:
                n("loot.drop_equipamento")
                n(f"loot.drop_raridade:{raridade(it)}")
        return it

    enc.get_loot = loot

    orig_eib = prog.equip_if_better

    def eib(hero, item):
        externo = ctx()
        ok = orig_eib(hero, item)
        if ok and externo == "" and not getattr(item, "consumable", False):
            n("loot.drop_equipado")
            n(f"loot.drop_equipado_raridade:{raridade(item)}")
        return ok

    prog.equip_if_better = eib

    orig_equip = Player.equip

    def equip(self, item, position=None):
        if C is not None and C["bot"] is not None and self is C["bot"].hero and position is None:
            disp = self.available_positions_for(item)
            livre = self.free_position_for(item)
            if disp and not livre:
                alvo = disp[0]
                sai = self.equipment.get(alvo)
                ocup = [self.equipment.get(p) for p in disp]
                pior = min(ocup, key=peso) if all(o is not None for o in ocup) else None
                cat = str(getattr(item, "slot", "?"))
                if pior is not None and sai is not pior and peso(sai) > peso(pior):
                    n(f"equip.trocou_a_peca_errada:{cat}")
                    n("equip.trocou_a_peca_errada")
                    if peso(item) < peso(sai):
                        n("equip.troca_errada_com_perda_liquida")
                        lista(
                            "trocas_com_perda",
                            {
                                "andar": getattr(C["bot"], "andar", None),
                                "contexto": ctx() or "loot",
                                "entrou": item.name,
                                "peso_entrou": peso(item),
                                "saiu": getattr(sai, "name", None),
                                "peso_saiu": peso(sai),
                                "pior": getattr(pior, "name", None),
                                "peso_pior": peso(pior),
                            },
                        )
                if sai is not None and getattr(sai, "origin", None) == "starter":
                    lista("starter_saiu", getattr(C["bot"], "andar", None))
        return orig_equip(self, item, position)

    Player.equip = equip


def fotografia_final(bot) -> dict:
    """O estado do herói no fim da run (morto ou extraído)."""
    from src.content import forge
    from src.sim import progression as prog

    h = bot.hero
    equip = {p: i for p, i in h.equipment.items() if i is not None}
    out = {
        "equipado": {
            p: {
                "nome": i.name,
                "slot": str(getattr(i, "slot", "?")),
                "raridade": str(getattr(i, "rarity", "?")),
                "mais": int(getattr(i, "enhancement_level", 0) or 0),
                "encantos": len(getattr(i, "enchantments", ()) or ()),
                "sockets": int(getattr(i, "socket_count", 0) or 0),
                "gemas": sum(1 for g in (getattr(i, "gems", None) or ()) if g is not None),
                "origem": getattr(i, "origin", None),
                "peso": prog._peso_do_item(i),
                "dano": float(getattr(i, "damage_bonus", 0) or 0),
            }
            for p, i in equip.items()
        },
        "gemas_na_bolsa": len(h.gems),
        "ouro": h.coins,
        "nivel": h.get_level(),
        "passivas": [getattr(p, "effect_type", "?") for p in h.passives],
        "skills": [getattr(s, "id", s.name) for s in h.skills.values()],
        "ledger": {k: v for k, v in h.ledger.items() if isinstance(v, (int, float))},
    }
    melhor_fora = {}
    for it in h.inventory:
        if getattr(it, "consumable", False):
            continue
        cat = str(getattr(it, "slot", "?"))
        posicoes = h.available_positions_for(it)
        if not posicoes:
            continue
        classes = getattr(it, "classes", None)
        if classes and h.get_classname() not in classes:
            continue
        ocup = [h.equipment.get(p) for p in posicoes]
        pior = 0.0 if any(o is None for o in ocup) else min(prog._peso_do_item(o) for o in ocup)
        ganho = prog._peso_do_item(it) - pior
        if ganho > 0 and ganho > melhor_fora.get(cat, 0):
            melhor_fora[cat] = ganho
    out["melhor_na_mochila_que_o_pior_equipado"] = melhor_fora
    armas = [i for i in equip.values() if str(getattr(i, "slot", "")) == "Weapon"]
    out["arma_pct_equipada"] = sum(float(getattr(i, "damage_bonus", 0) or 0) for i in armas)
    out["pocoes_restantes"] = dict(
        collections.Counter(
            str(i.effect_type) for i in h.inventory if getattr(i, "consumable", False)
        )
    )
    out["starter_ainda_equipado"] = any(
        getattr(i, "origin", None) == "starter" for i in equip.values()
    )
    out["socket_vazio_equipado"] = sum(
        sum(1 for g in it.gems if g is None) for it in forge.socketable(h)
    )
    return out


# --- o executor: o protocolo histórico de progressão, com as sondas ---------

# O coletor histórico é a régua. Ele é CARREGADO, não copiado: o registro de cada
# run sai do mesmo código que produziu a baseline publicada.
COLETOR = pathlib.Path(RAIZ) / "baselines" / "progression" / "d3105edc" / "run_auditoria.py"
CAMPOS_VOLATEIS = ("segundos",)


def _coletor():
    import importlib.util

    spec = importlib.util.spec_from_file_location("coletor_d3105edc", COLETOR)
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def uma_run(tarefa: tuple[str, str, int, int]) -> dict:
    """Uma run do protocolo histórico, com as sondas instaladas no processo."""
    global C
    instalar()
    C = _novo()
    registro = _coletor().uma_run(tarefa)
    bot = C["bot"]
    registro["cobertura"] = {
        "n": dict(C["n"]),
        "listas": {k: v for k, v in C["listas"].items() if k != "skills_disponiveis"},
        "skills_disponiveis": dict(collections.Counter(C["listas"].get("skills_disponiveis", []))),
        "starter": C.get("starter"),
        "final": fotografia_final(bot) if bot is not None else None,
    }
    C = None
    return registro


def rodar(saida: pathlib.Path, workers: int, classes, seeds, teto: int) -> None:
    coletor = _coletor()
    classes = classes or coletor.CLASSES
    seeds = seeds or coletor.SEEDS
    teto = teto or coletor.TETO
    tarefas = [(RAIZ, c, s, teto) for c in classes for s in seeds]
    # `spawn` e um processo por run, como o coletor histórico: nenhum estado de
    # uma run (nem o gerador global) vaza para a seguinte.
    with mp.get_context("spawn").Pool(workers, maxtasksperchild=1) as pool:
        with saida.open("w", encoding="utf-8") as f:
            for i, registro in enumerate(pool.imap(uma_run, tarefas), 1):
                f.write(json.dumps(registro, ensure_ascii=False, default=str) + "\n")
                f.flush()
                print(
                    f"[{i}/{len(tarefas)}] {registro['classe']} seed {registro['seed']} "
                    f"-> {registro['desfecho']} andar {registro['andar']}",
                    flush=True,
                )


def conferir(medido: pathlib.Path, referencia: pathlib.Path) -> int:
    """Compara os campos do coletor histórico, run a run. 0 se idênticos."""

    def chave(r):
        return (r["classe"], r["seed"])

    def ler(caminho):
        linhas = caminho.read_text(encoding="utf-8").splitlines()
        return {chave(r): r for r in (json.loads(x) for x in linhas if x.strip())}

    a, b = ler(medido), ler(referencia)
    # Run medida sem par na referência é divergência; run da referência que não
    # foi medida (um smoke por subconjunto de seeds) só é informada.
    divergentes = [(k, "sem referência") for k in sorted(set(a) - set(b))]
    for k in sorted(set(a) & set(b)):
        ra = {c: v for c, v in a[k].items() if c not in CAMPOS_VOLATEIS and c != "cobertura"}
        rb = {c: v for c, v in b[k].items() if c not in CAMPOS_VOLATEIS and c != "cobertura"}
        if ra != rb:
            campos = sorted(c for c in set(ra) | set(rb) if ra.get(c) != rb.get(c))
            divergentes.append((k, campos))
    print(
        f"runs medidas {len(a)}, de referência {len(b)}, "
        f"não medidas {len(set(b) - set(a))}, divergentes {len(divergentes)}"
    )
    for k, campos in divergentes[:20]:
        print(f"  {k}: {campos}")
    return 1 if divergentes else 0


def _intervalo(texto: str | None):
    if not texto:
        return None
    ini, _, fim = texto.partition("-")
    return range(int(ini), int(fim or ini) + 1)


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    p = sub.add_parser("rodar")
    p.add_argument("--saida", type=pathlib.Path, required=True)
    p.add_argument("--workers", type=int, default=os.cpu_count() or 1)
    p.add_argument("--classes", nargs="*")
    p.add_argument("--seeds", help="intervalo, ex.: 1-20")
    p.add_argument("--teto", type=int, default=0)
    p = sub.add_parser("conferir")
    p.add_argument("medido", type=pathlib.Path)
    p.add_argument("referencia", type=pathlib.Path)
    args = parser.parse_args()
    if args.comando == "rodar":
        rodar(args.saida, args.workers, args.classes, _intervalo(args.seeds), args.teto)
        return 0
    return conferir(args.medido, args.referencia)


if __name__ == "__main__":
    sys.exit(main())
