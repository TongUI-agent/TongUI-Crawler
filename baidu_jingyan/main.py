from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from html_parser import parse_baidu_jingyan
from ip_pool import get_proxy, get_proxy_host_port, create_proxyauth_extension

from tqdm import tqdm
import ray
import random
ray.init(num_cpus=1)
# Set up Chrome options

def get_website_html(url, wait_time=0.5, driver=None):
    """
    Visit a website using the local Chrome browser and get its HTML content
    
    Args:
        url (str): The website URL to visit
        wait_time (int): Time to wait for the page to load (in seconds)
    
    Returns:
        str: The HTML content of the page
    """
    
    
    try:
        # Enable Network logging
        # Visit the website
        driver.get(url)
        
        # Wait for the page to load
        time.sleep(random.uniform(1, 3))
        # 模拟真实用户的滚动行为
        scroll_height = random.randint(300, 1000)
        driver.execute_script(f"window.scrollTo(0, {scroll_height});")
        time.sleep(random.uniform(0.5, 1.5))
        # Get the page source (HTML)
        html_content = driver.page_source
        return html_content
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
def check_exists(file_path):
    if os.path.exists(file_path):
        with open(os.path.join(file_path, "steps.json"), "r") as f:
            data = json.load(f)
            return data["steps"] is not None and len(data["steps"]) > 0
    return False

def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start with maximized window
    # make chrome headless
    chrome_options.add_argument("--headless")
    return chrome_options

@ray.remote
def main(file_path):
    # Example usage
    with open(file_path, "r") as f:
        data = json.load(f)
    # data = data[:2]
    chrome_options = get_chrome_options()
    # Initialize the Chrome driver
    
    blacklist = set()
    with open("data/blacklist.txt", "r") as f:
        for line in f:
            blacklist.add(line.strip())
    for item in tqdm(data):
        
        url = item["link"]
        if url in blacklist:
            print("skip url in blacklist", url)
            continue
        
        article_id = item["link"].split("/")[-1].replace(".html", "")
        if check_exists(f"data/steps/{article_id}"):
            continue
        print("visit url", url)
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        html = get_website_html(url, driver=driver)
        
        if html:
            #print("HTML content length:", len(html))
            if "百度安全验证" in html:
                print("百度安全验证!")
                
                driver.quit()
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()),
                    options=get_chrome_options()
                )
                # append this url to blacklist
                with open("data/blacklist.txt", "a") as f:
                    f.write(url + "\n")
                blacklist.add(url)
                # time.sleep(600)
            step_data = parse_baidu_jingyan(html)
            #print(step_data)
            os.makedirs(f"data/steps/{article_id}", exist_ok=True)
            with open(f"data/steps/{article_id}/steps.json", "w") as f:
                step_data = {
                    "page": item,
                    "steps": step_data
                }
                json.dump(step_data, f, indent=4, ensure_ascii=False)
            with open(f"data/steps/{article_id}/page.html", "w") as f:
                f.write(html)
        else:
            print("Failed to get HTML content, so reset the driver")
        driver.quit()
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=get_chrome_options()
        )
    # driver.quit()

if __name__ == "__main__":
    file_paths = [f"data/summary/{tag_file}" for tag_file in os.listdir("data/summary")]
    print(file_paths)
    max_retries = 3
    results = []
    
    for file_path in file_paths:
        retry_count = 0
        while retry_count < max_retries:
            try:
                result = ray.get(main.remote(file_path))
                results.append(result)
                break
            except Exception as e:
                print(f"Task failed for {file_path}, attempt {retry_count + 1}/{max_retries}")
                retry_count += 1
                if retry_count == max_retries:
                    print(f"Max retries reached for {file_path}")
