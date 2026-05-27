import webview
import threading
import subprocess
import time

def run_streamlit():
    subprocess.call(["streamlit", "run", "web_app.py", "--server.headless=true"])

threading.Thread(target=run_streamlit, daemon=True).start()
time.sleep(3)
webview.create_window("生活数据管理", "http://localhost:8501", width=375, height=812)
webview.start()