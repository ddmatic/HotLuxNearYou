import pandas as pd
from flask import Flask, jsonify, render_template, send_file
import threading
import time
from main import run_scraper_script  # Make sure this imports your existing script
from config import TDY_PATH

app = Flask(__name__)

# Flag to track if the script is running
script_running = False


# Function to simulate running the script (replace with your actual script)
def run_script_background():
    global script_running
    try:
        script_running = True
        run_scraper_script()  # Call your actual script here
    finally:
        script_running = False


@app.route('/')
def home():
    # Path to your generated Excel file
    excel_file_path = TDY_PATH

    try:
        # Load the 'new_listings' sheet into a DataFrame
        df_new = pd.read_excel(excel_file_path, sheet_name="new_listings")
        df_all = pd.read_excel(excel_file_path, sheet_name="src")

        # Convert the DataFrame to a dictionary for rendering in the template
        new_listings = df_new.to_dict(orient='records')
        all_listings = df_all.to_dict(orient="records")

        return render_template('index.html', new_listings=new_listings, src_listings=all_listings)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Excel file not found."})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})


@app.route('/run-script', methods=['POST'])
def run_script():
    # Run the script in a background thread to avoid blocking the main thread
    if not script_running:
        thread = threading.Thread(target=run_script_background)
        thread.start()
        return jsonify({"status": "success", "message": "Script started running in the background."})
    else:
        return jsonify({"status": "error", "message": "Script is already running."})


@app.route('/status')
def status():
    # Return current status (whether the script is running or not)
    if script_running:
        return jsonify({"running": True, "message": "Script is running..."})
    else:
        return jsonify({"running": False, "message": "Script is not running."})


@app.route('/download')
def download():
    # Path to your generated Excel file
    excel_file_path = TDY_PATH
    try:
        return send_file(excel_file_path, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"status": "error", "message": "Excel file not found."})


# @app.route("/new_listings")
# def new_listings():
#     # Path to your generated Excel file
#     excel_file_path = TDY_PATH
#
#     try:
#         # Load the 'new_listings' sheet into a DataFrame
#         df = pd.read_excel(excel_file_path, sheet_name="new_listings")
#
#         # Print the data to the console to check if it's loaded correctly
#         print(df.head())  # Print the first few rows
#
#         # Convert the DataFrame to a dictionary for rendering in the template
#         listings = df.to_dict(orient='records')
#
#         # Check if listings are being converted to a dictionary correctly
#         print(listings)  # This will print the list of dictionaries
#
#         return render_template('index.html', listings=listings)
#     except FileNotFoundError:
#         return jsonify({"status": "error", "message": "Excel file not found."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})


# @app.route('/')
# def index():
#     # Path to your generated Excel file
#     excel_file_path = TDY_PATH
#
#     try:
#         # Load the 'new_listings' sheet into a DataFrame
#         df = pd.read_excel(excel_file_path, sheet_name="new_listings")
#
#         # Convert the DataFrame to a dictionary for rendering in the template
#         listings = df.to_dict(orient='records')
#
#         return render_template('index.html', listings=listings)
#     except FileNotFoundError:
#         return jsonify({"status": "error", "message": "Excel file not found."})
#     except Exception as e:
#         return jsonify({"status": "error", "message": str(e)})


if __name__ == "__main__":
    app.run(debug=True, port=5050)
