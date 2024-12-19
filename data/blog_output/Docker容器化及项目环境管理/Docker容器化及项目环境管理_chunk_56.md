## 4. 搭建Harbor私有Docker镜像仓库
### 4.3 使用Harbor镜像仓库
#### 4.3.2 上传Docker镜像

这里我已经准备好了一个docker镜像（yoyo-web-image:latest）用来测试。

Step1：查看docker镜像并对其打tag

基本格式：`docker tag 镜像名:版本 your-ip:端口/项目名称/新的镜像名:版本`

```shell
$ docker tag yoyo-web-image:latest 111.111.111.111:10010/library/yoyo-web-image:v1.0
```

查看打好tag的docker镜像。

```shell
$ docker images
111.111.111.111:10010/library/yoyo-web-image   v1.0            d5b625cc399c   2 weeks ago     951MB
```

Step2：推送镜像到harbor仓库

基本格式：`docker push 修改的镜像名`

```shell
$ docker push 111.111.111.111:10010/library/yoyo-web-image:v1.0
```

![推送镜像到Harbor仓库](https://image.eula.club/quantum/推送镜像到Harbor仓库.png)

访问Harbor管理面板，点进去library项目，即可查看到刚刚上传的镜像，再点进去可查看详细信息。

![在Harbor查看推送成功的镜像](https://image.eula.club/quantum/在Harbor查看推送成功的镜像.png)
