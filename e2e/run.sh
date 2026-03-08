#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
E2E_DIR="$ROOT_DIR/e2e"
COMPOSE_ARGS=(
  -f "$ROOT_DIR/docker-compose.deploy.yml"
  -f "$E2E_DIR/docker-compose.e2e.override.yml"
)

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
export APP_DATA_DIR="${APP_DATA_DIR:-$E2E_DIR/.data/$CI_RUN_ID}"
export E2E_EVALUATE_BASE_URL="${E2E_EVALUATE_BASE_URL:-http://127.0.0.1:${EVALUATEAPP_HOST_PORT}}"

cleanup() {
  local exit_code="$?"

  # 失败时保留关键服务日志，便于排查问题。
  if [[ "$exit_code" -ne 0 ]]; then
    mkdir -p "$E2E_DIR/artifacts"
    docker compose "${COMPOSE_ARGS[@]}" \
      logs webapp evaluateapp mongo > "$E2E_DIR/artifacts/service-logs.txt" || true
  fi

  docker compose "${COMPOSE_ARGS[@]}" \
    down -v --remove-orphans || true

  exit "$exit_code"
}

# 等待 Mongo 可接受连接，避免副本集初始化时机过早。
wait_for_mongo() {
  local attempt

  for attempt in {1..60}; do
    if docker compose "${COMPOSE_ARGS[@]}" exec -T mongo \
      mongosh -u root -p password --authenticationDatabase admin --quiet --eval "db.adminCommand({ ping: 1 }).ok" \
      >/dev/null 2>&1; then
      return 0
    fi

    sleep 2
  done

  echo "❌ Mongo 在预期时间内未就绪" >&2
  return 1
}

# 初始化副本集；如果已经初始化则直接复用。
ensure_mongo_replica_set() {
  local rs_status

  rs_status=$(docker compose "${COMPOSE_ARGS[@]}" exec -T mongo \
    mongosh -u root -p password --authenticationDatabase admin --quiet --eval "try { rs.status().ok } catch (error) { print('NOT_INITIALIZED') }" 2>/dev/null || true)

  if [[ "$rs_status" == *"1"* ]]; then
    return 0
  fi

  docker compose "${COMPOSE_ARGS[@]}" exec -T mongo \
    mongosh -u root -p password --authenticationDatabase admin --quiet --eval 'try { rs.initiate({ _id: "rs0", members: [{ _id: 0, host: "mongo:27017" }] }) } catch (error) { if (!String(error).includes("already initialized")) throw error }'
}

# 等待副本集主节点出现，确保 Prisma 和测试都能稳定连上。
wait_for_mongo_primary() {
  local attempt

  for attempt in {1..60}; do
    if docker compose "${COMPOSE_ARGS[@]}" exec -T mongo \
      mongosh -u root -p password --authenticationDatabase admin --quiet --eval "db.hello().isWritablePrimary ? 1 : 0" \
      | grep -q '^1$'; then
      return 0
    fi

    sleep 2
  done

  echo "❌ Mongo 副本集主节点在预期时间内未就绪" >&2
  return 1
}

trap cleanup EXIT

# 拉起整套服务，确保 Playwright 面向接近真实部署的环境执行。
cd "$ROOT_DIR"
docker compose "${COMPOSE_ARGS[@]}" up -d --build

wait_for_mongo
ensure_mongo_replica_set
wait_for_mongo_primary

cd "$E2E_DIR"
if [[ ! -d node_modules ]]; then
  pnpm install
fi

pnpm exec playwright install chromium
pnpm test "$@"
