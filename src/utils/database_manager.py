import pandas as pd
import sqlite3
import datetime as dt


class DatabaseManager:
    """Handles database operations for apartment listings."""

    def __init__(self, config):
        """Initialize with database path."""
        self.db_path = config.DB_PATH
        self.create_tables_if_not_exist()

    def create_tables_if_not_exist(self):
        """Create tables if they don't already exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create the main listings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            Price TEXT,
            Area TEXT,
            Rooms TEXT,
            Floor TEXT,
            "Max Floor" TEXT,
            AdText TEXT,
            GoToLink TEXT,
            ReportDate TEXT,
            is_active INTEGER DEFAULT 1,
            removed_date TEXT,
            add_date TEXT
        )
        ''')

        # Create the new_listings table with the same structure
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS new_listings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            Price TEXT,
            Area TEXT,
            Rooms TEXT,
            Floor TEXT,
            "Max Floor" TEXT,
            AdText TEXT,
            GoToLink TEXT,
            ReportDate TEXT,
            is_active INTEGER DEFAULT 1,
            removed_date TEXT,
            add_date TEXT
        )
        ''')

        conn.commit()
        conn.close()

    def clear_new_listings_table(self):
        """Delete all records from the new_listings table."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM new_listings")

        conn.commit()
        conn.close()
        print("Cleared all records from new_listings table")

    def get_all_active_listings(self):
        """Retrieve all active listings from the database."""
        try:
            conn = sqlite3.connect(self.db_path)
            query = "SELECT * FROM listings WHERE is_active = 1"
            df = pd.read_sql_query(query, conn)
            conn.close()
            return df
        except Exception as e:
            print(f"Error retrieving listings from database: {str(e)}")
            return None

    def save_new_listings(self, df_new):
        """
        Save new listings to the new_listings table.
        """
        if df_new.empty:
            print("No new listings to save.")
            return

        try:
            conn = sqlite3.connect(self.db_path)

            # Add add_date column with current date if it doesn't exist
            if "add_date" not in df_new.columns:
                df_new["add_date"] = dt.date.today().isoformat()

            # Add is_active column if it doesn't exist
            if "is_active" not in df_new.columns:
                df_new["is_active"] = 1

            # Save to database, replace if the URL already exists
            df_new.to_sql("new_listings", conn, if_exists="append", index=False)

            conn.close()
            print(f"Successfully saved {len(df_new)} new listings to new_listings table")
        except Exception as e:
            print(f"Error saving new listings to database: {str(e)}")

    def copy_new_listings_to_main(self):
        """
        Copy all records from new_listings to the main listings table.
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            # Insert records from new_listings into listings, ignoring duplicates by URL
            cursor.execute('''
            INSERT OR IGNORE INTO listings 
            (url, Price, Area, Rooms, Floor, "Max Floor", AdText, GoToLink, ReportDate, is_active, removed_date, add_date)
            SELECT url, Price, Area, Rooms, Floor, "Max Floor", AdText, GoToLink, ReportDate, is_active, removed_date, add_date
            FROM new_listings
            ''')

            copied_count = cursor.rowcount
            conn.commit()
            print(f"Successfully copied {copied_count} new listings to main listings table")

        except Exception as e:
            print(f"Error copying new listings to main table: {str(e)}")
        finally:
            conn.close()

    def save_listings(self, df):
        """Save all listings to the database."""
        try:
            conn = sqlite3.connect(self.db_path)

            # Add add_date column with current date if it doesn't exist
            if "add_date" not in df.columns:
                df["add_date"] = dt.date.today().isoformat()

            # Add is_active column if it doesn't exist
            if "is_active" not in df.columns:
                df["is_active"] = 1

            # Save to database, replace if the URL already exists
            df.to_sql("listings", conn, if_exists="replace", index=False)

            conn.close()
            print(f"Successfully saved {len(df)} listings to database")
        except Exception as e:
            print(f"Error saving listings to database: {str(e)}")

    def mark_listings_as_removed(self, url_list):
        """Mark listings as inactive and set removed date."""
        if not url_list:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            today = dt.date.today().isoformat()
            for url in url_list:
                cursor.execute(
                    "UPDATE listings SET is_active = 0, removed_date = ? WHERE url = ?",
                    (today, url)
                )

            conn.commit()
            print(f"Marked {len(url_list)} listings as removed")
        except Exception as e:
            print(f"Error marking listings as removed: {str(e)}")
        finally:
            conn.close()