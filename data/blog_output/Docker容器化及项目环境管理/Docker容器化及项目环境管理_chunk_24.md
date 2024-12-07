## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
#### 3.2.4 Docker常用命令

以下是Docker常用命令，需要熟练掌握。

| 命令              | 解释                             |
| ----------------- | -------------------------------- |
| docker run        | 运行一个容器                     |
| docker ps         | 列出运行中的容器                 |
| docker ps -a      | 列出所有容器，包括停止的容器     |
| docker images     | 列出本地镜像                     |
| docker pull       | 从远端仓库拉取镜像               |
| docker build      | 基于Dockerfile构建镜像           |
| docker exec       | 在运行中的容器中执行命令         |
| docker stop       | 停止一个或多个运行中的容器       |
| docker rm         | 删除一个或多个容器               |
| docker rmi        | 删除一个或多个本地镜像           |
| docker network ls | 列出所有网络                     |
| docker volume ls  | 列出所有卷                       |
| docker inspect    | 提供关于指定Docker对象的详细信息 |
| docker logs       | 查看容器的日志                   |
| docker cp         | 从容器复制文件到主机             |
| docker commit     | 创建一个新的镜像                 |

[1] 搜索及拉取docker镜像

```shell
$ docker search [NAME]              # 搜索docker镜像（搜索结果里OFFICIAL为OK的是官方镜像）
$ docker pull [IMAGE NAME]          # 拉取指定docker镜像（IMAGE NAME是搜索出来的指定镜像名）
```

[2] 查看docker容器实例和镜像

```shell
$ docker ps -a                      # 查看所有docker容器实例
$ docker ps                         # 查看所有正在运行的docker容器实例
$ docker images                     # 查看所有docker镜像
$ docker images [IMAGE NAME]        # 查看指定docker镜像（IMAGE NAME为镜像名）
```

[3] 开启停止docker容器实例和镜像

```shell
$ docker start [CONTAINER ID/NAMES]   # 开启指定docker容器实例
$ docker stop [CONTAINER ID/NAMES]    # 停止指定docker容器实例
$ docker restart [CONTAINER ID/NAMES] # 重启指定docker容器实例
$ docker start `docker ps -a -q`      # 批量启动所有的docker容器实例
$ docker stop `docker ps -a -q`       # 批量停止所有的docker容器实例
$ docker restart `docker ps -a -q`    # 批量重启所有的docker容器实例
```

注：可以使用docker pause 命令暂停容器运行。docker pause 命令挂起指定容器中的所有进程，docker stop 容器内主进程会在指定时间内被杀死。

```shell
$ docker pause [CONTAINER ID/NAMES]     # 暂停容器运行
$ docker unpause [CONTAINER ID/NAMES]   # 恢复容器运行
```

[4] 强制删除docker容器实例和镜像

```shell
$ docker rm -f [CONTAINER ID/NAMES]   # 强制删除指定docker容器实例（删除前需先停止实例）
$ docker rmi -f [CONTAINER ID/NAMES]  # 强制删除指定docker镜像（删除前需先停止实例）
$ docker rm -f `docker ps -a -q`      # 批量强制删除所有的docker容器实例（删除前需先停止实例）
$ docker rmi -f `docker images -q`    # 批量强制删除所有的docker镜像（删除前需先停止实例）
```

[5] 进入/退出docker容器内部

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/bash   # 进入指定docker容器内部
$ exit                                             # 从docker容器内部退出
```

注：如果遇到`OCI runtime exec failed: exec failed`问题，则使用如下命令进入

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/sh
```

[6] 查看docker运行日志

```shell
$ docker logs -f [CONTAINER ID/NAMES] --tail 100    # 查看指定条数的docker运行日志
$ docker logs --since 30m [CONTAINER ID/NAMES]      # 查看指定分钟内的docker运行日志   
```

[7] docker容器内部的文件上传和下载

```shell
$ docker cp /root/test.txt [CONTAINER ID/NAMES]:/root       # 上传文件
$ docker cp [CONTAINER ID/NAMES]:/root/test.txt /root       # 下载文件
```

[8] 让容器使用GPU环境

docker run 的时候加上 --gpus all 即可

```shell
--gpus all
```

[9] 在docker容器外执行容器内的命令

