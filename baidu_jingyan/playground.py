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
    
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start with maximized window
    return chrome_options

if __name__ == "__main__":
    link = "http://jingyan.baidu.com/article/a378c9608bf679b32828303d.html"
    chrome_options = get_chrome_options()
    # Initialize the Chrome driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    html = get_website_html(link, driver=driver)
    # print(html)
    step_data = parse_baidu_jingyan(html)
    print(step_data)
