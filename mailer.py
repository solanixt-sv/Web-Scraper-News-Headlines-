import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_news_digest(smtp_email, smtp_password, recipient_email, news_items):
    """Sends a news digest email using SMTP."""
    try:
        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = "🗞️ Your Daily Intelligence Digest - Top 10 Stories"
        msg["From"] = f"News Intelligence Hub <{smtp_email}>"
        msg["To"] = recipient_email

        # Create HTML Content
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">
            <div style="max-width: 600px; margin: auto; background: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                <h2 style="color: #3b82f6; text-align: center;">📡 Intelligence Digest</h2>
                <p style="color: #666; text-align: center;">Here are the top 10 most impactful stories for today.</p>
                <hr style="border: 0; border-top: 1px solid #eee;">
                
                {"".join([f'''
                <div style="margin-bottom: 20px; padding-bottom: 10px; border-bottom: 1px solid #eee;">
                    <h3 style="margin: 0; color: #1e293b;">{item.title}</h3>
                    <p style="font-size: 14px; color: #475569; margin: 5px 0;">{item.description[:150]}...</p>
                    <a href="{item.link}" style="color: #3b82f6; font-weight: bold; text-decoration: none; font-size: 13px;">Read Full Report →</a>
                </div>
                ''' for item in news_items])}
                
                <p style="font-size: 11px; color: #94a3b8; text-align: center; margin-top: 30px;">
                    You are receiving this because you subscribed to the News Intelligence Dashboard.<br>
                    © 2026 Intelligence Hub
                </p>
            </div>
        </body>
        </html>
        """
        
        msg.attach(MIMEText(html, "html"))

        # Connect and Send
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(smtp_email, smtp_password)
            server.sendmail(smtp_email, recipient_email, msg.as_string())
        
        return True, "Email sent successfully!"
    except Exception as e:
        return False, str(e)
