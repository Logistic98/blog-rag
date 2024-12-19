# -*- coding: utf-8 -*-

import os
import torch
import gc
import logging
import hashlib
import numpy as np
from tqdm import tqdm
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection, connections
import redis
from milvus_model.hybrid import BGEM3EmbeddingFunction


def batch_generator(iterable, batch_size):
    """生成器函数，将可迭代对象分批次返回。"""
    batch = []
    for item in iterable:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


class MilvusManager:
    """Milvus管理类，负责集合的创建、索引和操作。"""
    def __init__(self, host, port, user, password):
        connections.connect(
            alias="default",
            host=host,
            port=port,
            user=user,
            password=password
        )

    def create_collection(self, col_name, dense_dim, max_content_length):
        """创建或获取 Milvus 集合，并创建索引。"""
        fields = [
            FieldSchema(
                name="chunk_file",
                dtype=DataType.VARCHAR,
                max_length=255,
                is_primary=True
            ),
            FieldSchema(
                name="doc_name",
                dtype=DataType.VARCHAR,
                max_length=255
            ),
            FieldSchema(
                name="chunk_content",
                dtype=DataType.VARCHAR,
                max_length=max_content_length
            ),
            FieldSchema(
                name="dense_vector",
                dtype=DataType.FLOAT_VECTOR,
                dim=dense_dim
            ),
        ]
        schema = CollectionSchema(fields, description="Schema for blog data storage")
        col = Collection(col_name, schema, consistency_level="Strong")

        if not col.has_index():
            logging.info("未找到索引。正在创建索引...")
            dense_index = {"index_type": "FLAT", "metric_type": "L2"}
            col.create_index("dense_vector", dense_index)
        else:
            logging.info("索引已存在，使用现有索引。")
        return col


class RedisManager:
    """Redis管理类，负责哈希记录的获取和更新。"""
    def __init__(self, host, port, password, file_hashes_key):
        self.client = redis.Redis(host=host, port=port, password=password, decode_responses=True)
        self.file_hashes_key = file_hashes_key

    def get_existing_file_hashes(self):
        """从 Redis 获取所有已存在的文件哈希值。"""
        existing_hashes = self.client.hgetall(self.file_hashes_key)
        logging.info(f"已记录的文件哈希总数：{len(existing_hashes)}")
        return existing_hashes

    def update_existing_file_hashes(self, file_hashes):
        """更新 Redis 中的文件哈希值。"""
        if file_hashes:
            self.client.hset(self.file_hashes_key, mapping=file_hashes)
            logging.info(f"已更新 {len(file_hashes)} 个文件哈希到 Redis。")

    def delete_file_hashes(self, keys):
        """从 Redis 删除文件哈希值。"""
        if keys:
            self.client.hdel(self.file_hashes_key, *keys)
            logging.info(f"已从 Redis 删除 {len(keys)} 个文件哈希")


def calculate_file_hash(file_path):
    """计算文件内容的哈希值（SHA256）。"""
    with open(file_path, 'rb') as f:
        file_content = f.read()
    return hashlib.sha256(file_content).hexdigest()


def get_current_files(data_dir):
    """获取当前目录中所有的文件及其哈希值，用于与已记录的哈希进行比较"""
    current_files = {}
    for root, _, files in os.walk(data_dir):
        if os.path.commonpath([data_dir, root]) != data_dir:
            continue
        doc_name = os.path.relpath(root, data_dir)
        doc_name = os.path.basename(doc_name)
        md_files = [
            f for f in files if f.endswith('.md')
        ]
        for filename in md_files:
            file_path = os.path.abspath(os.path.join(root, filename))
            file_hash = calculate_file_hash(file_path)
            current_files[filename] = (doc_name, file_hash)
    return current_files


def delete_removed_files(col, redis_manager, existing_file_hashes, current_files):
    """删除已删除文件对应的 Milvus 记录和 Redis 哈希值。"""
    to_delete = [chunk_file for chunk_file in existing_file_hashes if chunk_file not in current_files]

    if to_delete:
        logging.info(f"将删除 {len(to_delete)} 个文件的记录")
        expr = f'chunk_file in ["' + '","'.join(to_delete) + '"]'
        col.delete(expr=expr)
        logging.info(f"已删除 {len(to_delete)} 个文件的记录")
        redis_manager.delete_file_hashes(to_delete)
        return len(to_delete)
    else:
        logging.info("没有找到需要删除的文件记录")
        return 0


