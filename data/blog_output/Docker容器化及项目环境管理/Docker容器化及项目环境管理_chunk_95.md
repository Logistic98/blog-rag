## 5. Docker搭建中间件服务
### 5.13 Docker-Milvus环境搭建
#### 5.13.2 Milvus可视化管理工具

可以安装开源的 Attu 工具进行可视化管理，可以在Linux上搭建网页端，也可以在Mac、Win上直接安装客户端。

- 项目地址：[https://github.com/zilliztech/attu](https://github.com/zilliztech/attu)

这里我是直接在 Mac 上安装了客户端，会提示“attu.app 已损坏，无法打开”，执行以下命令即可。

```shell
$ sudo xattr -rd com.apple.quarantine /Applications/attu.app
```

![Attu](https://image.eula.club/quantum/Attu.png)
