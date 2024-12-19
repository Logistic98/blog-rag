## 5. Docker搭建中间件服务
### 5.8 Docker-Kafka环境搭建
#### 5.8.1 部署单机版Kafka

**[1] 部署ZooKeeper及单机版 Kafka 服务**

kafka的运行依赖于zookeeper，因而编写zookeeper与kafka的编排文件docker-compose.yml内容如下：

```yml
version: '3.2'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - "2181:2181"
    restart: always
  kafka:
    image: wurstmeister/kafka
    container_name: kafka
    ports:
      - "9092:9092"
    environment:
      - KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
      - KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://IP:9092
      - KAFKA_LISTENERS=PLAINTEXT://:9092
    volumes:
      - ./docker.sock:/var/run/docker.sock
    restart: always
```

注：KAFKA_ADVERTISED_LISTENERS 填写为 `PLAINTEXT://IP:9092`，这里的 IP 填写成你的公网 IP，如果没带上这个的话，PC是无法连接到服务器上的 kafka 服务的。这里搭建的 kafka 服务仅用于测试，没有设置用户名及密码，勿用于公网生产环境。

编写完毕后，在该文件下的目录下依次执行下面两条命令即可构建好zookeeper和kafka容器：

```shell
$ docker-compose build     // 构建镜像
$ docker-compose up -d     // 运行容器
```

配置文件目录：`/opt/kafka_2.13-2.8.1/config`

**[2] 验证Kafka是否搭建成功**

进入到kafka容器中 并创建topic生产者，执行如下命令：

```shell
$ docker exec -it kafka /bin/bash
$ cd /opt/kafka_2.13-2.8.1/bin/
$ ./kafka-topics.sh --create --zookeeper zookeeper:2181 --replication-factor 1 --partitions 8 --topic test
$ ./kafka-console-producer.sh --broker-list localhost:9092 --topic test
```

执行上述命令后，另起一个窗口，执行如下命令，创建kafka消费者消费消息。

```shell
$ docker exec -it kafka /bin/bash
$ cd /opt/kafka_2.13-2.8.1/bin/
$ ./kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic test --from-beginning
```

执行完上诉命令后，在生产者窗口中输入任意内容回车，即可在消费者的窗口查看到消息。

注：kafka_2.13-2.8.1的含义为，2.13是Scala版本，2.8.1是Kafka版本。
