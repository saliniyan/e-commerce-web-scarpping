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

def scrape_bigbasket_products(url, max_products=50):
    """Scrape product details from BigBasket"""
    driver = setup_driver()
    products = []
    
    try:
        driver.get(url)
        
        # Wait for product elements to appear
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0"))
        )
        
        while len(products) < max_products:
            product_cards = driver.find_elements(By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0")
            
            for card in product_cards:
                if len(products) >= max_products:
                    break
                
                product = {}
                try:
                    # Extract product name
                    product['name'] = card.find_element(By.CSS_SELECTOR, 'h3 a span').text
                    
                    # Extract price
                    product['price'] = card.find_element(By.CLASS_NAME, 'Pricing___StyledLabel-sc-pldi2d-1').text
                    
                    # Extract quantity (pack size) - Handle missing element
                    try:
                        product['pack_size'] = card.find_element(By.CLASS_NAME, 'PackSelector___StyledLabel-sc-1lmu4hv-0').text
                    except:
                        product['pack_size'] = "N/A"  # Default if not found
                    
                    # Extract discount (if available)
                    try:
                        product['discount'] = card.find_element(By.CLASS_NAME, 'Tags___StyledLabel-sc-aeruf4-0').text
                    except:
                        product['discount'] = "No discount"
                    
                    # Extract image URL
                    try:
                        img_element = card.find_element(By.CSS_SELECTOR, 'img')
                        product['image_url'] = img_element.get_attribute("src") if img_element else "N/A"
                    except:
                        product['image_url'] = "N/A"
                    
                    # Extract product link
                    try:
                        link_element = card.find_element(By.TAG_NAME, "a")
                        product['product_url'] = link_element.get_attribute("href")
                    except:
                        product['product_url'] = "N/A"
                    
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
    with open('bigbasket_products.json', 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

    return products


if __name__ == "__main__":
    bigbasket_url = "https://www.bigbasket.com/cl/electronics/earbuds/"
    results = scrape_bigbasket_products(bigbasket_url)

    if results:
        print(f"Successfully scraped {len(results)} products")
        print("Results have been saved to 'bigbasket_products.json'")
    else:
        print("Scraping failed")
