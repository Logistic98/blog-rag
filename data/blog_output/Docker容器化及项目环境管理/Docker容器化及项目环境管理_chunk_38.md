## 3. Docker环境搭建及使用
### 3.6 动态接入服务地址的前端容器化部署
#### 3.6.2 配置文件及使用方式

这里以Vue项目为例，配置文件采用的config.json。

Dockerfile

```Dockerfile
# 基于Node官方镜像
FROM node:lts

# 创建并设置工作目录
WORKDIR /code

# 复制项目文件到工作目录
COPY . /code/

# 安装依赖
RUN npm install --registry=http://registry.npm.taobao.org

# 安装jq命令
RUN apt-get update && apt-get install -y jq

# entrypoint.sh赋予可执行权限
RUN chmod +x /code/entrypoint.sh

# 使用entrypoint.sh作为入口点
ENTRYPOINT ["/code/entrypoint.sh"]

# 启动前端
CMD ["npm", "run", "serve"]
```

config.json

```json
{
  "算法服务1": "",
  "算法服务2": ""
}
```

entrypoint.sh

```shell
#!/bin/bash

# 检查 CONFIG_JSON_PATH 环境变量是否已设置，并提供默认值
CONFIG_JSON_PATH=${CONFIG_JSON_PATH:-"/code/src/config.json"}

# 环境变量与 config.json 中字段的映射关系
declare -A env_config_map=(
    ["API_URL_1"]="算法服务1"
    ["API_URL_2"]="算法服务2"
)

# 使用 jq 更新 config.json 中的值
for env_var in "${!env_config_map[@]}"; do
    config_key=${env_config_map[$env_var]}
    env_value=$(eval echo \$$env_var)
    if [ -n "$env_value" ]; then
        jq --arg key "$config_key" --arg value "$env_value" \
           '.[$key] = $value' $CONFIG_JSON_PATH > $CONFIG_JSON_PATH.temp && mv $CONFIG_JSON_PATH.temp $CONFIG_JSON_PATH
    fi
done

exec "$@"
```

build.sh

```shell
docker build -t vue-demo-image .
docker run -d --name vue-demo  \
           -p 54320:54320   \
           -e API_URL_1=http://xxx.xxx.xxx.xxx:54321/api/xxx \
           -e API_URL_2=http://xxx.xxx.xxx.xxx:54322/api/xxx \
           vue-demo-image:latest
docker update vue-demo --restart=always
```
