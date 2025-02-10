from openai import AzureOpenAI
import base64

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
if __name__ == "__main__":
    if os.path.exists("data/image_classification_result.csv"):
        df = pd.read_csv("data/image_classification_result.csv")
    else:
        df = pd.DataFrame(columns=["image_id", "is_gui"])
        
    images = os.listdir("data/images")
    images = [os.path.join("data/images", image) for image in images]
    # peek
    images = images[:70]
    for image in tqdm(images):
        image_id = image.split("/")[-1].split(".")[0]
        if image_id in df["image_id"].values:
            continue
        prompt = "Please classify the image as GUI screenshot or not. Answer a single word by yes or no."
        try:
            if image in df["image_id"].values:
                print('already computed')
                continue
            result = analyze_image(image, prompt)
            print(result)
            # append the result to df
            # check if image_id is in df
            df = pd.concat([df, pd.DataFrame([{"image_id": image, "is_gui": result.lower()}])], ignore_index=True)
            
        except Exception as e:
            print(f"Error analyzing image: {e}")
    df.drop_duplicates(subset="image_id", keep="first", inplace=True)
    df.to_csv("data/image_classification_result.csv", index=False)