# E2E 测试建议

## 当前定位

`e2e/` 使用 Playwright，默认通过 Docker Compose 拉起接近部署态的整套服务：

- `webapp`
- `evaluateapp`
- `mongo`
- `redis`
- `minio`

适合验证这类主链路：

- 注册 / 登录
- 比赛创建与题目上传
- 组队与报名
- 提交上传与评测回调
- 排行榜更新
- 管理后台操作

## 推荐运行方式

### 冒烟测试

当前建议至少保这两条：

```bash
cd /proj/aigame/e2e
./run.sh tests/05-admin-problem.spec.ts tests/08-submission-evaluateapp.spec.ts
```

这两条覆盖了：

- 管理端题目资源上传与批量导入
- 提交流程、评测回调、重入队与排行榜口径

### 全量测试

```bash
cd /proj/aigame/e2e
./run.sh
```

### 已启动服务后的手动运行

如果你已经自己把服务启动好了，也可以只在 `e2e/` 里跑：

```bash
cd /proj/aigame/e2e
pnpm test
```

## `run.sh` 当前会做什么

`e2e/run.sh` 已经内置了完整流程：

- 拉起 `docker-compose.deploy.yml` + `e2e/docker-compose.e2e.override.yml`
- 等待 MongoDB 可连接
- 自动初始化 MongoDB 副本集
- 等待 PRIMARY 就绪
- 安装 Playwright Chromium（缺失时）
- 执行测试
- 失败时导出关键服务日志
- 最后自动 `down -v --remove-orphans`

## 推荐测试策略

### 开发中

- 改页面样式：可以先不跑 E2E
- 改接口语义、权限、Cookie、队列、提交、回调：建议至少跑一次冒烟
- 改 Dockerfile、Compose、环境变量、Prisma、登录态：建议跑 deploy + E2E 冒烟

### 提交前

至少做其中一项：

- 跑两条冒烟
- 或跑你改动相关的 spec
- 或在 CI 中跑全量

### 合并前

建议：

- 核心链路改动跑全量
- 普通业务改动至少跑冒烟

## 常见排查入口

### 服务日志

测试失败时，`run.sh` 会把关键日志写到：

- `e2e/artifacts/service-logs.txt`

### Playwright 报告

```bash
cd /proj/aigame/e2e
pnpm test:report
```

### 单条用例调试

```bash
cd /proj/aigame/e2e
./run.sh tests/08-submission-evaluateapp.spec.ts --reporter=line
```

或：

```bash
cd /proj/aigame/e2e
pnpm test --headed
```

## 新增 E2E 用例建议

- 用例标题尽量保持中文，方便业务同学直接看报告。
- 优先覆盖真实业务路径，不要只测纯接口 happy path。
- 测试数据尽量带 `runId` 前缀，避免并发冲突。
- 如果用例可能重试，资源名建议拼上 `test.info().retry`。
- 涉及主链路的断言要包含状态变化，而不是只断言 `200`。

## 当前高价值目录

- `e2e/tests/05-admin-problem.spec.ts`
- `e2e/tests/08-submission-evaluateapp.spec.ts`
- `e2e/global-setup.ts`
- `e2e/utils/mongo.ts`
- `e2e/run.sh`

如果你要先熟悉现状，优先从这几个文件开始看。
