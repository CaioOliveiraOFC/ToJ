# Copa Arena 03 — a geração: 64 Guerreiros extraídos do PvE real

Gerado por `tools/arena_copa_03_geracao.py` e `tools/arena_copa_03.py`. Cada gladiador é um personagem que começou no nível 1 pela criação canônica de uma nova jornada, atravessou a dungeon jogado pelo BotPadrão (numa variante experimental de perfil e política) e saiu vivo pela Extração, com a Chave e o mecanismo do jogo.

> Perfil, política, RNG da jornada e RNG do duelo atuam juntos em cada gladiador. As tabelas mostram associações observadas nesta amostra, não efeitos causais isolados.

## Resumo

- **Geração original: 1315 runs**, 902 mortes (68.6%), 413 extrações (31.4%), 0 chegaram ao teto técnico vivas e 0 erros técnicos.
- **Seleção original: 53 aceitos** (conservador 22/22, moderado 21/21, hardcore 10/21). As quotas 22/21/21 NÃO foram cumpridas: o hardcore ficou em 10/21.
- **Preenchimento: 11 vagas**, por decisão do usuário, com 110 runs novas de conservador e moderado (73 mortes, 37 extrações, 12 na faixa).
- **Os 64 por perfil:** conservador 27, moderado 27, hardcore 10.
- Das 413 extrações, 53 ficaram na faixa de OP 20–30 (12.8%); 359 passaram de 30 e 1 ficaram abaixo de 20. 0 qualificada(s) chegaram depois de a quota do grupo fechar e ficaram de fora.
- OP dos 64 aceitos: média 28.99, mediana 29.23, mínimo 27.79, máximo 29.98.
- Nenhuma decisão de mapa fora das opções legais (0 ilegais em 89841 decisões). A agenda de risco mudou 6868 decisões (7.6%) em relação ao que o cérebro canônico faria no mesmo estado.
- Horizonte técnico: 200 andares; o andar mais fundo alcançado foi 28. Tempo de CPU somado das runs: 14.0 h.

## Protocolo

- **Seed.** Principal `20261025`. Cada tentativa: os 8 primeiros bytes (big-endian) de `sha256(f"{seed}:v2:{perfil}:{politica}:{k}")` (o piloto v1 usou `sha256(f"{seed}:{perfil}:{politica}:{k}")`). Nenhuma seed foi repetida, e o checkpoint recusa seed ou tentativa duplicada.
- **Run.** `BotPadrao` do repositório, classe `warrior`, criação por `create_player_for_new_run` com o gerador da run (nível 1, uma skill, Starter Kit sorteado). Teto técnico de 200 andares, o mesmo das auditorias de progressão. Nenhum item concedido, nenhuma oferta escolhida à mão, nenhum atributo mexido.
- **Variante experimental.** `BotExperimental` (subclasse em `tools/`) troca a política de escolha pelo atributo `picker` que o driver já consulta e aplica a agenda de risco do perfil: a linha de aposta a cada andar e a matriz de extração do perfil. O BotPadrão oficial, `src/` e as baselines não mudaram.
- **Aceite.** Guerreiro; run terminada pela Extração; vivo; Chave gasta e marca de extração no andar certo; snapshot pela serialização canônica do save (`to_save_data`), reconstruído por `player_from_save_data` (o caminho da Arena) com a mesma assinatura de build, o mesmo deck, passivas, equipamento, HP/MP máximos e nível, e a ida e volta reproduzindo o snapshot; `overall_power(...)` do reconstruído, sem cache, entre 20 e 30; vaga no grupo.
- **Ordem de aceite.** Dentro de cada grupo, as primeiras qualificadas pela ordem da tentativa, sem lacuna. Assim o resultado não depende de quantos processos rodaram nem de qual terminou antes. Tentativas que estavam em voo quando a quota fechou foram executadas e registradas.
- **Isolamento.** A Extração passa por `extraction.finish_run` com gravação em memória; nenhum slot, `saves/` ou `trophies.json` foi tocado.
- **Checkpoint.** Cada tentativa concluída foi gravada e sincronizada em disco no momento em que terminou; snapshots e estado da fila com escrita atômica. Retomar não repete runs nem mede de novo aceitos.
- **Quirk registrado.** A recarga canônica do save soma 1 a `ledger.items_equipped` por peça reequipada. É telemetria do livro-caixa, não build; a conferência de ida e volta ignora só esse contador.

## A escalada de risco: o que decide e o que foi medido

### O que foi verificado no BotPadrão

