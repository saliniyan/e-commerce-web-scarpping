from flask import Flask, render_template, request, jsonify
import subprocess
import schedule
import time
import json
import os
import threading
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# Connect to MongoDB
try:
    client = MongoClient("mongodb+srv://saliniyan:saliniyan@cluster0.tp4v7al.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["scraped_data"]  # Database name
    print("✅ Connected to MongoDB successfully!")
except Exception as e:
    print("❌ MongoDB Connection Error:", e)
    exit()

def store_to_mongo(file_path, collection_name):
    """Store JSON data into MongoDB with a timestamp."""
    if not os.path.exists(file_path):
        print(f"⚠️ File not found: {file_path}")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        if not data:
            print(f"⚠️ No data found in {file_path}. Skipping storage.")
            return
        
        if isinstance(data, list):
            for item in data:
                item["scraped_date"] = datetime.utcnow().strftime("%Y-%m-%d")
            db[collection_name].insert_many(data)
        else:
            data["scraped_date"] = datetime.utcnow().strftime("%Y-%m-%d")
            db[collection_name].insert_one(data)

        print(f"✅ Stored {file_path} into MongoDB collection: {collection_name}")
    except json.JSONDecodeError:
        print(f"❌ JSON decoding error in {file_path}. File might be corrupted.")
    except Exception as e:
        print(f"❌ Error storing {file_path} in MongoDB: {e}")

def run_scrapers():
    """Runs all scrapers in batches and stores data in MongoDB."""
    print("\n🚀 Starting Scraping Process...")

    batches = [(0, 1)]
    sources = {
        "blinkit": "blinkit_products.json",
        "bigbasket": "big_products.json",
        "swiggy": "swiggy.json",
        "zepto": "zepto.json"
    }

    for start, end in batches:
        print(f"\n🟢 Processing Batch: {start} to {end}")
        for scraper, file in sources.items():
            try:
                print(f"▶️ Running {scraper.capitalize()} Scraper for range {start} to {end}...")
                subprocess.run(["python", f"{scraper}.py", str(start), str(end)], check=True)
                print(f"✅ {scraper.capitalize()} Scraper Completed for range {start} to {end}.")
                store_to_mongo(file, scraper)
            except subprocess.CalledProcessError as e:
                print(f"❌ Error running {scraper}.py for batch {start}-{end}: {e}")

    print("\n🎯 Scraping Process Completed.\n")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start_scraping', methods=['POST'])
def start_scraping():
    threading.Thread(target=run_scrapers).start()
    return jsonify({"message": "Scraping started successfully!"})

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(60)

# Schedule the scraper to run daily at 2:15 AM
schedule.every().day.at("02:15").do(run_scrapers)
threading.Thread(target=run_scheduler, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
