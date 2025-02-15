import multiprocessing
import subprocess

def run_scraper(script, product_name):
    """Run a scraper script as a subprocess."""
    try:
        subprocess.run(["python", script, product_name], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running {script}: {e}")

if __name__ == "__main__":
    product_name = input("Enter the product name you want to scrape: ")

    # Define scraper scripts
    scripts = [
        "new/search/bigbasket.py",
        "new/search/blinkit.py",
        "new/search/swiggy.py",
    ]

    # Create a pool of workers
    with multiprocessing.Pool(processes=len(scripts)) as pool:
        # Map the scraper function to the list of scripts
        pool.starmap(run_scraper, [(script, product_name) for script in scripts])

    print(f"Scraping completed for '{product_name}' across all platforms!")