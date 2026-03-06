# 文档总览

本文档目录用于说明 `aigame` 的常见工作流。建议把根 README 当入口，把 `docs/` 当操作手册。

## 适合谁看

- 开发同学：先看 `docs/development.md`
- 运维 / 部署同学：先看 `docs/deployment.md`
- 测试 / 质量同学：先看 `docs/e2e-testing.md`
- 出题人 / 赛事运营同学：先看 `docs/problem-authoring.md`

## 文档索引

- `docs/development.md`
  - 本地开发模式选择
  - 依赖安装与环境变量建议
  - WebApp / EvaluateApp 联调建议
  - 常见开发命令

- `docs/deployment.md`
  - 服务器准备建议
  - Docker Compose 部署步骤
  - 端口、数据目录、反向代理建议
  - 备份与安全建议

- `docs/e2e-testing.md`
  - E2E 运行方式
  - 冒烟测试建议
  - 失败排查入口
  - 新增用例建议

- `docs/problem-authoring.md`
  - 题目目录规范
  - `judge.py` 与 `problem.yml` 约定
  - 打包与后台上传方法
  - 本地自测建议

## 模块补充文档

- `evaluateapp/README.md`：重点讲评测沙箱和 Docker 评测后端。
- `evaluate_example/README.md`：重点讲题目样例、打包与本地评测。
- `webapp/README.md`：当前仍是 Nuxt 默认模板说明，建议以根文档和 `docs/` 为准。

## 推荐工作流

- 改页面 / API：开发态启动依赖，本机跑 `webapp`。
- 改评测逻辑：开发态启动依赖，本机跑 `evaluateapp`，必要时用 `evaluate_example/test_evaluate.py` 自测。
- 改部署链路：直接使用 `docker-compose.deploy.yml` 验证。
- 改主流程：至少补跑一次 E2E 冒烟。
