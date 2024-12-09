import os
import subprocess
import whisper
from zhconv import convert
from typing import Optional


def extract_audio_from_video(video_path: str, temp_audio_filename: Optional[str] = None) -> str:

    try:
        # 构建 FFmpeg 命令
        command = [
            r"ffmpeg",
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
            shell=False,
            capture_output=True
        )


        # 检查是否执行成功
        if process.returncode == 0:
            print(f"音频提取成功！保存为: {temp_audio_filename}")
            return temp_audio_filename
        else:
            print(f"FFmpeg 执行失败！错误信息:\n{process.stderr}")

    except Exception as e:
        print(f"发生异常: {e}")


def process_audio(audio_path, srt_path, txt_path):
    """
       使用 Whisper 模型将音频文件转录为文本，保存为 SRT 和 TXT 文件。
       """
    try:
        # 加载 Whisper 模型
        model = whisper.load_model("large", download_root=os.path.join(".", ".cache", "whisper"))

        # 转录音频
        result = model.transcribe(audio_path,
                                  language="zh",
                                     temperature=0.2,
                                     fp16=False,
                                    word_timestamps=True,
                                  condition_on_previous_text=False)

        # 提取转录文本
        segments = result.get("segments", [])
        full_text = convert(result.get("text", ""),"zh-hans")

        # 保存为 TXT 文件（无时间戳）
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(full_text)

        # 保存为 SRT 文件（带时间戳）
        with open(srt_path, 'w', encoding='utf-8') as srt_file:
            for i, segment in enumerate(segments):
                start = format_timestamp(segment['start'])
                end = format_timestamp(segment['end'])
                text = convert(segment['text'].strip(),"zh-hans")

                srt_file.write(f"{i + 1}\n")
                srt_file.write(f"{start} --> {end}\n")
                srt_file.write(f"{text}\n\n")

        print(f"音频处理完成：{audio_path}, 已生成 {srt_path} 和 {txt_path}")
    except Exception as e:
        print(f"处理音频失败：{audio_path}, 错误: {e}")


def format_timestamp(seconds):
    """
    将秒数格式化为 SRT 时间戳格式 (hh:mm:ss,ms).
    """
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"


def convert_videos_to_srt(input_folder, output_audio_folder, output_srt_folder):
    if not os.path.exists(output_audio_folder):
        os.makedirs(output_audio_folder)
    if not os.path.exists(output_srt_folder):
        os.makedirs(output_srt_folder)

    for file_name in os.listdir(input_folder):
        file_path = os.path.join(input_folder, file_name)
        if not os.path.isfile(file_path):
            continue

        file_base, file_ext = os.path.splitext(file_name)
        srt_path = os.path.join(output_srt_folder, f"{file_base}.srt")
        txt_path = os.path.join(output_srt_folder, f"{file_base}.txt")

        # 跳过已处理文件
        if os.path.exists(srt_path):
            print(f"跳过已处理文件：{file_name}")
            continue

        # 如果是mp3或m4a文件，直接处理
        if file_ext.lower() in ['.mp3', '.m4a']:
            process_audio(file_path, srt_path, txt_path)
            print(f"处理完成：{file_name}")

        # 如果是mp4文件，先提取音频再处理
        elif file_ext.lower() == '.mp4':
            output_audio_path = os.path.join(output_audio_folder, f"{file_base}.mp3")
            extract_audio_from_video(file_path, output_audio_path)
            process_audio(output_audio_path, srt_path, txt_path)
            print(f"处理完成：{file_name}")
        else:
            print(f"跳过不支持的文件类型：{file_name}")

def check_dir_exist(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)

if __name__ == "__main__":
    # 示例调用
    input_folder = "input_videos"  # 输入视频文件夹路径
    output_audio_folder = "output_audios"  # 提取的音频文件保存路径
    output_srt_folder = "output_texts"  # 生成的srt和txt文件保存路径

    check_dir_exist(input_folder)
    check_dir_exist(output_audio_folder)
    check_dir_exist(output_srt_folder)

    convert_videos_to_srt(input_folder, output_audio_folder, output_srt_folder)