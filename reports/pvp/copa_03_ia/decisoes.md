# Copa Arena 03 v2 — Inteligência Estratégica — as decisões da IA

A IA tomou 3564 decisões nas 63 partidas auditadas; em 3005 havia mais de uma ação legal (sem contar a rendição). Nessas, ela escolheu o mesmo que a `PoliticaCopa` escolheria NA MESMA VISÃO em 760 (25,3%) e divergiu em 2245.

A `PoliticaCopa` é consultada em cada visão só para registro — ela não influencia a escolha. As explicações abaixo usam apenas o que estava disponível no momento: a visão (HP/MP dos dois, efeitos e buffs visíveis, ações legais, recargas) e as estimativas que a IA calculou com o modelo dela do adversário.

## Onde divergiram

| A PoliticaCopa faria | A IA fez | Vezes |
|---|---|---|
| buff | dano | 400 |
| buff | básico | 350 |
| redução de dano | dano | 314 |
| dano | básico | 313 |
| status | dano | 244 |
| status | básico | 150 |
| dano | dano | 121 |
| redução de dano | básico | 103 |
| dano | cura | 54 |
| buff | status | 49 |
| cura | dano | 26 |
| dano | buff | 25 |
| status | buff | 19 |
| status | cura | 15 |
| redução de dano | cura | 13 |
| cura | básico | 13 |
| buff | cura | 11 |
| básico | buff | 7 |
| buff | redução de dano | 4 |
| básico | cura | 3 |
| redução de dano | buff | 3 |
| buff | buff | 2 |
| cura | buff | 2 |
| dano | status | 1 |
| básico | status | 1 |
| status | status | 1 |
| cura | status | 1 |

## Por quê, caso a caso

Em cada categoria, o caso em que a IA via mais diferença entre a escolha dela e a da política, e um caso típico (o da diferença mediana):

### A política: buff → a IA: dano

- Leitura: a política lança todo buff que não está ativo; a IA compara o buff com o golpe que ele substitui, e o buff só vence quando ainda há oportunidades suficientes para ele render.

**O caso mais nítido.** Oitavas 5 — frttt × Neskwga, rodada 18, frttt. Na tela: HP 176/5379, MP 266/1042; o adversário com HP 591/6216, MP 96/668, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Pausa Útil**: Pausa Útil é legal e não está ativo (buffs visíveis: []).
- A IA fez **Mira Calma** (justificativa registrada por ela): P(vitória) 0.950±0.053 com Mira Calma; contra ataque básico 0.100, Pausa Útil 0.100, Estocada Seca 0.100; dano esperado 734; chance de derrubar já 95%; custa 116 MP.
- Todas as opções avaliadas: Mira Calma P 0,950, 116 MP, chance de derrubar 95,0%; ataque básico P 0,100; Pausa Útil P 0,100, 52 MP; Estocada Seca P 0,100, 70 MP.
- Modelo do adversário naquele momento: ofensa ×0,80, defesa ×1,19 sobre a priori; cartas reveladas: Escudo Protetor, Golpe Duplo, Golpe Poderoso, Mira Calma.

**Um caso típico.** Fase de 64 31 — aspaszin × sacy, rodada 18, aspaszin. Na tela: HP 2961/4874, MP 375/882; o adversário com HP 5307/7520, MP 66/786, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fôlego de Marcha**: Fôlego de Marcha é legal e não está ativo (buffs visíveis: []).
- A IA fez **Quebra-Guarda** (justificativa registrada por ela): P(vitória) 0.316±0.021 com Quebra-Guarda; contra ataque básico 0.309, Fôlego de Marcha 0.295; dano esperado 236; custa 63 MP.
- Todas as opções avaliadas: Quebra-Guarda P 0,316, 63 MP; ataque básico P 0,309; Fôlego de Marcha P 0,295, 73 MP.
- Modelo do adversário naquele momento: ofensa ×0,70, defesa ×0,80 sobre a priori; cartas reveladas: Escudo Protetor, Golpe Duplo.

### A política: buff → a IA: básico

- Leitura: a política lança todo buff que não está ativo; a IA não lança buff quando ele não tem rodadas suficientes para render mais que o golpe que custa — no fim da luta, ou com o MP guardado para uma carta que vale mais.

**O caso mais nítido.** Fase de 64 18 — bakzera × furq, rodada 24, bakzera. Na tela: HP 325/5860, MP 128/1020; o adversário com HP 622/6074, MP 28/756, efeitos frailty; buffs próprios nenhum.

- A `PoliticaCopa` faria **Veterania**: Veterania é legal e não está ativo (buffs visíveis: []).
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.800±0.096 com ataque básico; contra Mira Calma 0.700, Veterania 0.138, Provocação 0.043; dano esperado 173.
- Todas as opções avaliadas: ataque básico P 0,800; Mira Calma P 0,700, 116 MP, chance de derrubar 14,2%; Veterania P 0,138, 111 MP; Provocação P 0,043, 71 MP.
- Modelo do adversário naquele momento: ofensa ×1,03, defesa ×0,99 sobre a priori; cartas reveladas: Areia no Chão, Estocada Seca, Golpe Poderoso, Guarda Cruzada, Quebra-Guarda.

**Um caso típico.** Fase de 64 13 — SkipNhO × Tealzlol, rodada 7, Tealzlol. Na tela: HP 2981/4334, MP 281/510; o adversário com HP 5326/7167, MP 497/766, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fôlego de Marcha**: Fôlego de Marcha é legal e não está ativo (buffs visíveis: []).
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.225±0.018 com ataque básico; contra Mira Calma 0.219, Ritmo de Duelo 0.215, Fôlego de Marcha 0.208; dano esperado 81.
- Todas as opções avaliadas: ataque básico P 0,225; Mira Calma P 0,219, 73 MP; Ritmo de Duelo P 0,215, 67 MP; Fôlego de Marcha P 0,208, 52 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,26 sobre a priori; cartas reveladas: Golpe Poderoso.

