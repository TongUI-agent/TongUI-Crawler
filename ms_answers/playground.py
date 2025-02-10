from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
import os
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
def get_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")  # Start with maximized window
    # make chrome headless
    # chrome_options.add_argument("--headless")
    return chrome_options

def parse_html(html):
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.find_all("div", class_="c-card")
    card_info_list = []
    for card in cards:
        card_info = card.find("a", class_="c-hyperlink")
        card_info_item = dict()
        if card_info:
            link = card_info.attrs["href"]
            title = card_info.text
            print(link, title)
            card_info_item["link"] = link
            card_info_item["title"] = title
        else:
            print("no card info")
        card_stats = card.find_all("div", class_="stat")
        for card_stat in card_stats:
            card_stat_value = card_stat.attrs["aria-label"]
            if "replies" in card_stat_value:
                card_info_item["replies"] = card_stat_value.split(" ")[0]
        # print("Card Info\n", json.dumps(card_info_item, indent=4, ensure_ascii=False))
        card_info_list.append(card_info_item)
    return card_info_list

def click_filter(driver, date=None):
    # click filter
    filter_span = driver.find_element(By.ID, "threadTypeQuestionsLabel")
    filter_span.click()
    time.sleep(0.1)
    answered_option = driver.find_element(By.ID, "thread-option-answered")
    driver.execute_script("arguments[0].click();", answered_option)
    time.sleep(0.1)
    if date is not None:
        # Use JavaScript to set the date value
        date_input = driver.find_element(By.ID, "postedBefore")
        driver.execute_script(f"arguments[0].value = '{date}';", date_input)
        # Trigger change event to ensure the page recognizes the new value
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_input)
        time.sleep(0.1)
        date_input = driver.find_element(By.ID, "postedAfter")
        # get 1 month before from date
        date_before = datetime.strptime(date, "%Y-%m-%d") - timedelta(days=30)
        driver.execute_script(f"arguments[0].value = '{date_before.strftime('%Y-%m-%d')}';", date_input)
        # Trigger change event to ensure the page recognizes the new value
        driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", date_input)
        time.sleep(0.1)
    # find button with id applyButton
    apply_button = driver.find_element(By.ID, "applyButton")
    apply_button.click()
    time.sleep(0.3)
    
    
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=get_chrome_options())
driver.get("https://answers.microsoft.com/en-us/msoffice/forum")
time.sleep(3)
click_filter(driver, date="2024-01-19")
time.sleep(60)
# parse_html(driver.page_source)
driver.quit()