- `Perfil.hp_engajar` e `Perfil.mp_engajar` (55/15, 45/10, 38/5) **não são lidos por nenhuma decisão**. O docstring de `ProgressionState` diz que ficaram no driver por compatibilidade, e `tests/test_bot_observation.py` proíbe que voltem ao estado. Os três perfis oficiais jogam runs idênticas; baixar esses números não aumentaria risco.
- `DESVIO_ACEITAVEL`, `HP_SAUDAVEL`, `FOLGA_PARA_COMPRAR`, `HP_PARA_ALTAR` e `POCOES_PARA_SUSTENTAR` também não decidem mais nada; `_sinais_de_risco` só escreve no trace.
- O que decide no mapa é **um limiar**: `evaluators.HP_DE_APOSTA` (0.35). Ele mede a capacidade de cada luta (`hp − aposta`), decide quando curar vira SOBREVIVER ou RECUPERAR e quando a saída do andar vira descanso. Do lado do driver, `bot_padrao.HP_CRITICO` (0.35) é a mesma linha: abaixo dela a Loja pode gastar a reserva da saída em recuperação.
- **Continuar ou extrair** é a matriz `evaluators._MATRIZ` (banda da build contra o benchmark da Arena × fôlego observado). Não tem parâmetro; é outra constante de módulo lida no momento da chamada.
- **Sem alavanca externa, e por isso canônicos nos três perfis:** MP (o mapa não tem limiar de mana; ela só pesa dentro do duelo), desvio voluntário (o adaptador enumera todo serviço alcançável) e o combate (fuga, cura, buff e controle).

### Como a agenda foi aplicada

As duas linhas e a matriz são constantes de módulo lidas no momento da chamada. A variante as sobrescreve em tempo de execução, só dentro da run experimental, e as devolve ao valor canônico no fim (verificado em todas as runs). Não é um ponto de configuração que o projeto já declarava: é a menor intervenção que muda risco de verdade sem duplicar regra nem avaliador. Nenhum arquivo de `src/` ou de `tools/bot_padrao.py` mudou.

A linha de base sai do próprio perfil oficial: o driver documenta que o piso de engajamento fica 0,20 acima da linha crítica, então a linha do perfil é `hp_engajar − 0,20`. Com a profundidade ela desce 0.02 a cada 5 andares, até o piso.

| Perfil | Base | Piso | 1-5 | 6-10 | 11-15 | 16-20 | 21-25 | 26-30 |
|---|---|---|---|---|---|---|---|---|
| Conservador | 0.35 | 0.27 | 0.35 | 0.33 | 0.31 | 0.29 | 0.27 | 0.27 |
| Moderado | 0.25 | 0.19 | 0.25 | 0.23 | 0.21 | 0.19 | 0.19 | 0.19 |
| Hardcore | 0.18 | 0.12 | 0.18 | 0.16 | 0.14 | 0.12 | 0.12 | 0.12 |

### A decisão de extrair, por perfil (v2)

A matriz do perfil só ACRESCENTA preservação à canônica: a partir da banda indicada, o perfil preserva a build com qualquer fôlego; abaixo dela, e no hardcore inteiro, vale a canônica, que só preserva entre 0,95 e 1,05 do benchmark com o fôlego curto e acima de 1,05 sempre. O conservador sai mais cedo; o hardcore aposta mais.

| Perfil | Preserva com qualquer fôlego a partir de | OP equivalente |
|---|---|---|
| Conservador | CLOSE_ENOUGH | ≥ 27,7 |
| Moderado | META_BATIDA | ≥ 29,17 |
| Hardcore | HARD_STOP (canônica) | > 30,6 |

### O efeito medido: decisões que a agenda mudou

Em cada decisão de mapa, o mesmo estado foi avaliado de novo com a linha e a matriz canônicas (a decisão-sombra, sem consumir RNG). Uma divergência é uma decisão de família diferente (lutar em vez de beber, extrair em vez de seguir) num estado que a run realmente alcançou. O conservador nos andares 1–5 usa a linha canônica, então ali só a extração pode divergir.

| Perfil | Decisões | Divergentes | Taxa | /100 em 1-5 | /100 em 6-10 | /100 em 11-15 | /100 em 16-20 | /100 em 21-25 | /100 em 26-30 |
|---|---|---|---|---|---|---|---|---|---|
| Conservador | 7268 | 99 | 1.4% | 0.0 | 1.9 | 1.3 | 2.6 | 5.9 | 0.0 |
| Moderado | 10516 | 714 | 6.8% | 9.1 | 9.5 | 4.9 | 3.6 | 1.1 | 0.0 |
| Hardcore | 72057 | 6055 | 8.4% | 14.8 | 13.1 | 4.8 | 1.7 | 0.9 | 0.0 |