### A política: redução de dano → a IA: dano

- Leitura: a política ergue toda redução de dano inativa; a IA só a ergue quando o dano que ela evita no tempo que dura passa o golpe que se perde.

**O caso mais nítido.** Oitavas 8 — mount × sacy, rodada 53, mount. Na tela: HP 249/7863, MP 78/786; o adversário com HP 814/7520, MP 48/786, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Couro Batido**: Couro Batido é legal e não está ativo (buffs visíveis: []).
- A IA fez **Soco de Placa** (justificativa registrada por ela): P(vitória) 0.540±0.119 com Soco de Placa; contra Golpe Poderoso 0.518, ataque básico 0.506, Couro Batido 0.129; dano esperado 294; custa 61 MP.
- Todas as opções avaliadas: Soco de Placa P 0,540, 61 MP; Golpe Poderoso P 0,518, 52 MP; ataque básico P 0,506; Couro Batido P 0,129, 70 MP.
- Modelo do adversário naquele momento: ofensa ×0,54, defesa ×1,05 sobre a priori; cartas reveladas: Escudo Protetor, Golpe Devastador, Golpe Duplo, Mira Calma.

**Um caso típico.** Fase de 64 29 — RazaH × mount, rodada 9, mount. Na tela: HP 4642/7863, MP 423/786; o adversário com HP 2572/5285, MP 426/537, efeitos nenhum; buffs próprios Disciplina de Forja.

- A `PoliticaCopa` faria **Couro Batido**: Couro Batido é legal e não está ativo (buffs visíveis: ['Disciplina de Forja']).
- A IA fez **Golpe Poderoso** (justificativa registrada por ela): P(vitória) 0.208±0.075 com Golpe Poderoso; contra Soco de Placa 0.206, ataque básico 0.196, Couro Batido 0.190; dano esperado 333; custa 52 MP.
- Todas as opções avaliadas: Golpe Poderoso P 0,208, 52 MP; Soco de Placa P 0,206, 61 MP; ataque básico P 0,196; Couro Batido P 0,190, 70 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,26 sobre a priori; cartas reveladas: Mão Dupla.

### A política: dano → a IA: básico

- Leitura: a política gasta a primeira carta de dano legal; a IA guarda o MP quando ele compra mais depois — uma cura que vai ser necessária, a carta condicional que vai valer mais, ou simplesmente quando o básico já resolve.

**O caso mais nítido.** Fase de 64 7 — Dilera × JonVlogs, rodada 98, Dilera. Na tela: HP 497/5077, MP 55/868; o adversário com HP 789/6314, MP 22/708, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Investida**: primeira skill de dano legal do deck: Investida.
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.150±0.019 com ataque básico; contra Investida 0.017; dano esperado 73.
- Todas as opções avaliadas: ataque básico P 0,149; Investida P 0,017, 47 MP.
- Modelo do adversário naquele momento: ofensa ×0,77, defesa ×0,80 sobre a priori; cartas reveladas: Guarda Alta, Investida.

**Um caso típico.** Oitavas 3 — Tenz × DavyJones, rodada 42, DavyJones. Na tela: HP 867/5333, MP 57/829; o adversário com HP 1117/5519, MP 85/1050, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Golpe Poderoso**: primeira skill de dano legal do deck: Golpe Poderoso.
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.039±0.016 com ataque básico; contra Golpe Poderoso 0.036; dano esperado 103.
- Todas as opções avaliadas: ataque básico P 0,039; Golpe Poderoso P 0,036, 47 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,82 sobre a priori; cartas reveladas: nenhuma.

### A política: status → a IA: dano

- Leitura: a política aplica todo status que o alvo não carrega; a IA mede o que o status muda nas próximas rodadas contra o dano que se perde nesta.

**O caso mais nítido.** Fase de 32 12 — casimito × XANDAOOGOD, rodada 21, casimito. Na tela: HP 994/7113, MP 289/726; o adversário com HP 1032/5684, MP 123/1037, efeitos nenhum; buffs próprios Disciplina de Forja.

- A `PoliticaCopa` faria **Provocação**: Provocação aplica weakened, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **Esmagar** (justificativa registrada por ela): P(vitória) 0.700±0.110 com Esmagar; contra ataque básico 0.150, Provocação 0.100; dano esperado 984; chance de derrubar já 24%; custa 161 MP.
- Todas as opções avaliadas: Esmagar P 0,700, 161 MP, chance de derrubar 24,1%; ataque básico P 0,150; Provocação P 0,100, 71 MP.
- Modelo do adversário naquele momento: ofensa ×0,76, defesa ×1,10 sobre a priori; cartas reveladas: Esmagar, Golpe Duplo, Mira Calma, Veterania.

**Um caso típico.** Quartas 2 — Tenz × aXtLOL, rodada 2, Tenz. Na tela: HP 4980/5519, MP 998/1050; o adversário com HP 5033/5454, MP 682/766, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Gancho e Corda**: Gancho e Corda aplica stun, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **Soco de Placa** (justificativa registrada por ela): P(vitória) 0.467±0.005 com Soco de Placa; contra ataque básico 0.466, Tomar Fôlego 0.459, Gancho e Corda 0.446; dano esperado 312; custa 61 MP.
- Todas as opções avaliadas: Soco de Placa P 0,467, 61 MP; ataque básico P 0,466; Tomar Fôlego P 0,459, 93 MP; Gancho e Corda P 0,446, 117 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,11 sobre a priori; cartas reveladas: Ferro Contra Ferro.

### A política: status → a IA: básico

- Leitura: a política aplica todo status que o alvo não carrega; a IA só o aplica quando o que ele muda nas próximas rodadas passa o golpe desta e o MP.

