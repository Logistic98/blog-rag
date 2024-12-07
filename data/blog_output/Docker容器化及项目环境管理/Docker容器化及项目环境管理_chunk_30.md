## 3. Docker环境搭建及使用
### 3.3 Docker Compose环境搭建与基本使用
#### 3.3.2 Docker Compose基本使用

首先要编写好docker-compose.yml文件，然后构建镜像、运行容器即可。

```shell
$ cd <docker-compose-path>  // 切换到docker-compose.yml文件所在的目录
$ docker-compose build      // 构建镜像
$ docker-compose up -d      // 运行容器
$ docker-compose stop       // 停止容器
```

注：如果不是默认的docker-compose.yml文件，需要使用 -f 参数手动指定。

```shell
$ docker-compose -f custom-docker-compose.yml up -d
```
