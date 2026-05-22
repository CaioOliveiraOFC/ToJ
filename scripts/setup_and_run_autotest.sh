#!/usr/bin/env bash
set -euo pipefail

# Uso:
#   bash scripts/setup_and_run_autotest.sh
#
# O script:
# 1) cria/atualiza .venv local
# 2) instala dependências para rodar o auto_test
# 3) executa o auto-test via menu principal (opção 6)

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERRO] Python não encontrado: $PYTHON_BIN"
  exit 1
fi

echo "[1/4] Criando ambiente virtual (.venv)..."
"$PYTHON_BIN" -m venv .venv

# shellcheck disable=SC1091
source .venv/bin/activate

echo "[2/4] Atualizando ferramentas base de instalação..."
python -m pip install --upgrade pip setuptools wheel

echo "[3/4] Instalando dependências do projeto + auto-test..."
# -e . instala o pacote local
# rich e pyfiglet são usados pela UI e necessários para executar o fluxo do jogo/auto-test
python -m pip install -e . rich pyfiglet

echo "[4/4] Executando auto-test (main.py -> opção 6)..."
# Sequência enviada:
# 6 = iniciar auto-test
# <enter> = continuar ao final do relatório
# 5 = sair do jogo ao voltar para o menu
printf '6\n\n5\n' | python main.py

echo
echo "[OK] Auto-test executado."
echo "Relatórios gerados em: $ROOT_DIR/reports"
