from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
# Set up Chrome options
chrome_options = Options()
chrome_options.add_argument("--start-maximized")  # Start with maximized window

# Optional: Run in headless mode (no GUI)
# chrome_options.add_argument("--headless")

# Initialize the Chrome driver
driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=chrome_options
)

urls = []
with open("data/index/index.txt", "r") as f:
    for line in f:
        url = line.strip()
        urls.append(url)

print(urls)
output = []
for url in tqdm(urls):
    title = url[url.find("Category:")+9:]
    if os.path.exists(f"data/summary/{title}.json"):
        with open(f"data/summary/{title}.json", "r") as f:
            data = json.load(f)

        print(f"Skip {title} because it has already been crawled, {len(data)} items")
        continue
    driver.get(url)
    time.sleep(1)
    
    next_page = True
    while next_page:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        summary_list = soup.find('div', id='cat_all')
        if summary_list is None:
            print(f"No summary list found for {url}")
            next_page = False
            continue

        summary_items = summary_list.find_all('div', class_='responsive_thumb')
        if len(summary_items) == 0:
            print(f"No summary items found for {url}")
            next_page = False
            continue

        for summary_item in summary_items:
            summary_item_title = summary_item.find('div', class_='responsive_thumb_title').text
            summary_item_url = summary_item.find('a')['href']
            print(summary_item_title, summary_item_url)
            output.append({
                "title": summary_item_title.strip(),
                "url": summary_item_url.strip()
            })

        # find button with class class="button buttonright pag_next primary" and check if it is disabled
        try:
            button = driver.find_element("css selector", "a[class='button buttonright pag_next primary']")
            # Scroll the button into view
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            time.sleep(1)  # Give time for any overlays to clear
            # Click using JavaScript instead of regular click
            driver.execute_script("arguments[0].click();", button)
        except Exception as e:
            print(f"No next page button found for {url}: {e}")
            next_page = False
            continue

        time.sleep(2)  # Wait for page load
    
        
    with open(f"data/summary/{title}.json", "w") as f:
        json.dump(output, f, indent=4, ensure_ascii=False)
