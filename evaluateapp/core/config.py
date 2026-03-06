from pathlib import Path
from pydantic import model_validator
from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent  # evaluateapp/ 目录
ROOT_DIR = BASE_DIR.parent
ROOT_ENV_FILE = ROOT_DIR / ".env"
LOCAL_ENV_FILE = BASE_DIR / ".env"
ENV_FILE = str(ROOT_ENV_FILE if ROOT_ENV_FILE.exists() else LOCAL_ENV_FILE)


class Settings(BaseSettings):
    PUBLIC_HOST: str = "localhost"
    WEBAPP_HOST_PORT: int = 33000
    WEBAPP_CALLBACK_URL: str = ""
    # 统一共享密钥：用于双向签名校验
    SHARED_SECRET: str = "a-very-long-and-random-shared-secret"
    # 是否启用调试用的 Gradio 页面
    ENABLE_GRADIO: bool = False
    # Gradio 页面挂载路径
    GRADIO_PATH: str = "/gradio"
    # 是否启用 Seccomp 过滤（默认关闭，避免阻断 exec 等系统调用）
    ENABLE_SECCOMP: bool = False
    # 评测后端：CHROOT 或 DOCKER
    SANDBOX_BACKEND: str = "CHROOT"

    # Docker 评测相关配置（当 SANDBOX_BACKEND=DOCKER 时生效）
    DOCKER_IMAGE: str = "swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/library/python:3.12-slim-bookworm"
    DOCKER_PULL: bool = False
    DOCKER_SOCKET: str = "/var/run/docker.sock"  # 仅用于部署文档提示
    DOCKER_MEMORY: str = "2g"
    DOCKER_CPUS: float = 1.0
    DOCKER_NETWORK_MODE: str = "none"
    DOCKER_USER: str | None = None
    DOCKER_SELF_BUILD_ON_HOST: bool = True
    DOCKER_SELF_TAG: str = "aigame-eval:self"
    DOCKER_SELF_CONTEXT: str = str(BASE_DIR.parent)
    DOCKER_SELF_DOCKERFILE: str = "evaluateapp/docker/evaluateapp.Dockerfile"

    @model_validator(mode="after")
    def apply_derived_defaults(self):
        if not self.WEBAPP_CALLBACK_URL:
            self.WEBAPP_CALLBACK_URL = f"http://{self.PUBLIC_HOST}:{self.WEBAPP_HOST_PORT}/api/submissions/callback"
        return self

    class Config:
        env_file = ENV_FILE
        env_file_encoding = "utf-8"


settings = Settings()
