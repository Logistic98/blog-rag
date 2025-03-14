# -*- coding: utf-8 -*-

import gc
import os
import hashlib
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

import torch
import numpy as np
from tqdm import tqdm
from pymilvus import FieldSchema, CollectionSchema, DataType, Collection, connections, utility
import redis
from milvus_model.hybrid import BGEM3EmbeddingFunction
from logging.handlers import RotatingFileHandler
from config import Config


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
                is_primary=True,
                description="切片文件，用于唯一标识"
            ),
            FieldSchema(
                name="doc_name",
                dtype=DataType.VARCHAR,
                max_length=255,
                description="文档文件名"
            ),
            FieldSchema(
                name="file_type",
                dtype=DataType.VARCHAR,
                max_length=50,
                description="文件类型（chunk、metadata、toc）"
            ),
            FieldSchema(
                name="chunk_content",
                dtype=DataType.VARCHAR,
                max_length=max_content_length,
                description="切片内容"
            ),
            FieldSchema(
                name="dense_vector",
                dtype=DataType.FLOAT_VECTOR,
                dim=dense_dim,
                description="切片内容的向量化信息"
            )
        ]
        schema = CollectionSchema(fields, description="文档数据知识库")

        if utility.has_collection(col_name):
            col = Collection(col_name)
            logging.info(f"集合 '{col_name}' 已存在。")
        else:
            col = Collection(col_name, schema, consistency_level="Strong")
            logging.info(f"集合 '{col_name}' 创建成功。")

        if not col.has_index():
            logging.info("未找到索引。正在创建索引...")
            dense_index = {"index_type": "IVF_FLAT", "metric_type": "COSINE", "params": {"nlist": 128}}
            col.create_index("dense_vector", dense_index)
            logging.info("索引创建完成。")
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
        """批量更新 Redis 中的文件哈希值。"""
        if file_hashes:
            with self.client.pipeline() as pipe:
                pipe.hset(self.file_hashes_key, mapping=file_hashes)
                pipe.execute()
            logging.info(f"已更新 {len(file_hashes)} 个文件哈希到 Redis。")

    def delete_file_hashes(self, keys):
        """批量从 Redis 删除文件哈希值。"""
        if keys:
            with self.client.pipeline() as pipe:
                pipe.hdel(self.file_hashes_key, *keys)
                pipe.execute()
            logging.info(f"已从 Redis 删除 {len(keys)} 个文件哈希")


def calculate_file_hash(file_path):
    """计算文件内容的哈希值（SHA256）。"""
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
        file_hash = hashlib.sha256(file_content).hexdigest()
        filename = os.path.basename(file_path)
        doc_name = os.path.basename(os.path.dirname(file_path))
        return filename, doc_name, file_hash
    except Exception as e:
        logging.error(f"计算文件哈希时出错：{file_path}, 错误：{e}")
        return None


def get_current_files(data_dir):
    """获取当前目录中所有的文件及其哈希值，用于与已记录的哈希进行比较"""
    current_files = {}
    futures = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        for root, _, files in os.walk(data_dir):
            if os.path.commonpath([data_dir, root]) != data_dir:
                continue
            doc_name = os.path.basename(os.path.relpath(root, data_dir))
            md_files = [f for f in files if f.endswith('.md')]
            for filename in md_files:
                file_path = os.path.abspath(os.path.join(root, filename))
                futures.append(executor.submit(calculate_file_hash, file_path))

        for future in tqdm(as_completed(futures), total=len(futures), desc="计算文件哈希"):
            result = future.result()
            if result:
                filename, doc_name, file_hash = result
                current_files[filename] = (doc_name, file_hash)

    logging.info(f"当前目录中找到 {len(current_files)} 个文件。")
    return current_files


def delete_removed_files(col, redis_manager, existing_file_hashes, current_files):
    """删除已删除文件对应的 Milvus 记录和 Redis 哈希值。"""
    to_delete = [chunk_file for chunk_file in existing_file_hashes if chunk_file not in current_files]

    if to_delete:
        logging.info(f"将删除 {len(to_delete)} 个文件的记录")
        expr = f'chunk_file in ["' + '","'.join(to_delete) + '"]'
        try:
            col.delete(expr=expr)
            logging.info(f"已删除 {len(to_delete)} 个文件的记录")
            redis_manager.delete_file_hashes(to_delete)
            return len(to_delete)
        except Exception as e:
            logging.error(f"删除文件记录时出错：{e}")
            return 0
    else:
        logging.info("没有找到需要删除的文件记录")
        return 0


def determine_file_type(filename):
    """根据文件名确定文件类型。"""
    if "chunk" in filename.lower():
        return "chunk"
    elif "metadata" in filename.lower():
        return "metadata"
    elif "toc" in filename.lower():
        return "toc"
    else:
        return "unknown"