- Conservador: trocas mais frequentes (canônica→experimental) pocao→lutar ×27, lutar→extrair ×24, saida→lutar ×18, shop→lutar ×16, pocao→saida ×8, pocao→forge ×3; orçamento da Loja com a reserva tratada diferente em 22 de 5514 visitas.
- Moderado: trocas mais frequentes (canônica→experimental) pocao→lutar ×197, saida→lutar ×185, shop→lutar ×152, pocao→saida ×67, pocao→forge ×34, saida→forge ×23; orçamento da Loja com a reserva tratada diferente em 332 de 8040 visitas.
- Hardcore: trocas mais frequentes (canônica→experimental) pocao→lutar ×1801, shop→lutar ×1468, saida→lutar ×1463, pocao→saida ×588, pocao→forge ×251, saida→forge ×157; orçamento da Loja com a reserva tratada diferente em 3232 de 58480 visitas.

Leitura: a agenda mudou escolhas em estados alcançáveis em todos os perfis com linha diferente da canônica. Taxa de decisões mudadas, da maior para a menor: Hardcore 8.4%, Moderado 6.8%, Conservador 1.4%. 5331 das 6868 trocas foram para `lutar` (no lugar de beber poção, comprar cura, ir a um serviço ou sair para descansar). A agenda não desliga proteção: abaixo da linha o cérebro continua mandando curar ou sair, e a fuga dentro do duelo é a canônica.

## O piloto v1 e a decisão de extrair

A primeira versão da variante mexia só na linha de aposta e deixava a matriz de extração canônica nos três perfis. Ela rodou como piloto, com as seeds `sha256(f"{seed}:{perfil}:{politica}:{k}")`, e foi interrompida por decisão do usuário diante do resultado abaixo. Nenhuma build dela entrou na Copa; as runs estão em `runs_piloto.jsonl`.

- 195 runs: 133 mortes, 62 extrações, 1 na faixa de OP 20–30.
- OP das extrações: de 29.29 a 36.67 (mediana 32.29).
- Banda da build quando o bot decidiu preservar: CLOSE_ENOUGH ×1, HARD_STOP ×61.
- Em 22 de 23 oportunidades de extração com a build entre 0,95 e 1,05 do benchmark (OP 27,7–30,6), a matriz canônica mandou continuar: o fôlego estava saudável.
- Projeção daquele ritmo: cerca de 12.480 runs para as 64 vagas, com os grupos do conservador e do moderado sem nenhuma extração na faixa.

Por isso a v2 pôs a decisão de continuar ou extrair na agenda do perfil (seção anterior). O que não mudou: a dungeon, o motor, o `overall_power`, a faixa de OP, a linha de aposta e o critério de aceite.

## Runs necessárias, por grupo

| Grupo | Quota | Runs | Última aceita | Mortes | Extrações | Na faixa | OP > 30 | OP < 20 | Sem vaga | Após a quota |
|---|---|---|---|---|---|---|---|---|---|---|
| Conservador/survival | 8 | 36 | #36 | 26 (72%) | 10 (28%) | 8 | 2 | 0 | 0 | 0 |
| Conservador/offense | 7 | 33 | #33 | 22 (67%) | 11 (33%) | 7 | 4 | 0 | 0 | 0 |
| Conservador/economy | 7 | 36 | #36 | 22 (61%) | 14 (39%) | 7 | 7 | 0 | 0 | 0 |
| Moderado/survival | 7 | 25 | #25 | 12 (48%) | 13 (52%) | 7 | 6 | 0 | 0 | 0 |
| Moderado/offense | 7 | 73 | #73 | 53 (73%) | 20 (27%) | 7 | 13 | 0 | 0 | 0 |
| Moderado/economy | 7 | 63 | #61 | 49 (78%) | 14 (22%) | 7 | 7 | 0 | 0 | 2 |
| Hardcore/survival | 7 | 234 | #232 | 152 (65%) | 82 (35%) | 5 | 77 | 0 | 0 | 0 |
| Hardcore/offense | 7 | 363 | #217 | 264 (73%) | 99 (27%) | 3 | 95 | 1 | 0 | 0 |
| Hardcore/economy | 7 | 452 | #326 | 302 (67%) | 150 (33%) | 2 | 148 | 0 | 0 | 0 |

"Última aceita" é o número da tentativa que fechou a quota; "após a quota" são as que já estavam em voo quando isso aconteceu e terminaram depois.

## O preenchimento

Depois de 1315 tentativas da geração original (conservador 22/22, moderado 21/21, hardcore 10/21), o usuário retirou a obrigatoriedade das quotas: a seleção original fica, e as vagas restantes vão para novas runs v2 de conservador e moderado, perto de 50/50, com as políticas equilibradas.

- Seleção original mantida inteira: 53 gladiadores, com snapshots, seeds e builds como estavam.
- Qualificadas que sobraram no checkpoint: 0 (nenhuma extração com OP acima de 30 foi usada).
- Tentativas interrompidas no encerramento da geração original (em voo, sem resultado registrado): hardcore-offense #360, hardcore-economy #450.
- Regra das vagas novas (determinística): a política com menos gladiadores nos 64 (empate: survival, offense, economy) e, dentro dela, o perfil com menos vagas novas nessa política (empate: menos vagas novas no total; depois conservador). Cada grupo continua a própria numeração de tentativas depois da última da geração original, com as seeds v2 e o mesmo BotExperimental (linha de aposta e matriz de extração do perfil).
- 110 runs no preenchimento: 73 mortes, 37 extrações (33.6%), 12 na faixa (aprovação por OP: 32.4% das extrações).

