## 5. Docker搭建中间件服务
### 5.3 Docker-Oracle环境搭建
#### 5.3.3 修改密码创建用户

```shell
$ sqlplus /nolog  #
$ conn / as sysdba  # 以dba身份登录

# 修改用户system、sys用户的密码 
$ alter user system identified by system;   
$ alter user sys identified by sys;
$ ALTER PROFILE DEFAULT LIMIT PASSWORD_LIFE_TIME UNLIMITED;
```
