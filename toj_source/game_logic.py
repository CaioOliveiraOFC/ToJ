#!/usr/bin/env python3

import random
from .classes import Warrior, Mage, Rogue, Monster, show_status
from .interactions import fight, menu, screen_clear
from time import sleep

def create_player():
    """
    Função para criar o personagem do jogador.
    """
    while True:
        player_c_selection = input("Por favor, selecione uma classe: [guerreiro, mago, ladino] ").lower()
        if player_c_selection in ["guerreiro", "mago", "ladino"]:
            break
        print("Classe inválida. Por favor, tente novamente.")

    while True:
        player_name_selection = input("Por favor, selecione um nome: ")
        if player_name_selection.strip(): # Garante que o nome não seja vazio
            break
        print("O nome não pode estar em branco.")

    if player_c_selection == "guerreiro":
        return Warrior(player_name_selection)
    elif player_c_selection == "mago":
        return Mage(player_name_selection)
    elif player_c_selection == "ladino":
        return Rogue(player_name_selection)

def generate_monsters_for_level(dungeon_level: int) -> list[Monster]:
    """
    Gera uma lista de monstros para um determinado nível de masmorra,
    com dificuldade crescente.
    """
    monsters = []
    
    # Base number of monsters, increases with dungeon level
    base_num_monsters = 2
    num_monsters_scaling = dungeon_level // 3 # Add one extra monster every 3 levels
    num_monsters = base_num_monsters + num_monsters_scaling
    
    # Ensure there's always at least one monster
    num_monsters = max(1, num_monsters) 

    monster_types = {
        "common": ["Goblin", "Orc", "Esqueleto", "Zumbi"],
        "uncommon": ["Aranha Gigante", "Lobo Mal", "Serpente Venenosa"],
        "rare": ["Minotauro", "Gárgula", "Cavaleiro Corrompido"],
        "boss": ["Dragão Jovem", "Lich Menor"] # Placeholder for potential boss levels
    }

    # Adjust monster generation based on dungeon level
    for _ in range(num_monsters):
        monster_level = dungeon_level + random.randint(-2, 3)
        monster_level = max(1, monster_level) # Ensure level is at least 1

        # Determine monster rarity/strength based on dungeon level
        if dungeon_level < 5:
            # Mostly common monsters at lower levels
            chosen_type = random.choice(monster_types["common"])
        elif 5 <= dungeon_level < 10:
            # Mix of common and uncommon
            chosen_type = random.choice(monster_types["common"] + monster_types["uncommon"])
        elif 10 <= dungeon_level < 20:
            # Mix of uncommon and rare
            chosen_type = random.choice(monster_types["uncommon"] + monster_types["rare"])
        else:
            # Mostly rare, with a small chance of a "boss-like" monster
            if random.random() < 0.1 and dungeon_level > 20: # 10% chance for a 'boss' type monster at very high levels
                chosen_type = random.choice(monster_types["boss"])
                monster_level += 5 # Bosses are stronger
            else:
                chosen_type = random.choice(monster_types["rare"])

        monster_name = f"{chosen_type} Nv.{monster_level}"
        monsters.append(Monster(monster_name, monster_level))
    
    # TODO (DataDesigner): Expand on Monster class to include more attributes (e.g., specific abilities, elemental resistances)
    # TODO (DataDesigner): Define more distinct monster types and their base stats/rarities in a structured way.

    return monsters

def main():
    """
    Função principal que executa o jogo.
    """
    # Criando um novo jogador
    pier = create_player()
    screen_clear()

    # Saudando o jogador
    print(f"Bem-vindo ao jogo, {pier.nick_name}!")
    sleep(1)
    print("Você foi escolhido para o mundo do jogo.")
    sleep(1)
    print("Você tem que lutar contra o Mago Maligno.")
    sleep(1)
    print("Você tem que derrotá-lo e salvar o mundo.")
    
    while True:
        answer = input("Você está pronto para começar? [s/n] ").lower()
        if answer in ["s", "n"]:
            break
        print("Resposta inválida.")

    if answer == "n":
        print("Adeus!")
        exit()

    print("Vamos lá!")
    sleep(2)
    screen_clear()

    # Corrigido: Cada inimigo em uma variável diferente
    enemy1 = Monster("Lobo", 1)
    enemy2 = Monster("Goblin", 2)
    enemy3 = Monster("Troll", 3)
    enemy4 = Monster("Esqueleto", 4)
    enemy5 = Monster("Dragão", 20)
    enemy6 = Monster("Mago Maligno", 30)
    enemy7 = Monster("Cavaleiro Negro", 50)

    # Loop principal do jogo
    while True:
        menu(("Lutar", "Ver status", "Sair"), "O que você quer fazer?")
        try:
            answer = int(input("> "))
            if answer == 1:
               print('A primeira luta é contra o lobo.')
               print("Um oponente muito fraco (espero).")
               sleep(2)
               fight(pier, enemy1)
               # Adicionar lógica para próximas lutas aqui
            elif answer == 2:
               while True:
                   screen_clear()
                   show_status(pier)
                   sleep(1)
                   if input("Pressione Enter para voltar ao menu..."):
                       pass
                   screen_clear()
                   break
            elif answer == 3:
               print("Obrigado por jogar!")
               exit()
            else:
                print("Opção inválida.")
                sleep(1)
        except ValueError:
            print("Entrada inválida. Por favor, insira um número.")
            sleep(1)
        
        screen_clear()
