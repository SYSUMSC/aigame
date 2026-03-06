#!/bin/bash
set -euo pipefail

# 自动化初始化脚本：
# 1. 根据 compose 文件里的 Mongo 镜像准备数据目录与 keyfile 权限
# 2. 启动 Mongo 容器
# 3. 初始化副本集
#
# 默认读取根目录 `.env` 中的共享变量；
# 如需指定 compose 文件，可在执行前设置 COMPOSE_FILE，例如：
# COMPOSE_FILE=docker-compose.dev.yml sh ./init.sh

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT_DIR"

if [ -f .env ]; then
  set -a
  . ./.env
  set +a
fi

COMPOSE_FILE="${COMPOSE_FILE:-docker-compose.yml}"
MONGO_ROOT_USERNAME="${MONGO_ROOT_USERNAME:-root}"
MONGO_ROOT_PASSWORD="${MONGO_ROOT_PASSWORD:-password}"
MONGODB_REPLICA_SET="${MONGODB_REPLICA_SET:-rs0}"

# 从 compose 文件中提取 MongoDB 镜像名称
MONGO_IMAGE=$(awk '
  $1 == "mongo:" { in_mongo=1; next }
  in_mongo && $1 == "image:" { print $2; exit }
  in_mongo && $1 ~ /^[A-Za-z0-9_-]+:$/ { exit }
' "$COMPOSE_FILE")

if [ -z "$MONGO_IMAGE" ]; then
  echo "❌ 错误：无法在 $COMPOSE_FILE 中找到 mongo 服务镜像。"
  exit 1
fi

echo "--> 检测到 MongoDB 镜像为: $MONGO_IMAGE"

echo "--> 正在获取用户和组 ID..."
MONGO_UID=$(docker run --rm "$MONGO_IMAGE" id -u mongodb)
MONGO_GID=$(docker run --rm "$MONGO_IMAGE" id -g mongodb)

if ! [[ "$MONGO_UID" =~ ^[0-9]+$ ]] || ! [[ "$MONGO_GID" =~ ^[0-9]+$ ]]; then
  echo "❌ 错误：无法从镜像 '$MONGO_IMAGE' 获取有效的 mongodb 用户或组 ID。"
  exit 1
fi

echo "✅ 成功获取! 用户ID (UID): $MONGO_UID, 组ID (GID): $MONGO_GID"

echo "--> 正在创建目录和密钥文件..."
mkdir -p ./data/mongo
if [ ! -f ./data/mongodb.key ]; then
  openssl rand -base64 756 > ./data/mongodb.key
fi

echo "--> 正在设置文件和目录权限..."
sudo chown -R "$MONGO_UID:$MONGO_GID" ./data/mongo
sudo chown "$MONGO_UID:$MONGO_GID" ./data/mongodb.key
sudo chmod 400 ./data/mongodb.key
echo "✅ 权限设置完成。"

echo "--> 正在启动 MongoDB 容器..."
docker compose -f "$COMPOSE_FILE" up -d mongo

echo "--> 等待 MongoDB 就绪..."
sleep 10

echo "--> 正在初始化 MongoDB 副本集..."
docker compose -f "$COMPOSE_FILE" exec mongo \
  mongosh -u "$MONGO_ROOT_USERNAME" -p "$MONGO_ROOT_PASSWORD" --authenticationDatabase admin \
  --eval "try { rs.status().ok } catch (error) { rs.initiate({ _id: '$MONGODB_REPLICA_SET', members: [ { _id: 0, host: 'mongo:27017' } ]}) }"

echo "🎉 MongoDB 初始化成功完成！"
