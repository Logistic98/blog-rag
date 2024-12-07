## 3. Docker环境搭建及使用
### 3.5 通过Dockerfile自动构建镜像
#### 3.5.3 使用Docker部署前端项目

Step1：将前端项目打包，生成dist文件（或者其他的），编写Dockerfile，示例如下：

```dockerfile
# 设置基础镜像
FROM nginx
# 将dist文件中的内容复制到 /usr/share/nginx/html/这个目录下面
COPY dist/  /usr/share/nginx/html/
# 安装vim命令
RUN apt-get update && apt-get install vim -y 
```

Step2：将项目和Dockerfile上传到服务器并制作镜像运行容器

```shell
$ cd /root/deploy                                                     // 切换到存放项目和Dockerfile的目录
$ docker build -t test-web-image .                                    // 使用Dockerfile构建镜像
$ docker run -d -p 8081:80 --name test-web -e TZ="Asia/Shanghai" test-web-image:latest      // 通过镜像运行容器
$ docker update test-web --restart=always                             // 设置开机自启
```

访问地址：`http://ip:8081`

注意事项：

[1] 容器内nginx的默认端口是80，如要使用其他端口，请修改nginx配置。以下是容器内的几个重要目录，如有需要可挂载出来。

```
/etc/nginx/conf.d                                                     // Nginx配置目录
/usr/share/nginx/html                                                 // Nginx存放资源的目录
/var/log/nginx                                                        // Nginx日志目录
```

[2] 如果访问页面时出现403问题，进入容器内修改权限即可。

```shell
$ docker exec -it test-web /bin/bash
$ chmod -R 755 /usr/share/nginx/html
```
