## 3. Docker环境搭建及使用
### 3.5 通过Dockerfile自动构建镜像
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
