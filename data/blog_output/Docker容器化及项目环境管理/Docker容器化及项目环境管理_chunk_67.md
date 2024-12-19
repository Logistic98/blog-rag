## 5. Docker搭建中间件服务
### 5.3 Docker-Oracle环境搭建
#### 5.3.4 用可视化工具连接

在PLSQL里使用 system/system 账号连接，注意服务名不是orcl，而是helowin。

具体可查看tnsnames.ora文件的配置：

```shell
$ vi /home/oracle/app/oracle/product/11.2.0/dbhome_2/network/admin/tnsnames.ora
```