**O caso mais nítido.** Fase de 64 28 — Felps × Hayashii, rodada 8, Felps. Na tela: HP 1370/4098, MP 402/618; o adversário com HP 2265/4939, MP 812/898, efeitos poison, vulnerable, vulnerable; buffs próprios nenhum.

- A `PoliticaCopa` faria **Travar o Pulso**: Travar o Pulso aplica weakened, que o adversário não carrega (efeitos visíveis: ['poison', 'vulnerable', 'vulnerable']).
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.628±0.138 com ataque básico; contra Quebra-Guarda 0.471, Travar o Pulso 0.431; dano esperado 264.
- Todas as opções avaliadas: ataque básico P 0,628; Quebra-Guarda P 0,471, 50 MP; Travar o Pulso P 0,431, 50 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,14 sobre a priori; cartas reveladas: nenhuma.

**Um caso típico.** Fase de 64 24 — Forever × XANDAOOGOD, rodada 5, Forever. Na tela: HP 4901/5225, MP 727/842; o adversário com HP 5284/5684, MP 882/1037, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Grito Curto**: Grito Curto aplica fear, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.414±0.015 com ataque básico; contra Grito Curto 0.391; dano esperado 146.
- Todas as opções avaliadas: ataque básico P 0,414; Grito Curto P 0,391, 57 MP.
- Modelo do adversário naquele momento: ofensa ×0,94, defesa ×0,81 sobre a priori; cartas reveladas: Golpe Duplo, Veterania.

### A política: dano → a IA: dano

- Leitura: a política pega a primeira carta de dano na ordem do deck; a IA pega a de maior valor esperado no estado — bônus situacional, chance de derrubar, recarga.

**O caso mais nítido.** Fase de 64 21 — PlayHard × xandfps, rodada 8, xandfps. Na tela: HP 2741/4259, MP 509/856; o adversário com HP 3196/4339, MP 737/946, efeitos nenhum; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **Mão Dupla**: primeira skill de dano legal do deck: Mão Dupla.
- A IA fez **Mira Calma** (justificativa registrada por ela): P(vitória) 0.388±0.071 com Mira Calma; contra ataque básico 0.264, Mão Dupla 0.228; dano esperado 531; custa 92 MP.
- Todas as opções avaliadas: Mira Calma P 0,388, 92 MP; ataque básico P 0,264; Mão Dupla P 0,228, 76 MP.
- Modelo do adversário naquele momento: ofensa ×1,03, defesa ×1,08 sobre a priori; cartas reveladas: Areia no Chão, Golpe Duplo, Quebra-Guarda.

**Um caso típico.** Fase de 32 10 — NOBRU × Neskwga, rodada 9, NOBRU. Na tela: HP 3816/5469, MP 398/1024; o adversário com HP 5724/6216, MP 340/668, efeitos nenhum; buffs próprios Imortal, Postura de Muro.

- A `PoliticaCopa` faria **Cutelada**: primeira skill de dano legal do deck: Cutelada.
- A IA fez **Investida** (justificativa registrada por ela): P(vitória) 0.166±0.007 com Investida; contra ataque básico 0.163, Cutelada 0.161; dano esperado 234; custa 59 MP.
- Todas as opções avaliadas: Investida P 0,166, 59 MP; ataque básico P 0,163; Cutelada P 0,162, 85 MP.
- Modelo do adversário naquele momento: ofensa ×0,91, defesa ×0,80 sobre a priori; cartas reveladas: Escudo Protetor, Golpe Duplo, Golpe Poderoso, Mira Calma.

### A política: redução de dano → a IA: básico

- Leitura: a política ergue toda redução de dano inativa; a IA guarda o MP quando o dano que a redução evitaria no tempo que dura é pequeno.

**O caso mais nítido.** Fase de 64 7 — Dilera × JonVlogs, rodada 104, Dilera. Na tela: HP 408/5077, MP 60/868; o adversário com HP 300/6314, MP 48/708, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Couraça Improvisada**: Couraça Improvisada é legal e não está ativo (buffs visíveis: []).
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.393±0.242 com ataque básico; contra Golpe Poderoso 0.104, Investida 0.071, Couraça Improvisada 0.023; dano esperado 73.
- Todas as opções avaliadas: ataque básico P 0,393; Golpe Poderoso P 0,104, 42 MP; Investida P 0,071, 47 MP; Couraça Improvisada P 0,023, 56 MP.
- Modelo do adversário naquele momento: ofensa ×0,75, defesa ×0,79 sobre a priori; cartas reveladas: Guarda Alta, Investida.

**Um caso típico.** Oitavas 8 — mount × sacy, rodada 21, mount. Na tela: HP 4651/7863, MP 435/786; o adversário com HP 5054/7520, MP 144/786, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Couro Batido**: Couro Batido é legal e não está ativo (buffs visíveis: []).
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.798±0.008 com ataque básico; contra Golpe Poderoso 0.798, Soco de Placa 0.798, Couro Batido 0.782; dano esperado 140.
- Todas as opções avaliadas: ataque básico P 0,798; Golpe Poderoso P 0,798, 52 MP; Soco de Placa P 0,798, 61 MP; Couro Batido P 0,782, 70 MP; Disciplina de Forja P 0,779, 105 MP.
- Modelo do adversário naquele momento: ofensa ×0,59, defesa ×1,06 sobre a priori; cartas reveladas: Escudo Protetor, Golpe Devastador, Golpe Duplo.

### A política: dano → a IA: cura

- Leitura: a IA curou antes da metade do HP, quando o próximo golpe do outro já derrubaria e ela age primeiro.

