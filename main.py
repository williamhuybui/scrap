import pandas as pd
import numpy as np
import csv
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from config import *

def core_scraping(driver, link):
    # open link
    driver.get(link)

    # wait until it's available and get all info
    # title
    title = (
        WebDriverWait(driver, 5)
        .until(
            EC.presence_of_element_located(
                (By.XPATH, '//div[@class="xyamay9 x1pi30zi x18d9i69 x1swvt13"]//h1')
            )
        )
        .text
    )
    # print(title)

    # time and location
    time_location = driver.find_element(
        By.XPATH,
        '//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x4zkp8e x676frb x1nxh6w3 x1sibtaa xo1l8bm xi81zsa"]',
    ).text
    # print(time_location)

    # price
    price = driver.find_element(
        By.XPATH,
        '//div[@class="x1xmf6yo"]//span[@class="x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x676frb x1lkfr7t x1lbecb7 xk50ysn xzsf02u"]',
    ).text
    # print(price)
    # get multiple picture links
    picture_links = driver.find_elements(
        By.XPATH, '//div[@class="x1a0syf3 x1ja2u2z"]//img'
    )
    picture_links_list = []
    for i in range(len(picture_links)):
        # print(picture_links[i].get_attribute('src'))
        picture_links_list.append(picture_links[i].get_attribute("src"))

    # Update time
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    return current_time, title, time_location, picture_links_list, price


def is_row_in_df(df, row):

    # # Import
    # # Try decoding the file using different encodings
    # encodings = ["iso-8859-1", "utf-8", "cp1252"]
    # for encoding in encodings:
    #     try:
    #         df = pd.read_csv("data.csv", encoding=encoding)
    #         # print("Successfully decoded file using encoding:", encoding)
    #         break
    #     except UnicodeDecodeError:
    #         print("Error decoding file using encoding:", encoding)

    # Check
    row = pd.DataFrame(row)
    is_in_df = row.isin(df)
    if is_in_df.any(axis=None):
        print("New listing")
        return True
    print("Old listing")
    return False


def loop_over_item(driver, df, item_links, verbose=False):
    for item_link in item_links:
        # get all info
        try:
            (
                current_time,
                title,
                time_location,
                picture_links_list,
                price,
            ) = core_scraping(driver, item_link)
        # print exception
        except Exception as e:
            print(e)
            print("Error at: ", item_link)
            # skip that item
            continue

        # create a row of data with dictionary
        row = {
            "current_time": current_time,
            "title": title,
            "time_location": time_location,
            "price": price,
            "picture_links_list": picture_links_list,
            "item_link": item_link,
        }
        # Check if the data is old, if it is not, append new data
        if is_row_in_df(df, row) == False:
            with open("data.csv", "a", newline="", encoding="utf-8") as f:
                dictWriter = csv.DictWriter(f, row.keys())
                dictWriter.writerow(row)

        if verbose:
            print(current_time, title, time_location, price)


def scroll(driver, n_loads):
    # Scroll down to load more items 10000 times
    for i in range(n_loads):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)


def get_item_links(driver, url, n_loads):
    # go to the url
    driver.get(url)
    # wait for the page to load
    time.sleep(5)
    # scroll down to load all items
    scroll(driver, n_loads)
    items = driver.find_elements(
        By.XPATH,
        '//a[@class="x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g x1lku1pv"]',
    )
    # list of all items' link
    item_links = []

    print(len(items))
    # loop through all items
    for item in items:
        # print(item.get_attribute('href'))
        item_links.append(item.get_attribute("href"))
    return item_links


def customize_url(filter):
    """
    Example: url = f"https://www.facebook.com/marketplace/tampa/search/?daysSinceListed=1&query={item}&exact=false
    """
    if filter["location"]:
        raw = f"https://www.facebook.com/marketplace/{filter['location']}/search/?"
    else:
        raw = "https://www.facebook.com/marketplace/category/search/?"

    for key in filter:
        if key != "location":
            raw += f"{key}={filter[key]}&"
    return raw.strip("&")


# Execution
def main():
    # Set up WEBDRIVER
    chrome_options = Options()  # Set up Chrome Options
    chrome_options.add_argument("start-maximized")
    driver = webdriver.Chrome(
        executable_path="chromedriver.exe", options=chrome_options
    )

    df = pd.read_csv(output_dir, encoding="iso-8859-1")
    url = customize_url(filter)
    print(url)
    
    while True:
        item_links = get_item_links(driver, url, n_loads)  # get all items
        loop_over_item(driver, df, item_links, verbose=verbose)
        time.sleep(refresh_rate)
        # driver.quit()

main()
