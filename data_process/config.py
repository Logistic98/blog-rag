# -*- coding: utf-8 -*-

class Config:

    MILVUS_HOST = "98.142.139.99"                        # Milvus主机地址
    MILVUS_PORT = "19530"                                # Milvus端口
    MILVUS_COLLECTION_NAME = "vuepress_blog"             # Milvus集合名称
    MILVUS_USER = "root"                                 # Milvus用户名
    MILVUS_PASSWORD = "sf72vdgVWX5ypaWV"                 # Milvus密码
    REDIS_HOST = "98.142.139.99"                         # Redis主机地址
    REDIS_PORT = 6382                                    # Redis端口
    REDIS_PASSWORD = "33497Vr62K94qeksg82679o22kr774ee"  # Redis密码
    REDIS_KEY = "file_hashes"                            # Redis键
    BGE_M3_PATH = "../model_weight/bge-m3"               # 模型路径
    DATA_DIR = "../data/blog_output"                     # 数据目录
    BATCH_SIZE = 5                                       # 批次大小
    MAX_CONTENT_LENGTH = 60000                           # 最大内容长度
    LOG_FILE = "build_index.log"                         # 日志文件路径