| Grupo | Vagas | Primeira tentativa | Runs | Aceitas (tentativas) |
|---|---|---|---|---|
| Conservador/survival | 1 | #37 | 9 | #44 |
| Conservador/offense | 2 | #34 | 14 | #35, #43 |
| Conservador/economy | 2 | #37 | 4 | #39, #40 |
| Moderado/survival | 1 | #26 | 11 | #33 |
| Moderado/offense | 2 | #74 | 34 | #83, #101 |
| Moderado/economy | 3 | #64 | 38 | #80, #93, #100 |

### Distribuição final dos 64

Não é a distribuição das quotas originais: ela mistura a seleção original e o preenchimento.

| Perfil | survival | offense | economy | Total | Do preenchimento |
|---|---|---|---|---|---|
| Conservador | 9 | 9 | 9 | 27 | 5 |
| Moderado | 8 | 9 | 10 | 27 | 6 |
| Hardcore | 5 | 3 | 2 | 10 | 0 |
| Total | 22 | 21 | 21 | 64 | 11 |

## Morte e extração por perfil e por política

| Perfil | Runs | Mortes | Mortes até o andar 5 | Andar de morte (média · mediana) | HP ao entrar na luta fatal (mediana) | Extrações | Aprovação por OP (na faixa / extrações) | Na faixa / runs | Combates por run | Fugas por run | Poções bebidas por run |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | 105 | 70 (66.7%) | 33 | 6.0 · 6 | 43% | 35 (33.3%) | 22 (62.9%) | 21.0% | 49.6 | 6.40 | 2.54 |
| Moderado | 161 | 114 (70.8%) | 74 | 4.7 · 4 | 41% | 47 (29.2%) | 21 (44.7%) | 13.0% | 47.8 | 5.81 | 1.67 |
| Hardcore | 1049 | 718 (68.4%) | 551 | 4.0 · 4 | 36% | 331 (31.6%) | 10 (3.0%) | 1.0% | 51.4 | 5.27 | 1.07 |

| Política | Runs | Mortes | Extrações | Na faixa | OP médio das extrações |
|---|---|---|---|---|---|
| survival | 295 | 190 (64.4%) | 105 (35.6%) | 20 | 31.50 |
| offense | 469 | 339 (72.3%) | 130 (27.7%) | 17 | 32.21 |
| economy | 551 | 373 (67.7%) | 178 (32.3%) | 16 | 32.16 |

### Sobrevivência por andar

Fração das runs que entrou viva no andar:

| Perfil | Andar 1 | Andar 2 | Andar 3 | Andar 5 | Andar 8 | Andar 10 | Andar 12 | Andar 15 | Andar 18 | Andar 20 | Andar 22 | Andar 25 | Andar 28 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Conservador | 100.0% | 95.2% | 91.4% | 76.2% | 53.3% | 40.0% | 36.2% | 35.2% | 29.5% | 20.0% | 3.8% | 0.0% | 0.0% |
| Moderado | 100.0% | 86.3% | 78.9% | 61.5% | 42.2% | 35.4% | 31.7% | 30.4% | 28.0% | 21.1% | 9.9% | 1.2% | 0.0% |
| Hardcore | 100.0% | 87.8% | 74.3% | 56.3% | 38.8% | 35.0% | 32.7% | 31.7% | 31.1% | 27.0% | 15.6% | 2.2% | 0.1% |

| Perfil | Mortes em 1-5 | Mortes em 6-10 | Mortes em 11-15 | Mortes em 16-20 | Mortes em 21-25 | Mortes em 26-30 |
|---|---|---|---|---|---|---|
| Conservador | 33 | 33 | 2 | 2 | 0 | 0 |
| Moderado | 74 | 36 | 2 | 2 | 0 | 0 |
| Hardcore | 551 | 149 | 17 | 1 | 0 | 0 |

## Overall Power das extrações

413 extrações medidas. Distribuição por unidade de OP (o número é o piso do intervalo):

| OP | 5 | 27 | 28 | 29 | 30 | 31 | 32 | 33 | 34 | 35 | 36 | 37 | 38 | 39 | 40 | 42 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| extrações | 1 | 10 | 14 | 29 | 61 | 139 | 48 | 34 | 37 | 18 | 5 | 12 | 1 | 1 | 2 | 1 |

- Na faixa 20–30: 53; acima de 30: 359; abaixo de 20: 1.
- OP médio de todas as extrações: 32.01; dos aceitos: 28.99.

