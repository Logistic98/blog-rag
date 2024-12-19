## 5. Docker搭建中间件服务
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
