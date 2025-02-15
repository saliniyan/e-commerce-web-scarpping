from pymongo import MongoClient
from datetime import datetime

# ✅ Connect to MongoDB
try:
    client = MongoClient("mongodb+srv://saliniyan:saliniyan@cluster0.tp4v7al.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    db = client["scraped_data"]
    print("✅ Connected to MongoDB successfully!\n")
except Exception as e:
    print("❌ MongoDB Connection Error:", e)
    exit()

def get_available_dates():
    """Lists all unique dates available in each collection."""
    sources = ["blinkit", "bigbasket", "swiggy", "zepto"]
    
    print("📅 Available Scraped Dates:\n")
    for source in sources:
        collection = db[source]
        dates = collection.distinct("scraped_date")  # Get unique dates
        print(f"🔹 {source.capitalize()}: {dates}")

def get_products_by_date(date_str, source):
    """
    Fetches scraped data from MongoDB for a specific date and source.
    
    :param date_str: Date in "YYYY-MM-DD" format.
    :param source: Collection name (blinkit, bigbasket, swiggy, zepto).
    :return: List of products scraped on that date.
    """
    collection = db[source]
    results = list(collection.find({"scraped_date": date_str}, {"_id": 0}))  # Exclude MongoDB _id field

    if results:
        print(f"\n✅ Found {len(results)} products from {source} on {date_str}:")
        for i, product in enumerate(results[:5]):  # Show first 5 products as a preview
            print(f"{i+1}. {product}")
        return results
    else:
        print(f"\n⚠️ No products found in {source} on {date_str}.")
        return []

# 🎯 Main Menu
while True:
    print("\n📌 Select an option:")
    print("1️⃣ List available dates")
    print("2️⃣ Fetch products by date")
    print("3️⃣ Exit")

    choice = input("Enter choice (1/2/3): ")

    if choice == "1":
        get_available_dates()

    elif choice == "2":
        date_input = input("Enter date (YYYY-MM-DD) to fetch products: ")
        source_input = input("Enter source (blinkit, bigbasket, swiggy, zepto): ")
        get_products_by_date(date_input, source_input)

    elif choice == "3":
        print("🚀 Exiting program. Goodbye!")
        break

    else:
        print("❌ Invalid choice. Please select 1, 2, or 3.")
