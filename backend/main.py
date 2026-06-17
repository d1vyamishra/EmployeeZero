import time
import asyncio
from modules.db import supabase
from modules.ai_brain import process_lead_ai_logic
from modules.email_sender import send_autonomous_email
from modules.scraper import scrape_company_website
from modules.linkedin_agent import find_linkedin_profile_simple, update_lead_linkedin_url
from modules.reply_processor import check_for_replies_and_respond  # Added inbound check

async def run_automation_cycle():
    print("\n🔄 [Cycle Start] EmployeeZero: Scanning database and email channels...")

    # ------------------------------------------------------------
    # STEP 0: CHECK FOR INBOUND RESPONSES AND AUTOMATE REPLIES
    # ------------------------------------------------------------
    try:
        check_for_replies_and_respond()
    except Exception as e:
        print(f"⚠️ Inbound reply check skipped or failed: {e}")

    # ------------------------------------------------------------
    # STEP 1: AUTO-FIND MISSING LINKEDIN PROFILES FOR NEW LEADS
    # ------------------------------------------------------------
    missing_li_leads = supabase.table("leads")\
        .select("*")\
        .eq("status", "New")\
        .is_("linkedin_url", "null")\
        .execute()

    if missing_li_leads.data:
        print(f"🔍 Found {len(missing_li_leads.data)} leads missing LinkedIn profiles. Mining started...")
        for lead in missing_li_leads.data:
            company = lead.get('company_name')
            if company:
                profile_url = await find_linkedin_profile_simple(company, "Founder")
                if profile_url:
                    update_lead_linkedin_url(company, profile_url)
                    await asyncio.sleep(5)
    else:
        print("✅ All current 'New' leads have LinkedIn URLs attached.")


    # ------------------------------------------------------------
    # STEP 2: PROCESS LEADS AND DEPLOY AUTONOMOUS COLD EMAILS
    # ------------------------------------------------------------
    leads = supabase.table("leads").select("*").eq("status", "New").execute()

    if not leads.data:
        print("📭 No pending 'New' leads left to email during this cycle.")
        return

    print(f"📈 Found {len(leads.data)} leads ready for email processing.")

    for lead in leads.data:
        lead_id = lead['id']
        name = lead['full_name']
        email = lead.get('email') or lead.get('email_address')
        
        if not email:
            print(f"⚠️ Skipping lead {name} - No target email found in database row.")
            continue
        
        company = lead['company_name'] or "their company"
        website = lead.get('website_url')

        print(f"\n🧠 Brain generating custom pitch for: {name} ({company}) -> Target: {email}...")

        # Extract Web Data
        scraped_context = "No website available"
        if website and str(website).strip().startswith("http"):
            try:
                scraped_context = await scrape_company_website(website)
            except Exception as e:
                print(f"⚠️ Scraping bypassed due to load delay: {e}")

        # Cooldown guard to respect free rate-limits
        print("⏳ Cooling down model API usage state...")
        await asyncio.sleep(12) 
        
        result = process_lead_ai_logic(lead_id, name, company, scraped_context)

        if result:
            current_row = result[0] if isinstance(result, list) else result
            winning_draft = current_row.get('selected_best_draft')
            
            if not winning_draft:
                print("⚠️ Could not extract 'selected_best_draft'. Skipping delivery.")
                continue

            subject = f"Automation Strategy for {company}"
            email_success = send_autonomous_email(email, subject, winning_draft)

            if email_success:
                supabase.table("leads").update({"status": "Emailed"}).eq("id", lead_id).execute()
                print(f"🎉 Finished processing {name}. Status updated to 'Emailed'.")
            else:
                print(f"⚠️ Mail delivery failed, keeping status 'New' for retry.")
        else:
            print(f"❌ Skipping lead {name} due to AI Gen failure.")

def run_automation():
    """Synchronous execution wrapper for the background worker script"""
    asyncio.run(run_automation_cycle())

async def main_loop():
    print("🤖 EmployeeZero Autonomous Engine Activated.")
    print("⏰ Interval check locked to: Every 10 Minutes (600 Seconds)")
    
    while True:
        try:
            await run_automation_cycle()
        except Exception as e:
            print(f"🚨 Engine Runtime Exception caught during loop: {e}")
            
        print("\n😴 Cycle complete. Sleeping for 10 minutes before next sweep...")
        await asyncio.sleep(600)

if __name__ == "__main__":
    asyncio.run(main_loop())