# File: src/api/main_api.py
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import os
import sys
import yaml
from sqlalchemy import create_engine

# --- CẤU HÌNH ĐƯỜNG DẪN ---
# Để import được các module cũ trong thư mục src
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import các module CŨ của bạn
from src.ingestion.file_uploader import save_uploaded_file
from src.serving.chatbot import Chatbot

# Load Config
with open(os.path.join(project_root, "config", "settings.yaml"), "r") as f:
    config = yaml.safe_load(f)
db_url = config['database']['connection_string']
engine = create_engine(db_url)

# Khởi tạo App FastAPI
app = FastAPI(title="SMB Data Hub API")

# --- CẤU HÌNH CORS (Quan trọng) ---
# Để cho phép giao diện HTML (chạy ở port khác hoặc file local) gọi được vào API này
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Cho phép tất cả nguồn (để demo cho dễ)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- KHỞI TẠO CHATBOT AI ---
try:
    bot = Chatbot(db_url)
    print("✅ API: Chatbot đã sẵn sàng.")
except Exception as e:
    bot = None
    print(f"⚠️ API: Lỗi khởi tạo Chatbot: {e}")

# === ĐỊNH NGHĨA CÁC API ENDPOINTS ===

@app.get("/")
def read_root():
    return {"message": "SMB Data Hub API is running!"}

# 1. API Lấy thống kê Dashboard (Trả về JSON)
@app.get("/api/stats")
def get_dashboard_stats():
    try:
        logs_df = pd.read_sql("SELECT * FROM process_logs", engine)
        total_files = len(logs_df)
        
        total_rows = logs_df['total_rows'].sum() if not logs_df.empty else 0
        clean_rows = logs_df['valid_rows'].sum() if not logs_df.empty else 0
        clean_rate = (clean_rows / total_rows * 100) if total_rows > 0 else 0
        
        return {
            "total_files": int(total_files),
            "clean_rate": round(clean_rate, 1),
            "recent_logs": logs_df.tail(5).to_dict(orient="records")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. API Upload file
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        upload_dir = os.path.join(project_root, config['data_dirs']['upload'])
        # Tái sử dụng hàm save_uploaded_file cũ của bạn!
        # Lưu ý: Cần sửa nhẹ hàm save cũ để nhận object của FastAPI (sẽ hướng dẫn sau nếu lỗi)
        # Ở đây tôi viết lại nhanh logic lưu:
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
            
        return {"filename": file.filename, "status": "Uploaded successfully. Waiting for processing."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. API Chat với AI
class ChatRequest(BaseModel):
    question: str

@app.post("/api/chat")
def chat_with_ai(request: ChatRequest):
    if not bot or not bot.is_ai_ready:
        raise HTTPException(status_code=503, detail="AI Chatbot chưa sẵn sàng.")
    
    try:
        # Gọi lại hàm chatbot cũ của bạn!
        response = bot.process_query(request.question)
        return {"answer": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- CHẠY SERVER ---
# Để chạy file này, dùng lệnh ở Terminal:
# uvicorn src.api.main_api:app --reload --port 8000