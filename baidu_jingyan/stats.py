import os
import json

data_root = "data/summary"
links = set()
for file in os.listdir(data_root):
    with open(os.path.join(data_root, file), "r") as f:
        data = json.load(f)
        for each in data:
            link = each["link"]
            links.add(link)
            
print("Remove duplicate links")
print(len(links))


steps_files = "data/steps"
for file in os.listdir(steps_files):
    with open(os.path.join(steps_files, file), "r") as f:
        data = json.load(f)
        print(len(data))
print("Total steps:", total_steps)