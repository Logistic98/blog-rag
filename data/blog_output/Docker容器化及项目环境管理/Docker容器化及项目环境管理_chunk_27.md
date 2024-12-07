## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
#### 3.2.7 查看Latest的镜像具体版本

```shell
// 查看容器使用的镜像具体版本
$ docker inspect minio|grep -i version
// 查看镜像具体版本
$ docker image inspect minio/minio:latest|grep -i version
```
