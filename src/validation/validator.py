import pandas as pd
import logging

class DataValidator:
    def __init__(self, schemas_config):
        # schemas_config giờ là toàn bộ dictionary 'schemas' từ yaml
        self.schemas = schemas_config 

    def get_rules_by_filename(self, filename):
        """
        Hàm thông minh: Nhìn tên file đoán kiểu dữ liệu
        """
        fname = filename.lower()
        
        if "churn" in fname or "telco" in fname:
            return self.schemas.get('telco', {}).get('required', []), "Telco Schema"
        
        elif "sv" in fname or "student" in fname or "dssv" in fname:
            return self.schemas.get('student', {}).get('required', []), "Student Schema"
            
        else:
            # Nếu không nhận ra, dùng luật Default (cho qua, chỉ warning)
            return self.schemas.get('default', {}).get('required', []), "Default Schema"

    def validate(self, df, filename):
        """
        Validate dựa trên tên file
        """
        # 1. Chọn luật
        required_cols, schema_name = self.get_rules_by_filename(filename)
        
        # 2. Nếu là Default Schema (không bắt buộc cột nào) -> Pass luôn
        if not required_cols:
            return df, pd.DataFrame(), f"Warning: Unknown file type '{filename}'. Skipped strict validation."

        # 3. Kiểm tra Schema
        missing_cols = [col for col in required_cols if col not in df.columns]
        
        if missing_cols:
            msg = f"Failed {schema_name}. Missing columns: {missing_cols}"
            return None, None, msg

        # 4. Kiểm tra dữ liệu rỗng (Logic chung)
        # Giữ lại logic cũ: lọc bỏ dòng mà các cột quan trọng bị Null
        valid_mask = pd.Series([True] * len(df))
        for col in required_cols:
             if col in df.columns:
                valid_mask = valid_mask & (~df[col].isnull())

        clean_df = df[valid_mask].copy()
        error_df = df[~valid_mask].copy()

        return clean_df, error_df, f"Success (Matched {schema_name})"