**O caso mais nítido.** Fase de 64 22 — Gaules × tteuw, rodada 10, tteuw. Na tela: HP 2825/4842, MP 244/521; o adversário com HP 2486/5209, MP 219/695, efeitos nenhum; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **Golpe Poderoso**: primeira skill de dano legal do deck: Golpe Poderoso.
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.356±0.065 com Tomar Fôlego; contra Golpe Poderoso 0.305, Escudo Protetor 0.300, ataque básico 0.297; custa 59 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,356, 59 MP; Golpe Poderoso P 0,305, 33 MP; Escudo Protetor P 0,300, 69 MP; ataque básico P 0,297.
- Modelo do adversário naquele momento: ofensa ×0,97, defesa ×1,33 sobre a priori; cartas reveladas: Fúria, Mão Dupla, Quebra-Guarda.

**Um caso típico.** Fase de 64 19 — calango × NOBRU, rodada 12, calango. Na tela: HP 3978/5367, MP 646/829; o adversário com HP 4601/5469, MP 714/1024, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Golpe Poderoso**: primeira skill de dano legal do deck: Golpe Poderoso.
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.111±0.004 com Tomar Fôlego; contra Golpe Poderoso 0.106, ataque básico 0.104; custa 83 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,112, 83 MP; Golpe Poderoso P 0,106, 47 MP; ataque básico P 0,104.
- Modelo do adversário naquele momento: ofensa ×0,80, defesa ×0,88 sobre a priori; cartas reveladas: Cutelada, Investida.

### A política: buff → a IA: status

- Leitura: a política prefere o buff ao status pela ordem das regras; a IA comparou os dois no motor.

**O caso mais nítido.** Semifinal 1 — Smzinho × Tenz, rodada 16, Smzinho. Na tela: HP 2728/5701, MP 125/958; o adversário com HP 1892/5519, MP 602/1050, efeitos vulnerable; buffs próprios nenhum.

- A `PoliticaCopa` faria **Veterania**: Veterania é legal e não está ativo (buffs visíveis: []).
- A IA fez **Estocada Seca** (justificativa registrada por ela): P(vitória) 0.771±0.078 com Estocada Seca; contra Cutelada 0.699, ataque básico 0.591, Veterania 0.526; custa 70 MP.
- Todas as opções avaliadas: Estocada Seca P 0,770, 70 MP; Cutelada P 0,699, 85 MP; ataque básico P 0,591; Veterania P 0,526, 111 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,95 sobre a priori; cartas reveladas: Berro de Ferro, Golpe Poderoso, Quebra-Ossos.

**Um caso típico.** Fase de 32 11 — PlayHard × Gaules, rodada 1, Gaules. Na tela: HP 5209/5209, MP 695/695; o adversário com HP 4339/4339, MP 946/946, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fúria**: Fúria é legal e não está ativo (buffs visíveis: []).
- A IA fez **Estocada Seca** (justificativa registrada por ela): P(vitória) 0.577±0.015 com Estocada Seca; contra ataque básico 0.569, Mão Dupla 0.557, Fúria 0.557; custa 62 MP.
- Todas as opções avaliadas: Estocada Seca P 0,577, 62 MP; ataque básico P 0,569; Mão Dupla P 0,557, 85 MP; Fúria P 0,557, 171 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,00 sobre a priori; cartas reveladas: nenhuma.

### A política: cura → a IA: dano

- Leitura: a política cura com HP até a metade; a IA corre quando o golpe dela chega antes do dele.

**O caso mais nítido.** Fase de 32 6 — alanzoka × DavyJones, rodada 40, DavyJones. Na tela: HP 2660/5333, MP 103/829; o adversário com HP 2434/7387, MP 42/845, efeitos bleed; buffs próprios nenhum.

- A `PoliticaCopa` faria **Respirar Fundo**: HP 2660/5333 (49.9%) ≤ 50% e há cura legal: Respirar Fundo.
- A IA fez **Mira Calma** (justificativa registrada por ela): P(vitória) 0.855±0.042 com Mira Calma; contra ataque básico 0.843, Respirar Fundo 0.632, Golpe Poderoso 0.631; dano esperado 798; custa 103 MP.
- Todas as opções avaliadas: Mira Calma P 0,855, 103 MP; ataque básico P 0,843; Respirar Fundo P 0,632, 73 MP; Golpe Poderoso P 0,631, 47 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,19 sobre a priori; cartas reveladas: nenhuma.

**Um caso típico.** Fase de 32 13 — Patriota × dona, rodada 27, dona. Na tela: HP 3171/7574, MP 415/746; o adversário com HP 484/4779, MP 756/855, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Respirar Fundo**: HP 3171/7574 (41.9%) ≤ 50% e há cura legal: Respirar Fundo.
- A IA fez **Cutelada** (justificativa registrada por ela): P(vitória) 0.945±0.008 com Cutelada; contra Investida 0.939, Respirar Fundo 0.936, ataque básico 0.918; dano esperado 384; chance de derrubar já 13%; custa 85 MP.
- Todas as opções avaliadas: Cutelada P 0,945, 85 MP, chance de derrubar 12,9%; Investida P 0,939, 59 MP, chance de derrubar 12,9%; Respirar Fundo P 0,936, 82 MP; ataque básico P 0,918; Grito de Guerra P 0,909, 100 MP.
- Modelo do adversário naquele momento: ofensa ×0,85, defesa ×1,22 sobre a priori; cartas reveladas: Peso do Machado, Pisada de Ferro, Provocação.

### A política: dano → a IA: buff

- Leitura: a política gasta a carta de dano; a IA viu o buff render mais nas rodadas seguintes do que o golpe agora.