### A banda da build no momento da extração

Extrair exige a Chave no bolso e a casa `E` alcançável no andar; a banda é a da build contra o benchmark da Arena (OP 29,17) quando o bot decidiu preservar. Uma extração acima de 30 é uma em que a primeira oportunidade depois de cruzar a banda do perfil já caiu acima de 30, ou, no hardcore, uma em que o fôlego seguiu saudável até 1,05:

| Perfil | ABAIXO | CLOSE_ENOUGH | META_BATIDA | HARD_STOP |
|---|---|---|---|---|
| Conservador | 0 | 17 | 9 | 9 |
| Moderado | 0 | 0 | 24 | 23 |
| Hardcore | 1 | 9 | 2 | 319 |

Nada aqui foi ajustado para caber na faixa: a extração fora dela foi registrada e descartada, e a geração continuou até as vagas fecharem.

## Andares e níveis dos 64

Andar de extração: média 19.2 (de 16 a 22). Nível: média 21.9 (de 18 a 24).

| Andar | 16 | 17 | 18 | 19 | 20 | 21 | 22 |
|---|---|---|---|---|---|---|---|
| gladiadores | 1 | 9 | 7 | 18 | 18 | 10 | 1 |

| Nível | 18 | 19 | 20 | 21 | 22 | 23 | 24 |
|---|---|---|---|---|---|---|---|
| gladiadores | 1 | 2 | 6 | 11 | 19 | 21 | 4 |

## Equipamento, aprimoramentos, gemas e encantos (os 64)

- 638 peças equipadas (10.0 por gladiador). Raridade: Comum 244, Rara 332, Épica 50, Lendária 12.
- Ferreiro: 165 peças com `+N` (soma 186, maior +2); 161 peças com gema (204 gemas); 60 com encanto (60 encantos).
- Peças do Starter Kit ainda equipadas: 15.
- Peças mais comuns: Amuleto da Mana ×23, Anel da Esmeralda ×22, Anel Vegetal ×21, Anel de Diamante ×18, Botas de Aço ×17, Luvas de Aço ×17, Perneiras de Aço ×17, Amuleto da Vida ×16, Calça de Cota ×16, Capacete de Ferro ×16, Anel de Palha ×14, Anel de Bronze ×14.

## Skills e passivas (os 64)

- Decks distintos: 64 de 64. Conjuntos de passivas distintos: 64. Equipamentos distintos: 64.
- Cartas no deck: Mira Calma ×26, Golpe Poderoso ×23, Quebra-Guarda ×12, Cutelada ×11, Investida ×11, Tomar Fôlego ×10, Respirar Fundo ×9, Soco de Placa ×8, Areia no Chão ×7, Estocada Seca ×7, Postura de Muro ×7, Baluarte ×6, Mão Dupla ×6, Escudo Protetor ×6, Leitura de Terreno ×5, Golpe Duplo ×5, Tremor de Bigorna ×5, Fúria ×4, Peso do Machado ×4, Golpe Devastador ×4.
- Famílias de passiva: max_hp ×219, strength ×117, life_steal ×110, max_mp ×89, crit_chance ×87, essence_bonus ×73, agility ×72, damage_reduction ×71, defense ×66, mana_regen ×60, damage_percent ×58, precision ×57, status_resistance ×47, magic ×45, potion_heal_bonus ×38, bleed_chance ×26, crit_damage ×25, gold_drop_bonus ×24, stun_chance ×19, fear_chance ×14, poison_chance ×12, evasion ×9, death_ignore ×2.
- Raridade das passivas: Comum 836, Rara 370, Épica 116, Lendária 18.
- Passivas mais repetidas: Sangue de Guerreiro ×85, Coração de Ferro ×76, Boca de Sangue ×65, Músculos de Aço ×64, Olho de Águia ×53, Pele Grossa ×46, Postura Fechada ×43, Pele de Sal ×43, Sorte de Principiante ×41, Respiração Contada ×39, Passo de Corça ×38, Sede Silenciosa ×37, Ódio Baixo ×37, Reserva Arcana ×36, Mente Serena ×36.

## Builds de crítico, defesa, controle e sustento

Leitura feita DEPOIS da geração, só para descrever; nenhuma build foi escolhida por isso. Regras: crítico = 3+ passivas de crítico; defesa = metade ou mais das passivas em vida/defesa/redução/esquiva/resistência, ou carta de redução no deck; controle = carta de atordoar/sono/congelar/medo ou passiva de chance de atordoar/medo; sustento = carta de cura ou 2+ passivas de roubo de vida/bônus de poção/ignorar a morte. Uma build pode ter vários canais.

- Nos 64 aceitos: sustento ×40, defesa ×26, controle ×19, crítico ×18, sem canal dominante ×4.
- Em todas as 413 extrações: sustento ×286, defesa ×144, crítico ×134, controle ×101, sem canal dominante ×13.

