"""Auditoria de cobertura PvE: sondas por wrapper, só neste processo.

Nada em `src/` ou `tools/` muda. Cada sonda envolve uma função real, chama a
original e só OBSERVA: não sorteia, não altera argumento nem retorno. A prova é
o determinismo: cada run reexecutada tem de reproduzir o registro do log real
(desfecho, andar, nível, combates, ações, serviços, ouro).

Uso:
    python sondas.py rodar <amostra.json> <saida.jsonl> [--trabalhadores N]
"""

from __future__ import annotations

import collections
import json
import pathlib
import multiprocessing as mp
import os
import sys
import time
import traceback

RAIZ = str(pathlib.Path(__file__).resolve().parents[3])
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


def instalar() -> None:
    """Instala as sondas. Chamado uma vez por processo trabalhador."""
    import tools.arena_copa_03_geracao as ger
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

    ITENS = {}
    try:
        from src.content.items import get_all_items

        for it in get_all_items().values():
            ITENS[str(getattr(it, "id", it.name))] = it
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
    orig_init = ger.BotExperimental.__init__

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

    ger.BotExperimental.__init__ = init

    orig_jogar = ger.BotExperimental.jogar

    def jogar(self):
        try:
            return orig_jogar(self)
        finally:
            if C is not None:
                C["encerrada"] = True

    ger.BotExperimental.jogar = jogar

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
        lista("op_na_run", {"andar": getattr(C["bot"], "andar", None) if C and C["bot"] else None,
                            "relativo": round(float(r.relativo), 4)})
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
                it = ITENS.get(o.action_id[5:])
                n(f"item_disponivel_turno:{getattr(it, 'effect_type', '?')}")
        if aid.startswith("skill:"):
            n(f"skill_heroi_escolhida:{aid[6:]}")
        if aid.startswith("item:"):
            it = ITENS.get(aid[5:])
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


def uma_run(tarefa: dict) -> dict:
    global C
    import tools.arena_copa_03_geracao as ger

    C = _novo()
    inicio = time.time()
    try:
        reg = ger.executar(
            tarefa["perfil"], tarefa["politica"], tarefa["tentativa"], tarefa["classe"], faixa=None
        )
        bot = C["bot"]
        foto = fotografia_final(bot) if bot is not None else None
    except Exception:  # noqa: BLE001
        C = None
        return {"tarefa": {k: v for k, v in tarefa.items() if k != "log"},
                "erro": traceback.format_exc(limit=10)}
    reg.pop("_snapshot", None)
    log = tarefa.get("log") or {}
    campos = ("seed", "desfecho", "andar", "nivel", "combates", "acoes", "servicos", "ouro_ganho",
              "pocoes_bebidas", "saidas_pagas", "saidas_nao_pagas")
    diverge = {c: (log.get(c), reg.get(c)) for c in campos if c in log and log.get(c) != reg.get(c)}
    if log.get("op") is not None and reg.get("op") is not None:
        if abs(float(log["op"]) - float(reg["op"])) > 1e-9:
            diverge["op"] = (log["op"], reg["op"])
    saida = {
        "tarefa": {k: v for k, v in tarefa.items() if k != "log"},
        "reproduziu": not diverge,
        "divergencias_do_log": diverge,
        "registro": {k: reg.get(k) for k in (
            "desfecho", "andar", "nivel", "combates", "acoes", "servicos", "pocoes_bebidas",
            "saidas_pagas", "saidas_nao_pagas", "ouro_ganho", "reserva_gasta", "extracao", "op",
            "fugas_na_ficha", "build",
        )},
        "n": dict(C["n"]),
        "listas": {k: v for k, v in C["listas"].items() if k != "skills_disponiveis"},
        "skills_disponiveis": dict(collections.Counter(C["listas"].get("skills_disponiveis", []))),
        "starter": C.get("starter"),
        "final": foto,
        "tempo_s": round(time.time() - inicio, 1),
    }
    C = None
    return saida


def rodar(amostra_path: str, saida_path: str, trabalhadores: int) -> None:
    tarefas = json.load(open(amostra_path))
    feitas = set()
    if os.path.exists(saida_path):
        for linha in open(saida_path):
            if linha.strip():
                try:
                    t = json.loads(linha)["tarefa"]
                    feitas.add((t["classe"], t["perfil"], t["politica"], t["tentativa"]))
                except Exception:  # noqa: BLE001
                    pass
    pend = [
        t for t in tarefas
        if (t["classe"], t["perfil"], t["politica"], t["tentativa"]) not in feitas
    ]
    print(f"{len(tarefas)} tarefas, {len(feitas)} feitas, {len(pend)} pendentes", flush=True)
    ctxmp = mp.get_context("fork")
    with ctxmp.Pool(trabalhadores, initializer=instalar, maxtasksperchild=8) as pool, open(
        saida_path, "a"
    ) as out:
        for i, r in enumerate(pool.imap_unordered(uma_run, pend), 1):
            out.write(json.dumps(r, ensure_ascii=False, default=str) + "\n")
            out.flush()
            t = r["tarefa"]
            reg = r.get("registro") or {}
            print(
                f"[{i}/{len(pend)}] {t['classe']} {t['perfil']} {t['politica']} k={t['tentativa']} "
                f"-> {reg.get('desfecho', 'ERRO')} andar={reg.get('andar')} "
                f"reproduziu={r.get('reproduziu')} {r.get('tempo_s')}s",
                flush=True,
            )


if __name__ == "__main__":
    if sys.argv[1] == "rodar":
        trab = (
            int(sys.argv[sys.argv.index("--trabalhadores") + 1])
            if "--trabalhadores" in sys.argv
            else 3
        )
        rodar(sys.argv[2], sys.argv[3], trab)
