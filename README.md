## blog-rag

## 1. 项目简介

针对自己的 [Quantum Bit](https://www.imiao.top/) 博客构建的私域知识问答系统，主要特性如下：

- 数据切片：针对博客文章的特性进行定制化的精准解析与分割，可得到高质量的数据切片，支持增量构建索引。
- 检索系统：采用Milvus向量检索库，利用bge-m3、bge-reranker-v2-m3检索和重排序，有较高检索准确率。
- 基座模型：支持接入OpenAI格式的大模型服务作为问答核心引擎，提供vLLM推理加速和Nginx负载均衡的支持。
- 安全机制：使用到的中间件都配置了账号验证，部署的大模型和RAG服务也都开启了密钥验证，保证其安全性。
- 界面展示：支持分析步骤的展示与流式输出、Markdown格式渲染、参考博客链接的返回，具有较好的页面体验。

![blog-rag效果图](README.assets/display/display.png)

本项目的技术实现细节详见我的博客：[针对自己博客定制的私域知识问答系统](https://www.imiao.top/blogs/针对自己博客定制的私域知识问答系统.html)

## 2. 技术架构

[1] 基础框架

- 后端服务：FastAPI（高性能服务框架，基于Starlette和Pydantic构建而成，具有较好并发支持）
- 前端界面：Vue（目前最主流的三大前端开发框架之一，它是渐进式的，具备简洁易用的特性）

[2] 中间件

- 向量检索库：Milvus（高性能、高扩展性的向量数据库，适于处理海量向量数据的实时召回）
- 高速缓存：Redis（基于内存的数据存储系统，能提供极快速度，适用于需要快速响应的场景）

[3] 模型文件

- 大模型基座：Qwen2.5-7B-Instruct、QWQ-32B（可接入任意大模型服务，是OpenAI格式即可）
- Embedding模型：bge-m3（同时支持密集检索、多向量检索、稀疏检索，有较好混合召回效果）
- 重排序模型：bge-reranker-v2-m3（搜到的文档不都是相关的，重排序可让更相关的文档排前面）

## 3. 核心流程

问题重写——问题扩展——问题相关判断——多数投票——检索文档数据——重排序——文档相关判断——大模型总结

![flowchart](README.assets/flowchart/flowchart.png)

## 4. 部署使用

运行环境：Macbook Pro 2021，M1 pro芯片，16G内存，1024G存储，macOS Sonoma 14.5 系统，Python3.10环境

```ini
.
├── data                        // 数据文件
│   ├── blog_input
│   └── blog_output
├── data_process                // 数据处理
│   ├── config.py
│   ├── build_index.py
│   └── parse_md.py
├── model_weight                // 模型文件
│   ├── QwQ-32B
│   ├── Qwen2.5-7B-Instruct
│   ├── bge-m3
│   └── bge-reranker-v2-m3
├── llm_service                 // 大模型服务
│   ├── llm_server.py
│   ├── llmtuner
│   └── requirements.txt
├── nginx_balance               // 负载均衡
│   ├── Dockerfile
│   ├── build.sh
│   ├── nginx.conf
│   ├── nginx_balance.conf
│   └── proxy.conf
├── milvus                      // 向量检索库
│   └── standalone_embed.sh
├── rag_chat                    // 问答页面
│   ├── .env
│   ├── babel.config.js
│   ├── jsconfig.json
│   ├── package.json
│   ├── public
│   ├── src
│   └── vue.config.js
├── rag_service                // RAG服务
│   ├── requirements.txt
│   ├── config.py
│   ├── fastapi_app.py
│   ├── knowledge_base.py
│   ├── llm.py
│   ├── logging_setup.py
│   ├── models.py
│   ├── prompts.py
│   ├── rag_server.py
│   └── validators.py
└── script                     // 实用脚本
│   ├── download_models.py
│   ├── milvus_password.py
│   ├── requirements.txt
│   └── rag_service_test.sh
├── build.sh 
├── start.sh
├── Dockerfile
└── README.md
```

Step1：安装Conda环境

```shell
$ conda create -n blog_rag python=3.10
$ conda activate blog_rag
```

Step2：安装基础中间件

```shell
// 安装Redis
$ docker pull redis:6.2.12
$ docker run --name redis -p 6379:6379 -d redis:6.2.12 --requirepass "52497Vr62K94qeksg82679o22kr774ee" --appendonly yes

// 安装Milvus
$ mkdir milvus && cd milvus
$ curl -sfL https://raw.githubusercontent.com/milvus-io/milvus/master/scripts/standalone_embed.sh -o standalone_embed.sh
$ chmod u+x ./standalone_embed.sh
$ ./standalone_embed.sh start

// 建议打开Milvus的账号验证
$ docker exec -it milvus-standalone /bin/bash
$ apt-get update && apt-get install vim -y
$ vim /milvus/configs/milvus.yaml                    //  将authorizationEnabled参数改为true
$ exit
$ docker restart milvus-standalone
$ cd script 
$ python3 milvus_password.py
```

Step3：下载所需模型

```shell
$ mkdir model_weight
$ cd script
$ pip3 install -r requirements.txt
$ python3 download_models.py
```

Step4：数据切片及入库

```shell
$ cd data_process 
$ pip3 install -r requirements.txt
$ mv example_config.py config.py
$ vim config.py
```

如果前面的步骤都使用我的默认配置，这里只需要改下Milvus和Redis的IP即可

```python
MILVUS_HOST = "127.0.0.1"                            # Milvus主机地址
MILVUS_PORT = "19530"                                # Milvus端口
MILVUS_COLLECTION_NAME = "vuepress_blog"             # Milvus集合名称
MILVUS_USER = "root"                                 # Milvus用户名
MILVUS_PASSWORD = "cG72vdgVWX5ypaWV"                 # Milvus密码
REDIS_HOST = "127.0.0.1"                             # Redis主机地址
REDIS_PORT = 6379                                    # Redis端口
REDIS_PASSWORD = "52497Vr62K94qeksg82679o22kr774ee"  # Redis密码
REDIS_KEY = "file_hashes"                            # Redis键
BGE_M3_PATH = "../model_weight/bge-m3"               # 模型路径
DATA_DIR = "../data/blog_output"                     # 数据目录
BATCH_SIZE = 5                                       # 批次大小
MAX_CONTENT_LENGTH = 60000                           # 最大内容长度
LOG_FILE = "build_index.log"                         # 日志文件路径
```

执行数据切片及入库的程序

```shell
$ python3 parse_md.py
$ python3 build_index.py
```

Step5：修改后端配置并部署服务

大模型服务可以使用 llm_service 目录的代码进行部署，也可以直接使用商业大模型服务，保证是 OpenAI 格式的即可，部署步骤略。

```shell
$ cd rag_service
$ mv example_config.py config.py
$ vim config.py
```

如果前面的步骤都使用我的默认配置，则这里只需要修改大模型服务配置即可，实测QwQ-32B就可以有比较好的效果。

```shell
# LLM相关配置
LLM_BASE_URL = 'https://xxx.xxx.xxx/v1'                               # 接入LLM服务的基础URL
LLM_API_KEY = 'sk-xxx'                                                # 接入LLM服务的API_KEY
LLM_MODEL = 'gpt-4o-mini'                                             # 接入LLM服务的模型选择
LLM_COT_MODEL = 'deepseek-r1'                                         # 接入推理LLM服务的模型选择

# 本服务的授权验证
API_KEYS = ['sk-67hBSTsaf0qqvpTN2eA5A4433c2343D3867d0f74D8F0322']     # 本服务允许使用的API_KEY列表

# Milvus向量数据库
MILVUS_SERVER = '127.0.0.1'                                           # Milvus服务的IP地址
MILVUS_PORT = '19530'                                                 # Milvus服务的端口号
MILVUS_USER = 'root'                                                  # Milvus服务的用户名
MILVUS_PASSWORD = 'cG72vdgVWX5ypaWV'                                  # Milvus服务的密码
MILVUS_KB_NAME = 'vuepress_blog'                                      # Milvus知识库的名称

# 知识库检索及模型
QUESTION_REWRITE_ENABLED = True                                       # 是否开启重写重写扩展
QUESTION_REWRITE_NUM = 2                                              # 问题重写扩展数量（额外扩展的问题数量）
QUESTION_RETRIEVE_ENABLED = True                                      # 是否开启问题相关性判断
EMBEDDING_MODEL = '../model_weight/bge-m3'                            # 嵌入模型的路径
RETRIEVE_TOPK = 5                                                     # 检索的文档数量上限
RERANKING_MODEL = '../model_weight/bge-reranker-v2-m3'                # 重排序模型的路径
USE_RERANKER = True                                                   # 是否使用重排序模型优化结果

# 相关性判断策略
STRATEGY = 'llm'                                                      # 相关性判断策略，可选'llm'或'thres'
THRESHOLD = 0.85                                                      # 使用'thres'策略时的相关性阈值
```

说明：LLM_API_KEY是大模型服务的密钥，不要将其泄露出去。而API_KEYS是配置RAG服务的密钥（是可以自定义的），若API_KEYS为空列表，则不开启验证，为了保证安全性，还是建议将其开启。

部署后端服务：

```shell
$ cd rag_service
$ pip3 install -r requirements.txt
$ python3 rag_server.py
```

验证接口服务：

```shell
curl --location 'http://127.0.0.1:18888/v1/chat/completions' \
--header 'Content-Type: application/json' \
--header 'Authorization: Bearer sk-67hBSTsaf0qqvpTN2eA5A4433c2343D3867d0f74D8F0322' \
--data '{
  "model": "deepseek-r1",
  "messages": [
    {
      "role": "user",
      "content": "docker容器如何迁移"
    }
  ],
  "stream": true
}'
data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 1, "message": "调整问题上下文指代信息..."}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 1, "message": "根据上下文重写后的问题为：如何迁移Docker容器？"}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 1, "message": "对问题进行重写扩展..."}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 1, "message": "重写扩展为3个问题"}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 2, "message": "判断是否需检索知识库..."}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 3, "message": "检索文档切片中..."}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 3, "message": "数据相关性分析中..."}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 3, "message": "存在2条相关数据"}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": [], "step": 4, "message": "正在总结答案..."}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "<think>", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

...[省略中间思考过程]

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "</think>", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "\n\n", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "要将", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "D", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "ocker", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

...[省略最终回复数据]

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": "。", "step": 4, "message": "正在总结...", "reference": []}, "finish_reason": null}]}

data: {"id": "8d5abe47-36c7-4050-b91a-179af96c833c", "model": "deepseek-r1", "choices": [{"index": 0, "delta": {"role": null, "content": null, "reference": ["Docker容器化及项目环境管理"], "step": 4, "message": "回答完成"}, "finish_reason": null}]}

data: [DONE]
```

Step6：安装前端依赖并启动

```shell
$ cd rag_chat 
$ npm install
$ npm run serve
```

另注：Step5和Step6部署应用程序可以使用Docker一键脚本，如果有GPU环境可以在build.sh里额外加上--gpus all参数。

```shell
$ chmod u+x build.sh
$ ./build.sh
```

启动成功之后，使用Chrome浏览器访问 [http://localhost:28888](http://localhost:28888) 地址即可使用。

![display](README.assets/display/display.gif)
