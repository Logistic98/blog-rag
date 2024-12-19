## 3. Docker环境搭建及使用
### 3.1 Docker简介
#### 3.1.4 Docker与Docker Compose的区别

Docker是一个供开发和运维人员开发，测试，部署和运行应用的容器平台。这种用linux container部署应用的方式叫容器化。

Docker Compose是一个用于运行和管理多个容器化应用的工具。

我们可以列出下列几项来进行二者对比：

- docker是自动化构建镜像，并启动镜像。 docker compose是自动化编排容器。

- docker是基于Dockerfile得到images，启动的时候是一个单独的container。

- docker-compose是基于docker-compose.yml，通常启动的时候是一个服务，这个服务通常由多个container共同组成，并且端口，配置等由docker-compose定义好。

- 两者都需要安装，但是要使用docker-compose，必须已经安装docker。
