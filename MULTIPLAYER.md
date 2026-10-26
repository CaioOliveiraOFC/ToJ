# Multiplayer humano × humano — como jogar em rede

Três computadores (ou dois, se um deles também roda o servidor): o servidor e um
cliente para cada jogador. As regras e garantias estão em
[`GAMEPLAY_CONTRACTS.md`](GAMEPLAY_CONTRACTS.md#multiplayer--compatibilidade-de-versão).

## 1. Todos os computadores

A mesma versão do jogo, do mesmo commit, e as dependências:

```bash
git clone https://github.com/CaioOliveiraOFC/ToJ.git && cd ToJ
git checkout phase/pvp-arena
pip install -r requirements.txt
python tools/multiplayer_manifesto.py verificar --sem-git
```

O último comando confirma que esta instalação é exatamente a versão declarada.
Cliente e servidor só jogam juntos com a identidade de versão idêntica; o
servidor recusa qualquer outra, avisando que a atualização é obrigatória.

## 2. O servidor (administrador)

Escolha uma pasta de dados fora do repositório, ou dentro de `saves/`, que o git
ignora. Ela guarda contas (senhas só em hash), a chave dos tokens e o registro de
gladiadores, todos com permissão 0600. Nunca a publique.

**Contas.** Uma por jogador; a senha é pedida sem eco, duas vezes:

```bash
python tools/toj_multiplayer.py conta criar --dados saves/servidor --usuario <usuario_1>
python tools/toj_multiplayer.py conta criar --dados saves/servidor --usuario <usuario_2>
```

**Gladiadores.** Hoje a única origem confiável são os snapshots publicados da
Copa Arena 03, conferidos pelo sha256 do índice (`reports/pvp/copa_03/`). Cada
gladiador tem um dono, e não há transferência:

```bash
python tools/toj_multiplayer.py gladiador importar --dados saves/servidor --dono <usuario_1> --id W23
python tools/toj_multiplayer.py gladiador importar --dados saves/servidor --dono <usuario_2> --id W64
python tools/toj_multiplayer.py gladiador listar --dados saves/servidor
```

**Certificado TLS.** Fora do loopback, o servidor só escuta com TLS. Numa rede de
teste, um certificado autoassinado basta. Troque o IP pelo do servidor:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -days 30 \
  -keyout chave.pem -out certificado.pem -subj "/CN=toj-servidor" \
  -addext "subjectAltName=IP:192.168.0.10"
```

Guarde `chave.pem` só no servidor. Os clientes recebem `certificado.pem`, que é
público.

**Subir:**

```bash
python tools/toj_multiplayer.py servidor --dados saves/servidor \
  --host 0.0.0.0 --porta 8765 --certificado certificado.pem --chave chave.pem
```

Libere a porta 8765/TCP no firewall do servidor. Para encerrar, use Ctrl+C.

## 3. Cada jogador

```bash
python tools/toj_multiplayer.py cliente --url wss://192.168.0.10:8765 \
  --usuario <seu_usuario> --autoridade certificado.pem
```

O cliente pede a senha, entra e mostra os gladiadores da sua conta. Depois:

1. Escolha o gladiador.
2. Um jogador escolhe **Criar uma sala** e passa o código ao outro; o outro
   escolhe **Entrar na sala de alguém** e digita o código.
3. Os dois veem a ficha pública do confronto.
4. A cada rodada, escolha a ação. O adversário não vê a sua escolha antes de os
   dois travarem; o servidor resolve a rodada e mostra o resultado aos dois.
5. No fim, os dois recebem o resultado.

Se a conexão cair no meio da partida, o cliente tenta voltar sozinho. A partida
espera no servidor.

## Problemas comuns

| mensagem | o que fazer |
|---|---|
| `Atualização do jogo obrigatória` | os dois lados precisam do mesmo commit; rode `git pull` e confira com `verificar` |
| `Esta instalação não confere com o manifesto` | há arquivo de jogo alterado localmente; desfaça a alteração ou atualize |
| erro de certificado no cliente | passe `--autoridade certificado.pem`; o IP do `subjectAltName` tem de ser o da URL |
| `Escutar em 0.0.0.0 sem TLS...` | forneça `--certificado` e `--chave`. `--sem-tls` existe só para desenvolvimento e manda senha e token sem criptografia |
| `Este gladiador não é da sua conta` | o administrador precisa importar um gladiador para a sua conta |
| `Esta conta já está conectada em outro lugar` | a mesma conta não joga duas sessões ao mesmo tempo |

Para testar tudo num computador só, use `--host 127.0.0.1` no servidor (o
loopback dispensa TLS) e `--url ws://127.0.0.1:8765` nos dois clientes.
