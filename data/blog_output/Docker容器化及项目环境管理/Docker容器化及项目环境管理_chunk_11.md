## 2. Nginx配置及项目发布
### 2.2 Nginx配置服务负载均衡
#### 2.2.2 Nginx剔除失效节点

**[1] 失效节点的自动剔除**

在Nginx中实现负载均衡并自动剔除挂掉的服务器，可以通过配置`upstream`块并启用`fail_timeout`和`max_fails`来实现。这样，当某台服务器无法响应时，Nginx会自动停止向其发送请求。

```ini
http {
    upstream backend {
        server server1.example.com max_fails=1 fail_timeout=10s;
        server server2.example.com max_fails=1 fail_timeout=10s;
        server server3.example.com max_fails=1 fail_timeout=10s;
    }

    server {
        listen 80;

        location / {
            proxy_pass http://backend;
        }
    }
}
```

含义解释：

- `max_fails=1`：表示在`fail_timeout`时间内最多允许失败1次。如果超过这个次数，Nginx会将该服务器标记为“不可用”，停止将请求转发给它。
- `fail_timeout=10s`：指定在失败后暂停多长时间，重新尝试将请求发给这台服务器。服务器被标记为不可用，Nginx也会每10秒重新尝试连接该服务器，查看是否恢复正常。

**[2] 自动选用有效节点**

proxy_next_upstream 配置的错误状态码或超时等条件触发时，Nginx会跳转到下一个健康的节点提供服务。

```ini
    # 添加proxy_next_upstream指令，实现失败时的自动跳转
    proxy_next_upstream error timeout http_500 http_502 http_503 http_504;
```
