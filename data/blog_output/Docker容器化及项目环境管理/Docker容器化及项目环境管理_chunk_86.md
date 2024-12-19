## 5. Docker搭建中间件服务
### 5.10 Docker-ElasticSearch环境搭建
#### 5.10.1 拉取镜像并运行容器

**部署命令**

```shell
$ docker pull elasticsearch:7.16.2
$ docker run -d --name es \
-p 9200:9200 -p 9300:9300 \
-v /root/docker/es/data:/usr/share/elasticsearch/data \
-v /root/docker/es/config:/usr/share/elasticsearch/config \
-v /root/docker/es/plugins:/usr/share/elasticsearch/plugins \
-e "discovery.type=single-node" -e ES_JAVA_OPTS="-Xms1g -Xmx1g" \
elasticsearch:7.16.2
$ docker update es --restart=always
```

**进入容器进行配置**

```shell
$ docker exec -it es /bin/bash 
$ cd config
$ chmod o+w elasticsearch.yml
$ vi elasticsearch.yml
```

其中，在 elasticsearch.yml 文件的末尾添加以下三行代码（前两行如果开启则代表允许跨域，出于安全考虑把它关了，第三行开启xpack安全认证）

```yml
# http.cors.enabled: true
# http.cors.allow-origin: "*"
xpack.security.enabled: true    
```

然后把权限修改回来，重启容器，设置账号密码，浏览器访问`http://IP:9200`地址即可（用 elastic账号 和自己设置的密码登录即可）

```shell
$ chmod o-w elasticsearch.yml
$ exit
$ docker restart es
$ docker exec -it es /bin/bash 
$ ./bin/elasticsearch-setup-passwords interactive   // 然后设置一大堆账号密码
```

**注意事项**

1）Elasticsearch请选择7.16.0之后的版本，之前的所有版本都使用了易受攻击的 Log4j2版本，存在严重安全漏洞。  

2）`ES_JAVA_OPTS="-Xms1g -Xmx1g"`只是一个示例，内存设置的少了会导致数据查询速度变慢，具体设置多少要根据业务需求来定，一般而言公司的实际项目要设置8g内存以上。

**数据挂载遇到的问题**

[1] 数据锁定问题

- 报错信息：`java.lang.IllegalStateException: failed to obtain node locks, tried [[/usr/share/elasticsearch/data]] with lock id [0]; maybe these locations are not writable or multiple nodes were started without increasing `

- 产生原因：ES在运行时会在`/data/nodes/具体分片`目录里生成一个`node.lock`文件，由于我是在运行期scp过来的挂载数据，这个也被拷贝过来了，导致数据被锁定。

- 解决办法：删掉`/data/nodes/具体分片/node.lock`文件即可

[2] data目录权限问题

- 解决办法：进入容器内部，把data目录的权限设置为777即可

[3] 集群与单节点问题

- 解决办法：修改`config/elasticsearch.yml`里的集群配置即可，如果原来是集群，现在要单节点，就把集群配置去掉。

[4] 堆内存配置问题

- 报错信息：`initial heap size [8589934592] not equal to maximum heap size [17179869184]; this can cause resize pauses`

- 解决办法：-Xms 与 -Xmx 设置成相同大小的内存。
