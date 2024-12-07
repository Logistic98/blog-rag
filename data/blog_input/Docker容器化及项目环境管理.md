---
title: Docker容器化及项目环境管理
comments: true
toc: true
date: 2022-03-26 13:22:24
categories: 部署运维
tags:
- Docker
- Docker-Compose
- Dockerfile
- Harbor
- 容器化
- 项目环境管理
- 私有镜像仓库
pic:
---

## 1. 项目环境管理

平时在开发项目的过程中，常常因为开发环境、测试环境、演示环境、正式环境等各种环境的存在且不同从而影响开发进度。开发系统时，项目环境管理的重要性就凸显出来了。通过下面几个实例来了解一下项目环境管理的重要性。

-  开发人员在开发环境开发好了功能接口，并在开发环境中自测无问题，直接提交到测试环境，测试人员也测试无问题，提交到了正式运行环境，但是偏偏就在正式运行环境报了错，最后排查是正式环境的JDK版本和开发、测试环境的JDK版本不一致，导致代码出错。
- 开发人员在开发环境中登录测试均无问题，但是测试人员在测试环境中无法登录，最后排查是测试环境的Nginx内部转发出了问题，因为开发环境和测试环境均不是同一个部署，所以部署方式不同，就可能会造成不同的结果。
- 一个开发完成很久的项目，突然需要给新的客户进行演示，且时间要求很紧张，但是之前的开发环境和测试环境均被收回，那么找人再一步一步安装演示环境就很浪费时间。
- 客户发现正式环境的数据有部分乱码问题，但是开发人员反复从开发环境寻找问题（因客户是隐私内网部署系统），均未找到问题所在，最后客户那边自查发现是服务器系统编码有问题，虽然客户自查出来了，但是这样的效率是很低的。

从上面几个开发过程中我真实遇到的坑不难看出，项目环境管理势在必行。

### 1.1 环境管理目标及实现

环境管理目标：易部署、易维护、易伸缩、易交接、稳定运行

#### 1.1.1 环境管理实现

开发环境使用Docker进行部署，各组件之间使用Docker Network进行内部通信，将打包好的镜像放置到镜像仓库中，测试、演示、正式环境直接从镜像开始构建服务。

