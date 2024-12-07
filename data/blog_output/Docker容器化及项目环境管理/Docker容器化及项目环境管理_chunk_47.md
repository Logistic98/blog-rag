## 3. Docker环境搭建及使用
### 3.9 使用Docker Buildx构建跨架构镜像
#### 3.9.1 服务器架构导致的镜像兼容问题

情景描述：由于客户涉密环境不能联网，因此提前准备了离线镜像。但由于我们是使用的x86架构服务器，而客户是使用的是国产arm架构服务器，部署不兼容。

报错信息：WARNING: The reguested image's platform (linux/and64) does not match the detected host platform (linux/arm64/v8) and no specific platform was requested.

解决方案：使用Docker Buildx进行跨平台构建或者找一台相同架构的服务器进行构建，可以使用 arch 命令查看硬件架构。
