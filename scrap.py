from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import json

def setup_driver():
    """Set up the Firefox webdriver with appropriate options"""
    firefox_options = Options()
    # Uncomment the line below if you want to run in headless mode
    # firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def scrape_products(url):
    """Scrape product information from the given Zepto URL"""
    driver = setup_driver()
    products = []
    
    try:
        driver.get(url)
        # Wait for the products to load
        time.sleep(5)  # Allow dynamic content to load
        
        # Find all product cards
        product_cards = driver.find_elements(By.CSS_SELECTOR, "[data-testid='product-card']")
        
        for card in product_cards:
            product = {}
            
            try:
                # Extract product name
                product['name'] = card.find_element(
                    By.CSS_SELECTOR, "[data-testid='product-card-name']"
                ).text
                
                # Extract price
                price_element = card.find_element(
                    By.CSS_SELECTOR, "[data-testid='product-card-price']"
                )
                product['price'] = price_element.text
                
                # Extract quantity
                quantity_element = card.find_element(
                    By.CSS_SELECTOR, "[data-testid='product-card-quantity']"
                )
                product['quantity'] = quantity_element.text
                
                # Try to extract discount if available
                try:
                    discount_element = card.find_element(
                        By.CSS_SELECTOR, ".absolute.top-0.text-center.font-title.text-white"
                    )
                    product['discount'] = discount_element.text
                except:
                    product['discount'] = "No discount"
                
                # Try to extract original price if available
                try:
                    original_price = card.find_element(
                        By.CSS_SELECTOR, ".line-through"
                    ).text
                    product['original_price'] = original_price
                except:
                    product['original_price'] = None
                
                # Extract image URL
                try:
                    img_element = card.find_element(By.CSS_SELECTOR, "[data-testid='product-card-image']")
                    product['image_url'] = img_element.get_attribute('src')
                except:
                    product['image_url'] = None
                
                products.append(product)
                
            except Exception as e:
                print(f"Error extracting product details: {str(e)}")
                continue
        
        # Save results to a JSON file
        with open('zepto_products.json', 'w', encoding='utf-8') as f:
            json.dump(products, f, ensure_ascii=False, indent=2)
            
        return products
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None
        
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.zeptonow.com/cn/dairy-bread-eggs/cheese/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/f594b28a-4775-48ac-8840-b9030229ff87"
    results = scrape_products(url)
    
    if results:
        print(f"Successfully scraped {len(results)} products")
        print("Results have been saved to 'zepto_products.json'")
    else:
        print("Scraping failed")