import os
import imaplib
import email
from email.header import decode_header
from openai import OpenAI
from dotenv import load_dotenv
from modules.db import supabase
from modules.email_sender import send_autonomous_email

load_dotenv()

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
)

def check_for_replies_and_respond():
    """Checks your Gmail for real unread customer responses, sends a reply, and updates Supabase."""
    IMAP_SERVER = "imap.gmail.com"
    EMAIL_ACCOUNT = os.getenv("GMAIL_USER", "employeezero00@gmail.com")
    EMAIL_PASSWORD = os.getenv("GMAIL_APP_PASSWORD") 

    if not EMAIL_PASSWORD:
        print("⚠️ GMAIL_APP_PASSWORD not set in your environment file. Skipping inbound check.")
        return

    try:
        print("📥 Connecting to inbox to check for customer responses...")
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
        mail.select("inbox")

        status, messages = mail.search(None, 'UNSEEN')
        
        if messages[0] == b'':
            print("😴 No fresh unread incoming lead replies found.")
            return

        for num in messages[0].split():
            status, data = mail.fetch(num, "(RFC822)")
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    from_text, encoding = decode_header(msg["From"])[0]
                    if isinstance(from_text, bytes):
                        from_text = from_text.decode(encoding or "utf-8")
                    
                    ignore_keywords = [
                        "onboarding@resend.dev", "employeezero", "noreply", "donotreply",
                        "google", "reddit", "arxiv", "preprints", "instagram", "canva", 
                        "x.com", "twitter", "hackerone", "streamlabs", "verify", "security"
                    ]
                    if any(keyword in from_text.lower() for keyword in ignore_keywords):
                        continue
                    
                    subject_text, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject_text, bytes):
                        subject_text = subject_text.decode(encoding or "utf-8")

                    incoming_body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                incoming_body = part.get_payload(decode=True).decode()
                                break
                    else:
                        incoming_body = msg.get_payload(decode=True).decode()

                    print(f"✉️ Found fresh reply from {from_text} (Subject: {subject_text})! Processing...")
                    
                    ai_response = draft_reply_with_ai(incoming_body)
                    
                    if ai_response:
                        print(f"🤖 AI Generated Follow-up Answer:\n{ai_response}\n")
                        
                        reply_subject = f"Re: {subject_text}" if not subject_text.startswith("Re:") else subject_text
                        email_sent = send_autonomous_email(from_text, reply_subject, ai_response)
                        
                        if email_sent:
                            print("🚀 Reply message successfully dispatched via Gmail SMTP server!")
                        
                        try:
                            supabase.table("lead_replies").insert({
                                "incoming_message": incoming_body,
                                "ai_reply_draft": ai_response,
                                "status": "Sent" if email_sent else "Failed"
                            }).execute()
                            print("💾 Conversation saved to Supabase.")
                        except Exception as db_err:
                            print(f"⚠️ Could not log reply to Supabase: {db_err}")

                        mail.store(num, '+FLAGS', '\\Seen')

        mail.logout()

    except Exception as e:
        print(f"❌ Failed processing incoming mailboxes: {e}")

def draft_reply_with_ai(incoming_question):
    """Processes questions and frames an answer leveraging openrouter/free."""
    system_prompt = (
        "You are an expert BPO Automation Consultant agent representing Employee Zero.\n"
        "A lead replied to our cold outreach email with a question or objection.\n"
        "Our core value proposition: We deploy custom AI Agents to cut BPO workloads and labor costs by 60%.\n\n"
        "CRITICAL COMPANY KNOWLEDGE:\n"
        "- Our Founder is: Divya Prakash Mishra\n"
        "- Location: Living in Ballia\n"
        "- Founder's GitHub: https://github.com/d1vyamishra/\n\n"
        "Rules:\n"
        "1. If the lead asks anything about the founder, who started this company, or the team behind it, you MUST explicitly state that the founder is Divya Prakash Mishra, living in Ballia, and provide his GitHub link.\n"
        "2. Formulate a concise, highly strategic response answering their question under 80 words. End with a calendar link offer.\n"
        "3. Do NOT include any 'User Safety' or internal system metadata text in your reply content. Start writing the email body immediately."
    )
    
    try:
        response = client.chat.completions.create(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Lead incoming message: {incoming_question}"}
            ]
        )
        raw_content = response.choices[0].message.content.strip()
        
        if "user safety:" in raw_content.lower():
            raw_content = raw_content.replace("User Safety: safe", "").replace("User Safety: Safe", "").strip()
            
        return raw_content
    except Exception as e:
        print(f"❌ OpenRouter Free Reply Generation Failure: {e}")
        return None
