## 4. 搭建Harbor私有Docker镜像仓库
### 4.2 搭建Harbor镜像仓库
#### 4.2.3 安装并启动Harbor

Step1：Harbor安装环境预处理

```shell
$ ./prepare
```

![Harbor安装环境预处理](https://image.eula.club/quantum/Harbor安装环境预处理.png)

Step2：安装并启动Harbor

```shell
$ ./install.sh 
```

注：安装Harbor会给构建9个容器，其中容易重名的有nginx、redis，如果之前搭建了的话需要将旧容器重命名一下，否则会出错。

![安装并启动Harbor](https://image.eula.club/quantum/安装并启动Harbor.png)
