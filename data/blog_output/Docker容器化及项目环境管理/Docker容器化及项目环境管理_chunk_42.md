## 3. Docker环境搭建及使用
### 3.7 正式环境的前后端分离项目部署
#### 3.7.3 准备一键部署包的配置文件及脚本

项目部署所需要文件的目录结构如下：

```
.
├── config
    ├── application-prod.properties
    └── application.properties
├── dist.zip
├── Dockerfile
├── nginx.conf
├── proxy.conf
├── yoyo_web.conf
├── web_manage-0.0.1.jar
├── unzip.sh
├── build.sh
├── rebuild.sh
└── start_web.sh
```

[1] 准备 nginx 配置文件 （nginx.conf、yoyo_web.conf、proxy.conf）

nginx.conf（无需修改）

```ini
user  root;
worker_processes  auto;

error_log  /var/log/nginx/error.log notice;
pid        /var/run/nginx.pid;


events {
    worker_connections  1024;
}


http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    log_format  main  '$remote_addr - $remote_user [$time_local] "$request" '
                      '$status $body_bytes_sent "$http_referer" '
                      '"$http_user_agent" "$http_x_forwarded_for"';

    access_log  /var/log/nginx/access.log  main;

    sendfile        on;
    #tcp_nopush     on;

    keepalive_timeout  65;

    #gzip  on;

    include /etc/nginx/conf.d/*.conf;
}
```

yoyo_web.conf（需要修改后端的接口地址和前端文件的存放路径，`location ~* ^`这里根据实际项目的路由配置进行转发）

```ini
upstream dev_yoyo_web {
        server 127.0.0.1:8081 weight=1 max_fails=1 fail_timeout=10s;
}
server {
    listen       82;
    server_name  127.0.0.1;
    location / {
        gzip on;
        gzip_vary on;
        gzip_min_length 1k;
        gzip_buffers 16 16k;
        gzip_http_version 1.1;
        gzip_comp_level 9;
        gzip_types text/plain application/javascript application/x-javascript text/css text/xml text/javascript application/json;
        root  /storage/web_code;
        index index.html;
        try_files $uri $uri/ /index.html?$query_string;
    }

    location ~* ^(/login|/logout|/api/|/auth/) {
        proxy_pass http://dev_yoyo_web; 
        client_max_body_size    48m;
        include proxy.conf;
    }
}
```

proxy.conf（无需修改）

```ini
proxy_connect_timeout 900s;
proxy_send_timeout 900;
proxy_read_timeout 900;
proxy_buffer_size 32k;
proxy_buffers 4 64k;
proxy_busy_buffers_size 128k;
proxy_redirect off;
proxy_hide_header Vary;
proxy_set_header Accept-Encoding '';
proxy_set_header Referer $http_referer;
proxy_set_header Cookie $http_cookie;
proxy_set_header Host $host;
proxy_set_header X-Real-IP $remote_addr;
proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
proxy_set_header X-Forwarded-Proto $scheme;
```

[2] 准备Dockerfile（可不修改，也可根据实际需要修改）

```dockerfile
# 设置基础镜像
FROM nginx

# 安装常用命令
RUN apt-get update
RUN apt-get install -y wget       # 安装wget
RUN apt-get install vim -y        # 安装vim
RUN apt-get install -y psmisc     # 安装ps

# 设置工作目录
RUN mkdir /storage
WORKDIR /storage

# 安装java8环境
RUN mkdir /usr/local/java
# 方式一：下载jdk并解压到指定目录（适用于网速快的情况，需要提前安装wget）
RUN wget https://mirrors.huaweicloud.com/java/jdk/8u202-b08/jdk-8u202-linux-x64.tar.gz
RUN tar zxvf jdk-8u202-linux-x64.tar.gz -C /usr/local/java && rm -f jdk-8u202-linux-x64.tar.gz
# 方式二：将本地jdk复制到内部目录并自动解压（适用于网速慢的情况，提前下载好）
# ADD jdk-8u202-linux-x64.tar.gz /usr/local/java
# RUN rm -f jdk-8u202-linux-x64.tar.gz
RUN ln -s /usr/local/java/jdk1.8.0_202 /usr/local/java/jdk
ENV JAVA_HOME /usr/local/java/jdk
ENV JRE_HOME ${JAVA_HOME}/jre
ENV CLASSPATH .:${JAVA_HOME}/lib:${JRE_HOME}/lib
ENV PATH ${JAVA_HOME}/bin:$PATH

# 放置前端代码及nginx配置
ADD dist/ /storage/web_code
COPY nginx.conf /etc/nginx/nginx.conf
COPY yoyo_web.conf /etc/nginx/conf.d/yoyo_web.conf
COPY proxy.conf /etc/nginx

# 放置后端代码及包外配置
COPY web_manage-0.0.1.jar /storage
COPY config /storage

# 放置启动脚本并授予权限
COPY start_web.sh /storage/start_web.sh
RUN chmod u+x /storage/start_web.sh

# 容器服务自启
ENTRYPOINT ["/storage/start_web.sh"]
```

