from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from html_parser import parse_baidu_jingyan
from tqdm import tqdm
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
def get_website_html(url, wait_time=0.5):
    """
    Visit a website using the local Chrome browser and get its HTML content
    
    Args:
        url (str): The website URL to visit
        wait_time (int): Time to wait for the page to load (in seconds)
    
    Returns:
        str: The HTML content of the page
    """
    
    
    try:
        # Visit the website
        driver.get(url)
        # Wait for the page to load
        time.sleep(wait_time)
        # Get the page source (HTML)
        html_content = driver.page_source
        return html_content
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
    
def main():
    # Example usage
    with open("data/WINDOWS.json", "r") as f:
        data = json.load(f)
    # data = data[:2]
    for item in tqdm(data):
        url = item["link"]
        article_id = item["link"].split("/")[-1].replace(".html", "")
        if os.path.exists(f"data/steps/{article_id}"):
            continue
        html = get_website_html(url)
        
        if html:
            #print("HTML content length:", len(html))
            step_data = parse_baidu_jingyan(html)
            #print(step_data)
            os.makedirs(f"data/steps/{article_id}", exist_ok=True)
            with open(f"data/steps/{article_id}/steps.json", "w") as f:
                step_data = {
                    "page": item,
                    "steps": step_data
                }
                json.dump(step_data, f, indent=4, ensure_ascii=False)
        else:
            print("Failed to get HTML content, so reset the driver")
            driver.quit()
            driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )
    driver.quit()

if __name__ == "__main__":
    main()