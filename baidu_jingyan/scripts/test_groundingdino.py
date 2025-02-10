#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# pip3 install requests

import time
import requests
import base64

headers = {
    "Content-Type": "application/json",
    "Token"       : "6c4b0934f1a71a85122a81700191677b"
}
# base64 encode image   
with open("data/temp/bd72f23834bb19ef605994a2497bd28286893a5d.jpg", "rb") as f:
    image_data = f.read()
    image_base64 = base64.b64encode(image_data).decode("utf-8")

body = {
    "image": f"data:image/jpg;base64,{image_base64}",
    "prompts": [
        {"type": "text", "text": "red box"},
    ],
    "model": 'GroundingDino-1.5-Pro',
    "targets": ["bbox"]
}

max_retries = 60  # max retry times
retry_count = 0

# send request
resp = requests.post(
    'https://api.deepdataspace.com/tasks/detection',
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
else:
    print(f'Error: {resp.status_code} - {resp.text}')