## Diversidade entre os nove grupos

| Grupo | n | OP médio | Nível médio | Andar médio | Decks distintos | Famílias mais frequentes | Canais |
|---|---|---|---|---|---|---|---|
| Conservador/survival | 9 | 28.21 | 21.7 | 19.7 | 9 | max_hp ×48, damage_reduction ×21, defense ×19 | sustento ×8, defesa ×6, crítico ×2 |
| Conservador/offense | 9 | 28.65 | 20.6 | 19.0 | 9 | strength ×30, damage_percent ×19, magic ×18 | controle ×7, crítico ×6, defesa ×2, sustento ×2 |
| Conservador/economy | 9 | 28.74 | 21.9 | 17.8 | 9 | essence_bonus ×35, max_mp ×33, life_steal ×24 | sustento ×7, defesa ×3 |
| Moderado/survival | 8 | 29.59 | 22.4 | 20.0 | 8 | max_hp ×49, damage_reduction ×19, defense ×14 | sustento ×8, defesa ×6, crítico ×2, controle ×1 |
| Moderado/offense | 9 | 29.76 | 22.1 | 19.4 | 9 | strength ×28, damage_percent ×24, crit_chance ×23 | controle ×8, crítico ×7 |
| Moderado/economy | 10 | 29.61 | 22.8 | 18.8 | 10 | max_mp ×32, max_hp ×32, essence_bonus ×31 | sustento ×9, defesa ×3, controle ×1 |
| Hardcore/survival | 5 | 28.48 | 21.8 | 19.8 | 5 | max_hp ×28, life_steal ×13, agility ×13 | sustento ×4, defesa ×4 |
| Hardcore/offense | 3 | 28.37 | 21.7 | 20.0 | 3 | strength ×14, magic ×9, damage_percent ×7 | controle ×2, crítico ×1, defesa ×1 |
| Hardcore/economy | 2 | 28.25 | 23.5 | 19.5 | 2 | life_steal ×9, essence_bonus ×7, max_hp ×5 | sustento ×2, defesa ×1 |

Semelhança média dos decks (Jaccard das cartas) entre dois gladiadores do mesmo grupo: 0.11; de grupos diferentes: 0.08.

## Builds marcantes

Apontadas depois da geração, só para descrever.

- Mais trabalho de Ferreiro: SkipNhO (W52, Hardcore/economy), `+6` somados nas peças.
- Mais gemas encaixadas: PlayHard (W18, Conservador/economy), 10.
- Mais passivas Épicas ou Lendárias: brtt (W13, Conservador/offense), 6 (0 Lendária(s)).
- Mais passivas de crítico: casimito (W55, Moderado/offense), 7.
- Cartas que só um dos 64 levou: Sede de Batalha (yayahuz (W07, Conservador/survival)); Investida de Aríete (Patriota (W10, Conservador/offense)); Última Carta (Forever (W11, Conservador/offense)); Encarar (blackoutz (W12, Conservador/offense)); Silêncio do Veterano (sacy (W16, Conservador/economy)); Fio no Rebite (k13tv (W17, Conservador/economy)); Resistência Heróica (PlayHard (W18, Conservador/economy)); Olho de Ferreiro (boltz (W21, Conservador/economy)).
- Extração mais funda: XANDAOOGOD (W47, Hardcore/survival), andar 22, nível 23; mais rasa: tteuw (W19, Conservador/economy), andar 16, nível 19.
- Maior OP: brtt (W13, Conservador/offense), 29.98; menor: yayahuz (W07, Conservador/survival), 27.79.

## Risco, sobrevivência e poder extraído

> Perfil, política, RNG da jornada e RNG do duelo atuam juntos em cada gladiador. As tabelas mostram associações observadas nesta amostra, não efeitos causais isolados.

| Perfil | Mortes | Extrações | OP médio das extrações | OP médio dos aceitos | Andar médio dos aceitos | Runs por aceito na seleção original |
|---|---|---|---|---|---|---|
| Conservador | 66.7% | 33.3% | 29.68 | 28.53 | 18.9 | 4.8 |
| Moderado | 70.8% | 29.2% | 31.20 | 29.67 | 19.4 | 7.7 |
| Hardcore | 68.4% | 31.6% | 32.37 | 28.40 | 19.8 | 104.9 |

## Os 64, na ordem de aceite

