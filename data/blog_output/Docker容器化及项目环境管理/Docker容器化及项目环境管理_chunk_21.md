## 3. Docker环境搭建及使用
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
