## 4. 搭建Harbor私有Docker镜像仓库
### 4.2 搭建Harbor镜像仓库
#### 4.2.1 搭建前的环境准备

搭建Harbor的服务器及基础环境如下：

| 项目           | 描述             |
| -------------- | ---------------- |
| 操作系统       | Debian 11 x86_64 |
| Docker         | 20.10.17         |
| Docker-compose | 1.29.2           |
| Harbor         | 2.7.0            |

另注：Harbor镜像仓库可以与Drone持续集成配合使用，项目部署后自动保存一份镜像到Harbor，关于Drone的搭建及使用见我的另一篇博客：[使用Gitea及Drone搭建轻量持续集成服务](https://www.eula.club/blogs/使用Gitea及Drone搭建轻量持续集成服务.html)
