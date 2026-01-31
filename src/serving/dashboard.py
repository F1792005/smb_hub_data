
import sys
import os

# --- [BẮT BUỘC] ĐOẠN CODE NÀY PHẢI NẰM TRÊN CÙNG ---
# Giúp Python tìm thấy thư mục gốc 'smb_data_hub'
current_dir = os.path.dirname(os.path.abspath(__file__))
# Đi ngược lên 2 cấp thư mục: src/serving -> src -> smb_data_hub
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)
# ---------------------------------------------------

# SAU ĐÓ MỚI ĐƯỢC IMPORT CÁC MODULE KHÁC
import streamlit as st
import pandas as pd
import yaml
import time
from sqlalchemy import create_engine, text
from src.storage.db_handler import DBHandler
# Import các module tự viết
try:
    from src.serving.chatbot import Chatbot
    from src.ingestion.file_uploader import save_uploaded_file
except ModuleNotFoundError as e:
    st.error(f"Lỗi không tìm thấy module: {e}")
    st.info("Hãy kiểm tra xem bạn đã tạo file '__init__.py' trong các thư mục src, src/ingestion chưa?")
    st.stop()

# --- CẤU HÌNH TRANG ---
st.set_page_config(page_title="SMB Data Hub", layout="wide", page_icon="🏢")

# Load Config
config_path = os.path.join(project_root, "config", "settings.yaml")
if not os.path.exists(config_path):
    st.error(f"Không tìm thấy file config tại: {config_path}")
    st.stop()

with open(config_path, "r") as f:
    config = yaml.safe_load(f)

# Khởi tạo DBHandler để nó tự động chạy lệnh CREATE TABLE nếu chưa có
try:
    DBHandler(config['database']['connection_string'])
except Exception as e:
    st.error(f"Lỗi khởi tạo Database: {e}")
# -----------------------

# Kết nối DB & Chatbot
db_url = config['database']['connection_string']
engine = create_engine(db_url)
bot = Chatbot(db_url)

