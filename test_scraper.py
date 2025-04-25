import asyncio
import logging
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_scrape(url):
    try:
        ua = UserAgent()
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent=ua.random,
                extra_http_headers={
                    "Accept-Language": "en-US,en;q=0.9",
                    "Referer": "https://www.google.com/"
                }
            )
            
            page = await context.new_page()
            logger.info(f"Testing URL: {url}")
            
            # First request to bypass Cloudflare
            await page.goto(url, wait_until="networkidle", timeout=60000)
            
            # Check for Cloudflare challenge
            if "Just a moment" in await page.title():
                logger.info("Solving Cloudflare challenge...")
                await page.wait_for_selector('#cf-challenge-running', state='detached', timeout=60000)
            
            content = await page.content()
            await browser.close()
            
            logger.info(f"Successfully loaded page: {await page.title()}")
            logger.info(f"Content length: {len(content)} bytes")
            
            return True
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

async def main():
    test_url = "https://4khdhub.fans"  # Change this to your target URL
    success = await test_scrape(test_url)
    
    if success:
        logger.info("✅ Scraping test successful!")
    else:
        logger.info("❌ Scraping test failed")

if __name__ == "__main__":
    asyncio.run(main())