## 3. Docker环境搭建及使用
### 3.5 通过Dockerfile自动构建镜像

Step1：在项目里面再新建一个Dockerfile文件（有的开源项目会提供现成的 Dockerfile，如果没有就要自己去写）。

| 指令名称     | 说明                                              | 示例                          |
| ------------ | ------------------------------------------------- | ----------------------------- |
| `FROM`       | 指定基础镜像名称/ID                               | `FROM centos:7`               |
| `ENV`        | 设置环境变量，可在后面的指令中使用                | `ENV key value`               |
| `COPY`       | 拷贝本地文件/目录到镜像的指定目录                 | `COPY <源路径> <目标路径>`    |
| `ADD`        | 与COPY类似，目录或远程URL从源复制到镜像的目标目录 | `ADD <源路径> <目标路径>`     |
| `RUN`        | 执行Linux的shell命令，一般是编译/安装软件的命令   | `RUN yum install gcc`         |
| `EXPOSE`     | 指定容器运行时监听的端口号                        | `EXPOSE 80`                   |
| `ENTRYPOINT` | 容器启动时用的启动命令，容器运行时的入口          | `ENTRYPOINT java -jar xx.jar` |

Step2：切换到项目目录里，执行如下命令即可成功构建镜像。

```shell
$ docker build -t 'test-image' .
```

Step3：我们可以打包导出镜像，示例如下。

```shell
$ docker save test-image > test-image.v1.dockerimage  
```
