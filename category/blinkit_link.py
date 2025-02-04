from selenium import webdriver
from selenium.webdriver.common.by import By
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

def scrape_blinkit_category_links(url):
    """Scrape all category links from Blinkit"""
    driver = setup_driver()
    category_links = []
    
    try:
        driver.get(url)
        
        # Wait for category list to load
        time.sleep(5)  # Adjust if needed for dynamic content
        
        # Find all category links
        category_elements = driver.find_elements(By.CSS_SELECTOR, "a.Category__PageLink-sc-1k4awti-2")
        
        for element in category_elements:
            try:
                link = element.get_attribute("href")
                category_links.append(link)
            except Exception as e:
                print(f"Error extracting link: {e}")
                continue
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()
    
    # Save category links to JSON
    with open('blinkit_category_links.json', 'w', encoding='utf-8') as f:
        json.dump(category_links, f, ensure_ascii=False, indent=2)
    
    return category_links

if __name__ == "__main__":
    blinkit_url = "https://blinkit.com/categories"
    results = scrape_blinkit_category_links(blinkit_url)

    if results:
        print(f"Successfully scraped {len(results)} category links")
        print("Results have been saved to 'blinkit_category_links.json'")
    else:
        print("Scraping failed")
