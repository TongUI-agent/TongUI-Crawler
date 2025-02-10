from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
import random
from selenium.webdriver.common.by import By
from tqdm import tqdm
from bs4 import BeautifulSoup
import ray
import urllib.parse
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from tqdm import tqdm
ray.init(num_cpus=1)
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start with maximized window

# Optional: Run in headless mode (no GUI)
# chrome_options.add_argument("--headless")

# Initialize the Chrome driver
# set max number of concurrent tasks to 10
@ray.remote
def main(link):
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    def visit(link, limit=10):
        next_page = True
        driver.get(link)
        results = []
        count = 0
        current_page = link
        pbar = tqdm(desc="Processing")
        while next_page:
            # time.sleep(10)
            # get list of item
            # for retry
            pbar.update(1)
            for i in range(3):
                success = False
                if i > 0:
                    print("Refresh page!", current_page)
                    driver.get(current_page)
                    
                try:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    # find elements with tag ul and class wgt-list
                    items = soup.find('ul', class_='wgt-list')
                    if items is None:
                        print("No items found")
                        return results

                    # Fix: Find all dt elements and get their first a tag
                    dt_elements = items.find_all("dt")
                    if len(dt_elements) == 0:
                        print("No items found")
                        return results
                        
                    for dt in dt_elements:
                        link_element = dt.find('a')
                        if link_element:
                            results.append({
                                "title": link_element.text.strip(),
                                "link": link_element.get("href").strip()
                            })
                            # print(link_element.text, link_element.get("href"))

                    # Wait up to 10 seconds for the pagination links to appear
                    try:
                        tags = WebDriverWait(driver, 10).until(
                            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.padding8"))
                        )
                    except TimeoutException:
                        print("Pagination links did not appear")
                        tags = []
                
                    if len(tags) == 0:
                        print("No tags found")
                        return results
                    
                    for tag in tags:
                        # print(tag.text, tag.get_attribute("href"))
                        if tag.text == ">":
                            current_page_update = tag.get_attribute("href")
                            tag.click()
                            current_page = current_page_update
                            # Wait for page to load and render
                            # add some random sleep
                            time.sleep(random.uniform(1, 3))
                            tags = WebDriverWait(driver, 10).until(
                                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ul.wgt-list"))
                            )
                            next_page = True
                            # time.sleep(1)
                            break
                        else:
                            next_page = False
                    count += 1
                    if limit > 0 and count > limit:
                        next_page = False
                    success = True
                except Exception as e:
                    import traceback
                    traceback.print_exc()
                    print(e)
                    next_page = False
                if success:
                    print("Success! and skip to next page")
                    break
        return results
        
    # get query parameter from link
    query_params = link.split("?")[1]
    query_params = query_params.split("&")
    query_params = [param.split("=")[1] for param in query_params if param.split("=")[0] == "tagName"]
    # urldecode this param
    tag_name = urllib.parse.unquote(query_params[0]).strip()
    if os.path.exists(f"data/summary/{tag_name}.json"):
        print(f"File {tag_name}.json already exists")
        results = json.load(open(f"data/summary/{tag_name}.json", "r"))
        link += f"&pn={(len(results) + 10) // 10 * 10}" # add offset
    else:
        results = []
    print("Start visit", link)
    results += visit(link, limit=-1)
    print("Output", len(results))
    with open(f"data/summary/{tag_name}.json", "w") as f:
        json.dump(results, f, indent=4, ensure_ascii=False)
    # driver.quit()

if __name__ == "__main__":
    links = []
    with open("data/index/index.txt", "r") as f:
        links = f.readlines()
    ray.get([main.remote(link) for link in links])
