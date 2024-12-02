from pydub import AudioSegment
from pydub.silence import detect_silence
import os

def ms_to_timestamp(milliseconds):
    """
    将毫秒转换为可读的时间戳格式（HH:MM:SS）。
    """
    seconds = milliseconds // 1000
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02}:{minutes:02}:{seconds:02}"

def split_audio_smart_with_timestamps(input_file, output_dir, min_silence_len=1000, silence_thresh=-40, segment_duration_ms=30000):
    """
    智能分割会议音频，优先在静音处分割，并在文件名中包含时间戳。

    :param input_file: 输入音频文件路径
    :param output_dir: 输出的片段存放目录
    :param min_silence_len: 静音的最小时长（毫秒），默认为 1000 毫秒
    :param silence_thresh: 静音的阈值（dBFS），默认为 -40 dB
    :param segment_duration_ms: 每段音频的目标最大时长（毫秒）
    """
    # 加载音频
    audio = AudioSegment.from_file(input_file)
    audio_length = len(audio)

    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 检测静音部分（开始和结束时间的列表）
    silences = detect_silence(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    silences = [((start + end) // 2) for start, end in silences]  # 静音点取中间值

    # 添加人工切割点以确保不会超时
    cut_points = [0]  # 开始点
    for i in range(segment_duration_ms, audio_length, segment_duration_ms):
        # 寻找离目标点最近的静音位置
        closest_silence = min(silences, key=lambda x: abs(x - i), default=None)
        if closest_silence and abs(closest_silence - i) < segment_duration_ms // 2:
            cut_points.append(closest_silence)
        else:
            cut_points.append(i)
    cut_points.append(audio_length)  # 结束点

    # 分割音频并导出
    for i in range(len(cut_points) - 1):
        start = cut_points[i]
        end = cut_points[i + 1]
        segment = audio[start:end]
        start_time = ms_to_timestamp(start)
        end_time = ms_to_timestamp(end)
        output_file = os.path.join(output_dir, f"segment_{i + 1}_{start_time}_to_{end_time}.mp3")
        segment.export(output_file, format="mp3")
        print(f"已导出: {output_file} (时长: {len(segment) / 1000} 秒)")

# 示例调用
input_audio = "temp/temp_audio_example_video_mp4_exported.mp3"  # 替换为你的音频文件路径
output_directory = "output_segments_with_timestamps"  # 替换为你的输出目录
split_audio_smart_with_timestamps(input_audio, output_directory)