有时候我们想执行某个容器的某条命令，但又不想进入容器内，可通过如下命令示例实现：

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/bash -c 'cd /code && python test.py'
```

如果遇到`the input device is not a TTY`问题，去掉t即可，即：

```shell
$ docker exec -i [CONTAINER ID/NAMES] /bin/bash -c 'cd /code && python test.py'
```

注：可以通过这种方式在容器外拿到容器里的执行结果

![在docker容器外执行容器内的命令](https://image.eula.club/quantum/在docker容器外执行容器内的命令.png)

[10] docker的跨容器调用

需求情景：爬虫项目和定时任务项目分别在两个容器中部署的，想要在定时任务项目里编写脚本调用爬虫项目中的具体执行文件。

我们可以通过挂载`docker.sock`和`docker`命令行客户端实现用`docker exec`来间接调用。只需要在docker run的时候挂载如下路径即可：

```shell
-v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker
```

[11] 给docker镜像打Tag

```shell
$ docker tag [IMAGEID] [REPOSITORY]:[TAG]
```

[12] 给docker容器设置开机自启

```shell
$ docker update [CONTAINER ID/NAMES] --restart=always
```

[13] 显示docker容器占用的系统资源

```shell
$ docker stats               // stats命令默认会每隔1秒钟刷新一次输出的内容直到你按下ctrl + c
$ docker stats --no-stream   // 如果不想持续的监控容器使用资源的情况，可以通过 --no-stream 选项输出当前的状态
$ docker stats --no-stream [CONTAINER ID/NAMES]  // 只输出指定容器的
$ docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"  // 格式化输出结果，可以只输出部分指标项
```

另注：可使用 [ctop](https://github.com/bcicen/ctop) 工具监控docker容器占用的资源。

```shell
// Linux环境的通用安装
$ sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
$ sudo chmod +x /usr/local/bin/ctop
// ctop的基本使用
$ ctop
```

ctop工具的资源监控效果如下图所示：

![ctop](https://image.eula.club/quantum/ctop.png)

[14] 容器进程查看

```shell
$ docker ps -q | xargs docker inspect --format '{{.State.Pid}}, {{.Name}}' | grep "PID"  // 根据PID查docker名
$ docker top [CONTAINER ID/NAMES]	  // 列出容器中运行的进程
$ ps -ef   // 查看容器内进程（需要先进入容器内部）
```

[15] 查看容器内系统版本

```shell
$ cat /etc/*release     // 查看容器内系统版本（需要先进入容器内部）
```

[16] 无ENTRYPOINT方式启动

如果是直接执行的代码，写Dockerfile时就不需要加ENTRYPOINT了，然后用以下命令进入容器：

```shell
$ docker run -it --name [CONTAINER ID/NAMES] [IMAGE ID/NAMES] /bin/bash
```

如果要覆盖原先Dockerfile里的ENTRYPOINT配置，加个`--entrypoint /bin/bash`即可。

```shell
$ docker run -it --entrypoint /bin/bash --name [CONTAINER ID/NAMES] [IMAGE ID/NAMES]
```

[17] 查看指定容器的元数据

```shell
$ docker inspect [CONTAINER ID/NAMES]  // 查看指定容器的元数据
$ docker inspect [CONTAINER ID/NAMES] | grep -i Status -A 10  // 查看容器状态及退出原因
$ docker image inspect [IMAGE NAMES]:latest |grep -i version  // 查看指定latest镜像的版本号
```

[18] 设置开机自启与取消开机自启

```shell
$ docker update --restart=always [CONTAINER ID/NAMES]  // 设置开机自启
$ docker update --restart=no [CONTAINER ID/NAMES]      // 取消开机自启
```

[19] docker network相关命令

默认docker之间的网络不互通，如果需要其互相连接，则需要配置docker network。

```shell
$ docker network create [network_name]    // 创建网络
$ docker network ls                       // 查看已创建的网络列表
$ docker network inspect [network_name]   // 查看具体的网络详情
$ docker network connect [network_name] [CONTAINER ID/NAMES]      // 将容器加入网络，或者 docker run 时加 --network 进行指定
$ docker network disconnect [network_name] [CONTAINER ID/NAMES]   // 将容器移除网络
$ docker network rm [network_name]        // 删除具体的网络
```

[20] 查看容器与镜像的差异

```shell
$ docker diff [CONTAINER ID/NAMES]   // 显示容器与镜像的差异（修改后的文件）
```

[21] 根据容器id检索容器名

```shell
$ docker inspect -f '{{.Name}}' [CONTAINER ID] | sed 's/^\///'
```

[22] 清理Docker镜像构建缓存

```shell
$ docker builder prune
```

[23] 查看指定端口的Docker容器

```shell
$ docker ps --filter "publish=8000"       # 方式一
$ docker ps -a | grep "0.0.0.0:8000"      # 方式二
```
