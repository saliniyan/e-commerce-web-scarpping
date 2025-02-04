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

def scrape_blinkit_products(url, max_products=10):
    """Scrape product details from Blinkit"""
    driver = setup_driver()
    products = []
    category = extract_category_from_url(url)

    try:
        driver.get(url)
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5"))
        )

        while len(products) < max_products:
            product_cards = driver.find_elements(By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5")
            for card in product_cards:
                if len(products) >= max_products:
                    break

                product = {'category': category}
                try:
                    product['name'] = card.find_element(By.CLASS_NAME, "Product__UpdatedTitle-sc-11dk8zk-9").text
                    product['price'] = card.find_element(By.CLASS_NAME, "Product__UpdatedPriceAndAtcContainer-sc-11dk8zk-10").text.split("\n")[0]
                    product['quantity'] = card.find_element(By.CLASS_NAME, "bff_variant_text_only").text
                    product['eta'] = card.find_element(By.CLASS_NAME, "Product__UpdatedETAContainer-sc-11dk8zk-6").text.strip()
                    
                    try:
                        img_element = card.find_element(By.CSS_SELECTOR, "img")
                        product['image_url'] = img_element.get_attribute("src") if img_element else "N/A"
                    except:
                        product['image_url'] = "N/A"

                    products.append(product)
                except:
                    continue

                time.sleep(0.5)  # Small delay to prevent overloading

            driver.execute_script("window.scrollBy(0, 600);")
            time.sleep(3)

    except Exception as e:
        print(f"Error scraping {url}: {e}")
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
    for url in category_links[:3]:
        print(f"Scraping: {url}")
        category_products = scrape_blinkit_products(url)
        all_products.extend(category_products)
        
        if len(all_products) >= 30:
            break

    # Save results
    with open('blinkit_multi_category_products.json', 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"Total products scraped: {len(all_products)}")

if __name__ == "__main__":
    main()