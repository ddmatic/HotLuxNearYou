import pandas as pd


class DataProcessor:
    """Handles data processing operations for apartment listings."""

    @staticmethod
    def create_hyperlink(url):
        """Create an Excel hyperlink formula for a URL."""
        return f'=HYPERLINK("{url}", "ClickToGo")'

    @staticmethod
    def append_new_rows(df_old, df_new, compare_col="url"):
        """
        Find rows in df_new that don't exist in df_old based on the compare_col.
        Returns a DataFrame of new rows.
        """
        # First, check if the column exists in both DataFrames
        if compare_col not in df_old.columns or compare_col not in df_new.columns:
            print(f"Warning: '{compare_col}' column missing in one or both DataFrames")
            print(f"df_old columns: {df_old.columns.tolist()}")
            print(f"df_new columns: {df_new.columns.tolist()}")

            # Choose a fallback column if available
            if len(df_old.columns) > 0 and len(df_new.columns) > 0:
                common_cols = set(df_old.columns).intersection(set(df_new.columns))
                if common_cols:
                    compare_col = list(common_cols)[0]
                    print(f"Using '{compare_col}' as alternative comparison column")
                else:
                    # No common columns, can't compare
                    print("No common columns found, cannot find new rows")
                    return df_new.iloc[0:0]  # Return empty DataFrame with same structure
            else:
                return df_new.iloc[0:0]  # Return empty DataFrame with same structure

        # Find rows in df_new that aren't in df_old based on the comparison column
        new_rows = df_new[~df_new[compare_col].isin(df_old[compare_col])]

        return new_rows

    @staticmethod
    def merge_with_db_listings(df_scraped, df_db, key_col="url"):
        """
        Merge scraped listings with database listings to preserve text descriptions.
        Returns merged DataFrame with updated information and preserved descriptions.
        """
        # Create a copy to avoid modifying the original
        result = df_scraped.copy()

        # Iterate through rows to preserve AdText from database
        for index, row in result.iterrows():
            # Find matching row in database
            db_row = df_db[df_db[key_col] == row[key_col]]
            if not db_row.empty:
                # Copy AdText from database if it exists
                if "AdText" in db_row.columns and not pd.isna(db_row["AdText"].iloc[0]):
                    result.at[index, "AdText"] = db_row["AdText"].iloc[0]

        return result

    @staticmethod
    def process_floor_data(df):
        """Split the floor column into Floor and Max Floor columns."""
        df[["Floor", "Max Floor"]] = df["floor"].str.split("/", expand=True)
        return df.drop(columns=["floor"])

    @staticmethod
    def add_hyperlinks_and_date(df):
        """Add hyperlink formulas and current date to DataFrame."""
        import datetime as dt

        df["GoToLink"] = df["url"].apply(lambda x: DataProcessor.create_hyperlink(x))
        df["ReportDate"] = dt.date.today()
        return df

    @staticmethod
    def identify_new_and_removed_listings(df_today, df_ytd):
        """
        Compare current and previous listings to identify new and removed ads.
        Returns new_ads and removed_ads DataFrames.
        """
        # Identify new listings by comparing URLs
        new_ads = df_today[~df_today["url"].isin(df_ytd["url"])]

        # Identify removed listings by comparing URLs
        removed_ads = df_ytd[~df_ytd["url"].isin(df_today["url"])]

        return new_ads, removed_ads