"""BASELINE OFICIAL: 1.000 seeds x 3 classes, antes do Balanceamento Global.

Nao altera NADA. Envolve o BotPadrao em quatro pontos de escuta, todos passivos:

    _decidir_no_mapa       a matriz build x runway (telemetria que ja existia)
    _escolher_do_nivel     o que o nivel OFERECEU e o que foi ESCOLHIDO
    _decidir_no_combate    qual skill o cerebro escolheu neste turno
    Observador             o que a skill escolhida efetivamente FEZ

Nenhum dos quatro consome sorteio. O unico cuidado com RNG e nao reinvocar o
picker para descobrir a escolha: a escolha e lida por DIFERENCA do estado do
heroi antes e depois da chamada original.

`overall_power` so aparece quando ja foi naturalmente medido. Duas fontes, ambas
gratuitas: o `poder_relativo` que o portao de extracao pagou durante a run, e o
cache de `sim.arena` consultado no fim -- se a build final ja estiver medida, o
numero e uma leitura de dicionario; se nao estiver, o campo vem `None`. Nenhuma
medicao e forcada.

Escreve JSONL incremental: se o processo morrer, o que ja foi medido sobrevive.
"""

import argparse
import contextlib
import io
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.content import extraction  # noqa: E402
from src.shared import combat_topics as T  # noqa: E402
from src.sim import arena  # noqa: E402
from src.sim.bot import decidir_no_mapa  # noqa: E402
from src.sim.bot.decision import Need  # noqa: E402
from src.sim.bot.evaluators import (  # noqa: E402
    _banda_da_build,
    _estado_do_runway,
    _runway_em_andares,
)
from tools import bot_adapter as adapter  # noqa: E402
from tools.arena_alvo import PODER_ESPERADO  # noqa: E402
from tools.bot_padrao import BotPadrao, Observador  # noqa: E402

CLASSES = ("warrior", "mage", "rogue")


class ObservadorEspiao(Observador):
    """O Observador de sempre, mais um livro-caixa por SKILL.

    O barramento publica `COMBAT_SKILL_OUTCOME` com o RESULTADO, nao com o nome
    da skill: para `damage` o nome viaja dentro do golpe, mas para `heal` e
    `status` nao viaja nenhum. O nome vem, entao, de quem escolheu -- o proprio
    bot, um instante antes, no mesmo turno. Nao ha ambiguidade: entre a escolha e
    o resultado nao existe outra skill do heroi.
    """

    def __init__(self, heroi_nome: str) -> None:
        super().__init__(heroi_nome)
        self.skill_atual: str | None = None
        self.usos: Counter = Counter()
        self.dano_por_skill: Counter = Counter()
        self.mp_por_skill: Counter = Counter()
        self.cura_por_skill: Counter = Counter()
        self.status_ok: Counter = Counter()
        self.status_falhou: Counter = Counter()

    def __call__(self, topic: str, evento) -> None:
        super().__call__(topic, evento)
        if topic != T.COMBAT_SKILL_OUTCOME:
            return
        payload = getattr(evento, "payload", {}) or {}
        if self._nome(payload.get("caster")) != self.heroi:
            return
        nome = self.skill_atual
        if nome is None:
            return
        res = payload.get("result")
        self.usos[nome] += 1
        self.mp_por_skill[nome] += int(getattr(res, "mp_spent", 0) or 0)
        golpe = getattr(res, "strike", None)
        if golpe is not None and not getattr(golpe, "was_evaded", False):
            self.dano_por_skill[nome] += int(getattr(golpe, "damage", 0) or 0)
        cura = int(getattr(res, "heal_amount", 0) or 0)
        if cura:
            self.cura_por_skill[nome] += cura
        if getattr(res, "kind", "") == "status":
            if getattr(res, "status_success", False):
                self.status_ok[nome] += 1
            else:
                self.status_falhou[nome] += 1


