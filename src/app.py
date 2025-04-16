import os
import threading
from datetime import datetime
from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlite3
import sys

# Add 'src' to sys.path to import custom modules properly
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from config import Config
from core.roman_converter import RomanConverter
from core.data_processor import DataProcessor
from services.scraper import Scraper
from utils.file_manager import FileManager
from utils.database_manager import DatabaseManager
from utils.sql_queries import listings_table_sql, new_listings_table_sql
from core.apartment_tracker import ApartmentTracker

# Initialize Flask
app = Flask(__name__)

# Initialize core components
config = Config()
roman_converter = RomanConverter()
data_processor = DataProcessor()
scraper = Scraper(config, roman_converter)
file_manager = FileManager(config)
database_manager = DatabaseManager(config)

apartment_tracker = ApartmentTracker(
    config=config,
    roman_converter=roman_converter,
    data_processor=data_processor,
    scraper=scraper,
    file_manager=file_manager,
    database_manager=database_manager,
    ai_analyzer=None
)

# Scraper tracking
is_scraper_running = False
last_run_time = None

def run_scraper_async():
    global is_scraper_running, last_run_time
    is_scraper_running = True
    try:
        apartment_tracker.run()
        print("Scraper run completed successfully.")
        last_run_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print("Error during scraper run:", e)
    finally:
        is_scraper_running = False
    print("Scraper run thread finished.")

@app.route('/')
def index():
    # Connect to DB
    if not os.path.exists(config.DB_PATH):
        return "Database not found at path: {}".format(config.DB_PATH)

    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()

    # Load column names excluding a few
    cursor.execute("PRAGMA table_info(listings)")
    columns = [col[1] for col in cursor.fetchall() if col[1] not in ('id', 'GoToLink', 'AdText')]

    # Fetch filter options
    filters = {}
    for column in columns:
        try:
            quoted = f'"{column}"' if ' ' in column else column
            cursor.execute(f"SELECT DISTINCT {quoted} FROM listings ORDER BY {quoted}")
            values = [row[0] for row in cursor.fetchall() if row[0] is not None]
            if values:
                filters[column] = values
        except sqlite3.OperationalError:
            continue

    conn.close()

    return render_template(
        'index.html',
        filters=filters,
        columns=columns,
        is_scraper_running=is_scraper_running,
        last_run_time=last_run_time
    )

@app.route('/listings')
def get_listings():
    filters = {
        key.replace('filter_', ''): value
        for key, value in request.args.items()
        if key.startswith('filter_') and value
    }

    table_type = request.args.get('table_type', 'all')

    conn = sqlite3.connect(config.DB_PATH)
    query = new_listings_table_sql if table_type == 'new' else listings_table_sql
    params = []

    for column, value in filters.items():
        quoted = f'"{column}"' if ' ' in column else column
        query += f" AND {quoted} LIKE ?"
        params.append(f"%{value}%")

    try:
        df = pd.read_sql_query(query, conn, params=params)
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)})
    conn.close()

    if 'url' in df.columns:
        df['url'] = df['url'].apply(lambda x: f'<a href="{x}" target="_blank" class="btn btn-sm btn-primary">View</a>')

    return jsonify({
        'data': df.to_dict('records'),
        'columns': df.columns.tolist()
    })

@app.route('/run-scraper', methods=['POST'])
def run_scraper():
    global is_scraper_running
    if not is_scraper_running:
        thread = threading.Thread(target=run_scraper_async)
        thread.daemon = True
        thread.start()
        return jsonify({"status": "started"})
    return jsonify({"status": "already_running"})

@app.route('/scraper-status')
def scraper_status():
    return jsonify({
        "is_running": is_scraper_running,
        "last_run": last_run_time
    })

if __name__ == '__main__':
    print("Starting Flask app with DB:", config.DB_PATH)
    app.run(debug=False, host='0.0.0.0', port=5000)
