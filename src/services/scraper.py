import re
import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd


class Scraper:
    """Handles web scraping operations for apartment listings."""

    def __init__(self, config, roman_converter):
        """Initialize with configuration and converter objects."""
        self.config = config
        self.roman_converter = roman_converter

    def scrape_listings(self):
        """
        Scrape apartment listings from the configured URL.
        Returns a list of dictionaries with listing details.
        """
        ads = []
        page = 1

        while True:
            url = self.config.SRC + self.config.PGR + str(page)
            print(f"Scraping page {page}: {url}")

            r = requests.get(url, headers=self.config.HEADERS)
            soup = BeautifulSoup(r.content, "html.parser")

            listings = soup.find_all("div", class_=re.compile(r"product-item product-list-item (Premium|Standard|Top) "
                                                              r"real-estates my-product-placeholder"))

            if not listings:
                print("\nNo more listings found. Stopping.\n")
                break

            for listing in listings:
                info_div = listing.find("div", class_="col-md-6 col-sm-5 col-xs-6 col-lg-6 sm-margin")
                if info_div:
                    a_tag = info_div.find("h3", class_="product-title").a
                    if a_tag and a_tag.has_attr("href"):
                        href = "https://www.halooglasi.com" + a_tag["href"]

                        # Extract price
                        price_div = listing.find("div", class_="central-feature-wrapper")
                        price = None
                        if price_div:
                            value_span = price_div.find("span", attrs={"data-value": True})
                            if value_span:
                                price = value_span["data-value"]

                        # Extract features: area, rooms, floor
                        features = {"Area": None, "Rooms": None, "floor": None}
                        feature_list = info_div.find_all("li", class_="col-p-1-3")
                        for li in feature_list:
                            legend = li.find("span", class_="legend")
                            if not legend:
                                continue
                            label = legend.get_text(strip=True)
                            value = li.get_text(strip=True).replace(label, "").strip()

                            if label == "Kvadratura":
                                features["Area"] = value.replace("m²", "").replace("m2", "").strip()
                            elif label == "Broj soba":
                                features["Rooms"] = value
                            elif label == "Spratnost":
                                features["floor"] = self.roman_converter.convert_mixed_numerals(value)

                        ads.append({
                            "url": href,
                            "Price": price,
                            "Area": features["Area"],
                            "Rooms": features["Rooms"],
                            "floor": features["floor"]
                        })

            page += 1

        for num, ad in enumerate(ads):
            print(f"Ad No. {num}: {ad}")

        return ads

    def scrape_single_ad(self, url):
        """
        Scrape detailed description text from a single ad URL.
        Returns the description text.
        """
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

    def scrape_ad_descriptions(self, df):
        """
        Process a DataFrame to scrape missing ad descriptions.
        Returns the DataFrame with updated ad descriptions.
        """
        df["AdText2"] = df.apply(
            lambda row: self.scrape_single_ad(row["url"])
            if pd.isna(row.get("AdText")) or not row.get("AdText")
            else row.get("AdText"),
            axis=1
        )

        if "AdText" not in df.columns:
            df["AdText"] = ""

        df["AdText"] = df["AdText"].fillna(df["AdText2"])

        df = df.drop(columns=["AdText2"])

        return df
