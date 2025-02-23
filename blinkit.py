import json
import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from urllib.parse import quote
import sys

def setup_driver():
    """Initialize Firefox WebDriver with headless options."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.set_preference('permissions.default.image', 2)
    return webdriver.Firefox(options=firefox_options)

def get_high_quality_image(card):
    """Extracts high-quality product image from the card."""
    try:
        image_element = card.find_element(By.CSS_SELECTOR, "img")
        return (
            image_element.get_attribute("srcset") or
            image_element.get_attribute("data-src") or
            image_element.get_attribute("src")
        )
    except:
        return None

def get_stock_status(card):
    """Check if product is in stock."""
    try:
        out_of_stock = len(card.find_elements(By.CLASS_NAME, "AddToCart__UpdatedOutOfStockTag-sc-17ig0e3-4")) > 0
        return 'No' if out_of_stock else 'Yes'
    except:
        return "Unknown"

def extract_price_info(price_container):
    """Extract new and old prices from price container."""
    try:
        price_elements = price_container.find_elements(By.CSS_SELECTOR, "div[style*='color']")
        new_price, old_price = "", ""
        
        for price in price_elements:
            style = price.get_attribute('style')
            if 'text-decoration-line: line-through' in style:
                old_price = price.text.replace('₹', '').strip()
            elif 'color: rgb(31, 31, 31)' in style:
                new_price = price.text.replace('₹', '').strip()
        
        return float(new_price) if new_price else None, float(old_price) if old_price else None
    except:
        return None, None

def calculate_discount(new_price, old_price):
    """Calculate discount percentage."""
    try:
        if old_price and new_price:
            discount = ((old_price - new_price) / old_price) * 100
            return f"{round(discount)}%"
    except:
        pass
    return "No discount"

def scroll_to_load_products(driver, max_scrolls=10):
    """Scroll page to load all products."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    scrolls = 0
    
    while scrolls < max_scrolls:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1.5)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        scrolls += 1

def scrape_blinkit_products(urls):
    """Main scraping function."""
    driver = setup_driver()
    products = []

    try:
        for name in urls:
            try:
                url = f"https://blinkit.com/s/?q={quote(name.replace(' ', '+'))}"
                driver.get(url)
                print(f"Scraping: {name}")
                
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5"))
                    )
                except:
                    continue

                scroll_to_load_products(driver)
                product_cards = driver.find_elements(By.CSS_SELECTOR, "a[data-test-id='plp-product']")

                if not product_cards:
                    continue

                for card in product_cards[:40]:  # Limit to first 20 products per category
                    try:
                        price_container = card.find_element(By.CLASS_NAME, "Product__UpdatedPriceAndAtcContainer-sc-11dk8zk-10")
                        new_price, old_price = extract_price_info(price_container)
                        
                        product = {
                            'category': name,
                            'name': card.find_element(By.CLASS_NAME, "Product__UpdatedTitle-sc-11dk8zk-9").text,
                            'image_url': get_high_quality_image(card),
                            'product_url': card.get_attribute('href'),
                            'weight': card.find_element(By.CLASS_NAME, "bff_variant_text_only").text,
                            'new_price': new_price,
                            'old_price': old_price,
                            'discount': calculate_discount(new_price, old_price),
                            'in_stock': get_stock_status(card),
                            'special_offer': None
                        }

                        # Try to get special offer if available
                        try:
                            product['special_offer'] = card.find_element(By.CLASS_NAME, "OfferTag__StyledOfferTag-sc-1p5qqkx-0").text
                        except:
                            pass

                        products.append(product)

                    except Exception as e:
                        continue

            except Exception as e:
                pass
                continue

    except Exception as e:
        pass
    finally:
        driver.quit()

    return products

def save_products(products, output_file):
    """Save products to JSON file, appending to existing data."""
    try:
        with open(output_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    except:
        existing_data = []
    
    existing_data.extend(products)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

def scrape_wrapper(chunk):
    """Wrapper function for multiprocessing."""
    return scrape_blinkit_products(chunk)

def main(start_idx=0, end_idx=None):
    try:
        with open('/home/saliniyan/Documents/git_project/e-commerce/e-commerce-web-scarpping/new/product_links/product_details.json', 'r') as f:
            category_links = [item["name"] for item in json.load(f)]
    except Exception as e:
        print(f"Error loading category links: {e}")
        return

    # Slice category links based on input arguments
    category_links = category_links[start_idx:end_idx]
    
    output_file = 'blinkit_products.json'  # Change to 'new/big_products.json' for BigBasket

    num_processes = 3
    chunk_size = max(1, len(category_links) // num_processes)
    chunks = [category_links[i:i + chunk_size] for i in range(0, len(category_links), chunk_size)]

    with multiprocessing.Pool(num_processes) as pool:
        results = pool.map(scrape_wrapper, chunks)

    all_products = [product for sublist in results for product in sublist]
    save_products(all_products, output_file)
    print(f"Total products scraped: {len(all_products)}")
    print(f"Products saved to: {output_file}")

if __name__ == "__main__":
    # Read start and end indices from command-line arguments
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else None
    main(start_idx, end_idx)
