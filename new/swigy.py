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
    options = Options()
    options.add_argument('--headless')  # Keep headless mode
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    # Force image loading in headless mode
    options.set_preference('permissions.default.image', 1)

    return webdriver.Firefox(options=options)


def scroll_to_load_products(driver, max_scrolls=10):
    """Scroll page to load all products and images."""
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(max_scrolls):
        driver.execute_script("window.scrollBy(0, 600);")  # Scroll step by step
        time.sleep(2)  # Allow images to load
        new_height = driver.execute_script("return document.body.scrollHeight")

        if new_height == last_height:
            break
        last_height = new_height


def extract_product_image(container):
    """Extract product image URL and alt text."""
    img_url, img_alt = None, None
    try:
        # Locate image using multiple strategies
        img_selectors = [
            'img.sc-iGgWBj.bnWvUc._1NxA5',  # Common class pattern
            'img[class*="bnWvUc"]',  # Partial class match
            'img[src*="media-assets.swiggy.com"]'  # URL-based matching
        ]
        
        for selector in img_selectors:
            try:
                img_element = container.find_element(By.CSS_SELECTOR, selector)
                img_url = img_element.get_attribute('src')
                img_alt = img_element.get_attribute('alt')
                
                if img_url:
                    # Fix URL issues
                    img_url = img_url.replace('fl*lossy', 'fl_lossy')
                    break  # Stop if a valid image is found
            except:
                continue
        
    except Exception as e:
        pass
    
    return img_url, img_alt

def extract_product_details(container):
    """Extract all available product details from a container."""
    product = {}
    try:
        # Name extraction
        try:
            product['name'] = container.find_element(By.CSS_SELECTOR, 'div[class*="novMV"], div[class*="styles_item"]').text.strip()
        except:
            return None  # Skip if no name found as it's essential
        
        product['image_url'], product['image_alt'] = extract_product_image(container)

        # Discount
        try:
            discount_selectors = [
                '[data-testid="item-offer-label-discount-text"]',
                'div[class*="styles_offer"]',
                'span[class*="discount"]'
            ]
            for selector in discount_selectors:
                try:
                    discount_element = container.find_element(By.CSS_SELECTOR, selector)
                    product['discount'] = discount_element.text.strip()
                    break
                except:
                    continue
            if 'discount' not in product:
                product['discount'] = "No discount"
        except:
            product['discount'] = "No discount"

        # Delivery time
        try:
            delivery_selectors = [
                'div[class*="GOJ8s"]',
                'div[class*="styles_delivery"]'
            ]
            for selector in delivery_selectors:
                try:
                    delivery_element = container.find_element(By.CSS_SELECTOR, selector)
                    product['delivery_time'] = delivery_element.text.strip()
                    break
                except:
                    continue
        except:
            product['delivery_time'] = None

        # Weight
        try:
            weight_selectors = [
                'div[class*="entQHA"]',
                'div[class*="styles_weight"]',
                'div[class*="weight"]'
            ]
            for selector in weight_selectors:
                try:
                    weight_element = container.find_element(By.CSS_SELECTOR, selector)
                    product['weight'] = weight_element.text.strip()
                    break
                except:
                    continue
        except:
            product['weight'] = None

        # Price
        try:
            price_selectors = [
                '[data-testid="itemMRPPrice"]',
                'div[class*="styles_price"]',
                'div[class*="price-container"]'
            ]
            for selector in price_selectors:
                try:
                    price_container = container.find_element(By.CSS_SELECTOR, selector)
                    
                    # New price
                    new_price_selectors = [
                        '[data-testid="itemOfferPrice"]',
                        'span[class*="discounted"]',
                        'div[class*="final"]'
                    ]
                    for new_selector in new_price_selectors:
                        try:
                            new_price_element = price_container.find_element(By.CSS_SELECTOR, new_selector)
                            price_text = new_price_element.get_attribute('aria-label') or new_price_element.text
                            product['new_price'] = float(price_text.replace('₹', '').replace(',', '').strip())
                            break
                        except:
                            continue
                    
                    # Old price
                    old_price_selectors = [
                        'div[class*="JZGfZ"]',
                        'span[class*="original"]',
                        'div[class*="strike"]'
                    ]
                    for old_selector in old_price_selectors:
                        try:
                            old_price_element = price_container.find_element(By.CSS_SELECTOR, old_selector)
                            price_text = old_price_element.get_attribute('aria-label') or old_price_element.text
                            product['old_price'] = float(price_text.replace('₹', '').replace(',', '').strip())
                            break
                        except:
                            continue
                    
                    break
                except:
                    continue
        except:
            product['new_price'] = None
            product['old_price'] = None

        # Stock status
        try:
            out_of_stock = container.find_elements(By.XPATH, ".//*[contains(text(), 'Out of stock') or contains(text(), 'Sold out')]")
            product['in_stock'] = 'No' if out_of_stock else 'Yes'
        except:
            product['in_stock'] = "Unknown"

        # Advertisement status
        try:
            ad_selectors = [
                '[data-testid="badge-wrapper"]',
                'div[class*="ad-badge"]'
            ]
            is_ad = False
            for selector in ad_selectors:
                try:
                    ad_element = container.find_element(By.CSS_SELECTOR, selector)
                    if ad_element.text.strip().lower() == "ad":
                        is_ad = True
                        break
                except:
                    continue
            product['is_advertisement'] = is_ad
        except:
            product['is_advertisement'] = False

    except Exception as e:
        return None

    return product
    return product

def scrape_swiggy_instamart_products(urls):
    """Main scraping function."""
    driver = setup_driver()
    products = []
    try:
        for name in urls:
            url = f"https://www.swiggy.com/instamart/search?location=chennai&custom_back=true&query={quote(name.replace(' ', '+'))}"
            driver.get(url)
            print(f"Scraping: {name}")

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="default_container_ux4"]'))
                )
            except:
                print(f"No results found for {name}")
                continue

            scroll_to_load_products(driver)
            product_containers = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="default_container_ux4"]')

            if not product_containers:
                print(f"No product containers found for: {name}")
                continue

            for container in product_containers[:40]:
                product = extract_product_details(container)
                if product:
                    product['category'] = name
                    product['product_url'] = url
                    product['scraped_at'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    products.append(product)
    
    finally:
        driver.quit()
    return products

def save_products(products, output_file):
    """Save products to JSON file."""
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
    return scrape_swiggy_instamart_products(chunk)

def main():
    try:
        with open('new/product_links/product_details.json', 'r') as f:
            category_links = [item["name"] for item in json.load(f)]
    except Exception as e:
        return

    category_links = category_links[:1]
    output_file = 'new/swiggy_instamart_products.json'
    num_processes = 1
    chunk_size = max(1, len(category_links) // num_processes)
    chunks = [category_links[i:i + chunk_size] for i in range(0, len(category_links), chunk_size)]
    
    with multiprocessing.Pool(num_processes) as pool:
        results = pool.map(scrape_wrapper, chunks)
    
    all_products = [product for sublist in results for product in sublist]
    save_products(all_products, output_file)
    print(f"Total products scraped: {len(all_products)}")
    print(f"Products saved to: {output_file}")

if __name__ == "__main__":
    main()
