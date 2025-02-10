from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import time
import json

def setup_driver():
    """Set up the Firefox webdriver with appropriate options"""
    firefox_options = Options()
    # Uncomment the line below if you want to run in headless mode
    # firefox_options.add_argument('--headless')
    driver = webdriver.Firefox(options=firefox_options)
    return driver

def scrape_swiggy_restaurants(url, max_restaurants=200):
    driver = setup_driver()
    driver.get(url)

    # Wait until restaurant elements are loaded
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.sc-empnci"))
        )
    except Exception as e:
        print("Timeout: Unable to locate restaurant elements", e)
        driver.quit()
        return []

    restaurants_data = []
    
    while len(restaurants_data) < max_restaurants:
        restaurant_cards = driver.find_elements(By.CSS_SELECTOR, "a.sc-empnci")
        
        for card in restaurant_cards:
            if len(restaurants_data) >= max_restaurants:
                break
            try:
                WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, ".sc-aXZVg.kVQudY"))
                )
                
                name = card.find_element(By.CSS_SELECTOR, ".sc-aXZVg.kVQudY").text
                rating_delivery = card.find_element(By.CSS_SELECTOR, ".sc-aXZVg.kIcQre").text.split('•')
                rating = rating_delivery[0].strip() if len(rating_delivery) > 0 else "N/A"
                delivery_time = rating_delivery[1].strip() if len(rating_delivery) > 1 else "N/A"
                cuisine = card.find_element(By.CSS_SELECTOR, ".sw-restaurant-card-descriptions-container .sc-aXZVg.klLkzp").text
                location = card.find_elements(By.CSS_SELECTOR, ".sw-restaurant-card-descriptions-container .sc-aXZVg.klLkzp")[1].text
                image_url = card.find_element(By.CSS_SELECTOR, "img.sc-bXCLTC").get_attribute('src')

                restaurant_info = {
                    'Name': name,
                    'Rating': rating,
                    'Delivery Time': delivery_time,
                    'Cuisine': cuisine,
                    'Location': location,
                    'Image URL': image_url
                }
                restaurants_data.append(restaurant_info)

            except Exception as e:
                print(f"Error extracting details: {e}")

        # Scroll down to load more restaurants
        driver.execute_script("window.scrollBy(0, 500);")
        time.sleep(3)  # Wait for more elements to load

    driver.quit()

    with open('swiggy_restaurants.json', 'w', encoding='utf-8') as f:
        json.dump(restaurants_data, f, ensure_ascii=False, indent=4)

    return restaurants_data

url = "https://www.swiggy.com/restaurants"
restaurants = scrape_swiggy_restaurants(url)
print(f"Scraped {len(restaurants)} restaurants")
