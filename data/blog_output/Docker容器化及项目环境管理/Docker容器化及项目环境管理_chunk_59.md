## 5. Docker搭建中间件服务
### 5.1 Docker-MySQL环境搭建
#### 5.1.2 创建数据库及用户

在本地使用Navicat工具使用root用户连接上该数据库，使用如下四条命令创建数据库及用户。

```shell
--创建新的数据库，并设置数据库编码
$ CREATE DATABASE 你的数据库名 DEFAULT CHARSET=utf8 DEFAULT COLLATE utf8_unicode_ci;

--创建新的用户
$ CREATE USER '你的用户名'@'你的服务器IP' IDENTIFIED BY '你的密码';

--把数据库的管理权限给予刚刚创建的MySQL用户
$ GRANT ALL PRIVILEGES ON *.* TO '你的用户名'@'%' IDENTIFIED BY '你的密码' WITH GRANT OPTION;

--刷新权限，使用设置生效
$ FLUSH PRIVILEGES;
```

注：如果连接数据库时出现`Access denied for user '用户名'@'某IP' (using password: YES)`问题，则是第三句授权出了问题，你的本地外网IP被拦截了，那个'%'代表的是访问IP不受限制。
