## 3. Docker环境搭建及使用
### 3.7 正式环境的前后端分离项目部署
#### 3.7.1 准备中间件及数据库环境

建议新建个docker network，将这些容器加到同一个网络环境里面，这样可以不对外暴露一些不必要的数据库及中间件环境，更加安全。

```shell
$ docker network create yoyo

$ docker run -itd --name yoyo_mysql -h yoyo_mysql --network yoyo -p 3306:3306 \
-e TZ=Asia/Shanghai \
-v /root/docker/mysql/conf:/etc/mysql/conf.d \
-v /root/docker/mysql/logs:/var/log/mysql \
-v /root/docker/mysql/data:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=[password] \
mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
$ docker update yoyo_mysql --restart=always

$ docker run -itd --name yoyo_redis -h yoyo_redis --network yoyo -p 6379:6379 redis:3.2.8 --requirepass "mypassword"
$ docker update yoyo_redis --restart=always

$ docker run -itd --name yoyo_es -h yoyo_es --network yoyo -p 9200:9200 \
-e "discovery.type=single-node" \
-e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
elasticsearch:7.16.2
$ docker update yoyo_es --restart=always

$ docker run -itd --name yoyo_emqx -h yoyo_emqx --network yoyo -p 1883:1883 -p 18083:18083 emqx/emqx
$ docker update yoyo_emqx --restart=always
```

注：可使用 `docker network ls` 命令查看已创建的网络，创建容器时需要使用--network 指定网络，建议用 -h 指定 hostname，除 emqx 的1883端口外，其他服务可不使用 -p 对外映射端口号，我这里为了调试方便，仍然把不必要的端口暴露出来了。