注意事项：

- ENTRYPOINT 里的配置会覆盖父镜像的启动命令，因此这里需要启动 Nginx 和 Jar 的两个命令。若用`&&`连接的话只会执行前面的那一个，因此这里将两个启动命令都写进一个Shell脚本里。

  ```
  关于CMD和ENTRYPOINT有一点需要特别注意：如果一个Dockerfile中有多个CMD或ENTRYPOINT，只有最后一个会生效，前面其他的都会被覆盖。
  ```

- 前端包我这里采用的是将 zip 通过shell脚本解压后再拷贝进容器的方式，如果采用 tar.gz 格式，ADD命令会自动对其进行解压（其他压缩格式不可以）。

  ```
  ADD dist.tar.gz /storage/web_code
  ```

[3] 准备部署脚本

unzip.sh（无需修改）

```shell
#!/bin/bash

#define default variable
base_path=$(cd `dirname $0`; pwd)
app_path="${base_path}/dist"
zip_name="${base_path}/dist.zip"
rm -fr ${app_path}
unzip -d ${app_path} ${zip_name}
echo "unzip success!"
```

start_web.sh（可不修改，也可根据实际需要修改）

```shell
#!/bin/bash

/docker-entrypoint.sh nginx -g 'daemon off;' &
java -jar /storage/web_manage-0.0.1.jar --spring.profiles.active=prod
```

注意：前面的服务一定要在后台运行，即后面加个&，最后一个服务要以前台运行。否则，全部以前台运行的话，只有第一个服务会启动；全部以后台运行的话，当最后一个服务执行完成后，容器就退出了。

build.sh（可不修改，也可根据实际需要修改）

```shell
#!/bin/bash

base_path=$(cd `dirname $0`; pwd)
uploads_path="${base_path}/uploads"
mkdir ${uploads_path}
chmod u+x ${base_path}/unzip.sh
${base_path}/unzip.sh
docker build -t 'yoyo_web_image' .
docker run -itd --name yoyo_web -h yoyo_web --network yoyo -v ${uploads_path}:/storage/web_code/uploads -p 8082:82 -p 8081:8081 -e TZ="Asia/Shanghai" yoyo_web_image
```

rebuild.sh（可不修改，也可根据实际需要修改）

```shell
#!/bin/bash

docker rm -f yoyo_web
docker rmi -f yoyo_web_image
base_path=$(cd `dirname $0`; pwd)
uploads_path="${base_path}/uploads"
mkdir ${uploads_path}
chmod u+x ${base_path}/unzip.sh
${base_path}/unzip.sh
docker build -t 'yoyo_web_image' .
docker run -itd --name yoyo_web -h yoyo_web --network yoyo -v ${uploads_path}:/storage/web_code/uploads -p 8082:82 -p 8081:8081 -e TZ="Asia/Shanghai" yoyo_web_image
```

如果没有配置好自启动，也可以在Shell脚本里加上在容器外执行容器内命令的方式启动，但这种方式重启容器后就又需要手动开启了，因此不推荐使用。

```shell
docker exec -itd `docker ps |grep yoyo_web |awk '{print $1}'` /bin/bash -c 'java -jar -Duser.timezone=GMT+8 /storage/web_manage-0.0.1.jar > /storage/web_manage-0.0.1.log 2>&1'
docker exec -it `docker ps |grep yoyo_web |awk '{print $1}'` /bin/bash -c 'tail -fn 100 /storage/web_manage-0.0.1.log'
```

注意：docker exec -it 这里必须不带上d，否则看不到输出结果。
