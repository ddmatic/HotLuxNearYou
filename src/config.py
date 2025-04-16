import os


class Config:
    """Centralized configuration for the apartment tracking application."""

    def __init__(self):
        # Define project root and directories
        self.ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.DATA_DIR = os.path.join(self.ROOT, "data")
        self.SCRIPTS_DIR = os.path.join(self.ROOT, "scripts")

        # Paths for the Excel files
        self.TDY_PATH = os.path.join(self.DATA_DIR, "apts_tdy.xlsx")
        self.YTD_PATH = os.path.join(self.DATA_DIR, "apts_ytd.xlsx")
        self.DB_PATH = os.path.join(self.DATA_DIR, "apartment_tracker.db")

        # .bat File Location
        self.BAT_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                          "scripts\\Hot Lux Near You Runner.bat")

        # URL and request headers for scraping
        # Set filters on https://www.halooglasi.com/nekretnine for your search and replace SRC
        self.SRC = "https://www.halooglasi.com/nekretnine/izdavanje-stanova?grad_id_l-lokacija_id_l-mikrolokacija_id_l=40761%2C40784%2C40788%2C59345&cena_d_from=450&cena_d_to=600&cena_d_unit=4&kvadratura_d_from=40&kvadratura_d_unit=1&ostalo_id_ls=12100016"
        # Shorter list of apts in case of testing
        # self.SRC = "https://www.halooglasi.com/nekretnine/izdavanje-stanova?grad_id_l-lokacija_id_l-mikrolokacija_id_l=40761%2C40784%2C40788%2C59345&cena_d_from=450&cena_d_to=450&cena_d_unit=4&kvadratura_d_from=40&kvadratura_d_unit=1&ostalo_id_ls=12100016"
        self.PGR = "&page="
        self.HEADERS = {"User-Agent": "Mozilla/5.0"}

    def print_paths(self):
        """Print configured paths for debugging purposes."""
        print(f"Data directory: {self.DATA_DIR}")
        print(f"TDY file path: {self.TDY_PATH}")
        print(f"YTD file path: {self.YTD_PATH}")