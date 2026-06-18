import asyncio
import re
from playwright.async_api import async_playwright
from modules.db import supabase  
EMAIL_REGEX = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

async def extract_email_from_website(browser, url):
    """Nayi tab kholkar website se email dhoondhne ka function"""
    try:
        context = await browser.new_context()
        page = await context.new_page()
        await page.goto(url, timeout=15000)
        await page.wait_for_timeout(3000)
        
        page_source = await page.content()
        emails = re.findall(EMAIL_REGEX, page_source)
        
        await context.close()
        
        if emails:
            valid_emails = [e for e in emails if not e.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
            return valid_emails[0] if valid_emails else None
        return None
    except Exception as e:
        print(f"⚠️ Website open karne mein dikkat aayi: {url}")
        return None

async def scrape_and_save_leads():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()
        
        print("🤖 Agent Google Maps se fresh data utha raha hai...")
        search_query = "Tech Companies in Delhi"
        await page.goto(f"https://www.google.com/maps/search/{search_query}")
        
        await page.wait_for_timeout(5000)
        cards = await page.locator('//a[contains(@href, "/maps/place/")]').all()
        
        for index, card in enumerate(cards[:3]):
            try:
                name = await card.get_attribute('aria-label')
                if name:
                    print(f"\n🏢 Company #{index+1}: {name}")
                    await card.click()
                    await page.wait_for_timeout(3000)
                    
                    website_element = page.locator('//a[@data-item-id="authority"]')
                    if await website_element.count() > 0:
                        url = await website_element.get_attribute('href')
                        print(f"🌐 Website: {url} -> Extracting Email...")
                        
                        email = await extract_email_from_website(browser, url)
                        
                        if email:
                            print(f"📧 Email Found: {email}")
                            
                    
                            print("💾 Saving lead to Supabase...")
                            data, count = supabase.table("leads").insert({
                                "company_name": name,
                                "email_address": email,
                                "full_name": "Tech Team", 
                                "status": "New"  
                            }).execute()
                            print("✅ Successfully Saved!")
                        else:
                            print("📭 Website par direct public email nahi mila.")
                    else:
                        print("📭 Website available nahi hai.")
            except Exception as e:
                print(f"⚠️ Error processing card: {e}")
                continue
                
        await browser.close()

if __name__ == "__main__":
    asyncio.run(scrape_and_save_leads())
