import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

class DBHandler:
    def __init__(self, connection_string):
        self.engine = create_engine(connection_string)
        self.init_metadata_table()

    def init_metadata_table(self):
        # Tạo bảng log xử lý nếu chưa có
        query = """
        CREATE TABLE IF NOT EXISTS process_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            upload_time TIMESTAMP,
            total_rows INTEGER,
            valid_rows INTEGER,
            error_rows INTEGER,
            status TEXT,
            error_message TEXT
        )
        """
        with self.engine.connect() as conn:
            conn.execute(text(query))

    def log_process(self, file_name, total, valid, error, status, msg=""):
        # Ghi nhận lịch sử xử lý file (Data Lineage) [cite: 94]
        data = {
            "file_name": file_name,
            "upload_time": datetime.now(),
            "total_rows": total,
            "valid_rows": valid,
            "error_rows": error,
            "status": status,
            "error_message": msg
        }
        df = pd.DataFrame([data])
        df.to_sql('process_logs', self.engine, if_exists='append', index=False)
    
    def save_clean_data(self, df, table_name="customers_telco"):
        # Lưu dữ liệu sạch vào DB [cite: 182]
        df.to_sql(table_name, self.engine, if_exists='append', index=False)
        
    def get_logs(self):
        return pd.read_sql("SELECT * FROM process_logs ORDER BY upload_time DESC", self.engine)