![环境管理实现](https://image.eula.club/quantum/环境管理实现.png)

#### 1.1.2 网络与映射

将Docker与宿主机的网络进行映射。

<img src="https://image.eula.club/quantum/网络与映射.png" alt="网络与映射" style="zoom:120%;" />

#### 1.1.3 持久化存储

宿主机存储内容：业务相关数据、业务相关配置、环境相关配置

容器存储内容：业务无关数据、业务无关配置、环境无关配置

<img src="https://image.eula.club/quantum/持久化存储.png" alt="持久化存储" style="zoom:120%;" />

### 1.2 人员权限与责任

开发、测试、演示、正式环境的人员权限及责任如下表所示：

| **环境名称** | **服务器准备** | **搭建角色** | **测试角色** | **运维角色** | **访问权限**   |
| ------------ | -------------- | ------------ | ------------ | ------------ | -------------- |
| 开发环境     | 运维人员       | 开发人员     | 开发人员     | 开发人员     | 开发人员       |
| 测试环境     | 运维人员       | 测试人员     | 测试人员     | 测试人员     | 测试人员       |
| 演示环境     | 运维人员       | 开发人员     | 测试人员     | 开发人员     | 开发人员、客户 |
| 正式环境     | 运维人员       | 运维人员     | 测试人员     | 运维人员     | 客户           |

## 2. Nginx配置及项目发布

### 2.1 正向代理与反向代理

#### 2.1.1 正向代理概述

在大多数情况下，我们说的代理服务器指的是最普通的代理，即正向代理。这类代理位于用户之前，在用户与其访问的网页服务器之间充当中介。这就是说用户的请求要通过正向代理后才能抵达网页。从互联网检索数据后，这些数据就会被发送到代理服务器并将其重定向后返回请求者。从互联网服务器的角度来看，这个请求是有代理服务器、而不是用户发送的。正向代理还可以缓存信息并将信息用于处理今后的请求。

由于正向代理可以看做访问和控制点，因此它可以提高专用网络用户的安全性，调节流量并通过隐藏原始 IP 地址而保持用户的匿名状态。

个人用户或企业出于各种原因使用正向代理：

- 访问受限地理位置。正向代理服务器在访问受地理限制的内容时非常方便。用户浏览互联网时，他们能浏览的内容通常由自己所在的地理位置来决定。使用正向代理时，用户可以访问定位给其他国家/地区的各种内容。
- 确保匿名性。正向代理服务器可以用作额外的安全保护层，可以通过使用自己的 IP 地址来隐藏网页服务器的真实IP 地址。这就是使用正向代理服务器来确保更高级别的匿名性和安全性的原因。
- 网络抓取。代理最常见的用途是网络抓取。公司通常采集数据来帮助改进营销、定价和其他业务策略。

#### 2.2.2 反向代理概述

与代表客户端的正向代理不同，反向代理服务器位于后端服务器之前，将客户端请求转发至这些服务器。反向代理通常用于提高防护、速度和可靠度。反向代理从客户端获取请求，将请求传递到其他服务器，然后将其转发回相关客户端，使它看起来像是初始代理服务器在处理请求。这类代理可以确保用户不会直接访问原始服务器，因此可为这类网页服务器提供匿名性。

尽管对普通消费者和普通人不会特别有用，但反向代理服务器非常适合服务提供商和每天访问量大的网站。这些代理可以保护网页服务器，增强网站性能并帮助避免过载。反向代理也可用于负载平衡、缓存和 SSL 加密。

网站和服务提供商可能出于各种原因使用反向代理，部分用途如下：

- 负载均衡。高流量的网站有时可能需要反向代理服务器来处理传入流量。一个热门站点不会自行处理流量，而可能在多个后端服务器之间分配流量，从而提高容量以处理大量请求。如果其中一台服务器过载并出现故障，可以将流量重定向至其它在线服务器，以确保网页正常运行。网站工程师甚至可以添加更多后端服务器到此负载均衡器，以增加容量，满足不断提高的性能要求。
- 缓存。反向代理可以缓存经常请求的数据。需要存储大量图片和视频的企业也可以通过缓存这些内容，降低网站服务器的负载来提高网站性能。 
- 匿名信和安全性。由于反向代理拦截所有传入请求，它们会为后端服务器带来更高层级的保护。它可以阻止来自特定 IP 地址的可疑流量，从而有助于防止恶意访问者滥用网页服务器。

#### 2.2.3 正向代理与反向代理的区别

正向代理和反向代理之间的关键区别在于，前者由客户端使用，例如专用网络内的用户；而后者由互联网服务器使用。正向代理确保网站绝不与用户直接通信，而反向代理确保用户不会与后端服务器直接通信。

![正向代理与反向代理](https://image.eula.club/quantum/正向代理与反向代理.png)

### 2.2 Nginx配置服务负载均衡

#### 2.2.1 Nginx负载均衡方式

**[1] 轮询**

轮询方式是Nginx负载默认的方式，所有请求都按照时间顺序分配到不同的服务上，如果服务挂掉了，可以自动剔除。

```ini
upstream  nginx_balance {
        server xxx.xxx.xxx.xxx:1701;
        server xxx.xxx.xxx.xxx:1702;
}
```

**[2] 权重**

指定每个服务的权重比例，weight和访问比率成正比，通常用于后端服务机器性能不统一，将性能好的分配权重高来发挥服务器最大性能，如下配置后1702服务的访问频率会是1701服务的2倍。

```ini
upstream nginx_balance {
        server xxx.xxx.xxx.xxx:1701 weight=1;
        server xxx.xxx.xxx.xxx:1702 weight=2;
}
```

**[3] iphash**

每个请求都根据访问ip的hash结果分配，经过这样的处理，每个访客固定访问一个后端服务。

```ini
upstream nginx_balance {
			  ip_hash;
        server xxx.xxx.xxx.xxx:1701 weight=1;
        server xxx.xxx.xxx.xxx:1702 weight=2;
}
```

注意：配置之后，再访问主服务时，当前IP地址固定访问其中的一个地址，不会再发生变更了，ip_hash可以和weight配合使用。

**[4] 最少连接**

将请求分配到连接数最少的服务上

```ini
upstream nginx_balance {
			  least_conn;
        server xxx.xxx.xxx.xxx:1701 weight=1;
        server xxx.xxx.xxx.xxx:1702 weight=2;
}
```

#### 2.2.2 Nginx剔除失效节点

**[1] 失效节点的自动剔除**

在Nginx中实现负载均衡并自动剔除挂掉的服务器，可以通过配置`upstream`块并启用`fail_timeout`和`max_fails`来实现。这样，当某台服务器无法响应时，Nginx会自动停止向其发送请求。

```ini
http {
    upstream backend {
        server server1.example.com max_fails=1 fail_timeout=10s;
        server server2.example.com max_fails=1 fail_timeout=10s;
        server server3.example.com max_fails=1 fail_timeout=10s;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

含义解释：

- `max_fails=1`：表示在`fail_timeout`时间内最多允许失败1次。如果超过这个次数，Nginx会将该服务器标记为“不可用”，停止将请求转发给它。
- `fail_timeout=10s`：指定在失败后暂停多长时间，重新尝试将请求发给这台服务器。服务器被标记为不可用，Nginx也会每10秒重新尝试连接该服务器，查看是否恢复正常。

**[2] 自动选用有效节点**

proxy_next_upstream 配置的错误状态码或超时等条件触发时，Nginx会跳转到下一个健康的节点提供服务。

```ini
    # 添加proxy_next_upstream指令，实现失败时的自动跳转
    proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
```

#### 2.2.3 Nginx负载均衡实例

需求情景：有多台GPU服务器，分别部署了多个大模型服务，现在想要提高大模型服务的并发量，可以使用Nginx负载均衡来实现。

假设有3个服务，分别是1701、1702、1703端口，现在想要将其使用Nginx进行负载均衡，统一用1700端口来访问。

```
.
├── Dockerfile
├── nginx.conf
├── nginx_balance.conf
├── proxy.conf
└── build.sh
```

Dockerfile

```Dockerfile
# 设置基础镜像
FROM nginx

# 放置nginx配置
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx_balance.conf /etc/nginx/conf.d/nginx_balance.conf
COPY proxy.conf /etc/nginx
```

nginx.conf

```ini
user  root;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
```

nginx_balance.conf

```ini
upstream nginx_balance {
        server xxx.xxx.xxx.xxx:1701 weight=1 max_fails=1 fail_timeout=10s;
        server xxx.xxx.xxx.xxx:1702 weight=1 max_fails=1 fail_timeout=10s;
        server xxx.xxx.xxx.xxx:1703 weight=1 max_fails=1 fail_timeout=10s;
}
server {
    listen       1700;
    server_name  127.0.0.1;
    location ~* ^(/) {
        gzip on;
        gzip_vary on;
	      gzip_min_length 1k;
	      gzip_buffers 16 16k;
        gzip_http_version 1.1;
        gzip_comp_level 9;
        gzip_types text/plain application/javascript application/x-javascript text/css text/xml text/javascript application/json;
        proxy_pass http://nginx_balance;
        client_max_body_size    48m;
        # 添加proxy_next_upstream指令，实现失败时的自动跳转
        proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
        include proxy.conf;
    }
}
```

proxy.conf

```ini
proxy_connect_timeout 900s;
proxy_send_timeout 900;
proxy_read_timeout 900;
proxy_buffer_size 32k;
proxy_buffers 4 64k;
proxy_busy_buffers_size 128k;
proxy_redirect off;
proxy_hide_header Vary;
proxy_set_header Accept-Encoding '';
proxy_set_header Referer $http_referer;
proxy_set_header Cookie $http_cookie;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

build.sh

```shell
#!/bin/bash

docker build -t 'nginx_balance_image' .
docker run -itd --name nginx_balance -h nginx_balance -p 1700:1700 nginx_balance_image
docker update nginx_balance --restart=always
```

上传到服务器上之后，给 build.sh 添加可执行权限，执行该脚本即可。

### 2.3 蓝绿发布与灰度发布

#### 2.3.1 蓝绿发布

蓝绿发布是指在部署的时候准备新旧两个部署版本，通过域名解析切换的方式将用户使用环境切换到新版本中，当出现问题的时候，可以快速地将用户环境切回旧版本，并对新版本进行修复和调整。

要借助Nginx实现Docker的不停机更新，可以采用以下步骤：

- 在Docker中创建新版本的容器，并将其部署到与旧版本容器相同的网络中。
- 在Nginx配置文件中添加upstream指令，指向新版本容器的网络地址和端口。
- 使用nginx -s reload命令重新加载Nginx配置文件，使其生效。
- 通过逐步将流量从旧版本容器转移到新版本容器，实现无缝更新。可以使用Nginx的upstream模块提供的health_check指令来检查新版本容器的健康状态，并自动切换流量。

需要注意的是，在进行更新前应该进行充分的测试和备份，以确保服务的可靠性和安全性。此外，如果涉及到数据库等有状态服务的更新，还需要考虑数据一致性和数据迁移等问题。

#### 2.3.2 灰度发布

灰度发布又名金丝雀发布，是指当有新版本发布的时候，先让少量用户使用新版本，并且观察新版本是否存在问题。如果出现问题，就及时处理并重新发布；如果一切正常，就稳步地将新版本适配给所有的用户。

## 3. Docker环境搭建及使用

### 3.1 Docker简介

#### 3.1.1 Docker是什么

是什么：Docker是一个用于开发，交付和运行应用程序的开放平台。可以将应用程序与基础架构分开，从而可以快速交付软件。

作用：将一整套环境打包封装成镜像，无需重复配置环境，解决环境带来的种种问题。Docker容器间是进程隔离的，谁也不会影响谁。

官方文档：[Docker官方文档](https://docs.docker.com/get-started/)

#### 3.1.2 Docker的架构

Docker 其实指代的是用于开发，部署，运行应用的一个平台。平常中说的 Docker 准确来说是 Docker Engine。Docker Engine 是一个 C/S 架构的应用。其中主要的组件有：

- Docker Server：长时间运行在后台的程序，就是熟悉的 daemon 进程.
- Docker Client：命令行接口的客户端。
- REST API：用于和 daemon 进程的交互。

![Docker的架构](https://image.eula.club/quantum/Docker的架构.png)

我们通过给 Docker Client 下发各种指令，然后 Client 通过 Docker daemon 提供的 REST API 接口进行交互，来让 daemon 处理编译，运行，部署容器的繁重工作。 大多数情况下， Docker Client 和 Docker Daemon 运行在同一个系统下，但有时也可以使用 Docker Client 来连接远程的 Docker Daemon 进程，也就是远程的 Server 端。

#### 3.1.3 Docker Compose是什么

Compose 是用于定义和运行多容器 Docker 应用程序的工具。通过 Compose，您可以使用 YML 文件来配置应用程序需要的所有服务。然后，使用一个命令，就可以从 YML 文件配置中创建并启动所有服务。

Compose 使用的三个步骤：

- 使用 `Dockerfile` 定义应用程序的环境。
- 使用 `docker-compose.yml` 定义构成应用程序的服务，这样它们可以在隔离环境中一起运行。
- 最后，执行 `docker-compose up` 命令来启动并运行整个应用程序。

![Docker-Compose组成](https://image.eula.club/quantum/Docker-Compose组成.png)

#### 3.1.4 Docker与Docker Compose的区别

Docker是一个供开发和运维人员开发，测试，部署和运行应用的容器平台。这种用linux container部署应用的方式叫容器化。

Docker Compose是一个用于运行和管理多个容器化应用的工具。

我们可以列出下列几项来进行二者对比：

- docker是自动化构建镜像，并启动镜像。 docker compose是自动化编排容器。

- docker是基于Dockerfile得到images，启动的时候是一个单独的container。

- docker-compose是基于docker-compose.yml，通常启动的时候是一个服务，这个服务通常由多个container共同组成，并且端口，配置等由docker-compose定义好。

- 两者都需要安装，但是要使用docker-compose，必须已经安装docker。

#### 3.1.5 直接安装和Docker安装的区别

下面以MySQL数据库为例，看看直接安装MySQL和使用Docker安装MySQL有什么区别：

- docker安装快速，效率高；
- docker隔离性好，可以安装无数个mysql实例，互相不干扰，只要映射主机端口不同即可；
- 占用资源少，MB级别，而服务器安装GB级别；
- 启动速度秒级，而服务器安装启动分钟级别；
- 性能接近原生，而服务器安装较低；
- 数据备份、迁移，docker更方便强大；
- 卸载管理更方便和干净，直接删除容器和镜像即可；
- 稳定性，只要保证docker环境没问题，mysql就没问题。

#### 3.1.6 为什么Docker比虚拟机小很多

Docker使用的base镜像是经过精简的，只包括最基本的命令、工具和程序库。相比物理机安装的操作系统会小很多。另外base镜像只包括操作系统的rootfs部分，不包括bootfs和kermel，并且和Host共用kernel。

Docker的每一层都代表着代码、运行时、库、环境变量和配置文件。下图为例，该新镜像在 Debian base 镜像上构建，添加了一层emacs 编辑器，再添加了一层apache2。新镜像是从 base 镜像一层一层叠加生成的。每安装一个软件，就在现有镜像的基础上增加一层。

![为什么Docker比虚拟机小很多](https://image.eula.club/quantum/为什么Docker比虚拟机小很多.png)

当容器启动时，还会添加一个新的可写层被加载到镜像的顶部。 这一层通常被称作“容器层”，“容器层”之下的都叫“镜像层“。所有对容器的改动，无论添加、删除，还是修改文件都只会发生在容器层中。只有容器层是可写的，容器层下面的所有镜像层都是只读的。 只有当需要修改时才复制一份数据，这种特性被称作 Copy-on-Write。

分层结构最主要的目的是共享资源，如果有多个镜像都从相同的 base 镜像构建而来，那么 Docker Host 只需在磁盘上保存一份 base 镜像；同时内存中也只需加载一份 base 镜像，就可以为所有容器服务了，而且镜像的每一层都可以被共享 。

### 3.2 Docker环境搭建

#### 3.2.1 卸载原先安装的Docker

Debian11系统：

```shell
$ dpkg -l | grep docker   # 查询相关软件包
$ sudo apt remove --purge xxx  # 把查出来的软件包执行此命令（替换xxx）
```

CentOS7系统：

```shell
$ sudo yum remove docker \
                  docker-client \
                  docker-client-latest \
                  docker-common \
                  docker-latest \
                  docker-latest-logrotate \
                  docker-logrotate \
                  docker-selinux \
                  docker-engine-selinux \
                  docker-engine
```

#### 3.2.2 安装Docker环境

Debian11系统：

方式一：通过脚本安装（推荐）

```shell
$ apt-get update -y && apt-get install curl -y  # 安装curl
$ curl https://get.docker.com | sh -   # 安装docker
$ sudo systemctl start docker  # 启动docker服务（改成restart即为重启服务）
$ docker version # 查看docker版本（客户端要与服务端一致）
```

方式二：手动安装

```shell
$ sudo apt-get update
$ sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common
$ curl -fsSL https://download.docker.com/linux/debian/gpg | sudo apt-key add -
$ sudo apt-key fingerprint 0EBFCD88
$ sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
$ sudo apt-get update
$ sudo apt-get install docker-ce docker-ce-cli containerd.io  // 升级Docker版本也是用这个命令，原有镜像和容器还在，可能需要重启容器
$ sudo systemctl start docker
$ docker version
```

CentOS7系统：

```shell
$ curl -fsSL get.docker.com -o get-docker.sh
$ sudo sh get-docker.sh --mirror Aliyun
$ sudo systemctl enable docker
$ sudo systemctl start docker
$ docker version
```

AnolisOS8系统（基于CentOS的）：

```shell
$ dnf config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
$ dnf install docker-ce docker-compose-plugin docker-buildx-plugin
$ systemctl enable --now docker
$ docker -v
$ docker compose version
```

#### 3.2.3 Docker的GPU环境配置

在Docker中使用GPU，首先需要有CUDA及相关环境，保证Docker的版本在19.03以上，然后创建容器时必须设置上`--gpus`参数。

- 有关cuda、nvidia driver、nvidia-cuda-tookit等环境的搭建，详见我的另一篇博客：[常用深度学习平台的使用指南](https://www.eula.club/blogs/常用深度学习平台的使用指南.html)

关于配置Docker使用GPU，其实只用装官方提供的 nvidia-container-toolkit 即可。未配置的话会有`Error response from daemon: could not select device driver "" with capabilities: [[gpu]]`的报错。

Debian/Ubuntu系统：

```shell
$ curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
$ curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
$ sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
$ sudo systemctl restart docker
```

CentOS/Redhat系统：

```shell
$ curl -s -L https://nvidia.github.io/libnvidia-container/stable/rpm/nvidia-container-toolkit.repo | sudo tee /etc/yum.repos.d/nvidia-container-toolkit.repo  
$ sudo yum install -y nvidia-container-toolkit   
$ sudo nvidia-ctk runtime configure --runtime=docker
$ sudo systemctl restart docker   
```

详见：[https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)

注：可通过如下命令检查 nvidia-container-toolkit 是否安装成功

```shell
$ dpkg -l | grep nvidia-container-toolkit     // Debian/Ubuntu系统
$ rpm -qa | grep nvidia-container-toolkit     // CentOS/Redhat系统
```

#### 3.2.4 Docker常用命令

以下是Docker常用命令，需要熟练掌握。

| 命令              | 解释                             |
| ----------------- | -------------------------------- |
| docker run        | 运行一个容器                     |
| docker ps         | 列出运行中的容器                 |
| docker ps -a      | 列出所有容器，包括停止的容器     |
| docker images     | 列出本地镜像                     |
| docker pull       | 从远端仓库拉取镜像               |
| docker build      | 基于Dockerfile构建镜像           |
| docker exec       | 在运行中的容器中执行命令         |
| docker stop       | 停止一个或多个运行中的容器       |
| docker rm         | 删除一个或多个容器               |
| docker rmi        | 删除一个或多个本地镜像           |
| docker network ls | 列出所有网络                     |
| docker volume ls  | 列出所有卷                       |
| docker inspect    | 提供关于指定Docker对象的详细信息 |
| docker logs       | 查看容器的日志                   |
| docker cp         | 从容器复制文件到主机             |
| docker commit     | 创建一个新的镜像                 |

[1] 搜索及拉取docker镜像

```shell
$ docker search [NAME]              # 搜索docker镜像（搜索结果里OFFICIAL为OK的是官方镜像）
$ docker pull [IMAGE NAME]          # 拉取指定docker镜像（IMAGE NAME是搜索出来的指定镜像名）
```

[2] 查看docker容器实例和镜像

```shell
$ docker ps -a                      # 查看所有docker容器实例
$ docker ps                         # 查看所有正在运行的docker容器实例
$ docker images                     # 查看所有docker镜像
$ docker images [IMAGE NAME]        # 查看指定docker镜像（IMAGE NAME为镜像名）
```

[3] 开启停止docker容器实例和镜像

```shell
$ docker start [CONTAINER ID/NAMES]   # 开启指定docker容器实例
$ docker stop [CONTAINER ID/NAMES]    # 停止指定docker容器实例
$ docker restart [CONTAINER ID/NAMES] # 重启指定docker容器实例
$ docker start `docker ps -a -q`      # 批量启动所有的docker容器实例
$ docker stop `docker ps -a -q`       # 批量停止所有的docker容器实例
$ docker restart `docker ps -a -q`    # 批量重启所有的docker容器实例
```

注：可以使用docker pause 命令暂停容器运行。docker pause 命令挂起指定容器中的所有进程，docker stop 容器内主进程会在指定时间内被杀死。

```shell
$ docker pause [CONTAINER ID/NAMES]     # 暂停容器运行
$ docker unpause [CONTAINER ID/NAMES]   # 恢复容器运行
```

[4] 强制删除docker容器实例和镜像

```shell
$ docker rm -f [CONTAINER ID/NAMES]   # 强制删除指定docker容器实例（删除前需先停止实例）
$ docker rmi -f [CONTAINER ID/NAMES]  # 强制删除指定docker镜像（删除前需先停止实例）
$ docker rm -f `docker ps -a -q`      # 批量强制删除所有的docker容器实例（删除前需先停止实例）
$ docker rmi -f `docker images -q`    # 批量强制删除所有的docker镜像（删除前需先停止实例）
```

[5] 进入/退出docker容器内部

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/bash   # 进入指定docker容器内部
$ exit                                             # 从docker容器内部退出
```

注：如果遇到`OCI runtime exec failed: exec failed`问题，则使用如下命令进入

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/sh
```

[6] 查看docker运行日志

```shell
$ docker logs -f [CONTAINER ID/NAMES] --tail 100    # 查看指定条数的docker运行日志
$ docker logs --since 30m [CONTAINER ID/NAMES]      # 查看指定分钟内的docker运行日志   
```

[7] docker容器内部的文件上传和下载

```shell
$ docker cp /root/test.txt [CONTAINER ID/NAMES]:/root       # 上传文件
$ docker cp [CONTAINER ID/NAMES]:/root/test.txt /root       # 下载文件
```

[8] 让容器使用GPU环境

docker run 的时候加上 --gpus all 即可

```shell
--gpus all
```

[9] 在docker容器外执行容器内的命令

有时候我们想执行某个容器的某条命令，但又不想进入容器内，可通过如下命令示例实现：

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/bash -c 'cd /code && python test.py'
```

如果遇到`the input device is not a TTY`问题，去掉t即可，即：

```shell
$ docker exec -i [CONTAINER ID/NAMES] /bin/bash -c 'cd /code && python test.py'
```

注：可以通过这种方式在容器外拿到容器里的执行结果

![在docker容器外执行容器内的命令](https://image.eula.club/quantum/在docker容器外执行容器内的命令.png)

[10] docker的跨容器调用

需求情景：爬虫项目和定时任务项目分别在两个容器中部署的，想要在定时任务项目里编写脚本调用爬虫项目中的具体执行文件。

我们可以通过挂载`docker.sock`和`docker`命令行客户端实现用`docker exec`来间接调用。只需要在docker run的时候挂载如下路径即可：

```shell
-v /var/run/docker.sock:/var/run/docker.sock -v /usr/bin/docker:/usr/bin/docker
```

[11] 给docker镜像打Tag

```shell
$ docker tag [IMAGEID] [REPOSITORY]:[TAG]
```

[12] 给docker容器设置开机自启

```shell
$ docker update [CONTAINER ID/NAMES] --restart=always
```

[13] 显示docker容器占用的系统资源

```shell
$ docker stats               // stats命令默认会每隔1秒钟刷新一次输出的内容直到你按下ctrl + c
$ docker stats --no-stream   // 如果不想持续的监控容器使用资源的情况，可以通过 --no-stream 选项输出当前的状态
$ docker stats --no-stream [CONTAINER ID/NAMES]  // 只输出指定容器的
$ docker stats --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"  // 格式化输出结果，可以只输出部分指标项
```

另注：可使用 [ctop](https://github.com/bcicen/ctop) 工具监控docker容器占用的资源。

```shell
// Linux环境的通用安装
$ sudo wget https://github.com/bcicen/ctop/releases/download/v0.7.7/ctop-0.7.7-linux-amd64 -O /usr/local/bin/ctop
$ sudo chmod +x /usr/local/bin/ctop
// ctop的基本使用
$ ctop
```

ctop工具的资源监控效果如下图所示：

![ctop](https://image.eula.club/quantum/ctop.png)

[14] 容器进程查看

```shell
$ docker ps -q | xargs docker inspect --format '{{.State.Pid}}, {{.Name}}' | grep "PID"  // 根据PID查docker名
$ docker top [CONTAINER ID/NAMES]	  // 列出容器中运行的进程
$ ps -ef   // 查看容器内进程（需要先进入容器内部）
```

[15] 查看容器内系统版本

```shell
$ cat /etc/*release     // 查看容器内系统版本（需要先进入容器内部）
```

[16] 无ENTRYPOINT方式启动

如果是直接执行的代码，写Dockerfile时就不需要加ENTRYPOINT了，然后用以下命令进入容器：

```shell
$ docker run -it --name [CONTAINER ID/NAMES] [IMAGE ID/NAMES] /bin/bash
```

如果要覆盖原先Dockerfile里的ENTRYPOINT配置，加个`--entrypoint /bin/bash`即可。

```shell
$ docker run -it --entrypoint /bin/bash --name [CONTAINER ID/NAMES] [IMAGE ID/NAMES]
```

[17] 查看指定容器的元数据

```shell
$ docker inspect [CONTAINER ID/NAMES]  // 查看指定容器的元数据
$ docker inspect [CONTAINER ID/NAMES] | grep -i Status -A 10  // 查看容器状态及退出原因
$ docker image inspect [IMAGE NAMES]:latest |grep -i version  // 查看指定latest镜像的版本号
```

[18] 设置开机自启与取消开机自启

```shell
$ docker update --restart=always [CONTAINER ID/NAMES]  // 设置开机自启
$ docker update --restart=no [CONTAINER ID/NAMES]      // 取消开机自启
```

[19] docker network相关命令

默认docker之间的网络不互通，如果需要其互相连接，则需要配置docker network。

```shell
$ docker network create [network_name]    // 创建网络
$ docker network ls                       // 查看已创建的网络列表
$ docker network inspect [network_name]   // 查看具体的网络详情
$ docker network connect [network_name] [CONTAINER ID/NAMES]      // 将容器加入网络，或者 docker run 时加 --network 进行指定
$ docker network disconnect [network_name] [CONTAINER ID/NAMES]   // 将容器移除网络
$ docker network rm [network_name]        // 删除具体的网络
```

[20] 查看容器与镜像的差异

```shell
$ docker diff [CONTAINER ID/NAMES]   // 显示容器与镜像的差异（修改后的文件）
```

[21] 根据容器id检索容器名

```shell
$ docker inspect -f '{{.Name}}' [CONTAINER ID] | sed 's/^\///'
```

[22] 清理Docker镜像构建缓存

```shell
$ docker builder prune
```

[23] 查看指定端口的Docker容器

```shell
$ docker ps --filter "publish=8000"       # 方式一
$ docker ps -a | grep "0.0.0.0:8000"      # 方式二
```

#### 3.2.5 清理Docker占用的存储空间

[1] docker空间清理

```shell
$ docker system df                 # 类似于Linux上的df命令，用于查看Docker的磁盘使用情况
$ docker ps --size                 # 查看Docker容器占用的磁盘空间
$ docker builder prune             # 清理Docker镜像的构建缓存
$ docker builder prune -f          # 清理Docker镜像的构建缓存（自动确认而不需要提示）
$ docker system prune              # 可用于清理磁盘，删除关闭的容器、无用的数据卷和网络，以及无tag的镜像
$ docker system prune -a           # 清理得更加彻底，除了上述内容之外，还可以将没有容器使用Docker镜像都删掉。
```

[2] 查看并清空容器日志

在Linux上，Docker容器日志一般存放在`/var/lib/docker/containers/container_id/`下面， 以json.log结尾。

手动处理容器日志：

```shell
$ docker inspect --format='{{.LogPath}}' [CONTAINER ID/NAMES]       # 查看指定容器的日志
$ echo |sudo tee $(docker inspect --format='{{.LogPath}}' [CONTAINER ID/NAMES])  # 清空指定容器的日志
```

批量查找容器日志find_docker_log.sh：

```shell
#!/bin/sh

echo "======== docker containers logs file size ========"  

logs=$(find /var/lib/docker/containers/ -name *-json.log)  

for log in $logs  
        do  
             ls -lh $log   
        done  
```

批量清空容器日志 clear_docker_log.sh：

```shell
#!/bin/sh 

echo "======== start clean docker containers logs ========"  

logs=$(find /var/lib/docker/containers/ -name *-json.log)  

for log in $logs  
        do 
                echo "clean logs : $log"  
                cat /dev/null > $log  
        done  

echo "======== end clean docker containers logs ========"  
```

注：以上清理日志的方法治标不治本，可通过以下方式设置Docker容器日志大小治本。

方案一：设置一个容器服务的日志大小上限

设置一个容器服务的日志大小上限

```
--log-driver json-file  #日志驱动
--log-opt max-size=[0-9+][k|m|g] #文件的大小
--log-opt max-file=[0-9+] #文件数量
```

方案二：全局设置

编辑文件`/etc/docker/daemon.json`, 增加以下日志的配置：

```
"log-driver":"json-file",
"log-opts": {"max-size":"500m", "max-file":"3"}
```

解释说明：

- max-size=500m，意味着一个容器日志大小上限是500M，
- max-file=3，意味着一个容器有三个日志，分别是id+.json、id+1.json、id+2.json。

然后重启docker守护进程

```shell
$ systemctl daemon-reload
$ systemctl restart docker
```

注：设置的日志大小限制，只对新建的容器有效。

#### 3.2.6 解决Docker容器时区不正确的问题

[1] 修改已运行容器的时区

Step1：进入需要更改时区的容器

```shell
$ docker exec -it <容器> /bin/bash
```

Step2：将宿主机的时区链接到容器里

```shell
$ ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
```

Step3：退出并重启容器

```shell
$ exit
$ docker restart <容器>
```

[2] 在docker run命令中修改时区

运行容器时，加上挂载参数

```shell
$ docker run -d <容器> -v /etc/timezone:/etc/timezone -v /etc/localtime:/etc/localtime
```

或者通过-e TZ="Asia/Shanghai"设置时区：

```shell
$ docker run -d <容器> -e TZ="Asia/Shanghai"
```

[3] 在Dockerfile中修改时区

在Dockerfile中

```Dockerfile
RUN ln -sf /usr/share/zoneinfo/Asia/Shanghai /etc/localtime
RUN echo 'Asia/Shanghai' > /etc/timezone
```

[4] 在Compose中修改时区

在docker-compose.yml文件中

```yml
volumes:
  - /etc/timezone:/etc/timezone
  - /etc/localtime:/etc/localtime
```

#### 3.2.7 查看Latest的镜像具体版本

```shell
// 查看容器使用的镜像具体版本
$ docker inspect minio|grep -i version
// 查看镜像具体版本
$ docker image inspect minio/minio:latest|grep -i version
```

#### 3.2.8 解决Docker普通用户无权限问题

给普通用户（如git）添加进Docker组

```shell
$ su git                           // 切换普通用户（如git）
$ sudo usermod -aG docker $USER    // 将当前用户添加到docker组，需要输入git用户密码（忘记了可以在root用户下重置）
$ newgrp docker                    // 激活组权限
```

### 3.3 Docker Compose环境搭建与基本使用

#### 3.3.1 Docker Compose环境搭建

Debian11系统：

```shell
// 下载安装docker-compose，最新版见：https://github.com/docker/compose/releases
$ sudo curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-`uname -s`-`uname -m` -o /usr/local/bin/docker-compose       
// 赋予docker-compose执行权限
$ sudo chmod +x /usr/local/bin/docker-compose
// 查看docker-compose版本号，验证是否安装成功
$ docker-compose --version
```

![docker-compose](https://image.eula.club/quantum/docker-compose.Png)

CentOS7系统：

```shell
$ sudo curl -L https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-Linux-x86_64 -o /usr/local/bin/docker-compose
$ sudo chmod +x /usr/local/bin/docker-compose
$ docker-compose --version
```

#### 3.3.2 Docker Compose基本使用

首先要编写好docker-compose.yml文件，然后构建镜像、运行容器即可。

```shell
$ cd <docker-compose-path>  // 切换到docker-compose.yml文件所在的目录
$ docker-compose build      // 构建镜像
$ docker-compose up -d      // 运行容器
$ docker-compose stop       // 停止容器
```

注：如果不是默认的docker-compose.yml文件，需要使用 -f 参数手动指定。

```shell
$ docker-compose -f custom-docker-compose.yml up -d
```

### 3.4 Docker官方源国内被墙问题

#### 3.4.1 Cloudfare代理Docker镜像库

Step1：登录 [Cloudflare](https://dash.cloudflare.com)，选择左侧的 `Workers & Pages`，点击Create按钮创建，然后再下一级的页面点击“Create Worker”按钮。

![Cloudfare创建Workers](https://image.eula.club/quantum/Cloudfare创建Workers.png)

Step2：修改Worker的名称为docker-proxy，先点击deploy。然后再复制以下代码进去（需修改“自定义域名”那里），再次点击deploy。

![Cloudfare代理Docker镜像库的代码](https://image.eula.club/quantum/Cloudfare代理Docker镜像库的代码.png)

代码内容如下：

```javascript
// Docker镜像仓库主机地址
let hub_host = 'registry-1.docker.io';
// Docker认证服务器地址
const auth_url = 'https://auth.docker.io';
// 自定义的工作服务器地址
let workers_url = 'https://你的自定义域名/';

let 屏蔽爬虫UA = ['netcraft'];

// 根据主机名选择对应的上游地址
function routeByHosts(host) {
	// 定义路由表
	const routes = {
		// 生产环境
		"quay": "quay.io",
		"gcr": "gcr.io",
		"k8s-gcr": "k8s.gcr.io",
		"k8s": "registry.k8s.io",
		"ghcr": "ghcr.io",
		"cloudsmith": "docker.cloudsmith.io",
		"nvcr": "nvcr.io",
		
		// 测试环境
		"test": "registry-1.docker.io",
	};

	if (host in routes) return [ routes[host], false ];
	else return [ hub_host, true ];
}

/** @type {RequestInit} */
const PREFLIGHT_INIT = {
	// 预检请求配置
	headers: new Headers({
		'access-control-allow-origin': '*', // 允许所有来源
		'access-control-allow-methods': 'GET,POST,PUT,PATCH,TRACE,DELETE,HEAD,OPTIONS', // 允许的HTTP方法
		'access-control-max-age': '1728000', // 预检请求的缓存时间
	}),
}

/**
 * 构造响应
 * @param {any} body 响应体
 * @param {number} status 响应状态码
 * @param {Object<string, string>} headers 响应头
 */
function makeRes(body, status = 200, headers = {}) {
	headers['access-control-allow-origin'] = '*' // 允许所有来源
	return new Response(body, { status, headers }) // 返回新构造的响应
}

/**
 * 构造新的URL对象
 * @param {string} urlStr URL字符串
 */
function newUrl(urlStr) {
	try {
		return new URL(urlStr) // 尝试构造新的URL对象
	} catch (err) {
		return null // 构造失败返回null
	}
}

function isUUID(uuid) {
	// 定义一个正则表达式来匹配 UUID 格式
	const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-[4][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
	
	// 使用正则表达式测试 UUID 字符串
	return uuidRegex.test(uuid);
}

async function nginx() {
	const text = `
	<!DOCTYPE html>
	<html>
	<head>
	<title>Welcome to nginx!</title>
	<style>
		body {
			width: 35em;
			margin: 0 auto;
			font-family: Tahoma, Verdana, Arial, sans-serif;
		}
	</style>
	</head>
	<body>
	<h1>Welcome to nginx!</h1>
	<p>If you see this page, the nginx web server is successfully installed and
	working. Further configuration is required.</p>
	
	<p>For online documentation and support please refer to
	<a href="http://nginx.org/">nginx.org</a>.<br/>
	Commercial support is available at
	<a href="http://nginx.com/">nginx.com</a>.</p>
	
	<p><em>Thank you for using nginx.</em></p>
	</body>
	</html>
	`
	return text;
}

async function searchInterface() {
	const text = `
	<!DOCTYPE html>
	<html>
	<head>
		<title>Docker Hub Search</title>
		<style>
		body {
			font-family: Arial, sans-serif;
			display: flex;
			flex-direction: column;
			align-items: center;
			justify-content: center;
			height: 100vh;
			margin: 0;
			background: linear-gradient(to right, rgb(28, 143, 237), rgb(29, 99, 237));
		}
		.logo {
			margin-bottom: 20px;
		}
		.search-container {
			display: flex;
			align-items: center;
		}
		#search-input {
			padding: 10px;
			font-size: 16px;
			border: 1px solid #ddd;
			border-radius: 4px;
			width: 300px;
			margin-right: 10px;
		}
		#search-button {
			padding: 10px;
			background-color: rgba(255, 255, 255, 0.2); /* 设置白色，透明度为10% */
			border: none;
			border-radius: 4px;
			cursor: pointer;
			width: 44px;
			height: 44px;
			display: flex;
			align-items: center;
			justify-content: center;
		}			
		#search-button svg {
			width: 24px;
			height: 24px;
		}
		</style>
	</head>
	<body>
		<div class="logo">
		<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 18" fill="#ffffff" width="100" height="75">
			<path d="M23.763 6.886c-.065-.053-.673-.512-1.954-.512-.32 0-.659.03-1.01.087-.248-1.703-1.651-2.533-1.716-2.57l-.345-.2-.227.328a4.596 4.596 0 0 0-.611 1.433c-.23.972-.09 1.884.403 2.666-.596.331-1.546.418-1.744.42H.752a.753.753 0 0 0-.75.749c-.007 1.456.233 2.864.692 4.07.545 1.43 1.355 2.483 2.409 3.13 1.181.725 3.104 1.14 5.276 1.14 1.016 0 2.03-.092 2.93-.266 1.417-.273 2.705-.742 3.826-1.391a10.497 10.497 0 0 0 2.61-2.14c1.252-1.42 1.998-3.005 2.553-4.408.075.003.148.005.221.005 1.371 0 2.215-.55 2.68-1.01.505-.5.685-.998.704-1.053L24 7.076l-.237-.19Z"></path>
			<path d="M2.216 8.075h2.119a.186.186 0 0 0 .185-.186V6a.186.186 0 0 0-.185-.186H2.216A.186.186 0 0 0 2.031 6v1.89c0 .103.083.186.185.186Zm2.92 0h2.118a.185.185 0 0 0 .185-.186V6a.185.185 0 0 0-.185-.186H5.136A.185.185 0 0 0 4.95 6v1.89c0 .103.083.186.186.186Zm2.964 0h2.118a.186.186 0 0 0 .185-.186V6a.186.186 0 0 0-.185-.186H8.1A.185.185 0 0 0 7.914 6v1.89c0 .103.083.186.186.186Zm2.928 0h2.119a.185.185 0 0 0 .185-.186V6a.185.185 0 0 0-.185-.186h-2.119a.186.186 0 0 0-.185.186v1.89c0 .103.083.186.185.186Zm-5.892-2.72h2.118a.185.185 0 0 0 .185-.186V3.28a.186.186 0 0 0-.185-.186H5.136a.186.186 0 0 0-.186.186v1.89c0 .103.083.186.186.186Zm2.964 0h2.118a.186.186 0 0 0 .185-.186V3.28a.186.186 0 0 0-.185-.186H8.1a.186.186 0 0 0-.186.186v1.89c0 .103.083.186.186.186Zm2.928 0h2.119a.185.185 0 0 0 .185-.186V3.28a.186.186 0 0 0-.185-.186h-2.119a.186.186 0 0 0-.185.186v1.89c0 .103.083.186.185.186Zm0-2.72h2.119a.186.186 0 0 0 .185-.186V.56a.185.185 0 0 0-.185-.186h-2.119a.186.186 0 0 0-.185.186v1.89c0 .103.083.186.185.186Zm2.955 5.44h2.118a.185.185 0 0 0 .186-.186V6a.185.185 0 0 0-.186-.186h-2.118a.185.185 0 0 0-.185.186v1.89c0 .103.083.186.185.186Z"></path>
		</svg>
		</div>
		<div class="search-container">
		<input type="text" id="search-input" placeholder="Search Docker Hub">
		<button id="search-button">
			<svg focusable="false" aria-hidden="true" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
			<path d="M21 21L16.65 16.65M19 11C19 15.4183 15.4183 19 11 19C6.58172 19 3 15.4183 3 11C3 6.58172 6.58172 3 11 3C15.4183 3 19 6.58172 19 11Z" stroke="white" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"></path>
			</svg>
		</button>
		</div>
		<script>
		function performSearch() {
			const query = document.getElementById('search-input').value;
			if (query) {
			window.location.href = '/search?q=' + encodeURIComponent(query);
			}
		}
	
		document.getElementById('search-button').addEventListener('click', performSearch);
		document.getElementById('search-input').addEventListener('keypress', function(event) {
			if (event.key === 'Enter') {
			performSearch();
			}
		});
		</script>
	</body>
	</html>
	`;
	return text;
}

export default {
	async fetch(request, env, ctx) {
		const getReqHeader = (key) => request.headers.get(key); // 获取请求头

		let url = new URL(request.url); // 解析请求URL
		const userAgentHeader = request.headers.get('User-Agent');
		const userAgent = userAgentHeader ? userAgentHeader.toLowerCase() : "null";
		if (env.UA) 屏蔽爬虫UA = 屏蔽爬虫UA.concat(await ADD(env.UA));
		workers_url = `https://${url.hostname}`;
		const pathname = url.pathname;

		// 获取请求参数中的 ns
		const ns = url.searchParams.get('ns'); 
		const hostname = url.searchParams.get('hubhost') || url.hostname;
		const hostTop = hostname.split('.')[0]; // 获取主机名的第一部分

		let checkHost; // 在这里定义 checkHost 变量
		// 如果存在 ns 参数，优先使用它来确定 hub_host
		if (ns) {
			if (ns === 'docker.io') {
				hub_host = 'registry-1.docker.io'; // 设置上游地址为 registry-1.docker.io
			} else {
				hub_host = ns; // 直接使用 ns 作为 hub_host
			}
		} else {
			checkHost = routeByHosts(hostTop);
			hub_host = checkHost[0]; // 获取上游地址
		}

		const fakePage = checkHost ? checkHost[1] : false; // 确保 fakePage 不为 undefined
		console.log(`域名头部: ${hostTop}\n反代地址: ${hub_host}\n伪装首页: ${fakePage}`);
		const isUuid = isUUID(pathname.split('/')[1].split('/')[0]);

		if (屏蔽爬虫UA.some(fxxk => userAgent.includes(fxxk)) && 屏蔽爬虫UA.length > 0) {
			// 首页改成一个nginx伪装页
			return new Response(await nginx(), {
				headers: {
					'Content-Type': 'text/html; charset=UTF-8',
				},
			});
		}

		const conditions = [
			isUuid,
			pathname.includes('/_'),
			pathname.includes('/r/'),
			pathname.includes('/v2/repositories'),
			pathname.includes('/v2/user'),
			pathname.includes('/v2/orgs'),
			pathname.includes('/v2/_catalog'),
			pathname.includes('/v2/categories'),
			pathname.includes('/v2/feature-flags'),
			pathname.includes('search'),
			pathname.includes('source'),
			pathname == '/',
			pathname == '/favicon.ico',
			pathname == '/auth/profile',
		];

		if (conditions.some(condition => condition) && (fakePage === true || hostTop == 'docker')) {
			if (env.URL302) {
				return Response.redirect(env.URL302, 302);
			} else if (env.URL) {
				if (env.URL.toLowerCase() == 'nginx') {
					//首页改成一个nginx伪装页
					return new Response(await nginx(), {
						headers: {
							'Content-Type': 'text/html; charset=UTF-8',
						},
					});
				} else return fetch(new Request(env.URL, request));
			} else if (url.pathname == '/'){
				return new Response(await searchInterface(), {
					headers: {
					  'Content-Type': 'text/html; charset=UTF-8',
					},
				});
			}
			
			const newUrl = new URL("https://registry.hub.docker.com" + pathname + url.search);

			// 复制原始请求的标头
			const headers = new Headers(request.headers);

			// 确保 Host 头部被替换为 hub.docker.com
			headers.set('Host', 'registry.hub.docker.com');

			const newRequest = new Request(newUrl, {
					method: request.method,
					headers: headers,
					body: request.method !== 'GET' && request.method !== 'HEAD' ? await request.blob() : null,
					redirect: 'follow'
			});

			return fetch(newRequest);
		}

		// 修改包含 %2F 和 %3A 的请求
		if (!/%2F/.test(url.search) && /%3A/.test(url.toString())) {
			let modifiedUrl = url.toString().replace(/%3A(?=.*?&)/, '%3Alibrary%2F');
			url = new URL(modifiedUrl);
			console.log(`handle_url: ${url}`);
		}

		// 处理token请求
		if (url.pathname.includes('/token')) {
			let token_parameter = {
				headers: {
					'Host': 'auth.docker.io',
					'User-Agent': getReqHeader("User-Agent"),
					'Accept': getReqHeader("Accept"),
					'Accept-Language': getReqHeader("Accept-Language"),
					'Accept-Encoding': getReqHeader("Accept-Encoding"),
					'Connection': 'keep-alive',
					'Cache-Control': 'max-age=0'
				}
			};
			let token_url = auth_url + url.pathname + url.search;
			return fetch(new Request(token_url, request), token_parameter);
		}

		// 修改 /v2/ 请求路径
		if ( hub_host == 'registry-1.docker.io' && /^\/v2\/[^/]+\/[^/]+\/[^/]+$/.test(url.pathname) && !/^\/v2\/library/.test(url.pathname)) {
			//url.pathname = url.pathname.replace(/\/v2\//, '/v2/library/');
			url.pathname = '/v2/library/' + url.pathname.split('/v2/')[1];
			console.log(`modified_url: ${url.pathname}`);
		}

		// 更改请求的主机名
		url.hostname = hub_host;

		// 构造请求参数
		let parameter = {
			headers: {
				'Host': hub_host,
				'User-Agent': getReqHeader("User-Agent"),
				'Accept': getReqHeader("Accept"),
				'Accept-Language': getReqHeader("Accept-Language"),
				'Accept-Encoding': getReqHeader("Accept-Encoding"),
				'Connection': 'keep-alive',
				'Cache-Control': 'max-age=0'
			},
			cacheTtl: 3600 // 缓存时间
		};

		// 添加Authorization头
		if (request.headers.has("Authorization")) {
			parameter.headers.Authorization = getReqHeader("Authorization");
		}

		// 发起请求并处理响应
		let original_response = await fetch(new Request(url, request), parameter);
		let original_response_clone = original_response.clone();
		let original_text = original_response_clone.body;
		let response_headers = original_response.headers;
		let new_response_headers = new Headers(response_headers);
		let status = original_response.status;

		// 修改 Www-Authenticate 头
		if (new_response_headers.get("Www-Authenticate")) {
			let auth = new_response_headers.get("Www-Authenticate");
			let re = new RegExp(auth_url, 'g');
			new_response_headers.set("Www-Authenticate", response_headers.get("Www-Authenticate").replace(re, workers_url));
		}

		// 处理重定向
		if (new_response_headers.get("Location")) {
			return httpHandler(request, new_response_headers.get("Location"));
		}

		// 返回修改后的响应
		let response = new Response(original_text, {
			status,
			headers: new_response_headers
		});
		return response;
	}
};

/**
 * 处理HTTP请求
 * @param {Request} req 请求对象
 * @param {string} pathname 请求路径
 */
function httpHandler(req, pathname) {
	const reqHdrRaw = req.headers;

	// 处理预检请求
	if (req.method === 'OPTIONS' &&
		reqHdrRaw.has('access-control-request-headers')
	) {
		return new Response(null, PREFLIGHT_INIT);
	}

	let rawLen = '';

	const reqHdrNew = new Headers(reqHdrRaw);

	const refer = reqHdrNew.get('referer');

	let urlStr = pathname;

	const urlObj = newUrl(urlStr);

	/** @type {RequestInit} */
	const reqInit = {
		method: req.method,
		headers: reqHdrNew,
		redirect: 'follow',
		body: req.body
	};
	return proxy(urlObj, reqInit, rawLen);
}

/**
 * 代理请求
 * @param {URL} urlObj URL对象
 * @param {RequestInit} reqInit 请求初始化对象
 * @param {string} rawLen 原始长度
 */
async function proxy(urlObj, reqInit, rawLen) {
	const res = await fetch(urlObj.href, reqInit);
	const resHdrOld = res.headers;
	const resHdrNew = new Headers(resHdrOld);

	// 验证长度
	if (rawLen) {
		const newLen = resHdrOld.get('content-length') || '';
		const badLen = (rawLen !== newLen);

		if (badLen) {
			return makeRes(res.body, 400, {
				'--error': `bad len: ${newLen}, except: ${rawLen}`,
				'access-control-expose-headers': '--error',
			});
		}
	}
	const status = res.status;
	resHdrNew.set('access-control-expose-headers', '*');
	resHdrNew.set('access-control-allow-origin', '*');
	resHdrNew.set('Cache-Control', 'max-age=1500');

	// 删除不必要的头
	resHdrNew.delete('content-security-policy');
	resHdrNew.delete('content-security-policy-report-only');
	resHdrNew.delete('clear-site-data');

	return new Response(res.body, {
		status,
		headers: resHdrNew
	});
}

async function ADD(envadd) {
	var addtext = envadd.replace(/[	 |"'\r\n]+/g, ',').replace(/,+/g, ',');	// 将空格、双引号、单引号和换行符替换为逗号
	if (addtext.charAt(0) == ',') addtext = addtext.slice(1);
	if (addtext.charAt(addtext.length - 1) == ',') addtext = addtext.slice(0, addtext.length - 1);
	const add = addtext.split(',');
	return add;
}
```

Step3：在Settings的Domains & Routes处添加自定义域名，与脚本那里填写的抑制即可，这个域名不需要在DNS那里再配置一下。

![Cloudfare配置自定义域名](https://image.eula.club/quantum/Cloudfare配置自定义域名.png)

#### 3.4.2 Docker更换镜像源地址

缘由：在Dockerfile创建镜像拉取基础镜像时遇到了`Get "https://registry-1.docker.io/v2/": net/http: request canceled while waiting for connection (Client.Timeout exceeded while awaiting headers)`报错，原因是连不上官方的源，可修改配置换源解决。

Docker安装后默认没有`daemon.json`这个配置文件，需要进行手动创建，配置文件的默认路径：`/etc/docker/daemon.json`，权限为644，内容如下：

```json
{
 "registry-mirrors":[
    "https://docker.eula.club"
 ],
 "runtimes": {
     "nvidia": {
         "path": "/usr/bin/nvidia-container-runtime",
         "runtimeArgs": []
     }
 }
} 
```

注：这里配置的是通过Cloudfare代理Docker镜像库的地址，也可从网上自行搜寻可用的镜像地址。

修改后需要重新加载配置，然后重启docker服务。

```shell
$ sudo systemctl daemon-reload
$ systemctl restart docker.service
```

注：如果不想重启 Docker 守护进程，可以通过如下命令重新加载 Docker 守护进程配置。

```shell
$ sudo kill -SIGHUP $(pidof dockerd)
```

修改完成之后，可通过如下命令查看是否生效，生效了的话会打印出刚配置出的镜像地址。

```shell
$ docker info
```

### 3.5 通过Dockerfile自动构建镜像

Step1：在项目里面再新建一个Dockerfile文件（有的开源项目会提供现成的 Dockerfile，如果没有就要自己去写）。

| 指令名称     | 说明                                              | 示例                          |
| ------------ | ------------------------------------------------- | ----------------------------- |
| `FROM`       | 指定基础镜像名称/ID                               | `FROM centos:7`               |
| `ENV`        | 设置环境变量，可在后面的指令中使用                | `ENV key value`               |
| `COPY`       | 拷贝本地文件/目录到镜像的指定目录                 | `COPY <源路径> <目标路径>`    |
| `ADD`        | 与COPY类似，目录或远程URL从源复制到镜像的目标目录 | `ADD <源路径> <目标路径>`     |
| `RUN`        | 执行Linux的shell命令，一般是编译/安装软件的命令   | `RUN yum install gcc`         |
| `EXPOSE`     | 指定容器运行时监听的端口号                        | `EXPOSE 80`                   |
| `ENTRYPOINT` | 容器启动时用的启动命令，容器运行时的入口          | `ENTRYPOINT java -jar xx.jar` |

Step2：切换到项目目录里，执行如下命令即可成功构建镜像。

```shell
$ docker build -t 'test-image' .
```

Step3：我们可以打包导出镜像，示例如下。

```shell
$ docker save test-image > test-image.v1.dockerimage  
```

#### 3.5.1 使用Docker部署Springboot项目

Step1：使用Maven将项目打包成jar包，并编写Dockerfile，示例如下：

```Dockerfile
# 基于java8镜像创建新镜像
FROM java:8
# 将jar包添加到容器中并更名为app.jar
COPY test-project-0.0.1-SNAPSHOT.jar /app.jar
# 安装vim命令
RUN apt-get update && apt-get install vim -y 
# 运行jar包
ENTRYPOINT ["java","-jar","/app.jar"]
```

另注：如果想要指定用哪个配置文件，可以使用如下自启动配置

```
ENTRYPOINT java -jar /app.jar --spring.profiles.active=prod
```

Step2：将jar包和Dockerfile上传到服务器并制作镜像运行容器

```shell
$ cd /root/deploy                                                                // 切换到存放jar包和Dockerfile的目录
$ docker build -t test-springboot-image .                                        // 使用Dockerfile构建镜像
$ docker run -d -p 8080:8080 --name test-springboot -e TZ="Asia/Shanghai" test-springboot-image:latest // 通过镜像运行容器
$ docker update test-springboot --restart=always                                 // 设置开机自启
```

#### 3.5.2 使用Docker部署Flask项目

Step1：导出项目依赖，并编写Dockerfile，示例如下：

```shell
$ pip freeze > requirements.txt
```

注：建议对项目单独建一个conda虚拟环境，再导出依赖，这样导出的依赖就这一个项目的，就不用手动删除无用的了。

```dockerfile
# 基于python3.7镜像创建新镜像
FROM python:3.7
# 创建容器内部目录
RUN mkdir /code
# 将项目复制到内部目录
ADD test-project /code/
# 切换到工作目录
WORKDIR /code
# 修改pip镜像源为阿里云，并设置为可信主机
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
RUN pip config set global.trusted-host mirrors.aliyun.com
# 更新pip到最新版本
RUN pip install --upgrade pip
# 手动安装setuptools_scm
RUN pip install setuptools_scm
# 安装项目依赖
RUN pip install -r requirements.txt
# 启动项目
ENTRYPOINT ["python","server.py"]
```

Step2：将项目和Dockerfile上传到服务器并制作镜像运行容器

```shell
$ cd /root/deploy                                                       // 切换到存放项目和Dockerfile的目录
$ docker build -t test-flask-image .                                    // 使用Dockerfile构建镜像
$ docker run -d -p 5000:5000 --name test-flask -e TZ="Asia/Shanghai" test-flask-image:latest  // 通过镜像运行容器
$ docker update test-flask --restart=always                             // 设置开机自启
```

#### 3.5.3 使用Docker部署前端项目

Step1：将前端项目打包，生成dist文件（或者其他的），编写Dockerfile，示例如下：

```dockerfile
# 设置基础镜像
FROM nginx
# 将dist文件中的内容复制到 /usr/share/nginx/html/这个目录下面
COPY dist/  /usr/share/nginx/html/
# 安装vim命令
RUN apt-get update && apt-get install vim -y 
```

Step2：将项目和Dockerfile上传到服务器并制作镜像运行容器

```shell
$ cd /root/deploy                                                     // 切换到存放项目和Dockerfile的目录
$ docker build -t test-web-image .                                    // 使用Dockerfile构建镜像
$ docker run -d -p 8081:80 --name test-web -e TZ="Asia/Shanghai" test-web-image:latest      // 通过镜像运行容器
$ docker update test-web --restart=always                             // 设置开机自启
```

访问地址：`http://ip:8081`

注意事项：

[1] 容器内nginx的默认端口是80，如要使用其他端口，请修改nginx配置。以下是容器内的几个重要目录，如有需要可挂载出来。

```
/etc/nginx/conf.d                                                     // Nginx配置目录
/usr/share/nginx/html                                                 // Nginx存放资源的目录
/var/log/nginx                                                        // Nginx日志目录
```

[2] 如果访问页面时出现403问题，进入容器内修改权限即可。

```shell
$ docker exec -it test-web /bin/bash
$ chmod -R 755 /usr/share/nginx/html
```

### 3.6 动态接入服务地址的前端容器化部署

#### 3.6.1 适用情景及解决方案

情景描述：前端通过读取配置文件接入算法服务，但前端和算法服务放在不同的Docker容器里。对外部署的时候，算法服务的IP地址是不固定的，而前端编译成dist后这个地址就编译进去了，无法动态的去调整。使用Docker Network也不可行，因为前端是客户端去访问，它通过容器的 hostname 是访问不到服务的。

解决方案：放弃编译成dist采用Nginx进行代理访问的方案，改成直接前端启动的方式，在Docker容器创建时用 -e 参数去动态指定服务地址，配置文件里的地址通过脚本去进行修改。

#### 3.6.2 配置文件及使用方式

这里以Vue项目为例，配置文件采用的config.json。

Dockerfile

```Dockerfile
# 基于Node官方镜像
FROM node:lts

# 创建并设置工作目录
WORKDIR /code

# 复制项目文件到工作目录
COPY . /code/

# 安装依赖
RUN npm install --registry=http://registry.npm.taobao.org

# 安装jq命令
RUN apt-get update && apt-get install -y jq

# entrypoint.sh赋予可执行权限
RUN chmod +x /code/entrypoint.sh

# 使用entrypoint.sh作为入口点
ENTRYPOINT ["/code/entrypoint.sh"]

# 启动前端
CMD ["npm", "run", "serve"]
```

config.json

```json
{
  "算法服务1": "",
  "算法服务2": ""
}
```

entrypoint.sh

```shell
#!/bin/bash

# 检查 CONFIG_JSON_PATH 环境变量是否已设置，并提供默认值
CONFIG_JSON_PATH=${CONFIG_JSON_PATH:-"/code/src/config.json"}

# 环境变量与 config.json 中字段的映射关系
declare -A env_config_map=(
    ["API_URL_1"]="算法服务1"
    ["API_URL_2"]="算法服务2"
)

# 使用 jq 更新 config.json 中的值
for env_var in "${!env_config_map[@]}"; do
    config_key=${env_config_map[$env_var]}
    env_value=$(eval echo \$$env_var)
    if [ -n "$env_value" ]; then
        jq --arg key "$config_key" --arg value "$env_value" \
           '.[$key] = $value' $CONFIG_JSON_PATH > $CONFIG_JSON_PATH.temp && mv $CONFIG_JSON_PATH.temp $CONFIG_JSON_PATH
    fi
done

exec "$@"
```

build.sh

```shell
docker build -t vue-demo-image .
docker run -d --name vue-demo  \
           -p 54320:54320   \
           -e API_URL_1=http://xxx.xxx.xxx.xxx:54321/api/xxx \
           -e API_URL_2=http://xxx.xxx.xxx.xxx:54322/api/xxx \
           vue-demo-image:latest
docker update vue-demo --restart=always
```

### 3.7 正式环境的前后端分离项目部署

正式环境使用Docker Network对Docker容器进行统一管理，像数据库这种提供服务的，可不对外提供端口，各容器之间通过hostname进行内部通信。

下面以一个Springboot + Vue的前后端分离项目（项目依赖于MySQL、Redis、 Elasticsearch、Emqx）为例。

#### 3.7.1 准备中间件及数据库环境

建议新建个docker network，将这些容器加到同一个网络环境里面，这样可以不对外暴露一些不必要的数据库及中间件环境，更加安全。

```shell
$ docker network create yoyo

$ docker run -itd --name yoyo_mysql -h yoyo_mysql --network yoyo -p 3306:3306 \
-e TZ=Asia/Shanghai \
-v /root/docker/mysql/conf:/etc/mysql/conf.d \
-v /root/docker/mysql/logs:/var/log/mysql \
-v /root/docker/mysql/data:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=[password] \
mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
$ docker update yoyo_mysql --restart=always

$ docker run -itd --name yoyo_redis -h yoyo_redis --network yoyo -p 6379:6379 redis:3.2.8 --requirepass "mypassword"
$ docker update yoyo_redis --restart=always

$ docker run -itd --name yoyo_es -h yoyo_es --network yoyo -p 9200:9200 \
-e "discovery.type=single-node" \
-e ES_JAVA_OPTS="-Xms512m -Xmx512m" \
elasticsearch:7.16.2
$ docker update yoyo_es --restart=always

$ docker run -itd --name yoyo_emqx -h yoyo_emqx --network yoyo -p 1883:1883 -p 18083:18083 emqx/emqx
$ docker update yoyo_emqx --restart=always
```

注：可使用 `docker network ls` 命令查看已创建的网络，创建容器时需要使用--network 指定网络，建议用 -h 指定 hostname，除 emqx 的1883端口外，其他服务可不使用 -p 对外映射端口号，我这里为了调试方便，仍然把不必要的端口暴露出来了。

#### 3.7.2 项目打包并准备项目配置

将Springboot项目打成jar包，Vue项目打成dist包。除此之外，需要修改Springboot项目的配置文件（把项目依赖的MySQL、Redis、 Elasticsearch、Emqx环境地址由原来的ip:port改成 docker 的 hostname），这里采用包外配置。

前端项目打包（以 Angular 为例）

```shell
$ npm install -g @angular/cli   
$ npm install   
$ ng build --base-href ./  
```

后端项目打包（以Springboot为例）

```shell
$ mvn clean
$ mvn install
$ mvn package
```

#### 3.7.3 准备一键部署包的配置文件及脚本

项目部署所需要文件的目录结构如下：

```
.
├── config
    ├── application-prod.properties
    └── application.properties
├── dist.zip
├── Dockerfile
├── nginx.conf
├── proxy.conf
├── yoyo_web.conf
├── web_manage-0.0.1.jar
├── unzip.sh
├── build.sh
├── rebuild.sh
└── start_web.sh
```

[1] 准备 nginx 配置文件 （nginx.conf、yoyo_web.conf、proxy.conf）

nginx.conf（无需修改）

```ini
user  root;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
```

yoyo_web.conf（需要修改后端的接口地址和前端文件的存放路径，`location ~* ^`这里根据实际项目的路由配置进行转发）

```ini
upstream dev_yoyo_web {
        server 127.0.0.1:8081 weight=1 max_fails=1 fail_timeout=10s;
}
server {
    listen       82;
    server_name  127.0.0.1;
    location / {
        gzip on;
        gzip_vary on;
        gzip_min_length 1k;
        gzip_buffers 16 16k;
        gzip_http_version 1.1;
        gzip_comp_level 9;
        gzip_types text/plain application/javascript application/x-javascript text/css text/xml text/javascript application/json;
        root  /storage/web_code;
        index index.html;
        try_files $uri $uri/ /index.html?$query_string;
    }

    location ~* ^(/login|/logout|/api/|/auth/) {
        proxy_pass http://dev_yoyo_web; 
        client_max_body_size    48m;
        include proxy.conf;
    }
}
```

proxy.conf（无需修改）

```ini
proxy_connect_timeout 900s;
proxy_send_timeout 900;
proxy_read_timeout 900;
proxy_buffer_size 32k;
proxy_buffers 4 64k;
proxy_busy_buffers_size 128k;
proxy_redirect off;
proxy_hide_header Vary;
proxy_set_header Accept-Encoding '';
proxy_set_header Referer $http_referer;
proxy_set_header Cookie $http_cookie;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

[2] 准备Dockerfile（可不修改，也可根据实际需要修改）

```dockerfile
# 设置基础镜像
FROM nginx

# 安装常用命令
RUN apt-get update
RUN apt-get install -y wget       # 安装wget
RUN apt-get install vim -y        # 安装vim
RUN apt-get install -y psmisc     # 安装ps

# 设置工作目录
RUN mkdir /storage
WORKDIR /storage

# 安装java8环境
RUN mkdir /usr/local/java
# 方式一：下载jdk并解压到指定目录（适用于网速快的情况，需要提前安装wget）
RUN wget https://mirrors.huaweicloud.com/java/jdk/8u202-b08/jdk-8u202-linux-x64.tar.gz
RUN tar zxvf jdk-8u202-linux-x64.tar.gz -C /usr/local/java && rm -f jdk-8u202-linux-x64.tar.gz
# 方式二：将本地jdk复制到内部目录并自动解压（适用于网速慢的情况，提前下载好）
# ADD jdk-8u202-linux-x64.tar.gz /usr/local/java
# RUN rm -f jdk-8u202-linux-x64.tar.gz
RUN ln -s /usr/local/java/jdk1.8.0_202 /usr/local/java/jdk
ENV JAVA_HOME /usr/local/java/jdk
ENV JRE_HOME ${JAVA_HOME}/jre
ENV CLASSPATH .:${JAVA_HOME}/lib:${JRE_HOME}/lib
ENV PATH ${JAVA_HOME}/bin:$PATH

# 放置前端代码及nginx配置
ADD dist/ /storage/web_code
COPY nginx.conf /etc/nginx/nginx.conf
COPY yoyo_web.conf /etc/nginx/conf.d/yoyo_web.conf
COPY proxy.conf /etc/nginx

# 放置后端代码及包外配置
COPY web_manage-0.0.1.jar /storage
COPY config /storage

# 放置启动脚本并授予权限
COPY start_web.sh /storage/start_web.sh
RUN chmod u+x /storage/start_web.sh

# 容器服务自启
ENTRYPOINT ["/storage/start_web.sh"]
```

注意事项：

- ENTRYPOINT 里的配置会覆盖父镜像的启动命令，因此这里需要启动 Nginx 和 Jar 的两个命令。若用`&&`连接的话只会执行前面的那一个，因此这里将两个启动命令都写进一个Shell脚本里。

  ```
  关于CMD和ENTRYPOINT有一点需要特别注意：如果一个Dockerfile中有多个CMD或ENTRYPOINT，只有最后一个会生效，前面其他的都会被覆盖。
  ```

- 前端包我这里采用的是将 zip 通过shell脚本解压后再拷贝进容器的方式，如果采用 tar.gz 格式，ADD命令会自动对其进行解压（其他压缩格式不可以）。

  ```
  ADD dist.tar.gz /storage/web_code
  ```

[3] 准备部署脚本

unzip.sh（无需修改）

```shell
#!/bin/bash

#define default variable
base_path=$(cd `dirname $0`; pwd)
app_path="${base_path}/dist"
zip_name="${base_path}/dist.zip"
rm -fr ${app_path}
unzip -d ${app_path} ${zip_name}
echo "unzip success!"
```

start_web.sh（可不修改，也可根据实际需要修改）

```shell
#!/bin/bash

/docker-entrypoint.sh nginx -g 'daemon off;' &
java -jar /storage/web_manage-0.0.1.jar --spring.profiles.active=prod
```

注意：前面的服务一定要在后台运行，即后面加个&，最后一个服务要以前台运行。否则，全部以前台运行的话，只有第一个服务会启动；全部以后台运行的话，当最后一个服务执行完成后，容器就退出了。

build.sh（可不修改，也可根据实际需要修改）

```shell
#!/bin/bash

base_path=$(cd `dirname $0`; pwd)
uploads_path="${base_path}/uploads"
mkdir ${uploads_path}
chmod u+x ${base_path}/unzip.sh
${base_path}/unzip.sh
docker build -t 'yoyo_web_image' .
docker run -itd --name yoyo_web -h yoyo_web --network yoyo -v ${uploads_path}:/storage/web_code/uploads -p 8082:82 -p 8081:8081 -e TZ="Asia/Shanghai" yoyo_web_image
```

rebuild.sh（可不修改，也可根据实际需要修改）

```shell
#!/bin/bash

docker rm -f yoyo_web
docker rmi -f yoyo_web_image
base_path=$(cd `dirname $0`; pwd)
uploads_path="${base_path}/uploads"
mkdir ${uploads_path}
chmod u+x ${base_path}/unzip.sh
${base_path}/unzip.sh
docker build -t 'yoyo_web_image' .
docker run -itd --name yoyo_web -h yoyo_web --network yoyo -v ${uploads_path}:/storage/web_code/uploads -p 8082:82 -p 8081:8081 -e TZ="Asia/Shanghai" yoyo_web_image
```

如果没有配置好自启动，也可以在Shell脚本里加上在容器外执行容器内命令的方式启动，但这种方式重启容器后就又需要手动开启了，因此不推荐使用。

```shell
docker exec -itd `docker ps |grep yoyo_web |awk '{print $1}'` /bin/bash -c 'java -jar -Duser.timezone=GMT+8 /storage/web_manage-0.0.1.jar > /storage/web_manage-0.0.1.log 2>&1'
docker exec -it `docker ps |grep yoyo_web |awk '{print $1}'` /bin/bash -c 'tail -fn 100 /storage/web_manage-0.0.1.log'
```

注意：docker exec -it 这里必须不带上d，否则看不到输出结果。

#### 3.7.4 打包镜像并创建容器启动项目

1）初次部署

```shell
切换到工作目录
$ chmod u+x unzip.sh build.sh rebuild.sh
$ ./build.sh
```

启动成功后，项目就部署好了，Chrome访问 `IP:8082`地址即可访问前端页面，8081端口是留给后端的。

2）后续更新

```
切换到工作目录
把 dist.zip 和 web_manage-0.0.1.jar 更换掉，然后执行 rebuild.sh 脚本即可
```

### 3.8 将已有镜像容器部署到其他服务器

#### 3.8.1 整体流程概述

步骤简述：将容器保存成镜像 / 使用Dockerfile构建镜像——将镜像打成tar包，压缩成tar.gz——使用scp命令将文件传输到目标服务器——将tar.gz解压成tar包，载入镜像——docker run 运行镜像创建容器

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

#### 3.8.3 需要注意的问题

[1] 通过容器打Docker镜像要比Dockerfile生成的包要大（里面有很多没用的东西），尽量使用后者，但一些需要离线部署并且需要自动下载算法模型的除外。

[2] 直接对设置挂载的容器打包，会导致通过挂载加进去的文件并没有加进去（打出来的镜像不包含挂载进去的文件），可以再创建个不挂载的容器，把文件替换进去，再对这个不挂载的容器打包。

[3] Docker挂载目录权限问题：容器外啥权限，里面就啥权限。不管里面改权限还是外面改权限，都是同步动的，其实就是同一个文件，这个文件是在容器外的。

### 3.9 使用Docker Buildx构建跨架构镜像

#### 3.9.1 服务器架构导致的镜像兼容问题

情景描述：由于客户涉密环境不能联网，因此提前准备了离线镜像。但由于我们是使用的x86架构服务器，而客户是使用的是国产arm架构服务器，部署不兼容。

报错信息：WARNING: The reguested image's platform (linux/and64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested.

解决方案：使用Docker Buildx进行跨平台构建或者找一台相同架构的服务器进行构建，可以使用 arch 命令查看硬件架构。

#### 3.9.2 构建跨架构镜像进行部署

大多数情况下，如果 Docker 版本是 19.03 或更高，Buildx 应该已经预装在 Docker 中了，可通过以下命令检查 Buildx 是否可用。

```shell
$ docker buildx version
```

之后，需要切换到带有Dockerfile的原始源码目录，通过Docker Buildx构建跨架构镜像，再用它进行部署。

```shell
$ docker buildx create --name mymultiarchbuilder --use
$ docker buildx build --platform linux/arm64 -t project-arm64:v1.0 . --load       // 构建跨架构镜像的命令
$ docker save -o project-v1.0-arm64.tar project-arm64:v1.0
$ docker load -i project-v1.0-arm64.tar
$ docker run -itd --name project -p 8081:80 project-arm64:v1.0 
$ docker update project --restart=always
```

注意：这种方式是直接使用Dockerfile构建的镜像，如果有那种首次使用时自动下载镜像的情况，需要一并在Dockerfile里将其放进去。

## 4. 搭建Harbor私有Docker镜像仓库

### 4.1 镜像仓库及Harbor概述

#### 4.1.1 镜像仓库

云原生技术的兴起为企业数字化转型带来新的可能。作为云原生的要素之一，带来更为轻量级虚拟化的容器技术具有举足轻重的推动作用。其实很早之前，容器技术已经有所应用，而 Docker 的出现和兴起彻底带火了容器。其关键因素是 Docker 提供了使用容器的完整工具链，使得容器的上手和使用变得非常简单。工具链中的一个关键，就是定义了新的软件打包格式——容器镜像。镜像包含了软件运行所需要的包含基础 OS 在内的所有依赖，推送至运行时可直接启动。从镜像构建环境到运行环境，镜像的快速分发成为硬需求。同时，大量构建以及依赖的镜像的出现，也给镜像的维护管理带来挑战，镜像仓库的出现成为必然。

![镜像仓库](https://image.eula.club/quantum/镜像仓库.png)

镜像构建之后可以推送至镜像仓库储存和管理，在有应用运行需求时，从仓库拉取特定的应用镜像来运行。镜像仓库作为镜像的分发媒介，可以实现特定的管理和访问控制机制。仓库作为镜像传输流动的主要媒介，成为云原生应用平台运转的核心要件。Docker 开源了其 registry 实现,  目前已经成为 CNCF 的沙箱项目Distribution。不过，Distribution 项目仅仅实现了对镜像存储的支持，对企业级的一些管理诉求并无法提供支持。为了实现企业级镜像仓库的支持，Harbor 项目应运而生。

#### 4.1.2 Harbor基本介绍

**[1] Harbor发展历史**

Harbor Registry 由 VMware 公司中国研发中心云原生实验室原创，并于 2016 年 3 月开源。Harbor 在 Docker Distribution的基础上增加了企业用户必需的权限控制、镜像签名、安全漏洞扫描和远程复制等重要功能，还提供了图形管理界面及面向国内用户的中文支持，开源后迅速在中国开发者和用户社区流行，成为中国云原生用户的主流容器镜像仓库。

2018年7月，VMware 捐赠 Harbor 给 CNCF，使Harbor成为社区共同维护的开源项目，也是首个源自中国的 CNCF 项目。在加入 CNCF 之后，Harbor 融合到全球的云原生社区中，众多的合作伙伴、用户和开发者都参与了Harbor项目的贡献，数以千计的用户在生产系统中部署和使用 Harbor，Harbor 每个月的下载量超过3万次。2020 年 6 月，Harbor 成为首个中国原创的 CNCF 毕业项目。

**[2] Harbor是什么**

Harbor是一个用于存储和分发Docker镜像的企业级Registry服务器，虽然Docker官方也提供了公共的镜像仓库，但是从安全和效率等方面考虑，部署企业内部的私有环境Registry是非常必要的，Harbor和docker中央仓库的关系，就类似于nexus和Maven中央仓库的关系，Harbor除了存储和分发镜像外还具有用户管理，项目管理，配置管理和日志查询，高可用部署等主要功能。

项目地址：[https://github.com/goharbor/harbor/](https://github.com/goharbor/harbor/)

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

#### 4.2.2 下载安装包并修改配置文件

```shell
$ cd /root/Harbor
$ wget https://github.com/goharbor/harbor/releases/download/v2.7.0/harbor-offline-installer-v2.7.0.tgz
$ tar -xvf harbor-offline-installer-v2.7.0.tgz
$ cd harbor
$ cp -ar harbor.yml.tmpl harbor.yml      # 复制配置文件并改名为harbor.yml
$ vim harbor.yml
```

修改了的配置如下，https的配置整个注释掉，其余的配置项没动。

```
hostname: 111.111.111.111
http:
  port: 10010
harbor_admin_password: your_harbor_admin_password
database:
  password: your_db_password
data_volume: /data/harbor
```

注：hostname设置成你的服务器IP（这里脱敏成111.111.111.111），http的端口我这里改成了10010，harbor_admin_password是你的harbor管理员登录密码，database我只改了数据库密码，data_volume改了一下挂载路径。配置文件里有详细的注释说明，如果要改其他的，根据说明进行修改即可。

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

#### 4.2.4 访问Harbor管理面板

访问地址：`http://ip:port`   用户名：admin 密码：your_harbor_admin_password

![Harbor管理面板](https://image.eula.club/quantum/Harbor管理面板.png)

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

#### 4.3.3 拉取Docker镜像

这里我换了一台服务器，拉取刚刚上传的docker镜像，在这台服务器上，仍要按照4.1节修改一下docker配置并登录。

在镜像详细信息界面，可以获取到镜像拉取命令。

![获取镜像拉取命令](https://image.eula.club/quantum/获取镜像拉取命令.png)

docker login之后，将镜像拉取命令复制到终端即可。

![从Harbor仓库拉取镜像](https://image.eula.club/quantum/从Harbor仓库拉取镜像.png)

## 5. Docker搭建中间件服务

### 5.1 Docker-MySQL环境搭建

#### 5.1.1 拉取镜像创建容器

```shell
$ docker pull mysql:5.7
$ docker run -p 3306:3306 --name mysql \
-e TZ=Asia/Shanghai \
-v /root/docker/mysql/conf:/etc/mysql/conf.d \
-v /root/docker/mysql/logs:/var/log/mysql \
-v /root/docker/mysql/data:/var/lib/mysql \
-e MYSQL_ROOT_PASSWORD=[password] \
-d mysql:5.7 --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci
$ docker update mysql --restart=always
```

命令解释说明：

```
-p 3306:3306：将主机的3306端口映射到docker容器的3306端口。
--name mysql：运行服务名字
-e TZ=Asia/Shanghai：时区是使用了世界标准时间(UTC)。因为在中国使用，所以需要把时区改成东八区的。
-e MYSQL_ROOT_PASSWORD=[password]：初始化 root 用户的密码。
-d mysql:5.7 : 后台程序运行mysql5.7
--character-set-server=utf8mb4 ：设置字符集
--collation-server=utf8mb4_unicode_ci：设置校对集
```

说明：如果是挂载已有的其他服务器数据，可能会出现用户权限问题，如果网络是通的，建议使用Navicat的数据传输功能（工具——数据传输——配置源与目标链接——选择需要传输的数据表即可），数据传输速度很快。

#### 5.1.2 创建数据库及用户

在本地使用Navicat工具使用root用户连接上该数据库，使用如下四条命令创建数据库及用户。

```shell
--创建新的数据库，并设置数据库编码
$ CREATE DATABASE 你的数据库名 DEFAULT CHARSET=utf8 DEFAULT COLLATE utf8_unicode_ci;

--创建新的用户
$ CREATE USER '你的用户名'@'你的服务器IP' IDENTIFIED BY '你的密码';

--把数据库的管理权限给予刚刚创建的MySQL用户
$ GRANT ALL PRIVILEGES ON *.* TO '你的用户名'@'%' IDENTIFIED BY '你的密码' WITH GRANT OPTION;

--刷新权限，使用设置生效
$ FLUSH PRIVILEGES;
```

注：如果连接数据库时出现`Access denied for user '用户名'@'某IP' (using password: YES)`问题，则是第三句授权出了问题，你的本地外网IP被拦截了，那个'%'代表的是访问IP不受限制。

### 5.2 Docker-Nginx环境搭建

#### 5.2.1 拉取镜像创建容器

```shell
$ docker pull nginx
$ docker run -d --name nginx -p 9999:80 nginx:latest
```

#### 5.2.2 修改Nginx配置文件

[1] 每次都进入到nginx容器内部修改--适用于临时修改情况

Step1：进入到nginx容器内部

```shell
$ docker exec -it [CONTAINER ID/NAMES] /bin/bash
```

命令解释说明：

```
- exec 命令代表附着到运行着的容器内部
- -it 是 -i 与 -t两个参数合并写法，-i -t 标志着为我们指定的容器创建了TTY并捕捉了STDIN
- [CONTAINER ID/NAMES] 是我们要进入的容器ID（可以省略后面的部分，能唯一区分即可）或名字
- /bin/bash 指定了执行命令的shell
```

进入到nginx容器内部后，我们可以`cd /etc/nginx`，可以看到相关的nginx配置文件都在`/etc/nginx`目录下。而nginx容器内的默认首页html文件目录为`/usr/share/nginx/html`，日志文件位于`/var/log/nginx`。执行`exit`命令可以从容器内部退出。

[2] 将nginx容器内部配置文件挂载到主机--适用于频繁修改情况

Step1：创建挂载目录

这里我为了跟mysql的挂载目录保持一致，也使用了自己创建的`/root/docker`目录（一般放在`/mnt`目录，这个是Linux专门的挂载目录）

```shell
$ cd /root/docker
$ mkdir -p ./nginx/{conf,html,logs}
```

Step2：将容器内的`nginx.conf`与`default.conf`文件分别拷贝到主机`/root/docker/nginx`与`/root/docker/nginx/conf`目录下

```shell
$ cd /root/docker/nginx
$ docker cp [CONTAINER ID/NAMES]:/etc/nginx/nginx.conf ./ 
$ docker cp [CONTAINER ID/NAMES]:/etc/nginx/conf.d/default.conf ./conf/
```

命令解释说明：

```
- [CONTAINER ID/NAMES] 是我们要进入的容器ID（可以省略后面的部分，能唯一区分即可）或名字
- /etc/nginx/nginx.conf 是容器内部nginx.conf的路径
```

Step3：重新创建容器实例

先停止、删除原有的容器实例

```shell
$ docker stop [CONTAINER ID/NAMES]              # 停止指定docker容器实例
$ docker rm -f [CONTAINER ID/NAMES]             # 强制删除指定docker容器实例（删除前需先停止实例）
```

再重新创建新的容器实例

```shell
$ docker run -d --name nginx -p 9999:80 -v /root/docker/nginx/nginx.conf:/etc/nginx/nginx.conf -v /root/docker/nginx/logs:/var/log/nginx -v /root/docker/nginx/html:/usr/share/nginx/html -v /root/docker/nginx/conf:/etc/nginx/conf.d --privileged=true [image-id]
```

命令解释说明：

```
-v 挂载目录，表示将主机目录与容器目录之间进行共享
--privileged=true 容器内部对挂载的目录拥有读写等特权
```

Step4：设置开机自启

```shell
$ docker update nginx --restart=always
```

#### 5.2.3 测试Nginx环境

Step1：新建测试用的`index.html`文件（不配置会出现403报错）

```shell
$ cd /root/docker/nginx/html
$ touch index.html
$ echo "hello world" >> index.html
```

Step2：打开Chrome浏览器，地址输入`IP:port`，出现`hello world`即配置成功。

附：Nginx的常用管理命令

```shell
$ nginx -t                  # 检查nginx配置的语法是否正确
$ nginx -s reload           # 重新加载配置文件，而nginx服务不会中断
```

#### 5.2.4 搭建过程踩的坑

**[1] 非安全端口问题**

情景描述：搭建完的nginx在本地用`curl IP:port`可以访问（当然在nginx容器里使用`curl 127.0.0.1`也是可以访问的），但在浏览器内找不到该地址（提示“该网页可能已永久移到新的网址”）。

错误原因：创建nginx容器时误用了Chrome浏览器的默认非安全端口，访问会直接被拦截，因而出现了该情况。Chrome 默认非安全端口列表如下：

```
1, 7, 9, 11, 13, 15, 17, 19, 20, 21, 22, 23, 25, 37, 42, 43, 53, 77, 79, 87, 95, 101, 102, 103, 104, 109, 110, 111, 113, 115, 117, 119, 123, 135, 139, 143, 179, 389, 465, 512, 513, 514, 515, 526, 530, 531, 532, 540, 556, 563, 587, 601, 636, 993, 995, 2049, 3659, 4045, 6000, 6665, 6666, 6667, 6668, 6669
```

解决办法：删掉nginx容器重新搭建，创建nginx容器时避开Chrome浏览器的默认非安全端口即可。

**[2] 访问资源403问题**

情景描述：部署的项目有上传文件功能，上传成功后要在网页上进行显示，但该资源却403无权限访问，改目录权限777虽然可以临时使其可以访问，但后续上传的文件又权限不足。

错误原因：启动nginx的用户没有该资源的访问权限

解决办法：修改nginx的启动用户为root，访问权限就有了。

```shell
$ vim /etc/nginx/nginx.conf    // 把第一行的用户配置改成“user  root;”
```

### 5.3 Docker-Oracle环境搭建

#### 5.3.1 拉取镜像并运行容器

```shell
$ docker pull registry.cn-hangzhou.aliyuncs.com/helowin/oracle_11g 
$ docker run -d -p 1521:1521 --name oracle11g registry.cn-hangzhou.aliyuncs.com/helowin/oracle_11g
$ docker update oracle11g --restart=always
```

#### 5.3.2 进入容器进行配置

Step1：进入容器，切换到root用户

```shell
$ docker exec -it oracle11g /bin/bash  # 进入oracle11g容器
$ su root  # 默认密码：helowin （可通过passwd命令修改成自己的）
```

Step2：配置环境变量

```shell
$ vi /etc/profile
```

在末尾加上：

```
export ORACLE_HOME=/home/oracle/app/oracle/product/11.2.0/dbhome_2
export ORACLE_SID=helowin
export PATH=$ORACLEHOME/bin:PATH
```

Step3：创建软连接，并用oracle用户登录

```shell
$ ln -s $ORACLE_HOME/bin/sqlplus /usr/bin   # 创建软链接
$ su - oracle    # 切换到oracle用户
```

#### 5.3.3 修改密码创建用户

```shell
$ sqlplus /nolog  #
$ conn / as sysdba  # 以dba身份登录

# 修改用户system、sys用户的密码 
$ alter user system identified by system;   
$ alter user sys identified by sys;
$ ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;
```

#### 5.3.4 用可视化工具连接

在PLSQL里使用 system/system 账号连接，注意服务名不是orcl，而是helowin。

具体可查看tnsnames.ora文件的配置：

```shell
$ vi /home/oracle/app/oracle/product/11.2.0/dbhome_2/network/admin/tnsnames.ora
```

### 5.4 Docker-MongoDB环境搭建

#### 5.4.1 拉取镜像并运行容器

这个mongodb未设置账号密码，仅限内网测试使用。

```shell
$ docker pull mongo:latest
$ mkdir -p /root/docker/mongodb/data
$ docker run -itd --name mongodb -v /root/docker/mongodb/data:/data/db -p 27017:27017 mongo:latest
```

#### 5.4.2 用可视化工具连接

使用Navicat工具连接查看，账号密码验证空着即可，可使用如下命令查看版本。

```shell
$ db.version();
```

### 5.5 Docker-SQLServer环境搭建

#### 5.5.1 拉取镜像并运行容器

```shell
$ docker run --name sqlserver -d \
-e 'ACCEPT_EULA=Y' \
-e 'SA_PASSWORD=your_password' \
-p 1433:1433  \
mcr.microsoft.com/mssql/server:2019-latest
```

注意：SQLServer默认需要2gb内存，不足的话启动不起来，密码设置需要是个强密码。

#### 5.5.2 用可视化工具连接

使用Navicat进行连接即可，默认用户sa，密码是部署时设置的。

### 5.6 Docker-PostgreSQL环境搭建

#### 5.6.1 拉取镜像并运行容器

```shell
$ docker run -d \
  --name test_postgres \
  --restart always \
  -p 5432:5432 \
  -e POSTGRES_USER=test \
  -e POSTGRES_PASSWORD=your_password \
  -e POSTGRES_DB=testdb \
  postgres:11
```

#### 5.6.2 用可视化工具连接

使用Navicat进行连接即可。

### 5.7 Docker-RabbitMQ环境搭建

#### 5.7.1 拉取镜像并运行容器

```shell
$ docker pull rabbitmq:3.8-management
$ docker run --name rabbitmq -d -p 15672:15672 -p 5672:5672 rabbitmq:3.8-management
```

注：默认RabbitMQ镜像是不带web端管理插件的，所以指定了镜像tag为3.8-management，表示下载包含web管理插件版本镜像。

#### 5.7.2 RabbitMQ创建用户并可视化查看

用Chrome访问`http://ip:15672`即可访问RabbitMQ的Web端管理界面，默认用户名和密码都是guest，出现如下界面代表已经成功了。

![RabbitMQ](https://image.eula.club/quantum/RabbitMQ.png)

默认的 guest 账户有访问限制，只能通过本地网络访问，远程网络访问受限，所以在使用时我们一般另外添加用户。

```shell
$ docker exec -i -t rabbitmq  bin/bash  
$ rabbitmqctl add_user root 123456   // 添加用户（实际密码设置复杂一些）
$ rabbitmqctl set_permissions -p / root ".*" ".*" ".*"   // 赋予root用户所有权限
$ rabbitmqctl set_user_tags root administrator           // 赋予root用户administrator角色
$ rabbitmqctl list_users  // 查看所有用户即可看到root用户已经添加成功
$ exit 
```

### 5.8 Docker-Kafka环境搭建

以下使用 Docker Compose 搭建单机版 Kafka 服务、集群版Kafka，搭建Docker Compose环境见本文5.3节

#### 5.8.1 部署单机版Kafka

**[1] 部署ZooKeeper及单机版 Kafka 服务**

kafka的运行依赖于zookeeper，因而编写zookeeper与kafka的编排文件docker-compose.yml内容如下：

```yml
version: '3.2'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    restart: always
  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://IP:9092
      - KAFKA_LISTENERS=PLAINTEXT://:9092
    volumes:
      - ./docker.sock:/var/run/docker.sock
    restart: always
```

注：KAFKA_ADVERTISED_LISTENERS 填写为 `PLAINTEXT://IP:9092`，这里的 IP 填写成你的公网 IP，如果没带上这个的话，PC是无法连接到服务器上的 kafka 服务的。这里搭建的 kafka 服务仅用于测试，没有设置用户名及密码，勿用于公网生产环境。

编写完毕后，在该文件下的目录下依次执行下面两条命令即可构建好zookeeper和kafka容器：

```shell
$ docker-compose build     // 构建镜像
$ docker-compose up -d     // 运行容器
```

配置文件目录：`/opt/kafka_2.13-2.8.1/config`

**[2] 验证Kafka是否搭建成功**

进入到kafka容器中 并创建topic生产者，执行如下命令：

```shell
$ docker exec -it kafka /bin/bash
$ cd /opt/kafka_2.13-2.8.1/bin/
$ ./kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 8 --topic test
$ ./kafka-console-producer.sh --broker-list localhost:9092 --topic test
```

执行上述命令后，另起一个窗口，执行如下命令，创建kafka消费者消费消息。

```shell
$ docker exec -it kafka /bin/bash
$ cd /opt/kafka_2.13-2.8.1/bin/
$ ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
```

执行完上诉命令后，在生产者窗口中输入任意内容回车，即可在消费者的窗口查看到消息。

注：kafka_2.13-2.8.1的含义为，2.13是Scala版本，2.8.1是Kafka版本。

#### 5.8.2 部署集群版Kafka

把编排文件docker-compose.yml修改成如下内容，即可部署集群版Kafka（如下是3个节点，如果需要更多可以在后面继续追加）

```yml
version: '3.3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - 2181:2181
    volumes:
      - ./data/zookeeper/data:/data
      - ./data/zookeeper/datalog:/datalog
      - ./data/zookeeper/logs:/logs
    restart: always
  kafka1:
    image: wurstmeister/kafka
    depends_on:
      - zookeeper
    container_name: kafka1
    ports:
      - 9092:9092
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://IP:9092
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_LOG_DIRS: /data/kafka-data
      KAFKA_LOG_RETENTION_HOURS: 168
    volumes:
      - ./data/kafka1/data:/data/kafka-data
    restart: unless-stopped  
  kafka2:
    image: wurstmeister/kafka
    depends_on:
      - zookeeper
    container_name: kafka2
    ports:
      - 9093:9093
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://IP:9093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9093
      KAFKA_LOG_DIRS: /data/kafka-data
      KAFKA_LOG_RETENTION_HOURS: 168
    volumes:
      - ./data/kafka2/data:/data/kafka-data
    restart: unless-stopped
  kafka3:
    image: wurstmeister/kafka
    depends_on:
      - zookeeper
    container_name: kafka3
    ports:
      - 9094:9094
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://IP:9094
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9094
      KAFKA_LOG_DIRS: /data/kafka-data
      KAFKA_LOG_RETENTION_HOURS: 168
    volumes:
      - ./data/kafka3/data:/data/kafka-data
    restart: unless-stopped
```

#### 5.8.3 搭建SASL账号密码验证的Kafka

自0.9.0.0版本开始Kafka社区添加了许多功能用于提高Kafka的安全性，Kafka提供SSL或者SASL两种安全策略。SSL方式主要是通过CA令牌实现，此处主要介绍SASL方式。

新建一个目录，放置以下4个文件（需要改动的只有server_jaas.conf）

```shell
$ mkdir -p ./kafka-sasl/conf
```

zoo.cfg

```ini
# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial 
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between 
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just 
# example sakes.
dataDir=/opt/zookeeper-3.4.13/data
# the port at which the clients will connect
clientPort=2181
# the maximum number of client connections.
# increase this if you need to handle more clients
#maxClientCnxns=60
#
# Be sure to read the maintenance section of the 
# administrator guide before turning on autopurge.
#
# http://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
autopurge.snapRetainCount=3
# Purge task interval in hours
# Set to "0" to disable auto purge feature
autopurge.purgeInterval=1

authProvider.1=org.apache.zookeeper.server.auth.SASLAuthenticationProvider
requireClientAuthScheme=sasl
jaasLoginRenew=3600000
zookeeper.sasl.client=true
```

server_jaas.conf

```ini
Client {
    org.apache.zookeeper.server.auth.DigestLoginModule required
    username="admin"
    password="your_password";
};

Server {
    org.apache.zookeeper.server.auth.DigestLoginModule required
    username="admin"
    password="your_password"
    user_super="your_password"
    user_admin="your_password";
};

KafkaServer {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="admin"
    password="your_password"
    user_admin="your_password";
};

KafkaClient {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="admin"
    password="your_password";
};
```

log4j.properties

```properties
# Define some default values that can be overridden by system properties
zookeeper.root.logger=INFO, CONSOLE
zookeeper.console.threshold=INFO
zookeeper.log.dir=.
zookeeper.log.file=zookeeper.log
zookeeper.log.threshold=DEBUG
zookeeper.tracelog.dir=.
zookeeper.tracelog.file=zookeeper_trace.log

#
# ZooKeeper Logging Configuration
#

# Format is "<default threshold> (, <appender>)+

# DEFAULT: console appender only
log4j.rootLogger=${zookeeper.root.logger}

# Example with rolling log file
#log4j.rootLogger=DEBUG, CONSOLE, ROLLINGFILE

# Example with rolling log file and tracing
#log4j.rootLogger=TRACE, CONSOLE, ROLLINGFILE, TRACEFILE

#
# Log INFO level and above messages to the console
#
log4j.appender.CONSOLE=org.apache.log4j.ConsoleAppender
log4j.appender.CONSOLE.Threshold=${zookeeper.console.threshold}
log4j.appender.CONSOLE.layout=org.apache.log4j.PatternLayout
log4j.appender.CONSOLE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n

#
# Add ROLLINGFILE to rootLogger to get log file output
#    Log DEBUG level and above messages to a log file
log4j.appender.ROLLINGFILE=org.apache.log4j.RollingFileAppender
log4j.appender.ROLLINGFILE.Threshold=${zookeeper.log.threshold}
log4j.appender.ROLLINGFILE.File=${zookeeper.log.dir}/${zookeeper.log.file}

# Max log file size of 10MB
log4j.appender.ROLLINGFILE.MaxFileSize=10MB
# uncomment the next line to limit number of backup files
log4j.appender.ROLLINGFILE.MaxBackupIndex=10

log4j.appender.ROLLINGFILE.layout=org.apache.log4j.PatternLayout
log4j.appender.ROLLINGFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n


#
# Add TRACEFILE to rootLogger to get log file output
#    Log DEBUG level and above messages to a log file
log4j.appender.TRACEFILE=org.apache.log4j.FileAppender
log4j.appender.TRACEFILE.Threshold=TRACE
log4j.appender.TRACEFILE.File=${zookeeper.tracelog.dir}/${zookeeper.tracelog.file}

log4j.appender.TRACEFILE.layout=org.apache.log4j.PatternLayout
### Notice we are including log4j's NDC here (%x)
log4j.appender.TRACEFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L][%x] - %m%n
```

configuration.xsl

```xml
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>
<xsl:template match="configuration">
<html>
<body>
<table border="1">
<tr>
 <td>name</td>
 <td>value</td>
 <td>description</td>
</tr>
<xsl:for-each select="property">
<tr>
  <td><a name="{name}"><xsl:value-of select="name"/></a></td>
  <td><xsl:value-of select="value"/></td>
  <td><xsl:value-of select="description"/></td>
</tr>
</xsl:for-each>
</table>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
```

然后再创建一个 Docker Compose 编排文件。

docker-compose.yml

```yml
version: "3"

services:

  zookeeper:
    image: wurstmeister/zookeeper
    hostname: zookeeper_sasl
    container_name: zookeeper_sasl
    restart: always
    ports:
      - 2181:2181
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      SERVER_JVMFLAGS: -Djava.security.auth.login.config=/opt/zookeeper-3.4.13/secrets/server_jaas.conf
    volumes:
      - ./kafka-sasl/conf:/opt/zookeeper-3.4.13/conf
      - ./kafka-sasl/conf/:/opt/zookeeper-3.4.13/secrets/ 

  kafka:
    image: wurstmeister/kafka:2.11-0.11.0.3
    restart: always
    hostname: broker
    container_name: kafka_sasl
    depends_on:
      - zookeeper
    ports:
      - 9092:9092
    environment:
      KAFKA_BROKER_ID: 0
      KAFKA_ADVERTISED_LISTENERS: SASL_PLAINTEXT://IP:9092
      KAFKA_ADVERTISED_PORT: 9092 
      KAFKA_LISTENERS: SASL_PLAINTEXT://0.0.0.0:9092
      KAFKA_SECURITY_INTER_BROKER_PROTOCOL: SASL_PLAINTEXT
      KAFKA_PORT: 9092 
      KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: PLAIN
      KAFKA_SASL_ENABLED_MECHANISMS: PLAIN
      KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.auth.SimpleAclAuthorizer
      KAFKA_SUPER_USERS: User:admin
      KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "true" #设置为true，ACL机制为黑名单机制，只有黑名单中的用户无法访问，默认为false，ACL机制为白名单机制，只有白名单中的用户可以访问
      KAFKA_ZOOKEEPER_CONNECT: zookeeper_sasl:2181
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_OPTS: -Djava.security.auth.login.config=/opt/kafka/secrets/server_jaas.conf
    volumes:
      - ./kafka-sasl/conf/:/opt/kafka/secrets/
```

编写完毕后，在该文件下的目录下依次执行下面两条命令即可构建好zookeeper和kafka容器：

```shell
$ docker-compose build     // 构建镜像
$ docker-compose up -d     // 运行容器
```

代码请求测试：

```python
# -*- coding: utf-8 -*-

import time
import json
from datetime import datetime
from kafka import KafkaProducer


def producer_event(server_info):
    producer = KafkaProducer(bootstrap_servers=server_info,
                             security_protocol='SASL_PLAINTEXT',
                             sasl_mechanism='PLAIN',
                             sasl_plain_username='admin',
                             sasl_plain_password='your_password')
    topic = "test_kafka_topic"
    print("kafka连接成功")
    for i in range(7200):
        data = {
            "name": "hello world"
        }
        data_json = json.dumps(data)
        producer.send(topic, data_json.encode()).get(timeout=30)
        print("数据推送成功,当前时间为：{},数据为：{}".format(datetime.now(), data_json))
        time.sleep(1)
    producer.close()


server = "IP:9092"
producer_event(server)
```

#### 5.8.4 搭建kafka管理平台

**[1] kafka-map**

kafka-map是一个美观简洁且强大的kafka web管理工具。

项目地址：[https://github.com/dushixiang/kafka-map](https://github.com/dushixiang/kafka-map)

```shell
docker run -d \
    -p 8080:8080 \
    -v /root/kafka-map/data:/usr/local/kafka-map/data \
    -e DEFAULT_USERNAME=your_user \
    -e DEFAULT_PASSWORD=your_password \
    --name kafka-map \
    --restart always dushixiang/kafka-map:latest
```

用Chrome访问`http://ip:8080`即可访问 kafka-map 管理界面

![kafka-map](https://image.eula.club/quantum/kafka-map.png)

注：如果配置了4.6.3节的SASL账号密码验证，这里安全验证选择“SASL_PLAINTEXT”，协议机制选择“PLAIN”（虽然连上了，但一些功能不好使了）

**[2] kafka-manager**

kafka-manager是目前最受欢迎的kafka集群管理工具，最早由雅虎开源，用户可以在Web界面执行一些简单的集群管理操作。

```shell
$ docker pull sheepkiller/kafka-manager
$ docker run --name kafka-manager -itd -p 9000:9000 -e ZK_HOSTS="IP:2181" sheepkiller/kafka-manager  // 把IP处换成你的服务器IP地址
```

用Chrome访问`http://ip:9000`即可访问 kafka-manager 管理界面

![kafka管理面板-1](https://image.eula.club/quantum/kafka管理面板-1.png)

连接kafka：点击Cluster，选择Add Cluster，填写Cluster Name（随便起）、Cluster Zookeeper Hosts（zookeeper地址）保存即可。

![kafka管理面板-2](https://image.eula.club/quantum/kafka管理面板-2.png)

**[3] KnowStreaming**

Know Streaming是一套云原生的Kafka管控平台，脱胎于众多互联网内部多年的Kafka运营实践经验，专注于Kafka运维管控、监控告警、资源治理、多活容灾等核心场景。在用户体验、监控、运维管控上进行了平台化、可视化、智能化的建设，提供一系列特色的功能，极大地方便了用户和运维人员的日常使用。

项目地址：[https://github.com/didi/KnowStreaming](https://github.com/didi/KnowStreaming)

官方的一键脚本会将所部署机器上的 MySQL、JDK、ES 等进行删除重装。因此不建议使用它进行部署，下面采用手动部署的方式。

Step0：准备MySQL、ElasticSearch、JDK等基础环境

| 软件名        | 版本要求     |
| ------------- | ------------ |
| MySQL         | v5.7 或 v8.0 |
| ElasticSearch | v7.6+        |
| JDK           | v8+          |

注：这些环境我之前都用Docker搭建过了，我的版本是MySQL5.7、ElasticSearch7.16.2（KnowStreaming目前不支持使用设置了密码的ES，如果设置了就另外再搭一个吧）、JDK8（官方推荐JDK11，但是JDK8也可以用）

Step1：下载安装包并解压

```shell
// 下载安装包
$ wget https://s3-gzpu.didistatic.com/pub/knowstreaming/KnowStreaming-3.0.0-beta.1.tar.gz
// 解压安装包到指定目录
$ tar -zxf KnowStreaming-3.0.0-beta.1.tar.gz -C /data/
```

Step2：导入MySQL数据和ES索引结构

```shell
$ cd /data/KnowStreaming

用Navicat创建数据库，create database know_streaming;
打开./init/sql目录，然后执行里面的这5个sql文件，ddl-ks-km.sql、ddl-logi-job.sql、ddl-logi-security.sql、dml-ks-km.sql、dml-logi.sql

打开 ./bin目录，修改一下init_es_template.sh文件里的ES连接信息，执行该脚本。
```

Step3：修改配置文件

```shell
$ cd /data/KnowStreaming
$ vim ./conf/application.yml

修改监听端口、MySQL及ES连接信息
```

Step4：启动项目

在bin目录有官方提供的启动脚本，但我这里因为没用它的那个方式进行搭建JDK，执行该脚本时报错，这里就不用它了。该项目就是个很常规的Java项目，自己启动就行了。

我这里把conf目录的配置文件都剪切到了libs目录，将其与jar包放置在一起，在bin目录写了个start.sh脚本用于启动程序。

```shell
#!/bin/bash

#define default variable
app_path="/data/KnowStreaming/libs"
app_log="/data/KnowStreaming/app.log"

if [ -e $app_log ]; then
	touch ${app_log}
fi

#goto directory
cd ${app_path}

#start app
nohup java -jar *.jar  1>${app_log} &
tail -fn 100 ${app_log}
exit 0
```

启动后，访问`http://ip:port`地址访问即可，默认账号及密码：`admin` / `admin2022_` 进行登录（另注：`v3.0.0-beta.2`版本开始，默认账号密码为`admin` / `admin`）。若要停止该项目，`lsof -i:port`搭配 `kill -9 PID`使用即可。

![KnowStreaming](https://image.eula.club/quantum/KnowStreaming.jpeg)

#### 5.8.5 不停机查看及修改消息保留时长

需求情景：生产者程序将处理后的数据存入Kafka，但消费者的处理能力不行，数据有大量积压。磁盘还有大量空间，为了防止丢数据，需要在不停机的情况下修改kafka的消息保留时长。

基于时间保留：通过保留期属性，消息就有了TTL（time to live 生存时间）。到期后，消息被标记为删除，从而释放磁盘空间。对于kafka主题中所有消息具有相同的生存时间，但可以在创建主题之前设置属性，或对已存在的主题在运行时修改属性。Kafka支持配置保留策略，可以通过以下三个时间配置属性中的一个来进行调整：`log.retention.hours`、`log.retention.minutes`、`log.retention.ms`，Kafka用更高精度值覆盖低精度值，所以log.retention.ms具有最高的优先级。

以4.6.3节搭建的kafka为例，演示如何查看及不停机修改消息保留时长。

[1] 查看全局的消息保留时长

```shell
$ docker exec -it kafka_sasl /bin/bash
$ cd  /opt/kafka_2.11-0.11.0.3
$ grep -i 'log.retention.[hms].*\=' config/server.properties
log.retention.hours=168
```

[2] 不停机修改某个Topic的消息保留时长并查看

```shell
$ docker exec -it kafka_sasl /bin/bash
$ cd  /opt/kafka_2.11-0.11.0.3/bin
$ ./kafka-configs.sh --zookeeper zookeeper_sasl:2181 --alter --entity-name yoyo_admin_topic --entity-type topics --add-config retention.ms=60000
Completed Updating config for entity: topic 'yoyo_admin_topic'.
$ ./kafka-topics.sh --describe --zookeeper zookeeper_sasl:2181 --topic yoyo_admin_topic
Topic:yoyo_admin_topic  PartitionCount:1        ReplicationFactor:1     Configs:retention.ms=60000
        Topic: yoyo_admin_topic Partition: 0    Leader: 0       Replicas: 0     Isr: 0
```

注意事项：

- 需要修改的地方：将`zookeeper_sasl:2181`换成实际的zookeeper地址，将`yoyo_admin_topic`换成实际的topic，为了快速看到效果，保留时长仅设置了60000ms，正式修改按照实际的来。
- 测试流程：提前在topic里写入数据，然后修改topic的消息保留时长并查看，1分钟后去查看该topic的消息是否还存在，发现消息已经被删除了。

#### 5.8.6 Kafka分区数应设置多少及默认配置

kafka的每个topic都可以创建多个partition，理论上partition的数量无上限。通常情况下，越多的partition会带来越高的吞吐量，但是同时也会给broker节点带来相应的性能损耗和潜在风险，虽然这些影响很小，但不可忽略，所以确定partition的数量需要权衡一些因素。

**[1] 越多的partition可以提供更高的吞吐量**

- 单个partition是kafka并行操作的最小单元。每个partition可以独立接收推送的消息以及被consumer消费，相当于topic的一个子通道，partition和topic的关系就像高速公路的车道和高速公路的关系一样，起始点和终点相同，每个车道都可以独立实现运输，不同的是kafka中不存在车辆变道的说法，入口时选择的车道需要从一而终。
- kafka的吞吐量显而易见，在资源足够的情况下，partition越多速度越快。这里提到的资源充足解释一下，假设我现在一个partition的最大传输速度为p，目前kafka集群共有三个broker，每个broker的资源足够支撑三个partition最大速度传输，那我的集群最大传输速度为3\*3\*p=9p。

**[2] 越多的分区需要打开更多的文件句柄**

- 在kafka的broker中，每个分区都会对照着文件系统的一个目录。
- 在kafka的数据日志文件目录中，每个日志数据段都会分配两个文件，一个索引文件和一个数据文件。因此，随着partition的增多，需要的文件句柄数急剧增加，必要时需要调整操作系统允许打开的文件句柄数。

**[3] 更多的分区会导致端对端的延迟**

- kafka端对端的延迟为producer端发布消息到consumer端消费消息所需的时间，即consumer接收消息的时间减去produce发布消息的时间。
- kafka在消息正确接收后才会暴露给消费者，即在保证in-sync副本复制成功之后才会暴露，瓶颈则来自于此。
- leader broker上的副本从其他broker的leader上复制数据的时候只会开启一个线程，假设partition数量为n，每个副本同步的时间为1ms，那in-sync操作完成所需的时间即`n * 1ms`，若n为10000，则需要10秒才能返回同步状态，数据才能暴露给消费者，这就导致了较大的端对端的延迟。

**[4] 越多的partition意味着需要更多的内存**

- 在新版本的kafka中可以支持批量提交和批量消费，而设置了批量提交和批量消费后，每个partition都会需要一定的内存空间。
- 无限的partition数量很快就会占据大量的内存，造成性能瓶颈。假设每个partition占用的内存为100k，当partition为100时，producer端和consumer端都需要10M的内存；当partition为100000时，producer端和consumer端则都需要10G内存。

**[5] 越多的partition会导致更长时间的恢复期**

- kafka通过多副本复制技术，实现kafka的高可用性和稳定性。每个partition都会有多个副本存在于多个broker中，其中一个副本为leader，其余的为follower。
- kafka集群其中一个broker出现故障时，在这个broker上的leader会需要在其他broker上重新选择一个副本启动为leader，这个过程由kafka controller来完成，主要是从Zookeeper读取和修改受影响partition的一些元数据信息。
- 通常情况下，当一个broker有计划的停机，该broker上的partition leader会在broker停机前有次序的一一移走，假设移走一个需要1ms，10个partition leader则需要10ms，这影响很小，并且在移动其中一个leader的时候，其他九个leader是可用的。因此实际上每个partition leader的不可用时间为1ms。但是在宕机情况下，所有的10个partition
- leader同时无法使用，需要依次移走，最长的leader则需要10ms的不可用时间窗口，平均不可用时间窗口为5.5ms，假设有10000个leader在此宕机的broker上，平均的不可用时间窗口则为5.5s。
- 更极端的情况是，当时的broker是kafka controller所在的节点，那需要等待新的kafka leader节点在投票中产生并启用，之后新启动的kafka leader还需要从zookeeper中读取每一个partition的元数据信息用于初始化数据。在这之前partition leader的迁移一直处于等待状态。

可以在`/config/sever.properties`配置文件中，设置默认分区数，以后每次创建topic默认都是分区数。

以4.6.3节搭建的kafka为例，演示如何修改该配置：

```shell
$ docker exec -it kafka_sasl /bin/bash
$ cd /opt/kafka_2.13-2.8.1/bin/config
$ vi server.properties
```

sever.properties里有如下配置，默认分区数为1，我们可以根据自己需要进行修改

```properties
# The default number of log partitions per topic. More partitions allow greater
# parallelism for consumption, but this will also result in more files across
# the brokers.
num.partitions=10
```

之后退出容器并重启容器

```shell
$ exit
$ docker restart kafka_sasl
```

### 5.9 Docker-Redis环境搭建

#### 5.9.1 拉取镜像并运行容器

方案一：不使用配置文件启动

```shell
$ docker pull redis:3.2.8
$ docker run --name redis -p 6379:6379 -d redis:3.2.8 --requirepass "mypassword" --appendonly yes
$ docker update redis --restart=always
```

注：--requirepass用来设置密码，--appendonly yes用来设置AOF持久化。

方案二：使用redis.conf配置文件启动

redis容器里没有redis.conf文件，可以从 [https://redis.io/docs/management/config](https://redis.io/docs/management/config) 地址下载对应版本的配置文件，挂载进去。

```shell
$ docker pull redis:3.2.8
$ cd /root/redis
$ wget https://raw.githubusercontent.com/redis/redis/3.2/redis.conf
$ chmod 777 redis.conf
$ vim /root/redis/redis.conf

修改以下配置项
# bind 127.0.0.1 # 这行要注释掉，解除本地连接限制
protected-mode no # 默认yes，如果设置为yes，则只允许在本机的回环连接，其他机器无法连接。
daemonize no # 默认no 为不守护进程模式，docker部署不需要改为yes，docker run -d本身就是后台启动，不然会冲突
requirepass mypassword # 设置密码
appendonly yes # 持久化

$ docker run --name redis \
-p 6379:6379 \
-v /root/redis/redis.conf:/etc/redis/redis.conf \
-v /root/redis/data:/data \
-d redis:3.2.8 redis-server
$ docker update redis --restart=always
```

#### 5.9.2 Redis数据库的可视化连接

建议使用 [AnotherRedisDesktopManager](https://github.com/qishibo/AnotherRedisDesktopManager) 开源工具进行可视化连接和管理。

![ARDM工具](https://image.eula.club/quantum/ARDM工具.png)

### 5.10 Docker-ElasticSearch环境搭建

#### 5.10.1 拉取镜像并运行容器

**部署命令**

```shell
$ docker pull elasticsearch:7.16.2
$ docker run -d --name es \
-p 9200:9200 -p 9300:9300 \
-v /root/docker/es/data:/usr/share/elasticsearch/data \
-v /root/docker/es/config:/usr/share/elasticsearch/config \
-v /root/docker/es/plugins:/usr/share/elasticsearch/plugins \
-e "discovery.type=single-node" -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
elasticsearch:7.16.2
$ docker update es --restart=always
```

**进入容器进行配置**

```shell
$ docker exec -it es /bin/bash 
$ cd config
$ chmod o+w elasticsearch.yml
$ vi elasticsearch.yml
```

其中，在 elasticsearch.yml 文件的末尾添加以下三行代码（前两行如果开启则代表允许跨域，出于安全考虑把它关了，第三行开启xpack安全认证）

```yml
# http.cors.enabled: true
# http.cors.allow-origin: "*"
xpack.security.enabled: true    
```

然后把权限修改回来，重启容器，设置账号密码，浏览器访问`http://IP:9200`地址即可（用 elastic账号 和自己设置的密码登录即可）

```shell
$ chmod o-w elasticsearch.yml
$ exit
$ docker restart es
$ docker exec -it es /bin/bash 
$ ./bin/elasticsearch-setup-passwords interactive   // 然后设置一大堆账号密码
```

**注意事项**

1）Elasticsearch请选择7.16.0之后的版本，之前的所有版本都使用了易受攻击的 Log4j2版本，存在严重安全漏洞。  

2）`ES_JAVA_OPTS="-Xms1g -Xmx1g"`只是一个示例，内存设置的少了会导致数据查询速度变慢，具体设置多少要根据业务需求来定，一般而言公司的实际项目要设置8g内存以上。

**数据挂载遇到的问题**

[1] 数据锁定问题

- 报错信息：`java.lang.IllegalStateException: failed to obtain node locks, tried [[/usr/share/elasticsearch/data]] with lock id [0]; maybe these locations are not writable or multiple nodes were started without increasing `

- 产生原因：ES在运行时会在`/data/nodes/具体分片`目录里生成一个`node.lock`文件，由于我是在运行期scp过来的挂载数据，这个也被拷贝过来了，导致数据被锁定。

- 解决办法：删掉`/data/nodes/具体分片/node.lock`文件即可

[2] data目录权限问题

- 解决办法：进入容器内部，把data目录的权限设置为777即可

[3] 集群与单节点问题

- 解决办法：修改`config/elasticsearch.yml`里的集群配置即可，如果原来是集群，现在要单节点，就把集群配置去掉。

[4] 堆内存配置问题

- 报错信息：`initial heap size [8589934592] not equal to maximum heap size [17179869184]; this can cause resize pauses`

- 解决办法：-Xms 与 -Xmx 设置成相同大小的内存。

#### 5.10.2 可视化管理ES

**（1）使用Elasticvue浏览器插件**

可借助 [Elasticvue](https://chrome.google.com/webstore/detail/elasticvue/hkedbapjpblbodpgbajblpnlpenaebaa) Chrome插件实现ES数据库的可视化管理，支持所有版本ES。

![elasticvue](https://image.eula.club/quantum/elasticvue.png)

**（2）使用ElasticHD可视化面板**

ElasticHD支持所有版本ES，特色功能是支持“SQL转DSL”。

项目地址：[https://github.com/qax-os/ElasticHD](https://github.com/qax-os/ElasticHD)

```shell
$ docker run -d --name elastichd -p 9800:9800 containerize/elastichd
$ docker update elastichd --restart=always
```

浏览器打开`http://ip:9800/`地址，即可访问面板，在左上角配置ES连接信息即可。如果是带鉴权的ES，按照`http://user:password@xxx.xxx.xxx.xxx:9800`配置ES连接信息即可。

![ElasticHD](https://image.eula.club/quantum/ElasticHD.png)

在Tools——SQL Convert DSL处，可以编写SQL生成操作ES的DSL语句（作为辅助手段使用，一些复杂的SQL可能不适用）

另注：也可以使用一些在线工具进行转换，例如，[https://printlove.cn/tools/sql2es](https://printlove.cn/tools/sql2es)、[http://sql2dsl.atotoa.com](http://sql2dsl.atotoa.com)

**（3）安装kibana可视化插件**

下载与ES版本相同的Kibana

```shell
$ mkdir -p /root/kibana
$ cd /root/kibana
$ wget https://artifacts.elastic.co/downloads/kibana/kibana-7.16.2-linux-x86_64.tar.gz
$ tar -zxvf kibana-7.16.2-linux-x86_64.tar.gz
$ cd /root/kibana/kibana-7.16.2-linux-x86_64
$ vi /config/kibana.yml
```

修改配置文件内容如下（用不到的我这里给删掉了，原配置文件有着很详尽的英文说明）：

```yml
server.port: 5601
server.host: "ip" 
elasticsearch.hosts: ["http://ip:9200"]
elasticsearch.username: "username"
elasticsearch.password: "password"
i18n.locale: "zh-CN"
```

启动kibana：

```shell
$ cd /root/kibana/kibana-7.16.2-linux-x86_64/bin # 进入可执行目录
$ nohup /root/kibana/kibana-7.16.2-linux-x86_64/bin/kibana & # 启动kibana 
```

说明：root用户，会报`Kibana should not be run as root.  Use --allow-root to continue.`的错误，建议切换别的用户去执行，如果就是想用root用户启动，则使用`nohup /root/docker/kibana/kibana-7.16.2-linux-x86_64/bin/kibana --allow-root &`。

启动成功后，浏览器打开`http://ip:5601/`地址，用es的用户名和密码进行登录，就可以使用了。

![Kibana管理面板](https://image.eula.club/quantum/Kibana管理面板.png)

关闭kibana：

```shell
$ ps -ef | grep kibana
$ kill -9 [PID]
```

#### 5.10.3 安装ik分词器插件

IK 分析插件将 Lucene IK 分析器集成到 elasticsearch 中，支持自定义字典。

- 项目地址：[https://github.com/medcl/elasticsearch-analysis-ik](https://github.com/medcl/elasticsearch-analysis-ik)

安装方式：挂载目录或者进容器下载（版本一定不要安装错，不然就进不去容器了）

- 方式一：去Releases下载对应ES版本的ik分词器插件，然后上传到plugins目录将其挂载到容器内。

- 方式二：进入容器内直接下载对应ES版本的ik分词器插件，并放到相应目录。

  ```shell
  $ docker exec -it es /bin/bash
  $ apt-get install -y wget   
  $ wget https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.16.2/elasticsearch-analysis-ik-7.16.2.zip
  $ unzip -o -d /usr/share/elasticsearch/elasticsearch-analysis-ik-7.16.2 /usr/share/elasticsearch/elasticsearch-analysis-ik-7.16.2.zip
  $ rm –f elasticsearch-analysis-ik-7.16.2.zip
  $ mv /usr/share/elasticsearch/elasticsearch-analysis-ik-7.16.2 /usr/share/elasticsearch/plugins/ik
  $ exit
  $ docker restart es
  ```

测试方式：可以进行存在测试和功能测试

```shell
$ docker exec -it es /bin/bash
$ cd /usr/share/elasticsearch/bin
$ elasticsearch-plugin list
```

ik分词器有2种算法：ik_smart和ik_max_word，下面我们通过postman工具来测试ik分词器的分词算法。

[1] 测试ik_smart分词

请求url：http://ip:9200/_analyze      请求方式：get

请求参数：

```json
{
    "analyzer":"ik_smart",
    "text":"我爱你，特靠谱"
}
```

[2] 测试ik_max_word分词

请求url：http://ip:9200/_analyze     请求方式：get

请求参数：

```json
{
    "analyzer":"ik_max_word",
    "text":"我爱你，特靠谱"
}
```

上面测试例子可以看到，不管是ik_smart还是ik_max_word算法，都不认为"特靠谱"是一个关键词（ik分词器的自带词库中没有有"特靠谱"这个词），所以将这个词拆成了三个词：特、靠、谱。

自定义词库：ik分词器会把分词库中没有的中文按每个字进行拆分。如果不想被拆分，那么就需要维护一套自己的分词库。

- Step1：进入`ik分词器路径/config`目录，新建一个`my.dic`文件，添加一些关键词，如"特靠谱"、"靠谱"等，每一行就是一个关键词。

- Step2：修改配置文件`IKAnalyzer.cfg.xml`，配置`<entry key="ext_dict"></entry>`。

  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
  <properties>
      <comment>IK Analyzer 扩展配置</comment>
      <!--用户可以在这里配置自己的扩展字典 -->
      <entry key="ext_dict">my.dic</entry>
       <!--用户可以在这里配置自己的扩展停止词字典-->
      <entry key="ext_stopwords"></entry>
      <!--用户可以在这里配置远程扩展字典 -->
      <!-- <entry key="remote_ext_dict">words_location</entry> -->
      <!--用户可以在这里配置远程扩展停止词字典-->
      <!-- <entry key="remote_ext_stopwords">words_location</entry> -->
  </properties>
  ```

- Step3：重启ES，并再次使用Postman测试上述请求，发现"特靠谱"、"靠谱"等将其视为一个词了。

#### 5.10.4 使用curl命令操作ES

**[1] 索引操作**

```shell
// 查询所有索引
$ curl -u 用户名:密码 http://ip:port/_cat/indices

// 删除索引（包含结构）
$ curl -u 用户名:密码 -XDELETE http://ip:port/索引名

// 清空索引（不包含结构，即删除所有文档）
$ curl -u 用户名:密码 -XPOST 'http://ip:port/索引名/_delete_by_query?refresh&slices=5&pretty' -H 'Content-Type: application/json' -d'{"query": {"match_all": {}}}'

// 创建索引
$ curl -u 用户名:密码 -XPUT 'http://ip:port/索引名' -H 'Content-Type: application/json' -d'
{
    "settings" : {
      "index" : {
        "number_of_shards" : "5",
        "number_of_replicas" : "1"
      }
    },
    "mappings" : {
        "properties" : {
          "post_date": {
               "type": "date"
          },
          "tags": {
               "type": "keyword"
          },
          "title" : {
               "type" : "text"
          }
        }
    }
}'

// 修改索引
$ curl -u 用户名:密码 -XPUT 'http://ip:port/索引名/_mapping' -H 'Content-Type: application/json' -d'
{
  "properties" : {
    "post_date": {
         "type": "date"
    },
    "tags_modify": {
         "type": "keyword"
    },
    "title" : {
         "type" : "text"
    },
    "content": {
         "type": "text"
    }
  }
}'

// 调整副本数量（分片数量不可调整，要修改就只能删除索引重建）
$ curl -u 用户名:密码 -XPUT 'ip:port/索引名/_settings' -H 'Content-Type: application/json' -d '
{
    "index": {
       "number_of_replicas": "0"
    }
}'

// 查看单个索引信息（可以查看到单个索引的数据量)
$ curl -u 用户名:密码 -XGET 'http://ip:port/_cat/indices/index_1?v'

health status index      uuid                   pri rep docs.count docs.deleted store.size pri.store.size
green  open   index_1    aado9-iGRFGN9twQb040ds   5   1   28800345            0        3gb          1.5gb

// 按照文档数量排序索引（可以查看到所有索引的数据量)
$ curl -u 用户名:密码 -XGET 'http://ip:port/_cat/indices?v&s=docs.count:desc'
```

注意事项：创建索引时，有的教程在“mappings”里嵌套了“_doc”，会报如下错误，这是因为版本 7.x 不再支持映射类型，将其删除即可。

```
{"error":{"root_cause":[{"type":"illegal_argument_exception","reason":"The mapping definition cannot be nested under a type [_doc] unless include_type_name is set to true."}],"type":"illegal_argument_exception","reason":"The mapping definition cannot be nested under a type [_doc] unless include_type_name is set to true."},"status":400}%
```

**[2] 文档操作**

```shell
// 根据_id查询文档
$ curl -u 用户名:密码 -XGET 'http://ip:port/索引名/_doc/1'

// 新增和修改文档
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XPOST 'http://ip:port/索引名/_doc/1' -d '
     {
        "msgId": "10010",
        "title": "test-title",
        "content": "test-content",
        "isDeleted": 0,
        "publishTime": "1586707200000",
        "insertTime": "1668212021000",
        "updateTime": "1678687631000"
    }'
         
// 根据_id删除文档
$ curl -u 用户名:密码 -XDELETE "http://ip:port/索引名/_doc/1"

// 查询所有数据
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}}}'

// 查询指定条数的数据
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}},"size":2}'

// 查询指定列数据
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}},"_source":["publishTime","updateTime"]}'

// 查询数据并排序
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match_all":{}},"sort":{"_id":{"order":"desc"}}}'
 
// 匹配查询
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"match":{"title":"test"}}}'

// 精准查询
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"term":{"title.keyword":"test-title"}}}'

// 范围查询
$ curl -u 用户名:密码 -H "Content-Type:application/json" -XGET http://ip:port/索引名/_search?pretty -d '{"query":{"range":{"msgId":{"gt":"1","lte":"20000"}}}}'
```

### 5.11 Docker-EMQX环境搭建

#### 5.11.1 拉取镜像并运行容器

```shell
$ docker pull emqx/emqx
$ docker run -d --name emqx -p 1883:1883 -p 8086:8086 -p 8883:8883 -p 8084:8084 -p 18083:18083 emqx/emqx
```

#### 5.11.2 EMQX的管理面板

搭建完后用浏览器访问 `http://IP:18083/`地址，默认账号及密码为：`admin / public`，登录后建议立刻修改密码。

<img src="https://image.eula.club/quantum/EMQX物联网MQTT消息服务器面板.png" alt="EMQX物联网MQTT消息服务器面板"  />

### 5.12 Docker-MinIO环境搭建

#### 5.12.1 拉取镜像并运行容器

```shell
$ docker pull minio/minio
$ mkdir -p /home/data/minio/data
$ mkdir -p /home/data/minio/config
$ docker run -d --restart always \
   -p 9000:9000 -p 9001:9001 --name minio \
   -e "MINIO_ACCESS_KEY=admin" \
   -e "MINIO_SECRET_KEY=password" \
   -v /home/data/minio/data:/data \
   -v /home/data/minio/config:/root/.minio \
   minio/minio server --console-address ":9001" /data
```

注：密码不可以设置的太简单了（会导致创建失败），出现此问题请查看容器日志。

#### 5.12.2 MinIO的管理面板

浏览器打开：`http://IP:9001` 查看即可。MINIO_ACCESS_KEY为账号，MINIO_SECRET_KEY为密码。进去之后创建存储桶，即可进行使用。

![minio-console](https://image.eula.club/quantum/minio-console.png)

### 5.13 Docker-Milvus环境搭建

#### 5.13.1 拉取镜像并运行容器

官方文档里提供了一键脚本进行部署，[https://milvus.io/docs/install_standalone-docker.md](https://milvus.io/docs/install_standalone-docker.md)

```shell
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
$ ./standalone_embed.sh start
```

该脚本还提供了以下管理命令：

```shell
$ ./standalone_embed.sh start
$ ./standalone_embed.sh stop
$ ./standalone_embed.sh delete
$ ./standalone_embed.sh upgrade
```

#### 5.13.2 Milvus可视化管理工具

可以安装开源的 Attu 工具进行可视化管理，可以在Linux上搭建网页端，也可以在Mac、Win上直接安装客户端。

- 项目地址：[https://github.com/zilliztech/attu](https://github.com/zilliztech/attu)

这里我是直接在 Mac 上安装了客户端，会提示“attu.app 已损坏，无法打开”，执行以下命令即可。

```shell
$ sudo xattr -rd com.apple.quarantine /Applications/attu.app
```

![Attu](https://image.eula.club/quantum/Attu.png)

## 6. 参考资料

[1] [项目环境管理思路 from fish-aroma](https://www.fish-aroma.top/blogs/system/xi-tong-huan-jing-guan-li-si-lu.html)

[2] [Debian安装Docker_from 简书](https://www.jianshu.com/p/12ef4246b048)

[3] [直接安装和docker安装的区别 from php中文网](https://www.php.cn/docker/445063.html)

[4] [Docker下安装MySQL from CSDN](https://blog.csdn.net/J080624/article/details/104297654)

[5] [使用docker安装nginx from 掘金](https://juejin.cn/post/6844904016086827016)

[6] [Docker--删除容器实例和镜像 from 极客分享](https://www.geek-share.com/detail/2791558825.html)

[7] [docker与docker-compose介绍，对比与使用 from 简书](https://www.jianshu.com/p/5794ec7e603b)

[8] [如何在Debian 9上安装Docker Compose from 腾讯云](https://cloud.tencent.com/developer/article/1360749)

[9] [通过 DockerFile 打包镜像 from cnblog](https://www.cnblogs.com/michael9/p/12303748.html)

[10] [如何构建 Docker 镜像 from tkestack](https://tkestack.github.io/docs/zh/%E4%BA%A7%E5%93%81%E5%BF%AB%E9%80%9F%E5%85%A5%E9%97%A8/%E5%85%A5%E9%97%A8%E7%A4%BA%E4%BE%8B/%E5%A6%82%E4%BD%95%E6%9E%84%E5%BB%BADocker%E9%95%9C%E5%83%8F.html)

[11] [docker安装RabbitMq from 稀土掘金](https://juejin.cn/post/6844903970545090574)

[12] [docker简易搭建kafka from 知乎](https://zhuanlan.zhihu.com/p/366981391)

[13] [中间件docker compose，包含redis、elasticsearch、mongo、mysql、rocketmq、kafka，一键启动 from github](https://github.com/q474818917/docker-component)

[14] [Linux Docker springboot jar 日志时间不正确 from CSDN](https://blog.csdn.net/q1009020096/article/details/88088458)

[15] [docker安装oracle11g(linux环境) from CSDN](https://blog.csdn.net/enthan809882/article/details/104656554)

[16] [Docker 快速安装&搭建 Elasticsearch 环境 from 异常教程](https://www.exception.site/docker/docker-install-elasticserach)

[17] [EMQX docker安装及运行 from CSDN](https://blog.csdn.net/u011089760/article/details/89892591)

[18] [docker搭建elasticsearch6.8.7并开启x-pack认证 from 程序员宅基地](https://www.cxyzjd.com/article/qq_33235529/110482614)

[19] [Cannot stop or restart a docker container from stackoverflow](https://stackoverflow.com/questions/31365827/cannot-stop-or-restart-a-docker-container)

[20] [Docker启动提示 response from daemon: OCI runtime create failed: container with id exists:XXX:unknown from CSDN](https://blog.csdn.net/kevinyankai/article/details/107002375)

[21] [如何在ubuntu 中彻底删除docker from 腾讯云](https://cloud.tencent.com/developer/article/1541011)

[22] [docker可视化工具Portainer部署与汉化 from WebEnh](https://www.cnblogs.com/webenh/p/13327915.html)

[23] [关于docker容器内部的文件上传和下载 from 代码先锋网](https://www.codeleading.com/article/36703481671/)

[24] [docker容器打包成镜像和压缩以及解压和载入镜像 from 程序员宝宝](https://cxybb.com/article/sunmingyang1987/104555190)

[25] [利用Dockerfile部署SpringBoot项目 from 51CTO博客](https://blog.51cto.com/u_3664660/3212692#:~:text=%E5%88%A9%E7%94%A8Dockerfile%E9%83%A8%E7%BD%B2SpringBoot%E9%A1%B9%E7%9B%AE)

[26] [在docker下部署Python项目 from Python Free](https://www.pythonf.cn/read/58009)

[27] [docker在容器外执行某个容器内的某个命令 from CSDN](https://blog.csdn.net/weixin_32820767/article/details/80643091)

[28] [如何跨容器调用可执行命令 from lyer's blog](https://biningo.github.io/2021/11/22/%E5%A6%82%E4%BD%95%E8%B7%A8%E5%AE%B9%E5%99%A8%E8%B0%83%E7%94%A8%E5%8F%AF%E6%89%A7%E8%A1%8C%E5%91%BD%E4%BB%A4/)

[29] [Docker daemon.json的作用（八）from CSDN](https://blog.csdn.net/u013948858/article/details/79974796)

[30] [清空docker container logs from 暗无天日](http://blog.lujun9972.win/blog/2019/03/24/%E6%B8%85%E7%A9%BAdocker-container-logs/index.html)

[31] [docker 容器日志清理方案 from 简书](https://www.jianshu.com/p/28f1acb11f6b)

[32] [Docker容器使用NFS from cloud-atlas](https://cloud-atlas.readthedocs.io/zh_CN/latest/docker/storage/docker_container_nfs.html)

[33] [解决Docker容器时区不正确的问题 form 简书](https://www.jianshu.com/p/43e5d72b0f63)

[34] [Docker无视防火墙 from fish-aroma](https://www.fish-aroma.top/blogs/system/dockerwu-shi-fang-huo-qiang.html#%E5%9C%BA%E6%99%AF)

[35] [Docker系列-查看Latest的镜像具体版本和查看容器用到的镜像版本](https://blog.51cto.com/u_15670038/5393486)

[36] [docker 利用CMD或者ENTRYPOINT命令同时启动多个服务 from CSDN](https://blog.csdn.net/shadow_zed/article/details/103867359)

[37] [Docker之docker run参数覆盖Dockerfile中CMD命令以及CMD与ENTRYPOINT的区别 from CSDN](https://blog.csdn.net/wangziyang777/article/details/114277452)

[38] [Harbor安装和配置 from Harbor官方文档](https://goharbor.io/docs/2.7.0/)

[39] [Linux中基于Docker搭建harbor私有镜像仓库 from CSDN](https://blog.csdn.net/liu_chen_yang/article/details/124623482)

[40] [http: server gave HTTP response to HTTPS client from 博客园](https://www.cnblogs.com/programmer-tlh/p/10996443.html)

[41] [Harbor功能特点看这一篇就够了 from CSDN](https://blog.csdn.net/q48S71bCzBeYLOu9T0n/article/details/115474510)

[42] [使用Nginx实现多台服务器网站负载均衡的配置方法介绍 from CSDN](https://blog.csdn.net/guo_qiangqiang/article/details/106598695)

[43] [Dockerfile语法、自定义镜像构建详解 from CSDN](https://blog.csdn.net/qq_44749491/article/details/126752064)

[44] [Docker核心知识概括 from 知乎](https://zhuanlan.zhihu.com/p/688772736)

[45] [正向代理与反向代理的区别 from oxylabs](https://oxylabs.cn/blog/reverse-proxy-vs-forward-proxy) 

[46] [基于 Cloudflare Worker 的容器镜像加速器 from Github](https://github.com/Doublemine/container-registry-worker)

[47] [自建Docker Hub加速镜像 from Ling的博客](https://blog.lty520.faith/%E5%8D%9A%E6%96%87/%E8%87%AA%E5%BB%BAdocker-hub%E5%8A%A0%E9%80%9F%E9%95%9C%E5%83%8F/)

[48] [AnolisOS8安装Docker from CSDN](https://blog.csdn.net/lyace2010/article/details/133296691)

[49] [创建个人Docker镜像仓库代理 from Datehoer's Blog](https://www.datehoer.com/blogs/other/createapersonaldockerproxy.html)
