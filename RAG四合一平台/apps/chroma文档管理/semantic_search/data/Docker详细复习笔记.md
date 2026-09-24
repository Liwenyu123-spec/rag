# Docker 详细复习笔记

> 仿照《集成学习详细笔记》写法：直觉 → 概念 → 对照表 → 逐行注释示例 → 易错点 → 自测。  
> 结合 FastAPI 项目常见部署场景（镜像、容器、compose、卷、网络）。  
> 命令与配置示例带中文注释风格说明。  
> 姊妹篇：`FastAPI详细复习笔记.md`、`HTML详细复习笔记.md`。

---

## 〇、这份笔记怎么用

一句话抓住全篇：

> **Docker 把「应用 + 运行环境」打成可搬运的集装箱：在你电脑能跑，到服务器也按同一套跑。**

| 章 | 核心问题 |
| --- | --- |
| 一 | 为什么需要 Docker |
| 二 | 镜像、容器、仓库 |
| 三 | Dockerfile 写法 |
| 四 | 常用命令 |
| 五 | docker-compose 多容器 |
| 六 | 卷、网络、环境变量 |
| 七 | FastAPI 实战编排 |
| 八 | 易错点、自测、练习 |

本机需安装 Docker Desktop（Windows/macOS）或 Docker Engine（Linux）。

---

## 一、总地图：解决什么痛点

### 1.1 没有容器时的经典灾难

- A 电脑 Python 3.11，服务器 3.8  
- 本地有库，服务器缺库  
- 「在我机器上是好的」  

Docker 的目标：把依赖、系统工具、启动命令一起打包。

### 1.2 虚拟机 vs 容器

| | 虚拟机 VM | 容器 Container |
| --- | --- | --- |
| 隔离级别 | 硬件级，带完整客户机 OS | 进程级，共享宿主机内核 |
| 体积 | 很大（GB 级） | 较小（常几十到几百 MB） |
| 启动 | 较慢 | 秒级 |
| 密度 | 一台机器跑不多 | 可跑很多 |
| 典型用途 | 强隔离、完整系统 | 应用交付、微服务 |

### 1.3 三个核心词

| 概念 | 类比 | 含义 |
| --- | --- | --- |
| 镜像 Image | 类 / 安装包 / 只读模板 | 怎么建环境的说明书打包结果 |
| 容器 Container | 对象 / 运行中的进程 | 镜像跑起来的实例 |
| 仓库 Registry | 应用商店 | 存放镜像，如 Docker Hub、私有仓 |

关系：

```text
Dockerfile  --build-->  Image  --run-->  Container
                              ^
                              |
                         pull / push
                              |
                          Registry
```

### 1.4 概念卡片

| 概念 | 人话 |
| --- | --- |
| Dockerfile | 构建镜像的菜谱 |
| Tag | 镜像版本号，如 `app:1.0` |
| 端口映射 `-p` | 宿主机端口 → 容器端口 |
| 数据卷 Volume | 把数据落到宿主机，容器删了数据还在 |
| 网络 Network | 容器之间怎么互相访问 |
| Compose | 用一份 YAML 一次拉起多个容器 |
| `.dockerignore` | 构建时忽略哪些文件（像 `.gitignore`） |

---

## 二、镜像与容器生命周期

### 2.1 生命周期口诀

1. `build` 得到镜像  
2. `run` 得到容器  
3. `stop` / `start` 停与启  
4. `logs` 看日志  
5. `exec` 进容器排查  
6. `rm` 删容器；`rmi` 删镜像  

### 2.2 镜像分层（为什么构建要会缓存）

Dockerfile 每条指令通常一层。  
**不变的层放前面，常变的（代码）放后面**，重复构建更快。

坏顺序：先 COPY 全部代码，再 pip install → 代码一改，依赖层缓存全废。  
好顺序：先复制 `requirements.txt` 并安装，再 COPY 源码。

---

## 三、Dockerfile 详细写法（FastAPI 向）

### 3.1 最小可用 Dockerfile

