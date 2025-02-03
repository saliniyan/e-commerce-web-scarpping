from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import json
import time

def setup_driver():
    """Initialize Firefox WebDriver with options"""
    firefox_options = Options()
    # Uncomment for headless mode
    # firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def scrape_blinkit_products(url, max_products=50):
    """Scrape product details from Blinkit"""
    driver = setup_driver()
    products = []
    
    try:
        driver.get(url)
        
        # Wait for product elements to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5"))
        )
        
        while len(products) < max_products:
            product_cards = driver.find_elements(By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5")
            
            for card in product_cards:
                if len(products) >= max_products:
                    break
                
                product = {}
                try:
                    # Extract product name
                    product['name'] = card.find_element(By.CLASS_NAME, "Product__UpdatedTitle-sc-11dk8zk-9").text
                    
                    # Extract price
                    product['price'] = card.find_element(By.CLASS_NAME, "Product__UpdatedPriceAndAtcContainer-sc-11dk8zk-10").text.split("\n")[0]
                    
                    # Extract quantity (weight)
                    product['quantity'] = card.find_element(By.CLASS_NAME, "bff_variant_text_only").text
                    
                    # Extract ETA (estimated delivery time)
                    product['eta'] = card.find_element(By.CLASS_NAME, "Product__UpdatedETAContainer-sc-11dk8zk-6").text.strip()
                    
                    # Extract image URL
                    try:
                        img_element = card.find_element(By.CSS_SELECTOR, "img")
                        product['image_url'] = img_element.get_attribute("src") if img_element else "N/A"
                    except:
                        product['image_url'] = "N/A"

                    products.append(product)

                except Exception as e:
                    print(f"Error extracting product details: {e}")
                    continue
            
            # Scroll down to load more products
            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(3)  # Allow time for new products to load

    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()
    
    # Save data to JSON
    with open('blinkit_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    return products

if __name__ == "__main__":
    blinkit_url = "https://blinkit.com/cn/chicken/cid/4/1362"
    results = scrape_blinkit_products(blinkit_url)

    if results:
        print(f"Successfully scraped {len(results)} products")
        print("Results have been saved to 'blinkit_products.json'")
    else:
        print("Scraping failed")
