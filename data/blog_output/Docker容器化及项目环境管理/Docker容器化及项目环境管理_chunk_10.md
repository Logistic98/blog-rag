## 2. Nginx配置及项目发布
### 2.2 Nginx配置服务负载均衡
#### 2.2.1 Nginx负载均衡方式

**[1] 轮询**

轮询方式是Nginx负载默认的方式，所有请求都按照时间顺序分配到不同的服务上，如果服务挂掉了，可以自动剔除。

```ini
upstream  nginx_balance {
        server xxx.xxx.xxx.xxx:1701;
        server xxx.xxx.xxx.xxx:1702;
}
```

**[2] 权重**

指定每个服务的权重比例，weight和访问比率成正比，通常用于后端服务机器性能不统一，将性能好的分配权重高来发挥服务器最大性能，如下配置后1702服务的访问频率会是1701服务的2倍。

```ini
upstream nginx_balance {
        server xxx.xxx.xxx.xxx:1701 weight=1;
        server xxx.xxx.xxx.xxx:1702 weight=2;
}
```

**[3] iphash**

每个请求都根据访问ip的hash结果分配，经过这样的处理，每个访客固定访问一个后端服务。

```ini
upstream nginx_balance {
			  ip_hash;
        server xxx.xxx.xxx.xxx:1701 weight=1;
        server xxx.xxx.xxx.xxx:1702 weight=2;
}
```

注意：配置之后，再访问主服务时，当前IP地址固定访问其中的一个地址，不会再发生变更了，ip_hash可以和weight配合使用。

**[4] 最少连接**

将请求分配到连接数最少的服务上

```ini
upstream nginx_balance {
			  least_conn;
        server xxx.xxx.xxx.xxx:1701 weight=1;
        server xxx.xxx.xxx.xxx:1702 weight=2;
}
```
