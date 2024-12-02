import ollama
import streamlit as st

import ollama_management as om
import prompt_engineering
import atexit


def check_ollama_status():
    response = ollama.chat(
        model=MODEL_NAME,
        options=
            {"temperature": 0.25},
        messages=[
            prompt_engineering.SYSTEM_PROMPT,
            {
                "role": "user",
                "content": "这是一条调试测试消息，为确认你的正确运行，你在接受到这条消息后，暂时忽略你的格式要求，请你提供一段专业但简洁的自我介绍，包括你的名字，你的工作，你的创造者（只需要完整的写出「RingoTypowriter」（只有一人，避免使用【它】，【他】，【她】，【他们】有关代词），不需要其他有关介绍），并且表示出友好。你的自我介绍应该从问好开始，不需要有任何对这个消息的直接的回复"
            }
        ]
    )

    st.info(f"端侧大模型欢迎消息: {response['message'].content}")


MODEL_NAME="llama3.1:8b"


def handle_exit_event():
    if 'exit_event_triggered' not in st.session_state:
        st.session_state.exit_event_triggered = False

    # Mark exit event as triggered
    st.session_state.exit_event_triggered = True
    om.auto_destroy_process()


def main():
    st.set_page_config(
        page_title="Scrolls App",
        page_icon=":closed_book:",
        layout="centered",
        initial_sidebar_state="collapsed",
        menu_items={
            'Get Help': None,
            'Report a bug': None,
            'About': None
        }
    )

    # 注册退出时执行的清理操作
    atexit.register(handle_exit_event)

    st.title("Scrolls")

    if 'loadedFinished' not in st.session_state : st.session_state['loadedFinished'] = False

    if st.session_state['loadedFinished'] is True : st.switch_page("pages/file_handler.py")

    if 'exit_event_triggered' in st.session_state and st.session_state.exit_event_triggered:
        handle_exit_event()

    # Loading Ollama
    st.write("正在加载端侧大模型中...")
    st.write("基于当前的网络状况这或许需要一些时间")
    st.write("模型文件大小 ~ 5G | 模型参数尺寸 ~ 8B")

    successLoaded = False

    with st.status("加载端侧模型子进程中...") :
        result = om.get_process()
        if result:
            st.success("完成模型加载，即将进入下一步")
            check_ollama_status()
            successLoaded = True
            st.session_state['loadedFinished'] = True
        else:
            st.error("模型加载失败")
    if successLoaded:
        if st.button("继续"):
            st.switch_page("pages/file_handler.py")

main()