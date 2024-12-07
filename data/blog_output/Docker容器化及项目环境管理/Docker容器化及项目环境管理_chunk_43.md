## 3. Docker环境搭建及使用
### 3.7 正式环境的前后端分离项目部署
#### 3.7.4 打包镜像并创建容器启动项目

1）初次部署

```shell
切换到工作目录
$ chmod u+x unzip.sh build.sh rebuild.sh
$ ./build.sh
```

启动成功后，项目就部署好了，Chrome访问 `IP:8082`地址即可访问前端页面，8081端口是留给后端的。

2）后续更新

```
切换到工作目录
把 dist.zip 和 web_manage-0.0.1.jar 更换掉，然后执行 rebuild.sh 脚本即可
```
