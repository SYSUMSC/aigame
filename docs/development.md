# 本地开发建议

## 开发模式选择

### 方案一：日常开发模式

适合页面、接口、管理后台、排行榜等日常开发。

- 依赖服务用 Docker 启动：MongoDB、Redis、MinIO
- WebApp 在宿主机运行：`pnpm dev`
- EvaluateApp 按需在宿主机运行：`uv run uvicorn ...`
- 优点：重载快、日志直观、改代码反馈快

### 方案二：接近线上联调模式

适合集成联调、部署问题排查、提测前验证。

- 直接使用 `docker-compose.deploy.yml`
- WebApp 与 EvaluateApp 都在容器里运行
- 优点：行为更接近线上，环境差异更小

## 环境准备

建议的本机工具：

- Docker / Docker Compose
- Node.js 24
- `pnpm`
- Python 3.12
- `uv`

如果要跑 E2E，还需要：

- `cd /proj/aigame/e2e && pnpm install`
- `cd /proj/aigame/e2e && pnpm exec playwright install chromium`

## 第一次启动建议

### 1. 启动开发依赖

```bash
cd /proj/aigame
docker compose -f docker-compose.dev.yml up -d
```

### 2. 准备 WebApp

```bash
cd /proj/aigame/webapp
cp .env.example .env
pnpm install
pnpm prisma:generate
pnpm dev
```

### 3. 准备 EvaluateApp

```bash
cd /proj/aigame/evaluateapp
cp .env.example .env
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 本地开发的环境变量建议

### WebApp

`webapp/.env.example` 默认使用 `mongo`、`redis`、`minio` 作为主机名。

你有两种做法：

- 做法 A：保留默认配置，并在本机 `hosts` 中加入：

```text
127.0.0.1 mongo
127.0.0.1 redis
127.0.0.1 minio
```

- 做法 B：直接把 `webapp/.env` 改成宿主机地址，例如：
  - `MONGODB_URI=mongodb://root:password@127.0.0.1:27017/aigame?authSource=admin&replicaSet=rs0&directConnection=true`
  - `REDIS_URL=redis://127.0.0.1:6379`
  - `MINIO_ENDPOINT=127.0.0.1`
  - `MINIO_INTERNAL_URL=http://127.0.0.1:9000`

建议：如果你只在自己电脑开发，优先使用做法 B，少改系统级配置。

### MongoDB 副本集说明

- WebApp 当前使用带副本集参数的 MongoDB 连接串。
- `docker-compose.deploy.yml` 已自动初始化副本集。
- `docker-compose.dev.yml` 只负责启动依赖，不会自动做这一步。

如果你在开发态首次启动 MongoDB，可以：

- 复用已有数据目录；或
- 参考根目录 `init.sh` 做一次初始化；或
- 手工进入 Mongo 容器执行 `rs.initiate(...)`

## 推荐开发顺序

### 只改 Web 页面 / API

```bash
cd /proj/aigame
docker compose -f docker-compose.dev.yml up -d

cd /proj/aigame/webapp
pnpm dev
```

### 改评测逻辑

```bash
cd /proj/aigame
docker compose -f docker-compose.dev.yml up -d

cd /proj/aigame/evaluateapp
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

然后用：

- `evaluate_example/test_evaluate.py`
- 或 `evaluateapp` 的 `/gradio`
- 或 E2E 的 `08-submission-evaluateapp.spec.ts`

做联调验证。

### 改部署 / 容器 / 构建链路

直接用：

```bash
cd /proj/aigame
docker compose -f docker-compose.deploy.yml up -d --build
```

这样最容易提前发现 Docker 构建、运行时环境变量、Prisma Client、容器网络等问题。

## 常用命令

### WebApp

```bash
cd /proj/aigame/webapp
pnpm dev
pnpm build
pnpm prisma:generate
pnpm db:init
pnpm db:admin
pnpm minio:init
pnpm db:seed
```

### EvaluateApp

```bash
cd /proj/aigame/evaluateapp
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### Docker

```bash
cd /proj/aigame
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml down

docker compose -f docker-compose.deploy.yml up -d --build
docker compose -f docker-compose.deploy.yml down
```

## 本地开发建议

- 不要一上来就用部署态改前端页面，反馈回路太慢。
- 改了登录、提交、评测、排行榜、后台管理等主链路后，至少补跑一次 E2E 冒烟。
- 改了 Dockerfile、Compose、环境变量、Prisma、Cookie、安全鉴权后，优先用部署态复验。
- 如果你要清库再跑测试，先确认是否会影响已有本地数据目录。
