import requests
import time
import random

TARGET_URL = "http://127.0.0.1:8000/search"

# Carefully curated payloads to trigger all layers of the WAF
payloads = [
    ("?q=normal_user_search", "Normal Traffic"),
    ("?q=where_to_buy_shoes", "Normal Traffic"),
    ("?q=<script>alert('hack')</script>", "OWASP XSS"),
    ("?q=admin' union select 1,2--", "OWASP SQLi"),
    ("?q=../../../etc/passwd", "OWASP Path Traversal"),
    ("?q=<svg/onload=prompt(1)>", "AI Zero-Day XSS"),
    ("?q=admin\" AND 5>4;--", "AI Zero-Day SQLi")
]

print("🚀 Starting UNLIMITED Presentation-Ready WAF Simulation...")
print("⚠️  Press CTRL+C in this terminal to stop the simulation at any time.")
print("-" * 50)

try:
    while True:
        # ==============================================================
        # PHASE 1: DIVERSE GLOBAL TRAFFIC
        # ==============================================================
        print("\n📡 Phase 1: Simulating Global Attackers (OWASP & AI)...")
        
        # Fire a randomized batch of 15 to 30 requests before switching to Phase 2
        for i in range(random.randint(15, 30)):
            payload, attack_category = random.choice(payloads)
            
            # Generate a fake IP to bypass the Bot Rate Limiter
            fake_ip = f"{random.randint(11, 199)}.{random.randint(1, 255)}.0.{random.randint(1, 255)}"
            headers = {"X-Forwarded-For": fake_ip}
            
            try:
                response = requests.get(f"{TARGET_URL}{payload}", headers=headers)
                if response.status_code == 403:
                    print(f"✅ BLOCKED by WAF  | {attack_category:<20} | IP: {fake_ip}")
                elif response.status_code == 200:
                    print(f"🟢 ALLOWED (Clean) | {attack_category:<20} | IP: {fake_ip}")
            except requests.exceptions.ConnectionError:
                print("❌ Server is offline.")
                
            time.sleep(0.3) # Slowed down to ensure natural dashboard flow

        # ==============================================================
        # PHASE 2: BOT BURST FROM A SINGLE IP
        # ==============================================================
        print("\n🤖 Phase 2: Initiating Automated Bot Attack Burst...")
        bot_ip = "10.0.0.99" 
        bot_payload = "?q=scraping_bulk_data"

        for i in range(25):
            headers = {"X-Forwarded-For": bot_ip}
            try:
                response = requests.get(f"{TARGET_URL}{bot_payload}", headers=headers)
                
                # Check for 403 or 429 to account for WAF standardizations
                if response.status_code in [403, 429]:
                    print(f"🛑 RATE LIMITED (Bot) | IP: {bot_ip} | Request {i+1}")
                else:
                    print(f"🟡 Warning Tracker   | IP: {bot_ip} | Request {i+1}")
            except requests.exceptions.ConnectionError:
                pass
                
            time.sleep(0.05) # Extreme speed to trigger the >15 requests WAF limit
            
except KeyboardInterrupt:
    print("\n" + "-" * 50)
    print("🛑 Simulation manually stopped.")