# pywebview_app.py (PyWebView Desktop Application)
import subprocess
import sys
import time

import webview

__st_process = None

# 启动 Streamlit 应用
def start_streamlit_app():
    return subprocess.Popen(['streamlit', 'run', 'loading.py' ])  # 启动本地 Streamlit 应用

# 使用 PyWebView 打开 Sreamlit 页面
def run_webview():
    window = webview.create_window("Scrolls", "http://127.0.0.1:8501", confirm_close=True)  # 显示本地 Streamlit 页面

    window.events.closed += on_window_close

    webview.start()  # 启动 WebView


def on_window_close():
    global __st_process
    print("Window is closed!")
    stop_subprocess(__st_process)
    sys.exit(0)  # 程序退出

def stop_subprocess(process):
    if process.poll() is None:
        print("Terminating subprocess...")
        process.terminate()
        try:
            process.wait(timeout=15)  # 等待子进程终止
        except subprocess.TimeoutExpired:
            print("Subprocess did not terminate, forcing kill...")
            process.kill()  # 强制终止子进程
    print("Subprocess terminated.")
if __name__ == '__main__':
    process = start_streamlit_app()  # 启动 Streamlit 服务
    __st_process = process
    time.sleep(3)  # 等待 3 秒钟，让 Streamlit 启动
    run_webview()  # 启动 PyWebView 显示 Streamlit 应用