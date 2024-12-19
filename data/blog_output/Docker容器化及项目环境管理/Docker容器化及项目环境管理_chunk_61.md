## 5. Docker搭建中间件服务
### 5.2 Docker-Nginx环境搭建
#### 5.2.2 修改Nginx配置文件

[1] 每次都进入到nginx容器内部修改--适用于临时修改情况

Step1：进入到nginx容器内部

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/bash
```

命令解释说明：

```
- exec 命令代表附着到运行着的容器内部
- -it 是 -i 与 -t两个参数合并写法，-i -t 标志着为我们指定的容器创建了TTY并捕捉了STDIN
- [CONTAINER ID/NAMES] 是我们要进入的容器ID（可以省略后面的部分，能唯一区分即可）或名字
- /bin/bash 指定了执行命令的shell
```

进入到nginx容器内部后，我们可以`cd /etc/nginx`，可以看到相关的nginx配置文件都在`/etc/nginx`目录下。而nginx容器内的默认首页html文件目录为`/usr/share/nginx/html`，日志文件位于`/var/log/nginx`。执行`exit`命令可以从容器内部退出。

[2] 将nginx容器内部配置文件挂载到主机--适用于频繁修改情况

Step1：创建挂载目录

这里我为了跟mysql的挂载目录保持一致，也使用了自己创建的`/root/docker`目录（一般放在`/mnt`目录，这个是Linux专门的挂载目录）

```shell
$ cd /root/docker
$ mkdir -p ./nginx/{conf,html,logs}
```

Step2：将容器内的`nginx.conf`与`default.conf`文件分别拷贝到主机`/root/docker/nginx`与`/root/docker/nginx/conf`目录下

```shell
$ cd /root/docker/nginx
$ docker cp [CONTAINER ID/NAMES]:/etc/nginx/nginx.conf ./ 
$ docker cp [CONTAINER ID/NAMES]:/etc/nginx/conf.d/default.conf ./conf/
```

命令解释说明：

```
- [CONTAINER ID/NAMES] 是我们要进入的容器ID（可以省略后面的部分，能唯一区分即可）或名字
- /etc/nginx/nginx.conf 是容器内部nginx.conf的路径
```

Step3：重新创建容器实例

先停止、删除原有的容器实例

```shell
$ docker stop [CONTAINER ID/NAMES]              # 停止指定docker容器实例
$ docker rm -f [CONTAINER ID/NAMES]             # 强制删除指定docker容器实例（删除前需先停止实例）
```

再重新创建新的容器实例

```shell
$ docker run -d --name nginx -p 9999:80 -v /root/docker/nginx/nginx.conf:/etc/nginx/nginx.conf -v /root/docker/nginx/logs:/var/log/nginx -v /root/docker/nginx/html:/usr/share/nginx/html -v /root/docker/nginx/conf:/etc/nginx/conf.d --privileged=true [image-id]
```

命令解释说明：

```
-v 挂载目录，表示将主机目录与容器目录之间进行共享
--privileged=true 容器内部对挂载的目录拥有读写等特权
```

Step4：设置开机自启

```shell
$ docker update nginx --restart=always
```
