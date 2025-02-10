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
# Set up Chrome options
from urllib.parse import unquote
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("--urls", action="store_true")
args = parser.parse_args()

def get_urls():
    count_set = set()
    for file in tqdm(os.listdir("data/summary")):
        with open(f"data/summary/{file}", "r") as f:
            data = json.load(f)
            # print(file, len(data))
            for item in data:
                count_set.add(item["url"])
    print("Total unique urls:", len(count_set))
    return list(count_set)

def main():
    with open("data/urls.json", "r") as f:
        urls = json.load(f)
        
    for url in tqdm(urls):
        folder_name = unquote(url.split("/")[-1])  # Decode URL-encoded characters
        if not os.path.exists(f"data/steps/{folder_name}"):
            os.makedirs(f"data/steps/{folder_name}")
            print(f"Folder {folder_name} created")
        else:
            print(f"Folder {folder_name} already exists")
            continue
        try:
            html = get_html(url)
        except Exception as e:
            print(f"Error fetching HTML for {url}: {e}")
            continue
        soup = BeautifulSoup(html, "html.parser")
        # find id=intro
        introduction = soup.find("div", class_="pre-content")
        # print(introduction.text)
        # make sure div has two classes section and steps
        sections = soup.find_all("div", class_=['section', 'steps'])
        # print(len(sections))
        step_dict = {}
        step_dict["introduction"] = introduction.text.strip()
        step_dict["sections"] = []

        for section_id, section in enumerate(sections):
            # print(section)
            # print(section_id)
            headline = section.find("span", class_="mw-headline")
            if headline is None:
                continue
            headline_text = headline.text.strip()
            steps = section.find_all("li")
            section_dict = {}
            section_dict["headline"] = headline_text
            section_dict["steps"] = []
            for step in steps:
                step_info = step.find("div", class_="step")
                if step_info is None:
                    # print("Text Not Found",step)
                    continue
                step_info_text = step_info.text.strip()
                # try get image src
                # find tag img with class whcdn
                image_tag = step.find("img", class_="whcdn")
                if image_tag is not None:
                    image_src = image_tag.get("data-src")
                    section_dict["steps"].append({
                        "text": step_info_text,
                        "image_src": image_src,
                    })
                else:
                    # print("Image Not Found",step)
                    section_dict["steps"].append({
                        "text": step_info_text,
                    })
            if len(section_dict["steps"]) > 0:
                step_dict["sections"].append(section_dict)
        
        step_dict["page"] = dict(
            url=url,
            title=soup.find("title").text.strip(),
        )
        with open(f"data/steps/{folder_name}/steps.json", "w") as f:
            json.dump(step_dict, f, indent=4, ensure_ascii=False)
        
        with open(f"data/steps/{folder_name}/page.html", "w") as f:
            f.write(html)

        time.sleep(1)

def get_html(url):
    response = requests.get(url, timeout=3)
    return response.text

if __name__ == "__main__":
    if args.urls:
        urls = get_urls()
        with open("data/urls.json", "w") as f:
            json.dump(urls, f, indent=4, ensure_ascii=False)
    else:
        main()
        
    # with open("data/urls.json", "w") as f:
    #     json.dump(urls, f, indent=4, ensure_ascii=False)
