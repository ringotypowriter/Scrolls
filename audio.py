import os
import ssl
import subprocess
import time
from typing import Optional, Dict

import whisper
from zhconv import convert

import audio_segment as segement

ssl._create_default_https_context = ssl._create_unverified_context

TEMP_DIR = os.path.join(os.getcwd(), "temp","audio")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

print(f"Temporary files will be stored in: {TEMP_DIR}")


# Function to extract audio from the given video file and save it as a temporary WAV file
def extract_audio_from_video(video_path: str, temp_audio_filename: Optional[str] = None) -> str:
    # If no specific audio filename is provided, generate a temporary file path
    if not temp_audio_filename:
        temp_audio_filename = os.path.join("temp", "extracted_audio.mp3")

    # # Load the video file and extract the audio
    # video = mp.VideoFileClip(video_path)
    # audio = video.audio
    #
    # # Save audio as MP3 (using 128kbps bitrate to balance between quality and file size)
    # audio.write_audiofile(temp_audio_filename,
    #                       codec='libmp3lame',
    #                       fps=22050,
    #                       bitrate='128k',
    #                       buffersize=120000,
    #                       nbytes=4,
    #                       write_logfile=True,
    #                       ffmpeg_params=["-err_detect", "ignore_err",
    #                                      "-max_interleave_delta","0",
    #                                      "-timeout","10000"
    #                                      "-q:a",
    #                                      "-bufsize", "128k",
    #                                      "-fflags", "+discardcorrupt"])

    try:
        # 构建 FFmpeg 命令
        command = [
            "ffmpeg",
            "-i", video_path,   # 输入文件
            "-vn",              # 不处理视频流
            "-acodec", "libmp3lame",  # 使用 MP3 编码器
            "-b:a", "192k",    # 设置音频比特率
            temp_audio_filename,         # 输出文件
            "-y"
        ]

        # 调用 FFmpeg 并捕获输出
        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,  # 捕获标准输出
            stderr=subprocess.PIPE,  # 捕获错误输出
            text=True                # 将输出解码为文本
        )

        # 检查是否执行成功
        if process.returncode == 0:
            print(f"音频提取成功！保存为: {temp_audio_filename}")
        else:
            print(f"FFmpeg 执行失败！错误信息:\n{process.stderr}")

    except Exception as e:
        print(f"发生异常: {e}")


    return temp_audio_filename


# Function to transcribe the extracted audio using Whisper model
def transcribe_audio_with_whisper(audio_path: str, need_timestamp : bool = False, language: str = 'zh') -> Dict:
    """Transcribe audio into text using Whisper model."""

    srt_content = []
    global_segment_index = 1
    audio_files = segement.split_audio_smart_with_timestamps(audio_path,"./temp/segments_" + os.path.basename(audio_path).replace(".","_"))

    model = whisper.load_model("medium", download_root="./.cache/whisper")

    # Transcribe the audio file, supporting multi-language transcription
    # result = model.transcribe(audio_path, language=language, fp16=False, word_timestamps=need_timestamp)
    for audio_file in audio_files:
        # 提取文件名和时间范围
        file_name = os.path.basename(audio_file)
        if "@" in file_name:
            time_range = file_name.split("_")[-1].replace(".mp3", "")
            start_time, end_time = time_range.split("@")
            start_offset = int(start_time.split(":")[0]) * 3600 + int(start_time.split(":")[1]) * 60 + int(
                start_time.split(":")[2])
        else:
            start_time, end_time, start_offset = "Unknown", "Unknown", 0

        print(f"正在处理音频: {file_name} (时间: {start_time} 到 {end_time})")

        # 转录音频
        transcription = model.transcribe(audio_file,
                                     language="zh",
                                     temperature=0.3,
                                     fp16=False,
                                    word_timestamps=True)

        for segment in transcription["segments"]:
            start_time = format_timestamp(segment["start"] + start_offset)
            end_time = format_timestamp(segment["end"] + start_offset)
            text = segment["text"]

            # 添加到 SRT 内容列表
            srt_content.append({
                "index": global_segment_index,
                "start_time": start_time,
                "end_time": end_time,
                "text": text
            })
            global_segment_index += 1

    return srt_content

def format_timestamp(seconds):
    """
    将时间戳转换为 SRT 格式的时间戳（HH:MM:SS,msmsms）。
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{milliseconds:03}"

def save_segments_srt(transcription, srt_file):
    """
    保存转录结果为 SRT 文件。

    :param transcription: Whisper 转录结果
    :param srt_file: SRT 文件路径
    """
    with open(srt_file, "w", encoding="utf-8") as f:
        for entry in transcription:
            simple = entry['text']
            if simple.strip() == "":
                continue
            else:
                simple = convert(simple,"zh-hans")
                f.write(f"{entry['index']}\n")
                f.write(f"{entry['start_time']} --> {entry['end_time']}\n")
                f.write(f"{simple}\n\n")

# Function to generate SRT (SubRip Subtitle) file content from Whisper transcription
def generate_srt(segments: list) -> str:
    """Generate SRT subtitle content from transcription segments."""
    srt_content = ""
    for idx, segment in enumerate(segments, start=1):
        start_time = format_time(segment["start"])
        end_time = format_time(segment["end"])
        text = segment["text"]

        srt_content += f"{idx}\n"
        srt_content += f"{start_time} --> {end_time}\n"
        srt_content += f"{text}\n\n"
    return srt_content


# Function to format time in seconds into SRT subtitle format (HH:MM:SS,mmm)
def format_time(seconds: float) -> str:
    """Format time in seconds into SRT format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    milliseconds = int((seconds % 1) * 1000)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


# Function to save the transcription text to a .txt file
def save_transcription_to_txt(transcript: str, output_txt_path: str) -> None:
    """Save the transcription result to a text file."""
    with open(output_txt_path, 'w', encoding='utf-8') as f:
        f.write(transcript)
    print(f"Transcription saved to: {output_txt_path}")



# Example usage:
if __name__ == "__main__":
    # Example file paths
    video_path = 'example_video.mp4'  # Path to the video file
    output_txt_path = 'transcription_output.txt'  # Output path for transcription text file
    output_srt_path = 'temp/output.srt'  # Output path for SRT subtitle file

    start_time = time.time()

    audio_path = extract_audio_from_video(video_path)
    results = transcribe_audio_with_whisper(audio_path, need_timestamp=True)

    save_segments_srt(results, output_srt_path)

    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"音频内容分析处理耗时: {elapsed_time:.6f} 秒")

    # model = whisper.load_model("medium", download_root="./.cache/whisper")
    #
    # # 转录音频
    # transcription = model.transcribe("temp/segments_extracted_audio_mp3/segment_1_00:00:00@00:00:29.mp3",
    #                                  language="zh",
    #                                  temperature=0.3,
    #                                  fp16=False,
    #                                 word_timestamps=True)
    #
    # print(transcription['text'])