class Espiao(BotPadrao):
    def __init__(self, classe, seed, max_andar=20):
        super().__init__(classe, seed, max_andar)
        # Troca o ouvinte por um que tambem conta skill. `publish=self.observador`
        # e resolvido na hora da chamada, entao a troca aqui basta.
        self.observador = ObservadorEspiao(self.hero.get_nick_name())
        self.avaliacoes = []
        self.ofertas_passiva = []  # [{nivel, oferecidas, escolhida}]
        self.ofertas_skill = []  # [{nivel, oferecidas, escolhida, slot_trocado}]

    # -- escuta 1: a decisao de extrair ------------------------------------

    def _decidir_no_mapa(self):
        mapa, prog = adapter.estado_do_mapa(self)
        opcoes, destinos = adapter.acoes_do_mapa(self, mapa, prog)
        decisao = decidir_no_mapa(mapa, prog, opcoes)
        if any(o.family == "extrair" for o in opcoes):
            sc = next(s for s in decisao.scores if s.action_id == "extrair")
            runway = _runway_em_andares(mapa, prog)
            poder = prog.poder_relativo
            self.avaliacoes.append(
                dict(
                    andar=self.andar,
                    poder=poder,
                    banda=_banda_da_build(poder) if poder > 0 else "NAO_MEDIDO",
                    runway=runway,
                    estado=_estado_do_runway(runway) if runway is not None else "SEM_EVIDENCIA",
                    preservou=sc.need is Need.PRESERVAR,
                    venceu=decisao.action_id == "extrair",
                    lutas_ate_e=mapa.lutas_ate_extracao,
                    hp_frac=prog.hp_frac,
                    nivel=prog.nivel,
                )
            )
        return decisao, destinos.get(decisao.action_id)

    # -- escuta 2: a oferta de nivel ---------------------------------------

    def _escolher_do_nivel(self, jogador, oferta) -> None:
        passivas_antes = Counter(_nome_da_carta(p) for p in jogador.passives)
        skills_antes = {sid: _nome_da_carta(s) for sid, s in jogador.skills.items()}

        super()._escolher_do_nivel(jogador, oferta)

        passivas_depois = Counter(_nome_da_carta(p) for p in jogador.passives)
        nova_passiva = list((passivas_depois - passivas_antes).elements())
        self.ofertas_passiva.append(
            dict(
                nivel=oferta.level,
                oferecidas=[_nome_da_carta(p) for p in oferta.passives],
                escolhida=nova_passiva[0] if nova_passiva else None,
            )
        )

        if not oferta.tem_skill:
            return
        skills_depois = {sid: _nome_da_carta(s) for sid, s in jogador.skills.items()}
        entrou = [n for sid, n in skills_depois.items() if skills_antes.get(sid) != n]
        saiu = [n for sid, n in skills_antes.items() if skills_depois.get(sid) != n]
        self.ofertas_skill.append(
            dict(
                nivel=oferta.level,
                oferecidas=[_nome_da_carta(s) for s in oferta.skills],
                escolhida=entrou[0] if entrou else None,
                substituiu=saiu[0] if saiu else None,
            )
        )

    # -- escuta 3: a skill do turno ----------------------------------------

    def _decidir_no_combate(self, heroi, monstros, turno: int):
        acao = super()._decidir_no_combate(heroi, monstros, turno)
        skill = getattr(acao, "skill", None)
        self.observador.skill_atual = _nome_da_carta(skill) if skill is not None else None
        return acao


def _nome_da_carta(carta) -> str | None:
    if carta is None:
        return None
    nome = getattr(carta, "name", None)
    if nome is None:
        nome = getattr(carta, "display_name", None)
    return str(nome) if nome is not None else str(carta)


# -- retrato da build final -----------------------------------------------


def _peca(item) -> dict | None:
    if item is None:
        return None
    return dict(
        nome=str(item.name),
        raridade=str(getattr(item, "rarity", "?")),
        mais_n=int(getattr(item, "enhancement_level", 0) or 0),
        sockets=int(getattr(item, "socket_count", 0) or 0),
        # `gems` tem UM lugar por socket, e o lugar vazio e `None`. Filtrar aqui
        # e a diferenca entre "tem socket" e "tem gema cravada".
        gemas=[
            str(getattr(g, "display_name", g))
            for g in (getattr(item, "gems", None) or [])
            if g is not None
        ],
        encantos=[
            f"{getattr(e, 'effect', '?')}={getattr(e, 'value', '?')}"
            for e in (getattr(item, "enchantments", None) or [])
        ],
        dano=int(getattr(item, "damage_bonus", 0) or 0),
        defesa=int(getattr(item, "defense_bonus", 0) or 0),
    )