# --- SIDEBAR: UPLOAD & SETTINGS ---
with st.sidebar:
    st.title("📂 Data Ingestion")
    st.info("Upload file Excel/CSV để chạy pipeline tự động.")
    
    uploaded_file = st.file_uploader("Chọn file dữ liệu", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        if st.button("🚀 Upload & Process"):
            # 1. Upload file
            with st.spinner("Đang tải file lên hệ thống..."):
                upload_dir = os.path.join(project_root, config['data_dirs']['upload'])
                success, msg = save_uploaded_file(uploaded_file, upload_dir)
            
            if success:
                # 2. Tạo hộp thông báo trạng thái chờ
                status_box = st.info(f"⏳ File `{uploaded_file.name}` đã vào hàng đợi. Đang chờ xử lý...")
                progress_bar = st.progress(0)
                
                # 3. Vòng lặp kiểm tra (Polling) xem xong chưa
                # Thử tối đa 20 lần, mỗi lần đợi 1 giây (Tổng 20s)
                max_retries = 20
                is_processed = False
                
                for i in range(max_retries):
                    time.sleep(1) # Đợi 1 giây
                    progress_bar.progress((i + 1) / max_retries)
                    
                    # Truy vấn thử vào Database xem file này đã xuất hiện trong bảng logs chưa
                    try:
                        # Query tìm file mới nhất có tên trùng khớp
                        check_query = f"SELECT status FROM process_logs WHERE file_name = '{uploaded_file.name}' ORDER BY upload_time DESC LIMIT 1"
                        df_check = pd.read_sql(check_query, engine)
                        
                        if not df_check.empty:
                            # Nếu tìm thấy dữ liệu -> Nghĩa là Pipeline đã chạy xong!
                            is_processed = True
                            break
                    except Exception:
                        pass # Bỏ qua lỗi kết nối tạm thời nếu có
                
                # 4. Xử lý kết quả
                if is_processed:
                    progress_bar.progress(100)
                    status_box.success("✅ Đã xử lý xong! Đang cập nhật Dashboard...")
                    time.sleep(1) # Để người dùng kịp đọc thông báo
                    st.rerun() # Tự động F5
                else:
                    status_box.warning("⚠️ File lớn hoặc hệ thống bận. Vui lòng F5 thủ công sau vài giây.")
            else:
                st.error(f"Lỗi upload: {msg}")

    st.divider()
    # --- [THÊM ĐOẠN NÀY VÀO CUỐI SIDEBAR] ---
    st.subheader("⚠️ Quản trị")
    if st.button("🗑️ Reset Toàn Bộ Hệ Thống"):
        with st.spinner("Đang làm sạch hệ thống..."):
            import shutil
            
            # 1. Xóa dữ liệu trong Database
            try:
                with engine.connect() as conn:
                    conn.execute(text("DELETE FROM process_logs"))
                    try:
                        conn.execute(text("DELETE FROM customers_telco"))
                    except:
                        pass
                    
                    # Reset bộ đếm ID (cho SQLite)
                    try:
                        conn.execute(text("DELETE FROM sqlite_sequence WHERE name='process_logs'"))
                    except:
                        pass
                        
                    conn.commit()
            except Exception as e:
                st.error(f"Lỗi khi xóa DB: {e}")
            
            # 2. Xóa file trong các thư mục
            folders_to_clean = [
                os.path.join(project_root, "data", "raw"),
                os.path.join(project_root, "data", "clean"),
                os.path.join(project_root, "data", "error"),
                os.path.join(project_root, "data", "uploads"),
                os.path.join(project_root, "logs")
            ]
            
            for folder_path in folders_to_clean:
                if os.path.exists(folder_path):
                    for filename in os.listdir(folder_path):
                        file_path = os.path.join(folder_path, filename)
                        try:
                            if os.path.isfile(file_path) or os.path.islink(file_path):
                                os.unlink(file_path)
                            elif os.path.isdir(file_path):
                                shutil.rmtree(file_path)
                        except Exception as e:
                            print(f"Không xóa được {file_path}: {e}")

            # [QUAN TRỌNG] 3. Xóa sạch Session State (Bộ nhớ tạm)
            # Bước này giúp xóa lịch sử chat và các biến đã lưu
            st.session_state.clear()

            st.success("Đã làm sạch dữ liệu thành công!")
            time.sleep(1)
            
            # 4. Tự động Rerun (F5)
            st.rerun()

    st.caption(f"Phiên bản: 1.0.0 | Environment: {os.name}")

# --- MAIN DASHBOARD ---
st.title("📊 SMB Data Hub - Monitor Center")

# TAB SYSTEM
tab1, tab2, tab3 = st.tabs(["📈 Dashboard Tổng Quan", "🤖 Trợ Lý Dữ Liệu", "📜 Logs Chi Tiết"])

with tab1:
    st.header("Trạng thái sức khỏe hệ thống")
    try:
        logs = pd.read_sql("SELECT * FROM process_logs", engine)
        
        if not logs.empty:
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("File Đã Xử Lý", len(logs))
            
            valid_sum = logs['valid_rows'].sum() if 'valid_rows' in logs else 0
            total_sum = logs['total_rows'].sum() if 'total_rows' in logs else 1 # Tránh chia cho 0
            
            clean_rate = round((valid_sum / total_sum) * 100, 1)
            col2.metric("Tỷ lệ Sạch", f"{clean_rate}%")
            col3.metric("Tổng Dòng Lỗi", logs['error_rows'].sum())
            
            last_run = pd.to_datetime(logs['upload_time']).iloc[-1].strftime('%H:%M')
            col4.metric("Last Run", last_run)
            
            st.subheader("Biểu đồ chất lượng dữ liệu")
            if 'file_name' in logs.columns:
                chart_data = logs[['file_name', 'valid_rows', 'error_rows']].tail(10)
                st.bar_chart(chart_data.set_index('file_name'))
        else:
            st.info("Hệ thống chưa có dữ liệu. Vui lòng upload file ở menu bên trái.")
            
    except Exception as e:
        st.error(f"Không thể kết nối Database hoặc chưa có bảng log: {e}")

with tab2:
    st.header("Chat với dữ liệu (Demo)")
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Xin chào! Tôi là trợ lý Data Engineer. Bạn cần kiểm tra gì hôm nay?"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("VD: File vừa nạp có lỗi không?"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Đang truy vấn metadata..."):
                response = bot.process_query(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

with tab3:
    st.header("Audit Trail & Data Lineage")
    try:
        logs_df = pd.read_sql("SELECT * FROM process_logs ORDER BY upload_time DESC", engine)
        st.dataframe(logs_df, use_container_width=True)
    except:
        st.caption("Chưa có logs.")