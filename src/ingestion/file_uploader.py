import os

def save_uploaded_file(uploaded_file, target_folder):
    try:
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        
        file_path = os.path.join(target_folder, uploaded_file.name)
        
        # Ghi dữ liệu từ RAM xuống Ổ cứng
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        return True, file_path
    except Exception as e:
        return False, str(e)