## 3. Docker环境搭建及使用
### 3.2 Docker环境搭建
#### 3.2.8 解决Docker普通用户无权限问题

给普通用户（如git）添加进Docker组

```shell
$ su git                           // 切换普通用户（如git）
$ sudo usermod -aG docker $USER    // 将当前用户添加到docker组，需要输入git用户密码（忘记了可以在root用户下重置）
$ newgrp docker                    // 激活组权限
```
