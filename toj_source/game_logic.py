#!/usr/bin/env python3

# This progam is a game where you have to fight against the Evil Wizard
# The player has to defeat him and save the world
# The player has to choose a class and a name
# The player has to fight against the monsters


from classes import *
from interactions import *
from weapons import *
from time import sleep

def main_menu():
    menu(("Start", "See current stats", "Exit"), "What do you want to do?")

def main():
    # Creating a new player
    try:
        player_C_selection = input("please, select a class: [warrior; mage; rogue] ")
        player_name_selection = input("please, select a name: ")
        if player_C_selection in ["warrior", "mage", "rogue"]:
            if player_C_selection == "warrior":
                pier = Warrior(player_name_selection)
            elif player_C_selection == "mage":
                pier = Mage(player_name_selection)
            elif player_C_selection == "rogue":
                pier = Rogue(player_name_selection)
    except ValueError:
        print("Please, select a valid class")
    except TypeError:
        print("Please, select a valid class")
    screen_clear()

    # Greating the player
    print(f"Welcome to the game {pier.nick_name}")
    sleep(1)
    print("You have been selected to the world of the game")
    sleep(1)
    print("You have to fight against the Evil Wizard")
    sleep(1)
    print("You have to defeat him and save the world")
    
    print("Are you ready to start? [y/n]")
    answer = input()
    if answer == "y":
        print("Let's go!")
        sleep(2)
        screen_clear()
    elif answer == "n":
        print("Goodbye")
        exit()

    # Creating a new enemy
    enemy1 = Monster("Wolf", 1)
    enemy2 = Monster("Goblin", 2)
    enemy3 = Monster("Troll", 3)
    enemy4 = Monster("Skeleton", 4)
    enemy4 = Monster("Dragon", 20)
    enemy5 = Monster("Evil wizard", 30)
    enemy6 = Monster("Black Knight", 50)
    screen_clear()

# Main game loop
    while True:
        main_menu()
        answer = int(input())
        if answer == 1:
           print('The first fight is against the wolf')
           print("A very weak opponent (I hope)")
           sleep(2)
            
           fight(pier, enemy1)
        elif answer == 2:
           while True:
               screen_clear()
               show_status(pier)
               sleep(2)
               print("Press y to continue back to the menu")
               if input() == "y":
                   screen_clear()
                   break
           continue
        elif answer == 3:
            
           exit()

        break # for safety

if __name__ == '__main__':
    main()
