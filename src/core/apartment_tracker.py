import pandas as pd


class ApartmentTracker:
    """Main application class for tracking apartment listings."""

    def __init__(self, config, roman_converter, data_processor, scraper, file_manager, ai_analyzer=None):
        """Initialize with all component objects."""
        self.config = config
        self.roman_converter = roman_converter
        self.data_processor = data_processor
        self.scraper = scraper
        self.file_manager = file_manager
        self.ai_analyzer = ai_analyzer
        self.do_ai_stuff = ai_analyzer is not None

    def run(self):
        """Run the apartment tracking process."""
        # Create necessary directories
        self.file_manager.create_directories()

        # Scrape listings
        ads = self.scraper.scrape_listings()

        # Convert to DataFrame and process floor data
        df_today = pd.DataFrame(ads)
        df_today = self.data_processor.process_floor_data(df_today)

        # Load existing data and find new rows
        existing_df = self.file_manager.load_tdy_data()

        if existing_df is not None:
            print(f"TDY: {df_today.columns}")
            print(f"YTD: {existing_df.columns}")
            new_rows = self.data_processor.append_new_rows(existing_df, df_today)
            new_rows = new_rows.dropna(axis=1, how="all")
            df_today = pd.concat([existing_df, new_rows])

        # Scrape ad descriptions
        df_today = self.scraper.scrape_ad_descriptions(df_today)

        # Add hyperlinks and date
        df_today = self.data_processor.add_hyperlinks_and_date(df_today)

        # Perform AI analysis if enabled
        if self.do_ai_stuff:
            df_today = self.ai_analyzer.process_dataframe(df_today)

        # Handle existing files (delete YTD, rename TDY to YTD)
        ytd_exists = self.file_manager.handle_excel_files()

        # Load previous listings if available
        if ytd_exists:
            df_ytd = self.file_manager.load_ytd_data()

            # Identify new and removed listings
            new_ads, removed_ads = self.data_processor.identify_new_and_removed_listings(df_today, df_ytd)

            print(f"{len(new_ads)} new listings found.")
            print(f"{len(removed_ads)} removed listings found.")
        else:
            print("apts_ytd.xlsx not found. Treating all current listings as new.")
            new_ads = df_today.copy()
            removed_ads = pd.DataFrame(columns=df_today.columns)

        # Save data to Excel
        self.file_manager.save_data_to_excel(df_today, new_ads, removed_ads)

        # Create or update .bat file
        self.file_manager.create_or_update_bat_file()