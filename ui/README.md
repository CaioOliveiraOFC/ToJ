# ToJ 2D UI — Vertical Slice

Esta camada é uma apresentação web mobile-first do ToJ. A decisão para esta etapa é **vanilla HTML/CSS/JS**, não Phaser.

## Decisão de engine

Phaser seria útil para cenas complexas, spritesheets, câmera, input espacial e física. O ToJ atual não precisa disso: o combate é discreto, por turnos, sem movimento livre ou colisão física. Para o vertical slice, vanilla reduz dependências e mantém a UI fina sobre a lógica. A migração para Phaser deve acontecer apenas se exploração visual, mapas navegáveis, spritesheets complexos ou gerenciamento de cenas justificarem o custo.

## Escopo

- Mobile-first, largura máxima de 480px.
- Combate por turnos com as ações existentes: ataque, skill, poção e fuga.
- Animação idle → ataque → impacto + dano flutuante.
- Pixel art SVG crisp-edges para herói e cinco arquétipos visuais de ameaça.
- Reveal de multiplicador como pico visual.
- Sem novas classes, itens ou sistemas de gameplay.

## Relação com o core

O core Python continua sendo a fonte de verdade para as regras. A implementação web deste slice é uma casca demonstrativa; antes de produção, as fórmulas devem ser extraídas para um módulo compartilhado/API ou portadas automaticamente com testes de paridade. Não tratar este `game.js` como substituto definitivo de `src/mechanics/`.
