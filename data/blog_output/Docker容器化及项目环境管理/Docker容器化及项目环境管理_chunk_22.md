## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
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