**O caso mais nítido.** Fase de 64 21 — PlayHard × xandfps, rodada 10, xandfps. Na tela: HP 2261/4259, MP 407/856; o adversário com HP 2391/4339, MP 705/946, efeitos nenhum; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **Peso do Machado**: primeira skill de dano legal do deck: Peso do Machado.
- A IA fez **Escudo Protetor** (justificativa registrada por ela): P(vitória) 0.537±0.080 com Escudo Protetor; contra ataque básico 0.397, Peso do Machado 0.389; custa 87 MP.
- Todas as opções avaliadas: Escudo Protetor P 0,537, 87 MP; ataque básico P 0,397; Peso do Machado P 0,389, 58 MP.
- Modelo do adversário naquele momento: ofensa ×0,88, defesa ×1,10 sobre a priori; cartas reveladas: Areia no Chão, Golpe Duplo, Quebra-Guarda.

**Um caso típico.** Fase de 64 8 — Coringa × LuquEt4, rodada 6, LuquEt4. Na tela: HP 5875/7257, MP 346/773; o adversário com HP 2989/3226, MP 253/568, efeitos frailty; buffs próprios Grito de Guerra.

- A `PoliticaCopa` faria **Cutelada**: primeira skill de dano legal do deck: Cutelada.
- A IA fez **Grito de Guerra** (justificativa registrada por ela): P(vitória) 0.864±0.004 com Grito de Guerra; contra ataque básico 0.851, Cutelada 0.843; custa 100 MP.
- Todas as opções avaliadas: Grito de Guerra P 0,864, 100 MP; ataque básico P 0,851; Cutelada P 0,843, 85 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,85 sobre a priori; cartas reveladas: Escudo Protetor.

### A política: status → a IA: buff

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 31 — aspaszin × sacy, rodada 10, sacy. Na tela: HP 6943/7520, MP 199/786; o adversário com HP 3470/4874, MP 605/882, efeitos nenhum; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **Silêncio do Veterano**: Silêncio do Veterano aplica fear, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **Escudo Protetor** (justificativa registrada por ela): P(vitória) 0.739±0.016 com Escudo Protetor; contra ataque básico 0.726, Golpe Devastador 0.706, Silêncio do Veterano 0.674; custa 109 MP.
- Todas as opções avaliadas: Escudo Protetor P 0,739, 109 MP; ataque básico P 0,726; Golpe Devastador P 0,706, 120 MP; Silêncio do Veterano P 0,674, 135 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,97 sobre a priori; cartas reveladas: Berro de Ferro, Curativo de Campo, Encarar.

**Um caso típico.** Oitavas 8 — mount × sacy, rodada 4, sacy. Na tela: HP 7273/7520, MP 613/786; o adversário com HP 7188/7863, MP 711/786, efeitos nenhum; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **Silêncio do Veterano**: Silêncio do Veterano aplica fear, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **Escudo Protetor** (justificativa registrada por ela): P(vitória) 0.210±0.004 com Escudo Protetor; contra Golpe Devastador 0.200, ataque básico 0.199, Silêncio do Veterano 0.196; custa 109 MP.
- Todas as opções avaliadas: Escudo Protetor P 0,210, 109 MP; Golpe Devastador P 0,200, 120 MP; ataque básico P 0,199; Silêncio do Veterano P 0,196, 135 MP.
- Modelo do adversário naquele momento: ofensa ×0,95, defesa ×0,91 sobre a priori; cartas reveladas: Soco de Placa.

### A política: status → a IA: cura

- Leitura: a IA curou antes de aplicar status: sobreviver valia mais.

**O caso mais nítido.** Oitavas 3 — Tenz × DavyJones, rodada 17, Tenz. Na tela: HP 2985/5519, MP 610/1050; o adversário com HP 3466/5333, MP 330/829, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Gancho e Corda**: Gancho e Corda aplica stun, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.647±0.037 com Tomar Fôlego; contra Soco de Placa 0.630, Golpe Poderoso 0.630, ataque básico 0.626; custa 93 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,647, 93 MP; Soco de Placa P 0,630, 61 MP; Golpe Poderoso P 0,630, 52 MP; ataque básico P 0,626; Gancho e Corda P 0,591, 117 MP.
- Modelo do adversário naquele momento: ofensa ×0,74, defesa ×0,93 sobre a priori; cartas reveladas: Golpe Duplo, Golpe Poderoso, Mira Calma, Paciência do Coveiro, Respirar Fundo.

**Um caso típico.** Final — Tenz × fer, rodada 13, Tenz. Na tela: HP 3493/5519, MP 661/1050; o adversário com HP 3983/5977, MP 780/1103, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Gancho e Corda**: Gancho e Corda aplica stun, que o adversário não carrega (efeitos visíveis: []).
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.181±0.008 com Tomar Fôlego; contra Soco de Placa 0.177, ataque básico 0.172, Gancho e Corda 0.166; custa 93 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,181, 93 MP; Soco de Placa P 0,176, 61 MP; ataque básico P 0,172; Gancho e Corda P 0,166, 117 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,97 sobre a priori; cartas reveladas: Golpe Poderoso.

### A política: redução de dano → a IA: cura

- Leitura: a IA preferiu devolver HP a reduzir o dano que viria.

**O caso mais nítido.** Semifinal 2 — Neskwga × fer, rodada 3, fer. Na tela: HP 5009/5977, MP 1073/1103; o adversário com HP 5856/6216, MP 485/668, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Juramento da Muralha**: Juramento da Muralha é legal e não está ativo (buffs visíveis: []).
- A IA fez **Respirar Fundo** (justificativa registrada por ela): P(vitória) 0.463±0.023 com Respirar Fundo; contra Juramento da Muralha 0.426, ataque básico 0.421, Soco de Placa 0.421; custa 82 MP.
- Todas as opções avaliadas: Respirar Fundo P 0,463, 82 MP; Juramento da Muralha P 0,426, 152 MP; ataque básico P 0,421; Soco de Placa P 0,421, 61 MP; Golpe Poderoso P 0,419, 52 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,91 sobre a priori; cartas reveladas: Escudo Protetor, Mira Calma.

