## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
#### 3.2.5 清理Docker占用的存储空间

[1] docker空间清理

```shell
$ docker system df                 # 类似于Linux上的df命令，用于查看Docker的磁盘使用情况
$ docker ps --size                 # 查看Docker容器占用的磁盘空间
$ docker builder prune             # 清理Docker镜像的构建缓存
$ docker builder prune -f          # 清理Docker镜像的构建缓存（自动确认而不需要提示）
$ docker system prune              # 可用于清理磁盘，删除关闭的容器、无用的数据卷和网络，以及无tag的镜像
$ docker system prune -a           # 清理得更加彻底，除了上述内容之外，还可以将没有容器使用Docker镜像都删掉。
```

[2] 查看并清空容器日志

在Linux上，Docker容器日志一般存放在`/var/lib/docker/containers/container_id/`下面， 以json.log结尾。

手动处理容器日志：

```shell
$ docker inspect --format='{{.LogPath}}' [CONTAINER ID/NAMES]       # 查看指定容器的日志
$ echo |sudo tee $(docker inspect --format='{{.LogPath}}' [CONTAINER ID/NAMES])  # 清空指定容器的日志
```

批量查找容器日志find_docker_log.sh：

```shell
#!/bin/sh

echo "======== docker containers logs file size ========"  

logs=$(find /var/lib/docker/containers/ -name *-json.log)  

for log in $logs  
        do  
             ls -lh $log   
        done  
```

批量清空容器日志 clear_docker_log.sh：

```shell
#!/bin/sh 

echo "======== start clean docker containers logs ========"  

logs=$(find /var/lib/docker/containers/ -name *-json.log)  

for log in $logs  
        do 
                echo "clean logs : $log"  
                cat /dev/null > $log  
        done  

echo "======== end clean docker containers logs ========"  
```

注：以上清理日志的方法治标不治本，可通过以下方式设置Docker容器日志大小治本。

方案一：设置一个容器服务的日志大小上限

设置一个容器服务的日志大小上限

```
--log-driver json-file  #日志驱动
--log-opt max-size=[0-9+][k|m|g] #文件的大小
--log-opt max-file=[0-9+] #文件数量
```

方案二：全局设置

编辑文件`/etc/docker/daemon.json`, 增加以下日志的配置：

```
"log-driver":"json-file",
"log-opts": {"max-size":"500m", "max-file":"3"}
```

解释说明：

- max-size=500m，意味着一个容器日志大小上限是500M，
- max-file=3，意味着一个容器有三个日志，分别是id+.json、id+1.json、id+2.json。

然后重启docker守护进程

```shell
$ systemctl daemon-reload
$ systemctl restart docker
```

注：设置的日志大小限制，只对新建的容器有效。
