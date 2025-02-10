import json

with open("data/tags/tags.json", "r") as f:
    tags = json.load(f)

print("Total tags:", len(tags))

with open("data/index/index.txt", "w") as f:
    for tag in tags:
        tag_url = "https://www.wikihow.com" + tag[1]
        f.write(tag_url + "\n")
