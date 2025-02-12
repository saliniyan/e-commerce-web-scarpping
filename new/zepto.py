import json
import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import urllib.parse

def setup_driver():
    """Initialize Firefox WebDriver with headless options."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')  # Run without opening a window
    return webdriver.Firefox(options=firefox_options)

def convert_to_zepto_search_url(product_name):
    """Convert product name to Zepto search URL."""
    base_url = "https://www.zeptonow.com/search?query="
    return base_url + urllib.parse.quote(product_name)

def scroll_to_load_products(driver):
    """Scroll dynamically to load all products on the page."""
    previous_height = 0
    while True:
        product_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")
        if not product_cards:
            break  # Exit if no products found

        last_product = product_cards[-1]
        driver.execute_script("arguments[0].scrollIntoView();", last_product)
        time.sleep(2)  # Allow content to load

        new_height = len(product_cards)
        if new_height == previous_height:
            break  # Stop scrolling if no new products loaded
        previous_height = new_height

def get_product_image(card):
    """Extract product image URL."""
    try:
        img_element = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-image']")
        return img_element.get_attribute('src')
    except:
        return None

def get_discount(card):
    """Extract discount details."""
    try:
        discount_element = card.find_element(By.CSS_SELECTOR, ".absolute.top-0.text-center.font-title.text-white")
        return discount_element.text
    except:
        return "No discount"

def get_original_price(card):
    """Extract original (strikethrough) price if available."""
    try:
        return card.find_element(By.CSS_SELECTOR, ".line-through").text
    except:
        return None

def get_stock_status(card):
    """Check if the product is in stock."""
    try:
        stock_element = card.find_elements(By.CLASS_NAME, "bg-opacity-50")
        return "No" if stock_element else "Yes"
    except:
        return "Unknown"

def get_product_link(card):
    """Extract product link correctly."""
    try:
        # Find the 'Add to Cart' button and get its parent anchor tag
        link_element = card.find_element(By.XPATH, ".//button[@data-testid='product-card-add-btn']/ancestor::a")
        return link_element.get_attribute('href') if link_element else None
    except:
        return None

def scrape_zepto_products(urls, shared_products):
    """Scrape product details from Zepto search results."""
    driver = setup_driver()
    
    try:
        for product_name in urls:
            category=product_name
            url = convert_to_zepto_search_url(product_name)
            print(f"Scraping: {url}")
            driver.get(url)
            
            # Wait for product elements to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='product-card']"))
            )

            # Scroll to load all products
            scroll_to_load_products(driver)

            product_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")
            for card in product_cards:
                try:
                    product = {
                        'category': category,
                        'name': card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-name']").text,
                        'price': card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-price']").text,
                        'quantity': card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-quantity']").text,
                        'discount': get_discount(card),
                        'original_price': get_original_price(card),
                        'image_url': get_product_image(card),
                        'in_stock': get_stock_status(card),
                        'product_link': get_product_link(card)  # Extracted product link
                    }
                    shared_products.append(product)
                
                except Exception as e:
                    print(f"Error extracting product details: {e}")
                    continue
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    print(f"Total products scraped: {len(shared_products)}")

def process_scraping(urls, shared_products):
    """Runs scraping on a list of product names and saves all results in a single file."""
    scrape_zepto_products(urls, shared_products)

def main():
    try:
        with open('new/product_links/product_details.json', 'r') as f:
            category = json.load(f)
            product_names = [item["name"] for item in category]
            product_names=product_names[:1]
    except Exception as e:
        print(f"Failed to load product names: {e}")
        return

    num_processes = 1  # Adjust based on system capabilities
    manager = multiprocessing.Manager()
    shared_products = manager.list()

    chunk_size = len(product_names) // num_processes
    chunks = [product_names[i:i + chunk_size] for i in range(0, len(product_names), chunk_size)]

    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(target=process_scraping, args=(chunk, shared_products))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    # Save all scraped products to one file
    with open('new/frontend/public/zepto_products.json', 'w', encoding='utf-8') as f:
        json.dump(list(shared_products), f, ensure_ascii=False, indent=2)

    print(f"All products saved to 'new/frontend/public/zepto_products.json'")

if __name__ == "__main__":
    main()
