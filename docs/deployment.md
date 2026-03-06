# 服务器部署建议

## 推荐部署方式

当前推荐直接使用：`docker-compose.deploy.yml`

原因：

- 会同时拉起 `mongo`、`redis`、`minio`、`evaluateapp`、`webapp`
- WebApp 和 EvaluateApp 都跑在容器里，和线上更接近
- 已自动初始化 MongoDB 副本集，避免首启时额外手工操作

## 服务器基线建议

最低建议：

- 4 核 CPU
- 8 GB 内存
- 50 GB SSD
- Linux x86_64
- Docker Engine + Docker Compose Plugin

如果比赛高峰期提交较多，建议提高：

- 8 核 CPU
- 16 GB 内存以上
- 独立数据盘给 MongoDB / MinIO

## 部署前检查

### 1. 替换默认密钥与密码

当前仓库里的默认值更适合开发或测试，不建议直接上线。

部署前至少检查这些位置：

- `docker-compose.deploy.yml`
- `webapp/.env`
- `evaluateapp/.env`
- `data/mongodb.key`

尤其需要替换：

- MongoDB root 密码
- Redis 密码
- MinIO root 用户名 / 密码
- WebApp JWT / 认证密钥
- EvaluateApp 回调密钥 / 入站鉴权密钥
- MongoDB 副本集 keyfile

### 2. 准备环境文件

```bash
cd /proj/aigame
cp webapp/.env.example webapp/.env
cp evaluateapp/.env.example evaluateapp/.env
```

然后按你的域名、端口、密钥、邮件配置修改。

### 3. 检查端口规划

默认宿主机端口：

- WebApp：`33000`
- EvaluateApp：`38000`
- MongoDB：`37017`
- Redis：`36379`
- MinIO API：`39000`
- MinIO Console：`39001`

如有冲突，可以在启动前通过环境变量覆盖：

```bash
export WEBAPP_HOST_PORT=33080
export EVALUATEAPP_HOST_PORT=38080
```

## 启动方式

```bash
cd /proj/aigame
docker compose -f docker-compose.deploy.yml up -d --build
```

## 启动后检查

### 服务状态

```bash
cd /proj/aigame
docker compose -f docker-compose.deploy.yml ps
```

### 关键接口

```bash
curl -I http://127.0.0.1:33000/
curl -I http://127.0.0.1:38000/docs
curl http://127.0.0.1:33000/api/competitions
```

### MongoDB 副本集

```bash
docker exec mongo mongosh -u root -p password --authenticationDatabase admin --quiet --eval 'rs.status().ok'
```

返回 `1` 说明副本集已经正常就绪。

## 反向代理建议

生产环境建议在前面接一层 Nginx / Caddy：

- 对外只暴露 80 / 443
- WebApp 用域名反代到 `33000`
- 如不需要外部直连，可不直接暴露 MongoDB / Redis / MinIO
- 开启 HTTPS 后，登录态 Cookie 行为会更接近真实线上

## 数据与目录建议

当前重要数据目录：

- `data/mongo/`
- `data/redis/`
- `data/minio/`
- `data/mongodb.key`

建议：

- 把这些目录挂到稳定磁盘
- 做定期备份
- 对备份做恢复演练，不要只做“有文件没验证”的备份

## 运维建议

- 发布前先在同机执行一次 `docker compose ... build`
- 升级前先备份 MongoDB 和 MinIO
- 比赛期间重点盯：WebApp 日志、EvaluateApp 日志、磁盘空间、Docker 容器数量
- 如果评测任务依赖 Docker 沙箱，确认宿主机 Docker 服务稳定，且 `/var/run/docker.sock` 可被 EvaluateApp 容器访问

## 更稳妥的上线建议

推荐顺序：

1. 本地 `docker-compose.deploy.yml` 验证通过
2. 跑一次关键 E2E 冒烟
3. 推到服务器构建镜像
4. 启动容器并做接口健康检查
5. 再放开正式流量
