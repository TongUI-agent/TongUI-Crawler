from openai import AzureOpenAI
import base64
from transformers.agents import ReactCodeAgent
import json

REGION = "eastus"
MODEL = "gpt-4o-mini-2024-07-18"
API_KEY = "c07c4489f222bc394807d68fb3da9cb1"

API_BASE = "https://api.tonggpt.mybigai.ac.cn/proxy"
ENDPOINT = f"{API_BASE}/{REGION}"


client = AzureOpenAI(
    api_key=API_KEY,
    api_version="2024-02-01",
    azure_endpoint=ENDPOINT,
)

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path, prompt):
    """
    使用OpenAI的Vision模型分析图片
    Args:
        image_path: 图片路径
        prompt: 提示词
    Returns:
        模型的回复内容
    """
    base64_image = encode_image(image_path)
    
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{base64_image}"
                        }
                    }
                ]
            }
        ]
    )
    
    return response.choices[0].message.content

import os
import pandas as pd
from tqdm import tqdm

file_path = "data/steps_subset/00a07f38a87953c3d028dca9"

if __name__ == "__main__":
    with open("action_agent/prompts/parse_action.txt", "r") as f:
        prompt = f.read()
    
    with open(os.path.join(file_path, "steps_with_images.json"), "r") as f:
        data = json.load(f)
    
    for step in data["steps"]:
        response = client.chat.completions.create(
                model=MODEL,
                messages=[
                {"role": "system", "content": prompt},
                {
                    "role": "user", 
                    "content": f"""Task: {step["text"]}\nActions:"""
                }
            ]
        )
        print("Task: ", step["text"])
        print("Actions: ", response.choices[0].message.content)
        break