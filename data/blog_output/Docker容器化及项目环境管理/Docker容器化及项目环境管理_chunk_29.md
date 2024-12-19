## 3. Docker环境搭建及使用
### 3.3 Docker Compose环境搭建与基本使用
#### 3.3.1 Docker Compose环境搭建

Debian11系统：

```shell
// 下载安装docker-compose，最新版见：https://github.com/docker/compose/releases
$ sudo curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose       
// 赋予docker-compose执行权限
$ sudo chmod +x /usr/local/bin/docker-compose
// 查看docker-compose版本号，验证是否安装成功
$ docker-compose --version
```

![docker-compose](https://image.eula.club/quantum/docker-compose.Png)

CentOS7系统：

```shell
$ sudo curl -L https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
```
