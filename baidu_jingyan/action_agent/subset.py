import os
import shutil
import random
import json
os.makedirs("data/steps_subset", exist_ok=True)
# subset folder in data/steps/ and cp them into new folder data/steps_subset/

for folder in os.listdir("data/steps"):
    if random.random() < 0.01:
        
        # copy images as well
        shutil.copytree(os.path.join("data/steps", folder), os.path.join("data/steps_subset", folder))
        try:
            with open(os.path.join("data/steps", folder, "steps_with_images.json"), "r") as f:
                data = json.load(f)
            for step in data["steps"]:
                if step["image_url"] is not None:
                    if os.path.exists(os.path.join("data/images", step["image_url"])):
                        os.makedirs(os.path.join("data/steps_subset", folder), exist_ok=True)
                        shutil.copy(os.path.join("data/images", step["image_url"]), os.path.join("data/steps_subset", folder, step["image_url"]))
                        print("Copy success: ", os.path.join("data/steps_subset", folder, step["image_url"]))
        except Exception as e:
            print(f"Error copying {folder}: {e}")