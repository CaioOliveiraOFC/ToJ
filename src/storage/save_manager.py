from __future__ import annotations

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

from src.content.gems import gem_from_dict, gem_to_dict
from src.content.passives import get_passive_by_id
from src.content.skills_loader import get_skill_by_id

# Save antigo guardava uma posição por categoria ("Weapon", "Ring"); o personagem
# agora tem duas de cada. A peça salva entra na primeira, e `Weapon2`, `Ring2` e
# `Accessory` nascem vazios. Mapear na leitura, em vez de migrar o arquivo, mantém
# saves de versões anteriores carregáveis sem tocar em nada em disco.
POSICAO_LEGADA = {"Weapon": "Weapon1", "Ring": "Ring1"}

if TYPE_CHECKING:
    from src.entities.heroes import Player

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "saves")
SAVE_FILE = "savegame.json"
TROPHY_FILE = "trophies.json"
SLOT_COUNT = 10

# Type aliases
ItemRegistry = dict[str, object]
PlayerFactory = type["Player"]
SaveResult = dict[str, bool | str]


def _ensure_save_dir() -> None:
    """Garante que o diretório de saves existe."""
    if not os.path.exists(SAVE_DIR):
        os.makedirs(SAVE_DIR)


def get_slot_file(slot: int) -> str:
    """Retorna o nome do arquivo para o slot."""
    return os.path.join(SAVE_DIR, f"slot_{slot}.json")


def list_slots() -> list[dict]:
    """Lista todos os slots, indicando quais estão ocupados."""
    _ensure_save_dir()
    slots = []
    for i in range(1, SLOT_COUNT + 1):
        filepath = get_slot_file(i)
        if os.path.exists(filepath):
            try:
                with open(filepath, "r") as f:
                    data = json.load(f)
                    slots.append(
                        {
                            "slot": i,
                            "occupied": True,
                            "name": data.get("player_name", "?"),
                            "class": data.get("player_class", "?"),
                            "level": data.get("level", 0),
                            "floor": data.get("dungeon_level", 0),
                        }
                    )
            except Exception:
                slots.append({"slot": i, "occupied": False})
        else:
            slots.append({"slot": i, "occupied": False})
    return slots


def _serializar(item) -> dict | None:
    """O exemplar em disco: a definição pelo nome, mais o estado dele.

    Só o nome não basta desde que existe `+N`: duas Espadas de Ferro podem estar
    +3 e +17, e o nome é a mesma chave para as duas. Campos com valor default
    não são gravados, então um save sem aprimoramento nenhum continua do mesmo
    tamanho de antes.
    """
    if item is None:
        return None
    registro: dict = {"name": item.name}
    rank = int(getattr(item, "enhancement_level", 0) or 0)
    if rank:
        registro["enhancement_level"] = rank
    gemas = list(getattr(item, "gems", ()) or ())
    if any(g is not None for g in gemas):
        registro["gems"] = [gem_to_dict(g) for g in gemas]
    return registro


def _desserializar(registro, item_registry):
    """Reconstrói o exemplar. Aceita o formato antigo (só o nome).

    Save anterior ao `+N` guardava strings; elas viram exemplares +0, sem
    migração de arquivo. Sempre devolve uma INSTÂNCIA, nunca a definição do
    catálogo: dois exemplares carregados do mesmo nome precisam ser objetos
    diferentes, ou aprimorar um aprimoraria o outro.
    """
    if not registro:
        return None
    nome = registro if isinstance(registro, str) else registro.get("name")
    definicao = item_registry.get(nome)
    if definicao is None:
        return None
    item = definicao.instance()
    if isinstance(registro, dict):
        item.enhancement_level = max(0, int(registro.get("enhancement_level", 0) or 0))
        gemas = registro.get("gems")
        if gemas is not None:
            # A contagem de sockets vem da definição; o save só diz o que está
            # encaixado. Se o catálogo mudar o item para menos sockets, a pedra
            # a mais some do encaixe — mas o excedente volta para a bolsa, em
            # `load_game`, em vez de evaporar.
            for i, dados in enumerate(gemas[: item.socket_count]):
                item.gems[i] = gem_from_dict(dados)
            item.gems_excedentes = [
                g for g in (gem_from_dict(d) for d in gemas[item.socket_count :]) if g
            ]
    return item


