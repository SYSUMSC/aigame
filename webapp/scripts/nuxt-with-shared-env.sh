#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
. "$SCRIPT_DIR/env-common.sh"

if [ -n "${SHARED_DOTENV_PATH:-}" ]; then
  exec pnpm exec nuxt "$@" --dotenv "$SHARED_DOTENV_PATH"
fi

exec pnpm exec nuxt "$@"
