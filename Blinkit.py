import json
import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options

def setup_driver():
    """Initialize Firefox WebDriver with headless options."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')  # Run without opening a window
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def extract_category_from_url(url):
    """Extract product category from Blinkit URL."""
    try:
        category = url.split('/cn/')[1].split('/')[0]
        return category
    except Exception:
        return "Unknown"

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

def scroll_down(driver, max_scrolls=5):
    """Scrolls the page progressively to load all products."""
    for _ in range(max_scrolls):
        driver.execute_script("window.scrollBy(0, 600);")
        time.sleep(1.5)  # Allow time for images to load

def scrape_blinkit_products(urls):
    driver = setup_driver()
    products = []
    try:
        for url in urls:
            print(f"Scraping: {url}")
            category = extract_category_from_url(url)
            driver.get(url)
            
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "Product__UpdatedDetailContainer-sc-11dk8zk-5"))
            )

            # Scroll to load more products
            scroll_down(driver)

            product_cards = driver.find_elements(By.CSS_SELECTOR, "a[data-test-id='plp-product']")

            for card in product_cards:
                try:
                    product_url = card.get_attribute('href')
                    image_url = get_high_quality_image(card)
                    name = card.find_element(By.CLASS_NAME, "Product__UpdatedTitle-sc-11dk8zk-9").text
                    weight = card.find_element(By.CLASS_NAME, "bff_variant_text_only").text

                    # Extract price information
                    price_container = card.find_element(By.CLASS_NAME, "Product__UpdatedPriceAndAtcContainer-sc-11dk8zk-10")
                    price_elements = price_container.find_elements(By.CSS_SELECTOR, "div[style*='color']")
                    
                    new_price, old_price = "", ""
                    for price in price_elements:
                        style = price.get_attribute('style')
                        if 'text-decoration-line: line-through' in style:
                            old_price = price.text
                        elif 'color: rgb(31, 31, 31)' in style:
                            new_price = price.text

                    # Calculate discount
                    discount = ''
                    if old_price and new_price:
                        try:
                            old_price_value = float(old_price.replace('₹', '').strip())
                            new_price_value = float(new_price.replace('₹', '').strip())
                            discount = f"{round(((old_price_value - new_price_value) / old_price_value) * 100)}%"
                        except ValueError:
                            pass

                    # Stock status
                    out_of_stock = len(card.find_elements(By.CLASS_NAME, "AddToCart__UpdatedOutOfStockTag-sc-17ig0e3-4")) > 0
                    in_stock = 'No' if out_of_stock else 'Yes'

                    product = {
                        'category': category,
                        'name': name,
                        'image_url': image_url,
                        'product_url': product_url,
                        'weight': weight,
                        'new_price': new_price,
                        'old_price': old_price,
                        'discount': discount,
                        'in_stock': in_stock
                    }

                    if product not in products:
                        products.append(product)

                except Exception as e:
                    continue

    except Exception as e:
        pass
    finally:
        driver.quit()
    print(f"Total products scraped: {len(products)}")
    return products

def process_scraping(urls, output_file):
    """Runs scraping on a list of URLs and saves the results."""
    products = scrape_blinkit_products(urls)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def main():
    try:
        with open('category/blinkit_category_links.json', 'r') as f:
            category_links = json.load(f)
    except Exception as e:
        print(f"Failed to load category links: {e}")
        return

    # Limit the number of categories to scrape for testing
    category_links = category_links[:10]

    num_processes = 2  # Adjust based on system capabilities
    chunk_size = len(category_links) // num_processes
    chunks = [category_links[i:i + chunk_size] for i in range(0, len(category_links), chunk_size)]

    processes = []
    for i, chunk in enumerate(chunks):
        output_file = f'frontend/public/blinkit_products_part_{i+1}.json'
        p = multiprocessing.Process(target=process_scraping, args=(chunk, output_file))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

if __name__ == "__main__":
    main()
