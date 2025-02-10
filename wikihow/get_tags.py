from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
import requests


sitemap_url = "https://www.wikihow.com/Special:Sitemap"

response = requests.get(sitemap_url)

soup = BeautifulSoup(response.text, "html.parser")

tag_lists = soup.find_all("div", class_="cat_list")
print("Tag lists:", len(tag_lists))


root = []
for tag_list in tag_lists:
    tag_list_content = tag_list.find_all("li")
    tag_title = tag_list.find("h3").text.strip()
    print("Title:", tag_title)
    print("Number of tags:", len(tag_list_content))
    for tag in tag_list_content:
        tag_name = tag.find("a").text.strip()
        tag_url = tag.find("a")["href"]
        print(tag_name, tag_url)
        root.append((tag_name, tag_url))

print("Total tags:", len(root))
# do bfs and visited all sub-tags
def get_sub_tags(tag_url, visited_set):
    response = requests.get(tag_url)
    soup = BeautifulSoup(response.text, "html.parser")
    tag_list = soup.find_all("div", id="cat_sub_categories")
    if len(tag_list) == 0:
        print("No sub-tags found for", tag_url)
        return []
    
    sub_tags = []
    for tag in tag_list:
        tag_infos = tag.find_all("div", class_="subcat_container")
        for tag_info in tag_infos:
            tag_name = tag_info.find("a").text.strip()
            tag_url = tag_info.find("a")["href"]
            # print(tag_name, tag_url)
            if tag_name in visited_set:
                continue
            visited_set.add(tag_name)
            sub_tags.append((tag_name, tag_url))
    print("Visited", tag_url, "Get sub-tags", len(sub_tags), sub_tags)
    return sub_tags
    

def bfs(root):
    if len(root) == 0:
        return []
    all_nodes = []
    all_nodes.extend(root)
    queue = root
    # total is unk
    pbar = tqdm()
    visited_set = set()
    while len(queue) > 0:
        pbar.update(1)
        tag_name, tag_url = queue.pop(0)
        tag_url = "https://www.wikihow.com" + tag_url
        # print(tag_name, tag_url)
        # get all sub-tags
        sub_tags = get_sub_tags(tag_url, visited_set)
        # exit()
        all_nodes.extend(sub_tags)
        queue.extend(sub_tags)
        print("Current Queue size", len(queue))
    return all_nodes

all_nodes = bfs(root)
print("Total nodes:", len(all_nodes))
os.makedirs("data/tags", exist_ok=True)
with open("data/tags/tags.json", "w") as f:
    json.dump(all_nodes, f, indent=4, ensure_ascii=False)
