## 1. 项目环境管理
### 1.1 环境管理目标及实现
#### 1.1.1 环境管理实现

开发环境使用Docker进行部署，各组件之间使用Docker Network进行内部通信，将打包好的镜像放置到镜像仓库中，测试、演示、正式环境直接从镜像开始构建服务。

![环境管理实现](https://image.eula.club/quantum/环境管理实现.png)
