#!/usr/bin/env python3

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
