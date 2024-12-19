## 5. Docker搭建中间件服务
### 5.8 Docker-Kafka环境搭建
#### 5.8.2 部署集群版Kafka

把编排文件docker-compose.yml修改成如下内容，即可部署集群版Kafka（如下是3个节点，如果需要更多可以在后面继续追加）

```yml
version: '3.3'
services:
  zookeeper:
    image: wurstmeister/zookeeper
    container_name: zookeeper
    ports:
      - 2181:2181
    volumes:
      - ./data/zookeeper/data:/data
      - ./data/zookeeper/datalog:/datalog
      - ./data/zookeeper/logs:/logs
    restart: always
  kafka1:
    image: wurstmeister/kafka
    depends_on:
      - zookeeper
    container_name: kafka1
    ports:
      - 9092:9092
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://IP:9092
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092
      KAFKA_LOG_DIRS: /data/kafka-data
      KAFKA_LOG_RETENTION_HOURS: 168
    volumes:
      - ./data/kafka1/data:/data/kafka-data
    restart: unless-stopped  
  kafka2:
    image: wurstmeister/kafka
    depends_on:
      - zookeeper
    container_name: kafka2
    ports:
      - 9093:9093
    environment:
      KAFKA_BROKER_ID: 2
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://IP:9093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9093
      KAFKA_LOG_DIRS: /data/kafka-data
      KAFKA_LOG_RETENTION_HOURS: 168
    volumes:
      - ./data/kafka2/data:/data/kafka-data
    restart: unless-stopped
  kafka3:
    image: wurstmeister/kafka
    depends_on:
      - zookeeper
    container_name: kafka3
    ports:
      - 9094:9094
    environment:
      KAFKA_BROKER_ID: 3
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://IP:9094
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9094
      KAFKA_LOG_DIRS: /data/kafka-data
      KAFKA_LOG_RETENTION_HOURS: 168
    volumes:
      - ./data/kafka3/data:/data/kafka-data
    restart: unless-stopped
```
