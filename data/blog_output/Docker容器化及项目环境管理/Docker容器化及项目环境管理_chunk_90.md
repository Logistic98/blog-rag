## 5. Docker搭建中间件服务
### 5.11 Docker-EMQX环境搭建
#### 5.11.1 拉取镜像并运行容器

```shell
$ docker pull emqx/emqx
$ docker run -d --name emqx -p 1883:1883 -p 8086:8086 -p 8883:8883 -p 8084:8084 -p 18083:18083 emqx/emqx
```
