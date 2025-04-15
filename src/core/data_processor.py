import pandas as pd


class DataProcessor:
    """Handles data processing operations for apartment listings."""

    @staticmethod
    def create_hyperlink(url):
        """Create an Excel hyperlink formula for a URL."""
        return f'=HYPERLINK("{url}", "ClickToGo")'

    @staticmethod
    def append_new_rows(df_old, df_new):
        """
        Find rows in df_new that don't exist in df_old based on URL.
        Returns a DataFrame of new rows.
        """
        compare_col = "URL"

        # Find URLs that are in df_new but not in df_old
        new_urls = df_new[~df_new[compare_col].isin(df_old[compare_col])]

        return new_urls

    @staticmethod
    def process_floor_data(df):
        """Split the floor column into Floor and Max Floor columns."""
        df[["Floor", "Max Floor"]] = df["floor"].str.split("/", expand=True)
        return df.drop(columns=["floor"])

    @staticmethod
    def add_hyperlinks_and_date(df):
        """Add hyperlink formulas and current date to DataFrame."""
        import datetime as dt

        df["GoToLink"] = df["URL"].apply(lambda x: DataProcessor.create_hyperlink(x))
        df["ReportDate"] = dt.date.today()
        return df

    @staticmethod
    def identify_new_and_removed_listings(df_today, df_ytd):
        """
        Compare current and previous listings to identify new and removed ads.
        Returns new_ads and removed_ads DataFrames.
        """
        # Identify new listings by comparing URLs
        new_ads = df_today[~df_today["URL"].isin(df_ytd["URL"])]

        # Identify removed listings by comparing URLs
        removed_ads = df_ytd[~df_ytd["URL"].isin(df_today["URL"])]

        return new_ads, removed_ads