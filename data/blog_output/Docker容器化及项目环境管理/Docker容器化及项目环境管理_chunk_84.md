## 5. Docker搭建中间件服务
### 5.9 Docker-Redis环境搭建
#### 5.9.1 拉取镜像并运行容器

方案一：不使用配置文件启动

```shell
$ docker pull redis:3.2.8
$ docker run --name redis -p 6379:6379 -d redis:3.2.8 --requirepass "mypassword" --appendonly yes
$ docker update redis --restart=always
```

注：--requirepass用来设置密码，--appendonly yes用来设置AOF持久化。

方案二：使用redis.conf配置文件启动

redis容器里没有redis.conf文件，可以从 [https://redis.io/docs/management/config](https://redis.io/docs/management/config) 地址下载对应版本的配置文件，挂载进去。

```shell
$ docker pull redis:3.2.8
$ cd /root/redis
$ wget https://raw.githubusercontent.com/redis/redis/3.2/redis.conf
$ chmod 777 redis.conf
$ vim /root/redis/redis.conf

修改以下配置项
# bind 127.0.0.1 # 这行要注释掉，解除本地连接限制
protected-mode no # 默认yes，如果设置为yes，则只允许在本机的回环连接，其他机器无法连接。
daemonize no # 默认no 为不守护进程模式，docker部署不需要改为yes，docker run -d本身就是后台启动，不然会冲突
requirepass mypassword # 设置密码
appendonly yes # 持久化

$ docker run --name redis \
-p 6379:6379 \
-v /root/redis/redis.conf:/etc/redis/redis.conf \
-v /root/redis/data:/data \
-d redis:3.2.8 redis-server
$ docker update redis --restart=always
```
