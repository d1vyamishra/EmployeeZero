import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")

print(f"Connecting to: {url}")

supabase: Client = create_client(url, key)

def test_connection():
    try:
        dummy_data = {
            "full_name": "Test Connection",
            "email_address": "connection_test@example.com",
            "status": "New"
        }
        
        response = supabase.table("leads").insert(dummy_data).execute()
        print("✅ Connection Successful!")
        print(f"Response: {response.data}")
        
    except Exception as e:
        print(f"❌ Connection Failed: {e}")

if __name__ == "__main__":
    test_connection()
