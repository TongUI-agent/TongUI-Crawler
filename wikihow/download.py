import requests
import os
import json
import copy
from tqdm import tqdm
import ray
import numpy as np
import random
ray.init(num_cpus=10)
os.makedirs("data/images", exist_ok=True)
def download_file(url, file_path):
    for i in range(3):
        try:
            response = requests.get(url, timeout=10)
            with open(file_path, "wb") as f:
                f.write(response.content)
            break
        except Exception as e:
            print(f"Download failed: {e}")
            print(f"Retry {i+1}")
            
step_files = os.listdir("data/steps")

@ray.remote
def main(step_files):
    for step_file in tqdm(step_files):
        if not os.path.exists(f"data/steps/{step_file}/steps.json"):
            print(f"File {step_file} does not exist")
            continue
        with open(f"data/steps/{step_file}/steps.json", "r") as f:
            step_data = json.load(f)
            # print(step_data)
        
        sections = step_data["sections"]
        sections_processed = []
        for section in sections:
            # print(section)
            step_processed = []
            for step in section["steps"]:
                temp = copy.deepcopy(step)
                if "image_src" in temp and temp["image_src"] is not None:
                    image_src = temp["image_src"]
                    image_file_name = image_src.split("/")[-1]
                    image_file_path = f"data/images/{image_file_name}"
                    if not os.path.exists(image_file_path):
                        download_file(image_src, image_file_path)
                    else:
                        print(f"Image {image_file_name} already exists")
                    temp["image_src"] = image_file_name
                step_processed.append(temp)
            section_processed = copy.deepcopy(section)
            section_processed["steps"] = step_processed
            sections_processed.append(section_processed)
        step_data["sections"] = sections_processed
        with open(f"data/steps/{step_file}/steps_processed.json", "w") as f:
            json.dump(step_data, f, indent=4)

if __name__ == "__main__":
    # split step_files into 10 parts
    random.shuffle(step_files)
    step_files_split = np.array_split(step_files, 10)
    futures = []
    for i in range(10):
        futures.append(main.remote(step_files_split[i]))
    ray.get(futures)
    print("Done")