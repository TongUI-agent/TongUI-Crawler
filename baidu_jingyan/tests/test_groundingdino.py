#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip3 install requests

import time
import requests
import base64
import unittest
from PIL import Image, ImageDraw, ImageFont

API_ENDPOINTS = {
    "GroundingDINO-1.5-Pro": "https://api.deepdataspace.com/tasks/detection",
    "DinoX": "https://api.deepdataspace.com/tasks/dinox",
}
def call_groundingdino(image_path, prompt, model="GroundingDINO-1.5-Pro"):
    headers = {
        "Content-Type": "application/json",
        "Token"       : "6c4b0934f1a71a85122a81700191677b"
    }
    # base64 encode image   
    with open(image_path, "rb") as f:
        image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")
    if model is not None:
        body = {
            "image": f"data:image/jpg;base64,{image_base64}",
            "prompts": [
                {"type": "text", "text": prompt},
                
            ],
            "model": model,
            "targets": ["bbox"]
        }
    else:
        body = {
            "image": f"data:image/jpg;base64,{image_base64}",
            "prompts": [
                {"type": "text", "text": prompt}
            ]
        }

    max_retries = 60  # max retry times
    retry_count = 0

    # send request
    api_endpoint = API_ENDPOINTS[model]
    resp = requests.post(
        api_endpoint,
        json=body,
        headers=headers
    )

    if resp.status_code == 200:
        json_resp = resp.json()
        print(json_resp)
        # {'code': 0, 'data': {'task_uuid': '092ccde4-a51a-489b-b384-9c4ba8af7375'}, 'msg': 'ok'}

        # get task_uuid
        task_uuid = json_resp["data"]["task_uuid"]
        print(f'task_uuid:{task_uuid}')

        # poll get task result
        while retry_count < max_retries:
            resp = requests.get(f'https://api.deepdataspace.com/task_statuses/{task_uuid}', headers=headers)
            if resp.status_code != 200:
                break
            json_resp = resp.json()
            if json_resp["data"]["status"] not in ["waiting", "running"]:
                break
            time.sleep(1)
            retry_count += 1

        if json_resp["data"]["status"] == "failed":
            print(f'failed resp: {json_resp}')
        elif json_resp["data"]["status"] == "success":
            print(f'success resp: {json_resp}')
        else:
            print(f'get task resp: {resp.status_code} - {resp.text}')
        return json_resp
    else:
        print(f'Error: {resp.status_code} - {resp.text}')
        return None

def draw_bbox(image_path, bbox, category):
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)
    draw.rectangle(bbox, outline='blue')
    draw.text((bbox[0], bbox[1]), f"{category}", fill='blue', font=ImageFont.truetype("arial.ttf", 20))
    image.show()
    # Convert RGBA to RGB before saving as JPEG
    rgb_image = Image.new('RGB', image.size, (255, 255, 255))
    rgb_image.paste(image, mask=image.split()[3] if len(image.split()) == 4 else None)
    rgb_image.save(f"{image_path.split('.')[0]}_groundingdino.jpg")

class TestGroundingDINO(unittest.TestCase):
    def test_case1(self):
        image_path = "data/temp/bd72f23834bb19ef605994a2497bd28286893a5d.jpg"
        prompt = "red box"
        model = "GroundingDINO-1.5-Pro"
        json_resp = call_groundingdino(image_path, prompt, model)
        bbox = json_resp["data"]["result"]["objects"][0]["bbox"]
        category = json_resp["data"]["result"]["objects"][0]["category"]
        draw_bbox(image_path, bbox, category)
        
    def test_case2(self):
        image_path = "data/temp/1f03436b04d14929126037ab63e5eceeacbc7e40.jpg"
        prompt = "yellow boxes"
        model = "DinoX"
        json_resp = call_groundingdino(image_path, prompt, model)
        bbox = json_resp["data"]["result"]["objects"][0]["bbox"]
        category = json_resp["data"]["result"]["objects"][0]["category"]
        draw_bbox(image_path, bbox, category)
        
    def test_case3(self):
        image_path = "data/temp/baab2086304861436f1243858febf6a75e0f531e.jpg"
        prompt = "red arrow"
        model = "DinoX"
        json_resp = call_groundingdino(image_path, prompt, model)
        bbox = json_resp["data"]["result"]["objects"][0]["bbox"]
        category = json_resp["data"]["result"]["objects"][0]["category"]
        draw_bbox(image_path, bbox, category)
    
    def test_case4(self):
        image_path = "data/temp/aid1375465-v4-728px-Make-an-Exe-File-Step-1-Version-3.jpg"
        prompt = "green box"
        model = "DinoX"
        json_resp = call_groundingdino(image_path, prompt, model)
        bbox = json_resp["data"]["result"]["objects"][0]["bbox"]
        category = json_resp["data"]["result"]["objects"][0]["category"]
        draw_bbox(image_path, bbox, category)
        
if __name__ == "__main__":
    unittest.main()