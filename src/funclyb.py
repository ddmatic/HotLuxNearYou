import re
import os
from config import ROOT, BAT_FILE_PATH, DATA_DIR, SCRIPTS_DIR
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd


def roman_to_arabic(roman):
    values = {
        "I": 1,
        "V": 5,
        "X": 10,
        "L": 50,
        "C": 100,
        "D": 500,
        "M": 1000
    }

    result = 0
    prev_value = 0

    # Process the Roman numeral from right to left
    for char in reversed(roman):
        current_value = values[char]

        # If current value is greater than or equal to previous value, add it
        # Otherwise subtract it (handles cases like IV = 4, IX = 9)
        if current_value >= prev_value:
            result += current_value
        else:
            result -= current_value

        prev_value = current_value

    return result


def convert_mixed_numerals(num: str) -> str:
    if "VPR" in num or "PR" in num:
        return re.sub(r"PR|VPR", "Ground Floor", num)

    if "/" not in num:
        return str(roman_to_arabic(num)) + "/?"

    parts = num.split("/")
    roman = parts[0]

    arabic_num = roman_to_arabic(roman)

    return f"{arabic_num}/{parts[1]}"


def create_hyperlink(url):
    return f'=HYPERLINK("{url}", "ClickToGo")'


def create_or_update_bat_file():
    src_dir = os.path.join(ROOT, "src")

    if os.path.exists(BAT_FILE_PATH):
        print("\n.bat file ok!\n")
        return

    # Generate the full path for the .bat file
    bat_content = f'''@echo off
    cd /d "{src_dir}"
    python main.py
    pause
    '''

    # Write the content to the .bat file
    with open(BAT_FILE_PATH, 'w') as bat_file:
        bat_file.write(bat_content)

    print(f"\nCreated the .bat file at {BAT_FILE_PATH}")


def create_paths():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(SCRIPTS_DIR, exist_ok=True)


def scrape_single_ad(url):
    description_text = "Description not available"

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(url)
        time.sleep(1)  # Wait for JavaScript to execute

        soup = BeautifulSoup(driver.page_source, "html.parser")
        info = soup.find_all("div", class_="col-md-12")

        for i in range(len(info)):
            if info[i].find_all("div", class_="product-page view-mode theme-blue"):
                info = info[i].find_all("div", class_="product-page view-mode theme-blue")
                break

        # Check if info is not empty before accessing its first element
        if info:
            tab_groups = info[0].find_all("div", class_="tab-top-group")
            if tab_groups:
                tab_header3 = tab_groups[0].find_all("div", id="tabTopHeader3")
                if tab_header3:
                    description_span = tab_header3[0].find('span', id='plh51')
                    if description_span and description_span.text.strip():
                        description_text = description_span.text.strip()
    except Exception as e:
        description_text = f"Error scraping ad: {str(e)}"
    finally:
        driver.quit()

    print("Done!")
    return description_text


def append_new_rows(df_old: pd.DataFrame, df_new: pd.DataFrame) -> pd.DataFrame:
    compare_col = "URL"

    # Find URLs that are in df_new but not in df_old
    new_urls = df_new[~df_new[compare_col].isin(df_old[compare_col])]

    return new_urls
