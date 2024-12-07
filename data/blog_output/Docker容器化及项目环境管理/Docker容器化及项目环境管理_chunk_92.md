## 5. Docker搭建中间件服务
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
