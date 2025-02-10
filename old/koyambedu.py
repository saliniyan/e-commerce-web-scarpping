from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import json
import re

class KoyambeduScraper:
    def __init__(self, headless=False):
        self.base_url = "https://www.koyambedumarket.in/shopproducts/chennai/koyambedu/retail/ee-614"
        self.firefox_options = Options()
        if headless:
            self.firefox_options.add_argument('--headless')
        self.driver = None
        
    def setup_driver(self):
        """Initialize the webdriver"""
        self.driver = webdriver.Firefox(options=self.firefox_options)
        
    def close_driver(self):
        """Close the webdriver"""
        if self.driver:
            self.driver.quit()
            
    def calculate_discount(self, current_price, original_price):
        """Calculate discount percentage"""
        try:
            current = float(current_price.replace('Rs.', '').strip())
            original = float(original_price.replace('Rs.', '').strip())
            discount = ((original - current) / original) * 100
            return round(discount, 2)
        except:
            return None
            
    def clean_price(self, price_text):
        """Clean price text to extract the number"""
        if price_text:
            return price_text.replace('Rs.', '').strip()
        return None
        
    def scrape_page(self, page_number):
        """Scrape a single page of products"""
        products = []
        url = f"{self.base_url}?page={page_number}"
        
        try:
            self.driver.get(url)
            time.sleep(5)  # Wait for page to load
            
            # Find all product items
            product_items = self.driver.find_elements(By.CLASS_NAME, "featured__item__text")
            
            for item in product_items:
                try:
                    product = {}
                    
                    # Get product name
                    name_element = item.find_element(By.CSS_SELECTOR, "h6 a")
                    product['name'] = name_element.text.strip()
                    
                    # Get current price
                    price_element = item.find_element(By.CSS_SELECTOR, "span[style*='color: #208e70']")
                    product['current_price'] = self.clean_price(price_element.text)
                    
                    # Get original price (strikethrough)
                    try:
                        strike_element = item.find_element(By.CSS_SELECTOR, "strike")
                        product['original_price'] = self.clean_price(strike_element.text)
                    except:
                        product['original_price'] = product['current_price']
                    
                    # Calculate discount
                    if product['original_price'] != product['current_price']:
                        product['discount'] = self.calculate_discount(
                            product['current_price'],
                            product['original_price']
                        )
                    else:
                        product['discount'] = 0
                    
                    # Get image URL
                    try:
                        # Need to go up to parent to find the image
                        parent_div = self.driver.find_element(
                            By.CSS_SELECTOR,
                            f"a[href*='{name_element.get_attribute('href')}']"
                        ).find_element(By.XPATH, "./../../..")
                        
                        img_div = parent_div.find_element(By.CLASS_NAME, "featured__item__pic")
                        img_url = img_div.get_attribute('data-setbg')
                        product['image_url'] = img_url
                    except:
                        product['image_url'] = None
                    
                    products.append(product)
                    
                except Exception as e:
                    print(f"Error extracting product details: {str(e)}")
                    continue
            
            return products
            
        except Exception as e:
            print(f"Error scraping page {page_number}: {str(e)}")
            return []
    
    def scrape_all_pages(self, start_page=1, end_page=3):
        """Scrape multiple pages of products"""
        try:
            self.setup_driver()
            all_products = []
            
            for page in range(start_page, end_page + 1):
                print(f"Scraping page {page}...")
                products = self.scrape_page(page)
                all_products.extend(products)
                
                # Save progress for each page
                with open(f'koyambedu_page_{page}.json', 'w', encoding='utf-8') as f:
                    json.dump(products, f, ensure_ascii=False, indent=2)
                
                print(f"Found {len(products)} products on page {page}")
                
                # Small delay between pages
                time.sleep(2)
            
            # Save all products to a single file
            with open('koyambedu_all_products.json', 'w', encoding='utf-8') as f:
                json.dump(all_products, f, ensure_ascii=False, indent=2)
            
            return all_products
            
        except Exception as e:
            print(f"An error occurred during scraping: {str(e)}")
            return None
            
        finally:
            self.close_driver()

if __name__ == "__main__":
    scraper = KoyambeduScraper(headless=False)  # Set headless=True for running without GUI
    results = scraper.scrape_all_pages(1, 3)  # Scrape pages 1-3
    
    if results:
        print("\nScraping completed successfully!")
        print(f"Total products scraped: {len(results)}")
        print("\nResults have been saved to:")
        print("- Individual JSON files for each page (koyambedu_page_X.json)")
        print("- Complete file with all products (koyambedu_all_products.json)")
        
        # Print sample of results
        print("\nSample of scraped data:")
        for product in results[:2]:  # Show first 2 products
            print(f"\nProduct: {product['name']}")
            print(f"Current Price: Rs.{product['current_price']}")
            print(f"Original Price: Rs.{product['original_price']}")
            print(f"Discount: {product['discount']}%")
            print(f"Image URL: {product['image_url']}")
    else:
        print("\nScraping failed")