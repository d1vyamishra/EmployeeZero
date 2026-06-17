# Save this inside backend/modules/scraper.py
import asyncio
from playwright.async_api import async_playwright

async def scrape_company_website(url: str):
    """
    Navigates to a company website and extracts main text content.
    Optimized with fast DOM loading to prevent timeout errors on heavy sites.
    """
    print(f"🌐 Agent opening browser to visit: {url}...")
    
    async with async_playwright() as p:
        # Launching a headless browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            # Set a standard user agent to avoid basic bot blocks
            await page.set_extra_http_headers({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            })

            # Changed wait_until to 'domcontentloaded' to avoid freezing on heavy trackers/analytics scripts
            await page.goto(url, wait_until="domcontentloaded", timeout=25000)
            
            # Extract page title
            title = await page.title()
            
            # Extract raw inner text from the body element
            body_text = await page.evaluate("() => document.body.innerText")
            
            # Clean up excessive white spaces and newlines
            clean_text = " ".join(body_text.split())
            
            # Limit context size to 1500 characters so we don't blow past Gemini's prompt tokens
            truncated_context = clean_text[:1500] 
            
            print(f"✅ Successfully scraped context from: '{title}'")
            await browser.close()
            return truncated_context

        except Exception as e:
            print(f"❌ Failed to scrape {url}: {e}")
            await browser.close()
            return "No website data available due to connection timeout."

if __name__ == "__main__":
    # Quick Local Module Testing
    test_url = "https://example.com"
    print("🧪 Testing Scraper Module locally...")
    context = asyncio.run(scrape_company_website(test_url))
    print(f"\n📄 Scraped Context Output:\n{context}")