def _build_final(hero) -> dict:
    equip = {slot: _peca(item) for slot, item in hero.equipment.items()}
    pocoes = Counter()
    outros_consumiveis = Counter()
    for i in hero.inventory:
        if not getattr(i, "consumable", False):
            continue
        if getattr(i, "is_potion", False):
            pocoes[str(i.name)] += 1
        else:
            outros_consumiveis[str(i.name)] += 1
    return dict(
        nivel=hero.get_level(),
        xp=int(getattr(hero, "xp_points", 0) or 0),
        hp_max=int(hero.base_hp),
        mp_max=int(hero.base_mp),
        st=int(hero.get_st()),
        mg=int(hero.get_mg()),
        ag=int(hero.get_ag()),
        df=int(hero.get_df()),
        dano_medio=float(hero.get_avg_damage()),
        equip_percent={
            k: float(hero.equipment_percent(k)) for k in ("hp", "mp", "st", "mg", "ag", "df")
        },
        arma_percent=float(hero.weapon_percent()),
        skills=[_nome_da_carta(s) for s in hero.skills.values()],
        passivas=sorted(_nome_da_carta(p) for p in hero.passives),
        equipamento=equip,
        pecas_equipadas=sum(1 for v in equip.values() if v),
        mais_n_total=sum(v["mais_n"] for v in equip.values() if v),
        gemas_cravadas=sum(len(v["gemas"]) for v in equip.values() if v),
        encantos_totais=sum(len(v["encantos"]) for v in equip.values() if v),
        sockets_totais=sum(v["sockets"] for v in equip.values() if v),
        ouro=int(hero.coins),
        pocoes=dict(pocoes),
        outros_consumiveis=dict(outros_consumiveis),
        itens_na_mochila=len(hero.inventory),
        chaves=extraction.keys_of(hero),
    )


def _poder_do_cache(hero) -> float | None:
    """`overall_power` da build final SE ela ja estiver no cache. Nunca mede.

    A chave e montada exatamente como `arena.overall_power` monta a dela. Se
    faltar, devolve `None` -- forcar a bisseccao aqui seria pagar centenas de
    duelos por run so para completar uma coluna do relatorio.
    """
    try:
        proto = arena._normalizado(hero)
        chave = (
            arena._assinatura_do_clone(proto),
            arena.ARENA_DUELS_PER_PROBE,
            arena.ARENA_MEASURE_SEED,
        )
        leitura = arena._cache.get(chave)
    except Exception:  # noqa: BLE001 - coluna opcional nunca derruba a run
        return None
    return leitura.nivel_equivalente if leitura is not None else None


# -- uma run ---------------------------------------------------------------