**Um caso típico.** Fase de 64 7 — Dilera × JonVlogs, rodada 19, Dilera. Na tela: HP 3508/5077, MP 462/868; o adversário com HP 4840/6314, MP 318/708, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Couraça Improvisada**: Couraça Improvisada é legal e não está ativo (buffs visíveis: []).
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.127±0.005 com Tomar Fôlego; contra Investida 0.113, Couraça Improvisada 0.111, ataque básico 0.109; custa 74 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,127, 74 MP; Investida P 0,113, 47 MP; Couraça Improvisada P 0,111, 56 MP; ataque básico P 0,109.
- Modelo do adversário naquele momento: ofensa ×0,84, defesa ×0,89 sobre a priori; cartas reveladas: Investida.

### A política: cura → a IA: básico

- Leitura: a política cura com HP até a metade; a IA não curou porque o dano do outro até o fim previsto não justificava a cura agora.

**O caso mais nítido.** Fase de 32 6 — alanzoka × DavyJones, rodada 39, DavyJones. Na tela: HP 2629/5333, MP 83/829; o adversário com HP 2068/7387, MP 108/845, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Respirar Fundo**: HP 2629/5333 (49.3%) ≤ 50% e há cura legal: Respirar Fundo.
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.660±0.054 com ataque básico; contra Golpe Poderoso 0.534, Respirar Fundo 0.521; dano esperado 183.
- Todas as opções avaliadas: ataque básico P 0,660; Golpe Poderoso P 0,534, 47 MP; Respirar Fundo P 0,521, 73 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,23 sobre a priori; cartas reveladas: nenhuma.

**Um caso típico.** Oitavas 3 — Tenz × DavyJones, rodada 25, DavyJones. Na tela: HP 2333/5333, MP 86/829; o adversário com HP 2062/5519, MP 314/1050, efeitos poison; buffs próprios nenhum.

- A `PoliticaCopa` faria **Respirar Fundo**: HP 2333/5333 (43.7%) ≤ 50% e há cura legal: Respirar Fundo.
- A IA fez **ataque básico** (justificativa registrada por ela): P(vitória) 0.057±0.003 com ataque básico; contra Respirar Fundo 0.057, Golpe Poderoso 0.051; dano esperado 71.
- Todas as opções avaliadas: ataque básico P 0,057; Respirar Fundo P 0,057, 73 MP; Golpe Poderoso P 0,051, 47 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,71 sobre a priori; cartas reveladas: nenhuma.

### A política: buff → a IA: cura

- Leitura: a IA curou antes de buffar: sobreviver valia mais.

**O caso mais nítido.** Fase de 64 31 — aspaszin × sacy, rodada 21, aspaszin. Na tela: HP 2588/4874, MP 316/882; o adversário com HP 4717/7520, MP 144/786, efeitos vulnerable; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fôlego de Marcha**: Fôlego de Marcha é legal e não está ativo (buffs visíveis: []).
- A IA fez **Respirar Fundo** (justificativa registrada por ela): P(vitória) 0.335±0.012 com Respirar Fundo; contra Quebra-Guarda 0.318, Golpe Poderoso 0.314, ataque básico 0.312; custa 73 MP.
- Todas as opções avaliadas: Respirar Fundo P 0,335, 73 MP; Quebra-Guarda P 0,318, 63 MP; Golpe Poderoso P 0,314, 47 MP; ataque básico P 0,311; Fôlego de Marcha P 0,293, 73 MP.
- Modelo do adversário naquele momento: ofensa ×0,70, defesa ×0,86 sobre a priori; cartas reveladas: Escudo Protetor, Golpe Duplo.

**Um caso típico.** Fase de 64 31 — aspaszin × sacy, rodada 1, aspaszin. Na tela: HP 4874/4874, MP 882/882; o adversário com HP 7520/7520, MP 786/786, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fôlego de Marcha**: Fôlego de Marcha é legal e não está ativo (buffs visíveis: []).
- A IA fez **Respirar Fundo** (justificativa registrada por ela): P(vitória) 0.397±0.004 com Respirar Fundo; contra Golpe Poderoso 0.395, ataque básico 0.395, Quebra-Guarda 0.394; custa 73 MP.
- Todas as opções avaliadas: Respirar Fundo P 0,397, 73 MP; Golpe Poderoso P 0,395, 47 MP; ataque básico P 0,395; Quebra-Guarda P 0,394, 63 MP; Fôlego de Marcha P 0,393, 73 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,00 sobre a priori; cartas reveladas: nenhuma.

### A política: básico → a IA: buff

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 32 2 — gafallen × loud_thurzin, rodada 10, gafallen. Na tela: HP 3303/3973, MP 432/763; o adversário com HP 2265/5110, MP 794/963, efeitos vulnerable; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **ataque básico**: nenhuma skill útil e legal (fora: ['Tomar Fôlego', 'Mira Calma', 'Quebra-Guarda']); ataque básico.
- A IA fez **Escudo Protetor** (justificativa registrada por ela): P(vitória) 0.537±0.045 com Escudo Protetor; contra ataque básico 0.468; custa 77 MP.
- Todas as opções avaliadas: Escudo Protetor P 0,537, 77 MP; ataque básico P 0,468.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,03 sobre a priori; cartas reveladas: Carga do Condenado, Golpe Devastador.

**Um caso típico.** Fase de 64 20 — coldzin × Neskwga, rodada 4, Neskwga. Na tela: HP 5674/6216, MP 455/668; o adversário com HP 6372/8119, MP 920/961, efeitos nenhum; buffs próprios Escudo Protetor.

- A `PoliticaCopa` faria **ataque básico**: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Mira Calma', 'Baluarte']); ataque básico.
- A IA fez **Escudo Protetor** (justificativa registrada por ela): P(vitória) 0.595±0.019 com Escudo Protetor; contra ataque básico 0.568; custa 97 MP.
- Todas as opções avaliadas: Escudo Protetor P 0,595, 97 MP; ataque básico P 0,568.
- Modelo do adversário naquele momento: ofensa ×0,85, defesa ×1,42 sobre a priori; cartas reveladas: Cutelada.

