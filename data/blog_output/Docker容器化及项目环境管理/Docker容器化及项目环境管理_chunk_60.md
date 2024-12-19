## 5. Docker搭建中间件服务
### 5.2 Docker-Nginx环境搭建
#### 5.2.1 拉取镜像创建容器

```shell
$ docker pull nginx
$ docker run -d --name nginx -p 9999:80 nginx:latest
```
