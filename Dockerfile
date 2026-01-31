# Sử dụng Python 3.9 gọn nhẹ
FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các dependencies hệ thống (ví dụ cho OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements và cài đặt thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào image
COPY . .

# Tạo các thư mục dữ liệu cần thiết
RUN mkdir -p data/uploads data/raw data/clean data/error logs

# Thiết lập biến môi trường
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Mặc định chạy Dashboard khi start container
CMD ["streamlit", "run", "src/serving/dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]