import os
import sys
import json
import re
from openai import OpenAI  
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from db import supabase
except ImportError:
    from modules.db import supabase

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

MODEL_ID = "openrouter/free" 

def process_lead_ai_logic(lead_id, lead_name, company_name, scraped_context="No website available"):
    """
    Makes ONE single optimized call to OpenRouter Dynamic Free Tier.
    Generates 3 variant emails, judges the consensus best, and persists it to Supabase.
    """
    print(f"🧠 Processing lead generation logic via OpenRouter (Dynamic Free) for {lead_name}...")

    system_instructions = (
        "You are an expert BPO Automation Consultant agent.\n"
        "Task: Create 3 distinct cold email drafts targeting the recipient and choose the absolute best one.\n"
        "Our Value Proposition: We deploy AI Agents to automate BPO operations, reducing workload and cutting labor costs by 60%.\n\n"
        "Draft Requirements:\n"
        "1. Formal persona: Executive tone, focus on high ROI and operational metrics.\n"
        "2. Casual persona: Peer-to-peer, conversational, helpful.\n"
        "3. Direct persona: Punchy, maximum 2-3 sentences, straight to the point.\n"
        "Constraint: Keep all drafts under 100 words. Never use 'Dear Sir/Madam'.\n\n"
        "CRITICAL: You must reply ONLY with a valid JSON object. Do not wrap in markdown blocks, no text before or after the JSON.\n"
        "Expected JSON Structure:\n"
        "{\n"
        "    \"formal\": \"text of formal email\",\n"
        "    \"casual\": \"text of casual email\",\n"
        "    \"direct\": \"text of direct email\",\n"
        "    \"selected_best_draft\": \"the exact text of the one draft you judge to be most effective here\"\n"
        "}"
    )

    user_payload = f"""
    Recipient Name: {lead_name}
    Company Name: {company_name}
    Live Website Context: {scraped_context}
    """

    try:
        response = client.chat.completions.create(
            model=MODEL_ID,
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": user_payload}
            ]
        )
        
        raw_content = response.choices[0].message.content.strip()
        
        # Isolate JSON block bounds if extra text was included
        if "{" in raw_content and "}" in raw_content:
            start_idx = raw_content.find("{")
            end_idx = raw_content.rfind("}") + 1
            raw_content = raw_content[start_idx:end_idx]
        elif "```json" in raw_content:
            raw_content = raw_content.split("```json")[1].split("```")[0].strip()
        elif "```" in raw_content:
            raw_content = raw_content.split("```")[1].split("```")[0].strip()
            
 
        raw_content = re.sub(r'[\n\r\t]', ' ', raw_content)
                raw_content = re.sub(r'(?<!\\)"', r'"', raw_content) 

        ai_data = json.loads(raw_content)

        supabase_payload = {
            "lead_id": lead_id,
            "draft_1": ai_data.get("formal", "").strip(),
            "draft_2": ai_data.get("casual", "").strip(),
            "draft_3": ai_data.get("direct", "").strip(),
            "selected_best_draft": ai_data.get("selected_best_draft", "").strip()
        }

        if not supabase_payload["selected_best_draft"]:
            supabase_payload["selected_best_draft"] = supabase_payload["draft_3"] or supabase_payload["draft_2"]

        res = supabase.table("ai_drafts").insert(supabase_payload).execute()
        print("✅ Single-call consensus complete. Drafts saved via openrouter/free.")
        return res.data

    except Exception as e:
        print(f"❌ OpenRouter Free Model Engine Error: {e}")
        return None

if __name__ == "__main__":
    print("🚀 Local Token Test for OpenRouter...")
    process_lead_ai_logic(
        "9d4dd59b-c3c6-439b-a8be-8c3aebbe03f9", 
        "Vishal", 
        "Employee Zero", 
        "Scraped landing page mockup text"
    )
