import sys
import os

# --- CẤU HÌNH ĐƯỜNG DẪN ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# Import pipeline
from src.pipeline.main_flow import run_pipeline

# --- CHẠY THỬ NGHIỆM ---
print("🚀 Đang bắt đầu chạy thử nghiệm thủ công...")

# 1. Kiểm tra xem có file nào trong folder uploads không
upload_dir = os.path.join("data", "uploads")
if not os.path.exists(upload_dir):
    os.makedirs(upload_dir)
    print(f"⚠️ Đã tạo thư mục {upload_dir}. Hãy copy file CSV vào đây!")
    sys.exit()

files = os.listdir(upload_dir)
csv_files = [f for f in files if f.endswith('.csv') or f.endswith('.xlsx')]

if not csv_files:
    print(f"❌ Không tìm thấy file CSV/Excel nào trong {upload_dir}")
    print("👉 Hãy copy file 'telco_customer_churn.csv' vào thư mục 'data/uploads' rồi chạy lại file này.")
else:
    print(f"✅ Tìm thấy {len(csv_files)} file. Bắt đầu xử lý...")
    for f in csv_files:
        file_path = os.path.join(upload_dir, f)
        print(f"\n--- Đang xử lý file: {f} ---")
        try:
            # Gọi hàm xử lý chính
            run_pipeline(file_path)
            print("✅ Xử lý xong! Hãy mở Dashboard kiểm tra.")
        except Exception as e:
            print(f"❌ LỖI LỚN RỒI: {e}")
            import traceback
            traceback.print_exc()