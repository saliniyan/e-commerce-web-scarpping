import json
import time
import multiprocessing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from urllib.parse import quote
from concurrent.futures import ProcessPoolExecutor

def setup_driver():
    """Initialize Firefox WebDriver with headless options."""
    firefox_options = Options()
    firefox_options.add_argument('--headless')
    return webdriver.Firefox(options=firefox_options)

def get_product_image(card):
    """Extract high-quality product image URL."""
    try:
        return card.find_element(By.CSS_SELECTOR, "img").get_attribute("src")
    except:
        return None

def get_stock_status(card):
    """Check if product is in stock."""
    try:
        return "No" if card.find_elements(By.CSS_SELECTOR, "div.bg-opacity-50") else "Yes"
    except:
        return "Unknown"

def get_ratings_info(card):
    """Extract ratings and review count."""
    try:
        ratings_div = card.find_element(By.CLASS_NAME, "ReviewsAndRatings___StyledDiv-sc-2rprpc-0")
        rating = float(ratings_div.find_element(By.CSS_SELECTOR, "span.Label-sc-15v1nk5-0.Badges___StyledLabel-sc-1k3p1ug-0 span").text)
        review_count = ratings_div.find_element(By.CLASS_NAME, "ReviewsAndRatings___StyledLabel-sc-2rprpc-1").text
        return {'rating': rating, 'review_count': review_count}
    except:
        return {'rating': 0.0, 'review_count': "0 Ratings"}

def extract_price_info(card):
    """Extract price information."""
    try:
        price_div = card.find_element(By.CLASS_NAME, "Pricing___StyledDiv-sc-pldi2d-0")
        new_price = float(price_div.find_element(By.CLASS_NAME, "Pricing___StyledLabel-sc-pldi2d-1").text.replace('₹', '').strip())
        old_price = None
        try:
            old_price = float(price_div.find_element(By.CLASS_NAME, "Pricing___StyledLabel2-sc-pldi2d-2").text.replace('₹', '').strip())
        except:
            pass
        return new_price, old_price
    except:
        return None, None

def extract_discount(card):
    """Extract discount percentage."""
    try:
        return card.find_element(By.CSS_SELECTOR, "span.font-semibold.leading-xxl").text.strip()
    except:
        return "No discount"

def scroll_to_load_products(driver):
    """Scroll dynamically to load all products."""
    previous_height = 0
    while True:
        product_cards = driver.find_elements(By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0")
        if not product_cards:
            break
        driver.execute_script("arguments[0].scrollIntoView();", product_cards[-1])
        time.sleep(2)
        if len(product_cards) == previous_height:
            break
        previous_height = len(product_cards)

def generate_bigbasket_url(product_name):
    """Generate BigBasket search URL from product name."""
    return f"https://www.bigbasket.com/ps/?q={quote(product_name.replace(' ', '+'))}&nc=as"

def scrape_bigbasket_products(urls):
    """Scrape product details from BigBasket."""
    driver = setup_driver()
    products = []

    try:
        for name in urls:
            driver.get(generate_bigbasket_url(name))
            print(f"scraping: {name}")
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0"))
            )

            scroll_to_load_products(driver)
            product_cards = driver.find_elements(By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0")

            for card in product_cards:
                try:
                    new_price, old_price = extract_price_info(card)
                    product = {
                        'category': name,
                        'brand': card.find_element(By.CLASS_NAME, "BrandName___StyledLabel2-sc-hssfrl-1").text,
                        'name': card.find_element(By.CSS_SELECTOR, "h3.line-clamp-2").text,
                        'image_url': get_product_image(card),
                        'in_stock': get_stock_status(card),
                        'new_price': new_price,
                        'old_price': old_price,
                        'discount': extract_discount(card),
                        'pack_size': None,
                        'special_offer': None,
                        'product_url': None
                    }

                    try:
                        product['product_url'] = card.find_element(By.TAG_NAME, "a").get_attribute("href")
                    except:
                        pass

                    try:
                        product['pack_size'] = card.find_element(By.CLASS_NAME, "PackSelector___StyledLabel-sc-1lmu4hv-0").text.strip()
                    except:
                        pass

                    try:
                        product['special_offer'] = card.find_element(By.CLASS_NAME, "OfferCommunication___StyledDiv-sc-zgmi5i-0").text.strip()
                    except:
                        pass

                    product.update(get_ratings_info(card))
                    products.append(product)

                except:
                    pass  # Skip product if error occurs
    except:
        pass  # Skip category if error occurs
    finally:
        driver.quit()

    return products

def process_scraping(urls, output_file):
    """Runs scraping on a list of URLs and saves the results."""
    products = scrape_bigbasket_products(urls)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def main():
    """Main function to execute scraping process."""
    try:
        with open('new/product_links/product_details.json', 'r') as f:
            category_links = [item["name"] for item in json.load(f)]
    except:
        return

    category_links = category_links[:100]
    num_processes = 3
    chunk_size = max(1, len(category_links) // num_processes)
    chunks = [category_links[i:i + chunk_size] for i in range(0, len(category_links), chunk_size)]

    manager = multiprocessing.Manager()
    results_list = manager.list()

    processes = []
    for chunk in chunks:
        p = multiprocessing.Process(
            target=lambda q, urls: q.append(scrape_bigbasket_products(urls)), 
            args=(results_list, chunk)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    all_products = [product for sublist in results_list for product in sublist]
    output_file = 'new/big_products.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)
        print(f"Total products scraped: {len(all_products)}")

if __name__ == "__main__":
    main()