def process_documents(data_dir, collection_name, batch_size, ef, col, redis_manager, max_content_length):
    """文档处理，支持动态调整批次大小和累计进度跟踪。"""
    processed_files_count = 0
    updated_redis_count = 0

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
        file_type = determine_file_type(filename)
        all_files.append((filename, doc_name, file_path, file_hash, file_type))

        previous_hash = existing_file_hashes.get(filename)
        if previous_hash is None:
            added_docs += 1
        elif file_hash != previous_hash:
            updated_docs += 1

    files_to_process = [file for file in all_files if file[3] != existing_file_hashes.get(file[0])]
    total_files = len(files_to_process)
    progress_bar = tqdm(
        desc="处理文件进度",
        total=total_files,
        unit="个文件"
    )

    for batch_files in batch_generator(files_to_process, batch_size):
        chunk_files = []
        doc_names = []
        chunk_contents = []
        file_hashes = {}
        file_types = []

        for filename, doc_name, file_path, file_hash, file_type in batch_files:
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
            except Exception as e:
                logging.error(f"读取文件 {file_path} 时出错：{e}")
                continue

            content_length = len(chunk_content)
            if content_length > max_content_length:
                chunk_content = chunk_content[:max_content_length]
                logging.warning(
                    f"文件 {chunk_file} 内容过大（{content_length} 字符），已截取前 {max_content_length} 个字符。"
                )

            chunk_files.append(chunk_file)
            doc_names.append(doc_name)
            file_types.append(file_type)
            chunk_contents.append(chunk_content)
            file_hashes[chunk_file] = file_hash

        if not chunk_files:
            tqdm.write("当前批次无需要处理的文件，跳过。")
            continue

        try:
            with torch.no_grad():
                embeddings = ef(chunk_contents)["dense"]
                embeddings = embeddings.cpu().numpy() if isinstance(embeddings, torch.Tensor) else np.array(embeddings)
                embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
                entities = [
                    {
                        "chunk_file": cf,
                        "doc_name": dn,
                        "file_type": ft,
                        "chunk_content": cc,
                        "dense_vector": dv
                    }
                    for cf, dn, ft, cc, dv in zip(chunk_files, doc_names, file_types, chunk_contents, embeddings.tolist())
                ]
                col.insert(entities)
                try:
                    redis_manager.update_existing_file_hashes(file_hashes)
                    updated_redis_count += len(file_hashes)
                except Exception as redis_e:
                    logging.error(f"更新 Redis 失败: {redis_e}. 尝试回滚 Milvus 插入.")
                    rollback_expr = f'chunk_file in ["' + '","'.join(chunk_files) + '"]'
                    try:
                        col.delete(expr=rollback_expr)
                        logging.info(f"已回滚 Milvus 中的 {len(chunk_files)} 条记录。")
                    except Exception as rollback_e:
                        logging.error(f"回滚 Milvus 插入时出错：{rollback_e}")
                    raise redis_e

                existing_file_hashes.update(file_hashes)

            try:
                col.flush()
                logging.info("已刷新数据到 Milvus。")
            except Exception as e:
                logging.error(f"刷新数据到 Milvus 时出错：{e}")

        except RuntimeError as e:
            tqdm.write(f"显存不足或其他错误，尝试减小批次大小: {e}")
            batch_size = max(1, batch_size // 2)
            logging.warning(f"批次大小调整为 {batch_size}")
            continue
        except Exception as e:
            logging.error(f"处理批次时出错：{e}")
            continue

        processed_files_count += len(chunk_files)

        del chunk_files, doc_names, file_types, chunk_contents, embeddings, entities
        gc.collect()
        if DEVICE == "cuda":
            torch.cuda.empty_cache()

    try:
        col.flush()
        col.load()
    except Exception as e:
        logging.error(f"最终刷新或加载集合时出错：{e}")

    progress_bar.close()

    logging.info(f"{collection_name} 索引完成")
    logging.info(f"新增文档数: {added_docs}")
    logging.info(f"更新文档数: {updated_docs}")
    logging.info(f"删除文档数: {deleted_docs}")


if __name__ == "__main__":

    class TqdmLoggingHandler(logging.Handler):
        """自定义日志处理器，用于与 tqdm 兼容的日志输出。"""
        def emit(self, record):
            try:
                msg = self.format(record)
                tqdm.write(msg)
            except Exception:
                self.handleError(record)

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    tqdm_handler = TqdmLoggingHandler()
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    tqdm_handler.setFormatter(formatter)
    logger.addHandler(tqdm_handler)

    file_handler = RotatingFileHandler(Config.LOG_FILE, maxBytes=10**6, backupCount=5, encoding='utf-8')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if torch.cuda.is_available():
        DEVICE = "cuda"
    elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
        DEVICE = "mps"
    else:
        DEVICE = "cpu"
    logging.info(f"使用设备: {DEVICE}")

    redis_manager = RedisManager(Config.REDIS_HOST, Config.REDIS_PORT, Config.REDIS_PASSWORD, Config.REDIS_KEY)
    milvus_manager = MilvusManager(Config.MILVUS_HOST, Config.MILVUS_PORT, Config.MILVUS_USER, Config.MILVUS_PASSWORD)

    try:
        ef = BGEM3EmbeddingFunction(
            model_name=Config.BGE_M3_PATH,
            use_fp16=False,
            device=DEVICE,
            batch_size=Config.BATCH_SIZE
        )
        dense_dim = ef.dim["dense"]
        logging.info("嵌入函数初始化成功。")
    except Exception as e:
        logging.error(f"初始化嵌入函数时出错：{e}")
        exit(1)

    try:
        collection = milvus_manager.create_collection(Config.MILVUS_COLLECTION_NAME, dense_dim, Config.MAX_CONTENT_LENGTH)
    except Exception as e:
        logging.error(f"创建或获取 Milvus 集合时出错：{e}")
        exit(1)

    try:
        process_documents(Config.DATA_DIR, Config.MILVUS_COLLECTION_NAME, Config.BATCH_SIZE, ef, collection, redis_manager, Config.MAX_CONTENT_LENGTH)
    except Exception as e:
        logging.error(f"处理文档时出错：{e}")
        exit(1)

    del ef
    del collection
    gc.collect()
    if DEVICE == "cuda":
        torch.cuda.empty_cache()
    logging.info("所有资源已成功释放。")
