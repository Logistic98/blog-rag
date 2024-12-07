## 5. Docker搭建中间件服务
### 5.8 Docker-Kafka环境搭建
#### 5.8.3 搭建SASL账号密码验证的Kafka

自0.9.0.0版本开始Kafka社区添加了许多功能用于提高Kafka的安全性，Kafka提供SSL或者SASL两种安全策略。SSL方式主要是通过CA令牌实现，此处主要介绍SASL方式。

新建一个目录，放置以下4个文件（需要改动的只有server_jaas.conf）

```shell
$ mkdir -p ./kafka-sasl/conf
```

zoo.cfg

```ini
# The number of milliseconds of each tick
tickTime=2000
# The number of ticks that the initial 
# synchronization phase can take
initLimit=10
# The number of ticks that can pass between 
# sending a request and getting an acknowledgement
syncLimit=5
# the directory where the snapshot is stored.
# do not use /tmp for storage, /tmp here is just 
# example sakes.
dataDir=/opt/zookeeper-3.4.13/data
# the port at which the clients will connect
clientPort=2181
# the maximum number of client connections.
# increase this if you need to handle more clients
#maxClientCnxns=60
#
# Be sure to read the maintenance section of the 
# administrator guide before turning on autopurge.
#
# http://zookeeper.apache.org/doc/current/zookeeperAdmin.html#sc_maintenance
#
# The number of snapshots to retain in dataDir
autopurge.snapRetainCount=3
# Purge task interval in hours
# Set to "0" to disable auto purge feature
autopurge.purgeInterval=1

authProvider.1=org.apache.zookeeper.server.auth.SASLAuthenticationProvider
requireClientAuthScheme=sasl
jaasLoginRenew=3600000
zookeeper.sasl.client=true
```

server_jaas.conf

```ini
Client {
    org.apache.zookeeper.server.auth.DigestLoginModule required
    username="admin"
    password="your_password";
};

Server {
    org.apache.zookeeper.server.auth.DigestLoginModule required
    username="admin"
    password="your_password"
    user_super="your_password"
    user_admin="your_password";
};

KafkaServer {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="admin"
    password="your_password"
    user_admin="your_password";
};

KafkaClient {
    org.apache.kafka.common.security.plain.PlainLoginModule required
    username="admin"
    password="your_password";
};
```

log4j.properties

```properties
# Define some default values that can be overridden by system properties
zookeeper.root.logger=INFO, CONSOLE
zookeeper.console.threshold=INFO
zookeeper.log.dir=.
zookeeper.log.file=zookeeper.log
zookeeper.log.threshold=DEBUG
zookeeper.tracelog.dir=.
zookeeper.tracelog.file=zookeeper_trace.log

#
# ZooKeeper Logging Configuration
#

# Format is "<default threshold> (, <appender>)+

# DEFAULT: console appender only
log4j.rootLogger=${zookeeper.root.logger}

# Example with rolling log file
#log4j.rootLogger=DEBUG, CONSOLE, ROLLINGFILE

# Example with rolling log file and tracing
#log4j.rootLogger=TRACE, CONSOLE, ROLLINGFILE, TRACEFILE

#
# Log INFO level and above messages to the console
#
log4j.appender.CONSOLE=org.apache.log4j.ConsoleAppender
log4j.appender.CONSOLE.Threshold=${zookeeper.console.threshold}
log4j.appender.CONSOLE.layout=org.apache.log4j.PatternLayout
log4j.appender.CONSOLE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n

#
# Add ROLLINGFILE to rootLogger to get log file output
#    Log DEBUG level and above messages to a log file
log4j.appender.ROLLINGFILE=org.apache.log4j.RollingFileAppender
log4j.appender.ROLLINGFILE.Threshold=${zookeeper.log.threshold}
log4j.appender.ROLLINGFILE.File=${zookeeper.log.dir}/${zookeeper.log.file}

# Max log file size of 10MB
log4j.appender.ROLLINGFILE.MaxFileSize=10MB
# uncomment the next line to limit number of backup files
log4j.appender.ROLLINGFILE.MaxBackupIndex=10

log4j.appender.ROLLINGFILE.layout=org.apache.log4j.PatternLayout
log4j.appender.ROLLINGFILE.layout.ConversionPattern=%d{ISO8601} [myid:%X{myid}] - %-5p [%t:%C{1}@%L] - %m%n


#
# Add TRACEFILE to rootLogger to get log file output
#    Log DEBUG level and above messages to a log file
log4j.appender.TRACEFILE=org.apache.log4j.FileAppender
log4j.appender.TRACEFILE.Threshold=TRACE
log4j.appender.TRACEFILE.File=${zookeeper.tracelog.dir}/${zookeeper.tracelog.file}

log4j.appender.TRACEFILE.layout=org.apache.log4j.PatternLayout
