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

def scrape_bigbasket_category_links(url, max_links=50):
    """Scrape the final category links from BigBasket"""
    driver = setup_driver()
    category_links = []
    
    try:
        driver.get(url)
        
        # Wait for category list to load
        time.sleep(5)  # Adjust if needed for dynamic content
        
        # Find all categories (you can adjust the class names or CSS selectors based on actual page structure)
        category_sections = driver.find_elements(By.CSS_SELECTOR, "ul.jsx-1259984711 li")
        
        for section in category_sections:
            try:
                # Get the last link in each section
                last_link = section.find_elements(By.CSS_SELECTOR, 'a.CategoryTree___StyledLink-sc-8wbym9-0')[-1]
                category_links.append(last_link.get_attribute("href"))
                
                if len(category_links) >= max_links:
                    break  # Stop when the max number of links is reached

            except Exception as e:
                print(f"Error extracting link: {e}")
                continue
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()
    
    # Save category links to JSON
    with open('bigbasket_category_links.json', 'w', encoding='utf-8') as f:
        json.dump(category_links, f, ensure_ascii=False, indent=2)

    return category_links


if __name__ == "__main__":
    bigbasket_url = "https://www.bigbasket.com/"
    results = scrape_bigbasket_category_links(bigbasket_url)

    if results:
        print(f"Successfully scraped {len(results)} category links")
        print("Results have been saved to 'bigbasket_category_links.json'")
    else:
        print("Scraping failed")
