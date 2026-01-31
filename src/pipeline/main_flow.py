import sys
import os

# Thêm đoạn này lên đầu file folder_watcher.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import time
from watchdog.observers import Observer



import pandas as pd
import yaml
import os
import shutil
import time
from src.utils.logger import setup_logger
from src.validation.validator import DataValidator
from src.processing.transform import DataTransformer
from src.storage.db_handler import DBHandler
from src.serving.notifier import Notifier

# Load Config
CONFIG_PATH = "config/settings.yaml"
if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

# Khởi tạo các module
logger = setup_logger()
db = DBHandler(config['database']['connection_string'])
validator = DataValidator(config['schemas'])
transformer = DataTransformer()
notifier = Notifier() # Email user/pass có thể lấy từ biến môi trường

def run_pipeline(file_path):
    filename = os.path.basename(file_path)
    logger.info(f"🚀 --- BẮT ĐẦU XỬ LÝ: {filename} ---")
    
    start_time = time.time()
    total_rows = 0
    clean_rows = 0
    error_rows = 0
    
    try:
        # --- BƯỚC 1: DATA INGESTION ---
        # Đọc file vào DataFrame
        if filename.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif filename.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file_path)
        else:
            msg = f"Định dạng file không hỗ trợ: {filename}"
            logger.error(msg)
            db.log_process(filename, 0, 0, 0, "SKIPPED", msg)
            return

        total_rows = len(df)
        
        # Backup file gốc vào Raw Zone
        raw_path = os.path.join(config['data_dirs']['raw'], filename)
        shutil.copy(file_path, raw_path)
        logger.info(f"Đã lưu backup tại: {raw_path}")

        # --- BƯỚC 2: DATA VALIDATION ---
        clean_df, error_df, val_msg = validator.validate(df, filename)
        
        # Nếu lỗi nghiêm trọng (vd: thiếu cột bắt buộc) -> Dừng pipeline
        if clean_df is None:
            logger.error(f"❌ Validation Critical Fail: {val_msg}")
            db.log_process(filename, total_rows, 0, total_rows, "FAILED", val_msg)
            
            # Gửi email cảnh báo Admin
            notifier.send_email(
                "admin@smb-hub.com", 
                f"LỖI NGHIÊM TRỌNG: {filename}", 
                f"File bị từ chối xử lý.\nLý do: {val_msg}"
            )
            return

        # Xử lý các dòng lỗi (nếu có)
        error_rows = len(error_df)
        if not error_df.empty:
            error_path = os.path.join(config['data_dirs']['error'], f"error_{filename}")
            error_df.to_csv(error_path, index=False)
            logger.warning(f"⚠️ Phát hiện {error_rows} dòng lỗi. Chi tiết tại: {error_path}")

        # --- BƯỚC 3: TRANSFORMATION ---
        processed_df = transformer.process(clean_df)
        clean_rows = len(processed_df)

        # --- BƯỚC 4: STORAGE & SERVING ---
        if not processed_df.empty:
            # [LOGIC MỚI] Tự động chọn tên bảng dựa trên tên file
            fname_lower = filename.lower()
            if "sv" in fname_lower or "student" in fname_lower or "ds" in fname_lower:
                target_table = "students_list"  # Lưu vào bảng riêng cho sinh viên
            else:
                target_table = "customers_telco" # Mặc định lưu vào bảng Telco
            
            # Lưu vào Database với tên bảng động
            db.save_clean_data(processed_df, table_name=target_table)
            
            # Lưu file sạch ra folder
            clean_path = os.path.join(config['data_dirs']['clean'], f"clean_{filename}")
            processed_df.to_csv(clean_path, index=False)
            
            # Đồng bộ Google Sheet (Giả lập)
            notifier.sync_to_google_sheet(processed_df, "Data_Report")

        # --- BƯỚC 5: LOGGING METADATA ---
        status = "SUCCESS" if error_rows == 0 else "WARNING"
        processing_time = round(time.time() - start_time, 2)
        
        db.log_process(filename, total_rows, clean_rows, error_rows, status, f"Time: {processing_time}s")
        
        success_msg = (
            f"✅ Hoàn thành xử lý file {filename}.\n"
            f"- Tổng: {total_rows}\n"
            f"- Sạch: {clean_rows}\n"
            f"- Lỗi: {error_rows}"
        )
        logger.info(success_msg)

        # Gửi email báo cáo nếu cần (hoặc chỉ gửi khi có warning)
        if status == "WARNING":
            notifier.send_email("manager@smb-hub.com", f"Báo cáo xử lý: {filename}", success_msg)

        # Cleanup: Xóa file trong uploads sau khi xong để tránh xử lý lại
        if os.path.exists(file_path):
            os.remove(file_path)

    except Exception as e:
        logger.error(f"❌ LỖI HỆ THỐNG (CRASH): {str(e)}")
        db.log_process(filename, total_rows, 0, 0, "CRASH", str(e))
        notifier.send_email("admin@smb-hub.com", "SYSTEM CRASH", str(e))

if __name__ == "__main__":
    # Chế độ chạy thủ công: Quét toàn bộ folder uploads
    upload_dir = config['data_dirs']['upload']
    logger.info(f"Đang quét thư mục: {upload_dir}")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    files = [f for f in os.listdir(upload_dir) if os.path.isfile(os.path.join(upload_dir, f))]
    
    if not files:
        logger.info("Không có file nào trong thư mục uploads.")
    else:
        for f in files:
            run_pipeline(os.path.join(upload_dir, f))