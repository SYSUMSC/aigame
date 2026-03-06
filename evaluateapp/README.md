EvaluateApp – Docker Sandbox Backend

概述
- 新增基于 Docker 的评测后端，可通过环境变量切换：`SANDBOX_BACKEND=CHROOT|DOCKER`。
- 两种部署方式均支持：
  1) EvaluateApp 直接运行在宿主机，使用宿主机 Docker（默认 `/var/run/docker.sock`）。
  2) EvaluateApp 以容器部署，同时将宿主机 Docker 控制文件挂载进来（挂载 `/var/run/docker.sock`）。

使用配置
- 现在默认推荐直接在根目录 `.env` 中设置；只有需要模块级覆盖时，才额外使用 `evaluateapp/.env`。
- 宿主机直接运行 `EvaluateApp` 时，根目录 `.env` 中的 `SANDBOX_BACKEND` / `DOCKER_IMAGE` 会按原值生效。
- 通过 `docker-compose.yml`、`docker-compose.deploy.yml` 或 E2E 运行容器版 `EvaluateApp` 时，Compose 会显式覆盖为 `SANDBOX_BACKEND=DOCKER` 与 `DOCKER_IMAGE=self`，避免把宿主机开发用的 `CHROOT` 配置带进容器。
  - `SANDBOX_BACKEND=DOCKER`
  - `DOCKER_IMAGE`：评测容器镜像。需包含 judge 可能使用到的依赖（如 numpy/pandas/sklearn/opencv 等）。
  - 可选限制项：`DOCKER_MEMORY`（默认 `2g`）、`DOCKER_CPUS`（默认 `1.0`）、`DOCKER_NETWORK_MODE`（默认 `none` 禁网）、`DOCKER_USER`（容器内以哪个用户运行）。
  - 可选：`DOCKER_PULL=true` 在每次任务前尝试拉取镜像。

评测容器内执行流程
- EvaluateApp 在宿主（或 Eval 容器）创建临时目录，解包 `submission.zip`、`judge.zip`。
- 生成 `/workspace/eval_runner.py`（只读挂载）并将以下目录只读挂载进容器：
  - `submission` → `/workspace/submission`
  - `judge` → `/workspace/judge`
- 在容器内执行 `python /workspace/eval_runner.py`，采集 stdout/stderr。
- 读取 stdout 中的 JSON 结果（`{"status","score","logs"}`），失败时回传容器日志。

部署方式 A：宿主机直接运行 EvaluateApp
- 前提：宿主机已安装并运行 Docker，EvaluateApp 进程能够访问 `/var/run/docker.sock`。
- 启动 EvaluateApp（示例）：
  - `cd evaluateapp && uvicorn main:app --host 0.0.0.0 --port 8000`
- 配置 `.env`：
  - `SANDBOX_BACKEND=DOCKER`
  - `DOCKER_IMAGE` 指向包含评测依赖的镜像

部署方式 B：EvaluateApp 以容器运行但挂载宿主机 Docker
- 核心是把宿主机的 Docker socket 挂载到 EvaluateApp 容器：
  - `-v /var/run/docker.sock:/var/run/docker.sock`
- 推荐直接在 Compose 里显式写死 `SANDBOX_BACKEND=DOCKER` 与 `DOCKER_IMAGE=self`，不要依赖根目录 `.env` 中的默认值。
- 示例 docker-compose 片段：
  - `environment` 中包含 `SANDBOX_BACKEND=DOCKER`
  - `environment` 中包含 `DOCKER_IMAGE=self`
  - volumes 中包含 `- /var/run/docker.sock:/var/run/docker.sock`

评测镜像建议
- 若“EvaluateApp 以容器运行”，推荐将 `.env` 中 `DOCKER_IMAGE=self`，使评测容器直接复用服务容器镜像（镜像由 `evaluateapp/docker/evaluateapp.Dockerfile` 构建，uv 已锁定依赖）。
- 若“EvaluateApp 在宿主机运行”但仍希望使用相同依赖集，可先构建服务镜像并赋予自定义 tag，然后将 `.env` 中 `DOCKER_IMAGE` 设置为该 tag：
  - `docker build -t aigame-eval:py312 -f evaluateapp/docker/evaluateapp.Dockerfile .`
  - `.env` 中配置：`DOCKER_IMAGE=aigame-eval:py312`

复用 EvaluateApp 的 Python 环境
- 如果你希望评测容器与 EvaluateApp 使用完全一致的 Python 运行环境（同一镜像与包），可将 `.env` 中 `DOCKER_IMAGE` 设置为 `self`：
  - 当 EvaluateApp 运行于容器中时，会自动解析当前容器的镜像并用于评测容器运行；
  - 这要求你通过 `evaluateapp/docker/evaluateapp.Dockerfile` 预装好评测所需依赖（已使用 uv 锁定安装）。

注意事项
- 默认为禁网（`DOCKER_NETWORK_MODE=none`）；如确需网络请明确配置其他 network mode 并评估安全风险。
- 为避免容器内并发过高，默认设置了若干线程环境变量（`OMP_NUM_THREADS=1` 等）。
- 评测超时时长与 chroot 后端保持一致（约 310s）。

使用 uv 管理包（服务容器）
- EvaluateApp 服务镜像基于 `evaluateapp/docker/evaluateapp.Dockerfile` 构建，使用 uv：
  - `uv export --frozen` 导出锁定依赖并安装到系统解释器（非 venv），确保评测容器用 `/usr/bin/python3` 即可访问同一套包；
  - 运行时默认 `SANDBOX_BACKEND=DOCKER` 且 `DOCKER_IMAGE=self`，即评测容器复用服务的 Python 环境；
  - 需要宿主机挂载 docker.sock 以启动评测容器。