### A política: buff → a IA: redução de dano

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 6 — yayahuz × k13tv, rodada 3, k13tv. Na tela: HP 4522/5439, MP 658/806; o adversário com HP 5160/6296, MP 537/674, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fio no Rebite**: Fio no Rebite é legal e não está ativo (buffs visíveis: []).
- A IA fez **Guarda Cruzada** (justificativa registrada por ela): P(vitória) 0.358±0.022 com Guarda Cruzada; contra Golpe Poderoso 0.334, ataque básico 0.331, Fio no Rebite 0.320; custa 111 MP.
- Todas as opções avaliadas: Guarda Cruzada P 0,358, 111 MP; Golpe Poderoso P 0,334, 52 MP; ataque básico P 0,331; Fio no Rebite P 0,320, 82 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,16 sobre a priori; cartas reveladas: Mira Calma.

**Um caso típico.** Fase de 64 6 — yayahuz × k13tv, rodada 27, k13tv. Na tela: HP 800/5439, MP 145/806; o adversário com HP 2440/6296, MP 47/674, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fio no Rebite**: Fio no Rebite é legal e não está ativo (buffs visíveis: []).
- A IA fez **Guarda Cruzada** (justificativa registrada por ela): P(vitória) 0.016±0.012 com Guarda Cruzada; contra Mira Calma 0.012, Golpe Poderoso 0.011, ataque básico 0.011; custa 111 MP.
- Todas as opções avaliadas: Guarda Cruzada P 0,016, 111 MP; Mira Calma P 0,012, 116 MP; Golpe Poderoso P 0,011, 52 MP; ataque básico P 0,011; Fio no Rebite P 0,008, 82 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,05 sobre a priori; cartas reveladas: Golpe Devastador, Mira Calma.

### A política: básico → a IA: cura

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 6 — yayahuz × k13tv, rodada 3, yayahuz. Na tela: HP 5160/6296, MP 537/674; o adversário com HP 4522/5439, MP 658/806, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **ataque básico**: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Mira Calma', 'Sede de Batalha']); ataque básico.
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.385±0.006 com Tomar Fôlego; contra ataque básico 0.377; custa 83 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,385, 83 MP; ataque básico P 0,377.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,22 sobre a priori; cartas reveladas: Golpe Duplo, Golpe Poderoso.

**Um caso típico.** Fase de 32 3 — fnxLNTC × yayahuz, rodada 13, yayahuz. Na tela: HP 5695/6296, MP 338/674; o adversário com HP 4079/5355, MP 598/951, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **ataque básico**: nenhuma skill útil e legal (fora: ['Golpe Poderoso', 'Mira Calma', 'Sede de Batalha']); ataque básico.
- A IA fez **Tomar Fôlego** (justificativa registrada por ela): P(vitória) 0.200±0.006 com Tomar Fôlego; contra ataque básico 0.195; custa 83 MP.
- Todas as opções avaliadas: Tomar Fôlego P 0,200, 83 MP; ataque básico P 0,196.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×0,78 sobre a priori; cartas reveladas: Investida, Investida de Aríete.

### A política: redução de dano → a IA: buff

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 29 — RazaH × mount, rodada 8, mount. Na tela: HP 5491/7863, MP 509/786; o adversário com HP 2563/5285, MP 484/537, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Couro Batido**: Couro Batido é legal e não está ativo (buffs visíveis: []).
- A IA fez **Disciplina de Forja** (justificativa registrada por ela): P(vitória) 0.650±0.061 com Disciplina de Forja; contra Soco de Placa 0.632, Couro Batido 0.632, ataque básico 0.621; custa 105 MP.
- Todas as opções avaliadas: Disciplina de Forja P 0,650, 105 MP; Soco de Placa P 0,632, 61 MP; Couro Batido P 0,632, 70 MP; ataque básico P 0,621.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,26 sobre a priori; cartas reveladas: Mão Dupla.

**Um caso típico.** Fase de 64 7 — Dilera × JonVlogs, rodada 28, JonVlogs. Na tela: HP 4794/6314, MP 97/708; o adversário com HP 3450/5077, MP 276/868, efeitos nenhum; buffs próprios Guarda Alta.

- A `PoliticaCopa` faria **Couraça Improvisada**: Couraça Improvisada é legal e não está ativo (buffs visíveis: ['Guarda Alta']).
- A IA fez **Guarda Alta** (justificativa registrada por ela): P(vitória) 0.195±0.006 com Guarda Alta; contra ataque básico 0.194, Investida 0.192, Couraça Improvisada 0.189; custa 57 MP.
- Todas as opções avaliadas: Guarda Alta P 0,195, 57 MP; ataque básico P 0,194; Investida P 0,192, 53 MP; Couraça Improvisada P 0,189, 62 MP.
- Modelo do adversário naquele momento: ofensa ×0,84, defesa ×0,90 sobre a priori; cartas reveladas: Couraça Improvisada, Ferro Contra Ferro, Investida, Marca do Açougueiro, Tomar Fôlego.

### A política: buff → a IA: buff

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 13 — SkipNhO × Tealzlol, rodada 2, Tealzlol. Na tela: HP 4162/4334, MP 437/510; o adversário com HP 6405/7167, MP 714/766, efeitos vulnerable; buffs próprios nenhum.

