from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import json

def setup_driver():
    """Set up the Firefox webdriver with headless mode for efficiency."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')  # Run in headless mode
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def extract_category_from_url(url):
    """Extract category from Zepto URL."""
    try:
        parts = url.split('/cn/')[-1].split('/cid/')[0].split('/')
        category = parts[-1] if parts else "Unknown"
        return category.replace("-", " ").title()
    except Exception:
        return "Unknown"

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
    """Extract product link if available."""
    try:
        link_element = card.find_element(By.CSS_SELECTOR, "a")
        return link_element.get_attribute('href') if link_element else None
    except:
        return None

def scrape_zepto_products(urls):
    """Scrape product details from Zepto."""
    driver = setup_driver()
    products = []
    
    try:
        for url in urls:
            print(f"Scraping: {url}")
            category = extract_category_from_url(url)
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
                    products.append(product)
                
                except Exception as e:
                    print(f"Error extracting product details: {e}")
                    continue
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        driver.quit()

    print(f"Total products scraped: {len(products)}")
    return products

def main():
    urls = [
        "https://www.zeptonow.com/cn/dairy-bread-eggs/cheese/cid/4b938e02-7bde-4479-bc0a-2b54cb6bd5f5/scid/f594b28a-4775-48ac-8840-b9030229ff87"
    ]

    results = scrape_zepto_products(urls)

    if results:
        with open('zepto_products.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        print(f"Successfully scraped {len(results)} products")
        print("Results have been saved to 'zepto_products.json'")

if __name__ == "__main__":
    main()
