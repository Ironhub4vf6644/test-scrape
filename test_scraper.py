import asyncio
import logging
from fake_useragent import UserAgent
from playwright.async_api import async_playwright

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def solve_cloudflare(page):
    try:
        logger.info("Waiting for Cloudflare challenge...")
        await page.wait_for_selector('#challenge-stage', state='attached', timeout=30000)
        logger.info("Cloudflare challenge detected, solving...")
        
        # Add manual delay to simulate human interaction
        await asyncio.sleep(5)
        
        # Wait for challenge to complete
        await page.wait_for_selector('#challenge-stage', state='detached', timeout=60000)
        logger.info("Cloudflare challenge solved successfully")
        return True
    except Exception as e:
        logger.error(f"Cloudflare challenge error: {str(e)}")
        return False

async def test_scrape(url):
    try:
        ua = UserAgent()
        async with async_playwright() as p:
            # Configure browser with additional options
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-setuid-sandbox'
                ]
            )
            
            context = await browser.new_context(
                user_agent=ua.random,
                viewport={'width': 1920, 'height': 1080},
                extra_http_headers={
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Referer": "https://www.google.com/",
                }
            )
            
            page = await context.new_page()
            logger.info(f"Testing URL: {url}")

            # First navigation attempt
            try:
                await page.goto(url, wait_until="domcontentloaded", timeout=60000)
            except:
                pass

            # Check and handle Cloudflare challenge
            if await solve_cloudflare(page):
                # Second navigation attempt after challenge
                await page.goto(url, wait_until="networkidle", timeout=60000)
                
                content = await page.content()
                logger.info(f"Final page title: {await page.title()}")
                logger.info(f"Content length: {len(content)} bytes")
                return True
            
            await browser.close()
            return False
            
    except Exception as e:
        logger.error(f"Test failed: {str(e)}")
        return False

async def main():
    test_url = "https://4khdhub.fans"
    logger.info("Starting test...")
    
    for attempt in range(3):
        logger.info(f"Attempt {attempt + 1}/3")
        success = await test_scrape(test_url)
        if success:
            logger.info("✅ Scraping test successful!")
            return
        logger.info("Retrying...")
        await asyncio.sleep(5)
    
    logger.info("❌ All scraping attempts failed")

if __name__ == "__main__":
    asyncio.run(main())