```dockerfile
# 基础镜像：官方 Python 精简版
FROM python:3.11-slim

# 容器内工作目录
WORKDIR /app

# 环境变量：不写 .pyc；日志直接打到终端
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 先只复制依赖清单，利用缓存
COPY requirements.txt .

# 安装依赖（--no-cache-dir 减小镜像）
RUN pip install --no-cache-dir -r requirements.txt

# 再复制项目代码
COPY . .

# 容器对外声明端口（文档意义为主，真正映射靠 -p）
EXPOSE 8000

# 容器启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

要点：

- `--host 0.0.0.0`：允许容器外访问；只绑 `127.0.0.1` 时宿主机进不去  
- `CMD` 可被 `docker run` 命令覆盖；`ENTRYPOINT` 更偏「固定入口」  

### 3.2 `.dockerignore` 建议

```text
.git
.venv
__pycache__
*.pyc
.env
.idea
.vscode
tests
docs
*.md
```

避免把虚拟环境和机密文件打进镜像。

### 3.3 多阶段构建（进阶，减小镜像）

前端构建或编译型项目常用；纯 Python API 有时用 `slim` 就够。思路：

```dockerfile
# 阶段1：构建
FROM node:20 AS build
WORKDIR /web
COPY web/package*.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

# 阶段2：运行
FROM nginx:alpine
COPY --from=build /web/dist /usr/share/nginx/html
```

---

## 四、常用命令（带注释理解）

### 4.1 镜像

```bash
docker pull python:3.11-slim          # 从仓库拉取镜像
docker images                         # 列出本地镜像
docker build -t myapi:1.0 .           # 当前目录构建，打标签 myapi:1.0
docker rmi myapi:1.0                  # 删除镜像
docker tag myapi:1.0 myrepo/myapi:1.0 # 改名/加仓库前缀
docker push myrepo/myapi:1.0          # 推到仓库（需先 login）
```

### 4.2 容器

```bash
docker run -d --name myapi -p 8000:8000 myapi:1.0   # 后台运行并端口映射
docker ps                                           # 看正在运行的容器
docker ps -a                                        # 含已停止
docker logs -f myapi                                # 跟踪日志
docker stop myapi                                   # 停止
docker start myapi                                  # 再启动
docker restart myapi                                # 重启
docker exec -it myapi bash                          # 进入容器（没有 bash 就用 sh）
docker rm myapi                                     # 删除已停止容器
docker rm -f myapi                                  # 强删运行中容器
```

端口映射读法：`-p 宿主机端口:容器端口`  
例：`-p 8080:8000` → 浏览器访问本机 8080，转发到容器内 8000。

### 4.3 查看与清理

```bash
docker inspect myapi          # 超详细 JSON 配置
docker stats                  # CPU/内存实时
docker system df              # 占了多少磁盘
docker system prune           # 清理无用数据（慎用）
```

---

## 五、docker-compose：多容器一键起

一个 FastAPI + PostgreSQL 的常见骨架：

```yaml
# docker-compose.yml
services:  # 定义多个服务
  api:  # FastAPI 服务名
    build: .  # 用当前目录 Dockerfile 构建
    container_name: ecommerce_api  # 容器名
    ports:  # 端口映射
      - "8000:8000"  # 宿主机8000 -> 容器8000
    environment:  # 环境变量
      DATABASE_URL: postgresql+psycopg2://app:app@db:5432/appdb  # 注意主机名是 db
      APP_ENV: production  # 环境标记
    volumes:  # 开发时可挂源码；生产常不挂
      - ./app:/app/app  # 热更新示例（按需）
    depends_on:  # 启动顺序提示（不保证 db 已就绪）
      - db  # 依赖数据库服务
    restart: unless-stopped  # 异常退出自动重启

  db:  # 数据库服务
    image: postgres:16-alpine  # 官方镜像
    container_name: ecommerce_db  # 容器名
    environment:  # 官方镜像识别的变量
      POSTGRES_USER: app  # 用户
      POSTGRES_PASSWORD: app  # 密码
      POSTGRES_DB: appdb  # 库名
    ports:  # 可选：宿主机调试用
      - "5432:5432"  # 暴露数据库端口
    volumes:  # 持久化数据
      - pgdata:/var/lib/postgresql/data  # 命名卷
    restart: unless-stopped  # 自动重启

volumes:  # 声明命名卷
  pgdata:  # 给 db 用
