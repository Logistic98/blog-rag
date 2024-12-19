## 2. Nginx配置及项目发布
### 2.2 Nginx配置服务负载均衡
#### 2.2.3 Nginx负载均衡实例

需求情景：有多台GPU服务器，分别部署了多个大模型服务，现在想要提高大模型服务的并发量，可以使用Nginx负载均衡来实现。

假设有3个服务，分别是1701、1702、1703端口，现在想要将其使用Nginx进行负载均衡，统一用1700端口来访问。

```
.
├── Dockerfile
├── nginx.conf
├── nginx_balance.conf
├── proxy.conf
└── build.sh
```

Dockerfile

```Dockerfile
# 设置基础镜像
FROM nginx

# 放置nginx配置
COPY nginx.conf /etc/nginx/nginx.conf
COPY nginx_balance.conf /etc/nginx/conf.d/nginx_balance.conf
COPY proxy.conf /etc/nginx
```

nginx.conf

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

nginx_balance.conf

```ini
upstream nginx_balance {
        server xxx.xxx.xxx.xxx:1701 weight=1 max_fails=1 fail_timeout=10s;
        server xxx.xxx.xxx.xxx:1702 weight=1 max_fails=1 fail_timeout=10s;
        server xxx.xxx.xxx.xxx:1703 weight=1 max_fails=1 fail_timeout=10s;
}
server {
    listen       1700;
    server_name  127.0.0.1;
    location ~* ^(/) {
        gzip on;
        gzip_vary on;
	      gzip_min_length 1k;
	      gzip_buffers 16 16k;
        gzip_http_version 1.1;
        gzip_comp_level 9;
        gzip_types text/plain application/javascript application/x-javascript text/css text/xml text/javascript application/json;
        proxy_pass http://nginx_balance;
        client_max_body_size    48m;
        # 添加proxy_next_upstream指令，实现失败时的自动跳转
        proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
        include proxy.conf;
    }
}
```

proxy.conf

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

build.sh

```shell
#!/bin/bash

docker build -t 'nginx_balance_image' .
docker run -itd --name nginx_balance -h nginx_balance -p 1700:1700 nginx_balance_image
docker update nginx_balance --restart=always
```

上传到服务器上之后，给 build.sh 添加可执行权限，执行该脚本即可。
