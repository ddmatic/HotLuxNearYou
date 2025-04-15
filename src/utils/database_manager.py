import sqlite3
import pandas as pd
import os
from datetime import datetime


class DatabaseManager:
    """Handles all database operations for the apartment tracker."""

    def __init__(self, config):
        """Initialize with configuration object."""
        self.config = config
        self.db_path = os.path.join(self.config.DATA_DIR, "apartment_tracker.db")
        self.setup_database()

    def setup_database(self):
        """Create database tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create listings table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS listings (
            id INTEGER PRIMARY KEY,
            url TEXT UNIQUE,
            price REAL,
            area REAL,
            rooms TEXT,
            floor TEXT,
            max_floor TEXT,
            ad_text TEXT,
            report_date DATE,
            ai_analysis TEXT,
            go_to_link TEXT
        )
        ''')

        # Create a table for tracking listing status
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS listing_history (
            id INTEGER PRIMARY KEY,
            url TEXT,
            status TEXT,
            change_date DATE,
            FOREIGN KEY (url) REFERENCES listings (url)
        )
        ''')

        conn.commit()
        conn.close()

        print(f"Database initialized at {self.db_path}")

    def save_listings(self, df):
        """Save DataFrame listings to the database."""
        conn = sqlite3.connect(self.db_path)

        # Convert DataFrame to format suitable for database
        df_to_save = df.copy()
        df_to_save['report_date'] = pd.to_datetime(df_to_save['ReportDate']).dt.date

        # Map DataFrame columns to database columns
        columns_mapping = {
            'url': 'url',
            'Price': 'price',
            'Area': 'area',
            'Rooms': 'rooms',
            'Floor': 'floor',
            'Max Floor': 'max_floor',
            'AdText': 'ad_text',
            'AISays': 'ai_analysis',
            'GoToLink': 'go_to_link',
            'report_date': 'report_date'
        }

        # Select and rename columns for database insertion
        df_db = df_to_save[[col for col in columns_mapping.keys() if col in df_to_save.columns]]
        df_db = df_db.rename(columns=columns_mapping)

        # 🚨 NEW: Filter out duplicate URLs that already exist in DB
        existing_urls = pd.read_sql_query("SELECT url FROM listings", conn)['url'].tolist()
        df_db = df_db[~df_db['url'].isin(existing_urls)]

        if df_db.empty:
            print("No new listings to save.")
            conn.close()
            return

        # Insert data into the database
        df_db.to_sql('listings', conn, if_exists='append', index=False)

        # Record listing history
        today = datetime.now().date()
        for url in df_db['url']:
            cursor = conn.cursor()
            cursor.execute('''
            INSERT INTO listing_history (url, status, change_date)
            VALUES (?, ?, ?)
            ''', (url, 'active', today))

        conn.commit()
        conn.close()

        print(f"Saved {len(df_db)} new listings to database")

    def mark_listings_as_removed(self, removed_urls):
        """Mark listings as removed in the database."""
        if not removed_urls or len(removed_urls) == 0:
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        today = datetime.now().date()

        for url in removed_urls:
            cursor.execute('''
            INSERT INTO listing_history (url, status, change_date)
            VALUES (?, ?, ?)
            ''', (url, 'removed', today))

        conn.commit()
        conn.close()

        print(f"Marked {len(removed_urls)} listings as removed")

    def get_all_active_listings(self):
        """Retrieve all currently active listings from the database."""
        conn = sqlite3.connect(self.db_path)

        # Get the most recent status for each URL
        query = '''
        SELECT l.*, 
               (SELECT status FROM listing_history h 
                WHERE h.url = l.url 
                ORDER BY change_date DESC LIMIT 1) as status
        FROM listings l
        WHERE status = 'active'
        '''

        df = pd.read_sql_query(query, conn)

        # Rename columns back to application format
        columns_mapping = {
            'url': 'url',
            'price': 'Price',
            'area': 'Area',
            'rooms': 'Rooms',
            'floor': 'Floor',
            'max_floor': 'Max Floor',
            'ad_text': 'AdText',
            'ai_analysis': 'AISays',
            'go_to_link': 'GoToLink',
            'report_date': 'ReportDate'
        }

        df = df.rename(columns={v: k for k, v in columns_mapping.items() if v in df.columns})

        conn.close()
        return df

    def get_new_listings_since(self, date):
        """Get listings that were added after the specified date."""
        conn = sqlite3.connect(self.db_path)

        query = '''
        SELECT l.* FROM listings l
        JOIN listing_history h ON l.url = h.url
        WHERE h.status = 'active'
        AND h.change_date >= ?
        AND h.id IN (
            SELECT MIN(id) FROM listing_history
            WHERE url = l.url
            GROUP BY url
        )
        '''

        df = pd.read_sql_query(query, conn, params=(date,))

        # Rename columns back to application format
        columns_mapping = {
            'url': 'url',
            'price': 'Price',
            'area': 'Area',
            'rooms': 'Rooms',
            'floor': 'Floor',
            'max_floor': 'Max Floor',
            'ad_text': 'AdText',
            'ai_analysis': 'AISays',
            'go_to_link': 'GoToLink',
            'report_date': 'ReportDate'
        }

        df = df.rename(columns={v: k for k, v in columns_mapping.items() if v in df.columns})

        conn.close()
        return df

    def get_removed_listings_since(self, date):
        """Get listings that were removed after the specified date."""
        conn = sqlite3.connect(self.db_path)

        query = '''
        SELECT l.* FROM listings l
        JOIN listing_history h ON l.url = h.url
        WHERE h.status = 'removed'
        AND h.change_date >= ?
        '''

        df = pd.read_sql_query(query, conn, params=(date,))

        # Rename columns back to application format
        columns_mapping = {
            'url': 'url',
            'price': 'Price',
            'area': 'Area',
            'rooms': 'Rooms',
            'floor': 'Floor',
            'max_floor': 'Max Floor',
            'ad_text': 'AdText',
            'ai_analysis': 'AISays',
            'go_to_link': 'GoToLink',
            'report_date': 'ReportDate'
        }

        df = df.rename(columns={v: k for k, v in columns_mapping.items() if v in df.columns})

        conn.close()
        return df
