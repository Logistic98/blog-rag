## 5. Docker搭建中间件服务
### 5.7 Docker-RabbitMQ环境搭建
#### 5.7.1 拉取镜像并运行容器

```shell
$ docker pull rabbitmq:3.8-management
$ docker run --name rabbitmq -d -p 15672:15672 -p 5672:5672 rabbitmq:3.8-management
```

注：默认RabbitMQ镜像是不带web端管理插件的，所以指定了镜像tag为3.8-management，表示下载包含web管理插件版本镜像。
