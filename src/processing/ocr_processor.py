import pytesseract
from PIL import Image
import os

class OCRProcessor:
    def __init__(self, tesseract_cmd=None):
        # Nếu dùng Windows, cần chỉ định đường dẫn tesseract.exe
        # if tesseract_cmd:
        #     pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
        pass

    def extract_text_from_image(self, image_path):
        """Trích xuất toàn bộ text từ ảnh hóa đơn"""
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang='vie+eng') # Hỗ trợ tiếng Việt/Anh
            return text
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    def extract_key_value(self, text):
        """
        Hàm demo đơn giản để tìm thông tin quan trọng từ text thô.
        Ví dụ tìm 'Tổng tiền'
        """
        lines = text.split('\n')
        data = {}
        for line in lines:
            line = line.lower()
            if "total" in line or "tổng cộng" in line:
                # Logic bóc tách số đơn giản (demo)
                data['total_amount'] = line
            if "tax" in line or "thuế" in line:
                data['tax_code'] = line
        return data

# Test nhanh nếu chạy trực tiếp file này
if __name__ == "__main__":
    # Giả sử có file test.png
    processor = OCRProcessor()
    # text = processor.extract_text_from_image("data/uploads/test_invoice.png")
    # print(text)
    print("Module OCR đã sẵn sàng. Cần cài đặt Tesseract Engine để chạy.")