## 5. Docker搭建中间件服务
### Notice we are including log4j's NDC here (%x)
#### 5.8.6 Kafka分区数应设置多少及默认配置

kafka的每个topic都可以创建多个partition，理论上partition的数量无上限。通常情况下，越多的partition会带来越高的吞吐量，但是同时也会给broker节点带来相应的性能损耗和潜在风险，虽然这些影响很小，但不可忽略，所以确定partition的数量需要权衡一些因素。

**[1] 越多的partition可以提供更高的吞吐量**

- 单个partition是kafka并行操作的最小单元。每个partition可以独立接收推送的消息以及被consumer消费，相当于topic的一个子通道，partition和topic的关系就像高速公路的车道和高速公路的关系一样，起始点和终点相同，每个车道都可以独立实现运输，不同的是kafka中不存在车辆变道的说法，入口时选择的车道需要从一而终。
- kafka的吞吐量显而易见，在资源足够的情况下，partition越多速度越快。这里提到的资源充足解释一下，假设我现在一个partition的最大传输速度为p，目前kafka集群共有三个broker，每个broker的资源足够支撑三个partition最大速度传输，那我的集群最大传输速度为3\*3\*p=9p。

**[2] 越多的分区需要打开更多的文件句柄**

- 在kafka的broker中，每个分区都会对照着文件系统的一个目录。
- 在kafka的数据日志文件目录中，每个日志数据段都会分配两个文件，一个索引文件和一个数据文件。因此，随着partition的增多，需要的文件句柄数急剧增加，必要时需要调整操作系统允许打开的文件句柄数。

**[3] 更多的分区会导致端对端的延迟**

- kafka端对端的延迟为producer端发布消息到consumer端消费消息所需的时间，即consumer接收消息的时间减去produce发布消息的时间。
- kafka在消息正确接收后才会暴露给消费者，即在保证in-sync副本复制成功之后才会暴露，瓶颈则来自于此。
- leader broker上的副本从其他broker的leader上复制数据的时候只会开启一个线程，假设partition数量为n，每个副本同步的时间为1ms，那in-sync操作完成所需的时间即`n * 1ms`，若n为10000，则需要10秒才能返回同步状态，数据才能暴露给消费者，这就导致了较大的端对端的延迟。

**[4] 越多的partition意味着需要更多的内存**

- 在新版本的kafka中可以支持批量提交和批量消费，而设置了批量提交和批量消费后，每个partition都会需要一定的内存空间。
- 无限的partition数量很快就会占据大量的内存，造成性能瓶颈。假设每个partition占用的内存为100k，当partition为100时，producer端和consumer端都需要10M的内存；当partition为100000时，producer端和consumer端则都需要10G内存。

**[5] 越多的partition会导致更长时间的恢复期**

- kafka通过多副本复制技术，实现kafka的高可用性和稳定性。每个partition都会有多个副本存在于多个broker中，其中一个副本为leader，其余的为follower。
- kafka集群其中一个broker出现故障时，在这个broker上的leader会需要在其他broker上重新选择一个副本启动为leader，这个过程由kafka controller来完成，主要是从Zookeeper读取和修改受影响partition的一些元数据信息。
- 通常情况下，当一个broker有计划的停机，该broker上的partition leader会在broker停机前有次序的一一移走，假设移走一个需要1ms，10个partition leader则需要10ms，这影响很小，并且在移动其中一个leader的时候，其他九个leader是可用的。因此实际上每个partition leader的不可用时间为1ms。但是在宕机情况下，所有的10个partition
- leader同时无法使用，需要依次移走，最长的leader则需要10ms的不可用时间窗口，平均不可用时间窗口为5.5ms，假设有10000个leader在此宕机的broker上，平均的不可用时间窗口则为5.5s。
- 更极端的情况是，当时的broker是kafka controller所在的节点，那需要等待新的kafka leader节点在投票中产生并启用，之后新启动的kafka leader还需要从zookeeper中读取每一个partition的元数据信息用于初始化数据。在这之前partition leader的迁移一直处于等待状态。

可以在`/config/sever.properties`配置文件中，设置默认分区数，以后每次创建topic默认都是分区数。

以4.6.3节搭建的kafka为例，演示如何修改该配置：

```shell
$ docker exec -it kafka_sasl /bin/bash
$ cd /opt/kafka_2.13-2.8.1/bin/config
$ vi server.properties
```

sever.properties里有如下配置，默认分区数为1，我们可以根据自己需要进行修改

```properties
# The default number of log partitions per topic. More partitions allow greater
# parallelism for consumption, but this will also result in more files across
# the brokers.
num.partitions=10
```

之后退出容器并重启容器

```shell
$ exit
$ docker restart kafka_sasl
```
