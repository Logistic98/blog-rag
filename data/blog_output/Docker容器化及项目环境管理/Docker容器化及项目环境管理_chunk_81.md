## 5. Docker搭建中间件服务
### Notice we are including log4j's NDC here (%x)
#### 5.8.4 搭建kafka管理平台

**[1] kafka-map**

kafka-map是一个美观简洁且强大的kafka web管理工具。

项目地址：[https://github.com/dushixiang/kafka-map](https://github.com/dushixiang/kafka-map)

```shell
docker run -d \
    -p 8080:8080 \
    -v /root/kafka-map/data:/usr/local/kafka-map/data \
    -e DEFAULT_USERNAME=your_user \
    -e DEFAULT_PASSWORD=your_password \
    --name kafka-map \
    --restart always dushixiang/kafka-map:latest
```

用Chrome访问`http://ip:8080`即可访问 kafka-map 管理界面

![kafka-map](https://image.eula.club/quantum/kafka-map.png)

注：如果配置了4.6.3节的SASL账号密码验证，这里安全验证选择“SASL_PLAINTEXT”，协议机制选择“PLAIN”（虽然连上了，但一些功能不好使了）

**[2] kafka-manager**

kafka-manager是目前最受欢迎的kafka集群管理工具，最早由雅虎开源，用户可以在Web界面执行一些简单的集群管理操作。

```shell
$ docker pull sheepkiller/kafka-manager
$ docker run --name kafka-manager -itd -p 9000:9000 -e ZK_HOSTS="IP:2181" sheepkiller/kafka-manager  // 把IP处换成你的服务器IP地址
```

用Chrome访问`http://ip:9000`即可访问 kafka-manager 管理界面

![kafka管理面板-1](https://image.eula.club/quantum/kafka管理面板-1.png)

连接kafka：点击Cluster，选择Add Cluster，填写Cluster Name（随便起）、Cluster Zookeeper Hosts（zookeeper地址）保存即可。

![kafka管理面板-2](https://image.eula.club/quantum/kafka管理面板-2.png)

**[3] KnowStreaming**

Know Streaming是一套云原生的Kafka管控平台，脱胎于众多互联网内部多年的Kafka运营实践经验，专注于Kafka运维管控、监控告警、资源治理、多活容灾等核心场景。在用户体验、监控、运维管控上进行了平台化、可视化、智能化的建设，提供一系列特色的功能，极大地方便了用户和运维人员的日常使用。

项目地址：[https://github.com/didi/KnowStreaming](https://github.com/didi/KnowStreaming)

官方的一键脚本会将所部署机器上的 MySQL、JDK、ES 等进行删除重装。因此不建议使用它进行部署，下面采用手动部署的方式。

Step0：准备MySQL、ElasticSearch、JDK等基础环境

| 软件名        | 版本要求     |
| ------------- | ------------ |
| MySQL         | v5.7 或 v8.0 |
| ElasticSearch | v7.6+        |
| JDK           | v8+          |

注：这些环境我之前都用Docker搭建过了，我的版本是MySQL5.7、ElasticSearch7.16.2（KnowStreaming目前不支持使用设置了密码的ES，如果设置了就另外再搭一个吧）、JDK8（官方推荐JDK11，但是JDK8也可以用）

Step1：下载安装包并解压

```shell
// 下载安装包
$ wget https://s3-gzpu.didistatic.com/pub/knowstreaming/KnowStreaming-3.0.0-beta.1.tar.gz
// 解压安装包到指定目录
$ tar -zxf KnowStreaming-3.0.0-beta.1.tar.gz -C /data/
```

Step2：导入MySQL数据和ES索引结构

```shell
$ cd /data/KnowStreaming

用Navicat创建数据库，create database know_streaming;
打开./init/sql目录，然后执行里面的这5个sql文件，ddl-ks-km.sql、ddl-logi-job.sql、ddl-logi-security.sql、dml-ks-km.sql、dml-logi.sql

打开 ./bin目录，修改一下init_es_template.sh文件里的ES连接信息，执行该脚本。
```

Step3：修改配置文件

```shell
$ cd /data/KnowStreaming
$ vim ./conf/application.yml

修改监听端口、MySQL及ES连接信息
```

Step4：启动项目

在bin目录有官方提供的启动脚本，但我这里因为没用它的那个方式进行搭建JDK，执行该脚本时报错，这里就不用它了。该项目就是个很常规的Java项目，自己启动就行了。

我这里把conf目录的配置文件都剪切到了libs目录，将其与jar包放置在一起，在bin目录写了个start.sh脚本用于启动程序。

```shell
#!/bin/bash

#define default variable
app_path="/data/KnowStreaming/libs"
app_log="/data/KnowStreaming/app.log"

if [ -e $app_log ]; then
	touch ${app_log}
fi

#goto directory
cd ${app_path}

#start app
nohup java -jar *.jar  1>${app_log} &
tail -fn 100 ${app_log}
exit 0
```

启动后，访问`http://ip:port`地址访问即可，默认账号及密码：`admin` / `admin2022_` 进行登录（另注：`v3.0.0-beta.2`版本开始，默认账号密码为`admin` / `admin`）。若要停止该项目，`lsof -i:port`搭配 `kill -9 PID`使用即可。

![KnowStreaming](https://image.eula.club/quantum/KnowStreaming.jpeg)
