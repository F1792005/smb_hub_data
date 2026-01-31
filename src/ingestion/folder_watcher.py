import sys
import os

# Thêm đoạn này lên đầu file folder_watcher.py
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

import time
from watchdog.observers import Observer

import time
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from src.pipeline.main_flow import run_pipeline
from src.utils.logger import setup_logger

logger = setup_logger(name="FolderWatcher")

class Watcher:
    def __init__(self, directory_to_watch):
        self.DIRECTORY_TO_WATCH = directory_to_watch
        self.observer = Observer()

    def run(self):
        event_handler = Handler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=False)
        self.observer.start()
        logger.info(f"Đang giám sát thư mục: {self.DIRECTORY_TO_WATCH}")
        try:
            while True:
                time.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")

        self.observer.join()

class Handler(FileSystemEventHandler):
    @staticmethod
    def on_created(event):
        if event.is_directory:
            return None
        
        # Chỉ xử lý khi file đã copy xong (tránh lỗi file đang copy dở)
        # Trong thực tế có thể cần check kỹ hơn, ở đây ta delay nhẹ
        time.sleep(1) 
        
        logger.info(f"Phát hiện file mới: {event.src_path}")
        # Kích hoạt pipeline xử lý
        run_pipeline(event.src_path)

if __name__ == "__main__":
    # Đảm bảo đường dẫn đúng với config
    path = "data/uploads"
    if not os.path.exists(path):
        os.makedirs(path)
    
    w = Watcher(path)
    w.run()