- A `PoliticaCopa` faria **Fôlego de Marcha**: Fôlego de Marcha é legal e não está ativo (buffs visíveis: []).
- A IA fez **Ritmo de Duelo** (justificativa registrada por ela): P(vitória) 0.308±0.008 com Ritmo de Duelo; contra Golpe Poderoso 0.302, ataque básico 0.301, Fôlego de Marcha 0.295; custa 67 MP.
- Todas as opções avaliadas: Ritmo de Duelo P 0,308, 67 MP; Golpe Poderoso P 0,302, 33 MP; ataque básico P 0,301; Fôlego de Marcha P 0,295, 52 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,11 sobre a priori; cartas reveladas: nenhuma.

### A política: cura → a IA: buff

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 30 — jukes × gabepeixe, rodada 11, jukes. Na tela: HP 2524/5515, MP 574/841; o adversário com HP 1806/4274, MP 338/712, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Respirar Fundo**: HP 2524/5515 (45.8%) ≤ 50% e há cura legal: Respirar Fundo.
- A IA fez **Leitura de Terreno** (justificativa registrada por ela): P(vitória) 0.455±0.069 com Leitura de Terreno; contra Mira Calma 0.392, Respirar Fundo 0.373, Golpe Poderoso 0.354; custa 99 MP.
- Todas as opções avaliadas: Leitura de Terreno P 0,455, 99 MP; Mira Calma P 0,393, 103 MP; Respirar Fundo P 0,373, 73 MP; Golpe Poderoso P 0,354, 47 MP; ataque básico P 0,319.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,00 sobre a priori; cartas reveladas: Fúria.

### A política: dano → a IA: status

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 3 — gafallen × blackoutz, rodada 8, blackoutz. Na tela: HP 541/3915, MP 243/517; o adversário com HP 1582/3973, MP 579/763, efeitos bleed, poison, vulnerable; buffs próprios nenhum.

- A `PoliticaCopa` faria **Golpe Duplo**: primeira skill de dano legal do deck: Golpe Duplo.
- A IA fez **Encarar** (justificativa registrada por ela): P(vitória) 0.400±0.118 com Encarar; contra Golpe Duplo 0.150, ataque básico 0.100; custa 54 MP.
- Todas as opções avaliadas: Encarar P 0,400, 54 MP; Golpe Duplo P 0,150, 82 MP; ataque básico P 0,100.
- Modelo do adversário naquele momento: ofensa ×0,73, defesa ×1,00 sobre a priori; cartas reveladas: Curativo de Campo, Escudo Protetor.

### A política: básico → a IA: status

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 22 — Gaules × tteuw, rodada 6, Gaules. Na tela: HP 4275/5209, MP 372/695; o adversário com HP 3533/4842, MP 355/521, efeitos bleed; buffs próprios Fúria.

- A `PoliticaCopa` faria **ataque básico**: nenhuma skill útil e legal (fora: ['Mão Dupla', 'Peso do Machado', 'Fúria']); ataque básico.
- A IA fez **Estocada Seca** (justificativa registrada por ela): P(vitória) 0.878±0.007 com Estocada Seca; contra ataque básico 0.862; custa 62 MP.
- Todas as opções avaliadas: Estocada Seca P 0,878, 62 MP; ataque básico P 0,862.
- Modelo do adversário naquele momento: ofensa ×0,80, defesa ×0,77 sobre a priori; cartas reveladas: Escudo Protetor.

### A política: status → a IA: status

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Fase de 64 28 — Felps × Hayashii, rodada 6, Felps. Na tela: HP 2283/4098, MP 472/618; o adversário com HP 3389/4939, MP 825/898, efeitos bleed, poison, vulnerable; buffs próprios nenhum.

- A `PoliticaCopa` faria **Travar o Pulso**: Travar o Pulso aplica weakened, que o adversário não carrega (efeitos visíveis: ['bleed', 'poison', 'vulnerable']).
- A IA fez **Sangue nos Olhos** (justificativa registrada por ela): P(vitória) 0.708±0.104 com Sangue nos Olhos; contra ataque básico 0.683, Marca do Açougueiro 0.581, Travar o Pulso 0.554; custa 50 MP.
- Todas as opções avaliadas: Sangue nos Olhos P 0,708, 50 MP; ataque básico P 0,683; Marca do Açougueiro P 0,581, 44 MP; Travar o Pulso P 0,554, 50 MP.
- Modelo do adversário naquele momento: ofensa ×1,00, defesa ×1,09 sobre a priori; cartas reveladas: nenhuma.

### A política: cura → a IA: status

- Leitura: a avaliação no motor preferiu a outra ação.

**O caso mais nítido.** Semifinal 1 — Smzinho × Tenz, rodada 16, Tenz. Na tela: HP 1892/5519, MP 602/1050; o adversário com HP 2728/5701, MP 125/958, efeitos nenhum; buffs próprios nenhum.

- A `PoliticaCopa` faria **Tomar Fôlego**: HP 1892/5519 (34.3%) ≤ 50% e há cura legal: Tomar Fôlego.
- A IA fez **Gancho e Corda** (justificativa registrada por ela): P(vitória) 0.514±0.085 com Gancho e Corda; contra Tomar Fôlego 0.463, Soco de Placa 0.449, ataque básico 0.408; custa 117 MP.
- Todas as opções avaliadas: Gancho e Corda P 0,514, 117 MP; Tomar Fôlego P 0,463, 93 MP; Soco de Placa P 0,449, 61 MP; ataque básico P 0,408.
- Modelo do adversário naquele momento: ofensa ×0,81, defesa ×1,08 sobre a priori; cartas reveladas: Cutelada, Estocada Seca, Golpe Duplo, Marca do Açougueiro, Mira Calma, Veterania.

## Os ataques básicos da IA

1505 básicos em 3564 ações (42,2%). Motivo de cada um:

| Motivo | Básicos |
|---|---|
| MP insuficiente | 483 (32,1%) |
| recarga | 76 (5,0%) |
| requisito de equipamento | 0 (0,0%) |
| havia skill legal (escolha do controlador) | 946 (62,9%) |

