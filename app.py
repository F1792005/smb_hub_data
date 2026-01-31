import streamlit as st
import pandas as pd
import time
import plotly.express as px

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Data Monitor Center",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. CSS TỐI ƯU HIỂN THỊ (HIGH CONTRAST) ---
st.markdown("""
<style>
    /* Import Font Inter cho nét chữ dày dặn, dễ đọc */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #171717; /* Chữ màu đen than, không dùng màu xám nhạt */
    }

    /* === NỀN TỔNG THỂ: Xám xanh nhẹ (Chống chói) === */
    .stApp {
        background-color: #F0F2F6; 
    }

    /* === CÁC KHỐI NỘI DUNG (CARD) === */
    /* Tạo khung trắng cho các biểu đồ và metric để nổi bật */
    .css-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    /* === TIÊU ĐỀ (HEADER) === */
    h1, h2, h3 {
        color: #0F172A; /* Xanh đen đậm */
        font-weight: 700;
    }

    /* === NÚT BẤM (BUTTONS) === */
    div.stButton > button {
        background-color: #2563EB; /* Xanh Royal rõ ràng */
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 600;
        padding: 0.5rem 1rem;
        transition: 0.2s;
    }
    div.stButton > button:hover {
        background-color: #1D4ED8; /* Đậm hơn khi hover */
        color: white;
    }

    /* === METRICS (SỐ LIỆU) === */
    [data-testid="stMetricValue"] {
        color: #2563EB; /* Số liệu màu xanh chủ đạo */
        font-size: 32px;
        font-weight: 700;
    }
    [data-testid="stMetricLabel"] {
        color: #4B5563; /* Nhãn màu xám đậm, dễ đọc */
        font-weight: 500;
        font-size: 16px;
    }

    /* === KHUNG VIỀN STREAMLIT === */
    [data-testid="stExpander"] {
        background-color: white;
        border: 1px solid #E5E7EB;
        border-radius: 8px;
    }
    
    /* Ẩn header mặc định */
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- 3. KHỞI TẠO DỮ LIỆU ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Chào bạn! Tôi là trợ lý phân tích dữ liệu. Bạn cần xem thông tin gì?"}
    ]
if "data_processed" not in st.session_state:
    st.session_state.data_processed = False

# --- 4. BỐ CỤC CHÍNH (GRID 2 CỘT) ---
# Tỉ lệ 65% (Nội dung) - 35% (Chatbot) để Chatbot rộng rãi hơn chút cho dễ đọc
col_dash, col_chat = st.columns([0.65, 0.35], gap="large")

# ==============================================================================
# CỘT TRÁI: DASHBOARD & THỐNG KÊ
# ==============================================================================
with col_dash:
    st.title("📊 Monitor Center")
    st.markdown("**Trạng thái hệ thống thời gian thực**")
    st.write("") # Spacer

    # --- BLOCK 1: CONTROL PANEL (NỀN TRẮNG) ---
    with st.container():
        st.markdown('<div class="css-card">', unsafe_allow_html=True) # Hack để đánh dấu vùng
        with st.expander("📂 **Nhập & Xử lý dữ liệu (Data Ingestion)**", expanded=True):
            c1, c2 = st.columns([3, 1])
            with c1:
                uploaded_file = st.file_uploader("Tải lên file Excel/CSV", type=['csv', 'xlsx'])
            with c2:
                st.write("") # Căn chỉnh nút xuống dưới
                if st.button("🚀 Bắt đầu xử lý", use_container_width=True):
                    if uploaded_file:
                        with st.spinner("Đang phân tích dữ liệu..."):
                            time.sleep(1.2)
                            st.session_state.data_processed = True
                        st.success("Hoàn tất!")
                    else:
                        st.error("Chưa có file!")
                
                if st.button("🔄 Làm mới", use_container_width=True):
                    st.session_state.data_processed = False
                    st.session_state.messages = []
                    st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # --- BLOCK 2: METRICS (SỐ TO, RÕ) ---
    st.subheader("Tổng quan số liệu")
    
    # Logic dữ liệu
    val_u, val_d, val_l = ("18,500", "120 GB", "98%") if st.session_state.data_processed else ("---", "---", "---")
    
    # Dùng container border của Streamlit để tạo khung
    m1, m2, m3 = st.columns(3)
    with m1:
        with st.container(border=True):
            st.metric("Người dùng active", val_u, "12% tăng")
    with m2:
        with st.container(border=True):
            st.metric("Dữ liệu đã nạp", val_d, "5 GB mới")
    with m3:
        with st.container(border=True):
            st.metric("Độ ổn định (SLA)", val_l, "Ổn định")

    # --- BLOCK 3: CHART (RÕ RÀNG) ---
    st.write("")
    st.subheader("Biểu đồ xu hướng")
    
    with st.container(border=True):
        if st.session_state.data_processed:
            df = pd.DataFrame({
                'Giờ': ['8h', '9h', '10h', '11h', '12h', '13h', '14h'],
                'Truy cập': [120, 300, 450, 400, 600, 550, 700]
            })
            
            # Màu xanh đậm cho biểu đồ dễ nhìn trên nền trắng
            fig = px.bar(df, x='Giờ', y='Truy cập', title="Lưu lượng theo giờ")
            fig.update_traces(marker_color='#2563EB') 
            fig.update_layout(
                plot_bgcolor='white',
                font=dict(color='#171717', size=14) # Chữ trong biểu đồ to rõ
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Vui lòng nạp dữ liệu để hiển thị biểu đồ.")
            st.markdown("<div style='height: 250px; background: #F3F4F6; border-radius: 8px;'></div>", unsafe_allow_html=True)

# ==============================================================================
# CỘT PHẢI: AI ASSISTANT (TƯƠNG PHẢN TỐT)
# ==============================================================================
with col_chat:
    # Header Chatbot: Màu tối để tách biệt hẳn
    st.markdown("""
    <div style="background-color: #1E293B; padding: 15px; border-radius: 10px 10px 0 0; color: white; display: flex; align-items: center; justify-content: space-between;">
        <div style="font-weight: bold; font-size: 16px;">🤖 AI Data Assistant</div>
        <div style="font-size: 12px; background: #10B981; padding: 2px 8px; border-radius: 10px;">Online</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Container Chat: Nền trắng, viền xám
    chat_box = st.container(height=650, border=True)

    with chat_box:
        for msg in st.session_state.messages:
            # Phân biệt màu sắc tin nhắn RÕ RÀNG
            if msg["role"] == "user":
                # Tin nhắn người dùng: Nền xanh, chữ trắng
                with st.chat_message("user", avatar="👤"):
                    st.markdown(f"<div style='background: #EBF5FF; color: #1e3a8a; padding: 10px; border-radius: 8px; border: 1px solid #bfdbfe;'><b>Bạn:</b> {msg['content']}</div>", unsafe_allow_html=True)
            else:
                # Tin nhắn Bot: Nền xám nhạt, chữ đen
                with st.chat_message("assistant", avatar="🤖"):
                    st.markdown(f"<div style='color: #111;'>{msg['content']}</div>", unsafe_allow_html=True)

    # Input Area
    st.write("---") # Đường kẻ phân cách
    if prompt := st.chat_input("Nhập câu hỏi tại đây...", key="chat_input_final"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Reload lại khung chat để hiện tin nhắn mới ngay lập tức
        st.rerun()

    # Xử lý response sau khi rerun (để tránh lặp lại logic hiển thị)
    if st.session_state.messages[-1]["role"] == "user":
        time.sleep(0.5)
        if st.session_state.data_processed:
            reply = f"Hệ thống ghi nhận câu hỏi: '{prompt}'. Dữ liệu hiện tại cho thấy xu hướng đang tăng trưởng."
        else:
            reply = "Tôi chưa có dữ liệu để phân tích. Hãy upload file trước nhé."
        
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()