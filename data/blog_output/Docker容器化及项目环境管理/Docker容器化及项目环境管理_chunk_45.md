## 3. Docker环境搭建及使用
### 3.8 将已有镜像容器部署到其他服务器
#### 3.8.2 具体操作步骤

Step1：将容器保存成镜像（如果已有请省略）

```shell
$ docker ps -a
$ docker commit -a "eula" -m "commit uptime-kuma" 1c786853ea40 eula/uptime-kuma:v1.0
$ docker images
```

说明：-a后面的是提交用户的用户名，-m后面的是提交信息，1c786853ea40是容器id，最后是镜像名及tag，打包出来的镜像如下：

```
REPOSITORY                                          TAG            IMAGE ID       CREATED              SIZE
eula/uptime-kuma                                    v1.0           b217262a8fe7   About a minute ago   323MB
```

Step2：将镜像打包并压缩

```shell
$ docker save -o eula-uptime-kuma-v1.0.tar eula/uptime-kuma:v1.0
$ tar -zcvf eula-uptime-kuma-v1.0.tar.gz eula-uptime-kuma-v1.0.tar 
$ rm -f eula-uptime-kuma-v1.0.tar
```

Step3：将文件传输到目标服务器

```shell
$ scp -P port /root/eula-uptime-kuma-v1.0.tar.gz root@ip:/root/eula-uptime-kuma-v1.0.tar.gz
```

Step4：解压并载入镜像

```shell
$ tar -zxvf eula-uptime-kuma-v1.0.tar.gz
$ docker load -i eula-uptime-kuma-v1.0.tar
$ docker images
$ rm -f eula-uptime-kuma-v1.0.tar
```

载入出来的镜像如下：

```
REPOSITORY                                      TAG             IMAGE ID        CREATED               SIZE
eula/uptime-kuma                                v1.0            b217262a8fe7    About an hour ago     323MB
```

Step5：运行镜像创建容器

```shell
$ docker run -d --restart=always -p 3001:3001 --name uptime-kuma eula/uptime-kuma:v1.0
$ docker ps
```
