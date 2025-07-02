import os
import whisper

def transcribe_with_whisper(audio_path, model):
    result = model.transcribe(audio_path, word_timestamps=True)
    return result

def format_time(seconds):
    milliseconds = int((seconds - int(seconds)) * 1000)
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    return f"{hours:02}:{minutes:02}:{seconds:02}.{milliseconds:03}"

def format_transcription(result):
    output = ["WEBVTT\n"]

    for segment in result["segments"]:
        start_time = format_time(segment["start"])
        end_time = format_time(segment["end"])
        text = segment["text"].strip()
        output.append(f"{start_time} --> {end_time}\n{text}")
    return "\n\n".join(output)

def process_audio_files(audio_base_path, output_base_path, model):
    for root, dirs, files in os.walk(audio_base_path):
        for file in files:
            if file.endswith(".mp4"):
                audio_file_path = os.path.join(root, file)
                
                relative_path = os.path.relpath(root, audio_base_path)
                output_folder = os.path.join(output_base_path, relative_path)
                os.makedirs(output_folder, exist_ok=True)

                output_file_path = os.path.join(output_folder, file.replace(".mp4", ".vtt"))

                if os.path.exists(output_file_path):
                    print(f"Skip {output_file_path}")
                    continue

                print(f"Process {audio_file_path}")
                try:
                    transcription_result = transcribe_with_whisper(audio_file_path, model)
                except:
                    continue

                formatted_output = format_transcription(transcription_result)

                with open(output_file_path, "w", encoding="utf-8") as output_file:
                    output_file.write(formatted_output)

                print(f"Save {output_file_path}")

if __name__ == "__main__":
    model = whisper.load_model("base")

    app = "word"
    audio_base_path = f"videos/{app}"
    output_base_path = f"audios_text/{app}"

    process_audio_files(audio_base_path, output_base_path, model)
