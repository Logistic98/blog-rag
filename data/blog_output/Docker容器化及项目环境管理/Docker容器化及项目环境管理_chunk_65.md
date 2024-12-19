## 5. Docker搭建中间件服务
### 5.3 Docker-Oracle环境搭建
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
