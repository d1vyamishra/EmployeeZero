import os
import sys
import asyncio
import random
from playwright.async_api import async_playwright
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
try:
    from db import supabase
except ImportError:
    from modules.db import supabase

load_dotenv()

async def find_linkedin_profile_simple(company_name, role="Founder"):
    print(f"🕵️‍♂️ Agent search activated for: {company_name} ({role})...")
    
    search_query_a = f"site:linkedin.com/in/ \"{company_name}\" \"{role}\""
    search_query_b = f"\"{company_name}\" \"{role}\" linkedin profile"
    
    found_url = None
    
    async with async_playwright() as p:
        
        user_data_dir = os.path.join(os.getcwd(), "playwright_browser_profile")
        
        browser_context = await p.chromium.launch_persistent_context(
            user_data_dir,
            headless=False, 
            args=["--disable-blink-features=AutomationControlled"] # Hides the automated banner
        )
        
        page = browser_context.pages[0] if browser_context.pages else await browser_context.new_page()
        
        for idx, query in enumerate([search_query_a, search_query_b]):
            if idx > 0:
                print("🔄 Strategy A restricted. Deploying fallback search strategy...")
                await asyncio.sleep(random.uniform(3.0, 5.0))
                
            encoded_query = query.replace(" ", "+")
            target_search_url = f"https://www.google.com/search?q={encoded_query}"
            
            try:
                await page.goto(target_search_url, wait_until="domcontentloaded", timeout=15000)
                
                await page.wait_for_timeout(3000)
                
                hrefs = await page.evaluate(
                    "() => Array.from(document.querySelectorAll('a')).map(a => a.href)"
                )
                
                for href in hrefs:
                    if "linkedin.com/in/" in href and "google.com" not in href:
                        found_url = href.split("?")[0].split("&")[0]
                        break
                        
                if found_url:
                    break
                    
            except Exception as e:
                print(f"⚠️ Search step timed out: {e}")
                
        await browser_context.close()
        return found_url

def update_lead_linkedin_url(company_name, linkedin_url):
    try:
        res = supabase.table("leads")\
            .update({"linkedin_url": linkedin_url})\
            .ilike("company_name", f"%{company_name}%")\
            .execute()
        print(f"💾 Supabase Synchronization complete for {company_name}.")
        return res.data
    except Exception as e:
        print(f"❌ Database synchronization failed: {e}")
        return None

async def main():
    test_company = "Appfinz Technologies"
    profile_url = await find_linkedin_profile_simple(test_company, "Founder")
    
    if profile_url:
        print(f"\n🎯 Target Found! LinkedIn Profile: {profile_url}")
        update_lead_linkedin_url(test_company, profile_url)
    else:
        print("\n📭 LinkedIn profile search returned no records. Check the opened browser window for blocks.")

if __name__ == "__main__":
    asyncio.run(main())
