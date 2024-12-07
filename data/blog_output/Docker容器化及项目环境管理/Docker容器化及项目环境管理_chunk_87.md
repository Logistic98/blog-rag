## 5. Docker搭建中间件服务
### 5.10 Docker-ElasticSearch环境搭建
#### 5.10.2 可视化管理ES

**（1）使用Elasticvue浏览器插件**

可借助 [Elasticvue](https://chrome.google.com/webstore/detail/elasticvue/hkedbapjpblbodpgbajblpnlpenaebaa) Chrome插件实现ES数据库的可视化管理，支持所有版本ES。

![elasticvue](https://image.eula.club/quantum/elasticvue.png)

**（2）使用ElasticHD可视化面板**

ElasticHD支持所有版本ES，特色功能是支持“SQL转DSL”。

项目地址：[https://github.com/qax-os/ElasticHD](https://github.com/qax-os/ElasticHD)

```shell
$ docker run -d --name elastichd -p 9800:9800 containerize/elastichd
$ docker update elastichd --restart=always
```

浏览器打开`http://ip:9800/`地址，即可访问面板，在左上角配置ES连接信息即可。如果是带鉴权的ES，按照`http://user:password@xxx.xxx.xxx.xxx:9800`配置ES连接信息即可。

![ElasticHD](https://image.eula.club/quantum/ElasticHD.png)

在Tools——SQL Convert DSL处，可以编写SQL生成操作ES的DSL语句（作为辅助手段使用，一些复杂的SQL可能不适用）

另注：也可以使用一些在线工具进行转换，例如，[https://printlove.cn/tools/sql2es](https://printlove.cn/tools/sql2es)、[http://sql2dsl.atotoa.com](http://sql2dsl.atotoa.com)

**（3）安装kibana可视化插件**

下载与ES版本相同的Kibana

```shell
$ mkdir -p /root/kibana
$ cd /root/kibana
$ wget https://artifacts.elastic.co/downloads/kibana/kibana-7.16.2-linux-x86_64.tar.gz
$ tar -zxvf kibana-7.16.2-linux-x86_64.tar.gz
$ cd /root/kibana/kibana-7.16.2-linux-x86_64
$ vi /config/kibana.yml
```

修改配置文件内容如下（用不到的我这里给删掉了，原配置文件有着很详尽的英文说明）：

```yml
server.port: 5601
server.host: "ip" 
elasticsearch.hosts: ["http://ip:9200"]
elasticsearch.username: "username"
elasticsearch.password: "password"
i18n.locale: "zh-CN"
```

启动kibana：

```shell
$ cd /root/kibana/kibana-7.16.2-linux-x86_64/bin # 进入可执行目录
$ nohup /root/kibana/kibana-7.16.2-linux-x86_64/bin/kibana & # 启动kibana 
```

说明：root用户，会报`Kibana should not be run as root.  Use --allow-root to continue.`的错误，建议切换别的用户去执行，如果就是想用root用户启动，则使用`nohup /root/docker/kibana/kibana-7.16.2-linux-x86_64/bin/kibana --allow-root &`。

启动成功后，浏览器打开`http://ip:5601/`地址，用es的用户名和密码进行登录，就可以使用了。

![Kibana管理面板](https://image.eula.club/quantum/Kibana管理面板.png)

关闭kibana：

```shell
$ ps -ef | grep kibana
$ kill -9 [PID]
```
