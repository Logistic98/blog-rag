## 5. Docker搭建中间件服务
### 5.10 Docker-ElasticSearch环境搭建
#### 5.10.3 安装ik分词器插件

IK 分析插件将 Lucene IK 分析器集成到 elasticsearch 中，支持自定义字典。

- 项目地址：[https://github.com/medcl/elasticsearch-analysis-ik](https://github.com/medcl/elasticsearch-analysis-ik)

安装方式：挂载目录或者进容器下载（版本一定不要安装错，不然就进不去容器了）

- 方式一：去Releases下载对应ES版本的ik分词器插件，然后上传到plugins目录将其挂载到容器内。

- 方式二：进入容器内直接下载对应ES版本的ik分词器插件，并放到相应目录。

  ```shell
  $ docker exec -it es /bin/bash
  $ apt-get install -y wget   
  $ wget https://github.com/medcl/elasticsearch-analysis-ik/releases/download/v7.16.2/elasticsearch-analysis-ik-7.16.2.zip
  $ unzip -o -d /usr/share/elasticsearch/elasticsearch-analysis-ik-7.16.2 /usr/share/elasticsearch/elasticsearch-analysis-ik-7.16.2.zip
  $ rm –f elasticsearch-analysis-ik-7.16.2.zip
  $ mv /usr/share/elasticsearch/elasticsearch-analysis-ik-7.16.2 /usr/share/elasticsearch/plugins/ik
  $ exit
  $ docker restart es
  ```

测试方式：可以进行存在测试和功能测试

```shell
$ docker exec -it es /bin/bash
$ cd /usr/share/elasticsearch/bin
$ elasticsearch-plugin list
```

ik分词器有2种算法：ik_smart和ik_max_word，下面我们通过postman工具来测试ik分词器的分词算法。

[1] 测试ik_smart分词

请求url：http://ip:9200/_analyze      请求方式：get

请求参数：

```json
{
    "analyzer":"ik_smart",
    "text":"我爱你，特靠谱"
}
```

[2] 测试ik_max_word分词

请求url：http://ip:9200/_analyze     请求方式：get

请求参数：

```json
{
    "analyzer":"ik_max_word",
    "text":"我爱你，特靠谱"
}
```

上面测试例子可以看到，不管是ik_smart还是ik_max_word算法，都不认为"特靠谱"是一个关键词（ik分词器的自带词库中没有有"特靠谱"这个词），所以将这个词拆成了三个词：特、靠、谱。

自定义词库：ik分词器会把分词库中没有的中文按每个字进行拆分。如果不想被拆分，那么就需要维护一套自己的分词库。

- Step1：进入`ik分词器路径/config`目录，新建一个`my.dic`文件，添加一些关键词，如"特靠谱"、"靠谱"等，每一行就是一个关键词。

- Step2：修改配置文件`IKAnalyzer.cfg.xml`，配置`<entry key="ext_dict"></entry>`。

  ```xml
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
  <properties>
      <comment>IK Analyzer 扩展配置</comment>
      <!--用户可以在这里配置自己的扩展字典 -->
      <entry key="ext_dict">my.dic</entry>
       <!--用户可以在这里配置自己的扩展停止词字典-->
      <entry key="ext_stopwords"></entry>
      <!--用户可以在这里配置远程扩展字典 -->
      <!-- <entry key="remote_ext_dict">words_location</entry> -->
      <!--用户可以在这里配置远程扩展停止词字典-->
      <!-- <entry key="remote_ext_stopwords">words_location</entry> -->
  </properties>
  ```

- Step3：重启ES，并再次使用Postman测试上述请求，发现"特靠谱"、"靠谱"等将其视为一个词了。
