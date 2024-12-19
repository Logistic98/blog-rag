## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
#### 3.2.6 解决Docker容器时区不正确的问题

[1] 修改已运行容器的时区

Step1：进入需要更改时区的容器

```shell
$ docker exec -it <容器> /bin/bash
```

Step2：将宿主机的时区链接到容器里

```shell
$ ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

Step3：退出并重启容器

```shell
$ exit
$ docker restart <容器>
```

[2] 在docker run命令中修改时区

运行容器时，加上挂载参数

```shell
$ docker run -d <容器> -v /etc/timezone:/etc/timezone -v /etc/localtime:/etc/localtime
```

或者通过-e TZ="Asia/Shanghai"设置时区：

```shell
$ docker run -d <容器> -e TZ="Asia/Shanghai"
```

[3] 在Dockerfile中修改时区

在Dockerfile中

```Dockerfile
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone
```

[4] 在Compose中修改时区

在docker-compose.yml文件中

```yml
volumes:
  - /etc/timezone:/etc/timezone
  - /etc/localtime:/etc/localtime
```
