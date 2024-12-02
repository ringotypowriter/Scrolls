import streamlit as st
from streamlit import button

import audio
import os
import time


TEMP_DIR = os.path.join(os.getcwd(), "output")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

def main():

    st.title("上传课程有关文件")


    if 'to_analysis' in st.session_state : st.switch_page("pages/analysis.py")



    if 'fileStartHandling' not in st.session_state : st.session_state['fileStartHandling'] = False
    if 'runningForResult' not in st.session_state: st.session_state['runningForResult'] = False

    need_srt = st.toggle("是否需要SRT文件？（包含时间轴）", value=False, help="将会占用更多的时间，但后续对其文本分析也会提供时间轴信息", disabled=st.session_state['fileStartHandling'])

    # Display file uploader widget
    uploaded_file = st.file_uploader("上传您所需要处理的视频或音频文件", type=["mp4","mp3","wav"])

    if uploaded_file is not None :
        st.session_state['fileStartHandling'] = True
        if st.session_state['runningForResult'] is False :
            # Start run the program
            st.session_state['needSRT'] = need_srt
            st.session_state['runningForResult'] = True
            st.rerun()
        with st.status("正在处理文件...", expanded=True):
            need_srt = st.session_state['needSRT']
            st.write(f"文件名: {uploaded_file.name}")
            st.write(f"文件类型: {uploaded_file.type}")

            current_directory = os.getcwd()

            file_path = os.path.join(current_directory,"temp", uploaded_file.name)
            result_path = os.path.join("output",uploaded_file.name + "_output.txt")
            result_segments_path = os.path.join("output",uploaded_file.name + "_output.srt")

            # Save the file
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            st.write("已保存至工作文件夹")

            audio_file_name = file_path

            if uploaded_file.type.startswith("video") :
                audio_file_name = audio.extract_audio_from_video(file_path, os.path.join("temp",f"temp_audio_{uploaded_file.name.replace('.', '_')}_exported.mp3"))
                st.write("检测为视频，已提取音频")

            st.write(f"正在处理音频 {audio_file_name}")

            start_time = time.time()
            transcription_result = audio.transcribe_audio_with_whisper(audio_file_name, need_srt)
            transcript_text = transcription_result['text']


            audio.save_transcription_to_txt(transcript_text, result_path)
            st.write(f"分析文本TXT文件保存至: {result_path}")

            if need_srt:
                segments = transcription_result['segments']
                srt_content = audio.generate_srt(segments)
                with open(result_segments_path, 'w', encoding='utf-8') as f:
                    f.write(srt_content)
                st.write(f"时间轴SRT文件保存至: {result_segments_path}")

            end_time = time.time()
            elapsed_time = end_time - start_time
            st.write(f"音频内容分析处理耗时: {elapsed_time:.6f} 秒")
            st.session_state['to_analysis'] = result_path
        if st.button("继续") :
            st.switch_page("pages/analysis.py")

main()