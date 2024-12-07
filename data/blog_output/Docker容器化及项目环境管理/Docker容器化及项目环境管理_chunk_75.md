## 5. Docker搭建中间件服务
### 5.7 Docker-RabbitMQ环境搭建
#### 5.7.2 RabbitMQ创建用户并可视化查看

用Chrome访问`http://ip:15672`即可访问RabbitMQ的Web端管理界面，默认用户名和密码都是guest，出现如下界面代表已经成功了。

![RabbitMQ](https://image.eula.club/quantum/RabbitMQ.png)

默认的 guest 账户有访问限制，只能通过本地网络访问，远程网络访问受限，所以在使用时我们一般另外添加用户。

```shell
$ docker exec -i -t rabbitmq  bin/bash  
$ rabbitmqctl add_user root 123456   // 添加用户（实际密码设置复杂一些）
$ rabbitmqctl set_permissions -p / root ".*" ".*" ".*"   // 赋予root用户所有权限
$ rabbitmqctl set_user_tags root administrator           // 赋予root用户administrator角色
$ rabbitmqctl list_users  // 查看所有用户即可看到root用户已经添加成功
$ exit 
```
