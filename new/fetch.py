from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from datetime import datetime

app = Flask(__name__)

# ✅ Connect to MongoDB
client = MongoClient("mongodb+srv://saliniyan:saliniyan@cluster0.tp4v7al.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["scraped_data"]
sources = ["blinkit", "bigbasket", "swiggy", "zepto"]

@app.route("/")
def index():
    """Homepage - Show available scraped dates."""
    available_dates = {source: db[source].distinct("scraped_date") for source in sources}
    return render_template("fetch.html", sources=sources, available_dates=available_dates)

@app.route("/fetch", methods=["POST"])
def fetch_products():
    """Fetch products based on selected date and source."""
    date = request.form["date"]
    source = request.form["source"]

    collection = db[source]
    
    # Fetch products for selected date
    products = list(collection.find({"scraped_date": date, "new_price": {"$exists": True, "$ne": None}}, {"_id": 0, "name": 1, "new_price": 1})) 

    available_dates = {source: db[source].distinct("scraped_date") for source in sources}

    return render_template(
        "fetch.html", 
        sources=sources, 
        available_dates=available_dates,  
        products=products, 
        selected_date=date, 
        selected_source=source
    )

@app.route("/product_prices", methods=["GET"])
def product_prices():
    """Fetch price trends of selected product for each month and today's price."""
    product_name = request.args.get("name")
    selected_source = request.args.get("source")
    
    if not product_name or not selected_source:
        return jsonify([])  # Return empty if no product is selected

    collection = db[selected_source]

    # Fetch price history for selected product
    product_prices = list(collection.find({"name": product_name}, {"_id": 0, "scraped_date": 1, "new_price": 1}))

    # Get today's date
    today = datetime.today().strftime('%Y-%m-%d')

    # Prepare a dictionary to hold price data per month
    monthly_prices = {}

    for product in product_prices:
        month = product["scraped_date"][:7]  # Extract month in YYYY-MM format
        monthly_prices[month] = product["new_price"]

    # Ensure the current month is included with today's price
    monthly_prices[today[:7]] = next((p["new_price"] for p in product_prices if p["scraped_date"] == today), "-")

    # Fill in missing months with "-"
    all_months = sorted(list(monthly_prices.keys()))
    price_data = [{"month": month, "price": monthly_prices.get(month, "-")} for month in all_months]

    return jsonify(price_data)

if __name__ == "__main__":
    app.run(debug=True)
