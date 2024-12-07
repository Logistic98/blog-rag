## 3. Docker环境搭建及使用
### 3.4 Docker官方源国内被墙问题
#### 3.4.2 Docker更换镜像源地址

缘由：在Dockerfile创建镜像拉取基础镜像时遇到了`Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)`报错，原因是连不上官方的源，可修改配置换源解决。

Docker安装后默认没有`daemon.json`这个配置文件，需要进行手动创建，配置文件的默认路径：`/etc/docker/daemon.json`，权限为644，内容如下：

```json
{
 "registry-mirrors":[
    "https://docker.eula.club"
 ],
 "runtimes": {
     "nvidia": {
         "path": "/usr/bin/nvidia-container-runtime",
         "runtimeArgs": []
     }
 }
} 
```

注：这里配置的是通过Cloudfare代理Docker镜像库的地址，也可从网上自行搜寻可用的镜像地址。

修改后需要重新加载配置，然后重启docker服务。

```shell
$ sudo systemctl daemon-reload
$ systemctl restart docker.service
```

注：如果不想重启 Docker 守护进程，可以通过如下命令重新加载 Docker 守护进程配置。

```shell
$ sudo kill -SIGHUP $(pidof dockerd)
```

修改完成之后，可通过如下命令查看是否生效，生效了的话会打印出刚配置出的镜像地址。

```shell
$ docker info
```
