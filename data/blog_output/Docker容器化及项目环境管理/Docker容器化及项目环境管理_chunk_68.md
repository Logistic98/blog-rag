## 5. Docker搭建中间件服务
### 5.4 Docker-MongoDB环境搭建
#### 5.4.1 拉取镜像并运行容器

这个mongodb未设置账号密码，仅限内网测试使用。

```shell
$ docker pull mongo:latest
$ mkdir -p /root/docker/mongodb/data
$ docker run -itd --name mongodb -v /root/docker/mongodb/data:/data/db -p 27017:27017 mongo:latest
```
