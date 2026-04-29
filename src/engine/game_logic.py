#!/usr/bin/env python3

from time import sleep

from src.content.factories.monsters import create_monster
from src.content.skills import mage_skills, rogue_skills, warrior_skills
from src.engine.loop import fight
from src.entities.heroes import Mage, Rogue, Warrior
from src.ui.renderer import show_status
from src.ui.screens import menu
from src.ui.utils import clear_screen


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
        player = Warrior(player_name_selection)
        player.learnable_skills = warrior_skills
    elif player_c_selection == "mago":
        player = Mage(player_name_selection)
        player.learnable_skills = mage_skills
    elif player_c_selection == "ladino":
        player = Rogue(player_name_selection)
        player.learnable_skills = rogue_skills

    player.learn_new_skills(show=False)
    return player

def main():
    """
    Função principal que executa o jogo.
    """
    # Criando um novo jogador
    pier = create_player()
    clear_screen()

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
    clear_screen()

    # Corrigido: Cada inimigo em uma variável diferente
    enemy1 = create_monster("Lobo", 1)
    enemy2 = create_monster("Goblin", 2)
    enemy3 = create_monster("Troll", 3)
    enemy4 = create_monster("Esqueleto", 4)
    enemy5 = create_monster("Dragão", 20)
    enemy6 = create_monster("Mago Maligno", 30)
    enemy7 = create_monster("Cavaleiro Negro", 50)

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
                   clear_screen()
                   show_status(pier)
                   sleep(1)
                   if input("Pressione Enter para voltar ao menu..."):
                       pass
                   clear_screen()
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

        clear_screen()
