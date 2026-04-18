#!/usr/bin/env bash
# Configura o remoto origin (HTTPS ou SSH). Uso: ./scripts/setup-git-remote.sh <URL>
set -euo pipefail
REPO_URL="${1:-}"
if [[ -z "$REPO_URL" ]]; then
  echo "Uso: $0 <URL do repositório>"
  echo "Ex.: $0 https://github.com/mathalves23/agroadb-app.git"
  exit 1
fi
cd "$(dirname "$0")/.."
if git remote get-url origin &>/dev/null; then
  git remote set-url origin "$REPO_URL"
  echo "Remoto origin actualizado."
else
  git remote add origin "$REPO_URL"
  echo "Remoto origin adicionado."
fi
git remote -v
