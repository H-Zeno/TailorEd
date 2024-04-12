import openai
import subprocess
import os

recdir = "./data/recordings/"
txtdir = "./data/transcriptions/"

file_name = "intro.wav"
file_extension = ".wav"
# Compress to ogg file
COMPRESS_AUDIO = True


# Load the OpenAI API key from a file
with open("key.txt", "r") as file:
    key = file.read().strip()

openai.api_key = key


def convert_audio(input_file, output_file):
    """
    Convert an audio file to Opus format using FFmpeg.
    """
    # Define the FFmpeg command as a list of arguments
    command = [
        'ffmpeg',
        '-i', input_file,   # Input file
        '-vn',              # No video
        '-map_metadata', '-1',  # Strip metadata
        '-ac', '1',         # Set audio channels to 1 (mono)
        '-c:a', 'libopus',  # Codec for audio: Opus
        '-b:a', '12k',      # Bitrate for audio: 12 kbps
        '-application', 'voip',  # Optimize for VoIP
        output_file         # Output file
    ]
    
    try:
        subprocess.run(command, check=True)
        print(f"File converted successfully: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting the file: {e}")


def transcribe_audio(audio_file):
    
    response = openai.Audio.transcribe(
        model="whisper-1",
        file=open(audio_file, "rb")
    )
    return response['text']


if __name__ == "__main__":
    if COMPRESS_AUDIO:
        ogg_file = file_name.replace(file_extension, ".ogg")
        convert_audio(recdir + file_name, recdir + ogg_file)
        file_name = ogg_file
        file_extension = ".ogg"

    transcription = transcribe_audio(recdir + file_name)
    transcription_file = txtdir + file_name.replace(file_extension, ".txt")

    with open(transcription_file, "w") as file:
        file.write(transcription)
