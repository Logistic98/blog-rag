## 4. 搭建Harbor私有Docker镜像仓库
### 4.3 使用Harbor镜像仓库
#### 4.3.1 修改Docker配置并登录

由于docker默认不允许使用非https方式推送和拉取镜像，所以需要修改docker配置。

```shell
$ vim /etc/docker/daemon.json
```

修改的内容如下：

```
{"insecure-registries": ["111.111.111.111:10010"]}
```

然后重载配置并重启docker。

```shell
$ systemctl daemon-reload
$ systemctl restart docker
```

之后就可以成功docker login了（用户名：admin，密码：your_harbor_admin_password）

```shell
$ docker login 111.111.111.111:10010
```

![docker-login登录成功](https://image.eula.club/quantum/docker-login登录成功.png)

注：如果没有修改docker配置，docker login时会报如下错误

```
Error response from daemon: Get "https://111.111.111.111:10010/v2/": http: server gave HTTP response to HTTPS client
```
