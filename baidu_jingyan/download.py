import os
import requests
from tqdm import tqdm
import json
import ray

num_workers = 10
ray.init(num_cpus=num_workers)

@ray.remote
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

def get_file_name_and_id_from_url(url):
    # url is like https://exp-picture.cdn.bcebos.com/b666b2530688912c66bbe05b1b4800fc76f797c4.jpg?x-bce-process=image%2Fresize%2Cm_lfit%2Cw_500%2Climit_1%2Fformat%2Cf_auto%2Fquality%2Cq_80
    # get xx.jpg from the url
    file_name = url.split("/")[-1].split("?")[0]
    file_id = file_name.split(".")[0]
    return file_name, file_id

def main():
    steps_data_folder = "data/steps"
    for folder in tqdm(os.listdir(steps_data_folder)):
        folder_path = os.path.join(steps_data_folder, folder)
        if not os.path.exists(os.path.join(folder_path, "steps.json")):
            continue
        # print(f"Downloading images for {folder}")
        steps_new = []
        with open(os.path.join(folder_path, "steps.json"), "r") as f:
            data = json.load(f)
            steps = data["steps"]
            if steps is None:
                print("This page is failed: ", folder)
                continue
            futures = []
            for step in steps:
                if "image_url" in step and step["image_url"] is not None and len(step["image_url"]) > 0:
                    url = step["image_url"]
                    # remove all query parameters
                    url = url.split("?")[0]
                    file_name, file_id = get_file_name_and_id_from_url(url)
                    
                    if not os.path.exists(os.path.join("data/images", file_name)):
                        future = download_file.remote(url, os.path.join("data/images", file_name))
                        futures.append(future)
                    
                    if len(futures) >= num_workers:
                        ray.wait(futures)
                        futures = []
                    steps_new.append({
                        "text": step["text"] if "text" in step else "",
                        "image_url": file_name
                    })
                else:
                    steps_new.append(step)
        
        with open(os.path.join(folder_path, "steps_with_images.json"), "w") as f:
            data["steps"] = steps_new
            json.dump(data, f, indent=4, ensure_ascii=False)

    
if __name__ == "__main__":
    main()
