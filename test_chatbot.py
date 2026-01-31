import sys
import os
import yaml
from dotenv import load_dotenv

# --- 1. CẤU HÌNH ĐƯỜNG DẪN (Để tránh lỗi ModuleNotFoundError) ---
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

# --- 2. LOAD CẤU HÌNH ---
print("🔄 Đang tải cấu hình...")
load_dotenv() # Load file .env

config_path = "config/settings.yaml"
if not os.path.exists(config_path):
    print(f"❌ Lỗi: Không tìm thấy file config tại {config_path}")
    sys.exit(1)

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# --- 3. IMPORT CHATBOT ---
try:
    from src.serving.chatbot import Chatbot
    print("✅ Import module Chatbot thành công.")
except ImportError as e:
    print(f"❌ Lỗi Import: {e}")
    print("👉 Hãy chắc chắn bạn đang chạy file này từ thư mục gốc 'smb_data_hub'")
    sys.exit(1)

# --- 4. BẮT ĐẦU TEST ---
def run_test():
    db_url = config['database']['connection_string']
    print(f"🔌 Đang kết nối Database: {db_url}")
    
    # Khởi tạo Chatbot
    bot = Chatbot(db_url)
    
    # TEST A: Kiểm tra biến môi trường Azure
    print("\n--- [TEST 1] KIỂM TRA BIẾN MÔI TRƯỜNG ---")
    required_vars = ["AZURE_OPENAI_ENDPOINT", "AZURE_OPENAI_API_KEY", "AZURE_OPENAI_DEPLOYMENT_NAME"]
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"❌ Thiếu biến môi trường trong .env: {missing}")
        return
    else:
        print("✅ Đã tìm thấy đủ cấu hình Azure OpenAI.")

    # TEST B: Kiểm tra lấy Context từ DB (RAG)
    print("\n--- [TEST 2] KIỂM TRA LẤY DỮ LIỆU DB (RAG) ---")
    context = bot.get_system_context()
    if "Logs" in context or "chưa có dữ liệu" in context:
        print("✅ Lấy context thành công.")
        print(f"📄 Nội dung context trích xuất (rút gọn): {context[:100]}...")
    else:
        print(f"⚠️ Cảnh báo: Context trả về lạ: {context}")

    # TEST C: Gọi API Azure OpenAI thực tế
    print("\n--- [TEST 3] GỌI API AZURE OPENAI ---")
    question = "Xin chào, hãy tóm tắt tình trạng hệ thống giúp tôi."
    print(f"❓ Câu hỏi test: {question}")
    print("⏳ Đang gửi request lên Azure (vui lòng đợi)...")
    
    try:
        response = bot.process_query(question)
        print("\n🤖 === PHẢN HỒI CỦA AI ===")
        print(response)
        print("===========================")
        
        if "Lỗi" in response or "Error" in response:
            print("❌ Test thất bại: Có lỗi trả về từ AI.")
        else:
            print("✅ Test thành công! Chatbot hoạt động tốt.")
            
    except Exception as e:
        print(f"❌ Test thất bại (Exception): {str(e)}")

if __name__ == "__main__":
    run_test()