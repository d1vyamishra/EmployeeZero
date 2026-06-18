import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def send_autonomous_email(to_email, subject, email_body):
    """Sends a beautifully formatted HTML email directly using employeezero00@gmail.com."""
    sender_email = os.getenv("GMAIL_USER", "employeezero00@gmail.com")
    app_password = os.getenv("GMAIL_APP_PASSWORD")

    if not app_password:
        print("⚠️ GMAIL_APP_PASSWORD missing in configuration.")
        return False

    try:
        formatted_body = email_body.replace("\n", "<br />")
        
        placeholders = ["{Your Name}", "[Your Name]", "{My Name}", "[My Name]"]
        for placeholder in placeholders:
            formatted_body = formatted_body.replace(placeholder, "Employee Zero Team")

        html_content = f"""
        <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; 
                    font-size: 15px; line-height: 1.6; color: #333333; max-width: 600px;">
            {formatted_body}
        </div>
        """

        msg = MIMEMultipart("alternative")
        msg["From"] = f"Employee Zero <{sender_email}>"  
        msg["To"] = to_email
        msg["Subject"] = subject
        
        msg.attach(MIMEText(html_content, "html"))

        print(f"📧 Dispatching direct Gmail SMTP email to: {to_email}...")

        server = smtplib.SMTP("smtp.gmail.com", 587)  
        server.starttls() 
        server.login(sender_email, app_password)
        
        server.sendmail(sender_email, to_email, msg.as_string())
        server.quit()

        print(f"✅ Email successfully sent directly from {sender_email}!")
        return True

    except Exception as e:
        print(f"❌ Direct Gmail SMTP delivery failed: {e}")
        return False
