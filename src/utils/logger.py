import logging
import os

def setup_logger(name='SMB_Logger', log_file='logs/pipeline.log'):
    # Tạo thư mục logs nếu chưa có
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Format: Thời gian - Mức độ - Thông báo
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    
    # Ghi ra file
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)
    
    # Ghi ra màn hình console
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger