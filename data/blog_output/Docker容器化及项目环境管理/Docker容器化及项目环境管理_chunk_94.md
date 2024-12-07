## 5. Docker搭建中间件服务
### 5.13 Docker-Milvus环境搭建
#### 5.13.1 拉取镜像并运行容器

官方文档里提供了一键脚本进行部署，[https://milvus.io/docs/install_standalone-docker.md](https://milvus.io/docs/install_standalone-docker.md)

```shell
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
$ ./standalone_embed.sh start
```

该脚本还提供了以下管理命令：

```shell
$ ./standalone_embed.sh start
$ ./standalone_embed.sh stop
$ ./standalone_embed.sh delete
$ ./standalone_embed.sh upgrade
```
