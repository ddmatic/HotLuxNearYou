import os

# Define project root and directories
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(ROOT, "data")
SCRIPTS_DIR = os.path.join(ROOT, "scripts")

# Paths for the Excel files
TDY_PATH = os.path.join(DATA_DIR, "apts_tdy.xlsx")
YTD_PATH = os.path.join(DATA_DIR, "apts_ytd.xlsx")

# .bat File Location
BAT_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts\\Hot Lux Near You Runner.bat")

# URL and request headers for scraping
# Set filters on https://www.halooglasi.com/nekretnine for your search and replace SRC
SRC = "https://www.halooglasi.com/nekretnine/izdavanje-stanova?grad_id_l-lokacija_id_l-mikrolokacija_id_l=40761%2C40784%2C40788%2C59345&cena_d_from=450&cena_d_to=600&cena_d_unit=4&kvadratura_d_from=40&kvadratura_d_unit=1&ostalo_id_ls=12100016"
PGR = "&page="
HEADERS = {"User-Agent": "Mozilla/5.0"}