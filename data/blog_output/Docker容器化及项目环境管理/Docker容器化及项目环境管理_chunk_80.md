## 5. Docker搭建中间件服务
### Notice we are including log4j's NDC here (%x)
log4j.appender.TRACEFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L][%x] - %m%n
```

configuration.xsl

```xml
<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
<xsl:output method="html"/>
<xsl:template match="configuration">
<html>
<body>
<table border="1">
<tr>
 <td>name</td>
 <td>value</td>
 <td>description</td>
</tr>
<xsl:for-each select="property">
<tr>
  <td><a name="{name}"><xsl:value-of select="name"/></a></td>
  <td><xsl:value-of select="value"/></td>
  <td><xsl:value-of select="description"/></td>
</tr>
</xsl:for-each>
</table>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
```

然后再创建一个 Docker Compose 编排文件。

docker-compose.yml

```yml
version: "3"

services:

  zookeeper:
    image: wurstmeister/zookeeper
    hostname: zookeeper_sasl
    container_name: zookeeper_sasl
    restart: always
    ports:
      - 2181:2181
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      SERVER_JVMFLAGS: -Djava.security.auth.login.config=/opt/zookeeper-3.4.13/secrets/server_jaas.conf
    volumes:
      - ./kafka-sasl/conf:/opt/zookeeper-3.4.13/conf
      - ./kafka-sasl/conf/:/opt/zookeeper-3.4.13/secrets/ 

  kafka:
    image: wurstmeister/kafka:2.11-0.11.0.3
    restart: always
    hostname: broker
    container_name: kafka_sasl
    depends_on:
      - zookeeper
    ports:
      - 9092:9092
    environment:
      KAFKA_BROKER_ID: 0
      KAFKA_ADVERTISED_LISTENERS: SASL_PLAINTEXT://IP:9092
      KAFKA_ADVERTISED_PORT: 9092 
      KAFKA_LISTENERS: SASL_PLAINTEXT://0.0.0.0:9092
      KAFKA_SECURITY_INTER_BROKER_PROTOCOL: SASL_PLAINTEXT
      KAFKA_PORT: 9092 
      KAFKA_SASL_MECHANISM_INTER_BROKER_PROTOCOL: PLAIN
      KAFKA_SASL_ENABLED_MECHANISMS: PLAIN
      KAFKA_AUTHORIZER_CLASS_NAME: kafka.security.auth.SimpleAclAuthorizer
      KAFKA_SUPER_USERS: User:admin
      KAFKA_ALLOW_EVERYONE_IF_NO_ACL_FOUND: "true" #设置为true，ACL机制为黑名单机制，只有黑名单中的用户无法访问，默认为false，ACL机制为白名单机制，只有白名单中的用户可以访问
      KAFKA_ZOOKEEPER_CONNECT: zookeeper_sasl:2181
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_GROUP_INITIAL_REBALANCE_DELAY_MS: 0
      KAFKA_OPTS: -Djava.security.auth.login.config=/opt/kafka/secrets/server_jaas.conf
    volumes:
      - ./kafka-sasl/conf/:/opt/kafka/secrets/
```

编写完毕后，在该文件下的目录下依次执行下面两条命令即可构建好zookeeper和kafka容器：

```shell
$ docker-compose build     // 构建镜像
$ docker-compose up -d     // 运行容器
```

代码请求测试：

```python
# -*- coding: utf-8 -*-

import time
import json
from datetime import datetime
from kafka import KafkaProducer


def producer_event(server_info):
    producer = KafkaProducer(bootstrap_servers=server_info,
                             security_protocol='SASL_PLAINTEXT',
                             sasl_mechanism='PLAIN',
                             sasl_plain_username='admin',
                             sasl_plain_password='your_password')
    topic = "test_kafka_topic"
    print("kafka连接成功")
    for i in range(7200):
        data = {
            "name": "hello world"
        }
        data_json = json.dumps(data)
        producer.send(topic, data_json.encode()).get(timeout=30)
        print("数据推送成功,当前时间为：{},数据为：{}".format(datetime.now(), data_json))
        time.sleep(1)
    producer.close()


server = "IP:9092"
producer_event(server)
```
