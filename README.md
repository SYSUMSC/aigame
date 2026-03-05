# aigame

## 两种 Docker Compose 方案（开发/部署）

- 开发态（EvaluateApp 在宿主机运行）：`docker-compose.dev.yml`
  - 仅启动依赖：MongoDB、Redis、MinIO；EvaluateApp 用 uv 在宿主机运行。
  - 启动依赖：`docker compose -f docker-compose.dev.yml up -d`
  - 启动 EvaluateApp：
    - `cd evaluateapp && cp .env.example .env`（按需编辑 `.env`）
    - 安装依赖：`uv sync`
    - 运行服务：`uv run uvicorn main:app --host 0.0.0.0 --port 8000`
    - 若评测走 Docker 后端，设置 `.env` 中 `SANDBOX_BACKEND=DOCKER` 且指定 `DOCKER_IMAGE=<你的评测镜像>`（宿主运行不支持 `self`）。

- 部署态（EvaluateApp 在容器运行）：`docker-compose.deploy.yml`
  - 启动：`docker compose -f docker-compose.deploy.yml up -d --build`
  - 该方案会同时启动：`mongo`、`redis`、`minio`、`evaluateapp`、`webapp`
  - 默认宿主机端口（可通过环境变量覆盖）：
    - MongoDB: `37017`（`MONGO_HOST_PORT`）
    - Redis: `36379`（`REDIS_HOST_PORT`）
    - MinIO API: `39000`（`MINIO_API_HOST_PORT`）
    - MinIO Console: `39001`（`MINIO_CONSOLE_HOST_PORT`）
    - EvaluateApp: `38000`（`EVALUATEAPP_HOST_PORT`）
    - WebApp: `33000`（`WEBAPP_HOST_PORT`）
  - 该方案会构建 `evaluateapp/docker/evaluateapp.Dockerfile`，镜像基于：
    - `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.12-slim`
  - WebApp 镜像基于：
    - `swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/node:24.14.0-bookworm`
  - 容器默认 `SANDBOX_BACKEND=DOCKER` 且 `DOCKER_IMAGE=self`，评测容器会复用服务容器的 Python 环境与依赖。
  - 依赖服务与 EvaluateApp 同网段 `aigame`，`evaluateapp` 暴露 `8000` 端口。

> 说明：根目录原有 `docker-compose.yml` 保留兼容，推荐使用新文件分别在开发/部署环境中运行。

## 当前的docker服务

Redis,Mongodb,minio

### 初次启动mongodb的初始化

需要设置data权限

```shell
chmod 755 ./init.sh
sh ./init.sh
```

### 后续正常启动docker compose（推荐使用 dev/deploy 文件）

开发态依赖：
```shell
docker compose -f docker-compose.dev.yml up -d
```

部署态服务：
```shell
docker compose -f docker-compose.deploy.yml up -d --build
```


## python evaluate（宿主机运行 EvaluateApp）

需要先安装 uv，之后
```shell
cd evaluateapp
cp .env.example .env
uv sync
```

创建沙盒
```shell
# 创建一个不允许登录的系统用户和组
sudo groupadd sandboxgroup
sudo useradd --system --no-create-home --shell /bin/false -g sandboxgroup sandboxuser
# 创建监狱目录
sudo mkdir -p /opt/sandbox_jail
sudo chown root:root /opt/sandbox_jail
sudo mkdir -p /opt/sandboxes
sudo chmod 1777 /opt/sandboxes
```

若要在宿主机上使用 Docker 作为评测后端：
- 在 `evaluateapp/.env` 设置：`SANDBOX_BACKEND=DOCKER` 与 `DOCKER_IMAGE=<包含评测依赖的镜像>`。
- 注意：`DOCKER_IMAGE=self` 仅在“EvaluateApp 以容器运行”时可用于复用服务容器镜像；
  宿主机运行时如需与服务容器相同环境，可构建服务镜像并指定其 tag：
  - `docker build -t aigame-eval:py312 -f evaluateapp/docker/evaluateapp.Dockerfile .`
  - `.env` 中设置：`DOCKER_IMAGE=aigame-eval:py312`


## Nuxt Web APP

使用`pnpm`进行启动，css采用`tailwind`

为了方便调试统一环境

需要修改host

`sudo nano /etc/hosts`

