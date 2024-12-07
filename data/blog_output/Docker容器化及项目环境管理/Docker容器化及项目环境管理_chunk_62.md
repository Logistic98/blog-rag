## 5. Docker搭建中间件服务
### 5.2 Docker-Nginx环境搭建
#### 5.2.3 测试Nginx环境

Step1：新建测试用的`index.html`文件（不配置会出现403报错）

```shell
$ cd /root/docker/nginx/html
$ touch index.html
$ echo "hello world" >> index.html
```

Step2：打开Chrome浏览器，地址输入`IP:port`，出现`hello world`即配置成功。

附：Nginx的常用管理命令

```shell
$ nginx -t                  # 检查nginx配置的语法是否正确
$ nginx -s reload           # 重新加载配置文件，而nginx服务不会中断
```
