import base64
from openai import OpenAI
import random
from PIL import Image
import re
import os
from pathlib import Path
import pysrt
from io import BytesIO
import json
import math

from transformers import AutoProcessor, AutoModelForImageTextToText

processor = AutoProcessor.from_pretrained("ByteDance-Seed/UI-TARS-1.5-7B")
model = AutoModelForImageTextToText.from_pretrained("ByteDance-Seed/UI-TARS-1.5-7B")

def get_task_and_thought(vtt_path, segment_index):
    task = Path(vtt_path).stem
    task = task.split("~~")[0]
    subs = pysrt.open(vtt_path, encoding='utf-8')
    subtitles = [sub.text for sub in subs]
    try:
        thought = task + "." + subtitles[segment_index-1][:1000]
    except:
        thought = task
    return task, thought

def extract_video_info(video_path):
    parts = Path(video_path).parts
    operation = parts[-3]
    video_name = parts[-1]
    video_base = parts[-2]
    segment_match = re.search(r"segment_(\d+)_", video_name)
    segment_index = int(segment_match.group(1)) if segment_match else None
    return operation, video_base, segment_index

def resize_image_if_needed(image, max_pixels=3000 * 28 * 28):
    if image.width * image.height > max_pixels:
        resize_factor = math.sqrt(max_pixels / (image.width * image.height))
        new_width = int(image.width * resize_factor)
        new_height = int(image.height * resize_factor)
        image = image.resize((new_width, new_height), Image.ANTIALIAS)
    return image

def construct_prompt_desktop(thought):
    return f"""You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

## Output Format
Thought: ...
Action: ...

## Action Space

click(start_box='<|box_start|>(x1,y1)<|box_end|>')
left_double(start_box='<|box_start|>(x1,y1)<|box_end|>')
right_single(start_box='<|box_start|>(x1,y1)<|box_end|>')
drag(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
hotkey(key='')
type(content='') #If you want to submit your input, use \"\\n\" at the end of `content`.
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', direction='down or up or right or left')
wait()
finished()
call_user()

## Note
- Use Chinese in `Thought` part.
- Summarize your next action (with its target element) in one sentence in `Thought` part.

## User Instruction
{thought}
"""

def construct_prompt_mobile(thought):
    return f"""You are a GUI agent. You are given a task and your action history, with screenshots. You need to perform the next action to complete the task. 

## Output Format
Thought: ...
Action: ...

## Action Space
click(start_box='<|box_start|>(x1,y1)<|box_end|>')
long_press(start_box='<|box_start|>(x1,y1)<|box_end|>', time='')
type(content='')
scroll(start_box='<|box_start|>(x1,y1)<|box_end|>', end_box='<|box_start|>(x3,y3)<|box_end|>')
press_home()
press_back()
finished(content='')

## Note
- Use English in `Thought` part.
- Write a small plan and finally summarize your next action (with its target element) in `Thought` part.

## User Instruction
{thought}
"""

def process_images(img_root, subtitle_root, action_root, prompt_mapping):
    for root, _, files in os.walk(img_root):
        for file in files:
            if not file.startswith("segment_") or not file.endswith(".png"):
                continue

            img_path = os.path.join(root, file)
            operation, video_base, segment_index = extract_video_info(img_path)

            action_path = os.path.join(action_root, operation, video_base)
            os.makedirs(action_path, exist_ok=True)
            action_file_path = os.path.join(action_path, f"{Path(file).stem}.txt")
            thought_file_path = os.path.join(action_path, f"{Path(file).stem}_thought.txt")

            if os.path.exists(action_file_path):
                continue

            vtt_path = os.path.join(subtitle_root, operation, f"{video_base}.srt")
            if not os.path.exists(vtt_path):
                continue

            task, thought = get_task_and_thought(vtt_path, segment_index)

            key = vtt_path.replace(".srt", ".mp4")

            device_type = prompt_mapping.get(key, "")
            if "Desktop" in device_type:
                prompt = construct_prompt_desktop(thought)
            elif "Mobile" in device_type:
                prompt = construct_prompt_mobile(thought)
            else:
                continue

            try:
                image = Image.open(img_path).convert("RGB")
                image = resize_image_if_needed(image)
            except:
                continue

            inputs = processor(prompt, images=image, return_tensors="pt").to(model.device)

            success = False
            for _ in range(3):
                try:
                    output_ids = model.generate(**inputs, max_new_tokens=128)
                    content = processor.batch_decode(output_ids, skip_special_tokens=True)[0]
                except Exception:
                    continue
                else:
                    success = True
                    break

            if not success:
                continue

            action_match = re.search(r"Action: (.*)", content)
            if action_match:
                action = action_match.group(1)
                with open(action_file_path, "w") as f:
                    f.write(action)

            thought_match = re.search(r"(.*?)Action:", content, re.DOTALL)
            with open(thought_file_path, "w") as f:
                f.write(thought_match.group(1).strip() if thought_match else content)


if __name__ == "__main__":
    app = "word"
    img_root = f"images/{app}"
    subtitle_root = f"audios_text0/{app}"
    action_root = f"actions/{app}"

    json_path = f"cls/{app}_cls.json"
    with open(json_path, "r", encoding="utf-8") as json_file:
        prompt_mapping = json.load(json_file)

    process_images(img_root, subtitle_root, action_root, prompt_mapping)
