# Copa Arena 03 — 64 Guerreiros extraídos do PvE real

Campeonato técnico da Arena PvP, gerado por `tools/arena_copa_03.py`. A geração dos 64 está em [`geracao.md`](geracao.md).

> Os nomes são apenas identificadores fictícios de personagens simulados, tirados de canais da Twitch. Não existe participação, autorização ou endosso dessas pessoas. Os nicknames foram sorteados independentemente das builds, dos perfis e da chave.
>
> Uma Copa MD1 é uma amostra de 63 duelos sob uma política fixa, com uma seed por confronto. Ela aponta casos para investigar; não prova balanceamento.

## Resumo

- **Campeão: fer (W64)**, Guerreiro moderado/survival, extraído no andar 21, nível 23, OP 29.98 (defesa + sustento).
- Vice: lubatv (W23), moderado/survival, andar 20, nível 22, OP 29.17.
- OP médio 28.99 (mínimo 27.79, máximo 29.98).
- Os 64: conservador 27, moderado 27, hardcore 10; 53 da seleção original e 11 do preenchimento. As quotas originais 22/21/21 não foram cumpridas (o hardcore não fechou); a distribuição final está em [`geracao.md`](geracao.md).
- 63 partidas, 1831 rodadas, 2582 golpes (2138 conectados), 326 críticos.
- O favorito (OP maior) venceu 44 das 63 partidas; houve 19 zebras.
- As 63 partidas rodaram duas vezes, sem e com auditoria, com o resultado conferido na tabela de auditoria resumida.

Arquivos: [`geracao.md`](geracao.md), [`final_detalhada.md`](final_detalhada.md), [`final_trace.json`](final_trace.json), [`dashboard.html`](dashboard.html), [`relatorio_visual.pdf`](relatorio_visual.pdf), [`gladiadores.json`](gladiadores.json), [`runs.jsonl`](runs.jsonl), [`runs_preenchimento.jsonl`](runs_preenchimento.jsonl), [`preenchimento.json`](preenchimento.json), [`runs_piloto.jsonl`](runs_piloto.jsonl), [`diagnostico_rng.json`](diagnostico_rng.json) e `snapshots/`.

## Como a Copa foi disputada

- **Gladiadores.** Os 64 snapshots canônicos, reconstruídos por `player_from_save_data` sobre cópia (o caminho da Arena) e preparados por `prepare_gladiator` a cada duelo: HP e MP cheios, efeitos, buffs e recargas limpos, consumíveis fora. O snapshot não muda; o nickname vai só na instância reconstruída.
- **Chave.** `random.Random(sha256("20261025:chave")).shuffle` dos 64 IDs, pares em ordem, sem cabeças de chave. Seed de cada partida: 8 bytes de `sha256(f"20261025:{fase}:{índice}")`, o esquema das Copas 01 e 02.
- **Política.** A `PoliticaCopa` das Copas anteriores, igual para os 64: cura com HP ≤ 50%; senão buff ou redução ainda não ativos; senão status que o adversário não carrega; senão a primeira skill de dano legal; senão ataque básico.
- **Limite técnico** do laço: 500 rodadas (inconclusivo, nunca empate).

## Participantes

| ID | Gladiador | Perfil | Política | Andar | Nível | OP | HP | MP | ST | MG | AG | DF | Canais | Skills | Passivas | Equipamento |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| W13 | brtt | Conservador | offense | 20 | 21 | 29.98 | 4244 | 607 | 509 | 311 | 107 | 352 | controle + sustento | Respirar Fundo, Mira Calma, Estocada Seca, Soco de Placa | Sangue de Vidente ×2, Cabeça Dura, Instinto Frio, Ódio Baixo ×2, Lâmina do Juízo ×2, Fúria Berserker ×2, Unha Suja, Olho de Caçador, Ódio Antigo, Agulha no Osso, Presença Errada ×2, Ritmo Profano, Sangue Tóxico, Oráculo Partido, Pele Grossa | Helmet: Elmo de Madeira; Amulet: Amuleto de Concha; Weapon1: Lâmina Veloz; Weapon2: Clava de Madeira; Body: Colete da Resistência; Legs: Bermuda de Couro; Hands: Martelo de Mão; Shoes: Botas de Pano; Ring1: Anel da Esmeralda; Ring2: Anel de Bronze |
| W29 | DavyJones | Moderado | survival | 20 | 22 | 29.98 | 5333 | 829 | 583 | 324 | 104 | 586 | defesa + sustento | Golpe Poderoso, Mira Calma, Paciência do Coveiro, Respirar Fundo | Boca de Sangue ×3, Pele de Sal ×2, Postura Fechada, Sangue de Guerreiro ×5, Músculos de Aço, Casco Calejado ×3, Coração de Ferro ×3, Escudo da Fé, Passos Leves, Pele Grossa | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana; Weapon1: Machado de Guerra; Weapon2: Cajado da Galáxia; Body: Armadura Titânica; Legs: Perneiras de Aço +1; Hands: Escudo de Ferro; Shoes: Botas de Aço; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante |
| W30 | bakzera | Moderado | offense | 20 | 23 | 29.98 | 5860 | 1020 | 629 | 395 | 134 | 520 | crítico + controle | Golpe Duplo, Mira Calma, Provocação, Veterania | Olho de Águia ×3, Oráculo Partido, Passos Leves, Essência Fluída ×3, Fio Serrilhado, Bênção Divina, Músculos de Aço ×2, Cabeça Dura, Mente Serena, Herança do Abismo ×2, Toque do Dragão ×2, Ódio Antigo, Passo de Corça, Ódio Baixo, Coração de Ferro | Helmet: Elmo de Couro; Amulet: Amuleto da Mana +1; Weapon1: Machado Terrível +1; Weapon2: Espada Longa; Body: Armadura de Espinhos; Legs: Calça de Cota +1; Hands: Luvas Rasas; Shoes: Botas de Aço; Ring1: Anel de Aço; Ring2: Anel de Bronze +1; Accessory: Talismã do Viajante +1 |
| W36 | Gaules | Moderado | offense | 20 | 22 | 29.98 | 5209 | 695 | 626 | 332 | 119 | 415 | crítico + controle | Mão Dupla, Peso do Machado, Estocada Seca, Fúria | Toque do Dragão, Coração de Ferro ×2, Fúria Berserker ×2, Cabeça Dura, Lâmina Afiada ×3, Unha Suja, Sangue de Guerreiro, Respiração Contada, Sede de Sangue, Herança do Abismo, Músculos de Aço ×2, Fio Serrilhado, Olho de Caçador ×2, Escudo da Fé, Reserva Arcana | Helmet: Elmo de Madeira; Amulet: Amuleto da Agilidade +1; Weapon1: Lâmina da Tempestade; Weapon2: Gravetos Mágicos +1; Body: Placa Pesada; Legs: Perneiras de Ferro; Hands: Escudo Torre; Shoes: Chinelos de Pano; Ring1: Anel Vegetal; Ring2: Anel de Palha |
| W64 | fer | Moderado | survival | 21 | 23 | 29.98 | 5977 | 1103 | 654 | 446 | 142 | 503 | defesa + sustento | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | Sangue de Guerreiro, Essência Fluída ×4, Coração de Ferro ×4, Instinto Frio, Olho de Águia, Herança do Abismo, Bênção Divina, Postura Fechada, Boca de Sangue ×2, Pele Grossa, Fúria Berserker, Vulto, Músculos de Aço, Sede de Sangue, Escudo da Fé | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +2; Weapon1: Cajado de Cristal; Weapon2: Porrete +1; Body: Placa Pesada; Legs: Calça de Cota; Hands: Luvas de Aço +1; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante +1; Accessory: Talismã do Viajante +1 |
| W10 | Patriota | Conservador | offense | 21 | 22 | 29.87 | 4779 | 855 | 621 | 330 | 110 | 473 | controle | Pisada de Ferro, Investida de Aríete, Pancada na Nuca, Pausa Útil | Cabeça Dura ×3, Músculos de Aço ×4, Olho de Águia, Sangue de Vidente ×2, Olho de Caçador, Passo de Corça, Punho Atordoante, Passos Leves, Sangue de Guerreiro, Sangue Tóxico, Ódio Baixo, Pele Grossa, Instinto Frio, Presença Errada, Voracidade | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Clava Pesada; Weapon2: Clava de Madeira +1; Body: Peitoral de Cota; Legs: Perneiras de Aço; Hands: Martelo de Mão; Shoes: Sapatos de Couro; Ring1: Anel da Esmeralda; Ring2: Anel de Palha |
| W32 | loud_thurzin | Moderado | offense | 19 | 22 | 29.87 | 5110 | 963 | 538 | 324 | 135 | 477 | crítico + controle | Marca do Caçador, Golpe Devastador, Guarda Alta, Grito Curto | Olho de Caçador ×2, Fio Serrilhado ×2, Essência Fluída, Olho de Águia ×2, Passo de Corça ×2, Cabeça Dura ×2, Lâmina do Juízo, Pulso Certeiro, Unha Suja, Músculos de Aço ×3, Instinto Frio ×2, Passos Leves ×2 | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Espada de Aço; Weapon2: Gládio de Ferro; Body: Armadura Divina; Legs: Calça de Cota; Hands: Escudo Torre; Shoes: Botas de Corrida; Ring1: Anel Vegetal; Ring2: Anel de Bronze |
| W34 | LuquEt4 | Moderado | offense | 21 | 23 | 29.87 | 7257 | 773 | 612 | 437 | 145 | 503 | crítico | Golpe Duplo, Grito de Guerra, Cutelada, Areia no Chão | Ódio Baixo ×7, Olho de Caçador ×2, Fúria Berserker ×2, Postura Fechada, Músculos de Aço, Sangue de Vidente ×2, Lâmina Lendária, Olho de Águia ×2, Pulso Certeiro ×2, Passos Leves, Pele Grossa | Helmet: Elmo de Dragão +1; Amulet: Amuleto da Vida; Weapon1: Cajado de Cristal; Weapon2: Adaga de Madeira +1; Body: Camisa de Corrente; Legs: Perneiras de Aço; Hands: Martelo de Mão; Shoes: Botas de Pano; Ring1: Anel de Diamante; Ring2: Anel de Bronze |
| W37 | gafallen | Moderado | economy | 17 | 20 | 29.87 | 3973 | 763 | 422 | 282 | 93 | 369 | sustento | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda | Escudo da Fé, Reserva Arcana ×2, Sede Silenciosa ×5, Ritmo Profano ×3, Mente Serena, Lâmina do Juízo, Dívida de Ouro, Alquimia do Desespero, Mãos de Midas ×3, Sangue de Guerreiro | Helmet: Elmo de Dragão +1; Amulet: Amuleto da Mana; Weapon1: Machado de Guerra; Weapon2: Espada de Aço; Body: Armadura de Couro; Legs: Perneiras de Ferro; Hands: Luvas de Titânio +2; Shoes: Botas de Pano; Ring1: Anel da Esmeralda; Ring2: Anel de Bronze |
| W39 | yeTz | Moderado | economy | 20 | 23 | 29.87 | 7383 | 776 | 604 | 363 | 126 | 542 | sustento | Paciência do Coveiro, Quebra-Guarda, Postura de Muro, Cutelada | Bebida dos Deuses ×2, Mente Serena, Ritmo Profano, Sorte de Principiante ×2, Sede Silenciosa ×2, Respiração Contada ×2, Fúria Berserker, Passo de Corça, Boca de Sangue ×4, Vulto, Poço Fundo, Músculos de Aço, Sangue de Guerreiro, Coração de Ferro, Mãos de Midas | Helmet: Elmo de Madeira; Amulet: Amuleto de Prata +2; Weapon1: Lâmina Veloz; Weapon2: Clava Pesada; Body: Peitoral de Ferro; Legs: Calça de Ferro; Hands: Escudo de Madeira; Shoes: Botas de Ferro; Ring1: Anel de Couro; Ring2: Anel Vegetal +1 |
| W26 | MeikodRJ | Moderado | survival | 19 | 22 | 29.75 | 4969 | 829 | 611 | 389 | 106 | 530 | sustento | Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno | Sangue de Guerreiro ×4, Bebida dos Deuses ×2, Pele de Sal ×3, Alma Eterna, Olho de Águia ×2, Toque do Dragão, Alquimia do Desespero, Sede Silenciosa, Postura Fechada, Coração de Ferro, Boca de Sangue ×2, Passo de Corça, Fio Serrilhado | Helmet: Elmo de Aço; Amulet: Amuleto da Mana; Weapon1: Machado de Guerra +1; Weapon2: Cajado de Cristal; Body: Armadura Titânica; Legs: Perneiras de Aço; Hands: Manoplas de Ferro; Shoes: Botas de Aço; Ring1: Anel de Ouro; Ring2: Anel da Esmeralda |
| W35 | Smzinho | Moderado | offense | 20 | 23 | 29.75 | 5701 | 958 | 612 | 374 | 128 | 487 | controle | Cutelada, Mira Calma, Veterania, Estocada Seca | Ódio Antigo ×2, Passos Leves, Passo de Corça ×3, Ódio Baixo ×2, Sangue de Guerreiro, Voz no Escuro, Cabeça Dura, Fúria Berserker ×2, Herança do Abismo, Sangue de Vidente, Olho de Águia, Instinto Frio ×2, Ritmo Profano, Músculos de Aço, Pele Grossa, Pulso Certeiro | Helmet: Elmo de Madeira; Amulet: Amuleto da Mana +1; Weapon1: Espada da Vingança; Weapon2: Machado Enferrujado; Body: Armadura Titânica; Legs: Bermuda de Couro; Hands: Escudo de Madeira; Ring1: Anel Vegetal; Ring2: Anel de Palha |
| W40 | NOBRU | Moderado | economy | 19 | 23 | 29.75 | 5469 | 1024 | 633 | 363 | 121 | 503 | sustento | Cutelada, Investida, Postura de Muro, Imortal | Boca de Sangue ×3, Essência Viva ×2, Essência Fluída, Reflexos Rápidos, Mente Serena, Coração de Ferro ×2, Sede Silenciosa ×2, Sangue de Guerreiro ×3, Reserva Arcana ×2, Respiração Contada, Pele de Sal, Toque do Dragão, Sorte de Principiante, Postura Fechada | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Machado de Guerra; Weapon2: Gládio de Ferro; Body: Armadura Divina +1; Legs: Bermuda de Couro; Hands: Luvas de Couro; Ring1: Anel de Ouro; Ring2: Anel Vegetal |
| W43 | aXtLOL | Moderado | economy | 20 | 23 | 29.75 | 5454 | 766 | 675 | 363 | 128 | 549 | sustento | Travar o Pulso, Mira Calma, Ferro Contra Ferro, Ritmo de Duelo | Olho de Caçador, Casco Calejado, Mente Serena ×2, Essência Viva ×2, Respiração Contada, Pele de Sal, Reserva Arcana, Essência Fluída ×2, Bebida dos Deuses, Dívida de Ouro, Sangue de Guerreiro ×2, Ritmo Profano ×3, Fúria Berserker, Boca de Sangue, Mãos de Midas, Olho de Águia | Helmet: Elmo de Dragão +1; Amulet: Amuleto da Imortalidade; Weapon1: Machado de Batalha; Weapon2: Espada de Ferro; Body: Gibão de Couro; Legs: Perneiras de Ferro; Hands: Luvas de Titânio +1; Shoes: Botas de Couro; Ring1: Anel de Ouro; Ring2: Anel de Bronze +1 |
| W55 | casimito | Moderado | offense | 21 | 23 | 29.75 | 7113 | 726 | 691 | 425 | 144 | 546 | crítico + controle | Peso do Machado, Esmagar, Provocação, Disciplina de Forja | Postura Fechada ×2, Lâmina Afiada, Sangue de Vidente, Olho de Águia ×2, Ódio Baixo ×3, Sangue de Guerreiro ×2, Fúria Berserker ×2, Instinto Frio, Músculos de Aço ×2, Coração de Ferro, Pulso Certeiro ×4, Voz no Escuro | Helmet: Elmo de Ferro; Amulet: Amuleto da Vida +1; Weapon1: Lança de Madeira; Weapon2: Gravetos Mágicos; Body: Armadura Divina; Legs: Armadura de Camisa; Hands: Luvas de Aço; Shoes: Botas de Aço; Ring1: Anel do Rubi; Ring2: Anel de Diamante +1 |
| W31 | Felps | Moderado | offense | 17 | 20 | 29.64 | 4098 | 618 | 487 | 258 | 92 | 350 | crítico + controle | Sangue nos Olhos, Quebra-Guarda, Travar o Pulso, Marca do Açougueiro | Punho Atordoante, Fúria Berserker, Sede Silenciosa, Agulha no Osso, Ódio Baixo ×2, Olho de Águia, Coração de Ferro ×2, Sangue de Guerreiro, Sede de Sangue, Instinto Frio, Pulso Certeiro ×3, Olho de Caçador, Músculos de Aço, Sangue Tóxico, Cabeça Dura | Helmet: Elmo de Ferro; Amulet: Amuleto de Pedra; Weapon1: Machado de Batalha; Weapon2: Espada de Ferro; Body: Peitoral de Ferro; Legs: Calça de Cota +1; Hands: Luvas de Titânio +1; Shoes: Botas de Couro; Ring1: Anel de Ouro; Ring2: Anel de Palha |
| W41 | coldzin | Moderado | economy | 21 | 24 | 29.64 | 8119 | 961 | 667 | 423 | 153 | 542 | sustento | Pancada na Nuca, Postura de Muro, Cutelada, Tremor de Bigorna | Passo de Corça, Respiração Contada, Essência Viva ×2, Sede Silenciosa, Reflexos Rápidos, Olho de Caçador, Fortuna Absoluta ×2, Boca de Sangue, Mente Serena ×3, Bebida dos Deuses, Reserva Arcana ×2, Alquimia do Desespero, Passos Leves, Poço Fundo, Lâmina Afiada, Instinto Frio, Músculos de Aço, Sorte de Principiante | Helmet: Bandana de Tecido; Amulet: Amuleto da Vida +1; Weapon1: Espada da Vingança; Weapon2: Adaga de Madeira +1; Body: Armadura de Placa; Legs: Calça de Ferro; Hands: Luvas de Titânio +2; Shoes: Botas de Corrida; Ring1: Anel de Diamante; Ring2: Anel de Couro |
| W42 | RNakano | Moderado | economy | 19 | 24 | 29.64 | 8159 | 913 | 664 | 407 | 136 | 568 | sustento | Golpe Duplo, Cutelada, Gancho e Corda, Disciplina de Forja | Essência Viva, Mãos de Midas ×2, Poço Fundo ×2, Mente Serena ×2, Pele Grossa, Ritmo Profano, Essência Fluída, Boca de Sangue ×3, Respiração Contada, Bebida dos Deuses ×2, Sangue de Guerreiro, Voracidade, Sorte de Principiante ×2, Alma Eterna, Ódio Antigo, Essência Pura | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada da Vingança; Weapon2: Espada de Ferro; Body: Armadura de Fenrir; Legs: Calça de Cota; Hands: Martelo de Mão +1; Shoes: Botas de Aço; Ring1: Anel do Rubi +1; Ring2: Anel da Esmeralda +1; Accessory: Talismã do Viajante +2 |
| W47 | XANDAOOGOD | Hardcore | survival | 22 | 23 | 29.64 | 5684 | 1037 | 638 | 366 | 127 | 503 | defesa | Esmagar, Mira Calma, Leitura de Terreno, Veterania | Respiração Contada, Sangue de Vidente, Olho de Águia, Coração de Ferro ×4, Alma Eterna, Passo de Corça, Reserva Arcana, Poço Fundo, Músculos de Aço ×2, Bebida dos Deuses, Coração de Titã, Instinto Frio, Pele de Sal ×3, Agulha no Osso, Postura Fechada, Pele de Adamântio | Helmet: Elmo de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Clava Pesada; Weapon2: Espada de Treino +1; Body: Armadura de Cota de Malha; Legs: Calça de Cota; Hands: Luvas de Aço +1; Shoes: Botas de Aço; Ring1: Anel de Couro; Ring2: Anel de Couro |
| W54 | TheBurntPeanut | Conservador | economy | 20 | 23 | 29.64 | 5364 | 1053 | 593 | 371 | 132 | 506 | sem canal dominante | Mão Dupla, Mira Calma, Provocação, Grito de Guerra | Essência Viva, Sorte de Principiante ×2, Mãos de Midas, Dívida de Ouro, Reserva Arcana ×2, Coração de Ferro, Respiração Contada ×2, Escudo da Fé, Olho de Águia ×2, Pele Grossa ×2, Herança do Abismo, Olho de Caçador ×2, Mente Serena ×2, Sangue de Guerreiro, Sede Silenciosa | Helmet: Elmo de Ferro; Amulet: Amuleto da Mana +2; Weapon1: Clava Pesada; Weapon2: Faca de Caça; Body: Armadura de Placa; Legs: Calça de Cota +1; Hands: Luvas de Aço +1; Shoes: Botas de Couro; Ring1: Anel de Bronze +1; Ring2: Anel de Ouro |
| W59 | liminhag0d | Moderado | offense | 19 | 22 | 29.64 | 4809 | 648 | 581 | 348 | 110 | 502 | crítico + controle | Golpe Poderoso, Investida, Estocada Seca, Guarda Alta | Coração de Ferro, Ódio Baixo, Instinto Frio, Fio Serrilhado ×3, Pulso Certeiro ×2, Passos Leves, Olho de Águia ×2, Escudo da Fé, Postura Fechada, Ódio Antigo ×2, Voz no Escuro, Lâmina Afiada ×2, Essência Fluída, Fúria Berserker, Sangue de Vidente | Helmet: Elmo de Aço; Amulet: Amuleto da Imortalidade; Weapon1: Lança de Madeira; Weapon2: Espada de Aço; Body: Armadura Divina; Legs: Calça de Ferro; Hands: Martelo de Mão; Shoes: Chinelos de Pano; Ring1: Anel de Diamante; Ring2: Anel Vegetal +1 |
| W16 | sacy | Conservador | economy | 19 | 23 | 29.52 | 7520 | 786 | 593 | 386 | 132 | 522 | sustento | Golpe Devastador, Mira Calma, Escudo Protetor, Silêncio do Veterano | Reflexos Rápidos, Boca de Sangue ×2, Essência Viva, Fome de Batalha, Sorte de Principiante, Mente Serena ×4, Mãos de Midas, Pele Grossa, Sede Silenciosa, Pele de Sal, Sangue de Guerreiro, Respiração Contada ×2, Postura Fechada ×2, Corpo Inviolável, Passos Leves, Reserva Arcana | Helmet: Capacete de Ferro; Amulet: Amuleto da Vida +2; Weapon1: Espada de Treino; Weapon2: Gravetos Mágicos; Body: Armadura de Cota de Malha; Legs: Perneiras de Aço; Hands: Escudo Torre; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda +1; Ring2: Anel do Rubi +1 |
| W22 | jovirone | Conservador | economy | 17 | 24 | 29.52 | 6345 | 1191 | 664 | 407 | 147 | 556 | sustento | Marca do Açougueiro, Quebra-Guarda, Disciplina de Forja, Sangue nos Olhos | Voracidade ×2, Dívida de Ouro, Poço Fundo ×2, Fome de Batalha, Sorte de Principiante ×4, Sangue de Guerreiro ×2, Coração de Ferro ×2, Essência Pura, Mente Serena, Casco Calejado, Pele de Sal, Ritmo Profano, Essência Viva, Lâmina Afiada, Boca de Sangue ×2 | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Espada Longa; Weapon2: Adaga de Madeira +2; Body: Armadura de Placa; Legs: Perneiras de Aço; Hands: Martelo de Mão; Ring1: Anel de Diamante +1; Ring2: Anel Vegetal; Accessory: Talismã do Viajante |
| W24 | fnxLNTC | Moderado | survival | 19 | 22 | 29.52 | 5355 | 951 | 573 | 371 | 120 | 505 | defesa + sustento | Golpe Poderoso, Investida, Couraça Improvisada, Berro de Ferro | Sede Silenciosa, Postura Fechada ×3, Passo de Corça ×2, Pele de Sal ×2, Lâmina Afiada, Corpo Inviolável, Pele de Adamântio, Herança do Abismo, Bebida dos Deuses, Sangue de Guerreiro ×3, Pele Grossa, Boca de Sangue, Passos Leves, Coração de Ferro, Essência Fluída | Helmet: Elmo de Aço; Amulet: Amuleto da Mana +1; Weapon1: Espada da Vingança; Weapon2: Cajado de Cristal; Body: Armadura Divina; Legs: Perneiras de Aço; Hands: Martelo de Mão; Shoes: Botas de Couro; Ring1: Anel da Esmeralda; Ring2: Anel Vegetal |
| W25 | mount | Moderado | survival | 21 | 23 | 29.52 | 7863 | 786 | 596 | 401 | 125 | 575 | defesa + sustento | Golpe Poderoso, Soco de Placa, Couro Batido, Disciplina de Forja | Pele de Adamântio, Bebida dos Deuses ×3, Sangue de Guerreiro ×6, Ódio Baixo, Boca de Sangue ×2, Escudo da Fé ×3, Músculos de Aço, Sangue de Vidente, Lâmina Afiada, Pele Grossa ×2, Respiração Contada | Helmet: Capacete de Couro; Amulet: Amuleto da Vida +2; Weapon1: Lança de Madeira; Weapon2: Machado Enferrujado; Body: Armadura Titânica; Legs: Perneiras de Ferro; Hands: Luvas de Aço +1; Shoes: Botas de Ferro; Ring1: Anel da Fênix; Ring2: Anel de Palha |
| W28 | furq | Moderado | survival | 21 | 23 | 29.52 | 7593 | 756 | 665 | 363 | 155 | 525 | defesa + controle + sustento | Golpe Poderoso, Quebra-Guarda, Guarda Cruzada, Areia no Chão | Pele Grossa ×2, Bebida dos Deuses, Essência Fluída, Escudo da Fé ×2, Passos Leves ×2, Boca de Sangue, Coração de Ferro, Sangue de Guerreiro ×4, Pele de Sal, Ódio Baixo, Respiração Contada, Passo de Corça, Fúria Berserker, Mente Serena, Punho Atordoante, Reserva Arcana | Helmet: Capacete de Couro; Amulet: Amuleto da Vida +1; Weapon1: Machado de Batalha; Weapon2: Espada de Treino +1; Body: Armadura de Cota de Malha; Legs: Perneiras de Aço; Hands: Luvas de Lã; Shoes: Botas de Corrida; Ring1: Anel de Couro; Ring2: Anel de Palha |
| W60 | frttt | Moderado | economy | 19 | 23 | 29.52 | 5379 | 1042 | 604 | 363 | 131 | 499 | sustento | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca | Sangue de Guerreiro, Coração de Ferro ×2, Olho de Águia, Respiração Contada ×2, Músculos de Aço, Sorte de Principiante ×2, Reserva Arcana ×2, Olho de Caçador, Bebida dos Deuses, Pele de Sal, Sede Silenciosa, Mente Serena, Fome de Batalha, Mãos de Midas, Fúria Berserker, Boca de Sangue ×2, Sede de Sangue | Helmet: Elmo de Couro; Amulet: Amuleto de Ouro +1; Weapon1: Espada da Vingança; Weapon2: Faca de Caça +1; Body: Armadura Divina; Legs: Bermuda de Couro; Hands: Luvas de Aço; Shoes: Botas de Aço; Ring1: Anel de Ouro; Ring2: Anel Vegetal |
| W33 | YoDa | Moderado | offense | 18 | 21 | 29.41 | 5464 | 603 | 492 | 305 | 91 | 473 | controle | Mão Dupla, Tremor de Bigorna, Estocada Seca, Lâmina Assentada | Fio Serrilhado ×2, Imortalidade Momentânea, Olho de Águia, Voz no Escuro ×2, Ódio Antigo ×2, Pele Grossa ×2, Sangue de Guerreiro, Fúria Berserker ×2, Herança do Abismo ×2, Olho de Caçador ×2, Ódio Baixo, Pulso Certeiro, Músculos de Aço | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Machado de Batalha; Weapon2: Espada de Treino +1; Body: Armadura Titânica; Legs: Calça de Pano; Hands: Luvas de Titânio +2; Shoes: Botas de Aço; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi; Accessory: Talismã do Viajante |
| W38 | Neskwga | Moderado | economy | 18 | 22 | 29.41 | 6216 | 668 | 532 | 416 | 108 | 504 | defesa + sustento | Golpe Poderoso, Mira Calma, Escudo Protetor, Baluarte | Essência Viva ×3, Alma Eterna, Coração de Ferro ×2, Alquimia do Desespero, Ódio Antigo, Sorte de Principiante, Respiração Contada, Dívida de Ouro, Pele de Sal, Sangue de Guerreiro ×2, Reserva Arcana, Mãos de Midas, Ódio Baixo, Postura Fechada, Sede de Sangue, Músculos de Aço, Boca de Sangue | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata +1; Weapon1: Cajado de Cristal; Weapon2: Arco Composto; Body: Armadura de Espinhos; Legs: Perneiras de Ferro; Hands: Luvas de Titânio +2; Shoes: Botas de Ferro; Ring1: Anel de Aço +1; Ring2: Anel da Fênix +1 |
| W63 | tioorochitwitch | Moderado | economy | 18 | 23 | 29.41 | 7189 | 736 | 599 | 406 | 134 | 604 | defesa + sustento | Golpe Poderoso, Investida, Postura de Muro, Baluarte | Sangue de Guerreiro ×3, Músculos de Aço ×2, Sorte de Principiante ×4, Ritmo Profano ×2, Bênção Divina, Coração de Ferro, Dívida de Ouro, Pele Grossa, Mãos de Midas, Mente Serena, Pele de Sal, Bebida dos Deuses, Essência Fluída, Boca de Sangue, Olho de Águia | Helmet: Elmo de Aço; Amulet: Amuleto de Prata +1; Weapon1: Cajado de Cristal; Weapon2: Tridente do Guerreiro +1; Body: Armadura de Fenrir; Legs: Perneiras de Aço; Hands: Manoplas de Ferro +1; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda +1; Ring2: Anel da Fênix +1 |
| W27 | aspaszin | Moderado | survival | 19 | 22 | 29.29 | 4874 | 882 | 547 | 337 | 118 | 496 | crítico + defesa + sustento | Golpe Poderoso, Quebra-Guarda, Fôlego de Marcha, Respirar Fundo | Sangue de Guerreiro ×2, Toque do Dragão, Passos Leves ×2, Reflexos Rápidos, Sede Silenciosa, Bebida dos Deuses, Casco Calejado, Coração de Ferro ×2, Pele de Sal ×3, Essência Fluída, Sede de Sangue ×2, Olho de Águia, Postura Fechada, Músculos de Aço, Pele Grossa | Helmet: Elmo de Aço; Amulet: Amuleto da Mana +1; Weapon1: Espada Lendária; Weapon2: Bastão Cru +1; Body: Armadura Divina; Legs: Calça de Cota +1; Hands: Luvas de Aço; Shoes: Tamancos de Madeira; Ring1: Anel de Diamante +1; Ring2: Anel do Rubi |
| W56 | sofiaespanha | Moderado | economy | 17 | 23 | 29.29 | 7757 | 836 | 593 | 363 | 121 | 529 | defesa + controle | Soco de Placa, Passo Lateral, Quebra-Guarda, Baluarte | Instinto Frio, Essência Viva ×3, Cabeça Dura, Boca de Sangue, Reserva Arcana ×5, Sorte de Principiante ×2, Pele Grossa ×2, Pele de Sal, Fome de Batalha, Vulto, Mente Serena, Bênção Divina, Sangue de Guerreiro, Respiração Contada | Helmet: Capacete de Ferro; Amulet: Amuleto da Vida +2; Weapon1: Tridente do Guerreiro; Weapon2: Adaga de Madeira +1; Body: Armadura de Espinhos; Legs: Bermuda de Couro; Shoes: Sapatos de Couro; Ring1: Anel da Esmeralda +1; Ring2: Anel da Esmeralda +1; Accessory: Talismã do Viajante |
| W19 | tteuw | Conservador | economy | 16 | 19 | 29.17 | 4842 | 521 | 377 | 250 | 77 | 353 | defesa + sustento | Golpe Poderoso, Mira Calma, Tomar Fôlego, Escudo Protetor | Coração de Ferro, Boca de Sangue, Casco Calejado ×3, Ritmo Profano ×2, Pele de Adamântio ×2, Sorte de Principiante, Mente Serena ×2, Sede Silenciosa, Postura Fechada, Bebida dos Deuses, Bênção Divina, Sangue de Guerreiro, Voracidade | Helmet: Elmo de Aço; Amulet: Amuleto da Vida +1; Weapon1: Espada Lendária; Weapon2: Espada do Eclipse; Body: Armadura de Couro; Legs: Perneiras de Aço; Hands: Luvas de Aço; Shoes: Chinelos de Pano; Ring1: Anel de Diamante; Ring2: Anel de Diamante |
| W23 | lubatv | Moderado | survival | 20 | 22 | 29.17 | 5275 | 908 | 547 | 337 | 114 | 527 | crítico + sustento | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | Músculos de Aço, Postura Fechada ×3, Reserva Arcana ×2, Olho de Caçador, Vulto ×2, Pele Grossa, Casco Calejado, Alma Eterna, Toque do Dragão, Sangue de Guerreiro, Passo de Corça, Lâmina Afiada ×3, Olho de Águia, Bênção Divina, Passos Leves | Helmet: Elmo de Dragão; Amulet: Amuleto da Mana +1; Weapon1: Gládio de Ferro; Weapon2: Lança de Madeira +1; Body: Armadura Titânica; Legs: Calça de Cota; Hands: Martelo de Mão; Shoes: Chinelos de Pano; Ring1: Anel Vegetal +1; Ring2: Anel de Palha |
| W01 | dona | Conservador | survival | 21 | 23 | 29.06 | 7574 | 746 | 616 | 363 | 158 | 541 | sustento | Cutelada, Investida, Respirar Fundo, Grito de Guerra | Coração de Ferro ×2, Sede Silenciosa, Sangue de Guerreiro ×3, Respiração Contada, Passo de Corça ×2, Alma Eterna, Passos Leves ×3, Boca de Sangue ×2, Toque do Dragão, Olho de Águia, Lâmina Afiada, Fúria Berserker, Reserva Arcana, Escudo da Fé, Postura Fechada | Helmet: Elmo de Aço; Amulet: Amuleto da Vida +1; Weapon1: Lança de Madeira; Weapon2: Espada de Treino +2; Body: Armadura Titânica; Legs: Calça de Cota; Hands: Martelo de Mão; Shoes: Botas de Aço; Ring1: Anel Vegetal; Ring2: Anel Vegetal; Accessory: Talismã do Viajante |
| W15 | RazaH | Conservador | offense | 18 | 20 | 29.06 | 5285 | 537 | 497 | 298 | 93 | 400 | crítico + controle | Marca do Caçador, Grito Curto, Pausa Útil, Mão Dupla | Punho Atordoante, Olho de Caçador, Olho de Águia ×2, Essência Fluída, Unha Suja, Ódio Baixo, Presença Errada, Fúria Berserker, Sangue de Vidente ×2, Músculos de Aço, Pele Grossa, Fio Serrilhado ×2, Pulso Certeiro, Lâmina Afiada, Reserva Arcana, Herança do Abismo | Helmet: Elmo de Ferro; Amulet: Amuleto da Vida +1; Weapon1: Tridente do Guerreiro; Weapon2: Faca de Caça; Body: Armadura Divina; Legs: Perneiras de Ferro; Hands: Escudo de Ferro; Shoes: Botas de Couro; Ring1: Anel da Esmeralda; Ring2: Anel Vegetal; Accessory: Talismã do Viajante +1 |
| W08 | Tenz | Conservador | survival | 20 | 23 | 28.71 | 5519 | 1050 | 601 | 406 | 121 | 509 | crítico + sustento | Golpe Poderoso, Soco de Placa, Gancho e Corda, Tomar Fôlego | Reserva Arcana, Sede Silenciosa, Sangue de Guerreiro ×5, Boca de Sangue ×2, Mente Serena, Imortalidade Momentânea, Olho de Caçador, Fúria Berserker, Olho de Águia ×3, Poço Fundo, Pele de Sal ×2, Bênção Divina, Postura Fechada, Pele de Adamântio | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Cajado de Cristal; Weapon2: Espada da Vingança +1; Body: Peitoral de Cota; Legs: Perneiras de Aço; Hands: Luvas de Couro; Shoes: Sapatos de Couro; Ring1: Anel da Esmeralda +1; Ring2: Anel de Bronze +1 |
| W11 | Forever | Conservador | offense | 20 | 22 | 28.71 | 5225 | 842 | 623 | 351 | 110 | 457 | crítico + defesa + controle | Grito Curto, Peso do Machado, Couro Batido, Última Carta | Bênção Divina, Respiração Contada, Lâmina Afiada ×2, Olho de Caçador ×2, Fúria Berserker ×2, Olho de Águia, Estrela Quebrada, Cabeça Dura, Ódio Baixo, Voz no Escuro, Mente Serena, Músculos de Aço ×2, Sangue de Vidente ×2, Agulha no Osso ×2, Passos Leves | Helmet: Elmo de Ferro; Amulet: Amuleto de Ouro +2; Weapon1: Lança de Madeira; Weapon2: Bastão Cru +1; Body: Armadura de Espinhos; Legs: Calças de Tecido; Hands: Luvas de Lã +1; Shoes: Botas de Aço; Ring1: Anel de Bronze +1; Ring2: Anel de Palha |
| W44 | calango | Hardcore | survival | 19 | 22 | 28.60 | 5367 | 829 | 529 | 324 | 119 | 451 | sustento | Golpe Poderoso, Quebra-Guarda, Imortal, Tomar Fôlego | Voracidade ×2, Alma Eterna ×2, Sangue de Guerreiro, Passos Leves ×3, Coração de Ferro ×3, Sede Silenciosa, Pele Grossa ×2, Boca de Sangue ×2, Instinto Frio ×2, Olho de Caçador, Olho de Águia, Essência Fluída | Helmet: Elmo de Couro; Amulet: Amuleto da Mana; Weapon1: Tridente do Guerreiro; Weapon2: Gravetos Mágicos; Body: Placa Pesada; Legs: Calça de Cota; Hands: Manoplas de Ferro; Shoes: Botas de Couro; Ring1: Anel Vegetal +1; Ring2: Anel da Esmeralda; Accessory: Talismã do Viajante +1 |
| W49 | Bisteconee | Hardcore | offense | 20 | 22 | 28.60 | 4779 | 829 | 586 | 407 | 124 | 387 | controle | Cutelada, Mira Calma, Areia no Chão, Leitura de Terreno | Sangue de Vidente ×3, Sangue de Guerreiro, Cabeça Dura, Músculos de Aço ×2, Fio Serrilhado, Mente Serena, Herança do Abismo ×2, Olho de Águia, Ódio Antigo ×2, Ódio Baixo ×2, Olho de Caçador ×3, Agulha no Osso, Toque do Dragão | Helmet: Elmo de Couro; Amulet: Amuleto de Ouro +1; Weapon1: Espada da Vingança; Weapon2: Espada de Treino +1; Body: Cota Leve; Legs: Saia de Tecido; Hands: Escudo de Madeira; Shoes: Botas de Couro; Ring1: Anel de Diamante +1; Ring2: Anel de Palha |
| W50 | hastad | Hardcore | offense | 21 | 22 | 28.60 | 4794 | 648 | 546 | 343 | 112 | 418 | crítico + defesa + controle | Mão Dupla, Mira Calma, Estocada Seca, Couro Batido | Olho de Águia ×2, Lâmina Lendária, Ódio Baixo ×2, Músculos de Aço ×3, Fúria Berserker, Sangue de Guerreiro, Respiração Contada ×2, Coração de Ferro, Agulha no Osso, Herança do Abismo ×2, Sangue de Vidente, Pele Grossa, Passo de Corça, Voz no Escuro, Fio Serrilhado | Helmet: Capacete de Couro +1; Weapon1: Tridente do Guerreiro; Weapon2: Adaga de Madeira +1; Body: Peitoral de Ferro; Legs: Bermuda de Couro; Hands: Luvas Rasas; Shoes: Botas de Aço; Ring1: Anel de Ouro; Ring2: Anel de Bronze +1 |
| W58 | JonVlogs | Conservador | economy | 19 | 22 | 28.60 | 6314 | 708 | 538 | 364 | 116 | 485 | defesa + sustento | Golpe Poderoso, Investida, Guarda Alta, Couraça Improvisada | Olho de Águia, Boca de Sangue ×2, Reserva Arcana ×2, Respiração Contada, Músculos de Aço ×3, Instinto Frio, Mente Serena ×2, Sorte de Principiante ×2, Coração de Ferro ×2, Mãos de Midas, Pele de Sal, Pele Grossa, Fome de Batalha, Ódio Antigo | Helmet: Elmo de Dragão +1; Amulet: Amuleto da Vida +1; Weapon1: Porrete; Weapon2: Gravetos Mágicos; Body: Armadura de Cota de Malha; Legs: Perneiras de Aço; Hands: Luvas de Aço; Shoes: Tamancos de Madeira; Ring1: Anel da Fênix +1; Ring2: Anel da Esmeralda +1 |
| W62 | gabepeixe | Conservador | offense | 19 | 21 | 28.60 | 4274 | 712 | 586 | 289 | 113 | 416 | crítico + controle | Fúria, Soco de Placa, Travar o Pulso, Tremor de Bigorna | Coração de Ferro ×2, Sede de Sangue, Músculos de Aço ×2, Voz no Escuro, Fúria Berserker ×2, Lâmina Lendária, Ódio Antigo ×2, Ódio Baixo, Instinto Frio, Passos Leves, Pulso Certeiro, Passo de Corça, Cabeça Dura, Olho de Águia, Toque do Dragão, Sangue Tóxico | Amulet: Amuleto de Ouro; Weapon1: Espada da Vingança; Weapon2: Espada Lendária +1; Body: Peitoral de Cota; Legs: Calça de Cota; Hands: Luvas de Titânio +2; Shoes: Botas de Aço; Ring1: Anel de Bronze; Ring2: Anel de Couro |
| W20 | xandfps | Conservador | economy | 17 | 21 | 28.48 | 4259 | 856 | 473 | 289 | 100 | 361 | sustento | Mão Dupla, Mira Calma, Escudo Protetor, Peso do Machado | Sede Silenciosa ×3, Coração de Ferro, Mãos de Midas, Essência Viva, Reserva Arcana, Boca de Sangue ×4, Respiração Contada ×4, Sorte de Principiante ×2, Bebida dos Deuses, Mente Serena, Poço Fundo | Helmet: Elmo de Couro; Amulet: Amuleto da Mana +1; Weapon1: Machado de Batalha; Weapon2: Tridente do Guerreiro; Legs: Calça de Cota; Hands: Martelo de Mão; Shoes: Botas de Aço; Ring1: Anel de Diamante; Ring2: Anel Vegetal |
| W46 | PaulinhoLOKObr | Hardcore | survival | 20 | 22 | 28.48 | 5803 | 766 | 552 | 350 | 133 | 484 | defesa + sustento | Tremor de Bigorna, Quebra-Guarda, Respirar Fundo, Baluarte | Corpo Inviolável, Postura Fechada, Passo de Corça ×3, Passos Leves, Respiração Contada, Toque do Dragão, Casco Calejado, Escudo da Fé, Coração de Ferro ×3, Bebida dos Deuses, Essência Fluída ×3, Boca de Sangue, Pele de Sal, Sede Silenciosa, Fúria Berserker | Helmet: Capacete de Ferro; Amulet: Amuleto de Pedra; Weapon1: Espada Longa; Weapon2: Clava de Madeira; Body: Armadura de Fenrir; Legs: Calça de Cota +1; Hands: Luvas de Titânio +1; Shoes: Botas de Ferro; Ring1: Anel de Diamante +1; Ring2: Anel Vegetal +1 |
| W53 | babi | Hardcore | economy | 20 | 24 | 28.48 | 6153 | 1208 | 667 | 460 | 153 | 572 | sustento | Rasgo de Gancho, Postura de Muro, Sangue nos Olhos, Marca do Açougueiro | Postura Fechada ×2, Sede Silenciosa, Boca de Sangue ×5, Reserva Arcana ×2, Essência Fluída, Sangue de Guerreiro ×2, Músculos de Aço, Olho de Águia ×2, Olho de Caçador ×2, Alma Eterna, Essência Pura, Respiração Contada, Pele Grossa ×2 | Helmet: Elmo de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Pá de Batalha; Weapon2: Clava Pesada; Body: Peitoral de Cota; Legs: Calça de Cota; Hands: Luvas de Titânio +2; Shoes: Tamancos de Madeira; Ring1: Anel de Diamante; Ring2: Anel do Rubi |
| W02 | alanzoka | Conservador | survival | 20 | 23 | 28.37 | 7387 | 845 | 596 | 363 | 127 | 495 | defesa + sustento | Golpe Poderoso, Respirar Fundo, Soco de Placa, Guarda Cruzada | Passo de Corça, Passos Leves, Pele Grossa, Postura Fechada ×2, Escudo da Fé, Essência Fluída ×2, Sangue de Guerreiro ×2, Pele de Sal ×3, Bebida dos Deuses, Olho de Águia, Mente Serena, Músculos de Aço, Boca de Sangue, Alma Eterna, Casco Calejado ×2, Coração de Ferro | Helmet: Capacete de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada Longa; Weapon2: Espada de Treino +1; Body: Colete de Pano; Legs: Calça de Pano; Hands: Luvas de Aço; Shoes: Botas de Ferro; Ring1: Anel de Diamante; Ring2: Anel do Rubi |
| W03 | jukes | Conservador | survival | 21 | 22 | 28.14 | 5515 | 841 | 532 | 337 | 125 | 454 | defesa + sustento | Golpe Poderoso, Respirar Fundo, Mira Calma, Leitura de Terreno | Bênção Divina ×2, Respiração Contada ×3, Músculos de Aço, Alma Eterna ×2, Essência Fluída, Olho de Águia, Pele Grossa ×3, Pele de Sal, Coração de Ferro, Boca de Sangue, Mente Serena ×2, Ódio Antigo, Sangue de Guerreiro, Casco Calejado | Helmet: Capacete de Ferro; Amulet: Amuleto de Ouro +1; Weapon1: Porrete +1; Weapon2: Adaga de Madeira +1; Legs: Perneiras de Aço; Hands: Luvas de Aço +1; Shoes: Botas de Ferro; Ring1: Anel Vegetal; Ring2: Anel de Palha |
| W61 | Tealzlol | Conservador | survival | 17 | 19 | 28.14 | 4334 | 510 | 395 | 250 | 81 | 351 | crítico + sustento | Golpe Poderoso, Mira Calma, Fôlego de Marcha, Ritmo de Duelo | Olho de Águia ×2, Passo de Corça, Postura Fechada ×2, Sede Silenciosa, Sangue de Guerreiro, Escudo da Fé ×2, Pele de Sal ×2, Músculos de Aço, Corpo Inviolável, Olho de Caçador, Boca de Sangue ×2, Sede de Sangue, Toque do Dragão | Helmet: Elmo de Ferro; Amulet: Amuleto de Prata; Weapon1: Espada do Universo; Weapon2: Espada do Universo; Body: Armadura Divina; Legs: Bermuda de Couro; Hands: Luvas de Aço; Shoes: Botas de Aço; Ring1: Anel de Couro; Ring2: Anel de Bronze |
| W09 | brino | Conservador | offense | 17 | 18 | 28.02 | 4119 | 446 | 347 | 212 | 74 | 338 | crítico + controle | Cutelada, Investida, Areia no Chão, Fúria | Casco Calejado, Pulso Certeiro ×2, Sangue de Vidente ×2, Sangue Tóxico, Coração de Ferro, Unha Suja, Músculos de Aço, Boca de Sangue, Olho de Águia, Fúria Berserker, Ódio Antigo, Sangue de Guerreiro, Fio Serrilhado, Ódio Baixo, Cabeça Dura | Helmet: Elmo de Dragão; Amulet: Amuleto da Vida; Weapon1: Arco Composto; Weapon2: Faca de Caça; Body: Armadura Divina; Legs: Perneiras de Ferro; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda |
| W14 | G0ularte | Conservador | offense | 19 | 21 | 28.02 | 4354 | 812 | 508 | 312 | 112 | 420 | crítico + controle + sustento | Mira Calma, Investida, Tomar Fôlego, Areia no Chão | Passo de Corça ×2, Ódio Baixo, Fúria Berserker, Músculos de Aço ×4, Sangue de Vidente, Olho de Águia ×3, Bênção Divina, Sangue de Guerreiro, Toque do Dragão, Herança do Abismo, Coração de Ferro, Postura Fechada, Voz no Escuro ×2 | Helmet: Elmo de Dragão +1; Amulet: Amuleto da Mana +1; Weapon1: Machado de Guerra; Weapon2: Espada de Treino +1; Body: Armadura de Couro; Legs: Perneiras de Aço; Hands: Manoplas de Ferro; Shoes: Botas de Corrida; Ring1: Anel de Ouro; Ring2: Anel de Palha |
| W18 | PlayHard | Conservador | economy | 17 | 21 | 28.02 | 4339 | 946 | 495 | 289 | 135 | 428 | sem canal dominante | Resistência Heróica, Mira Calma, Quebra-Guarda, Gancho e Corda | Sorte de Principiante ×4, Sangue de Guerreiro, Coração de Ferro ×2, Boca de Sangue, Essência Fluída, Músculos de Aço, Reserva Arcana ×3, Poço Fundo ×2, Pele de Sal, Respiração Contada, Mente Serena, Ritmo Profano, Sede de Sangue | Helmet: Elmo de Ferro; Amulet: Amuleto da Agilidade; Weapon1: Gládio de Ferro; Weapon2: Porrete +1; Body: Colete da Resistência; Legs: Calça de Ferro; Hands: Luvas de Titânio +2; Shoes: Tamancos de Madeira; Ring1: Anel de Diamante +1; Ring2: Anel do Rubi +1 |
| W52 | SkipNhO | Hardcore | economy | 19 | 23 | 28.02 | 7167 | 766 | 650 | 386 | 132 | 445 | defesa + sustento | Golpe Poderoso, Postura de Muro, Pisada de Ferro, Juramento da Muralha | Boca de Sangue, Sede Silenciosa ×2, Bebida dos Deuses, Sangue de Guerreiro, Sorte de Principiante ×4, Respiração Contada ×3, Poço Fundo, Pele de Sal, Alquimia do Desespero, Olho de Águia ×2, Passos Leves, Ritmo Profano, Essência Viva, Fome de Batalha, Mãos de Midas | Helmet: Elmo de Madeira; Amulet: Amuleto da Vida +2; Weapon1: Bastão Cru +1; Weapon2: Adaga de Madeira +1; Body: Jaqueta de Couro; Hands: Luvas de Aço +1; Shoes: Botas de Corrida; Ring1: Anel de Palha +1; Ring2: Anel Vegetal |
| W04 | belrodrigues | Conservador | survival | 19 | 21 | 27.91 | 5834 | 603 | 515 | 289 | 112 | 414 | defesa | Fúria, Investida, Fôlego de Marcha, Mira Calma | Olho de Águia, Pele de Adamântio, Passo de Corça ×3, Essência Fluída, Passos Leves ×2, Sede Silenciosa, Coração de Ferro ×3, Lâmina Afiada, Pele Grossa, Postura Fechada ×3, Pele de Sal, Músculos de Aço, Sangue de Guerreiro | Helmet: Elmo de Aço; Amulet: Amuleto da Vida +2; Weapon1: Machado de Batalha; Weapon2: Espada de Aço; Body: Armadura de Espinhos; Legs: Perneiras de Aço; Hands: Manoplas de Ferro; Shoes: Botas de Aço; Ring1: Anel da Esmeralda; Ring2: Anel do Rubi +1 |
| W05 | Dilera | Conservador | survival | 19 | 21 | 27.91 | 5077 | 868 | 476 | 320 | 114 | 424 | defesa + sustento | Golpe Poderoso, Investida, Couraça Improvisada, Tomar Fôlego | Pele Grossa ×4, Sede Silenciosa ×2, Passos Leves ×2, Boca de Sangue, Ritmo Profano, Poço Fundo, Coração de Ferro ×2, Passo de Corça, Pele de Adamântio, Essência Fluída, Alquimia do Desespero, Casco Calejado, Músculos de Aço, Coração de Titã | Helmet: Elmo de Aço; Amulet: Amuleto da Mana +1; Weapon1: Gravetos Mágicos; Weapon2: Adaga de Madeira +1; Body: Armadura de Cota de Malha; Legs: Bermuda de Couro; Hands: Luvas de Aço +1; Shoes: Botas de Ferro; Ring1: Anel de Diamante +1; Ring2: Anel de Bronze +1 |
| W06 | Baiano | Conservador | survival | 20 | 21 | 27.91 | 4349 | 803 | 507 | 316 | 117 | 428 | defesa + sustento | Tomar Fôlego, Mira Calma, Ritmo de Duelo, Cutelada | Passo de Corça, Sangue de Guerreiro ×3, Reserva Arcana, Pele de Sal ×2, Casco Calejado, Pele Grossa ×2, Coração de Ferro ×2, Postura Fechada, Mente Serena, Instinto Frio, Olho de Caçador, Sede Silenciosa ×2, Ódio Baixo, Músculos de Aço | Helmet: Capacete de Couro; Amulet: Amuleto da Mana +1; Weapon1: Porrete; Weapon2: Gravetos Mágicos; Body: Armadura de Couro; Legs: Bermuda de Couro; Hands: Luvas de Titânio +2; Shoes: Botas de Ferro; Ring1: Anel da Esmeralda; Ring2: Anel de Palha |
| W17 | k13tv | Conservador | economy | 18 | 23 | 27.91 | 5439 | 806 | 671 | 366 | 121 | 495 | defesa + sustento | Golpe Poderoso, Mira Calma, Fio no Rebite, Guarda Cruzada | Poço Fundo ×2, Essência Viva ×4, Bebida dos Deuses ×4, Toque do Dragão, Alquimia do Desespero, Coração de Ferro, Alma Eterna, Sorte de Principiante ×3, Fúria Berserker, Pele Grossa, Sangue de Vidente, Respiração Contada, Olho de Caçador | Helmet: Elmo de Aço; Amulet: Amuleto da Força; Weapon1: Espada da Vingança; Weapon2: Porrete +2; Body: Armadura de Cota de Malha; Legs: Bermuda de Couro; Hands: Martelo de Mão; Shoes: Botas de Ferro; Ring1: Anel do Rubi +1; Ring2: Anel da Esmeralda +1 |
| W45 | Hayashii | Hardcore | survival | 20 | 22 | 27.91 | 4939 | 898 | 554 | 324 | 119 | 457 | defesa + sustento | Golpe Poderoso, Quebra-Guarda, Quebra-Ossos, Baluarte | Pele de Sal ×3, Postura Fechada ×2, Coração de Ferro ×4, Alma Eterna, Pele Grossa, Boca de Sangue ×2, Sangue de Guerreiro, Passo de Corça ×2, Olho de Caçador ×2, Voracidade, Músculos de Aço, Sede Silenciosa | Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +1; Weapon1: Arco Composto; Weapon2: Bastão Cru +1; Body: Armadura de Fenrir; Legs: Perneiras de Couro; Hands: Luvas de Titânio +1; Shoes: Botas de Corrida; Ring1: Anel de Palha; Ring2: Anel de Couro |
| W51 | suetam1v4 | Hardcore | offense | 19 | 21 | 27.91 | 5734 | 579 | 516 | 297 | 108 | 380 | sem canal dominante | Golpe Duplo, Tremor de Bigorna, Areia no Chão, Postura de Muro | Fio Serrilhado ×2, Toque do Dragão, Passo de Corça ×2, Ódio Antigo, Músculos de Aço ×4, Fúria Berserker ×2, Olho de Caçador, Instinto Frio, Sangue de Guerreiro, Herança do Abismo, Pulso Certeiro, Unha Suja, Lâmina Afiada, Pele Grossa | Helmet: Elmo de Ferro; Amulet: Amuleto de Prata +1; Weapon1: Porrete; Weapon2: Faca de Caça; Body: Cota Leve; Legs: Perneiras de Aço; Hands: Manoplas de Ferro +1; Shoes: Tamancos de Madeira; Ring1: Anel de Aço +1; Ring2: Anel Vegetal |
| W07 | yayahuz | Conservador | survival | 20 | 22 | 27.79 | 6296 | 674 | 596 | 355 | 120 | 428 | defesa + sustento | Golpe Poderoso, Mira Calma, Sede de Batalha, Tomar Fôlego | Coração de Ferro ×5, Pele Grossa ×2, Escudo da Fé, Sangue de Guerreiro ×2, Casco Calejado, Pele de Sal ×2, Essência Fluída, Bebida dos Deuses ×2, Pele de Adamântio, Postura Fechada ×2, Boca de Sangue, Toque do Dragão | Helmet: Elmo de Aço; Amulet: Amuleto da Vida; Weapon1: Porrete; Weapon2: Adaga de Madeira +1; Body: Cota Leve; Legs: Armadura de Camisa; Hands: Manoplas de Ferro +1; Shoes: Botas de Corrida; Ring1: Anel de Couro; Ring2: Anel Vegetal |
| W12 | blackoutz | Conservador | offense | 19 | 20 | 27.79 | 3915 | 517 | 428 | 264 | 94 | 334 | crítico + defesa | Golpe Duplo, Mira Calma, Baluarte, Encarar | Passo de Corça ×2, Instinto Frio, Sangue de Vidente ×2, Agulha no Osso, Ódio Antigo, Sede de Sangue, Unha Suja, Olho de Águia, Pele Grossa, Músculos de Aço ×2, Fio Serrilhado, Sangue de Guerreiro, Ritmo Profano, Alma Eterna, Olho de Caçador, Lâmina do Juízo | Helmet: Bandana de Tecido; Weapon1: Espada Lendária +1; Weapon2: Cajado da Galáxia; Body: Armadura de Espinhos; Legs: Armadura de Camisa; Hands: Luvas de Couro; Ring1: Anel de Bronze; Ring2: Anel Vegetal |
| W21 | boltz | Conservador | economy | 17 | 21 | 27.79 | 5385 | 746 | 473 | 308 | 104 | 389 | sustento | Investida, Soco de Placa, Leitura de Terreno, Olho de Ferreiro | Essência Viva, Ritmo Profano ×2, Sorte de Principiante ×3, Respiração Contada ×2, Mãos de Midas, Reserva Arcana, Poço Fundo ×2, Coração de Ferro ×2, Mente Serena, Bebida dos Deuses ×2, Boca de Sangue ×3 | Helmet: Elmo de Couro; Amulet: Amuleto de Prata +1; Weapon1: Machado de Guerra +1; Weapon2: Espada da Vingança; Body: Armadura de Espinhos; Legs: Calça de Cota; Hands: Luvas de Aço +1; Shoes: Botas de Aço; Ring1: Anel da Fênix +1; Ring2: Anel da Esmeralda |
| W48 | Bagi | Hardcore | survival | 18 | 20 | 27.79 | 5319 | 538 | 440 | 258 | 94 | 421 | defesa + sustento | Golpe Poderoso, Respirar Fundo, Mira Calma, Olho Treinado | Postura Fechada ×4, Sede Silenciosa ×2, Escudo da Fé, Toque do Dragão, Casco Calejado ×2, Bebida dos Deuses, Passos Leves ×2, Pele de Sal, Sangue de Guerreiro ×2, Coração de Ferro, Passo de Corça, Músculos de Aço | Helmet: Elmo de Ferro; Amulet: Amuleto da Vida +1; Weapon1: Espada da Vingança; Weapon2: Bastão Cru; Body: Armadura Divina; Legs: Perneiras de Aço; Hands: Luvas de Aço; Shoes: Botas de Aço; Ring1: Anel de Couro; Accessory: Talismã do Viajante +1 |
| W57 | Coringa | Conservador | offense | 18 | 20 | 27.79 | 4033 | 568 | 482 | 309 | 92 | 401 | sem canal dominante | Cutelada, Golpe Devastador, Areia no Chão, Escudo Protetor | Ódio Baixo ×4, Pulso Certeiro, Olho de Caçador ×2, Lâmina Lendária, Fúria Berserker ×2, Coração de Ferro, Sangue de Vidente, Postura Fechada, Passos Leves, Ódio Antigo, Instinto Frio, Toque do Dragão, Escudo da Fé, Herança do Abismo | Helmet: Elmo de Dragão +1; Amulet: Amuleto de Pedra; Weapon1: Lâmina Veloz +1; Weapon2: Machado Enferrujado; Body: Armadura Divina; Legs: Bermuda de Couro; Hands: Luvas de Aço; Shoes: Botas de Pano; Ring1: Anel de Diamante; Ring2: Anel da Fênix +1; Accessory: Talismã do Viajante +1 |

## Chave

```
Fase de 64
   1. Smzinho (29.8) × G0ularte (28.0)  →  Smzinho
   2. sofiaespanha (29.3) × brino (28.0)  →  sofiaespanha
   3. gafallen (29.9) × blackoutz (27.8)  →  gafallen
   4. Bagi (27.8) × loud_thurzin (29.9)  →  loud_thurzin
   5. fnxLNTC (29.5) × hastad (28.6)  →  fnxLNTC
   6. yayahuz (27.8) × k13tv (27.9)  →  yayahuz
   7. Dilera (27.9) × JonVlogs (28.6)  →  JonVlogs
   8. Coringa (27.8) × LuquEt4 (29.9)  →  LuquEt4
   9. liminhag0d (29.6) × tioorochitwitch (29.4)  →  tioorochitwitch
  10. MeikodRJ (29.8) × Tenz (28.7)  →  MeikodRJ
  11. alanzoka (28.4) × Bisteconee (28.6)  →  Bisteconee
  12. TheBurntPeanut (29.6) × DavyJones (30.0)  →  DavyJones
  13. SkipNhO (28.0) × Tealzlol (28.1)  →  SkipNhO
  14. boltz (27.8) × lubatv (29.2)  →  lubatv
  15. suetam1v4 (27.9) × babi (28.5)  →  babi
  16. aXtLOL (29.8) × brtt (30.0)  →  aXtLOL
  17. frttt (29.5) × belrodrigues (27.9)  →  frttt
  18. bakzera (30.0) × furq (29.5)  →  bakzera
  19. calango (28.6) × NOBRU (29.8)  →  NOBRU
  20. coldzin (29.6) × Neskwga (29.4)  →  Neskwga
  21. PlayHard (28.0) × xandfps (28.5)  →  xandfps
  22. Gaules (30.0) × tteuw (29.2)  →  Gaules
  23. casimito (29.8) × YoDa (29.4)  →  YoDa
  24. Forever (28.7) × XANDAOOGOD (29.6)  →  XANDAOOGOD
  25. Patriota (29.9) × jovirone (29.5)  →  jovirone
  26. yeTz (29.9) × dona (29.1)  →  yeTz
  27. fer (30.0) × Baiano (27.9)  →  fer
  28. Felps (29.6) × Hayashii (27.9)  →  Felps
  29. RazaH (29.1) × mount (29.5)  →  RazaH
  30. jukes (28.1) × gabepeixe (28.6)  →  jukes
  31. aspaszin (29.3) × sacy (29.5)  →  sacy
  32. RNakano (29.6) × PaulinhoLOKObr (28.5)  →  RNakano
Fase de 32
   1. Smzinho (29.8) × sofiaespanha (29.3)  →  Smzinho
   2. gafallen (29.9) × loud_thurzin (29.9)  →  gafallen
   3. fnxLNTC (29.5) × yayahuz (27.8)  →  fnxLNTC
   4. JonVlogs (28.6) × LuquEt4 (29.9)  →  LuquEt4
   5. tioorochitwitch (29.4) × MeikodRJ (29.8)  →  MeikodRJ
   6. Bisteconee (28.6) × DavyJones (30.0)  →  DavyJones
   7. SkipNhO (28.0) × lubatv (29.2)  →  lubatv
   8. babi (28.5) × aXtLOL (29.8)  →  aXtLOL
   9. frttt (29.5) × bakzera (30.0)  →  frttt
  10. NOBRU (29.8) × Neskwga (29.4)  →  NOBRU
  11. xandfps (28.5) × Gaules (30.0)  →  Gaules
  12. YoDa (29.4) × XANDAOOGOD (29.6)  →  XANDAOOGOD
  13. jovirone (29.5) × yeTz (29.9)  →  jovirone
  14. fer (30.0) × Felps (29.6)  →  fer
  15. RazaH (29.1) × jukes (28.1)  →  jukes
  16. sacy (29.5) × RNakano (29.6)  →  RNakano
Oitavas
   1. Smzinho (29.8) × gafallen (29.9)  →  gafallen
   2. fnxLNTC (29.5) × LuquEt4 (29.9)  →  LuquEt4
   3. MeikodRJ (29.8) × DavyJones (30.0)  →  MeikodRJ
   4. lubatv (29.2) × aXtLOL (29.8)  →  lubatv
   5. frttt (29.5) × NOBRU (29.8)  →  frttt
   6. Gaules (30.0) × XANDAOOGOD (29.6)  →  XANDAOOGOD
   7. jovirone (29.5) × fer (30.0)  →  fer
   8. jukes (28.1) × RNakano (29.6)  →  RNakano
Quartas
   1. gafallen (29.9) × LuquEt4 (29.9)  →  gafallen
   2. MeikodRJ (29.8) × lubatv (29.2)  →  lubatv
   3. frttt (29.5) × XANDAOOGOD (29.6)  →  frttt
   4. fer (30.0) × RNakano (29.6)  →  fer
Semifinal
   1. gafallen (29.9) × lubatv (29.2)  →  lubatv
   2. frttt (29.5) × fer (30.0)  →  fer
Final
   1. lubatv (29.2) × fer (30.0)  →  fer
Campeão: fer (W64)
```

## Resultados por fase

### Fase de 64

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Smzinho (29.75) | G0ularte (28.02) | **Smzinho** | 19 | 2673/5701 | +1.73 |  |
| 2 | sofiaespanha (29.29) | brino (28.02) | **sofiaespanha** | 23 | 4528/7757 | +1.27 |  |
| 3 | gafallen (29.87) | blackoutz (27.79) | **gafallen** | 10 | 1334/3973 | +2.07 |  |
| 4 | Bagi (27.79) | loud_thurzin (29.87) | **loud_thurzin** | 35 | 688/5110 | +2.07 |  |
| 5 | fnxLNTC (29.52) | hastad (28.60) | **fnxLNTC** | 27 | 1865/5355 | +0.92 |  |
| 6 | yayahuz (27.79) | k13tv (27.91) | **yayahuz** | 21 | 3788/6296 | -0.12 | sim |
| 7 | Dilera (27.91) | JonVlogs (28.60) | **JonVlogs** | 64 | 2640/6314 | +0.69 |  |
| 8 | Coringa (27.79) | LuquEt4 (29.87) | **LuquEt4** | 17 | 5123/7257 | +2.07 |  |
| 9 | liminhag0d (29.64) | tioorochitwitch (29.41) | **tioorochitwitch** | 25 | 945/7189 | -0.23 | sim |
| 10 | MeikodRJ (29.75) | Tenz (28.71) | **MeikodRJ** | 36 | 931/4969 | +1.04 |  |
| 11 | alanzoka (28.37) | Bisteconee (28.60) | **Bisteconee** | 26 | 148/4779 | +0.23 |  |
| 12 | TheBurntPeanut (29.64) | DavyJones (29.98) | **DavyJones** | 16 | 1722/5333 | +0.35 |  |
| 13 | SkipNhO (28.02) | Tealzlol (28.14) | **SkipNhO** | 22 | 4250/7167 | -0.12 | sim |
| 14 | boltz (27.79) | lubatv (29.17) | **lubatv** | 15 | 2423/5275 | +1.38 |  |
| 15 | suetam1v4 (27.91) | babi (28.48) | **babi** | 15 | 1371/6153 | +0.58 |  |
| 16 | aXtLOL (29.75) | brtt (29.98) | **aXtLOL** | 13 | 2470/5454 | -0.23 | sim |
| 17 | frttt (29.52) | belrodrigues (27.91) | **frttt** | 20 | 3590/5379 | +1.61 |  |
| 18 | bakzera (29.98) | furq (29.52) | **bakzera** | 39 | 529/5860 | +0.46 |  |
| 19 | calango (28.60) | NOBRU (29.75) | **NOBRU** | 64 | 746/5469 | +1.15 |  |
| 20 | coldzin (29.64) | Neskwga (29.41) | **Neskwga** | 42 | 324/6216 | -0.23 | sim |
| 21 | PlayHard (28.02) | xandfps (28.48) | **xandfps** | 14 | 212/4259 | +0.46 |  |
| 22 | Gaules (29.98) | tteuw (29.17) | **Gaules** | 21 | 1317/5209 | +0.81 |  |
| 23 | casimito (29.75) | YoDa (29.41) | **YoDa** | 12 | 2399/5464 | -0.35 | sim |
| 24 | Forever (28.71) | XANDAOOGOD (29.64) | **XANDAOOGOD** | 14 | 3615/5684 | +0.92 |  |
| 25 | Patriota (29.87) | jovirone (29.52) | **jovirone** | 30 | 3029/6345 | -0.35 | sim |
| 26 | yeTz (29.87) | dona (29.06) | **yeTz** | 59 | 1856/7383 | +0.81 |  |
| 27 | fer (29.98) | Baiano (27.91) | **fer** | 15 | 3978/5977 | +2.07 |  |
| 28 | Felps (29.64) | Hayashii (27.91) | **Felps** | 14 | 2557/4098 | +1.73 |  |
| 29 | RazaH (29.06) | mount (29.52) | **RazaH** | 31 | 509/5285 | -0.46 | sim |
| 30 | jukes (28.14) | gabepeixe (28.60) | **jukes** | 18 | 1110/5515 | -0.46 | sim |
| 31 | aspaszin (29.29) | sacy (29.52) | **sacy** | 58 | 1211/7520 | +0.23 |  |
| 32 | RNakano (29.64) | PaulinhoLOKObr (28.48) | **RNakano** | 50 | 4619/8159 | +1.15 |  |

### Fase de 32

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Smzinho (29.75) | sofiaespanha (29.29) | **Smzinho** | 26 | 1519/5701 | +0.46 |  |
| 2 | gafallen (29.87) | loud_thurzin (29.87) | **gafallen** | 26 | 1731/3973 | +0.00 |  |
| 3 | fnxLNTC (29.52) | yayahuz (27.79) | **fnxLNTC** | 54 | 942/5355 | +1.73 |  |
| 4 | JonVlogs (28.60) | LuquEt4 (29.87) | **LuquEt4** | 36 | 3148/7257 | +1.27 |  |
| 5 | tioorochitwitch (29.41) | MeikodRJ (29.75) | **MeikodRJ** | 25 | 1085/4969 | +0.35 |  |
| 6 | Bisteconee (28.60) | DavyJones (29.98) | **DavyJones** | 10 | 3618/5333 | +1.38 |  |
| 7 | SkipNhO (28.02) | lubatv (29.17) | **lubatv** | 33 | 2005/5275 | +1.15 |  |
| 8 | babi (28.48) | aXtLOL (29.75) | **aXtLOL** | 34 | 2006/5454 | +1.27 |  |
| 9 | frttt (29.52) | bakzera (29.98) | **frttt** | 24 | 1218/5379 | -0.46 | sim |
| 10 | NOBRU (29.75) | Neskwga (29.41) | **NOBRU** | 31 | 665/5469 | +0.35 |  |
| 11 | xandfps (28.48) | Gaules (29.98) | **Gaules** | 16 | 723/5209 | +1.50 |  |
| 12 | YoDa (29.41) | XANDAOOGOD (29.64) | **XANDAOOGOD** | 13 | 4339/5684 | +0.23 |  |
| 13 | jovirone (29.52) | yeTz (29.87) | **jovirone** | 39 | 2144/6345 | -0.35 | sim |
| 14 | fer (29.98) | Felps (29.64) | **fer** | 15 | 1651/5977 | +0.35 |  |
| 15 | RazaH (29.06) | jukes (28.14) | **jukes** | 29 | 2703/5515 | -0.92 | sim |
| 16 | sacy (29.52) | RNakano (29.64) | **RNakano** | 63 | 5160/8159 | +0.12 |  |

### Oitavas

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | Smzinho (29.75) | gafallen (29.87) | **gafallen** | 23 | 1510/3973 | +0.12 |  |
| 2 | fnxLNTC (29.52) | LuquEt4 (29.87) | **LuquEt4** | 47 | 2483/7257 | +0.35 |  |
| 3 | MeikodRJ (29.75) | DavyJones (29.98) | **MeikodRJ** | 26 | 895/4969 | -0.23 | sim |
| 4 | lubatv (29.17) | aXtLOL (29.75) | **lubatv** | 31 | 1877/5275 | -0.58 | sim |
| 5 | frttt (29.52) | NOBRU (29.75) | **frttt** | 24 | 2170/5379 | -0.23 | sim |
| 6 | Gaules (29.98) | XANDAOOGOD (29.64) | **XANDAOOGOD** | 13 | 2385/5684 | -0.35 | sim |
| 7 | jovirone (29.52) | fer (29.98) | **fer** | 36 | 2215/5977 | +0.46 |  |
| 8 | jukes (28.14) | RNakano (29.64) | **RNakano** | 41 | 5109/8159 | +1.50 |  |

### Quartas

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | gafallen (29.87) | LuquEt4 (29.87) | **gafallen** | 24 | 1442/3973 | +0.00 |  |
| 2 | MeikodRJ (29.75) | lubatv (29.17) | **lubatv** | 24 | 2288/5275 | -0.58 | sim |
| 3 | frttt (29.52) | XANDAOOGOD (29.64) | **frttt** | 23 | 147/5379 | -0.12 | sim |
| 4 | fer (29.98) | RNakano (29.64) | **fer** | 43 | 2470/5977 | +0.35 |  |

### Semifinal

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | gafallen (29.87) | lubatv (29.17) | **lubatv** | 56 | 217/5275 | -0.69 | sim |
| 2 | frttt (29.52) | fer (29.98) | **fer** | 24 | 1977/5977 | +0.46 |  |

### Final

| # | Lado 1 (OP) | Lado 2 (OP) | Vencedor | Rodadas | HP do vencedor | ΔOP | Zebra |
|---|---|---|---|---|---|---|---|
| 1 | lubatv (29.17) | fer (29.98) | **fer** | 37 | 1165/5977 | +0.81 |  |

## Estatísticas agregadas

> Uma Copa MD1 é uma amostra de 63 duelos sob uma política fixa, com uma seed por confronto. Ela aponta casos para investigar; não prova balanceamento.

### Perfis, políticas e canais na Arena

> Perfil, política, RNG da jornada e RNG do duelo atuam juntos em cada gladiador. As tabelas mostram associações observadas nesta amostra, não efeitos causais isolados.

| Perfil | Participantes | OP médio | Vitórias | Derrotas | Taxa | Dano por partida | Acerto | Críticos (taxa) | Nas oitavas | Nas quartas |
|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | 27 | 28.53 | 9 | 27 | 25.0% | 4937 | 80.1% | 55 (9.7%) | 2 | 0 |
| Moderado | 27 | 29.66 | 48 | 26 | 64.9% | 6353 | 83.5% | 230 (17.7%) | 13 | 7 |
| Hardcore | 10 | 28.40 | 6 | 10 | 37.5% | 5156 | 85.3% | 41 (15.1%) | 1 | 1 |

| Política | Participantes | OP médio | Vitórias | Derrotas | Taxa | Dano por partida | Acerto | Críticos (taxa) | Nas oitavas | Nas quartas |
|---|---|---|---|---|---|---|---|---|---|---|
| survival | 22 | 28.78 | 24 | 21 | 53.3% | 6025 | 82.5% | 150 (16.2%) | 7 | 4 |
| offense | 21 | 29.09 | 13 | 21 | 38.2% | 5254 | 89.7% | 88 (22.9%) | 3 | 1 |
| economy | 21 | 29.11 | 26 | 21 | 55.3% | 5971 | 80.3% | 88 (10.6%) | 6 | 3 |

| Canal da build | Participantes | OP médio | Vitórias | Derrotas | Taxa | Dano por partida | Acerto | Críticos (taxa) | Nas oitavas | Nas quartas |
|---|---|---|---|---|---|---|---|---|---|---|
| crítico | 18 | 29.05 | 14 | 18 | 43.8% | 5893 | 85.9% | 154 (30.7%) | 3 | 2 |
| defesa | 26 | 28.71 | 21 | 25 | 45.7% | 5306 | 83.4% | 104 (12.4%) | 5 | 2 |
| controle | 19 | 29.28 | 11 | 19 | 36.7% | 5244 | 85.9% | 56 (17.1%) | 2 | 0 |
| sustento | 40 | 28.95 | 46 | 39 | 54.1% | 6045 | 81.0% | 228 (13.7%) | 12 | 6 |

Vitórias do perfil da linha sobre o da coluna:

| Vencedor \ Perdedor | Conservador | Moderado | Hardcore |
|---|---|---|---|
| Conservador | 6 | 3 | 0 |
| Moderado | 18 | 21 | 9 |
| Hardcore | 3 | 2 | 1 |

Correlação de postos (Spearman) entre OP e número de vitórias: 0.52.

### Overall Power dos vencedores por fase

| Fase | Partidas | OP médio de quem entrou (mín–máx) | OP médio dos vencedores (mín–máx) | OP médio dos perdedores | Favorito venceu |
|---|---|---|---|---|---|
| Fase de 64 | 32 | 28.99 (27.79–29.98) | 29.35 (27.79–29.98) | 28.62 | 23/32 |
| Fase de 32 | 16 | 29.35 (27.79–29.98) | 29.61 (28.14–29.98) | 29.09 | 13/16 |
| Oitavas | 8 | 29.61 (28.14–29.98) | 29.68 (29.17–29.98) | 29.55 | 4/8 |
| Quartas | 4 | 29.68 (29.17–29.98) | 29.64 (29.17–29.98) | 29.72 | 2/4 |
| Semifinal | 2 | 29.64 (29.17–29.98) | 29.58 (29.17–29.98) | 29.69 | 1/2 |
| Final | 1 | 29.58 (29.17–29.98) | 29.98 (29.98–29.98) | 29.17 | 1/1 |

### Confrontos com as maiores diferenças de OP

| Partida | Vencedor (OP) | Perdedor (OP) | ΔOP | Rodadas |
|---|---|---|---|---|
| Fase de 64 3 — gafallen × blackoutz | gafallen (29.87) | blackoutz (27.79) | +2.07 | 10 |
| Fase de 64 4 — Bagi × loud_thurzin | loud_thurzin (29.87) | Bagi (27.79) | +2.07 | 35 |
| Fase de 64 8 — Coringa × LuquEt4 | LuquEt4 (29.87) | Coringa (27.79) | +2.07 | 17 |
| Fase de 64 27 — fer × Baiano | fer (29.98) | Baiano (27.91) | +2.07 | 15 |
| Fase de 64 1 — Smzinho × G0ularte | Smzinho (29.75) | G0ularte (28.02) | +1.73 | 19 |
| Fase de 64 28 — Felps × Hayashii | Felps (29.64) | Hayashii (27.91) | +1.73 | 14 |
| Fase de 32 3 — fnxLNTC × yayahuz | fnxLNTC (29.52) | yayahuz (27.79) | +1.73 | 54 |
| Fase de 64 17 — frttt × belrodrigues | frttt (29.52) | belrodrigues (27.91) | +1.61 | 20 |
| Fase de 32 11 — xandfps × Gaules | Gaules (29.98) | xandfps (28.48) | +1.50 | 16 |
| Oitavas 8 — jukes × RNakano | RNakano (29.64) | jukes (28.14) | +1.50 | 41 |

### Vitórias de quem tinha o OP menor (19 zebras)

| Partida | Vencedor (OP) | Perdedor (OP) | ΔOP | Rodadas |
|---|---|---|---|---|
| Fase de 32 15 — RazaH × jukes | jukes (28.14) | RazaH (29.06) | -0.92 | 29 |
| Semifinal 1 — gafallen × lubatv | lubatv (29.17) | gafallen (29.87) | -0.69 | 56 |
| Oitavas 4 — lubatv × aXtLOL | lubatv (29.17) | aXtLOL (29.75) | -0.58 | 31 |
| Quartas 2 — MeikodRJ × lubatv | lubatv (29.17) | MeikodRJ (29.75) | -0.58 | 24 |
| Fase de 64 29 — RazaH × mount | RazaH (29.06) | mount (29.52) | -0.46 | 31 |
| Fase de 64 30 — jukes × gabepeixe | jukes (28.14) | gabepeixe (28.60) | -0.46 | 18 |
| Fase de 32 9 — frttt × bakzera | frttt (29.52) | bakzera (29.98) | -0.46 | 24 |
| Fase de 64 23 — casimito × YoDa | YoDa (29.41) | casimito (29.75) | -0.35 | 12 |
| Fase de 64 25 — Patriota × jovirone | jovirone (29.52) | Patriota (29.87) | -0.35 | 30 |
| Fase de 32 13 — jovirone × yeTz | jovirone (29.52) | yeTz (29.87) | -0.35 | 39 |
| Oitavas 6 — Gaules × XANDAOOGOD | XANDAOOGOD (29.64) | Gaules (29.98) | -0.35 | 13 |
| Fase de 64 9 — liminhag0d × tioorochitwitch | tioorochitwitch (29.41) | liminhag0d (29.64) | -0.23 | 25 |
| Fase de 64 16 — aXtLOL × brtt | aXtLOL (29.75) | brtt (29.98) | -0.23 | 13 |
| Fase de 64 20 — coldzin × Neskwga | Neskwga (29.41) | coldzin (29.64) | -0.23 | 42 |
| Oitavas 3 — MeikodRJ × DavyJones | MeikodRJ (29.75) | DavyJones (29.98) | -0.23 | 26 |
| Oitavas 5 — frttt × NOBRU | frttt (29.52) | NOBRU (29.75) | -0.23 | 24 |
| Fase de 64 6 — yayahuz × k13tv | yayahuz (27.79) | k13tv (27.91) | -0.12 | 21 |
| Fase de 64 13 — SkipNhO × Tealzlol | SkipNhO (28.02) | Tealzlol (28.14) | -0.12 | 22 |
| Quartas 3 — frttt × XANDAOOGOD | frttt (29.52) | XANDAOOGOD (29.64) | -0.12 | 23 |

Vencedor × perdedor por faixa medida (1 = 20–22,5 … 4 = 27,5–30): 4→4: 63

### Comparação com a Copa 02 (só o que é comparável)

A Copa 02 tinha três classes e builds montadas à mão; esta, só Guerreiros que vieram de runs reais. Mesma `PoliticaCopa`, mesmo motor, mesmo esquema de seeds por partida. Classe, build e OP diferem, então a comparação descreve as duas amostras, não isola causa.

| Métrica | Copa 02 | Copa 03 |
|---|---|---|
| OP médio | 25.17 | 28.99 |
| Amplitude de OP (máx − mín) | 9.45 | 2.19 |
| Favorito venceu | 52/63 | 44/63 |
| Zebras | 11 | 19 |
| Maior ΔOP de uma zebra | 2.77 | 0.92 |
| Rodadas por partida | 9.48 | 29.06 |
| Golpes que conectaram | 81.9% | 82.8% |
| Críticos por golpe conectado | 17.2% | 15.2% |
| Partidas de uma rodada | 0 | 0 |

### Maiores golpes

| Dano | Crítico | Atacante | Alvo | Ação | Partida | Rodada |
|---|---|---|---|---|---|---|
| 1790 | sim | gafallen (W37) | blackoutz (W12) | Mira Calma | Fase de 64 3 — gafallen × blackoutz | 10 |
| 1485 | sim | PlayHard (W18) | xandfps (W20) | Mira Calma | Fase de 64 21 — PlayHard × xandfps | 5 |
| 1334 | sim | casimito (W55) | YoDa (W33) | Esmagar | Fase de 64 23 — casimito × YoDa | 9 |
| 1323 | sim | gafallen (W37) | Smzinho (W35) | Mira Calma | Oitavas 1 — Smzinho × gafallen | 6 |
| 1323 | sim | gafallen (W37) | Smzinho (W35) | Mira Calma | Oitavas 1 — Smzinho × gafallen | 23 |
| 1315 |  | lubatv (W23) | boltz (W21) | Esmagar | Fase de 64 14 — boltz × lubatv | 14 |
| 1314 | sim | XANDAOOGOD (W47) | Gaules (W36) | Esmagar | Oitavas 6 — Gaules × XANDAOOGOD | 12 |
| 1271 | sim | gafallen (W37) | loud_thurzin (W32) | Mira Calma | Fase de 32 2 — gafallen × loud_thurzin | 6 |
| 1267 | sim | aXtLOL (W43) | brtt (W13) | Mira Calma | Fase de 64 16 — aXtLOL × brtt | 13 |
| 1211 |  | DavyJones (W29) | Bisteconee (W49) | Mira Calma | Fase de 32 6 — Bisteconee × DavyJones | 3 |

Críticos: 326 em 2138 golpes conectados; o maior, 1790 de dano de gafallen (W37) (Mira Calma).

### Partidas mais longas e mais curtas

Mais longas: Fase de 64 19 — calango × NOBRU (64 rodadas); Fase de 64 7 — Dilera × JonVlogs (64 rodadas); Fase de 32 16 — sacy × RNakano (63 rodadas); Fase de 64 26 — yeTz × dona (59 rodadas); Fase de 64 31 — aspaszin × sacy (58 rodadas)

Mais curtas: Fase de 32 6 — Bisteconee × DavyJones (10 rodadas); Fase de 64 3 — gafallen × blackoutz (10 rodadas); Fase de 64 23 — casimito × YoDa (12 rodadas); Fase de 32 12 — YoDa × XANDAOOGOD (13 rodadas); Fase de 64 16 — aXtLOL × brtt (13 rodadas)

Rodadas por partida: 10: 2, 12: 1, 13: 3, 14: 3, 15: 4, 16: 2, 17: 1, 18: 1, 19: 1, 20: 1, 21: 2, 22: 1, 23: 3, 24: 5, 25: 2, 26: 4, 27: 1, 29: 1, 30: 1, 31: 3, 33: 1, 34: 1, 35: 1, 36: 3, 37: 1, 39: 2, 41: 1, 42: 1, 43: 1, 47: 1, 50: 1, 54: 1, 56: 1, 58: 1, 59: 1, 63: 1, 64: 2.

### Uso de skills, buffs, controles e curas

Skills mais usadas: Golpe Poderoso ×492, Mira Calma ×191, Quebra-Guarda ×151, Investida ×136, Cutelada ×108, Escudo Protetor ×83, Soco de Placa ×74, Estocada Seca ×57, Areia no Chão ×56, Couraça Improvisada ×53, Postura de Muro ×49, Tomar Fôlego ×48, Disciplina de Forja ×48, Mão Dupla ×42, Sangue nos Olhos ×42.

Buffs ativados: Escudo Protetor ×83, Couraça Improvisada ×53, Postura de Muro ×49, Disciplina de Forja ×48, Pausa Útil ×42, Guarda Alta ×39, Veterania ×34, Juramento da Muralha ×30, Grito de Guerra ×20, Ritmo de Duelo ×20, Postura Impecável ×18, Fúria ×16, Couro Batido ×15, Leitura de Terreno ×14, Passo Lateral ×13, Fôlego de Marcha ×11, Guarda Cruzada ×9, Imortal ×6, Lâmina Assentada ×6, Fio no Rebite ×5, Baluarte ×5, Olho de Ferreiro ×4.

Status aplicados: vulnerable ×163, bleed ×139, stun ×105, weakened ×78, slowed ×57, fear ×53, poison ×50, hexed ×28, frailty ×18. Tentativas que não pegaram: stun ×1587, bleed ×806, poison ×339, fear ×273, vulnerable ×218, weakened ×66, slowed ×36, hexed ×15, frailty ×11.

Controles que tiram a vez (atordoar, sono, congelar) aplicados: stun ×105, sleep ×0, frozen ×0; ações perdidas por controle no total: 103.

Cura total (skill + roubo de vida): 132312. Quem mais curou: gafallen (W37) 20926, MeikodRJ (W26) 15057, RNakano (W42) 9937, calango (W44) 9850, NOBRU (W40) 6203.

Critério que decidiu a ordem, por rodada: score ×1831.

## Diagnóstico do RNG do duelo

Depois da Copa oficial, 10 confrontos foram repetidos 200 vezes cada, com os mesmos dois gladiadores, a mesma `PoliticaCopa` e seeds novas (`sha256(f"{seed}:rng:{fase}:{índice}:{r}")`), metade com os lados trocados. Nada disso altera o resultado oficial. Foram escolhidos a final, as zebras de maior diferença e os confrontos mais parelhos em OP.

| Confronto | Vencedor oficial (OP) | Perdedor oficial (OP) | Vitórias do vencedor oficial | IC 95% | Rodadas (média) |
|---|---|---|---|---|---|
| Final — lubatv × fer | fer (29.98) | lubatv (29.17) | 174/200 (87.0%) | 81.6%–91.0% | 36.8 |
| Fase de 32 15 — RazaH × jukes (zebra) | jukes (28.14) | RazaH (29.06) | 169/200 (84.5%) | 78.8%–88.9% | 24.8 |
| Semifinal 1 — gafallen × lubatv (zebra) | lubatv (29.17) | gafallen (29.87) | 126/200 (63.0%) | 56.1%–69.4% | 32.2 |
| Oitavas 4 — lubatv × aXtLOL (zebra) | lubatv (29.17) | aXtLOL (29.75) | 181/200 (90.5%) | 85.6%–93.8% | 29.9 |
| Quartas 2 — MeikodRJ × lubatv (zebra) | lubatv (29.17) | MeikodRJ (29.75) | 157/200 (78.5%) | 72.3%–83.6% | 29.6 |
| Fase de 64 29 — RazaH × mount (zebra) | RazaH (29.06) | mount (29.52) | 106/200 (53.0%) | 46.1%–59.8% | 30.0 |
| Fase de 32 2 — gafallen × loud_thurzin | gafallen (29.87) | loud_thurzin (29.87) | 197/200 (98.5%) | 95.7%–99.5% | 26.9 |
| Quartas 1 — gafallen × LuquEt4 | gafallen (29.87) | LuquEt4 (29.87) | 179/200 (89.5%) | 84.5%–93.0% | 29.8 |
| Fase de 32 16 — sacy × RNakano | RNakano (29.64) | sacy (29.52) | 200/200 (100.0%) | 98.1%–100.0% | 60.3 |
| Oitavas 1 — Smzinho × gafallen | gafallen (29.87) | Smzinho (29.75) | 83/200 (41.5%) | 34.9%–48.4% | 21.3 |

Como ler: os três componentes estão separados no experimento só até certo ponto. O RNG da jornada PvE e as decisões do perfil produziram a build (e o OP); aqui ela fica fixa, e só o RNG do duelo varia. Uma taxa perto de 50% diz que, entre esses dois, o duelo é decidido pelo sorteio; perto de 100%, pela build. O experimento não separa o que, dentro da build, veio do perfil e o que veio do RNG da jornada.

## O campeão

**fer (W64)**, Guerreiro nível 23, OP 29.98 (faixa 4), build *Moderado · survival*: defesa + sustento.

- Skills: Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo
- Passivas: Sangue de Guerreiro, Essência Fluída ×4, Coração de Ferro ×4, Instinto Frio, Olho de Águia, Herança do Abismo, Bênção Divina, Postura Fechada, Boca de Sangue ×2, Pele Grossa, Fúria Berserker, Vulto, Músculos de Aço, Sede de Sangue, Escudo da Fé
- Equipamento: Helmet: Capacete de Ferro; Amulet: Amuleto da Mana +2; Weapon1: Cajado de Cristal; Weapon2: Porrete +1; Body: Placa Pesada; Legs: Calça de Cota; Hands: Luvas de Aço +1; Shoes: Botas de Corrida; Ring1: Anel da Esmeralda; Ring2: Anel de Diamante +1; Accessory: Talismã do Viajante +1
- HP 5977, MP 1103, ST 654, MG 446, AG 142, DF 503

| Fase | Adversário (OP) | Rodadas | Dano causado | Dano recebido | Cura | MP | Acertos/erros | Críticos | HP final |
|---|---|---|---|---|---|---|---|---|---|
| Fase de 64 | Baiano (27.91) | 15 | 5611 | 2668 | 669 | 1125 | 11/1 | 5 | 3978/5977 |
| Fase de 32 | Felps (29.64) | 15 | 4891 | 5436 | 1110 | 1033 | 9/0 | 3 | 1651/5977 |
| Oitavas | jovirone (29.52) | 36 | 8158 | 4776 | 1014 | 1806 | 30/2 | 12 | 2215/5977 |
| Quartas | RNakano (29.64) | 43 | 9929 | 4715 | 1208 | 1962 | 37/1 | 7 | 2470/5977 |
| Semifinal | frttt (29.52) | 24 | 5904 | 5311 | 1311 | 1567 | 17/1 | 5 | 1977/5977 |
| Final | lubatv (29.17) | 37 | 5298 | 5494 | 682 | 1858 | 22/11 | 5 | 1165/5977 |

Totais: 170 rodadas, 39791 de dano causado, 28400 recebido, 5994 de cura, 9351 de MP, 131 skills e 35 ataques básicos, 126 acertos, 16 erros, 37 críticos.

## Curiosidades

- Maior zebra: jukes (W03), OP 28.14, eliminou RazaH (W15), OP 29.06 (Fase de 32, diferença de 0.92).
- Vitória mais apertada: frttt (W60) terminou com 147/5379 de HP contra XANDAOOGOD (W47) (Quartas).
- `death_ignore` salvou um golpe letal 3 vez(es): liminhag0d (W59) em Fase de 64 9 — liminhag0d × tioorochitwitch; Tenz (W08) em Fase de 64 10 — MeikodRJ × Tenz; aXtLOL (W43) em Oitavas 4 — lubatv × aXtLOL.
- 13 partida(s) terminaram num golpe crítico; o maior deles tirou 1790 de HP.
- 6 partida(s) foram vencidas por quem NUNCA agiu primeiro, como frttt (W60) em Fase de 64 17 — frttt × belrodrigues.
- O gladiador extraído mais fundo é XANDAOOGOD (W47), andar 22 (nível 23, OP 29.64); o mais raso, tteuw (W19), andar 16 (nível 19, OP 29.17).
- Na Arena, o perfil com a maior taxa de vitória foi o Moderado (48–26); o perfil decide a jornada PvE, e no duelo todos usam a mesma `PoliticaCopa`.
- Correlação de postos (Spearman) entre OP e vitórias na Copa: 0.52.
- 16 das 63 vitórias saíram sem nenhum crítico do vencedor.

## Auditoria resumida das 63 partidas

Cada partida rodou sem instrumentação e auditada, com a mesma seed; as verificações são as das Copas 01 e 02.

| Partida | Seed | Rodadas | Sorteios | Fidelidade | Coerência |
|---|---|---|---|---|---|
| Fase de 64 1 — Smzinho × G0ularte | `15680085034463772073` | 19 | 96 | idêntica | ok |
| Fase de 64 2 — sofiaespanha × brino | `1531925714914894290` | 23 | 132 | idêntica | ok |
| Fase de 64 3 — gafallen × blackoutz | `5116284588478050991` | 10 | 60 | idêntica | ok |
| Fase de 64 4 — Bagi × loud_thurzin | `9981607956343163088` | 35 | 182 | idêntica | ok |
| Fase de 64 5 — fnxLNTC × hastad | `8825721451302242450` | 27 | 146 | idêntica | ok |
| Fase de 64 6 — yayahuz × k13tv | `1388346834123313183` | 21 | 95 | idêntica | ok |
| Fase de 64 7 — Dilera × JonVlogs | `17893717569376441782` | 64 | 220 | idêntica | ok |
| Fase de 64 8 — Coringa × LuquEt4 | `3601920012618483097` | 17 | 62 | idêntica | ok |
| Fase de 64 9 — liminhag0d × tioorochitwitch | `1339762318995372611` | 25 | 178 | idêntica | ok |
| Fase de 64 10 — MeikodRJ × Tenz | `11447462072290798616` | 36 | 188 | idêntica | ok |
| Fase de 64 11 — alanzoka × Bisteconee | `17311463052517239433` | 26 | 122 | idêntica | ok |
| Fase de 64 12 — TheBurntPeanut × DavyJones | `13270816932769152964` | 16 | 89 | idêntica | ok |
| Fase de 64 13 — SkipNhO × Tealzlol | `15329195925884803276` | 22 | 83 | idêntica | ok |
| Fase de 64 14 — boltz × lubatv | `15144210590413717805` | 15 | 74 | idêntica | ok |
| Fase de 64 15 — suetam1v4 × babi | `12954259252142384667` | 15 | 86 | idêntica | ok |
| Fase de 64 16 — aXtLOL × brtt | `9777167068430930388` | 13 | 81 | idêntica | ok |
| Fase de 64 17 — frttt × belrodrigues | `3553688020881821888` | 20 | 101 | idêntica | ok |
| Fase de 64 18 — bakzera × furq | `17700058813706348266` | 39 | 217 | idêntica | ok |
| Fase de 64 19 — calango × NOBRU | `16730638574478466645` | 64 | 306 | idêntica | ok |
| Fase de 64 20 — coldzin × Neskwga | `14112623888638305206` | 42 | 272 | idêntica | ok |
| Fase de 64 21 — PlayHard × xandfps | `5218381777248435903` | 14 | 89 | idêntica | ok |
| Fase de 64 22 — Gaules × tteuw | `7026902445234392979` | 21 | 106 | idêntica | ok |
| Fase de 64 23 — casimito × YoDa | `2845307736597708112` | 12 | 55 | idêntica | ok |
| Fase de 64 24 — Forever × XANDAOOGOD | `10313238421112521520` | 14 | 74 | idêntica | ok |
| Fase de 64 25 — Patriota × jovirone | `5100617546764134280` | 30 | 134 | idêntica | ok |
| Fase de 64 26 — yeTz × dona | `6093964812114948536` | 59 | 216 | idêntica | ok |
| Fase de 64 27 — fer × Baiano | `3743995336007600765` | 15 | 71 | idêntica | ok |
| Fase de 64 28 — Felps × Hayashii | `14407454639189636163` | 14 | 79 | idêntica | ok |
| Fase de 64 29 — RazaH × mount | `989407218878997817` | 31 | 160 | idêntica | ok |
| Fase de 64 30 — jukes × gabepeixe | `8932018971394209653` | 18 | 89 | idêntica | ok |
| Fase de 64 31 — aspaszin × sacy | `15802958274225019879` | 58 | 200 | idêntica | ok |
| Fase de 64 32 — RNakano × PaulinhoLOKObr | `10076971382503481094` | 50 | 197 | idêntica | ok |
| Fase de 32 1 — Smzinho × sofiaespanha | `7745829876537198877` | 26 | 125 | idêntica | ok |
| Fase de 32 2 — gafallen × loud_thurzin | `1365251658866500399` | 26 | 134 | idêntica | ok |
| Fase de 32 3 — fnxLNTC × yayahuz | `9762848969340625506` | 54 | 278 | idêntica | ok |
| Fase de 32 4 — JonVlogs × LuquEt4 | `9583618915835800529` | 36 | 154 | idêntica | ok |
| Fase de 32 5 — tioorochitwitch × MeikodRJ | `4874100928450260687` | 25 | 181 | idêntica | ok |
| Fase de 32 6 — Bisteconee × DavyJones | `15408156701190931824` | 10 | 66 | idêntica | ok |
| Fase de 32 7 — SkipNhO × lubatv | `7325394041001865093` | 33 | 141 | idêntica | ok |
| Fase de 32 8 — babi × aXtLOL | `12181601168899415817` | 34 | 142 | idêntica | ok |
| Fase de 32 9 — frttt × bakzera | `11442713055583528856` | 24 | 135 | idêntica | ok |
| Fase de 32 10 — NOBRU × Neskwga | `7082001218792862799` | 31 | 193 | idêntica | ok |
| Fase de 32 11 — xandfps × Gaules | `10611109298908495297` | 16 | 100 | idêntica | ok |
| Fase de 32 12 — YoDa × XANDAOOGOD | `17524866069901069562` | 13 | 62 | idêntica | ok |
| Fase de 32 13 — jovirone × yeTz | `3753158130026634828` | 39 | 125 | idêntica | ok |
| Fase de 32 14 — fer × Felps | `4743871819551685823` | 15 | 75 | idêntica | ok |
| Fase de 32 15 — RazaH × jukes | `5903575241729991190` | 29 | 130 | idêntica | ok |
| Fase de 32 16 — sacy × RNakano | `6729932908895877751` | 63 | 232 | idêntica | ok |
| Oitavas 1 — Smzinho × gafallen | `8956104733299499117` | 23 | 101 | idêntica | ok |
| Oitavas 2 — fnxLNTC × LuquEt4 | `15604872752174960703` | 47 | 223 | idêntica | ok |
| Oitavas 3 — MeikodRJ × DavyJones | `17158717865381310413` | 26 | 165 | idêntica | ok |
| Oitavas 4 — lubatv × aXtLOL | `3009443185611807458` | 31 | 142 | idêntica | ok |
| Oitavas 5 — frttt × NOBRU | `209543163798074548` | 24 | 112 | idêntica | ok |
| Oitavas 6 — Gaules × XANDAOOGOD | `17965660940518739940` | 13 | 64 | idêntica | ok |
| Oitavas 7 — jovirone × fer | `18064589888594402206` | 36 | 164 | idêntica | ok |
| Oitavas 8 — jukes × RNakano | `9536441814756278971` | 41 | 168 | idêntica | ok |
| Quartas 1 — gafallen × LuquEt4 | `16121932450484780189` | 24 | 122 | idêntica | ok |
| Quartas 2 — MeikodRJ × lubatv | `3701790827052938640` | 24 | 121 | idêntica | ok |
| Quartas 3 — frttt × XANDAOOGOD | `239342085775483302` | 23 | 116 | idêntica | ok |
| Quartas 4 — fer × RNakano | `9149351047459092604` | 43 | 197 | idêntica | ok |
| Semifinal 1 — gafallen × lubatv | `10346392674869592990` | 56 | 258 | idêntica | ok |
| Semifinal 2 — frttt × fer | `14455366452904822823` | 24 | 108 | idêntica | ok |
| Final — lubatv × fer | `6619800792897972838` | 37 | 168 | idêntica | ok |

## As 63 partidas em detalhe

### Fase de 64: detalhes

#### Fase de 64 1 — Smzinho × G0ularte

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W35 | Smzinho | Guerreiro | 23 | 29.75 | Cutelada, Mira Calma, Veterania, Estocada Seca | controle |
| p2 | W14 | G0ularte | Guerreiro | 21 | 28.02 | Mira Calma, Investida, Tomar Fôlego, Areia no Chão | crítico + controle + sustento |

- Seed da partida: `15680085034463772073`
- Rodadas: **19**
- Vencedor: **Smzinho** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2673/5701 (46.9%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Smzinho | G0ularte |
|---|---|---|
| Dano causado (golpes + DoT) | 5570 (4700 + 870) | 3028 (2572 + 456) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 1108 (1044 + 64) |
| MP gasto em ações | 1412 | 984 |
| Skills / ataques básicos | 15 / 3 | 15 / 2 |
| Acertos / erros | 10 / 0 | 6 / 4 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 2 | 17 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- Smzinho aplicou: vulnerable (rodada 4), stun (rodada 10), bleed (rodada 12), fear (rodada 13), bleed (rodada 17)
- Smzinho tentou sem sucesso: bleed (rodada 2), stun (rodada 3), fear (rodada 3), stun (rodada 4), fear (rodada 4), stun (rodada 5), fear (rodada 5), bleed (rodada 7), stun (rodada 8), fear (rodada 8), stun (rodada 9), fear (rodada 9), vulnerable (rodada 9), fear (rodada 10), stun (rodada 13), stun (rodada 14), fear (rodada 14), vulnerable (rodada 14), stun (rodada 15), fear (rodada 15), stun (rodada 18), fear (rodada 18)
- Smzinho ativou: Veterania ×4
- G0ularte aplicou: slowed (rodada 1), fear (rodada 3), slowed (rodada 5), bleed (rodada 6), vulnerable (rodada 6), slowed (rodada 9), vulnerable (rodada 12), slowed (rodada 13), vulnerable (rodada 13), fear (rodada 16), slowed (rodada 17)
- G0ularte tentou sem sucesso: vulnerable (rodada 1), stun (rodada 3), bleed (rodada 3), stun (rodada 3), vulnerable (rodada 5), stun (rodada 6), fear (rodada 6), stun (rodada 8), bleed (rodada 8), fear (rodada 8), vulnerable (rodada 9), stun (rodada 12), bleed (rodada 12), fear (rodada 12), stun (rodada 16), bleed (rodada 16), vulnerable (rodada 16), vulnerable (rodada 17), stun (rodada 18), bleed (rodada 18), fear (rodada 18), stun (rodada 18)
- Leis disparadas por G0ularte: PÂNICO (rodada 13)

Rodada a rodada:

| Rodada | Ordem (critério) | Smzinho (p1) | G0ularte (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Areia no Chão — executada, dano 0, MP −56 | 5701 / 4354 | 847 / 756 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 0, MP −92 | 5701 / 4354 | 808 / 680 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 432, MP −85 | Investida — executada, dano 359, MP −47 | 5342 / 3922 | 754 / 649 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 754, MP −116 | Ataque básico — executada, dano 0 | 5342 / 3168 | 669 / 665 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 259 | Areia no Chão — executada, dano 0, MP −56 | 5342 / 2909 | 700 / 625 |
| 6 | p1 → p2 (score) | Veterania — executada, dano 0, MP −111 | Mira Calma — executada, dano 624, MP −92 | 4718 / 2927 | 620 / 549 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Investida — executada, dano 0, MP −47 | 4490 / 2927 | 581 / 518 |
| 8 | p2 → p1 (score) | Cutelada — executada, dano 432, MP −85 | Ataque básico — executada, dano 203 | 4059 / 2501 | 527 / 534 |
| 9 | p2 → p1 (score) | Mira Calma — executada, dano 672, MP −116 | Areia no Chão — executada, dano 0, MP −56 | 4059 / 1829 | 442 / 494 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 217 | Tomar Fôlego — executada, dano 0, MP −74 | 4059 / 2134 | 473 / 436 |
| 11 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Mira Calma — cancelada por controle | 4059 / 2134 | 393 / 452 |
| 12 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 545, MP −92 | 3514 / 2150 | 354 / 376 |
| 13 | p2 → p1 (score) | Cutelada — executada, dano 589, MP −85 | Areia no Chão — executada, dano 0, MP −56 | 3514 / 1387 | 300 / 336 |
| 14 | p2 → p1 (score) | Mira Calma — executada, dano 539, MP −116 | Investida — executada, dano 0, MP −47 | 3514 / 674 | 215 / 305 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 217 | Tomar Fôlego — executada, dano 0, MP −74 | 3514 / 805 | 246 / 247 |
| 16 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Mira Calma — executada, dano 545, MP −92 | 2969 / 821 | 166 / 171 |
| 17 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Areia no Chão — executada, dano 0, MP −56 | 2969 / 821 | 127 / 131 |
| 18 | p2 → p1 (score) | Cutelada — executada, dano 589, MP −85 | Investida — executada, dano 296, MP −47 | 2673 / 66 | 73 / 100 |
| 19 | p2 → p1 (score) | Ataque básico — não alcançada (o duelo acabou antes) | Mira Calma — cancelada por morte | 2673 / -108 | 73 / 116 |

#### Fase de 64 2 — sofiaespanha × brino

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W56 | sofiaespanha | Guerreiro | 23 | 29.29 | Soco de Placa, Passo Lateral, Quebra-Guarda, Baluarte | defesa + controle |
| p2 | W09 | brino | Guerreiro | 18 | 28.02 | Cutelada, Investida, Areia no Chão, Fúria | crítico + controle |

- Seed da partida: `1531925714914894290`
- Rodadas: **23**
- Vencedor: **sofiaespanha** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4528/7757 (58.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | sofiaespanha | brino |
|---|---|---|
| Dano causado (golpes + DoT) | 4399 (4071 + 328) | 3749 (1545 + 2204) |
| Cura (skill + roubo de vida) | 520 (0 + 520) | 133 (0 + 133) |
| MP gasto em ações | 1091 | 594 |
| Skills / ataques básicos | 17 / 5 | 12 / 10 |
| Acertos / erros | 16 / 0 | 8 / 9 |
| Críticos (dano) | 0 (0) | 1 (351) |
| Agiu primeiro (rodadas) | 17 | 6 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- sofiaespanha aplicou: bleed (rodada 7), weakened (rodada 12), weakened (rodada 15), weakened (rodada 17), weakened (rodada 19)
- sofiaespanha tentou sem sucesso: stun (rodada 2), bleed (rodada 2), weakened (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), weakened (rodada 4), stun (rodada 6), bleed (rodada 6), weakened (rodada 6), stun (rodada 7), stun (rodada 8), bleed (rodada 8), weakened (rodada 8), stun (rodada 10), bleed (rodada 10), weakened (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 21), bleed (rodada 21), weakened (rodada 21), stun (rodada 23), bleed (rodada 23), weakened (rodada 23)
- sofiaespanha ativou: Passo Lateral ×6
- brino aplicou: poison (rodada 4), slowed (rodada 6), poison (rodada 8), stun (rodada 12), poison (rodada 18)
- brino tentou sem sucesso: slowed (rodada 2), stun (rodada 3), bleed (rodada 3), poison (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 4), vulnerable (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 8), slowed (rodada 10), bleed (rodada 12), poison (rodada 12), stun (rodada 13), bleed (rodada 13), poison (rodada 13), stun (rodada 13), stun (rodada 16), bleed (rodada 16), poison (rodada 16), stun (rodada 18), bleed (rodada 18), stun (rodada 21), bleed (rodada 21), poison (rodada 21), stun (rodada 21)
- brino ativou: Fúria ×2

Rodada a rodada:

| Rodada | Ordem (critério) | sofiaespanha (p1) | brino (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Passo Lateral — executada, dano 0, MP −70 | Fúria — executada, dano 0, MP −108 | 7757 / 4119 | 766 / 338 |
| 2 | p2 → p1 (score) | Soco de Placa — executada, dano 296, MP −61 | Areia no Chão — executada, dano 0, MP −39 | 7757 / 3823 | 725 / 307 |
| 3 | p2 → p1 (score) | Ataque básico — executada, dano 163 | Cutelada — executada, dano 222, MP −48 | 7557 / 3679 | 745 / 267 |
| 4 | p2 → p1 (score) | Soco de Placa — executada, dano 296, MP −61 | Investida — executada, dano 232, MP −33 | 7250 / 3403 | 704 / 242 |
| 5 | p1 → p2 (score) | Passo Lateral — executada, dano 0, MP −70 | Fúria — executada, dano 0, MP −108 | 7134 / 3403 | 654 / 142 |
| 6 | p2 → p1 (score) | Soco de Placa — executada, dano 296, MP −61 | Areia no Chão — executada, dano 0, MP −39 | 7059 / 3107 | 613 / 111 |
| 7 | p2 → p1 (score) | Ataque básico — executada, dano 163 | Cutelada — executada, dano 0, MP −48 | 6965 / 2944 | 633 / 71 |
| 8 | p2 → p1 (score) | Soco de Placa — executada, dano 296, MP −61 | Investida — executada, dano 232, MP −33 | 6542 / 2504 | 592 / 46 |
| 9 | p1 → p2 (score) | Passo Lateral — executada, dano 0, MP −70 | Ataque básico — executada, dano 0 | 6310 / 2340 | 542 / 54 |
| 10 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Areia no Chão — executada, dano 0, MP −39 | 6119 / 2044 | 501 / 23 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 163 | Ataque básico — executada, dano 0 | 5909 / 1881 | 521 / 31 |
| 12 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Ataque básico — executada, dano 92 | 5626 / 1593 | 480 / 39 |
| 13 | p1 → p2 (score) | Passo Lateral — cancelada por controle | Investida — executada, dano 351, MP −33 | 5275 / 1624 | 500 / 14 |
| 14 | p1 → p2 (score) | Passo Lateral — executada, dano 0, MP −70 | Ataque básico — executada, dano 0 | 5275 / 1624 | 450 / 22 |
| 15 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Ataque básico — executada, dano 0 | 5316 / 1328 | 409 / 30 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 163 | Ataque básico — executada, dano 111 | 5227 / 1174 | 429 / 38 |
| 17 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Investida — executada, dano 0, MP −33 | 5268 / 878 | 388 / 13 |
| 18 | p1 → p2 (score) | Passo Lateral — executada, dano 0, MP −70 | Ataque básico — executada, dano 111 | 5157 / 887 | 338 / 21 |
| 19 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Ataque básico — executada, dano 0 | 5082 / 591 | 297 / 29 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 163 | Ataque básico — executada, dano 0 | 4988 / 428 | 317 / 37 |
| 21 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Investida — executada, dano 194, MP −33 | 4719 / 149 | 276 / 12 |
| 22 | p1 → p2 (score) | Passo Lateral — executada, dano 0, MP −70 | Ataque básico — executada, dano 0 | 4603 / 149 | 226 / 20 |
| 23 | p1 → p2 (score) | Soco de Placa — executada, dano 296, MP −61 | Ataque básico — cancelada por morte | 4528 / -147 | 185 / 20 |

#### Fase de 64 3 — gafallen × blackoutz

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W37 | gafallen | Guerreiro | 20 | 29.87 | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda | sustento |
| p2 | W12 | blackoutz | Guerreiro | 20 | 27.79 | Golpe Duplo, Mira Calma, Baluarte, Encarar | crítico + defesa |

- Seed da partida: `5116284588478050991`
- Rodadas: **10**
- Vencedor: **gafallen** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1334/3973 (33.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | gafallen | blackoutz |
|---|---|---|
| Dano causado (golpes + DoT) | 4684 (4684 + 0) | 4234 (2361 + 1873) |
| Cura (skill + roubo de vida) | 1595 (533 + 1062) | 0 (0 + 0) |
| MP gasto em ações | 643 | 436 |
| Skills / ataques básicos | 9 / 1 | 6 / 3 |
| Acertos / erros | 5 / 1 | 7 / 0 |
| Críticos (dano) | 1 (1790) | 2 (1040) |
| Agiu primeiro (rodadas) | 10 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- gafallen aplicou: vulnerable (rodada 3), vulnerable (rodada 6), vulnerable (rodada 10)
- gafallen tentou sem sucesso: stun (rodada 2), bleed (rodada 2), vulnerable (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 6), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), vulnerable (rodada 7), stun (rodada 10), bleed (rodada 10)
- gafallen ativou: Escudo Protetor ×3
- blackoutz aplicou: bleed (rodada 2), frailty (rodada 2), bleed (rodada 3), bleed (rodada 4), bleed (rodada 6), frailty (rodada 6), bleed (rodada 7), vulnerable (rodada 7)
- blackoutz tentou sem sucesso: vulnerable (rodada 1), poison (rodada 2), poison (rodada 3), vulnerable (rodada 3), poison (rodada 4), vulnerable (rodada 5), poison (rodada 6), poison (rodada 7), bleed (rodada 8), poison (rodada 8), bleed (rodada 9), poison (rodada 9)

Rodada a rodada:

| Rodada | Ordem (critério) | gafallen (p1) | blackoutz (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −77 | Encarar — executada, dano 0, MP −54 | 3973 / 3915 | 686 / 463 |
| 2 | p1 → p2 (score) | Mira Calma — executada, dano 1055, MP −82 | Golpe Duplo — executada, dano 288, MP −82 | 3685 / 2860 | 643 / 399 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 422, MP −50 | Mira Calma — executada, dano 365, MP −82 | 2813 / 2438 | 632 / 335 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 174 | 2385 / 2438 | 671 / 353 |
| 5 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −77 | Encarar — executada, dano 0, MP −54 | 2004 / 2438 | 633 / 317 |
| 6 | p1 → p2 (score) | Mira Calma — executada, dano 918, MP −82 | Golpe Duplo — executada, dano 288, MP −82 | 1653 / 1520 | 590 / 253 |
| 7 | p1 → p2 (score) | Quebra-Guarda — executada, dano 499, MP −50 | Mira Calma — executada, dano 782, MP −82 | 968 / 1021 | 579 / 189 |
| 8 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 206 | 1041 / 1021 | 552 / 207 |
| 9 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 258 | 529 / 1021 | 514 / 225 |
| 10 | p1 → p2 (score) | Mira Calma — executada, dano 1790, MP −82 | Encarar — cancelada por morte | 1334 / -769 | 471 / 225 |

#### Fase de 64 4 — Bagi × loud_thurzin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W48 | Bagi | Guerreiro | 20 | 27.79 | Golpe Poderoso, Respirar Fundo, Mira Calma, Olho Treinado | defesa + sustento |
| p2 | W32 | loud_thurzin | Guerreiro | 22 | 29.87 | Marca do Caçador, Golpe Devastador, Guarda Alta, Grito Curto | crítico + controle |

- Seed da partida: `9981607956343163088`
- Rodadas: **35**
- Vencedor: **loud_thurzin** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 688/5110 (13.5%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Bagi | loud_thurzin |
|---|---|---|
| Dano causado (golpes + DoT) | 4539 (4083 + 456) | 6516 (4182 + 2334) |
| Cura (skill + roubo de vida) | 1157 (610 + 547) | 117 (0 + 117) |
| MP gasto em ações | 830 | 1554 |
| Skills / ataques básicos | 17 / 15 | 22 / 13 |
| Acertos / erros | 21 / 10 | 18 / 1 |
| Críticos (dano) | 0 (0) | 2 (985) |
| Agiu primeiro (rodadas) | 0 | 35 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- Bagi aplicou: vulnerable (rodada 6), vulnerable (rodada 14), poison (rodada 24), poison (rodada 34)
- Bagi tentou sem sucesso: poison (rodada 1), poison (rodada 2), vulnerable (rodada 2), poison (rodada 5), poison (rodada 6), poison (rodada 9), poison (rodada 10), vulnerable (rodada 10), poison (rodada 11), poison (rodada 12), poison (rodada 13), poison (rodada 14), poison (rodada 15), poison (rodada 18), poison (rodada 20), poison (rodada 23), poison (rodada 28), poison (rodada 30), poison (rodada 31), poison (rodada 32), poison (rodada 33)
- loud_thurzin aplicou: fear (rodada 2), weakened (rodada 2), bleed (rodada 4), fear (rodada 6), bleed (rodada 8), fear (rodada 10), weakened (rodada 10), bleed (rodada 16), fear (rodada 18), fear (rodada 22), weakened (rodada 22), stun (rodada 27), fear (rodada 28), stun (rodada 29), bleed (rodada 29), bleed (rodada 30), poison (rodada 35)
- loud_thurzin tentou sem sucesso: stun (rodada 3), bleed (rodada 3), poison (rodada 3), stun (rodada 4), poison (rodada 4), weakened (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), stun (rodada 8), poison (rodada 8), stun (rodada 11), bleed (rodada 11), poison (rodada 11), stun (rodada 12), bleed (rodada 12), poison (rodada 12), fear (rodada 14), stun (rodada 15), bleed (rodada 15), poison (rodada 15), stun (rodada 16), poison (rodada 16), weakened (rodada 18), stun (rodada 19), bleed (rodada 19), poison (rodada 19), stun (rodada 20), bleed (rodada 20), poison (rodada 20), stun (rodada 23), bleed (rodada 23), poison (rodada 23), stun (rodada 24), bleed (rodada 24), poison (rodada 24), stun (rodada 26), bleed (rodada 26), poison (rodada 26), bleed (rodada 27), poison (rodada 27), weakened (rodada 28), poison (rodada 29), stun (rodada 30), poison (rodada 30), stun (rodada 33), bleed (rodada 33), poison (rodada 33), fear (rodada 34), stun (rodada 35), bleed (rodada 35)
- loud_thurzin ativou: Guarda Alta ×8

Rodada a rodada:

| Rodada | Ordem (critério) | Bagi (p1) | loud_thurzin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Golpe Poderoso — executada, dano 183, MP −37 | Guarda Alta — executada, dano 0, MP −57 | 5319 / 4927 | 501 / 906 |
| 2 | p2 → p1 (score) | Mira Calma — executada, dano 421, MP −82 | Grito Curto — executada, dano 0, MP −57 | 5319 / 4506 | 429 / 868 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −37 | Golpe Devastador — executada, dano 686, MP −107 | 4633 / 4526 | 402 / 780 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 4279 / 4530 | 412 / 799 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 183, MP −37 | Guarda Alta — executada, dano 0, MP −57 | 4096 / 4347 | 385 / 761 |
| 6 | p2 → p1 (score) | Mira Calma — executada, dano 421, MP −82 | Grito Curto — executada, dano 0, MP −57 | 4163 / 3926 | 313 / 723 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −37 | Golpe Devastador — executada, dano 327, MP −107 | 3836 / 3935 | 286 / 635 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 3482 / 3939 | 296 / 654 |
| 9 | p2 → p1 (score) | Golpe Poderoso — executada, dano 169, MP −37 | Guarda Alta — executada, dano 0, MP −57 | 3297 / 3770 | 269 / 616 |
| 10 | p2 → p1 (score) | Mira Calma — executada, dano 366, MP −82 | Grito Curto — executada, dano 0, MP −57 | 3355 / 3404 | 197 / 578 |
| 11 | p2 → p1 (score) | Golpe Poderoso — executada, dano 169, MP −37 | Golpe Devastador — executada, dano 327, MP −107 | 3055 / 3244 | 170 / 490 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 118 | Ataque básico — executada, dano 142 | 2931 / 3130 | 180 / 509 |
| 13 | p2 → p1 (score) | Golpe Poderoso — executada, dano 169, MP −37 | Guarda Alta — executada, dano 0, MP −57 | 2958 / 2961 | 153 / 471 |
| 14 | p2 → p1 (score) | Mira Calma — executada, dano 366, MP −82 | Grito Curto — executada, dano 0, MP −57 | 3016 / 2595 | 81 / 433 |
| 15 | p2 → p1 (score) | Golpe Poderoso — executada, dano 197, MP −37 | Golpe Devastador — executada, dano 327, MP −107 | 2720 / 2407 | 54 / 345 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 2366 / 2411 | 64 / 364 |
| 17 | p2 → p1 (score) | Respirar Fundo — executada, dano 0, MP −58 | Guarda Alta — executada, dano 0, MP −57 | 2764 / 2411 | 16 / 326 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 97 | Grito Curto — executada, dano 0, MP −57 | 2779 / 2314 | 26 / 288 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Golpe Devastador — executada, dano 327, MP −107 | 2452 / 2323 | 36 / 200 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 118 | Ataque básico — executada, dano 142 | 2328 / 2209 | 46 / 219 |
| 21 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −37 | Guarda Alta — executada, dano 0, MP −57 | 2328 / 2209 | 19 / 181 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Grito Curto — executada, dano 0, MP −57 | 2328 / 2209 | 29 / 143 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 97 | Golpe Devastador — executada, dano 327, MP −107 | 2016 / 2121 | 39 / 55 |
| 24 | p2 → p1 (score) | Golpe Poderoso — executada, dano 205, MP −37 | Ataque básico — executada, dano 142 | 1906 / 1920 | 12 / 74 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Guarda Alta — executada, dano 0, MP −57 | 1906 / 1844 | 22 / 36 |
| 26 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 1764 / 1772 | 32 / 55 |
| 27 | p2 → p1 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 142 | 1622 / 1700 | 42 / 74 |
| 28 | p2 → p1 (score) | Golpe Poderoso — executada, dano 205, MP −37 | Grito Curto — executada, dano 0, MP −57 | 1654 / 1419 | 15 / 36 |
| 29 | p2 → p1 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 142 | 1300 / 1347 | 25 / 55 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 118 | Ataque básico — executada, dano 142 | 751 / 1233 | 35 / 74 |
| 31 | p2 → p1 (score) | Ataque básico — executada, dano 97 | Guarda Alta — executada, dano 0, MP −57 | 341 / 1136 | 45 / 36 |
| 32 | p2 → p1 (score) | Golpe Poderoso — executada, dano 169, MP −37 | Ataque básico — executada, dano 0 | 368 / 967 | 18 / 55 |
| 33 | p2 → p1 (score) | Ataque básico — executada, dano 97 | Ataque básico — executada, dano 142 | 241 / 874 | 28 / 74 |
| 34 | p2 → p1 (score) | Ataque básico — executada, dano 118 | Grito Curto — executada, dano 0, MP −57 | 259 / 756 | 38 / 36 |
| 35 | p2 → p1 (score) | Golpe Poderoso — cancelada por morte | Ataque básico — executada, dano 299 | -40 / 688 | 38 / 55 |

#### Fase de 64 5 — fnxLNTC × hastad

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W24 | fnxLNTC | Guerreiro | 22 | 29.52 | Golpe Poderoso, Investida, Couraça Improvisada, Berro de Ferro | defesa + sustento |
| p2 | W50 | hastad | Guerreiro | 22 | 28.60 | Mão Dupla, Mira Calma, Estocada Seca, Couro Batido | crítico + defesa + controle |

- Seed da partida: `8825721451302242450`
- Rodadas: **27**
- Vencedor: **fnxLNTC** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1865/5355 (34.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fnxLNTC | hastad |
|---|---|---|
| Dano causado (golpes + DoT) | 4888 (4533 + 355) | 4258 (3830 + 428) |
| Cura (skill + roubo de vida) | 768 (0 + 768) | 0 (0 + 0) |
| MP gasto em ações | 1398 | 1106 |
| Skills / ataques básicos | 26 / 1 | 14 / 12 |
| Acertos / erros | 12 / 1 | 18 / 2 |
| Críticos (dano) | 2 (1407) | 10 (2693) |
| Agiu primeiro (rodadas) | 27 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- fnxLNTC aplicou: hexed (rodada 2), hexed (rodada 10), hexed (rodada 14), fear (rodada 14), poison (rodada 15), hexed (rodada 18)
- fnxLNTC tentou sem sucesso: fear (rodada 2), stun (rodada 3), poison (rodada 3), hexed (rodada 6), stun (rodada 7), poison (rodada 7), stun (rodada 8), poison (rodada 8), stun (rodada 8), fear (rodada 10), stun (rodada 11), poison (rodada 11), stun (rodada 12), poison (rodada 12), stun (rodada 12), stun (rodada 15), stun (rodada 16), poison (rodada 16), stun (rodada 16), fear (rodada 18), stun (rodada 19), poison (rodada 19), stun (rodada 20), poison (rodada 20), stun (rodada 20), hexed (rodada 22), stun (rodada 23), poison (rodada 23), stun (rodada 24), poison (rodada 24), stun (rodada 24), hexed (rodada 26), stun (rodada 27), poison (rodada 27)
- fnxLNTC ativou: Couraça Improvisada ×7
- hastad aplicou: fear (rodada 2), bleed (rodada 6)
- hastad tentou sem sucesso: bleed (rodada 2), bleed (rodada 2), bleed (rodada 3), fear (rodada 3), vulnerable (rodada 3), bleed (rodada 4), fear (rodada 4), fear (rodada 6), bleed (rodada 6), bleed (rodada 7), fear (rodada 7), vulnerable (rodada 7), bleed (rodada 8), fear (rodada 8), bleed (rodada 10), fear (rodada 10), bleed (rodada 10), bleed (rodada 11), fear (rodada 11), vulnerable (rodada 11), bleed (rodada 12), fear (rodada 12), bleed (rodada 14), fear (rodada 14), bleed (rodada 15), fear (rodada 15), bleed (rodada 15), bleed (rodada 16), fear (rodada 16), bleed (rodada 17), fear (rodada 17), bleed (rodada 19), fear (rodada 19), bleed (rodada 20), fear (rodada 20), bleed (rodada 23), fear (rodada 23), bleed (rodada 24), fear (rodada 24), bleed (rodada 26), fear (rodada 26)
- hastad ativou: Couro Batido ×6

Rodada a rodada:

| Rodada | Ordem (critério) | fnxLNTC (p1) | hastad (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Couro Batido — executada, dano 0, MP −62 | 5355 / 4794 | 889 / 586 |
| 2 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mão Dupla — executada, dano 270, MP −85 | 5085 / 4794 | 856 / 521 |
| 3 | p1 → p2 (score) | Golpe Poderoso — executada, dano 324, MP −47 | Mira Calma — executada, dano 559, MP −103 | 4581 / 4470 | 828 / 438 |
| 4 | p1 → p2 (score) | Investida — executada, dano 0, MP −53 | Ataque básico — executada, dano 110 | 4471 / 4470 | 794 / 458 |
| 5 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Couro Batido — executada, dano 0, MP −62 | 4471 / 4470 | 751 / 416 |
| 6 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mão Dupla — executada, dano 180, MP −85 | 4291 / 4470 | 718 / 351 |
| 7 | p1 → p2 (score) | Golpe Poderoso — executada, dano 324, MP −47 | Mira Calma — executada, dano 491, MP −103 | 3641 / 4146 | 690 / 268 |
| 8 | p1 → p2 (score) | Investida — executada, dano 850, MP −53 | Ataque básico — executada, dano 165 | 3406 / 3296 | 656 / 288 |
| 9 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Couro Batido — executada, dano 0, MP −62 | 3406 / 3296 | 613 / 246 |
| 10 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mão Dupla — executada, dano 180, MP −85 | 3226 / 3296 | 580 / 181 |
| 11 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −47 | Mira Calma — executada, dano 491, MP −103 | 2786 / 2996 | 552 / 98 |
| 12 | p1 → p2 (score) | Investida — executada, dano 378, MP −53 | Ataque básico — executada, dano 165 | 2685 / 2618 | 518 / 118 |
| 13 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Couro Batido — executada, dano 0, MP −62 | 2685 / 2618 | 475 / 76 |
| 14 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 72 | 2613 / 2618 | 442 / 96 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −47 | Mão Dupla — executada, dano 268, MP −85 | 2396 / 2247 | 414 / 31 |
| 16 | p1 → p2 (score) | Investida — executada, dano 378, MP −53 | Ataque básico — executada, dano 165 | 2295 / 1798 | 380 / 51 |
| 17 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 111 | 2184 / 1727 | 337 / 71 |
| 18 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Couro Batido — executada, dano 0, MP −62 | 2184 / 1656 | 304 / 29 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −47 | Ataque básico — executada, dano 107 | 2128 / 1285 | 276 / 49 |
| 20 | p1 → p2 (score) | Investida — executada, dano 302, MP −53 | Ataque básico — executada, dano 165 | 2014 / 983 | 242 / 69 |
| 21 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 0 | 2014 / 983 | 199 / 89 |
| 22 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Couro Batido — executada, dano 0, MP −62 | 2014 / 983 | 166 / 47 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −47 | Ataque básico — executada, dano 110 | 1955 / 683 | 138 / 67 |
| 24 | p1 → p2 (score) | Investida — executada, dano 557, MP −53 | Ataque básico — executada, dano 110 | 1939 / 126 | 104 / 87 |
| 25 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Mão Dupla — executada, dano 0, MP −85 | 1939 / 126 | 61 / 22 |
| 26 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 111 | 1828 / 126 | 28 / 42 |
| 27 | p1 → p2 (score) | Ataque básico — executada, dano 220 | Ataque básico — cancelada por morte | 1865 / -94 | 47 / 42 |

#### Fase de 64 6 — yayahuz × k13tv

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W07 | yayahuz | Guerreiro | 22 | 27.79 | Golpe Poderoso, Mira Calma, Sede de Batalha, Tomar Fôlego | defesa + sustento |
| p2 | W17 | k13tv | Guerreiro | 23 | 27.91 | Golpe Poderoso, Mira Calma, Fio no Rebite, Guarda Cruzada | defesa + sustento |

- Seed da partida: `1388346834123313183`
- Rodadas: **21**
- Vencedor: **yayahuz** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3788/6296 (60.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | yayahuz | k13tv |
|---|---|---|
| Dano causado (golpes + DoT) | 5574 (5574 + 0) | 2671 (2671 + 0) |
| Cura (skill + roubo de vida) | 163 (0 + 163) | 132 (0 + 132) |
| MP gasto em ações | 882 | 1124 |
| Skills / ataques básicos | 14 / 7 | 14 / 4 |
| Acertos / erros | 20 / 1 | 9 / 2 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 21 | 0 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- yayahuz aplicou: stun (rodada 2), vulnerable (rodada 6), stun (rodada 10), vulnerable (rodada 10), vulnerable (rodada 14)
- yayahuz tentou sem sucesso: stun (rodada 1), vulnerable (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 7), stun (rodada 8), stun (rodada 9), stun (rodada 11), stun (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), stun (rodada 20), stun (rodada 21)
- k13tv tentou sem sucesso: stun (rodada 4), stun (rodada 6), stun (rodada 11), stun (rodada 12), vulnerable (rodada 12), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 19), stun (rodada 20)
- k13tv ativou: Fio no Rebite ×5, Guarda Cruzada ×2

Rodada a rodada:

| Rodada | Ordem (critério) | yayahuz (p1) | k13tv (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Golpe Poderoso — executada, dano 333, MP −47 | Fio no Rebite — executada, dano 0, MP −82 | 6296 / 5106 | 627 / 724 |
| 2 | p1 → p2 (score) | Mira Calma — executada, dano 574, MP −103 | Guarda Cruzada — cancelada por controle | 6296 / 4532 | 537 / 744 |
| 3 | p1 → p2 (score) | Golpe Poderoso — executada, dano 333, MP −47 | Guarda Cruzada — executada, dano 0, MP −111 | 6296 / 4199 | 503 / 653 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 121 | Golpe Poderoso — executada, dano 342, MP −52 | 5954 / 4095 | 516 / 621 |
| 5 | p1 → p2 (score) | Golpe Poderoso — executada, dano 210, MP −47 | Fio no Rebite — executada, dano 0, MP −82 | 5962 / 3885 | 482 / 559 |
| 6 | p1 → p2 (score) | Mira Calma — executada, dano 339, MP −103 | Golpe Poderoso — executada, dano 342, MP −52 | 5633 / 3563 | 392 / 527 |
| 7 | p1 → p2 (score) | Golpe Poderoso — executada, dano 370, MP −47 | Mira Calma — executada, dano 0, MP −116 | 5647 / 3193 | 358 / 431 |
| 8 | p1 → p2 (score) | Ataque básico — executada, dano 178 | Guarda Cruzada — executada, dano 0, MP −111 | 5654 / 3015 | 371 / 340 |
| 9 | p1 → p2 (score) | Golpe Poderoso — executada, dano 210, MP −47 | Fio no Rebite — executada, dano 0, MP −82 | 5662 / 2805 | 337 / 278 |
| 10 | p1 → p2 (score) | Mira Calma — executada, dano 339, MP −103 | Golpe Poderoso — cancelada por controle | 5675 / 2466 | 247 / 298 |
| 11 | p1 → p2 (score) | Golpe Poderoso — executada, dano 251, MP −47 | Golpe Poderoso — executada, dano 342, MP −52 | 5343 / 2232 | 213 / 266 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 178 | Mira Calma — executada, dano 605, MP −116 | 4745 / 2084 | 226 / 170 |
| 13 | p1 → p2 (score) | Golpe Poderoso — executada, dano 309, MP −47 | Fio no Rebite — executada, dano 0, MP −82 | 4757 / 1775 | 192 / 108 |
| 14 | p1 → p2 (score) | Mira Calma — executada, dano 499, MP −103 | Golpe Poderoso — executada, dano 0, MP −52 | 4776 / 1276 | 102 / 76 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 181 | 4595 / 1285 | 68 / 96 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 178 | Golpe Poderoso — executada, dano 316, MP −52 | 4286 / 1122 | 81 / 64 |
| 17 | p1 → p2 (score) | Golpe Poderoso — executada, dano 309, MP −47 | Ataque básico — executada, dano 181 | 4117 / 822 | 47 / 84 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 178 | Fio no Rebite — executada, dano 0, MP −82 | 4124 / 644 | 60 / 22 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 309, MP −47 | Ataque básico — executada, dano 181 | 3955 / 344 | 26 / 42 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 178 | Ataque básico — executada, dano 181 | 3781 / 175 | 39 / 62 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 178 | Golpe Poderoso — cancelada por morte | 3788 / -3 | 52 / 62 |

#### Fase de 64 7 — Dilera × JonVlogs

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W05 | Dilera | Guerreiro | 21 | 27.91 | Golpe Poderoso, Investida, Couraça Improvisada, Tomar Fôlego | defesa + sustento |
| p2 | W58 | JonVlogs | Guerreiro | 22 | 28.60 | Golpe Poderoso, Investida, Guarda Alta, Couraça Improvisada | defesa + sustento |

- Seed da partida: `17893717569376441782`
- Rodadas: **64**
- Vencedor: **JonVlogs** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2640/6314 (41.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Dilera | JonVlogs |
|---|---|---|
| Dano causado (golpes + DoT) | 5684 (5684 + 0) | 8858 (8858 + 0) |
| Cura (skill + roubo de vida) | 3656 (2556 + 1100) | 2010 (0 + 2010) |
| MP gasto em ações | 2587 | 1968 |
| Skills / ataques básicos | 53 / 8 | 37 / 25 |
| Acertos / erros | 36 / 7 | 42 / 2 |
| Críticos (dano) | 0 (0) | 5 (1734) |
| Agiu primeiro (rodadas) | 25 | 39 |
| Ações perdidas por controle | 3 | 2 |

Efeitos relevantes:
- Dilera aplicou: stun (rodada 41), stun (rodada 45)
- Dilera tentou sem sucesso: stun (rodada 3), stun (rodada 11), stun (rodada 15), stun (rodada 19), stun (rodada 24), stun (rodada 28), stun (rodada 32)
- Dilera ativou: Couraça Improvisada ×15
- JonVlogs aplicou: stun (rodada 12), stun (rodada 20), stun (rodada 34)
- JonVlogs tentou sem sucesso: stun (rodada 3), stun (rodada 4), stun (rodada 4), stun (rodada 7), stun (rodada 8), stun (rodada 8), stun (rodada 11), stun (rodada 12), stun (rodada 15), stun (rodada 16), stun (rodada 16), stun (rodada 19), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 30), stun (rodada 32), stun (rodada 33), stun (rodada 35), stun (rodada 36), stun (rodada 37), stun (rodada 40), stun (rodada 41), stun (rodada 44), stun (rodada 47), stun (rodada 49), stun (rodada 50), stun (rodada 51), stun (rodada 52), stun (rodada 54), stun (rodada 55), stun (rodada 56), stun (rodada 57), stun (rodada 59), stun (rodada 60), stun (rodada 61), stun (rodada 62), stun (rodada 63), stun (rodada 64)
- JonVlogs ativou: Guarda Alta ×13, Couraça Improvisada ×5

Rodada a rodada:

| Rodada | Ordem (critério) | Dilera (p1) | JonVlogs (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 5077 / 6314 | 812 / 651 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 130, MP −42 | Couraça Improvisada — executada, dano 0, MP −62 | 5077 / 6184 | 798 / 610 |
| 3 | p2 → p1 (score) | Investida — executada, dano 150, MP −47 | Golpe Poderoso — executada, dano 236, MP −47 | 4871 / 6088 | 779 / 584 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −42 | Investida — executada, dano 525, MP −53 | 4346 / 6208 | 765 / 552 |
| 5 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 4346 / 6208 | 737 / 516 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 130, MP −42 | Couraça Improvisada — executada, dano 0, MP −62 | 4372 / 6078 | 723 / 475 |
| 7 | p2 → p1 (score) | Investida — executada, dano 0, MP −47 | Golpe Poderoso — executada, dano 236, MP −47 | 4136 / 6132 | 704 / 449 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 210, MP −42 | Investida — executada, dano 350, MP −53 | 3828 / 6002 | 690 / 417 |
| 9 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 3828 / 6002 | 662 / 381 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 130, MP −42 | Couraça Improvisada — executada, dano 0, MP −62 | 3854 / 5872 | 648 / 340 |
| 11 | p2 → p1 (score) | Investida — executada, dano 150, MP −47 | Golpe Poderoso — executada, dano 220, MP −47 | 3664 / 5772 | 629 / 314 |
| 12 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Investida — executada, dano 290, MP −53 | 3374 / 5838 | 657 / 282 |
| 13 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 3374 / 5838 | 629 / 246 |
| 14 | p2 → p1 (score) | Golpe Poderoso — executada, dano 130, MP −42 | Couraça Improvisada — executada, dano 0, MP −62 | 3400 / 5708 | 615 / 205 |
| 15 | p2 → p1 (score) | Investida — executada, dano 150, MP −47 | Golpe Poderoso — executada, dano 330, MP −47 | 3100 / 5633 | 596 / 179 |
| 16 | p2 → p1 (score) | Golpe Poderoso — executada, dano 210, MP −42 | Investida — executada, dano 290, MP −53 | 2852 / 5489 | 582 / 147 |
| 17 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 2852 / 5489 | 554 / 111 |
| 18 | p2 → p1 (score) | Golpe Poderoso — executada, dano 130, MP −42 | Couraça Improvisada — executada, dano 0, MP −62 | 2878 / 5359 | 540 / 70 |
| 19 | p2 → p1 (score) | Investida — executada, dano 150, MP −47 | Golpe Poderoso — executada, dano 220, MP −47 | 2688 / 5259 | 521 / 44 |
| 20 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Ataque básico — executada, dano 169 | 2519 / 5297 | 549 / 65 |
| 21 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −74 | Guarda Alta — executada, dano 0, MP −57 | 3371 / 5297 | 503 / 29 |
| 22 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 169 | 3202 / 5335 | 475 / 50 |
| 23 | p2 → p1 (score) | Golpe Poderoso — executada, dano 174, MP −42 | Golpe Poderoso — executada, dano 220, MP −47 | 3016 / 5211 | 461 / 24 |
| 24 | p2 → p1 (score) | Investida — executada, dano 242, MP −47 | Ataque básico — executada, dano 129 | 2935 / 4998 | 442 / 45 |
| 25 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Ataque básico — executada, dano 169 | 2805 / 4841 | 428 / 66 |
| 26 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 2805 / 4841 | 400 / 30 |
| 27 | p2 → p1 (score) | Golpe Poderoso — executada, dano 161, MP −42 | Ataque básico — executada, dano 129 | 2708 / 4709 | 386 / 51 |
| 28 | p2 → p1 (score) | Investida — executada, dano 164, MP −47 | Golpe Poderoso — executada, dano 220, MP −47 | 2520 / 4595 | 367 / 25 |
| 29 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −74 | Ataque básico — executada, dano 169 | 3203 / 4633 | 321 / 46 |
| 30 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 129 | 3074 / 4662 | 293 / 67 |
| 31 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Guarda Alta — executada, dano 0, MP −57 | 3113 / 4467 | 279 / 31 |
| 32 | p2 → p1 (score) | Investida — executada, dano 164, MP −47 | Ataque básico — executada, dano 129 | 3016 / 4332 | 260 / 52 |
| 33 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −42 | Golpe Poderoso — executada, dano 288, MP −47 | 2728 / 4398 | 246 / 26 |
| 34 | p2 → p1 (score) | Couraça Improvisada — cancelada por controle | Ataque básico — executada, dano 169 | 2559 / 4436 | 274 / 47 |
| 35 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Golpe Poderoso — executada, dano 220, MP −47 | 2339 / 4486 | 246 / 21 |
| 36 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −74 | Ataque básico — executada, dano 129 | 3062 / 4515 | 200 / 42 |
| 37 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Ataque básico — executada, dano 169 | 2932 / 4358 | 186 / 63 |
| 38 | p1 → p2 (score) | Investida — executada, dano 0, MP −47 | Guarda Alta — executada, dano 0, MP −57 | 2932 / 4358 | 167 / 27 |
| 39 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 0 | 2932 / 4358 | 139 / 48 |
| 40 | p2 → p1 (score) | Golpe Poderoso — executada, dano 161, MP −42 | Golpe Poderoso — executada, dano 220, MP −47 | 2744 / 4247 | 125 / 22 |
| 41 | p2 → p1 (score) | Investida — executada, dano 198, MP −47 | Ataque básico — executada, dano 129 | 2654 / 4078 | 106 / 43 |
| 42 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Ataque básico — cancelada por controle | 2693 / 3883 | 92 / 64 |
| 43 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Guarda Alta — executada, dano 0, MP −57 | 2693 / 3883 | 64 / 28 |
| 44 | p2 → p1 (score) | Golpe Poderoso — executada, dano 161, MP −42 | Ataque básico — executada, dano 194 | 2531 / 3766 | 50 / 49 |
| 45 | p2 → p1 (score) | Investida — executada, dano 164, MP −47 | Golpe Poderoso — executada, dano 0, MP −47 | 2563 / 3602 | 31 / 23 |
| 46 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — cancelada por controle | 2563 / 3602 | 59 / 44 |
| 47 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 129 | 2434 / 3631 | 31 / 65 |
| 48 | p1 → p2 (score) | Ataque básico — executada, dano 114 | Guarda Alta — executada, dano 0, MP −57 | 2456 / 3517 | 59 / 29 |
| 49 | p2 → p1 (score) | Golpe Poderoso — executada, dano 161, MP −42 | Ataque básico — executada, dano 129 | 2359 / 3385 | 45 / 50 |
| 50 | p2 → p1 (score) | Ataque básico — executada, dano 94 | Golpe Poderoso — executada, dano 288, MP −47 | 2089 / 3357 | 73 / 24 |
| 51 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 169 | 1920 / 3395 | 45 / 45 |
| 52 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Ataque básico — executada, dano 129 | 1830 / 3229 | 31 / 66 |
| 53 | p1 → p2 (score) | Ataque básico — executada, dano 114 | Guarda Alta — executada, dano 0, MP −57 | 1852 / 3115 | 59 / 30 |
| 54 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −42 | Ataque básico — executada, dano 169 | 1683 / 3153 | 45 / 51 |
| 55 | p2 → p1 (score) | Ataque básico — executada, dano 94 | Golpe Poderoso — executada, dano 288, MP −47 | 1413 / 3125 | 73 / 25 |
| 56 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 169 | 1244 / 3163 | 45 / 46 |
| 57 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −42 | Ataque básico — executada, dano 129 | 1115 / 3192 | 31 / 67 |
| 58 | p1 → p2 (score) | Ataque básico — executada, dano 114 | Guarda Alta — executada, dano 0, MP −57 | 1137 / 3078 | 59 / 31 |
| 59 | p2 → p1 (score) | Golpe Poderoso — executada, dano 161, MP −42 | Ataque básico — executada, dano 169 | 1000 / 2955 | 45 / 52 |
| 60 | p2 → p1 (score) | Ataque básico — executada, dano 94 | Golpe Poderoso — executada, dano 431, MP −47 | 587 / 2960 | 73 / 26 |
| 61 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −56 | Ataque básico — executada, dano 169 | 418 / 2998 | 45 / 47 |
| 62 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Golpe Poderoso — executada, dano 220, MP −47 | 237 / 2853 | 31 / 21 |
| 63 | p1 → p2 (score) | Ataque básico — executada, dano 114 | Ataque básico — executada, dano 254 | 5 / 2797 | 59 / 42 |
| 64 | p1 → p2 (score) | Golpe Poderoso — executada, dano 195, MP −42 | Ataque básico — executada, dano 169 | -125 / 2640 | 45 / 63 |

#### Fase de 64 8 — Coringa × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W57 | Coringa | Guerreiro | 20 | 27.79 | Cutelada, Golpe Devastador, Areia no Chão, Escudo Protetor | sem canal dominante |
| p2 | W34 | LuquEt4 | Guerreiro | 23 | 29.87 | Golpe Duplo, Grito de Guerra, Cutelada, Areia no Chão | crítico |

- Seed da partida: `3601920012618483097`
- Rodadas: **17**
- Vencedor: **LuquEt4** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 5123/7257 (70.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Coringa | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 2134 (2134 + 0) | 4248 (4248 + 0) |
| Cura (skill + roubo de vida) | 210 (0 + 210) | 0 (0 + 0) |
| MP gasto em ações | 696 | 982 |
| Skills / ataques básicos | 11 / 4 | 11 / 6 |
| Acertos / erros | 8 / 0 | 10 / 0 |
| Críticos (dano) | 0 (0) | 5 (3051) |
| Agiu primeiro (rodadas) | 0 | 17 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- Coringa aplicou: slowed (rodada 2), slowed (rodada 6), vulnerable (rodada 6), slowed (rodada 10)
- Coringa tentou sem sucesso: vulnerable (rodada 2), vulnerable (rodada 10), slowed (rodada 14)
- Coringa ativou: Escudo Protetor ×3
- LuquEt4 aplicou: slowed (rodada 2), slowed (rodada 6), vulnerable (rodada 6), frailty (rodada 7), stun (rodada 8), slowed (rodada 12)
- LuquEt4 tentou sem sucesso: vulnerable (rodada 2), stun (rodada 3), frailty (rodada 3), stun (rodada 4), stun (rodada 7), stun (rodada 10), stun (rodada 11), vulnerable (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15), slowed (rodada 16), stun (rodada 17)
- LuquEt4 ativou: Grito de Guerra ×3

Rodada a rodada:

| Rodada | Ordem (critério) | Coringa (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito de Guerra — executada, dano 0, MP −100 | 4033 / 7257 | 491 / 673 |
| 2 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −50 | Areia no Chão — executada, dano 0, MP −70 | 4033 / 7257 | 452 / 618 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 386, MP −60 | Golpe Duplo — executada, dano 985, MP −116 | 3086 / 6871 | 403 / 517 |
| 4 | p2 → p1 (score) | Golpe Devastador — executada, dano 326, MP −85 | Cutelada — executada, dano 330, MP −85 | 2788 / 6545 | 329 / 447 |
| 5 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito de Guerra — executada, dano 0, MP −100 | 2788 / 6545 | 263 / 362 |
| 6 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −50 | Areia no Chão — executada, dano 0, MP −70 | 2788 / 6545 | 224 / 307 |
| 7 | p2 → p1 (score) | Cutelada — executada, dano 464, MP −60 | Golpe Duplo — executada, dano 1121, MP −116 | 1713 / 6081 | 175 / 206 |
| 8 | p2 → p1 (score) | Golpe Devastador — cancelada por controle | Cutelada — executada, dano 376, MP −85 | 1337 / 6081 | 186 / 136 |
| 9 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito de Guerra — executada, dano 0, MP −100 | 1337 / 6081 | 120 / 51 |
| 10 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −50 | Ataque básico — executada, dano 163 | 1174 / 6081 | 81 / 66 |
| 11 | p2 → p1 (score) | Cutelada — executada, dano 386, MP −60 | Ataque básico — executada, dano 163 | 1049 / 5695 | 32 / 81 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 143 | Areia no Chão — executada, dano 0, MP −70 | 1063 / 5552 | 43 / 26 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 143 | Ataque básico — executada, dano 315 | 762 / 5409 | 54 / 41 |
| 14 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −50 | Ataque básico — executada, dano 315 | 447 / 5409 | 15 / 56 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 143 | Ataque básico — executada, dano 315 | 146 / 5266 | 26 / 71 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 143 | Areia no Chão — executada, dano 0, MP −70 | 160 / 5123 | 37 / 16 |
| 17 | p2 → p1 (score) | Ataque básico — cancelada por morte | Ataque básico — executada, dano 165 | -5 / 5123 | 37 / 31 |

#### Fase de 64 9 — liminhag0d × tioorochitwitch

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W59 | liminhag0d | Guerreiro | 22 | 29.64 | Golpe Poderoso, Investida, Estocada Seca, Guarda Alta | crítico + controle |
| p2 | W63 | tioorochitwitch | Guerreiro | 23 | 29.41 | Golpe Poderoso, Investida, Postura de Muro, Baluarte | defesa + sustento |

- Seed da partida: `1339762318995372611`
- Rodadas: **25**
- Vencedor: **tioorochitwitch** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 945/7189 (13.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | liminhag0d | tioorochitwitch |
|---|---|---|
| Dano causado (golpes + DoT) | 7050 (4754 + 2296) | 5297 (5297 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 806 (0 + 806) |
| MP gasto em ações | 870 | 1325 |
| Skills / ataques básicos | 16 / 6 | 24 / 0 |
| Acertos / erros | 14 / 0 | 22 / 2 |
| Críticos (dano) | 4 (1975) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 25 |
| Ações perdidas por controle | 2 | 1 |

Efeitos relevantes:
- liminhag0d aplicou: stun (rodada 9), bleed (rodada 11), bleed (rodada 15), bleed (rodada 22), fear (rodada 22)
- liminhag0d tentou sem sucesso: bleed (rodada 3), stun (rodada 4), bleed (rodada 4), fear (rodada 4), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), fear (rodada 8), stun (rodada 9), bleed (rodada 9), fear (rodada 9), stun (rodada 12), bleed (rodada 12), fear (rodada 12), stun (rodada 13), bleed (rodada 13), fear (rodada 13), stun (rodada 13), stun (rodada 16), bleed (rodada 16), fear (rodada 16), stun (rodada 17), bleed (rodada 17), fear (rodada 17), stun (rodada 17), stun (rodada 18), bleed (rodada 18), fear (rodada 18), stun (rodada 19), bleed (rodada 19), fear (rodada 19), stun (rodada 20), bleed (rodada 20), fear (rodada 20), stun (rodada 21), bleed (rodada 21), fear (rodada 21), stun (rodada 22), stun (rodada 23), bleed (rodada 23), fear (rodada 23), stun (rodada 24), bleed (rodada 24), fear (rodada 24)
- liminhag0d ativou: Guarda Alta ×4
- tioorochitwitch aplicou: stun (rodada 2), stun (rodada 5)
- tioorochitwitch tentou sem sucesso: stun (rodada 1), fear (rodada 1), stun (rodada 2), fear (rodada 2), stun (rodada 3), fear (rodada 3), stun (rodada 4), fear (rodada 4), stun (rodada 4), fear (rodada 5), stun (rodada 6), fear (rodada 6), stun (rodada 6), stun (rodada 7), fear (rodada 7), stun (rodada 8), fear (rodada 8), stun (rodada 8), stun (rodada 9), fear (rodada 9), stun (rodada 11), fear (rodada 11), stun (rodada 12), fear (rodada 12), stun (rodada 12), stun (rodada 14), fear (rodada 14), stun (rodada 14), stun (rodada 15), fear (rodada 15), stun (rodada 16), fear (rodada 16), stun (rodada 16), stun (rodada 17), fear (rodada 17), stun (rodada 18), fear (rodada 18), stun (rodada 18), stun (rodada 19), fear (rodada 19), stun (rodada 20), fear (rodada 20), stun (rodada 20), stun (rodada 21), fear (rodada 21), stun (rodada 22), fear (rodada 22), stun (rodada 22), stun (rodada 24), fear (rodada 24), stun (rodada 24), stun (rodada 25), fear (rodada 25)
- Leis disparadas por tioorochitwitch: PÂNICO (rodada 22)

Rodada a rodada:

| Rodada | Ordem (critério) | liminhag0d (p1) | tioorochitwitch (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Golpe Poderoso — executada, dano 276, MP −52 | 4533 / 7189 | 591 / 684 |
| 2 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Investida — executada, dano 261, MP −59 | 4272 / 7189 | 603 / 655 |
| 3 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 228, MP −52 | 4044 / 7189 | 553 / 633 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 654, MP −47 | Investida — executada, dano 261, MP −59 | 3783 / 6535 | 518 / 604 |
| 5 | p2 → p1 (score) | Guarda Alta — cancelada por controle | Golpe Poderoso — executada, dano 255, MP −52 | 3528 / 6583 | 530 / 582 |
| 6 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Investida — executada, dano 259, MP −59 | 3269 / 6632 | 485 / 553 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 211, MP −52 | 3058 / 6672 | 435 / 531 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 344, MP −47 | Investida — executada, dano 214, MP −59 | 2844 / 6368 | 400 / 502 |
| 9 | p2 → p1 (score) | Investida — executada, dano 381, MP −53 | Golpe Poderoso — executada, dano 211, MP −52 | 2633 / 6027 | 359 / 480 |
| 10 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Investida — cancelada por controle | 2633 / 6027 | 314 / 510 |
| 11 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 211, MP −52 | 2422 / 6067 | 264 / 488 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 344, MP −47 | Investida — executada, dano 214, MP −59 | 2208 / 5476 | 229 / 459 |
| 13 | p2 → p1 (score) | Investida — executada, dano 322, MP −53 | Golpe Poderoso — executada, dano 0, MP −52 | 2208 / 4867 | 188 / 437 |
| 14 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Investida — executada, dano 259, MP −59 | 1949 / 4629 | 143 / 408 |
| 15 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 211, MP −52 | 1738 / 4669 | 93 / 386 |
| 16 | p2 → p1 (score) | Golpe Poderoso — executada, dano 322, MP −47 | Investida — executada, dano 214, MP −59 | 1524 / 4100 | 58 / 357 |
| 17 | p2 → p1 (score) | Investida — executada, dano 322, MP −53 | Golpe Poderoso — executada, dano 211, MP −52 | 1313 / 3531 | 17 / 335 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 354 | Investida — executada, dano 259, MP −59 | 1054 / 2939 | 29 / 306 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 186 | Golpe Poderoso — executada, dano 255, MP −52 | 799 / 2801 | 41 / 284 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 186 | Investida — executada, dano 259, MP −59 | 540 / 2664 | 53 / 255 |
| 21 | p2 → p1 (score) | Golpe Poderoso — executada, dano 613, MP −47 | Golpe Poderoso — executada, dano 255, MP −52 | 285 / 2099 | 18 / 233 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 354 | Investida — executada, dano 259, MP −59 | 26 / 1794 | 30 / 204 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 186 | Golpe Poderoso — executada, dano 0, MP −52 | 26 / 1321 | 42 / 182 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 186 | Investida — executada, dano 25, MP −59 | 1 / 897 | 54 / 153 |
| 25 | p2 → p1 (score) | Golpe Poderoso — cancelada por morte | Golpe Poderoso — executada, dano 255, MP −52 | -254 / 945 | 54 / 131 |

#### Fase de 64 10 — MeikodRJ × Tenz

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W26 | MeikodRJ | Guerreiro | 22 | 29.75 | Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno | sustento |
| p2 | W08 | Tenz | Guerreiro | 23 | 28.71 | Golpe Poderoso, Soco de Placa, Gancho e Corda, Tomar Fôlego | crítico + sustento |

- Seed da partida: `11447462072290798616`
- Rodadas: **36**
- Vencedor: **MeikodRJ** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 931/4969 (18.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | MeikodRJ | Tenz |
|---|---|---|
| Dano causado (golpes + DoT) | 8362 (7482 + 880) | 8445 (8445 + 0) |
| Cura (skill + roubo de vida) | 4407 (3039 + 1368) | 2425 (662 + 1763) |
| MP gasto em ações | 1366 | 1716 |
| Skills / ataques básicos | 22 / 13 | 26 / 9 |
| Acertos / erros | 28 / 4 | 27 / 3 |
| Críticos (dano) | 2 (644) | 4 (1863) |
| Agiu primeiro (rodadas) | 34 | 2 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- MeikodRJ aplicou: vulnerable (rodada 2), bleed (rodada 16), bleed (rodada 35)
- MeikodRJ tentou sem sucesso: stun (rodada 1), bleed (rodada 1), stun (rodada 2), bleed (rodada 2), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 7), bleed (rodada 7), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 12), bleed (rodada 12), stun (rodada 13), bleed (rodada 13), vulnerable (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 16), stun (rodada 17), bleed (rodada 17), vulnerable (rodada 17), stun (rodada 18), bleed (rodada 18), stun (rodada 19), bleed (rodada 19), stun (rodada 21), bleed (rodada 21), stun (rodada 22), bleed (rodada 22), stun (rodada 23), bleed (rodada 23), stun (rodada 27), bleed (rodada 27), stun (rodada 28), bleed (rodada 28), stun (rodada 29), bleed (rodada 29), stun (rodada 30), bleed (rodada 30), stun (rodada 31), bleed (rodada 31), stun (rodada 32), bleed (rodada 32), stun (rodada 33), bleed (rodada 33), stun (rodada 34), bleed (rodada 34), stun (rodada 35), stun (rodada 36), bleed (rodada 36)
- Tenz aplicou: weakened (rodada 5), stun (rodada 6)
- Tenz tentou sem sucesso: stun (rodada 1), weakened (rodada 3), vulnerable (rodada 6), weakened (rodada 8), weakened (rodada 10), stun (rodada 11), weakened (rodada 13), weakened (rodada 15), stun (rodada 16), weakened (rodada 19)

Rodada a rodada:

| Rodada | Ordem (critério) | MeikodRJ (p1) | Tenz (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Golpe Poderoso — executada, dano 293, MP −47 | Gancho e Corda — executada, dano 0, MP −117 | 4969 / 5226 | 782 / 933 |
| 2 | p1 → p2 (score) | Mira Calma — executada, dano 609, MP −103 | Golpe Poderoso — executada, dano 345, MP −52 | 4624 / 4689 | 695 / 902 |
| 3 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Soco de Placa — executada, dano 336, MP −61 | 4288 / 4759 | 664 / 862 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Golpe Poderoso — executada, dano 345, MP −52 | 3976 / 4673 | 680 / 831 |
| 5 | p1 → p2 (score) | Golpe Poderoso — executada, dano 293, MP −47 | Soco de Placa — executada, dano 336, MP −61 | 3701 / 4450 | 649 / 791 |
| 6 | p2 → p1 (score) | Mira Calma — cancelada por controle | Gancho e Corda — executada, dano 0, MP −117 | 3701 / 4450 | 665 / 695 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 293, MP −47 | Golpe Poderoso — executada, dano 320, MP −52 | 3442 / 4224 | 634 / 664 |
| 8 | p1 → p2 (score) | Mira Calma — executada, dano 0, MP −103 | Soco de Placa — executada, dano 336, MP −61 | 3106 / 4294 | 547 / 624 |
| 9 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 320, MP −52 | 2842 / 4090 | 516 / 593 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Soco de Placa — executada, dano 539, MP −61 | 2336 / 4045 | 532 / 553 |
| 11 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Gancho e Corda — executada, dano 0, MP −117 | 3349 / 4045 | 465 / 457 |
| 12 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 320, MP −52 | 3085 / 3841 | 434 / 426 |
| 13 | p1 → p2 (score) | Mira Calma — executada, dano 530, MP −103 | Soco de Placa — executada, dano 336, MP −61 | 2860 / 3381 | 347 / 386 |
| 14 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 0, MP −52 | 2916 / 3110 | 316 / 355 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Soco de Placa — executada, dano 336, MP −61 | 2613 / 3022 | 332 / 315 |
| 16 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Gancho e Corda — executada, dano 0, MP −117 | 2669 / 2531 | 301 / 219 |
| 17 | p1 → p2 (score) | Mira Calma — executada, dano 530, MP −103 | Tomar Fôlego — executada, dano 0, MP −93 | 2780 / 2443 | 214 / 147 |
| 18 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 320, MP −52 | 2516 / 2239 | 183 / 116 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Soco de Placa — executada, dano 336, MP −61 | 2213 / 2151 | 199 / 76 |
| 20 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Golpe Poderoso — executada, dano 320, MP −52 | 2906 / 2218 | 132 / 45 |
| 21 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Ataque básico — executada, dano 300 | 2662 / 2010 | 101 / 66 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Golpe Poderoso — executada, dano 320, MP −52 | 2375 / 1919 | 117 / 35 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Ataque básico — executada, dano 188 | 2243 / 1687 | 86 / 56 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 0, MP −52 | 2243 / 1687 | 102 / 25 |
| 25 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Ataque básico — executada, dano 188 | 3068 / 1726 | 35 / 46 |
| 26 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 188 | 2880 / 1765 | 51 / 67 |
| 27 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 512, MP −52 | 2424 / 1601 | 20 / 36 |
| 28 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Ataque básico — executada, dano 0 | 2457 / 1443 | 36 / 57 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Golpe Poderoso — executada, dano 512, MP −52 | 1978 / 1392 | 52 / 26 |
| 30 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Ataque básico — executada, dano 188 | 1846 / 1160 | 21 / 47 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Ataque básico — executada, dano 188 | 1691 / 1041 | 37 / 68 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 237 | Golpe Poderoso — executada, dano 320, MP −52 | 1420 / 871 | 53 / 37 |
| 33 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Ataque básico — executada, dano 188 | 1288 / 639 | 22 / 58 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Golpe Poderoso — executada, dano 320, MP −52 | 1001 / 548 | 38 / 27 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Ataque básico — executada, dano 188 | 846 / 209 | 54 / 48 |
| 36 | p1 → p2 (score) | Golpe Poderoso — executada, dano 208, MP −47 | Ataque básico — cancelada por morte | 931 / -219 | 23 / 69 |

#### Fase de 64 11 — alanzoka × Bisteconee

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W02 | alanzoka | Guerreiro | 23 | 28.37 | Golpe Poderoso, Respirar Fundo, Soco de Placa, Guarda Cruzada | defesa + sustento |
| p2 | W49 | Bisteconee | Guerreiro | 22 | 28.60 | Cutelada, Mira Calma, Areia no Chão, Leitura de Terreno | controle |

- Seed da partida: `17311463052517239433`
- Rodadas: **26**
- Vencedor: **Bisteconee** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 148/4779 (3.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | alanzoka | Bisteconee |
|---|---|---|
| Dano causado (golpes + DoT) | 4631 (4631 + 0) | 9295 (6345 + 2950) |
| Cura (skill + roubo de vida) | 1876 (1696 + 180) | 0 (0 + 0) |
| MP gasto em ações | 1207 | 1164 |
| Skills / ataques básicos | 17 / 5 | 15 / 11 |
| Acertos / erros | 13 / 3 | 19 / 1 |
| Críticos (dano) | 1 (360) | 2 (1450) |
| Agiu primeiro (rodadas) | 14 | 12 |
| Ações perdidas por controle | 3 | 0 |

Efeitos relevantes:
- alanzoka tentou sem sucesso: weakened (rodada 5), weakened (rodada 14)
- alanzoka ativou: Guarda Cruzada ×4
- Leis disparadas por alanzoka: FERIDA ABERTA (rodada 8), FERIDA ABERTA (rodada 25)
- Bisteconee aplicou: slowed (rodada 1), stun (rodada 3), slowed (rodada 5), stun (rodada 7), vulnerable (rodada 7), bleed (rodada 8), slowed (rodada 9), stun (rodada 10), bleed (rodada 10), bleed (rodada 19), slowed (rodada 23), vulnerable (rodada 23), bleed (rodada 25), stun (rodada 26)
- Bisteconee tentou sem sucesso: vulnerable (rodada 1), stun (rodada 2), bleed (rodada 2), bleed (rodada 3), vulnerable (rodada 3), stun (rodada 4), bleed (rodada 4), vulnerable (rodada 5), stun (rodada 6), bleed (rodada 6), bleed (rodada 7), stun (rodada 8), vulnerable (rodada 9), stun (rodada 11), bleed (rodada 11), vulnerable (rodada 11), stun (rodada 12), bleed (rodada 12), slowed (rodada 13), stun (rodada 15), bleed (rodada 15), vulnerable (rodada 15), stun (rodada 16), bleed (rodada 16), slowed (rodada 17), stun (rodada 18), bleed (rodada 18), stun (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 21), bleed (rodada 21), stun (rodada 22), bleed (rodada 22), stun (rodada 24), bleed (rodada 24), stun (rodada 25), bleed (rodada 26)

Rodada a rodada:

| Rodada | Ordem (critério) | alanzoka (p1) | Bisteconee (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Guarda Cruzada — executada, dano 0, MP −111 | Areia no Chão — executada, dano 0, MP −62 | 7387 / 4779 | 734 / 767 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 419, MP −52 | Cutelada — executada, dano 578, MP −76 | 6825 / 4360 | 698 / 707 |
| 3 | p2 → p1 (score) | Soco de Placa — cancelada por controle | Mira Calma — executada, dano 361, MP −103 | 6464 / 4360 | 714 / 620 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 419, MP −52 | Ataque básico — executada, dano 127 | 6353 / 3941 | 678 / 636 |
| 5 | p1 → p2 (score) | Soco de Placa — executada, dano 409, MP −61 | Areia no Chão — executada, dano 0, MP −62 | 6369 / 3532 | 633 / 590 |
| 6 | p2 → p1 (score) | Guarda Cruzada — executada, dano 0, MP −111 | Cutelada — executada, dano 541, MP −76 | 5828 / 3532 | 538 / 530 |
| 7 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Mira Calma — executada, dano 321, MP −103 | 5507 / 3532 | 554 / 443 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 153 | 4764 / 3532 | 518 / 459 |
| 9 | p1 → p2 (score) | Soco de Placa — executada, dano 0, MP −61 | Areia no Chão — executada, dano 0, MP −62 | 4174 / 3532 | 473 / 413 |
| 10 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Cutelada — executada, dano 541, MP −76 | 3338 / 3532 | 489 / 353 |
| 11 | p2 → p1 (score) | Respirar Fundo — executada, dano 0, MP −82 | Mira Calma — executada, dano 872, MP −103 | 3019 / 3532 | 423 / 266 |
| 12 | p2 → p1 (score) | Guarda Cruzada — executada, dano 0, MP −111 | Ataque básico — executada, dano 203 | 2816 / 3532 | 328 / 282 |
| 13 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Areia no Chão — executada, dano 0, MP −62 | 2831 / 3144 | 292 / 236 |
| 14 | p1 → p2 (score) | Soco de Placa — executada, dano 409, MP −61 | Cutelada — executada, dano 0, MP −76 | 2847 / 2735 | 247 / 176 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Mira Calma — executada, dano 512, MP −103 | 2350 / 2347 | 211 / 89 |
| 16 | p1 → p2 (score) | Respirar Fundo — executada, dano 0, MP −82 | Ataque básico — executada, dano 203 | 2995 / 2347 | 145 / 105 |
| 17 | p1 → p2 (score) | Guarda Cruzada — executada, dano 0, MP −111 | Areia no Chão — executada, dano 0, MP −62 | 2995 / 2347 | 50 / 59 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 127 | 2868 / 2347 | 66 / 75 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Ataque básico — executada, dano 127 | 2756 / 1959 | 30 / 91 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 360 | Cutelada — executada, dano 541, MP −76 | 1934 / 1599 | 46 / 31 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 225 | Ataque básico — executada, dano 203 | 1445 / 1374 | 62 / 47 |
| 22 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Ataque básico — executada, dano 203 | 1257 / 986 | 26 / 63 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 225 | Areia no Chão — executada, dano 0, MP −62 | 1266 / 761 | 42 / 17 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 225 | Ataque básico — executada, dano 244 | 1031 / 536 | 58 / 33 |
| 25 | p2 → p1 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Ataque básico — executada, dano 244 | 212 / 148 | 22 / 49 |
| 26 | p2 → p1 (score) | Ataque básico — cancelada por morte | Ataque básico — executada, dano 244 | -32 / 148 | 22 / 65 |

#### Fase de 64 12 — TheBurntPeanut × DavyJones

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W54 | TheBurntPeanut | Guerreiro | 23 | 29.64 | Mão Dupla, Mira Calma, Provocação, Grito de Guerra | sem canal dominante |
| p2 | W29 | DavyJones | Guerreiro | 22 | 29.98 | Golpe Poderoso, Mira Calma, Paciência do Coveiro, Respirar Fundo | defesa + sustento |

- Seed da partida: `13270816932769152964`
- Rodadas: **16**
- Vencedor: **DavyJones** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1722/5333 (32.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | TheBurntPeanut | DavyJones |
|---|---|---|
| Dano causado (golpes + DoT) | 4880 (4454 + 426) | 5587 (4723 + 864) |
| Cura (skill + roubo de vida) | -204 (0 + -204) | 1269 (533 + 736) |
| MP gasto em ações | 1412 | 1086 |
| Skills / ataques básicos | 15 / 1 | 14 / 2 |
| Acertos / erros | 8 / 0 | 11 / 1 |
| Críticos (dano) | 3 (2240) | 0 (0) |
| Agiu primeiro (rodadas) | 12 | 4 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- TheBurntPeanut aplicou: weakened (rodada 2), vulnerable (rodada 4), weakened (rodada 10), weakened (rodada 14), bleed (rodada 15)
- TheBurntPeanut tentou sem sucesso: bleed (rodada 3), bleed (rodada 3), bleed (rodada 4), weakened (rodada 6), bleed (rodada 7), bleed (rodada 7), bleed (rodada 8), vulnerable (rodada 8), bleed (rodada 11), bleed (rodada 11), bleed (rodada 12), vulnerable (rodada 12), bleed (rodada 15), bleed (rodada 16)
- TheBurntPeanut ativou: Grito de Guerra ×4
- DavyJones aplicou: poison (rodada 1), frailty (rodada 1), poison (rodada 7), vulnerable (rodada 9), poison (rodada 14), frailty (rodada 14)
- DavyJones tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 3), vulnerable (rodada 3), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), frailty (rodada 7), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), vulnerable (rodada 16)

Rodada a rodada:

| Rodada | Ordem (critério) | TheBurntPeanut (p1) | DavyJones (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −100 | Paciência do Coveiro — executada, dano 0, MP −125 | 5300 / 5333 | 953 / 704 |
| 2 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Golpe Poderoso — executada, dano 363, MP −47 | 4873 / 5333 | 913 / 677 |
| 3 | p1 → p2 (score) | Mão Dupla — executada, dano 496, MP −95 | Mira Calma — executada, dano 875, MP −103 | 3416 / 4985 | 849 / 594 |
| 4 | p1 → p2 (score) | Mira Calma — executada, dano 570, MP −116 | Golpe Poderoso — executada, dano 0, MP −47 | 3397 / 4415 | 764 / 567 |
| 5 | p1 → p2 (score) | Grito de Guerra — executada, dano 0, MP −100 | Ataque básico — executada, dano 192 | 3125 / 4447 | 695 / 587 |
| 6 | p1 → p2 (score) | Provocação — executada, dano 0, MP −71 | Golpe Poderoso — executada, dano 336, MP −47 | 2789 / 4504 | 655 / 560 |
| 7 | p1 → p2 (score) | Mão Dupla — executada, dano 744, MP −95 | Paciência do Coveiro — executada, dano 0, MP −125 | 2848 / 3760 | 591 / 455 |
| 8 | p1 → p2 (score) | Mira Calma — executada, dano 752, MP −116 | Golpe Poderoso — executada, dano 336, MP −47 | 2492 / 3065 | 506 / 428 |
| 9 | p2 → p1 (score) | Grito de Guerra — executada, dano 0, MP −100 | Mira Calma — executada, dano 761, MP −103 | 1651 / 3194 | 437 / 345 |
| 10 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Golpe Poderoso — executada, dano 403, MP −47 | 1168 / 3262 | 397 / 318 |
| 11 | p1 → p2 (score) | Mão Dupla — executada, dano 496, MP −95 | Ataque básico — executada, dano 158 | 969 / 2792 | 333 / 338 |
| 12 | p1 → p2 (score) | Mira Calma — executada, dano 501, MP −116 | Golpe Poderoso — executada, dano 269, MP −47 | 660 / 2336 | 248 / 311 |
| 13 | p1 → p2 (score) | Grito de Guerra — executada, dano 0, MP −100 | Respirar Fundo — executada, dano 0, MP −73 | 660 / 2869 | 179 / 258 |
| 14 | p1 → p2 (score) | Provocação — executada, dano 0, MP −71 | Paciência do Coveiro — executada, dano 0, MP −125 | 660 / 2869 | 139 / 153 |
| 15 | p1 → p2 (score) | Mão Dupla — executada, dano 744, MP −95 | Golpe Poderoso — executada, dano 269, MP −47 | 386 / 1957 | 75 / 126 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 151 | Mira Calma — executada, dano 761, MP −103 | -427 / 1722 | 106 / 43 |

#### Fase de 64 13 — SkipNhO × Tealzlol

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W52 | SkipNhO | Guerreiro | 23 | 28.02 | Golpe Poderoso, Postura de Muro, Pisada de Ferro, Juramento da Muralha | defesa + sustento |
| p2 | W61 | Tealzlol | Guerreiro | 19 | 28.14 | Golpe Poderoso, Mira Calma, Fôlego de Marcha, Ritmo de Duelo | crítico + sustento |

- Seed da partida: `15329195925884803276`
- Rodadas: **22**
- Vencedor: **SkipNhO** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4250/7167 (59.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | SkipNhO | Tealzlol |
|---|---|---|
| Dano causado (golpes + DoT) | 5186 (5186 + 0) | 3885 (3313 + 572) |
| Cura (skill + roubo de vida) | 968 (0 + 968) | 657 (0 + 657) |
| MP gasto em ações | 1452 | 700 |
| Skills / ataques básicos | 19 / 3 | 15 / 6 |
| Acertos / erros | 17 / 1 | 14 / 2 |
| Críticos (dano) | 2 (902) | 5 (1288) |
| Agiu primeiro (rodadas) | 21 | 1 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- SkipNhO aplicou: slowed (rodada 9)
- SkipNhO tentou sem sucesso: slowed (rodada 15), slowed (rodada 21)
- SkipNhO ativou: Juramento da Muralha ×4
- Tealzlol aplicou: bleed (rodada 4), vulnerable (rodada 4)
- Tealzlol tentou sem sucesso: bleed (rodada 3), bleed (rodada 5), bleed (rodada 8), bleed (rodada 10), bleed (rodada 12), bleed (rodada 13), bleed (rodada 14), bleed (rodada 15), bleed (rodada 16), bleed (rodada 17), bleed (rodada 18), bleed (rodada 19), bleed (rodada 21)
- Tealzlol ativou: Fôlego de Marcha ×3, Ritmo de Duelo ×2

Rodada a rodada:

| Rodada | Ordem (critério) | SkipNhO (p1) | Tealzlol (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Fôlego de Marcha — executada, dano 0, MP −52 | 7167 / 4334 | 614 / 458 |
| 2 | p1 → p2 (score) | Golpe Poderoso — executada, dano 324, MP −52 | Ritmo de Duelo — executada, dano 0, MP −67 | 7167 / 4010 | 597 / 401 |
| 3 | p1 → p2 (score) | Pisada de Ferro — executada, dano 0, MP −68 | Golpe Poderoso — executada, dano 196, MP −33 | 6971 / 4049 | 564 / 378 |
| 4 | p1 → p2 (score) | Golpe Poderoso — executada, dano 324, MP −52 | Mira Calma — executada, dano 419, MP −73 | 6616 / 3808 | 547 / 315 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Golpe Poderoso — executada, dano 234, MP −33 | 6130 / 3681 | 582 / 292 |
| 6 | p1 → p2 (score) | Golpe Poderoso — executada, dano 324, MP −52 | Fôlego de Marcha — executada, dano 0, MP −52 | 5908 / 3357 | 565 / 250 |
| 7 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Ritmo de Duelo — executada, dano 0, MP −67 | 5908 / 3357 | 448 / 193 |
| 8 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −52 | Golpe Poderoso — executada, dano 295, MP −33 | 5673 / 3116 | 431 / 170 |
| 9 | p1 → p2 (score) | Pisada de Ferro — executada, dano 331, MP −68 | Mira Calma — executada, dano 0, MP −73 | 5739 / 2785 | 398 / 107 |
| 10 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −52 | Golpe Poderoso — executada, dano 196, MP −33 | 5603 / 2524 | 381 / 84 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 173 | Fôlego de Marcha — executada, dano 0, MP −52 | 5637 / 2351 | 416 / 42 |
| 12 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −52 | Golpe Poderoso — executada, dano 331, MP −33 | 5366 / 2117 | 399 / 19 |
| 13 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Ataque básico — executada, dano 106 | 5260 / 2138 | 282 / 29 |
| 14 | p1 → p2 (score) | Golpe Poderoso — executada, dano 451, MP −52 | Ataque básico — executada, dano 158 | 5192 / 1718 | 265 / 39 |
| 15 | p1 → p2 (score) | Pisada de Ferro — executada, dano 331, MP −68 | Golpe Poderoso — executada, dano 273, MP −33 | 4985 / 1441 | 232 / 16 |
| 16 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −52 | Ataque básico — executada, dano 106 | 4939 / 1162 | 215 / 26 |
| 17 | p1 → p2 (score) | Ataque básico — executada, dano 173 | Ataque básico — executada, dano 289 | 4684 / 1046 | 250 / 36 |
| 18 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −52 | Golpe Poderoso — executada, dano 331, MP −33 | 4413 / 812 | 233 / 13 |
| 19 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Ataque básico — executada, dano 106 | 4307 / 833 | 116 / 23 |
| 20 | p1 → p2 (score) | Golpe Poderoso — executada, dano 451, MP −52 | Ataque básico — executada, dano 0 | 4397 / 382 | 99 / 33 |
| 21 | p1 → p2 (score) | Pisada de Ferro — executada, dano 331, MP −68 | Golpe Poderoso — executada, dano 273, MP −33 | 4190 / 105 | 66 / 10 |
| 22 | p1 → p2 (score) | Golpe Poderoso — executada, dano 300, MP −52 | Ataque básico — cancelada por morte | 4250 / -195 | 49 / 10 |

#### Fase de 64 14 — boltz × lubatv

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W21 | boltz | Guerreiro | 21 | 27.79 | Investida, Soco de Placa, Leitura de Terreno, Olho de Ferreiro | sustento |
| p2 | W23 | lubatv | Guerreiro | 22 | 29.17 | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | crítico + sustento |

- Seed da partida: `15144210590413717805`
- Rodadas: **15**
- Vencedor: **lubatv** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2423/5275 (45.9%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | boltz | lubatv |
|---|---|---|
| Dano causado (golpes + DoT) | 3485 (1957 + 1528) | 6190 (6190 + 0) |
| Cura (skill + roubo de vida) | 526 (0 + 526) | 633 (633 + 0) |
| MP gasto em ações | 653 | 1097 |
| Skills / ataques básicos | 13 / 0 | 10 / 4 |
| Acertos / erros | 8 / 1 | 9 / 1 |
| Críticos (dano) | 2 (708) | 5 (3388) |
| Agiu primeiro (rodadas) | 0 | 15 |
| Ações perdidas por controle | 1 | 1 |

Efeitos relevantes:
- boltz aplicou: poison (rodada 3), weakened (rodada 3), bleed (rodada 4), stun (rodada 4), poison (rodada 7), weakened (rodada 7), weakened (rodada 11)
- boltz tentou sem sucesso: bleed (rodada 2), poison (rodada 2), stun (rodada 2), bleed (rodada 3), poison (rodada 4), bleed (rodada 7), bleed (rodada 8), poison (rodada 8), stun (rodada 8), bleed (rodada 10), poison (rodada 10), stun (rodada 10), bleed (rodada 11), poison (rodada 11), bleed (rodada 12), poison (rodada 12), stun (rodada 12)
- boltz ativou: Olho de Ferreiro ×4
- lubatv aplicou: stun (rodada 14)
- lubatv tentou sem sucesso: stun (rodada 2), stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 6), vulnerable (rodada 6), stun (rodada 8), stun (rodada 8), stun (rodada 10), stun (rodada 11), stun (rodada 14), stun (rodada 15)
- lubatv ativou: Postura Impecável ×3
- Leis disparadas por lubatv: FERIDA SÉPTICA (rodada 4)

Rodada a rodada:

| Rodada | Ordem (critério) | boltz (p1) | lubatv (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Olho de Ferreiro — executada, dano 0, MP −56 | Postura Impecável — executada, dano 0, MP −131 | 5385 / 5275 | 690 / 777 |
| 2 | p2 → p1 (score) | Investida — executada, dano 235, MP −47 | Esmagar — executada, dano 1160, MP −144 | 4288 / 5040 | 681 / 651 |
| 3 | p2 → p1 (score) | Soco de Placa — executada, dano 322, MP −49 | Quebra-Guarda — executada, dano 714, MP −63 | 3660 / 4718 | 670 / 606 |
| 4 | p2 → p1 (score) | Investida — executada, dano 235, MP −47 | Ataque básico — executada, dano 413 | 3310 / 4404 | 661 / 624 |
| 5 | p2 → p1 (score) | Olho de Ferreiro — executada, dano 0, MP −56 | Ataque básico — cancelada por controle | 3310 / 4114 | 643 / 642 |
| 6 | p2 → p1 (score) | Investida — executada, dano 0, MP −47 | Quebra-Guarda — executada, dano 461, MP −63 | 2849 / 3824 | 634 / 597 |
| 7 | p2 → p1 (score) | Soco de Placa — executada, dano 200, MP −49 | Postura Impecável — executada, dano 0, MP −131 | 2903 / 3545 | 623 / 484 |
| 8 | p2 → p1 (score) | Investida — executada, dano 193, MP −47 | Esmagar — executada, dano 1030, MP −144 | 1925 / 3194 | 614 / 358 |
| 9 | p2 → p1 (score) | Olho de Ferreiro — executada, dano 0, MP −56 | Quebra-Guarda — executada, dano 0, MP −63 | 1925 / 3036 | 596 / 313 |
| 10 | p2 → p1 (score) | Investida — executada, dano 193, MP −47 | Ataque básico — executada, dano 468 | 1509 / 2685 | 587 / 331 |
| 11 | p2 → p1 (score) | Soco de Placa — executada, dano 386, MP −49 | Ataque básico — executada, dano 317 | 1296 / 2141 | 576 / 349 |
| 12 | p2 → p1 (score) | Investida — executada, dano 193, MP −47 | Tomar Fôlego — executada, dano 0, MP −83 | 1348 / 2423 | 567 / 284 |
| 13 | p2 → p1 (score) | Olho de Ferreiro — executada, dano 0, MP −56 | Postura Impecável — executada, dano 0, MP −131 | 1348 / 2423 | 549 / 171 |
| 14 | p2 → p1 (score) | Investida — cancelada por controle | Esmagar — executada, dano 1315, MP −144 | 33 / 2423 | 587 / 45 |
| 15 | p2 → p1 (score) | Investida — cancelada por morte | Ataque básico — executada, dano 312 | -279 / 2423 | 587 / 63 |

#### Fase de 64 15 — suetam1v4 × babi

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W51 | suetam1v4 | Guerreiro | 21 | 27.91 | Golpe Duplo, Tremor de Bigorna, Areia no Chão, Postura de Muro | sem canal dominante |
| p2 | W53 | babi | Guerreiro | 24 | 28.48 | Rasgo de Gancho, Postura de Muro, Sangue nos Olhos, Marca do Açougueiro | sustento |

- Seed da partida: `12954259252142384667`
- Rodadas: **15**
- Vencedor: **babi** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1371/6153 (22.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | suetam1v4 | babi |
|---|---|---|
| Dano causado (golpes + DoT) | 4945 (2736 + 2209) | 5824 (3992 + 1832) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 163 (0 + 163) |
| MP gasto em ações | 689 | 312 |
| Skills / ataques básicos | 10 / 4 | 4 / 11 |
| Acertos / erros | 9 / 1 | 11 / 0 |
| Críticos (dano) | 2 (1124) | 5 (2236) |
| Agiu primeiro (rodadas) | 0 | 15 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- suetam1v4 aplicou: frailty (rodada 2), poison (rodada 6), frailty (rodada 6), poison (rodada 7), slowed (rodada 9), bleed (rodada 12), slowed (rodada 13), bleed (rodada 14)
- suetam1v4 tentou sem sucesso: slowed (rodada 1), stun (rodada 2), bleed (rodada 2), poison (rodada 2), stun (rodada 3), bleed (rodada 3), poison (rodada 3), stun (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), slowed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), stun (rodada 8), vulnerable (rodada 9), stun (rodada 11), bleed (rodada 11), poison (rodada 11), stun (rodada 12), poison (rodada 12), vulnerable (rodada 13), stun (rodada 14), poison (rodada 14), stun (rodada 14)
- Leis disparadas por suetam1v4: FERIDA ABERTA (rodada 9), FERIDA ABERTA (rodada 13)
- babi aplicou: vulnerable (rodada 1), vulnerable (rodada 9), bleed (rodada 9), vulnerable (rodada 13), bleed (rodada 13)
- babi tentou sem sucesso: bleed (rodada 1), vulnerable (rodada 5)
- Leis disparadas por babi: TOXICIDADE (rodada 7), FERIDA SÉPTICA (rodada 12), FERIDA SÉPTICA (rodada 14)

Rodada a rodada:

| Rodada | Ordem (critério) | suetam1v4 (p1) | babi (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −56 | Sangue nos Olhos — executada, dano 0, MP −78 | 5734 / 6153 | 523 / 1130 |
| 2 | p2 → p1 (score) | Golpe Duplo — executada, dano 506, MP −92 | Ataque básico — executada, dano 494 | 5240 / 5647 | 442 / 1158 |
| 3 | p2 → p1 (score) | Tremor de Bigorna — executada, dano 375, MP −63 | Ataque básico — executada, dano 309 | 4931 / 4547 | 390 / 1186 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 139 | Ataque básico — executada, dano 416 | 4515 / 4524 | 401 / 1208 |
| 5 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −56 | Sangue nos Olhos — executada, dano 0, MP −78 | 4515 / 4524 | 356 / 1130 |
| 6 | p2 → p1 (score) | Golpe Duplo — executada, dano 306, MP −92 | Ataque básico — executada, dano 260 | 4255 / 4290 | 275 / 1158 |
| 7 | p2 → p1 (score) | Ataque básico — executada, dano 139 | Ataque básico — executada, dano 416 | 3839 / 4194 | 286 / 1186 |
| 8 | p2 → p1 (score) | Tremor de Bigorna — executada, dano 375, MP −63 | Ataque básico — executada, dano 260 | 3579 / 3744 | 234 / 1208 |
| 9 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −56 | Sangue nos Olhos — executada, dano 0, MP −78 | 3121 / 3597 | 189 / 1130 |
| 10 | p2 → p1 (score) | Golpe Duplo — executada, dano 0, MP −92 | Ataque básico — executada, dano 309 | 2354 / 3499 | 108 / 1158 |
| 11 | p2 → p1 (score) | Ataque básico — executada, dano 139 | Ataque básico — executada, dano 309 | 2045 / 3262 | 119 / 1186 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 139 | Ataque básico — executada, dano 416 | 1629 / 3055 | 130 / 1208 |
| 13 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −56 | Sangue nos Olhos — executada, dano 0, MP −78 | 1171 / 2625 | 85 / 1130 |
| 14 | p2 → p1 (score) | Tremor de Bigorna — executada, dano 618, MP −63 | Ataque básico — executada, dano 309 | 404 / 1663 | 33 / 1158 |
| 15 | p2 → p1 (score) | Ataque básico — cancelada por morte | Ataque básico — executada, dano 494 | -90 / 1371 | 33 / 1186 |

#### Fase de 64 16 — aXtLOL × brtt

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W43 | aXtLOL | Guerreiro | 23 | 29.75 | Travar o Pulso, Mira Calma, Ferro Contra Ferro, Ritmo de Duelo | sustento |
| p2 | W13 | brtt | Guerreiro | 21 | 29.98 | Respirar Fundo, Mira Calma, Estocada Seca, Soco de Placa | controle + sustento |

- Seed da partida: `9777167068430930388`
- Rodadas: **13**
- Vencedor: **aXtLOL** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2470/5454 (45.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | aXtLOL | brtt |
|---|---|---|
| Dano causado (golpes + DoT) | 5205 (4867 + 338) | 3175 (1898 + 1277) |
| Cura (skill + roubo de vida) | 191 (0 + 191) | 496 (424 + 72) |
| MP gasto em ações | 1041 | 656 |
| Skills / ataques básicos | 11 / 2 | 10 / 2 |
| Acertos / erros | 7 / 0 | 7 / 1 |
| Críticos (dano) | 1 (1267) | 0 (0) |
| Agiu primeiro (rodadas) | 13 | 0 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- aXtLOL aplicou: vulnerable (rodada 3), weakened (rodada 4), bleed (rodada 9), weakened (rodada 9), weakened (rodada 12)
- aXtLOL tentou sem sucesso: weakened (rodada 2), bleed (rodada 3), bleed (rodada 4), bleed (rodada 5), weakened (rodada 7), bleed (rodada 8), vulnerable (rodada 8), bleed (rodada 10), slowed (rodada 12), bleed (rodada 13), vulnerable (rodada 13)
- aXtLOL ativou: Ritmo de Duelo ×3
- Leis disparadas por aXtLOL: FERIDA SÉPTICA (rodada 5)
- brtt aplicou: bleed (rodada 4), poison (rodada 5), fear (rodada 7), vulnerable (rodada 10), bleed (rodada 12)
- brtt tentou sem sucesso: bleed (rodada 1), stun (rodada 2), bleed (rodada 2), poison (rodada 2), fear (rodada 2), vulnerable (rodada 2), stun (rodada 3), bleed (rodada 3), poison (rodada 3), fear (rodada 3), weakened (rodada 3), stun (rodada 4), poison (rodada 4), fear (rodada 4), stun (rodada 5), bleed (rodada 5), fear (rodada 5), vulnerable (rodada 5), stun (rodada 6), bleed (rodada 6), poison (rodada 6), fear (rodada 6), weakened (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), bleed (rodada 8), stun (rodada 10), bleed (rodada 10), poison (rodada 10), fear (rodada 10)

Rodada a rodada:

| Rodada | Ordem (critério) | aXtLOL (p1) | brtt (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Ritmo de Duelo — executada, dano 0, MP −105 | Estocada Seca — executada, dano 0, MP −56 | 5454 / 4244 | 661 / 551 |
| 2 | p1 → p2 (score) | Travar o Pulso — executada, dano 0, MP −70 | Mira Calma — executada, dano 405, MP −92 | 5049 / 4244 | 638 / 479 |
| 3 | p1 → p2 (score) | Mira Calma — executada, dano 971, MP −116 | Soco de Placa — executada, dano 243, MP −49 | 4844 / 3285 | 569 / 450 |
| 4 | p1 → p2 (score) | Ferro Contra Ferro — executada, dano 682, MP −84 | Ataque básico — executada, dano 110 | 4761 / 2608 | 532 / 470 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 263 | Mira Calma — executada, dano 405, MP −92 | 4148 / 2365 | 579 / 398 |
| 6 | p1 → p2 (score) | Ritmo de Duelo — executada, dano 0, MP −105 | Soco de Placa — executada, dano 243, MP −49 | 3606 / 2377 | 521 / 369 |
| 7 | p1 → p2 (score) | Travar o Pulso — executada, dano 0, MP −70 | Ataque básico — executada, dano 133 | 3174 / 2383 | 498 / 389 |
| 8 | p1 → p2 (score) | Mira Calma — executada, dano 844, MP −116 | Estocada Seca — executada, dano 0, MP −56 | 3126 / 1539 | 429 / 353 |
| 9 | p1 → p2 (score) | Ferro Contra Ferro — executada, dano 577, MP −84 | Respirar Fundo — executada, dano 0, MP −65 | 3068 / 1217 | 392 / 308 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 263 | Mira Calma — executada, dano 359, MP −92 | 2638 / 802 | 439 / 236 |
| 11 | p1 → p2 (score) | Ritmo de Duelo — executada, dano 0, MP −105 | Soco de Placa — executada, dano 0, MP −49 | 2638 / 802 | 381 / 207 |
| 12 | p1 → p2 (score) | Travar o Pulso — executada, dano 0, MP −70 | Estocada Seca — executada, dano 0, MP −56 | 2638 / 802 | 358 / 171 |
| 13 | p1 → p2 (score) | Mira Calma — executada, dano 1267, MP −116 | Mira Calma — cancelada por morte | 2470 / -465 | 289 / 171 |

#### Fase de 64 17 — frttt × belrodrigues

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W60 | frttt | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca | sustento |
| p2 | W04 | belrodrigues | Guerreiro | 21 | 27.91 | Fúria, Investida, Fôlego de Marcha, Mira Calma | defesa |

- Seed da partida: `3553688020881821888`
- Rodadas: **20**
- Vencedor: **frttt** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3590/5379 (66.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | belrodrigues |
|---|---|---|
| Dano causado (golpes + DoT) | 6359 (5194 + 1165) | 2515 (2515 + 0) |
| Cura (skill + roubo de vida) | 726 (0 + 726) | 322 (0 + 322) |
| MP gasto em ações | 1432 | 808 |
| Skills / ataques básicos | 16 / 3 | 11 / 9 |
| Acertos / erros | 10 / 1 | 10 / 6 |
| Críticos (dano) | 4 (3175) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 20 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- frttt aplicou: bleed (rodada 7), bleed (rodada 18)
- frttt tentou sem sucesso: bleed (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 9), bleed (rodada 9), vulnerable (rodada 9), stun (rodada 10), bleed (rodada 10), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), vulnerable (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), vulnerable (rodada 20)
- frttt ativou: Pausa Útil ×4
- belrodrigues aplicou: stun (rodada 11)
- belrodrigues tentou sem sucesso: stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 8), stun (rodada 9), bleed (rodada 9), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 16), bleed (rodada 16), stun (rodada 16), stun (rodada 20), bleed (rodada 20), stun (rodada 20)
- belrodrigues ativou: Fúria ×2, Fôlego de Marcha ×2

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | belrodrigues (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Fúria — executada, dano 0, MP −152 | 5379 / 5834 | 990 / 451 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Fôlego de Marcha — executada, dano 0, MP −65 | 5379 / 5834 | 962 / 398 |
| 3 | p2 → p1 (score) | Golpe Devastador — executada, dano 633, MP −120 | Investida — executada, dano 0, MP −47 | 5379 / 5201 | 884 / 363 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 1021, MP −116 | Mira Calma — executada, dano 516, MP −92 | 5026 / 4247 | 810 / 283 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 172 | Fúria — executada, dano 0, MP −152 | 5053 / 4075 | 852 / 143 |
| 6 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Investida — executada, dano 323, MP −47 | 4730 / 4116 | 828 / 108 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Fôlego de Marcha — executada, dano 0, MP −65 | 4730 / 4116 | 800 / 55 |
| 8 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Investida — executada, dano 306, MP −47 | 4424 / 3922 | 722 / 20 |
| 9 | p2 → p1 (score) | Mira Calma — executada, dano 888, MP −116 | Ataque básico — executada, dano 141 | 4425 / 2819 | 648 / 32 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 172 | Ataque básico — executada, dano 0 | 4452 / 2414 | 690 / 44 |
| 11 | p2 → p1 (score) | Pausa Útil — cancelada por controle | Ataque básico — executada, dano 141 | 4311 / 2432 | 718 / 56 |
| 12 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Investida — executada, dano 306, MP −47 | 4005 / 2471 | 694 / 21 |
| 13 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 141 | 3864 / 2489 | 666 / 33 |
| 14 | p2 → p1 (score) | Golpe Devastador — executada, dano 395, MP −120 | Ataque básico — executada, dano 141 | 3786 / 2112 | 588 / 45 |
| 15 | p2 → p1 (score) | Mira Calma — executada, dano 554, MP −116 | Ataque básico — executada, dano 0 | 3874 / 1558 | 514 / 57 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 172 | Investida — executada, dano 250, MP −47 | 3651 / 1418 | 556 / 22 |
| 17 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Ataque básico — executada, dano 0 | 3651 / 1418 | 532 / 34 |
| 18 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 0 | 3651 / 1418 | 504 / 46 |
| 19 | p2 → p1 (score) | Golpe Devastador — executada, dano 633, MP −120 | Ataque básico — executada, dano 0 | 3752 / 552 | 426 / 58 |
| 20 | p2 → p1 (score) | Mira Calma — executada, dano 554, MP −116 | Investida — executada, dano 250, MP −47 | 3590 / -203 | 352 / 23 |

#### Fase de 64 18 — bakzera × furq

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W30 | bakzera | Guerreiro | 23 | 29.98 | Golpe Duplo, Mira Calma, Provocação, Veterania | crítico + controle |
| p2 | W28 | furq | Guerreiro | 23 | 29.52 | Golpe Poderoso, Quebra-Guarda, Guarda Cruzada, Areia no Chão | defesa + controle + sustento |

- Seed da partida: `17700058813706348266`
- Rodadas: **39**
- Vencedor: **bakzera** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 529/5860 (9.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | bakzera | furq |
|---|---|---|
| Dano causado (golpes + DoT) | 7931 (6154 + 1777) | 5331 (4863 + 468) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 187 (0 + 187) |
| MP gasto em ações | 1668 | 1429 |
| Skills / ataques básicos | 18 / 17 | 22 / 12 |
| Acertos / erros | 18 / 5 | 18 / 9 |
| Críticos (dano) | 4 (2540) | 0 (0) |
| Agiu primeiro (rodadas) | 17 | 22 |
| Ações perdidas por controle | 4 | 4 |

Efeitos relevantes:
- bakzera aplicou: weakened (rodada 2), bleed (rodada 3), poison (rodada 3), fear (rodada 4), weakened (rodada 7), frailty (rodada 8), vulnerable (rodada 9), stun (rodada 15), stun (rodada 16), weakened (rodada 17), weakened (rodada 21), stun (rodada 27), weakened (rodada 28), stun (rodada 29), bleed (rodada 29), fear (rodada 30), weakened (rodada 32), weakened (rodada 36), poison (rodada 39)
- bakzera tentou sem sucesso: stun (rodada 3), fear (rodada 3), frailty (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), vulnerable (rodada 4), stun (rodada 5), bleed (rodada 5), poison (rodada 5), fear (rodada 5), stun (rodada 8), bleed (rodada 8), poison (rodada 8), fear (rodada 8), stun (rodada 9), bleed (rodada 9), poison (rodada 9), fear (rodada 9), weakened (rodada 13), bleed (rodada 15), poison (rodada 15), fear (rodada 15), vulnerable (rodada 15), bleed (rodada 16), poison (rodada 16), fear (rodada 16), stun (rodada 18), bleed (rodada 18), poison (rodada 18), fear (rodada 18), stun (rodada 19), bleed (rodada 19), poison (rodada 19), fear (rodada 19), stun (rodada 23), bleed (rodada 23), poison (rodada 23), fear (rodada 23), stun (rodada 24), bleed (rodada 24), poison (rodada 24), fear (rodada 24), weakened (rodada 25), bleed (rodada 27), poison (rodada 27), fear (rodada 27), poison (rodada 29), fear (rodada 29), stun (rodada 30), bleed (rodada 30), poison (rodada 30), stun (rodada 31), bleed (rodada 31), poison (rodada 31), fear (rodada 31), stun (rodada 33), bleed (rodada 33), poison (rodada 33), fear (rodada 33), stun (rodada 37), bleed (rodada 37), poison (rodada 37), fear (rodada 37), stun (rodada 39), bleed (rodada 39), fear (rodada 39)
- bakzera ativou: Veterania ×3
- furq aplicou: slowed (rodada 2), vulnerable (rodada 2), slowed (rodada 7), stun (rodada 10), slowed (rodada 12), slowed (rodada 21), vulnerable (rodada 21), stun (rodada 22), bleed (rodada 30), stun (rodada 33), stun (rodada 34)
- furq tentou sem sucesso: vulnerable (rodada 7), stun (rodada 9), bleed (rodada 9), vulnerable (rodada 9), bleed (rodada 10), vulnerable (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 18), bleed (rodada 18), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), bleed (rodada 22), stun (rodada 23), bleed (rodada 23), stun (rodada 25), bleed (rodada 25), stun (rodada 27), bleed (rodada 27), stun (rodada 30), stun (rodada 31), bleed (rodada 31), stun (rodada 32), bleed (rodada 32), bleed (rodada 33), bleed (rodada 34), stun (rodada 35), bleed (rodada 35), stun (rodada 36), bleed (rodada 36), stun (rodada 38), bleed (rodada 38)
- furq ativou: Guarda Cruzada ×3
- Leis disparadas por furq: PÂNICO (rodada 4), PÂNICO (rodada 30)

Rodada a rodada:

| Rodada | Ordem (critério) | bakzera (p1) | furq (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Guarda Cruzada — executada, dano 0, MP −111 | 5860 / 7593 | 909 / 645 |
| 2 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Areia no Chão — executada, dano 0, MP −70 | 5860 / 7593 | 858 / 594 |
| 3 | p2 → p1 (score) | Golpe Duplo — executada, dano 623, MP −116 | Golpe Poderoso — executada, dano 0, MP −52 | 5860 / 6970 | 762 / 561 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 745, MP −116 | Quebra-Guarda — executada, dano 0, MP −70 | 5860 / 5809 | 666 / 510 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Golpe Poderoso — executada, dano 0, MP −52 | 5860 / 5188 | 686 / 477 |
| 6 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Guarda Cruzada — executada, dano 0, MP −111 | 5860 / 5075 | 595 / 385 |
| 7 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Areia no Chão — executada, dano 0, MP −70 | 5860 / 4962 | 544 / 334 |
| 8 | p2 → p1 (score) | Golpe Duplo — executada, dano 623, MP −116 | Golpe Poderoso — executada, dano 0, MP −52 | 5860 / 4226 | 448 / 301 |
| 9 | p1 → p2 (score) | Mira Calma — executada, dano 409, MP −116 | Quebra-Guarda — executada, dano 406, MP −70 | 5454 / 3833 | 352 / 250 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 388, MP −52 | 5066 / 3848 | 372 / 217 |
| 11 | p1 → p2 (score) | Veterania — cancelada por controle | Guarda Cruzada — executada, dano 0, MP −111 | 5066 / 3848 | 392 / 125 |
| 12 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Areia no Chão — executada, dano 0, MP −70 | 5066 / 3848 | 301 / 74 |
| 13 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Golpe Poderoso — executada, dano 388, MP −52 | 4678 / 3863 | 250 / 41 |
| 14 | p2 → p1 (score) | Golpe Duplo — executada, dano 0, MP −116 | Ataque básico — executada, dano 0 | 4678 / 3863 | 154 / 60 |
| 15 | p2 → p1 (score) | Mira Calma — executada, dano 986, MP −116 | Golpe Poderoso — executada, dano 0, MP −52 | 4678 / 2877 | 58 / 27 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 205 | Ataque básico — cancelada por controle | 4678 / 2672 | 78 / 46 |
| 17 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Ataque básico — cancelada por controle | 4678 / 2672 | 27 / 65 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Golpe Poderoso — executada, dano 288, MP −52 | 4390 / 2478 | 47 / 32 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Ataque básico — executada, dano 169 | 4221 / 2279 | 67 / 51 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 206 | 4015 / 2287 | 87 / 70 |
| 21 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Areia no Chão — executada, dano 0, MP −70 | 4015 / 2287 | 36 / 19 |
| 22 | p2 → p1 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 203 | 3812 / 2295 | 56 / 38 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 205 | Ataque básico — executada, dano 203 | 3609 / 2098 | 76 / 57 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 308 | Golpe Poderoso — executada, dano 0, MP −52 | 3609 / 1790 | 96 / 24 |
| 25 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Ataque básico — executada, dano 206 | 3403 / 1798 | 45 / 43 |
| 26 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 3403 / 1798 | 65 / 62 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 205 | Golpe Poderoso — executada, dano 360, MP −52 | 3043 / 1607 | 85 / 29 |
| 28 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Ataque básico — cancelada por controle | 3043 / 1607 | 34 / 48 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Ataque básico — cancelada por controle | 3043 / 1099 | 54 / 67 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Golpe Poderoso — executada, dano 288, MP −52 | 2755 / 602 | 74 / 34 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Ataque básico — executada, dano 206 | 2315 / 405 | 94 / 53 |
| 32 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Golpe Poderoso — executada, dano 360, MP −52 | 1721 / 419 | 43 / 20 |
| 33 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Ataque básico — executada, dano 169 | 1552 / 220 | 63 / 39 |
| 34 | p1 → p2 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 169 | 1383 / 226 | 83 / 58 |
| 35 | p1 → p2 (score) | Ataque básico — cancelada por controle | Golpe Poderoso — executada, dano 360, MP −52 | 1023 / 240 | 103 / 25 |
| 36 | p2 → p1 (score) | Provocação — executada, dano 0, MP −71 | Ataque básico — executada, dano 206 | 817 / 248 | 52 / 44 |
| 37 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Ataque básico — executada, dano 0 | 817 / 43 | 72 / 63 |
| 38 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 288, MP −52 | 529 / 54 | 92 / 30 |
| 39 | p1 → p2 (score) | Ataque básico — executada, dano 205 | Ataque básico — cancelada por morte | 529 / -151 | 112 / 30 |

#### Fase de 64 19 — calango × NOBRU

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W44 | calango | Guerreiro | 22 | 28.60 | Golpe Poderoso, Quebra-Guarda, Imortal, Tomar Fôlego | sustento |
| p2 | W40 | NOBRU | Guerreiro | 23 | 29.75 | Cutelada, Investida, Postura de Muro, Imortal | sustento |

- Seed da partida: `16730638574478466645`
- Rodadas: **64**
- Vencedor: **NOBRU** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 746/5469 (13.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | calango | NOBRU |
|---|---|---|
| Dano causado (golpes + DoT) | 8508 (8508 + 0) | 15240 (13528 + 1712) |
| Cura (skill + roubo de vida) | 9850 (5152 + 4698) | 3785 (0 + 3785) |
| MP gasto em ações | 1980 | 2483 |
| Skills / ataques básicos | 36 / 26 | 32 / 28 |
| Acertos / erros | 51 / 3 | 43 / 6 |
| Críticos (dano) | 5 (1403) | 2 (1172) |
| Agiu primeiro (rodadas) | 0 | 64 |
| Ações perdidas por controle | 1 | 4 |

Efeitos relevantes:
- calango aplicou: stun (rodada 3), stun (rodada 14), stun (rodada 20), stun (rodada 47)
- calango tentou sem sucesso: stun (rodada 1), stun (rodada 2), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 7), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 13), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), stun (rodada 21), stun (rodada 22), stun (rodada 25), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 37), stun (rodada 38), stun (rodada 39), stun (rodada 40), stun (rodada 42), stun (rodada 44), stun (rodada 45), stun (rodada 48), stun (rodada 49), stun (rodada 50), stun (rodada 52), stun (rodada 54), stun (rodada 55), stun (rodada 57), stun (rodada 58), stun (rodada 59), stun (rodada 60), stun (rodada 62), stun (rodada 63)
- NOBRU aplicou: bleed (rodada 6), bleed (rodada 26), bleed (rodada 51), bleed (rodada 53), stun (rodada 53)
- NOBRU tentou sem sucesso: bleed (rodada 3), bleed (rodada 7), stun (rodada 7), bleed (rodada 10), bleed (rodada 12), bleed (rodada 14), bleed (rodada 16), stun (rodada 16), bleed (rodada 18), bleed (rodada 19), stun (rodada 19), bleed (rodada 20), bleed (rodada 23), bleed (rodada 25), bleed (rodada 29), bleed (rodada 30), stun (rodada 30), bleed (rodada 32), stun (rodada 32), bleed (rodada 33), bleed (rodada 35), stun (rodada 35), bleed (rodada 36), bleed (rodada 37), stun (rodada 37), bleed (rodada 38), bleed (rodada 39), bleed (rodada 41), bleed (rodada 42), bleed (rodada 43), stun (rodada 43), bleed (rodada 44), bleed (rodada 45), stun (rodada 45), bleed (rodada 46), bleed (rodada 47), bleed (rodada 50), stun (rodada 51), bleed (rodada 52), bleed (rodada 54), bleed (rodada 55), bleed (rodada 56), stun (rodada 56), bleed (rodada 58), stun (rodada 58), bleed (rodada 59), bleed (rodada 60), bleed (rodada 61), stun (rodada 61), bleed (rodada 62), bleed (rodada 63), stun (rodada 63), bleed (rodada 64)
- NOBRU ativou: Postura de Muro ×9, Imortal ×2

Rodada a rodada:

| Rodada | Ordem (critério) | calango (p1) | NOBRU (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 5367 / 5280 | 782 / 948 |
| 2 | p2 → p1 (score) | Ataque básico — executada, dano 25 | Imortal — executada, dano 0, MP −228 | 5367 / 5255 | 801 / 744 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Cutelada — executada, dano 450, MP −85 | 5024 / 5192 | 773 / 683 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Investida — cancelada por controle | 5096 / 5065 | 792 / 707 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 5203 / 4876 | 764 / 655 |
| 6 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Cutelada — executada, dano 450, MP −85 | 4596 / 4901 | 783 / 594 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Investida — executada, dano 476, MP −59 | 4013 / 4845 | 755 / 559 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 32 | Imortal — executada, dano 0, MP −228 | 4031 / 4813 | 774 / 355 |
| 9 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 4138 / 4624 | 746 / 303 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Cutelada — executada, dano 450, MP −85 | 3745 / 4649 | 765 / 242 |
| 11 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Investida — executada, dano 0, MP −59 | 3852 / 4460 | 737 / 207 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 3699 / 4396 | 756 / 231 |
| 13 | p2 → p1 (score) | Golpe Poderoso — executada, dano 189, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 3806 / 4207 | 728 / 179 |
| 14 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Cutelada — executada, dano 450, MP −85 | 3413 / 4232 | 747 / 118 |
| 15 | p2 → p1 (score) | Golpe Poderoso — executada, dano 175, MP −47 | Investida — cancelada por controle | 3512 / 4057 | 719 / 142 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Investida — executada, dano 390, MP −59 | 3194 / 4039 | 738 / 107 |
| 17 | p2 → p1 (score) | Golpe Poderoso — executada, dano 175, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 3293 / 3864 | 710 / 55 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 153 | Ataque básico — executada, dano 225 | 3155 / 3774 | 729 / 79 |
| 19 | p2 → p1 (score) | Golpe Poderoso — executada, dano 175, MP −47 | Investida — executada, dano 390, MP −59 | 2864 / 3708 | 701 / 44 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 2711 / 3644 | 720 / 68 |
| 21 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Investida — cancelada por controle | 2835 / 3425 | 692 / 92 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Postura de Muro — executada, dano 0, MP −76 | 2892 / 3324 | 711 / 40 |
| 23 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 225 | 2667 / 3387 | 683 / 64 |
| 24 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Investida — executada, dano 0, MP −59 | 3311 / 3387 | 619 / 29 |
| 25 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 225 | 3210 / 3231 | 591 / 53 |
| 26 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 2843 / 3167 | 610 / 77 |
| 27 | p2 → p1 (score) | Golpe Poderoso — executada, dano 175, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 2728 / 2992 | 582 / 25 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Ataque básico — executada, dano 0 | 2785 / 2891 | 601 / 49 |
| 29 | p2 → p1 (score) | Golpe Poderoso — executada, dano 263, MP −47 | Ataque básico — executada, dano 225 | 2709 / 2691 | 573 / 73 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Investida — executada, dano 390, MP −59 | 2319 / 2800 | 592 / 38 |
| 31 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Ataque básico — executada, dano 0 | 2963 / 2800 | 528 / 62 |
| 32 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Investida — executada, dano 390, MP −59 | 2697 / 2690 | 500 / 27 |
| 33 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 2544 / 2626 | 519 / 51 |
| 34 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 0 | 2668 / 2407 | 491 / 75 |
| 35 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Investida — executada, dano 390, MP −59 | 2350 / 2389 | 510 / 40 |
| 36 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Ataque básico — executada, dano 225 | 2769 / 2452 | 446 / 64 |
| 37 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Investida — executada, dano 390, MP −59 | 2503 / 2342 | 418 / 29 |
| 38 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 2350 / 2278 | 437 / 53 |
| 39 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 225 | 2249 / 2122 | 409 / 77 |
| 40 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Postura de Muro — executada, dano 0, MP −76 | 2306 / 2021 | 428 / 25 |
| 41 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Ataque básico — executada, dano 225 | 2725 / 2084 | 364 / 49 |
| 42 | p2 → p1 (score) | Golpe Poderoso — executada, dano 175, MP −47 | Ataque básico — executada, dano 225 | 2599 / 1972 | 336 / 73 |
| 43 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Investida — executada, dano 390, MP −59 | 2209 / 2081 | 355 / 38 |
| 44 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 225 | 2108 / 1925 | 327 / 62 |
| 45 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Investida — executada, dano 390, MP −59 | 1790 / 1907 | 346 / 27 |
| 46 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Ataque básico — executada, dano 225 | 2209 / 1970 | 282 / 51 |
| 47 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 225 | 2108 / 1814 | 254 / 75 |
| 48 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Investida — cancelada por controle | 2180 / 1687 | 273 / 99 |
| 49 | p2 → p1 (score) | Golpe Poderoso — executada, dano 175, MP −47 | Postura de Muro — executada, dano 0, MP −76 | 2279 / 1512 | 245 / 47 |
| 50 | p2 → p1 (score) | Ataque básico — executada, dano 101 | Ataque básico — executada, dano 225 | 2111 / 1474 | 264 / 71 |
| 51 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Investida — executada, dano 390, MP −59 | 2151 / 1583 | 200 / 36 |
| 52 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 225 | 1836 / 1427 | 172 / 60 |
| 53 | p2 → p1 (score) | Ataque básico — cancelada por controle | Investida — executada, dano 390, MP −59 | 1232 / 1536 | 191 / 25 |
| 54 | p2 → p1 (score) | Golpe Poderoso — executada, dano 329, MP −47 | Ataque básico — executada, dano 225 | 980 / 1270 | 163 / 49 |
| 55 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 827 / 1206 | 182 / 73 |
| 56 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Investida — executada, dano 586, MP −59 | 885 / 1370 | 118 / 38 |
| 57 | p2 → p1 (score) | Golpe Poderoso — executada, dano 329, MP −47 | Ataque básico — executada, dano 0 | 1072 / 1041 | 90 / 62 |
| 58 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Investida — executada, dano 390, MP −59 | 754 / 1023 | 109 / 27 |
| 59 | p2 → p1 (score) | Golpe Poderoso — executada, dano 219, MP −47 | Ataque básico — executada, dano 225 | 653 / 867 | 81 / 51 |
| 60 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 500 / 803 | 100 / 75 |
| 61 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Investida — executada, dano 390, MP −59 | 754 / 912 | 36 / 40 |
| 62 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 225 | 601 / 848 | 55 / 64 |
| 63 | p2 → p1 (score) | Golpe Poderoso — executada, dano 329, MP −47 | Investida — executada, dano 586, MP −59 | 202 / 683 | 27 / 29 |
| 64 | p2 → p1 (score) | Ataque básico — cancelada por morte | Ataque básico — executada, dano 225 | -23 / 746 | 27 / 53 |

#### Fase de 64 20 — coldzin × Neskwga

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W41 | coldzin | Guerreiro | 24 | 29.64 | Pancada na Nuca, Postura de Muro, Cutelada, Tremor de Bigorna | sustento |
| p2 | W38 | Neskwga | Guerreiro | 22 | 29.41 | Golpe Poderoso, Mira Calma, Escudo Protetor, Baluarte | defesa + sustento |

- Seed da partida: `14112623888638305206`
- Rodadas: **42**
- Vencedor: **Neskwga** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 324/6216 (5.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | coldzin | Neskwga |
|---|---|---|
| Dano causado (golpes + DoT) | 6956 (6956 + 0) | 9186 (7976 + 1210) |
| Cura (skill + roubo de vida) | 823 (0 + 823) | 1064 (0 + 1064) |
| MP gasto em ações | 2037 | 1343 |
| Skills / ataques básicos | 24 / 17 | 23 / 19 |
| Acertos / erros | 22 / 1 | 31 / 8 |
| Críticos (dano) | 6 (2817) | 5 (1373) |
| Agiu primeiro (rodadas) | 36 | 6 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- coldzin aplicou: hexed (rodada 2), hexed (rodada 10), hexed (rodada 18), hexed (rodada 22), hexed (rodada 36)
- coldzin tentou sem sucesso: stun (rodada 3), stun (rodada 4), hexed (rodada 6), stun (rodada 7), stun (rodada 8), stun (rodada 11), stun (rodada 12), hexed (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 19), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 26), stun (rodada 28), stun (rodada 29), hexed (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 34), stun (rodada 37), stun (rodada 38), stun (rodada 40), stun (rodada 41), hexed (rodada 42)
- coldzin ativou: Postura de Muro ×9
- Neskwga aplicou: poison (rodada 2), vulnerable (rodada 3), poison (rodada 31), stun (rodada 34)
- Neskwga tentou sem sucesso: stun (rodada 2), bleed (rodada 2), fear (rodada 2), stun (rodada 3), bleed (rodada 3), poison (rodada 3), fear (rodada 3), stun (rodada 6), bleed (rodada 6), poison (rodada 6), fear (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), fear (rodada 7), vulnerable (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), fear (rodada 8), stun (rodada 10), bleed (rodada 10), poison (rodada 10), fear (rodada 10), stun (rodada 11), bleed (rodada 11), poison (rodada 11), fear (rodada 11), stun (rodada 12), bleed (rodada 12), poison (rodada 12), fear (rodada 12), stun (rodada 14), bleed (rodada 14), poison (rodada 14), fear (rodada 14), stun (rodada 15), bleed (rodada 15), poison (rodada 15), fear (rodada 15), stun (rodada 18), bleed (rodada 18), poison (rodada 18), fear (rodada 18), stun (rodada 19), bleed (rodada 19), poison (rodada 19), fear (rodada 19), stun (rodada 20), bleed (rodada 20), poison (rodada 20), fear (rodada 20), stun (rodada 21), bleed (rodada 21), poison (rodada 21), fear (rodada 21), stun (rodada 22), bleed (rodada 22), poison (rodada 22), fear (rodada 22), stun (rodada 23), bleed (rodada 23), poison (rodada 23), fear (rodada 23), stun (rodada 24), bleed (rodada 24), poison (rodada 24), fear (rodada 24), stun (rodada 26), bleed (rodada 26), poison (rodada 26), fear (rodada 26), stun (rodada 27), bleed (rodada 27), poison (rodada 27), fear (rodada 27), stun (rodada 28), bleed (rodada 28), poison (rodada 28), fear (rodada 28), stun (rodada 30), bleed (rodada 30), poison (rodada 30), fear (rodada 30), stun (rodada 31), bleed (rodada 31), fear (rodada 31), stun (rodada 32), bleed (rodada 32), poison (rodada 32), fear (rodada 32), bleed (rodada 34), poison (rodada 34), fear (rodada 34), stun (rodada 35), bleed (rodada 35), poison (rodada 35), fear (rodada 35), stun (rodada 36), bleed (rodada 36), poison (rodada 36), fear (rodada 36), stun (rodada 37), bleed (rodada 37), poison (rodada 37), fear (rodada 37), stun (rodada 39), bleed (rodada 39), poison (rodada 39), fear (rodada 39), stun (rodada 40), bleed (rodada 40), poison (rodada 40), fear (rodada 40), stun (rodada 41), bleed (rodada 41), poison (rodada 41), fear (rodada 41), stun (rodada 42), bleed (rodada 42), poison (rodada 42), fear (rodada 42)
- Neskwga ativou: Escudo Protetor ×3

Rodada a rodada:

| Rodada | Ordem (critério) | coldzin (p1) | Neskwga (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Escudo Protetor — executada, dano 0, MP −97 | 8119 / 6216 | 876 / 571 |
| 2 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 249, MP −47 | 7749 / 6216 | 825 / 541 |
| 3 | p1 → p2 (score) | Cutelada — executada, dano 426, MP −95 | Mira Calma — executada, dano 789, MP −103 | 6890 / 5900 | 757 / 455 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 0, MP −47 | 6792 / 5702 | 784 / 425 |
| 5 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Escudo Protetor — executada, dano 0, MP −97 | 6671 / 5702 | 726 / 345 |
| 6 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 249, MP −47 | 6301 / 5736 | 675 / 315 |
| 7 | p2 → p1 (score) | Cutelada — executada, dano 501, MP −95 | Mira Calma — executada, dano 696, MP −103 | 5665 / 5332 | 607 / 229 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 337 | Golpe Poderoso — executada, dano 232, MP −47 | 5473 / 5027 | 634 / 199 |
| 9 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Escudo Protetor — executada, dano 0, MP −97 | 5473 / 5027 | 576 / 119 |
| 10 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 232, MP −47 | 5241 / 5059 | 525 / 89 |
| 11 | p1 → p2 (score) | Cutelada — executada, dano 426, MP −95 | Ataque básico — executada, dano 134 | 5158 / 4651 | 457 / 106 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 148 | Golpe Poderoso — executada, dano 291, MP −47 | 4884 / 4543 | 484 / 76 |
| 13 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Ataque básico — executada, dano 0 | 4884 / 4543 | 426 / 93 |
| 14 | p1 → p2 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 232, MP −47 | 4652 / 4575 | 375 / 63 |
| 15 | p1 → p2 (score) | Cutelada — executada, dano 392, MP −95 | Ataque básico — executada, dano 139 | 4560 / 4202 | 307 / 80 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 0, MP −47 | 4583 / 4004 | 334 / 50 |
| 17 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Ataque básico — executada, dano 0 | 4583 / 4004 | 276 / 67 |
| 18 | p1 → p2 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 232, MP −47 | 4351 / 4036 | 225 / 37 |
| 19 | p1 → p2 (score) | Cutelada — executada, dano 569, MP −95 | Ataque básico — executada, dano 134 | 4285 / 3485 | 157 / 54 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 291, MP −47 | 3994 / 3525 | 184 / 24 |
| 21 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Ataque básico — executada, dano 139 | 3855 / 3544 | 126 / 41 |
| 22 | p1 → p2 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Ataque básico — executada, dano 203 | 3652 / 3572 | 75 / 58 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 232, MP −47 | 3443 / 3406 | 102 / 28 |
| 24 | p1 → p2 (score) | Cutelada — executada, dano 968, MP −95 | Ataque básico — executada, dano 263 | 3296 / 2474 | 34 / 45 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 337 | Ataque básico — executada, dano 0 | 3336 / 2137 | 61 / 62 |
| 26 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 291, MP −47 | 3068 / 1979 | 88 / 32 |
| 27 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Ataque básico — executada, dano 139 | 2929 / 1998 | 30 / 49 |
| 28 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 349, MP −47 | 2603 / 1848 | 57 / 19 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Ataque básico — executada, dano 0 | 2626 / 1650 | 84 / 36 |
| 30 | p1 → p2 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Ataque básico — executada, dano 175 | 2451 / 1674 | 33 / 53 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 291, MP −47 | 2183 / 1516 | 60 / 23 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Ataque básico — executada, dano 175 | 1910 / 1342 | 87 / 40 |
| 33 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Ataque básico — executada, dano 0 | 1789 / 1342 | 29 / 57 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 349, MP −47 | 1342 / 1192 | 56 / 27 |
| 35 | p1 → p2 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 209 | 1012 / 1221 | 83 / 44 |
| 36 | p1 → p2 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Ataque básico — executada, dano 169 | 722 / 1244 | 32 / 61 |
| 37 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Golpe Poderoso — executada, dano 291, MP −47 | 454 / 1086 | 59 / 31 |
| 38 | p1 → p2 (score) | Ataque básico — executada, dano 337 | Ataque básico — executada, dano 0 | 494 / 749 | 86 / 48 |
| 39 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −85 | Golpe Poderoso — executada, dano 232, MP −47 | 262 / 781 | 28 / 18 |
| 40 | p1 → p2 (score) | Ataque básico — executada, dano 337 | Ataque básico — executada, dano 139 | 163 / 463 | 55 / 35 |
| 41 | p1 → p2 (score) | Ataque básico — executada, dano 198 | Ataque básico — executada, dano 139 | 47 / 284 | 82 / 52 |
| 42 | p1 → p2 (score) | Pancada na Nuca — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 291, MP −47 | -244 / 324 | 31 / 22 |

#### Fase de 64 21 — PlayHard × xandfps

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W18 | PlayHard | Guerreiro | 21 | 28.02 | Resistência Heróica, Mira Calma, Quebra-Guarda, Gancho e Corda | sem canal dominante |
| p2 | W20 | xandfps | Guerreiro | 21 | 28.48 | Mão Dupla, Mira Calma, Escudo Protetor, Peso do Machado | sustento |

- Seed da partida: `5218381777248435903`
- Rodadas: **14**
- Vencedor: **xandfps** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 212/4259 (5.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | PlayHard | xandfps |
|---|---|---|
| Dano causado (golpes + DoT) | 5727 (5727 + 0) | 5244 (4206 + 1038) |
| Cura (skill + roubo de vida) | 522 (0 + 522) | 1680 (0 + 1680) |
| MP gasto em ações | 871 | 1044 |
| Skills / ataques básicos | 11 / 3 | 13 / 0 |
| Acertos / erros | 9 / 2 | 8 / 1 |
| Críticos (dano) | 5 (4385) | 0 (0) |
| Agiu primeiro (rodadas) | 13 | 1 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- PlayHard aplicou: vulnerable (rodada 3), vulnerable (rodada 5), vulnerable (rodada 10), stun (rodada 11)
- PlayHard tentou sem sucesso: stun (rodada 1), stun (rodada 2), vulnerable (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 7), vulnerable (rodada 7), stun (rodada 9), stun (rodada 10), vulnerable (rodada 11), stun (rodada 12), vulnerable (rodada 12), stun (rodada 13), vulnerable (rodada 13)
- xandfps aplicou: bleed (rodada 2), vulnerable (rodada 3), bleed (rodada 6), vulnerable (rodada 7), vulnerable (rodada 8)
- xandfps tentou sem sucesso: stun (rodada 2), bleed (rodada 2), poison (rodada 2), stun (rodada 3), bleed (rodada 3), poison (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), vulnerable (rodada 4), stun (rodada 6), bleed (rodada 6), poison (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), stun (rodada 12), bleed (rodada 12), poison (rodada 12), vulnerable (rodada 12), stun (rodada 14), bleed (rodada 14), poison (rodada 14), bleed (rodada 14)
- xandfps ativou: Escudo Protetor ×4

Rodada a rodada:

| Rodada | Ordem (critério) | PlayHard (p1) | xandfps (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Gancho e Corda — executada, dano 0, MP −93 | Escudo Protetor — executada, dano 0, MP −87 | 4339 / 4259 | 853 / 769 |
| 2 | p1 → p2 (score) | Mira Calma — executada, dano 954, MP −92 | Mão Dupla — executada, dano 423, MP −76 | 3916 / 3474 | 791 / 726 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 378, MP −56 | Mira Calma — executada, dano 707, MP −92 | 3077 / 3378 | 765 / 667 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 174 | Peso do Machado — executada, dano 518, MP −58 | 2405 / 3411 | 795 / 642 |
| 5 | p1 → p2 (score) | Mira Calma — executada, dano 1485, MP −92 | Escudo Protetor — executada, dano 0, MP −87 | 2395 / 1926 | 733 / 588 |
| 6 | p1 → p2 (score) | Gancho e Corda — executada, dano 0, MP −93 | Mão Dupla — executada, dano 423, MP −76 | 1972 / 2095 | 670 / 545 |
| 7 | p1 → p2 (score) | Quebra-Guarda — executada, dano 567, MP −56 | Mira Calma — executada, dano 680, MP −92 | 1181 / 1800 | 644 / 486 |
| 8 | p1 → p2 (score) | Mira Calma — executada, dano 0, MP −92 | Peso do Machado — executada, dano 518, MP −58 | 490 / 2007 | 582 / 461 |
| 9 | p1 → p2 (score) | Ataque básico — executada, dano 201 | Escudo Protetor — executada, dano 0, MP −87 | 339 / 1806 | 612 / 407 |
| 10 | p2 → p1 (score) | Quebra-Guarda — executada, dano 540, MP −56 | Mão Dupla — executada, dano 0, MP −76 | 398 / 1266 | 586 / 364 |
| 11 | p1 → p2 (score) | Gancho e Corda — executada, dano 0, MP −93 | Mira Calma — cancelada por controle | 398 / 1266 | 523 / 397 |
| 12 | p1 → p2 (score) | Mira Calma — executada, dano 589, MP −92 | Mira Calma — executada, dano 413, MP −92 | 49 / 842 | 461 / 338 |
| 13 | p1 → p2 (score) | Quebra-Guarda — executada, dano 839, MP −56 | Escudo Protetor — executada, dano 0, MP −87 | 141 / 3 | 435 / 284 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Mão Dupla — executada, dano 524, MP −76 | -383 / 212 | 465 / 241 |

#### Fase de 64 22 — Gaules × tteuw

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W36 | Gaules | Guerreiro | 22 | 29.98 | Mão Dupla, Peso do Machado, Estocada Seca, Fúria | crítico + controle |
| p2 | W19 | tteuw | Guerreiro | 19 | 29.17 | Golpe Poderoso, Mira Calma, Tomar Fôlego, Escudo Protetor | defesa + sustento |

- Seed da partida: `7026902445234392979`
- Rodadas: **21**
- Vencedor: **Gaules** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1317/5209 (25.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Gaules | tteuw |
|---|---|---|
| Dano causado (golpes + DoT) | 7711 (3336 + 4375) | 4019 (3603 + 416) |
| Cura (skill + roubo de vida) | 127 (0 + 127) | 2794 (2004 + 790) |
| MP gasto em ações | 1016 | 976 |
| Skills / ataques básicos | 10 / 11 | 18 / 0 |
| Acertos / erros | 14 / 0 | 8 / 3 |
| Críticos (dano) | 7 (1828) | 0 (0) |
| Agiu primeiro (rodadas) | 16 | 5 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- Gaules aplicou: bleed (rodada 2), bleed (rodada 3), bleed (rodada 6), bleed (rodada 7), stun (rodada 12), stun (rodada 13), bleed (rodada 16), poison (rodada 17), poison (rodada 19), bleed (rodada 19)
- Gaules tentou sem sucesso: stun (rodada 3), bleed (rodada 3), poison (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), stun (rodada 7), poison (rodada 7), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), stun (rodada 10), bleed (rodada 10), poison (rodada 10), bleed (rodada 11), bleed (rodada 12), poison (rodada 12), bleed (rodada 13), poison (rodada 13), stun (rodada 14), bleed (rodada 14), poison (rodada 14), bleed (rodada 15), stun (rodada 16), poison (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 18), bleed (rodada 18), poison (rodada 18), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), poison (rodada 20), stun (rodada 21), bleed (rodada 21), poison (rodada 21)
- Gaules ativou: Fúria ×3
- tteuw aplicou: bleed (rodada 7), vulnerable (rodada 7), vulnerable (rodada 17)
- tteuw tentou sem sucesso: bleed (rodada 4), bleed (rodada 6), bleed (rodada 10), bleed (rodada 16), bleed (rodada 17), bleed (rodada 18), bleed (rodada 20)
- tteuw ativou: Escudo Protetor ×4
- Leis disparadas por tteuw: FERIDA SÉPTICA (rodada 17), FERIDA SÉPTICA (rodada 19)

Rodada a rodada:

| Rodada | Ordem (critério) | Gaules (p1) | tteuw (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Fúria — executada, dano 0, MP −171 | Escudo Protetor — executada, dano 0, MP −69 | 5209 / 4842 | 524 / 452 |
| 2 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 0, MP −33 | 5209 / 4649 | 482 / 445 |
| 3 | p1 → p2 (score) | Mão Dupla — executada, dano 481, MP −85 | Mira Calma — executada, dano 0, MP −73 | 5209 / 3781 | 417 / 398 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 194 | Golpe Poderoso — executada, dano 306, MP −33 | 4903 / 3267 | 437 / 391 |
| 5 | p1 → p2 (score) | Fúria — executada, dano 0, MP −171 | Escudo Protetor — executada, dano 0, MP −69 | 4903 / 2880 | 286 / 348 |
| 6 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 306, MP −33 | 4597 / 2754 | 244 / 341 |
| 7 | p1 → p2 (score) | Mão Dupla — executada, dano 320, MP −85 | Mira Calma — executada, dano 964, MP −73 | 3649 / 2259 | 179 / 294 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 255 | Tomar Fôlego — executada, dano 0, MP −59 | 3453 / 2285 | 199 / 261 |
| 9 | p2 → p1 (score) | Fúria — executada, dano 0, MP −171 | Escudo Protetor — executada, dano 0, MP −69 | 3245 / 2285 | 48 / 218 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 194 | Golpe Poderoso — executada, dano 284, MP −33 | 2970 / 2153 | 68 / 211 |
| 11 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Mira Calma — executada, dano 0, MP −73 | 2970 / 2153 | 26 / 164 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 129 | Golpe Poderoso — cancelada por controle | 2976 / 2024 | 46 / 190 |
| 13 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Tomar Fôlego — cancelada por controle | 2984 / 1854 | 66 / 216 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 170 | Tomar Fôlego — executada, dano 0, MP −59 | 2992 / 2352 | 86 / 183 |
| 15 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Escudo Protetor — executada, dano 0, MP −69 | 2992 / 2352 | 44 / 140 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 194 | Golpe Poderoso — executada, dano 284, MP −33 | 2717 / 2220 | 64 / 133 |
| 17 | p2 → p1 (score) | Ataque básico — executada, dano 129 | Mira Calma — executada, dano 837, MP −73 | 1886 / 2082 | 84 / 86 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 170 | Golpe Poderoso — executada, dano 338, MP −33 | 1556 / 1721 | 104 / 79 |
| 19 | p1 → p2 (score) | Mão Dupla — executada, dano 420, MP −85 | Tomar Fôlego — executada, dano 0, MP −59 | 1577 / 1437 | 39 / 46 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 255 | Golpe Poderoso — executada, dano 284, MP −33 | 1305 / 712 | 59 / 39 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 255 | Ataque básico — cancelada por morte | 1317 / -75 | 79 / 65 |

#### Fase de 64 23 — casimito × YoDa

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W55 | casimito | Guerreiro | 23 | 29.75 | Peso do Machado, Esmagar, Provocação, Disciplina de Forja | crítico + controle |
| p2 | W33 | YoDa | Guerreiro | 21 | 29.41 | Mão Dupla, Tremor de Bigorna, Estocada Seca, Lâmina Assentada | controle |

- Seed da partida: `2845307736597708112`
- Rodadas: **12**
- Vencedor: **YoDa** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2399/5464 (43.9%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | casimito | YoDa |
|---|---|---|
| Dano causado (golpes + DoT) | 3144 (3144 + 0) | 7350 (1664 + 5686) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 79 (0 + 79) |
| MP gasto em ações | 850 | 536 |
| Skills / ataques básicos | 8 / 4 | 7 / 4 |
| Acertos / erros | 6 / 0 | 7 / 0 |
| Críticos (dano) | 2 (1845) | 3 (926) |
| Agiu primeiro (rodadas) | 12 | 0 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- casimito aplicou: weakened (rodada 2), fear (rodada 3), weakened (rodada 5), weakened (rodada 8), stun (rodada 9)
- casimito tentou sem sucesso: stun (rodada 3), fear (rodada 4), fear (rodada 7), fear (rodada 9), fear (rodada 10), fear (rodada 12)
- casimito ativou: Disciplina de Forja ×3
- Leis disparadas por casimito: PÂNICO (rodada 5)
- YoDa aplicou: bleed (rodada 2), bleed (rodada 3), bleed (rodada 3), bleed (rodada 5), fear (rodada 5), bleed (rodada 7), bleed (rodada 10), fear (rodada 12)
- YoDa tentou sem sucesso: fear (rodada 3), bleed (rodada 4), fear (rodada 4), bleed (rodada 7), fear (rodada 7), bleed (rodada 8), fear (rodada 8), fear (rodada 10), bleed (rodada 12), bleed (rodada 12)
- YoDa ativou: Lâmina Assentada ×3

Rodada a rodada:

| Rodada | Ordem (critério) | casimito (p1) | YoDa (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Disciplina de Forja — executada, dano 0, MP −105 | Lâmina Assentada — executada, dano 0, MP −84 | 7113 / 5464 | 621 / 519 |
| 2 | p1 → p2 (score) | Provocação — executada, dano 0, MP −71 | Estocada Seca — executada, dano 0, MP −56 | 7113 / 5464 | 569 / 475 |
| 3 | p1 → p2 (score) | Esmagar — executada, dano 606, MP −161 | Mão Dupla — executada, dano 195, MP −76 | 6634 / 4867 | 427 / 411 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 231 | Ataque básico — executada, dano 166 | 5615 / 4644 | 446 / 423 |
| 5 | p1 → p2 (score) | Provocação — executada, dano 0, MP −71 | Ataque básico — executada, dano 111 | 4651 / 4649 | 394 / 435 |
| 6 | p1 → p2 (score) | Disciplina de Forja — executada, dano 0, MP −105 | Lâmina Assentada — executada, dano 0, MP −84 | 3513 / 4649 | 308 / 363 |
| 7 | p1 → p2 (score) | Ataque básico — executada, dano 231 | Mão Dupla — executada, dano 594, MP −76 | 1781 / 4447 | 327 / 299 |
| 8 | p1 → p2 (score) | Provocação — executada, dano 0, MP −71 | Ataque básico — executada, dano 166 | 1331 / 4455 | 275 / 311 |
| 9 | p1 → p2 (score) | Esmagar — executada, dano 1334, MP −161 | Ataque básico — cancelada por controle | 1047 / 3121 | 133 / 323 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 231 | Ataque básico — executada, dano 135 | 628 / 2896 | 152 / 335 |
| 11 | p1 → p2 (score) | Disciplina de Forja — executada, dano 0, MP −105 | Lâmina Assentada — executada, dano 0, MP −84 | 344 / 2896 | 66 / 263 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 511 | Mão Dupla — executada, dano 297, MP −76 | -237 / 2399 | 85 / 199 |

#### Fase de 64 24 — Forever × XANDAOOGOD

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W11 | Forever | Guerreiro | 22 | 28.71 | Grito Curto, Peso do Machado, Couro Batido, Última Carta | crítico + defesa + controle |
| p2 | W47 | XANDAOOGOD | Guerreiro | 23 | 29.64 | Esmagar, Mira Calma, Leitura de Terreno, Veterania | defesa |

- Seed da partida: `10313238421112521520`
- Rodadas: **14**
- Vencedor: **XANDAOOGOD** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3615/5684 (63.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Forever | XANDAOOGOD |
|---|---|---|
| Dano causado (golpes + DoT) | 2069 (1615 + 454) | 5501 (4247 + 1254) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 0 (0 + 0) |
| MP gasto em ações | 645 | 1164 |
| Skills / ataques básicos | 9 / 2 | 9 / 5 |
| Acertos / erros | 4 / 0 | 10 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 14 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- Forever aplicou: fear (rodada 2), bleed (rodada 3), fear (rodada 10)
- Forever tentou sem sucesso: weakened (rodada 2), stun (rodada 3), fear (rodada 3), fear (rodada 3), stun (rodada 4), bleed (rodada 4), fear (rodada 4), fear (rodada 6), stun (rodada 8), bleed (rodada 8), fear (rodada 8), weakened (rodada 10), stun (rodada 11), bleed (rodada 11), fear (rodada 11), fear (rodada 11)
- Forever ativou: Couro Batido ×4
- Leis disparadas por Forever: FERIDA ABERTA (rodada 14)
- XANDAOOGOD aplicou: bleed (rodada 2), vulnerable (rodada 3), stun (rodada 7), bleed (rodada 10), stun (rodada 12), vulnerable (rodada 13), bleed (rodada 14)
- XANDAOOGOD tentou sem sucesso: poison (rodada 2), stun (rodada 2), bleed (rodada 3), poison (rodada 3), bleed (rodada 5), poison (rodada 5), bleed (rodada 7), poison (rodada 7), bleed (rodada 8), poison (rodada 8), vulnerable (rodada 8), bleed (rodada 9), poison (rodada 9), poison (rodada 10), bleed (rodada 12), poison (rodada 12), bleed (rodada 13), poison (rodada 13), poison (rodada 14)
- XANDAOOGOD ativou: Veterania ×3

Rodada a rodada:

| Rodada | Ordem (critério) | Forever (p1) | XANDAOOGOD (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −62 | Veterania — executada, dano 0, MP −111 | 5225 / 5684 | 780 / 926 |
| 2 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −57 | Esmagar — executada, dano 401, MP −161 | 4615 / 5684 | 743 / 789 |
| 3 | p2 → p1 (score) | Última Carta — executada, dano 512, MP −113 | Mira Calma — executada, dano 576, MP −116 | 3830 / 5172 | 650 / 697 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 200 | Ataque básico — executada, dano 0 | 3830 / 4745 | 670 / 721 |
| 5 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −62 | Ataque básico — executada, dano 203 | 3627 / 4518 | 628 / 745 |
| 6 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −57 | Veterania — executada, dano 0, MP −111 | 3627 / 4518 | 591 / 658 |
| 7 | p2 → p1 (score) | Ataque básico — cancelada por controle | Esmagar — executada, dano 401, MP −161 | 3226 / 4518 | 611 / 521 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 200 | Mira Calma — executada, dano 627, MP −116 | 2599 / 4318 | 631 / 429 |
| 9 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −62 | Ataque básico — executada, dano 203 | 2396 / 4318 | 589 / 453 |
| 10 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −57 | Ataque básico — executada, dano 162 | 2025 / 4318 | 552 / 477 |
| 11 | p2 → p1 (score) | Última Carta — executada, dano 703, MP −113 | Veterania — executada, dano 0, MP −111 | 1816 / 3615 | 459 / 390 |
| 12 | p2 → p1 (score) | Ataque básico — cancelada por controle | Esmagar — executada, dano 853, MP −161 | 963 / 3615 | 479 / 253 |
| 13 | p2 → p1 (score) | Couro Batido — executada, dano 0, MP −62 | Mira Calma — executada, dano 627, MP −116 | 336 / 3615 | 437 / 161 |
| 14 | p2 → p1 (score) | Grito Curto — cancelada por morte | Ataque básico — executada, dano 194 | -276 / 3615 | 457 / 185 |

#### Fase de 64 25 — Patriota × jovirone

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W10 | Patriota | Guerreiro | 22 | 29.87 | Pisada de Ferro, Investida de Aríete, Pancada na Nuca, Pausa Útil | controle |
| p2 | W22 | jovirone | Guerreiro | 24 | 29.52 | Marca do Açougueiro, Quebra-Guarda, Disciplina de Forja, Sangue nos Olhos | sustento |

- Seed da partida: `5100617546764134280`
- Rodadas: **30**
- Vencedor: **jovirone** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3029/6345 (47.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Patriota | jovirone |
|---|---|---|
| Dano causado (golpes + DoT) | 4761 (2766 + 1995) | 5431 (3903 + 1528) |
| Cura (skill + roubo de vida) | 628 (0 + 628) | 1445 (0 + 1445) |
| MP gasto em ações | 1020 | 1650 |
| Skills / ataques básicos | 18 / 10 | 18 / 6 |
| Acertos / erros | 15 / 1 | 9 / 3 |
| Críticos (dano) | 1 (436) | 0 (0) |
| Agiu primeiro (rodadas) | 2 | 28 |
| Ações perdidas por controle | 1 | 6 |

Efeitos relevantes:
- Patriota aplicou: stun (rodada 3), poison (rodada 3), slowed (rodada 3), stun (rodada 4), poison (rodada 4), hexed (rodada 7), stun (rodada 8), fear (rodada 8), slowed (rodada 8), stun (rodada 10), poison (rodada 10), hexed (rodada 12), slowed (rodada 13), fear (rodada 15), poison (rodada 19), stun (rodada 20), hexed (rodada 22), stun (rodada 24), hexed (rodada 28)
- Patriota tentou sem sucesso: hexed (rodada 2), fear (rodada 3), fear (rodada 4), stun (rodada 5), poison (rodada 5), fear (rodada 5), poison (rodada 8), stun (rodada 9), poison (rodada 9), fear (rodada 9), fear (rodada 10), stun (rodada 13), poison (rodada 13), fear (rodada 13), stun (rodada 14), poison (rodada 14), fear (rodada 14), stun (rodada 15), poison (rodada 15), hexed (rodada 17), stun (rodada 18), poison (rodada 18), fear (rodada 18), slowed (rodada 18), stun (rodada 19), fear (rodada 19), poison (rodada 20), fear (rodada 20), poison (rodada 24), fear (rodada 24), stun (rodada 25), poison (rodada 25), fear (rodada 25), stun (rodada 29), poison (rodada 29), fear (rodada 29), slowed (rodada 29)
- Patriota ativou: Pausa Útil ×6
- Leis disparadas por Patriota: FERIDA ABERTA (rodada 7), FERIDA ABERTA (rodada 28)
- jovirone aplicou: vulnerable (rodada 2), vulnerable (rodada 3), vulnerable (rodada 7), bleed (rodada 7), vulnerable (rodada 8), vulnerable (rodada 13), vulnerable (rodada 14), vulnerable (rodada 18), vulnerable (rodada 23), vulnerable (rodada 24), stun (rodada 26), vulnerable (rodada 28), bleed (rodada 28)
- jovirone tentou sem sucesso: bleed (rodada 2), stun (rodada 3), stun (rodada 8), bleed (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 16), bleed (rodada 18), stun (rodada 19), vulnerable (rodada 19), bleed (rodada 23), stun (rodada 24), stun (rodada 30)
- jovirone ativou: Disciplina de Forja ×6

Rodada a rodada:

| Rodada | Ordem (critério) | Patriota (p1) | jovirone (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −47 | Disciplina de Forja — executada, dano 0, MP −118 | 4779 / 6345 | 808 / 1073 |
| 2 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −62 | Sangue nos Olhos — executada, dano 0, MP −78 | 4779 / 6345 | 777 / 1026 |
| 3 | p2 → p1 (score) | Pisada de Ferro — executada, dano 234, MP −61 | Quebra-Guarda — executada, dano 610, MP −79 | 4222 / 6111 | 747 / 978 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Ataque básico — cancelada por controle | 4249 / 5896 | 778 / 1009 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 161 | Ataque básico — cancelada por controle | 4286 / 5545 | 809 / 1040 |
| 6 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −47 | Disciplina de Forja — executada, dano 0, MP −118 | 4286 / 5355 | 779 / 953 |
| 7 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −62 | Sangue nos Olhos — executada, dano 0, MP −78 | 3904 / 5165 | 748 / 906 |
| 8 | p2 → p1 (score) | Pisada de Ferro — executada, dano 290, MP −61 | Quebra-Guarda — executada, dano 610, MP −79 | 2978 / 4953 | 718 / 858 |
| 9 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Ataque básico — cancelada por controle | 3005 / 4643 | 749 / 889 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 161 | Ataque básico — executada, dano 0 | 3042 / 4482 | 780 / 920 |
| 11 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −47 | Disciplina de Forja — cancelada por controle | 3042 / 4387 | 750 / 951 |
| 12 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −62 | Disciplina de Forja — executada, dano 0, MP −118 | 3042 / 4292 | 719 / 864 |
| 13 | p2 → p1 (score) | Pisada de Ferro — executada, dano 290, MP −61 | Sangue nos Olhos — executada, dano 0, MP −78 | 3108 / 3907 | 689 / 817 |
| 14 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Quebra-Guarda — executada, dano 544, MP −79 | 2591 / 3931 | 720 / 769 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Ataque básico — executada, dano 311 | 2307 / 3852 | 751 / 800 |
| 16 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −47 | Ataque básico — executada, dano 249 | 2058 / 3961 | 721 / 831 |
| 17 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −62 | Disciplina de Forja — executada, dano 0, MP −118 | 2058 / 3961 | 690 / 744 |
| 18 | p2 → p1 (score) | Pisada de Ferro — executada, dano 234, MP −61 | Sangue nos Olhos — executada, dano 0, MP −78 | 2111 / 3727 | 660 / 697 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Quebra-Guarda — executada, dano 544, MP −79 | 1594 / 3846 | 691 / 649 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Ataque básico — executada, dano 0 | 1621 / 3631 | 722 / 680 |
| 21 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −47 | Ataque básico — cancelada por controle | 1621 / 3536 | 692 / 711 |
| 22 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −62 | Disciplina de Forja — executada, dano 0, MP −118 | 1621 / 3441 | 661 / 624 |
| 23 | p2 → p1 (score) | Pisada de Ferro — executada, dano 0, MP −61 | Sangue nos Olhos — executada, dano 0, MP −78 | 1621 / 3346 | 631 / 577 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Quebra-Guarda — executada, dano 544, MP −79 | 1104 / 3370 | 662 / 529 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Ataque básico — cancelada por controle | 1131 / 3250 | 693 / 560 |
| 26 | p2 → p1 (score) | Pausa Útil — cancelada por controle | Ataque básico — executada, dano 249 | 882 / 3359 | 710 / 591 |
| 27 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −47 | Disciplina de Forja — executada, dano 0, MP −118 | 882 / 3359 | 680 / 504 |
| 28 | p2 → p1 (score) | Pancada na Nuca — executada, dano 0, MP −62 | Sangue nos Olhos — executada, dano 0, MP −78 | 500 / 3359 | 649 / 457 |
| 29 | p2 → p1 (score) | Pisada de Ferro — executada, dano 436, MP −61 | Quebra-Guarda — executada, dano 0, MP −79 | 218 / 2923 | 619 / 409 |
| 30 | p2 → p1 (score) | Ataque básico — cancelada por morte | Ataque básico — executada, dano 242 | -24 / 3029 | 619 / 440 |

#### Fase de 64 26 — yeTz × dona

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W39 | yeTz | Guerreiro | 23 | 29.87 | Paciência do Coveiro, Quebra-Guarda, Postura de Muro, Cutelada | sustento |
| p2 | W01 | dona | Guerreiro | 23 | 29.06 | Cutelada, Investida, Respirar Fundo, Grito de Guerra | sustento |

- Seed da partida: `6093964812114948536`
- Rodadas: **59**
- Vencedor: **yeTz** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1856/7383 (25.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | yeTz | dona |
|---|---|---|
| Dano causado (golpes + DoT) | 8410 (7372 + 1038) | 7866 (7866 + 0) |
| Cura (skill + roubo de vida) | 2339 (0 + 2339) | 795 (757 + 38) |
| MP gasto em ações | 2518 | 1858 |
| Skills / ataques básicos | 32 / 24 | 27 / 31 |
| Acertos / erros | 31 / 10 | 33 / 20 |
| Críticos (dano) | 0 (0) | 4 (1609) |
| Agiu primeiro (rodadas) | 39 | 20 |
| Ações perdidas por controle | 3 | 0 |

Efeitos relevantes:
- yeTz aplicou: poison (rodada 2), frailty (rodada 2), vulnerable (rodada 6), poison (rodada 8), vulnerable (rodada 10), vulnerable (rodada 22), vulnerable (rodada 40), vulnerable (rodada 49)
- yeTz tentou sem sucesso: vulnerable (rodada 3), frailty (rodada 8), vulnerable (rodada 30), vulnerable (rodada 54), vulnerable (rodada 59)
- yeTz ativou: Postura de Muro ×13
- dona aplicou: stun (rodada 14), stun (rodada 20), stun (rodada 46)
- dona tentou sem sucesso: stun (rodada 2), stun (rodada 3), stun (rodada 3), stun (rodada 4), stun (rodada 7), stun (rodada 7), stun (rodada 10), stun (rodada 11), stun (rodada 11), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 17), stun (rodada 20), stun (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 27), stun (rodada 29), stun (rodada 29), stun (rodada 30), stun (rodada 35), stun (rodada 36), stun (rodada 37), stun (rodada 37), stun (rodada 39), stun (rodada 41), stun (rodada 42), stun (rodada 45), stun (rodada 46), stun (rodada 48), stun (rodada 51), stun (rodada 53), stun (rodada 54), stun (rodada 55), stun (rodada 55), stun (rodada 58), stun (rodada 58)
- dona ativou: Grito de Guerra ×4

Rodada a rodada:

| Rodada | Ordem (critério) | yeTz (p1) | dona (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Grito de Guerra — executada, dano 0, MP −100 | 7383 / 7574 | 700 / 646 |
| 2 | p2 → p1 (score) | Paciência do Coveiro — executada, dano 0, MP −140 | Cutelada — executada, dano 371, MP −85 | 7012 / 7574 | 591 / 581 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 379, MP −70 | Investida — executada, dano 589, MP −59 | 6544 / 6059 | 552 / 542 |
| 4 | p1 → p2 (score) | Cutelada — executada, dano 442, MP −85 | Ataque básico — executada, dano 172 | 6513 / 5554 | 498 / 562 |
| 5 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −76 | Grito de Guerra — executada, dano 0, MP −100 | 6513 / 5464 | 453 / 482 |
| 6 | p1 → p2 (score) | Quebra-Guarda — executada, dano 379, MP −70 | Cutelada — executada, dano 0, MP −85 | 6634 / 4995 | 414 / 417 |
| 7 | p1 → p2 (score) | Cutelada — executada, dano 532, MP −85 | Investida — executada, dano 392, MP −59 | 6412 / 4412 | 360 / 378 |
| 8 | p1 → p2 (score) | Paciência do Coveiro — executada, dano 0, MP −140 | Ataque básico — executada, dano 0 | 6412 / 4299 | 251 / 398 |
| 9 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Grito de Guerra — executada, dano 0, MP −100 | 6412 / 4186 | 206 / 318 |
| 10 | p2 → p1 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Cutelada — executada, dano 556, MP −85 | 5964 / 3821 | 167 / 253 |
| 11 | p1 → p2 (score) | Cutelada — executada, dano 0, MP −85 | Investida — executada, dano 392, MP −59 | 5572 / 3770 | 113 / 214 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 187 | Respirar Fundo — executada, dano 0, MP −82 | 5631 / 4227 | 144 / 152 |
| 13 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −76 | Grito de Guerra — executada, dano 0, MP −100 | 5631 / 4227 | 99 / 72 |
| 14 | p2 → p1 (score) | Quebra-Guarda — cancelada por controle | Investida — executada, dano 321, MP −59 | 5310 / 4278 | 130 / 33 |
| 15 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −70 | Ataque básico — executada, dano 179 | 5131 / 4306 | 91 / 53 |
| 16 | p2 → p1 (score) | Cutelada — executada, dano 0, MP −85 | Ataque básico — executada, dano 137 | 4994 / 4327 | 37 / 73 |
| 17 | p2 → p1 (score) | Ataque básico — executada, dano 155 | Investida — executada, dano 306, MP −59 | 4737 / 4220 | 68 / 34 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 0 | 4786 / 4065 | 99 / 54 |
| 19 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 4786 / 4065 | 54 / 74 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Investida — executada, dano 244, MP −59 | 4542 / 4104 | 85 / 35 |
| 21 | p1 → p2 (score) | Quebra-Guarda — cancelada por controle | Ataque básico — executada, dano 137 | 4405 / 4125 | 116 / 55 |
| 22 | p1 → p2 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Ataque básico — executada, dano 172 | 4341 / 3812 | 77 / 75 |
| 23 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −76 | Investida — executada, dano 244, MP −59 | 4097 / 3851 | 32 / 36 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 187 | Ataque básico — executada, dano 137 | 4019 / 3685 | 63 / 56 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 137 | 3882 / 3706 | 94 / 76 |
| 26 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −70 | Investida — executada, dano 0, MP −59 | 3882 / 3706 | 55 / 37 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 172 | 3759 / 3578 | 86 / 57 |
| 28 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 3759 / 3578 | 41 / 77 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Investida — executada, dano 244, MP −59 | 3564 / 3462 | 72 / 38 |
| 30 | p1 → p2 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Ataque básico — executada, dano 137 | 3535 / 3143 | 33 / 58 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 0 | 3584 / 2988 | 64 / 78 |
| 32 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Investida — executada, dano 0, MP −59 | 3584 / 2988 | 95 / 39 |
| 33 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 3584 / 2988 | 50 / 59 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Investida — executada, dano 0, MP −59 | 3584 / 2988 | 81 / 20 |
| 35 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −70 | Ataque básico — executada, dano 137 | 3447 / 3009 | 42 / 40 |
| 36 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 172 | 3324 / 2881 | 73 / 60 |
| 37 | p2 → p1 (score) | Ataque básico — executada, dano 155 | Investida — executada, dano 306, MP −59 | 3067 / 2774 | 104 / 21 |
| 38 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 3067 / 2774 | 59 / 41 |
| 39 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 206 | 2910 / 2651 | 90 / 61 |
| 40 | p1 → p2 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Investida — executada, dano 0, MP −59 | 3018 / 2311 | 51 / 22 |
| 41 | p1 → p2 (score) | Ataque básico — executada, dano 187 | Ataque básico — executada, dano 258 | 2819 / 2165 | 82 / 42 |
| 42 | p1 → p2 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 137 | 2682 / 2186 | 37 / 62 |
| 43 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Investida — executada, dano 0, MP −59 | 2731 / 2031 | 68 / 23 |
| 44 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 0 | 2780 / 1876 | 99 / 43 |
| 45 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −70 | Ataque básico — executada, dano 172 | 2608 / 1903 | 60 / 63 |
| 46 | p2 → p1 (score) | Ataque básico — cancelada por controle | Investida — executada, dano 306, MP −59 | 2302 / 1951 | 91 / 24 |
| 47 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 2302 / 1951 | 46 / 44 |
| 48 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 137 | 2214 / 1817 | 77 / 64 |
| 49 | p1 → p2 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Investida — executada, dano 0, MP −59 | 2322 / 1477 | 38 / 25 |
| 50 | p1 → p2 (score) | Ataque básico — executada, dano 187 | Ataque básico — executada, dano 0 | 2381 / 1290 | 69 / 45 |
| 51 | p1 → p2 (score) | Ataque básico — executada, dano 187 | Ataque básico — executada, dano 172 | 2268 / 1130 | 100 / 65 |
| 52 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Investida — executada, dano 0, MP −59 | 2268 / 1130 | 55 / 26 |
| 53 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 137 | 2180 / 996 | 86 / 46 |
| 54 | p1 → p2 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Ataque básico — executada, dano 137 | 2151 / 677 | 47 / 66 |
| 55 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Investida — executada, dano 306, MP −59 | 1894 / 570 | 78 / 27 |
| 56 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 1894 / 570 | 33 / 47 |
| 57 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Ataque básico — executada, dano 0 | 1943 / 415 | 64 / 67 |
| 58 | p1 → p2 (score) | Ataque básico — executada, dano 155 | Investida — executada, dano 244, MP −59 | 1748 / 299 | 95 / 28 |
| 59 | p1 → p2 (score) | Quebra-Guarda — executada, dano 340, MP −70 | Ataque básico — cancelada por morte | 1856 / -41 | 56 / 28 |

#### Fase de 64 27 — fer × Baiano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W64 | fer | Guerreiro | 23 | 29.98 | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | defesa + sustento |
| p2 | W06 | Baiano | Guerreiro | 21 | 27.91 | Tomar Fôlego, Mira Calma, Ritmo de Duelo, Cutelada | defesa + sustento |

- Seed da partida: `3743995336007600765`
- Rodadas: **15**
- Vencedor: **fer** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3978/5977 (66.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fer | Baiano |
|---|---|---|
| Dano causado (golpes + DoT) | 5611 (5611 + 0) | 2668 (2668 + 0) |
| Cura (skill + roubo de vida) | 669 (0 + 669) | 1184 (521 + 663) |
| MP gasto em ações | 1125 | 966 |
| Skills / ataques básicos | 15 / 0 | 12 / 2 |
| Acertos / erros | 11 / 1 | 9 / 1 |
| Críticos (dano) | 5 (3232) | 2 (910) |
| Agiu primeiro (rodadas) | 13 | 2 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- fer aplicou: weakened (rodada 3)
- fer tentou sem sucesso: stun (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), weakened (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 9), weakened (rodada 9), stun (rodada 10), stun (rodada 11), weakened (rodada 11), stun (rodada 12), stun (rodada 15), weakened (rodada 15)
- fer ativou: Juramento da Muralha ×3
- Baiano aplicou: vulnerable (rodada 5), vulnerable (rodada 8)
- Baiano tentou sem sucesso: stun (rodada 2), vulnerable (rodada 2), stun (rodada 3), stun (rodada 5), stun (rodada 7), stun (rodada 8), stun (rodada 10), stun (rodada 12), vulnerable (rodada 12), stun (rodada 13), stun (rodada 14)
- Baiano ativou: Ritmo de Duelo ×3

Rodada a rodada:

| Rodada | Ordem (critério) | fer (p1) | Baiano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Ritmo de Duelo — executada, dano 0, MP −84 | 5977 / 4349 | 951 / 719 |
| 2 | p1 → p2 (score) | Golpe Poderoso — executada, dano 419, MP −52 | Mira Calma — executada, dano 255, MP −92 | 5722 / 3993 | 921 / 646 |
| 3 | p1 → p2 (score) | Soco de Placa — executada, dano 653, MP −61 | Cutelada — executada, dano 108, MP −68 | 5698 / 3367 | 882 / 597 |
| 4 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Ataque básico — executada, dano 0 | 5748 / 2979 | 852 / 616 |
| 5 | p1 → p2 (score) | Soco de Placa — executada, dano 408, MP −61 | Mira Calma — executada, dano 517, MP −92 | 5284 / 2700 | 813 / 543 |
| 6 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Ritmo de Duelo — executada, dano 0, MP −84 | 5334 / 2312 | 783 / 478 |
| 7 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Cutelada — executada, dano 707, MP −68 | 4627 / 2488 | 653 / 429 |
| 8 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Mira Calma — executada, dano 223, MP −92 | 4454 / 2155 | 623 / 356 |
| 9 | p2 → p1 (score) | Soco de Placa — executada, dano 653, MP −61 | Tomar Fôlego — executada, dano 0, MP −74 | 4538 / 2023 | 584 / 301 |
| 10 | p1 → p2 (score) | Golpe Poderoso — executada, dano 620, MP −52 | Cutelada — executada, dano 203, MP −68 | 4415 / 1453 | 554 / 252 |
| 11 | p1 → p2 (score) | Soco de Placa — executada, dano 653, MP −61 | Ritmo de Duelo — executada, dano 0, MP −84 | 4499 / 800 | 515 / 187 |
| 12 | p1 → p2 (score) | Golpe Poderoso — executada, dano 388, MP −52 | Mira Calma — executada, dano 452, MP −92 | 4097 / 525 | 485 / 114 |
| 13 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Cutelada — executada, dano 135, MP −68 | 3962 / 558 | 355 / 65 |
| 14 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 68 | 3894 / 575 | 325 / 84 |
| 15 | p1 → p2 (score) | Soco de Placa — executada, dano 653, MP −61 | Tomar Fôlego — cancelada por morte | 3978 / -78 | 286 / 84 |

#### Fase de 64 28 — Felps × Hayashii

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W31 | Felps | Guerreiro | 20 | 29.64 | Sangue nos Olhos, Quebra-Guarda, Travar o Pulso, Marca do Açougueiro | crítico + controle |
| p2 | W45 | Hayashii | Guerreiro | 22 | 27.91 | Golpe Poderoso, Quebra-Guarda, Quebra-Ossos, Baluarte | defesa + sustento |

- Seed da partida: `14407454639189636163`
- Rodadas: **14**
- Vencedor: **Felps** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2557/4098 (62.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Felps | Hayashii |
|---|---|---|
| Dano causado (golpes + DoT) | 5492 (2852 + 2640) | 1766 (1766 + 0) |
| Cura (skill + roubo de vida) | 225 (0 + 225) | 521 (0 + 521) |
| MP gasto em ações | 632 | 544 |
| Skills / ataques básicos | 13 / 0 | 8 / 3 |
| Acertos / erros | 6 / 0 | 6 / 1 |
| Críticos (dano) | 2 (1410) | 0 (0) |
| Agiu primeiro (rodadas) | 3 | 11 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- Felps aplicou: stun (rodada 3), poison (rodada 3), weakened (rodada 6), slowed (rodada 6), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), vulnerable (rodada 9), weakened (rodada 10), bleed (rodada 12), vulnerable (rodada 13), bleed (rodada 13)
- Felps tentou sem sucesso: vulnerable (rodada 1), weakened (rodada 2), bleed (rodada 3), vulnerable (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), bleed (rodada 4), vulnerable (rodada 5), stun (rodada 7), poison (rodada 7), vulnerable (rodada 7), bleed (rodada 8), poison (rodada 8), bleed (rodada 9), slowed (rodada 10), stun (rodada 11), bleed (rodada 11), poison (rodada 11), vulnerable (rodada 11), stun (rodada 12), bleed (rodada 12), poison (rodada 12)
- Hayashii aplicou: slowed (rodada 1), slowed (rodada 5), slowed (rodada 9)
- Hayashii tentou sem sucesso: bleed (rodada 1), stun (rodada 3), bleed (rodada 3), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), slowed (rodada 13)
- Leis disparadas por Hayashii: FERIDA SÉPTICA (rodada 7), FERIDA ABERTA (rodada 13)

Rodada a rodada:

| Rodada | Ordem (critério) | Felps (p1) | Hayashii (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −50 | Quebra-Ossos — executada, dano 0, MP −89 | 4098 / 4939 | 568 / 809 |
| 2 | p2 → p1 (score) | Travar o Pulso — executada, dano 0, MP −50 | Golpe Poderoso — executada, dano 0, MP −47 | 4098 / 4939 | 530 / 779 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 396, MP −50 | Ataque básico — executada, dano 227 | 3902 / 4543 | 492 / 796 |
| 4 | p2 → p1 (score) | Marca do Açougueiro — executada, dano 295, MP −44 | Golpe Poderoso — cancelada por controle | 3925 / 4174 | 460 / 813 |
| 5 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −50 | Quebra-Ossos — executada, dano 0, MP −89 | 3925 / 4100 | 422 / 741 |
| 6 | p2 → p1 (score) | Travar o Pulso — executada, dano 0, MP −50 | Golpe Poderoso — executada, dano 425, MP −47 | 3500 / 4170 | 384 / 711 |
| 7 | p2 → p1 (score) | Quebra-Guarda — executada, dano 396, MP −50 | Ataque básico — executada, dano 187 | 3344 / 3763 | 346 / 728 |
| 8 | p1 → p2 (score) | Marca do Açougueiro — executada, dano 576, MP −44 | Golpe Poderoso — cancelada por controle | 3390 / 2718 | 314 / 745 |
| 9 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −50 | Quebra-Ossos — executada, dano 0, MP −89 | 3390 / 2249 | 276 / 673 |
| 10 | p2 → p1 (score) | Travar o Pulso — executada, dano 0, MP −50 | Golpe Poderoso — executada, dano 425, MP −47 | 2965 / 1924 | 238 / 643 |
| 11 | p1 → p2 (score) | Quebra-Guarda — executada, dano 834, MP −50 | Ataque básico — executada, dano 187 | 2844 / 1079 | 200 / 660 |
| 12 | p2 → p1 (score) | Marca do Açougueiro — executada, dano 355, MP −44 | Golpe Poderoso — executada, dano 315, MP −47 | 2557 / 757 | 168 / 630 |
| 13 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −50 | Quebra-Ossos — executada, dano 0, MP −89 | 2557 / 560 | 130 / 558 |
| 14 | p2 → p1 (score) | Travar o Pulso — não alcançada (o duelo acabou antes) | Golpe Poderoso — cancelada por morte | 2557 / -32 | 130 / 575 |

#### Fase de 64 29 — RazaH × mount

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W15 | RazaH | Guerreiro | 20 | 29.06 | Marca do Caçador, Grito Curto, Pausa Útil, Mão Dupla | crítico + controle |
| p2 | W25 | mount | Guerreiro | 23 | 29.52 | Golpe Poderoso, Soco de Placa, Couro Batido, Disciplina de Forja | defesa + sustento |

- Seed da partida: `989407218878997817`
- Rodadas: **31**
- Vencedor: **RazaH** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 509/5285 (9.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | RazaH | mount |
|---|---|---|
| Dano causado (golpes + DoT) | 8788 (2239 + 6549) | 4869 (4869 + 0) |
| Cura (skill + roubo de vida) | 93 (0 + 93) | 866 (0 + 866) |
| MP gasto em ações | 855 | 1298 |
| Skills / ataques básicos | 17 / 13 | 20 / 7 |
| Acertos / erros | 18 / 1 | 17 / 2 |
| Críticos (dano) | 1 (88) | 1 (291) |
| Agiu primeiro (rodadas) | 0 | 31 |
| Ações perdidas por controle | 0 | 3 |

Efeitos relevantes:
- RazaH aplicou: fear (rodada 2), weakened (rodada 2), fear (rodada 7), bleed (rodada 8), stun (rodada 10), bleed (rodada 10), fear (rodada 10), poison (rodada 12), stun (rodada 14), fear (rodada 14), bleed (rodada 17), fear (rodada 22), bleed (rodada 23), stun (rodada 24), poison (rodada 25), fear (rodada 27), bleed (rodada 28), poison (rodada 29)
- RazaH tentou sem sucesso: stun (rodada 3), bleed (rodada 3), poison (rodada 3), fear (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), fear (rodada 4), stun (rodada 5), bleed (rodada 5), poison (rodada 5), fear (rodada 5), weakened (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), fear (rodada 8), stun (rodada 9), bleed (rodada 9), poison (rodada 9), fear (rodada 9), poison (rodada 10), stun (rodada 12), bleed (rodada 12), fear (rodada 12), bleed (rodada 12), stun (rodada 13), bleed (rodada 13), poison (rodada 13), fear (rodada 13), bleed (rodada 14), poison (rodada 14), stun (rodada 17), bleed (rodada 17), poison (rodada 17), fear (rodada 17), fear (rodada 18), stun (rodada 19), bleed (rodada 19), poison (rodada 19), fear (rodada 19), stun (rodada 20), bleed (rodada 20), poison (rodada 20), fear (rodada 20), weakened (rodada 22), stun (rodada 23), bleed (rodada 23), poison (rodada 23), fear (rodada 23), bleed (rodada 24), poison (rodada 24), fear (rodada 24), stun (rodada 25), bleed (rodada 25), fear (rodada 25), weakened (rodada 27), stun (rodada 28), bleed (rodada 28), poison (rodada 28), fear (rodada 28), stun (rodada 29), bleed (rodada 29), fear (rodada 29), stun (rodada 30), bleed (rodada 30), poison (rodada 30), fear (rodada 30)
- RazaH ativou: Pausa Útil ×6
- mount ativou: Couro Batido ×5, Disciplina de Forja ×3
- Leis disparadas por mount: PÂNICO (rodada 10), FERIDA SÉPTICA (rodada 25), FERIDA SÉPTICA (rodada 28)

Rodada a rodada:

| Rodada | Ordem (critério) | RazaH (p1) | mount (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −37 | Couro Batido — executada, dano 0, MP −70 | 5285 / 7863 | 500 / 716 |
| 2 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −45 | Disciplina de Forja — executada, dano 0, MP −105 | 5285 / 7863 | 479 / 630 |
| 3 | p2 → p1 (score) | Mão Dupla — executada, dano 182, MP −68 | Golpe Poderoso — executada, dano 0, MP −52 | 5285 / 7681 | 435 / 597 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 74 | Soco de Placa — executada, dano 0, MP −61 | 5285 / 7607 | 459 / 555 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 53 | Couro Batido — executada, dano 0, MP −70 | 5285 / 7554 | 483 / 504 |
| 6 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −37 | Golpe Poderoso — executada, dano 357, MP −52 | 4928 / 7618 | 456 / 471 |
| 7 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −45 | Disciplina de Forja — executada, dano 0, MP −105 | 4928 / 7618 | 435 / 385 |
| 8 | p2 → p1 (score) | Mão Dupla — executada, dano 182, MP −68 | Golpe Poderoso — executada, dano 357, MP −52 | 4580 / 7500 | 391 / 352 |
| 9 | p2 → p1 (score) | Ataque básico — executada, dano 88 | Couro Batido — executada, dano 0, MP −70 | 4584 / 7098 | 415 / 301 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 53 | Golpe Poderoso — executada, dano 357, MP −52 | 4229 / 6795 | 439 / 268 |
| 11 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −37 | Soco de Placa — cancelada por controle | 4229 / 6166 | 412 / 287 |
| 12 | p2 → p1 (score) | Mão Dupla — executada, dano 182, MP −68 | Disciplina de Forja — executada, dano 0, MP −105 | 4238 / 5355 | 368 / 201 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 53 | Couro Batido — executada, dano 0, MP −70 | 4240 / 5185 | 392 / 150 |
| 14 | p2 → p1 (score) | Ataque básico — executada, dano 53 | Golpe Poderoso — executada, dano 357, MP −52 | 3885 / 5079 | 416 / 117 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Soco de Placa — cancelada por controle | 3885 / 4962 | 440 / 136 |
| 16 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −37 | Golpe Poderoso — executada, dano 331, MP −52 | 3554 / 4904 | 413 / 103 |
| 17 | p2 → p1 (score) | Mão Dupla — executada, dano 174, MP −68 | Couro Batido — executada, dano 0, MP −70 | 3562 / 4613 | 369 / 52 |
| 18 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −45 | Golpe Poderoso — executada, dano 331, MP −52 | 3231 / 4358 | 348 / 19 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 100 | Ataque básico — executada, dano 194 | 3042 / 3978 | 372 / 38 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 100 | Ataque básico — executada, dano 291 | 2756 / 3616 | 396 / 57 |
| 21 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −37 | Golpe Poderoso — executada, dano 331, MP −52 | 2425 / 3675 | 369 / 24 |
| 22 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −45 | Ataque básico — executada, dano 194 | 2231 / 3709 | 348 / 43 |
| 23 | p2 → p1 (score) | Mão Dupla — executada, dano 243, MP −68 | Ataque básico — executada, dano 194 | 2049 / 3500 | 304 / 62 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 100 | Golpe Poderoso — executada, dano 331, MP −52 | 1723 / 3145 | 328 / 29 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 100 | Ataque básico — cancelada por controle | 1728 / 2731 | 352 / 48 |
| 26 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −37 | Ataque básico — executada, dano 194 | 1534 / 2334 | 325 / 67 |
| 27 | p2 → p1 (score) | Grito Curto — executada, dano 0, MP −45 | Golpe Poderoso — executada, dano 331, MP −52 | 1203 / 1962 | 304 / 34 |
| 28 | p2 → p1 (score) | Mão Dupla — executada, dano 302, MP −68 | Ataque básico — executada, dano 194 | 1024 / 1577 | 260 / 53 |
| 29 | p2 → p1 (score) | Ataque básico — executada, dano 100 | Golpe Poderoso — executada, dano 331, MP −52 | 698 / 1105 | 284 / 20 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 100 | Ataque básico — executada, dano 194 | 509 / 490 | 308 / 39 |
| 31 | p2 → p1 (score) | Pausa Útil — não alcançada (o duelo acabou antes) | Ataque básico — cancelada por morte | 509 / -59 | 308 / 58 |

#### Fase de 64 30 — jukes × gabepeixe

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W03 | jukes | Guerreiro | 22 | 28.14 | Golpe Poderoso, Respirar Fundo, Mira Calma, Leitura de Terreno | defesa + sustento |
| p2 | W62 | gabepeixe | Guerreiro | 21 | 28.60 | Fúria, Soco de Placa, Travar o Pulso, Tremor de Bigorna | crítico + controle |

- Seed da partida: `8932018971394209653`
- Rodadas: **18**
- Vencedor: **jukes** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1110/5515 (20.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | jukes | gabepeixe |
|---|---|---|
| Dano causado (golpes + DoT) | 4418 (4418 + 0) | 5128 (4278 + 850) |
| Cura (skill + roubo de vida) | 723 (551 + 172) | 0 (0 + 0) |
| MP gasto em ações | 1210 | 876 |
| Skills / ataques básicos | 16 / 1 | 11 / 5 |
| Acertos / erros | 9 / 3 | 7 / 2 |
| Críticos (dano) | 1 (499) | 5 (3545) |
| Agiu primeiro (rodadas) | 6 | 12 |
| Ações perdidas por controle | 1 | 1 |

Efeitos relevantes:
- jukes aplicou: vulnerable (rodada 5), vulnerable (rodada 8), stun (rodada 15), vulnerable (rodada 18)
- jukes tentou sem sucesso: stun (rodada 5), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 12), stun (rodada 13), vulnerable (rodada 13), stun (rodada 17), stun (rodada 18)
- jukes ativou: Leitura de Terreno ×4
- gabepeixe aplicou: weakened (rodada 2), slowed (rodada 2), stun (rodada 3), weakened (rodada 6), bleed (rodada 12), poison (rodada 13), weakened (rodada 14), slowed (rodada 14)
- gabepeixe tentou sem sucesso: bleed (rodada 3), poison (rodada 3), fear (rodada 3), weakened (rodada 3), slowed (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), fear (rodada 7), weakened (rodada 7), weakened (rodada 10), stun (rodada 11), bleed (rodada 11), poison (rodada 11), fear (rodada 11), weakened (rodada 11), stun (rodada 12), poison (rodada 12), fear (rodada 12), stun (rodada 13), bleed (rodada 13), fear (rodada 13), weakened (rodada 13), stun (rodada 15), bleed (rodada 15), poison (rodada 15), fear (rodada 15), stun (rodada 17), bleed (rodada 17), poison (rodada 17), fear (rodada 17)
- gabepeixe ativou: Fúria ×3

Rodada a rodada:

| Rodada | Ordem (critério) | jukes (p1) | gabepeixe (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Fúria — executada, dano 0, MP −152 | 5515 / 4274 | 742 / 560 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Travar o Pulso — executada, dano 0, MP −56 | 5515 / 4274 | 723 / 518 |
| 3 | p2 → p1 (score) | Mira Calma — cancelada por controle | Soco de Placa — executada, dano 836, MP −49 | 4679 / 4274 | 751 / 483 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 0 | 4679 / 4274 | 732 / 497 |
| 5 | p1 → p2 (score) | Mira Calma — executada, dano 727, MP −103 | Fúria — executada, dano 0, MP −152 | 4708 / 3547 | 657 / 359 |
| 6 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Travar o Pulso — executada, dano 0, MP −56 | 4708 / 3547 | 586 / 317 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Soco de Placa — executada, dano 836, MP −49 | 3872 / 3547 | 567 / 282 |
| 8 | p2 → p1 (score) | Mira Calma — executada, dano 727, MP −103 | Ataque básico — executada, dano 0 | 3901 / 2820 | 492 / 296 |
| 9 | p1 → p2 (score) | Golpe Poderoso — executada, dano 396, MP −47 | Fúria — executada, dano 0, MP −152 | 3916 / 2424 | 473 / 158 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 193 | Travar o Pulso — executada, dano 0, MP −56 | 3923 / 2231 | 501 / 116 |
| 11 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Soco de Placa — executada, dano 477, MP −49 | 3446 / 2231 | 430 / 81 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 333, MP −47 | Ataque básico — executada, dano 449 | 2790 / 1898 | 411 / 95 |
| 13 | p1 → p2 (score) | Mira Calma — executada, dano 639, MP −103 | Soco de Placa — executada, dano 975, MP −49 | 1620 / 1259 | 336 / 60 |
| 14 | p1 → p2 (score) | Respirar Fundo — executada, dano 0, MP −73 | Travar o Pulso — executada, dano 0, MP −56 | 2089 / 1259 | 291 / 18 |
| 15 | p2 → p1 (score) | Golpe Poderoso — executada, dano 265, MP −47 | Ataque básico — executada, dano 256 | 1761 / 994 | 272 / 32 |
| 16 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Ataque básico — cancelada por controle | 1679 / 994 | 201 / 46 |
| 17 | p2 → p1 (score) | Golpe Poderoso — executada, dano 499, MP −47 | Ataque básico — executada, dano 449 | 1167 / 495 | 182 / 60 |
| 18 | p1 → p2 (score) | Mira Calma — executada, dano 639, MP −103 | Travar o Pulso — cancelada por morte | 1110 / -144 | 107 / 60 |

#### Fase de 64 31 — aspaszin × sacy

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W27 | aspaszin | Guerreiro | 22 | 29.29 | Golpe Poderoso, Quebra-Guarda, Fôlego de Marcha, Respirar Fundo | crítico + defesa + sustento |
| p2 | W16 | sacy | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Escudo Protetor, Silêncio do Veterano | sustento |

- Seed da partida: `15802958274225019879`
- Rodadas: **58**
- Vencedor: **sacy** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1211/7520 (16.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | aspaszin | sacy |
|---|---|---|
| Dano causado (golpes + DoT) | 7195 (6595 + 600) | 5393 (5393 + 0) |
| Cura (skill + roubo de vida) | 503 (0 + 503) | 886 (0 + 886) |
| MP gasto em ações | 1787 | 2152 |
| Skills / ataques básicos | 33 / 24 | 19 / 39 |
| Acertos / erros | 35 / 16 | 31 / 11 |
| Críticos (dano) | 13 (2930) | 3 (642) |
| Agiu primeiro (rodadas) | 0 | 58 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- aspaszin aplicou: bleed (rodada 12)
- aspaszin tentou sem sucesso: bleed (rodada 4), bleed (rodada 5), bleed (rodada 9), bleed (rodada 14), bleed (rodada 15), bleed (rodada 17), bleed (rodada 19), bleed (rodada 20), bleed (rodada 22), bleed (rodada 23), vulnerable (rodada 23), bleed (rodada 24), bleed (rodada 25), bleed (rodada 27), bleed (rodada 28), bleed (rodada 30), bleed (rodada 31), bleed (rodada 32), bleed (rodada 33), bleed (rodada 35), bleed (rodada 36), bleed (rodada 37), bleed (rodada 38), bleed (rodada 39), bleed (rodada 40), bleed (rodada 41), bleed (rodada 42), bleed (rodada 44), bleed (rodada 46), bleed (rodada 48), bleed (rodada 51), bleed (rodada 52), bleed (rodada 53), bleed (rodada 54), bleed (rodada 55)
- aspaszin ativou: Fôlego de Marcha ×6
- sacy aplicou: fear (rodada 2), vulnerable (rodada 2), vulnerable (rodada 4), fear (rodada 7)
- sacy tentou sem sucesso: vulnerable (rodada 7)
- sacy ativou: Escudo Protetor ×14

Rodada a rodada:

| Rodada | Ordem (critério) | aspaszin (p1) | sacy (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Fôlego de Marcha — executada, dano 0, MP −73 | Escudo Protetor — executada, dano 0, MP −109 | 4874 / 7520 | 809 / 677 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Silêncio do Veterano — executada, dano 0, MP −135 | 4874 / 7520 | 779 / 568 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Golpe Devastador — executada, dano 390, MP −120 | 4484 / 7520 | 733 / 474 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 268, MP −47 | Mira Calma — executada, dano 669, MP −116 | 3836 / 7252 | 703 / 384 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Escudo Protetor — executada, dano 0, MP −109 | 3849 / 7079 | 720 / 301 |
| 6 | p2 → p1 (score) | Fôlego de Marcha — executada, dano 0, MP −73 | Ataque básico — executada, dano 142 | 3707 / 7108 | 664 / 327 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Silêncio do Veterano — executada, dano 0, MP −135 | 3707 / 7108 | 634 / 218 |
| 8 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Golpe Devastador — executada, dano 0, MP −120 | 3707 / 7108 | 588 / 124 |
| 9 | p2 → p1 (score) | Golpe Poderoso — executada, dano 201, MP −47 | Escudo Protetor — executada, dano 0, MP −109 | 3723 / 6907 | 558 / 41 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 3581 / 6936 | 575 / 67 |
| 11 | p2 → p1 (score) | Fôlego de Marcha — executada, dano 0, MP −73 | Ataque básico — executada, dano 142 | 3439 / 6965 | 519 / 93 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 430, MP −47 | Ataque básico — executada, dano 142 | 3331 / 6564 | 489 / 119 |
| 13 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Escudo Protetor — executada, dano 0, MP −109 | 3331 / 6264 | 443 / 36 |
| 14 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Ataque básico — executada, dano 214 | 3131 / 5822 | 413 / 62 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Ataque básico — executada, dano 0 | 3144 / 5649 | 430 / 88 |
| 16 | p2 → p1 (score) | Fôlego de Marcha — executada, dano 0, MP −73 | Ataque básico — executada, dano 0 | 3144 / 5649 | 374 / 114 |
| 17 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Escudo Protetor — executada, dano 0, MP −109 | 3158 / 5463 | 344 / 31 |
| 18 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Ataque básico — executada, dano 142 | 3016 / 5492 | 298 / 57 |
| 19 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Ataque básico — executada, dano 0 | 3030 / 5306 | 268 / 83 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 144 | Ataque básico — executada, dano 142 | 2899 / 5191 | 285 / 109 |
| 21 | p2 → p1 (score) | Fôlego de Marcha — executada, dano 0, MP −73 | Escudo Protetor — executada, dano 0, MP −109 | 2899 / 5191 | 229 / 26 |
| 22 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Ataque básico — executada, dano 142 | 2771 / 5034 | 199 / 52 |
| 23 | p2 → p1 (score) | Quebra-Guarda — executada, dano 236, MP −63 | Ataque básico — executada, dano 142 | 2647 / 4827 | 153 / 78 |
| 24 | p2 → p1 (score) | Golpe Poderoso — executada, dano 248, MP −47 | Ataque básico — executada, dano 142 | 2524 / 4608 | 123 / 104 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 231 | Ataque básico — executada, dano 0 | 2542 / 4377 | 140 / 130 |
| 26 | p2 → p1 (score) | Fôlego de Marcha — executada, dano 0, MP −73 | Escudo Protetor — executada, dano 0, MP −109 | 2542 / 4377 | 84 / 47 |
| 27 | p2 → p1 (score) | Golpe Poderoso — executada, dano 298, MP −47 | Ataque básico — executada, dano 142 | 2423 / 4108 | 54 / 73 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 108 | Ataque básico — executada, dano 142 | 2289 / 4029 | 71 / 99 |
| 29 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 0 | 2289 / 4029 | 41 / 125 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Escudo Protetor — executada, dano 0, MP −109 | 2302 / 3856 | 58 / 42 |
| 31 | p2 → p1 (score) | Golpe Poderoso — executada, dano 298, MP −47 | Ataque básico — executada, dano 142 | 2183 / 3587 | 28 / 68 |
| 32 | p2 → p1 (score) | Ataque básico — executada, dano 108 | Ataque básico — executada, dano 0 | 2191 / 3479 | 45 / 94 |
| 33 | p2 → p1 (score) | Ataque básico — executada, dano 144 | Ataque básico — executada, dano 142 | 2060 / 3364 | 62 / 120 |
| 34 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Escudo Protetor — executada, dano 0, MP −109 | 2060 / 3364 | 32 / 37 |
| 35 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Ataque básico — executada, dano 142 | 1931 / 3220 | 49 / 63 |
| 36 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Ataque básico — executada, dano 0 | 1945 / 3034 | 19 / 89 |
| 37 | p2 → p1 (score) | Ataque básico — executada, dano 231 | Ataque básico — executada, dano 142 | 1821 / 2832 | 36 / 115 |
| 38 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Escudo Protetor — executada, dano 0, MP −109 | 1834 / 2659 | 53 / 32 |
| 39 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Ataque básico — executada, dano 142 | 1706 / 2502 | 23 / 58 |
| 40 | p2 → p1 (score) | Ataque básico — executada, dano 108 | Ataque básico — executada, dano 142 | 1572 / 2423 | 40 / 84 |
| 41 | p2 → p1 (score) | Ataque básico — executada, dano 144 | Ataque básico — executada, dano 0 | 1583 / 2279 | 57 / 110 |
| 42 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Escudo Protetor — executada, dano 0, MP −109 | 1597 / 2093 | 27 / 27 |
| 43 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 214 | 1383 / 2137 | 44 / 53 |
| 44 | p2 → p1 (score) | Ataque básico — executada, dano 108 | Ataque básico — executada, dano 142 | 1249 / 2058 | 61 / 79 |
| 45 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 0 | 1249 / 2058 | 31 / 105 |
| 46 | p2 → p1 (score) | Ataque básico — executada, dano 231 | Ataque básico — executada, dano 142 | 1125 / 1856 | 48 / 131 |
| 47 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Escudo Protetor — executada, dano 0, MP −109 | 1125 / 1856 | 18 / 48 |
| 48 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Ataque básico — executada, dano 142 | 996 / 1712 | 35 / 74 |
| 49 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 854 / 1741 | 52 / 100 |
| 50 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 142 | 712 / 1770 | 22 / 126 |
| 51 | p2 → p1 (score) | Ataque básico — executada, dano 108 | Escudo Protetor — executada, dano 0, MP −109 | 720 / 1662 | 39 / 43 |
| 52 | p2 → p1 (score) | Ataque básico — executada, dano 173 | Ataque básico — executada, dano 214 | 519 / 1533 | 56 / 69 |
| 53 | p2 → p1 (score) | Golpe Poderoso — executada, dano 186, MP −47 | Ataque básico — executada, dano 142 | 391 / 1376 | 26 / 95 |
| 54 | p2 → p1 (score) | Ataque básico — executada, dano 144 | Ataque básico — executada, dano 142 | 260 / 1261 | 43 / 121 |
| 55 | p2 → p1 (score) | Ataque básico — executada, dano 108 | Escudo Protetor — executada, dano 0, MP −109 | 268 / 1153 | 60 / 38 |
| 56 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 0 | 268 / 1153 | 30 / 64 |
| 57 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 126 / 1182 | 47 / 90 |
| 58 | p2 → p1 (score) | Golpe Poderoso — cancelada por morte | Ataque básico — executada, dano 142 | -16 / 1211 | 47 / 116 |

#### Fase de 64 32 — RNakano × PaulinhoLOKObr

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W42 | RNakano | Guerreiro | 24 | 29.64 | Golpe Duplo, Cutelada, Gancho e Corda, Disciplina de Forja | sustento |
| p2 | W46 | PaulinhoLOKObr | Guerreiro | 22 | 28.48 | Tremor de Bigorna, Quebra-Guarda, Respirar Fundo, Baluarte | defesa + sustento |

- Seed da partida: `10076971382503481094`
- Rodadas: **50**
- Vencedor: **RNakano** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4619/8159 (56.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | RNakano | PaulinhoLOKObr |
|---|---|---|
| Dano causado (golpes + DoT) | 8173 (8173 + 0) | 6381 (6381 + 0) |
| Cura (skill + roubo de vida) | 2841 (0 + 2841) | 2053 (1334 + 719) |
| MP gasto em ações | 2288 | 1617 |
| Skills / ataques básicos | 21 / 29 | 22 / 27 |
| Acertos / erros | 34 / 8 | 31 / 11 |
| Críticos (dano) | 2 (556) | 6 (1778) |
| Agiu primeiro (rodadas) | 20 | 30 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- RNakano aplicou: stun (rodada 12)
- RNakano tentou sem sucesso: stun (rodada 2), stun (rodada 3), frailty (rodada 3), stun (rodada 5), stun (rodada 7), stun (rodada 10), vulnerable (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 20), stun (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 31), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 37), stun (rodada 38), stun (rodada 39), stun (rodada 40), stun (rodada 41), stun (rodada 42), stun (rodada 43), stun (rodada 44), stun (rodada 45), stun (rodada 46), stun (rodada 49), stun (rodada 50)
- RNakano ativou: Disciplina de Forja ×5
- PaulinhoLOKObr aplicou: vulnerable (rodada 8)
- PaulinhoLOKObr tentou sem sucesso: stun (rodada 2), vulnerable (rodada 14), vulnerable (rodada 20), stun (rodada 23), vulnerable (rodada 25), stun (rodada 33), vulnerable (rodada 36), stun (rodada 44)
- PaulinhoLOKObr ativou: Baluarte ×5

Rodada a rodada:

| Rodada | Ordem (critério) | RNakano (p1) | PaulinhoLOKObr (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Baluarte — executada, dano 0, MP −94 | 8159 / 5803 | 795 / 672 |
| 2 | p1 → p2 (score) | Gancho e Corda — executada, dano 0, MP −131 | Tremor de Bigorna — executada, dano 234, MP −71 | 7925 / 5803 | 694 / 620 |
| 3 | p1 → p2 (score) | Golpe Duplo — executada, dano 295, MP −130 | Quebra-Guarda — executada, dano 0, MP −63 | 8028 / 5508 | 594 / 576 |
| 4 | p1 → p2 (score) | Cutelada — executada, dano 0, MP −95 | Ataque básico — executada, dano 111 | 7917 / 5521 | 529 / 595 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 7841 / 5327 | 559 / 614 |
| 6 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Baluarte — executada, dano 0, MP −94 | 7841 / 5327 | 471 / 539 |
| 7 | p1 → p2 (score) | Gancho e Corda — executada, dano 0, MP −131 | Tremor de Bigorna — executada, dano 0, MP −71 | 7841 / 5327 | 370 / 487 |
| 8 | p1 → p2 (score) | Golpe Duplo — executada, dano 0, MP −130 | Quebra-Guarda — executada, dano 270, MP −63 | 7571 / 5359 | 270 / 443 |
| 9 | p1 → p2 (score) | Cutelada — executada, dano 0, MP −95 | Ataque básico — executada, dano 127 | 7444 / 5374 | 205 / 462 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 0 | 7517 / 5163 | 235 / 481 |
| 11 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Baluarte — executada, dano 0, MP −94 | 7517 / 5163 | 147 / 406 |
| 12 | p1 → p2 (score) | Gancho e Corda — executada, dano 0, MP −131 | Tremor de Bigorna — cancelada por controle | 7517 / 5163 | 46 / 425 |
| 13 | p1 → p2 (score) | Ataque básico — executada, dano 135 | Tremor de Bigorna — executada, dano 0, MP −71 | 7564 / 5028 | 76 / 373 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 217 | Quebra-Guarda — executada, dano 270, MP −63 | 7369 / 4843 | 106 / 329 |
| 15 | p1 → p2 (score) | Cutelada — executada, dano 420, MP −95 | Ataque básico — executada, dano 149 | 7367 / 4440 | 41 / 348 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 135 | Baluarte — executada, dano 0, MP −94 | 7414 / 4305 | 71 / 273 |
| 17 | p2 → p1 (score) | Ataque básico — executada, dano 135 | Quebra-Guarda — executada, dano 0, MP −63 | 7461 / 4170 | 101 / 229 |
| 18 | p2 → p1 (score) | Cutelada — executada, dano 269, MP −95 | Tremor de Bigorna — executada, dano 0, MP −71 | 7555 / 3901 | 36 / 177 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 149 | 7406 / 3918 | 66 / 196 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Quebra-Guarda — executada, dano 363, MP −63 | 7116 / 3750 | 96 / 152 |
| 21 | p2 → p1 (score) | Cutelada — executada, dano 269, MP −95 | Baluarte — executada, dano 0, MP −94 | 7210 / 3481 | 31 / 77 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 135 | Ataque básico — executada, dano 0 | 7257 / 3346 | 61 / 96 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 135 | Tremor de Bigorna — executada, dano 503, MP −71 | 6801 / 3271 | 91 / 44 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 6725 / 3077 | 121 / 63 |
| 25 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Quebra-Guarda — executada, dano 363, MP −63 | 6362 / 3120 | 33 / 19 |
| 26 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 111 | 6324 / 2922 | 63 / 38 |
| 27 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 178 | 6219 / 2732 | 93 / 57 |
| 28 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 178 | 6114 / 2542 | 123 / 76 |
| 29 | p1 → p2 (score) | Cutelada — executada, dano 0, MP −95 | Respirar Fundo — executada, dano 0, MP −73 | 6114 / 3209 | 58 / 22 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 149 | 5965 / 3226 | 88 / 41 |
| 31 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 5889 / 3032 | 118 / 60 |
| 32 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Ataque básico — executada, dano 0 | 5889 / 3032 | 30 / 79 |
| 33 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Tremor de Bigorna — executada, dano 234, MP −71 | 5728 / 2849 | 60 / 27 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 111 | 5690 / 2651 | 90 / 46 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 178 | 5585 / 2461 | 120 / 65 |
| 36 | p1 → p2 (score) | Cutelada — executada, dano 420, MP −95 | Quebra-Guarda — executada, dano 323, MP −63 | 5409 / 2079 | 55 / 21 |
| 37 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 5333 / 1885 | 85 / 40 |
| 38 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 0 | 5406 / 1674 | 115 / 59 |
| 39 | p2 → p1 (score) | Cutelada — executada, dano 420, MP −95 | Ataque básico — executada, dano 149 | 5404 / 1271 | 50 / 78 |
| 40 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Respirar Fundo — executada, dano 0, MP −73 | 5477 / 1727 | 80 / 24 |
| 41 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 5401 / 1533 | 110 / 43 |
| 42 | p2 → p1 (score) | Cutelada — executada, dano 420, MP −95 | Ataque básico — executada, dano 149 | 5399 / 1130 | 45 / 62 |
| 43 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 5323 / 936 | 75 / 81 |
| 44 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Tremor de Bigorna — executada, dano 503, MP −71 | 4893 / 785 | 105 / 29 |
| 45 | p2 → p1 (score) | Cutelada — executada, dano 420, MP −95 | Ataque básico — executada, dano 0 | 5040 / 365 | 40 / 48 |
| 46 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 149 | 4964 / 171 | 70 / 67 |
| 47 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Quebra-Guarda — executada, dano 0, MP −63 | 4964 / 171 | 100 / 23 |
| 48 | p2 → p1 (score) | Cutelada — executada, dano 0, MP −95 | Ataque básico — executada, dano 149 | 4815 / 188 | 35 / 42 |
| 49 | p2 → p1 (score) | Ataque básico — executada, dano 211 | Ataque básico — executada, dano 238 | 4650 / 5 | 65 / 61 |
| 50 | p2 → p1 (score) | Ataque básico — executada, dano 339 | Ataque básico — executada, dano 149 | 4619 / -317 | 95 / 80 |

### Fase de 32: detalhes

#### Fase de 32 1 — Smzinho × sofiaespanha

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W35 | Smzinho | Guerreiro | 23 | 29.75 | Cutelada, Mira Calma, Veterania, Estocada Seca | controle |
| p2 | W56 | sofiaespanha | Guerreiro | 23 | 29.29 | Soco de Placa, Passo Lateral, Quebra-Guarda, Baluarte | defesa + controle |

- Seed da partida: `7745829876537198877`
- Rodadas: **26**
- Vencedor: **Smzinho** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1519/5701 (26.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Smzinho | sofiaespanha |
|---|---|---|
| Dano causado (golpes + DoT) | 8549 (5759 + 2790) | 4182 (4182 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 556 (0 + 556) |
| MP gasto em ações | 1678 | 1161 |
| Skills / ataques básicos | 18 / 6 | 18 / 6 |
| Acertos / erros | 12 / 2 | 14 / 3 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 6 | 20 |
| Ações perdidas por controle | 2 | 2 |

Efeitos relevantes:
- Smzinho aplicou: stun (rodada 3), vulnerable (rodada 4), bleed (rodada 7), stun (rodada 9), vulnerable (rodada 9), bleed (rodada 13), vulnerable (rodada 15), bleed (rodada 23)
- Smzinho tentou sem sucesso: bleed (rodada 2), fear (rodada 3), stun (rodada 4), fear (rodada 4), stun (rodada 5), fear (rodada 5), stun (rodada 8), fear (rodada 8), fear (rodada 9), stun (rodada 10), fear (rodada 10), stun (rodada 14), fear (rodada 14), stun (rodada 15), fear (rodada 15), bleed (rodada 17), stun (rodada 18), fear (rodada 18), stun (rodada 20), fear (rodada 20), stun (rodada 25), fear (rodada 25), stun (rodada 26), fear (rodada 26)
- Smzinho ativou: Veterania ×5
- sofiaespanha aplicou: weakened (rodada 6), stun (rodada 11), stun (rodada 22), weakened (rodada 22), weakened (rodada 24)
- sofiaespanha tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 6), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), bleed (rodada 11), weakened (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 14), bleed (rodada 14), weakened (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), weakened (rodada 16), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), weakened (rodada 20), bleed (rodada 22), stun (rodada 23), bleed (rodada 23), stun (rodada 24), bleed (rodada 24), stun (rodada 26), bleed (rodada 26), weakened (rodada 26)
- sofiaespanha ativou: Passo Lateral ×7

Rodada a rodada:

| Rodada | Ordem (critério) | Smzinho (p1) | sofiaespanha (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Passo Lateral — executada, dano 0, MP −70 | 5701 / 7757 | 847 / 766 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Soco de Placa — executada, dano 0, MP −61 | 5701 / 7757 | 808 / 725 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 450, MP −85 | Ataque básico — executada, dano 187 | 5514 / 7307 | 754 / 745 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 785, MP −116 | Soco de Placa — cancelada por controle | 5514 / 6522 | 669 / 765 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 272 | Passo Lateral — executada, dano 0, MP −70 | 5514 / 6250 | 700 / 715 |
| 6 | p1 → p2 (score) | Veterania — executada, dano 0, MP −111 | Soco de Placa — executada, dano 340, MP −61 | 5174 / 6297 | 620 / 674 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 187 | 4987 / 6323 | 581 / 694 |
| 8 | p2 → p1 (score) | Cutelada — executada, dano 614, MP −85 | Soco de Placa — executada, dano 0, MP −61 | 4987 / 5399 | 527 / 653 |
| 9 | p2 → p1 (score) | Mira Calma — executada, dano 700, MP −116 | Passo Lateral — executada, dano 0, MP −70 | 4987 / 4389 | 442 / 603 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 272 | Soco de Placa — cancelada por controle | 4987 / 3807 | 473 / 623 |
| 11 | p1 → p2 (score) | Veterania — executada, dano 0, MP −111 | Soco de Placa — executada, dano 340, MP −61 | 4647 / 3854 | 393 / 582 |
| 12 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Ataque básico — executada, dano 187 | 4460 / 3880 | 424 / 602 |
| 13 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Passo Lateral — executada, dano 0, MP −70 | 4460 / 3880 | 385 / 552 |
| 14 | p2 → p1 (score) | Cutelada — executada, dano 614, MP −85 | Soco de Placa — executada, dano 340, MP −61 | 4120 / 3003 | 331 / 511 |
| 15 | p2 → p1 (score) | Mira Calma — executada, dano 700, MP −116 | Ataque básico — executada, dano 187 | 3933 / 2019 | 246 / 531 |
| 16 | p1 → p2 (score) | Veterania — executada, dano 0, MP −111 | Soco de Placa — executada, dano 408, MP −61 | 3525 / 1766 | 166 / 490 |
| 17 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −70 | Passo Lateral — executada, dano 0, MP −70 | 3525 / 1766 | 127 / 440 |
| 18 | p2 → p1 (score) | Cutelada — executada, dano 450, MP −85 | Soco de Placa — executada, dano 0, MP −61 | 3525 / 1316 | 73 / 399 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 187 | 3338 / 1342 | 104 / 419 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 226 | Soco de Placa — executada, dano 408, MP −61 | 2930 / 1173 | 135 / 378 |
| 21 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Passo Lateral — executada, dano 0, MP −70 | 2930 / 1173 | 55 / 328 |
| 22 | p2 → p1 (score) | Ataque básico — cancelada por controle | Soco de Placa — executada, dano 408, MP −61 | 2522 / 1230 | 86 / 287 |
| 23 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 187 | 2335 / 1256 | 47 / 307 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Soco de Placa — executada, dano 408, MP −61 | 1927 / 1003 | 78 / 266 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 226 | Passo Lateral — executada, dano 0, MP −70 | 1927 / 467 | 109 / 216 |
| 26 | p2 → p1 (score) | Cutelada — executada, dano 450, MP −85 | Soco de Placa — executada, dano 408, MP −61 | 1519 / -236 | 55 / 175 |

#### Fase de 32 2 — gafallen × loud_thurzin

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W37 | gafallen | Guerreiro | 20 | 29.87 | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda | sustento |
| p2 | W32 | loud_thurzin | Guerreiro | 22 | 29.87 | Marca do Caçador, Golpe Devastador, Guarda Alta, Grito Curto | crítico + controle |

- Seed da partida: `1365251658866500399`
- Rodadas: **26**
- Vencedor: **gafallen** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1731/3973 (43.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | gafallen | loud_thurzin |
|---|---|---|
| Dano causado (golpes + DoT) | 5206 (4798 + 408) | 5593 (3536 + 2057) |
| Cura (skill + roubo de vida) | 3351 (1332 + 2019) | 91 (0 + 91) |
| MP gasto em ações | 1336 | 1326 |
| Skills / ataques básicos | 19 / 4 | 18 / 6 |
| Acertos / erros | 13 / 2 | 12 / 0 |
| Críticos (dano) | 1 (1271) | 1 (640) |
| Agiu primeiro (rodadas) | 8 | 18 |
| Ações perdidas por controle | 3 | 1 |

Efeitos relevantes:
- gafallen aplicou: vulnerable (rodada 3), vulnerable (rodada 6), bleed (rodada 10), vulnerable (rodada 11), vulnerable (rodada 19), stun (rodada 25)
- gafallen tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 10), vulnerable (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 12), bleed (rodada 12), stun (rodada 16), bleed (rodada 16), vulnerable (rodada 16), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), vulnerable (rodada 20), stun (rodada 21), bleed (rodada 21), bleed (rodada 25), vulnerable (rodada 25), stun (rodada 26), bleed (rodada 26), vulnerable (rodada 26)
- gafallen ativou: Escudo Protetor ×6
- loud_thurzin aplicou: fear (rodada 2), weakened (rodada 2), poison (rodada 4), fear (rodada 6), weakened (rodada 6), poison (rodada 8), fear (rodada 10), stun (rodada 12), fear (rodada 14), stun (rodada 15), bleed (rodada 15), bleed (rodada 16), fear (rodada 18), stun (rodada 24), bleed (rodada 24), poison (rodada 24)
- loud_thurzin tentou sem sucesso: stun (rodada 3), bleed (rodada 3), poison (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 7), bleed (rodada 7), poison (rodada 7), stun (rodada 8), bleed (rodada 8), weakened (rodada 10), stun (rodada 11), bleed (rodada 11), poison (rodada 11), bleed (rodada 12), poison (rodada 12), weakened (rodada 14), poison (rodada 15), stun (rodada 16), poison (rodada 16), weakened (rodada 18), stun (rodada 19), bleed (rodada 19), poison (rodada 19), stun (rodada 20), bleed (rodada 20), poison (rodada 20), fear (rodada 22), stun (rodada 23), bleed (rodada 23), poison (rodada 23)
- loud_thurzin ativou: Guarda Alta ×6

Rodada a rodada:

| Rodada | Ordem (critério) | gafallen (p1) | loud_thurzin (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Guarda Alta — executada, dano 0, MP −57 | 3973 / 5110 | 686 / 906 |
| 2 | p2 → p1 (score) | Mira Calma — executada, dano 0, MP −82 | Grito Curto — executada, dano 0, MP −57 | 3973 / 5110 | 643 / 868 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 241, MP −50 | Golpe Devastador — executada, dano 304, MP −107 | 3777 / 4869 | 632 / 780 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 115 | Ataque básico — executada, dano 174 | 3654 / 4759 | 671 / 799 |
| 5 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Guarda Alta — executada, dano 0, MP −57 | 3595 / 4759 | 633 / 761 |
| 6 | p1 → p2 (score) | Mira Calma — executada, dano 1271, MP −82 | Grito Curto — executada, dano 0, MP −57 | 3973 / 3488 | 590 / 723 |
| 7 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Golpe Devastador — executada, dano 304, MP −107 | 3610 / 3497 | 579 / 635 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 120 | Ataque básico — executada, dano 132 | 3413 / 3380 | 618 / 654 |
| 9 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Guarda Alta — executada, dano 0, MP −57 | 3294 / 3380 | 580 / 616 |
| 10 | p2 → p1 (score) | Mira Calma — executada, dano 469, MP −82 | Grito Curto — executada, dano 0, MP −57 | 3386 / 2911 | 537 / 578 |
| 11 | p2 → p1 (score) | Quebra-Guarda — executada, dano 215, MP −50 | Golpe Devastador — executada, dano 304, MP −107 | 3059 / 2501 | 526 / 490 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 115 | Ataque básico — executada, dano 174 | 2817 / 2187 | 565 / 509 |
| 13 | p2 → p1 (score) | Escudo Protetor — cancelada por controle | Guarda Alta — executada, dano 0, MP −57 | 2817 / 2187 | 604 / 471 |
| 14 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito Curto — executada, dano 0, MP −57 | 2817 / 2187 | 566 / 433 |
| 15 | p2 → p1 (score) | Mira Calma — cancelada por controle | Golpe Devastador — executada, dano 640, MP −107 | 2019 / 2206 | 605 / 345 |
| 16 | p2 → p1 (score) | Mira Calma — executada, dano 565, MP −82 | Ataque básico — executada, dano 132 | 1824 / 1644 | 562 / 364 |
| 17 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Guarda Alta — executada, dano 0, MP −57 | 2173 / 1644 | 535 / 326 |
| 18 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito Curto — executada, dano 0, MP −57 | 2173 / 1644 | 497 / 288 |
| 19 | p2 → p1 (score) | Mira Calma — executada, dano 469, MP −82 | Golpe Devastador — executada, dano 479, MP −107 | 1905 / 1189 | 454 / 200 |
| 20 | p1 → p2 (score) | Quebra-Guarda — executada, dano 250, MP −50 | Ataque básico — executada, dano 132 | 1885 / 942 | 443 / 219 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 144 | Guarda Alta — executada, dano 0, MP −57 | 1949 / 798 | 482 / 181 |
| 22 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Grito Curto — executada, dano 0, MP −57 | 2615 / 798 | 455 / 143 |
| 23 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Golpe Devastador — executada, dano 629, MP −107 | 1986 / 816 | 417 / 55 |
| 24 | p2 → p1 (score) | Mira Calma — cancelada por controle | Ataque básico — executada, dano 132 | 1637 / 819 | 456 / 74 |
| 25 | p1 → p2 (score) | Mira Calma — executada, dano 565, MP −82 | Guarda Alta — cancelada por controle | 1674 / 254 | 413 / 93 |
| 26 | p1 → p2 (score) | Quebra-Guarda — executada, dano 259, MP −50 | Guarda Alta — cancelada por morte | 1731 / -5 | 402 / 93 |

#### Fase de 32 3 — fnxLNTC × yayahuz

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W24 | fnxLNTC | Guerreiro | 22 | 29.52 | Golpe Poderoso, Investida, Couraça Improvisada, Berro de Ferro | defesa + sustento |
| p2 | W07 | yayahuz | Guerreiro | 22 | 27.79 | Golpe Poderoso, Mira Calma, Sede de Batalha, Tomar Fôlego | defesa + sustento |

- Seed da partida: `9762848969340625506`
- Rodadas: **54**
- Vencedor: **fnxLNTC** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 942/5355 (17.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fnxLNTC | yayahuz |
|---|---|---|
| Dano causado (golpes + DoT) | 6582 (6300 + 282) | 5476 (5476 + 0) |
| Cura (skill + roubo de vida) | 1063 (0 + 1063) | 184 (0 + 184) |
| MP gasto em ações | 1901 | 1305 |
| Skills / ataques básicos | 35 / 18 | 23 / 30 |
| Acertos / erros | 27 / 4 | 43 / 10 |
| Críticos (dano) | 3 (1527) | 0 (0) |
| Agiu primeiro (rodadas) | 54 | 0 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- fnxLNTC aplicou: hexed (rodada 2), hexed (rodada 10), fear (rodada 10), hexed (rodada 14), hexed (rodada 22), hexed (rodada 26), hexed (rodada 43), hexed (rodada 49), poison (rodada 51)
- fnxLNTC tentou sem sucesso: fear (rodada 2), stun (rodada 4), poison (rodada 4), stun (rodada 4), hexed (rodada 6), stun (rodada 8), poison (rodada 8), fear (rodada 14), stun (rodada 15), poison (rodada 15), stun (rodada 16), poison (rodada 16), stun (rodada 16), hexed (rodada 18), stun (rodada 19), poison (rodada 19), stun (rodada 20), poison (rodada 20), stun (rodada 20), fear (rodada 22), stun (rodada 23), poison (rodada 23), stun (rodada 24), poison (rodada 24), stun (rodada 24), fear (rodada 26), stun (rodada 27), poison (rodada 27), stun (rodada 28), poison (rodada 28), stun (rodada 28), stun (rodada 29), poison (rodada 29), hexed (rodada 31), stun (rodada 32), poison (rodada 32), stun (rodada 33), poison (rodada 33), stun (rodada 35), poison (rodada 35), stun (rodada 36), poison (rodada 36), hexed (rodada 37), stun (rodada 38), poison (rodada 38), stun (rodada 39), poison (rodada 39), stun (rodada 41), poison (rodada 41), stun (rodada 42), poison (rodada 42), fear (rodada 43), stun (rodada 44), poison (rodada 44), stun (rodada 45), poison (rodada 45), stun (rodada 47), poison (rodada 47), stun (rodada 48), poison (rodada 48), fear (rodada 49), stun (rodada 50), poison (rodada 50), stun (rodada 51), stun (rodada 53), poison (rodada 53), stun (rodada 54), poison (rodada 54)
- fnxLNTC ativou: Couraça Improvisada ×11
- yayahuz aplicou: stun (rodada 6)
- yayahuz tentou sem sucesso: stun (rodada 2), vulnerable (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), vulnerable (rodada 6), stun (rodada 7), stun (rodada 8), stun (rodada 9), stun (rodada 10), vulnerable (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 13), stun (rodada 14), vulnerable (rodada 14), stun (rodada 16), stun (rodada 17), stun (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 24), stun (rodada 25), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 38), stun (rodada 40), stun (rodada 41), stun (rodada 42), stun (rodada 45), stun (rodada 46), stun (rodada 47), stun (rodada 48), stun (rodada 49), stun (rodada 50), stun (rodada 51), stun (rodada 53)

Rodada a rodada:

| Rodada | Ordem (critério) | fnxLNTC (p1) | yayahuz (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 0, MP −47 | 5355 / 6296 | 889 / 627 |
| 2 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mira Calma — executada, dano 231, MP −103 | 5124 / 6296 | 856 / 537 |
| 3 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Golpe Poderoso — executada, dano 200, MP −47 | 4924 / 6296 | 828 / 503 |
| 4 | p1 → p2 (score) | Investida — executada, dano 617, MP −53 | Ataque básico — executada, dano 106 | 4922 / 5683 | 794 / 516 |
| 5 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 134, MP −47 | 4788 / 5688 | 751 / 482 |
| 6 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mira Calma — executada, dano 231, MP −103 | 4557 / 5697 | 718 / 392 |
| 7 | p1 → p2 (score) | Golpe Poderoso — cancelada por controle | Golpe Poderoso — executada, dano 200, MP −47 | 4357 / 5705 | 737 / 358 |
| 8 | p1 → p2 (score) | Golpe Poderoso — executada, dano 294, MP −47 | Ataque básico — executada, dano 106 | 4300 / 5415 | 709 / 371 |
| 9 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 134, MP −47 | 4166 / 5420 | 666 / 337 |
| 10 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mira Calma — executada, dano 201, MP −103 | 3965 / 5428 | 633 / 247 |
| 11 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Golpe Poderoso — executada, dano 185, MP −47 | 3780 / 5435 | 605 / 213 |
| 12 | p1 → p2 (score) | Investida — executada, dano 0, MP −53 | Ataque básico — executada, dano 106 | 3674 / 5439 | 571 / 226 |
| 13 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 124, MP −47 | 3550 / 5443 | 528 / 192 |
| 14 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Mira Calma — executada, dano 201, MP −103 | 3349 / 5451 | 495 / 102 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 294, MP −47 | Golpe Poderoso — executada, dano 0, MP −47 | 3398 / 5157 | 467 / 68 |
| 16 | p1 → p2 (score) | Investida — executada, dano 617, MP −53 | Ataque básico — executada, dano 106 | 3396 / 4544 | 433 / 81 |
| 17 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 124, MP −47 | 3272 / 4548 | 390 / 47 |
| 18 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 0 | 3272 / 4548 | 357 / 60 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 273, MP −47 | Golpe Poderoso — executada, dano 185, MP −47 | 3133 / 4282 | 329 / 26 |
| 20 | p1 → p2 (score) | Investida — executada, dano 274, MP −53 | Ataque básico — executada, dano 106 | 3073 / 4012 | 295 / 39 |
| 21 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 71 | 3002 / 4014 | 252 / 52 |
| 22 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 0, MP −47 | 3002 / 4014 | 219 / 18 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 273, MP −47 | Ataque básico — executada, dano 0 | 3048 / 3741 | 191 / 31 |
| 24 | p1 → p2 (score) | Investida — executada, dano 274, MP −53 | Ataque básico — executada, dano 106 | 2988 / 3471 | 157 / 44 |
| 25 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 71 | 2917 / 3473 | 114 / 57 |
| 26 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 124, MP −47 | 2793 / 3477 | 81 / 23 |
| 27 | p1 → p2 (score) | Golpe Poderoso — executada, dano 273, MP −47 | Ataque básico — executada, dano 104 | 2735 / 3208 | 53 / 36 |
| 28 | p1 → p2 (score) | Investida — executada, dano 274, MP −53 | Ataque básico — executada, dano 106 | 2675 / 2938 | 19 / 49 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Golpe Poderoso — executada, dano 185, MP −47 | 2517 / 2786 | 38 / 15 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 106 | 2411 / 2790 | 57 / 28 |
| 31 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 106 | 2305 / 2794 | 24 / 41 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 106 | 2226 / 2639 | 43 / 54 |
| 33 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Golpe Poderoso — executada, dano 185, MP −47 | 2068 / 2487 | 62 / 20 |
| 34 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 71 | 1997 / 2489 | 19 / 33 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 71 | 1953 / 2332 | 38 / 46 |
| 36 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 106 | 1874 / 2177 | 57 / 59 |
| 37 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 0, MP −47 | 1874 / 2177 | 24 / 25 |
| 38 | p1 → p2 (score) | Ataque básico — executada, dano 293 | Ataque básico — executada, dano 106 | 1817 / 1888 | 43 / 38 |
| 39 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 0 | 1844 / 1729 | 62 / 51 |
| 40 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Golpe Poderoso — executada, dano 124, MP −47 | 1720 / 1733 | 19 / 17 |
| 41 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 71 | 1676 / 1576 | 38 / 30 |
| 42 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 106 | 1597 / 1421 | 57 / 43 |
| 43 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 0 | 1597 / 1421 | 24 / 56 |
| 44 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Golpe Poderoso — executada, dano 0, MP −47 | 1624 / 1262 | 43 / 22 |
| 45 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 106 | 1545 / 1107 | 62 / 35 |
| 46 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 71 | 1474 / 1109 | 19 / 48 |
| 47 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Golpe Poderoso — executada, dano 124, MP −47 | 1377 / 954 | 38 / 14 |
| 48 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 106 | 1298 / 799 | 57 / 27 |
| 49 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 104 | 1194 / 803 | 24 / 40 |
| 50 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 104 | 1117 / 648 | 43 / 53 |
| 51 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Golpe Poderoso — executada, dano 185, MP −47 | 959 / 402 | 62 / 19 |
| 52 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 0 | 959 / 308 | 19 / 32 |
| 53 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 71 | 915 / 57 | 38 / 45 |
| 54 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Ataque básico — cancelada por morte | 942 / -102 | 57 / 45 |

#### Fase de 32 4 — JonVlogs × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W58 | JonVlogs | Guerreiro | 22 | 28.60 | Golpe Poderoso, Investida, Guarda Alta, Couraça Improvisada | defesa + sustento |
| p2 | W34 | LuquEt4 | Guerreiro | 23 | 29.87 | Golpe Duplo, Grito de Guerra, Cutelada, Areia no Chão | crítico |

- Seed da partida: `9583618915835800529`
- Rodadas: **36**
- Vencedor: **LuquEt4** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3148/7257 (43.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | JonVlogs | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 4109 (4109 + 0) | 7277 (7277 + 0) |
| Cura (skill + roubo de vida) | 931 (0 + 931) | 0 (0 + 0) |
| MP gasto em ações | 1401 | 1262 |
| Skills / ataques básicos | 26 / 9 | 15 / 20 |
| Acertos / erros | 21 / 1 | 23 / 1 |
| Críticos (dano) | 0 (0) | 9 (4270) |
| Agiu primeiro (rodadas) | 10 | 26 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- JonVlogs aplicou: stun (rodada 16)
- JonVlogs tentou sem sucesso: stun (rodada 4), stun (rodada 4), stun (rodada 7), stun (rodada 8), stun (rodada 8), stun (rodada 11), stun (rodada 12), stun (rodada 12), stun (rodada 15), stun (rodada 16), stun (rodada 19), stun (rodada 20), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 30), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 35)
- JonVlogs ativou: Guarda Alta ×8, Couraça Improvisada ×5
- LuquEt4 aplicou: slowed (rodada 2), slowed (rodada 6), vulnerable (rodada 6), slowed (rodada 17), vulnerable (rodada 17), slowed (rodada 26), vulnerable (rodada 26), slowed (rodada 30), slowed (rodada 35), vulnerable (rodada 35)
- LuquEt4 tentou sem sucesso: vulnerable (rodada 2), stun (rodada 3), frailty (rodada 3), stun (rodada 4), stun (rodada 7), frailty (rodada 7), stun (rodada 8), stun (rodada 11), slowed (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 18), stun (rodada 19), stun (rodada 20), slowed (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 27), stun (rodada 28), stun (rodada 29), vulnerable (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 36)
- LuquEt4 ativou: Grito de Guerra ×3

Rodada a rodada:

| Rodada | Ordem (critério) | JonVlogs (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Grito de Guerra — executada, dano 0, MP −100 | 6314 / 7257 | 651 / 673 |
| 2 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Areia no Chão — executada, dano 0, MP −70 | 6314 / 7257 | 610 / 618 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Golpe Duplo — executada, dano 511, MP −116 | 5803 / 7257 | 584 / 517 |
| 4 | p2 → p1 (score) | Investida — executada, dano 275, MP −53 | Cutelada — executada, dano 325, MP −85 | 5541 / 6982 | 552 / 447 |
| 5 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Grito de Guerra — executada, dano 0, MP −100 | 5541 / 6982 | 516 / 362 |
| 6 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Areia no Chão — executada, dano 0, MP −70 | 5541 / 6982 | 475 / 307 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 243, MP −47 | Golpe Duplo — executada, dano 1125, MP −116 | 4471 / 6739 | 449 / 206 |
| 8 | p2 → p1 (score) | Investida — executada, dano 275, MP −53 | Cutelada — executada, dano 717, MP −85 | 3817 / 6464 | 417 / 136 |
| 9 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Grito de Guerra — executada, dano 0, MP −100 | 3817 / 6464 | 381 / 51 |
| 10 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 0 | 3817 / 6464 | 340 / 66 |
| 11 | p2 → p1 (score) | Golpe Poderoso — executada, dano 243, MP −47 | Ataque básico — executada, dano 160 | 3712 / 6221 | 314 / 81 |
| 12 | p2 → p1 (score) | Investida — executada, dano 275, MP −53 | Areia no Chão — executada, dano 0, MP −70 | 3775 / 5946 | 282 / 26 |
| 13 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Ataque básico — executada, dano 379 | 3396 / 5946 | 246 / 41 |
| 14 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 124 | 3272 / 5946 | 205 / 56 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 243, MP −47 | Ataque básico — executada, dano 124 | 3203 / 5703 | 179 / 71 |
| 16 | p1 → p2 (score) | Investida — executada, dano 228, MP −53 | Areia no Chão — cancelada por controle | 3255 / 5475 | 147 / 86 |
| 17 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Areia no Chão — executada, dano 0, MP −70 | 3255 / 5475 | 111 / 31 |
| 18 | p2 → p1 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 199 | 3056 / 5475 | 70 / 46 |
| 19 | p2 → p1 (score) | Golpe Poderoso — executada, dano 226, MP −47 | Ataque básico — executada, dano 284 | 2823 / 5249 | 44 / 61 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 199 | 2654 / 5116 | 65 / 76 |
| 21 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Areia no Chão — executada, dano 0, MP −70 | 2654 / 5116 | 29 / 21 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 314 | 2370 / 4983 | 50 / 36 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 226, MP −47 | Ataque básico — executada, dano 165 | 2256 / 4757 | 24 / 51 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 199 | 2087 / 4624 | 45 / 66 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 199 | 1918 / 4491 | 66 / 81 |
| 26 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Areia no Chão — executada, dano 0, MP −70 | 1918 / 4491 | 30 / 26 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 199 | 1749 / 4358 | 51 / 41 |
| 28 | p2 → p1 (score) | Golpe Poderoso — executada, dano 226, MP −47 | Ataque básico — executada, dano 379 | 1421 / 4132 | 25 / 56 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 199 | 1252 / 3999 | 46 / 71 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 133 | Areia no Chão — executada, dano 0, MP −70 | 1282 / 3866 | 67 / 16 |
| 31 | p2 → p1 (score) | Guarda Alta — executada, dano 0, MP −57 | Ataque básico — executada, dano 379 | 903 / 3866 | 31 / 31 |
| 32 | p2 → p1 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 165 | 768 / 3733 | 52 / 46 |
| 33 | p1 → p2 (score) | Golpe Poderoso — executada, dano 226, MP −47 | Ataque básico — executada, dano 314 | 505 / 3507 | 26 / 61 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 133 | Ataque básico — executada, dano 379 | 156 / 3374 | 47 / 76 |
| 35 | p2 → p1 (score) | Golpe Poderoso — executada, dano 226, MP −47 | Areia no Chão — executada, dano 0, MP −70 | 207 / 3148 | 21 / 21 |
| 36 | p2 → p1 (score) | Ataque básico — cancelada por morte | Ataque básico — executada, dano 239 | -32 / 3148 | 21 / 36 |

#### Fase de 32 5 — tioorochitwitch × MeikodRJ

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W63 | tioorochitwitch | Guerreiro | 23 | 29.41 | Golpe Poderoso, Investida, Postura de Muro, Baluarte | defesa + sustento |
| p2 | W26 | MeikodRJ | Guerreiro | 22 | 29.75 | Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno | sustento |

- Seed da partida: `4874100928450260687`
- Rodadas: **25**
- Vencedor: **MeikodRJ** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1085/4969 (21.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | tioorochitwitch | MeikodRJ |
|---|---|---|
| Dano causado (golpes + DoT) | 7342 (7342 + 0) | 8572 (6848 + 1724) |
| Cura (skill + roubo de vida) | 1292 (0 + 1292) | 3458 (2026 + 1432) |
| MP gasto em ações | 1332 | 1151 |
| Skills / ataques básicos | 24 / 0 | 17 / 5 |
| Acertos / erros | 22 / 2 | 18 / 2 |
| Críticos (dano) | 2 (998) | 3 (1410) |
| Agiu primeiro (rodadas) | 23 | 2 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- tioorochitwitch aplicou: stun (rodada 12), stun (rodada 16), fear (rodada 20)
- tioorochitwitch tentou sem sucesso: stun (rodada 1), fear (rodada 1), stun (rodada 2), fear (rodada 2), stun (rodada 2), stun (rodada 4), fear (rodada 4), stun (rodada 4), stun (rodada 5), fear (rodada 5), stun (rodada 6), fear (rodada 6), stun (rodada 6), stun (rodada 7), fear (rodada 7), stun (rodada 8), fear (rodada 8), stun (rodada 8), stun (rodada 9), fear (rodada 9), stun (rodada 10), fear (rodada 10), stun (rodada 10), stun (rodada 11), fear (rodada 11), fear (rodada 12), stun (rodada 12), stun (rodada 13), fear (rodada 13), stun (rodada 14), fear (rodada 14), stun (rodada 14), stun (rodada 15), fear (rodada 15), stun (rodada 16), fear (rodada 16), stun (rodada 17), fear (rodada 17), stun (rodada 18), fear (rodada 18), stun (rodada 18), stun (rodada 20), stun (rodada 20), stun (rodada 21), fear (rodada 21), stun (rodada 22), fear (rodada 22), stun (rodada 22), stun (rodada 23), fear (rodada 23), stun (rodada 24), fear (rodada 24), stun (rodada 24)
- Leis disparadas por tioorochitwitch: FERIDA ABERTA (rodada 22)
- MeikodRJ aplicou: vulnerable (rodada 20), bleed (rodada 22), bleed (rodada 23)
- MeikodRJ tentou sem sucesso: stun (rodada 1), bleed (rodada 1), stun (rodada 2), bleed (rodada 2), vulnerable (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), vulnerable (rodada 6), stun (rodada 7), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), vulnerable (rodada 10), stun (rodada 11), bleed (rodada 11), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), vulnerable (rodada 15), stun (rodada 20), bleed (rodada 20), stun (rodada 21), bleed (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), bleed (rodada 24)

Rodada a rodada:

| Rodada | Ordem (critério) | tioorochitwitch (p1) | MeikodRJ (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Golpe Poderoso — executada, dano 499, MP −52 | Golpe Poderoso — executada, dano 321, MP −47 | 6868 / 4537 | 684 / 782 |
| 2 | p1 → p2 (score) | Investida — executada, dano 380, MP −59 | Mira Calma — executada, dano 668, MP −103 | 6272 / 4297 | 655 / 695 |
| 3 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 482, MP −47 | 5790 / 4398 | 633 / 664 |
| 4 | p1 → p2 (score) | Investida — executada, dano 380, MP −59 | Ataque básico — executada, dano 173 | 5689 / 4054 | 604 / 680 |
| 5 | p1 → p2 (score) | Golpe Poderoso — executada, dano 499, MP −52 | Golpe Poderoso — executada, dano 482, MP −47 | 5301 / 3656 | 582 / 649 |
| 6 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Mira Calma — executada, dano 581, MP −103 | 4779 / 3466 | 553 / 562 |
| 7 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Golpe Poderoso — executada, dano 297, MP −47 | 4540 / 3220 | 531 / 531 |
| 8 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Ataque básico — executada, dano 173 | 4426 / 2944 | 502 / 547 |
| 9 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Golpe Poderoso — executada, dano 297, MP −47 | 4187 / 2698 | 480 / 516 |
| 10 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Mira Calma — executada, dano 581, MP −103 | 3665 / 2508 | 451 / 429 |
| 11 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Golpe Poderoso — executada, dano 297, MP −47 | 3426 / 2262 | 429 / 398 |
| 12 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Tomar Fôlego — cancelada por controle | 3485 / 1950 | 400 / 414 |
| 13 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Tomar Fôlego — executada, dano 0, MP −83 | 3543 / 2655 | 378 / 347 |
| 14 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Golpe Poderoso — executada, dano 297, MP −47 | 3305 / 2405 | 349 / 316 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Mira Calma — executada, dano 581, MP −103 | 2782 / 2219 | 327 / 229 |
| 16 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Golpe Poderoso — cancelada por controle | 2841 / 1907 | 298 / 245 |
| 17 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Golpe Poderoso — executada, dano 0, MP −47 | 2899 / 1599 | 276 / 214 |
| 18 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Tomar Fôlego — executada, dano 0, MP −83 | 2958 / 2300 | 247 / 147 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 0, MP −47 | 2958 / 2300 | 225 / 116 |
| 20 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Mira Calma — executada, dano 581, MP −103 | 2436 / 2110 | 196 / 29 |
| 21 | p2 → p1 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Ataque básico — executada, dano 209 | 2285 / 1845 | 174 / 45 |
| 22 | p2 → p1 (score) | Investida — executada, dano 312, MP −59 | Ataque básico — executada, dano 209 | 1560 / 1576 | 145 / 61 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 308, MP −52 | Golpe Poderoso — executada, dano 446, MP −47 | 597 / 1361 | 123 / 30 |
| 24 | p1 → p2 (score) | Investida — executada, dano 312, MP −59 | Ataque básico — executada, dano 173 | 196 / 1085 | 94 / 46 |
| 25 | p1 → p2 (score) | Golpe Poderoso — cancelada por morte | Ataque básico — não alcançada (o duelo acabou antes) | -91 / 1085 | 124 / 46 |

#### Fase de 32 6 — Bisteconee × DavyJones

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W49 | Bisteconee | Guerreiro | 22 | 28.60 | Cutelada, Mira Calma, Areia no Chão, Leitura de Terreno | controle |
| p2 | W29 | DavyJones | Guerreiro | 22 | 29.98 | Golpe Poderoso, Mira Calma, Paciência do Coveiro, Respirar Fundo | defesa + sustento |

- Seed da partida: `15408156701190931824`
- Rodadas: **10**
- Vencedor: **DavyJones** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 3618/5333 (67.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Bisteconee | DavyJones |
|---|---|---|
| Dano causado (golpes + DoT) | 2415 (2415 + 0) | 5039 (4626 + 413) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 700 (0 + 700) |
| MP gasto em ações | 544 | 691 |
| Skills / ataques básicos | 7 / 2 | 9 / 1 |
| Acertos / erros | 6 / 0 | 7 / 1 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 3 | 7 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- Bisteconee aplicou: vulnerable (rodada 3), slowed (rodada 5), vulnerable (rodada 5), vulnerable (rodada 7), slowed (rodada 9)
- Bisteconee tentou sem sucesso: slowed (rodada 1), stun (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), vulnerable (rodada 9)
- DavyJones aplicou: poison (rodada 1), frailty (rodada 1), poison (rodada 7), frailty (rodada 7), stun (rodada 10)
- DavyJones tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 3), vulnerable (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), vulnerable (rodada 9), bleed (rodada 10)

Rodada a rodada:

| Rodada | Ordem (critério) | Bisteconee (p1) | DavyJones (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −62 | Paciência do Coveiro — executada, dano 0, MP −125 | 4722 / 5333 | 767 / 704 |
| 2 | p2 → p1 (score) | Cutelada — executada, dano 356, MP −76 | Golpe Poderoso — executada, dano 502, MP −47 | 4163 / 4977 | 707 / 677 |
| 3 | p2 → p1 (score) | Mira Calma — executada, dano 516, MP −103 | Mira Calma — executada, dano 1211, MP −103 | 2895 / 4666 | 620 / 594 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 220 | Golpe Poderoso — executada, dano 465, MP −47 | 2373 / 4525 | 636 / 567 |
| 5 | p1 → p2 (score) | Areia no Chão — executada, dano 0, MP −62 | Ataque básico — executada, dano 0 | 2302 / 4525 | 590 / 587 |
| 6 | p1 → p2 (score) | Cutelada — executada, dano 586, MP −76 | Golpe Poderoso — executada, dano 465, MP −47 | 1837 / 4018 | 530 / 560 |
| 7 | p1 → p2 (score) | Mira Calma — executada, dano 555, MP −103 | Paciência do Coveiro — executada, dano 0, MP −125 | 1837 / 3463 | 443 / 455 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 182 | Golpe Poderoso — executada, dano 465, MP −47 | 1315 / 3360 | 459 / 428 |
| 9 | p2 → p1 (score) | Areia no Chão — executada, dano 0, MP −62 | Mira Calma — executada, dano 1053, MP −103 | 205 / 3539 | 413 / 345 |
| 10 | p2 → p1 (score) | Cutelada — cancelada por morte | Golpe Poderoso — executada, dano 465, MP −47 | -260 / 3618 | 413 / 318 |

#### Fase de 32 7 — SkipNhO × lubatv

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W52 | SkipNhO | Guerreiro | 23 | 28.02 | Golpe Poderoso, Postura de Muro, Pisada de Ferro, Juramento da Muralha | defesa + sustento |
| p2 | W23 | lubatv | Guerreiro | 22 | 29.17 | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | crítico + sustento |

- Seed da partida: `7325394041001865093`
- Rodadas: **33**
- Vencedor: **lubatv** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2005/5275 (38.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | SkipNhO | lubatv |
|---|---|---|
| Dano causado (golpes + DoT) | 3270 (3270 + 0) | 8376 (8376 + 0) |
| Cura (skill + roubo de vida) | 649 (0 + 649) | 0 (0 + 0) |
| MP gasto em ações | 1780 | 1455 |
| Skills / ataques básicos | 25 / 7 | 16 / 17 |
| Acertos / erros | 16 / 12 | 26 / 4 |
| Críticos (dano) | 1 (193) | 10 (4463) |
| Agiu primeiro (rodadas) | 4 | 29 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- SkipNhO aplicou: slowed (rodada 15), slowed (rodada 27)
- SkipNhO tentou sem sucesso: slowed (rodada 3)
- SkipNhO ativou: Juramento da Muralha ×4
- lubatv aplicou: vulnerable (rodada 6), vulnerable (rodada 9), vulnerable (rodada 15), vulnerable (rodada 19), vulnerable (rodada 22)
- lubatv tentou sem sucesso: stun (rodada 2), stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), vulnerable (rodada 12), stun (rodada 14), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 26), vulnerable (rodada 26), stun (rodada 30), stun (rodada 32), stun (rodada 33), vulnerable (rodada 33)
- lubatv ativou: Postura Impecável ×3

Rodada a rodada:

| Rodada | Ordem (critério) | SkipNhO (p1) | lubatv (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Postura Impecável — executada, dano 0, MP −131 | 7167 / 5275 | 614 / 777 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 240, MP −52 | Esmagar — executada, dano 381, MP −144 | 6834 / 5035 | 597 / 651 |
| 3 | p2 → p1 (score) | Pisada de Ferro — executada, dano 245, MP −68 | Quebra-Guarda — executada, dano 592, MP −63 | 6291 / 4790 | 564 / 606 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 240, MP −52 | Ataque básico — executada, dano 154 | 6185 / 4550 | 547 / 624 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 128 | Ataque básico — executada, dano 156 | 6054 / 4422 | 582 / 642 |
| 6 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Quebra-Guarda — executada, dano 463, MP −63 | 5591 / 4422 | 565 / 597 |
| 7 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Postura Impecável — executada, dano 0, MP −131 | 5591 / 4422 | 448 / 484 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Esmagar — executada, dano 455, MP −144 | 5136 / 4422 | 431 / 358 |
| 9 | p2 → p1 (score) | Pisada de Ferro — executada, dano 0, MP −68 | Quebra-Guarda — executada, dano 352, MP −63 | 4784 / 4422 | 398 / 313 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 240, MP −52 | Ataque básico — executada, dano 184 | 4648 / 4182 | 381 / 331 |
| 11 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 124 | 4524 / 4182 | 416 / 349 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Quebra-Guarda — executada, dano 620, MP −63 | 3904 / 4182 | 399 / 304 |
| 13 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Postura Impecável — executada, dano 0, MP −131 | 3904 / 4182 | 282 / 191 |
| 14 | p2 → p1 (score) | Golpe Poderoso — executada, dano 222, MP −52 | Esmagar — executada, dano 572, MP −144 | 3376 / 3960 | 265 / 65 |
| 15 | p2 → p1 (score) | Pisada de Ferro — executada, dano 245, MP −68 | Quebra-Guarda — executada, dano 528, MP −63 | 2897 / 3715 | 232 / 20 |
| 16 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 184 | 2713 / 3715 | 215 / 38 |
| 17 | p2 → p1 (score) | Ataque básico — executada, dano 128 | Ataque básico — executada, dano 124 | 2614 / 3587 | 250 / 56 |
| 18 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 284 | 2330 / 3587 | 233 / 74 |
| 19 | p2 → p1 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Quebra-Guarda — executada, dano 620, MP −63 | 1710 / 3587 | 116 / 29 |
| 20 | p2 → p1 (score) | Golpe Poderoso — executada, dano 222, MP −52 | Ataque básico — executada, dano 124 | 1630 / 3365 | 99 / 47 |
| 21 | p2 → p1 (score) | Pisada de Ferro — executada, dano 0, MP −68 | Ataque básico — executada, dano 187 | 1443 / 3365 | 66 / 65 |
| 22 | p2 → p1 (score) | Golpe Poderoso — executada, dano 222, MP −52 | Quebra-Guarda — executada, dano 227, MP −63 | 1260 / 3143 | 49 / 20 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 128 | Ataque básico — executada, dano 124 | 1161 / 3015 | 84 / 38 |
| 24 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 226 | 935 / 3015 | 67 / 56 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 193 | Ataque básico — executada, dano 284 | 689 / 2822 | 102 / 74 |
| 26 | p2 → p1 (score) | Golpe Poderoso — executada, dano 222, MP −52 | Quebra-Guarda — executada, dano 413, MP −63 | 320 / 2600 | 85 / 29 |
| 27 | p2 → p1 (score) | Pisada de Ferro — executada, dano 245, MP −68 | Ataque básico — executada, dano 0 | 369 / 2355 | 52 / 47 |
| 28 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 0 | 369 / 2355 | 35 / 65 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Quebra-Guarda — executada, dano 0, MP −63 | 369 / 2355 | 70 / 20 |
| 30 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Ataque básico — executada, dano 189 | 180 / 2355 | 53 / 38 |
| 31 | p2 → p1 (score) | Ataque básico — executada, dano 128 | Ataque básico — executada, dano 0 | 205 / 2227 | 88 / 56 |
| 32 | p2 → p1 (score) | Golpe Poderoso — executada, dano 222, MP −52 | Ataque básico — executada, dano 189 | 60 / 2005 | 71 / 74 |
| 33 | p2 → p1 (score) | Pisada de Ferro — cancelada por morte | Quebra-Guarda — executada, dano 620, MP −63 | -560 / 2005 | 71 / 29 |

#### Fase de 32 8 — babi × aXtLOL

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W53 | babi | Guerreiro | 24 | 28.48 | Rasgo de Gancho, Postura de Muro, Sangue nos Olhos, Marca do Açougueiro | sustento |
| p2 | W43 | aXtLOL | Guerreiro | 23 | 29.75 | Travar o Pulso, Mira Calma, Ferro Contra Ferro, Ritmo de Duelo | sustento |

- Seed da partida: `12181601168899415817`
- Rodadas: **34**
- Vencedor: **aXtLOL** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2006/5454 (36.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | babi | aXtLOL |
|---|---|---|
| Dano causado (golpes + DoT) | 3714 (3714 + 0) | 7321 (6829 + 492) |
| Cura (skill + roubo de vida) | 984 (0 + 984) | 266 (0 + 266) |
| MP gasto em ações | 702 | 2120 |
| Skills / ataques básicos | 9 / 24 | 23 / 10 |
| Acertos / erros | 22 / 2 | 19 / 1 |
| Críticos (dano) | 6 (1398) | 3 (795) |
| Agiu primeiro (rodadas) | 17 | 17 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- babi aplicou: vulnerable (rodada 13), vulnerable (rodada 17), vulnerable (rodada 21), vulnerable (rodada 29), vulnerable (rodada 33)
- babi tentou sem sucesso: vulnerable (rodada 1), vulnerable (rodada 5), vulnerable (rodada 9), bleed (rodada 13), bleed (rodada 17), bleed (rodada 21), vulnerable (rodada 25), bleed (rodada 29), bleed (rodada 33)
- aXtLOL aplicou: weakened (rodada 2), slowed (rodada 2), vulnerable (rodada 3), weakened (rodada 7), vulnerable (rodada 8), weakened (rodada 9), weakened (rodada 12), slowed (rodada 12), vulnerable (rodada 13), weakened (rodada 14), weakened (rodada 17), slowed (rodada 17), weakened (rodada 22), weakened (rodada 26), slowed (rodada 26), weakened (rodada 30), weakened (rodada 31), bleed (rodada 32)
- aXtLOL tentou sem sucesso: bleed (rodada 3), bleed (rodada 4), weakened (rodada 4), bleed (rodada 5), slowed (rodada 7), bleed (rodada 8), bleed (rodada 9), bleed (rodada 10), bleed (rodada 13), bleed (rodada 14), bleed (rodada 18), vulnerable (rodada 18), bleed (rodada 19), weakened (rodada 19), bleed (rodada 20), slowed (rodada 22), bleed (rodada 23), bleed (rodada 24), vulnerable (rodada 24), bleed (rodada 25), bleed (rodada 27), bleed (rodada 29), slowed (rodada 30), bleed (rodada 31), bleed (rodada 33)
- aXtLOL ativou: Ritmo de Duelo ×6

Rodada a rodada:

| Rodada | Ordem (critério) | babi (p1) | aXtLOL (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ritmo de Duelo — executada, dano 0, MP −105 | 6153 / 5454 | 1130 / 661 |
| 2 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Travar o Pulso — executada, dano 0, MP −70 | 6153 / 5301 | 1158 / 638 |
| 3 | p2 → p1 (score) | Ataque básico — executada, dano 204 | Mira Calma — executada, dano 653, MP −116 | 5557 / 5123 | 1186 / 569 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 204 | Ferro Contra Ferro — executada, dano 468, MP −84 | 5146 / 4937 | 1208 / 532 |
| 5 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 265 | 4881 / 4947 | 1130 / 579 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ritmo de Duelo — executada, dano 0, MP −105 | 4881 / 4947 | 1158 / 521 |
| 7 | p1 → p2 (score) | Ataque básico — executada, dano 245 | Travar o Pulso — executada, dano 0, MP −70 | 4949 / 4702 | 1186 / 498 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Mira Calma — executada, dano 653, MP −116 | 4331 / 4601 | 1208 / 429 |
| 9 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ferro Contra Ferro — executada, dano 468, MP −84 | 3863 / 4619 | 1130 / 392 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 265 | 3633 / 4502 | 1158 / 439 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Ritmo de Duelo — executada, dano 0, MP −105 | 3675 / 4349 | 1186 / 381 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Travar o Pulso — executada, dano 0, MP −70 | 3717 / 4196 | 1208 / 358 |
| 13 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Mira Calma — executada, dano 567, MP −116 | 3150 / 4218 | 1130 / 289 |
| 14 | p2 → p1 (score) | Ataque básico — executada, dano 121 | Ferro Contra Ferro — executada, dano 416, MP −84 | 2767 / 4113 | 1158 / 252 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 2767 / 4113 | 1186 / 299 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 184 | Ritmo de Duelo — executada, dano 0, MP −105 | 2818 / 3929 | 1208 / 241 |
| 17 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Travar o Pulso — executada, dano 0, MP −70 | 2818 / 3929 | 1130 / 218 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 245 | Mira Calma — executada, dano 454, MP −116 | 2432 / 3702 | 1158 / 149 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 204 | Ferro Contra Ferro — executada, dano 388, MP −84 | 2101 / 3513 | 1186 / 112 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 153 | Ataque básico — executada, dano 176 | 1967 / 3367 | 1208 / 159 |
| 21 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ritmo de Duelo — executada, dano 0, MP −105 | 1967 / 3367 | 1130 / 101 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 184 | Travar o Pulso — executada, dano 0, MP −70 | 2018 / 3183 | 1158 / 78 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Ataque básico — executada, dano 176 | 1884 / 3037 | 1186 / 125 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Mira Calma — executada, dano 567, MP −116 | 1352 / 2932 | 1208 / 56 |
| 25 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 265 | 1087 / 2942 | 1130 / 103 |
| 26 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Travar o Pulso — executada, dano 0, MP −70 | 1129 / 2789 | 1158 / 80 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 176 | 988 / 2669 | 1186 / 127 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ritmo de Duelo — executada, dano 0, MP −105 | 1023 / 2542 | 1208 / 69 |
| 29 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 176 | 847 / 2549 | 1130 / 116 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 296 | Travar o Pulso — executada, dano 0, MP −70 | 929 / 2253 | 1158 / 93 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Ferro Contra Ferro — executada, dano 344, MP −84 | 627 / 2113 | 1186 / 56 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 121 | Ataque básico — executada, dano 176 | 484 / 1999 | 1208 / 103 |
| 33 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 176 | 62 / 2006 | 1130 / 150 |
| 34 | p1 → p2 (score) | Ataque básico — cancelada por morte | Ritmo de Duelo — não alcançada (o duelo acabou antes) | -184 / 2006 | 1158 / 150 |

#### Fase de 32 9 — frttt × bakzera

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W60 | frttt | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca | sustento |
| p2 | W30 | bakzera | Guerreiro | 23 | 29.98 | Golpe Duplo, Mira Calma, Provocação, Veterania | crítico + controle |

- Seed da partida: `11442713055583528856`
- Rodadas: **24**
- Vencedor: **frttt** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1218/5379 (22.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | bakzera |
|---|---|---|
| Dano causado (golpes + DoT) | 6429 (3855 + 2574) | 4773 (4773 + 0) |
| Cura (skill + roubo de vida) | 612 (0 + 612) | 0 (0 + 0) |
| MP gasto em ações | 1790 | 1410 |
| Skills / ataques básicos | 20 / 4 | 15 / 9 |
| Acertos / erros | 9 / 5 | 12 / 2 |
| Críticos (dano) | 3 (912) | 1 (1042) |
| Agiu primeiro (rodadas) | 0 | 24 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- frttt aplicou: bleed (rodada 2), bleed (rodada 7), vulnerable (rodada 9), bleed (rodada 17), vulnerable (rodada 19), bleed (rodada 22), vulnerable (rodada 24)
- frttt tentou sem sucesso: stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), bleed (rodada 12), stun (rodada 15), bleed (rodada 15), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 24), bleed (rodada 24)
- frttt ativou: Pausa Útil ×5
- bakzera aplicou: weakened (rodada 2), vulnerable (rodada 4), weakened (rodada 5), frailty (rodada 7), weakened (rodada 8), fear (rodada 13), fear (rodada 14), weakened (rodada 18), weakened (rodada 22)
- bakzera tentou sem sucesso: stun (rodada 4), bleed (rodada 4), poison (rodada 4), fear (rodada 4), stun (rodada 7), bleed (rodada 7), poison (rodada 7), fear (rodada 7), stun (rodada 9), bleed (rodada 9), poison (rodada 9), fear (rodada 9), vulnerable (rodada 9), stun (rodada 10), bleed (rodada 10), poison (rodada 10), fear (rodada 10), weakened (rodada 12), stun (rodada 13), bleed (rodada 13), poison (rodada 13), frailty (rodada 13), stun (rodada 14), bleed (rodada 14), poison (rodada 14), weakened (rodada 15), stun (rodada 16), bleed (rodada 16), poison (rodada 16), fear (rodada 16), stun (rodada 17), bleed (rodada 17), poison (rodada 17), fear (rodada 17), stun (rodada 19), bleed (rodada 19), poison (rodada 19), fear (rodada 19), stun (rodada 21), bleed (rodada 21), poison (rodada 21), fear (rodada 21), stun (rodada 23), bleed (rodada 23), poison (rodada 23), fear (rodada 23), stun (rodada 24), bleed (rodada 24), poison (rodada 24), fear (rodada 24)
- bakzera ativou: Veterania ×3

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | bakzera (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 5379 / 5860 | 990 / 909 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Provocação — executada, dano 0, MP −71 | 5379 / 5860 | 962 / 858 |
| 3 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Golpe Duplo — executada, dano 0, MP −116 | 5379 / 5626 | 884 / 762 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 557, MP −116 | Mira Calma — executada, dano 777, MP −116 | 4691 / 4835 | 810 / 666 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 249 | Provocação — executada, dano 0, MP −71 | 4730 / 4352 | 852 / 615 |
| 6 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 4730 / 4352 | 828 / 524 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Golpe Duplo — executada, dano 1042, MP −116 | 3688 / 4352 | 800 / 428 |
| 8 | p2 → p1 (score) | Golpe Devastador — executada, dano 345, MP −120 | Provocação — executada, dano 0, MP −71 | 3743 / 3773 | 722 / 377 |
| 9 | p2 → p1 (score) | Mira Calma — executada, dano 605, MP −116 | Mira Calma — executada, dano 777, MP −116 | 3062 / 2934 | 648 / 281 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 362 | Ataque básico — executada, dano 214 | 2905 / 2338 | 690 / 301 |
| 11 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 2905 / 2338 | 666 / 210 |
| 12 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Provocação — executada, dano 0, MP −71 | 2905 / 2338 | 638 / 159 |
| 13 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Golpe Duplo — executada, dano 465, MP −116 | 2440 / 2338 | 560 / 63 |
| 14 | p2 → p1 (score) | Mira Calma — executada, dano 0, MP −116 | Ataque básico — executada, dano 214 | 2226 / 2338 | 486 / 83 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 301 | Provocação — executada, dano 0, MP −71 | 2274 / 2037 | 528 / 32 |
| 16 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Ataque básico — executada, dano 214 | 2060 / 2037 | 504 / 52 |
| 17 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 214 | 1846 / 2037 | 476 / 72 |
| 18 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Provocação — executada, dano 0, MP −71 | 1846 / 1803 | 398 / 21 |
| 19 | p2 → p1 (score) | Mira Calma — executada, dano 605, MP −116 | Ataque básico — executada, dano 214 | 1728 / 964 | 324 / 41 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 226 | Ataque básico — executada, dano 0 | 1764 / 504 | 366 / 61 |
| 21 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Ataque básico — executada, dano 214 | 1550 / 504 | 342 / 81 |
| 22 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Provocação — executada, dano 0, MP −71 | 1550 / 504 | 314 / 30 |
| 23 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Ataque básico — executada, dano 214 | 1336 / 270 | 236 / 50 |
| 24 | p2 → p1 (score) | Mira Calma — executada, dano 605, MP −116 | Ataque básico — executada, dano 214 | 1218 / -569 | 162 / 70 |

#### Fase de 32 10 — NOBRU × Neskwga

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W40 | NOBRU | Guerreiro | 23 | 29.75 | Cutelada, Investida, Postura de Muro, Imortal | sustento |
| p2 | W38 | Neskwga | Guerreiro | 22 | 29.41 | Golpe Poderoso, Mira Calma, Escudo Protetor, Baluarte | defesa + sustento |

- Seed da partida: `7082001218792862799`
- Rodadas: **31**
- Vencedor: **NOBRU** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 665/5469 (12.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | NOBRU | Neskwga |
|---|---|---|
| Dano causado (golpes + DoT) | 7131 (5393 + 1738) | 6220 (4990 + 1230) |
| Cura (skill + roubo de vida) | 1416 (0 + 1416) | 689 (0 + 689) |
| MP gasto em ações | 1707 | 1117 |
| Skills / ataques básicos | 20 / 11 | 17 / 12 |
| Acertos / erros | 20 / 4 | 19 / 7 |
| Críticos (dano) | 0 (0) | 6 (1783) |
| Agiu primeiro (rodadas) | 8 | 23 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- NOBRU aplicou: stun (rodada 4), bleed (rodada 25), bleed (rodada 27), bleed (rodada 29)
- NOBRU tentou sem sucesso: bleed (rodada 3), bleed (rodada 4), bleed (rodada 6), bleed (rodada 10), bleed (rodada 12), bleed (rodada 14), bleed (rodada 16), bleed (rodada 17), bleed (rodada 18), stun (rodada 18), bleed (rodada 19), bleed (rodada 20), stun (rodada 20), bleed (rodada 21), bleed (rodada 22), bleed (rodada 23), stun (rodada 23), stun (rodada 25), bleed (rodada 26), bleed (rodada 30), bleed (rodada 31), stun (rodada 31)
- NOBRU ativou: Postura de Muro ×5, Imortal ×2
- Neskwga aplicou: poison (rodada 4), fear (rodada 7), poison (rodada 12), vulnerable (rodada 12), poison (rodada 19), fear (rodada 23)
- Neskwga tentou sem sucesso: stun (rodada 4), bleed (rodada 4), fear (rodada 4), stun (rodada 7), bleed (rodada 7), poison (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), fear (rodada 8), vulnerable (rodada 8), stun (rodada 9), bleed (rodada 9), poison (rodada 9), fear (rodada 9), stun (rodada 11), bleed (rodada 11), poison (rodada 11), fear (rodada 11), stun (rodada 12), bleed (rodada 12), fear (rodada 12), stun (rodada 14), bleed (rodada 14), poison (rodada 14), fear (rodada 14), stun (rodada 15), bleed (rodada 15), poison (rodada 15), fear (rodada 15), stun (rodada 16), bleed (rodada 16), poison (rodada 16), fear (rodada 16), stun (rodada 17), bleed (rodada 17), poison (rodada 17), fear (rodada 17), stun (rodada 18), bleed (rodada 18), poison (rodada 18), fear (rodada 18), stun (rodada 19), bleed (rodada 19), fear (rodada 19), stun (rodada 21), bleed (rodada 21), poison (rodada 21), fear (rodada 21), stun (rodada 23), bleed (rodada 23), poison (rodada 23), stun (rodada 24), bleed (rodada 24), poison (rodada 24), fear (rodada 24), stun (rodada 27), bleed (rodada 27), poison (rodada 27), fear (rodada 27), stun (rodada 28), bleed (rodada 28), poison (rodada 28), fear (rodada 28), stun (rodada 29), bleed (rodada 29), poison (rodada 29), fear (rodada 29), stun (rodada 30), bleed (rodada 30), poison (rodada 30), fear (rodada 30)
- Neskwga ativou: Escudo Protetor ×3

Rodada a rodada:

| Rodada | Ordem (critério) | NOBRU (p1) | Neskwga (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Escudo Protetor — executada, dano 0, MP −97 | 5469 / 6216 | 948 / 571 |
| 2 | p2 → p1 (score) | Imortal — executada, dano 0, MP −228 | Golpe Poderoso — executada, dano 0, MP −47 | 5469 / 6216 | 744 / 541 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 289, MP −85 | Mira Calma — executada, dano 0, MP −103 | 5469 / 5927 | 683 / 455 |
| 4 | p2 → p1 (score) | Investida — executada, dano 407, MP −59 | Golpe Poderoso — executada, dano 221, MP −47 | 5279 / 5550 | 648 / 425 |
| 5 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Escudo Protetor — cancelada por controle | 5197 / 5550 | 596 / 442 |
| 6 | p1 → p2 (score) | Cutelada — executada, dano 385, MP −85 | Escudo Protetor — executada, dano 0, MP −97 | 5222 / 5165 | 535 / 362 |
| 7 | p2 → p1 (score) | Investida — executada, dano 0, MP −59 | Golpe Poderoso — executada, dano 221, MP −47 | 4919 / 5195 | 500 / 332 |
| 8 | p2 → p1 (score) | Imortal — executada, dano 0, MP −228 | Mira Calma — executada, dano 700, MP −103 | 4137 / 5293 | 296 / 246 |
| 9 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Golpe Poderoso — executada, dano 65, MP −47 | 4072 / 5302 | 244 / 216 |
| 10 | p1 → p2 (score) | Cutelada — executada, dano 385, MP −85 | Escudo Protetor — executada, dano 0, MP −97 | 4179 / 4917 | 183 / 136 |
| 11 | p2 → p1 (score) | Investida — executada, dano 0, MP −59 | Golpe Poderoso — executada, dano 206, MP −47 | 3973 / 4945 | 148 / 106 |
| 12 | p2 → p1 (score) | Ataque básico — executada, dano 144 | Mira Calma — executada, dano 617, MP −103 | 3314 / 4887 | 172 / 20 |
| 13 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 0 | 3232 / 4887 | 120 / 37 |
| 14 | p1 → p2 (score) | Cutelada — executada, dano 385, MP −85 | Ataque básico — executada, dano 124 | 3133 / 4519 | 59 / 54 |
| 15 | p1 → p2 (score) | Investida — executada, dano 0, MP −59 | Golpe Poderoso — executada, dano 206, MP −47 | 2845 / 4547 | 24 / 24 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 192 | Ataque básico — executada, dano 233 | 2583 / 4387 | 48 / 41 |
| 17 | p2 → p1 (score) | Ataque básico — executada, dano 192 | Ataque básico — executada, dano 233 | 2403 / 4227 | 72 / 58 |
| 18 | p2 → p1 (score) | Investida — executada, dano 334, MP −59 | Golpe Poderoso — executada, dano 387, MP −47 | 2109 / 3947 | 37 / 28 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 192 | Ataque básico — executada, dano 155 | 1925 / 3776 | 61 / 45 |
| 20 | p2 → p1 (score) | Investida — executada, dano 334, MP −59 | Ataque básico — executada, dano 0 | 1936 / 3442 | 26 / 62 |
| 21 | p2 → p1 (score) | Ataque básico — executada, dano 192 | Golpe Poderoso — executada, dano 387, MP −47 | 1520 / 3304 | 50 / 32 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 192 | Ataque básico — executada, dano 0 | 1491 / 3112 | 74 / 49 |
| 23 | p2 → p1 (score) | Investida — executada, dano 334, MP −59 | Golpe Poderoso — executada, dano 258, MP −47 | 1244 / 2814 | 39 / 19 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 155 | 1089 / 2835 | 63 / 36 |
| 25 | p2 → p1 (score) | Investida — executada, dano 334, MP −59 | Ataque básico — executada, dano 0 | 1182 / 2501 | 28 / 53 |
| 26 | p2 → p1 (score) | Ataque básico — executada, dano 192 | Golpe Poderoso — executada, dano 0, MP −47 | 1235 / 2061 | 52 / 23 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 192 | Ataque básico — executada, dano 155 | 1133 / 1642 | 76 / 40 |
| 28 | p2 → p1 (score) | Postura de Muro — executada, dano 0, MP −76 | Ataque básico — executada, dano 233 | 900 / 1426 | 24 / 57 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 192 | Golpe Poderoso — executada, dano 310, MP −47 | 643 / 780 | 48 / 27 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 192 | Ataque básico — executada, dano 124 | 572 / 108 | 72 / 44 |
| 31 | p1 → p2 (score) | Investida — executada, dano 334, MP −59 | Ataque básico — cancelada por morte | 665 / -226 | 37 / 44 |

#### Fase de 32 11 — xandfps × Gaules

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W20 | xandfps | Guerreiro | 21 | 28.48 | Mão Dupla, Mira Calma, Escudo Protetor, Peso do Machado | sustento |
| p2 | W36 | Gaules | Guerreiro | 22 | 29.98 | Mão Dupla, Peso do Machado, Estocada Seca, Fúria | crítico + controle |

- Seed da partida: `10611109298908495297`
- Rodadas: **16**
- Vencedor: **Gaules** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 723/5209 (13.9%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | xandfps | Gaules |
|---|---|---|
| Dano causado (golpes + DoT) | 4631 (4007 + 624) | 6194 (3649 + 2545) |
| Cura (skill + roubo de vida) | 1600 (0 + 1600) | 145 (0 + 145) |
| MP gasto em ações | 1044 | 954 |
| Skills / ataques básicos | 13 / 0 | 9 / 7 |
| Acertos / erros | 7 / 2 | 10 / 0 |
| Críticos (dano) | 0 (0) | 3 (1639) |
| Agiu primeiro (rodadas) | 5 | 11 |
| Ações perdidas por controle | 3 | 0 |

Efeitos relevantes:
- xandfps aplicou: vulnerable (rodada 4), bleed (rodada 6), vulnerable (rodada 12)
- xandfps tentou sem sucesso: stun (rodada 4), bleed (rodada 4), poison (rodada 4), stun (rodada 6), bleed (rodada 6), poison (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), vulnerable (rodada 7), stun (rodada 10), bleed (rodada 10), poison (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), poison (rodada 11), vulnerable (rodada 11), stun (rodada 12), bleed (rodada 12), poison (rodada 12), stun (rodada 14), bleed (rodada 14), poison (rodada 14), bleed (rodada 14)
- xandfps ativou: Escudo Protetor ×4
- Leis disparadas por xandfps: FERIDA SÉPTICA (rodada 12), FERIDA SÉPTICA (rodada 15)
- Gaules aplicou: stun (rodada 3), bleed (rodada 3), bleed (rodada 7), bleed (rodada 10), poison (rodada 10), bleed (rodada 12), stun (rodada 14), stun (rodada 15), bleed (rodada 15), poison (rodada 15)
- Gaules tentou sem sucesso: bleed (rodada 2), bleed (rodada 3), poison (rodada 3), stun (rodada 4), bleed (rodada 4), poison (rodada 4), bleed (rodada 6), stun (rodada 7), bleed (rodada 7), poison (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), stun (rodada 10), stun (rodada 11), bleed (rodada 11), poison (rodada 11), stun (rodada 13), bleed (rodada 13), poison (rodada 13), bleed (rodada 14), poison (rodada 14), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), poison (rodada 16)
- Gaules ativou: Fúria ×3

Rodada a rodada:

| Rodada | Ordem (critério) | xandfps (p1) | Gaules (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −87 | Fúria — executada, dano 0, MP −171 | 4259 / 5209 | 769 / 524 |
| 2 | p2 → p1 (score) | Mão Dupla — executada, dano 0, MP −76 | Estocada Seca — executada, dano 0, MP −62 | 4259 / 5209 | 726 / 482 |
| 3 | p2 → p1 (score) | Mira Calma — cancelada por controle | Mão Dupla — executada, dano 500, MP −85 | 3589 / 5209 | 759 / 417 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 611, MP −92 | Ataque básico — executada, dano 202 | 3461 / 4598 | 700 / 437 |
| 5 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −87 | Fúria — executada, dano 0, MP −171 | 3291 / 4598 | 646 / 286 |
| 6 | p2 → p1 (score) | Mão Dupla — executada, dano 438, MP −76 | Estocada Seca — executada, dano 0, MP −62 | 3466 / 4160 | 603 / 244 |
| 7 | p2 → p1 (score) | Mira Calma — executada, dano 748, MP −92 | Mão Dupla — executada, dano 500, MP −85 | 3095 / 3229 | 544 / 179 |
| 8 | p2 → p1 (score) | Peso do Machado — executada, dano 0, MP −58 | Ataque básico — executada, dano 303 | 2622 / 3036 | 519 / 199 |
| 9 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −87 | Fúria — executada, dano 0, MP −171 | 2452 / 2828 | 465 / 48 |
| 10 | p2 → p1 (score) | Mão Dupla — executada, dano 438, MP −76 | Ataque básico — executada, dano 202 | 2192 / 2400 | 422 / 68 |
| 11 | p2 → p1 (score) | Mira Calma — executada, dano 748, MP −92 | Ataque básico — executada, dano 202 | 2056 / 1662 | 363 / 88 |
| 12 | p2 → p1 (score) | Peso do Machado — executada, dano 377, MP −58 | Estocada Seca — executada, dano 0, MP −62 | 1973 / 1285 | 338 / 46 |
| 13 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −87 | Ataque básico — executada, dano 202 | 1538 / 1295 | 284 / 66 |
| 14 | p1 → p2 (score) | Mão Dupla — executada, dano 647, MP −76 | Ataque básico — executada, dano 202 | 1361 / 658 | 241 / 86 |
| 15 | p1 → p2 (score) | Mira Calma — cancelada por controle | Mão Dupla — executada, dano 938, MP −85 | 360 / 704 | 274 / 21 |
| 16 | p1 → p2 (score) | Mira Calma — cancelada por controle | Ataque básico — executada, dano 398 | -335 / 723 | 307 / 41 |

#### Fase de 32 12 — YoDa × XANDAOOGOD

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W33 | YoDa | Guerreiro | 21 | 29.41 | Mão Dupla, Tremor de Bigorna, Estocada Seca, Lâmina Assentada | controle |
| p2 | W47 | XANDAOOGOD | Guerreiro | 23 | 29.64 | Esmagar, Mira Calma, Leitura de Terreno, Veterania | defesa |

- Seed da partida: `17524866069901069562`
- Rodadas: **13**
- Vencedor: **XANDAOOGOD** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 4339/5684 (76.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | YoDa | XANDAOOGOD |
|---|---|---|
| Dano causado (golpes + DoT) | 1345 (664 + 681) | 5596 (4375 + 1221) |
| Cura (skill + roubo de vida) | 32 (0 + 32) | 0 (0 + 0) |
| MP gasto em ações | 516 | 1164 |
| Skills / ataques básicos | 7 / 2 | 9 / 4 |
| Acertos / erros | 3 / 1 | 10 / 0 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 0 | 13 |
| Ações perdidas por controle | 3 | 0 |

Efeitos relevantes:
- YoDa aplicou: bleed (rodada 3), fear (rodada 10)
- YoDa tentou sem sucesso: bleed (rodada 4), fear (rodada 4), bleed (rodada 4), bleed (rodada 5), fear (rodada 5), bleed (rodada 8), bleed (rodada 10)
- YoDa ativou: Lâmina Assentada ×3
- Leis disparadas por YoDa: FERIDA SÉPTICA (rodada 4)
- XANDAOOGOD aplicou: poison (rodada 2), stun (rodada 2), bleed (rodada 4), stun (rodada 7), stun (rodada 12), bleed (rodada 13), vulnerable (rodada 13)
- XANDAOOGOD tentou sem sucesso: bleed (rodada 2), bleed (rodada 3), poison (rodada 3), vulnerable (rodada 3), poison (rodada 4), bleed (rodada 5), poison (rodada 5), bleed (rodada 7), poison (rodada 7), bleed (rodada 8), poison (rodada 8), vulnerable (rodada 8), bleed (rodada 9), poison (rodada 9), bleed (rodada 10), poison (rodada 10), bleed (rodada 12), poison (rodada 12), poison (rodada 13)
- XANDAOOGOD ativou: Veterania ×3

Rodada a rodada:

| Rodada | Ordem (critério) | YoDa (p1) | XANDAOOGOD (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Lâmina Assentada — executada, dano 0, MP −84 | Veterania — executada, dano 0, MP −111 | 5464 / 5684 | 519 / 926 |
| 2 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Esmagar — executada, dano 473, MP −161 | 4910 / 5684 | 531 / 789 |
| 3 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −56 | Mira Calma — executada, dano 679, MP −116 | 4150 / 5684 | 487 / 697 |
| 4 | p2 → p1 (score) | Mão Dupla — executada, dano 364, MP −76 | Ataque básico — executada, dano 191 | 3678 / 5093 | 423 / 721 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 191 | 3195 / 4716 | 435 / 745 |
| 6 | p2 → p1 (score) | Lâmina Assentada — executada, dano 0, MP −84 | Veterania — executada, dano 0, MP −111 | 3114 / 4489 | 363 / 658 |
| 7 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Esmagar — executada, dano 473, MP −161 | 2560 / 4489 | 375 / 521 |
| 8 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −56 | Mira Calma — executada, dano 591, MP −116 | 1888 / 4489 | 331 / 429 |
| 9 | p2 → p1 (score) | Mão Dupla — executada, dano 0, MP −76 | Ataque básico — executada, dano 191 | 1697 / 4489 | 267 / 453 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 191 | 1513 / 4339 | 279 / 477 |
| 11 | p2 → p1 (score) | Lâmina Assentada — executada, dano 0, MP −84 | Veterania — executada, dano 0, MP −111 | 1513 / 4339 | 207 / 390 |
| 12 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Esmagar — executada, dano 804, MP −161 | 709 / 4339 | 219 / 253 |
| 13 | p2 → p1 (score) | Estocada Seca — cancelada por morte | Mira Calma — executada, dano 591, MP −116 | -100 / 4339 | 231 / 161 |

#### Fase de 32 13 — jovirone × yeTz

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W22 | jovirone | Guerreiro | 24 | 29.52 | Marca do Açougueiro, Quebra-Guarda, Disciplina de Forja, Sangue nos Olhos | sustento |
| p2 | W39 | yeTz | Guerreiro | 23 | 29.87 | Paciência do Coveiro, Quebra-Guarda, Postura de Muro, Cutelada | sustento |

- Seed da partida: `3753158130026634828`
- Rodadas: **39**
- Vencedor: **jovirone** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2144/6345 (33.8%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | jovirone | yeTz |
|---|---|---|
| Dano causado (golpes + DoT) | 9017 (4297 + 4720) | 5557 (4759 + 798) |
| Cura (skill + roubo de vida) | 1356 (0 + 1356) | 1513 (0 + 1513) |
| MP gasto em ações | 2200 | 1864 |
| Skills / ataques básicos | 24 / 15 | 23 / 15 |
| Acertos / erros | 14 / 9 | 19 / 8 |
| Críticos (dano) | 1 (307) | 0 (0) |
| Agiu primeiro (rodadas) | 29 | 10 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- jovirone aplicou: vulnerable (rodada 2), bleed (rodada 2), vulnerable (rodada 22), bleed (rodada 22), vulnerable (rodada 23), vulnerable (rodada 27), bleed (rodada 27), vulnerable (rodada 32), vulnerable (rodada 33), vulnerable (rodada 37), bleed (rodada 37), vulnerable (rodada 38)
- jovirone tentou sem sucesso: stun (rodada 5), vulnerable (rodada 7), stun (rodada 9), stun (rodada 10), vulnerable (rodada 12), stun (rodada 13), vulnerable (rodada 13), stun (rodada 14), vulnerable (rodada 17), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 28), vulnerable (rodada 28), stun (rodada 29), stun (rodada 30), bleed (rodada 32), stun (rodada 33), stun (rodada 38), stun (rodada 39)
- jovirone ativou: Disciplina de Forja ×8
- yeTz aplicou: poison (rodada 2), frailty (rodada 2), poison (rodada 8), frailty (rodada 8), vulnerable (rodada 10), vulnerable (rodada 30)
- yeTz tentou sem sucesso: vulnerable (rodada 3), vulnerable (rodada 21), vulnerable (rodada 26), vulnerable (rodada 35)
- yeTz ativou: Postura de Muro ×9
- Leis disparadas por yeTz: FERIDA ABERTA (rodada 2), FERIDA ABERTA (rodada 22), FERIDA ABERTA (rodada 27), FERIDA ABERTA (rodada 37)

Rodada a rodada:

| Rodada | Ordem (critério) | jovirone (p1) | yeTz (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Postura de Muro — executada, dano 0, MP −76 | 6345 / 7383 | 1073 / 700 |
| 2 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Paciência do Coveiro — executada, dano 0, MP −140 | 6345 / 6793 | 1026 / 591 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −79 | Quebra-Guarda — executada, dano 299, MP −70 | 5970 / 6298 | 978 / 552 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Cutelada — executada, dano 349, MP −85 | 5545 / 6409 | 1009 / 498 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 307 | Postura de Muro — executada, dano 0, MP −76 | 5076 / 6102 | 1040 / 453 |
| 6 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Quebra-Guarda — executada, dano 0, MP −70 | 5000 / 6102 | 953 / 414 |
| 7 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Cutelada — executada, dano 244, MP −85 | 4661 / 6180 | 906 / 360 |
| 8 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −79 | Paciência do Coveiro — executada, dano 0, MP −140 | 4661 / 6180 | 858 / 251 |
| 9 | p1 → p2 (score) | Ataque básico — executada, dano 192 | Postura de Muro — executada, dano 0, MP −76 | 4669 / 5988 | 889 / 206 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 153 | Quebra-Guarda — executada, dano 299, MP −70 | 4361 / 5930 | 920 / 167 |
| 11 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Cutelada — executada, dano 563, MP −85 | 3722 / 6110 | 833 / 113 |
| 12 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 149 | 3497 / 6157 | 786 / 144 |
| 13 | p1 → p2 (score) | Quebra-Guarda — executada, dano 469, MP −79 | Postura de Muro — executada, dano 0, MP −76 | 3608 / 5688 | 738 / 99 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Quebra-Guarda — executada, dano 0, MP −70 | 3675 / 5535 | 769 / 60 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 3675 / 5535 | 800 / 91 |
| 16 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Cutelada — executada, dano 327, MP −85 | 3348 / 5639 | 713 / 37 |
| 17 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 0 | 3348 / 5639 | 666 / 68 |
| 18 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −79 | Ataque básico — executada, dano 122 | 3226 / 5678 | 618 / 99 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Postura de Muro — executada, dano 0, MP −76 | 3226 / 5678 | 649 / 54 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 3226 / 5678 | 680 / 85 |
| 21 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Quebra-Guarda — executada, dano 359, MP −70 | 2867 / 5792 | 593 / 46 |
| 22 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 122 | 2745 / 5241 | 546 / 77 |
| 23 | p1 → p2 (score) | Quebra-Guarda — executada, dano 503, MP −79 | Postura de Muro — executada, dano 0, MP −76 | 2966 / 4148 | 498 / 32 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 236 | Ataque básico — executada, dano 0 | 3069 / 3912 | 529 / 63 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 195 | Ataque básico — executada, dano 164 | 2990 / 3769 | 560 / 94 |
| 26 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Quebra-Guarda — executada, dano 359, MP −70 | 2631 / 3883 | 473 / 55 |
| 27 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 0 | 2631 / 3293 | 426 / 86 |
| 28 | p1 → p2 (score) | Quebra-Guarda — executada, dano 503, MP −79 | Postura de Muro — executada, dano 0, MP −76 | 2852 / 2200 | 378 / 41 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 185 | Ataque básico — executada, dano 122 | 2811 / 2054 | 409 / 72 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 159 | Quebra-Guarda — executada, dano 359, MP −70 | 2521 / 2009 | 440 / 33 |
| 31 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Ataque básico — executada, dano 0 | 2521 / 2009 | 353 / 64 |
| 32 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 149 | 2372 / 2056 | 306 / 95 |
| 33 | p1 → p2 (score) | Quebra-Guarda — executada, dano 503, MP −79 | Postura de Muro — executada, dano 0, MP −76 | 2593 / 1553 | 258 / 50 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 128 | 2465 / 1593 | 289 / 81 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Quebra-Guarda — executada, dano 359, MP −70 | 2106 / 1707 | 320 / 42 |
| 36 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Ataque básico — executada, dano 164 | 1942 / 1759 | 233 / 73 |
| 37 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 122 | 1820 / 1208 | 186 / 104 |
| 38 | p1 → p2 (score) | Quebra-Guarda — executada, dano 503, MP −79 | Postura de Muro — executada, dano 0, MP −76 | 2041 / 115 | 138 / 59 |
| 39 | p1 → p2 (score) | Ataque básico — executada, dano 236 | Ataque básico — cancelada por morte | 2144 / -121 | 169 / 59 |

#### Fase de 32 14 — fer × Felps

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W64 | fer | Guerreiro | 23 | 29.98 | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | defesa + sustento |
| p2 | W31 | Felps | Guerreiro | 20 | 29.64 | Sangue nos Olhos, Quebra-Guarda, Travar o Pulso, Marca do Açougueiro | crítico + controle |

- Seed da partida: `4743871819551685823`
- Rodadas: **15**
- Vencedor: **fer** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1651/5977 (27.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fer | Felps |
|---|---|---|
| Dano causado (golpes + DoT) | 4891 (4891 + 0) | 5436 (991 + 4445) |
| Cura (skill + roubo de vida) | 1110 (597 + 513) | 77 (0 + 77) |
| MP gasto em ações | 1033 | 682 |
| Skills / ataques básicos | 13 / 0 | 14 / 0 |
| Acertos / erros | 9 / 0 | 5 / 1 |
| Críticos (dano) | 3 (2301) | 1 (257) |
| Agiu primeiro (rodadas) | 15 | 0 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- fer aplicou: weakened (rodada 10), weakened (rodada 15)
- fer tentou sem sucesso: stun (rodada 2), stun (rodada 3), weakened (rodada 3), stun (rodada 4), stun (rodada 6), stun (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 14), stun (rodada 15)
- fer ativou: Juramento da Muralha ×3
- Leis disparadas por fer: FERIDA SÉPTICA (rodada 4), FERIDA SÉPTICA (rodada 7), FERIDA SÉPTICA (rodada 8)
- Felps aplicou: weakened (rodada 2), slowed (rodada 2), poison (rodada 3), stun (rodada 4), bleed (rodada 4), weakened (rodada 6), stun (rodada 7), bleed (rodada 7), bleed (rodada 8), vulnerable (rodada 9), weakened (rodada 10), poison (rodada 12), bleed (rodada 12), vulnerable (rodada 13), weakened (rodada 14)
- Felps tentou sem sucesso: vulnerable (rodada 1), stun (rodada 3), bleed (rodada 3), vulnerable (rodada 3), bleed (rodada 4), poison (rodada 4), vulnerable (rodada 5), slowed (rodada 6), poison (rodada 7), vulnerable (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), bleed (rodada 9), slowed (rodada 10), stun (rodada 12), bleed (rodada 12), bleed (rodada 13), slowed (rodada 14)

Rodada a rodada:

| Rodada | Ordem (critério) | fer (p1) | Felps (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Sangue nos Olhos — executada, dano 0, MP −50 | 5977 / 4098 | 951 / 568 |
| 2 | p1 → p2 (score) | Golpe Poderoso — executada, dano 507, MP −52 | Travar o Pulso — executada, dano 0, MP −50 | 5977 / 3591 | 921 / 530 |
| 3 | p1 → p2 (score) | Soco de Placa — executada, dano 395, MP −61 | Quebra-Guarda — executada, dano 177, MP −50 | 5800 / 3210 | 882 / 492 |
| 4 | p1 → p2 (score) | Golpe Poderoso — executada, dano 375, MP −52 | Marca do Açougueiro — executada, dano 131, MP −44 | 5628 / 2845 | 852 / 460 |
| 5 | p1 → p2 (score) | Soco de Placa — cancelada por controle | Sangue nos Olhos — executada, dano 0, MP −50 | 5300 / 2845 | 874 / 422 |
| 6 | p1 → p2 (score) | Golpe Poderoso — executada, dano 469, MP −52 | Travar o Pulso — executada, dano 0, MP −50 | 5032 / 2376 | 844 / 384 |
| 7 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Quebra-Guarda — executada, dano 159, MP −50 | 4545 / 2388 | 714 / 346 |
| 8 | p1 → p2 (score) | Golpe Poderoso — cancelada por controle | Marca do Açougueiro — executada, dano 257, MP −44 | 3960 / 2408 | 736 / 314 |
| 9 | p1 → p2 (score) | Golpe Poderoso — executada, dano 751, MP −52 | Sangue nos Olhos — executada, dano 0, MP −50 | 3490 / 1657 | 706 / 276 |
| 10 | p1 → p2 (score) | Soco de Placa — executada, dano 791, MP −61 | Travar o Pulso — executada, dano 0, MP −50 | 3025 / 866 | 667 / 238 |
| 11 | p1 → p2 (score) | Golpe Poderoso — executada, dano 375, MP −52 | Quebra-Guarda — executada, dano 0, MP −50 | 2506 / 491 | 637 / 200 |
| 12 | p1 → p2 (score) | Respirar Fundo — executada, dano 0, MP −82 | Marca do Açougueiro — executada, dano 267, MP −44 | 2747 / 512 | 577 / 168 |
| 13 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Sangue nos Olhos — executada, dano 0, MP −50 | 2329 / 512 | 447 / 130 |
| 14 | p1 → p2 (score) | Golpe Poderoso — executada, dano 469, MP −52 | Travar o Pulso — executada, dano 0, MP −50 | 1971 / 43 | 417 / 92 |
| 15 | p1 → p2 (score) | Soco de Placa — executada, dano 759, MP −61 | Quebra-Guarda — cancelada por morte | 1651 / -716 | 378 / 92 |

#### Fase de 32 15 — RazaH × jukes

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W15 | RazaH | Guerreiro | 20 | 29.06 | Marca do Caçador, Grito Curto, Pausa Útil, Mão Dupla | crítico + controle |
| p2 | W03 | jukes | Guerreiro | 22 | 28.14 | Golpe Poderoso, Respirar Fundo, Mira Calma, Leitura de Terreno | defesa + sustento |

- Seed da partida: `5903575241729991190`
- Rodadas: **29**
- Vencedor: **jukes** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2703/5515 (49.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | RazaH | jukes |
|---|---|---|
| Dano causado (golpes + DoT) | 4111 (2571 + 1540) | 5654 (5654 + 0) |
| Cura (skill + roubo de vida) | 123 (0 + 123) | 1299 (1102 + 197) |
| MP gasto em ações | 900 | 1570 |
| Skills / ataques básicos | 18 / 10 | 22 / 6 |
| Acertos / erros | 9 / 7 | 16 / 5 |
| Críticos (dano) | 3 (834) | 0 (0) |
| Agiu primeiro (rodadas) | 29 | 0 |
| Ações perdidas por controle | 1 | 1 |

Efeitos relevantes:
- RazaH aplicou: fear (rodada 2), weakened (rodada 2), stun (rodada 4), bleed (rodada 5), bleed (rodada 10), fear (rodada 12), bleed (rodada 13), fear (rodada 17), weakened (rodada 17), fear (rodada 24)
- RazaH tentou sem sucesso: bleed (rodada 4), poison (rodada 4), fear (rodada 4), stun (rodada 5), poison (rodada 5), fear (rodada 5), fear (rodada 7), stun (rodada 10), poison (rodada 10), fear (rodada 10), weakened (rodada 12), stun (rodada 13), bleed (rodada 13), poison (rodada 13), fear (rodada 13), stun (rodada 14), bleed (rodada 14), poison (rodada 14), fear (rodada 14), stun (rodada 15), bleed (rodada 15), poison (rodada 15), fear (rodada 15), stun (rodada 18), bleed (rodada 18), poison (rodada 18), fear (rodada 18), bleed (rodada 18), fear (rodada 22), stun (rodada 24), bleed (rodada 24), poison (rodada 24), fear (rodada 27), stun (rodada 28), bleed (rodada 28), poison (rodada 28), fear (rodada 28), bleed (rodada 28)
- RazaH ativou: Pausa Útil ×6
- jukes aplicou: stun (rodada 8)
- jukes tentou sem sucesso: stun (rodada 3), vulnerable (rodada 3), stun (rodada 5), vulnerable (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 13), vulnerable (rodada 13), stun (rodada 14), stun (rodada 18), stun (rodada 19), vulnerable (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 23), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 29)
- jukes ativou: Leitura de Terreno ×5

Rodada a rodada:

| Rodada | Ordem (critério) | RazaH (p1) | jukes (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −37 | Leitura de Terreno — executada, dano 0, MP −99 | 5285 / 5515 | 500 / 742 |
| 2 | p1 → p2 (score) | Grito Curto — executada, dano 0, MP −45 | Golpe Poderoso — executada, dano 0, MP −47 | 5285 / 5515 | 479 / 723 |
| 3 | p1 → p2 (score) | Mão Dupla — executada, dano 0, MP −68 | Mira Calma — executada, dano 665, MP −103 | 4620 / 5515 | 435 / 648 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 168 | Golpe Poderoso — cancelada por controle | 4628 / 5347 | 459 / 676 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 278 | Golpe Poderoso — executada, dano 326, MP −47 | 4315 / 4862 | 483 / 657 |
| 6 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −37 | Leitura de Terreno — executada, dano 0, MP −99 | 4315 / 4642 | 456 / 586 |
| 7 | p1 → p2 (score) | Grito Curto — executada, dano 0, MP −45 | Golpe Poderoso — executada, dano 0, MP −47 | 4315 / 4642 | 435 / 567 |
| 8 | p1 → p2 (score) | Mão Dupla — executada, dano 0, MP −68 | Mira Calma — executada, dano 665, MP −103 | 3650 / 4668 | 391 / 492 |
| 9 | p1 → p2 (score) | Ataque básico — cancelada por controle | Golpe Poderoso — executada, dano 304, MP −47 | 3346 / 4680 | 415 / 473 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 278 | Ataque básico — executada, dano 176 | 3183 / 4189 | 439 / 501 |
| 11 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −37 | Leitura de Terreno — executada, dano 0, MP −99 | 3183 / 3969 | 412 / 430 |
| 12 | p1 → p2 (score) | Grito Curto — executada, dano 0, MP −45 | Golpe Poderoso — executada, dano 0, MP −47 | 3183 / 3969 | 391 / 411 |
| 13 | p1 → p2 (score) | Mão Dupla — executada, dano 411, MP −68 | Mira Calma — executada, dano 583, MP −103 | 2620 / 3361 | 347 / 336 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 168 | Golpe Poderoso — executada, dano 304, MP −47 | 2324 / 2985 | 371 / 317 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 168 | Ataque básico — executada, dano 0 | 2332 / 2597 | 395 / 345 |
| 16 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −37 | Respirar Fundo — executada, dano 0, MP −73 | 2332 / 3148 | 368 / 300 |
| 17 | p1 → p2 (score) | Grito Curto — executada, dano 0, MP −45 | Leitura de Terreno — executada, dano 0, MP −99 | 2332 / 3148 | 347 / 229 |
| 18 | p1 → p2 (score) | Mão Dupla — executada, dano 411, MP −68 | Golpe Poderoso — executada, dano 304, MP −47 | 2048 / 2749 | 303 / 210 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Mira Calma — executada, dano 583, MP −103 | 1465 / 2772 | 327 / 135 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 304, MP −47 | 1161 / 2784 | 351 / 116 |
| 21 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −37 | Ataque básico — executada, dano 176 | 985 / 2791 | 324 / 144 |
| 22 | p1 → p2 (score) | Grito Curto — executada, dano 0, MP −45 | Leitura de Terreno — executada, dano 0, MP −99 | 985 / 2791 | 303 / 73 |
| 23 | p1 → p2 (score) | Mão Dupla — executada, dano 0, MP −68 | Golpe Poderoso — executada, dano 304, MP −47 | 681 / 2803 | 259 / 54 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 278 | Ataque básico — executada, dano 176 | 518 / 2532 | 283 / 82 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Respirar Fundo — executada, dano 0, MP −73 | 518 / 3083 | 307 / 37 |
| 26 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −37 | Ataque básico — executada, dano 176 | 342 / 3090 | 280 / 65 |
| 27 | p1 → p2 (score) | Grito Curto — executada, dano 0, MP −45 | Golpe Poderoso — executada, dano 304, MP −47 | 38 / 3102 | 259 / 46 |
| 28 | p1 → p2 (score) | Mão Dupla — executada, dano 411, MP −68 | Ataque básico — executada, dano 0 | 58 / 2691 | 215 / 74 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 304, MP −47 | -246 / 2703 | 239 / 55 |

#### Fase de 32 16 — sacy × RNakano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W16 | sacy | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Escudo Protetor, Silêncio do Veterano | sustento |
| p2 | W42 | RNakano | Guerreiro | 24 | 29.64 | Golpe Duplo, Cutelada, Gancho e Corda, Disciplina de Forja | sustento |

- Seed da partida: `6729932908895877751`
- Rodadas: **63**
- Vencedor: **RNakano** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 5160/8159 (63.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | sacy | RNakano |
|---|---|---|
| Dano causado (golpes + DoT) | 6079 (6079 + 0) | 8823 (8823 + 0) |
| Cura (skill + roubo de vida) | 1197 (0 + 1197) | 3080 (0 + 3080) |
| MP gasto em ações | 2370 | 2691 |
| Skills / ataques básicos | 21 / 42 | 25 / 38 |
| Acertos / erros | 38 / 7 | 43 / 11 |
| Críticos (dano) | 4 (788) | 1 (225) |
| Agiu primeiro (rodadas) | 57 | 6 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- sacy aplicou: fear (rodada 2), vulnerable (rodada 2), vulnerable (rodada 4), fear (rodada 7), vulnerable (rodada 7)
- sacy ativou: Escudo Protetor ×16
- RNakano tentou sem sucesso: stun (rodada 2), stun (rodada 3), frailty (rodada 3), stun (rodada 4), stun (rodada 7), stun (rodada 9), stun (rodada 10), stun (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 30), stun (rodada 31), stun (rodada 33), stun (rodada 35), stun (rodada 36), stun (rodada 37), stun (rodada 38), stun (rodada 40), stun (rodada 41), stun (rodada 44), stun (rodada 45), stun (rodada 46), stun (rodada 48), stun (rodada 49), stun (rodada 50), stun (rodada 51), stun (rodada 52), stun (rodada 54), stun (rodada 56), stun (rodada 57), stun (rodada 59), stun (rodada 60), stun (rodada 61), stun (rodada 62), stun (rodada 63)
- RNakano ativou: Disciplina de Forja ×6

Rodada a rodada:

| Rodada | Ordem (critério) | sacy (p1) | RNakano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Disciplina de Forja — executada, dano 0, MP −118 | 7520 / 8159 | 677 / 795 |
| 2 | p1 → p2 (score) | Silêncio do Veterano — executada, dano 0, MP −135 | Gancho e Corda — executada, dano 0, MP −131 | 7520 / 8159 | 568 / 694 |
| 3 | p1 → p2 (score) | Golpe Devastador — executada, dano 292, MP −120 | Golpe Duplo — executada, dano 306, MP −130 | 7214 / 7974 | 474 / 594 |
| 4 | p1 → p2 (score) | Mira Calma — executada, dano 503, MP −116 | Cutelada — executada, dano 372, MP −95 | 6947 / 7601 | 384 / 529 |
| 5 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 0 | 6947 / 7601 | 301 / 559 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Disciplina de Forja — executada, dano 0, MP −118 | 6978 / 7451 | 327 / 471 |
| 7 | p1 → p2 (score) | Silêncio do Veterano — executada, dano 0, MP −135 | Gancho e Corda — executada, dano 0, MP −131 | 6978 / 7451 | 218 / 370 |
| 8 | p1 → p2 (score) | Golpe Devastador — executada, dano 0, MP −120 | Golpe Duplo — executada, dano 0, MP −130 | 6978 / 7451 | 124 / 270 |
| 9 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −109 | Cutelada — executada, dano 372, MP −95 | 6606 / 7581 | 41 / 205 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 140 | 6489 / 7518 | 67 / 235 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Disciplina de Forja — executada, dano 0, MP −118 | 6489 / 7518 | 93 / 147 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Gancho e Corda — executada, dano 0, MP −131 | 6512 / 7406 | 119 / 46 |
| 13 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 187 | 6325 / 7471 | 36 / 76 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 140 | 6208 / 7408 | 62 / 106 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Cutelada — executada, dano 278, MP −95 | 5930 / 7505 | 88 / 41 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 5774 / 7420 | 114 / 71 |
| 17 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 225 | 5549 / 7498 | 31 / 101 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Cutelada — executada, dano 278, MP −95 | 5302 / 7445 | 57 / 36 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 226 | Ataque básico — executada, dano 140 | 5209 / 7268 | 83 / 66 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 0 | 5240 / 7118 | 109 / 96 |
| 21 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Cutelada — executada, dano 0, MP −95 | 5240 / 7118 | 26 / 31 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 5131 / 7017 | 52 / 61 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 5022 / 6916 | 78 / 91 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 4866 / 6831 | 104 / 121 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Disciplina de Forja — executada, dano 0, MP −118 | 4897 / 6681 | 130 / 33 |
| 26 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 187 | 4710 / 6746 | 47 / 63 |
| 27 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 140 | 4570 / 6795 | 73 / 93 |
| 28 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 140 | 4453 / 6732 | 99 / 123 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 168 | Cutelada — executada, dano 372, MP −95 | 4116 / 6694 | 125 / 58 |
| 30 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 140 | 3976 / 6743 | 42 / 88 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 3867 / 6642 | 68 / 118 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 226 | Disciplina de Forja — executada, dano 0, MP −118 | 3914 / 6416 | 94 / 30 |
| 33 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 187 | 3750 / 6369 | 120 / 60 |
| 34 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 0 | 3750 / 6369 | 37 / 90 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 140 | 3633 / 6306 | 63 / 120 |
| 36 | p1 → p2 (score) | Ataque básico — executada, dano 168 | Cutelada — executada, dano 278, MP −95 | 3390 / 6235 | 89 / 55 |
| 37 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 3234 / 6150 | 115 / 85 |
| 38 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 140 | 3094 / 6199 | 32 / 115 |
| 39 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Cutelada — executada, dano 0, MP −95 | 3125 / 6049 | 58 / 50 |
| 40 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 3016 / 5948 | 84 / 80 |
| 41 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 2860 / 5863 | 110 / 110 |
| 42 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Cutelada — executada, dano 0, MP −95 | 2860 / 5863 | 27 / 45 |
| 43 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 0 | 2891 / 5713 | 53 / 75 |
| 44 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 2782 / 5612 | 79 / 105 |
| 45 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Cutelada — executada, dano 372, MP −95 | 2441 / 5592 | 105 / 40 |
| 46 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 2285 / 5507 | 131 / 70 |
| 47 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 0 | 2285 / 5507 | 48 / 100 |
| 48 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Cutelada — executada, dano 278, MP −95 | 2038 / 5454 | 74 / 35 |
| 49 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 1929 / 5353 | 100 / 65 |
| 50 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 1773 / 5268 | 126 / 95 |
| 51 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Cutelada — executada, dano 278, MP −95 | 1495 / 5365 | 43 / 30 |
| 52 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 140 | 1355 / 5414 | 69 / 60 |
| 53 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 1355 / 5414 | 95 / 90 |
| 54 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 187 | 1199 / 5329 | 121 / 120 |
| 55 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Disciplina de Forja — executada, dano 0, MP −118 | 1199 / 5329 | 38 / 32 |
| 56 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 140 | 1082 / 5266 | 64 / 62 |
| 57 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 140 | 942 / 5315 | 90 / 92 |
| 58 | p1 → p2 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 0 | 965 / 5203 | 116 / 122 |
| 59 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −109 | Cutelada — executada, dano 372, MP −95 | 593 / 5333 | 33 / 57 |
| 60 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 484 / 5232 | 59 / 87 |
| 61 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Ataque básico — executada, dano 140 | 375 / 5131 | 85 / 117 |
| 62 | p1 → p2 (score) | Ataque básico — executada, dano 150 | Cutelada — executada, dano 372, MP −95 | 34 / 5111 | 111 / 52 |
| 63 | p1 → p2 (score) | Escudo Protetor — executada, dano 0, MP −109 | Ataque básico — executada, dano 140 | -106 / 5160 | 28 / 82 |

### Oitavas: detalhes

#### Oitavas 1 — Smzinho × gafallen

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W35 | Smzinho | Guerreiro | 23 | 29.75 | Cutelada, Mira Calma, Veterania, Estocada Seca | controle |
| p2 | W37 | gafallen | Guerreiro | 20 | 29.87 | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda | sustento |

- Seed da partida: `8956104733299499117`
- Rodadas: **23**
- Vencedor: **gafallen** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1510/3973 (38.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Smzinho | gafallen |
|---|---|---|
| Dano causado (golpes + DoT) | 6670 (5248 + 1422) | 5761 (5761 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 4207 (1998 + 2209) |
| MP gasto em ações | 1523 | 1302 |
| Skills / ataques básicos | 16 / 6 | 18 / 2 |
| Acertos / erros | 13 / 0 | 8 / 3 |
| Críticos (dano) | 0 (0) | 2 (2646) |
| Agiu primeiro (rodadas) | 7 | 16 |
| Ações perdidas por controle | 0 | 3 |

Efeitos relevantes:
- Smzinho aplicou: bleed (rodada 2), fear (rodada 5), fear (rodada 9), vulnerable (rodada 9), stun (rodada 10), bleed (rodada 12), fear (rodada 14), vulnerable (rodada 14), bleed (rodada 17), stun (rodada 18), stun (rodada 19)
- Smzinho tentou sem sucesso: stun (rodada 3), fear (rodada 3), stun (rodada 4), fear (rodada 4), vulnerable (rodada 4), stun (rodada 5), bleed (rodada 7), stun (rodada 8), fear (rodada 8), stun (rodada 9), fear (rodada 10), stun (rodada 13), fear (rodada 13), stun (rodada 14), stun (rodada 15), fear (rodada 15), fear (rodada 18), fear (rodada 19), stun (rodada 20), fear (rodada 20), stun (rodada 22), fear (rodada 22)
- Smzinho ativou: Veterania ×5
- gafallen aplicou: vulnerable (rodada 2), vulnerable (rodada 3), vulnerable (rodada 15), bleed (rodada 23), vulnerable (rodada 23)
- gafallen tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), vulnerable (rodada 6), stun (rodada 12), bleed (rodada 12), vulnerable (rodada 12), stun (rodada 15), bleed (rodada 15), stun (rodada 18), bleed (rodada 18), vulnerable (rodada 18), stun (rodada 23)
- gafallen ativou: Escudo Protetor ×6
- Leis disparadas por gafallen: PÂNICO (rodada 14)

Rodada a rodada:

| Rodada | Ordem (critério) | Smzinho (p1) | gafallen (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Veterania — executada, dano 0, MP −111 | Escudo Protetor — executada, dano 0, MP −77 | 5701 / 3973 | 847 / 686 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 780, MP −82 | 4921 / 3973 | 808 / 643 |
| 3 | p2 → p1 (score) | Cutelada — executada, dano 484, MP −85 | Quebra-Guarda — executada, dano 418, MP −50 | 4503 / 3489 | 754 / 632 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 652, MP −116 | Ataque básico — executada, dano 173 | 4330 / 2756 | 669 / 671 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 179 | Escudo Protetor — executada, dano 0, MP −77 | 4330 / 2419 | 700 / 633 |
| 6 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Mira Calma — executada, dano 1323, MP −82 | 3007 / 3014 | 620 / 590 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Quebra-Guarda — executada, dano 0, MP −50 | 3007 / 3014 | 581 / 579 |
| 8 | p2 → p1 (score) | Cutelada — executada, dano 467, MP −85 | Ataque básico — executada, dano 0 | 3007 / 2547 | 527 / 618 |
| 9 | p1 → p2 (score) | Mira Calma — executada, dano 726, MP −116 | Escudo Protetor — executada, dano 0, MP −77 | 3007 / 1821 | 442 / 580 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 215 | Tomar Fôlego — cancelada por controle | 3007 / 1606 | 473 / 619 |
| 11 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Tomar Fôlego — executada, dano 0, MP −66 | 3007 / 2272 | 393 / 592 |
| 12 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 485, MP −82 | 2522 / 2490 | 354 / 549 |
| 13 | p1 → p2 (score) | Cutelada — executada, dano 636, MP −85 | Escudo Protetor — executada, dano 0, MP −77 | 2522 / 1696 | 300 / 511 |
| 14 | p2 → p1 (score) | Mira Calma — executada, dano 553, MP −116 | Quebra-Guarda — executada, dano 0, MP −50 | 2522 / 985 | 215 / 500 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 203 | Mira Calma — executada, dano 581, MP −82 | 1941 / 885 | 246 / 457 |
| 16 | p2 → p1 (score) | Veterania — executada, dano 0, MP −111 | Tomar Fôlego — executada, dano 0, MP −66 | 1941 / 1551 | 166 / 430 |
| 17 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −70 | Escudo Protetor — executada, dano 0, MP −77 | 1941 / 1393 | 127 / 392 |
| 18 | p2 → p1 (score) | Cutelada — executada, dano 484, MP −85 | Mira Calma — executada, dano 678, MP −82 | 1263 / 1056 | 73 / 349 |
| 19 | p2 → p1 (score) | Ataque básico — executada, dano 179 | Quebra-Guarda — cancelada por controle | 1263 / 719 | 104 / 388 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 235 | Quebra-Guarda — cancelada por controle | 1263 / 484 | 135 / 427 |
| 21 | p1 → p2 (score) | Veterania — executada, dano 0, MP −111 | Tomar Fôlego — executada, dano 0, MP −66 | 1263 / 1150 | 55 / 400 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 235 | Escudo Protetor — executada, dano 0, MP −77 | 1263 / 915 | 86 / 362 |
| 23 | p2 → p1 (score) | Estocada Seca — cancelada por morte | Mira Calma — executada, dano 1323, MP −82 | -60 / 1510 | 86 / 319 |

#### Oitavas 2 — fnxLNTC × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W24 | fnxLNTC | Guerreiro | 22 | 29.52 | Golpe Poderoso, Investida, Couraça Improvisada, Berro de Ferro | defesa + sustento |
| p2 | W34 | LuquEt4 | Guerreiro | 23 | 29.87 | Golpe Duplo, Grito de Guerra, Cutelada, Areia no Chão | crítico |

- Seed da partida: `15604872752174960703`
- Rodadas: **47**
- Vencedor: **LuquEt4** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2483/7257 (34.2%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fnxLNTC | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 4774 (4774 + 0) | 6173 (6173 + 0) |
| Cura (skill + roubo de vida) | 799 (0 + 799) | 0 (0 + 0) |
| MP gasto em ações | 1787 | 1402 |
| Skills / ataques básicos | 33 / 14 | 17 / 28 |
| Acertos / erros | 21 / 6 | 32 / 0 |
| Críticos (dano) | 3 (1219) | 10 (2816) |
| Agiu primeiro (rodadas) | 29 | 18 |
| Ações perdidas por controle | 0 | 2 |

Efeitos relevantes:
- fnxLNTC aplicou: hexed (rodada 6), hexed (rodada 10), fear (rodada 10), hexed (rodada 14), hexed (rodada 18), fear (rodada 18), stun (rodada 20), hexed (rodada 22), hexed (rodada 31), hexed (rodada 37), stun (rodada 39), hexed (rodada 43)
- fnxLNTC tentou sem sucesso: hexed (rodada 2), stun (rodada 3), poison (rodada 3), fear (rodada 6), stun (rodada 7), poison (rodada 7), stun (rodada 11), poison (rodada 11), fear (rodada 14), stun (rodada 15), poison (rodada 15), stun (rodada 16), poison (rodada 16), stun (rodada 16), stun (rodada 19), poison (rodada 19), stun (rodada 20), poison (rodada 20), fear (rodada 22), stun (rodada 23), poison (rodada 23), stun (rodada 24), poison (rodada 24), stun (rodada 24), hexed (rodada 26), stun (rodada 28), poison (rodada 28), stun (rodada 29), poison (rodada 29), stun (rodada 30), poison (rodada 30), fear (rodada 31), stun (rodada 32), poison (rodada 32), stun (rodada 33), poison (rodada 33), stun (rodada 35), poison (rodada 35), stun (rodada 36), poison (rodada 36), fear (rodada 37), stun (rodada 38), poison (rodada 38), poison (rodada 39), stun (rodada 42), poison (rodada 42), fear (rodada 43), stun (rodada 44), poison (rodada 44), stun (rodada 47), poison (rodada 47)
- fnxLNTC ativou: Couraça Improvisada ×10
- LuquEt4 aplicou: slowed (rodada 2), slowed (rodada 26), slowed (rodada 35), vulnerable (rodada 35), slowed (rodada 40)
- LuquEt4 tentou sem sucesso: vulnerable (rodada 2), stun (rodada 3), frailty (rodada 3), stun (rodada 4), slowed (rodada 6), stun (rodada 7), frailty (rodada 7), stun (rodada 8), stun (rodada 10), stun (rodada 11), slowed (rodada 12), stun (rodada 13), stun (rodada 14), stun (rodada 15), slowed (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), slowed (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), vulnerable (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), slowed (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 36), stun (rodada 37), stun (rodada 38), vulnerable (rodada 40), stun (rodada 41), stun (rodada 42), stun (rodada 43), slowed (rodada 44), stun (rodada 45), stun (rodada 46), stun (rodada 47)
- LuquEt4 ativou: Grito de Guerra ×3

Rodada a rodada:

| Rodada | Ordem (critério) | fnxLNTC (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Grito de Guerra — executada, dano 0, MP −100 | 5355 / 7257 | 889 / 673 |
| 2 | p2 → p1 (score) | Berro de Ferro — executada, dano 0, MP −52 | Areia no Chão — executada, dano 0, MP −70 | 5355 / 7257 | 856 / 618 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 268, MP −47 | Golpe Duplo — executada, dano 407, MP −116 | 4993 / 6989 | 828 / 517 |
| 4 | p2 → p1 (score) | Investida — executada, dano 0, MP −53 | Cutelada — executada, dano 734, MP −85 | 4259 / 6989 | 794 / 447 |
| 5 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Grito de Guerra — executada, dano 0, MP −100 | 4259 / 6989 | 751 / 362 |
| 6 | p2 → p1 (score) | Berro de Ferro — executada, dano 0, MP −52 | Areia no Chão — executada, dano 0, MP −70 | 4259 / 6989 | 718 / 307 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 268, MP −47 | Golpe Duplo — executada, dano 284, MP −116 | 4020 / 6721 | 690 / 206 |
| 8 | p2 → p1 (score) | Investida — executada, dano 0, MP −53 | Cutelada — executada, dano 286, MP −85 | 3734 / 6721 | 656 / 136 |
| 9 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Grito de Guerra — executada, dano 0, MP −100 | 3734 / 6721 | 613 / 51 |
| 10 | p2 → p1 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 128 | 3606 / 6721 | 580 / 66 |
| 11 | p2 → p1 (score) | Golpe Poderoso — executada, dano 494, MP −47 | Ataque básico — executada, dano 238 | 3451 / 6227 | 552 / 81 |
| 12 | p2 → p1 (score) | Investida — executada, dano 0, MP −53 | Areia no Chão — executada, dano 0, MP −70 | 3451 / 6227 | 518 / 26 |
| 13 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 188 | 3263 / 6227 | 475 / 41 |
| 14 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 182 | 3081 / 6227 | 442 / 56 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 268, MP −47 | Ataque básico — executada, dano 142 | 2984 / 5959 | 414 / 71 |
| 16 | p1 → p2 (score) | Investida — executada, dano 305, MP −53 | Areia no Chão — executada, dano 0, MP −70 | 3035 / 5654 | 380 / 16 |
| 17 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 188 | 2847 / 5654 | 337 / 31 |
| 18 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 95 | 2752 / 5654 | 304 / 46 |
| 19 | p1 → p2 (score) | Golpe Poderoso — executada, dano 248, MP −47 | Ataque básico — executada, dano 142 | 2652 / 5406 | 276 / 61 |
| 20 | p1 → p2 (score) | Investida — executada, dano 250, MP −53 | Ataque básico — cancelada por controle | 2694 / 5156 | 242 / 76 |
| 21 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Areia no Chão — executada, dano 0, MP −70 | 2694 / 5156 | 199 / 21 |
| 22 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 95 | 2599 / 5156 | 166 / 36 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 458, MP −47 | Ataque básico — executada, dano 270 | 2406 / 4698 | 138 / 51 |
| 24 | p1 → p2 (score) | Investida — executada, dano 250, MP −53 | Ataque básico — executada, dano 279 | 2169 / 4448 | 104 / 66 |
| 25 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 98 | 2071 / 4448 | 61 / 81 |
| 26 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Areia no Chão — executada, dano 0, MP −70 | 2071 / 4448 | 28 / 26 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 188 | 1883 / 4448 | 47 / 41 |
| 28 | p2 → p1 (score) | Golpe Poderoso — executada, dano 248, MP −47 | Ataque básico — executada, dano 147 | 1778 / 4200 | 19 / 56 |
| 29 | p2 → p1 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 147 | 1655 / 4055 | 38 / 71 |
| 30 | p1 → p2 (score) | Ataque básico — executada, dano 145 | Areia no Chão — executada, dano 0, MP −70 | 1679 / 3910 | 57 / 16 |
| 31 | p1 → p2 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 270 | 1409 / 3910 | 24 / 31 |
| 32 | p1 → p2 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 142 | 1291 / 3765 | 43 / 46 |
| 33 | p1 → p2 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 279 | 1036 / 3620 | 62 / 61 |
| 34 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 98 | 938 / 3620 | 19 / 76 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 145 | Areia no Chão — executada, dano 0, MP −70 | 962 / 3475 | 38 / 21 |
| 36 | p2 → p1 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 118 | 868 / 3330 | 57 / 36 |
| 37 | p2 → p1 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 176 | 692 / 3330 | 24 / 51 |
| 38 | p2 → p1 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 171 | 545 / 3185 | 43 / 66 |
| 39 | p1 → p2 (score) | Ataque básico — executada, dano 267 | Ataque básico — cancelada por controle | 590 / 2918 | 62 / 81 |
| 40 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Areia no Chão — executada, dano 0, MP −70 | 590 / 2918 | 19 / 26 |
| 41 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 98 | 492 / 2918 | 38 / 41 |
| 42 | p2 → p1 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 98 | 418 / 2773 | 57 / 56 |
| 43 | p2 → p1 (score) | Berro de Ferro — executada, dano 0, MP −52 | Ataque básico — executada, dano 147 | 271 / 2773 | 24 / 71 |
| 44 | p1 → p2 (score) | Ataque básico — executada, dano 145 | Areia no Chão — executada, dano 0, MP −70 | 295 / 2628 | 43 / 16 |
| 45 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 142 | 153 / 2628 | 62 / 31 |
| 46 | p1 → p2 (score) | Couraça Improvisada — executada, dano 0, MP −62 | Ataque básico — executada, dano 98 | 55 / 2628 | 19 / 46 |
| 47 | p1 → p2 (score) | Ataque básico — executada, dano 145 | Ataque básico — executada, dano 98 | -19 / 2483 | 38 / 61 |

#### Oitavas 3 — MeikodRJ × DavyJones

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W26 | MeikodRJ | Guerreiro | 22 | 29.75 | Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno | sustento |
| p2 | W29 | DavyJones | Guerreiro | 22 | 29.98 | Golpe Poderoso, Mira Calma, Paciência do Coveiro, Respirar Fundo | defesa + sustento |

- Seed da partida: `17158717865381310413`
- Rodadas: **26**
- Vencedor: **MeikodRJ** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 895/4969 (18.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | MeikodRJ | DavyJones |
|---|---|---|
| Dano causado (golpes + DoT) | 7102 (6250 + 852) | 7605 (7295 + 310) |
| Cura (skill + roubo de vida) | 3531 (3039 + 492) | 1765 (533 + 1232) |
| MP gasto em ações | 1178 | 1274 |
| Skills / ataques básicos | 18 / 8 | 18 / 6 |
| Acertos / erros | 18 / 5 | 19 / 1 |
| Críticos (dano) | 4 (2164) | 0 (0) |
| Agiu primeiro (rodadas) | 20 | 6 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- MeikodRJ aplicou: stun (rodada 2), bleed (rodada 11), vulnerable (rodada 14), bleed (rodada 24)
- MeikodRJ tentou sem sucesso: stun (rodada 1), bleed (rodada 1), bleed (rodada 2), vulnerable (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 5), bleed (rodada 5), stun (rodada 6), bleed (rodada 6), vulnerable (rodada 6), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), vulnerable (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 11), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 20), bleed (rodada 20), stun (rodada 21), bleed (rodada 21), stun (rodada 22), bleed (rodada 22), stun (rodada 24), stun (rodada 25), bleed (rodada 25), stun (rodada 26), bleed (rodada 26)
- DavyJones aplicou: poison (rodada 1), frailty (rodada 1), vulnerable (rodada 15)
- DavyJones tentou sem sucesso: stun (rodada 2), bleed (rodada 2), stun (rodada 4), bleed (rodada 4), stun (rodada 5), bleed (rodada 5), vulnerable (rodada 5), stun (rodada 6), bleed (rodada 6), poison (rodada 7), stun (rodada 9), bleed (rodada 9), vulnerable (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 12), bleed (rodada 12), poison (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), stun (rodada 17), bleed (rodada 17), stun (rodada 18), bleed (rodada 18), stun (rodada 19), bleed (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 21), bleed (rodada 21), stun (rodada 22), bleed (rodada 22), stun (rodada 23), bleed (rodada 23), stun (rodada 24), bleed (rodada 24), stun (rodada 25), bleed (rodada 25)

Rodada a rodada:

| Rodada | Ordem (critério) | MeikodRJ (p1) | DavyJones (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Golpe Poderoso — executada, dano 439, MP −47 | Paciência do Coveiro — executada, dano 0, MP −125 | 4969 / 4894 | 782 / 704 |
| 2 | p2 → p1 (score) | Mira Calma — executada, dano 610, MP −103 | Golpe Poderoso — executada, dano 376, MP −47 | 3975 / 4347 | 695 / 677 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 439, MP −47 | Mira Calma — cancelada por controle | 3975 / 3908 | 664 / 697 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 376, MP −47 | 3540 / 3971 | 680 / 670 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Mira Calma — executada, dano 907, MP −103 | 2630 / 3854 | 649 / 587 |
| 6 | p1 → p2 (score) | Mira Calma — executada, dano 530, MP −103 | Golpe Poderoso — executada, dano 348, MP −47 | 2319 / 3383 | 562 / 560 |
| 7 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Paciência do Coveiro — executada, dano 0, MP −125 | 3332 / 3383 | 495 / 455 |
| 8 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 0, MP −47 | 3388 / 3112 | 464 / 428 |
| 9 | p1 → p2 (score) | Mira Calma — executada, dano 530, MP −103 | Mira Calma — executada, dano 789, MP −103 | 2710 / 2716 | 377 / 345 |
| 10 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 348, MP −47 | 2418 / 2504 | 346 / 318 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Respirar Fundo — executada, dano 0, MP −73 | 2451 / 2666 | 362 / 265 |
| 12 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Golpe Poderoso — executada, dano 348, MP −47 | 3116 / 2512 | 295 / 238 |
| 13 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Paciência do Coveiro — executada, dano 0, MP −125 | 3116 / 2512 | 264 / 133 |
| 14 | p1 → p2 (score) | Mira Calma — executada, dano 795, MP −103 | Golpe Poderoso — executada, dano 348, MP −47 | 2934 / 1776 | 177 / 106 |
| 15 | p1 → p2 (score) | Golpe Poderoso — executada, dano 491, MP −47 | Mira Calma — executada, dano 789, MP −103 | 2248 / 1419 | 146 / 23 |
| 16 | p2 → p1 (score) | Ataque básico — executada, dano 158 | Ataque básico — executada, dano 239 | 2042 / 1301 | 162 / 43 |
| 17 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Ataque básico — executada, dano 239 | 2816 / 1341 | 95 / 63 |
| 18 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Golpe Poderoso — executada, dano 348, MP −47 | 2468 / 1400 | 64 / 36 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 199 | 2269 / 1433 | 80 / 56 |
| 20 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 348, MP −47 | 1977 / 1221 | 49 / 29 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Ataque básico — executada, dano 199 | 1811 / 1096 | 65 / 49 |
| 22 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Golpe Poderoso — executada, dano 348, MP −47 | 1519 / 884 | 34 / 22 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 199 | 1320 / 917 | 50 / 42 |
| 24 | p1 → p2 (score) | Golpe Poderoso — executada, dano 271, MP −47 | Ataque básico — executada, dano 199 | 1177 / 466 | 19 / 62 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Golpe Poderoso — executada, dano 348, MP −47 | 862 / 154 | 35 / 35 |
| 26 | p1 → p2 (score) | Ataque básico — executada, dano 158 | Ataque básico — cancelada por morte | 895 / -4 | 51 / 35 |

#### Oitavas 4 — lubatv × aXtLOL

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W23 | lubatv | Guerreiro | 22 | 29.17 | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | crítico + sustento |
| p2 | W43 | aXtLOL | Guerreiro | 23 | 29.75 | Travar o Pulso, Mira Calma, Ferro Contra Ferro, Ritmo de Duelo | sustento |

- Seed da partida: `3009443185611807458`
- Rodadas: **31**
- Vencedor: **lubatv** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1877/5275 (35.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | lubatv | aXtLOL |
|---|---|---|
| Dano causado (golpes + DoT) | 5851 (5851 + 0) | 3398 (3398 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 131 (0 + 131) |
| MP gasto em ações | 1392 | 2082 |
| Skills / ataques básicos | 15 / 16 | 22 / 8 |
| Acertos / erros | 25 / 3 | 9 / 9 |
| Críticos (dano) | 8 (2242) | 1 (793) |
| Agiu primeiro (rodadas) | 19 | 12 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- lubatv aplicou: vulnerable (rodada 29)
- lubatv tentou sem sucesso: stun (rodada 2), stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), vulnerable (rodada 6), stun (rodada 10), stun (rodada 11), stun (rodada 12), vulnerable (rodada 12), stun (rodada 14), stun (rodada 14), stun (rodada 15), vulnerable (rodada 15), stun (rodada 17), stun (rodada 18), stun (rodada 19), vulnerable (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 22), vulnerable (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 26), vulnerable (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 30), stun (rodada 31)
- lubatv ativou: Postura Impecável ×3
- aXtLOL aplicou: weakened (rodada 2), weakened (rodada 4), vulnerable (rodada 7), weakened (rodada 8), slowed (rodada 8), weakened (rodada 12), weakened (rodada 14), weakened (rodada 23), slowed (rodada 23), weakened (rodada 28), slowed (rodada 28)
- aXtLOL tentou sem sucesso: slowed (rodada 2), bleed (rodada 4), bleed (rodada 7), bleed (rodada 9), weakened (rodada 9), bleed (rodada 10), vulnerable (rodada 10), slowed (rodada 12), bleed (rodada 13), vulnerable (rodada 13), bleed (rodada 14), bleed (rodada 15), bleed (rodada 17), vulnerable (rodada 17), weakened (rodada 19), bleed (rodada 26)
- aXtLOL ativou: Ritmo de Duelo ×6

Rodada a rodada:

| Rodada | Ordem (critério) | lubatv (p1) | aXtLOL (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Postura Impecável — executada, dano 0, MP −131 | Ritmo de Duelo — executada, dano 0, MP −105 | 5275 / 5454 | 777 / 661 |
| 2 | p1 → p2 (score) | Esmagar — executada, dano 466, MP −144 | Travar o Pulso — executada, dano 0, MP −70 | 5275 / 4988 | 651 / 638 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 419, MP −63 | Mira Calma — executada, dano 0, MP −116 | 5275 / 4569 | 606 / 569 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 248 | Ferro Contra Ferro — executada, dano 313, MP −84 | 4962 / 4333 | 624 / 532 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 104 | Ataque básico — executada, dano 0 | 4962 / 4229 | 642 / 579 |
| 6 | p1 → p2 (score) | Quebra-Guarda — executada, dano 221, MP −63 | Ritmo de Duelo — executada, dano 0, MP −105 | 4962 / 4008 | 597 / 521 |
| 7 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −131 | Mira Calma — executada, dano 793, MP −116 | 4169 / 4039 | 484 / 452 |
| 8 | p1 → p2 (score) | Esmagar — executada, dano 0, MP −144 | Travar o Pulso — executada, dano 0, MP −70 | 4169 / 4039 | 358 / 429 |
| 9 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Ferro Contra Ferro — executada, dano 313, MP −84 | 3856 / 4051 | 313 / 392 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 165 | Mira Calma — executada, dano 460, MP −116 | 3396 / 3904 | 331 / 323 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 127 | Ritmo de Duelo — executada, dano 0, MP −105 | 3396 / 3777 | 349 / 265 |
| 12 | p2 → p1 (score) | Quebra-Guarda — executada, dano 332, MP −63 | Travar o Pulso — executada, dano 0, MP −70 | 3396 / 3445 | 304 / 242 |
| 13 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −131 | Mira Calma — executada, dano 460, MP −116 | 2936 / 3463 | 191 / 173 |
| 14 | p1 → p2 (score) | Esmagar — executada, dano 437, MP −144 | Ferro Contra Ferro — executada, dano 313, MP −84 | 2623 / 3038 | 65 / 136 |
| 15 | p1 → p2 (score) | Quebra-Guarda — executada, dano 516, MP −63 | Ataque básico — executada, dano 143 | 2480 / 2527 | 20 / 183 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ritmo de Duelo — executada, dano 0, MP −105 | 2480 / 2527 | 38 / 125 |
| 17 | p1 → p2 (score) | Ataque básico — executada, dano 191 | Mira Calma — executada, dano 460, MP −116 | 2020 / 2354 | 56 / 56 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 0 | 2020 / 2227 | 74 / 103 |
| 19 | p2 → p1 (score) | Quebra-Guarda — executada, dano 277, MP −63 | Travar o Pulso — executada, dano 0, MP −70 | 2020 / 1950 | 29 / 80 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 127 | Ataque básico — executada, dano 0 | 2020 / 1823 | 47 / 127 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 127 | Ritmo de Duelo — executada, dano 0, MP −105 | 2020 / 1696 | 65 / 69 |
| 22 | p2 → p1 (score) | Quebra-Guarda — executada, dano 277, MP −63 | Ataque básico — executada, dano 0 | 2020 / 1419 | 20 / 116 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 104 | Travar o Pulso — executada, dano 0, MP −70 | 2020 / 1315 | 38 / 93 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 104 | Ferro Contra Ferro — executada, dano 0, MP −84 | 2020 / 1211 | 56 / 56 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 191 | Ataque básico — executada, dano 0 | 2020 / 1020 | 74 / 103 |
| 26 | p1 → p2 (score) | Quebra-Guarda — executada, dano 416, MP −63 | Ataque básico — executada, dano 143 | 1877 / 609 | 29 / 150 |
| 27 | p1 → p2 (score) | Ataque básico — executada, dano 191 | Ritmo de Duelo — executada, dano 0, MP −105 | 1877 / 418 | 47 / 92 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 157 | Travar o Pulso — executada, dano 0, MP −70 | 1877 / 261 | 65 / 69 |
| 29 | p2 → p1 (score) | Quebra-Guarda — executada, dano 221, MP −63 | Ataque básico — executada, dano 0 | 1877 / 40 | 20 / 116 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 39 | Mira Calma — executada, dano 0, MP −116 | 1877 / 1 | 38 / 47 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Ataque básico — cancelada por morte | 1877 / -152 | 56 / 47 |

#### Oitavas 5 — frttt × NOBRU

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W60 | frttt | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca | sustento |
| p2 | W40 | NOBRU | Guerreiro | 23 | 29.75 | Cutelada, Investida, Postura de Muro, Imortal | sustento |

- Seed da partida: `209543163798074548`
- Rodadas: **24**
- Vencedor: **frttt** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2170/5379 (40.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | NOBRU |
|---|---|---|
| Dano causado (golpes + DoT) | 6559 (4597 + 1962) | 3938 (3938 + 0) |
| Cura (skill + roubo de vida) | 729 (0 + 729) | 1002 (0 + 1002) |
| MP gasto em ações | 1790 | 1513 |
| Skills / ataques básicos | 20 / 4 | 17 / 5 |
| Acertos / erros | 13 / 1 | 14 / 2 |
| Críticos (dano) | 4 (1958) | 0 (0) |
| Agiu primeiro (rodadas) | 12 | 12 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- frttt aplicou: stun (rodada 9), vulnerable (rodada 9), bleed (rodada 12), bleed (rodada 17), bleed (rodada 22)
- frttt tentou sem sucesso: bleed (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 5), bleed (rodada 5), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), vulnerable (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 19), bleed (rodada 19), vulnerable (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 23), bleed (rodada 23), stun (rodada 24), bleed (rodada 24), vulnerable (rodada 24)
- frttt ativou: Pausa Útil ×5
- NOBRU tentou sem sucesso: bleed (rodada 3), bleed (rodada 4), stun (rodada 4), bleed (rodada 6), bleed (rodada 7), stun (rodada 7), bleed (rodada 11), bleed (rodada 12), stun (rodada 12), bleed (rodada 13), bleed (rodada 15), bleed (rodada 17), bleed (rodada 18), stun (rodada 18), bleed (rodada 19), bleed (rodada 21), bleed (rodada 22), bleed (rodada 23), stun (rodada 23)
- NOBRU ativou: Postura de Muro ×4, Imortal ×2

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | NOBRU (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −52 | Postura de Muro — executada, dano 0, MP −76 | 5379 / 5469 | 990 / 948 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Imortal — executada, dano 0, MP −228 | 5379 / 5469 | 962 / 744 |
| 3 | p2 → p1 (score) | Golpe Devastador — executada, dano 280, MP −120 | Cutelada — executada, dano 351, MP −85 | 5072 / 5189 | 884 / 683 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 565, MP −116 | Investida — executada, dano 372, MP −59 | 4790 / 4728 | 810 / 648 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 153 | Postura de Muro — executada, dano 0, MP −76 | 4814 / 4575 | 852 / 596 |
| 6 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Cutelada — executada, dano 351, MP −85 | 4463 / 4673 | 828 / 535 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Investida — executada, dano 372, MP −59 | 4091 / 4777 | 800 / 500 |
| 8 | p2 → p1 (score) | Golpe Devastador — executada, dano 142, MP −120 | Imortal — executada, dano 0, MP −228 | 4113 / 4635 | 722 / 296 |
| 9 | p1 → p2 (score) | Mira Calma — executada, dano 143, MP −116 | Postura de Muro — cancelada por controle | 4135 / 4492 | 648 / 320 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 184 | Postura de Muro — executada, dano 0, MP −76 | 4164 / 4308 | 690 / 268 |
| 11 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Cutelada — executada, dano 351, MP −85 | 3813 / 4406 | 666 / 207 |
| 12 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Investida — executada, dano 305, MP −59 | 3508 / 4491 | 638 / 172 |
| 13 | p2 → p1 (score) | Golpe Devastador — executada, dano 350, MP −120 | Ataque básico — executada, dano 175 | 3389 / 3972 | 560 / 196 |
| 14 | p1 → p2 (score) | Mira Calma — executada, dano 786, MP −116 | Postura de Muro — executada, dano 0, MP −76 | 3514 / 2968 | 486 / 144 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 122 | Cutelada — executada, dano 351, MP −85 | 3182 / 2726 | 528 / 83 |
| 16 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Investida — executada, dano 0, MP −59 | 3182 / 2726 | 504 / 48 |
| 17 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 175 | 3007 / 2775 | 476 / 72 |
| 18 | p1 → p2 (score) | Golpe Devastador — executada, dano 0, MP −120 | Investida — executada, dano 305, MP −59 | 2702 / 2642 | 398 / 37 |
| 19 | p1 → p2 (score) | Mira Calma — executada, dano 786, MP −116 | Ataque básico — executada, dano 175 | 2652 / 1687 | 324 / 61 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 244 | Investida — executada, dano 0, MP −59 | 2691 / 1225 | 366 / 26 |
| 21 | p1 → p2 (score) | Pausa Útil — executada, dano 0, MP −52 | Ataque básico — executada, dano 175 | 2516 / 1274 | 342 / 50 |
| 22 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 175 | 2341 / 1105 | 314 / 74 |
| 23 | p1 → p2 (score) | Golpe Devastador — executada, dano 350, MP −120 | Investida — executada, dano 305, MP −59 | 2092 / 622 | 236 / 39 |
| 24 | p1 → p2 (score) | Mira Calma — executada, dano 492, MP −116 | Ataque básico — cancelada por morte | 2170 / -88 | 162 / 63 |

#### Oitavas 6 — Gaules × XANDAOOGOD

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W36 | Gaules | Guerreiro | 22 | 29.98 | Mão Dupla, Peso do Machado, Estocada Seca, Fúria | crítico + controle |
| p2 | W47 | XANDAOOGOD | Guerreiro | 23 | 29.64 | Esmagar, Mira Calma, Leitura de Terreno, Veterania | defesa |

- Seed da partida: `17965660940518739940`
- Rodadas: **13**
- Vencedor: **XANDAOOGOD** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2385/5684 (42.0%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | Gaules | XANDAOOGOD |
|---|---|---|
| Dano causado (golpes + DoT) | 3299 (1483 + 1816) | 5455 (5039 + 416) |
| Cura (skill + roubo de vida) | 72 (0 + 72) | 0 (0 + 0) |
| MP gasto em ações | 869 | 1164 |
| Skills / ataques básicos | 8 / 3 | 9 / 3 |
| Acertos / erros | 3 / 2 | 9 / 0 |
| Críticos (dano) | 3 (1483) | 1 (1314) |
| Agiu primeiro (rodadas) | 9 | 4 |
| Ações perdidas por controle | 1 | 1 |

Efeitos relevantes:
- Gaules aplicou: bleed (rodada 2), stun (rodada 4), bleed (rodada 4)
- Gaules tentou sem sucesso: bleed (rodada 4), poison (rodada 4), bleed (rodada 7), stun (rodada 8), bleed (rodada 8), poison (rodada 8), bleed (rodada 8), stun (rodada 10), bleed (rodada 10), poison (rodada 10), bleed (rodada 11)
- Gaules ativou: Fúria ×3
- XANDAOOGOD aplicou: stun (rodada 2), bleed (rodada 5), vulnerable (rodada 8)
- XANDAOOGOD tentou sem sucesso: bleed (rodada 2), poison (rodada 2), bleed (rodada 3), poison (rodada 3), vulnerable (rodada 3), poison (rodada 5), bleed (rodada 7), poison (rodada 7), stun (rodada 7), bleed (rodada 8), poison (rodada 8), bleed (rodada 9), poison (rodada 9), bleed (rodada 10), poison (rodada 10), bleed (rodada 12), poison (rodada 12), stun (rodada 12), bleed (rodada 13), poison (rodada 13), vulnerable (rodada 13)
- XANDAOOGOD ativou: Veterania ×3

Rodada a rodada:

| Rodada | Ordem (critério) | Gaules (p1) | XANDAOOGOD (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Fúria — executada, dano 0, MP −171 | Veterania — executada, dano 0, MP −111 | 5209 / 5684 | 524 / 926 |
| 2 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Esmagar — executada, dano 515, MP −161 | 4694 / 5457 | 482 / 789 |
| 3 | p1 → p2 (score) | Mão Dupla — cancelada por controle | Mira Calma — executada, dano 741, MP −116 | 3953 / 5230 | 502 / 697 |
| 4 | p1 → p2 (score) | Mão Dupla — executada, dano 617, MP −85 | Ataque básico — cancelada por controle | 3983 / 4159 | 437 / 721 |
| 5 | p2 → p1 (score) | Fúria — executada, dano 0, MP −171 | Ataque básico — executada, dano 209 | 3566 / 3705 | 286 / 745 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Veterania — executada, dano 0, MP −111 | 3358 / 3251 | 306 / 658 |
| 7 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Esmagar — executada, dano 515, MP −161 | 2843 / 3251 | 264 / 521 |
| 8 | p1 → p2 (score) | Mão Dupla — executada, dano 617, MP −85 | Mira Calma — executada, dano 644, MP −116 | 2229 / 2634 | 199 / 429 |
| 9 | p2 → p1 (score) | Fúria — executada, dano 0, MP −171 | Ataque básico — executada, dano 248 | 1981 / 2634 | 48 / 453 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 249 | Ataque básico — executada, dano 209 | 1784 / 2385 | 68 / 477 |
| 11 | p1 → p2 (score) | Estocada Seca — executada, dano 0, MP −62 | Veterania — executada, dano 0, MP −111 | 1784 / 2385 | 26 / 390 |
| 12 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Esmagar — executada, dano 1314, MP −161 | 470 / 2385 | 46 / 253 |
| 13 | p2 → p1 (score) | Ataque básico — cancelada por morte | Mira Calma — executada, dano 644, MP −116 | -174 / 2385 | 46 / 161 |

#### Oitavas 7 — jovirone × fer

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W22 | jovirone | Guerreiro | 24 | 29.52 | Marca do Açougueiro, Quebra-Guarda, Disciplina de Forja, Sangue nos Olhos | sustento |
| p2 | W64 | fer | Guerreiro | 23 | 29.98 | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | defesa + sustento |

- Seed da partida: `18064589888594402206`
- Rodadas: **36**
- Vencedor: **fer** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2215/5977 (37.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | jovirone | fer |
|---|---|---|
| Dano causado (golpes + DoT) | 4776 (3820 + 956) | 8158 (8158 + 0) |
| Cura (skill + roubo de vida) | 1671 (0 + 1671) | 1014 (0 + 1014) |
| MP gasto em ações | 1925 | 1806 |
| Skills / ataques básicos | 21 / 13 | 26 / 10 |
| Acertos / erros | 14 / 6 | 30 / 2 |
| Críticos (dano) | 2 (565) | 12 (4022) |
| Agiu primeiro (rodadas) | 26 | 10 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- jovirone aplicou: vulnerable (rodada 2), vulnerable (rodada 7), vulnerable (rodada 17), vulnerable (rodada 18), vulnerable (rodada 23), vulnerable (rodada 27), vulnerable (rodada 28), vulnerable (rodada 32), bleed (rodada 32)
- jovirone tentou sem sucesso: bleed (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), bleed (rodada 7), stun (rodada 8), vulnerable (rodada 8), vulnerable (rodada 12), stun (rodada 14), stun (rodada 15), bleed (rodada 17), stun (rodada 18), vulnerable (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), bleed (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 33), vulnerable (rodada 33), stun (rodada 34), stun (rodada 35)
- jovirone ativou: Disciplina de Forja ×7
- fer aplicou: weakened (rodada 3), weakened (rodada 11), stun (rodada 29)
- fer tentou sem sucesso: stun (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), weakened (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 9), weakened (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 14), stun (rodada 15), weakened (rodada 15), stun (rodada 16), stun (rodada 17), weakened (rodada 17), stun (rodada 18), stun (rodada 20), stun (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 36)
- fer ativou: Juramento da Muralha ×4
- Leis disparadas por fer: FERIDA ABERTA (rodada 32)

Rodada a rodada:

| Rodada | Ordem (critério) | jovirone (p1) | fer (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Juramento da Muralha — executada, dano 0, MP −152 | 6345 / 5977 | 1073 / 951 |
| 2 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 238, MP −52 | 6107 / 5977 | 1026 / 921 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 422, MP −79 | Soco de Placa — executada, dano 232, MP −61 | 6060 / 5585 | 978 / 882 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 88 | Golpe Poderoso — executada, dano 238, MP −52 | 5860 / 5527 | 1009 / 852 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Soco de Placa — executada, dano 372, MP −61 | 5488 / 5575 | 1040 / 813 |
| 6 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Golpe Poderoso — executada, dano 319, MP −52 | 5169 / 5616 | 953 / 783 |
| 7 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Juramento da Muralha — executada, dano 0, MP −152 | 5169 / 5616 | 906 / 653 |
| 8 | p1 → p2 (score) | Quebra-Guarda — executada, dano 263, MP −79 | Golpe Poderoso — executada, dano 238, MP −52 | 5046 / 5383 | 858 / 623 |
| 9 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Soco de Placa — executada, dano 372, MP −61 | 4674 / 5431 | 889 / 584 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 296, MP −52 | 4378 / 5469 | 920 / 554 |
| 11 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Soco de Placa — executada, dano 498, MP −61 | 3880 / 5533 | 833 / 515 |
| 12 | p2 → p1 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 220, MP −52 | 3660 / 5561 | 786 / 485 |
| 13 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −79 | Juramento da Muralha — executada, dano 0, MP −152 | 3660 / 5561 | 738 / 355 |
| 14 | p1 → p2 (score) | Ataque básico — executada, dano 143 | Golpe Poderoso — executada, dano 354, MP −52 | 3368 / 5464 | 769 / 325 |
| 15 | p1 → p2 (score) | Ataque básico — executada, dano 89 | Soco de Placa — executada, dano 498, MP −61 | 2909 / 5439 | 800 / 286 |
| 16 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Golpe Poderoso — executada, dano 296, MP −52 | 2613 / 5477 | 713 / 256 |
| 17 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Soco de Placa — executada, dano 232, MP −61 | 2381 / 5507 | 666 / 217 |
| 18 | p1 → p2 (score) | Quebra-Guarda — executada, dano 534, MP −79 | Golpe Poderoso — executada, dano 220, MP −52 | 2395 / 5001 | 618 / 187 |
| 19 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Juramento da Muralha — executada, dano 0, MP −152 | 2395 / 5001 | 649 / 57 |
| 20 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 473, MP −52 | 1922 / 5062 | 680 / 27 |
| 21 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Ataque básico — executada, dano 278 | 1644 / 5098 | 593 / 49 |
| 22 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Ataque básico — executada, dano 129 | 1515 / 5114 | 546 / 71 |
| 23 | p1 → p2 (score) | Quebra-Guarda — executada, dano 219, MP −79 | Golpe Poderoso — executada, dano 220, MP −52 | 1391 / 4923 | 498 / 41 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 218 | Ataque básico — executada, dano 207 | 1279 / 4731 | 529 / 63 |
| 25 | p1 → p2 (score) | Ataque básico — executada, dano 218 | Golpe Poderoso — executada, dano 0, MP −52 | 1374 / 4513 | 560 / 33 |
| 26 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Ataque básico — executada, dano 173 | 1201 / 4535 | 473 / 55 |
| 27 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 220, MP −52 | 981 / 4563 | 426 / 25 |
| 28 | p1 → p2 (score) | Quebra-Guarda — executada, dano 477, MP −79 | Ataque básico — executada, dano 207 | 983 / 4112 | 378 / 47 |
| 29 | p1 → p2 (score) | Ataque básico — executada, dano 273 | Ataque básico — executada, dano 129 | 974 / 3855 | 409 / 69 |
| 30 | p1 → p2 (score) | Ataque básico — cancelada por controle | Golpe Poderoso — executada, dano 296, MP −52 | 678 / 3893 | 440 / 39 |
| 31 | p2 → p1 (score) | Disciplina de Forja — executada, dano 0, MP −118 | Ataque básico — executada, dano 278 | 400 / 3929 | 353 / 61 |
| 32 | p1 → p2 (score) | Sangue nos Olhos — executada, dano 0, MP −78 | Golpe Poderoso — executada, dano 220, MP −52 | 180 / 3479 | 306 / 31 |
| 33 | p1 → p2 (score) | Quebra-Guarda — executada, dano 477, MP −79 | Ataque básico — executada, dano 207 | 182 / 2550 | 258 / 53 |
| 34 | p1 → p2 (score) | Ataque básico — executada, dano 218 | Golpe Poderoso — executada, dano 220, MP −52 | 57 / 2360 | 289 / 23 |
| 35 | p1 → p2 (score) | Ataque básico — executada, dano 181 | Ataque básico — executada, dano 0 | 136 / 2179 | 320 / 45 |
| 36 | p2 → p1 (score) | Disciplina de Forja — cancelada por morte | Ataque básico — executada, dano 278 | -142 / 2215 | 320 / 67 |

#### Oitavas 8 — jukes × RNakano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W03 | jukes | Guerreiro | 22 | 28.14 | Golpe Poderoso, Respirar Fundo, Mira Calma, Leitura de Terreno | defesa + sustento |
| p2 | W42 | RNakano | Guerreiro | 24 | 29.64 | Golpe Duplo, Cutelada, Gancho e Corda, Disciplina de Forja | sustento |

- Seed da partida: `9536441814756278971`
- Rodadas: **41**
- Vencedor: **RNakano** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 5109/8159 (62.6%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | jukes | RNakano |
|---|---|---|
| Dano causado (golpes + DoT) | 5424 (5424 + 0) | 8000 (8000 + 0) |
| Cura (skill + roubo de vida) | 2410 (2204 + 206) | 2374 (0 + 2374) |
| MP gasto em ações | 1857 | 2003 |
| Skills / ataques básicos | 27 / 11 | 18 / 23 |
| Acertos / erros | 24 / 5 | 24 / 9 |
| Críticos (dano) | 0 (0) | 0 (0) |
| Agiu primeiro (rodadas) | 1 | 40 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- jukes aplicou: vulnerable (rodada 9)
- jukes tentou sem sucesso: stun (rodada 4), vulnerable (rodada 4), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 12), stun (rodada 13), vulnerable (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 19), vulnerable (rodada 19), stun (rodada 20), stun (rodada 22), stun (rodada 24), stun (rodada 25), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 36), stun (rodada 39), stun (rodada 40)
- jukes ativou: Leitura de Terreno ×5
- RNakano aplicou: stun (rodada 2), frailty (rodada 3), stun (rodada 7)
- RNakano tentou sem sucesso: vulnerable (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), vulnerable (rodada 7), stun (rodada 9), stun (rodada 10), stun (rodada 12), stun (rodada 15), stun (rodada 16), stun (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 23), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 31), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 37), stun (rodada 38), stun (rodada 39), stun (rodada 40), stun (rodada 41)
- RNakano ativou: Disciplina de Forja ×5

Rodada a rodada:

| Rodada | Ordem (critério) | jukes (p1) | RNakano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Disciplina de Forja — executada, dano 0, MP −118 | 5515 / 8159 | 742 / 795 |
| 2 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Gancho e Corda — executada, dano 0, MP −131 | 5515 / 8159 | 770 / 694 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Golpe Duplo — executada, dano 530, MP −130 | 4985 / 8159 | 751 / 594 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 423, MP −103 | Cutelada — executada, dano 684, MP −95 | 4317 / 7736 | 676 / 529 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 243 | 4074 / 7821 | 657 / 559 |
| 6 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Disciplina de Forja — executada, dano 0, MP −118 | 4074 / 7821 | 586 / 471 |
| 7 | p2 → p1 (score) | Golpe Poderoso — cancelada por controle | Gancho e Corda — executada, dano 0, MP −131 | 4074 / 7821 | 614 / 370 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 207, MP −47 | Golpe Duplo — executada, dano 0, MP −130 | 4082 / 7614 | 595 / 270 |
| 9 | p2 → p1 (score) | Mira Calma — executada, dano 423, MP −103 | Cutelada — executada, dano 483, MP −95 | 3615 / 7360 | 520 / 205 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 336, MP −47 | Ataque básico — executada, dano 243 | 3385 / 7109 | 501 / 235 |
| 11 | p1 → p2 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Disciplina de Forja — executada, dano 0, MP −118 | 3385 / 7109 | 430 / 147 |
| 12 | p2 → p1 (score) | Golpe Poderoso — executada, dano 207, MP −47 | Gancho e Corda — executada, dano 0, MP −131 | 3393 / 6902 | 411 / 46 |
| 13 | p2 → p1 (score) | Mira Calma — executada, dano 423, MP −103 | Ataque básico — executada, dano 0 | 3409 / 6479 | 336 / 76 |
| 14 | p2 → p1 (score) | Golpe Poderoso — executada, dano 194, MP −47 | Ataque básico — executada, dano 0 | 3416 / 6285 | 317 / 106 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 151 | Cutelada — executada, dano 483, MP −95 | 2939 / 6303 | 345 / 41 |
| 16 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Ataque básico — executada, dano 243 | 2696 / 6388 | 274 / 71 |
| 17 | p2 → p1 (score) | Respirar Fundo — executada, dano 0, MP −73 | Ataque básico — executada, dano 0 | 3247 / 6388 | 229 / 101 |
| 18 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Cutelada — executada, dano 0, MP −95 | 3247 / 6388 | 210 / 36 |
| 19 | p2 → p1 (score) | Mira Calma — executada, dano 498, MP −103 | Ataque básico — executada, dano 243 | 3023 / 5975 | 135 / 66 |
| 20 | p2 → p1 (score) | Golpe Poderoso — executada, dano 259, MP −47 | Ataque básico — executada, dano 243 | 2790 / 5801 | 116 / 96 |
| 21 | p2 → p1 (score) | Leitura de Terreno — executada, dano 0, MP −99 | Cutelada — executada, dano 483, MP −95 | 2307 / 5970 | 45 / 31 |
| 22 | p2 → p1 (score) | Ataque básico — executada, dano 151 | Ataque básico — executada, dano 0 | 2313 / 5819 | 73 / 61 |
| 23 | p2 → p1 (score) | Respirar Fundo — executada, dano 0, MP −73 | Ataque básico — executada, dano 243 | 2621 / 5904 | 28 / 91 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 151 | Ataque básico — executada, dano 0 | 2627 / 5753 | 56 / 121 |
| 25 | p2 → p1 (score) | Golpe Poderoso — executada, dano 194, MP −47 | Disciplina de Forja — executada, dano 0, MP −118 | 2634 / 5559 | 37 / 33 |
| 26 | p2 → p1 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 0 | 2638 / 5447 | 65 / 63 |
| 27 | p2 → p1 (score) | Golpe Poderoso — executada, dano 194, MP −47 | Ataque básico — executada, dano 243 | 2402 / 5338 | 46 / 93 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 243 | 2163 / 5311 | 74 / 123 |
| 29 | p2 → p1 (score) | Respirar Fundo — executada, dano 0, MP −73 | Cutelada — executada, dano 483, MP −95 | 2231 / 5480 | 29 / 58 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 151 | Ataque básico — executada, dano 0 | 2237 / 5329 | 57 / 88 |
| 31 | p2 → p1 (score) | Golpe Poderoso — executada, dano 259, MP −47 | Ataque básico — executada, dano 243 | 2004 / 5155 | 38 / 118 |
| 32 | p2 → p1 (score) | Ataque básico — executada, dano 112 | Disciplina de Forja — executada, dano 0, MP −118 | 2008 / 5043 | 66 / 30 |
| 33 | p2 → p1 (score) | Golpe Poderoso — executada, dano 194, MP −47 | Ataque básico — executada, dano 243 | 1772 / 4934 | 47 / 60 |
| 34 | p2 → p1 (score) | Ataque básico — executada, dano 112 | Ataque básico — executada, dano 243 | 1533 / 4907 | 75 / 90 |
| 35 | p2 → p1 (score) | Respirar Fundo — executada, dano 0, MP −73 | Ataque básico — executada, dano 243 | 1841 / 4992 | 30 / 120 |
| 36 | p2 → p1 (score) | Ataque básico — executada, dano 151 | Cutelada — executada, dano 483, MP −95 | 1364 / 5010 | 58 / 55 |
| 37 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 243 | 1121 / 5095 | 39 / 85 |
| 38 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 243 | 878 / 5180 | 67 / 115 |
| 39 | p2 → p1 (score) | Golpe Poderoso — executada, dano 259, MP −47 | Cutelada — executada, dano 483, MP −95 | 405 / 5090 | 48 / 50 |
| 40 | p2 → p1 (score) | Ataque básico — executada, dano 151 | Ataque básico — executada, dano 243 | 168 / 5024 | 76 / 80 |
| 41 | p2 → p1 (score) | Respirar Fundo — cancelada por morte | Ataque básico — executada, dano 243 | -75 / 5109 | 76 / 110 |

### Quartas: detalhes

#### Quartas 1 — gafallen × LuquEt4

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W37 | gafallen | Guerreiro | 20 | 29.87 | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda | sustento |
| p2 | W34 | LuquEt4 | Guerreiro | 23 | 29.87 | Golpe Duplo, Grito de Guerra, Cutelada, Areia no Chão | crítico |

- Seed da partida: `16121932450484780189`
- Rodadas: **24**
- Vencedor: **gafallen** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1442/3973 (36.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | gafallen | LuquEt4 |
|---|---|---|
| Dano causado (golpes + DoT) | 7278 (4378 + 2900) | 6231 (6231 + 0) |
| Cura (skill + roubo de vida) | 3700 (1998 + 1702) | 0 (0 + 0) |
| MP gasto em ações | 1243 | 1052 |
| Skills / ataques básicos | 18 / 5 | 12 / 11 |
| Acertos / erros | 14 / 1 | 15 / 0 |
| Críticos (dano) | 0 (0) | 4 (2993) |
| Agiu primeiro (rodadas) | 1 | 23 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- gafallen aplicou: vulnerable (rodada 6), bleed (rodada 7), bleed (rodada 12), vulnerable (rodada 21), vulnerable (rodada 22), bleed (rodada 23)
- gafallen tentou sem sucesso: stun (rodada 2), bleed (rodada 2), vulnerable (rodada 2), stun (rodada 3), bleed (rodada 3), vulnerable (rodada 3), stun (rodada 4), bleed (rodada 4), stun (rodada 6), bleed (rodada 6), stun (rodada 7), vulnerable (rodada 7), stun (rodada 8), bleed (rodada 8), stun (rodada 11), bleed (rodada 11), vulnerable (rodada 11), stun (rodada 12), vulnerable (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 16), bleed (rodada 16), vulnerable (rodada 16), stun (rodada 17), bleed (rodada 17), vulnerable (rodada 17), stun (rodada 21), bleed (rodada 21), stun (rodada 22), bleed (rodada 22), stun (rodada 23)
- gafallen ativou: Escudo Protetor ×5
- LuquEt4 aplicou: frailty (rodada 3), slowed (rodada 6), vulnerable (rodada 6), frailty (rodada 7), slowed (rodada 12), vulnerable (rodada 12), slowed (rodada 21)
- LuquEt4 tentou sem sucesso: slowed (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 7), stun (rodada 8), stun (rodada 10), stun (rodada 11), stun (rodada 13), stun (rodada 14), stun (rodada 15), slowed (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), stun (rodada 20), vulnerable (rodada 21), stun (rodada 22), stun (rodada 23)
- LuquEt4 ativou: Grito de Guerra ×3
- Leis disparadas por LuquEt4: FERIDA ABERTA (rodada 7), FERIDA ABERTA (rodada 23)

Rodada a rodada:

| Rodada | Ordem (critério) | gafallen (p1) | LuquEt4 (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito de Guerra — executada, dano 0, MP −100 | 3973 / 7257 | 686 / 673 |
| 2 | p2 → p1 (score) | Mira Calma — executada, dano 584, MP −82 | Areia no Chão — executada, dano 0, MP −70 | 3973 / 6673 | 643 / 618 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 261, MP −50 | Golpe Duplo — executada, dano 972, MP −116 | 3118 / 6412 | 632 / 517 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 107 | Cutelada — executada, dano 466, MP −85 | 2700 / 6305 | 671 / 447 |
| 5 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Grito de Guerra — executada, dano 0, MP −100 | 2700 / 6305 | 633 / 362 |
| 6 | p2 → p1 (score) | Mira Calma — executada, dano 500, MP −82 | Areia no Chão — executada, dano 0, MP −70 | 2925 / 5805 | 590 / 307 |
| 7 | p2 → p1 (score) | Quebra-Guarda — executada, dano 280, MP −50 | Golpe Duplo — executada, dano 831, MP −116 | 2220 / 5525 | 579 / 206 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 107 | Cutelada — executada, dano 1008, MP −85 | 1260 / 4838 | 618 / 136 |
| 9 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Grito de Guerra — executada, dano 0, MP −100 | 1926 / 4258 | 591 / 51 |
| 10 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 575 | 1351 / 4258 | 553 / 66 |
| 11 | p2 → p1 (score) | Mira Calma — executada, dano 508, MP −82 | Ataque básico — executada, dano 438 | 1141 / 3750 | 510 / 81 |
| 12 | p2 → p1 (score) | Quebra-Guarda — executada, dano 233, MP −50 | Areia no Chão — executada, dano 0, MP −70 | 1245 / 3517 | 499 / 26 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 107 | Ataque básico — executada, dano 201 | 1092 / 3120 | 538 / 41 |
| 14 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 277 | 1481 / 2830 | 511 / 56 |
| 15 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 233 | 1248 / 2830 | 473 / 71 |
| 16 | p2 → p1 (score) | Mira Calma — executada, dano 508, MP −82 | Areia no Chão — executada, dano 0, MP −70 | 1476 / 2322 | 430 / 16 |
| 17 | p2 → p1 (score) | Quebra-Guarda — executada, dano 233, MP −50 | Ataque básico — executada, dano 177 | 1403 / 2089 | 419 / 31 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 177 | 1226 / 2089 | 458 / 46 |
| 19 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 233 | 1659 / 2089 | 431 / 61 |
| 20 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 233 | 1426 / 2089 | 393 / 76 |
| 21 | p2 → p1 (score) | Mira Calma — executada, dano 508, MP −82 | Areia no Chão — executada, dano 0, MP −70 | 1654 / 1581 | 350 / 21 |
| 22 | p2 → p1 (score) | Quebra-Guarda — executada, dano 280, MP −50 | Ataque básico — executada, dano 177 | 1603 / 1301 | 339 / 36 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 162 | Ataque básico — executada, dano 233 | 1442 / 559 | 378 / 51 |
| 24 | p2 → p1 (score) | Tomar Fôlego — não alcançada (o duelo acabou antes) | Ataque básico — cancelada por morte | 1442 / -21 | 378 / 66 |

#### Quartas 2 — MeikodRJ × lubatv

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W26 | MeikodRJ | Guerreiro | 22 | 29.75 | Golpe Poderoso, Mira Calma, Tomar Fôlego, Leitura de Terreno | sustento |
| p2 | W23 | lubatv | Guerreiro | 22 | 29.17 | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | crítico + sustento |

- Seed da partida: `3701790827052938640`
- Rodadas: **24**
- Vencedor: **lubatv** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2288/5275 (43.4%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | MeikodRJ | lubatv |
|---|---|---|
| Dano causado (golpes + DoT) | 2987 (2987 + 0) | 8641 (8641 + 0) |
| Cura (skill + roubo de vida) | 3661 (3039 + 622) | 0 (0 + 0) |
| MP gasto em ações | 1131 | 1266 |
| Skills / ataques básicos | 17 / 5 | 13 / 11 |
| Acertos / erros | 9 / 10 | 20 / 1 |
| Críticos (dano) | 0 (0) | 5 (2783) |
| Agiu primeiro (rodadas) | 8 | 16 |
| Ações perdidas por controle | 1 | 0 |

Efeitos relevantes:
- MeikodRJ aplicou: vulnerable (rodada 8)
- MeikodRJ tentou sem sucesso: stun (rodada 3), bleed (rodada 3), stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 8), bleed (rodada 8), stun (rodada 10), bleed (rodada 10), stun (rodada 11), bleed (rodada 11), vulnerable (rodada 11), stun (rodada 13), bleed (rodada 13), stun (rodada 15), bleed (rodada 15), stun (rodada 16), bleed (rodada 16), vulnerable (rodada 16), stun (rodada 17), bleed (rodada 17)
- lubatv aplicou: stun (rodada 2), vulnerable (rodada 6), vulnerable (rodada 9), vulnerable (rodada 12), vulnerable (rodada 22)
- lubatv tentou sem sucesso: stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 14), stun (rodada 14), stun (rodada 15), vulnerable (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 19), vulnerable (rodada 19), stun (rodada 20), stun (rodada 22), stun (rodada 23), stun (rodada 24)
- lubatv ativou: Postura Impecável ×3

Rodada a rodada:

| Rodada | Ordem (critério) | MeikodRJ (p1) | lubatv (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Postura Impecável — executada, dano 0, MP −131 | 4969 / 5275 | 782 / 777 |
| 2 | p2 → p1 (score) | Mira Calma — cancelada por controle | Esmagar — executada, dano 582, MP −144 | 4387 / 5275 | 798 / 651 |
| 3 | p2 → p1 (score) | Golpe Poderoso — executada, dano 256, MP −47 | Quebra-Guarda — executada, dano 602, MP −63 | 3838 / 5019 | 767 / 606 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 532, MP −103 | Ataque básico — executada, dano 234 | 3715 / 4487 | 680 / 624 |
| 5 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 238 | 3477 / 4487 | 649 / 642 |
| 6 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Quebra-Guarda — executada, dano 347, MP −63 | 3130 / 4487 | 665 / 597 |
| 7 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Postura Impecável — executada, dano 0, MP −131 | 3130 / 4487 | 634 / 484 |
| 8 | p2 → p1 (score) | Mira Calma — executada, dano 426, MP −103 | Esmagar — executada, dano 1050, MP −144 | 2169 / 4061 | 547 / 358 |
| 9 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Quebra-Guarda — executada, dano 970, MP −63 | 2212 / 4061 | 480 / 313 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 237, MP −47 | Ataque básico — executada, dano 282 | 1979 / 3824 | 449 / 331 |
| 11 | p2 → p1 (score) | Mira Calma — executada, dano 462, MP −103 | Ataque básico — executada, dano 287 | 1789 / 3362 | 362 / 349 |
| 12 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Quebra-Guarda — executada, dano 347, MP −63 | 1442 / 3362 | 331 / 304 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 138 | Postura Impecável — executada, dano 0, MP −131 | 1470 / 3224 | 347 / 191 |
| 14 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Esmagar — executada, dano 1190, MP −144 | 1293 / 3224 | 280 / 65 |
| 15 | p2 → p1 (score) | Golpe Poderoso — executada, dano 237, MP −47 | Quebra-Guarda — executada, dano 646, MP −63 | 696 / 2987 | 249 / 20 |
| 16 | p2 → p1 (score) | Mira Calma — executada, dano 462, MP −103 | Ataque básico — executada, dano 234 | 559 / 2525 | 162 / 38 |
| 17 | p2 → p1 (score) | Golpe Poderoso — executada, dano 237, MP −47 | Ataque básico — executada, dano 238 | 370 / 2288 | 131 / 56 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 159 | 211 / 2288 | 147 / 74 |
| 19 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −83 | Quebra-Guarda — executada, dano 347, MP −63 | 877 / 2288 | 80 / 29 |
| 20 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Ataque básico — executada, dano 159 | 718 / 2288 | 49 / 47 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 718 / 2288 | 65 / 65 |
| 22 | p1 → p2 (score) | Golpe Poderoso — executada, dano 0, MP −47 | Quebra-Guarda — executada, dano 347, MP −63 | 371 / 2288 | 34 / 20 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 191 | 180 / 2288 | 50 / 38 |
| 24 | p2 → p1 (score) | Golpe Poderoso — cancelada por morte | Ataque básico — executada, dano 191 | -11 / 2288 | 50 / 56 |

#### Quartas 3 — frttt × XANDAOOGOD

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W60 | frttt | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca | sustento |
| p2 | W47 | XANDAOOGOD | Guerreiro | 23 | 29.64 | Esmagar, Mira Calma, Leitura de Terreno, Veterania | defesa |

- Seed da partida: `239342085775483302`
- Rodadas: **23**
- Vencedor: **frttt** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 147/5379 (2.7%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | XANDAOOGOD |
|---|---|---|
| Dano causado (golpes + DoT) | 6163 (3893 + 2270) | 5851 (4591 + 1260) |
| Cura (skill + roubo de vida) | 619 (0 + 619) | 0 (0 + 0) |
| MP gasto em ações | 1674 | 1502 |
| Skills / ataques básicos | 19 / 2 | 12 / 11 |
| Acertos / erros | 8 / 3 | 16 / 2 |
| Críticos (dano) | 1 (816) | 1 (240) |
| Agiu primeiro (rodadas) | 0 | 23 |
| Ações perdidas por controle | 2 | 0 |

Efeitos relevantes:
- frttt aplicou: bleed (rodada 2), bleed (rodada 8), bleed (rodada 17), bleed (rodada 22)
- frttt tentou sem sucesso: stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 9), bleed (rodada 9), stun (rodada 10), bleed (rodada 10), vulnerable (rodada 10), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), stun (rodada 15), bleed (rodada 15), vulnerable (rodada 15), stun (rodada 19), bleed (rodada 19), vulnerable (rodada 19), stun (rodada 20), bleed (rodada 20), stun (rodada 23), bleed (rodada 23)
- frttt ativou: Pausa Útil ×5
- XANDAOOGOD aplicou: vulnerable (rodada 3), stun (rodada 7), bleed (rodada 8), stun (rodada 12), poison (rodada 13), vulnerable (rodada 17), bleed (rodada 21)
- XANDAOOGOD tentou sem sucesso: bleed (rodada 3), poison (rodada 3), bleed (rodada 4), poison (rodada 4), bleed (rodada 5), poison (rodada 5), bleed (rodada 7), poison (rodada 7), poison (rodada 8), vulnerable (rodada 8), bleed (rodada 9), poison (rodada 9), bleed (rodada 12), poison (rodada 12), bleed (rodada 13), vulnerable (rodada 13), bleed (rodada 14), poison (rodada 14), bleed (rodada 15), poison (rodada 15), bleed (rodada 17), poison (rodada 17), bleed (rodada 18), poison (rodada 18), bleed (rodada 19), poison (rodada 19), bleed (rodada 20), poison (rodada 20), poison (rodada 21), bleed (rodada 23), poison (rodada 23)
- XANDAOOGOD ativou: Veterania ×5

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | XANDAOOGOD (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 5379 / 5684 | 990 / 926 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Esmagar — executada, dano 0, MP −161 | 5379 / 5684 | 962 / 789 |
| 3 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Mira Calma — executada, dano 570, MP −116 | 4809 / 5457 | 884 / 697 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 587, MP −116 | Ataque básico — executada, dano 192 | 4710 / 4643 | 810 / 721 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 160 | 4550 / 4416 | 852 / 745 |
| 6 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 4550 / 4416 | 828 / 658 |
| 7 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Esmagar — executada, dano 396, MP −161 | 4154 / 4416 | 870 / 521 |
| 8 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 495, MP −116 | 3444 / 4416 | 842 / 429 |
| 9 | p2 → p1 (score) | Golpe Devastador — executada, dano 364, MP −120 | Ataque básico — executada, dano 160 | 3127 / 3825 | 764 / 453 |
| 10 | p2 → p1 (score) | Mira Calma — executada, dano 510, MP −116 | Ataque básico — executada, dano 0 | 3208 / 3088 | 690 / 477 |
| 11 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 3208 / 2861 | 666 / 390 |
| 12 | p2 → p1 (score) | Estocada Seca — cancelada por controle | Esmagar — executada, dano 396, MP −161 | 2812 / 2861 | 708 / 253 |
| 13 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 495, MP −116 | 2237 / 2861 | 680 / 161 |
| 14 | p2 → p1 (score) | Golpe Devastador — executada, dano 364, MP −120 | Ataque básico — executada, dano 160 | 2055 / 2497 | 602 / 185 |
| 15 | p2 → p1 (score) | Mira Calma — executada, dano 510, MP −116 | Ataque básico — executada, dano 160 | 1896 / 1987 | 528 / 209 |
| 16 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Veterania — executada, dano 0, MP −111 | 1816 / 1987 | 504 / 122 |
| 17 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Mira Calma — executada, dano 495, MP −116 | 1241 / 1987 | 476 / 30 |
| 18 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Ataque básico — executada, dano 192 | 1049 / 1760 | 398 / 54 |
| 19 | p2 → p1 (score) | Mira Calma — executada, dano 816, MP −116 | Ataque básico — executada, dano 160 | 1019 / 717 | 324 / 78 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 159 | Ataque básico — executada, dano 160 | 884 / 331 | 366 / 102 |
| 21 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Ataque básico — executada, dano 240 | 429 / 331 | 342 / 126 |
| 22 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Veterania — executada, dano 0, MP −111 | 214 / 331 | 314 / 39 |
| 23 | p2 → p1 (score) | Golpe Devastador — executada, dano 583, MP −120 | Ataque básico — executada, dano 160 | 147 / -479 | 236 / 63 |

#### Quartas 4 — fer × RNakano

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W64 | fer | Guerreiro | 23 | 29.98 | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | defesa + sustento |
| p2 | W42 | RNakano | Guerreiro | 24 | 29.64 | Golpe Duplo, Cutelada, Gancho e Corda, Disciplina de Forja | sustento |

- Seed da partida: `9149351047459092604`
- Rodadas: **43**
- Vencedor: **fer** (p1), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 2470/5977 (41.3%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | fer | RNakano |
|---|---|---|
| Dano causado (golpes + DoT) | 9929 (9929 + 0) | 4715 (4715 + 0) |
| Cura (skill + roubo de vida) | 1208 (0 + 1208) | 1642 (0 + 1642) |
| MP gasto em ações | 1962 | 2098 |
| Skills / ataques básicos | 29 / 13 | 19 / 21 |
| Acertos / erros | 37 / 1 | 22 / 10 |
| Críticos (dano) | 7 (2830) | 1 (652) |
| Agiu primeiro (rodadas) | 25 | 18 |
| Ações perdidas por controle | 1 | 2 |

Efeitos relevantes:
- fer aplicou: stun (rodada 2), stun (rodada 5), weakened (rodada 11), weakened (rodada 15)
- fer tentou sem sucesso: stun (rodada 3), weakened (rodada 3), weakened (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 9), weakened (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 17), weakened (rodada 17), stun (rodada 18), stun (rodada 20), stun (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 37), stun (rodada 39), stun (rodada 40), stun (rodada 41), stun (rodada 42), stun (rodada 43)
- fer ativou: Juramento da Muralha ×4
- RNakano aplicou: stun (rodada 37)
- RNakano tentou sem sucesso: stun (rodada 2), stun (rodada 5), stun (rodada 8), stun (rodada 10), stun (rodada 11), stun (rodada 13), stun (rodada 14), stun (rodada 15), stun (rodada 18), stun (rodada 19), stun (rodada 21), stun (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), stun (rodada 31), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 38), stun (rodada 40)
- RNakano ativou: Disciplina de Forja ×5

Rodada a rodada:

| Rodada | Ordem (critério) | fer (p1) | RNakano (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Disciplina de Forja — executada, dano 0, MP −118 | 5977 / 8159 | 951 / 795 |
| 2 | p2 → p1 (score) | Golpe Poderoso — executada, dano 246, MP −52 | Gancho e Corda — executada, dano 0, MP −131 | 5977 / 7913 | 921 / 694 |
| 3 | p2 → p1 (score) | Soco de Placa — executada, dano 240, MP −61 | Golpe Duplo — cancelada por controle | 5977 / 7673 | 882 / 724 |
| 4 | p2 → p1 (score) | Golpe Poderoso — executada, dano 0, MP −52 | Golpe Duplo — executada, dano 0, MP −130 | 5977 / 7673 | 852 / 624 |
| 5 | p2 → p1 (score) | Soco de Placa — executada, dano 516, MP −61 | Cutelada — executada, dano 201, MP −95 | 5843 / 7227 | 813 / 559 |
| 6 | p1 → p2 (score) | Golpe Poderoso — executada, dano 330, MP −52 | Disciplina de Forja — cancelada por controle | 5885 / 6897 | 783 / 589 |
| 7 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Disciplina de Forja — executada, dano 0, MP −118 | 5885 / 6897 | 653 / 501 |
| 8 | p2 → p1 (score) | Golpe Poderoso — executada, dano 246, MP −52 | Gancho e Corda — executada, dano 0, MP −131 | 5916 / 6651 | 623 / 400 |
| 9 | p2 → p1 (score) | Soco de Placa — executada, dano 240, MP −61 | Golpe Duplo — executada, dano 0, MP −130 | 5947 / 6411 | 584 / 300 |
| 10 | p2 → p1 (score) | Golpe Poderoso — executada, dano 228, MP −52 | Cutelada — executada, dano 201, MP −95 | 5775 / 6253 | 554 / 235 |
| 11 | p2 → p1 (score) | Soco de Placa — executada, dano 516, MP −61 | Ataque básico — executada, dano 101 | 5741 / 5772 | 515 / 265 |
| 12 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Disciplina de Forja — executada, dano 0, MP −118 | 5780 / 5466 | 485 / 177 |
| 13 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Gancho e Corda — executada, dano 0, MP −131 | 5780 / 5466 | 355 / 76 |
| 14 | p2 → p1 (score) | Golpe Poderoso — executada, dano 228, MP −52 | Ataque básico — executada, dano 101 | 5708 / 5273 | 325 / 106 |
| 15 | p2 → p1 (score) | Soco de Placa — executada, dano 240, MP −61 | Cutelada — executada, dano 201, MP −95 | 5538 / 5103 | 286 / 41 |
| 16 | p1 → p2 (score) | Golpe Poderoso — executada, dano 365, MP −52 | Ataque básico — executada, dano 0 | 5585 / 4738 | 256 / 71 |
| 17 | p1 → p2 (score) | Soco de Placa — executada, dano 323, MP −61 | Ataque básico — executada, dano 0 | 5626 / 4415 | 217 / 101 |
| 18 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Cutelada — executada, dano 652, MP −95 | 5013 / 4337 | 187 / 36 |
| 19 | p1 → p2 (score) | Juramento da Muralha — executada, dano 0, MP −152 | Ataque básico — executada, dano 101 | 4912 / 4372 | 57 / 66 |
| 20 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Ataque básico — executada, dano 0 | 4951 / 4066 | 27 / 96 |
| 21 | p1 → p2 (score) | Ataque básico — executada, dano 180 | Cutelada — executada, dano 201, MP −95 | 4773 / 3956 | 49 / 31 |
| 22 | p1 → p2 (score) | Ataque básico — executada, dano 180 | Ataque básico — executada, dano 101 | 4695 / 3811 | 71 / 61 |
| 23 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Ataque básico — executada, dano 204 | 4530 / 3576 | 41 / 91 |
| 24 | p1 → p2 (score) | Ataque básico — executada, dano 180 | Ataque básico — executada, dano 204 | 4349 / 3467 | 63 / 121 |
| 25 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Disciplina de Forja — executada, dano 0, MP −118 | 4388 / 3161 | 33 / 33 |
| 26 | p2 → p1 (score) | Ataque básico — executada, dano 134 | Ataque básico — executada, dano 204 | 4201 / 3098 | 55 / 63 |
| 27 | p2 → p1 (score) | Golpe Poderoso — executada, dano 228, MP −52 | Ataque básico — executada, dano 204 | 4026 / 2941 | 25 / 93 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 134 | Ataque básico — executada, dano 204 | 3839 / 2878 | 47 / 123 |
| 29 | p2 → p1 (score) | Ataque básico — executada, dano 180 | Cutelada — executada, dano 407, MP −95 | 3455 / 2840 | 69 / 58 |
| 30 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Ataque básico — executada, dano 0 | 3494 / 2534 | 39 / 88 |
| 31 | p1 → p2 (score) | Ataque básico — executada, dano 289 | Ataque básico — executada, dano 204 | 3327 / 2316 | 61 / 118 |
| 32 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Disciplina de Forja — executada, dano 0, MP −118 | 3366 / 2010 | 31 / 30 |
| 33 | p2 → p1 (score) | Ataque básico — executada, dano 134 | Ataque básico — executada, dano 204 | 3179 / 1947 | 53 / 60 |
| 34 | p2 → p1 (score) | Golpe Poderoso — executada, dano 365, MP −52 | Ataque básico — executada, dano 204 | 3022 / 1653 | 23 / 90 |
| 35 | p2 → p1 (score) | Ataque básico — executada, dano 134 | Ataque básico — executada, dano 204 | 2835 / 1590 | 45 / 120 |
| 36 | p2 → p1 (score) | Ataque básico — executada, dano 180 | Cutelada — executada, dano 0, MP −95 | 2858 / 1410 | 67 / 55 |
| 37 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Ataque básico — executada, dano 204 | 2693 / 1175 | 37 / 85 |
| 38 | p1 → p2 (score) | Ataque básico — cancelada por controle | Ataque básico — executada, dano 204 | 2489 / 1246 | 59 / 115 |
| 39 | p1 → p2 (score) | Golpe Poderoso — executada, dano 306, MP −52 | Cutelada — executada, dano 0, MP −95 | 2528 / 940 | 29 / 50 |
| 40 | p1 → p2 (score) | Ataque básico — executada, dano 180 | Ataque básico — executada, dano 204 | 2347 / 831 | 51 / 80 |
| 41 | p1 → p2 (score) | Ataque básico — executada, dano 289 | Ataque básico — executada, dano 0 | 2384 / 542 | 73 / 110 |
| 42 | p1 → p2 (score) | Golpe Poderoso — executada, dano 490, MP −52 | Cutelada — executada, dano 0, MP −95 | 2447 / 52 | 43 / 45 |
| 43 | p1 → p2 (score) | Ataque básico — executada, dano 180 | Ataque básico — cancelada por morte | 2470 / -128 | 65 / 45 |

### Semifinal: detalhes

#### Semifinal 1 — gafallen × lubatv

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W37 | gafallen | Guerreiro | 20 | 29.87 | Tomar Fôlego, Mira Calma, Escudo Protetor, Quebra-Guarda | sustento |
| p2 | W23 | lubatv | Guerreiro | 22 | 29.17 | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | crítico + sustento |

- Seed da partida: `10346392674869592990`
- Rodadas: **56**
- Vencedor: **lubatv** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 217/5275 (4.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | gafallen | lubatv |
|---|---|---|
| Dano causado (golpes + DoT) | 5058 (4636 + 422) | 12066 (12066 + 0) |
| Cura (skill + roubo de vida) | 8073 (5994 + 2079) | 0 (0 + 0) |
| MP gasto em ações | 2824 | 1833 |
| Skills / ataques básicos | 42 / 14 | 22 / 33 |
| Acertos / erros | 17 / 18 | 47 / 5 |
| Críticos (dano) | 2 (673) | 15 (4752) |
| Agiu primeiro (rodadas) | 23 | 33 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- gafallen aplicou: vulnerable (rodada 3), vulnerable (rodada 21), vulnerable (rodada 27), bleed (rodada 37), vulnerable (rodada 42), stun (rodada 48), vulnerable (rodada 48)
- gafallen tentou sem sucesso: stun (rodada 2), bleed (rodada 2), vulnerable (rodada 2), stun (rodada 3), bleed (rodada 3), stun (rodada 8), bleed (rodada 8), stun (rodada 13), bleed (rodada 13), stun (rodada 16), bleed (rodada 16), vulnerable (rodada 16), stun (rodada 18), bleed (rodada 18), stun (rodada 21), bleed (rodada 21), stun (rodada 22), bleed (rodada 22), vulnerable (rodada 22), stun (rodada 26), bleed (rodada 26), vulnerable (rodada 26), stun (rodada 27), bleed (rodada 27), stun (rodada 34), bleed (rodada 34), vulnerable (rodada 34), stun (rodada 37), stun (rodada 40), bleed (rodada 40), stun (rodada 42), bleed (rodada 42), stun (rodada 45), bleed (rodada 45), vulnerable (rodada 45), bleed (rodada 48), stun (rodada 56), bleed (rodada 56)
- gafallen ativou: Escudo Protetor ×12
- lubatv aplicou: vulnerable (rodada 9), vulnerable (rodada 12), vulnerable (rodada 43), vulnerable (rodada 47)
- lubatv tentou sem sucesso: stun (rodada 2), stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), vulnerable (rodada 6), stun (rodada 8), stun (rodada 8), stun (rodada 9), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 20), stun (rodada 21), stun (rodada 22), vulnerable (rodada 22), stun (rodada 23), stun (rodada 24), stun (rodada 25), stun (rodada 27), stun (rodada 28), stun (rodada 29), vulnerable (rodada 29), stun (rodada 30), stun (rodada 31), stun (rodada 32), stun (rodada 33), vulnerable (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), vulnerable (rodada 36), stun (rodada 37), stun (rodada 38), stun (rodada 39), stun (rodada 40), vulnerable (rodada 40), stun (rodada 41), stun (rodada 42), stun (rodada 43), stun (rodada 44), stun (rodada 45), stun (rodada 46), stun (rodada 47), stun (rodada 50), vulnerable (rodada 50), stun (rodada 51), stun (rodada 52), stun (rodada 53), stun (rodada 54), vulnerable (rodada 54), stun (rodada 55), stun (rodada 56)
- lubatv ativou: Postura Impecável ×3

Rodada a rodada:

| Rodada | Ordem (critério) | gafallen (p1) | lubatv (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Postura Impecável — executada, dano 0, MP −131 | 3973 / 5275 | 686 / 777 |
| 2 | p2 → p1 (score) | Mira Calma — executada, dano 518, MP −82 | Esmagar — executada, dano 690, MP −144 | 3516 / 4757 | 643 / 651 |
| 3 | p2 → p1 (score) | Quebra-Guarda — executada, dano 232, MP −50 | Quebra-Guarda — executada, dano 714, MP −63 | 2906 / 4525 | 632 / 606 |
| 4 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 279 | 2627 / 4525 | 671 / 624 |
| 5 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 165 | 2462 / 4525 | 633 / 642 |
| 6 | p1 → p2 (score) | Mira Calma — executada, dano 0, MP −82 | Quebra-Guarda — executada, dano 274, MP −63 | 2188 / 4525 | 590 / 597 |
| 7 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Postura Impecável — executada, dano 0, MP −131 | 2188 / 4525 | 579 / 484 |
| 8 | p2 → p1 (score) | Ataque básico — executada, dano 187 | Esmagar — executada, dano 460, MP −144 | 1812 / 4338 | 618 / 358 |
| 9 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Quebra-Guarda — executada, dano 558, MP −63 | 1920 / 4338 | 591 / 313 |
| 10 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 289 | 1631 / 4338 | 553 / 331 |
| 11 | p2 → p1 (score) | Mira Calma — executada, dano 0, MP −82 | Ataque básico — executada, dano 226 | 1405 / 4338 | 510 / 349 |
| 12 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Quebra-Guarda — executada, dano 288, MP −63 | 1117 / 4338 | 499 / 304 |
| 13 | p2 → p1 (score) | Ataque básico — executada, dano 95 | Postura Impecável — executada, dano 0, MP −131 | 1159 / 4243 | 538 / 191 |
| 14 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Esmagar — executada, dano 0, MP −144 | 1825 / 4243 | 511 / 65 |
| 15 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Quebra-Guarda — executada, dano 0, MP −63 | 1825 / 4243 | 473 / 20 |
| 16 | p2 → p1 (score) | Mira Calma — executada, dano 518, MP −82 | Ataque básico — executada, dano 186 | 1872 / 3725 | 430 / 38 |
| 17 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Ataque básico — executada, dano 126 | 1746 / 3725 | 419 / 56 |
| 18 | p1 → p2 (score) | Ataque básico — executada, dano 95 | Ataque básico — executada, dano 165 | 1623 / 3630 | 458 / 74 |
| 19 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Quebra-Guarda — executada, dano 0, MP −63 | 2289 / 3630 | 431 / 29 |
| 20 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 165 | 2124 / 3630 | 393 / 47 |
| 21 | p1 → p2 (score) | Mira Calma — executada, dano 450, MP −82 | Ataque básico — executada, dano 189 | 2137 / 3180 | 350 / 65 |
| 22 | p1 → p2 (score) | Quebra-Guarda — executada, dano 486, MP −50 | Quebra-Guarda — executada, dano 274, MP −63 | 2081 / 2694 | 339 / 20 |
| 23 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 165 | 1916 / 2694 | 378 / 38 |
| 24 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 165 | 2417 / 2694 | 351 / 56 |
| 25 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 248 | 2169 / 2694 | 313 / 74 |
| 26 | p1 → p2 (score) | Mira Calma — executada, dano 450, MP −82 | Quebra-Guarda — executada, dano 0, MP −63 | 2371 / 2244 | 270 / 29 |
| 27 | p1 → p2 (score) | Quebra-Guarda — executada, dano 207, MP −50 | Ataque básico — executada, dano 126 | 2338 / 2037 | 259 / 47 |
| 28 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 165 | 2173 / 2037 | 298 / 65 |
| 29 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Quebra-Guarda — executada, dano 360, MP −63 | 1813 / 2037 | 260 / 20 |
| 30 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 189 | 2290 / 2037 | 233 / 38 |
| 31 | p1 → p2 (score) | Mira Calma — executada, dano 0, MP −82 | Ataque básico — executada, dano 126 | 2164 / 2037 | 190 / 56 |
| 32 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Ataque básico — executada, dano 248 | 1916 / 2037 | 179 / 74 |
| 33 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Quebra-Guarda — executada, dano 360, MP −63 | 1556 / 2037 | 141 / 29 |
| 34 | p1 → p2 (score) | Mira Calma — executada, dano 450, MP −82 | Ataque básico — executada, dano 126 | 1632 / 1587 | 98 / 47 |
| 35 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 126 | 2172 / 1587 | 71 / 65 |
| 36 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Quebra-Guarda — executada, dano 360, MP −63 | 1812 / 1587 | 60 / 20 |
| 37 | p2 → p1 (score) | Ataque básico — executada, dano 95 | Ataque básico — executada, dano 165 | 1689 / 1492 | 99 / 38 |
| 38 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 248 | 1441 / 1281 | 61 / 56 |
| 39 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Ataque básico — executada, dano 126 | 1315 / 1070 | 50 / 74 |
| 40 | p1 → p2 (score) | Ataque básico — executada, dano 95 | Quebra-Guarda — executada, dano 274, MP −63 | 1083 / 975 | 89 / 29 |
| 41 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 248 | 1501 / 975 | 62 / 47 |
| 42 | p2 → p1 (score) | Quebra-Guarda — executada, dano 207, MP −50 | Ataque básico — executada, dano 248 | 1346 / 768 | 51 / 65 |
| 43 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Quebra-Guarda — executada, dano 360, MP −63 | 986 / 768 | 90 / 20 |
| 44 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 196 | 790 / 768 | 52 / 38 |
| 45 | p1 → p2 (score) | Quebra-Guarda — executada, dano 249, MP −50 | Ataque básico — executada, dano 132 | 770 / 519 | 41 / 56 |
| 46 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 132 | 638 / 519 | 80 / 74 |
| 47 | p2 → p1 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Quebra-Guarda — executada, dano 288, MP −63 | 1016 / 519 | 53 / 29 |
| 48 | p2 → p1 (score) | Quebra-Guarda — executada, dano 207, MP −50 | Ataque básico — executada, dano 0 | 1109 / 312 | 42 / 47 |
| 49 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — cancelada por controle | 1109 / 312 | 81 / 65 |
| 50 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Quebra-Guarda — executada, dano 360, MP −63 | 749 / 312 | 43 / 20 |
| 51 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 126 | 623 / 312 | 82 / 38 |
| 52 | p1 → p2 (score) | Tomar Fôlego — executada, dano 0, MP −66 | Ataque básico — executada, dano 189 | 1100 / 312 | 55 / 56 |
| 53 | p1 → p2 (score) | Quebra-Guarda — executada, dano 0, MP −50 | Ataque básico — executada, dano 248 | 852 / 312 | 44 / 74 |
| 54 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Quebra-Guarda — executada, dano 540, MP −63 | 312 / 312 | 83 / 29 |
| 55 | p2 → p1 (score) | Escudo Protetor — executada, dano 0, MP −77 | Ataque básico — executada, dano 248 | 64 / 312 | 45 / 47 |
| 56 | p1 → p2 (score) | Ataque básico — executada, dano 95 | Ataque básico — executada, dano 126 | -20 / 217 | 84 / 65 |

#### Semifinal 2 — frttt × fer

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W60 | frttt | Guerreiro | 23 | 29.52 | Golpe Devastador, Mira Calma, Pausa Útil, Estocada Seca | sustento |
| p2 | W64 | fer | Guerreiro | 23 | 29.98 | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | defesa + sustento |

- Seed da partida: `14455366452904822823`
- Rodadas: **24**
- Vencedor: **fer** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1977/5977 (33.1%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | frttt | fer |
|---|---|---|
| Dano causado (golpes + DoT) | 5311 (2682 + 2629) | 5904 (5904 + 0) |
| Cura (skill + roubo de vida) | 425 (0 + 425) | 1311 (597 + 714) |
| MP gasto em ações | 1674 | 1567 |
| Skills / ataques básicos | 19 / 4 | 21 / 2 |
| Acertos / erros | 10 / 3 | 17 / 1 |
| Críticos (dano) | 1 (500) | 5 (2508) |
| Agiu primeiro (rodadas) | 0 | 24 |
| Ações perdidas por controle | 0 | 1 |

Efeitos relevantes:
- frttt aplicou: bleed (rodada 2), bleed (rodada 7), stun (rodada 10), bleed (rodada 17), bleed (rodada 22)
- frttt tentou sem sucesso: stun (rodada 4), bleed (rodada 4), vulnerable (rodada 4), stun (rodada 5), bleed (rodada 5), stun (rodada 8), bleed (rodada 8), stun (rodada 9), bleed (rodada 9), vulnerable (rodada 9), bleed (rodada 10), bleed (rodada 12), stun (rodada 13), bleed (rodada 13), stun (rodada 14), bleed (rodada 14), vulnerable (rodada 14), stun (rodada 15), bleed (rodada 15), stun (rodada 18), bleed (rodada 18), stun (rodada 23), bleed (rodada 23)
- frttt ativou: Pausa Útil ×5
- fer aplicou: weakened (rodada 3), weakened (rodada 5), weakened (rodada 15), weakened (rodada 17)
- fer tentou sem sucesso: stun (rodada 2), stun (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 8), stun (rodada 9), weakened (rodada 9), stun (rodada 10), stun (rodada 12), stun (rodada 14), stun (rodada 15), stun (rodada 16), stun (rodada 17), stun (rodada 18), stun (rodada 22), stun (rodada 23), stun (rodada 24)
- fer ativou: Juramento da Muralha ×4

Rodada a rodada:

| Rodada | Ordem (critério) | frttt (p1) | fer (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Juramento da Muralha — executada, dano 0, MP −152 | 5379 / 5977 | 990 / 951 |
| 2 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Golpe Poderoso — executada, dano 323, MP −52 | 5056 / 5977 | 962 / 921 |
| 3 | p2 → p1 (score) | Golpe Devastador — executada, dano 0, MP −120 | Soco de Placa — executada, dano 504, MP −61 | 4552 / 5803 | 884 / 882 |
| 4 | p2 → p1 (score) | Mira Calma — executada, dano 315, MP −116 | Golpe Poderoso — executada, dano 517, MP −52 | 4085 / 5316 | 810 / 852 |
| 5 | p2 → p1 (score) | Ataque básico — executada, dano 142 | Soco de Placa — executada, dano 504, MP −61 | 3603 / 5000 | 852 / 813 |
| 6 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 299, MP −52 | 3304 / 5038 | 828 / 783 |
| 7 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Juramento da Muralha — executada, dano 0, MP −152 | 3304 / 5038 | 800 / 653 |
| 8 | p2 → p1 (score) | Golpe Devastador — executada, dano 195, MP −120 | Golpe Poderoso — executada, dano 299, MP −52 | 3036 / 4642 | 722 / 623 |
| 9 | p2 → p1 (score) | Mira Calma — executada, dano 274, MP −116 | Soco de Placa — executada, dano 504, MP −61 | 2575 / 4194 | 648 / 584 |
| 10 | p2 → p1 (score) | Ataque básico — executada, dano 85 | Golpe Poderoso — executada, dano 299, MP −52 | 2289 / 3908 | 690 / 554 |
| 11 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Soco de Placa — cancelada por controle | 2289 / 3908 | 666 / 576 |
| 12 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Golpe Poderoso — executada, dano 299, MP −52 | 1990 / 3946 | 638 / 546 |
| 13 | p2 → p1 (score) | Golpe Devastador — executada, dano 195, MP −120 | Juramento da Muralha — executada, dano 0, MP −152 | 2021 / 3751 | 560 / 416 |
| 14 | p2 → p1 (score) | Mira Calma — executada, dano 274, MP −116 | Golpe Poderoso — executada, dano 299, MP −52 | 1765 / 3515 | 486 / 386 |
| 15 | p2 → p1 (score) | Ataque básico — executada, dano 70 | Soco de Placa — executada, dano 315, MP −61 | 1461 / 3485 | 528 / 347 |
| 16 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 299, MP −52 | 1162 / 3523 | 504 / 317 |
| 17 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Soco de Placa — executada, dano 315, MP −61 | 847 / 3563 | 476 / 278 |
| 18 | p2 → p1 (score) | Golpe Devastador — executada, dano 632, MP −120 | Golpe Poderoso — executada, dano 299, MP −52 | 649 / 2730 | 398 / 248 |
| 19 | p2 → p1 (score) | Mira Calma — executada, dano 0, MP −116 | Respirar Fundo — executada, dano 0, MP −82 | 649 / 3088 | 324 / 188 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Juramento da Muralha — executada, dano 0, MP −152 | 649 / 2849 | 366 / 58 |
| 21 | p2 → p1 (score) | Pausa Útil — executada, dano 0, MP −52 | Golpe Poderoso — executada, dano 0, MP −52 | 649 / 2849 | 342 / 28 |
| 22 | p2 → p1 (score) | Estocada Seca — executada, dano 0, MP −70 | Ataque básico — executada, dano 175 | 474 / 2871 | 314 / 50 |
| 23 | p2 → p1 (score) | Golpe Devastador — executada, dano 500, MP −120 | Ataque básico — executada, dano 175 | 379 / 2154 | 236 / 72 |
| 24 | p2 → p1 (score) | Mira Calma — cancelada por morte | Golpe Poderoso — executada, dano 479, MP −52 | -100 / 1977 | 236 / 42 |

### Final: detalhes

#### Final — lubatv × fer

| Lado | ID | Gladiador | Classe | Nível | OP | Skills | Característica |
|---|---|---|---|---|---|---|---|
| p1 | W23 | lubatv | Guerreiro | 22 | 29.17 | Esmagar, Quebra-Guarda, Tomar Fôlego, Postura Impecável | crítico + sustento |
| p2 | W64 | fer | Guerreiro | 23 | 29.98 | Golpe Poderoso, Juramento da Muralha, Soco de Placa, Respirar Fundo | defesa + sustento |

- Seed da partida: `6619800792897972838`
- Rodadas: **37**
- Vencedor: **fer** (p2), motivo `ko` (o adversário chegou a 0 de HP) — HP restante 1165/5977 (19.5%)
- Fidelidade (com × sem auditoria): **idêntico** em todas as verificações; coerência do trace com o motor: **ok**

| Total | lubatv | fer |
|---|---|---|
| Dano causado (golpes + DoT) | 5494 (5494 + 0) | 5298 (5298 + 0) |
| Cura (skill + roubo de vida) | 0 (0 + 0) | 682 (0 + 682) |
| MP gasto em ações | 1518 | 1858 |
| Skills / ataques básicos | 17 / 19 | 27 / 10 |
| Acertos / erros | 23 / 10 | 22 / 11 |
| Críticos (dano) | 9 (3084) | 5 (1961) |
| Agiu primeiro (rodadas) | 12 | 25 |
| Ações perdidas por controle | 0 | 0 |

Efeitos relevantes:
- lubatv aplicou: vulnerable (rodada 6), vulnerable (rodada 9), vulnerable (rodada 15), vulnerable (rodada 33)
- lubatv tentou sem sucesso: stun (rodada 2), stun (rodada 2), stun (rodada 3), vulnerable (rodada 3), stun (rodada 4), stun (rodada 5), stun (rodada 6), stun (rodada 9), stun (rodada 11), stun (rodada 15), stun (rodada 17), stun (rodada 18), stun (rodada 19), vulnerable (rodada 19), stun (rodada 20), stun (rodada 21), stun (rodada 22), vulnerable (rodada 22), stun (rodada 24), stun (rodada 25), stun (rodada 26), vulnerable (rodada 26), stun (rodada 27), stun (rodada 28), stun (rodada 29), vulnerable (rodada 29), stun (rodada 32), stun (rodada 33), stun (rodada 35)
- lubatv ativou: Postura Impecável ×3
- fer aplicou: weakened (rodada 11)
- fer tentou sem sucesso: stun (rodada 2), stun (rodada 4), stun (rodada 6), stun (rodada 8), stun (rodada 10), stun (rodada 11), stun (rodada 12), stun (rodada 14), stun (rodada 16), stun (rodada 17), weakened (rodada 17), stun (rodada 21), stun (rodada 22), stun (rodada 24), stun (rodada 26), stun (rodada 27), stun (rodada 29), stun (rodada 30), stun (rodada 33), stun (rodada 34), stun (rodada 35), stun (rodada 36), stun (rodada 37)
- fer ativou: Juramento da Muralha ×4

Rodada a rodada:

| Rodada | Ordem (critério) | lubatv (p1) | fer (p2) | HP fim p1 / p2 | MP fim p1 / p2 |
|---|---|---|---|---|---|
| 1 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −131 | Juramento da Muralha — executada, dano 0, MP −152 | 5275 / 5977 | 777 / 951 |
| 2 | p1 → p2 (score) | Esmagar — executada, dano 414, MP −144 | Golpe Poderoso — executada, dano 257, MP −52 | 5018 / 5596 | 651 / 921 |
| 3 | p1 → p2 (score) | Quebra-Guarda — executada, dano 285, MP −63 | Soco de Placa — executada, dano 0, MP −61 | 5018 / 5311 | 606 / 882 |
| 4 | p1 → p2 (score) | Ataque básico — executada, dano 111 | Golpe Poderoso — executada, dano 257, MP −52 | 4761 / 5233 | 624 / 852 |
| 5 | p1 → p2 (score) | Ataque básico — executada, dano 75 | Soco de Placa — executada, dano 0, MP −61 | 4761 / 5158 | 642 / 813 |
| 6 | p2 → p1 (score) | Quebra-Guarda — executada, dano 372, MP −63 | Golpe Poderoso — executada, dano 257, MP −52 | 4504 / 4819 | 597 / 783 |
| 7 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −131 | Juramento da Muralha — executada, dano 0, MP −152 | 4504 / 4819 | 484 / 653 |
| 8 | p1 → p2 (score) | Esmagar — executada, dano 0, MP −144 | Golpe Poderoso — executada, dano 413, MP −52 | 4091 / 4872 | 358 / 623 |
| 9 | p1 → p2 (score) | Quebra-Guarda — executada, dano 514, MP −63 | Soco de Placa — executada, dano 0, MP −61 | 4091 / 4358 | 313 / 584 |
| 10 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 239, MP −52 | 3852 / 4389 | 331 / 554 |
| 11 | p1 → p2 (score) | Ataque básico — executada, dano 90 | Soco de Placa — executada, dano 402, MP −61 | 3450 / 4351 | 349 / 515 |
| 12 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Golpe Poderoso — executada, dano 382, MP −52 | 3068 / 4400 | 304 / 485 |
| 13 | p2 → p1 (score) | Postura Impecável — executada, dano 0, MP −131 | Juramento da Muralha — executada, dano 0, MP −152 | 3068 / 4400 | 191 / 355 |
| 14 | p1 → p2 (score) | Esmagar — executada, dano 0, MP −144 | Golpe Poderoso — executada, dano 382, MP −52 | 2686 / 4449 | 65 / 325 |
| 15 | p1 → p2 (score) | Quebra-Guarda — executada, dano 254, MP −63 | Soco de Placa — executada, dano 0, MP −61 | 2686 / 4195 | 20 / 286 |
| 16 | p1 → p2 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 239, MP −52 | 2447 / 4226 | 38 / 256 |
| 17 | p1 → p2 (score) | Ataque básico — executada, dano 90 | Soco de Placa — executada, dano 251, MP −61 | 2196 / 4168 | 56 / 217 |
| 18 | p2 → p1 (score) | Ataque básico — executada, dano 228 | Golpe Poderoso — executada, dano 0, MP −52 | 2196 / 3940 | 74 / 187 |
| 19 | p2 → p1 (score) | Quebra-Guarda — executada, dano 164, MP −63 | Juramento da Muralha — executada, dano 0, MP −152 | 2196 / 3776 | 29 / 57 |
| 20 | p2 → p1 (score) | Ataque básico — executada, dano 75 | Golpe Poderoso — executada, dano 0, MP −52 | 2196 / 3701 | 47 / 27 |
| 21 | p2 → p1 (score) | Ataque básico — executada, dano 75 | Ataque básico — executada, dano 140 | 2056 / 3644 | 65 / 49 |
| 22 | p2 → p1 (score) | Quebra-Guarda — executada, dano 246, MP −63 | Ataque básico — executada, dano 140 | 1916 / 3416 | 20 / 71 |
| 23 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 0, MP −52 | 1916 / 3416 | 38 / 41 |
| 24 | p2 → p1 (score) | Ataque básico — executada, dano 152 | Ataque básico — executada, dano 140 | 1776 / 3282 | 56 / 63 |
| 25 | p2 → p1 (score) | Ataque básico — executada, dano 228 | Golpe Poderoso — executada, dano 0, MP −52 | 1776 / 3054 | 74 / 33 |
| 26 | p2 → p1 (score) | Quebra-Guarda — executada, dano 499, MP −63 | Ataque básico — executada, dano 140 | 1636 / 2573 | 29 / 55 |
| 27 | p2 → p1 (score) | Ataque básico — executada, dano 228 | Golpe Poderoso — executada, dano 239, MP −52 | 1397 / 2376 | 47 / 25 |
| 28 | p2 → p1 (score) | Ataque básico — executada, dano 228 | Ataque básico — executada, dano 0 | 1397 / 2148 | 65 / 47 |
| 29 | p2 → p1 (score) | Quebra-Guarda — executada, dano 332, MP −63 | Ataque básico — executada, dano 140 | 1257 / 1834 | 20 / 69 |
| 30 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 239, MP −52 | 1018 / 1865 | 38 / 39 |
| 31 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Ataque básico — executada, dano 0 | 1018 / 1865 | 56 / 61 |
| 32 | p2 → p1 (score) | Ataque básico — executada, dano 152 | Golpe Poderoso — executada, dano 0, MP −52 | 1018 / 1713 | 74 / 31 |
| 33 | p2 → p1 (score) | Quebra-Guarda — executada, dano 499, MP −63 | Ataque básico — executada, dano 140 | 878 / 1232 | 29 / 53 |
| 34 | p2 → p1 (score) | Ataque básico — executada, dano 0 | Golpe Poderoso — executada, dano 239, MP −52 | 639 / 1263 | 47 / 23 |
| 35 | p2 → p1 (score) | Ataque básico — executada, dano 183 | Ataque básico — executada, dano 140 | 499 / 1098 | 65 / 45 |
| 36 | p2 → p1 (score) | Quebra-Guarda — executada, dano 0, MP −63 | Ataque básico — executada, dano 140 | 359 / 1116 | 20 / 67 |
| 37 | p2 → p1 (score) | Ataque básico — cancelada por morte | Golpe Poderoso — executada, dano 382, MP −52 | -23 / 1165 | 20 / 37 |

