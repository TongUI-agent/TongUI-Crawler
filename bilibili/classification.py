import re
import json
import os
import time
from openai import AzureOpenAI

MODEL = ""
API_KEY = ""
API_VERSION = ""
API_BASE = ""
REGION = ""
ENDPOINT = f"{API_BASE}/{REGION}"

client = AzureOpenAI(
    api_key=API_KEY,
    api_version=API_VERSION,
    azure_endpoint=ENDPOINT,
)

def read_vtt_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
    
    vtt_text = []
    for line in lines:
        if not re.match(r"\d{2}:\d{2}:\d{2}\.\d{3} --> \d{2}:\d{2}:\d{2}\.\d{3}", line):
            vtt_text.append(line.strip())

    return " ".join(vtt_text)

def construct_prompt(task, content):

    prompt = f"""You are a GUI agent. You are given a text corpus that describe a GUI task. You need to identify the task type.

    Possible task types:
    - Mobile: the task can be completed by a mobile phone app.
    - Desktop: the task can be completed by a desktop or computer app.
    - Other: the task cannot be completed by a mobile phone, desktop, or computer app.

    Answer the question in a single word such as [Mobile, Desktop, Other].
    Task: {task}
    Content: {content}"""

    return prompt

def find_vtt_for_video(video_path, vtt_dir):
    relative_path = os.path.relpath(video_path, video_dir)
    vtt_path = os.path.join(vtt_dir, os.path.splitext(relative_path)[0] + ".vtt")
    return vtt_path if os.path.exists(vtt_path) else None

def classify_with_llm(title, content):
    prompt = construct_prompt(title, content[:2000])

    for i in range(3):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                        ],
                    },
                ],
                frequency_penalty=1,
                max_tokens=128,
            )
            print("response:", response.choices[0].message.content)
            return response.choices[0].message.content
        
        except Exception as e:
            print(f"Error in API call (attempt {i+1}/3): {str(e)}")
            time.sleep(5)

    return "Other"

def classify_videos(video_dir, vtt_dir):
    classification_results = {}

    for root, _, files in os.walk(video_dir):
        for file in files:
            if file.endswith(".mp4"):
                video_path = os.path.join(root, file)
                title = os.path.splitext(file)[0]
                title = title.split("~~")[0]
                vtt_path = find_vtt_for_video(video_path, vtt_dir)

                if vtt_path:
                    vtt_content = read_vtt_file(vtt_path)
                else:
                    vtt_content = ""

                category = classify_with_llm(title, vtt_content)
                
                rel_path = os.path.relpath(video_path, video_dir)
                classification_results[rel_path] = category

    return classification_results

if __name__ == "__main__":
    app = "word"
    video_dir = f"videos/{app}"
    vtt_dir = f"audios_text/{app}"

    classification_results = classify_videos(video_dir, vtt_dir)

    output_json = f"cls/{app}_cls.json"
    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(classification_results, f, indent=4)
