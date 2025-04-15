import os
import pandas as pd


class FileManager:
    """Handles file operations for the apartment tracking application."""

    def __init__(self, config):
        """Initialize with configuration object."""
        self.config = config

    def create_directories(self):
        """Create necessary directories if they don't exist."""
        os.makedirs(self.config.DATA_DIR, exist_ok=True)
        os.makedirs(self.config.SCRIPTS_DIR, exist_ok=True)

    def create_or_update_bat_file(self):
        """Create or update the .bat file for running the application."""
        src_dir = os.path.join(self.config.ROOT, "src")

        if os.path.exists(self.config.BAT_FILE_PATH):
            print("\n.bat file ok!\n")
            return

        # Generate the bat file content
        bat_content = f'''@echo off
cd /d "{src_dir}"
python main.py
pause
'''

        # Write the content to the .bat file
        with open(self.config.BAT_FILE_PATH, 'w') as bat_file:
            bat_file.write(bat_content)

        print(f"\nCreated the .bat file at {self.config.BAT_FILE_PATH}")

    def handle_excel_files(self):
        """
        Handle the daily Excel file management:
        1. Delete existing YTD file if it exists
        2. Rename TDY file to YTD if it exists
        Returns True if YTD file exists after operations
        """
        # Handle Existing apts_ytd.xlsx
        if os.path.exists(self.config.YTD_PATH):
            os.remove(self.config.YTD_PATH)
            print("\nExisting apts_ytd.xlsx deleted.")
        else:
            print("\napts_ytd.xlsx does not exist. Skipping deletion.")

        # Rename apts_tdy.xlsx to apts_ytd.xlsx if it exists
        if os.path.exists(self.config.TDY_PATH):
            os.rename(self.config.TDY_PATH, self.config.YTD_PATH)
            print("apts_tdy.xlsx renamed to apts_ytd.xlsx.\n")
            return True
        else:
            print("apts_tdy.xlsx does not exist. Skipping rename.\n")
            return False

    def load_ytd_data(self):
        """
        Load data from the YTD file if it exists.
        Returns DataFrame if file exists, None otherwise.
        """
        if os.path.exists(self.config.YTD_PATH):
            return pd.read_excel(self.config.YTD_PATH, sheet_name="src")
        return None

    def load_tdy_data(self):
        """
        Load data from the TDY file if it exists.
        Returns DataFrame if file exists, None otherwise.
        """
        if os.path.exists(self.config.TDY_PATH):
            df = pd.read_excel(self.config.TDY_PATH)
            df = df.dropna(axis=1, how="all")
            return df
        return None

    def save_data_to_excel(self, df_today, new_ads, removed_ads):
        """Save all data to Excel file with multiple sheets."""
        with pd.ExcelWriter(self.config.TDY_PATH, engine="openpyxl") as writer:
            # Write full data in "src" sheet
            df_today.to_excel(writer, sheet_name="src", index=False)

            # Write new and removed listings to new sheets
            new_ads.to_excel(writer, sheet_name="new_listings", index=False)
            removed_ads.to_excel(writer, sheet_name="removed_listings", index=False)

        print("Data saved to apts_tdy.xlsx.")