def uma_run(classe, seed):
    bot = Espiao(classe, seed, 20)
    with contextlib.redirect_stdout(io.StringIO()):
        try:
            bot.jogar()
        except Exception as e:  # noqa: BLE001 - a run que estoura vira dado, nao silencio
            bot.fim = f"ERRO {type(e).__name__}: {e}"

    fim = bot.fim
    desfecho = fim.split(" no andar ")[0]
    andar_final = bot.andar
    hero = bot.hero
    obs = bot.observador

    por_andar = {}
    for a in bot.avaliacoes:
        por_andar.setdefault(a["andar"], []).append(a)

    oportunidades = []
    for andar, avs in sorted(por_andar.items()):
        primeira, ultima = avs[0], avs[-1]
        vencedora = next((a for a in avs if a["venceu"]), None)
        runways = [a["runway"] for a in avs if a["runway"] is not None]
        poderes = [a["poder"] for a in avs if a["poder"] > 0]
        if desfecho == "EXTRAIU" and andar == andar_final:
            dese = "extraiu_aqui"
        elif desfecho == "MORREU" and andar == andar_final:
            dese = "morreu_no_andar"
        else:
            dese = "abandonou_andar"
        oportunidades.append(
            dict(
                tipo="oportunidade",
                seed=seed,
                classe=classe,
                andar=andar,
                avaliacoes=len(avs),
                banda_ini=primeira["banda"],
                poder_ini=primeira["poder"],
                runway_ini=primeira["runway"],
                estado_ini=primeira["estado"],
                decisao_ini="EXTRAI" if primeira["preservou"] else "CONTINUA",
                banda_fim=ultima["banda"],
                estado_fim=ultima["estado"],
                runway_min=min(runways) if runways else None,
                runway_max=max(runways) if runways else None,
                poder_min=min(poderes) if poderes else None,
                poder_max=max(poderes) if poderes else None,
                desfecho=dese,
                nivel=primeira["nivel"],
                hp_frac_ini=primeira["hp_frac"],
                poder_na_extracao=vencedora["poder"] if vencedora else None,
                runway_na_extracao=vencedora["runway"] if vencedora else None,
                banda_na_extracao=vencedora["banda"] if vencedora else None,
                estado_na_extracao=vencedora["estado"] if vencedora else None,
            )
        )

    # O poder medido NATURALMENTE: o ultimo que o portao pagou nesta run.
    medidos = [(a["andar"], a["poder"]) for a in bot.avaliacoes if a["poder"] > 0]
    poder_rel_ultimo = medidos[-1][1] if medidos else None
    poder_abs_cache = _poder_do_cache(hero)

    linha_run = dict(
        tipo="run",
        seed=seed,
        classe=classe,
        desfecho=desfecho,
        andar_final=andar_final,
        chegou_ao_20=andar_final >= 20,
        oportunidades=len(oportunidades),
        avaliacoes=len(bot.avaliacoes),
        # --- progresso e economia
        combates=bot.combates_na_run,
        fugas_na_ficha=bot.fugas_na_run,
        andares_concluidos=bot.andares_concluidos,
        pocoes_bebidas=bot.pocoes_bebidas,
        servicos=dict(bot.servicos),
        acoes_de_combate=dict(bot.acoes),
        mp_gasto=bot.mp_gasto,
        mp_disponivel=bot.mp_disponivel,
        dano_dado_total=obs.dado_total,
        dano_recebido_total=obs.recebido_total,
        crit_dados=obs.crit_dados,
        crit_recebidos=obs.crit_recebidos,
        erros_meus=obs.erros_meus,
        erros_deles=obs.erros_deles,
        egide_absorvida=obs.absorvido_egide,
        dot_sofrido=dict(obs.dot_sofrido),
        dano_recebido_frac=bot.dano_recebido_frac,
        # --- poder, so quando medido de graca
        poder_relativo_ultimo=poder_rel_ultimo,
        poder_relativo_max=max((p for _, p in medidos), default=None),
        andar_do_ultimo_poder=medidos[-1][0] if medidos else None,
        poder_absoluto_ultimo=(
            poder_rel_ultimo * PODER_ESPERADO if poder_rel_ultimo is not None else None
        ),
        poder_absoluto_build_final=poder_abs_cache,
        # --- a build
        build=_build_final(hero),
        # --- skills em uso
        skill_usos=dict(obs.usos),
        skill_dano=dict(obs.dano_por_skill),
        skill_mp=dict(obs.mp_por_skill),
        skill_cura=dict(obs.cura_por_skill),
        skill_status_ok=dict(obs.status_ok),
        skill_status_falhou=dict(obs.status_falhou),
        # --- ofertas de nivel
        ofertas_passiva=bot.ofertas_passiva,
        ofertas_skill=bot.ofertas_skill,
        # --- o combate que encerrou
        fatal=bot.fatal,
    )

    linhas = [linha_run]
    linhas += oportunidades
    for a in bot.avaliacoes:
        linhas.append(dict(tipo="avaliacao", seed=seed, classe=classe, **a))
    return linhas


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inicio", type=int, required=True)
    ap.add_argument("--fim", type=int, required=True)
    ap.add_argument("--saida", required=True)
    args = ap.parse_args()

    t0 = time.time()
    with open(args.saida, "w", buffering=1) as f:
        for seed in range(args.inicio, args.fim):
            for classe in CLASSES:
                for linha in uma_run(classe, seed):
                    f.write(json.dumps(linha) + "\n")
            print(f"seed {seed} ok ({time.time() - t0:.0f}s)", flush=True)
    print(f"FIM {args.inicio}-{args.fim} em {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
