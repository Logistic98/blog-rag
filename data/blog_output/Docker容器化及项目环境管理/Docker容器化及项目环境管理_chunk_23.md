## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
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
