docker pull <image:tag>
介绍：从远端 Registry 拉取指定版本，保持环境一致。
示例：docker pull nginx:1.25
应用：部署前锁定 tag，结合 docker history 回看镜像层级，确认是否包含定制依赖。

docker images
介绍：列出本地镜像及大小、创建时间。
示例：docker images --filter reference="project-*"
应用：定期对比团队基线镜像，避免“只在我电脑能跑”的情况。

docker rmi <image>
介绍：删除不再需要的镜像释放磁盘。
示例：docker rmi project/web:old
应用：配合 docker image prune 清掉 dangling 层，解决 runner 空间不足。

docker tag
介绍：给现有镜像添加新标签，便于分发。
示例：docker tag api:v1 registry.company.com/prod/api:1.0
应用：构建后立刻打版本标签，再 push；与 docker push 形成 CI 一体化流水线。
docker history
介绍：查看镜像构成的每一层命令。
示例：docker history api:v1
应用：排查镜像体积异常、敏感文件是否被 COPY 进镜像。

docker save / docker load
介绍：镜像离线导入导出。
示例：docker save -o api.tar api:v1；docker load -i api.tar
应用：在无法直连互联网的内网环境传递镜像

docker run --name <name> -d <image>
介绍：创建并后台启动容器，可自定义名称、端口、卷等参数。
示例：docker run --name web -d -p 8080:80 nginx:1.25
应用：CI 中启模拟依赖服务；搭配 --rm 做一次性任务。

docker ps
介绍：查看运行中容器；-a 查看全部。
示例：docker ps --format '{{.Names}}\t{{.Status}}'
应用：结合 compose ps 对齐服务状态，快速定位异常实例。

docker stop / docker start
介绍：优雅停止或重新启动容器。
示例：docker stop web && docker start web
应用：发布窗口先 stop、更新卷后 start，保障数据一致。

docker exec -it <container> sh
介绍：进入容器执行命令。
示例：docker exec -it web sh
应用：排查运行时配置、临时修改参数并记录成 Dockerfile 变更。

docker logs -f <container>
介绍：流式查看容器日志；-t 补时间戳。
示例：docker logs -ft web | grep ERROR
应用：上线初期重点监控；与 docker events 结合形成实时告警。

docker volume ls
介绍：查看 Docker 管理的卷，适用于生产。
示例：docker volume ls --filter name=db
应用：结合 docker volume create dbdata 为数据库分配独立磁盘。

docker volume create <vol>
介绍：创建命名卷。
示例：docker volume create --label env=prod pgdata
应用：在 compose 中引用 pgdata，实现数据库升级不丢表。

docker run -v <vol>:/path/in/container
介绍：挂载命名卷到容器路径。
示例：docker run -v pgdata:/var/lib/postgresql/data postgres:15
应用：灾备演练时直接切换容器而数据不动。

docker run -v $(pwd):/app
介绍：绑定宿主目录，常用于开发热更新。
示例：docker run --rm -it -v $(pwd):/app node:20 npm test
应用：前端项目直接利用主机代码，同时与 VSCode 共享文件。

docker network ls
介绍：列出已有网络类型（bridge/host/none）。
示例：docker network ls --filter driver=bridge
应用：确认多服务是否共享同一自定义网络。

docker network create <net>
介绍：创建自定义网络，支持子网、网关配置。
示例：docker network create --subnet 172.30.0.0/16 app-net
应用：把应用与数据库放在隔离段，减少端口暴露。

docker network connect <net> <container>
介绍：将容器加入网络。
示例：docker network connect app-net web
应用：热修复时把调试容器加入生产网段，观测真实流量。

docker run -p 8080:80 <image> / docker port <container>
介绍：端口映射与查询。
示例：docker run -p 127.0.0.1:8080:80 nginx
应用：内网服务通过端口绑定到指定网卡，减少攻击面。

docker build -t <repo:tag> .
介绍：基于 Dockerfile 构建镜像。
示例：docker build -t api:v1 .
应用：结合多阶段 Dockerfile，降低镜像体积。

Dockerfile 核心指令
FROM：选择基础镜像，示例 FROM alpine:3.19。
WORKDIR：设置工作目录，例如 WORKDIR /app。
COPY：复制代码；配合 .dockerignore 杜绝无关文件。
RUN：执行构建命令，例 RUN npm ci。
EXPOSE：声明暴露端口，如 EXPOSE 8080。
CMD：容器启动命令，例 CMD ["npm","start"]。

docker image prune / docker builder prune
介绍：清理构建缓存与悬空层。
示例：docker builder prune -f
应用：CI 每晚清理，避免缓存膨胀。

docker login
介绍：登录目标 Registry。
示例：docker login registry.company.com
应用：写入 CI/CD Credential Helper，避免明文密码。

docker tag image registry/repo:tag
介绍：重命名镜像为 Registry 路径。
示例：docker tag api:v1 registry/api:v1
应用：统一命名规范，配合镜像签名。

docker push registry/repo:tag
介绍：推送镜像到远端仓库。
示例：docker push registry/api:v1
应用：发布流程的“制品”阶段；结合 cosign 做签名。

docker pull <registry>/<repo>:<tag>
介绍：从仓库拉指定版本。
示例：docker pull registry/api:v1
应用：生产节点仅允许从私有仓库拉取，控制镜像来源。

docker compose up -d
介绍：根据 compose.yaml 创建并启动所有服务。
示例：docker compose up -d web db redis
应用：一键构建本地多容器环境；-d 让服务后台跑。

docker compose down
介绍：停止并移除容器、网络。
示例：docker compose down --volumes
应用：清理测试环境，防止网络残留。

docker compose ps
介绍：查看 compose 管理的服务状态。
示例：docker compose ps --services
应用：快速核对依赖都已就绪。

docker compose logs -f
介绍：聚合日志，支持实时跟踪。
示例：docker compose logs -f web
应用：定位跨服务调用链。

docker compose exec <svc> sh
介绍：进入指定服务容器。
示例：docker compose exec db psql -U postgres
应用：调试数据库、缓存等依赖。

docker rm -f $(docker ps -aq)
介绍：强制删除所有容器，危险操作需确认。
示例：docker rm -f $(docker ps -aq)
应用：CI runner 或演示服务器快速归零。

docker system prune -af --volumes
介绍：删除未使用的容器、镜像、网络和卷。
示例：docker system prune -af --volumes
应用：定期清理，避免磁盘爆满。

docker stats
介绍：实时资源使用统计。
示例：docker stats --no-stream
应用：配合 docker events 做异常监控。

docker system df
介绍：显示磁盘占用。
示例：docker system df -v
应用：找到最大镜像、卷，制定清理策略。

docker events
介绍：订阅 Docker 守护进程事件。
示例：docker events --filter type=container
应用：构建实时审计；接入 ELK。

docker inspect
介绍：输出容器或镜像的全部元数据。
示例：docker inspect web
应用：调试网络、卷挂载配置。

docker top
介绍：查看容器内进程列表。
示例：docker top web
应用：排查僵尸进程。

docker --version
介绍：输出 Docker 客户端版本。
示例：docker --version
应用：记录问题时附带环境信息。
