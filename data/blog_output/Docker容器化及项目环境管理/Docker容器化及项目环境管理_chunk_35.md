## 3. Docker环境搭建及使用
### 3.5 通过Dockerfile自动构建镜像
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
