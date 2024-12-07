## 5. Docker搭建中间件服务
### Notice we are including log4j's NDC here (%x)
#### 5.8.5 不停机查看及修改消息保留时长

需求情景：生产者程序将处理后的数据存入Kafka，但消费者的处理能力不行，数据有大量积压。磁盘还有大量空间，为了防止丢数据，需要在不停机的情况下修改kafka的消息保留时长。

基于时间保留：通过保留期属性，消息就有了TTL（time to live 生存时间）。到期后，消息被标记为删除，从而释放磁盘空间。对于kafka主题中所有消息具有相同的生存时间，但可以在创建主题之前设置属性，或对已存在的主题在运行时修改属性。Kafka支持配置保留策略，可以通过以下三个时间配置属性中的一个来进行调整：`log.retention.hours`、`log.retention.minutes`、`log.retention.ms`，Kafka用更高精度值覆盖低精度值，所以log.retention.ms具有最高的优先级。

以4.6.3节搭建的kafka为例，演示如何查看及不停机修改消息保留时长。

[1] 查看全局的消息保留时长

```shell
$ docker exec -it kafka_sasl /bin/bash
$ cd  /opt/kafka_2.11-0.11.0.3
$ grep -i 'log.retention.[hms].*\=' config/server.properties
log.retention.hours=168
```

[2] 不停机修改某个Topic的消息保留时长并查看

```shell
$ docker exec -it kafka_sasl /bin/bash
$ cd  /opt/kafka_2.11-0.11.0.3/bin
$ ./kafka-configs.sh --zookeeper zookeeper_sasl:2181 --alter --entity-name yoyo_admin_topic --entity-type topics --add-config retention.ms=60000
Completed Updating config for entity: topic 'yoyo_admin_topic'.
$ ./kafka-topics.sh --describe --zookeeper zookeeper_sasl:2181 --topic yoyo_admin_topic
Topic:yoyo_admin_topic  PartitionCount:1        ReplicationFactor:1     Configs:retention.ms=60000
        Topic: yoyo_admin_topic Partition: 0    Leader: 0       Replicas: 0     Isr: 0
```

注意事项：

- 需要修改的地方：将`zookeeper_sasl:2181`换成实际的zookeeper地址，将`yoyo_admin_topic`换成实际的topic，为了快速看到效果，保留时长仅设置了60000ms，正式修改按照实际的来。
- 测试流程：提前在topic里写入数据，然后修改topic的消息保留时长并查看，1分钟后去查看该topic的消息是否还存在，发现消息已经被删除了。