加入下面的

```
127.0.0.1   mongo
127.0.0.1   redis
127.0.0.1   minio
```

### 初次安装

```shell
cd webapp
pnpm i
pnpm npx generate
cp .env.example .env
```

### 启动测试

```shell
cd webapp
pnpm dev
```

### prisma重新生成
```shell
pnpm prisma generate
pnpm prisma db push
```

## 题目开发与打包

题目目录使用统一结构，便于快速打包和在后台上传：

```
evaluate_example/
  task_name/
    judge/           # 评测脚本 judge.py 及参考标签/文件
    data/            # 可选，提供给选手下载的数据集
    test_submit/     # 提交示例（示例结果或代码骨架）
    problem.yml      # 元信息（标题/简介/起止时间/分值等）
    desc.md          # 题目详细描述（Markdown）
```

注意：detailedDescription 已从 problem.yml 分离为独立的 desc.md 文件。后台批量上传会优先读取压缩包中的 desc.md。

### 创建与打包

- 在 `evaluate_example/` 中新增你的题目文件夹（英文名）。
- 将 `judge.py` 和参考标签等放入 `judge/`，示例提交放入 `test_submit/`，可选数据集放入 `data/`。
- 在根目录填写 `problem.yml`（无 detailedDescription 字段）以及 `desc.md`（Markdown）。
- 使用打包脚本生成上传包：

```bash
cd evaluate_example
python3 pack.py path/to/task_name
# 或者批量打包当前目录下所有题目
python3 pack.py --all --root .
```

脚本会在题目目录内生成三类子包：`judge.zip`、`test_submit.zip`、`data.zip`（可选），并最终生成 `task_name.zip`（包含上述子包 + problem.yml + desc.md）。

### 后台上传与模式选择（建议）

- 训练耗时较长（“训练久”）的题目：建议采用“标签上传”思路——选手线下训练，线上仅上传预测结果（例如 `results.csv`/`results.json`）。
  - 在 `judge/` 内放置参考标签文件，`judge.py` 做结果对齐与评分。
  - `test_submit/` 提供一个可直接压缩上传的结果示例。
- 训练较快（“训练快”）的题目：建议采用“文件上传”思路——选手上传可执行代码，线上快速运行并评分。
  - 在 `test_submit/` 提供最小可运行示例代码骨架（如 `main.py`）。
  - `judge.py` 负责拉起/校验代码产出的结果并打分。

最后在“管理后台 → 题目管理 → 批量上传”页面上传 `task_name.zip` 即可；若同名题目需更新，可选择“覆盖”。

## 脚本

项目包含一些用于数据库初始化和数据生成的辅助脚本，位于 `webapp/scripts` 目录下。

**重要:** 直接使用 `node` 运行这些脚本会失败，因为它们需要加载 `.env` 文件中的数据库连接等环境变量。请使用下面定义的 `pnpm` 命令来运行它们。

首先，确保你已经根据 `.env.example` 创建了 `.env` 文件：
```shell
cd webapp
cp .env.example .env
```
然后，你可以使用 `pnpm` 运行以下脚本命令 (我们将在下一步中把这些命令添加到 `package.json`):

### `db:init`

初始化数据库，主要用于测试数据库连接。

**用法:**
```shell
cd webapp
pnpm db:init
```

### `db:admin`

创建一个默认的管理员账户。如果已存在管理员或用户名为 `admin` 的账户，则不会创建。

-   **默认用户名:** `admin`
-   **默认密码:** `123456`

**用法:**
```shell
cd webapp
pnpm db:admin
```

### `minio:init`

初始化MinIO存储桶，确保存储桶存在并设置为公共读取权限。脚本会创建名为 `aigame` 的存储桶。

**用法:**
```shell
cd webapp
pnpm minio:init
```

### `db:seed`

为数据库生成一套完整的测试数据，包括竞赛、题目、队伍、用户、提交记录和排行榜。

**注意:** 此脚本会先**清空**数据库中除 `admin` 用户外的大部分数据，请谨慎在生产环境中使用。

**用法:**
```shell
cd webapp
pnpm db:seed
```


## 备注

### docker mongodb验证用户id的方法

```shell
docker run --rm swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/mongodb/mongodb-community-server:8.0.13-ubuntu2204 id -u mongodb
```
