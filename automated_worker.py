import json
import os
import time
import schedule
import pandas as pd
from datetime import datetime
from scraper import scrape_all
from mailer import send_news_digest

# --- Configuration Paths ---
USERS_FILE = "users.json"
CONFIG_FILE = "config.json"

def run_automated_digest():
    """Main worker function to scrape, select top news, and send emails."""
    print(f"\n[{datetime.now()}] 🚀 Starting Automated News Digest Process...")
    
    # 1. Load Configuration
    if not os.path.exists(CONFIG_FILE) or not os.path.exists(USERS_FILE):
        print("❌ Error: Missing config.json or users.json. Worker skipping...")
        return

    with open(CONFIG_FILE, "r") as f:
        config = json.load(f)
    
    with open(USERS_FILE, "r") as f:
        users = json.load(f)

    if not config.get("smtp_email") or not config.get("smtp_pass"):
        print("❌ Error: SMTP credentials not set in dashboard. Worker skipping...")
        return

    if not users:
        print("ℹ️ Info: No subscribers found. Worker skipping...")
        return

    # 2. Scrape Fresh News
    print("📡 Scraping latest global intelligence...")
    headlines = scrape_all(verbose=False)
    
    if not headlines:
        print("❌ Error: No headlines retrieved. Worker skipping...")
        return

    # 3. Select Top 10 "Moti News" (By Impact/Polarity)
    print("🧠 Analyzing impact and selecting 'Moti News'...")
    df = pd.DataFrame(headlines)
    df['impact'] = df['polarity'].abs()
    moti_news = df.sort_values('impact', ascending=False).head(10)
    news_list = list(moti_news.itertuples())

    # 4. Send to all subscribers
    print(f"📧 Sending digest to {len(users)} subscribers...")
    for user in users:
        try:
            success, msg = send_news_digest(
                config["smtp_email"], 
                config["smtp_pass"], 
                user["email"], 
                news_list
            )
            if success:
                print(f"  ✅ Sent to: {user['email']}")
            else:
                print(f"  ⚠️ Failed for {user['email']}: {msg}")
        except Exception as e:
            print(f"  ❌ Critical Error for {user['email']}: {str(e)}")

    print(f"[{datetime.now()}] ✨ Automated Digest Cycle Complete.")

# --- Schedule Configuration ---
# Schedule the digest for 10:00 AM every day
schedule.every().day.at("10:00").do(run_automated_digest)

# Also run once immediately on startup for verification (optional)
# run_automated_digest()

if __name__ == "__main__":
    print("🤖 News Scraper Automation Worker is ACTIVE.")
    print("⏰ Scheduled to send Daily Digest at 10:00 AM.")
    print("💡 Keep this window open for background automation.")
    
    while True:
        schedule.run_pending()
        time.sleep(60) # Check every minute
