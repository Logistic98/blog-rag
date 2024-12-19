## 3. Docker环境搭建及使用
### 3.1 Docker简介
#### 3.1.2 Docker的架构

Docker 其实指代的是用于开发，部署，运行应用的一个平台。平常中说的 Docker 准确来说是 Docker Engine。Docker Engine 是一个 C/S 架构的应用。其中主要的组件有：

- Docker Server：长时间运行在后台的程序，就是熟悉的 daemon 进程.
- Docker Client：命令行接口的客户端。
- REST API：用于和 daemon 进程的交互。

![Docker的架构](https://image.eula.club/quantum/Docker的架构.png)

我们通过给 Docker Client 下发各种指令，然后 Client 通过 Docker daemon 提供的 REST API 接口进行交互，来让 daemon 处理编译，运行，部署容器的繁重工作。 大多数情况下， Docker Client 和 Docker Daemon 运行在同一个系统下，但有时也可以使用 Docker Client 来连接远程的 Docker Daemon 进程，也就是远程的 Server 端。