def save_game(
    player: "Player", dungeon_level: int, map_state: dict | None = None, slot: int = 1
) -> SaveResult:
    """Salva o estado atual do jogo num ficheiro JSON."""
    inventory_names = [_serializar(item) for item in player.inventory]
    equipment_names = {slot: _serializar(item) for slot, item in player.equipment.items()}
    passive_ids = [p.id for p in player.passives]
    skills_data = {str(k): v.id for k, v in player.skills.items()}

    save_data = {
        "player_class": player.get_classname(),
        "player_name": player.get_nick_name(),
        "level": player.get_level(),
        "xp": player.xp_points,
        # HP e MP precisam ser gravados. Sem eles o herói era reconstruído no
        # nível salvo com os recursos no máximo, e extrair virava cura total
        # gratuita — a jogada ótima passava a ser sair e voltar a cada aperto.
        "hp": player.get_hp(),
        "mp": player.get_mp(),
        "coins": player.coins,
        # Livro-caixa e trava de juros. A trava precisa ser salva: sem ela,
        # carregar um save feito depois de concluir o andar pagaria os juros
        # daquele andar de novo, e salvar/carregar em laço imprimiria moeda.
        "ledger": dict(getattr(player, "ledger", {})),
        "last_interest_floor": int(getattr(player, "last_interest_floor", 0)),
        "gems": [gem_to_dict(g) for g in getattr(player, "gems", ())],
        "inventory": inventory_names,
        "equipment": equipment_names,
        "passives": passive_ids,
        "skills": skills_data,
        "initial_skills_learned": player.initial_skills_learned,
        "active_buffs": player.active_buffs,
        "active_effects": player.active_effects,
        "dungeon_level": dungeon_level,
        "map_state": map_state,
    }

    try:
        _ensure_save_dir()
        filepath = get_slot_file(slot)
        with open(filepath, "w") as f:
            json.dump(save_data, f, indent=4)
        return {"success": True, "message": f"Jogo salvo no slot {slot}!"}
    except Exception as e:
        return {"success": False, "message": f"Ocorreu um erro ao salvar: {e}"}


