from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import json
import time

def setup_driver():
    """Set up the Firefox webdriver with appropriate options"""
    firefox_options = Options()
    # Uncomment the line below if you want to run in headless mode
    # firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def scrape_dropdown_links(url):
    """Scrape all links inside the dropdown list"""
    driver = setup_driver()
    driver.get(url)

    # Wait until the dropdown list elements are loaded
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.jsx-1259984711 a"))
        )
    except Exception as e:
        print("Timeout: Unable to locate dropdown elements", e)
        driver.quit()
        return []

    links_data = []
    
    # Find all <a> tags inside the <li> elements
    link_elements = driver.find_elements(By.CSS_SELECTOR, "li.jsx-1259984711 a")
    
    for link in link_elements:
        try:
            href = link.get_attribute("href")
            text = link.text.strip()
            links_data.append({"text": text, "url": href})
        except Exception as e:
            print(f"Error extracting link details: {e}")

    driver.quit()

    # Save data to JSON file
    with open('dropdown_links.json', 'w', encoding='utf-8') as f:
        json.dump(links_data, f, ensure_ascii=False, indent=4)

    return links_data

url = "https://www.bigbasket.com/cl/fashion/?nc=nb"
links = scrape_dropdown_links(url)
print(f"Scraped {len(links)} links")
