## 5. Docker搭建中间件服务
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
