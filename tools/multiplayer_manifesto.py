"""Gate de publicação do multiplayer: o manifesto da versão confere com o código?

    python tools/multiplayer_manifesto.py verificar [--tag vX] [--sem-git] [--raiz DIR]
    python tools/multiplayer_manifesto.py gerar [--sem-git] [--raiz DIR]

`verificar` é o gate. Sai com código 1, listando cada problema, quando:

- não existe manifesto para a versão declarada em `src/multiplayer/versao.py`;
- os identificadores do manifesto não são os declarados;
- algum arquivo do escopo do gameplay mudou, apareceu ou sumiu sem que o
  manifesto fosse refeito (mudança de regra ou catálogo sem atualizar o
  manifesto);
- dois manifestos dão o mesmo identificador de regras, protocolo ou esquema a
  conteúdos diferentes;
- um manifesto publicado (com tag `v<versão>` no git) foi alterado ou apagado;
- com `--tag`, a tag não é `v` + a versão declarada.

`gerar` refaz o manifesto da versão declarada. Recusa quando essa versão já foi
publicada com outro conteúdo — manifesto publicado é imutável: declare uma
versão nova — ou quando o resultado quebraria a coerência entre versões.
"""

from __future__ import annotations

import argparse
import ast
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.multiplayer import manifesto as mf  # noqa: E402

PASTA_RELATIVA = "src/multiplayer/manifestos"
PREFIXO_DA_TAG = "v"
_CONSTANTES = {
    "VERSAO_DO_JOGO": "jogo",
    "VERSAO_DO_PROTOCOLO": "protocolo",
    "REGRAS_DE_COMBATE": "regras",
    "ESQUEMA_DO_GLADIADOR": "esquema_gladiador",
}


def declarados_de(raiz: Path) -> dict[str, object]:
    """Os quatro identificadores de `versao.py` da árvore em `raiz`, lidos sem importar."""
    arvore = ast.parse((raiz / "src/multiplayer/versao.py").read_text(encoding="utf-8"))
    achados: dict[str, object] = {}
    for no in arvore.body:
        if isinstance(no, ast.Assign) and len(no.targets) == 1:
            alvo = no.targets[0]
            if isinstance(alvo, ast.Name) and alvo.id in _CONSTANTES:
                achados[_CONSTANTES[alvo.id]] = ast.literal_eval(no.value)
    faltam = sorted(set(_CONSTANTES.values()) - set(achados))
    if faltam:
        raise SystemExit(f"versao.py não declara {faltam}.")
    return achados


def _git(raiz: Path, *argumentos: str) -> str | None:
    try:
        feito = subprocess.run(
            ["git", "-C", str(raiz), *argumentos], capture_output=True, text=True, check=False
        )
    except OSError:
        return None
    return feito.stdout if feito.returncode == 0 else None


def publicados_no_git(raiz: Path) -> dict[str, str] | None:
    """Versão → texto do manifesto no commit da tag `v<versão>`. `None` sem git."""
    tags = _git(raiz, "tag", "--list", f"{PREFIXO_DA_TAG}*")
    if tags is None:
        return None
    publicados = {}
    for tag in tags.split():
        jogo = tag[len(PREFIXO_DA_TAG) :]
        texto = _git(raiz, "show", f"{tag}:{PASTA_RELATIVA}/{jogo}.json")
        if texto is not None:
            publicados[jogo] = texto
    return publicados


def _textos_atuais(pasta: Path) -> dict[str, str]:
    return {p.stem: p.read_text(encoding="utf-8") for p in sorted(pasta.glob("*.json"))}


def verificar(raiz: Path = ROOT, *, tag: str | None = None, usar_git: bool = True) -> list[str]:
    """Todos os problemas que bloqueiam a publicação. Vazio = pode publicar."""
    pasta = raiz / PASTA_RELATIVA
    declarados = declarados_de(raiz)
    problemas: list[str] = []
    try:
        atual = mf.carregar(str(declarados["jogo"]), pasta)
    except mf.ManifestoInvalidoError as erro:
        problemas.append(str(erro))
        atual = None
    if atual is not None:
        problemas += mf.conferir_declaracao(atual, declarados)
        problemas += [
            f"Regra ou catálogo mudou sem atualizar o manifesto — {d}"
            for d in mf.divergencias(atual, raiz)
        ]
    try:
        problemas += mf.conferir_coerencia(mf.todos(pasta).values())
    except mf.ManifestoInvalidoError as erro:
        problemas.append(f"Manifesto ilegível na pasta: {erro}")
    if usar_git:
        publicados = publicados_no_git(raiz)
        if publicados is None:
            problemas.append(
                "git indisponível: a imutabilidade dos manifestos publicados não foi conferida."
            )
        else:
            problemas += mf.conferir_imutabilidade(publicados, _textos_atuais(pasta))
    if tag is not None and tag != f"{PREFIXO_DA_TAG}{declarados['jogo']}":
        problemas.append(
            f"A tag {tag!r} não é a versão declarada ({PREFIXO_DA_TAG}{declarados['jogo']})."
        )
    return problemas


def gerar(raiz: Path = ROOT, *, usar_git: bool = True) -> tuple[Path | None, list[str]]:
    """Escreve o manifesto da versão declarada. Devolve o caminho, ou os motivos da recusa."""
    pasta = raiz / PASTA_RELATIVA
    novo = mf.construir(declarados_de(raiz), raiz)
    if usar_git:
        publicados = publicados_no_git(raiz)
        if publicados is None:
            return None, ["git indisponível: não dá para saber se a versão já foi publicada."]
        if novo.jogo in publicados and publicados[novo.jogo] != novo.texto():
            return None, [
                f"A versão {novo.jogo} já foi publicada e o manifesto dela é imutável: "
                "declare uma versão nova em src/multiplayer/versao.py."
            ]
    outros = [m for jogo, m in mf.todos(pasta).items() if jogo != novo.jogo]
    problemas = mf.conferir_coerencia([*outros, novo])
    if problemas:
        return None, problemas
    pasta.mkdir(parents=True, exist_ok=True)
    caminho = mf.caminho_do_manifesto(novo.jogo, pasta)
    caminho.write_text(novo.texto(), encoding="utf-8")
    return caminho, []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome in ("verificar", "gerar"):
        p = sub.add_parser(nome)
        p.add_argument("--raiz", type=Path, default=ROOT)
        p.add_argument("--sem-git", action="store_true")
        if nome == "verificar":
            p.add_argument("--tag")
    args = parser.parse_args(argv)

    if args.comando == "gerar":
        caminho, problemas = gerar(args.raiz, usar_git=not args.sem_git)
        if problemas:
            print("Manifesto NÃO gerado:")
            print("\n".join(f"  - {p}" for p in problemas))
            return 1
        print(f"Manifesto escrito: {caminho.relative_to(args.raiz)}")
        return 0

    problemas = verificar(args.raiz, tag=args.tag, usar_git=not args.sem_git)
    if problemas:
        print(f"Publicação BLOQUEADA ({len(problemas)} problema(s)):")
        print("\n".join(f"  - {p}" for p in problemas))
        return 1
    jogo = declarados_de(args.raiz)["jogo"]
    print(f"Manifesto da versão {jogo} confere com o código.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