| ID | Nick | Perfil | Política | Tentativa | Seed | Andar | Nível | OP | Canais | Origem |
|---|---|---|---|---|---|---|---|---|---|---|
| W01 | dona | Conservador | survival | 7 | `2832237389801836401` | 21 | 23 | 29.06 | sustento | seleção original |
| W02 | alanzoka | Conservador | survival | 13 | `6058608939898478784` | 20 | 23 | 28.37 | defesa, sustento | seleção original |
| W03 | jukes | Conservador | survival | 15 | `812624488608970650` | 21 | 22 | 28.14 | defesa, sustento | seleção original |
| W04 | belrodrigues | Conservador | survival | 19 | `1846572177730036279` | 19 | 21 | 27.91 | defesa | seleção original |
| W05 | Dilera | Conservador | survival | 20 | `3994255704300115112` | 19 | 21 | 27.91 | defesa, sustento | seleção original |
| W06 | Baiano | Conservador | survival | 24 | `1025959111049801620` | 20 | 21 | 27.91 | defesa, sustento | seleção original |
| W07 | yayahuz | Conservador | survival | 30 | `3208297028327239230` | 20 | 22 | 27.79 | defesa, sustento | seleção original |
| W08 | Tenz | Conservador | survival | 36 | `4130039241501877988` | 20 | 23 | 28.71 | crítico, sustento | seleção original |
| W09 | brino | Conservador | offense | 4 | `18241902303696388387` | 17 | 18 | 28.02 | crítico, controle | seleção original |
| W10 | Patriota | Conservador | offense | 7 | `7926199109757061183` | 21 | 22 | 29.87 | controle | seleção original |
| W11 | Forever | Conservador | offense | 17 | `14613271384846002655` | 20 | 22 | 28.71 | crítico, defesa, controle | seleção original |
| W12 | blackoutz | Conservador | offense | 21 | `1797578634168002903` | 19 | 20 | 27.79 | crítico, defesa | seleção original |
| W13 | brtt | Conservador | offense | 22 | `7532868956086172557` | 20 | 21 | 29.98 | controle, sustento | seleção original |
| W14 | G0ularte | Conservador | offense | 24 | `6291530132541431858` | 19 | 21 | 28.02 | crítico, controle, sustento | seleção original |
| W15 | RazaH | Conservador | offense | 33 | `6882643742210834252` | 18 | 20 | 29.06 | crítico, controle | seleção original |
| W16 | sacy | Conservador | economy | 3 | `16876277710936082885` | 19 | 23 | 29.52 | sustento | seleção original |
| W17 | k13tv | Conservador | economy | 15 | `1590218668709156032` | 18 | 23 | 27.91 | defesa, sustento | seleção original |
| W18 | PlayHard | Conservador | economy | 23 | `5988562094137102994` | 17 | 21 | 28.02 | — | seleção original |
| W19 | tteuw | Conservador | economy | 24 | `18064938851122302866` | 16 | 19 | 29.17 | defesa, sustento | seleção original |
| W20 | xandfps | Conservador | economy | 26 | `15403883440795817470` | 17 | 21 | 28.48 | sustento | seleção original |
| W21 | boltz | Conservador | economy | 32 | `15217593058595529711` | 17 | 21 | 27.79 | sustento | seleção original |
| W22 | jovirone | Conservador | economy | 36 | `8138257030839068038` | 17 | 24 | 29.52 | sustento | seleção original |
| W23 | lubatv | Moderado | survival | 9 | `6639738590781069291` | 20 | 22 | 29.17 | crítico, sustento | seleção original |
| W24 | fnxLNTC | Moderado | survival | 11 | `12625970359534049939` | 19 | 22 | 29.52 | defesa, sustento | seleção original |
| W25 | mount | Moderado | survival | 14 | `165671388714954225` | 21 | 23 | 29.52 | defesa, sustento | seleção original |
| W26 | MeikodRJ | Moderado | survival | 15 | `3771523583190698800` | 19 | 22 | 29.75 | sustento | seleção original |
| W27 | aspaszin | Moderado | survival | 18 | `14843769489525258320` | 19 | 22 | 29.29 | crítico, defesa, sustento | seleção original |
| W28 | furq | Moderado | survival | 19 | `4703126176621684437` | 21 | 23 | 29.52 | defesa, controle, sustento | seleção original |
| W29 | DavyJones | Moderado | survival | 25 | `5183847945833891140` | 20 | 22 | 29.98 | defesa, sustento | seleção original |
| W30 | bakzera | Moderado | offense | 6 | `2794895444418811611` | 20 | 23 | 29.98 | crítico, controle | seleção original |
| W31 | Felps | Moderado | offense | 9 | `375831289381730531` | 17 | 20 | 29.64 | crítico, controle | seleção original |
| W32 | loud_thurzin | Moderado | offense | 37 | `4152108452749171475` | 19 | 22 | 29.87 | crítico, controle | seleção original |
| W33 | YoDa | Moderado | offense | 45 | `12897313214226887121` | 18 | 21 | 29.41 | controle | seleção original |
| W34 | LuquEt4 | Moderado | offense | 47 | `2809686733962074657` | 21 | 23 | 29.87 | crítico | seleção original |
| W35 | Smzinho | Moderado | offense | 48 | `11635301397804779693` | 20 | 23 | 29.75 | controle | seleção original |
| W36 | Gaules | Moderado | offense | 73 | `4961004880316520679` | 20 | 22 | 29.98 | crítico, controle | seleção original |
| W37 | gafallen | Moderado | economy | 2 | `9669742153661310724` | 17 | 20 | 29.87 | sustento | seleção original |
| W38 | Neskwga | Moderado | economy | 6 | `650757519477940328` | 18 | 22 | 29.41 | defesa, sustento | seleção original |
| W39 | yeTz | Moderado | economy | 43 | `488179884306871621` | 20 | 23 | 29.87 | sustento | seleção original |
| W40 | NOBRU | Moderado | economy | 44 | `2844704781525308444` | 19 | 23 | 29.75 | sustento | seleção original |
| W41 | coldzin | Moderado | economy | 50 | `9284565610362645380` | 21 | 24 | 29.64 | sustento | seleção original |
| W42 | RNakano | Moderado | economy | 57 | `4580664160974118811` | 19 | 24 | 29.64 | sustento | seleção original |
| W43 | aXtLOL | Moderado | economy | 61 | `16872040783703285537` | 20 | 23 | 29.75 | sustento | seleção original |
| W44 | calango | Hardcore | survival | 42 | `2645495527007246633` | 19 | 22 | 28.60 | sustento | seleção original |
| W45 | Hayashii | Hardcore | survival | 179 | `15214951623552712880` | 20 | 22 | 27.91 | defesa, sustento | seleção original |
| W46 | PaulinhoLOKObr | Hardcore | survival | 199 | `10006103864399723504` | 20 | 22 | 28.48 | defesa, sustento | seleção original |
| W47 | XANDAOOGOD | Hardcore | survival | 212 | `16962208254202598663` | 22 | 23 | 29.64 | defesa | seleção original |
| W48 | Bagi | Hardcore | survival | 232 | `15085905063680726777` | 18 | 20 | 27.79 | defesa, sustento | seleção original |
| W49 | Bisteconee | Hardcore | offense | 66 | `2487864230724086036` | 20 | 22 | 28.60 | controle | seleção original |
| W50 | hastad | Hardcore | offense | 164 | `4385105589953273700` | 21 | 22 | 28.60 | crítico, defesa, controle | seleção original |
| W51 | suetam1v4 | Hardcore | offense | 217 | `12730939534942729493` | 19 | 21 | 27.91 | — | seleção original |
| W52 | SkipNhO | Hardcore | economy | 3 | `13489461355466704452` | 19 | 23 | 28.02 | defesa, sustento | seleção original |
| W53 | babi | Hardcore | economy | 326 | `12624093366700675930` | 20 | 24 | 28.48 | sustento | seleção original |
| W54 | TheBurntPeanut | Conservador | economy | 39 | `16267420974496528008` | 20 | 23 | 29.64 | — | preenchimento (run nova) |
| W55 | casimito | Moderado | offense | 83 | `9680521760163710385` | 21 | 23 | 29.75 | crítico, controle | preenchimento (run nova) |
| W56 | sofiaespanha | Moderado | economy | 80 | `17466784782611362638` | 17 | 23 | 29.29 | defesa, controle | preenchimento (run nova) |
| W57 | Coringa | Conservador | offense | 35 | `2589369501754876463` | 18 | 20 | 27.79 | — | preenchimento (run nova) |
| W58 | JonVlogs | Conservador | economy | 40 | `8172921485304172074` | 19 | 22 | 28.60 | defesa, sustento | preenchimento (run nova) |
| W59 | liminhag0d | Moderado | offense | 101 | `2418842632503645723` | 19 | 22 | 29.64 | crítico, controle | preenchimento (run nova) |
| W60 | frttt | Moderado | economy | 93 | `10776659354567911830` | 19 | 23 | 29.52 | sustento | preenchimento (run nova) |
| W61 | Tealzlol | Conservador | survival | 44 | `5167399243287148898` | 17 | 19 | 28.14 | crítico, sustento | preenchimento (run nova) |
| W62 | gabepeixe | Conservador | offense | 43 | `2193193603985627856` | 19 | 21 | 28.60 | crítico, controle | preenchimento (run nova) |
| W63 | tioorochitwitch | Moderado | economy | 100 | `14337888470259174021` | 18 | 23 | 29.41 | defesa, sustento | preenchimento (run nova) |
| W64 | fer | Moderado | survival | 33 | `6146495459393456226` | 21 | 23 | 29.98 | defesa, sustento | preenchimento (run nova) |

Snapshots canônicos em `snapshots/`, metadados e assinatura de cada build em `gladiadores.json`, e cada tentativa em `runs.jsonl` (geração original) e `runs_preenchimento.jsonl` (preenchimento).

