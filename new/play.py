import json
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from urllib.parse import quote
import logging
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
import aiohttp

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BigBasketScraper:
    def __init__(self, max_concurrent_pages: int = 3, max_retries: int = 2):
        self.max_concurrent_pages = max_concurrent_pages
        self.max_retries = max_retries
        self.semaphore = asyncio.Semaphore(max_concurrent_pages)

    async def setup_browser(self):
        """Initialize Playwright browser with optimized settings."""
        playwright = await async_playwright().start()
        browser = await playwright.firefox.launch(
            headless=True,
            args=['--disable-dev-shm-usage', '--no-sandbox', '--disable-gpu']
        )
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        # Disable unnecessary resource loading
        await context.route("**/*.{png,jpg,jpeg,gif,svg,css,font}", lambda route: route.abort())
        context.set_default_timeout(30000)
        return playwright, browser, context

    async def extract_product_data(self, card) -> Dict[str, Any]:
        """Extract product data with optimized selectors."""
        try:
            # Use more specific selectors and extract data in parallel
            data_tasks = [
                self._get_text(card, ".BrandName___StyledLabel2-sc-hssfrl-1"),
                self._get_text(card, "h3.line-clamp-2"),
                self._get_price_info(card),
                self._get_text(card, ".PackSelector___StyledLabel-sc-1lmu4hv-0", "N/A"),
                self._get_text(card, ".OfferCommunication___StyledDiv-sc-zgmi5i-0", ""),
                self._get_ratings(card)
            ]
            brand, name, price_info, pack_size, special_offer, ratings = await asyncio.gather(*data_tasks)

            if not (brand and name):
                return None

            return {
                'brand': brand,
                'name': name,
                'new_price': price_info.get('new_price'),
                'old_price': price_info.get('old_price'),
                'pack_size': pack_size,
                'special_offer': special_offer,
                **ratings
            }
        except Exception as e:
            logger.error(f"Error extracting product data: {e}")
            return None

    async def _get_text(self, card, selector: str, default: str = "") -> str:
        """Optimized text extraction."""
        try:
            element = await card.query_selector(selector)
            return (await element.text_content()) if element else default
        except Exception:
            return default

    async def _get_price_info(self, card) -> Dict[str, float]:
        """Extract price information efficiently."""
        try:
            price_div = await card.query_selector(".Pricing___StyledDiv-sc-pldi2d-0")
            if not price_div:
                return {'new_price': None, 'old_price': None}

            async def extract_price(selector):
                elem = await price_div.query_selector(selector)
                if elem:
                    text = await elem.text_content()
                    return float(text.replace('₹', '').replace(',', '').strip())
                return None

            new_price, old_price = await asyncio.gather(
                extract_price(".Pricing___StyledLabel-sc-pldi2d-1"),
                extract_price(".Pricing___StyledLabel2-sc-pldi2d-2")
            )
            return {'new_price': new_price, 'old_price': old_price}
        except Exception:
            return {'new_price': None, 'old_price': None}

    async def _get_ratings(self, card) -> Dict[str, Any]:
        """Extract ratings information efficiently."""
        try:
            ratings_div = await card.query_selector(".ReviewsAndRatings___StyledDiv-sc-2rprpc-0")
            if not ratings_div:
                return {'rating': 0.0, 'review_count': "0 Ratings"}

            rating_elem = await ratings_div.query_selector("span.Label-sc-15v1nk5-0 span")
            review_count_elem = await ratings_div.query_selector(".ReviewsAndRatings___StyledLabel-sc-2rprpc-1")

            rating = float(await rating_elem.text_content()) if rating_elem else 0.0
            review_count = await review_count_elem.text_content() if review_count_elem else "0 Ratings"

            return {'rating': rating, 'review_count': review_count}
        except Exception:
            return {'rating': 0.0, 'review_count': "0 Ratings"}

    async def scrape_product_page(self, product_name: str) -> List[Dict[str, Any]]:
        """Scrape a single product page with optimized loading."""
        async with self.semaphore:
            url = f"https://www.bigbasket.com/ps/?q={quote(product_name.replace(' ', '+'))}&nc=as"
            print("Scrapping : ",url)
            products = []

            try:
                page = await self.context.new_page()
                await page.goto(url, wait_until="domcontentloaded")
                
                # Wait for the first product card only
                try:
                    await page.wait_for_selector(".SKUDeck___StyledDiv-sc-1e5d9gk-0", timeout=15000)
                except TimeoutError:
                    logger.warning(f"No products found for {product_name}")
                    return []

                # Optimized scrolling with reduced waits
                previous_height = 0
                for _ in range(3):  # Limit scrolling attempts
                    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                    await asyncio.sleep(0.5)  # Reduced sleep time
                    
                    cards = await page.query_selector_all(".SKUDeck___StyledDiv-sc-1e5d9gk-0")
                    if len(cards) == previous_height:
                        break
                    previous_height = len(cards)

                # Process all products in parallel
                tasks = [self.extract_product_data(card) for card in cards]
                results = await asyncio.gather(*tasks)
                products.extend([p for p in results if p])

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
            finally:
                await page.close()

            return products

    async def scrape_products(self, product_names: List[str]) -> List[Dict[str, Any]]:
        """Main scraping function with concurrent processing."""
        playwright, browser, self.context = await self.setup_browser()
        try:
            # Process multiple pages concurrently
            tasks = [self.scrape_product_page(name) for name in product_names]
            results = await asyncio.gather(*tasks)
            
            # Flatten results
            all_products = [product for sublist in results for product in sublist]
            return all_products

        finally:
            await self.context.close()
            await browser.close()
            await playwright.stop()

async def main():
    try:
        with open('new/product_links/product_details.json', 'r') as f:
            category = json.load(f)
            category_links = [item["name"] for item in category]
            category_links=category_links[:10]
    except Exception as e:
        logger.error(f"Failed to load category links: {e}")
        return

    scraper = BigBasketScraper(max_concurrent_pages=3)
    results = await scraper.scrape_products(category_links)

    output_file = 'new/big_products.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    logger.info(f"Saved {len(results)} products to {output_file}")

if __name__ == "__main__":
    asyncio.run(main())