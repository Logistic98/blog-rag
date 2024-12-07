## 4. 搭建Harbor私有Docker镜像仓库
### 4.3 使用Harbor镜像仓库
#### 4.3.3 拉取Docker镜像

这里我换了一台服务器，拉取刚刚上传的docker镜像，在这台服务器上，仍要按照4.1节修改一下docker配置并登录。

在镜像详细信息界面，可以获取到镜像拉取命令。

![获取镜像拉取命令](https://image.eula.club/quantum/获取镜像拉取命令.png)

docker login之后，将镜像拉取命令复制到终端即可。

![从Harbor仓库拉取镜像](https://image.eula.club/quantum/从Harbor仓库拉取镜像.png)