def process_documents(data_dir, collection_name, batch_size, ef, col, redis_manager, max_content_length, flush_interval, model_reload_interval):
    """文档处理，支持动态调整批次大小和累计进度跟踪。"""
    processed_files_count = 0
    updated_redis_count = 0
    current_batch = 0

    added_docs = 0
    updated_docs = 0
    deleted_docs = 0

    col.load()
    existing_file_hashes = redis_manager.get_existing_file_hashes()
    current_files = get_current_files(data_dir)
    deleted_docs += delete_removed_files(col, redis_manager, existing_file_hashes, current_files)
    col.release()

    all_files = []
    for filename, (doc_name, file_hash) in current_files.items():
        file_path = os.path.join(data_dir, doc_name, filename)
        if not os.path.exists(file_path):
            logging.error(f"文件 {file_path} 不存在，跳过处理。")
            continue
        all_files.append((filename, doc_name, file_path, file_hash))

        previous_hash = existing_file_hashes.get(filename)
        if previous_hash is None:
            added_docs += 1
        elif file_hash != previous_hash:
            updated_docs += 1

    total_files = len([file for file in all_files if file[3] != existing_file_hashes.get(file[0])])
    progress_bar = tqdm(
        desc="处理文件进度",
        total=total_files,
        unit="个文件"
    )

    for batch_files in batch_generator(all_files, batch_size):
        chunk_files = []
        doc_names = []
        chunk_contents = []
        file_hashes = {}

        for filename, doc_name, file_path, file_hash in batch_files:
            chunk_file = filename
            previous_hash = existing_file_hashes.get(chunk_file)

            progress_bar.update(1)

            if previous_hash is not None and file_hash == previous_hash:
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    chunk_content = f.read()
            except FileNotFoundError:
                logging.error(f"文件 {file_path} 不存在，跳过处理。")
                continue

            content_length = len(chunk_content)
            if content_length > max_content_length:
                chunk_content = chunk_content[:max_content_length]
                logging.warning(
                    f"文件 {chunk_file} 内容过大（{content_length} 字符），已截取前 {max_content_length} 个字符。"
                )

            chunk_files.append(chunk_file)
            doc_names.append(doc_name)
            chunk_contents.append(chunk_content)
            file_hashes[chunk_file] = file_hash

        if not chunk_files:
            tqdm.write("当前批次无需要处理的文件，跳过。")
            continue

        try:
            with torch.no_grad():
                embeddings_list = []
                for sub_batch in batch_generator(chunk_contents, batch_size // 2):
                    embeddings = ef(sub_batch)
                    embeddings_list.extend(embeddings["dense"])

                if isinstance(embeddings_list, list):
                    embeddings_list = np.array(embeddings_list)
                elif isinstance(embeddings_list, torch.Tensor):
                    embeddings_list = embeddings_list.cpu().numpy()

                col.insert([
                    chunk_files,
                    doc_names,
                    chunk_contents,
                    embeddings_list.tolist()
                ])

                existing_file_hashes.update(file_hashes)
                redis_manager.update_existing_file_hashes(file_hashes)
                updated_redis_count += len(file_hashes)

                tqdm.write(f"已更新 {len(file_hashes)} 个文件哈希到 Redis。")

        except RuntimeError as e:
            tqdm.write(f"显存不足或其他错误，尝试减小批次大小: {e}")
            batch_size = max(1, batch_size // 2)
            continue

        processed_files_count += len(chunk_files)
        current_batch += 1

        if processed_files_count % flush_interval == 0:
            col.flush()

        if current_batch % model_reload_interval == 0:
            tqdm.write("正在重载模型以释放内存...")
            del ef
            torch.cuda.empty_cache()
            gc.collect()
            ef = BGEM3EmbeddingFunction(
                model_name=BGE_M3_PATH,
                use_fp16=False,
                device=DEVICE,
                batch_size=BATCH_SIZE
            )

        del chunk_files, doc_names, chunk_contents, embeddings_list
        torch.cuda.empty_cache()
        gc.collect()

    col.flush()
    col.load()

    progress_bar.close()

    logging.info(f"{collection_name} 索引完成")
    logging.info(f"新增文档数: {added_docs}")
    logging.info(f"更新文档数: {updated_docs}")
    logging.info(f"删除文档数: {deleted_docs}")


if __name__ == "__main__":

    # 配置项
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
    MODEL_RELOAD_INTERVAL = 5                            # 模型重载间隔
    DATA_DIR = "../data/blog_output"                     # 数据目录
    BATCH_SIZE = 5                                       # 批次大小
    MAX_CONTENT_LENGTH = 60000                           # 最大内容长度
    FLUSH_INTERVAL = 5                                   # 刷新间隔
    LOG_FILE = "build_index.log"                         # 日志文件路径

    class TqdmLoggingHandler(logging.Handler):
        def __init__(self, level=logging.NOTSET):
            super().__init__(level)

        def emit(self, record):
            try:
                msg = self.format(record)
                tqdm.write(msg)
                self.flush()
            except Exception:
                self.handleError(record)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    tqdm_handler = TqdmLoggingHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    tqdm_handler.setFormatter(formatter)
    logger.addHandler(tqdm_handler)

    file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if torch.cuda.is_available():
        DEVICE = "cuda"
    elif torch.backends.mps.is_available():
        DEVICE = "mps"
    else:
        DEVICE = "cpu"
    logging.info(f"使用设备: {DEVICE}")

    redis_manager = RedisManager(REDIS_HOST, REDIS_PORT, REDIS_PASSWORD, REDIS_KEY)
    milvus_manager = MilvusManager(MILVUS_HOST, MILVUS_PORT, MILVUS_USER, MILVUS_PASSWORD)

    ef = BGEM3EmbeddingFunction(
        model_name=BGE_M3_PATH,
        use_fp16=False,
        device=DEVICE,
        batch_size=BATCH_SIZE
    )
    dense_dim = ef.dim["dense"]

    collection = milvus_manager.create_collection(MILVUS_COLLECTION_NAME, dense_dim, MAX_CONTENT_LENGTH)

    process_documents(
        DATA_DIR,
        MILVUS_COLLECTION_NAME,
        BATCH_SIZE,
        ef,
        collection,
        redis_manager,
        MAX_CONTENT_LENGTH,
        FLUSH_INTERVAL,
        MODEL_RELOAD_INTERVAL
    )
