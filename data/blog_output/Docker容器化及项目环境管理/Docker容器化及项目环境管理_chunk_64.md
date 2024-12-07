## 5. Docker搭建中间件服务
### 5.3 Docker-Oracle环境搭建
#### 5.3.1 拉取镜像并运行容器

```shell
$ docker pull registry.cn-hangzhou.aliyuncs.com/helowin/oracle_11g 
$ docker run -d -p 1521:1521 --name oracle11g registry.cn-hangzhou.aliyuncs.com/helowin/oracle_11g
$ docker update oracle11g --restart=always
```
