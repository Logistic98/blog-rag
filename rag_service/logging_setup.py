# -*- coding: utf-8 -*-

import logging
import os


def setup_logging(log_path):
    logger = logging.getLogger('rag_server')
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(formatter)
        logger.addHandler(console)
        handler = logging.FileHandler(log_path)
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger


current_dir = os.path.dirname(os.path.abspath(__file__))
log_path = os.path.join(current_dir, 'rag_server.log')
logger = setup_logging(log_path)
