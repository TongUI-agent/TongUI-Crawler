import os
import json

def get_stats():
    count_set = set()
    for file in os.listdir("data/summary"):
        with open(f"data/summary/{file}", "r") as f:
            data = json.load(f)
            print(file, len(data))
            for item in data:
                count_set.add(item["url"])
    print("Total unique urls:", len(count_set))

if __name__ == "__main__":
    get_stats()
