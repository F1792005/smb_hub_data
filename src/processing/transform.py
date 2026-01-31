import pandas as pd

class DataTransformer:
    def process(self, df):
        # 1. Chuẩn hóa Churn -> 0/1 [cite: 175]
        if 'Churn' in df.columns:
            df['Churn'] = df['Churn'].apply(lambda x: 1 if x == 'Yes' else 0)
        
        # 2. Ép kiểu TotalCharges (xử lý chuỗi rỗng thành 0) [cite: 176]
        if 'TotalCharges' in df.columns:
            df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce').fillna(0)
            
        # 3. Tạo cột mới (Feature Engineering) [cite: 178]
        # avg_charge = TotalCharges / tenure (tránh chia cho 0)
        if 'tenure' in df.columns and 'TotalCharges' in df.columns:
            df['avg_charge_per_month'] = df.apply(
                lambda row: row['TotalCharges'] / row['tenure'] if row['tenure'] > 0 else 0, 
                axis=1
            )
            
        return df