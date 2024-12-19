## 5. Docker搭建中间件服务
### 5.1 Docker-MySQL环境搭建
#### 5.1.1 拉取镜像创建容器

```shell
$ docker pull mysql:5.7
$ docker run -p 3306:3306 --name mysql \
-e TZ=Asia/Shanghai \
-v /root/docker/mysql/conf:/etc/mysql/conf.d \
-v /root/docker/mysql/logs:/var/log/mysql \
-v /root/docker/mysql/data:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=[password] \
-d mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
$ docker update mysql --restart=always
```

命令解释说明：

```
-p 3306:3306：将主机的3306端口映射到docker容器的3306端口。
--name mysql：运行服务名字
-e TZ=Asia/Shanghai：时区是使用了世界标准时间(UTC)。因为在中国使用，所以需要把时区改成东八区的。
-e MYSQL_ROOT_PASSWORD=[password]：初始化 root 用户的密码。
-d mysql:5.7 : 后台程序运行mysql5.7
--character-set-server=utf8mb4 ：设置字符集
--collation-server=utf8mb4_unicode_ci：设置校对集
```

说明：如果是挂载已有的其他服务器数据，可能会出现用户权限问题，如果网络是通的，建议使用Navicat的数据传输功能（工具——数据传输——配置源与目标链接——选择需要传输的数据表即可），数据传输速度很快。
