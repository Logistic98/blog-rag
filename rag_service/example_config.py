# -*- coding: utf-8 -*-

class Config:

    # LLM相关配置
    LLM_BASE_URL = 'https://api.openai.com/v1'                            # 接入LLM服务的基础URL
    LLM_API_KEY = 'sk-xxx'                                                # 接入LLM服务的API_KEY，若无需验证可随便传
    LLM_MODEL = 'gpt-4o-mini'                                             # 接入LLM服务的模型选择，若无需验证可随便传

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
    QUESTION_REWRITE_NUM = 2                                              # 问题重写扩展数量（额外扩展的问题数量，不含原问题）
    QUESTION_RETRIEVE_ENABLED = True                                      # 是否开启问题相关性判断
    EMBEDDING_MODEL = '../model_weight/bge-m3'                            # 嵌入模型的路径
    RETRIEVE_TOPK = 5                                                     # 每个问题检索的文档数量
    RERANKING_MODEL = '../model_weight/bge-reranker-v2-m3'                # 重排序模型的路径
    USE_RERANKER = True                                                   # 是否使用重排序模型进行结果优化，建议将其开启

    # 相关性判断策略
    STRATEGY = 'llm'                                                      # 相关性判断策略，可选'llm'或'thres'，选择'llm'的判断更精准一些
    THRESHOLD = 0.85                                                      # 使用'thres'策略时的相关性阈值