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
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def get_product_image(card):
    """Extract high-quality product image URL."""
    try:
        img_element = card.find_element(By.CSS_SELECTOR, "img")
        return img_element.get_attribute("src")
    except:
        return None

def get_stock_status(card):
    """Check if product is in stock."""
    try:
        unavailable = card.find_elements(By.CSS_SELECTOR, "div.bg-opacity-50")
        return "No" if unavailable else "Yes"
    except:
        return "Unknown"

def get_ratings_info(card):
    """Extract ratings and review count."""
    try:
        ratings_div = card.find_element(By.CLASS_NAME, "ReviewsAndRatings___StyledDiv-sc-2rprpc-0")
        rating = ratings_div.find_element(By.CSS_SELECTOR, "span.Label-sc-15v1nk5-0.Badges___StyledLabel-sc-1k3p1ug-0 span").text
        review_count = ratings_div.find_element(By.CLASS_NAME, "ReviewsAndRatings___StyledLabel-sc-2rprpc-1").text
        return {
            'rating': float(rating),
            'review_count': review_count
        }
    except:
        return {
            'rating': 0.0,
            'review_count': "0 Ratings"
        }

def extract_price_info(card):
    """Extract price information with improved error handling."""
    try:
        price_div = card.find_element(By.CLASS_NAME, "Pricing___StyledDiv-sc-pldi2d-0")
        
        # Extract new price
        new_price_elem = price_div.find_element(By.CLASS_NAME, "Pricing___StyledLabel-sc-pldi2d-1")
        new_price = float(new_price_elem.text.replace('₹', '').strip())
        
        # Extract old price (optional)
        try:
            old_price_elem = price_div.find_element(By.CLASS_NAME, "Pricing___StyledLabel2-sc-pldi2d-2")
            old_price = float(old_price_elem.text.replace('₹', '').strip())
        except:
            old_price = None
        
        return new_price, old_price
    
    except Exception as e:
        return None, None

def extract_discount(card):
    """Extract discount percentage."""
    try:
        discount_elem = card.find_element(By.CSS_SELECTOR, "span.font-semibold.leading-xxl")
        return discount_elem.text.strip()
    except Exception as e:
        return "No discount"

def scroll_to_load_products(driver):
    """Scroll dynamically to load all products by scrolling the last product into view."""
    previous_height = 0
    while True:
        product_cards = driver.find_elements(By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0")
        if not product_cards:
            break  # Exit if no products found

        last_product = product_cards[-1]
        driver.execute_script("arguments[0].scrollIntoView();", last_product)
        time.sleep(2)  # Wait for new products to load

        new_height = len(product_cards)
        if new_height == previous_height:
            break  # Stop scrolling if no new products loaded
        previous_height = new_height

def generate_bigbasket_url(product_name):
    """Generate BigBasket search URL from product name."""
    encoded_name = quote(product_name.replace(" ", "+"))
    return f"https://www.bigbasket.com/ps/?q={encoded_name}&nc=as"

def scrape_bigbasket_products(urls):
    """Scrape product details from BigBasket."""
    driver = setup_driver()
    products = []
    
    try:
        for name in urls:
            url = generate_bigbasket_url(name)
            print(f"Scraping: {url}")
            category = name
            driver.get(url)
            
            # Wait for product elements to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0"))
            )

            # Scroll to load all products
            scroll_to_load_products(driver)

            product_cards = driver.find_elements(By.CLASS_NAME, "SKUDeck___StyledDiv-sc-1e5d9gk-0")

            for card in product_cards:
                try:
                    # Extract price information
                    new_price, old_price = extract_price_info(card)
                    
                    # Base product details
                    product = {
                        'category': category,
                        'brand': card.find_element(By.CLASS_NAME, "BrandName___StyledLabel2-sc-hssfrl-1").text,
                        'name': card.find_element(By.CSS_SELECTOR, "h3.line-clamp-2").text,
                        'image_url': get_product_image(card),
                        'in_stock': get_stock_status(card),
                        'new_price': new_price,
                        'old_price': old_price,
                        'discount': extract_discount(card)
                    }

                    # Extract URL
                    try:
                        link = card.find_element(By.TAG_NAME, "a")
                        product['product_url'] = link.get_attribute("href")
                    except:
                        product['product_url'] = None

                    # Extract pack size
                    try:
                        product['pack_size'] = card.find_element(
                            By.CLASS_NAME, "PackSelector___StyledLabel-sc-1lmu4hv-0"
                        ).text.strip()
                    except:
                        product['pack_size'] = "N/A"

                    # Get ratings information
                    ratings_info = get_ratings_info(card)
                    product.update(ratings_info)

                    # Special offers/tags
                    try:
                        offer = card.find_element(By.CLASS_NAME, "OfferCommunication___StyledDiv-sc-zgmi5i-0")
                        product['special_offer'] = offer.text.strip()
                    except:
                        product['special_offer'] = None

                    if product not in products:
                        products.append(product)

                except Exception as e:
                    print(f"Error processing product card: {e}")
                    continue

    except Exception as e:
        pass
    finally:
        driver.quit()
        
    print(f"Total products scraped: {len(products)}")
    return products

def process_scraping(urls, output_file):
    """Runs scraping on a list of URLs and saves the results."""
    products = scrape_bigbasket_products(urls)
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(products, f, ensure_ascii=False, indent=2)

def main():
    try:
        with open('new/product_links/product_details.json', 'r') as f:
            category = json.load(f)
            category_links = [item["name"] for item in category]
    except Exception as e:
        print(f"Failed to load category links: {e}")
        return

    # Limit categories for testing
    category_links = category_links[:1]

    num_processes = 1
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
    output_file = 'new/frontend/public/big_products.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_products, f, ensure_ascii=False, indent=2)

    print(f"Total products saved: {len(all_products)}")

if __name__ == "__main__":
    main()