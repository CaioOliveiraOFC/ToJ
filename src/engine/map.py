#!/usr/bin/env python3.10
"""Lógica de mapa, geração procedural e movimentação."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, NamedTuple

from src.content.factories.monsters import create_monster
from src.shared.constants import DEFAULT_WALL_PERCENTAGE, MAP_BORDER_OFFSET

if TYPE_CHECKING:
    pass


class EventTile(NamedTuple):
    """O jogador pisou numa casa de evento. Carrega o tipo sorteado.

    Um tipo próprio, e não uma string: `move_player` já devolve `"level_complete"`
    e um `Monster`, e um terceiro retorno em string acabaria comparado por
    engano com o primeiro.
    """

    event_type: str | None


def _um_monstro(enemy_obj: object):
    """Desembrulha o que o chamador passou e garante UM monstro.

    A lista existia para carregar o encontro composto. Ela ainda é aceita por
    compatibilidade, com exatamente um elemento dentro — e é aqui que uma lista
    maior morre, em vez de virar uma casa com grupo dentro.
    """
    if isinstance(enemy_obj, list):
        if len(enemy_obj) != 1:
            raise ValueError(
                f"Uma casa guarda UM monstro: recebi {len(enemy_obj)}. "
                "Cada inimigo do andar ocupa a própria casa."
            )
        return enemy_obj[0]
    return enemy_obj


def _monstro_de(dado: dict):
    """Reconstrói um monstro a partir do que o save guardou."""
    return create_monster(dado["nick_name"], dado["level"], dado.get("role", "bruiser"))


class MapOfGame:
    """
    Esta classe gere a criação, exibição e interação com o mapa do jogo,
    incluindo jogador, inimigos e a saída da masmorra.
    """

    def __init__(self, height: int, width: int):
        self.height = height
        self.width = width
        self.grid = []
        self.player_pos = {"y": 0, "x": 0}
        self.exit_pos = {"y": 0, "x": 0}
        self.enemies_pos = {}
        # O evento é uma CASA do mapa, e não um sorteio de fim de andar. Guardar
        # aqui, e não no jogador, é o que faz "já visitei este altar" ser estado
        # do andar: salvar no meio do andar preserva a casa, e voltar a ele
        # depois de gastar o evento não o traz de volta.
        self.event_pos: tuple[int, int] | None = None
        self.event_type: str | None = None

    def _get_random_empty_spot(self, avoid_enemies: bool = False) -> tuple[int, int]:
        """Uma posição de chão livre, sorteada.

        `avoid_enemies` existe porque monstro NÃO é marcado no grid — ele vive em
        `enemies_pos`. Sem a checagem, dois monstros do mesmo andar podiam cair
        na mesma casa e o dicionário engolia um deles em silêncio: o andar
        entregava sete inimigos onde o gerador tinha produzido oito. Cai
        exatamente sobre o invariante da rodada passada, o de que o andar tem os
        monstros que o gerador criou.
        """
        for _ in range(self.height * self.width * 4):
            y = random.randint(MAP_BORDER_OFFSET, self.height - 2)
            x = random.randint(MAP_BORDER_OFFSET, self.width - 2)
            if self.grid[y][x] != ".":
                continue
            if avoid_enemies and (y, x) in self.enemies_pos:
                continue
            return y, x
        # Mapa apertado demais para o sorteio: varre e pega a primeira livre, em
        # vez de rodar para sempre.
        livre = self._nearest_free_spot()
        if livre is None:
            raise RuntimeError("O mapa não tem casa livre para colocar mais nada.")
        return livre

    def generate_map(self, percent_of_walls: float = DEFAULT_WALL_PERCENTAGE) -> None:
        """Gera o mapa usando Random Walk garantindo conectividade."""
        self.grid = [["#" for _ in range(self.width)] for _ in range(self.height)]

        target_empty = int((self.width - 2) * (self.height - 2) * (1.0 - percent_of_walls))

        y = self.height // 2
        x = self.width // 2
        self.grid[y][x] = "."
        empty_count = 1

        while empty_count < target_empty:
            direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
            ny = y + direction[0]
            nx = x + direction[1]

            if (
                MAP_BORDER_OFFSET <= ny < self.height - 1
                and MAP_BORDER_OFFSET <= nx < self.width - 1
            ):
                y, x = ny, nx
                if self.grid[y][x] == "#":
                    self.grid[y][x] = "."
                    empty_count += 1

    def place_player(self) -> None:
        """Coloca o jogador em um local aleatório no mapa."""
        y, x = self._get_random_empty_spot()
        self.player_pos["y"], self.player_pos["x"] = y, x

    def place_exit(self) -> None:
        """Coloca a saída 'X' no piso vazio mais distante do jogador."""
        player_y, player_x = self.player_pos["y"], self.player_pos["x"]

        max_dist = -1
        best_pos = None

        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == ".":
                    dist = abs(y - player_y) + abs(x - player_x)
                    if dist > max_dist:
                        max_dist = dist
                        best_pos = (y, x)

        if best_pos:
            exit_y, exit_x = best_pos
            self.grid[exit_y][exit_x] = "X"
            self.exit_pos = {"y": exit_y, "x": exit_x}

    def place_enemy(self, enemy_obj: object) -> None:
        """Coloca UM inimigo numa casa livre do mapa.

        Uma casa, um monstro, uma batalha. O andar pode ter dez inimigos — eles
        ocupam dez casas, e encontrar o segundo significa outra batalha, não um
        inimigo a mais na primeira.

        Aceita uma lista de um elemento porque o chamador antigo entregava o
        encontro inteiro; mais de um é erro, e não uma casa com grupo dentro.
        """
        y, x = self._get_random_empty_spot(avoid_enemies=True)
        self.enemies_pos[(y, x)] = _um_monstro(enemy_obj)

    def place_event(self, event_type: str) -> tuple[int, int] | None:
        """Põe o evento numa casa livre. Devolve a posição, ou `None`.

        Um por andar, e ele não divide casa com ninguém: nem jogador, nem saída,
        nem monstro, nem outro evento. Sem casa livre, o andar simplesmente não
        tem evento — melhor que sobrescrever um inimigo em silêncio.
        """
        if not event_type:
            return None
        jogador = (self.player_pos["y"], self.player_pos["x"])
        saida = (self.exit_pos["y"], self.exit_pos["x"])
        for _ in range(self.height * self.width * 4):
            y, x = self._get_random_empty_spot(avoid_enemies=True)
            if (y, x) in (jogador, saida):
                continue
            self.event_pos = (y, x)
            self.event_type = str(event_type)
            return self.event_pos
        return None

    def take_event(self) -> str | None:
        """Consome o evento da casa e devolve o tipo. Uso único.

        Chamado quando o jogador PISA nela, e não quando ele termina a conversa:
        recusar o Altar, ignorar a Fonte ou sair do Mercador sem comprar também
        gastam a casa. A escolha foi feita, e entrar e sair da mesma casa não
        pode virar farm.
        """
        tipo, self.event_type, self.event_pos = self.event_type, None, None
        return tipo

    def draw_map(self) -> list[str]:
        """Gera representação pura do mapa como lista de strings para renderização pela UI.

        Retorna lista de strings onde cada string representa uma linha do mapa
        com caracteres puros (sem formatação visual). A UI (renderer/screens) é
        responsável por aplicar cores e estilos.
        """
        lines: list[str] = []
        for y, row in enumerate(self.grid):
            display_row: list[str] = []
            for x, tile in enumerate(row):
                char = tile
                if y == self.player_pos["y"] and x == self.player_pos["x"]:
                    char = "@"
                elif (y, x) in self.enemies_pos:
                    mob = self.enemies_pos[(y, x)]
                    char = "B" if getattr(mob, "is_boss", False) else "&"
                elif self.event_pos == (y, x):
                    char = "?"
                elif tile == "X":
                    char = "X"
                elif tile == "D":
                    char = "D"
                display_row.append(char)
            lines.append(" ".join(display_row))
        return lines

    def move_player(self, direction: str) -> str | object | None:
        """
        Move o jogador, verifica colisões e retorna o resultado da ação.
        Retorna: 'level_complete', um objeto Monstro, ou None.
        """
        py, px = self.player_pos["y"], self.player_pos["x"]
        ny, nx = py, px

        if direction == "w":
            ny -= 1
        elif direction == "s":
            ny += 1
        elif direction == "a":
            nx -= 1
        elif direction == "d":
            nx += 1

        # Verifica colisão com parede ou limite do mapa
        if ny < 0 or ny >= self.height or nx < 0 or nx >= self.width:
            return None
        if self.grid[ny][nx] == "#":
            return None
        # Permite que o jogador passe por cima de corpos mortos
        if self.grid[ny][nx] == "D":
            self.player_pos = {"y": ny, "x": nx}
            return None  # Não há colisão significativa, apenas move o jogador

        # Verifica se chegou na saída
        if ny == self.exit_pos["y"] and nx == self.exit_pos["x"]:
            return "level_complete"

        # Casa de evento: opcional, e só acontece se o jogador andar até ela.
        if self.event_pos == (ny, nx):
            self.player_pos = {"y": ny, "x": nx}
            return EventTile(self.take_event())

        # Verifica colisão com inimigo
        if (ny, nx) in self.enemies_pos:
            enemy_collided = self.enemies_pos.pop((ny, nx))
            self.grid[ny][nx] = "D"  # Marca a posição onde o inimigo morreu com um 'D'
            self.player_pos = {"y": ny, "x": nx}
            return enemy_collided

        # Move o jogador se o caminho estiver livre ('.')
        if self.grid[ny][nx] == ".":
            self.player_pos = {"y": ny, "x": nx}
        return None

    def get_map_state(self) -> dict:
        """Retorna um dicionário com o estado atual do mapa para salvamento."""
        # Serializar enemies_pos para salvar. (y, x) -> {nick_name, level}
        # Um objeto por casa, nunca um array: o array era a representação do
        # encontro em grupo, e gravá-lo de novo reabriria a porta.
        enemies_serializable = {
            f"{y},{x}": {
                "nick_name": mob.nick_name,
                "level": mob.level,
                "role": getattr(mob, "role", "bruiser"),
            }
            for (y, x), mob in self.enemies_pos.items()
        }

        return {
            "height": self.height,
            "width": self.width,
            "grid": self.grid,
            "player_pos": self.player_pos,
            "exit_pos": self.exit_pos,
            "enemies_pos": enemies_serializable,
            "event": (
                {"y": self.event_pos[0], "x": self.event_pos[1], "type": self.event_type}
                if self.event_pos is not None
                else None
            ),
        }

    def load_map_state(self, map_state: dict) -> None:
        """Carrega o estado do mapa a partir de um dicionário."""
        self.height = map_state["height"]
        self.width = map_state["width"]
        self.grid = map_state["grid"]
        self.player_pos = map_state["player_pos"]
        self.exit_pos = map_state["exit_pos"]

        # Evento não visitado volta onde estava; consumido não volta, porque o
        # save nem chegou a gravá-lo. Save antigo, sem a chave, é andar sem
        # evento — que é exatamente o que ele era.
        evento = map_state.get("event")
        if isinstance(evento, dict) and evento.get("type"):
            self.event_pos = (int(evento["y"]), int(evento["x"]))
            self.event_type = str(evento["type"])
        else:
            self.event_pos, self.event_type = None, None

        self.enemies_pos = {}
        # Saves da fase de grupos guardam um ARRAY por casa. O primeiro monstro
        # fica onde estava e os demais ganham casa própria — ninguém é apagado,
        # porque perder inimigo de um save salvo é perder progresso do jogador.
        excedentes: list[dict] = []
        for pos_str, entry in map_state["enemies_pos"].items():
            y, x = map(int, pos_str.split(","))
            grupo = entry if isinstance(entry, list) else [entry]
            if not grupo:
                continue
            self.enemies_pos[(y, x)] = _monstro_de(grupo[0])
            excedentes.extend(grupo[1:])

        for dado in excedentes:
            destino = self._nearest_free_spot()
            if destino is None:
                break
            self.enemies_pos[destino] = _monstro_de(dado)

    def _nearest_free_spot(self) -> tuple[int, int] | None:
        """A primeira casa de chão livre, numa varredura estável.

        Determinística de propósito: carregar o mesmo save duas vezes tem de
        colocar os monstros nas mesmas casas, ou o save deixa de ser o save.
        """
        jogador = (self.player_pos["y"], self.player_pos["x"])
        saida = (self.exit_pos["y"], self.exit_pos["x"]) if self.exit_pos else None
        for y, linha in enumerate(self.grid):
            for x, tile in enumerate(linha):
                if tile != ".":
                    continue
                if (y, x) in self.enemies_pos or (y, x) == jogador or (y, x) == saida:
                    continue
                return (y, x)
        return None
