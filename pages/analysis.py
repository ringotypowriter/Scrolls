import streamlit as st
import os

from bottle import response

import summarize
from typing import Optional

TEMP_DIR = os.path.join(os.getcwd(), "output")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def analysisContent(file_path, output_md_path, srt_path: Optional[str] = None) :
    text = summarize.read_file(file_path)
    st.write(f"成功读取分析文本{file_path}")
    st.write(f"语言模型进行解析中...")
    result = summarize.refine_structure(text).content
    st.write(f"保存Markdown内容至: {output_md_path}")
    summarize.write_file(output_md_path, result)
    st.write(f"正在生成预览...")
    return result

def main() :
    st.title("内容分析")

    if 'to_analysis' not in st.session_state :
        pass # TODO
    else :
        file_path = st.session_state['to_analysis']
        output_md_path = file_path.replace('.','_') + "_summary.md"
        resultText = None
        with st.status("分析文本中..."):
            resultText = analysisContent(file_path, output_md_path)

        if resultText:
            with st.container(border=True, height=400):
                st.markdown(resultText)

            col1,col2 = st.columns(2)
            with col1:
                if st.button("下载Markdown格式"):
                    pass # TODO
            with col2:
                if st.button("下载PDF格式"):
                    pass # TODO

main()