import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

def setup_driver():
    """Initialize Firefox WebDriver with options"""
    firefox_options = Options()
    # Uncomment for headless mode
    # firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def extract_category_from_url(url):
    """Extract category from Blinkit URL"""
    try:
        category = url.split('/cn/')[1].split('/')[0]
        return category
    except Exception:
        return "Unknown"

def scrape_blinkit_products(url, max_products=1000):
    driver = setup_driver()
    products = []
    category = extract_category_from_url(url)
    
    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5"))
        )
        
        # More efficient scrolling strategy
        last_height = driver.execute_script("return document.body.scrollHeight")
        
        while len(products) < max_products:
            # Find current page products
            product_cards = driver.find_elements(By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5")
            
            for card in product_cards[:max_products - len(products)]:
                try:
                    product = {
                        'category': category,
                        'name': card.find_element(By.CLASS_NAME, "Product__UpdatedTitle-sc-11dk8zk-9").text,
                        'price': card.find_element(By.CLASS_NAME, "Product__UpdatedPriceAndAtcContainer-sc-11dk8zk-10").text.split("\n")[0],
                        'quantity': card.find_element(By.CLASS_NAME, "bff_variant_text_only").text,
                        'eta': card.find_element(By.CLASS_NAME, "Product__UpdatedETAContainer-sc-11dk8zk-6").text.strip(),
                        'image_url': card.find_element(By.CSS_SELECTOR, "img").get_attribute("src") or "N/A"
                    }
                    products.append(product)
                except Exception:
                    continue
            
            # Scroll down to trigger more content
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # Check new height
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    
    except Exception as e:
        print(f"Scraping error: {e}")
    finally:
        driver.quit()
    
    return products

def main():
    # Load category links
    try:
        with open('e-commerce-web-scarpping/category/blinkit_category_links.json', 'r') as f:
            category_links = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading links: {e}")
        return

    all_products = []
    for url in category_links[:1]:
        print(f"Scraping: {url}")
        category_products = scrape_blinkit_products(url)
        all_products.extend(category_products)
        
        if len(all_products) > 10000:
            break

    # Save results
    with open('e-commerce-web-scarpping/frontend/public/blinkit_multi_category_products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"Total products scraped: {len(all_products)}")

if __name__ == "__main__":
    main()