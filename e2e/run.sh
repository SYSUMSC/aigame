#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
E2E_DIR="$ROOT_DIR/e2e"

# 为每次执行生成独立 compose 项目标识，避免本地并行冲突。
export CI_RUN_ID="${CI_RUN_ID:-$(date +%s)}"
export COMPOSE_PROJECT_NAME="aigame-e2e-${CI_RUN_ID}"
export WEBAPP_HOST_PORT="${WEBAPP_HOST_PORT:-33000}"
export EVALUATEAPP_HOST_PORT="${EVALUATEAPP_HOST_PORT:-38000}"
export MONGO_HOST_PORT="${MONGO_HOST_PORT:-37017}"
export REDIS_HOST_PORT="${REDIS_HOST_PORT:-36379}"
export MINIO_API_HOST_PORT="${MINIO_API_HOST_PORT:-39000}"
export MINIO_CONSOLE_HOST_PORT="${MINIO_CONSOLE_HOST_PORT:-39001}"
export E2E_BASE_URL="${E2E_BASE_URL:-http://127.0.0.1:${WEBAPP_HOST_PORT}}"
export E2E_EVALUATE_BASE_URL="${E2E_EVALUATE_BASE_URL:-http://127.0.0.1:${EVALUATEAPP_HOST_PORT}}"

cleanup() {
  local exit_code="$?"

  # 失败时保留关键服务日志，便于排查问题。
  if [[ "$exit_code" -ne 0 ]]; then
    mkdir -p "$E2E_DIR/artifacts"
    docker compose \
      -f "$ROOT_DIR/docker-compose.deploy.yml" \
      -f "$E2E_DIR/docker-compose.e2e.override.yml" \
      logs webapp evaluateapp > "$E2E_DIR/artifacts/service-logs.txt" || true
  fi

  docker compose \
    -f "$ROOT_DIR/docker-compose.deploy.yml" \
    -f "$E2E_DIR/docker-compose.e2e.override.yml" \
    down -v --remove-orphans || true

  exit "$exit_code"
}

trap cleanup EXIT

# 拉起整套服务，确保 Playwright 面向接近真实部署的环境执行。
cd "$ROOT_DIR"
docker compose \
  -f "$ROOT_DIR/docker-compose.deploy.yml" \
  -f "$E2E_DIR/docker-compose.e2e.override.yml" \
  up -d --build

cd "$E2E_DIR"
if [[ ! -d node_modules ]]; then
  pnpm install
fi

pnpm exec playwright install chromium
pnpm test "$@"
