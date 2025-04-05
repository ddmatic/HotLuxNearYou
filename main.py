import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd

SRC = "https://www.halooglasi.com/nekretnine/izdavanje-stanova?grad_id_l-lokacija_id_l-mikrolokacija_id_l=40761%2C40784%2C40788%2C59345&cena_d_from=450&cena_d_to=600&cena_d_unit=4&kvadratura_d_from=40&kvadratura_d_unit=1&ostalo_id_ls=12100016"
PGR = "&page="
HEADERS = {"User-Agent": "Mozilla/5.0"}

ads = []
page = 1

while True:
    url = SRC + PGR + str(page)
    print(f"Scraping page {page}: {url}")

    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.content, "html.parser")

    listings = soup.find_all("div", class_=re.compile(r"product-item product-list-item (Premium|Standard) real-estates my-product-placeholder"))

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
                features = {"kvadratura": None, "broj_soba": None, "spratnost": None}
                feature_list = info_div.find_all("li", class_="col-p-1-3")
                for li in feature_list:
                    legend = li.find("span", class_="legend")
                    if not legend:
                        continue
                    label = legend.get_text(strip=True)
                    value = li.get_text(strip=True).replace(label, "").strip()

                    if label == "Kvadratura":
                        features["kvadratura"] = value.replace("m²", "").replace("m2", "").strip()
                    elif label == "Broj soba":
                        features["broj_soba"] = value
                    elif label == "Spratnost":
                        features["spratnost"] = value

                ads.append({
                    "url": href,
                    "price": price,
                    "area": features["kvadratura"],
                    "rooms": features["broj_soba"],
                    "floor": features["spratnost"]
                })

    page += 1

for num, ad in enumerate(ads):
    print(f"Ad No. {num}: {ad}")

# Convert to DataFrame and verify columns
df_today = pd.DataFrame(ads)

# Handle existing apts_ytd.xlsx
if os.path.exists('apts_ytd.xlsx'):
    os.remove('apts_ytd.xlsx')
    print("Existing apts_ytd.xlsx deleted.\n")

# Rename apts_tdy.xlsx to apts_ytd.xlsx
if os.path.exists('apts_tdy.xlsx'):
    os.rename('apts_tdy.xlsx', 'apts_ytd.xlsx')
    print("apts_tdy.xlsx renamed to apts_ytd.xlsx.\n")

# Load the previous listings (apts_ytd.xlsx)
df_ytd = pd.read_excel('apts_ytd.xlsx', sheet_name='src')

# Identify new listings by comparing URLs
new_ads = df_today[~df_today['url'].isin(df_ytd['url'])]

# Create a new Excel file with new sheet 'new_listings' and 'src' sheet
with pd.ExcelWriter('apts_tdy.xlsx', engine='openpyxl') as writer:
    # Write full data in 'src' sheet
    df_today.to_excel(writer, sheet_name='src', index=False)

    # Write new listings to 'new_listings' sheet
    new_ads.to_excel(writer, sheet_name='new_listings', index=False)

print("Data saved to apts_tdy.xlsx.")
