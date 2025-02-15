from flask import Flask, request, render_template, jsonify
import multiprocessing
import subprocess

app = Flask(__name__)

def run_scraper(script, product_name):
    """Run a scraper script as a subprocess."""
    try:
        subprocess.run(["python", script, product_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")

@app.route('/')
def home():
    """Render the home page."""
    return render_template("index.html")

@app.route('/scrape', methods=['POST'])
def scrape_product():
    """API to trigger scraping for a given product name."""
    data = request.get_json()
    if not data or "product_name" not in data:
        return jsonify({"error": "Missing 'product_name' in request"}), 400

    product_name = data["product_name"]

    # Define scraper scripts
    scripts = [
        "new/search/bigbasket.py",
        "new/search/blinkit.py",
        "new/search/swiggy.py",
    ]

    # Create and start processes
    processes = [multiprocessing.Process(target=run_scraper, args=(script, product_name)) for script in scripts]

    for p in processes:
        p.start()

    for p in processes:
        p.join()

    return jsonify({"message": f"Scraping completed for '{product_name}' across all platforms!"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
