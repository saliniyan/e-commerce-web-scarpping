import json
import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from urllib.parse import quote

def setup_driver():
    """Initialize Firefox WebDriver with headless options."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    firefox_options.add_argument('--disable-gpu')
    firefox_options.add_argument('--no-sandbox')
    firefox_options.add_argument('--disable-dev-shm-usage')
    firefox_options.set_preference('permissions.default.image', 2)
    return webdriver.Firefox(options=firefox_options)

def get_product_image(card):
    """Extract product image URL."""
    try:
        img_element = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-image']")
        return (
            img_element.get_attribute("srcset") or
            img_element.get_attribute("data-src") or
            img_element.get_attribute("src")
        )
    except:
        return None

def get_discount(card):
    """Extract discount details."""
    try:
        discount_element = card.find_element(By.CSS_SELECTOR, ".absolute.top-0.text-center.font-title.text-white")
        return discount_element.text.strip()
    except:
        return "No discount"

def get_stock_status(card):
    """Check if the product is in stock."""
    try:
        stock_element = card.find_elements(By.CLASS_NAME, "bg-opacity-50")
        return "No" if stock_element else "Yes"
    except:
        return "Unknown"

def get_product_link(card, driver):
    """Extract product link using JavaScript execution."""
    try:
        product_name = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-name']").text
        product_url = driver.execute_script(
            "return arguments[0].closest('a')?.href;", card
        )
        if not product_url:
            # Construct URL if not found using data attributes
            product_url = f"https://www.zeptonow.com/search?query={quote(product_name.replace(' ', '+'))}"
        return product_url
    except Exception as e:
        return None


def extract_price_info(card):
    """Extract new and old prices."""
    try:
        new_price = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-price']").text
        try:
            old_price = card.find_element(By.CSS_SELECTOR, ".line-through").text
        except:
            old_price = None
        
        # Convert prices to float, removing '₹' symbol
        new_price = float(new_price.replace('₹', '').strip()) if new_price else None
        old_price = float(old_price.replace('₹', '').strip()) if old_price else None
        
        return new_price, old_price
    except:
        return None, None

def scroll_to_load_products(driver):
    """Scroll dynamically to load all products."""
    previous_height = 0
    while True:
        product_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")
        if not product_cards:
            break
        driver.execute_script("arguments[0].scrollIntoView();", product_cards[-1])
        time.sleep(2)
        if len(product_cards) == previous_height:
            break
        previous_height = len(product_cards)

def scrape_zepto_products(urls):
    """Main scraping function."""
    driver = setup_driver()
    products = []

    try:
        for name in urls:
            try:
                url = f"https://www.zeptonow.com/search?query={quote(name.replace(' ', '+'))}"
                driver.get(url)
                print(f"Scraping: {name}")
                
                try:
                    WebDriverWait(driver, 15).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='product-card']"))
                    )
                except:
                    continue

                scroll_to_load_products(driver)
                product_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")

                if not product_cards:
                    continue

                for card in product_cards[:60]:  # Limit to first 40 products per category
                    try:
                        new_price, old_price = extract_price_info(card)
                        
                        product = {
                            'category': name,
                            'name': card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-name']").text,
                            'image_url': get_product_image(card),
                            'product_url': get_product_link(card, driver),
                            'quantity': card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-quantity']").text,
                            'new_price': new_price,
                            'old_price': old_price,
                            'discount': get_discount(card),
                            'in_stock': get_stock_status(card)
                        }

                        products.append(product)

                    except Exception as e:
                        continue

            except Exception as e:
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
    return scrape_zepto_products(chunk)

def main():
    try:
        # Load category links
        with open('new/product_links/product_details.json', 'r') as f:
            category_links = [item["name"] for item in json.load(f)]
    except Exception as e:
        return

    # Select range of categories to scrape (adjust as needed)
    category_links = category_links[:1]  # First 6 categories
    output_file = 'new/zepto_products.json'

    # Configure multiprocessing
    num_processes = 3
    chunk_size = max(1, len(category_links) // num_processes)
    chunks = [category_links[i:i + chunk_size] for i in range(0, len(category_links), chunk_size)]

    # Execute scraping with multiple processes
    with multiprocessing.Pool(num_processes) as pool:
        results = pool.map(scrape_wrapper, chunks)

    # Combine and save results
    all_products = [product for sublist in results for product in sublist]
    save_products(all_products, output_file)
    print(f"Total products scraped: {len(all_products)}")
    print(f"Products saved to: {output_file}")

if __name__ == "__main__":
    main()