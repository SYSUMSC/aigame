# aigame

`aigame` 是一个面向 AI 竞赛场景的完整平台，包含比赛管理、题目上传、提交评测、排行榜、题解上传，以及配套的端到端测试体系。

## 文档导航

- 总览：`docs/README.md`
- 本地开发建议：`docs/development.md`
- 服务器部署建议：`docs/deployment.md`
- E2E 测试建议：`docs/e2e-testing.md`
- 出题与打包方法：`docs/problem-authoring.md`
- 评测服务补充说明：`evaluateapp/README.md`
- 题目样例与打包细节：`evaluate_example/README.md`

## 仓库结构

- `webapp/`：Nuxt 4 Web 应用，包含页面、API、队列、排行榜与管理后台。
- `evaluateapp/`：评测服务，负责解包提交、执行评测脚本并回调 WebApp。
- `e2e/`：Playwright 端到端测试工程，默认按接近部署态的方式拉起整套服务。
- `evaluate_example/`：题目样例、打包脚本与本地评测示例。
- `docker-compose.dev.yml`：开发态依赖服务编排，适合本机开发 WebApp / EvaluateApp。
- `docker-compose.deploy.yml`：部署态编排，适合服务器启动整套服务。

## 快速入口

### 1. 本地开发

建议先看 `docs/development.md`。最常用的起步方式如下：

```bash
# 启动开发依赖
cd /proj/aigame
docker compose -f docker-compose.dev.yml up -d

# 启动 WebApp
cd /proj/aigame/webapp
cp .env.example .env
pnpm install
pnpm dev
```

如果你需要联调评测服务，再启动 EvaluateApp：

```bash
cd /proj/aigame/evaluateapp
cp .env.example .env
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

### 2. 服务器部署

建议先看 `docs/deployment.md`。当前推荐命令：

```bash
cd /proj/aigame
docker compose -f docker-compose.deploy.yml up -d --build
```

`docker-compose.deploy.yml` 已自动完成 MongoDB 副本集初始化，不需要再手工执行 `rs.initiate(...)`。

### 3. E2E 冒烟

建议先看 `docs/e2e-testing.md`。当前两条高价值冒烟用例：

```bash
cd /proj/aigame/e2e
./run.sh tests/05-admin-problem.spec.ts tests/08-submission-evaluateapp.spec.ts
```

## 推荐阅读顺序

- 第一次接手项目：先看 `docs/README.md`
- 要在本机改页面 / API：看 `docs/development.md`
- 要上线服务器：看 `docs/deployment.md`
- 要补测试或排查回归：看 `docs/e2e-testing.md`
- 要新增比赛题目：看 `docs/problem-authoring.md`

## 当前建议

- 日常功能开发优先使用开发态：依赖服务走 `docker-compose.dev.yml`，WebApp / EvaluateApp 在宿主机运行，调试效率更高。
- 集成联调、部署验证、提测前冒烟优先使用部署态：行为更接近线上。
- 正式环境不要直接沿用仓库里的默认密码与密钥，请在部署前统一替换。