def load_game(
    item_registry: ItemRegistry, player_factory: dict[str, PlayerFactory], slot: int = 1
) -> tuple["Player" | None, int | None, dict | None]:
    """Carrega o estado do jogo a partir de um ficheiro JSON."""
    filepath = get_slot_file(slot)
    if not os.path.exists(filepath):
        return None, None, None

    try:
        with open(filepath, "r") as f:
            save_data = json.load(f)

        player_class_name = save_data["player_class"]
        player_name = save_data["player_name"]

        player_class = player_factory.get(player_class_name)
        if not player_class:
            return None, None, None

        player = player_class(player_name)

        # Carrega skills do novo formato (por id)
        skills_loaded = True
        skills_data = save_data.get("skills", {})
        if skills_data:
            for key_str, skill_id in skills_data.items():
                skill = get_skill_by_id(skill_id)
                if skill:
                    player.skills[int(key_str)] = skill
                else:
                    skills_loaded = False
        else:
            skills_loaded = False

        if not skills_loaded:
            pass  # Aviso: Save incompatível - skills não puderam ser carregadas.

        player.initial_skills_learned = save_data.get("initial_skills_learned", len(player.skills))

        # Define o nível (isso vai disparar aprendizado de skills iniciais)
        saved_level = save_data["level"]
        player.set_level(saved_level)

        # Restaurar skills salvas (set_level limpa as skills)
        if skills_data:
            player.skills.clear()
            for key_str, skill_id in skills_data.items():
                skill = get_skill_by_id(skill_id)
                if skill:
                    player.skills[int(key_str)] = skill

        player.xp_points = save_data["xp"]
        player.coins = save_data["coins"]
        # `.get` com o padrão do herói: saves anteriores a esta economia não têm
        # os campos, e um KeyError aqui torna o save velho ilegível.
        player.ledger.update(save_data.get("ledger") or {})
        player.last_interest_floor = int(save_data.get("last_interest_floor", 0))

        # Reconstrói o inventário (pula itens que não existem mais no registro)
        player.gems = [g for g in (gem_from_dict(d) for d in save_data.get("gems", [])) if g]

        player.inventory = []
        for registro in save_data["inventory"]:
            item = _desserializar(registro, item_registry)
            if item:
                player.inventory.append(item)

        for slot, registro in save_data["equipment"].items():
            if registro:
                item_to_equip = _desserializar(registro, item_registry)
                if item_to_equip is None:
                    continue
                posicao = POSICAO_LEGADA.get(slot, slot)
                player.equip(item_to_equip, posicao if posicao in player.equipment else None)
                # `equip` pode recusar: classe errada, ou uma posição que este
                # personagem não tem (um save com arma secundária carregado por
                # quem não empunha duas). A peça recusada volta para a mochila.
                # Antes ela era retirada do inventário ANTES da tentativa e
                # sumia do jogo — o save perdia o item em silêncio.
                if (
                    item_to_equip not in player.equipment.values()
                    and item_to_equip not in player.inventory
                ):
                    player.inventory.append(item_to_equip)
                player.gems.extend(getattr(item_to_equip, "gems_excedentes", ()))

        player.active_buffs = save_data.get("active_buffs", {})
        player.active_effects = save_data.get("active_effects", {})

        passive_ids = save_data.get("passives", [])
        if passive_ids:
            for pid in passive_ids:
                passive = get_passive_by_id(pid)
                if passive:
                    player.add_passive_load(passive)

        # Restaurar por último: passivas e equipamento alteram `base_hp`/`base_mp`,
        # então o teto só é conhecido depois deles. Save antigo (sem os campos)
        # mantém o comportamento anterior e entra com os recursos cheios.
        hp_salvo = save_data.get("hp")
        if hp_salvo is not None:
            player._hp = max(1, min(int(hp_salvo), player.base_hp))
        mp_salvo = save_data.get("mp")
        if mp_salvo is not None:
            player._mp = max(0, min(int(mp_salvo), player.base_mp))

        dungeon_level = save_data["dungeon_level"]
        map_state = save_data.get("map_state", None)

        return player, dungeon_level, map_state

    except Exception:
        return None, None, None


def check_save_file(slot: int = 1) -> bool:
    """Verifica se o ficheiro de save existe."""
    return os.path.exists(get_slot_file(slot))


def delete_save(slot: int) -> bool:
    """Deleta o save do slot especificado."""
    filepath = get_slot_file(slot)
    if os.path.exists(filepath):
        try:
            os.remove(filepath)
            return True
        except Exception:
            return False
    return False


def add_trophy(
    player_name: str,
    player_class: str,
    level: int,
    floor_reached: int,
    cause: str = "Derrotado",
    economy: dict | None = None,
) -> bool:
    """Adiciona uma entrada ao livro de troféus (personagens que morreram).

    `economy` é o livro-caixa da run. Permadeath: o ouro não vira banco nem
    passa para outro personagem — o que fica é o registro de para onde ele foi,
    que é o que permite olhar depois e perguntar se a economia ofereceu
    decisões ou só acumulou moeda.
    """
    _ensure_save_dir()
    filepath = os.path.join(SAVE_DIR, TROPHY_FILE)

    trophies = []
    if os.path.exists(filepath):
        try:
            with open(filepath, "r") as f:
                trophies = json.load(f)
        except Exception:
            trophies = []

    trophy = {
        "name": player_name,
        "class": player_class,
        "level": level,
        "floor": floor_reached,
        "cause": cause,
        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "economy": dict(economy or {}),
    }
    trophies.append(trophy)

    try:
        with open(filepath, "w") as f:
            json.dump(trophies, f, indent=4)
        return True
    except Exception:
        return False


def get_trophies() -> list[dict]:
    """Retorna a lista de troféus (personagens que morreram)."""
    _ensure_save_dir()
    filepath = os.path.join(SAVE_DIR, TROPHY_FILE)

    if not os.path.exists(filepath):
        return []

    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except Exception:
        return []