```

常用命令：

```bash
docker compose up -d --build   # 构建并后台启动
docker compose ps              # 看服务状态
docker compose logs -f api     # 看 api 日志
docker compose exec api sh     # 进入 api 容器
docker compose down            # 停止并删除容器网络（默认不删命名卷）
docker compose down -v         # 连卷一起删（数据会没）
```

服务互访：在同一 compose 网络里，用 **服务名** 当主机名，例如 `db:5432`，不要写 `localhost`（localhost 是容器自己）。

---

## 六、卷、网络、环境变量

### 6.1 三种挂载

| 类型 | 写法直觉 | 用途 |
| --- | --- | --- |
| 命名卷 | `pgdata:/var/lib/postgresql/data` | 数据库持久化 |
| 绑定挂载 | `./app:/app/app` | 开发时改代码立即生效 |
| tmpfs | 内存盘 | 临时敏感文件 |

注意：Windows 路径绑定有时需确认 Docker Desktop 文件共享权限。

### 6.2 网络模式（够用版）

- compose 默认创建桥接网络，服务名 DNS 解析  
- `localhost` 在容器内 ≠ 宿主机；访问宿主机常用 `host.docker.internal`（Desktop）  

### 6.3 配置与密钥

推荐：

- 非机密：环境变量 / compose `environment`  
- 机密：Docker secrets / 外部密钥系统；至少用 `.env` 且 **不要打进镜像、不要提交 git**  

```bash
docker run --env-file .env -p 8000:8000 myapi:1.0
```

应用内用 Pydantic Settings 读环境变量（见 FastAPI 笔记）。

---

## 七、FastAPI 项目实战清单

### 7.1 推荐文件组合

```text
project/
  app/
  requirements.txt
  Dockerfile
  .dockerignore
  docker-compose.yml
  .env.example
```

### 7.2 健康检查（可选）

Dockerfile 或 compose 里可加健康检查，配合 `/health` 接口：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 5s
  retries: 3
```

（精简镜像若无 `curl`，可改用 wget 或专门健康检查工具。）

### 7.3 从开发到服务器的最短路径

1. 本地 `docker compose up --build` 跑通  
2. 打标签推仓库，或在服务器 `git pull` 后 compose 构建  
3. 前面加 Nginx 反代域名与 HTTPS  
4. `restart: unless-stopped` + 日志采集  

与课程部署文档的关系：`gunicorn + uvicorn worker`、systemd、Nginx 可以跑在「裸机」；Docker 则是把这些打包进容器。两者都要会，看团队规范。

### 7.4 对照命令速查

```text
构建: docker build -t name:tag .
运行: docker run -d -p 8000:8000 --name c name:tag
日志: docker logs -f c
进入: docker exec -it c sh
编排: docker compose up -d --build
停止编排: docker compose down
```

---

## 八、易错点、自测、练习

### 8.1 易错点

1. 容器内服务绑 `127.0.0.1`，宿主机访问不到。  
2. `-p` 写反成 `容器:宿主机`。  
3. compose 里数据库地址写成 `localhost`。  
4. 把 `.venv`、`.git`、大数据文件打进镜像。  
5. 用 `latest` 标签导致环境不可复现。  
6. 数据库没挂卷，`down` 后数据丢光。  
7. `depends_on` 当成「数据库已可连接」（其实只是容器启动了）。  
8. Windows 换行符 / 路径导致脚本异常。  
9. 容器时区、编码问题未处理。  
10. 以 root 跑一切、镜像乱来，安全无底线。  

### 8.2 自测

1. 镜像和容器差别？  
2. 为什么 Dockerfile 先复制 `requirements.txt`？  
3. `-p 8080:8000` 谁是宿主机端口？  
4. compose 中服务如何互访？  
5. 命名卷解决什么问题？  
6. `.dockerignore` 像什么？  

答案：模板 vs 实例；利用缓存；8080；服务名 DNS；数据持久化；`.gitignore`。

### 8.3 练习

1. 给任意 FastAPI 小项目写 Dockerfile 并成功 `run`。  
2. 用 compose 加一个 `redis` 或 `postgres`。  
3. 故意写错端口映射，观察现象再纠正。  
4. 给 API 加 `/health`，用 `curl` 从宿主机访问。  

---

## 九、一句话收束

> Docker 用镜像固化环境、用容器运行进程、用 compose 编排多服务；把端口、卷、环境变量和网络四个旋钮吃熟，FastAPI 项目就能稳定从本机搬到服务器。
