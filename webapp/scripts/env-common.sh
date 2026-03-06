#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEBAPP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ROOT_DIR="$(cd "$WEBAPP_DIR/.." && pwd)"
ROOT_ENV="$ROOT_DIR/.env"
LOCAL_ENV="$WEBAPP_DIR/.env"

if [ -f "$ROOT_ENV" ]; then
  set -a
  . "$ROOT_ENV"
  set +a
  SHARED_DOTENV_PATH="../.env"
elif [ -f "$LOCAL_ENV" ]; then
  set -a
  . "$LOCAL_ENV"
  set +a
  SHARED_DOTENV_PATH=".env"
else
  SHARED_DOTENV_PATH=""
fi

export TZ="${TZ:-Asia/Shanghai}"
export PUBLIC_HOST="${PUBLIC_HOST:-localhost}"

export MONGO_ROOT_USERNAME="${MONGO_ROOT_USERNAME:-root}"
export MONGO_ROOT_PASSWORD="${MONGO_ROOT_PASSWORD:-password}"
export MONGODB_REPLICA_SET="${MONGODB_REPLICA_SET:-rs0}"
export MONGO_HOST_PORT="${MONGO_HOST_PORT:-37017}"

export REDIS_PASSWORD="${REDIS_PASSWORD:-password}"
export REDIS_HOST_PORT="${REDIS_HOST_PORT:-36379}"

export MINIO_ROOT_USER="${MINIO_ROOT_USER:-root}"
export MINIO_ROOT_PASSWORD="${MINIO_ROOT_PASSWORD:-password}"
export MINIO_API_HOST_PORT="${MINIO_API_HOST_PORT:-39000}"
export MINIO_CONSOLE_HOST_PORT="${MINIO_CONSOLE_HOST_PORT:-39001}"

export WEBAPP_HOST_PORT="${WEBAPP_HOST_PORT:-33000}"
export EVALUATEAPP_HOST_PORT="${EVALUATEAPP_HOST_PORT:-38000}"

export SHARED_SECRET="${SHARED_SECRET:-a-very-long-and-random-shared-secret}"
export JWT_SECRET="${JWT_SECRET:-your-super-secret-jwt-key-change-this-in-production}"
export NEXTAUTH_SECRET="${NEXTAUTH_SECRET:-your-nextauth-secret-key}"
export SMTP_STUB="${SMTP_STUB:-false}"
export SMTP_HOST="${SMTP_HOST:-smtp.example.com}"
export SMTP_PORT="${SMTP_PORT:-587}"
export SMTP_USER="${SMTP_USER:-your-email@example.com}"
export SMTP_PASS="${SMTP_PASS:-your-smtp-password}"
export SMTP_FROM="${SMTP_FROM:-noreply@example.com}"
export SMTP_FROM_NAME="${SMTP_FROM_NAME:-AI Game Platform}"
export SMTP_SECURE="${SMTP_SECURE:-false}"
export SMTP_TLS="${SMTP_TLS:-true}"
export NODE_ENV="${NODE_ENV:-development}"
export EVALUATION_TIMEOUT_MS="${EVALUATION_TIMEOUT_MS:-900000}"

export MONGODB_URI="${MONGODB_URI:-mongodb://${MONGO_ROOT_USERNAME}:${MONGO_ROOT_PASSWORD}@127.0.0.1:${MONGO_HOST_PORT}/aigame?authSource=admin&replicaSet=${MONGODB_REPLICA_SET}&directConnection=true}"
export REDIS_URL="${REDIS_URL:-redis://127.0.0.1:${REDIS_HOST_PORT}}"
export MINIO_ENDPOINT="${MINIO_ENDPOINT:-127.0.0.1}"
export MINIO_PORT="${MINIO_PORT:-${MINIO_API_HOST_PORT}}"
export MINIO_ACCESS_KEY="${MINIO_ACCESS_KEY:-${MINIO_ROOT_USER}}"
export MINIO_SECRET_KEY="${MINIO_SECRET_KEY:-${MINIO_ROOT_PASSWORD}}"
export MINIO_PUBLIC_URL="${MINIO_PUBLIC_URL:-http://${PUBLIC_HOST}:${MINIO_API_HOST_PORT}}"
export MINIO_INTERNAL_URL="${MINIO_INTERNAL_URL:-http://127.0.0.1:${MINIO_API_HOST_PORT}}"
export WEBAPP_BASE_URL="${WEBAPP_BASE_URL:-http://${PUBLIC_HOST}:${WEBAPP_HOST_PORT}}"
export AUTH_ORIGIN="${AUTH_ORIGIN:-${WEBAPP_BASE_URL}}"
export NUXT_PUBLIC_BASE_URL="${NUXT_PUBLIC_BASE_URL:-${WEBAPP_BASE_URL}}"
export EVALUATE_APP_URL="${EVALUATE_APP_URL:-http://${PUBLIC_HOST}:${EVALUATEAPP_HOST_PORT}}"
export EVALUATE_APP_SECRET="${EVALUATE_APP_SECRET:-${SHARED_SECRET}}"
export EVALUATE_APP_UPLOAD_SECRET="${EVALUATE_APP_UPLOAD_SECRET:-${SHARED_SECRET}}"

cd "$WEBAPP_DIR"
