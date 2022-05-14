#!/usr/bin/env python3



# Progama que entrega números aleatorios entre 1 e 60.
# E pede para adivinhar qual o número escolhido.

import random


# cria função principal
def main():
    n = random.randint(1, 60)

    # cria loop para repetir enquanto o usuário não acertar
    while True:
        # pede para o usuário digitar um número
        num = int(input("Digite um número entre 1 e 60: "))

        # verifica se o número digitado é o número escolhido
        if num == n:
            print("Você acertou!")
            break
        else:
            print("Você errou!")



    


main()
