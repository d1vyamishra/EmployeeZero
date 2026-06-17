# Save this as backend/ingest_leads.py
import uuid
from modules.db import supabase

def bulk_ingest_leads(leads_list):
    """
    Takes a list of dictionaries containing lead data and pushes them to Supabase.
    Prevents crashing by checking key formats.
    """
    print(f"📥 Starting ingestion for {len(leads_list)} leads...")
    
    prepared_data = []
    for lead in leads_list:
        # Construct clean dictionary payload mapping your table columns
        payload = {
            "id": str(uuid.uuid4()),  # Generates unique IDs automatically
            "full_name": lead.get("full_name"),
            "email_address": lead.get("email_address"),
            "company_name": lead.get("company_name", "Unknown"),
            "website_url": lead.get("website_url"),
            "status": "New"  # Forces status back to 'New' so main.py handles it
        }
        prepared_data.append(payload)

    try:
        # Pushing the entire list in one heavy batch call
        response = supabase.table("leads").insert(prepared_data).execute()
        print(f"✅ Successfully ingested {len(response.data)} records into Supabase!")
        return response.data
    except Exception as e:
        print(f"❌ Batch ingestion failed: {e}")
        return None

if __name__ == "__main__":
    # Sample Mock Database List (Aap yahan real data fill kar sakte ho)
    mock_leads = [
        {
            "full_name": "Sam Altman",
            "email_address": "vishalmishra739831+sam@gmail.com", # +sam tags help test multiple inputs to one email
            "company_name": "OpenAI",
            "website_url": "https://openai.com"
        },
        {
            "full_name": "Tim Cook",
            "email_address": "vishalmishra739831+tim@gmail.com",
            "company_name": "Apple",
            "website_url": "https://apple.com"
        },
        {
            "full_name": "Satya Nadella",
            "email_address": "vishalmishra739831+satya@gmail.com",
            "company_name": "Microsoft",
            "website_url": "https://microsoft.com"
        }
    ]
    
    bulk_ingest_leads(mock_leads)