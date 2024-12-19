## 4. 搭建Harbor私有Docker镜像仓库
### 4.2 搭建Harbor镜像仓库
#### 4.2.2 下载安装包并修改配置文件

```shell
$ cd /root/Harbor
$ wget https://github.com/goharbor/harbor/releases/download/v2.7.0/harbor-offline-installer-v2.7.0.tgz
$ tar -xvf harbor-offline-installer-v2.7.0.tgz
$ cd harbor
$ cp -ar harbor.yml.tmpl harbor.yml      # 复制配置文件并改名为harbor.yml
$ vim harbor.yml
```

修改了的配置如下，https的配置整个注释掉，其余的配置项没动。

```
hostname: 111.111.111.111
http:
  port: 10010
harbor_admin_password: your_harbor_admin_password
database:
  password: your_db_password
data_volume: /data/harbor
```

注：hostname设置成你的服务器IP（这里脱敏成111.111.111.111），http的端口我这里改成了10010，harbor_admin_password是你的harbor管理员登录密码，database我只改了数据库密码，data_volume改了一下挂载路径。配置文件里有详细的注释说明，如果要改其他的，根据说明进行修改即可。
