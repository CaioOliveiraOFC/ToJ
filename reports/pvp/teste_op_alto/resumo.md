# Teste: gladiadores extraídos com OP 40–70

Gerados por `python tools/arena_teste_op_alto.py`: runs reais do BotExperimental (perfis
conservador e moderado, as três políticas) desde a criação do personagem até a Extração,
pelo mesmo caminho da população da Arena (`tools/arena_copa_03_geracao.executar`). A única
diferença é o alvo de OP da decisão de extrair (45, 55 ou 65 em vez de 29,17), trocado só
dentro dos processos do teste. **Não fazem parte do catálogo da Arena.**

60 tentativas (49 mortes, 11 extrações); 10 aceitos, no máximo 4 por classe. Cada run se refaz pela seed (`k` em `tentativas.jsonl`).

| arquivo | classe | nível | OP | andar | perfil/política (alvo) | HP | MP | ST | MG | AG | DF | arma | skills |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| `M08_op63.2.json` | Mage | 43 | 63.2 | 40 | conservador/offense (65) | 43358 | 31374 | 4414 | 8789 | 1167 | 5306 | Cajado do Equilíbrio | Bola de Fogo, Hora Parada, Lasca de Gelo, Passo Borrado |
| `W09_op62.5.json` | Warrior | 38 | 62.5 | 35 | conservador/offense (65) | 46389 | 4401 | 3868 | 2247 | 752 | 3310 | Espada Lendária +2 | Golpe Devastador, Carga do Condenado, Olho Treinado, Areia no Chão |
| `W10_op54.4.json` | Warrior | 39 | 54.4 | 37 | conservador/survival (55) | 44130 | 6793 | 3635 | 2488 | 780 | 3317 | Machado de Guerra | Marca do Caçador, Quebra-Guarda, Provocação, Respirar Fundo |
| `M05_op50.0.json` | Mage | 37 | 50.0 | 35 | moderado/offense (45) | 28901 | 8967 | 2324 | 3656 | 548 | 2362 | Clava de Madeira | Relâmpago, Guarda Cruzada, Travar o Pulso, Explosão Arcana |
| `R01_op49.7.json` | Rogue | 32 | 49.7 | 30 | conservador/offense (45) | 11905 | 4403 | 1796 | 1080 | 978 | 1468 | Machado de Guerra | Golpe nas Sombras, Mão Leve, Mira Calma, Estocada Seca |
| `M06_op47.4.json` | Mage | 39 | 47.4 | 36 | moderado/survival (45) | 34931 | 20054 | 2606 | 3863 | 731 | 3150 | Machado de Guerra | Bola de Fogo, Mira Calma, Respirar Fundo, Vigor Emprestado |
| `R07_op45.6.json` | Rogue | 37 | 45.6 | 30 | moderado/economy (45) | 27146 | 5422 | 2850 | 2252 | 1693 | 2138 | Machado de Guerra | Ataque Furtivo, Corte de Tendão, Lançar Adaga, Olho do Falcão |
| `R04_op45.4.json` | Rogue | 31 | 45.4 | 29 | moderado/survival (45) | 13579 | 2978 | 1572 | 959 | 830 | 1223 | Adaga Mortal +1 | Ataque Furtivo, Respirar Fundo, Voto de Silêncio, Assassinato |
| `M03_op43.5.json` | Mage | 37 | 43.5 | 31 | conservador/economy (45) | 32845 | 9054 | 1854 | 4174 | 616 | 2436 | Cajado Eterno | Relâmpago, Marca do Caçador, Gancho e Corda, Disciplina de Forja |
| `R02_op43.1.json` | Rogue | 35 | 43.1 | 26 | conservador/economy (45) | 16380 | 5917 | 2269 | 1509 | 1254 | 1582 | Espada de Aço | Testamento do Ladrão, Dança das Lâminas, Fôlego de Marcha, Envenenar |
