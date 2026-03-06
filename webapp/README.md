# WebApp 模块说明

`webapp/` 是 `aigame` 的前端与服务端一体应用，基于 Nuxt 4 构建，既提供用户界面，也承载大部分业务 API。

## 模块职责

`webapp` 主要负责：

- 用户注册、登录、权限控制
- 比赛、题目、队伍、报名、提交、题解等业务页面
- 管理后台页面与对应 API
- 提交队列消费、评测回调处理、排行榜同步
- MinIO 文件上传与资源访问

如果你是第一次接手项目，建议先看根文档：

- `/proj/aigame/README.md`
- `/proj/aigame/docs/development.md`
- `/proj/aigame/docs/deployment.md`
- `/proj/aigame/docs/e2e-testing.md`

## 技术栈

- Nuxt 4
- Vue 3
- Prisma
- MongoDB
- Redis / BullMQ
- MinIO
- Tailwind CSS

## 常用目录

- `server/api/`：后端业务 API
- `server/utils/`：服务端工具函数
- `server/plugins/`：队列、启动初始化等插件
- `server/middleware/`：鉴权与请求中间件
- `pages/`：页面路由
- `components/`：页面组件
- `composables/`：前端组合式逻辑
- `prisma/`：Prisma schema
- `scripts/`：数据库与 MinIO 初始化脚本
- `docker/`：WebApp Docker 构建文件

## 开发方式

### 1. 准备环境变量

```bash
cd /proj/aigame/webapp
cp .env.example .env
```

默认 `.env.example` 中使用：

- `mongo`
- `redis`
- `minio`

作为服务主机名。

如果你在宿主机开发，有两种常见做法：

- 保留这些主机名，并在本机 `hosts` 中映射到 `127.0.0.1`
- 或直接把 `.env` 改成 `127.0.0.1` 形式的连接地址

更完整的建议见：`/proj/aigame/docs/development.md`

如果你是通过 Compose 启动依赖服务，MongoDB / Redis / MinIO 的宿主机端口与密码统一由根目录 `.env` 管理。

### 2. 安装依赖

```bash
cd /proj/aigame/webapp
pnpm install
```

### 3. 生成 Prisma Client

```bash
cd /proj/aigame/webapp
pnpm prisma:generate
```

### 4. 启动开发服务

```bash
cd /proj/aigame/webapp
pnpm dev
```

默认会启动在 `http://localhost:3000`。

## 构建与生产运行

### 本地构建

```bash
cd /proj/aigame/webapp
pnpm build
```

当前 `build` 已显式包含 `prisma generate`，避免构建产物缺失 Prisma Client。

### Docker 构建

WebApp 的容器构建文件位于：

- `/proj/aigame/webapp/docker/webapp.Dockerfile`

整个项目推荐通过根目录 compose 启动，而不是单独手工构建 WebApp：

```bash
cd /proj/aigame
docker compose -f docker-compose.deploy.yml up -d --build
```

## 常用脚本

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

含义：

- `pnpm dev`：启动开发服务器
- `pnpm build`：构建生产产物
- `pnpm prisma:generate`：生成 Prisma Client
- `pnpm db:init`：初始化数据库连接与基础准备
- `pnpm db:admin`：创建默认管理员账号
- `pnpm minio:init`：初始化 MinIO 存储桶
- `pnpm db:seed`：生成测试数据

## 开发注意事项

### 1. 运行时配置优先看环境变量

该项目既使用 Nuxt `runtimeConfig`，也依赖 `process.env` 默认值。

在容器环境中，推荐通过 `NUXT_*` 环境变量显式传入运行时配置，避免构建时把错误的默认值烘焙进产物。

### 2. Prisma 相关

- 修改 `prisma/schema.prisma` 后，记得重新执行 `pnpm prisma:generate`
- 构建链路已经显式执行 Prisma Client 生成，不要再假设 `postinstall` 一定会替你完成

### 3. 本地 HTTP 登录态

项目已经兼容本地 HTTP / E2E 场景，不会在所有生产模式下一刀切强制 `Secure Cookie`。

如果你在本地调试登录问题，优先检查：

- `AUTH_ORIGIN`
- 请求头中的协议转发信息
- 当前是否处于反向代理 HTTPS 场景

### 4. 改动后建议回归的场景

如果你改了以下内容，建议至少跑一次针对性验证：

- 登录 / 注册 / 权限
- 提交上传 / 评测回调
- 排行榜同步
- 后台题目上传
- Docker 构建与 deploy 启动

相关文档：

- `/proj/aigame/docs/e2e-testing.md`

## 与其他模块的关系

- `evaluateapp/`：负责执行评测与回调结果
- `e2e/`：负责从用户视角和 API 视角验证主流程
- `evaluate_example/`：提供题目样例、打包与本地评测材料

## 推荐阅读

- 总入口：`/proj/aigame/README.md`
- 本地开发：`/proj/aigame/docs/development.md`
- 服务器部署：`/proj/aigame/docs/deployment.md`
- E2E 测试：`/proj/aigame/docs/e2e-testing.md`
- 出题方法：`/proj/aigame/docs/problem-authoring.md`
