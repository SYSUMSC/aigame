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
- 容器里的 `EvaluateApp` 会固定使用 `SANDBOX_BACKEND=DOCKER` 与 `DOCKER_IMAGE=self`
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

开发态和部署态的 Compose 现在都优先读取根目录 `.env`。建议先执行：

```bash
cd /proj/aigame
cp .env.example .env
```

其中 MongoDB / Redis / MinIO 的宿主机端口、密码、时区等共享配置，都放在这一个文件里统一维护。


### 1. 启动开发依赖

```bash
cd /proj/aigame
docker compose -f docker-compose.dev.yml up -d
```

### 2. 准备 WebApp

```bash
cd /proj/aigame/webapp
pnpm install
pnpm prisma:generate
pnpm dev
```

### 3. 准备 EvaluateApp

```bash
cd /proj/aigame/evaluateapp
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

## 本地开发的环境变量建议

### WebApp

WebApp 本地开发默认优先复用根目录 `.env`，不再要求单独维护 `webapp/.env`。

另外，根目录 `.env` 同时控制 Compose 暴露到宿主机的端口和 WebApp 本地脚本所需的连接配置。只有在你确实要做模块级覆盖时，才需要额外创建 `webapp/.env`。

默认情况下，你现在不需要再改 `webapp/.env` 或系统 `hosts`。

- 根目录 `.env` 负责维护共享端口、密码、公开地址等基础变量
- `webapp` 的本地命令会自动从根 `.env` 推导 `MONGODB_URI`、`REDIS_URL`、`MINIO_*`、`WEBAPP_BASE_URL` 等常用值

只有在你确实要做模块级覆盖时，才需要额外创建 `webapp/.env`。

### MongoDB 副本集说明

- WebApp 当前使用带副本集参数的 MongoDB 连接串。
- `docker-compose.deploy.yml` 已自动初始化副本集。
- `docker-compose.dev.yml` 现在也包含 `mongo-init`，首次清库后启动会自动初始化副本集。
- `docker-compose.dev.yml` 已包含 `mongo-perms` 预处理，删除 `data/mongo` 后可直接 `docker compose -f docker-compose.dev.yml up -d`。

如果你在开发态首次启动 MongoDB 且初始化未成功，可以：

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
