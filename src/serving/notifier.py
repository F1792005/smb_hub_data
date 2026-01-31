import smtplib
from email.mime.text import MIMEText
from src.utils.logger import setup_logger

logger = setup_logger(name="Notifier")

class Notifier:
    def __init__(self, email_user="demo@gmail.com", email_pass="password"):
        self.user = email_user
        self.password = email_pass

    def send_email(self, to_email, subject, message):
        """Gửi email thông báo (SMTP Gmail)"""
        try:
            msg = MIMEText(message)
            msg['Subject'] = f"[SMB Data Hub] {subject}"
            msg['From'] = self.user
            msg['To'] = to_email

            # Demo: Chỉ in ra log thay vì gửi thật để tránh lỗi credential
            logger.info(f"📧 [MOCK EMAIL] To: {to_email} | Subject: {subject} | Body: {message}")
            
            # Code thực tế (Cần App Password của Gmail):
            # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            #    server.login(self.user, self.password)
            #    server.send_message(msg)
            
            return True
        except Exception as e:
            logger.error(f"Gửi email thất bại: {str(e)}")
            return False

    def sync_to_google_sheet(self, dataframe, sheet_name):
        """
        Giả lập đồng bộ dữ liệu sạch lên Google Sheets.
        Để chạy thật cần Google Service Account JSON Key.
        """
        rows = len(dataframe)
        logger.info(f"📊 [GOOGLE SHEET] Đang đồng bộ {rows} dòng vào Sheet: '{sheet_name}'...")
        # Sử dụng thư viện gspread hoặc df.to_csv để đẩy lên API
        logger.info("✅ Đồng bộ Google Sheet thành công!")