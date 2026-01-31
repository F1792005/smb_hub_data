import os
import pandas as pd
from sqlalchemy import create_engine
from openai import AzureOpenAI
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

class Chatbot:
    def __init__(self, db_connection_string):
        self.engine = create_engine(db_connection_string)
        
        # Cấu hình Azure OpenAI Client
        try:
            self.client = AzureOpenAI(
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version=os.getenv("AZURE_OPENAI_API_VERSION")
            )
            self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
            self.is_ai_ready = True
        except Exception:
            self.is_ai_ready = False
            print("⚠️ Chưa cấu hình Azure OpenAI trong .env")

    def get_system_context(self):
        """
        Hàm này lấy dữ liệu từ DB để 'mớm' cho AI hiểu tình trạng hệ thống hiện tại.
        (Kỹ thuật RAG đơn giản)
        """
        context = ""
        try:
            # 1. Lấy thông tin logs gần nhất
            logs = pd.read_sql("SELECT * FROM process_logs ORDER BY upload_time DESC LIMIT 5", self.engine)
            
            # 2. Lấy tổng quan doanh thu (nếu có bảng customers_telco)
            try:
                rev_df = pd.read_sql("SELECT SUM(TotalCharges) as rev, COUNT(*) as cust FROM customers_telco", self.engine)
                revenue = rev_df['rev'].iloc[0]
                customers = rev_df['cust'].iloc[0]
                biz_context = f"- Tổng doanh thu hiện tại: ${revenue:,.2f}\n- Tổng số khách hàng: {customers}"
            except:
                biz_context = "- Chưa có dữ liệu kinh doanh."

            # 3. Tạo chuỗi context
            if not logs.empty:
                log_str = logs.to_string(index=False)
                context = (
                    f"Dưới đây là trạng thái hệ thống dữ liệu (SMB Data Hub):\n"
                    f"{biz_context}\n\n"
                    f"Các file vừa xử lý gần đây (Logs):\n{log_str}\n"
                )
            else:
                context = "Hệ thống chưa có dữ liệu log nào."
                
        except Exception as e:
            context = f"Không lấy được dữ liệu hệ thống. Lỗi: {str(e)}"
            
        return context

    def process_query(self, user_question):
        """
        Gửi context + câu hỏi lên Azure OpenAI để trả lời
        """
        if not self.is_ai_ready:
            return "⚠️ Hệ thống chưa kết nối được với Azure AI. Vui lòng kiểm tra file .env."

        # 1. Lấy dữ liệu nền
        system_data = self.get_system_context()

        # 2. Tạo Prompt (Kịch bản cho AI)
        system_prompt = f"""
        Bạn là Trợ lý Data Engineer chuyên nghiệp của hệ thống 'SMB Data Hub'.
        Nhiệm vụ của bạn là trả lời câu hỏi của quản lý dựa trên dữ liệu hệ thống được cung cấp dưới đây.
        
        QUY TẮC:
        - Chỉ trả lời dựa trên thông tin được cung cấp trong phần DỮ LIỆU HỆ THỐNG.
        - Nếu không có thông tin trong dữ liệu, hãy nói "Tôi chưa thấy thông tin này trong hệ thống".
        - Trả lời ngắn gọn, chuyên nghiệp, tập trung vào số liệu.
        - Có thể dùng Markdown để làm đậm số liệu quan trọng.

        --- DỮ LIỆU HỆ THỐNG ---
        {system_data}
        """

        try:
            # 3. Gọi API Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_question}
                ],
                temperature=0.3, # Giữ cho câu trả lời chính xác, ít sáng tạo lung tung
                max_tokens=300
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"❌ Lỗi khi gọi Azure AI: {str(e)}"