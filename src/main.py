import os
import re
import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime as dt
import funclyb as fl
from config import TDY_PATH, YTD_PATH, SRC, PGR, HEADERS, DATA_DIR

fl.create_paths()

ads = []
page = 1
DO_AI_STUFF = True

while True:
    url = SRC + PGR + str(page)
    print(f"Scraping page {page}: {url}")

    r = requests.get(url, headers=HEADERS)
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
                        features["floor"] = fl.convert_mixed_numerals(value)

                ads.append({
                    "URL": href,
                    "Price": price,
                    "Area": features["Area"],
                    "Rooms": features["Rooms"],
                    "floor": features["floor"]
                })

    page += 1

for num, ad in enumerate(ads):
    print(f"Ad No. {num}: {ad}")

# Convert to DataFrame and Handle Floor Column
df_today = pd.DataFrame(ads)
df_today[["Floor", "Max Floor"]] = df_today["floor"].str.split("/", expand=True)
df_today = df_today.drop(columns=["floor"])

df_loaded = pd.read_excel(DATA_DIR+"\\apts_tdy.xlsx") # Loading existing data from yesterday
df_loaded = df_loaded.dropna(axis=1, how="all")
new_rows = fl.append_new_rows(df_loaded, df_today)
new_rows = new_rows.dropna(axis=1, how="all")
df_today = pd.concat([df_loaded, new_rows])

df_today["AdText2"] = df_today.apply(
    lambda row: fl.scrape_single_ad(row["URL"]) if pd.isna(row["AdText"]) or not row["AdText"] else row["AdText"],
    axis=1
)
df_today["AdText"] = df_today["AdText"].fillna(df_today["AdText2"])

df_today = df_today.drop(columns=["AdText2"])

# Adding =HYPERLINK() for Excel and Date info
df_today["GoToLink"] = df_today["URL"].apply(lambda x: fl.create_hyperlink(x))
df_today["ReportDate"] = dt.date.today()

if DO_AI_STUFF:
    # Initialize AI
    client = fl.create_ai_client()
    df_today["AISays"] = df_today["AdText"].apply(lambda x: fl.ai_analyze(x, client))

    df_today["AISays2"] = df_today.apply(
        lambda row: fl.ai_analyze(row["AdText"], client) if pd.isna(row["AISays"]) or not row["AISays"] else row["AISays"],
        axis=1
    )
    df_today["AISays"] = df_today["AISays"].fillna(df_today["AISays2"])

    df_today = df_today.drop(columns=["AISays2"])

df_today[["AIGarage", "AIAlert"]] = df_today["AISays"].str.split(" > ", expand=True)

# Handle Existing apts_ytd.xlsx
if os.path.exists(YTD_PATH):
    os.remove(YTD_PATH)
    print("\nExisting apts_ytd.xlsx deleted.")
else:
    print("\napts_ytd.xlsx does not exist. Skipping deletion.")

# Rename apts_tdy.xlsx to apts_ytd.xlsx if it exists
if os.path.exists(TDY_PATH):
    os.rename(TDY_PATH, YTD_PATH)
    print("apts_tdy.xlsx renamed to apts_ytd.xlsx.\n")
else:
    print("apts_tdy.xlsx does not exist. Skipping rename.\n")

# Try loading the previous listings (apts_ytd.xlsx) if it exists
if os.path.exists(YTD_PATH):
    df_ytd = pd.read_excel(YTD_PATH, sheet_name="src")

    # Identify new listings by comparing URLs
    new_ads = df_today[~df_today["URL"].isin(df_ytd["URL"])]

    # Identify removed listings by comparing URLs
    removed_ads = df_ytd[~df_ytd["URL"].isin(df_today["URL"])]

    print(f"{len(new_ads)} new listings found.")
    print(f"{len(removed_ads)} removed listings found.")
else:
    print("apts_ytd.xlsx not found. Treating all current listings as new.")
    new_ads = df_today.copy()
    removed_ads = pd.DataFrame(columns=df_today.columns)

# Create a new Excel file with new sheet "new_listings" and "src" sheet
with pd.ExcelWriter(TDY_PATH, engine="openpyxl") as writer:
    # Write full data in "src" sheet
    df_today.to_excel(writer, sheet_name="src", index=False)

    # Write new and removed listings to new sheets
    new_ads.to_excel(writer, sheet_name="new_listings", index=False)
    removed_ads.to_excel(writer, sheet_name="removed_listings", index=False)

fl.create_or_update_bat_file()
print("Data saved to apts_tdy.xlsx.")
