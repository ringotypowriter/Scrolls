import os
import time
from typing import Optional, Dict
import ssl
import moviepy as mp
import whisper

ssl._create_default_https_context = ssl._create_unverified_context

TEMP_DIR = os.path.join(os.getcwd(), "temp")

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

print(f"Temporary files will be stored in: {TEMP_DIR}")


# Function to extract audio from the given video file and save it as a temporary WAV file
def extract_audio_from_video(video_path: str, temp_audio_filename: Optional[str] = None) -> str:
    """Extract audio from the video and save it as a temporary WAV file."""
    # If no specific audio filename is provided, generate a temporary file path
    if not temp_audio_filename:
        temp_audio_filename = os.path.join(TEMP_DIR, "extracted_audio.mp3")

    # Load the video file and extract the audio
    video = mp.VideoFileClip(video_path)
    audio = video.audio

    # Save audio as MP3 (using 128kbps bitrate to balance between quality and file size)
    audio.write_audiofile(temp_audio_filename, codec='libmp3lame', bitrate='128k')
    print(f"Audio extracted and saved to: {temp_audio_filename}")

    return temp_audio_filename


# Function to transcribe the extracted audio using Whisper model
def transcribe_audio_with_whisper(audio_path: str, need_timestamp : bool = False, language: str = 'zh') -> Dict:
    """Transcribe audio into text using Whisper model."""
    # Load the Whisper model (medium-sized version)
    model = whisper.load_model("turbo", download_root="./.cache/whisper")

    # Transcribe the audio file, supporting multi-language transcription
    result = model.transcribe(audio_path, language=language, fp16=False, word_timestamps=need_timestamp)

    return result


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


# Main function to process a video, extract audio, transcribe it, and optionally save text and SRT subtitles
def process_video_to_text_and_srt(video_path: str,
                                  output_txt_path: Optional[str] = None,
                                  output_srt_path: Optional[str] = None,
                                  save_txt: bool = True,
                                  save_srt: bool = True) -> Dict:
    """
    Extract audio from the given video file, transcribe it using Whisper,
    and save transcription text and/or SRT subtitles depending on the parameters.
    """
    start_time = time.time()

    # Extract audio from video
    audio_path = extract_audio_from_video(video_path)

    # Transcribe audio using Whisper
    transcription_result = transcribe_audio_with_whisper(audio_path, True)
    transcript_text = transcription_result['text']
    segments = transcription_result['segments']

    # Optionally save transcription text to a .txt file
    if save_txt and output_txt_path:
        save_transcription_to_txt(transcript_text, output_txt_path)

    # Optionally save SRT subtitle file
    if save_srt and output_srt_path:
        srt_content = generate_srt(segments)
        with open(output_srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        print(f"SRT subtitle file saved to: {output_srt_path}")

    # Calculate elapsed time for processing
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Processing time: {elapsed_time:.6f} seconds")

    # Return results as a dictionary
    return {
        'transcript': transcript_text,
        'segments': segments,
        'elapsed_time': elapsed_time
    }


# Example usage:
if __name__ == "__main__":
    # Example file paths
    video_path = 'example_video.mp4'  # Path to the video file
    output_txt_path = 'transcription_output.txt'  # Output path for transcription text file
    output_srt_path = 'output.srt'  # Output path for SRT subtitle file

    # Call the process_video_to_text_and_srt function to process the video
    result = process_video_to_text_and_srt(
        video_path,
        output_txt_path=output_txt_path,
        output_srt_path=output_srt_path,
        save_txt=True,
        save_srt=True
    )

    # Print the transcription result
    print("Transcription text:", result['transcript'])
