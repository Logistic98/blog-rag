## 3. Docker环境搭建及使用
### 3.9 使用Docker Buildx构建跨架构镜像
#### 3.9.2 构建跨架构镜像进行部署

大多数情况下，如果 Docker 版本是 19.03 或更高，Buildx 应该已经预装在 Docker 中了，可通过以下命令检查 Buildx 是否可用。

```shell
$ docker buildx version
```

之后，需要切换到带有Dockerfile的原始源码目录，通过Docker Buildx构建跨架构镜像，再用它进行部署。

```shell
$ docker buildx create --name mymultiarchbuilder --use
$ docker buildx build --platform linux/arm64 -t project-arm64:v1.0 . --load       // 构建跨架构镜像的命令
$ docker save -o project-v1.0-arm64.tar project-arm64:v1.0
$ docker load -i project-v1.0-arm64.tar
$ docker run -itd --name project -p 8081:80 project-arm64:v1.0 
$ docker update project --restart=always
```

注意：这种方式是直接使用Dockerfile构建的镜像，如果有那种首次使用时自动下载镜像的情况，需要一并在Dockerfile里将其放进去。
