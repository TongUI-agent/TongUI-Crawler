import re
import json
import os
import time

from PIL import Image

from transformers import Qwen2_5_VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info

model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
    "models/Qwen2.5-VL-7B-Instruct", torch_dtype="auto", device_map="auto"
)

processor = AutoProcessor.from_pretrained("models/Qwen2.5-VL-7B-Instruct")

def construct_prompt(task, content):

    prompt = f"""You are a GUI agent. You are given a task related to a graphical user interface (GUI), a current screen screenshot, and a proposed thought and action for the current step.

    Your job is to evaluate how reasonable the provided thought and action are **in helping to complete the given task given the current screen state**.

    Scoring guide:
    - 5: Very helpful — clearly contributes toward task success.
    - 4: Helpful — likely a good next step.
    - 3: Possibly helpful — may work depending on other context.
    - 2: Slightly helpful — some connection, but unlikely to help.
    - 1: Not helpful — almost irrelevant.
    - 0: Completely unrelated.

    Higher scores mean more helpful. Please respond with only a number between 0 and 5.

    Task: {task}
    Thought and Action: {content}
    Screenshots:"""

    return prompt

def verify_with_llm(task, content, image_path):
    prompt = construct_prompt(task, content)

    try:
        image = Image.open(image_path).convert("RGB")
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return -1

    messages=[{
            "role": "user",
            "content": [{"type": "text", "text": prompt},
                        {"type": "image", "image": image}]
    }]

    for i in range(3):
        try:
            text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
            image_inputs, video_inputs = process_vision_info(messages)

            inputs = processor(
                text=[text],
                images=image_inputs,
                videos=video_inputs,
                padding=True,
                return_tensors="pt",
            ).to("cuda")

            generated_ids = model.generate(**inputs, max_new_tokens=10)
            generated_ids_trimmed = [
                out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)
            ]

            output_text = processor.batch_decode(
                generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False
            )

            print("Qwen Response:", output_text[0])
            return output_text[0]
        
        except Exception as e:
            print(f"Error in API call (attempt {i+1}/3): {str(e)}")
            time.sleep(5)

    return -1

def score_single_json(json_path, score_json_root):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    score_json_path = json_path.replace("final_results", "score_results")

    score_results = {}

    for i, item in enumerate(data):
        images = item.get("images", [])
        if not images:
            continue

        image_path = images[-1]
        if image_path in score_results:
            continue

        messages = item.get("messages", [])

        match = re.search(r'Task:\s*(.*?)\s*<image>', messages[0].get("content"))
        if match:
            task = match.group(1).strip()
        else:
            print("No task found.")
            continue

        content = messages[-1].get("content")

        score = verify_with_llm(task, content, image_path)
        score_results[image_path] = score

        if (i + 1) % 10 == 0:
            with open(score_json_path, "w", encoding="utf-8") as f:
                json.dump(score_results, f, indent=4)

    with open(score_json_path, "w", encoding="utf-8") as f:
        json.dump(score_results, f, indent=4)

def score_all_json(result_json_root, score_json_root):
    for root, _, files in os.walk(result_json_root):
        for file in files:
            if file.endswith(".json"):
                json_path = os.path.join(root, file)
                score_single_json(json_path, score_json_root)

if __name__ == "__main__":
    app = "word"
    result_json_root = f"results/{app}"
    score_json_root = f"filter_results/{app}"

    score_all_json(result_json_root, score_json_root)
